"""Compose current verified authority, one sealed successor, and atomic admission.

This V0 layer preserves the already-qualified atomic_admission_v0 primitive and
adds the missing relation:

    current exact authority
    + exact sealed successor candidate
    -> one same-process atomic admission attempt

The authority envelope must be issued for the exact successor candidate. This
layer does not consume authority, invoke a model, or execute work.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc
from src.coordination.atomic_admission_v0 import try_atomic_admission
from src.coordination.authority_binding_v0 import (
    AuthorityBindingError,
    VERIFIED,
    verify_current_authority,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    _STATE_LOCK as _AUTHORITY_STATE_LOCK,
    canonical_sha256,
)


DECISION_TYPE = "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_DECISION_V0"
RECEIPT_TYPE = "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_RECEIPT_V0"
SUCCESSOR_TYPE = "SUCCESSOR_CANDIDATE_V1"


class VerifiedAuthorityAtomicAdmissionError(RuntimeError):
    pass


def _blocked(blocker: str, *, error: str | None = None) -> dict[str, Any]:
    return {
        "object_type": DECISION_TYPE,
        "admitted": False,
        "blockers": [blocker],
        "receipt": None,
        "error": error,
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "model_invocation_effect": "NONE",
    }


def validate_successor_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(candidate, Mapping):
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate must be an object"
        )
    retained = dict(candidate)
    try:
        wc.verify_seal(retained)
    except Exception as exc:
        raise VerifiedAuthorityAtomicAdmissionError(
            f"successor candidate seal invalid: {exc}"
        ) from exc

    if retained.get("object_type") != SUCCESSOR_TYPE:
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate object_type mismatch"
        )
    if retained.get("candidate_posture") != "PROPOSED_NOT_ADMITTED":
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate is not PROPOSED_NOT_ADMITTED"
        )
    successor_id = retained.get("successor_id")
    if not isinstance(successor_id, str) or not successor_id.startswith(
        "successor:sha256:"
    ):
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate identity missing"
        )
    for field in (
        "campaign_id",
        "parent_work_item_id",
        "basis_id",
        "operative_frame_ref",
        "reconciliation_identity",
        "successor_posture",
    ):
        value = retained.get(field)
        if not isinstance(value, str) or not value.strip():
            raise VerifiedAuthorityAtomicAdmissionError(
                f"successor candidate {field} missing"
            )
    if retained.get("work_admission_effect") != "NONE":
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate already claims work admission"
        )
    if retained.get("authority_effect") != "NONE":
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate authority effect is not NONE"
        )
    if retained.get("execution_effect") != "NONE":
        raise VerifiedAuthorityAtomicAdmissionError(
            "successor candidate execution effect is not NONE"
        )
    return retained


def successor_authority_coordinates(
    successor_candidate: Mapping[str, Any],
) -> dict[str, str]:
    retained = validate_successor_candidate(successor_candidate)
    request_material = {
        "object_type": "VERIFIED_SUCCESSOR_ADMISSION_REQUEST_V0",
        "campaign_id": retained["campaign_id"],
        "parent_work_item_id": retained["parent_work_item_id"],
        "basis_id": retained["basis_id"],
        "operative_frame_ref": retained["operative_frame_ref"],
        "reconciliation_identity": retained["reconciliation_identity"],
        "successor_posture": retained["successor_posture"],
        "successor_id": retained["successor_id"],
    }
    return {
        "request_sha256": canonical_sha256(request_material),
        "input_sha256": retained["integrity_sha256"],
    }


def try_verified_authority_atomic_admission(
    *,
    store_dir: str | Path,
    authority_store: LocalAuthorityStateStore,
    authority_envelope: Mapping[str, Any],
    attempting_principal_id: str,
    successor_candidate: Mapping[str, Any],
    work_attempt_id: str,
    seat_id: str,
    occupant_id: str,
    wake_generation: int,
    dependency_satisfied: bool,
    frame_current: bool,
    no_hold: bool,
    control: Mapping[str, Any],
    initial_budget: Mapping[str, Any],
) -> dict[str, Any]:
    """Attempt one same-process admission from current authority + successor.

    The authority-state RLock is held from verification through the atomic
    admission decision so same-process authority mutation cannot interleave.
    Authority remains unconsumed.
    """
    try:
        successor = validate_successor_candidate(successor_candidate)
    except VerifiedAuthorityAtomicAdmissionError as exc:
        return _blocked("successor_candidate_invalid", error=str(exc))

    expected = successor_authority_coordinates(successor)

    with _AUTHORITY_STATE_LOCK:
        try:
            binding = verify_current_authority(
                envelope=authority_envelope,
                attempting_principal_id=attempting_principal_id,
                store=authority_store,
            )
        except AuthorityBindingError as exc:
            return _blocked("authority_verification_failed", error=str(exc))

        if binding.get("verification_posture") != VERIFIED:
            return _blocked("authority_not_verified_current")
        if binding.get("request_sha256") != expected["request_sha256"]:
            return _blocked("authority_request_successor_mismatch")
        if binding.get("input_sha256") != expected["input_sha256"]:
            return _blocked("authority_input_successor_mismatch")

        atomic = try_atomic_admission(
            store_dir=store_dir,
            campaign_id=successor["campaign_id"],
            work_item_id=successor["successor_id"],
            work_attempt_id=work_attempt_id,
            seat_id=seat_id,
            occupant_id=occupant_id,
            wake_generation=wake_generation,
            authority_coordinate=binding["binding_id"],
            authority_satisfied=True,
            dependency_satisfied=dependency_satisfied,
            frame_current=frame_current,
            no_hold=no_hold,
            control=control,
            initial_budget=initial_budget,
        )

    if atomic.get("admitted") is not True:
        return {
            "object_type": DECISION_TYPE,
            "admitted": False,
            "blockers": list(atomic.get("blockers") or []),
            "receipt": None,
            "verified_binding_id": binding["binding_id"],
            "successor_id": successor["successor_id"],
            "authority_effect": "NONE",
            "consumption_effect": "NONE",
            "execution_effect": "NONE",
            "model_invocation_effect": "NONE",
        }

    inner = atomic["receipt"]
    composition_material = {
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "authority_binding_id": binding["binding_id"],
        "authority_state_sha256": binding["authority_state_sha256"],
        "authority_request_sha256": binding["request_sha256"],
        "authority_input_sha256": binding["input_sha256"],
        "atomic_admission_id": inner["admission_id"],
        "work_attempt_id": work_attempt_id,
        "seat_id": seat_id,
        "occupant_id": occupant_id,
        "wake_generation": wake_generation,
    }
    receipt = {
        "object_type": RECEIPT_TYPE,
        **composition_material,
        "composition_id": (
            "verified-authority-atomic-admission:sha256:"
            + canonical_sha256(composition_material)
        ),
        "authority_input_posture": "VERIFIED_CURRENT_BINDING",
        "authority_verification": VERIFIED,
        "authority_remaining_uses_at_verification": 1,
        "authority_consumed": False,
        "underlying_atomic_receipt_type": inner["object_type"],
        "underlying_atomic_receipt_claim_unchanged": True,
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "execution_performed": False,
        "model_invocation_effect": "NONE",
        "claim_ceiling": (
            "Same-process composition of one current verified one-use local "
            "authority binding for the exact sealed successor candidate into "
            "one existing atomic local admission transition. Authority is not "
            "consumed; no model invocation or work execution occurs. This does "
            "not establish cross-process authority/admission atomicity."
        ),
    }
    return {
        "object_type": DECISION_TYPE,
        "admitted": True,
        "blockers": [],
        "receipt": receipt,
        "atomic_admission_receipt": inner,
        "atomic_state_sha256": atomic.get("state_sha256"),
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "model_invocation_effect": "NONE",
    }
