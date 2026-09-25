"""Basis-bound workcycle wrapper V1.

This module wraps the existing bounded seat/work lifecycle with the missing
front and rear anchors:

    BASIS -> PRESSURE ADMISSIBILITY -> existing lifecycle
          -> APPLICATION -> CONSEQUENCE -> BASIS RECONCILIATION

It does not execute work, invoke models, create authority, or create scientific
standing.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import workcycle_v0 as wc


class BasisWorkcycleError(wc.WorkcycleError):
    pass


ADMISSIBILITY_TYPE = "PRESSURE_ADMISSIBILITY_V1"
NEXT_WORK_TYPE = "NEXT_WORK_POSTURE_V1"
RECONCILIATION_TYPE = "BASIS_RECONCILIATION_V1"
SUCCESSOR_CANDIDATE_TYPE = "SUCCESSOR_CANDIDATE_V1"

BASIS_ACTIVE = frozenset({"DECLARED", "SUPPORTED"})
BASIS_STATUSES = frozenset(
    {"DECLARED", "SUPPORTED", "CHALLENGED", "SUPERSEDED", "SATISFIED"}
)
LOAD_BEARING_EFFECTS = frozenset(
    {
        "APPLICATION",
        "AUTHORITY",
        "SAFETY",
        "RECONSTRUCTION",
        "BASIS",
        "OBSERVABILITY",
    }
)
NEXT_WORK_POSTURES = frozenset(
    {
        "APPLY_QUALIFIED_RESULT",
        "OBSERVE_APPLICATION_CONSEQUENCE",
        "RESOLVE_LOAD_BEARING_GAP",
        "CLOSE_BASIS",
        "HOLD_NO_JUSTIFIED_WORK",
    }
)
RECONCILIATION_DISPOSITIONS = frozenset(
    {
        "SATISFIED",
        "PARTIALLY_SATISFIED",
        "STILL_BLOCKED",
        "INVALIDATED",
        "REFRAMED",
    }
)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BasisWorkcycleError(f"{field} must be an object")
    return value


def _statement(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BasisWorkcycleError(f"{field} must be a non-empty string")
    return value.strip()


def validate_workflow_unit(unit: Mapping[str, Any]) -> None:
    identity = _mapping(unit.get("identity"), "identity")
    basis = _mapping(unit.get("basis"), "basis")
    pressure = _mapping(unit.get("pressure_selection"), "pressure_selection")
    contract = _mapping(unit.get("pressure_contract"), "pressure_contract")
    application = _mapping(unit.get("application"), "application")
    consequence = _mapping(
        unit.get("consequence_observation"), "consequence_observation"
    )
    reconciliation = _mapping(
        unit.get("basis_reconciliation"), "basis_reconciliation"
    )
    sanity = _mapping(unit.get("sanity_check"), "sanity_check")

    for field in ("work_item_id", "campaign_id", "operative_frame_ref"):
        _statement(identity.get(field), f"identity.{field}")

    _statement(basis.get("basis_id"), "basis.basis_id")
    if basis.get("basis_status") not in BASIS_STATUSES:
        raise BasisWorkcycleError("basis.basis_status is unsupported")
    _statement(basis.get("statement"), "basis.statement")
    desired = _mapping(basis.get("desired_consequence"), "basis.desired_consequence")
    obstruction = _mapping(basis.get("current_obstruction"), "basis.current_obstruction")
    _statement(desired.get("statement"), "basis.desired_consequence.statement")
    _statement(obstruction.get("statement"), "basis.current_obstruction.statement")

    distinction = _mapping(
        pressure.get("target_distinction"), "pressure_selection.target_distinction"
    )
    _statement(distinction.get("lhs"), "pressure_selection.target_distinction.lhs")
    _statement(distinction.get("rhs"), "pressure_selection.target_distinction.rhs")
    _statement(
        pressure.get("selection_basis"), "pressure_selection.selection_basis"
    )
    _statement(
        pressure.get("application_dependency"),
        "pressure_selection.application_dependency",
    )

    load_effects = pressure.get("load_bearing_effects")
    if not isinstance(load_effects, Sequence) or isinstance(load_effects, (str, bytes)):
        raise BasisWorkcycleError(
            "pressure_selection.load_bearing_effects must be a list"
        )

    budget = _mapping(contract.get("pressure_budget"), "pressure_contract.pressure_budget")
    for field in ("max_rounds", "max_branch_count", "max_unresolved_children"):
        value = budget.get(field)
        if not isinstance(value, int) or value < 0:
            raise BasisWorkcycleError(
                f"pressure_contract.pressure_budget.{field} must be nonnegative"
            )

    if not isinstance(application.get("required"), bool):
        raise BasisWorkcycleError("application.required must be boolean")
    if consequence.get("required_if_applied") is not True:
        raise BasisWorkcycleError(
            "consequence_observation.required_if_applied must be true"
        )
    _statement(
        consequence.get("expected_effect"),
        "consequence_observation.expected_effect",
    )

    _statement(
        reconciliation.get("original_basis_id"),
        "basis_reconciliation.original_basis_id",
    )
    if reconciliation.get("original_basis_id") != basis.get("basis_id"):
        raise BasisWorkcycleError(
            "basis_reconciliation.original_basis_id must bind basis.basis_id"
        )

    operating_change = _mapping(
        sanity.get("if_this_work_succeeds"),
        "sanity_check.if_this_work_succeeds",
    )
    _statement(
        operating_change.get("what_changes_in_the_operating_world"),
        "sanity_check.if_this_work_succeeds.what_changes_in_the_operating_world",
    )
    nothing = _mapping(
        sanity.get("if_nothing_would_change"),
        "sanity_check.if_nothing_would_change",
    )
    if nothing.get("posture") != "DO_NOT_RUN":
        raise BasisWorkcycleError(
            "sanity_check.if_nothing_would_change.posture must be DO_NOT_RUN"
        )


def pressure_admissibility(
    unit: Mapping[str, Any],
    *,
    qualified_result_already_resolves: bool = False,
) -> dict[str, Any]:
    """Determine whether one pressure may consume scientific consequence capacity.

    This is only an admissibility decision. It does not admit execution.
    """
    validate_workflow_unit(unit)
    basis = unit["basis"]
    pressure = unit["pressure_selection"]
    sanity = unit["sanity_check"]

    blockers: list[str] = []

    if basis["basis_status"] not in BASIS_ACTIVE:
        blockers.append("BASIS_NOT_ACTIVE")

    obstruction = basis["current_obstruction"]["statement"].strip()
    selection_basis = pressure["selection_basis"].strip()
    distinction = pressure["target_distinction"]
    if not obstruction:
        blockers.append("CURRENT_OBSTRUCTION_MISSING")
    if not selection_basis:
        blockers.append("DISTINCTION_NOT_LINKED_TO_OBSTRUCTION")
    if not distinction["lhs"].strip() or not distinction["rhs"].strip():
        blockers.append("TARGET_DISTINCTION_MISSING")

    effects = {
        str(value).upper()
        for value in pressure.get("load_bearing_effects") or []
        if isinstance(value, str)
    }
    material_effects = sorted(effects & LOAD_BEARING_EFFECTS)
    if not material_effects:
        blockers.append("NO_LOAD_BEARING_EFFECT")

    if qualified_result_already_resolves and pressure.get(
        "stop_if_resolved_by_existing_evidence"
    ) is True:
        blockers.append("EXISTING_QUALIFIED_RESULT_RESOLVES")

    operating_change = (
        sanity["if_this_work_succeeds"]["what_changes_in_the_operating_world"]
        .strip()
        .upper()
    )
    if operating_change in {"NONE", "NO CHANGE", "NO_CHANGE", "NOTHING"}:
        blockers.append("NO_OPERATING_CHANGE")

    admissible = not blockers
    return wc.seal_object(
        {
            "object_type": ADMISSIBILITY_TYPE,
            "work_item_id": unit["identity"]["work_item_id"],
            "basis_id": basis["basis_id"],
            "pressure_id": pressure.get("pressure_id"),
            "admissible": admissible,
            "material_effects": material_effects,
            "blockers": blockers,
            "work_admission_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def basis_reconciliation(
    unit: Mapping[str, Any],
    *,
    disposition: str,
    remaining_gap: str | None,
    next_pressure_basis: str | None = None,
) -> dict[str, Any]:
    validate_workflow_unit(unit)
    if disposition not in RECONCILIATION_DISPOSITIONS:
        raise BasisWorkcycleError("unsupported basis reconciliation disposition")

    next_allowed = disposition in {"PARTIALLY_SATISFIED", "STILL_BLOCKED", "REFRAMED"}
    if next_allowed and not (next_pressure_basis or "").strip():
        raise BasisWorkcycleError(
            "next_pressure_basis is required when another pressure remains eligible"
        )

    return wc.seal_object(
        {
            "object_type": RECONCILIATION_TYPE,
            "work_item_id": unit["identity"]["work_item_id"],
            "original_basis_id": unit["basis"]["basis_id"],
            "disposition": disposition,
            "remaining_gap": remaining_gap,
            "next_pressure_allowed": next_allowed,
            "next_pressure_basis": next_pressure_basis,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def derive_next_work_posture(
    unit: Mapping[str, Any],
    *,
    admissibility: Mapping[str, Any],
    reconciliation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive the next lawful work posture without generating new work."""
    validate_workflow_unit(unit)
    wc.verify_seal(admissibility)
    if admissibility.get("object_type") != ADMISSIBILITY_TYPE:
        raise BasisWorkcycleError("admissibility object_type mismatch")
    if admissibility.get("work_item_id") != unit["identity"]["work_item_id"]:
        raise BasisWorkcycleError("admissibility/work identity mismatch")

    if reconciliation is not None:
        wc.verify_seal(reconciliation)
        if reconciliation.get("object_type") != RECONCILIATION_TYPE:
            raise BasisWorkcycleError("reconciliation object_type mismatch")
        if reconciliation.get("work_item_id") != unit["identity"]["work_item_id"]:
            raise BasisWorkcycleError("reconciliation/work identity mismatch")

    qualification = _mapping(unit.get("qualification"), "qualification")
    application = unit["application"]
    consequence = unit["consequence_observation"]
    basis = unit["basis"]

    standing = qualification.get("scientific_standing")
    application_status = application.get("application_status")
    effect_class = consequence.get("effect_class")

    reason = ""
    if (
        application_status == "APPLIED"
        and consequence.get("required_if_applied") is True
        and effect_class in {None, "NOT_YET_OBSERVABLE"}
    ):
        posture = "OBSERVE_APPLICATION_CONSEQUENCE"
        reason = "applied change still owes consequence evidence"
    elif (
        standing == "QUALIFIED"
        and application.get("required") is True
        and application_status == "ELIGIBLE"
    ):
        posture = "APPLY_QUALIFIED_RESULT"
        reason = "qualified result is application-eligible"
    elif reconciliation is not None and reconciliation.get("disposition") == "SATISFIED":
        posture = "CLOSE_BASIS"
        reason = "basis reconciliation is satisfied"
    elif basis.get("basis_status") == "SATISFIED":
        posture = "CLOSE_BASIS"
        reason = "basis is already satisfied"
    elif admissibility.get("admissible") is True:
        posture = "RESOLVE_LOAD_BEARING_GAP"
        reason = "active basis has one admissible load-bearing pressure"
    else:
        posture = "HOLD_NO_JUSTIFIED_WORK"
        reason = "no currently admissible load-bearing pressure"

    if posture not in NEXT_WORK_POSTURES:
        raise BasisWorkcycleError("derived unsupported next work posture")

    return wc.seal_object(
        {
            "object_type": NEXT_WORK_TYPE,
            "work_item_id": unit["identity"]["work_item_id"],
            "basis_id": basis["basis_id"],
            "posture": posture,
            "reason": reason,
            "creates_work_item": False,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )



def derive_successor_candidate(
    unit: Mapping[str, Any],
    *,
    admissibility: Mapping[str, Any],
    reconciliation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive at most one deterministic successor candidate identity.

    This does not admit, execute, schedule, or authorize successor work.
    HOLD_NO_JUSTIFIED_WORK and CLOSE_BASIS produce no successor identity.
    """
    posture = derive_next_work_posture(
        unit,
        admissibility=admissibility,
        reconciliation=reconciliation,
    )
    wc.verify_seal(posture)

    no_successor = posture["posture"] in {
        "HOLD_NO_JUSTIFIED_WORK",
        "CLOSE_BASIS",
    }
    if no_successor:
        return wc.seal_object(
            {
                "object_type": SUCCESSOR_CANDIDATE_TYPE,
                "campaign_id": unit["identity"]["campaign_id"],
                "parent_work_item_id": unit["identity"]["work_item_id"],
                "basis_id": unit["basis"]["basis_id"],
                "successor_posture": posture["posture"],
                "successor_id": None,
                "candidate_posture": "NO_SUCCESSOR",
                "selection_basis": posture["reason"],
                "claim_ceiling": (
                    "Deterministic no-successor projection only. "
                    "No work is created, admitted, executed, or authorized."
                ),
                "work_admission_effect": "NONE",
                "authority_effect": "NONE",
                "execution_effect": "NONE",
                "scientific_standing_effect": "NONE",
                "integrity_sha256": "",
            }
        )

    reconciliation_identity = (
        reconciliation.get("integrity_sha256")
        if reconciliation is not None
        else "NO_RECONCILIATION"
    )
    material = {
        "campaign_id": unit["identity"]["campaign_id"],
        "parent_work_item_id": unit["identity"]["work_item_id"],
        "basis_id": unit["basis"]["basis_id"],
        "operative_frame_ref": unit["identity"]["operative_frame_ref"],
        "successor_posture": posture["posture"],
        "reconciliation_identity": reconciliation_identity,
        "next_pressure_basis": (
            None if reconciliation is None else reconciliation.get("next_pressure_basis")
        ),
    }
    successor_id = f"successor:sha256:{wc.canonical_sha256(material)}"
    return wc.seal_object(
        {
            "object_type": SUCCESSOR_CANDIDATE_TYPE,
            **material,
            "successor_id": successor_id,
            "candidate_posture": "PROPOSED_NOT_ADMITTED",
            "selection_basis": posture["reason"],
            "claim_ceiling": (
                "One deterministic successor candidate identity derived from exact "
                "basis/work/reconciliation/posture coordinates. This does not admit, "
                "execute, schedule, or authorize successor work."
            ),
            "work_admission_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


OBSTRUCTION_POSTURES = frozenset(
    {"RESOLVED", "REMAINS", "CHANGED", "UNRESOLVED"}
)
CONSEQUENCE_DISPOSITIONS = frozenset(
    {
        "CONSEQUENCE_MATCHED",
        "CONSEQUENCE_PARTIAL",
        "CONSEQUENCE_CONTRADICTED",
        "CONSEQUENCE_UNRESOLVED",
    }
)


def derive_basis_reconciliation_from_evidence(
    unit: Mapping[str, Any],
    *,
    consequence_evaluation: Mapping[str, Any] | None,
    current_obstruction_posture: str,
    remaining_gap: str | None = None,
    reframed_basis: str | None = None,
) -> dict[str, Any]:
    """Derive one bounded basis reconciliation from declared evidence.

    This function does not infer hidden world state. The current obstruction
    posture and any reframed basis must be supplied by source-supported upstream
    evidence. It does not create authority, admit work, execute, or invoke.
    """
    validate_workflow_unit(unit)

    if current_obstruction_posture not in OBSTRUCTION_POSTURES:
        raise BasisWorkcycleError("unsupported current_obstruction_posture")

    qualification = _mapping(unit.get("qualification"), "qualification")
    application = _mapping(unit.get("application"), "application")
    consequence = _mapping(
        unit.get("consequence_observation"), "consequence_observation"
    )

    scientific_standing = qualification.get("scientific_standing")
    application_status = application.get("application_status")
    regression_detected = consequence.get("regression_detected") is True
    effect_class = consequence.get("effect_class")

    consequence_disposition = None
    consequence_identity = None
    if consequence_evaluation is not None:
        wc.verify_seal(consequence_evaluation)
        if consequence_evaluation.get("work_item_id") != unit["identity"]["work_item_id"]:
            raise BasisWorkcycleError("consequence evaluation/work identity mismatch")
        consequence_disposition = consequence_evaluation.get("disposition")
        if consequence_disposition not in CONSEQUENCE_DISPOSITIONS:
            raise BasisWorkcycleError("unsupported consequence disposition")
        consequence_identity = consequence_evaluation.get("integrity_sha256")

    next_pressure_basis = None
    disposition = "STILL_BLOCKED"
    derived_remaining_gap = remaining_gap

    if regression_detected or consequence_disposition == "CONSEQUENCE_CONTRADICTED":
        if current_obstruction_posture == "CHANGED" and (reframed_basis or "").strip():
            disposition = "REFRAMED"
            derived_remaining_gap = remaining_gap or "original basis no longer describes current obstruction"
            next_pressure_basis = reframed_basis.strip()
        else:
            disposition = "INVALIDATED"
            derived_remaining_gap = remaining_gap or "observed consequence contradicts the active basis"
    elif scientific_standing == "QUALIFIED" and application.get("required") is True and application_status != "APPLIED":
        disposition = "STILL_BLOCKED"
        derived_remaining_gap = remaining_gap or "qualified result has not been applied"
        next_pressure_basis = "apply qualified result before basis closure"
    elif application_status == "APPLIED" and (
        consequence_evaluation is None
        or consequence_disposition == "CONSEQUENCE_UNRESOLVED"
        or effect_class in {None, "NOT_YET_OBSERVABLE"}
    ):
        disposition = "STILL_BLOCKED"
        derived_remaining_gap = remaining_gap or "applied change still lacks consequence evidence"
        next_pressure_basis = "observe application consequence before basis closure"
    elif consequence_disposition == "CONSEQUENCE_PARTIAL":
        disposition = "PARTIALLY_SATISFIED"
        derived_remaining_gap = remaining_gap or "expected consequence only partially observed"
        next_pressure_basis = "resolve remaining source-supported consequence gap"
    elif consequence_disposition == "CONSEQUENCE_MATCHED":
        if current_obstruction_posture == "RESOLVED":
            disposition = "SATISFIED"
            derived_remaining_gap = None
        elif current_obstruction_posture == "REMAINS":
            disposition = "PARTIALLY_SATISFIED"
            derived_remaining_gap = remaining_gap or "expected consequence matched but obstruction remains"
            next_pressure_basis = "resolve remaining source-supported obstruction"
        elif current_obstruction_posture == "CHANGED":
            if (reframed_basis or "").strip():
                disposition = "REFRAMED"
                derived_remaining_gap = remaining_gap or "obstruction changed after matched consequence"
                next_pressure_basis = reframed_basis.strip()
            else:
                disposition = "INVALIDATED"
                derived_remaining_gap = remaining_gap or "obstruction changed without a supported reframe"
        else:
            disposition = "STILL_BLOCKED"
            derived_remaining_gap = remaining_gap or "current obstruction posture remains unresolved"
            next_pressure_basis = "resolve current obstruction before basis closure"
    else:
        disposition = "STILL_BLOCKED"
        derived_remaining_gap = remaining_gap or "no matched operational consequence supports basis closure"
        next_pressure_basis = "obtain source-supported application/consequence evidence"

    next_allowed = disposition in {"PARTIALLY_SATISFIED", "STILL_BLOCKED", "REFRAMED"}

    return wc.seal_object(
        {
            "object_type": RECONCILIATION_TYPE,
            "work_item_id": unit["identity"]["work_item_id"],
            "original_basis_id": unit["basis"]["basis_id"],
            "source_scientific_standing": scientific_standing,
            "application_status": application_status,
            "consequence_disposition": consequence_disposition,
            "consequence_identity": consequence_identity,
            "current_obstruction_posture": current_obstruction_posture,
            "regression_detected": regression_detected,
            "disposition": disposition,
            "remaining_gap": derived_remaining_gap,
            "next_pressure_allowed": next_allowed,
            "next_pressure_basis": next_pressure_basis,
            "reframed_basis": reframed_basis,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )
