"""Basis-governed pressure justification for Atlas workcycle metabolism.

Science is an instrument inside a consequence loop, not a sovereign workload
generator. This projection asks whether a relational horizon carries enough
current load to justify one bounded next pressure.

No work is admitted or executed here.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


BASIS_OBJECT_TYPE = "BASIS_RECORD_V0"
JUSTIFICATION_OBJECT_TYPE = "PRESSURE_JUSTIFICATION_V0"

PRESSURE_POSTURES = {
    "JUSTIFIED",
    "ALREADY_RESOLVED",
    "NON_LOAD_BEARING",
    "UNRESOLVED",
}

NEXT_WORK_POSTURES = {
    "APPLY_QUALIFIED_RESULT",
    "OBSERVE_APPLICATION_CONSEQUENCE",
    "RESOLVE_LOAD_BEARING_GAP",
    "CLOSE_BASIS",
    "HOLD_NO_JUSTIFIED_WORK",
}


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _blockers(qualification: Mapping[str, Any], tier: str) -> list[str]:
    item = qualification.get(tier) or {}
    return [str(value) for value in item.get("blockers") or []]


def _cell_for_pressure(pressure: str | None) -> str | None:
    mapping = {
        "T0": "T0",
        "T1": "T1",
        "T2": "T2",
        "T2_ADJUDICATION": "T2",
        "T3": "T3",
        "T4": "T4",
        "T5": "T5",
        "T6": "T6",
        "T6_PRESSURE": "T6",
        "T7": "T7",
        "T7_PRESSURE": "T7",
    }
    return mapping.get(str(pressure)) if pressure is not None else None


def _expected_change(pressure: str) -> str:
    changes = {
        "T2_ADJUDICATION": (
            "replace exercised-but-unadjudicated campaign→work lineage debt with "
            "an independently matched or explicitly fractured disposition"
        ),
        "T6_PRESSURE": (
            "replace unpressured repair law with challengeable typed repair-routing evidence"
        ),
        "T7_PRESSURE": (
            "replace operator-projection uncertainty with challengeable currentness, "
            "control, budget, seat, and eligibility evidence"
        ),
        "TEMPORAL_HORIZON_ADJUDICATION": (
            "replace candidate temporal-horizon closure with an independent disposition "
            "over history/current/upcoming relation"
        ),
        "ONE_SUCCESSOR_PRESSURE": (
            "establish or fracture the one-successor non-executing continuation law"
        ),
        "ATOMIC_ADMISSION_PRESSURE": (
            "establish or fracture one fail-closed admission transaction binding "
            "frame, horizon, work, seat/lease, attempt, authority, and wake budget"
        ),
        "AUTHORITY_BINDING_PRESSURE": (
            "replace caller-supplied authority testimony with a source-bound current "
            "authority verification that grants and consumes nothing"
        ),
        "SUCCESSOR_IDENTITY_PRESSURE": (
            "replace planner-invented continuation identity with one deterministic "
            "source-bound successor candidate identity"
        ),
        "BASIS_RECONCILIATION_PRESSURE": (
            "establish or fracture deterministic reconciliation of observed consequence "
            "against the original load-bearing basis"
        ),
        "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_PRESSURE": (
            "bind verified current authority and a derived successor identity into "
            "one fail-closed atomic admission transition"
        ),
        "ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE": (
            "bind one exact admitted successor to the same current one-use authority "
            "and cross one bounded invocation boundary with replay denied"
        ),
        "INVOCATION_RESULT_WITNESS_PRESSURE": (
            "bind one successful consumed invocation return into an immutable result "
            "witness without semantic interpretation or settlement"
        ),
        "INVOCATION_RESULT_SETTLEMENT_PRESSURE": (
            "bind externally supplied field-level candidate dispositions and bases "
            "to one immutable result witness without qualification or witness rewrite"
        ),
        "SETTLEMENT_CONSEQUENCE_RECONCILIATION_PRESSURE": (
            "keep settlement distinct from consequence and bind independent consequence "
            "evidence into bounded basis reconciliation"
        ),
        "SECOND_SUCCESSOR_FROM_RECONCILIATION_PRESSURE": (
            "pressure whether fresh reconciliation changes next-work posture and exact "
            "successor projection without manual successor selection"
        ),
        "SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE": (
            "bind one exact successor projection to one explicit bounded work spec "
            "and materialize a complete next workflow unit without admission or execution"
        ),
        "REPEATED_METABOLIC_LOOP_PRESSURE": (
            "establish or fracture two consecutive basis-bound workcycle transitions "
            "whose successor selection is derived from prior witnessed consequence"
        ),
    }
    return changes.get(
        pressure,
        "reduce one explicit current workcycle blocker without widening campaign scope",
    )


def _select_pressure(
    *,
    workcycle: Mapping[str, Any],
    qualification: Mapping[str, Any],
) -> tuple[str | None, str]:
    """Select the first load-bearing pressure from existing bounded debt.

    This does not invent a new campaign. It orders already-declared/frozen
    qualification debt so science does not recursively generate arbitrary work.
    """
    progress = workcycle.get("campaign_progress") or {}
    declared = workcycle.get("next_pressure")

    cell = _cell_for_pressure(str(declared) if declared is not None else None)
    if cell and (progress.get(cell) or {}).get("posture") != "BOUNDED_PASS":
        return str(declared), "DECLARED_PRESSURE_STILL_LOAD_BEARING"

    bounded = _blockers(qualification, "bounded_workcycle")
    for blocker in bounded:
        if blocker.startswith("T7:"):
            return "T7_PRESSURE", "BOUNDED_QUALIFICATION_BLOCKER"
        if blocker.startswith("T6:"):
            return "T6_PRESSURE", "BOUNDED_QUALIFICATION_BLOCKER"
        if blocker.startswith("T2:"):
            return "T2_ADJUDICATION", "BOUNDED_QUALIFICATION_BLOCKER"
        if blocker.startswith("TEMPORAL_HORIZON:"):
            return "TEMPORAL_HORIZON_ADJUDICATION", "BOUNDED_QUALIFICATION_BLOCKER"

    self_moving = _blockers(qualification, "self_moving_workcycle")
    for blocker in self_moving:
        if blocker.startswith("ONE_SUCCESSOR:"):
            return "ONE_SUCCESSOR_PRESSURE", "SELF_MOVING_QUALIFICATION_BLOCKER"
        if blocker.startswith("ATOMIC_ADMISSION:"):
            return "ATOMIC_ADMISSION_PRESSURE", "SELF_MOVING_QUALIFICATION_BLOCKER"
        if blocker.startswith("AUTHORITY_BINDING:"):
            return "AUTHORITY_BINDING_PRESSURE", "SELF_MOVING_QUALIFICATION_BLOCKER"
        if blocker.startswith("SUCCESSOR_IDENTITY:"):
            return "SUCCESSOR_IDENTITY_PRESSURE", "SELF_MOVING_QUALIFICATION_BLOCKER"
        if blocker.startswith("BASIS_RECONCILIATION:"):
            return "BASIS_RECONCILIATION_PRESSURE", "SELF_MOVING_QUALIFICATION_BLOCKER"
        if blocker.startswith("VERIFIED_AUTHORITY_ATOMIC_ADMISSION:"):
            return (
                "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("ADMITTED_AUTHORITY_CONSUMPTION:"):
            return (
                "ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("INVOCATION_RESULT_WITNESS:"):
            return (
                "INVOCATION_RESULT_WITNESS_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("INVOCATION_RESULT_SETTLEMENT:"):
            return (
                "INVOCATION_RESULT_SETTLEMENT_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("SETTLEMENT_CONSEQUENCE_RECONCILIATION:"):
            return (
                "SETTLEMENT_CONSEQUENCE_RECONCILIATION_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("SECOND_SUCCESSOR_FROM_RECONCILIATION:"):
            return (
                "SECOND_SUCCESSOR_FROM_RECONCILIATION_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("SUCCESSOR_WORK_UNIT_MATERIALIZATION:"):
            return (
                "SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE",
                "SELF_MOVING_QUALIFICATION_BLOCKER",
            )
        if blocker.startswith("REPEATED_METABOLIC_LOOP:"):
            return "REPEATED_METABOLIC_LOOP_PRESSURE", "SELF_MOVING_QUALIFICATION_BLOCKER"

    if declared and declared != "AUTO_CONTINUATION_PRESSURE":
        return str(declared), "DECLARED_PRESSURE_UNMAPPED"

    return None, "NO_LOAD_BEARING_QUALIFICATION_BLOCKER"


def build_basis_record(
    *,
    workcycle: Mapping[str, Any],
    horizon_closure: Mapping[str, Any],
    qualification: Mapping[str, Any],
) -> dict[str, Any]:
    horizon = horizon_closure.get("primary_horizon") or {}
    loads = horizon_closure.get("six_load_dimensions") or {}
    surfaces = horizon_closure.get("seven_surfaces") or {}

    basis_core = {
        "campaign_id": workcycle.get("campaign_id"),
        "active_horizon_id": workcycle.get("active_horizon"),
        "horizon_family": horizon.get("family"),
        "horizon_subject": horizon.get("subject"),
        "horizon_disposition": horizon_closure.get("disposition"),
        "declared_next_pressure": workcycle.get("next_pressure"),
        "current_unresolved": list(workcycle.get("current_unresolved") or []),
        "bounded_qualification_blockers": _blockers(
            qualification, "bounded_workcycle"
        ),
        "self_moving_qualification_blockers": _blockers(
            qualification, "self_moving_workcycle"
        ),
        "seven_surfaces": surfaces,
        "six_load_dimensions": loads,
    }

    supported = (
        horizon_closure.get("disposition") == "HORIZON_MATCHED"
        and horizon_closure.get("history_posture") == "SUPPORTED"
        and horizon_closure.get("currentness_posture") == "SUPPORTED"
        and horizon_closure.get("upcoming_work_posture") == "SUPPORTED"
    )

    return {
        "object_type": BASIS_OBJECT_TYPE,
        "basis_id": f"basis:sha256:{_canonical_sha256(basis_core)}",
        "basis_posture": "SUPPORTED" if supported else "UNRESOLVED",
        **basis_core,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "Derived operative basis for pressure selection only; not campaign "
            "standing, work admission, execution authority, or semantic causation."
        ),
    }


def build_pressure_justification(
    *,
    workcycle: Mapping[str, Any],
    horizon_closure: Mapping[str, Any],
    qualification: Mapping[str, Any],
) -> dict[str, Any]:
    basis = build_basis_record(
        workcycle=workcycle,
        horizon_closure=horizon_closure,
        qualification=qualification,
    )
    horizon = horizon_closure.get("primary_horizon") or {}
    pressure, selection_basis = _select_pressure(
        workcycle=workcycle,
        qualification=qualification,
    )

    if basis["basis_posture"] != "SUPPORTED":
        posture = "UNRESOLVED"
        next_posture = "HOLD_NO_JUSTIFIED_WORK"
        obstruction = "operative basis is not fully supported"
    elif pressure is None:
        posture = "ALREADY_RESOLVED"
        next_posture = "HOLD_NO_JUSTIFIED_WORK"
        obstruction = "no load-bearing qualification blocker remains"
    else:
        posture = "JUSTIFIED"
        next_posture = "RESOLVE_LOAD_BEARING_GAP"
        obstruction = str(
            horizon.get("boundary_condition")
            or f"qualification debt requires {pressure}"
        )

    load_bearing = {
        name: value
        for name, value in (horizon_closure.get("six_load_dimensions") or {}).items()
        if (value or {}).get("direction") in {"INCREASING", "UNRESOLVED", "REDISTRIBUTED"}
    }

    if posture == "JUSTIFIED" and not load_bearing:
        posture = "NON_LOAD_BEARING"
        next_posture = "HOLD_NO_JUSTIFIED_WORK"

    target_distinctions = list(horizon_closure.get("distinctions_applied") or [])

    return {
        "object_type": JUSTIFICATION_OBJECT_TYPE,
        "basis_id": basis["basis_id"],
        "horizon_id": workcycle.get("active_horizon"),
        "horizon_family": horizon.get("family"),
        "load_bearing_relation": horizon.get("subject"),
        "load_bearing_dimensions": load_bearing,
        "current_obstruction": obstruction,
        "target_distinctions": target_distinctions,
        "proposed_pressure": pressure,
        "pressure_selection_basis": selection_basis,
        "if_resolved": {
            "expected_operating_change": (
                _expected_change(pressure)
                if pressure is not None
                else "no additional operating change required"
            )
        },
        "if_nothing_changes": "DO_NOT_RUN",
        "application_dependency": (
            "A qualified pressure result must later be applied and its observed "
            "operating consequence reconciled against a fresh basis."
        ),
        "existing_evidence_check": {
            "bounded_qualification_blockers": basis[
                "bounded_qualification_blockers"
            ],
            "self_moving_qualification_blockers": basis[
                "self_moving_qualification_blockers"
            ],
            "declared_next_pressure": basis["declared_next_pressure"],
        },
        "pressure_posture": posture,
        "next_work_posture": next_posture,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "work_admission_effect": "NONE",
        "claim_ceiling": (
            "One basis-governed pressure justification only. JUSTIFIED does not "
            "admit work, invoke a seat, create authority, or advance scientific standing."
        ),
    }
