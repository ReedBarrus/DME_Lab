#!/usr/bin/env python3
"""CAMPAIGN_BASIS_REVALIDATION_001 — basis-relative campaign applicability.

This module does exactly one thing: relate one immutable historical
development_campaign_v0 object to one exact candidate current basis using
requirements deterministically grounded in the campaign's own durable bytes.

It does not adopt campaigns, select work, assign seats, create priority, change
standing, grant authority, schedule work, wake seats, or execute consequences.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from tools.development_campaign_v0 import object_sha256, validate_campaign


REQUEST_SCHEMA = "campaign_basis_revalidation_request_v0"
RESULT_SCHEMA = "CAMPAIGN_BASIS_REVALIDATION_v0"
ARTIFACT_EVIDENCE_SCHEMA = "campaign_artifact_evidence_v0"
EFFECT_TRACE_SCHEMA = "campaign_effect_trace_v0"

CURRENTLY_APPLICABLE = "CURRENTLY_APPLICABLE"
NOT_APPLICABLE = "NOT_APPLICABLE"
INSUFFICIENT_BASIS = "INSUFFICIENT_BASIS"
DISPOSITIONS = {
    CURRENTLY_APPLICABLE,
    NOT_APPLICABLE,
    INSUFFICIENT_BASIS,
}

ESTABLISHED = "ESTABLISHED"
FRACTURED = "FRACTURED"
UNRESOLVED = "UNRESOLVED"
OBSERVED_RESULTS = {ESTABLISHED, FRACTURED, UNRESOLVED}

_EFFECT_FIELDS = (
    "authority_effect",
    "adoption_effect",
    "selection_effect",
    "standing_effect",
    "execution_effect",
    "priority_effect",
    "scheduler_effect",
)

_STORAGE_METADATA = {"_seq", "_rowid", "_inserted_at"}

_GIT_REF = re.compile(r"^git:([0-9a-f]{40})$")
_QUAL_REF = re.compile(r"^qualification:(.+)@([0-9a-f]{40})$")
_SHA256_REF = re.compile(r"^sha256:([A-Za-z0-9._:/-]+):([0-9a-f]{64})$")


class CampaignBasisRevalidationError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _git_blob_sha1(content: str) -> str:
    if not isinstance(content, str):
        raise CampaignBasisRevalidationError("artifact content must be text")
    raw = content.encode("utf-8")
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _strip_storage_metadata(value: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in value.items() if k not in _STORAGE_METADATA}


def _validate_basis_refs(refs: Any) -> list[str]:
    if not isinstance(refs, list) or not refs:
        raise CampaignBasisRevalidationError(
            "candidate_current_basis_refs must be a non-empty list"
        )
    if not all(isinstance(ref, str) and ref for ref in refs):
        raise CampaignBasisRevalidationError(
            "candidate current basis refs must be non-empty strings"
        )
    if len(refs) != len(set(refs)):
        raise CampaignBasisRevalidationError(
            "candidate current basis refs must be unique"
        )
    for ref in refs:
        if (
            _GIT_REF.fullmatch(ref) is None
            and _QUAL_REF.fullmatch(ref) is None
            and _SHA256_REF.fullmatch(ref) is None
        ):
            raise CampaignBasisRevalidationError(
                f"candidate basis ref is not explicit and content-addressed: {ref!r}"
            )
    return list(refs)


def _load_exact_campaign(campaign_bytes: Any) -> dict[str, Any]:
    if not isinstance(campaign_bytes, str) or not campaign_bytes:
        raise CampaignBasisRevalidationError("campaign_bytes must be exact UTF-8 text")
    try:
        campaign = json.loads(campaign_bytes)
    except json.JSONDecodeError as exc:
        raise CampaignBasisRevalidationError("campaign_bytes are not valid JSON") from exc
    if not isinstance(campaign, dict):
        raise CampaignBasisRevalidationError("campaign must decode to an object")
    try:
        validate_campaign(campaign)
    except Exception as exc:
        raise CampaignBasisRevalidationError(
            "historical campaign bytes are not a valid development_campaign_v0 object"
        ) from exc
    return campaign


def _qualification_requirement(ref: str) -> dict[str, Any]:
    match = _QUAL_REF.fullmatch(ref)
    if match is None:
        raise CampaignBasisRevalidationError("invalid qualification basis ref")
    path, blob_sha = match.groups()
    if not path:
        raise CampaignBasisRevalidationError("qualification path must be non-empty")
    return {
        "kind": "QUALIFICATION_ARTIFACT",
        "requirement_id": f"QUALIFICATION::{path}",
        "campaign_relevance_basis": ref,
        "historical_identity_or_relation": f"git_blob_sha1:{blob_sha}",
        "artifact_ref": path,
        "expected_blob_sha": blob_sha,
        "test_relation": (
            "CURRENT_QUALIFICATION_GIT_BLOB_SHA1 == "
            "HISTORICAL_QUALIFICATION_GIT_BLOB_SHA1"
        ),
    }


def _non_authorization_requirement(value: str) -> dict[str, Any]:
    if not isinstance(value, str) or not value.startswith("NO_") or len(value) <= 3:
        raise CampaignBasisRevalidationError(
            "explicit non-authorization must use NO_<EFFECT> form"
        )
    effect = value[3:]
    return {
        "kind": "NON_AUTHORIZATION",
        "requirement_id": f"NONAUTH::{effect}",
        "campaign_relevance_basis": f"explicit_non_authorizations:{value}",
        "historical_identity_or_relation": f"{effect}_EVENT_COUNT == 0",
        "effect": effect,
        "test_relation": f"len(raw_event_refs[{effect}]) == 0",
    }


def _derived_specs(campaign: dict[str, Any]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for ref in campaign["basis_refs"]:
        if _QUAL_REF.fullmatch(ref) is not None:
            specs.append(_qualification_requirement(ref))
    for value in campaign["explicit_non_authorizations"]:
        specs.append(_non_authorization_requirement(value))

    if not specs:
        raise CampaignBasisRevalidationError(
            "campaign bytes do not ground any continuity requirements"
        )

    ids = [spec["requirement_id"] for spec in specs]
    if len(ids) != len(set(ids)):
        raise CampaignBasisRevalidationError(
            "historical campaign grounds duplicate requirement identities"
        )
    return sorted(specs, key=lambda item: item["requirement_id"])


def derive_continuity_requirements(campaign: dict[str, Any]) -> list[dict[str, str]]:
    """Return the deterministic campaign-grounded requirement skeleton."""
    validate_campaign(campaign)
    out: list[dict[str, str]] = []
    for spec in _derived_specs(campaign):
        out.append(
            {
                "requirement_id": spec["requirement_id"],
                "campaign_relevance_basis": spec["campaign_relevance_basis"],
                "historical_identity_or_relation": spec[
                    "historical_identity_or_relation"
                ],
                "raw_current_evidence_inspected": "",
                "test_relation": spec["test_relation"],
                "observed_result": UNRESOLVED,
            }
        )
    return out


def _normalize_artifact_evidence(value: dict[str, Any]) -> dict[str, Any]:
    clean = _strip_storage_metadata(value)
    required = {"schema", "artifact_ref", "content"}
    if set(clean) != required or clean.get("schema") != ARTIFACT_EVIDENCE_SCHEMA:
        raise CampaignBasisRevalidationError(
            "artifact evidence fields are not exact raw evidence"
        )
    if not isinstance(clean["artifact_ref"], str) or not clean["artifact_ref"]:
        raise CampaignBasisRevalidationError("artifact_ref must be non-empty")
    if not isinstance(clean["content"], str):
        raise CampaignBasisRevalidationError("artifact evidence content must be text")
    return clean


def _normalize_effect_trace(value: dict[str, Any]) -> dict[str, Any]:
    clean = _strip_storage_metadata(value)
    required = {"schema", "effect", "event_refs"}
    if set(clean) != required or clean.get("schema") != EFFECT_TRACE_SCHEMA:
        raise CampaignBasisRevalidationError(
            "effect trace fields are not exact raw evidence"
        )
    if not isinstance(clean["effect"], str) or not clean["effect"]:
        raise CampaignBasisRevalidationError("effect must be non-empty")
    refs = clean["event_refs"]
    if (
        not isinstance(refs, list)
        or not all(isinstance(ref, str) and ref for ref in refs)
        or len(refs) != len(set(refs))
    ):
        raise CampaignBasisRevalidationError(
            "event_refs must be a unique list of non-empty raw event references"
        )
    clean["event_refs"] = sorted(refs)
    return clean


def _normalize_raw_evidence(raw_evidence: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_evidence, list):
        raise CampaignBasisRevalidationError("raw_evidence must be a list")
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for value in raw_evidence:
        if not isinstance(value, dict):
            raise CampaignBasisRevalidationError("raw evidence rows must be objects")
        clean = _strip_storage_metadata(value)
        schema = clean.get("schema")
        if schema == ARTIFACT_EVIDENCE_SCHEMA:
            row = _normalize_artifact_evidence(value)
            key = (schema, row["artifact_ref"])
        elif schema == EFFECT_TRACE_SCHEMA:
            row = _normalize_effect_trace(value)
            key = (schema, row["effect"])
        else:
            raise CampaignBasisRevalidationError(
                "unsupported raw evidence schema; semantic verdict inputs are rejected"
            )
        if key in seen:
            raise CampaignBasisRevalidationError("duplicate raw evidence identity")
        seen.add(key)
        normalized.append(row)

    return sorted(normalized, key=lambda item: _canonical_bytes(item))


def _evidence_ref(value: dict[str, Any]) -> str:
    if value["schema"] == ARTIFACT_EVIDENCE_SCHEMA:
        identity = value["artifact_ref"]
    else:
        identity = value["effect"]
    return f"evidence:{value['schema']}:{identity}:sha256:{_sha256(value)}"


def _evaluate(
    campaign: dict[str, Any],
    candidate_basis_refs: list[str],
    raw_evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[str]]:
    artifact_rows = {
        row["artifact_ref"]: row
        for row in raw_evidence
        if row["schema"] == ARTIFACT_EVIDENCE_SCHEMA
    }
    effect_rows = {
        row["effect"]: row
        for row in raw_evidence
        if row["schema"] == EFFECT_TRACE_SCHEMA
    }

    records: list[dict[str, str]] = []
    used_refs: set[str] = set()

    for spec in _derived_specs(campaign):
        inspected = ""
        observed = UNRESOLVED

        if spec["kind"] == "QUALIFICATION_ARTIFACT":
            row = artifact_rows.get(spec["artifact_ref"])
            if row is not None:
                ref = _evidence_ref(row)
                used_refs.add(ref)
                current_blob = _git_blob_sha1(row["content"])
                current_basis_ref = (
                    f"qualification:{spec['artifact_ref']}@{current_blob}"
                )
                inspected = (
                    f"{ref};git_blob_sha1:{current_blob};"
                    f"basis_declared:{current_basis_ref in candidate_basis_refs}"
                )
                if current_basis_ref not in candidate_basis_refs:
                    observed = UNRESOLVED
                elif current_blob == spec["expected_blob_sha"]:
                    observed = ESTABLISHED
                else:
                    # A changed replacement may later be qualified by a stronger
                    # membrane. This v0 refuses to infer semantic equivalence.
                    observed = UNRESOLVED

        elif spec["kind"] == "NON_AUTHORIZATION":
            row = effect_rows.get(spec["effect"])
            if row is not None:
                ref = _evidence_ref(row)
                used_refs.add(ref)
                inspected = f"{ref};event_count:{len(row['event_refs'])}"
                observed = ESTABLISHED if not row["event_refs"] else FRACTURED

        records.append(
            {
                "requirement_id": spec["requirement_id"],
                "campaign_relevance_basis": spec["campaign_relevance_basis"],
                "historical_identity_or_relation": spec[
                    "historical_identity_or_relation"
                ],
                "raw_current_evidence_inspected": inspected,
                "test_relation": spec["test_relation"],
                "observed_result": observed,
            }
        )

    return records, sorted(used_refs)


def build_revalidation(request: dict[str, Any]) -> dict[str, Any]:
    """Build one basis-relative result from exact history and raw evidence."""
    required = {
        "schema",
        "revalidation_id",
        "campaign_bytes",
        "candidate_current_basis_refs",
        "raw_evidence",
        "adjudication_ref",
    }
    if not isinstance(request, dict) or set(request) != required:
        raise CampaignBasisRevalidationError(
            "revalidation request fields are not exact; answer-key inputs are rejected"
        )
    if request.get("schema") != REQUEST_SCHEMA:
        raise CampaignBasisRevalidationError("wrong revalidation request schema")
    if (
        not isinstance(request["revalidation_id"], str)
        or not request["revalidation_id"]
    ):
        raise CampaignBasisRevalidationError("revalidation_id must be non-empty")
    if (
        not isinstance(request["adjudication_ref"], str)
        or not request["adjudication_ref"]
    ):
        raise CampaignBasisRevalidationError("adjudication_ref must be non-empty")

    campaign = _load_exact_campaign(request["campaign_bytes"])
    candidate_refs = _validate_basis_refs(request["candidate_current_basis_refs"])
    raw_evidence = _normalize_raw_evidence(request["raw_evidence"])

    requirements, evidence_refs = _evaluate(
        campaign,
        candidate_refs,
        raw_evidence,
    )
    observed = {row["observed_result"] for row in requirements}
    if FRACTURED in observed:
        disposition = NOT_APPLICABLE
    elif UNRESOLVED in observed:
        disposition = INSUFFICIENT_BASIS
    else:
        disposition = CURRENTLY_APPLICABLE

    result: dict[str, Any] = {
        "schema": RESULT_SCHEMA,
        "revalidation_id": request["revalidation_id"],
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": object_sha256(campaign),
        "historical_basis_refs": list(campaign["basis_refs"]),
        "historical_basis_sha256": object_sha256(campaign["basis_refs"]),
        "candidate_current_basis_refs": candidate_refs,
        "candidate_current_basis_sha256": object_sha256(candidate_refs),
        "derived_continuity_requirements": requirements,
        "evidence_refs": evidence_refs,
        "disposition": disposition,
        "adjudication_ref": request["adjudication_ref"],
        "authority_effect": "NONE",
        "adoption_effect": "NONE",
        "selection_effect": "NONE",
        "standing_effect": "NONE",
        "execution_effect": "NONE",
        "priority_effect": "NONE",
        "scheduler_effect": "NONE",
    }
    return result


def validate_revalidation(
    result: dict[str, Any],
    campaign: dict[str, Any],
) -> None:
    validate_campaign(campaign)
    required = {
        "schema",
        "revalidation_id",
        "campaign_id",
        "campaign_sha256",
        "historical_basis_refs",
        "historical_basis_sha256",
        "candidate_current_basis_refs",
        "candidate_current_basis_sha256",
        "derived_continuity_requirements",
        "evidence_refs",
        "disposition",
        "adjudication_ref",
        *_EFFECT_FIELDS,
    }
    if not isinstance(result, dict) or set(result) != required:
        raise CampaignBasisRevalidationError("revalidation result fields are not exact")
    if result["schema"] != RESULT_SCHEMA:
        raise CampaignBasisRevalidationError("wrong revalidation result schema")
    if not result["revalidation_id"] or not result["adjudication_ref"]:
        raise CampaignBasisRevalidationError(
            "revalidation_id and adjudication_ref must be non-empty"
        )
    if result["campaign_id"] != campaign["campaign_id"]:
        raise CampaignBasisRevalidationError("campaign_id mismatch")
    if result["campaign_sha256"] != object_sha256(campaign):
        raise CampaignBasisRevalidationError("campaign identity mismatch")
    if result["historical_basis_refs"] != campaign["basis_refs"]:
        raise CampaignBasisRevalidationError("historical basis bytes changed")
    if result["historical_basis_sha256"] != object_sha256(campaign["basis_refs"]):
        raise CampaignBasisRevalidationError("historical basis identity mismatch")
    candidate_refs = _validate_basis_refs(result["candidate_current_basis_refs"])
    if result["candidate_current_basis_sha256"] != object_sha256(candidate_refs):
        raise CampaignBasisRevalidationError("candidate current basis identity mismatch")
    if result["disposition"] not in DISPOSITIONS:
        raise CampaignBasisRevalidationError("invalid revalidation disposition")
    for field in _EFFECT_FIELDS:
        if result[field] != "NONE":
            raise CampaignBasisRevalidationError(f"{field} must remain NONE")

    requirements = result["derived_continuity_requirements"]
    if not isinstance(requirements, list):
        raise CampaignBasisRevalidationError(
            "derived_continuity_requirements must be a list"
        )
    expected_ids = [spec["requirement_id"] for spec in _derived_specs(campaign)]
    actual_ids: list[str] = []
    requirement_fields = {
        "requirement_id",
        "campaign_relevance_basis",
        "historical_identity_or_relation",
        "raw_current_evidence_inspected",
        "test_relation",
        "observed_result",
    }
    for row in requirements:
        if not isinstance(row, dict) or set(row) != requirement_fields:
            raise CampaignBasisRevalidationError(
                "derived requirement record fields are not exact"
            )
        if row["observed_result"] not in OBSERVED_RESULTS:
            raise CampaignBasisRevalidationError(
                "invalid derived requirement observed_result"
            )
        actual_ids.append(row["requirement_id"])
    if actual_ids != expected_ids:
        raise CampaignBasisRevalidationError(
            "derived requirement set/order does not match deterministic campaign grounding"
        )

    refs = result["evidence_refs"]
    if (
        not isinstance(refs, list)
        or not all(isinstance(ref, str) and ref for ref in refs)
        or refs != sorted(set(refs))
    ):
        raise CampaignBasisRevalidationError(
            "evidence_refs must be sorted unique durable identities"
        )


class CampaignBasisRevalidationStore:
    """Dedicated append-only store for basis-relative revalidation results."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS campaign_basis_revalidations(
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    revalidation_id TEXT UNIQUE NOT NULL,
                    result_sha256 TEXT NOT NULL,
                    campaign_id TEXT NOT NULL,
                    campaign_sha256 TEXT NOT NULL,
                    candidate_current_basis_sha256 TEXT NOT NULL,
                    disposition TEXT NOT NULL,
                    result_json TEXT NOT NULL
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

    def append(
        self,
        result: dict[str, Any],
        *,
        campaign: dict[str, Any],
    ) -> dict[str, Any]:
        validate_revalidation(result, campaign)
        digest = object_sha256(result)
        rendered = _canonical_bytes(result).decode("utf-8")

        conn = self._connect()
        try:
            existing = conn.execute(
                """
                SELECT result_sha256
                FROM campaign_basis_revalidations
                WHERE revalidation_id=?
                """,
                (result["revalidation_id"],),
            ).fetchone()
            if existing is not None:
                if existing["result_sha256"] != digest:
                    raise CampaignBasisRevalidationError(
                        "revalidation_id reused with different durable bytes"
                    )
                return {
                    "revalidation_id": result["revalidation_id"],
                    "result_sha256": digest,
                    "idempotent_replay": True,
                }

            conn.execute(
                """
                INSERT INTO campaign_basis_revalidations(
                    revalidation_id,
                    result_sha256,
                    campaign_id,
                    campaign_sha256,
                    candidate_current_basis_sha256,
                    disposition,
                    result_json
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    result["revalidation_id"],
                    digest,
                    result["campaign_id"],
                    result["campaign_sha256"],
                    result["candidate_current_basis_sha256"],
                    result["disposition"],
                    rendered,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return {
            "revalidation_id": result["revalidation_id"],
            "result_sha256": digest,
            "idempotent_replay": False,
        }

    def history(self, campaign_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT seq,result_json
                FROM campaign_basis_revalidations
                WHERE campaign_id=?
                ORDER BY seq
                """,
                (campaign_id,),
            ).fetchall()
        finally:
            conn.close()
        out: list[dict[str, Any]] = []
        for row in rows:
            value = json.loads(row["result_json"])
            value["_seq"] = row["seq"]
            out.append(value)
        return out

    @staticmethod
    def durable_object(history_row: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(history_row, dict):
            raise CampaignBasisRevalidationError("history row must be an object")
        return {
            key: value
            for key, value in history_row.items()
            if key not in _STORAGE_METADATA
        }

    def current_applicability(
        self,
        campaign: dict[str, Any],
        *,
        current_basis_refs: list[str],
    ) -> dict[str, Any]:
        validate_campaign(campaign)
        refs = _validate_basis_refs(current_basis_refs)
        campaign_sha = object_sha256(campaign)
        basis_sha = object_sha256(refs)
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT revalidation_id,result_json
                FROM campaign_basis_revalidations
                WHERE campaign_sha256=?
                  AND candidate_current_basis_sha256=?
                  AND disposition=?
                ORDER BY seq
                """,
                (campaign_sha, basis_sha, CURRENTLY_APPLICABLE),
            ).fetchall()
        finally:
            conn.close()

        if not rows:
            return {
                "campaign_id": campaign["campaign_id"],
                "campaign_sha256": campaign_sha,
                "current_basis_refs": refs,
                "current_basis_sha256": basis_sha,
                "applicability": "NOT_ESTABLISHED",
                "revalidation_ids": [],
                "adoption_effect": "NONE",
                "selection_effect": "NONE",
                "standing_effect": "NONE",
                "authority_effect": "NONE",
                "execution_effect": "NONE",
                "priority_effect": "NONE",
                "scheduler_effect": "NONE",
            }

        return {
            "campaign_id": campaign["campaign_id"],
            "campaign_sha256": campaign_sha,
            "current_basis_refs": refs,
            "current_basis_sha256": basis_sha,
            "applicability": CURRENTLY_APPLICABLE,
            "revalidation_ids": [row["revalidation_id"] for row in rows],
            "adoption_effect": "NONE",
            "selection_effect": "NONE",
            "standing_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "priority_effect": "NONE",
            "scheduler_effect": "NONE",
        }
