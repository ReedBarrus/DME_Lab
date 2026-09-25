"""Field-level candidate settlement over one immutable invocation result witness.

The caller supplies the field dispositions and explicit settlement bases.
This module records that classification deterministically. It does not decide
semantic truth, qualify scientific standing, grant authority, execute work,
or rewrite the source witness.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.observation.invocation_result_witness_v0 import WITNESS_TYPE
from src.runtime.local_authority_consumption_v0 import canonical_sha256


SETTLEMENT_TYPE = "INVOCATION_RESULT_CANDIDATE_SETTLEMENT_V0"

CANDIDATE_ACCEPTED = "CANDIDATE_ACCEPTED"
CANDIDATE_HELD = "CANDIDATE_HELD"
CANDIDATE_REJECTED = "CANDIDATE_REJECTED"
UNRESOLVED = "UNRESOLVED"

ALLOWED_DISPOSITIONS = {
    CANDIDATE_ACCEPTED,
    CANDIDATE_HELD,
    CANDIDATE_REJECTED,
    UNRESOLVED,
}


class ResultSettlementError(ValueError):
    pass


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ResultSettlementError(f"{field} must be a non-empty string")
    return value


def _validate_witness(witness: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(witness, Mapping):
        raise ResultSettlementError("result witness must be an object")

    retained = copy.deepcopy(dict(witness))
    if retained.get("object_type") != WITNESS_TYPE:
        raise ResultSettlementError("result witness type mismatch")

    required = (
        "witness_id",
        "consumption_id",
        "composition_id",
        "atomic_admission_id",
        "successor_id",
        "successor_integrity_sha256",
        "authority_binding_id",
        "authority_consumption_receipt_id",
        "authority_reservation_id",
        "capability_id",
        "work_attempt_id",
        "adapter_identity",
        "raw_output_sha256",
    )
    for field in required:
        _required_text(retained.get(field), field)

    if not isinstance(retained.get("raw_output"), Mapping):
        raise ResultSettlementError(
            "v0 settlement requires raw_output to be an object"
        )
    if retained.get("settlement_effect") != "NONE":
        raise ResultSettlementError(
            "source witness already claims settlement effect"
        )
    if retained.get("semantic_interpretation") != "NONE":
        raise ResultSettlementError(
            "source witness already claims semantic interpretation"
        )
    if retained.get("external_effect_inferred") is not False:
        raise ResultSettlementError(
            "source witness must not infer external effect"
        )

    limitations = retained.get("observer_limitations")
    if not isinstance(limitations, list) or not all(
        isinstance(item, str) and item for item in limitations
    ):
        raise ResultSettlementError("observer_limitations invalid")

    witness_core = {
        "consumption_id": retained["consumption_id"],
        "composition_id": retained["composition_id"],
        "atomic_admission_id": retained["atomic_admission_id"],
        "successor_id": retained["successor_id"],
        "successor_integrity_sha256": retained[
            "successor_integrity_sha256"
        ],
        "authority_binding_id": retained["authority_binding_id"],
        "authority_consumption_receipt_id": retained[
            "authority_consumption_receipt_id"
        ],
        "authority_reservation_id": retained["authority_reservation_id"],
        "capability_id": retained["capability_id"],
        "work_attempt_id": retained["work_attempt_id"],
        "adapter_identity": retained["adapter_identity"],
        "model_identity": retained.get("model_identity"),
        "raw_output_sha256": retained["raw_output_sha256"],
        "observer_limitations": limitations,
    }
    expected_witness_id = (
        "invocation-result-witness:sha256:" + canonical_sha256(witness_core)
    )
    if retained["witness_id"] != expected_witness_id:
        raise ResultSettlementError("result witness identity mismatch")

    return retained


def build_candidate_settlement(
    *,
    result_witness: Mapping[str, Any],
    field_dispositions: Mapping[str, str],
    settlement_basis: Mapping[str, str],
    settlement_actor_identity: str,
) -> dict[str, Any]:
    """Record externally supplied field-level candidate settlement."""

    witness = _validate_witness(result_witness)
    actor = _required_text(
        settlement_actor_identity,
        "settlement_actor_identity",
    )

    if not isinstance(field_dispositions, Mapping) or not field_dispositions:
        raise ResultSettlementError(
            "field_dispositions must be a non-empty object"
        )
    if not isinstance(settlement_basis, Mapping):
        raise ResultSettlementError("settlement_basis must be an object")

    raw_output = witness["raw_output"]
    normalized_dispositions: dict[str, str] = {}
    normalized_basis: dict[str, str] = {}

    for field, disposition in sorted(field_dispositions.items()):
        _required_text(field, "field_dispositions key")
        if field not in raw_output:
            raise ResultSettlementError(
                f"settled field not present in raw output: {field}"
            )
        if disposition not in ALLOWED_DISPOSITIONS:
            raise ResultSettlementError(
                f"unsupported field disposition: {disposition}"
            )
        basis = _required_text(
            settlement_basis.get(field),
            f"settlement_basis[{field}]",
        )
        normalized_dispositions[field] = disposition
        normalized_basis[field] = basis

    extra_basis = sorted(
        set(settlement_basis) - set(normalized_dispositions)
    )
    if extra_basis:
        raise ResultSettlementError(
            "settlement basis supplied for unclassified fields: "
            + ", ".join(extra_basis)
        )

    accepted = [
        field
        for field, disposition in normalized_dispositions.items()
        if disposition == CANDIDATE_ACCEPTED
    ]
    held = [
        field
        for field, disposition in normalized_dispositions.items()
        if disposition == CANDIDATE_HELD
    ]
    rejected = [
        field
        for field, disposition in normalized_dispositions.items()
        if disposition == CANDIDATE_REJECTED
    ]
    unresolved = [
        field
        for field, disposition in normalized_dispositions.items()
        if disposition == UNRESOLVED
    ]

    settlement_core = {
        "source_witness_id": witness["witness_id"],
        "source_raw_output_sha256": witness["raw_output_sha256"],
        "source_work_attempt_id": witness["work_attempt_id"],
        "settlement_actor_identity": actor,
        "field_dispositions": normalized_dispositions,
        "settlement_basis": normalized_basis,
    }

    return {
        "object_type": SETTLEMENT_TYPE,
        **settlement_core,
        "settlement_id": (
            "invocation-result-candidate-settlement:sha256:"
            + canonical_sha256(settlement_core)
        ),
        "accepted_fields": accepted,
        "held_fields": held,
        "rejected_fields": rejected,
        "unresolved_fields": unresolved,
        "source_witness_preserved": True,
        "classification_source": "EXTERNALLY_SUPPLIED",
        "scientific_admission_created": False,
        "qualification_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "atlas_mutation_effect": "NONE",
        "claim_ceiling": (
            "Deterministic field-level candidate settlement over one immutable "
            "result witness using externally supplied dispositions and bases. "
            "It does not establish semantic truth, external consequence, "
            "scientific qualification, authority, execution, or Atlas mutation."
        ),
    }
