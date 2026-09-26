"""Externally supplied one-horizon/one-gap control-kernel calibration cell."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import workcycle_v0 as wc

SPECIMEN_TYPE = "EXTERNALLY_SUPPLIED_CONTROL_KERNEL_CELL_001_SPECIMEN_V0"
RESULT_TYPE = "CONTROL_KERNEL_CELL_001_RESULT_V0"


class ControlKernelCell001Error(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ControlKernelCell001Error(f"{field} must be non-empty")
    return value


def evaluate_supplied_single_gap(
    *,
    specimen: Mapping[str, Any],
    repository_observation: Mapping[str, Any],
    remaining_gap_ids: Sequence[str],
) -> dict[str, Any]:
    if not isinstance(specimen, Mapping):
        raise ControlKernelCell001Error("specimen must be an object")
    s = copy.deepcopy(dict(specimen))
    if s.get("object_type") != SPECIMEN_TYPE:
        raise ControlKernelCell001Error("specimen type mismatch")
    if s.get("selection_source") != "EXTERNALLY_SUPPLIED":
        raise ControlKernelCell001Error("selection source must be EXTERNALLY_SUPPLIED")
    if s.get("machine_selection_claimed") is not False:
        raise ControlKernelCell001Error("machine selection must remain unclaimed")

    horizon = s.get("operative_horizon")
    gaps = s.get("supplied_live_gaps")
    competing = s.get("competing_gaps")
    if not isinstance(horizon, Mapping):
        raise ControlKernelCell001Error("operative_horizon must be an object")
    if not isinstance(gaps, list) or len(gaps) != 1:
        raise ControlKernelCell001Error("exactly one supplied live gap is required")
    if competing != []:
        raise ControlKernelCell001Error("competing gaps are not permitted in cell 001")

    gap = gaps[0]
    gap_id = _text(gap.get("gap_id"), "gap_id")
    if gap.get("work_eligible") is not True:
        raise ControlKernelCell001Error("supplied gap must be work eligible")

    if not isinstance(repository_observation, Mapping):
        raise ControlKernelCell001Error("repository_observation must be an object")
    obs = copy.deepcopy(dict(repository_observation))
    required_obs = (
        "precondition_present_before",
        "postcondition_present_after",
        "bounded_delta_observed",
    )
    for field in required_obs:
        if not isinstance(obs.get(field), bool):
            raise ControlKernelCell001Error(f"{field} must be boolean")

    if not isinstance(remaining_gap_ids, Sequence) or isinstance(
        remaining_gap_ids, (str, bytes)
    ):
        raise ControlKernelCell001Error("remaining_gap_ids must be a list")
    remaining = list(remaining_gap_ids)
    if any(item not in {gap_id} for item in remaining):
        raise ControlKernelCell001Error("cell 001 cannot introduce new gaps")

    resolved = (
        obs["precondition_present_before"]
        and obs["postcondition_present_after"]
        and obs["bounded_delta_observed"]
        and gap_id not in remaining
    )

    if resolved:
        horizon_posture = "HORIZON_SATISFIED"
        terminal_posture = "NO_JUSTIFIED_WORK"
        stop_required = True
    else:
        horizon_posture = "HORIZON_UNRESOLVED"
        terminal_posture = "LIVE_GAP_REMAINS"
        stop_required = False

    material = {
        "campaign_id": s["campaign_id"],
        "cell_id": s["cell_id"],
        "horizon_id": _text(horizon.get("horizon_id"), "horizon_id"),
        "supplied_gap_id": gap_id,
        "selection_source": s["selection_source"],
        "machine_selection_claimed": False,
        "repository_observation": obs,
        "remaining_gap_ids": remaining,
        "horizon_posture": horizon_posture,
        "terminal_posture": terminal_posture,
        "stop_required": stop_required,
    }

    return wc.seal_object({
        "object_type": RESULT_TYPE,
        **material,
        "result_id": "control-kernel-cell-001:sha256:" + wc.canonical_sha256(material),
        "gap_selection_effect": "NONE",
        "work_materialization_effect": "NONE",
        "work_admission_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "Externally supplied one-horizon/one-gap calibration only. "
            "A bounded observed repository repair may reconcile the supplied horizon "
            "to HORIZON_SATISFIED and an empty supplied gap set to NO_JUSTIFIED_WORK. "
            "No generalized horizon representation or machine gap selection is established."
        ),
        "integrity_sha256": "",
    })
