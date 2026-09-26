"""Single-gap-or-stop selector for one represented relational horizon.

V0 selects only when exactly one gap is already declared work-eligible by the
validated horizon representation. Multiple eligible gaps are deliberately
unsupported: ranking/optimization is a later capability.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc
from src.control.relational_horizon_v0 import validate_relational_horizon


SELECTION_TYPE = "HORIZON_GAP_SELECTION_V0"
SELECTED = "EXACT_ELIGIBLE_GAP"
STOP = "NO_JUSTIFIED_WORK"


class HorizonGapSelectorError(ValueError):
    pass


def select_gap_or_stop(horizon: Mapping[str, Any]) -> dict[str, Any]:
    validated = validate_relational_horizon(horizon)
    eligible = [
        copy.deepcopy(g)
        for g in validated["load_bearing_gaps"]
        if g["work_eligible"] is True
    ]

    if len(eligible) > 1:
        raise HorizonGapSelectorError(
            "v0 does not rank or choose among multiple eligible gaps"
        )

    if len(eligible) == 1:
        posture = SELECTED
        selected_gap = eligible[0]
        selected_gap_id = selected_gap["gap_id"]
        basis = "EXACTLY_ONE_DECLARED_WORK_ELIGIBLE_GAP"
        stop_required = False
    else:
        posture = STOP
        selected_gap = None
        selected_gap_id = None
        basis = "NO_DECLARED_WORK_ELIGIBLE_GAP"
        stop_required = True

    material = {
        "source_horizon_id": validated["horizon_id"],
        "source_horizon_state_id": validated["horizon_state_id"],
        "source_horizon_integrity_sha256": validated["integrity_sha256"],
        "selection_posture": posture,
        "selected_gap_id": selected_gap_id,
        "selected_gap": selected_gap,
        "eligible_gap_count": len(eligible),
        "selection_basis": basis,
        "stop_required": stop_required,
    }

    return wc.seal_object({
        "object_type": SELECTION_TYPE,
        **material,
        "selection_id": (
            "horizon-gap-selection:sha256:" + wc.canonical_sha256(material)
        ),
        "ranking_effect": "NONE",
        "planning_effect": "NONE",
        "work_materialization_effect": "NONE",
        "work_admission_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One deterministic selection over one validated represented horizon: "
            "exactly one already-declared work-eligible gap is returned, otherwise "
            "NO_JUSTIFIED_WORK. Multiple eligible gaps are rejected. No ranking, "
            "planning, work materialization, admission, authority, or execution is created."
        ),
        "integrity_sha256": "",
    })
