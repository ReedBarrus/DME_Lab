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

from src.control.current_horizon_distinction_dependence_v0 import (
    APPLICABLE,
    NOT_APPLICABLE,
    UNDERDETERMINED,
    UNRESOLVED,
    build_current_horizon_distinction_dependence,
)

OUT = ROOT / "current_horizon_distinction_dependence_v0_observation.json"
G4_WITNESS = ROOT / "world_method_reconciliation_v0_observation.json"
G5_WITNESS = ROOT / "method_distinction_load_ablation_v0_observation.json"
G5_RESULT = (
    ROOT
    / "docs/campaigns/method_distinction_load_001/pressure_runs/"
      "METHOD_DISTINCTION_LOAD_ABLATION_V0_PRESSURE_RESULT_001.md"
)

EXPECTED_G4_BLOB = "a49d948432c9560310133557ce6c8102ce4931ac"
EXPECTED_G5_WITNESS_BLOB = "a334412ac95fd66a228dba49fb888ffc225a6e7f"
EXPECTED_G5_RESULT_BLOB = "d738dd57ae7866bdf584509b553a6b061cd714d7"


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
            "remove existing current_horizon_distinction_dependence_v0_observation.json first"
        )

    g4 = json.loads(G4_WITNESS.read_text(encoding="utf-8"))
    g5 = json.loads(G5_WITNESS.read_text(encoding="utf-8"))
    g5_result = G5_RESULT.read_text(encoding="utf-8")

    g4_blob = git(
        "rev-parse", "HEAD:world_method_reconciliation_v0_observation.json"
    )
    g5_witness_blob = git(
        "rev-parse",
        "HEAD:method_distinction_load_ablation_v0_observation.json",
    )
    g5_result_blob = git(
        "rev-parse",
        "HEAD:docs/campaigns/method_distinction_load_001/pressure_runs/"
        "METHOD_DISTINCTION_LOAD_ABLATION_V0_PRESSURE_RESULT_001.md",
    )

    dependence = build_current_horizon_distinction_dependence(
        source_g4_observation_blob_sha=g4_blob,
        source_g5_result_blob_sha=g5_result_blob,
        g4_cases=g4["cases"],
        g5_collision_groups=g5["ablation"]["collision_groups"],
    )

    expected_pre = {
        "WORLD_ONLY": NOT_APPLICABLE,
        "METHOD_ONLY": APPLICABLE,
        "BOTH": APPLICABLE,
        "NEITHER": NOT_APPLICABLE,
        "WORLD_UNRESOLVED": NOT_APPLICABLE,
        "METHOD_UNRESOLVED": UNRESOLVED,
    }
    expected_post = {
        "CHANGED": UNDERDETERMINED,
        "UNCHANGED": NOT_APPLICABLE,
        "UNRESOLVED": UNDERDETERMINED,
    }

    assertions = {
        "g4_witness_blob_exact": g4_blob == EXPECTED_G4_BLOB,
        "g5_witness_blob_exact": (
            g5_witness_blob == EXPECTED_G5_WITNESS_BLOB
        ),
        "g5_result_blob_exact": g5_result_blob == EXPECTED_G5_RESULT_BLOB,
        "g5_standing_matched": (
            "DISPOSITION:\nMETHOD_DISTINCTION_LOAD_ABLATION_V0_MATCHED"
            in g5_result
        ),
        "g5_semantic_load_yes": (
            g5["ablation"]["load_profile"]["semantic"] == "YES"
        ),
        "g5_current_load_status_unresolved": (
            g5["ablation"]["current_load_bearing_status"] == "UNRESOLVED"
        ),
        "pre_ablation_applicability_exact": (
            dependence["pre_ablation_applicability"] == expected_pre
        ),
        "post_ablation_generic_applicability_exact": (
            dependence["post_ablation_generic_applicability"]
            == expected_post
        ),
        "changed_bucket_underdetermined": (
            dependence["post_ablation_generic_applicability"]["CHANGED"]
            == UNDERDETERMINED
        ),
        "unresolved_bucket_underdetermined": (
            dependence["post_ablation_generic_applicability"]["UNRESOLVED"]
            == UNDERDETERMINED
        ),
        "declared_horizon_load_bearing_yes": (
            dependence["declared_horizon_load_bearing_status"] == "YES"
        ),
        "global_current_load_bearing_unresolved": (
            dependence["global_current_load_bearing_status"]
            == "UNRESOLVED"
        ),
        "semantic_current_load_yes": (
            dependence["current_load_profile"]["semantic"] == "YES"
        ),
        "coordination_current_load_yes": (
            dependence["current_load_profile"]["coordination"] == "YES"
        ),
        "other_current_load_dimensions_unresolved": all(
            dependence["current_load_profile"][key] == "UNRESOLVED"
            for key in (
                "functional",
                "authority",
                "provenance",
                "temporal",
            )
        ),
        "no_retention_or_capitalization_effect": (
            dependence["retention_effect"] == "NONE"
            and dependence["method_capitalization_effect"] == "NONE"
        ),
        "no_downstream_consequence_effects": all(
            dependence[key] == "NONE"
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
        "object_type": "CURRENT_HORIZON_DISTINCTION_DEPENDENCE_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "CURRENT_HORIZON_DISTINCTION_DEPENDENCE_001",
        "gap_id": "G6_CURRENT_HORIZON_DISTINCTION_DEPENDENCE",
        "horizon_id": "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0",
        "specimen_distinction": "WORLD_CHANGE != METHOD_CHANGE",
        "basis": {
            "g4_witness": "world_method_reconciliation_v0_observation.json",
            "g4_witness_blob": g4_blob,
            "g5_witness": "method_distinction_load_ablation_v0_observation.json",
            "g5_witness_blob": g5_witness_blob,
            "g5_result": (
                "docs/campaigns/method_distinction_load_001/pressure_runs/"
                "METHOD_DISTINCTION_LOAD_ABLATION_V0_PRESSURE_RESULT_001.md"
            ),
            "g5_result_blob": g5_result_blob,
            "horizon_selection": (
                "docs/campaigns/current_horizon_distinction_dependence_001/"
                "HORIZON_SELECTION_G6_V0.md"
            ),
        },
        "dependence": dependence,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "WORLD_CHANGE != METHOD_CHANGE is load-bearing for the exact declared "
            "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0 because removing the "
            "distinction makes CHANGED and UNRESOLVED generic buckets unable to "
            "preserve deterministic method-specific applicability. Semantic and "
            "coordination current load are established only for this exact horizon. "
            "Global ecology dependence, functional/authority/provenance/temporal "
            "current load, retention value, capitalization, causal benefit, policy "
            "mutation, authority, execution, and scientific standing remain "
            "UNRESOLVED or NONE as declared."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print(
        "[OK] generic_applicability "
        + " ".join(
            f"{key}={value}"
            for key, value in dependence[
                "post_ablation_generic_applicability"
            ].items()
        )
    )
    print(
        "[OK] declared_horizon_load_bearing_status "
        + dependence["declared_horizon_load_bearing_status"]
    )
    print(
        "[OK] global_current_load_bearing_status "
        + dependence["global_current_load_bearing_status"]
    )
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
