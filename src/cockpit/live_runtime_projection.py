#!/usr/bin/env python3
"""LIVE_RUNTIME_PROJECTION_001 read-only runtime sidecar."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import subprocess
import threading
import time
from typing import Any, Iterator
from urllib.parse import urlparse


class LiveRuntimeProjectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeSources:
    repo: Path
    controller_db: Path | None = None
    campaign_db: Path | None = None
    selection_db: Path | None = None
    preparation_db: Path | None = None
    semantic_db: Path | None = None
    comparison_basis_refs: tuple[str, ...] = ()


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise LiveRuntimeProjectionError(
            "cannot resolve repository HEAD: " + result.stderr.strip()
        )
    return result.stdout.strip()


def resolve_comparison_basis(sources: RuntimeSources) -> list[str]:
    resolved: list[str] = []
    for ref in sources.comparison_basis_refs:
        if ref == "git:HEAD":
            resolved.append("git:" + _repo_head(sources.repo))
        else:
            resolved.append(ref)
    return resolved


def _ro_connect(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=2.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def _read_source(
    name: str,
    path: Path | None,
    queries: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if path is None:
        return {}, {"source": name, "status": "NOT_CONFIGURED"}
    if not path.exists():
        return {}, {
            "source": name,
            "status": "UNAVAILABLE",
            "path": str(path),
            "error": "database path does not exist",
        }

    conn: sqlite3.Connection | None = None
    try:
        conn = _ro_connect(path)
        values: dict[str, Any] = {}
        for key, sql in queries.items():
            rows = conn.execute(sql).fetchall()
            values[key] = [dict(row) for row in rows]
        return values, {
            "source": name,
            "status": "AVAILABLE",
            "path": str(path),
            "read_mode": "SQLITE_QUERY_ONLY",
        }
    except Exception as exc:
        return {}, {
            "source": name,
            "status": "UNAVAILABLE",
            "path": str(path),
            "error": f"{type(exc).__name__}: {exc}",
        }
    finally:
        if conn is not None:
            conn.close()


def _decode_json_fields(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        for field in fields:
            value = item.get(field)
            if isinstance(value, str):
                try:
                    item[field] = json.loads(value)
                except json.JSONDecodeError:
                    item[field] = {
                        "_projection_error": "INVALID_JSON",
                        "_raw_value": value,
                    }
        result.append(item)
    return result


def _current_selection(
    selection_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    current: dict[tuple[str, str], dict[str, Any]] = {}
    for row in selection_rows:
        event = row.get("event_json")
        if not isinstance(event, dict):
            continue
        key = (str(event.get("request_id")), str(event.get("request_sha256")))
        if event.get("selection_kind") == "SELECTED_FOR_PACKET_FORMATION":
            current[key] = event
        elif event.get("selection_kind") == "SELECTION_RELEASED":
            current.pop(key, None)
    return [current[key] for key in sorted(current)]


def _preparation_readiness(
    *,
    campaigns: list[dict[str, Any]],
    standing_rows: list[dict[str, Any]],
    request_rows: list[dict[str, Any]],
    current_selection: list[dict[str, Any]],
    prep_rows: list[dict[str, Any]],
    comparison_basis_refs: list[str],
) -> list[dict[str, Any]]:
    campaign_map = {
        row["campaign_id"]: row.get("campaign_json")
        for row in campaigns
        if isinstance(row.get("campaign_json"), dict)
    }
    standing = {
        (row["campaign_id"], row["relation_id"]): row["standing"]
        for row in standing_rows
    }
    requests = {
        row["request_id"]: row.get("request_json")
        for row in request_rows
        if isinstance(row.get("request_json"), dict)
    }

    receipts_by_request: dict[str, list[dict[str, Any]]] = {}
    for row in prep_rows:
        receipt = row.get("receipt_json")
        if isinstance(receipt, dict):
            receipts_by_request.setdefault(str(receipt.get("request_id")), []).append(receipt)

    out: list[dict[str, Any]] = []
    for selection in current_selection:
        request_id = str(selection.get("request_id"))
        request = requests.get(request_id)
        if not isinstance(request, dict):
            out.append({
                "request_id": request_id,
                "status": "UNRESOLVED_REQUEST",
            })
            continue

        campaign_id = str(request.get("campaign_id"))
        campaign = campaign_map.get(campaign_id)
        if not isinstance(campaign, dict):
            out.append({
                "request_id": request_id,
                "campaign_id": campaign_id,
                "status": "UNRESOLVED_CAMPAIGN",
            })
            continue

        relation_id = str(request.get("unresolved_relation_id"))
        relation_standing = standing.get((campaign_id, relation_id), "UNKNOWN")
        basis_status = (
            "CURRENT"
            if list(campaign.get("basis_refs", [])) == comparison_basis_refs
            else "STALE"
        )
        receipts = receipts_by_request.get(request_id, [])
        current_receipts = [
            r for r in receipts
            if r.get("preparation_basis_refs") == comparison_basis_refs
        ]
        stale_receipts = [
            r for r in receipts
            if r.get("preparation_basis_refs") != comparison_basis_refs
        ]

        if basis_status == "STALE":
            readiness = "PREP_BLOCKED_STALE"
        elif relation_standing == "FRACTURED":
            readiness = "PREP_BLOCKED_OBSOLETE"
        elif relation_standing == "EARNED":
            readiness = "PREP_BLOCKED_RESOLVED"
        else:
            review_results = {
                r.get("review_disposition")
                for r in current_receipts
                if r.get("preparation_kind") == "REVIEW_RESULT"
                and r.get("mechanical_status") == "PASS"
                and r.get("review_disposition") in {"PASS", "OBJECTION"}
            }
            has_draft = any(
                r.get("preparation_kind") == "DRAFT_PACKET"
                and r.get("mechanical_status") == "PASS"
                for r in current_receipts
            )
            if review_results == {"PASS", "OBJECTION"}:
                readiness = "PREP_INCOMPLETE_REVIEW_CONFLICT"
            elif "OBJECTION" in review_results:
                readiness = "PREP_INCOMPLETE_REVIEW_OBJECTION"
            elif has_draft:
                readiness = "PREP_READY_FOR_AUTHORITY_REVIEW"
            else:
                readiness = "PREP_INCOMPLETE"

        out.append({
            "campaign_id": campaign_id,
            "request_id": request_id,
            "request_sha256": selection.get("request_sha256"),
            "relation_id": relation_id,
            "attention": "SELECTED",
            "request_applicability": basis_status,
            "standing": relation_standing,
            "readiness": readiness,
            "current_preparation_receipts": len(current_receipts),
            "stale_preparation_receipts": len(stale_receipts),
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
            "standing_effect": "NONE",
            "priority_effect": "NONE",
        })
    return out


def build_runtime_state(sources: RuntimeSources) -> dict[str, Any]:
    comparison_basis = resolve_comparison_basis(sources)

    controller, controller_status = _read_source(
        "controller",
        sources.controller_db,
        {
            "seats": "SELECT * FROM seats ORDER BY seat_id",
            "wakes": "SELECT * FROM wakes ORDER BY created_order, wake_id",
            "operator_invocations": "SELECT * FROM operator_invocations ORDER BY operator_invocation_id",
            "action_requests": "SELECT * FROM action_requests ORDER BY request_id",
            "receipts": "SELECT * FROM receipts ORDER BY receipt_id",
            "semantic_requests": "SELECT * FROM semantic_requests ORDER BY request_id",
            "semantic_proposals": "SELECT * FROM semantic_proposals ORDER BY proposal_id",
            "authority": "SELECT * FROM seat_operator_authority ORDER BY seat_id, operator_id",
        },
    )
    controller["seats"] = _decode_json_fields(controller.get("seats", []), ("working_state_json",))
    controller["operator_invocations"] = _decode_json_fields(
        controller.get("operator_invocations", []), ("args_json", "result_json")
    )
    controller["receipts"] = _decode_json_fields(controller.get("receipts", []), ("payload_json",))
    controller["semantic_proposals"] = _decode_json_fields(
        controller.get("semantic_proposals", []), ("payload_json",)
    )

    campaign, campaign_status = _read_source(
        "campaign",
        sources.campaign_db,
        {
            "campaigns": "SELECT * FROM campaigns ORDER BY campaign_id",
            "standing": "SELECT * FROM relation_standing ORDER BY campaign_id, relation_id",
            "requests": "SELECT * FROM envelope_requests ORDER BY request_id",
            "execution_receipts": "SELECT * FROM execution_receipts ORDER BY receipt_id",
        },
    )
    campaign["campaigns"] = _decode_json_fields(
        campaign.get("campaigns", []), ("campaign_json",)
    )
    campaign["requests"] = _decode_json_fields(
        campaign.get("requests", []), ("request_json",)
    )

    selection, selection_status = _read_source(
        "selection",
        sources.selection_db,
        {
            "events": "SELECT * FROM selection_events ORDER BY seq",
        },
    )
    selection["events"] = _decode_json_fields(selection.get("events", []), ("event_json",))
    current_selection = _current_selection(selection.get("events", []))

    preparation, preparation_status = _read_source(
        "preparation",
        sources.preparation_db,
        {
            "receipts": "SELECT * FROM preparation_receipts ORDER BY seq",
            "artifacts": "SELECT * FROM prep_artifacts ORDER BY artifact_ref",
        },
    )
    preparation["receipts"] = _decode_json_fields(
        preparation.get("receipts", []), ("receipt_json",)
    )
    preparation["artifacts"] = _decode_json_fields(
        preparation.get("artifacts", []), ("artifact_json",)
    )

    semantic, semantic_status = _read_source(
        "semantic",
        sources.semantic_db,
        {
            "resources": "SELECT * FROM model_resources ORDER BY resource_id",
            "leases": "SELECT * FROM model_leases ORDER BY lease_id",
            "runs": "SELECT request_id,request_sha256,status FROM semantic_runs ORDER BY request_id",
        },
    )

    active_seats = [
        seat for seat in controller.get("seats", [])
        if seat.get("occupancy_state") == "OCCUPIED"
    ]
    active_wake_ids = {
        seat.get("current_wake_id")
        for seat in active_seats
        if seat.get("current_wake_id")
    }
    active_wakes = [
        wake for wake in controller.get("wakes", [])
        if wake.get("wake_id") in active_wake_ids
    ]
    active_invocations = [
        invocation for invocation in controller.get("operator_invocations", [])
        if invocation.get("wake_id") in active_wake_ids
        and invocation.get("status") in {"ADMITTED", "EXECUTED"}
    ]
    active_leases = [
        lease for lease in semantic.get("leases", [])
        if lease.get("status") == "ACTIVE"
    ]

    readiness = _preparation_readiness(
        campaigns=campaign.get("campaigns", []),
        standing_rows=campaign.get("standing", []),
        request_rows=campaign.get("requests", []),
        current_selection=current_selection,
        prep_rows=preparation.get("receipts", []),
        comparison_basis_refs=comparison_basis,
    )

    source_status = [
        controller_status,
        campaign_status,
        selection_status,
        preparation_status,
        semantic_status,
    ]
    overall_status = (
        "AVAILABLE"
        if all(item["status"] in {"AVAILABLE", "NOT_CONFIGURED"} for item in source_status)
        and all(item["status"] == "AVAILABLE" for item in source_status if item["source"] != "semantic" or sources.semantic_db is not None)
        else "PARTIAL"
    )

    return {
        "schema": "live_runtime_projection_v0",
        "projection_status": overall_status,
        "projection_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
        "source_of_truth": "DURABLE_RUNTIME_STORES",
        "cross_store_atomicity": "NOT_ESTABLISHED",
        "comparison_basis": {
            "configured_refs": list(sources.comparison_basis_refs),
            "resolved_refs": comparison_basis,
            "authority_effect": "NONE",
        },
        "sources": source_status,
        "seats": controller.get("seats", []),
        "active_operations": {
            "occupied_seats": active_seats,
            "active_wakes": active_wakes,
            "active_operator_invocations": active_invocations,
        },
        "authority": {
            "seat_operator_authority": controller.get("authority", []),
            "action_requests": controller.get("action_requests", []),
        },
        "controller_receipts": controller.get("receipts", []),
        "semantic_requests": controller.get("semantic_requests", []),
        "semantic_proposals": controller.get("semantic_proposals", []),
        "campaigns": campaign.get("campaigns", []),
        "frontier": campaign.get("standing", []),
        "requests": campaign.get("requests", []),
        "execution_receipts": campaign.get("execution_receipts", []),
        "selection_history": selection.get("events", []),
        "current_selection": current_selection,
        "preparation_receipts": preparation.get("receipts", []),
        "preparation_artifacts": preparation.get("artifacts", []),
        "preparation_readiness": readiness,
        "model_resources": semantic.get("resources", []),
        "model_leases": semantic.get("leases", []),
        "active_model_leases": active_leases,
        "semantic_runs": semantic.get("runs", []),
        "standing_movement_history": {
            "status": "UNAVAILABLE_IN_CURRENT_CAMPAIGN_STORE",
            "current_standing_only": True,
        },
    }


def build_snapshot(sources: RuntimeSources) -> dict[str, Any]:
    state = build_runtime_state(sources)
    state_sha = _sha256(state)
    return {
        "snapshot_schema": "live_runtime_snapshot_v0",
        "state_sha256": state_sha,
        "observed_at": _utc_now(),
        "state": state,
    }


def iter_changed_snapshots(
    sources: RuntimeSources,
    *,
    poll_interval: float = 0.25,
    stop_event: threading.Event | None = None,
) -> Iterator[dict[str, Any]]:
    last_sha: str | None = None
    while stop_event is None or not stop_event.is_set():
        snapshot = build_snapshot(sources)
        if snapshot["state_sha256"] != last_sha:
            last_sha = snapshot["state_sha256"]
            yield snapshot
        if stop_event is not None and stop_event.is_set():
            break
        time.sleep(poll_interval)


class RuntimeProjectionServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        server_address: tuple[str, int],
        sources: RuntimeSources,
        poll_interval: float,
    ):
        super().__init__(server_address, RuntimeProjectionHandler)
        self.sources = sources
        self.poll_interval = poll_interval


class RuntimeProjectionHandler(BaseHTTPRequestHandler):
    server: RuntimeProjectionServer

    def _common_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/runtime/snapshot.json":
            payload = _canonical_bytes(build_snapshot(self.server.sources))
            self.send_response(200)
            self._common_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if path == "/runtime/events":
            self.send_response(200)
            self._common_headers()
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                for snapshot in iter_changed_snapshots(
                    self.server.sources,
                    poll_interval=self.server.poll_interval,
                ):
                    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
                    self.wfile.write(b"event: runtime_projection\n")
                    self.wfile.write(
                        f"id: {snapshot['state_sha256']}\n".encode("utf-8")
                    )
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                return
            return

        self.send_response(404)
        self._common_headers()
        self.end_headers()

    def _reject_write(self) -> None:
        self.send_response(405)
        self._common_headers()
        self.send_header("Allow", "GET")
        self.end_headers()

    do_POST = _reject_write
    do_PUT = _reject_write
    do_PATCH = _reject_write
    do_DELETE = _reject_write

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(
    sources: RuntimeSources,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    poll_interval: float = 0.25,
) -> None:
    server = RuntimeProjectionServer((host, port), sources, poll_interval)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _optional_path(value: str | None) -> Path | None:
    return Path(value).resolve() if value else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--controller-db")
    parser.add_argument("--campaign-db")
    parser.add_argument("--selection-db")
    parser.add_argument("--preparation-db")
    parser.add_argument("--semantic-db")
    parser.add_argument("--comparison-basis-ref", action="append", default=[])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--poll-interval", type=float, default=0.25)
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args(argv)

    sources = RuntimeSources(
        repo=Path(args.repo).resolve(),
        controller_db=_optional_path(args.controller_db),
        campaign_db=_optional_path(args.campaign_db),
        selection_db=_optional_path(args.selection_db),
        preparation_db=_optional_path(args.preparation_db),
        semantic_db=_optional_path(args.semantic_db),
        comparison_basis_refs=tuple(args.comparison_basis_ref),
    )

    if args.snapshot:
        print(json.dumps(build_snapshot(sources), indent=2, sort_keys=True))
        return 0

    serve(
        sources,
        host=args.host,
        port=args.port,
        poll_interval=args.poll_interval,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
