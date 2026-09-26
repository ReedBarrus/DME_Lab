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

from src.control.distinction_retention_currentness_v0 import (
    build_distinction_retention_currentness,
)

OUT = ROOT / "distinction_retention_currentness_v0_observation.json"
G7_RESULT = (
    ROOT
    / "docs/campaigns/distinction_retention_mode_001/pressure_runs/"
      "DISTINCTION_RETENTION_MODE_V0_PRESSURE_RESULT_001.md"
)
G7_WITNESS = ROOT / "distinction_retention_mode_v0_observation.json"

EXPECTED_G7_RESULT_BLOB = "7d037362dd0e438ae7c1fb2553d452a9ae2fd233"
EXPECTED_G7_WITNESS_BLOB = "1ff52354096371710ccdcdd77dfb9a6b2c1ada3b"


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
            "remove existing distinction_retention_currentness_v0_observation.json first"
        )

    g7_result_text = G7_RESULT.read_text(encoding="utf-8")
    g7_witness = json.loads(G7_WITNESS.read_text(encoding="utf-8"))

    g7_result_blob = git(
        "rev-parse",
        "HEAD:docs/campaigns/distinction_retention_mode_001/pressure_runs/"
        "DISTINCTION_RETENTION_MODE_V0_PRESSURE_RESULT_001.md",
    )
    g7_witness_blob = git(
        "rev-parse", "HEAD:distinction_retention_mode_v0_observation.json"
    )

    cases = {
        posture: build_distinction_retention_currentness(
            source_g7_result_blob_sha=g7_result_blob,
            source_g7_witness_blob_sha=g7_witness_blob,
            horizon_currentness=posture,
        )
        for posture in ("CURRENT", "NONCURRENT", "UNRESOLVED")
    }

    assertions = {
        "g7_result_blob_exact": g7_result_blob == EXPECTED_G7_RESULT_BLOB,
        "g7_witness_blob_exact": g7_witness_blob == EXPECTED_G7_WITNESS_BLOB,
        "g7_standing_matched": (
            "DISPOSITION:\nDISTINCTION_RETENTION_MODE_V0_MATCHED"
            in g7_result_text
        ),
        "g7_retention_required_for_declared_horizon": (
            g7_witness["carrier"][
                "distinction_retention_required_for_declared_horizon"
            ]
            == "YES"
        ),
        "current_requires_hot": (
            cases["CURRENT"]["declared_horizon_hot_requirement"]
            == "REQUIRED"
        ),
        "noncurrent_removes_declared_horizon_requirement_only": (
            cases["NONCURRENT"]["declared_horizon_hot_requirement"]
            == "NOT_REQUIRED_FOR_DECLARED_HORIZON"
            and cases["NONCURRENT"]["global_hot_requirement"]
            == "UNRESOLVED"
        ),
        "unresolved_currentness_stays_unresolved": (
            cases["UNRESOLVED"]["declared_horizon_hot_requirement"]
            == "UNRESOLVED"
        ),
        "global_hot_requirement_unresolved_all_cases": all(
            case["global_hot_requirement"] == "UNRESOLVED"
            for case in cases.values()
        ),
        "cold_source_retention_required_all_cases": all(
            case["exact_cold_source_retention_required"] == "YES"
            for case in cases.values()
        ),
        "no_transition_or_deletion_effect": all(
            case["retention_transition_effect"] == "NONE"
            and case["raw_source_deletion_effect"] == "NONE"
            for case in cases.values()
        ),
        "no_downstream_consequence_effects": all(
            all(
                case[key] == "NONE"
                for key in (
                    "method_capitalization_effect",
                    "policy_mutation_effect",
                    "planning_effect",
                    "authority_effect",
                    "execution_effect",
                    "scientific_standing_effect",
                )
            )
            for case in cases.values()
        ),
    }

    obs = {
        "object_type": "DISTINCTION_RETENTION_CURRENTNESS_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "DISTINCTION_RETENTION_CURRENTNESS_001",
        "gap_id": "G8_RETENTION_CURRENTNESS_MEMBRANE",
        "distinction_id": "WORLD_CHANGE_NE_METHOD_CHANGE",
        "horizon_id": "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0",
        "basis": {
            "g7_result": (
                "docs/campaigns/distinction_retention_mode_001/pressure_runs/"
                "DISTINCTION_RETENTION_MODE_V0_PRESSURE_RESULT_001.md"
            ),
            "g7_result_blob": g7_result_blob,
            "g7_witness": "distinction_retention_mode_v0_observation.json",
            "g7_witness_blob": g7_witness_blob,
        },
        "cases": cases,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "The exact G7 horizon-scoped hot-retention requirement is "
            "currentness-conditioned for the exact declared horizon: CURRENT "
            "preserves REQUIRED, NONCURRENT yields "
            "NOT_REQUIRED_FOR_DECLARED_HORIZON, and UNRESOLVED remains "
            "UNRESOLVED. Global hot requirement remains UNRESOLVED and exact "
            "cold source retention remains required in all cases. No retention "
            "transition, deletion, global cooling, depreciation, quantitative "
            "cost optimum, capitalization, authority, execution, or scientific "
            "standing is established."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print("[OK] CURRENT -> REQUIRED")
    print("[OK] NONCURRENT -> NOT_REQUIRED_FOR_DECLARED_HORIZON")
    print("[OK] UNRESOLVED -> UNRESOLVED")
    print("[OK] global_hot_requirement UNRESOLVED")
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
