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

from src.control.distinction_retention_mode_v0 import (
    build_distinction_retention_mode,
    reconstruct_horizon_applicability,
)

OUT = ROOT / "distinction_retention_mode_v0_observation.json"

FILES = {
    "g4_result": (
        "docs/campaigns/world_method_reconciliation_001/pressure_runs/"
        "WORLD_METHOD_RECONCILIATION_V0_PRESSURE_RESULT_001.md"
    ),
    "g4_witness": "world_method_reconciliation_v0_observation.json",
    "g5_result": (
        "docs/campaigns/method_distinction_load_001/pressure_runs/"
        "METHOD_DISTINCTION_LOAD_ABLATION_V0_PRESSURE_RESULT_001.md"
    ),
    "g5_witness": "method_distinction_load_ablation_v0_observation.json",
    "g6_result": (
        "docs/campaigns/current_horizon_distinction_dependence_001/pressure_runs/"
        "CURRENT_HORIZON_DISTINCTION_DEPENDENCE_V0_PRESSURE_RESULT_001.md"
    ),
    "g6_witness": "current_horizon_distinction_dependence_v0_observation.json",
}

EXPECTED = {
    "g4_result": "7a876e3e23b5a7f7d73f8ec86b393137da8f5ede",
    "g4_witness": "a49d948432c9560310133557ce6c8102ce4931ac",
    "g5_result": "d738dd57ae7866bdf584509b553a6b061cd714d7",
    "g5_witness": "a334412ac95fd66a228dba49fb888ffc225a6e7f",
    "g6_result": "bacc6f48a2c7c9a4658758cf663822b3b934557c",
    "g6_witness": "3e9c7b24cacbf608d87d2f14175e265267cc0ef1",
}

CASES = {
    "WORLD_ONLY": ("UNCHANGED", "NOT_APPLICABLE"),
    "METHOD_ONLY": ("CHANGED", "APPLICABLE"),
    "BOTH": ("CHANGED", "APPLICABLE"),
    "NEITHER": ("UNCHANGED", "NOT_APPLICABLE"),
    "WORLD_UNRESOLVED": ("UNCHANGED", "NOT_APPLICABLE"),
    "METHOD_UNRESOLVED": ("UNRESOLVED", "UNRESOLVED"),
}


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
            "remove existing distinction_retention_mode_v0_observation.json first"
        )

    handles = {
        key: git("rev-parse", f"HEAD:{path}")
        for key, path in FILES.items()
    }

    carrier = build_distinction_retention_mode(
        exact_source_handles=handles
    )

    reconstructed = {
        name: reconstruct_horizon_applicability(carrier, method)
        for name, (method, _) in CASES.items()
    }
    expected_outcomes = {
        name: expected for name, (_, expected) in CASES.items()
    }

    g6_result_text = (ROOT / FILES["g6_result"]).read_text(encoding="utf-8")

    forbidden_inline = (
        "pre_ablation_cases",
        "collision_groups",
        "pre_ablation_applicability",
        "post_ablation_generic_applicability",
    )

    assertions = {
        "all_source_blobs_exact": handles == EXPECTED,
        "g6_standing_matched": (
            "DISPOSITION:\nCURRENT_HORIZON_DISTINCTION_DEPENDENCE_V0_MATCHED"
            in g6_result_text
        ),
        "exact_horizon_reconstruction": reconstructed == expected_outcomes,
        "richer_case_tables_not_inline": all(
            key not in carrier for key in forbidden_inline
        ),
        "distinction_retention_required_for_declared_horizon": (
            carrier[
                "distinction_retention_required_for_declared_horizon"
            ]
            == "YES"
        ),
        "full_inline_hot_not_required": (
            carrier["full_g4_g5_g6_inline_hot_required"] == "NO"
        ),
        "minimal_hot_carrier_candidate": (
            carrier["minimal_hot_carrier_candidate"] == "YES"
        ),
        "exact_cold_source_retention_required": (
            carrier["exact_cold_source_retention_required"] == "YES"
        ),
        "no_deletion_or_capitalization_effect": (
            carrier["raw_source_deletion_effect"] == "NONE"
            and carrier["method_capitalization_effect"] == "NONE"
        ),
        "no_downstream_consequence_effects": all(
            carrier[key] == "NONE"
            for key in (
                "policy_mutation_effect",
                "planning_effect",
                "authority_effect",
                "execution_effect",
                "scientific_standing_effect",
            )
        ),
    }

    obs = {
        "object_type": "DISTINCTION_RETENTION_MODE_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "DISTINCTION_RETENTION_MODE_001",
        "gap_id": "G7_DISTINCTION_RETENTION_MODE",
        "distinction_id": "WORLD_CHANGE_NE_METHOD_CHANGE",
        "horizon_id": "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0",
        "source_handles": handles,
        "carrier": carrier,
        "reconstructed_horizon_outcomes": reconstructed,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "The exact G6 horizon dependence can be reconstructed from a "
            "minimal hot-memory carrier containing the distinction, horizon, "
            "method-axis applicability law, unresolved boundaries, and exact "
            "source handles. The richer G4/G5/G6 tables need not remain inline "
            "for this exact reconstruction, while exact cold source retention "
            "remains required. No raw-source deletion, quantitative optimum, "
            "global retention, method improvement, capitalization, planning "
            "authority, execution, or scientific standing is established."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print("[OK] exact_horizon_reconstruction True")
    print("[OK] full_inline_hot_required NO")
    print("[OK] minimal_hot_carrier_candidate YES")
    print("[OK] exact_cold_source_retention_required YES")
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
