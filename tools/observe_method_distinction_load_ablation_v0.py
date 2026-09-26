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

from src.control.method_distinction_load_ablation_v0 import (
    build_method_distinction_load_ablation,
)

OUT = ROOT / "method_distinction_load_ablation_v0_observation.json"
G4_WITNESS = ROOT / "world_method_reconciliation_v0_observation.json"
G4_RESULT = (
    ROOT
    / "docs/campaigns/world_method_reconciliation_001/pressure_runs/"
      "WORLD_METHOD_RECONCILIATION_V0_PRESSURE_RESULT_001.md"
)
EXPECTED_G4_WITNESS_BLOB = "a49d948432c9560310133557ce6c8102ce4931ac"


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
            "remove existing method_distinction_load_ablation_v0_observation.json first"
        )

    g4 = json.loads(G4_WITNESS.read_text(encoding="utf-8"))
    g4_result = G4_RESULT.read_text(encoding="utf-8")
    observed_blob = git(
        "rev-parse", "HEAD:world_method_reconciliation_v0_observation.json"
    )

    ablation = build_method_distinction_load_ablation(
        source_g4_observation_blob_sha=observed_blob,
        cases=g4["cases"],
    )

    expected_changed = ["BOTH", "METHOD_ONLY", "WORLD_ONLY"]
    expected_unresolved = ["METHOD_UNRESOLVED", "WORLD_UNRESOLVED"]

    assertions = {
        "g4_standing_matched": (
            "DISPOSITION:\nWORLD_METHOD_RECONCILIATION_V0_MATCHED" in g4_result
        ),
        "g4_witness_blob_exact": observed_blob == EXPECTED_G4_WITNESS_BLOB,
        "g4_witness_assertions_pass": g4["all_assertions_pass"] is True,
        "six_pre_ablation_signatures": (
            ablation["pre_ablation_distinct_signature_count"] == 6
        ),
        "three_post_ablation_signatures": (
            ablation["post_ablation_distinct_signature_count"] == 3
        ),
        "changed_collision_exact": (
            ablation["collision_groups"]["CHANGED"] == expected_changed
        ),
        "unchanged_neither_only": (
            ablation["collision_groups"]["UNCHANGED"] == ["NEITHER"]
        ),
        "unresolved_collision_exact": (
            ablation["collision_groups"]["UNRESOLVED"] == expected_unresolved
        ),
        "semantic_discrimination_loss": (
            ablation["semantic_discrimination_loss"] is True
        ),
        "semantic_load_change_yes": (
            ablation["load_profile"]["semantic"] == "YES"
        ),
        "other_load_dimensions_unresolved": all(
            ablation["load_profile"][key] == "UNRESOLVED"
            for key in (
                "functional",
                "authority",
                "provenance",
                "temporal",
                "coordination",
            )
        ),
        "current_load_bearing_status_unresolved": (
            ablation["current_load_bearing_status"] == "UNRESOLVED"
        ),
        "no_retention_or_capitalization_effect": (
            ablation["retention_effect"] == "NONE"
            and ablation["method_capitalization_effect"] == "NONE"
        ),
        "no_downstream_consequence_effects": all(
            ablation[key] == "NONE"
            for key in (
                "policy_mutation_effect",
                "gap_selection_effect",
                "work_justification_effect",
                "planning_effect",
                "authority_effect",
                "execution_effect",
                "scientific_standing_effect",
            )
        ),
    }

    obs = {
        "object_type": "METHOD_DISTINCTION_LOAD_ABLATION_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "METHOD_DISTINCTION_LOAD_001",
        "gap_id": "G5_METHOD_DISTINCTION_LOAD_ABLATION",
        "specimen_distinction": "WORLD_CHANGE != METHOD_CHANGE",
        "basis": {
            "g4_result": (
                "docs/campaigns/world_method_reconciliation_001/pressure_runs/"
                "WORLD_METHOD_RECONCILIATION_V0_PRESSURE_RESULT_001.md"
            ),
            "g4_witness": "world_method_reconciliation_v0_observation.json",
            "g4_witness_blob": observed_blob,
            "ablation_protocol": "docs/methods/Distinction_Ablation_Protocol_v0.md",
            "load_dimensions": (
                "docs/campaigns/sca001/atlas/"
                "ATLAS_SEVEN_CONSERVATION_SURFACES_SIX_LOAD_DIMENSIONS_V0.md"
            ),
        },
        "ablation": ablation,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Removing WORLD_CHANGE != METHOD_CHANGE from the exact matched G4 "
            "case frame collapses six distinct world/method signatures into three "
            "generic change signatures. This establishes semantic / representational "
            "load for that distinction within this exact frame only. Functional, "
            "authority, provenance, temporal, and coordination load remain "
            "UNRESOLVED. Current live-horizon dependence, method improvement, "
            "retention value, capitalization, policy mutation, work justification, "
            "authority, execution, and scientific standing are not established."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print(
        "[OK] signature_counts "
        f"{ablation['pre_ablation_distinct_signature_count']} -> "
        f"{ablation['post_ablation_distinct_signature_count']}"
    )
    print(
        f"[OK] semantic_load_change "
        f"{ablation['load_profile']['semantic']}"
    )
    print(
        "[OK] current_load_bearing_status "
        f"{ablation['current_load_bearing_status']}"
    )
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
