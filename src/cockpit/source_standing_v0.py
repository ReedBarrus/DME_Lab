"""Bounded source-standing candidate for EDGE_SOURCE_STANDING_001.

This module intentionally answers only:

    SOURCE_STANDING_FOR_CLAIM:
    ESTABLISHED | NOT_ESTABLISHED

It does not establish relation truth, adjudication, incorporation, global
authority, or general standing semantics.

Candidate mechanism:
    exact relation-content verification
    + exact signed standing bytes
    + one verifier-pinned Ed25519 grounding public key
    + exact relation-class membership
    + exact ordered endpoint-pair membership

The caller never supplies semantic answer labels such as "independent" or
"standing_valid".
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from src.cockpit.edge_entitlement_v0 import (
    ESTABLISHED as CLAIM_ESTABLISHED,
    verify_exact_relation_claim,
)


STANDING_SCHEMA_VERSION = "concordance_source_standing_v0"
DEVELOPMENTAL_RELATION_JURISDICTION = "DEVELOPMENTAL_RELATION_ISSUANCE"

SOURCE_STANDING_ESTABLISHED = "ESTABLISHED"
SOURCE_STANDING_NOT_ESTABLISHED = "NOT_ESTABLISHED"


@dataclass(frozen=True)
class SourceStandingResult:
    status: str
    reason: str
    standing_sha256: str | None


class SourceStandingCandidateError(ValueError):
    pass


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def key_fingerprint(public_key_raw: bytes) -> str:
    return sha256_hex(public_key_raw)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _parse_standing_basis(data: bytes) -> dict[str, Any]:
    value = json.loads(data)
    if not isinstance(value, dict):
        raise SourceStandingCandidateError("standing basis must be a JSON object")

    expected_keys = {
        "schema_version",
        "grant_id",
        "source_ref",
        "issuer_ref",
        "issuer_key_fingerprint",
        "jurisdiction",
        "relation_classes",
        "endpoint_pairs",
    }
    if set(value) != expected_keys:
        raise SourceStandingCandidateError("unexpected standing basis shape")

    if value["schema_version"] != STANDING_SCHEMA_VERSION:
        raise SourceStandingCandidateError("unsupported standing basis schema")

    for field in (
        "grant_id",
        "source_ref",
        "issuer_ref",
        "issuer_key_fingerprint",
        "jurisdiction",
    ):
        if not isinstance(value[field], str) or not value[field]:
            raise SourceStandingCandidateError(f"{field} must be a non-empty string")

    relation_classes = value["relation_classes"]
    if not isinstance(relation_classes, list) or any(
        not isinstance(item, str) or not item for item in relation_classes
    ):
        raise SourceStandingCandidateError(
            "relation_classes must be a list of non-empty strings"
        )

    endpoint_pairs = value["endpoint_pairs"]
    if not isinstance(endpoint_pairs, list):
        raise SourceStandingCandidateError("endpoint_pairs must be a list")

    normalized_pairs: list[dict[str, str]] = []
    for pair in endpoint_pairs:
        if not isinstance(pair, dict) or set(pair) != {"from_ref", "to_ref"}:
            raise SourceStandingCandidateError(
                "endpoint pair must contain exactly from_ref and to_ref"
            )
        if (
            not isinstance(pair["from_ref"], str)
            or not pair["from_ref"]
            or not isinstance(pair["to_ref"], str)
            or not pair["to_ref"]
        ):
            raise SourceStandingCandidateError(
                "endpoint pair refs must be non-empty strings"
            )
        normalized_pairs.append(dict(pair))

    return {
        "schema_version": value["schema_version"],
        "grant_id": value["grant_id"],
        "source_ref": value["source_ref"],
        "issuer_ref": value["issuer_ref"],
        "issuer_key_fingerprint": value["issuer_key_fingerprint"],
        "jurisdiction": value["jurisdiction"],
        "relation_classes": list(relation_classes),
        "endpoint_pairs": normalized_pairs,
    }


class SourceStandingEvaluatorV0:
    """Derive source-standing-for-claim from raw candidate inputs.

    The grounding public key is evaluator configuration, not a per-claim caller
    input. The corresponding private key is not represented in this class.
    """

    def __init__(self, *, grounding_public_key_raw: bytes):
        if not isinstance(grounding_public_key_raw, bytes):
            raise SourceStandingCandidateError(
                "grounding_public_key_raw must be bytes"
            )
        try:
            self._grounding_public_key = Ed25519PublicKey.from_public_bytes(
                grounding_public_key_raw
            )
        except ValueError as exc:
            raise SourceStandingCandidateError(
                "invalid grounding public key"
            ) from exc
        self._grounding_key_fingerprint = key_fingerprint(
            grounding_public_key_raw
        )

    def derive(
        self,
        *,
        claim_artifact_bytes: bytes,
        expected_claim_sha256: str,
        expected_claim_artifact_id: str,
        source_ref: str,
        from_ref: str,
        relation_type: str,
        to_ref: str,
        standing_basis_bytes: bytes | None,
        grounding_signature: bytes | None,
    ) -> SourceStandingResult:
        """Return only bounded source standing for the exact requested claim."""

        claim_result = verify_exact_relation_claim(
            claim_artifact_bytes,
            expected_sha256=expected_claim_sha256,
            expected_artifact_id=expected_claim_artifact_id,
            from_ref=from_ref,
            relation_type=relation_type,
            to_ref=to_ref,
        )
        if claim_result.status != CLAIM_ESTABLISHED:
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "EXACT_CLAIM_CONTENT_NOT_ESTABLISHED",
                None,
            )

        if standing_basis_bytes is None or grounding_signature is None:
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "NO_GROUNDED_STANDING_BASIS",
                None,
            )

        standing_sha256 = sha256_hex(standing_basis_bytes)

        try:
            self._grounding_public_key.verify(
                grounding_signature,
                standing_basis_bytes,
            )
        except InvalidSignature:
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "GROUNDING_SIGNATURE_INVALID",
                standing_sha256,
            )

        try:
            standing = _parse_standing_basis(standing_basis_bytes)
        except (
            SourceStandingCandidateError,
            json.JSONDecodeError,
            UnicodeDecodeError,
        ):
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "INVALID_STANDING_BASIS",
                standing_sha256,
            )

        if (
            standing["issuer_key_fingerprint"]
            != self._grounding_key_fingerprint
        ):
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "GROUNDING_KEY_FINGERPRINT_MISMATCH",
                standing_sha256,
            )

        if standing["source_ref"] != source_ref:
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "SOURCE_NOT_COVERED",
                standing_sha256,
            )

        if (
            standing["jurisdiction"]
            != DEVELOPMENTAL_RELATION_JURISDICTION
        ):
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "JURISDICTION_NOT_COVERED",
                standing_sha256,
            )

        if relation_type not in standing["relation_classes"]:
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "RELATION_CLASS_NOT_COVERED",
                standing_sha256,
            )

        requested_pair = {
            "from_ref": from_ref,
            "to_ref": to_ref,
        }
        if requested_pair not in standing["endpoint_pairs"]:
            return SourceStandingResult(
                SOURCE_STANDING_NOT_ESTABLISHED,
                "ENDPOINT_SCOPE_NOT_COVERED",
                standing_sha256,
            )

        return SourceStandingResult(
            SOURCE_STANDING_ESTABLISHED,
            "EXACT_TESTED_SOURCE_RELATION_SCOPE_STANDING_ESTABLISHED",
            standing_sha256,
        )
