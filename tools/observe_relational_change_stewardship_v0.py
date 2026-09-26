#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.relational_change_steward_v0 import (
    RelationObligations,
    RelationState,
    steward_relation_change,
)

OUT = ROOT / "docs" / "evidence" / "for_planner" / "relational_change_stewardship_v0_observation.json"


def run_case(name: str, before, after, obligations, flow_witness):
    result = steward_relation_change(
        relation_id=name,
        before=before,
        after=after,
        obligations=obligations,
        flow_witness=flow_witness,
    )
    return {
        "case_id": name,
        "result": result,
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    before = RelationState(endpoint="A0", counterpart="B0", edge="E0")

    common = RelationObligations(
        endpoint="CHANGE",
        counterpart="PRESERVE",
        edge="PRESERVE",
        flow="PASS",
    )

    c1 = run_case(
        "C1_COHERENT",
        before,
        RelationState(endpoint="A1", counterpart="B0", edge="E0"),
        common,
        "PASS",
    )

    c2 = run_case(
        "C2_MISSING_FLOW",
        before,
        RelationState(endpoint="A1", counterpart="B0", edge="E0"),
        common,
        "ABSENT",
    )

    c3 = run_case(
        "C3_COUNTERPART_DRIFT",
        before,
        RelationState(endpoint="A1", counterpart="B1", edge="E0"),
        common,
        "PASS",
    )

    c4 = run_case(
        "C4_UNRESOLVED",
        before,
        RelationState(endpoint="A1", counterpart="B0", edge="E0"),
        RelationObligations(
            endpoint="CHANGE",
            counterpart="UNRESOLVED",
            edge="PRESERVE",
            flow="PASS",
        ),
        "PASS",
    )

    cases = [c1, c2, c3, c4]
    expected = {
        "C1_COHERENT": "COHERENT",
        "C2_MISSING_FLOW": "HOLD",
        "C3_COUNTERPART_DRIFT": "HOLD",
        "C4_UNRESOLVED": "UNRESOLVED",
    }

    checks = {
        case["case_id"]: (
            case["result"]["closure_posture"] == expected[case["case_id"]]
        )
        for case in cases
    }

    observation = {
        "object_type": "RELATIONAL_CHANGE_STEWARDSHIP_V0_OBSERVATION",
        "pressure_id": "RELATIONAL_CHANGE_STEWARDSHIP_V0_PRESSURE_001",
        "cases": cases,
        "expected_closure": expected,
        "checks": checks,
        "all_cases_match": all(checks.values()),
        "candidate_relation": {
            "local_transformation_success_ne_relational_closure": "YES",
            "required_flow_witness_carries_closure_load": "YES",
            "counterpart_preservation_carries_closure_load": "YES",
        },
        "effects": {
            "mutation_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One deterministic four-case pressure over supplied relation states, "
            "supplied post-change obligations, and supplied flow witnesses. "
            "No relation discovery, propagation inference, planning activation, "
            "mutation authority, execution, or global coherence claim is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    for case in cases:
        cid = case["case_id"]
        print(f"[OK] {cid} -> {case['result']['closure_posture']}")
    print(f"[OK] all_cases_match {observation['all_cases_match']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
