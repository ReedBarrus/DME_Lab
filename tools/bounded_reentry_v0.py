#!/usr/bin/env python3
"""BOUNDED_REENTRY_001 — one wake, at most one bounded preparation unit."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
from typing import Any, Callable

from tools.development_campaign_v0 import CampaignStore, object_sha256
from tools.envelope_selection_v0 import SelectionStore
from tools.goblin_pool import GoblinPool
from tools.preparation_v0 import PreparationStore, build_receipt

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "bounded_reentry_v0.sql"
_SHA1 = re.compile(r"^[0-9a-f]{40}$")


class BoundedReentryError(RuntimeError):
    pass


class InjectedReentryCrash(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise BoundedReentryError("cannot resolve Git HEAD: " + result.stderr.strip())
    head = result.stdout.strip()
    if _SHA1.fullmatch(head) is None:
        raise BoundedReentryError("Git HEAD is not a 40-hex commit")
    return head


def _load_request(campaign_store: CampaignStore, request_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(campaign_store.db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT request_json FROM envelope_requests WHERE request_id=?",
            (request_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise BoundedReentryError(f"unknown request {request_id!r}")
    return json.loads(row["request_json"])


def _load_selection(selection_store: SelectionStore, selection_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(selection_store.db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT event_json FROM selection_events WHERE selection_id=?",
            (selection_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise BoundedReentryError(f"unknown selection {selection_id!r}")
    return json.loads(row["event_json"])


def _current_basis(campaign: dict[str, Any], current_head: str) -> list[str]:
    result: list[str] = []
    replaced = False
    for ref in campaign["basis_refs"]:
        if isinstance(ref, str) and ref.startswith("git:"):
            result.append("git:" + current_head)
            replaced = True
        else:
            result.append(ref)
    if not replaced:
        result.append("git:" + current_head)
    return result


def build_wake_opportunity(
    *,
    campaign: dict[str, Any],
    seat_id: str,
    opportunity_id: str,
    opportunity_basis: str,
    max_consumed_events: int = 8,
    request: dict[str, Any] | None = None,
    selection: dict[str, Any] | None = None,
    preparation_kind: str | None = None,
) -> dict[str, Any]:
    if not opportunity_id or not seat_id:
        raise BoundedReentryError("opportunity_id and seat_id are required")
    if _SHA1.fullmatch(opportunity_basis) is None:
        raise BoundedReentryError("opportunity_basis must be a 40-hex Git commit")
    if not isinstance(max_consumed_events, int) or not 0 <= max_consumed_events <= 32:
        raise BoundedReentryError("max_consumed_events must be 0..32")
    if request is None:
        if selection is not None or preparation_kind is not None:
            raise BoundedReentryError("no-target opportunity cannot bind selection/preparation")
        request_id = request_sha = selection_ref = selection_sha = None
    else:
        if selection is None or preparation_kind != "RESOLVE_REFS":
            raise BoundedReentryError("targeted v0 opportunity requires selection + RESOLVE_REFS")
        if request["campaign_id"] != campaign["campaign_id"]:
            raise BoundedReentryError("request/campaign mismatch")
        if selection["request_id"] != request["request_id"]:
            raise BoundedReentryError("selection/request mismatch")
        if selection["request_sha256"] != object_sha256(request):
            raise BoundedReentryError("selection does not bind exact request bytes")
        request_id = request["request_id"]
        request_sha = object_sha256(request)
        selection_ref = selection["selection_id"]
        selection_sha = object_sha256(selection)
    return {
        "schema": "wake_opportunity_v0",
        "opportunity_id": opportunity_id,
        "seat_id": seat_id,
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": object_sha256(campaign),
        "request_id": request_id,
        "request_sha256": request_sha,
        "selection_ref": selection_ref,
        "selection_sha256": selection_sha,
        "preparation_kind": preparation_kind,
        "opportunity_basis": opportunity_basis,
        "max_consumed_events": max_consumed_events,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scheduler_effect": "NONE",
    }


class ReentryStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def post_opportunity(self, opportunity: dict[str, Any]) -> dict[str, Any]:
        required = {
            "schema","opportunity_id","seat_id","campaign_id","campaign_sha256",
            "request_id","request_sha256","selection_ref","selection_sha256",
            "preparation_kind","opportunity_basis","max_consumed_events",
            "authority_effect","execution_effect","scheduler_effect",
        }
        if set(opportunity) != required or opportunity["schema"] != "wake_opportunity_v0":
            raise BoundedReentryError("wake opportunity fields are not exact")
        if opportunity["authority_effect"] != "NONE" or opportunity["execution_effect"] != "NONE" or opportunity["scheduler_effect"] != "NONE":
            raise BoundedReentryError("wake opportunity may not grant authority/execution/scheduling")
        digest = _sha(opportunity)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT opportunity_sha256 FROM wake_opportunities WHERE opportunity_id=?",
                (opportunity["opportunity_id"],),
            ).fetchone()
            if row is not None:
                if row["opportunity_sha256"] != digest:
                    raise BoundedReentryError("opportunity_id reused with different bytes")
                return {"idempotent_replay": True, "opportunity_id": opportunity["opportunity_id"]}
            conn.execute(
                """
                INSERT INTO wake_opportunities(
                    opportunity_id,opportunity_sha256,seat_id,campaign_id,
                    request_id,request_sha256,selection_ref,selection_sha256,
                    preparation_kind,opportunity_basis,max_consumed_events,opportunity_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    opportunity["opportunity_id"],digest,opportunity["seat_id"],
                    opportunity["campaign_id"],opportunity["request_id"],
                    opportunity["request_sha256"],opportunity["selection_ref"],
                    opportunity["selection_sha256"],opportunity["preparation_kind"],
                    opportunity["opportunity_basis"],opportunity["max_consumed_events"],
                    _canonical(opportunity),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {"idempotent_replay": False, "opportunity_id": opportunity["opportunity_id"]}

    def opportunity(self, opportunity_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT opportunity_json FROM wake_opportunities WHERE opportunity_id=?",
                (opportunity_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise BoundedReentryError(f"unknown wake opportunity {opportunity_id!r}")
        return json.loads(row["opportunity_json"])

    def append_event(self, *, opportunity_id: str, wake_id: str, seat_id: str, kind: str, payload: dict[str, Any]) -> str:
        conn = self._connect()
        try:
            next_seq = conn.execute(
                "SELECT COALESCE(MAX(seq),0)+1 FROM reentry_events"
            ).fetchone()[0]
            event_id = f"RE-{int(next_seq):06d}"
            conn.execute(
                """
                INSERT INTO reentry_events(event_id,opportunity_id,wake_id,seat_id,event_kind,payload_json)
                VALUES(?,?,?,?,?,?)
                """,
                (event_id, opportunity_id, wake_id, seat_id, kind, _canonical(payload)),
            )
            conn.commit()
            return event_id
        finally:
            conn.close()

    def events(self, opportunity_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM reentry_events WHERE opportunity_id=? ORDER BY seq",
                (opportunity_id,),
            ).fetchall()
        finally:
            conn.close()
        return [
            {
                "seq": row["seq"],
                "event_id": row["event_id"],
                "opportunity_id": row["opportunity_id"],
                "wake_id": row["wake_id"],
                "seat_id": row["seat_id"],
                "event_kind": row["event_kind"],
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def receipt(self, opportunity_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT receipt_json FROM reentry_receipts WHERE opportunity_id=?",
                (opportunity_id,),
            ).fetchone()
        finally:
            conn.close()
        return json.loads(row["receipt_json"]) if row is not None else None

    def retain_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        required = {
            "schema","receipt_id","opportunity_id","wake_id","seat_id","outcome",
            "preparation_receipt_id","controller_receipt_id","work_units_performed",
            "occupancy_released","authority_effect","execution_authority_effect",
            "scheduler_effect",
        }
        if set(receipt) != required or receipt["schema"] != "bounded_reentry_receipt_v0":
            raise BoundedReentryError("reentry receipt fields are not exact")
        if receipt["authority_effect"] != "NONE" or receipt["execution_authority_effect"] != "NONE" or receipt["scheduler_effect"] != "NONE":
            raise BoundedReentryError("reentry receipt may not create authority/scheduling")
        if receipt["work_units_performed"] not in {0, 1}:
            raise BoundedReentryError("one wake may retain at most one work unit")
        digest = _sha(receipt)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT receipt_sha256 FROM reentry_receipts WHERE opportunity_id=?",
                (receipt["opportunity_id"],),
            ).fetchone()
            if row is not None:
                if row["receipt_sha256"] != digest:
                    raise BoundedReentryError("opportunity already has different terminal receipt")
                return {"idempotent_replay": True, "receipt_id": receipt["receipt_id"]}
            conn.execute(
                """
                INSERT INTO reentry_receipts(
                    receipt_id,receipt_sha256,opportunity_id,wake_id,seat_id,outcome,
                    preparation_receipt_id,controller_receipt_id,receipt_json
                ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    receipt["receipt_id"],digest,receipt["opportunity_id"],
                    receipt["wake_id"],receipt["seat_id"],receipt["outcome"],
                    receipt["preparation_receipt_id"],receipt["controller_receipt_id"],
                    _canonical(receipt),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {"idempotent_replay": False, "receipt_id": receipt["receipt_id"]}


class BoundedReentryRunner:
    def __init__(
        self,
        *,
        repo: str | Path,
        pool: GoblinPool,
        campaign_store: CampaignStore,
        selection_store: SelectionStore,
        preparation_store: PreparationStore,
        reentry_store: ReentryStore,
    ):
        self.repo = Path(repo).resolve()
        self.pool = pool
        self.campaign_store = campaign_store
        self.selection_store = selection_store
        self.preparation_store = preparation_store
        self.reentry_store = reentry_store

    def _terminal(
        self,
        *,
        opportunity: dict[str, Any],
        wake_id: str,
        outcome: str,
        preparation_receipt_id: str | None,
        controller_receipt_id: str | None,
        work_units: int,
        occupancy_released: bool,
    ) -> dict[str, Any]:
        receipt = {
            "schema": "bounded_reentry_receipt_v0",
            "receipt_id": f"BRR-{opportunity['opportunity_id']}",
            "opportunity_id": opportunity["opportunity_id"],
            "wake_id": wake_id,
            "seat_id": opportunity["seat_id"],
            "outcome": outcome,
            "preparation_receipt_id": preparation_receipt_id,
            "controller_receipt_id": controller_receipt_id,
            "work_units_performed": work_units,
            "occupancy_released": occupancy_released,
            "authority_effect": "NONE",
            "execution_authority_effect": "NONE",
            "scheduler_effect": "NONE",
        }
        self.reentry_store.retain_receipt(receipt)
        return receipt

    def _commit_non_effect(
        self,
        *,
        opportunity: dict[str, Any],
        wake_id: str,
        start: dict[str, Any],
        consumed: list[str],
        outcome: str,
    ) -> dict[str, Any]:
        state = copy.deepcopy(start["working_state"])
        state["last_reentry"] = {
            "opportunity_id": opportunity["opportunity_id"],
            "wake_id": wake_id,
            "outcome": outcome,
            "work_units_performed": 0,
        }
        commit = self.pool.commit_transition(
            wake_id,
            transition_id=f"T-{opportunity['opportunity_id']}",
            output_id=f"O-{opportunity['opportunity_id']}",
            output_kind="BOUNDED_REENTRY_RESULT",
            output_payload={
                "outcome": outcome,
                "preparation_receipt_id": None,
                "authority_effect": "NONE",
                "execution_authority_effect": "NONE",
            },
            consumed_event_ids=consumed,
            resulting_working_state=state,
        )
        self.reentry_store.append_event(
            opportunity_id=opportunity["opportunity_id"],
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="SUCCESSOR_COMMITTED",
            payload={"outcome": outcome, "controller_receipt_id": commit["receipt_id"]},
        )
        self.reentry_store.append_event(
            opportunity_id=opportunity["opportunity_id"],
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="DORMANT",
            payload={"occupancy_state": "AVAILABLE"},
        )
        return self._terminal(
            opportunity=opportunity,
            wake_id=wake_id,
            outcome=outcome,
            preparation_receipt_id=None,
            controller_receipt_id=commit["receipt_id"],
            work_units=0,
            occupancy_released=True,
        )

    def run_once(
        self,
        opportunity_id: str,
        *,
        inject_crash_at: str | None = None,
        phase_hook: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        prior = self.reentry_store.receipt(opportunity_id)
        if prior is not None:
            result = dict(prior)
            result["idempotent_replay"] = True
            return result

        opportunity = self.reentry_store.opportunity(opportunity_id)
        campaign = self.campaign_store.get_campaign(opportunity["campaign_id"])
        if opportunity["campaign_sha256"] != object_sha256(campaign):
            raise BoundedReentryError("wake opportunity campaign identity mismatch")

        request = None
        selection = None
        if opportunity["request_id"] is not None:
            request = _load_request(self.campaign_store, opportunity["request_id"])
            selection = _load_selection(self.selection_store, opportunity["selection_ref"])
            if opportunity["request_sha256"] != object_sha256(request):
                raise BoundedReentryError("wake opportunity request identity mismatch")
            if opportunity["selection_sha256"] != object_sha256(selection):
                raise BoundedReentryError("wake opportunity selection identity mismatch")

        wake_id = f"W-{opportunity_id}"
        start = self.pool.start_wake(opportunity["seat_id"], wake_id)
        if start["status"] == "OCCUPANCY_CONFLICT":
            self.reentry_store.append_event(
                opportunity_id=opportunity_id,
                wake_id=wake_id,
                seat_id=opportunity["seat_id"],
                kind="WAKE_BLOCKED",
                payload={"classification": "OCCUPANCY_CONFLICT"},
            )
            return self._terminal(
                opportunity=opportunity,
                wake_id=wake_id,
                outcome="OCCUPANCY_CONFLICT",
                preparation_receipt_id=None,
                controller_receipt_id=None,
                work_units=0,
                occupancy_released=False,
            )
        if start["status"] not in {"STARTED", "COMMITTED"}:
            raise BoundedReentryError(f"unsupported wake status {start['status']!r}")

        self.reentry_store.append_event(
            opportunity_id=opportunity_id,
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="WAKE_ACCEPTED",
            payload={
                "basis_version": start["basis_version"],
                "basis_cursor_event_id": start["basis_cursor_event_id"],
            },
        )
        if phase_hook:
            phase_hook("WAKE_ACCEPTED", {"wake_id": wake_id, "start": start})

        current_head = _git_head(self.repo)
        eligible_events = self.pool.eligible_events(opportunity["seat_id"])
        consumed = [
            event["event_id"]
            for event in eligible_events[: opportunity["max_consumed_events"]]
        ]
        self.reentry_store.append_event(
            opportunity_id=opportunity_id,
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="RECONSTRUCTED",
            payload={
                "seat_version": start["basis_version"],
                "cursor_event_id": start["basis_cursor_event_id"],
                "eligible_event_count": len(eligible_events),
                "consumed_event_ids": consumed,
                "world_basis": current_head,
            },
        )
        if phase_hook:
            phase_hook("RECONSTRUCTED", {"world_basis": current_head, "consumed": consumed})

        if inject_crash_at == "BEFORE_UNIT":
            raise InjectedReentryCrash("synthetic crash before bounded unit")

        current_basis = _current_basis(campaign, current_head)

        if request is None:
            return self._commit_non_effect(
                opportunity=opportunity,
                wake_id=wake_id,
                start=start,
                consumed=consumed,
                outcome="NO_WORK",
            )

        selection_projection = self.selection_store.projection(
            campaign["campaign_id"],
            current_basis_refs=current_basis,
        )
        selected = next(
            (
                item for item in selection_projection["current_selection_set"]
                if item["request_id"] == request["request_id"]
                and item["request_sha256"] == object_sha256(request)
            ),
            None,
        )

        if selected is None:
            return self._commit_non_effect(
                opportunity=opportunity,
                wake_id=wake_id,
                start=start,
                consumed=consumed,
                outcome="BLOCKED_NOT_SELECTED",
            )
        if selected["request_applicability"] == "STALE":
            return self._commit_non_effect(
                opportunity=opportunity,
                wake_id=wake_id,
                start=start,
                consumed=consumed,
                outcome="BLOCKED_STALE",
            )
        if selected["developmental_relevance"] == "OBSOLETE_FRACTURED":
            return self._commit_non_effect(
                opportunity=opportunity,
                wake_id=wake_id,
                start=start,
                consumed=consumed,
                outcome="BLOCKED_OBSOLETE",
            )
        if selected["developmental_relevance"] == "RESOLVED_EARNED":
            return self._commit_non_effect(
                opportunity=opportunity,
                wake_id=wake_id,
                start=start,
                consumed=consumed,
                outcome="BLOCKED_RESOLVED",
            )
        if selected["preparation"] != "ELIGIBLE_FOR_PACKET_PREPARATION":
            raise BoundedReentryError("selected request is not preparation eligible")

        self.reentry_store.append_event(
            opportunity_id=opportunity_id,
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="UNIT_STARTED",
            payload={"preparation_kind": opportunity["preparation_kind"], "request_id": request["request_id"]},
        )
        if phase_hook:
            phase_hook("UNIT_STARTED", {"request_id": request["request_id"]})

        prep_id = f"BRP-{opportunity_id}"
        prep = build_receipt(
            campaign=campaign,
            request=request,
            selection=selection,
            preparation_id=prep_id,
            prepared_by=opportunity["seat_id"],
            preparation_kind="RESOLVE_REFS",
            preparation_basis_refs=current_basis,
            input_refs=[f"campaign://{campaign['campaign_id']}@{object_sha256(campaign)}", f"request://{request['request_id']}@{object_sha256(request)}"],
            output_refs=[f"selection://{selection['selection_id']}@{object_sha256(selection)}"],
            mechanical_status="PASS",
        )
        self.preparation_store.append(prep, current_basis_refs=current_basis)
        self.reentry_store.append_event(
            opportunity_id=opportunity_id,
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="UNIT_RECEIPT_EMITTED",
            payload={"preparation_receipt_id": prep_id},
        )
        if phase_hook:
            phase_hook("UNIT_RECEIPT_EMITTED", {"preparation_receipt_id": prep_id})

        if inject_crash_at == "AFTER_UNIT_BEFORE_COMMIT":
            raise InjectedReentryCrash("synthetic crash after prep receipt before seat commit")

        if phase_hook:
            phase_hook("BEFORE_SUCCESSOR", {"wake_basis": current_head})

        head_after = _git_head(self.repo)
        if head_after != current_head:
            self.reentry_store.append_event(
                opportunity_id=opportunity_id,
                wake_id=wake_id,
                seat_id=opportunity["seat_id"],
                kind="WAKE_ABORTED",
                payload={
                    "classification": "STALE_AFTER_EFFECT",
                    "wake_basis": current_head,
                    "current_basis": head_after,
                    "preparation_receipt_id": prep_id,
                },
            )
            recovery = self.pool.recover_lease(
                opportunity["seat_id"], wake_id, reason="STALE_AFTER_EFFECT"
            )
            self.reentry_store.append_event(
                opportunity_id=opportunity_id,
                wake_id=wake_id,
                seat_id=opportunity["seat_id"],
                kind="DORMANT",
                payload={"occupancy_state": self.pool.seat_snapshot(opportunity["seat_id"])["occupancy_state"]},
            )
            return self._terminal(
                opportunity=opportunity,
                wake_id=wake_id,
                outcome="STALE_AFTER_EFFECT",
                preparation_receipt_id=prep_id,
                controller_receipt_id=None,
                work_units=1,
                occupancy_released=recovery["status"] in {"RECOVERED", "NO_RECOVERY_NEEDED"},
            )

        state = copy.deepcopy(start["working_state"])
        state["last_reentry"] = {
            "opportunity_id": opportunity_id,
            "wake_id": wake_id,
            "outcome": "UNIT_COMPLETED",
            "preparation_receipt_id": prep_id,
            "work_units_performed": 1,
        }
        commit = self.pool.commit_transition(
            wake_id,
            transition_id=f"T-{opportunity_id}",
            output_id=f"O-{opportunity_id}",
            output_kind="BOUNDED_REENTRY_PREPARATION",
            output_payload={
                "preparation_receipt_id": prep_id,
                "request_id": request["request_id"],
                "world_basis": current_head,
                "authority_effect": "NONE",
                "execution_authority_effect": "NONE",
            },
            consumed_event_ids=consumed,
            resulting_working_state=state,
        )
        self.reentry_store.append_event(
            opportunity_id=opportunity_id,
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="SUCCESSOR_COMMITTED",
            payload={"controller_receipt_id": commit["receipt_id"], "preparation_receipt_id": prep_id},
        )
        self.reentry_store.append_event(
            opportunity_id=opportunity_id,
            wake_id=wake_id,
            seat_id=opportunity["seat_id"],
            kind="DORMANT",
            payload={"occupancy_state": "AVAILABLE"},
        )
        return self._terminal(
            opportunity=opportunity,
            wake_id=wake_id,
            outcome="UNIT_COMPLETED",
            preparation_receipt_id=prep_id,
            controller_receipt_id=commit["receipt_id"],
            work_units=1,
            occupancy_released=True,
        )
