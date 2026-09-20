#!/usr/bin/env python3
"""PREPARATION_001 append-only preparation receipts and readiness projection."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

from tools.development_campaign_v0 import CampaignStore, object_sha256
from tools.envelope_selection_v0 import SelectionStore, EnvelopeSelectionError

PREP_SCHEMA = "preparation_receipt_v0"
PREP_KINDS = {
    "RESOLVE_REFS",
    "REVALIDATE_BASIS",
    "ASSEMBLE_EVIDENCE",
    "DRAFT_PACKET",
    "REQUEST_REVIEW",
    "REVIEW_RESULT",
    "ESTIMATE_RESOURCES",
    "DETECT_CONFLICTS",
    "DERIVE_STOP_CONDITIONS",
}
MECH = {"PASS", "FAIL", "PARTIAL"}
REVIEWS = {None, "PASS", "OBJECTION"}

PACKET_FIELDS = {
    "PACKET_ID",
    "BASIS",
    "CURRENT_PRESSURE",
    "ADMITTED_EVIDENCE",
    "UNRESOLVED",
    "AUTHORIZED_OPERATIONS",
    "UNAUTHORIZED_EXTRAPOLATIONS",
    "REQUIRED_EVIDENCE_RETURN",
    "STOP_OR_ESCALATE_IF",
    "EXECUTION_QUESTIONS",
    "AUTHORIZATION",
}


class PreparationError(RuntimeError):
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
        raise PreparationError(f"unknown request {request_id!r}")
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
        raise PreparationError(f"unknown selection {selection_id!r}")
    return json.loads(row["event_json"])


def validate_packet_draft(packet: dict[str, Any]) -> None:
    if not isinstance(packet, dict) or set(packet) != PACKET_FIELDS:
        raise PreparationError("packet draft does not match Twinning required fields")
    if packet["AUTHORIZATION"] != "NOT_AUTHORIZED":
        raise PreparationError("preparation packet may not self-authorize")
    for field in ("PACKET_ID", "BASIS", "CURRENT_PRESSURE"):
        if not isinstance(packet[field], str) or not packet[field]:
            raise PreparationError(f"{field} must be non-empty text")
    for field in (
        "ADMITTED_EVIDENCE",
        "UNRESOLVED",
        "AUTHORIZED_OPERATIONS",
        "UNAUTHORIZED_EXTRAPOLATIONS",
        "REQUIRED_EVIDENCE_RETURN",
        "STOP_OR_ESCALATE_IF",
        "EXECUTION_QUESTIONS",
    ):
        if not isinstance(packet[field], list):
            raise PreparationError(f"{field} must be a list")


def build_receipt(
    *,
    campaign: dict[str, Any],
    request: dict[str, Any],
    selection: dict[str, Any],
    preparation_id: str,
    prepared_by: str,
    preparation_kind: str,
    preparation_basis_refs: list[str],
    input_refs: list[str],
    output_refs: list[str],
    mechanical_status: str,
    review_disposition: str | None = None,
) -> dict[str, Any]:
    if preparation_kind not in PREP_KINDS:
        raise PreparationError("unsupported preparation kind")
    if mechanical_status not in MECH:
        raise PreparationError("invalid mechanical status")
    if review_disposition not in REVIEWS:
        raise PreparationError("invalid review disposition")
    if preparation_kind == "REVIEW_RESULT" and review_disposition is None:
        raise PreparationError("REVIEW_RESULT requires disposition")
    if preparation_kind != "REVIEW_RESULT" and review_disposition is not None:
        raise PreparationError("review disposition only valid for REVIEW_RESULT")
    if not preparation_id or not prepared_by:
        raise PreparationError("preparation_id and prepared_by required")
    if not preparation_basis_refs or len(preparation_basis_refs) != len(set(preparation_basis_refs)):
        raise PreparationError("preparation basis refs must be non-empty and unique")
    if len(input_refs) != len(set(input_refs)) or len(output_refs) != len(set(output_refs)):
        raise PreparationError("input/output refs must be unique")

    return {
        "schema": PREP_SCHEMA,
        "preparation_id": preparation_id,
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": object_sha256(campaign),
        "request_id": request["request_id"],
        "request_sha256": object_sha256(request),
        "selection_ref": selection["selection_id"],
        "selection_sha256": object_sha256(selection),
        "prepared_by": prepared_by,
        "preparation_kind": preparation_kind,
        "preparation_basis_refs": list(preparation_basis_refs),
        "preparation_basis_sha256": object_sha256(preparation_basis_refs),
        "input_refs": list(input_refs),
        "output_refs": list(output_refs),
        "mechanical_status": mechanical_status,
        "review_disposition": review_disposition,
        "preparation_effect": "PREPARATION_ONLY",
        "canonical_mutation_effect": "NONE",
        "authorization_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
        "priority_effect": "NONE",
    }


class PreparationStore:
    def __init__(
        self,
        campaign_store: CampaignStore,
        selection_store: SelectionStore,
        db_path: str | Path,
    ):
        self.campaign_store = campaign_store
        self.selection_store = selection_store
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS prep_artifacts(
                    artifact_ref TEXT PRIMARY KEY,
                    artifact_kind TEXT NOT NULL,
                    artifact_sha256 TEXT NOT NULL,
                    artifact_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS preparation_receipts(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT UNIQUE NOT NULL,
                    receipt_sha256 TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    request_sha256 TEXT NOT NULL,
                    selection_ref TEXT NOT NULL,
                    receipt_json TEXT NOT NULL
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

    def register_artifact(self, artifact_ref: str, artifact_kind: str, value: dict[str, Any]) -> dict[str, Any]:
        if not artifact_ref or not artifact_kind:
            raise PreparationError("artifact ref/kind required")
        if artifact_kind == "EXECUTION_PACKET_v0":
            validate_packet_draft(value)
        digest = object_sha256(value)
        rendered = _canonical(value)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT artifact_sha256 FROM prep_artifacts WHERE artifact_ref=?",
                (artifact_ref,),
            ).fetchone()
            if row is not None:
                if row["artifact_sha256"] != digest:
                    raise PreparationError("artifact ref reused with different bytes")
                return {"artifact_ref": artifact_ref, "idempotent_replay": True}
            conn.execute(
                "INSERT INTO prep_artifacts VALUES(?,?,?,?)",
                (artifact_ref, artifact_kind, digest, rendered),
            )
            conn.commit()
        finally:
            conn.close()
        return {"artifact_ref": artifact_ref, "idempotent_replay": False}

    def _artifact(self, artifact_ref: str) -> tuple[str, dict[str, Any]]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT artifact_kind,artifact_json FROM prep_artifacts WHERE artifact_ref=?",
                (artifact_ref,),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            raise PreparationError(f"unknown preparation artifact {artifact_ref!r}")
        return row["artifact_kind"], json.loads(row["artifact_json"])

    def history(self, campaign_id: str, request_id: str | None = None) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            if request_id is None:
                rows = conn.execute(
                    "SELECT seq,receipt_json FROM preparation_receipts WHERE campaign_id=? ORDER BY seq",
                    (campaign_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT seq,receipt_json FROM preparation_receipts
                    WHERE campaign_id=? AND request_id=? ORDER BY seq
                    """,
                    (campaign_id, request_id),
                ).fetchall()
        finally:
            conn.close()
        out = []
        for row in rows:
            receipt = json.loads(row["receipt_json"])
            receipt["_seq"] = row["seq"]
            out.append(receipt)
        return out

    def _validate_receipt(self, receipt: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        required = {
            "schema","preparation_id","campaign_id","campaign_sha256","request_id",
            "request_sha256","selection_ref","selection_sha256","prepared_by",
            "preparation_kind","preparation_basis_refs","preparation_basis_sha256",
            "input_refs","output_refs","mechanical_status","review_disposition",
            "preparation_effect","canonical_mutation_effect","authorization_effect",
            "execution_effect","standing_effect","priority_effect",
        }
        if set(receipt) != required or receipt["schema"] != PREP_SCHEMA:
            raise PreparationError("preparation receipt fields are not exact")
        if receipt["preparation_kind"] not in PREP_KINDS:
            raise PreparationError("invalid preparation kind")
        if receipt["mechanical_status"] not in MECH:
            raise PreparationError("invalid mechanical status")
        if receipt["review_disposition"] not in REVIEWS:
            raise PreparationError("invalid review disposition")
        if receipt["preparation_effect"] != "PREPARATION_ONLY":
            raise PreparationError("invalid preparation effect")
        for field in (
            "canonical_mutation_effect","authorization_effect","execution_effect",
            "standing_effect","priority_effect",
        ):
            if receipt[field] != "NONE":
                raise PreparationError(f"{field} must remain NONE")

        campaign = self.campaign_store.get_campaign(receipt["campaign_id"])
        request = _load_request(self.campaign_store, receipt["request_id"])
        selection = _load_selection(self.selection_store, receipt["selection_ref"])

        if receipt["campaign_sha256"] != object_sha256(campaign):
            raise PreparationError("campaign identity mismatch")
        if receipt["request_sha256"] != object_sha256(request):
            raise PreparationError("request identity mismatch")
        if receipt["selection_sha256"] != object_sha256(selection):
            raise PreparationError("selection identity mismatch")
        if selection["request_id"] != request["request_id"] or selection["request_sha256"] != object_sha256(request):
            raise PreparationError("selection does not bind exact request")
        refs = receipt["preparation_basis_refs"]
        if receipt["preparation_basis_sha256"] != object_sha256(refs):
            raise PreparationError("preparation basis identity mismatch")

        if receipt["preparation_kind"] == "REVIEW_RESULT" and receipt["review_disposition"] is None:
            raise PreparationError("review result requires disposition")
        if receipt["preparation_kind"] != "REVIEW_RESULT" and receipt["review_disposition"] is not None:
            raise PreparationError("review disposition only valid for review result")

        if receipt["preparation_kind"] == "DRAFT_PACKET":
            if not receipt["output_refs"]:
                raise PreparationError("DRAFT_PACKET requires output artifact")
            packet_found = False
            for ref in receipt["output_refs"]:
                kind, value = self._artifact(ref)
                if kind == "EXECUTION_PACKET_v0":
                    validate_packet_draft(value)
                    packet_found = True
            if not packet_found:
                raise PreparationError("DRAFT_PACKET has no EXECUTION_PACKET_v0 artifact")

        return campaign, request, selection

    def append(self, receipt: dict[str, Any], *, current_basis_refs: list[str]) -> dict[str, Any]:
        campaign, request, selection = self._validate_receipt(receipt)

        projection = self.selection_store.projection(
            campaign["campaign_id"],
            current_basis_refs=current_basis_refs,
        )
        selected = {
            (item["request_id"], item["request_sha256"]): item
            for item in projection["current_selection_set"]
        }
        key = (request["request_id"], object_sha256(request))
        current = selected.get(key)
        if current is None:
            raise PreparationError("request is not currently selected")
        if current["preparation"] != "ELIGIBLE_FOR_PACKET_PREPARATION":
            raise PreparationError(
                f"request is not preparation-eligible: {current['preparation']}"
            )
        if receipt["preparation_basis_refs"] != current_basis_refs:
            raise PreparationError("receipt basis must equal current preparation basis")

        digest = object_sha256(receipt)
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT receipt_sha256 FROM preparation_receipts WHERE preparation_id=?",
                (receipt["preparation_id"],),
            ).fetchone()
            if row is not None:
                if row["receipt_sha256"] != digest:
                    raise PreparationError("preparation_id reused with different bytes")
                return {
                    "preparation_id": receipt["preparation_id"],
                    "idempotent_replay": True,
                    "authorization_effect": "NONE",
                    "execution_effect": "NONE",
                    "standing_effect": "NONE",
                }
            conn.execute(
                """
                INSERT INTO preparation_receipts(
                    preparation_id,receipt_sha256,campaign_id,request_id,
                    request_sha256,selection_ref,receipt_json
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    receipt["preparation_id"],digest,receipt["campaign_id"],
                    receipt["request_id"],receipt["request_sha256"],
                    receipt["selection_ref"],_canonical(receipt),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {
            "preparation_id": receipt["preparation_id"],
            "idempotent_replay": False,
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
            "standing_effect": "NONE",
        }

    def projection(
        self,
        campaign_id: str,
        request_id: str,
        *,
        current_basis_refs: list[str],
        external_authority_status: str = "ABSENT",
    ) -> dict[str, Any]:
        if external_authority_status not in {"ABSENT", "PRESENT"}:
            raise PreparationError("invalid external authority status")

        request = _load_request(self.campaign_store, request_id)
        request_sha = object_sha256(request)
        selection_projection = self.selection_store.projection(
            campaign_id,
            current_basis_refs=current_basis_refs,
        )
        selected = {
            (item["request_id"], item["request_sha256"]): item
            for item in selection_projection["current_selection_set"]
        }.get((request_id, request_sha))

        receipts = self.history(campaign_id, request_id)
        current_receipts = [
            r for r in receipts if r["preparation_basis_refs"] == current_basis_refs
        ]
        stale_receipts = [
            r for r in receipts if r["preparation_basis_refs"] != current_basis_refs
        ]

        if selected is None:
            readiness = "PREP_NOT_SELECTED"
        elif selected["request_applicability"] == "STALE":
            readiness = "PREP_BLOCKED_STALE"
        elif selected["developmental_relevance"] == "OBSOLETE_FRACTURED":
            readiness = "PREP_BLOCKED_OBSOLETE"
        elif selected["developmental_relevance"] == "RESOLVED_EARNED":
            readiness = "PREP_BLOCKED_RESOLVED"
        else:
            review_results = [
                r["review_disposition"]
                for r in current_receipts
                if r["preparation_kind"] == "REVIEW_RESULT"
                and r["mechanical_status"] == "PASS"
            ]
            review_set = set(review_results)
            draft_receipts = [
                r for r in current_receipts
                if r["preparation_kind"] == "DRAFT_PACKET"
                and r["mechanical_status"] == "PASS"
            ]
            if "PASS" in review_set and "OBJECTION" in review_set:
                readiness = "PREP_INCOMPLETE_REVIEW_CONFLICT"
            elif "OBJECTION" in review_set:
                readiness = "PREP_INCOMPLETE_REVIEW_OBJECTION"
            elif not draft_receipts:
                readiness = "PREP_INCOMPLETE"
            else:
                readiness = "PREP_READY_FOR_AUTHORITY_REVIEW"

        return {
            "campaign_id": campaign_id,
            "request_id": request_id,
            "request_sha256": request_sha,
            "selected_projection": selected,
            "readiness": readiness,
            "receipt_count": len(receipts),
            "current_receipt_count": len(current_receipts),
            "stale_receipt_count": len(stale_receipts),
            "external_authority_status": external_authority_status,
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
            "standing_effect": "NONE",
            "canonical_mutation_effect": "NONE",
            "priority_effect": "NONE",
        }
