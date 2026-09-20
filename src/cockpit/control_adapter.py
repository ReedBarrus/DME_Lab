#!/usr/bin/env python3
"""COCKPIT_CONTROL_ADAPTER_001 — typed human control over already-qualified stores."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sqlite3
import subprocess
from typing import Any
from urllib.parse import urlparse

from tools.bounded_reentry_v0 import ReentryStore, build_wake_opportunity
from tools.development_campaign_v0 import CampaignStore, object_sha256
from tools.envelope_selection_v0 import (
    SELECT,
    SelectionStore,
    build_selection_event,
)
from tools.preparation_assignment_v0 import (
    ASSIGN,
    RELEASE,
    AssignmentStore,
    build_assignment_event,
)
from tools.preparation_v0 import PREP_KINDS, PreparationStore
from tools.wake_source_v0 import WakeSourceStore, build_manual_bell


VERBS = {"FOCUS", "ASSIGN", "RELEASE", "RING"}
EXECUTIVE = "REED"
_GESTURE = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")


class CockpitControlError(RuntimeError):
    pass


@dataclass(frozen=True)
class ControlSources:
    repo: Path
    campaign_db: Path
    selection_db: Path
    preparation_db: Path
    assignment_db: Path
    reentry_db: Path
    wake_source_db: Path
    comparison_basis_refs: tuple[str, ...]


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _repo_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise CockpitControlError(
            "cannot resolve repository HEAD: " + result.stderr.strip()
        )
    head = result.stdout.strip()
    if _SHA1.fullmatch(head) is None:
        raise CockpitControlError("repository HEAD is not a 40-hex commit")
    return head


def _load_request(store: CampaignStore, request_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(store.db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT request_json FROM envelope_requests WHERE request_id=?",
            (request_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise CockpitControlError(f"unknown request {request_id!r}")
    return json.loads(row["request_json"])


def _load_selection(store: SelectionStore, selection_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(store.db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT event_json FROM selection_events WHERE selection_id=?",
            (selection_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise CockpitControlError(f"unknown selection {selection_id!r}")
    return json.loads(row["event_json"])


class CockpitControlAdapter:
    """Separate write membrane. It has no controller-store dependency."""

    def __init__(self, sources: ControlSources):
        self.sources = sources
        for path in (
            sources.campaign_db,
            sources.selection_db,
            sources.preparation_db,
            sources.assignment_db,
            sources.reentry_db,
            sources.wake_source_db,
        ):
            if not path.exists():
                raise CockpitControlError(
                    f"control source must already exist: {path}"
                )

        self.campaign_store = CampaignStore(sources.campaign_db)
        self.selection_store = SelectionStore(
            self.campaign_store,
            sources.selection_db,
        )
        self.preparation_store = PreparationStore(
            self.campaign_store,
            self.selection_store,
            sources.preparation_db,
        )
        self.assignment_store = AssignmentStore(
            self.campaign_store,
            self.selection_store,
            self.preparation_store,
            sources.assignment_db,
        )
        self.reentry_store = ReentryStore(sources.reentry_db)
        self.wake_store = WakeSourceStore(
            assignment_store=self.assignment_store,
            reentry_store=self.reentry_store,
            db_path=sources.wake_source_db,
        )

    def current_basis_refs(self) -> list[str]:
        out: list[str] = []
        for ref in self.sources.comparison_basis_refs:
            if ref == "git:HEAD":
                out.append("git:" + _repo_head(self.sources.repo))
            else:
                out.append(ref)
        if not out:
            raise CockpitControlError("comparison basis refs are required")
        if len(out) != len(set(out)):
            raise CockpitControlError("comparison basis refs must be unique")
        return out

    def _gesture(self, intent: dict[str, Any]) -> str:
        gesture = intent.get("gesture_id")
        if not isinstance(gesture, str) or _GESTURE.fullmatch(gesture) is None:
            raise CockpitControlError(
                "gesture_id must be 1..96 safe identifier characters"
            )
        return gesture

    def _verb(self, intent: dict[str, Any]) -> str:
        verb = intent.get("verb")
        if verb not in VERBS:
            raise CockpitControlError(
                "v0 control verb must be one of FOCUS/ASSIGN/RELEASE/RING"
            )
        allowed = {
            "FOCUS": {"verb", "gesture_id", "campaign_id", "request_id", "reason"},
            "ASSIGN": {
                "verb", "gesture_id", "campaign_id", "request_id",
                "seat_id", "preparation_kind", "reason",
            },
            "RELEASE": {
                "verb", "gesture_id", "campaign_id", "assignment_id", "reason",
            },
            "RING": {
                "verb", "gesture_id", "campaign_id", "assignment_id", "reason",
            },
        }[str(verb)]
        extras = set(intent) - allowed
        required = allowed - {"reason"}
        missing = required - set(intent)
        if extras or missing:
            raise CockpitControlError(
                f"{verb} intent fields not exact; missing={sorted(missing)} extras={sorted(extras)}"
            )
        return str(verb)

    def _current_selection_for_request(
        self,
        campaign_id: str,
        request_id: str,
    ) -> dict[str, Any]:
        matches = [
            event
            for event in self.selection_store.current_set(campaign_id)
            if event["request_id"] == request_id
        ]
        if len(matches) != 1:
            raise CockpitControlError(
                f"request {request_id!r} has {len(matches)} current selections"
            )
        return matches[0]

    def _current_assignment(
        self,
        campaign_id: str,
        assignment_id: str,
    ) -> dict[str, Any]:
        matches: list[dict[str, Any]] = []
        for assigned, released in self.assignment_store._assigned_lineage(
            campaign_id
        ):
            if (
                released is None
                and assigned.get("assignment_id") == assignment_id
            ):
                matches.append(assigned)
        if len(matches) != 1:
            raise CockpitControlError(
                f"assignment {assignment_id!r} is not exactly one current allocation"
            )
        return matches[0]

    def _git_basis(self, basis_refs: list[str]) -> str:
        git_refs = [
            ref.removeprefix("git:")
            for ref in basis_refs
            if isinstance(ref, str)
            and ref.startswith("git:")
            and _SHA1.fullmatch(ref.removeprefix("git:")) is not None
        ]
        if len(git_refs) != 1:
            raise CockpitControlError(
                "RING requires exactly one 40-hex git basis ref"
            )
        return git_refs[0]

    def build_preview(self, intent: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(intent, dict):
            raise CockpitControlError("control intent must be an object")
        verb = self._verb(intent)
        gesture = self._gesture(intent)
        basis = self.current_basis_refs()
        reason = intent.get("reason")
        if reason is not None and not isinstance(reason, str):
            raise CockpitControlError("reason must be text or null")

        objects: list[dict[str, Any]] = []
        normalized: dict[str, Any] = {
            "verb": verb,
            "gesture_id": gesture,
            "reason": reason,
        }

        if verb == "FOCUS":
            campaign_id = str(intent.get("campaign_id") or "")
            request_id = str(intent.get("request_id") or "")
            campaign = self.campaign_store.get_campaign(campaign_id)
            request = _load_request(self.campaign_store, request_id)
            if request["campaign_id"] != campaign_id:
                raise CockpitControlError("request/campaign mismatch")
            if any(
                item["request_id"] == request_id
                for item in self.selection_store.current_set(campaign_id)
            ):
                raise CockpitControlError("request is already currently selected")
            event = build_selection_event(
                campaign=campaign,
                request=request,
                selection_id=f"CCA-S-{gesture}",
                basis_refs=basis,
                kind=SELECT,
                reason=reason,
            )
            objects.append(event)
            normalized.update(
                {"campaign_id": campaign_id, "request_id": request_id}
            )

        elif verb == "ASSIGN":
            campaign_id = str(intent.get("campaign_id") or "")
            request_id = str(intent.get("request_id") or "")
            seat_id = str(intent.get("seat_id") or "")
            preparation_kind = str(intent.get("preparation_kind") or "")
            if not seat_id:
                raise CockpitControlError("seat_id required")
            if preparation_kind not in PREP_KINDS:
                raise CockpitControlError("unsupported preparation kind")
            campaign = self.campaign_store.get_campaign(campaign_id)
            request = _load_request(self.campaign_store, request_id)
            if request["campaign_id"] != campaign_id:
                raise CockpitControlError("request/campaign mismatch")
            selection = self._current_selection_for_request(
                campaign_id,
                request_id,
            )
            event = build_assignment_event(
                campaign=campaign,
                request=request,
                selection=selection,
                assignment_id=f"CCA-A-{gesture}",
                seat_id=seat_id,
                preparation_kind=preparation_kind,
                assigned_at_basis_refs=basis,
                kind=ASSIGN,
                reason=reason,
            )
            projection = self.assignment_store.projection(
                campaign_id,
                current_basis_refs=basis,
            )
            if any(
                row["request_id"] == request_id
                and row["request_sha256"] == event["request_sha256"]
                and row["seat_id"] == seat_id
                and row["preparation_kind"] == preparation_kind
                and row["assignment_state"] != "RELEASED"
                for row in projection["assignment_projection"]
            ):
                raise CockpitControlError(
                    "exact seat/request/preparation allocation already exists"
                )
            objects.append(event)
            normalized.update(
                {
                    "campaign_id": campaign_id,
                    "request_id": request_id,
                    "seat_id": seat_id,
                    "preparation_kind": preparation_kind,
                }
            )

        elif verb == "RELEASE":
            campaign_id = str(intent.get("campaign_id") or "")
            assignment_id = str(intent.get("assignment_id") or "")
            assigned = self._current_assignment(campaign_id, assignment_id)
            campaign = self.campaign_store.get_campaign(campaign_id)
            request = _load_request(
                self.campaign_store,
                assigned["request_id"],
            )
            selection = _load_selection(
                self.selection_store,
                assigned["selection_ref"],
            )
            event = build_assignment_event(
                campaign=campaign,
                request=request,
                selection=selection,
                assignment_id=f"CCA-R-{gesture}",
                seat_id=assigned["seat_id"],
                preparation_kind=assigned["preparation_kind"],
                assigned_at_basis_refs=basis,
                kind=RELEASE,
                reason=reason,
            )
            objects.append(event)
            normalized.update(
                {
                    "campaign_id": campaign_id,
                    "assignment_id": assignment_id,
                }
            )

        elif verb == "RING":
            campaign_id = str(intent.get("campaign_id") or "")
            assignment_id = str(intent.get("assignment_id") or "")
            assigned = self._current_assignment(campaign_id, assignment_id)
            projection = self.assignment_store.projection(
                campaign_id,
                current_basis_refs=basis,
            )
            current = next(
                (
                    row
                    for row in projection["assignment_projection"]
                    if row["assignment_id"] == assignment_id
                    and row["assignment_sha256"] == object_sha256(assigned)
                ),
                None,
            )
            if (
                current is None
                or current["assignment_state"] != "OUTSTANDING"
                or current["wake_eligible"] is not True
            ):
                state = (
                    current["assignment_state"]
                    if current is not None
                    else "MISSING"
                )
                raise CockpitControlError(
                    f"assignment is not ring-eligible: {state}"
                )
            if assigned["preparation_kind"] != "RESOLVE_REFS":
                raise CockpitControlError(
                    "v0 RING only supports RESOLVE_REFS reentry"
                )

            campaign = self.campaign_store.get_campaign(campaign_id)
            request = _load_request(
                self.campaign_store,
                assigned["request_id"],
            )
            selection = _load_selection(
                self.selection_store,
                assigned["selection_ref"],
            )
            bell = build_manual_bell(
                assignment=assigned,
                bell_id=f"CCA-B-{gesture}",
                bell_basis_refs=basis,
            )
            opportunity_basis = self._git_basis(basis)
            opportunity = build_wake_opportunity(
                campaign=campaign,
                seat_id=assigned["seat_id"],
                opportunity_id=f"CCA-W-{gesture}",
                opportunity_basis=opportunity_basis,
                max_consumed_events=8,
                request=request,
                selection=selection,
                preparation_kind=assigned["preparation_kind"],
                assignment=assigned,
                manual_bell=bell,
                wake_source_kind="MANUAL_BELL",
            )
            objects.extend([bell, opportunity])
            normalized.update(
                {
                    "campaign_id": campaign_id,
                    "assignment_id": assignment_id,
                }
            )

        preview = {
            "schema": "cockpit_control_preview_v0",
            "adapter_id": "COCKPIT_CONTROL_ADAPTER_001",
            "verb": verb,
            "gesture_id": gesture,
            "intent": normalized,
            "basis_refs": basis,
            "durable_objects": objects,
            "declared_effects": {
                "direct_controller_mutation": "NONE",
                "priority_effect": "NONE",
                "authority_effect": "NONE",
                "standing_effect": "NONE",
                "scheduler_effect": "NONE",
            },
            "confirmation_required": True,
        }
        return {
            "preview": preview,
            "preview_sha256": _sha(preview),
        }

    def commit(
        self,
        *,
        preview: dict[str, Any],
        preview_sha256: str,
        confirmed_by: str,
    ) -> dict[str, Any]:
        if confirmed_by != EXECUTIVE:
            raise CockpitControlError("v0 confirmation must be REED")
        if not isinstance(preview, dict):
            raise CockpitControlError("preview must be an object")
        if _sha(preview) != preview_sha256:
            raise CockpitControlError("preview identity mismatch")

        fresh = self.build_preview(preview.get("intent", {}))
        if (
            fresh["preview_sha256"] != preview_sha256
            or fresh["preview"] != preview
        ):
            raise CockpitControlError(
                "preview is stale; re-preview exact current object before commit"
            )

        verb = preview["verb"]
        basis = preview["basis_refs"]
        objects = preview["durable_objects"]

        if verb == "FOCUS":
            store_result = self.selection_store.append(objects[0])
            retained = [
                {
                    "kind": objects[0]["schema"],
                    "id": objects[0]["selection_id"],
                    "sha256": object_sha256(objects[0]),
                }
            ]

        elif verb in {"ASSIGN", "RELEASE"}:
            store_result = self.assignment_store.append(
                objects[0],
                current_basis_refs=basis,
            )
            retained = [
                {
                    "kind": objects[0]["schema"],
                    "id": objects[0]["assignment_id"],
                    "sha256": object_sha256(objects[0]),
                }
            ]

        elif verb == "RING":
            bell, opportunity = objects
            campaign = self.campaign_store.get_campaign(bell["campaign_id"])
            request = _load_request(
                self.campaign_store,
                bell["request_id"],
            )
            selection = _load_selection(
                self.selection_store,
                bell["selection_ref"],
            )
            store_result = self.wake_store.emit(
                bell,
                current_basis_refs=basis,
                opportunity_id=opportunity["opportunity_id"],
                opportunity_basis=opportunity["opportunity_basis"],
                campaign=campaign,
                request=request,
                selection=selection,
                max_consumed_events=opportunity["max_consumed_events"],
            )
            if (
                store_result["opportunity_sha256"]
                != object_sha256(opportunity)
            ):
                raise CockpitControlError(
                    "retained wake opportunity differs from previewed bytes"
                )
            retained = [
                {
                    "kind": bell["schema"],
                    "id": bell["bell_id"],
                    "sha256": object_sha256(bell),
                },
                {
                    "kind": opportunity["schema"],
                    "id": opportunity["opportunity_id"],
                    "sha256": object_sha256(opportunity),
                },
            ]
        else:
            raise CockpitControlError("unsupported commit verb")

        return {
            "schema": "cockpit_control_result_v0",
            "adapter_id": "COCKPIT_CONTROL_ADAPTER_001",
            "verb": verb,
            "gesture_id": preview["gesture_id"],
            "preview_sha256": preview_sha256,
            "confirmed_by": confirmed_by,
            "retained_objects": retained,
            "store_result": store_result,
            "direct_controller_mutation": "NONE",
            "priority_effect": "NONE",
            "authority_effect": "NONE",
            "standing_effect": "NONE",
            "scheduler_effect": "NONE",
        }

    def state(self) -> dict[str, Any]:
        conn = sqlite3.connect(self.campaign_store.db_path)
        conn.row_factory = sqlite3.Row
        try:
            campaigns = [
                json.loads(row["campaign_json"])
                for row in conn.execute(
                    "SELECT campaign_json FROM campaigns ORDER BY campaign_id"
                ).fetchall()
            ]
            requests = [
                json.loads(row["request_json"])
                for row in conn.execute(
                    "SELECT request_json FROM envelope_requests ORDER BY request_id"
                ).fetchall()
            ]
        finally:
            conn.close()

        basis = self.current_basis_refs()
        selection: list[dict[str, Any]] = []
        assignments: list[dict[str, Any]] = []
        for campaign in campaigns:
            cid = campaign["campaign_id"]
            selection.extend(self.selection_store.current_set(cid))
            assignments.extend(
                self.assignment_store.projection(
                    cid,
                    current_basis_refs=basis,
                )["assignment_projection"]
            )

        return {
            "schema": "cockpit_control_state_v0",
            "basis_refs": basis,
            "campaigns": [
                {
                    "campaign_id": c["campaign_id"],
                    "objective": c.get("objective"),
                }
                for c in campaigns
            ],
            "requests": [
                {
                    "request_id": r["request_id"],
                    "campaign_id": r["campaign_id"],
                    "relation_id": r.get("unresolved_relation_id"),
                }
                for r in requests
            ],
            "current_selection": selection,
            "assignment_projection": assignments,
            "verbs": sorted(VERBS),
            "direct_controller_mutation": "NONE",
            "priority_effect": "NONE",
            "authority_effect": "NONE",
        }


def _json_response(
    handler: BaseHTTPRequestHandler,
    status: int,
    payload: dict[str, Any],
) -> None:
    body = _canonical(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(adapter: CockpitControlAdapter):
    class ControlHandler(BaseHTTPRequestHandler):
        def do_OPTIONS(self) -> None:  # noqa: N802
            _json_response(self, 200, {"status": "OK"})

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/control/health":
                _json_response(
                    self,
                    200,
                    {
                        "status": "AVAILABLE",
                        "adapter_id": "COCKPIT_CONTROL_ADAPTER_001",
                        "direct_controller_mutation": "NONE",
                    },
                )
                return
            if path == "/control/state":
                try:
                    _json_response(self, 200, adapter.state())
                except Exception as exc:
                    _json_response(
                        self,
                        409,
                        {
                            "status": "REJECTED",
                            "error": f"{type(exc).__name__}: {exc}",
                        },
                    )
                return
            _json_response(self, 404, {"status": "NOT_FOUND"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                _json_response(self, 400, {"status": "INVALID_LENGTH"})
                return
            if length <= 0 or length > 1_000_000:
                _json_response(self, 400, {"status": "INVALID_BODY_SIZE"})
                return
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                if path == "/control/preview":
                    result = adapter.build_preview(body)
                elif path == "/control/commit":
                    result = adapter.commit(
                        preview=body.get("preview"),
                        preview_sha256=str(body.get("preview_sha256") or ""),
                        confirmed_by=str(body.get("confirmed_by") or ""),
                    )
                else:
                    _json_response(self, 404, {"status": "NOT_FOUND"})
                    return
                _json_response(self, 200, result)
            except Exception as exc:
                _json_response(
                    self,
                    409,
                    {
                        "status": "REJECTED",
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                )

        def log_message(self, format: str, *args: Any) -> None:
            return

    return ControlHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--campaign-db", required=True)
    parser.add_argument("--selection-db", required=True)
    parser.add_argument("--preparation-db", required=True)
    parser.add_argument("--assignment-db", required=True)
    parser.add_argument("--reentry-db", required=True)
    parser.add_argument("--wake-source-db", required=True)
    parser.add_argument("--basis-ref", action="append", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    args = parser.parse_args(argv)

    sources = ControlSources(
        repo=Path(args.repo).resolve(),
        campaign_db=Path(args.campaign_db).resolve(),
        selection_db=Path(args.selection_db).resolve(),
        preparation_db=Path(args.preparation_db).resolve(),
        assignment_db=Path(args.assignment_db).resolve(),
        reentry_db=Path(args.reentry_db).resolve(),
        wake_source_db=Path(args.wake_source_db).resolve(),
        comparison_basis_refs=tuple(args.basis_ref),
    )
    adapter = CockpitControlAdapter(sources)
    server = ThreadingHTTPServer(
        (args.host, args.port),
        make_handler(adapter),
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
