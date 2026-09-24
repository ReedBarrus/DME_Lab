"""WORKCYCLE_STABILIZATION_001 deterministic lifecycle primitives.

This module does not invoke models, schedule workers, grant authority, promote
scientific standing, or mutate the Atlas. It derives bounded workcycle state
from explicit evidence and enforces typed budget/eligibility relations.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class WorkcycleError(ValueError):
    pass


PROGRESS_TYPE = "WORKCYCLE_CAMPAIGN_PROGRESS_V0"
CONSEQUENCE_TYPE = "OBSERVED_CONSEQUENCE_V0"
EVALUATION_TYPE = "CONSEQUENCE_EVALUATION_V0"
REPAIR_ROUTE_TYPE = "REPAIR_ROUTE_V0"
BUDGET_TYPE = "WAKE_BUDGET_V0"

CONSEQUENCE_DISPOSITIONS = frozenset(
    {
        "CONSEQUENCE_MATCHED",
        "CONSEQUENCE_PARTIAL",
        "CONSEQUENCE_CONTRADICTED",
        "CONSEQUENCE_UNRESOLVED",
        "WORK_ENVELOPE_VIOLATION",
    }
)
REPAIR_CLASSES = frozenset(
    {
        "NONE",
        "OUTPUT_DEFECT",
        "DECOMPOSITION_DEFECT",
        "CAMPAIGN_HORIZON_DEFECT",
        "APPARATUS_DEFECT",
        "HOLD",
    }
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def seal_object(value: Mapping[str, Any]) -> dict[str, Any]:
    retained = copy.deepcopy(dict(value))
    retained.pop("integrity_sha256", None)
    retained["integrity_sha256"] = canonical_sha256(retained)
    return retained


def verify_seal(value: Mapping[str, Any]) -> str:
    observed = value.get("integrity_sha256")
    if not isinstance(observed, str) or len(observed) != 64:
        raise WorkcycleError("missing or invalid integrity_sha256")
    retained = copy.deepcopy(dict(value))
    retained.pop("integrity_sha256", None)
    expected = canonical_sha256(retained)
    if observed != expected:
        raise WorkcycleError(
            f"object integrity mismatch (expected {expected}, got {observed})"
        )
    return observed


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _exists(repo: Path, rel: str) -> bool:
    return (repo / rel).is_file()


def _contains(repo: Path, rel: str, needle: str) -> bool:
    path = repo / rel
    return path.is_file() and needle in _text(path)


def _markdown_field(repo: Path, rel: str, field: str) -> str | None:
    path = repo / rel
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    target = field.strip().rstrip(":")
    for index, line in enumerate(lines):
        if line.strip().rstrip(":") != target:
            continue
        for candidate in lines[index + 1:]:
            value = candidate.strip()
            if value:
                return value
    return None


def _validated_consequence_pair(
    repo: Path,
    consequence_rel: str,
    evaluation_rel: str,
) -> tuple[bool, list[str]]:
    consequence_path = repo / consequence_rel
    evaluation_path = repo / evaluation_rel
    if not consequence_path.is_file() or not evaluation_path.is_file():
        return False, ["observed consequence/evaluation not yet both present"]
    try:
        consequence = _load_json(consequence_path)
        evaluation = _load_json(evaluation_path)
        verify_seal(consequence)
        verify_seal(evaluation)
    except Exception as exc:
        return False, [f"consequence/evaluation validation failed: {type(exc).__name__}: {exc}"]
    if consequence.get("object_type") != CONSEQUENCE_TYPE:
        return False, ["observed consequence object_type mismatch"]
    if evaluation.get("object_type") != EVALUATION_TYPE:
        return False, ["consequence evaluation object_type mismatch"]
    if evaluation.get("work_item_id") != consequence.get("work_item_id"):
        return False, ["work-item identity mismatch between consequence and evaluation"]
    if evaluation.get("consequence_id") != consequence.get("consequence_id"):
        return False, ["consequence identity mismatch between witness and evaluation"]
    if evaluation.get("disposition") != "CONSEQUENCE_MATCHED":
        return False, [f"consequence disposition is {evaluation.get('disposition', 'MISSING')}"]
    return True, []


def derive_campaign_progress(repo_root: str | Path) -> dict[str, Any]:
    """Derive current campaign posture from explicit evidence artifacts.

    This is a projection only. It does not create campaign/scientific standing.
    """
    repo = Path(repo_root).resolve()
    cells: dict[str, dict[str, Any]] = {}

    t0 = "docs/campaigns/load_transfer_001/LOAD_TRANSFER_001_MECHANICAL_TEST_RESULT_001.md"
    cells["T0"] = {
        "posture": "BOUNDED_PASS" if _contains(repo, t0, "18 / 18 PASS") else "UNRESOLVED",
        "evidence": [t0] if _exists(repo, t0) else [],
        "unresolved": [] if _exists(repo, t0) else ["mechanical result absent"],
    }

    t1 = "docs/campaigns/load_transfer_001/LOAD_TRANSFER_001_LIVE_TWO_SEAT_PRESSURE_RESULT_001.md"
    cells["T1"] = {
        "posture": "BOUNDED_PASS" if _contains(repo, t1, "RESULT:\nBOUNDED PASS") else "UNRESOLVED",
        "evidence": [t1] if _exists(repo, t1) else [],
        "unresolved": [] if _exists(repo, t1) else ["live two-seat pressure result absent"],
    }

    d001 = "docs/campaigns/workcycle_stabilization_001/decomposition/WORKCYCLE_STABILIZATION_001_D001.json"
    w1 = "docs/campaigns/workcycle_stabilization_001/decomposition/WORKCYCLE_STABILIZATION_001_COMPRESSION_W1.json"
    t2_result = "docs/campaigns/workcycle_stabilization_001/decomposition/DECOMPOSITION_D001_ADJUDICATION_RESULT_001.md"
    t2_ok = _exists(repo, d001) and _exists(repo, w1)
    t2_disposition = _markdown_field(repo, t2_result, "DISPOSITION")
    t2_pass = t2_ok and t2_disposition == "DECOMPOSITION_MATCHED"
    cells["T2"] = {
        "posture": (
            "BOUNDED_PASS"
            if t2_pass
            else "ADJUDICATED_NOT_MATCHED"
            if t2_ok and t2_disposition is not None
            else "EXERCISED_UNADJUDICATED"
            if t2_ok
            else "NOT_STARTED"
        ),
        "evidence": [p for p in (d001, w1, t2_result) if _exists(repo, p)],
        "unresolved": (
            []
            if t2_pass
            else [f"decomposition adjudication disposition: {t2_disposition}"]
            if t2_ok and t2_disposition is not None
            else ["independent decomposition adjudication not yet frozen"]
            if t2_ok
            else ["decomposition lineage objects absent"]
        ),
    }

    consequence = "docs/campaigns/workcycle_stabilization_001/state/WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_OBSERVED_CONSEQUENCE.json"
    evaluation = "docs/campaigns/workcycle_stabilization_001/state/WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_CONSEQUENCE_EVALUATION.json"
    t3_pass, t3_unresolved = _validated_consequence_pair(
        repo, consequence, evaluation
    )
    cells["T3"] = {
        "posture": (
            "BOUNDED_PASS"
            if t3_pass
            else "UNRESOLVED"
            if _exists(repo, consequence) or _exists(repo, evaluation)
            else "NOT_STARTED"
        ),
        "evidence": [p for p in (consequence, evaluation) if _exists(repo, p)],
        "unresolved": t3_unresolved,
    }

    review = "docs/campaigns/workcycle_stabilization_001/compression/ATLAS_COORDINATION_ROUNDS_010_012_REVIEW.md"
    review_pass = _markdown_field(repo, review, "DISPOSITION") == "CONSEQUENCE_MATCHED"
    cells["T4"] = {
        "posture": "BOUNDED_PASS" if review_pass else "UNRESOLVED",
        "evidence": [review] if _exists(repo, review) else [],
        "unresolved": [] if review_pass else ["bounded conservation review not matched"],
    }
    cells["T5"] = {
        "posture": "BOUNDED_PASS" if review_pass else "UNRESOLVED",
        "evidence": [review] if _exists(repo, review) else [],
        "unresolved": [] if review_pass else ["compression consequence not matched"],
    }

    repair_spec = "docs/campaigns/workcycle_stabilization_001/state/REPAIR_ROUTING_PRESSURE_SPEC_001.json"
    repair_result = "docs/campaigns/workcycle_stabilization_001/state/REPAIR_ROUTING_PRESSURE_ADJUDICATION_RESULT_001.md"
    t6_discriminated = _markdown_field(
        repo, repair_result, "ALL_FOUR_CLASSES_DISCRIMINATED"
    )
    t6_pass = t6_discriminated == "YES"
    cells["T6"] = {
        "posture": (
            "BOUNDED_PASS"
            if t6_pass
            else "ADJUDICATED_NOT_MATCHED"
            if _exists(repo, repair_result)
            else "IMPLEMENTED_UNPRESSURED"
            if _exists(repo, repair_spec)
            else "NOT_STARTED"
        ),
        "evidence": [p for p in (repair_spec, repair_result) if _exists(repo, p)],
        "unresolved": (
            []
            if t6_pass
            else [f"repair routing discrimination result: {t6_discriminated or 'MISSING'}"]
            if _exists(repo, repair_result)
            else ["typed repair routing requires independent pressure"]
            if _exists(repo, repair_spec)
            else ["typed repair routing not yet implemented"]
        ),
    }

    cockpit = "src/cockpit/workcycle_projection.py"
    cells["T7"] = {
        "posture": "IMPLEMENTED_UNPRESSURED" if _exists(repo, cockpit) else "NOT_STARTED",
        "evidence": [cockpit] if _exists(repo, cockpit) else [],
        "unresolved": (
            ["operator projection requires pressure against current repository state"]
            if _exists(repo, cockpit)
            else ["workcycle cockpit projection absent"]
        ),
    }

    return seal_object(
        {
            "object_type": PROGRESS_TYPE,
            "campaign_id": "WORKCYCLE_STABILIZATION_001",
            "projection_effect": {
                "campaign_standing": "NONE",
                "scientific_standing": "NONE",
                "authority": "NONE",
                "execution": "NONE",
            },
            "cells": cells,
            "next_pressure": _next_pressure(cells),
            "integrity_sha256": "",
        }
    )


def _next_pressure(cells: Mapping[str, Mapping[str, Any]]) -> str:
    if cells["T0"]["posture"] != "BOUNDED_PASS":
        return "T0"
    if cells["T1"]["posture"] != "BOUNDED_PASS":
        return "T1"
    if cells["T2"]["posture"] == "EXERCISED_UNADJUDICATED":
        return "T2_ADJUDICATION"
    if cells["T2"]["posture"] != "BOUNDED_PASS":
        return "T2"
    if cells["T3"]["posture"] != "BOUNDED_PASS":
        return "T3"
    if cells["T4"]["posture"] != "BOUNDED_PASS":
        return "T4"
    if cells["T5"]["posture"] != "BOUNDED_PASS":
        return "T5"
    if cells["T6"]["posture"] == "IMPLEMENTED_UNPRESSURED":
        return "T6_PRESSURE"
    if cells["T6"]["posture"] != "BOUNDED_PASS":
        return "T6"
    if cells["T7"]["posture"] == "IMPLEMENTED_UNPRESSURED":
        return "T7_PRESSURE"
    if cells["T7"]["posture"] != "BOUNDED_PASS":
        return "T7"
    return "AUTO_CONTINUATION_PRESSURE"


def observed_consequence(
    *,
    consequence_id: str,
    work_item_id: str,
    decomposition_id: str,
    input_state_identity: str,
    output_artifact_identities: Sequence[str],
    observations: Mapping[str, Any],
    declared_changes_observed: Mapping[str, Any],
    unchanged_coordinates_observed: Mapping[str, Any],
    evidence_handles: Sequence[str],
    unresolved: Sequence[str],
) -> dict[str, Any]:
    if not consequence_id or not work_item_id or not decomposition_id:
        raise WorkcycleError("consequence/work/decomposition identities are required")
    return seal_object(
        {
            "object_type": CONSEQUENCE_TYPE,
            "consequence_id": consequence_id,
            "work_item_id": work_item_id,
            "decomposition_id": decomposition_id,
            "input_state_identity": input_state_identity,
            "output_artifact_identities": list(output_artifact_identities),
            "observations": copy.deepcopy(dict(observations)),
            "declared_changes_observed": copy.deepcopy(dict(declared_changes_observed)),
            "unchanged_coordinates_observed": copy.deepcopy(
                dict(unchanged_coordinates_observed)
            ),
            "evidence_handles": list(evidence_handles),
            "unresolved": list(unresolved),
            "authority_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def consequence_evaluation(
    *,
    evaluation_id: str,
    work_item: Mapping[str, Any],
    consequence: Mapping[str, Any],
    disposition: str,
    conservation_surfaces: Mapping[str, str],
    load_dimensions: Mapping[str, str],
    unresolved: Sequence[str],
) -> dict[str, Any]:
    verify_seal(consequence)
    if consequence.get("object_type") != CONSEQUENCE_TYPE:
        raise WorkcycleError("evaluation requires OBSERVED_CONSEQUENCE_V0")
    if consequence.get("work_item_id") != work_item.get("work_item_id"):
        raise WorkcycleError("work/consequence identity mismatch")
    if disposition not in CONSEQUENCE_DISPOSITIONS:
        raise WorkcycleError("unsupported consequence disposition")
    return seal_object(
        {
            "object_type": EVALUATION_TYPE,
            "evaluation_id": evaluation_id,
            "work_item_id": work_item["work_item_id"],
            "consequence_id": consequence["consequence_id"],
            "disposition": disposition,
            "conservation_surfaces": copy.deepcopy(dict(conservation_surfaces)),
            "load_dimensions": copy.deepcopy(dict(load_dimensions)),
            "unresolved": list(unresolved),
            "campaign_progress_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "authority_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def route_repair(
    *,
    evaluation_id: str,
    defect_class: str,
    affected_object: str,
    basis: Sequence[str],
) -> dict[str, Any]:
    if defect_class not in REPAIR_CLASSES:
        raise WorkcycleError("unsupported repair class")
    rules = {
        "NONE": ("NONE", False, False),
        "OUTPUT_DEFECT": ("WORK_OUTPUT_REPAIR", False, False),
        "DECOMPOSITION_DEFECT": ("REDECOMPOSE_WORK_FAMILY", False, False),
        "CAMPAIGN_HORIZON_DEFECT": ("HOLD_FOR_CAMPAIGN_REPLAN", False, True),
        "APPARATUS_DEFECT": ("APPARATUS_REPAIR", False, False),
        "HOLD": ("HOLD_UNRESOLVED", False, False),
    }
    destination, retry_permitted, campaign_replan = rules[defect_class]
    return seal_object(
        {
            "object_type": REPAIR_ROUTE_TYPE,
            "source_evaluation_id": evaluation_id,
            "defect_class": defect_class,
            "affected_object": affected_object,
            "basis": list(basis),
            "repair_destination": destination,
            "retry_permitted": retry_permitted,
            "fresh_authority_required": False,
            "campaign_replan_required": campaign_replan,
            "preserve_evidence": True,
            "authority_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def new_budget(
    *,
    campaign_id: str,
    allowed_work_items_per_wake: int = 1,
    allowed_seat_invocations_per_wake: int = 1,
    allowed_repairs: int = 0,
    max_files_per_item: int = 4,
) -> dict[str, Any]:
    if min(
        allowed_work_items_per_wake,
        allowed_seat_invocations_per_wake,
        allowed_repairs,
        max_files_per_item,
    ) < 0:
        raise WorkcycleError("budget values must be nonnegative")
    return seal_object(
        {
            "object_type": BUDGET_TYPE,
            "campaign_id": campaign_id,
            "work_items": {
                "allowed_per_wake": allowed_work_items_per_wake,
                "reserved": 0,
                "consumed": 0,
            },
            "seat_invocations": {
                "allowed_per_wake": allowed_seat_invocations_per_wake,
                "reserved": 0,
                "consumed": 0,
            },
            "repair_attempts": {
                "allowed": allowed_repairs,
                "reserved": 0,
                "consumed": 0,
            },
            "mutation": {
                "max_files_per_item": max_files_per_item,
                "source_deletions_allowed": 0,
                "trust_root_mutations_allowed": 0,
            },
            "authority": {
                "allowed_classes": ["REPO_LOCAL_CANDIDATE"],
                "forbidden": ["TRUST_ROOT_PROMOTION", "SOURCE_DELETION"],
            },
            "integrity_sha256": "",
        }
    )


def reserve_one_item(budget: Mapping[str, Any]) -> dict[str, Any]:
    verify_seal(budget)
    retained = copy.deepcopy(dict(budget))
    for field in ("work_items", "seat_invocations"):
        slot = retained[field]
        if slot["reserved"] + slot["consumed"] >= slot["allowed_per_wake"]:
            raise WorkcycleError(f"{field} budget exhausted")
    retained["work_items"]["reserved"] += 1
    retained["seat_invocations"]["reserved"] += 1
    return seal_object(retained)


def settle_one_item(budget: Mapping[str, Any]) -> dict[str, Any]:
    verify_seal(budget)
    retained = copy.deepcopy(dict(budget))
    for field in ("work_items", "seat_invocations"):
        slot = retained[field]
        if slot["reserved"] < 1:
            raise WorkcycleError(f"no reserved {field} budget to settle")
        slot["reserved"] -= 1
        slot["consumed"] += 1
    return seal_object(retained)


def reset_wake_budget(budget: Mapping[str, Any]) -> dict[str, Any]:
    """Open a new wake only when no prior reservation remains unsettled."""
    verify_seal(budget)
    retained = copy.deepcopy(dict(budget))
    for field in ("work_items", "seat_invocations", "repair_attempts"):
        if retained[field]["reserved"] != 0:
            raise WorkcycleError("cannot reset wake with unsettled reservations")
        retained[field]["consumed"] = 0
    return seal_object(retained)


def evaluate_eligibility(
    *,
    dependency_satisfied: bool,
    frame_current: bool,
    seat_available: bool,
    no_hold: bool,
    authority_satisfied: bool,
    budget: Mapping[str, Any],
) -> dict[str, Any]:
    verify_seal(budget)
    budget_available = all(
        budget[field]["reserved"] + budget[field]["consumed"]
        < budget[field]["allowed_per_wake"]
        for field in ("work_items", "seat_invocations")
    )
    coordinates = {
        "dependency_satisfied": dependency_satisfied,
        "frame_current": frame_current,
        "seat_available": seat_available,
        "no_hold": no_hold,
        "authority_satisfied": authority_satisfied,
        "budget_reservable": budget_available,
    }
    blockers = [key for key, value in coordinates.items() if not value]
    return {
        "eligible": not blockers,
        "coordinates": coordinates,
        "blockers": blockers,
    }


def evaluate_one_successor_continuation(
    *,
    control: Mapping[str, Any],
    dependency_satisfied: bool,
    frame_current: bool,
    seat_available: bool,
    no_hold: bool,
    authority_satisfied: bool,
    budget: Mapping[str, Any],
) -> dict[str, Any]:
    """Decide whether one successor may be admitted for execution.

    This function never invokes a model or mutates the supplied budget.
    """
    eligibility = evaluate_eligibility(
        dependency_satisfied=dependency_satisfied,
        frame_current=frame_current,
        seat_available=seat_available,
        no_hold=no_hold,
        authority_satisfied=authority_satisfied,
        budget=budget,
    )
    control_coordinates = {
        "workflow_enabled": bool(control.get("workflow_enabled")),
        "campaign_enabled": bool(control.get("campaign_enabled")),
        "seat_work_enabled": bool(control.get("seat_work_enabled")),
        "wake_requested": bool(control.get("wake_requested")),
        "auto_continuation_available": int(control.get("auto_continuation_limit", 0)) >= 1,
    }
    blockers = list(eligibility["blockers"])
    blockers.extend(
        key for key, value in control_coordinates.items() if not value
    )
    return {
        "admit_one_successor": not blockers,
        "lifecycle_coordinates": eligibility["coordinates"],
        "control_coordinates": control_coordinates,
        "blockers": blockers,
        "max_successors_admitted": 1 if not blockers else 0,
        "execution_performed": False,
        "authority_effect": "NONE",
    }
