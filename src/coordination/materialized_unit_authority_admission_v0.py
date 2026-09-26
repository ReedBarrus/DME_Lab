"""Exact materialized-work authority binding into atomic admission.

This layer preserves the previously qualified successor-bound authority law and
adds a narrower composition for exact consequence-bearing work:

    exact successor
    + exact sealed work spec
    + exact sealed materialized workflow unit
    + current verified one-use authority for those exact coordinates
    -> one same-process atomic admission attempt

The authority envelope binds the exact materialized unit integrity as its input
and binds successor/work-spec/materialization lineage in its request hash.

Authority remains unconsumed. No model invocation or work execution occurs.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

from src.coordination import basis_workcycle_v1 as bw
from src.coordination import workcycle_v0 as wc
from src.coordination.atomic_admission_v0 import try_atomic_admission
from src.coordination.authority_binding_v0 import (
    AuthorityBindingError,
    VERIFIED,
    verify_current_authority,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    MATERIALIZATION_TYPE,
    WORK_SPEC_TYPE,
)
from src.coordination.verified_authority_admission_v0 import (
    VerifiedAuthorityAtomicAdmissionError,
    validate_successor_candidate,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    _STATE_LOCK as _AUTHORITY_STATE_LOCK,
    canonical_sha256,
)


DECISION_TYPE = "MATERIALIZED_UNIT_VERIFIED_AUTHORITY_ATOMIC_ADMISSION_DECISION_V0"
RECEIPT_TYPE = "MATERIALIZED_UNIT_VERIFIED_AUTHORITY_ATOMIC_ADMISSION_RECEIPT_V0"


class MaterializedUnitAuthorityAdmissionError(RuntimeError):
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


def validate_bound_work_spec(
    *,
    successor_candidate: Mapping[str, Any],
    work_spec: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        successor = validate_successor_candidate(successor_candidate)
    except VerifiedAuthorityAtomicAdmissionError as exc:
        raise MaterializedUnitAuthorityAdmissionError(str(exc)) from exc

    if not isinstance(work_spec, Mapping):
        raise MaterializedUnitAuthorityAdmissionError("work_spec must be an object")
    retained = copy.deepcopy(dict(work_spec))
    try:
        wc.verify_seal(retained)
    except Exception as exc:
        raise MaterializedUnitAuthorityAdmissionError(
            f"work_spec seal invalid: {exc}"
        ) from exc

    if retained.get("object_type") != WORK_SPEC_TYPE:
        raise MaterializedUnitAuthorityAdmissionError("work_spec type mismatch")
    if retained.get("spec_source") != "EXTERNALLY_SUPPLIED":
        raise MaterializedUnitAuthorityAdmissionError(
            "work_spec source must be EXTERNALLY_SUPPLIED"
        )
    required = {
        "source_successor_id": successor["successor_id"],
        "source_successor_integrity_sha256": successor["integrity_sha256"],
        "source_reconciliation_identity": successor["reconciliation_identity"],
        "source_next_pressure_basis": successor["next_pressure_basis"],
    }
    for field, expected in required.items():
        if retained.get(field) != expected:
            raise MaterializedUnitAuthorityAdmissionError(
                f"work_spec binding mismatch: {field}"
            )
    return retained


def validate_materialized_unit_binding(
    *,
    successor_candidate: Mapping[str, Any],
    work_spec: Mapping[str, Any],
    materialized_unit: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        successor = validate_successor_candidate(successor_candidate)
    except VerifiedAuthorityAtomicAdmissionError as exc:
        raise MaterializedUnitAuthorityAdmissionError(str(exc)) from exc
    spec = validate_bound_work_spec(
        successor_candidate=successor,
        work_spec=work_spec,
    )

    if not isinstance(materialized_unit, Mapping):
        raise MaterializedUnitAuthorityAdmissionError(
            "materialized_unit must be an object"
        )
    unit = copy.deepcopy(dict(materialized_unit))
    try:
        wc.verify_seal(unit)
        bw.validate_workflow_unit(unit)
    except Exception as exc:
        raise MaterializedUnitAuthorityAdmissionError(
            f"materialized unit invalid: {exc}"
        ) from exc

    identity = unit.get("identity")
    materialization = unit.get("materialization")
    if not isinstance(identity, Mapping):
        raise MaterializedUnitAuthorityAdmissionError(
            "materialized unit identity missing"
        )
    if not isinstance(materialization, Mapping):
        raise MaterializedUnitAuthorityAdmissionError(
            "materialized unit materialization record missing"
        )
    if materialization.get("object_type") != MATERIALIZATION_TYPE:
        raise MaterializedUnitAuthorityAdmissionError(
            "materialized unit materialization type mismatch"
        )

    exact = {
        "work_item_id": successor["successor_id"],
        "campaign_id": successor["campaign_id"],
        "parent_work_item_id": successor["parent_work_item_id"],
        "operative_frame_ref": successor["operative_frame_ref"],
    }
    for field, expected in exact.items():
        if identity.get(field) != expected:
            raise MaterializedUnitAuthorityAdmissionError(
                f"materialized unit identity mismatch: {field}"
            )

    materialized_exact = {
        "source_successor_id": successor["successor_id"],
        "source_successor_integrity_sha256": successor["integrity_sha256"],
        "source_reconciliation_identity": successor["reconciliation_identity"],
        "source_next_pressure_basis": successor["next_pressure_basis"],
        "work_spec_id": spec["work_spec_id"],
        "work_spec_integrity_sha256": spec["integrity_sha256"],
        "spec_source": "EXTERNALLY_SUPPLIED",
    }
    for field, expected in materialized_exact.items():
        if materialization.get(field) != expected:
            raise MaterializedUnitAuthorityAdmissionError(
                f"materialized unit binding mismatch: {field}"
            )

    for field in (
        "work_admission_effect",
        "authority_effect",
        "execution_effect",
        "scientific_standing_effect",
    ):
        if materialization.get(field) != "NONE":
            raise MaterializedUnitAuthorityAdmissionError(
                f"materialized unit {field} must be NONE before admission"
            )
    return unit


def materialized_unit_authority_coordinates(
    *,
    successor_candidate: Mapping[str, Any],
    work_spec: Mapping[str, Any],
    materialized_unit: Mapping[str, Any],
) -> dict[str, str]:
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

    request_material = {
        "object_type": "VERIFIED_MATERIALIZED_WORK_ADMISSION_REQUEST_V0",
        "campaign_id": successor["campaign_id"],
        "parent_work_item_id": successor["parent_work_item_id"],
        "basis_id": successor["basis_id"],
        "operative_frame_ref": successor["operative_frame_ref"],
        "reconciliation_identity": successor["reconciliation_identity"],
        "successor_posture": successor["successor_posture"],
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "materialized_work_item_id": unit["identity"]["work_item_id"],
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "work_spec_id": spec["work_spec_id"],
        "work_spec_integrity_sha256": spec["integrity_sha256"],
    }
    return {
        "request_sha256": canonical_sha256(request_material),
        "input_sha256": unit["integrity_sha256"],
    }


def try_materialized_unit_verified_authority_atomic_admission(
    *,
    store_dir: str | Path,
    authority_store: LocalAuthorityStateStore,
    authority_envelope: Mapping[str, Any],
    attempting_principal_id: str,
    successor_candidate: Mapping[str, Any],
    work_spec: Mapping[str, Any],
    materialized_unit: Mapping[str, Any],
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
    """Attempt exact materialized-work admission under current verified authority."""
    try:
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
        expected = materialized_unit_authority_coordinates(
            successor_candidate=successor,
            work_spec=spec,
            materialized_unit=unit,
        )
    except (
        VerifiedAuthorityAtomicAdmissionError,
        MaterializedUnitAuthorityAdmissionError,
    ) as exc:
        return _blocked("materialized_work_binding_invalid", error=str(exc))

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
            return _blocked("authority_request_materialized_work_mismatch")
        if binding.get("input_sha256") != expected["input_sha256"]:
            return _blocked("authority_input_materialized_unit_mismatch")

        atomic = try_atomic_admission(
            store_dir=store_dir,
            campaign_id=successor["campaign_id"],
            work_item_id=unit["identity"]["work_item_id"],
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
            "materialized_unit_integrity_sha256": unit["integrity_sha256"],
            "work_spec_id": spec["work_spec_id"],
            "work_spec_integrity_sha256": spec["integrity_sha256"],
            "authority_effect": "NONE",
            "consumption_effect": "NONE",
            "execution_effect": "NONE",
            "model_invocation_effect": "NONE",
        }

    inner = atomic["receipt"]
    composition_material = {
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "materialized_work_item_id": unit["identity"]["work_item_id"],
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "work_spec_id": spec["work_spec_id"],
        "work_spec_integrity_sha256": spec["integrity_sha256"],
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
            "materialized-unit-verified-authority-atomic-admission:sha256:"
            + canonical_sha256(composition_material)
        ),
        "authority_input_posture": "VERIFIED_CURRENT_EXACT_MATERIALIZED_WORK_BINDING",
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
            "authority binding for the exact sealed successor, exact sealed "
            "externally supplied work spec, and exact sealed materialized workflow "
            "unit into one existing atomic local admission transition. Authority "
            "is not consumed; no model invocation or work execution occurs. This "
            "does not establish cross-process authority/admission atomicity."
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
