#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.partial_basis_retention_profile_v0 import (
    build_partial_basis_retention_profile,
    evaluate_basis_extension,
)

OUT = ROOT / "partial_basis_retention_profile_v0_observation.json"
G9_RESULT = (
    ROOT
    / "docs/campaigns/retention_scope_aggregation_001/pressure_runs/"
      "RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_RESULT_001.md"
)
G9_WITNESS = ROOT / "retention_scope_aggregation_v0_observation.json"

EXPECTED_G9_RESULT_BLOB = "94152a26078c527cabfef7cd2cf1e7e3b4990df1"
EXPECTED_G9_WITNESS_BLOB = "212d7a9d4fb7bc982cb83b418ee6d5982008c574"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing partial_basis_retention_profile_v0_observation.json first"
        )

    g9_result_text = G9_RESULT.read_text(encoding="utf-8")
    g9_witness = json.loads(G9_WITNESS.read_text(encoding="utf-8"))

    g9_result_blob = git(
        "rev-parse",
        "HEAD:docs/campaigns/retention_scope_aggregation_001/pressure_runs/"
        "RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_RESULT_001.md",
    )
    g9_witness_blob = git(
        "rev-parse", "HEAD:retention_scope_aggregation_v0_observation.json"
    )

    b0 = build_partial_basis_retention_profile(
        source_g9_result_blob_sha=g9_result_blob,
        source_g9_witness_blob_sha=g9_witness_blob,
        basis_id="B0",
        horizon_requirements={
            "H_A": "REQUIRED",
            "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
        },
    )

    b1 = build_partial_basis_retention_profile(
        source_g9_result_blob_sha=g9_result_blob,
        source_g9_witness_blob_sha=g9_witness_blob,
        basis_id="B1",
        horizon_requirements={
            "H_A": "REQUIRED",
            "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            "H_C": "UNRESOLVED",
        },
    )

    extension = evaluate_basis_extension(b0, b1)

    expected_b0 = {
        "required_members": ["H_A"],
        "unresolved_members": [],
        "not_required_members": ["H_B"],
        "n_required": 1,
        "n_unresolved": 0,
        "n_not_required": 1,
        "basis_size": 2,
    }
    expected_b1 = {
        "required_members": ["H_A"],
        "unresolved_members": ["H_C"],
        "not_required_members": ["H_B"],
        "n_required": 1,
        "n_unresolved": 1,
        "n_not_required": 1,
        "basis_size": 3,
    }

    assertions = {
        "g9_result_blob_exact": g9_result_blob == EXPECTED_G9_RESULT_BLOB,
        "g9_witness_blob_exact": g9_witness_blob == EXPECTED_G9_WITNESS_BLOB,
        "g9_standing_matched": (
            "DISPOSITION:\nRETENTION_SCOPE_AGGREGATION_V0_MATCHED"
            in g9_result_text
        ),
        "g9_scope_aggregation_witness_passed": (
            g9_witness["all_assertions_pass"] is True
        ),
        "b0_profile_exact": b0["retention_profile"] == expected_b0,
        "b1_profile_exact": b1["retention_profile"] == expected_b1,
        "b0_scope_requirement_required": (
            b0["declared_scope_hot_requirement"] == "REQUIRED"
        ),
        "b1_scope_requirement_required": (
            b1["declared_scope_hot_requirement"] == "REQUIRED"
        ),
        "prior_local_coordinates_preserved": (
            extension["prior_local_coordinates_preserved"] == "YES"
        ),
        "new_horizon_exact": extension["new_horizons"] == ["H_C"],
        "exterior_unresolved_both_bases": (
            b0["exterior_posture"] == "UNRESOLVED"
            and b1["exterior_posture"] == "UNRESOLVED"
        ),
        "global_ecology_hot_unresolved_both_bases": (
            b0["global_ecology_hot_requirement"] == "UNRESOLVED"
            and b1["global_ecology_hot_requirement"] == "UNRESOLVED"
        ),
        "no_scalar_hotness_fields": all(
            key not in b0 and key not in b1
            for key in (
                "scalar_hotness",
                "load_weight",
                "utility",
                "economic_value",
            )
        ),
        "no_transition_or_downstream_effects": all(
            all(
                profile[key] == "NONE"
                for key in (
                    "retention_transition_effect",
                    "raw_source_deletion_effect",
                    "method_capitalization_effect",
                    "policy_mutation_effect",
                    "planning_effect",
                    "authority_effect",
                    "execution_effect",
                    "scientific_standing_effect",
                )
            )
            for profile in (b0, b1)
        ),
    }

    obs = {
        "object_type": "PARTIAL_BASIS_RETENTION_PROFILE_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "PARTIAL_BASIS_RETENTION_PROFILE_001",
        "gap_id": "G10_PARTIAL_DECLARED_BASIS_RETENTION_PROFILE",
        "distinction_id": "WORLD_CHANGE_NE_METHOD_CHANGE",
        "basis": {
            "g9_result": (
                "docs/campaigns/retention_scope_aggregation_001/pressure_runs/"
                "RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_RESULT_001.md"
            ),
            "g9_result_blob": g9_result_blob,
            "g9_witness": "retention_scope_aggregation_v0_observation.json",
            "g9_witness_blob": g9_witness_blob,
        },
        "b0": b0,
        "b1": b1,
        "extension": extension,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "One exact partial declared basis for WORLD_CHANGE != METHOD_CHANGE "
            "can carry a non-scalar retention profile over REQUIRED, UNRESOLVED, "
            "and NOT_REQUIRED member sets while the exterior remains explicitly "
            "UNRESOLVED. Extending B0 to B1 by adding H_C preserves unchanged "
            "prior horizon-local coordinates. Counts are occupancy only and do "
            "not establish load weights, scalar hotness, global ecology coverage, "
            "economic optimality, global invariance, cooling authority, "
            "retention transition, authority, execution, or scientific standing."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print("[OK] B0 profile (1,0,1)")
    print("[OK] B1 profile (1,1,1)")
    print("[OK] prior_local_coordinates_preserved YES")
    print("[OK] exterior_posture UNRESOLVED")
    print("[OK] scalar_hotness NOT_ESTABLISHED")
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
