"""Consume one exact materialized-work admission authority at most once.

This layer composes the exact materialized-work admission receipt with the
existing one-shot authority-consumption substrate. It preserves exact successor,
work-spec, and materialized-unit identities across the consumption boundary.

It does not create authority, admission, settlement, external consequence, or
scientific standing. The supplied callback is the only invocation boundary.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from src.coordination.authority_binding_v0 import (
    AuthorityBindingError,
    verify_current_authority,
)
from src.coordination.materialized_unit_authority_admission_v0 import (
    RECEIPT_TYPE as EXACT_ADMISSION_RECEIPT_TYPE,
    materialized_unit_authority_coordinates,
    validate_bound_work_spec,
    validate_materialized_unit_binding,
)
from src.coordination.verified_authority_admission_v0 import validate_successor_candidate
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    _STATE_LOCK as _AUTHORITY_STATE_LOCK,
    canonical_sha256,
    consume_authority_once,
)


DECISION_TYPE = "MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_DECISION_V0"
RECEIPT_TYPE = "MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_RECEIPT_V0"


class MaterializedAdmittedAuthorityConsumptionError(RuntimeError):
    pass


def _blocked(blocker: str, *, error: str | None = None) -> dict[str, Any]:
    return {
        "object_type": DECISION_TYPE,
        "consumed": False,
        "invocation_performed": False,
        "blockers": [blocker],
        "receipt": None,
        "error": error,
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
    }


def _receipt_material(receipt: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "successor_id",
        "successor_integrity_sha256",
        "materialized_work_item_id",
        "materialized_unit_integrity_sha256",
        "work_spec_id",
        "work_spec_integrity_sha256",
        "authority_binding_id",
        "authority_state_sha256",
        "authority_request_sha256",
        "authority_input_sha256",
        "atomic_admission_id",
        "work_attempt_id",
        "seat_id",
        "occupant_id",
        "wake_generation",
    )
    return {field: receipt.get(field) for field in fields}


def validate_exact_admission_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise MaterializedAdmittedAuthorityConsumptionError(
            "exact admission receipt must be an object"
        )
    retained = dict(receipt)
    if retained.get("object_type") != EXACT_ADMISSION_RECEIPT_TYPE:
        raise MaterializedAdmittedAuthorityConsumptionError(
            "exact admission receipt type mismatch"
        )
    if retained.get("authority_input_posture") != (
        "VERIFIED_CURRENT_EXACT_MATERIALIZED_WORK_BINDING"
    ):
        raise MaterializedAdmittedAuthorityConsumptionError(
            "exact admission receipt authority posture mismatch"
        )
    if retained.get("authority_consumed") is not False:
        raise MaterializedAdmittedAuthorityConsumptionError(
            "exact admission receipt must represent unconsumed authority"
        )
    if retained.get("execution_performed") is not False:
        raise MaterializedAdmittedAuthorityConsumptionError(
            "exact admission receipt already claims execution"
        )

    material = _receipt_material(retained)
    for field, value in material.items():
        if field == "wake_generation":
            if not isinstance(value, int) or value < 0:
                raise MaterializedAdmittedAuthorityConsumptionError(
                    "exact admission receipt wake_generation invalid"
                )
        elif not isinstance(value, str) or not value:
            raise MaterializedAdmittedAuthorityConsumptionError(
                f"exact admission receipt {field} missing"
            )

    expected = (
        "materialized-unit-verified-authority-atomic-admission:sha256:"
        + canonical_sha256(material)
    )
    if retained.get("composition_id") != expected:
        raise MaterializedAdmittedAuthorityConsumptionError(
            "exact admission receipt identity mismatch"
        )
    return retained


def consume_materialized_admitted_authority_once(
    *,
    admission_receipt: Mapping[str, Any],
    successor_candidate: Mapping[str, Any],
    work_spec: Mapping[str, Any],
    materialized_unit: Mapping[str, Any],
    authority_envelope: Mapping[str, Any],
    attempting_principal_id: str,
    authority_store: LocalAuthorityStateStore,
    invoke: Callable[[], Any],
    clock: Callable[[], str],
) -> dict[str, Any]:
    """Consume one exact admitted materialized-work authority at most once."""
    try:
        admission = validate_exact_admission_receipt(admission_receipt)
        successor = validate_successor_candidate(successor_candidate)
        spec = validate_bound_work_spec(
            successor_candidate=successor,
            work_spec=work_spec,
        )
        unit = validate_materialized_unit_binding(
            successor_candidate=successor,
            work_spec=spec,
            materialized_unit=materialized_unit,
        )
    except Exception as exc:
        return _blocked("admission_or_materialized_work_invalid", error=str(exc))

    exact_fields = {
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "materialized_work_item_id": unit["identity"]["work_item_id"],
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "work_spec_id": spec["work_spec_id"],
        "work_spec_integrity_sha256": spec["integrity_sha256"],
    }
    for field, expected in exact_fields.items():
        if admission.get(field) != expected:
            return _blocked(f"admission_{field}_mismatch")

    expected_coordinates = materialized_unit_authority_coordinates(
        successor_candidate=successor,
        work_spec=spec,
        materialized_unit=unit,
    )
    if authority_envelope.get("request_sha256") != expected_coordinates["request_sha256"]:
        return _blocked("authority_request_materialized_work_mismatch")
    if authority_envelope.get("input_sha256") != expected_coordinates["input_sha256"]:
        return _blocked("authority_input_materialized_unit_mismatch")

    with _AUTHORITY_STATE_LOCK:
        try:
            binding = verify_current_authority(
                envelope=authority_envelope,
                attempting_principal_id=attempting_principal_id,
                store=authority_store,
            )
        except AuthorityBindingError as exc:
            return _blocked("authority_verification_failed", error=str(exc))

        exact_binding_fields = {
            "binding_id": "authority_binding_id",
            "authority_state_sha256": "authority_state_sha256",
            "request_sha256": "authority_request_sha256",
            "input_sha256": "authority_input_sha256",
        }
        for binding_field, admission_field in exact_binding_fields.items():
            if binding.get(binding_field) != admission.get(admission_field):
                return _blocked(f"admission_{admission_field}_mismatch")

        invocation = consume_authority_once(
            authority_envelope,
            attempting_principal_id=attempting_principal_id,
            store=authority_store,
            invoke=invoke,
            clock=clock,
        )

    if invocation.get("decision") != "INVOKED":
        return _blocked(
            "authority_consumption_denied",
            error=str((invocation.get("witness") or {}).get("reason")),
        )

    authority_receipt = invocation["receipt"]
    chain_material = {
        "composition_id": admission["composition_id"],
        "atomic_admission_id": admission["atomic_admission_id"],
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "materialized_work_item_id": unit["identity"]["work_item_id"],
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "work_spec_id": spec["work_spec_id"],
        "work_spec_integrity_sha256": spec["integrity_sha256"],
        "authority_binding_id": binding["binding_id"],
        "authority_consumption_receipt_id": authority_receipt["receipt_id"],
        "authority_reservation_id": authority_receipt["reservation_id"],
        "capability_id": authority_receipt["capability_id"],
        "work_attempt_id": admission["work_attempt_id"],
    }
    receipt = {
        "object_type": RECEIPT_TYPE,
        **chain_material,
        "consumption_id": (
            "materialized-admitted-authority-consumption:sha256:"
            + canonical_sha256(chain_material)
        ),
        "authority_status_after": authority_receipt["status"],
        "authority_remaining_uses_after": authority_receipt[
            "post_use_remaining_uses"
        ],
        "authority_consumed": True,
        "invocation_performed": True,
        "invocation_count": authority_receipt["invocation_count"],
        "authority_effect": "NONE",
        "consumption_effect": "CONSUMED_ONE_USE",
        "execution_effect": "CALLBACK_BOUNDARY_ONLY",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One exact admitted materialized-work object was rebound to the same "
            "current one-use local authority state and crossed one caller-supplied "
            "callback under one-shot consumption. The receipt conserves exact "
            "successor, work-spec, and materialized-unit identities. This does not "
            "establish semantic correctness, external consequence, settlement, "
            "production execution, or cross-process atomicity."
        ),
    }
    return {
        "object_type": DECISION_TYPE,
        "consumed": True,
        "invocation_performed": True,
        "blockers": [],
        "receipt": receipt,
        "authority_consumption_receipt": authority_receipt,
        "invocation_result": invocation["invocation_result"],
        "authority_effect": "NONE",
        "consumption_effect": "CONSUMED_ONE_USE",
        "execution_effect": "CALLBACK_BOUNDARY_ONLY",
        "scientific_standing_effect": "NONE",
    }
