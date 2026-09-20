"""Bounded exact-content relation entitlement candidate for Concordance Cockpit v0.

This module answers only whether exact frozen artifact bytes explicitly carry an
exact developmental relation tuple. It does not establish the truth, authority,
standing, or causal validity of the claim source.

    EXACT CLAIM DECLARED
    !=
    CLAIM SOURCE ENTITLED
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


SCHEMA_VERSION = "concordance_edge_relation_claims_v0"
ESTABLISHED = "ESTABLISHED"
NOT_ESTABLISHED = "NOT_ESTABLISHED"

_ALLOWED_RELATIONS = {
    "RECORDED",
    "REFERENCED_BY",
    "MOTIVATED",
    "CONSTRAINS",
    "INCORPORATED",
    "TEMPORALLY_PRECEDES",
}


@dataclass(frozen=True)
class RelationEntitlementResult:
    status: str
    reason: str
    artifact_sha256: str


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _parse_claim_artifact(artifact_bytes: bytes) -> dict[str, Any]:
    value = json.loads(artifact_bytes)
    if not isinstance(value, dict):
        raise ValueError("artifact must be a JSON object")
    if set(value) != {"schema_version", "artifact_id", "relation_claims"}:
        raise ValueError("unexpected top-level claim artifact shape")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported claim artifact schema")
    if not isinstance(value["artifact_id"], str) or not value["artifact_id"]:
        raise ValueError("artifact_id must be non-empty")
    claims = value["relation_claims"]
    if not isinstance(claims, list):
        raise ValueError("relation_claims must be a list")

    normalized: list[dict[str, str]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("relation claim must be an object")
        if set(claim) != {"from_ref", "relation_type", "to_ref"}:
            raise ValueError("unexpected relation claim shape")
        for key in ("from_ref", "relation_type", "to_ref"):
            if not isinstance(claim[key], str) or not claim[key]:
                raise ValueError(f"{key} must be non-empty")
        if claim["relation_type"] not in _ALLOWED_RELATIONS:
            raise ValueError("unsupported relation_type")
        normalized.append(dict(claim))

    return {
        "schema_version": value["schema_version"],
        "artifact_id": value["artifact_id"],
        "relation_claims": normalized,
    }


def verify_exact_relation_claim(
    artifact_bytes: bytes,
    *,
    expected_sha256: str,
    expected_artifact_id: str,
    from_ref: str,
    relation_type: str,
    to_ref: str,
) -> RelationEntitlementResult:
    """Check only exact frozen-byte identity + exact relation tuple presence."""
    observed_sha256 = sha256_hex(artifact_bytes)
    if observed_sha256 != expected_sha256:
        return RelationEntitlementResult(
            NOT_ESTABLISHED,
            "ARTIFACT_IDENTITY_MISMATCH",
            observed_sha256,
        )

    try:
        artifact = _parse_claim_artifact(artifact_bytes)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return RelationEntitlementResult(
            NOT_ESTABLISHED,
            "INVALID_RELATION_CLAIM_ARTIFACT",
            observed_sha256,
        )

    if artifact["artifact_id"] != expected_artifact_id:
        return RelationEntitlementResult(
            NOT_ESTABLISHED,
            "ARTIFACT_ID_MISMATCH",
            observed_sha256,
        )

    requested = {
        "from_ref": from_ref,
        "relation_type": relation_type,
        "to_ref": to_ref,
    }
    if requested not in artifact["relation_claims"]:
        return RelationEntitlementResult(
            NOT_ESTABLISHED,
            "EXACT_RELATION_CLAIM_ABSENT",
            observed_sha256,
        )

    return RelationEntitlementResult(
        ESTABLISHED,
        "EXACT_FROZEN_RELATION_CLAIM_PRESENT",
        observed_sha256,
    )
