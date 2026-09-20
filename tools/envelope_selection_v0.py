#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from tools.development_campaign_v0 import CampaignStore, object_sha256

SELECTION_SCHEMA = "envelope_selection_v0"
SELECT = "SELECTED_FOR_PACKET_FORMATION"
RELEASE = "SELECTION_RELEASED"
EXECUTIVE = "REED"


class EnvelopeSelectionError(RuntimeError):
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
        raise EnvelopeSelectionError(f"unknown request {request_id!r}")
    return json.loads(row["request_json"])


def build_selection_event(
    *,
    campaign: dict[str, Any],
    request: dict[str, Any],
    selection_id: str,
    basis_refs: list[str],
    kind: str,
    reason: str | None = None,
    selected_by: str = EXECUTIVE,
) -> dict[str, Any]:
    if kind not in {SELECT, RELEASE}:
        raise EnvelopeSelectionError("invalid selection kind")
    if selected_by != EXECUTIVE:
        raise EnvelopeSelectionError("v0 selector must be REED")
    if not selection_id:
        raise EnvelopeSelectionError("selection_id required")
    if not basis_refs or len(basis_refs) != len(set(basis_refs)):
        raise EnvelopeSelectionError("basis refs must be non-empty and unique")
    return {
        "schema": SELECTION_SCHEMA,
        "selection_id": selection_id,
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": object_sha256(campaign),
        "request_id": request["request_id"],
        "request_sha256": object_sha256(request),
        "selected_by": selected_by,
        "selected_at_basis_refs": list(basis_refs),
        "selected_at_basis_sha256": object_sha256(basis_refs),
        "selection_kind": kind,
        "selection_reason": reason,
        "authorization_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
    }


class SelectionStore:
    def __init__(self, campaign_store: CampaignStore, db_path: str | Path):
        self.campaign_store = campaign_store
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS selection_events(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    selection_id TEXT UNIQUE NOT NULL,
                    event_sha256 TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    event_json TEXT NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _validate(self, event: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        required = {
            "schema","selection_id","campaign_id","campaign_sha256","request_id",
            "request_sha256","selected_by","selected_at_basis_refs",
            "selected_at_basis_sha256","selection_kind","selection_reason",
            "authorization_effect","execution_effect","standing_effect",
        }
        if set(event) != required:
            raise EnvelopeSelectionError("selection fields are not exact")
        if event["schema"] != SELECTION_SCHEMA:
            raise EnvelopeSelectionError("wrong schema")
        if event["selected_by"] != EXECUTIVE:
            raise EnvelopeSelectionError("v0 selector must be REED")
        if event["selection_kind"] not in {SELECT, RELEASE}:
            raise EnvelopeSelectionError("invalid selection kind")
        if event["authorization_effect"] != "NONE" or event["execution_effect"] != "NONE" or event["standing_effect"] != "NONE":
            raise EnvelopeSelectionError("selection effects must remain NONE")

        campaign = self.campaign_store.get_campaign(event["campaign_id"])
        request = _load_request(self.campaign_store, event["request_id"])
        if event["campaign_sha256"] != object_sha256(campaign):
            raise EnvelopeSelectionError("campaign identity mismatch")
        if event["request_sha256"] != object_sha256(request):
            raise EnvelopeSelectionError("request identity mismatch")
        if request["campaign_id"] != campaign["campaign_id"]:
            raise EnvelopeSelectionError("request/campaign mismatch")

        refs = event["selected_at_basis_refs"]
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
            raise EnvelopeSelectionError("invalid selection basis refs")
        if event["selected_at_basis_sha256"] != object_sha256(refs):
            raise EnvelopeSelectionError("selection basis identity mismatch")
        return campaign, request

    def history(self, campaign_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT seq,event_json FROM selection_events WHERE campaign_id=? ORDER BY seq",
                (campaign_id,),
            ).fetchall()
        finally:
            conn.close()
        out = []
        for row in rows:
            event = json.loads(row["event_json"])
            event["_seq"] = row["seq"]
            out.append(event)
        return out

    def current_set(self, campaign_id: str) -> list[dict[str, Any]]:
        selected: dict[tuple[str, str], dict[str, Any]] = {}
        for event in self.history(campaign_id):
            key = (event["request_id"], event["request_sha256"])
            if event["selection_kind"] == SELECT:
                selected[key] = event
            else:
                selected.pop(key, None)
        return [selected[k] for k in sorted(selected)]

    def append(self, event: dict[str, Any]) -> dict[str, Any]:
        self._validate(event)
        digest = object_sha256(event)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT event_sha256 FROM selection_events WHERE selection_id=?",
                (event["selection_id"],),
            ).fetchone()
            if row is not None:
                if row["event_sha256"] != digest:
                    raise EnvelopeSelectionError("selection_id reused with different bytes")
                return {"idempotent_replay": True, "selection_id": event["selection_id"]}

            current = {
                (e["request_id"], e["request_sha256"])
                for e in self.current_set(event["campaign_id"])
            }
            key = (event["request_id"], event["request_sha256"])
            if event["selection_kind"] == SELECT and key in current:
                raise EnvelopeSelectionError("request already selected")
            if event["selection_kind"] == RELEASE and key not in current:
                raise EnvelopeSelectionError("request is not selected")

            conn.execute(
                """
                INSERT INTO selection_events(
                    selection_id,event_sha256,campaign_id,request_id,request_sha256,event_json
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    event["selection_id"],digest,event["campaign_id"],event["request_id"],
                    event["request_sha256"],_canonical(event),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {"idempotent_replay": False, "selection_id": event["selection_id"]}

    def projection(self, campaign_id: str, current_basis_refs: list[str]) -> dict[str, Any]:
        campaign = self.campaign_store.get_campaign(campaign_id)
        snap = self.campaign_store.snapshot(
            campaign_id,
            current_basis_refs=current_basis_refs,
        )
        result = []
        for selection in self.current_set(campaign_id):
            request = _load_request(self.campaign_store, selection["request_id"])
            if object_sha256(request) != selection["request_sha256"]:
                raise EnvelopeSelectionError("selected request bytes changed")
            standing = snap["standing"][request["unresolved_relation_id"]]["standing"]
            applicability = "CURRENT" if snap["basis_status"] == "CURRENT" else "STALE"
            relevance = {
                "OPEN": "OPEN",
                "EARNED": "RESOLVED_EARNED",
                "FRACTURED": "OBSOLETE_FRACTURED",
            }[standing]
            if applicability == "STALE":
                prep = "BLOCKED_PENDING_REVALIDATION"
            elif standing == "FRACTURED":
                prep = "BLOCKED_OBSOLETE"
            elif standing == "EARNED":
                prep = "BLOCKED_RESOLVED"
            else:
                prep = "ELIGIBLE_FOR_PACKET_PREPARATION"
            result.append({
                "request_id": request["request_id"],
                "request_sha256": object_sha256(request),
                "relation_id": request["unresolved_relation_id"],
                "attention": "SELECTED",
                "request_applicability": applicability,
                "developmental_relevance": relevance,
                "preparation": prep,
                "selection_id": selection["selection_id"],
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
                "standing_effect": "NONE",
                "priority_effect": "NONE",
            })
        return {
            "campaign_id": campaign_id,
            "campaign_sha256": object_sha256(campaign),
            "current_selection_set": result,
            "selection_count": len(result),
            "priority_effect": "NONE",
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
            "standing_effect": "NONE",
        }
