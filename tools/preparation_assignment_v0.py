#!/usr/bin/env python3
"""PREPARATION_ASSIGNMENT_001 — durable sticky-note allocation without wake/authority."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from tools.development_campaign_v0 import CampaignStore, object_sha256
from tools.envelope_selection_v0 import SelectionStore
from tools.preparation_v0 import PREP_KINDS, PreparationStore

ASSIGNMENT_SCHEMA = "preparation_assignment_v0"
SATISFACTION_SCHEMA = "assignment_satisfaction_v0"
ASSIGN = "ASSIGNED"
RELEASE = "ASSIGNMENT_RELEASED"
EXECUTIVE = "REED"


class PreparationAssignmentError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


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
        raise PreparationAssignmentError(f"unknown request {request_id!r}")
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
        raise PreparationAssignmentError(f"unknown selection {selection_id!r}")
    return json.loads(row["event_json"])


def _load_preparation_receipt(
    preparation_store: PreparationStore,
    preparation_id: str,
) -> dict[str, Any]:
    conn = sqlite3.connect(preparation_store.db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT receipt_json FROM preparation_receipts WHERE preparation_id=?",
            (preparation_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise PreparationAssignmentError(
            f"unknown preparation receipt {preparation_id!r}"
        )
    return json.loads(row["receipt_json"])


def build_assignment_event(
    *,
    campaign: dict[str, Any],
    request: dict[str, Any],
    selection: dict[str, Any],
    assignment_id: str,
    seat_id: str,
    preparation_kind: str,
    assigned_at_basis_refs: list[str],
    kind: str = ASSIGN,
    reason: str | None = None,
    assigned_by: str = EXECUTIVE,
) -> dict[str, Any]:
    if kind not in {ASSIGN, RELEASE}:
        raise PreparationAssignmentError("invalid assignment kind")
    if assigned_by != EXECUTIVE:
        raise PreparationAssignmentError("v0 assigner must be REED")
    if not assignment_id or not seat_id:
        raise PreparationAssignmentError("assignment_id and seat_id are required")
    if preparation_kind not in PREP_KINDS:
        raise PreparationAssignmentError("unsupported preparation kind")
    if (
        not assigned_at_basis_refs
        or len(assigned_at_basis_refs) != len(set(assigned_at_basis_refs))
    ):
        raise PreparationAssignmentError(
            "assignment basis refs must be non-empty and unique"
        )
    return {
        "schema": ASSIGNMENT_SCHEMA,
        "assignment_id": assignment_id,
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": object_sha256(campaign),
        "request_id": request["request_id"],
        "request_sha256": object_sha256(request),
        "selection_ref": selection["selection_id"],
        "selection_sha256": object_sha256(selection),
        "seat_id": seat_id,
        "preparation_kind": preparation_kind,
        "assigned_by": assigned_by,
        "assigned_at_basis_refs": list(assigned_at_basis_refs),
        "assigned_at_basis_sha256": object_sha256(assigned_at_basis_refs),
        "assignment_kind": kind,
        "assignment_reason": reason,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
        "priority_effect": "NONE",
        "wake_effect": "NONE",
    }


def build_satisfaction(
    *,
    assignment: dict[str, Any],
    preparation_receipt: dict[str, Any],
    satisfaction_id: str,
) -> dict[str, Any]:
    if not satisfaction_id:
        raise PreparationAssignmentError("satisfaction_id required")
    return {
        "schema": SATISFACTION_SCHEMA,
        "satisfaction_id": satisfaction_id,
        "assignment_id": assignment["assignment_id"],
        "assignment_sha256": object_sha256(assignment),
        "preparation_receipt_id": preparation_receipt["preparation_id"],
        "preparation_receipt_sha256": object_sha256(preparation_receipt),
        "request_id": assignment["request_id"],
        "request_sha256": assignment["request_sha256"],
        "seat_id": assignment["seat_id"],
        "preparation_kind": assignment["preparation_kind"],
        "satisfaction_effect": "SATISFIES_EXACT_ASSIGNMENT",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
        "priority_effect": "NONE",
        "wake_effect": "NONE",
    }


class AssignmentStore:
    def __init__(
        self,
        campaign_store: CampaignStore,
        selection_store: SelectionStore,
        preparation_store: PreparationStore,
        db_path: str | Path,
    ):
        self.campaign_store = campaign_store
        self.selection_store = selection_store
        self.preparation_store = preparation_store
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS assignment_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id TEXT UNIQUE NOT NULL,
                    event_sha256 TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    seat_id TEXT NOT NULL,
                    preparation_kind TEXT NOT NULL,
                    event_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS assignment_satisfactions(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    satisfaction_id TEXT UNIQUE NOT NULL,
                    satisfaction_sha256 TEXT NOT NULL,
                    assignment_id TEXT NOT NULL,
                    assignment_sha256 TEXT NOT NULL,
                    preparation_receipt_id TEXT NOT NULL,
                    preparation_receipt_sha256 TEXT NOT NULL,
                    satisfaction_json TEXT NOT NULL
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _key(event: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            event["request_id"],
            event["request_sha256"],
            event["seat_id"],
            event["preparation_kind"],
        )

    def history(self, campaign_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT seq,event_json FROM assignment_events "
                "WHERE campaign_id=? ORDER BY seq",
                (campaign_id,),
            ).fetchall()
        finally:
            conn.close()
        out: list[dict[str, Any]] = []
        for row in rows:
            event = json.loads(row["event_json"])
            event["_seq"] = row["seq"]
            out.append(event)
        return out

    def satisfaction_history(self) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT seq,satisfaction_json FROM assignment_satisfactions "
                "ORDER BY seq"
            ).fetchall()
        finally:
            conn.close()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = json.loads(row["satisfaction_json"])
            item["_seq"] = row["seq"]
            out.append(item)
        return out

    def _assigned_lineage(
        self,
        campaign_id: str,
    ) -> list[tuple[dict[str, Any], dict[str, Any] | None]]:
        active: dict[tuple[str, str, str, str], int] = {}
        lineage: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
        for event in self.history(campaign_id):
            key = self._key(event)
            if event["assignment_kind"] == ASSIGN:
                active[key] = len(lineage)
                lineage.append((event, None))
            else:
                index = active.pop(key, None)
                if index is not None:
                    assigned, _ = lineage[index]
                    lineage[index] = (assigned, event)
        return lineage

    def _validate_event(
        self,
        event: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        required = {
            "schema","assignment_id","campaign_id","campaign_sha256",
            "request_id","request_sha256","selection_ref","selection_sha256",
            "seat_id","preparation_kind","assigned_by",
            "assigned_at_basis_refs","assigned_at_basis_sha256",
            "assignment_kind","assignment_reason","authority_effect",
            "execution_effect","standing_effect","priority_effect","wake_effect",
        }
        if set(event) != required or event["schema"] != ASSIGNMENT_SCHEMA:
            raise PreparationAssignmentError("assignment fields are not exact")
        if event["assignment_kind"] not in {ASSIGN, RELEASE}:
            raise PreparationAssignmentError("invalid assignment kind")
        if event["assigned_by"] != EXECUTIVE:
            raise PreparationAssignmentError("v0 assigner must be REED")
        if not event["seat_id"] or event["preparation_kind"] not in PREP_KINDS:
            raise PreparationAssignmentError("invalid seat/preparation kind")
        for field in (
            "authority_effect","execution_effect","standing_effect",
            "priority_effect","wake_effect",
        ):
            if event[field] != "NONE":
                raise PreparationAssignmentError(f"{field} must remain NONE")

        campaign = self.campaign_store.get_campaign(event["campaign_id"])
        request = _load_request(self.campaign_store, event["request_id"])
        selection = _load_selection(self.selection_store, event["selection_ref"])
        if event["campaign_sha256"] != object_sha256(campaign):
            raise PreparationAssignmentError("campaign identity mismatch")
        if event["request_sha256"] != object_sha256(request):
            raise PreparationAssignmentError("request identity mismatch")
        if event["selection_sha256"] != object_sha256(selection):
            raise PreparationAssignmentError("selection identity mismatch")
        if (
            selection["request_id"] != request["request_id"]
            or selection["request_sha256"] != object_sha256(request)
        ):
            raise PreparationAssignmentError("selection does not bind exact request")
        refs = event["assigned_at_basis_refs"]
        if (
            not isinstance(refs, list)
            or not refs
            or len(refs) != len(set(refs))
            or event["assigned_at_basis_sha256"] != object_sha256(refs)
        ):
            raise PreparationAssignmentError("assignment basis identity mismatch")
        return campaign, request, selection

    def append(
        self,
        event: dict[str, Any],
        *,
        current_basis_refs: list[str],
    ) -> dict[str, Any]:
        campaign, request, selection = self._validate_event(event)
        digest = object_sha256(event)

        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT event_sha256 FROM assignment_events WHERE assignment_id=?",
                (event["assignment_id"],),
            ).fetchone()
        finally:
            conn.close()
        if row is not None:
            if row["event_sha256"] != digest:
                raise PreparationAssignmentError(
                    "assignment_id reused with different bytes"
                )
            return {
                "assignment_id": event["assignment_id"],
                "idempotent_replay": True,
                "authority_effect": "NONE",
                "execution_effect": "NONE",
                "wake_effect": "NONE",
            }

        current: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        for assigned, released in self._assigned_lineage(campaign["campaign_id"]):
            if released is None:
                current[self._key(assigned)] = assigned
        key = self._key(event)

        if event["assignment_kind"] == ASSIGN:
            if key in current:
                raise PreparationAssignmentError(
                    "exact seat/request/preparation tuple already assigned"
                )
            selection_projection = self.selection_store.projection(
                campaign["campaign_id"],
                current_basis_refs=current_basis_refs,
            )
            selected = {
                (item["request_id"], item["request_sha256"]): item
                for item in selection_projection["current_selection_set"]
            }.get((request["request_id"], object_sha256(request)))
            if selected is None:
                raise PreparationAssignmentError(
                    "request is not currently selected"
                )
            if selected["selection_id"] != selection["selection_id"]:
                raise PreparationAssignmentError(
                    "assignment does not bind current exact selection"
                )
            if selected["preparation"] != "ELIGIBLE_FOR_PACKET_PREPARATION":
                raise PreparationAssignmentError(
                    f"request is not assignment-eligible: {selected['preparation']}"
                )
            if event["assigned_at_basis_refs"] != current_basis_refs:
                raise PreparationAssignmentError(
                    "assignment basis must equal current basis"
                )
        else:
            assigned = current.get(key)
            if assigned is None:
                raise PreparationAssignmentError(
                    "cannot release non-current assignment"
                )
            if (
                assigned["selection_ref"] != event["selection_ref"]
                or assigned["selection_sha256"] != event["selection_sha256"]
            ):
                raise PreparationAssignmentError(
                    "release does not bind current assignment selection"
                )

        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO assignment_events(
                    assignment_id,event_sha256,campaign_id,request_id,
                    request_sha256,seat_id,preparation_kind,event_json
                ) VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    event["assignment_id"],digest,event["campaign_id"],
                    event["request_id"],event["request_sha256"],event["seat_id"],
                    event["preparation_kind"],_canonical(event),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {
            "assignment_id": event["assignment_id"],
            "idempotent_replay": False,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "wake_effect": "NONE",
        }

    def _load_assignment(self, assignment_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT event_json FROM assignment_events WHERE assignment_id=?",
                (assignment_id,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise PreparationAssignmentError(
                f"unknown assignment {assignment_id!r}"
            )
        return json.loads(row["event_json"])

    def append_satisfaction(
        self,
        satisfaction: dict[str, Any],
    ) -> dict[str, Any]:
        required = {
            "schema","satisfaction_id","assignment_id","assignment_sha256",
            "preparation_receipt_id","preparation_receipt_sha256",
            "request_id","request_sha256","seat_id","preparation_kind",
            "satisfaction_effect","authority_effect","execution_effect",
            "standing_effect","priority_effect","wake_effect",
        }
        if (
            set(satisfaction) != required
            or satisfaction["schema"] != SATISFACTION_SCHEMA
        ):
            raise PreparationAssignmentError("satisfaction fields are not exact")
        if satisfaction["satisfaction_effect"] != "SATISFIES_EXACT_ASSIGNMENT":
            raise PreparationAssignmentError("invalid satisfaction effect")
        for field in (
            "authority_effect","execution_effect","standing_effect",
            "priority_effect","wake_effect",
        ):
            if satisfaction[field] != "NONE":
                raise PreparationAssignmentError(
                    f"{field} must remain NONE"
                )

        assignment = self._load_assignment(satisfaction["assignment_id"])
        if assignment["assignment_kind"] != ASSIGN:
            raise PreparationAssignmentError("only ASSIGNED event may be satisfied")
        if satisfaction["assignment_sha256"] != object_sha256(assignment):
            raise PreparationAssignmentError("assignment identity mismatch")

        receipt = _load_preparation_receipt(
            self.preparation_store,
            satisfaction["preparation_receipt_id"],
        )
        if (
            satisfaction["preparation_receipt_sha256"]
            != object_sha256(receipt)
        ):
            raise PreparationAssignmentError(
                "preparation receipt identity mismatch"
            )

        expected = {
            "request_id": assignment["request_id"],
            "request_sha256": assignment["request_sha256"],
            "seat_id": assignment["seat_id"],
            "preparation_kind": assignment["preparation_kind"],
        }
        for field, value in expected.items():
            if satisfaction[field] != value:
                raise PreparationAssignmentError(
                    f"satisfaction {field} does not bind assignment"
                )
        if (
            receipt["request_id"] != assignment["request_id"]
            or receipt["request_sha256"] != assignment["request_sha256"]
            or receipt["selection_ref"] != assignment["selection_ref"]
            or receipt["selection_sha256"] != assignment["selection_sha256"]
            or receipt["prepared_by"] != assignment["seat_id"]
            or receipt["preparation_kind"] != assignment["preparation_kind"]
            or receipt["mechanical_status"] != "PASS"
        ):
            raise PreparationAssignmentError(
                "preparation receipt does not qualify exact assignment"
            )

        digest = object_sha256(satisfaction)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT satisfaction_sha256 FROM assignment_satisfactions "
                "WHERE satisfaction_id=?",
                (satisfaction["satisfaction_id"],),
            ).fetchone()
            if row is not None:
                if row["satisfaction_sha256"] != digest:
                    raise PreparationAssignmentError(
                        "satisfaction_id reused with different bytes"
                    )
                return {
                    "satisfaction_id": satisfaction["satisfaction_id"],
                    "idempotent_replay": True,
                    "wake_effect": "NONE",
                }

            already = conn.execute(
                "SELECT satisfaction_id FROM assignment_satisfactions "
                "WHERE assignment_id=? AND assignment_sha256=?",
                (
                    satisfaction["assignment_id"],
                    satisfaction["assignment_sha256"],
                ),
            ).fetchone()
            if already is not None:
                raise PreparationAssignmentError(
                    "exact assignment already satisfied"
                )

            conn.execute(
                """
                INSERT INTO assignment_satisfactions(
                    satisfaction_id,satisfaction_sha256,assignment_id,
                    assignment_sha256,preparation_receipt_id,
                    preparation_receipt_sha256,satisfaction_json
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    satisfaction["satisfaction_id"],digest,
                    satisfaction["assignment_id"],
                    satisfaction["assignment_sha256"],
                    satisfaction["preparation_receipt_id"],
                    satisfaction["preparation_receipt_sha256"],
                    _canonical(satisfaction),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {
            "satisfaction_id": satisfaction["satisfaction_id"],
            "idempotent_replay": False,
            "wake_effect": "NONE",
        }

    def projection(
        self,
        campaign_id: str,
        *,
        current_basis_refs: list[str],
    ) -> dict[str, Any]:
        selection_projection = self.selection_store.projection(
            campaign_id,
            current_basis_refs=current_basis_refs,
        )
        selected = {
            (item["request_id"], item["request_sha256"]): item
            for item in selection_projection["current_selection_set"]
        }
        satisfactions = {
            (item["assignment_id"], item["assignment_sha256"]): item
            for item in self.satisfaction_history()
        }

        rows: list[dict[str, Any]] = []
        for assignment, release in self._assigned_lineage(campaign_id):
            assignment_sha = object_sha256(
                {k: v for k, v in assignment.items() if k != "_seq"}
            )
            satisfaction = satisfactions.get(
                (assignment["assignment_id"], assignment_sha)
            )
            selected_row = selected.get(
                (assignment["request_id"], assignment["request_sha256"])
            )

            if release is not None:
                state = "RELEASED"
            elif satisfaction is not None:
                state = "SATISFIED"
            elif selected_row is None:
                state = "BLOCKED_NOT_SELECTED"
            elif selected_row["request_applicability"] == "STALE":
                state = "BLOCKED_STALE"
            elif selected_row["developmental_relevance"] == "OBSOLETE_FRACTURED":
                state = "BLOCKED_OBSOLETE"
            elif selected_row["developmental_relevance"] == "RESOLVED_EARNED":
                state = "BLOCKED_RESOLVED"
            elif selected_row["preparation"] != "ELIGIBLE_FOR_PACKET_PREPARATION":
                state = "BLOCKED_PREPARATION"
            else:
                state = "OUTSTANDING"

            wake_eligible = state == "OUTSTANDING"
            rows.append(
                {
                    "assignment_id": assignment["assignment_id"],
                    "assignment_sha256": assignment_sha,
                    "request_id": assignment["request_id"],
                    "request_sha256": assignment["request_sha256"],
                    "seat_id": assignment["seat_id"],
                    "preparation_kind": assignment["preparation_kind"],
                    "assignment_state": state,
                    "wake_eligible": wake_eligible,
                    "release_event_id": (
                        release["assignment_id"] if release is not None else None
                    ),
                    "satisfaction_id": (
                        satisfaction["satisfaction_id"]
                        if satisfaction is not None
                        else None
                    ),
                    "authority_effect": "NONE",
                    "execution_effect": "NONE",
                    "standing_effect": "NONE",
                    "priority_effect": "NONE",
                    "wake_effect": "NONE",
                }
            )

        wake_eligible_assignments = sorted(
            (
                {
                    "assignment_id": row["assignment_id"],
                    "assignment_sha256": row["assignment_sha256"],
                    "seat_id": row["seat_id"],
                    "request_id": row["request_id"],
                    "request_sha256": row["request_sha256"],
                    "preparation_kind": row["preparation_kind"],
                }
                for row in rows
                if row["wake_eligible"]
            ),
            key=lambda item: item["assignment_id"],
        )
        return {
            "campaign_id": campaign_id,
            "assignment_projection": rows,
            "wake_eligible_assignments": wake_eligible_assignments,
            "wake_eligible_count": len(wake_eligible_assignments),
            "priority_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "standing_effect": "NONE",
            "wake_effect": "NONE",
        }
