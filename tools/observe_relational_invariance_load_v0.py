#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
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

OUT = ROOT / "docs" / "evidence" / "for_planner" / "relational_invariance_load_v0_observation.json"

EXPECTED_BLOBS = {
    "g19_adjudication": (
        "docs/campaigns/relational_change_stewardship_001/pressure_runs/RELATIONAL_CHANGE_STEWARDSHIP_V0_ADJUDICATION_RESULT_001.md",
        "b22483a5ecf9551bfdf9c22834367db4082640a5",
    ),
    "g19_steward": (
        "src/control/relational_change_steward_v0.py",
        "8dddd57779d2432dd87c92ce95056dee2be398b5",
    ),
    "g22_adjudication": (
        "docs/campaigns/invariance_catalogue_carrier_reconstruction_001/pressure_runs/INVARIANCE_CATALOGUE_CARRIER_RECONSTRUCTION_LOAD_V0_ADJUDICATION_RESULT_001.md",
        "c7597a8e8f5e9c9306b288bed50608ef182e23bd",
    ),
    "projection": (
        "docs/projections/RELATIONAL_INVARIANCE_FOUNDATION_PRESSURE_TRAIN_V0.md",
        "d8b8727b752ed318d60f877466fe536d1a8abc87",
    ),
    "horizon": (
        "docs/campaigns/relational_invariance_load_001/HORIZON_SELECTION_RIL1_V0.md",
        "77f1cc23a6fb5db096c39df13e7aebd77b59825b",
    ),
}


def git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def run_case(
    case_id: str,
    before: RelationState,
    after: RelationState,
    obligations: RelationObligations,
    flow_witness: str,
) -> dict:
    result = steward_relation_change(
        relation_id=case_id,
        before=before,
        after=after,
        obligations=obligations,
        flow_witness=flow_witness,
    )
    return {
        "case_id": case_id,
        "result": result,
    }


def normalized_consequence_signature(case: dict) -> dict:
    result = case["result"]
    before = result["before"]
    after = result["after"]

    return {
        "change_pattern": {
            "endpoint_changed": before["endpoint"] != after["endpoint"],
            "counterpart_changed": before["counterpart"] != after["counterpart"],
            "edge_changed": before["edge"] != after["edge"],
        },
        "obligations": result["obligations"],
        "checks": result["checks"],
        "closure_posture": result["closure_posture"],
        "effects": result["effects"],
    }


def endpoint_local_state(case: dict) -> dict:
    result = case["result"]
    return {
        "before_endpoint": result["before"]["endpoint"],
        "after_endpoint": result["after"]["endpoint"],
        "before_counterpart": result["before"]["counterpart"],
        "after_counterpart": result["after"]["counterpart"],
    }


