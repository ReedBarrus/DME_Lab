"""Read-only Cockpit projection for WORKCYCLE_STABILIZATION_001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.coordination import workcycle_v0 as wc


STATE_ROOT = Path("docs/campaigns/workcycle_stabilization_001/state")

CONSEQUENCE_PATH = STATE_ROOT / "WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_OBSERVED_CONSEQUENCE.json"
EVALUATION_PATH = STATE_ROOT / "WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_CONSEQUENCE_EVALUATION.json"
BUDGET_PATH = STATE_ROOT / "CAMPAIGN_BUDGET_V0.json"
REPAIR_SPEC_PATH = STATE_ROOT / "REPAIR_ROUTING_PRESSURE_SPEC_001.json"
REPAIR_RESULT_PATH = STATE_ROOT / "REPAIR_ROUTING_PRESSURE_ADJUDICATION_RESULT_001.md"
CONTROL_PATH = STATE_ROOT / "WORKCYCLE_CONTROL_V0.json"


def _load_optional(repo: Path, rel: Path) -> dict[str, Any] | None:
    path = repo / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _verified_optional(
    repo: Path,
    rel: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = _load_optional(repo, rel)
    except Exception as exc:
        return None, f"{rel}: {type(exc).__name__}: {exc}"
    if value is None:
        return None, None
    try:
        wc.verify_seal(value)
    except Exception as exc:
        return None, f"{rel}: {type(exc).__name__}: {exc}"
    return value, None


def build_workcycle_projection(repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    progress = wc.derive_campaign_progress(repo)
    consequence, consequence_error = _verified_optional(repo, CONSEQUENCE_PATH)
    evaluation, evaluation_error = _verified_optional(repo, EVALUATION_PATH)
    budget, budget_error = _verified_optional(repo, BUDGET_PATH)
    repair_spec = _load_optional(repo, REPAIR_SPEC_PATH)
    repair_result_path = repo / REPAIR_RESULT_PATH
    repair_result = (
        repair_result_path.read_text(encoding="utf-8")
        if repair_result_path.is_file()
        else None
    )
    control = _load_optional(repo, CONTROL_PATH) or {
        "workflow_enabled": False,
        "campaign_enabled": False,
        "seat_work_enabled": False,
        "wake_requested": False,
        "auto_continuation_limit": 0,
        "operator_posture": "UNCONFIGURED",
    }

    eligibility = None
    if budget is not None:
        budget_reservable = all(
            budget[field]["reserved"] + budget[field]["consumed"]
            < budget[field]["allowed_per_wake"]
            for field in ("work_items", "seat_invocations")
        )
        eligibility = {
            "posture": "PARTIAL_COORDINATES_ONLY",
            "eligible": None,
            "known_coordinates": {
                "wake_budget_reservable": budget_reservable,
            },
            "unresolved_coordinates": [
                "dependency_satisfied",
                "frame_current",
                "seat_available",
                "no_hold",
                "authority_satisfied",
            ],
            "claim_ceiling": (
                "Budget-side eligibility only; real work eligibility is unresolved "
                "until runtime coordinates are source-bound."
            ),
        }

    cells = progress["cells"]
    active_horizon = "FIRST_PERMANENT_WORKLOAD_COMPRESSION_HISTORY_CONSERVATION"
    active_work_item = None
    latest_completed_work_item = (
        consequence.get("work_item_id")
        if consequence is not None and evaluation is not None
        else None
    )
    next_eligible_work_item = None

    projection_errors = [
        error
        for error in (consequence_error, evaluation_error, budget_error)
        if error is not None
    ]

    current_unresolved = (
        list(evaluation.get("unresolved", []))
        if evaluation is not None
        else list(consequence.get("unresolved", []))
        if consequence is not None
        else []
    )
    current_unresolved.extend(projection_errors)

    return {
        "projection_schema": "workcycle_cockpit_projection_v0",
        "campaign_id": progress["campaign_id"],
        "active_horizon": active_horizon,
        "campaign_progress": cells,
        "next_pressure": progress["next_pressure"],
        "active_work_item": active_work_item,
        "latest_completed_work_item": latest_completed_work_item,
        "next_eligible_work_item": next_eligible_work_item,
        "latest_consequence": consequence,
        "latest_consequence_evaluation": evaluation,
        "current_unresolved": current_unresolved,
        "projection_errors": projection_errors,
        "historical_unresolved": (
            list(consequence.get("unresolved", []))
            if consequence is not None
            else []
        ),
        "repair_routing": {
            "spec": repair_spec,
            "result": repair_result,
            "result_present": repair_result is not None,
        },
        "wake_budget": budget,
        "campaign_cumulative_budget": {
            "status": "NOT_IMPLEMENTED",
            "claim_ceiling": "No cumulative campaign spend cap is mechanically enforced yet.",
        },
        "eligibility": eligibility,
        "requested_control": control,
        "operative_control": {
            "status": "LOCAL_OPERATOR_CONTROL_NOT_IMPLEMENTED",
            "workflow_enabled": False,
            "seat_work_enabled": False,
            "wake_requested": False,
            "auto_continuation_limit": 0,
            "repo_control_has_execution_effect": False,
        },
        "operator_summary": {
            "workflow": "OFF",
            "campaign": "ACTIVE" if control.get("campaign_enabled") else "PAUSED",
            "seat_work": "DISABLED",
            "wake_requested": False,
            "requested_workflow": "ON" if control.get("workflow_enabled") else "OFF",
            "requested_seat_work": "ENABLED" if control.get("seat_work_enabled") else "DISABLED",
            "requested_wake": bool(control.get("wake_requested")),
            "auto_continuation_limit": 0,
            "control_source": "REPO_REQUEST_ONLY",
            "local_control_admitted": False,
            "reed_action": (
                "REVIEW_NEXT_PRESSURE"
                if progress["next_pressure"] in {"T2_ADJUDICATION", "T6_PRESSURE", "T7_PRESSURE"}
                else "NONE"
            ),
        },
        "projection_boundary": {
            "read_only": True,
            "creates_authority": False,
            "performs_execution": False,
            "advances_campaign_standing": False,
            "mutates_atlas": False,
        },
    }
