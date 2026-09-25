"""Bind an admitted successor to one-shot authority consumption.

This layer composes an already verified/admitted successor with the existing
single-process authority-consumption substrate. It does not create admission,
authority, settlement, or scientific standing.

The exact composition receipt, successor candidate, and current authority
binding must still agree immediately before authority is consumed.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from src.coordination.authority_binding_v0 import (
    AuthorityBindingError,
    VERIFIED,
    verify_current_authority,
)
from src.coordination.verified_authority_admission_v0 import (
    RECEIPT_TYPE as COMPOSITION_RECEIPT_TYPE,
    successor_authority_coordinates,
    validate_successor_candidate,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    _STATE_LOCK as _AUTHORITY_STATE_LOCK,
    canonical_sha256,
    consume_authority_once,
)


DECISION_TYPE = "ADMITTED_AUTHORITY_CONSUMPTION_DECISION_V0"
RECEIPT_TYPE = "ADMITTED_AUTHORITY_CONSUMPTION_RECEIPT_V0"


class AdmittedAuthorityConsumptionError(RuntimeError):
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
        "scientific_standing_effect": "NONE",
    }


def _composition_material(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "successor_id": receipt.get("successor_id"),
        "successor_integrity_sha256": receipt.get("successor_integrity_sha256"),
        "authority_binding_id": receipt.get("authority_binding_id"),
        "authority_state_sha256": receipt.get("authority_state_sha256"),
        "authority_request_sha256": receipt.get("authority_request_sha256"),
        "authority_input_sha256": receipt.get("authority_input_sha256"),
        "atomic_admission_id": receipt.get("atomic_admission_id"),
        "work_attempt_id": receipt.get("work_attempt_id"),
        "seat_id": receipt.get("seat_id"),
        "occupant_id": receipt.get("occupant_id"),
        "wake_generation": receipt.get("wake_generation"),
    }


def validate_composition_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise AdmittedAuthorityConsumptionError(
            "composition receipt must be an object"
        )
    retained = dict(receipt)
    if retained.get("object_type") != COMPOSITION_RECEIPT_TYPE:
        raise AdmittedAuthorityConsumptionError(
            "composition receipt object_type mismatch"
        )
    if retained.get("authority_input_posture") != "VERIFIED_CURRENT_BINDING":
        raise AdmittedAuthorityConsumptionError(
            "composition receipt authority posture mismatch"
        )
    if retained.get("authority_verification") != VERIFIED:
        raise AdmittedAuthorityConsumptionError(
            "composition receipt authority verification mismatch"
        )
    if retained.get("authority_consumed") is not False:
        raise AdmittedAuthorityConsumptionError(
            "composition receipt does not represent unconsumed authority"
        )
    if retained.get("execution_performed") is not False:
        raise AdmittedAuthorityConsumptionError(
            "composition receipt already claims execution"
        )
    material = _composition_material(retained)
    for field, value in material.items():
        if field == "wake_generation":
            if not isinstance(value, int) or value < 0:
                raise AdmittedAuthorityConsumptionError(
                    "composition receipt wake_generation invalid"
                )
        elif not isinstance(value, str) or not value:
            raise AdmittedAuthorityConsumptionError(
                f"composition receipt {field} missing"
            )
    expected = (
        "verified-authority-atomic-admission:sha256:"
        + canonical_sha256(material)
    )
    if retained.get("composition_id") != expected:
        raise AdmittedAuthorityConsumptionError(
            "composition receipt identity mismatch"
        )
    return retained


def consume_admitted_authority_once(
    *,
    composition_receipt: Mapping[str, Any],
    successor_candidate: Mapping[str, Any],
    authority_envelope: Mapping[str, Any],
    attempting_principal_id: str,
    authority_store: LocalAuthorityStateStore,
    invoke: Callable[[], Any],
    clock: Callable[[], str],
) -> dict[str, Any]:
    """Consume the exact admitted successor's current authority at most once.

    Same-process authority state is held from current-binding verification
    through reservation/invocation/consumption so the verified binding cannot
    be replaced between the check and the one-shot consumption boundary.
    """
    try:
        composition = validate_composition_receipt(composition_receipt)
        successor = validate_successor_candidate(successor_candidate)
    except Exception as exc:
        return _blocked("admission_or_successor_invalid", error=str(exc))

    if composition["successor_id"] != successor["successor_id"]:
        return _blocked("composition_successor_id_mismatch")
    if composition["successor_integrity_sha256"] != successor["integrity_sha256"]:
        return _blocked("composition_successor_integrity_mismatch")

    expected_coordinates = successor_authority_coordinates(successor)
    if authority_envelope.get("request_sha256") != expected_coordinates["request_sha256"]:
        return _blocked("authority_request_successor_mismatch")
    if authority_envelope.get("input_sha256") != expected_coordinates["input_sha256"]:
        return _blocked("authority_input_successor_mismatch")

    with _AUTHORITY_STATE_LOCK:
        try:
            binding = verify_current_authority(
                envelope=authority_envelope,
                attempting_principal_id=attempting_principal_id,
                store=authority_store,
            )
        except AuthorityBindingError as exc:
            return _blocked("authority_verification_failed", error=str(exc))

        if binding["binding_id"] != composition["authority_binding_id"]:
            return _blocked("composition_binding_id_mismatch")
        if binding["authority_state_sha256"] != composition["authority_state_sha256"]:
            return _blocked("composition_authority_state_mismatch")
        if binding["request_sha256"] != composition["authority_request_sha256"]:
            return _blocked("composition_authority_request_mismatch")
        if binding["input_sha256"] != composition["authority_input_sha256"]:
            return _blocked("composition_authority_input_mismatch")

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
        "composition_id": composition["composition_id"],
        "atomic_admission_id": composition["atomic_admission_id"],
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "authority_binding_id": binding["binding_id"],
        "authority_consumption_receipt_id": authority_receipt["receipt_id"],
        "authority_reservation_id": authority_receipt["reservation_id"],
        "capability_id": authority_receipt["capability_id"],
        "work_attempt_id": composition["work_attempt_id"],
    }
    receipt = {
        "object_type": RECEIPT_TYPE,
        **chain_material,
        "consumption_id": (
            "admitted-authority-consumption:sha256:"
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
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One exact composed admission was rebound to the same current "
            "single-process authority state and crossed one caller-supplied "
            "invocation callback under one-shot consumption. This does not "
            "establish model execution, result witnessing, settlement, or "
            "cross-process atomicity."
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
        "scientific_standing_effect": "NONE",
    }
