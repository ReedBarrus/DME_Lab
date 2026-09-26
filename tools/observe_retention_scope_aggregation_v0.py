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

from src.control.retention_scope_aggregation_v0 import (
    build_retention_scope_aggregation,
)

OUT = ROOT / "retention_scope_aggregation_v0_observation.json"
G8_RESULT = (
    ROOT
    / "docs/campaigns/distinction_retention_currentness_001/pressure_runs/"
      "DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_RESULT_001.md"
)
G8_WITNESS = ROOT / "distinction_retention_currentness_v0_observation.json"

EXPECTED_G8_RESULT_BLOB = "e5f603fbea6ef05193f092245252cd26d6eae66a"
EXPECTED_G8_WITNESS_BLOB = "949ff2b9333146ca16e68981123f338f6e4dfd15"


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
            "remove existing retention_scope_aggregation_v0_observation.json first"
        )

    g8_result_text = G8_RESULT.read_text(encoding="utf-8")
    g8_witness = json.loads(G8_WITNESS.read_text(encoding="utf-8"))

    g8_result_blob = git(
        "rev-parse",
        "HEAD:docs/campaigns/distinction_retention_currentness_001/pressure_runs/"
        "DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_RESULT_001.md",
    )
    g8_witness_blob = git(
        "rev-parse",
        "HEAD:distinction_retention_currentness_v0_observation.json",
    )

    cases = {
        "REQUIRED_PLUS_NOT_REQUIRED": {
            "H_CURRENT": "REQUIRED",
            "H_NONCURRENT": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
        },
        "ALL_NOT_REQUIRED": {
            "H_A": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
        },
        "NOT_REQUIRED_PLUS_UNRESOLVED": {
            "H_A": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            "H_B": "UNRESOLVED",
        },
        "REQUIRED_PLUS_UNRESOLVED": {
            "H_A": "REQUIRED",
            "H_B": "UNRESOLVED",
        },
    }

    results = {
        name: build_retention_scope_aggregation(
            source_g8_result_blob_sha=g8_result_blob,
            source_g8_witness_blob_sha=g8_witness_blob,
            horizon_requirements=requirements,
        )
        for name, requirements in cases.items()
    }

    assertions = {
        "g8_result_blob_exact": g8_result_blob == EXPECTED_G8_RESULT_BLOB,
        "g8_witness_blob_exact": g8_witness_blob == EXPECTED_G8_WITNESS_BLOB,
        "g8_standing_matched": (
            "DISPOSITION:\nDISTINCTION_RETENTION_CURRENTNESS_V0_MATCHED"
            in g8_result_text
        ),
        "g8_current_required": (
            g8_witness["cases"]["CURRENT"][
                "declared_horizon_hot_requirement"
            ] == "REQUIRED"
        ),
        "required_plus_not_required_scope_required": (
            results["REQUIRED_PLUS_NOT_REQUIRED"][
                "declared_scope_hot_requirement"
            ] == "REQUIRED"
        ),
        "all_not_required_scope_not_required": (
            results["ALL_NOT_REQUIRED"][
                "declared_scope_hot_requirement"
            ] == "NOT_REQUIRED_FOR_DECLARED_SCOPE"
        ),
        "unresolved_survives_without_required": (
            results["NOT_REQUIRED_PLUS_UNRESOLVED"][
                "declared_scope_hot_requirement"
            ] == "UNRESOLVED"
        ),
        "required_dominates_unresolved": (
            results["REQUIRED_PLUS_UNRESOLVED"][
                "declared_scope_hot_requirement"
            ] == "REQUIRED"
        ),
        "declared_scope_complete_all_cases": all(
            result["declared_scope_complete_for_supplied_horizons"] == "YES"
            for result in results.values()
        ),
        "global_ecology_hot_unresolved_all_cases": all(
            result["global_ecology_hot_requirement"] == "UNRESOLVED"
            for result in results.values()
        ),
        "cold_source_retention_required_all_cases": all(
            result["exact_cold_source_retention_required"] == "YES"
            for result in results.values()
        ),
        "no_transition_or_downstream_effects": all(
            all(
                result[key] == "NONE"
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
            for result in results.values()
        ),
    }

    obs = {
        "object_type": "RETENTION_SCOPE_AGGREGATION_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "RETENTION_SCOPE_AGGREGATION_001",
        "gap_id": "G9_RETENTION_SCOPE_AGGREGATION",
        "distinction_id": "WORLD_CHANGE_NE_METHOD_CHANGE",
        "basis": {
            "g8_result": (
                "docs/campaigns/distinction_retention_currentness_001/pressure_runs/"
                "DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_RESULT_001.md"
            ),
            "g8_result_blob": g8_result_blob,
            "g8_witness": "distinction_retention_currentness_v0_observation.json",
            "g8_witness_blob": g8_witness_blob,
        },
        "cases": results,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Exact non-empty declared sets of horizon-local hot-retention "
            "requirements for WORLD_CHANGE != METHOD_CHANGE can be aggregated "
            "deterministically into one declared-scope posture: REQUIRED if any "
            "local horizon requires it; otherwise UNRESOLVED if any local horizon "
            "is unresolved; otherwise NOT_REQUIRED_FOR_DECLARED_SCOPE. The "
            "declared set is complete only for supplied horizons. Global ecology "
            "hot requirement remains UNRESOLVED. No retention transition, "
            "deletion, cooling authority, cost optimum, capitalization, authority, "
            "execution, or scientific standing is established."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print("[OK] REQUIRED + NOT_REQUIRED -> REQUIRED")
    print("[OK] all NOT_REQUIRED -> NOT_REQUIRED_FOR_DECLARED_SCOPE")
    print("[OK] NOT_REQUIRED + UNRESOLVED -> UNRESOLVED")
    print("[OK] REQUIRED + UNRESOLVED -> REQUIRED")
    print("[OK] global_ecology_hot_requirement UNRESOLVED")
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
