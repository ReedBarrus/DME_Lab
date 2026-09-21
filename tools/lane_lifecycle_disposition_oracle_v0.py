#!/usr/bin/env python3
"""Independent scorer/oracle for LANE_LIFECYCLE_DISPOSITION_001 pressure."""

from __future__ import annotations

import copy
from typing import Any, Dict, Mapping, Sequence


def d1_d3_result(output: Mapping[str, Any]) -> Dict[str, str]:
    state = output.get("resulting_state")
    if state is None:
        return {"D1": "NOT_APPLICABLE", "D2": "NOT_APPLICABLE", "D3": "NOT_APPLICABLE"}

    claim = state.get("claim_status")
    lane = state.get("lane_status")
    occupant = state.get("occupant_binding")
    return {
        "D1": "FAIL" if claim == "ACTIVE" and lane == "READY_UNCLAIMED" and occupant is None else "PASS",
        "D2": "FAIL" if claim == "BLOCKED" and lane == "READY_UNCLAIMED" else "PASS",
        "D3": "FAIL" if claim == "BLOCKED" and lane == "HELD" and occupant is None else "PASS",
    }


def _same_state(observed: Any, expected: Any) -> bool:
    return observed == expected


def score_branch(
    cell_id: str,
    output: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    checks = {
        "requested_transition": output.get("requested_transition") == expected.get("requested_transition"),
        "selected_branch": output.get("selected_branch") == expected.get("selected_branch"),
        "admissible": output.get("admissible") == expected.get("admissible"),
        "blocking_predicate": output.get("blocking_predicate") == expected.get("blocking_predicate"),
        "resulting_state": _same_state(output.get("resulting_state"), expected.get("resulting_state")),
        "authority_effect": output.get("authority_effect") == "NONE",
        "execution_effect": output.get("execution_effect") == "NONE",
        "integration_effect": output.get("integration_effect") == "NONE",
        "historical_claim_retained": isinstance(output.get("historical_claim"), dict),
    }
    required_refs = expected.get("required_refs", [])
    if required_refs:
        checks["required_refs_preserved"] = sorted(output.get("unresolved_refs", [])) == sorted(required_refs)

    d = d1_d3_result(output)
    checks["D1_D3"] = all(v != "FAIL" for v in d.values())
    passed = all(checks.values())
    return {
        "status": expected.get("status") if passed else "MISMATCH",
        "checks": checks,
        "D1_D3": d,
        "pass": passed,
    }


def detect_adversarial_violation(
    cell_id: str,
    mutated: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> Dict[str, Any]:
    violation = None
    status = "VALID"

    if cell_id == "E":
        if "historical_claim" not in mutated:
            violation = "HISTORICAL_CLAIM_NOT_RETAINED"
            status = "INVALID_LIFECYCLE_RESULT"
    elif cell_id == "F":
        required = sorted(baseline.get("unresolved_refs", []))
        observed = sorted(mutated.get("unresolved_refs", []))
        if observed != required:
            violation = "REQUIRED_REFS_NOT_PRESERVED"
            status = "INVALID_LIFECYCLE_RESULT"
    elif cell_id == "G":
        state = mutated.get("resulting_state") or {}
        expected_claim = {
            "COMPLETE": "COMPLETED",
            "RELEASE": "RELEASED",
            "MARK_BLOCKED": "BLOCKED",
        }.get(mutated.get("selected_branch"))
        if state.get("claim_status") != expected_claim:
            violation = "RESULTING_STATE_DOES_NOT_MATCH_SELECTED_BRANCH"
            status = "INVALID_LIFECYCLE_RESULT"
    elif cell_id == "H":
        if any(
            mutated.get(key) != "NONE"
            for key in ("authority_effect", "execution_effect", "integration_effect")
        ):
            violation = "AUTHORITY_OR_EFFECT_MANUFACTURED"
            status = "INVALID"
    else:
        raise ValueError(f"unsupported adversarial cell: {cell_id}")

    d = d1_d3_result(mutated)
    return {
        "status": status,
        "violation": violation,
        "D1_D3": d,
        "pass": violation is not None,
    }


def score_invariant_group(
    observed: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    expected_sub = expected["subcells"]
    checks = {}
    for subcell_id, violation_id in expected_sub.items():
        row = observed["subcells"][subcell_id]
        checks[subcell_id] = (
            row.get("valid") is False
            and violation_id in row.get("violations", [])
        )
    passed = all(checks.values())
    return {
        "status": expected["status"] if passed else "MISMATCH",
        "checks": checks,
        "D1_D3": {
            "D1": "PASS" if checks.get("D1") else "FAIL",
            "D2": "PASS" if checks.get("D2") else "FAIL",
            "D3": "PASS" if checks.get("D3") else "FAIL",
        },
        "pass": passed,
    }


def score_reactivation(
    output: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    checks = {
        "status_invalid": output.get("admissible") is False,
        "reason_code": output.get("reason_code") == expected.get("reason_code"),
        "blocking_predicate": output.get("blocking_predicate") == expected.get("blocking_predicate"),
        "predicates": output.get("predicates_consulted") == ["P13", "P14", "P15", "P16", "P17"],
    }
    return {
        "status": expected["status"] if all(checks.values()) else "MISMATCH",
        "checks": checks,
        "D1_D3": {"D1": "NOT_APPLICABLE", "D2": "NOT_APPLICABLE", "D3": "NOT_APPLICABLE"},
        "pass": all(checks.values()),
    }


def score_guard_intervention(
    baseline: Mapping[str, Any],
    intervention: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    checks = {
        "baseline_admissible": baseline.get("admissible") == expected.get("baseline_admissible"),
        "baseline_selected_branch": baseline.get("selected_branch") == expected.get("selected_branch"),
        "intervention_selected_branch": intervention.get("selected_branch") == expected.get("selected_branch"),
        "intervention_admissible": intervention.get("admissible") == expected.get("intervention_admissible"),
        "blocking_predicate": intervention.get("blocking_predicate") == expected.get("blocking_predicate"),
        "no_postcondition": intervention.get("resulting_state") is None,
    }
    return {
        "status": expected["status"] if all(checks.values()) else "MISMATCH",
        "checks": checks,
        "D1_D3": d1_d3_result(intervention),
        "pass": all(checks.values()),
    }


def score_dispatch_intervention(
    baseline: Mapping[str, Any],
    intervention: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    expected_intervention = expected.get("intervention_selected_branch")
    excluded_expected = sorted(
        x for x in ("COMPLETE", "RELEASE", "MARK_BLOCKED")
        if x != expected_intervention
    )
    checks = {
        "baseline_selected_branch": baseline.get("selected_branch") == expected.get("baseline_selected_branch"),
        "intervention_selected_branch": intervention.get("selected_branch") == expected_intervention,
        "branch_changed": baseline.get("selected_branch") != intervention.get("selected_branch"),
        "excluded_branches": sorted(intervention.get("excluded_branches", [])) == excluded_expected,
        "intervention_admissible": intervention.get("admissible") == expected.get("intervention_admissible"),
    }
    if "resulting_state" in expected:
        checks["resulting_state"] = intervention.get("resulting_state") == expected.get("resulting_state")
    if "blocking_predicate" in expected:
        checks["blocking_predicate"] = intervention.get("blocking_predicate") == expected.get("blocking_predicate")
    return {
        "status": expected["status"] if all(checks.values()) else "MISMATCH",
        "checks": checks,
        "D1_D3": d1_d3_result(intervention),
        "pass": all(checks.values()),
    }
