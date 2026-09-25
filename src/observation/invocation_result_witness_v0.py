"""Deterministic immutable witness for one successful invocation return.

This module records exact observable chain identities and raw callback output.
It performs no I/O, settlement, semantic interpretation, Atlas mutation,
authority change, or scientific promotion.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping

from src.coordination.admitted_authority_consumption_v0 import (
    RECEIPT_TYPE as CONSUMPTION_RECEIPT_TYPE,
)
from src.runtime.local_authority_consumption_v0 import canonical_sha256


WITNESS_TYPE = "INVOCATION_RESULT_WITNESS_V0"


class InvocationResultWitnessError(ValueError):
    pass


_CHAIN_FIELDS = (
    "composition_id",
    "atomic_admission_id",
    "successor_id",
    "successor_integrity_sha256",
    "authority_binding_id",
    "authority_consumption_receipt_id",
    "authority_reservation_id",
    "capability_id",
    "work_attempt_id",
)


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvocationResultWitnessError(f"{field} must be a non-empty string")
    return value


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise InvocationResultWitnessError(
            "raw output must be canonical-JSON serializable"
        ) from exc
    return text.encode("utf-8")


def _validate_consumption_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise InvocationResultWitnessError("consumption receipt must be an object")

    retained = copy.deepcopy(dict(receipt))
    if retained.get("object_type") != CONSUMPTION_RECEIPT_TYPE:
        raise InvocationResultWitnessError("consumption receipt type mismatch")
    if retained.get("authority_consumed") is not True:
        raise InvocationResultWitnessError(
            "consumption receipt must show authority_consumed=true"
        )
    if retained.get("invocation_performed") is not True:
        raise InvocationResultWitnessError(
            "consumption receipt must show invocation_performed=true"
        )
    if retained.get("invocation_count") != 1:
        raise InvocationResultWitnessError(
            "consumption receipt must show invocation_count=1"
        )
    if retained.get("authority_status_after") != "CONSUMED":
        raise InvocationResultWitnessError(
            "consumption receipt must show authority_status_after=CONSUMED"
        )
    if retained.get("authority_remaining_uses_after") != 0:
        raise InvocationResultWitnessError(
            "consumption receipt must show authority_remaining_uses_after=0"
        )

    chain = {}
    for field in _CHAIN_FIELDS:
        chain[field] = _required_text(retained.get(field), field)

    expected_consumption_id = (
        "admitted-authority-consumption:sha256:" + canonical_sha256(chain)
    )
    if retained.get("consumption_id") != expected_consumption_id:
        raise InvocationResultWitnessError("consumption receipt identity mismatch")

    return retained


def build_invocation_result_witness(
    *,
    consumption_receipt: Mapping[str, Any],
    raw_output: Any,
    adapter_identity: str,
    observer_limitations: list[str] | tuple[str, ...],
    model_identity: str | None = None,
) -> dict[str, Any]:
    """Build one deterministic immutable result witness from explicit inputs."""

    receipt = _validate_consumption_receipt(consumption_receipt)
    adapter = _required_text(adapter_identity, "adapter_identity")

    if model_identity is not None:
        model = _required_text(model_identity, "model_identity")
    else:
        model = None

    if not isinstance(observer_limitations, (list, tuple)):
        raise InvocationResultWitnessError(
            "observer_limitations must be a list or tuple"
        )
    limitations = [
        _required_text(item, "observer_limitations[]")
        for item in observer_limitations
    ]

    raw_output_copy = copy.deepcopy(raw_output)
    raw_output_bytes = _canonical_json_bytes(raw_output_copy)
    raw_output_sha256 = hashlib.sha256(raw_output_bytes).hexdigest()

    witness_core = {
        "consumption_id": receipt["consumption_id"],
        "composition_id": receipt["composition_id"],
        "atomic_admission_id": receipt["atomic_admission_id"],
        "successor_id": receipt["successor_id"],
        "successor_integrity_sha256": receipt["successor_integrity_sha256"],
        "authority_binding_id": receipt["authority_binding_id"],
        "authority_consumption_receipt_id": receipt[
            "authority_consumption_receipt_id"
        ],
        "authority_reservation_id": receipt["authority_reservation_id"],
        "capability_id": receipt["capability_id"],
        "work_attempt_id": receipt["work_attempt_id"],
        "adapter_identity": adapter,
        "model_identity": model,
        "raw_output_sha256": raw_output_sha256,
    }

    unresolved_fields = []
    if model is None:
        unresolved_fields.append("model_identity")

    witness = {
        "object_type": WITNESS_TYPE,
        **witness_core,
        "witness_id": (
            "invocation-result-witness:sha256:" + canonical_sha256(witness_core)
        ),
        "raw_output": raw_output_copy,
        "raw_output_canonical_json": raw_output_bytes.decode("utf-8"),
        "measured_fields": [
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
        ] + ([] if model is None else ["model_identity"]),
        "unresolved_fields": unresolved_fields,
        "observer_limitations": limitations,
        "semantic_interpretation": "NONE",
        "settlement_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "external_effect_inferred": False,
        "claim_ceiling": (
            "Deterministic immutable witness that one already-consumed exact work "
            "attempt returned the supplied raw callback output under the supplied "
            "adapter/model metadata. It does not establish semantic correctness, "
            "external consequence, settlement, qualification, or authority."
        ),
    }
    return witness