def full_relation_state(case: dict) -> dict:
    result = case["result"]
    return {
        "before": result["before"],
        "after": result["after"],
        "obligations": result["obligations"],
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    actual_blobs = {
        name: git_blob(path)
        for name, (path, _) in EXPECTED_BLOBS.items()
    }
    blob_checks = {
        name: actual_blobs[name] == expected
        for name, (_, expected) in EXPECTED_BLOBS.items()
    }
    if not all(blob_checks.values()):
        raise SystemExit(f"frozen blob mismatch: {blob_checks}")

    common_obligations = RelationObligations(
        endpoint="CHANGE",
        counterpart="PRESERVE",
        edge="PRESERVE",
        flow="PASS",
    )

    r0 = run_case(
        "R0_BASE_COHERENT",
        RelationState(endpoint="A0", counterpart="B0", edge="E0"),
        RelationState(endpoint="A1", counterpart="B0", edge="E0"),
        common_obligations,
        "PASS",
    )

    r1 = run_case(
        "R1_BIJECTIVE_SYMBOL_RENAMING",
        RelationState(endpoint="P7", counterpart="Q3", edge="LINK9"),
        RelationState(endpoint="P8", counterpart="Q3", edge="LINK9"),
        common_obligations,
        "PASS",
    )

    r2 = run_case(
        "R2_EDGE_DRIFT",
        RelationState(endpoint="A0", counterpart="B0", edge="E0"),
        RelationState(endpoint="A1", counterpart="B0", edge="E1"),
        common_obligations,
        "PASS",
    )

    r3 = run_case(
        "R3_FLOW_LOSS",
        RelationState(endpoint="A0", counterpart="B0", edge="E0"),
        RelationState(endpoint="A1", counterpart="B0", edge="E0"),
        common_obligations,
        "ABSENT",
    )

    base_sig = normalized_consequence_signature(r0)
    renamed_sig = normalized_consequence_signature(r1)

    checks = {
        "frozen_blobs_match": all(blob_checks.values()),
        "r0_coherent": r0["result"]["closure_posture"] == "COHERENT",
        "r1_coherent": r1["result"]["closure_posture"] == "COHERENT",
        "r1_raw_labels_differ_from_r0": (
            r1["result"]["before"] != r0["result"]["before"]
            and r1["result"]["after"] != r0["result"]["after"]
        ),
        "r1_normalized_consequence_signature_matches_r0": renamed_sig == base_sig,
        "r2_endpoint_local_state_matches_r0": (
            endpoint_local_state(r2) == endpoint_local_state(r0)
        ),
        "r2_edge_state_differs_from_r0": (
            r2["result"]["after"]["edge"] != r0["result"]["after"]["edge"]
        ),
        "r2_hold": r2["result"]["closure_posture"] == "HOLD",
        "r2_consequence_differs_from_r0": (
            r2["result"]["closure_posture"] != r0["result"]["closure_posture"]
        ),
        "r3_static_relation_state_matches_r0": (
            full_relation_state(r3) == full_relation_state(r0)
        ),
        "r3_flow_witness_differs_from_r0": (
            r3["result"]["checks"]["flow_witness"]
            != r0["result"]["checks"]["flow_witness"]
        ),
        "r3_hold": r3["result"]["closure_posture"] == "HOLD",
        "r3_consequence_differs_from_r0": (
            r3["result"]["closure_posture"] != r0["result"]["closure_posture"]
        ),
    }

    observation = {
        "object_type": "RELATIONAL_INVARIANCE_LOAD_V0_OBSERVATION",
        "pressure_id": "RELATIONAL_INVARIANCE_LOAD_V0_PRESSURE_001",
        "frozen_basis": {
            "expected_blobs": {
                name: expected
                for name, (_, expected) in EXPECTED_BLOBS.items()
            },
            "actual_blobs": actual_blobs,
            "blob_checks": blob_checks,
        },
        "declared_transformation_class": (
            "BIJECTIVE_SYMBOL_RENAMING_PRESERVING_EQUALITY_AND_CHANGE_STRUCTURE"
        ),
        "cases": {
            "r0_base": r0,
            "r1_symbol_renaming": r1,
            "r2_edge_drift": r2,
            "r3_flow_loss": r3,
        },
        "normalized_signatures": {
            "r0_base": base_sig,
            "r1_symbol_renaming": renamed_sig,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "candidate_relations": {
            "qualified_relational_consequence_invariant_under_bijective_symbol_renaming": "YES",
            "endpoint_local_state_equivalence_ne_relational_consequence_equivalence": "YES",
            "static_relation_state_equivalence_ne_flow_consequence_equivalence": "YES",
            "relational_configuration_carries_consequential_load_beyond_endpoint_local_state": "YES",
        },
        "effects": {
            "relation_discovery_effect": "NONE",
            "topology_law_effect": "NONE",
            "trajectory_law_effect": "NONE",
            "planning_effect": "NONE",
            "seat_identity_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One deterministic stewardship operator over four supplied synthetic "
            "cases. The pressure tests consequence preservation under one declared "
            "bijective symbol-renaming class and consequence change under one edge "
            "drift and one missing-flow intervention. No physical causation claim, "
            "universal ontology, global coupling claim, multi-relation topology law, "
            "trajectory/history law, planning activation, seat identity law, "
            "authority, execution, or scientific standing is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] R0 closure {r0['result']['closure_posture']}")
    print(f"[OK] R1 closure {r1['result']['closure_posture']}")
    print(
        "[OK] R1 normalized signature matches R0 "
        f"{checks['r1_normalized_consequence_signature_matches_r0']}"
    )
    print(f"[OK] R2 closure {r2['result']['closure_posture']}")
    print(
        "[OK] R2 endpoint-local state matches R0 "
        f"{checks['r2_endpoint_local_state_matches_r0']}"
    )
    print(f"[OK] R3 closure {r3['result']['closure_posture']}")
    print(
        "[OK] R3 static relation state matches R0 "
        f"{checks['r3_static_relation_state_matches_r0']}"
    )
    print(f"[OK] all_checks_pass {observation['all_checks_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
