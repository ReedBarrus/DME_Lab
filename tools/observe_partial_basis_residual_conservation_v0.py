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

from src.control.partial_basis_residual_conservation_v0 import (
    build_partial_basis_residual_conservation,
)

OUT = ROOT / "partial_basis_residual_conservation_v0_observation.json"
G10_RESULT = (
    ROOT
    / "docs/campaigns/partial_basis_retention_profile_001/pressure_runs/"
      "PARTIAL_BASIS_RETENTION_PROFILE_V0_PRESSURE_RESULT_001.md"
)
G10_WITNESS = ROOT / "partial_basis_retention_profile_v0_observation.json"

EXPECTED_G10_RESULT_BLOB = "e0c27dd06b68ac7e3dc08d20093e60eee35509eb"
EXPECTED_G10_WITNESS_BLOB = "4f4c7efef184c1f60ab362420d7ef09a1c43dab1"


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
            "remove existing partial_basis_residual_conservation_v0_observation.json first"
        )

    g10_result_text = G10_RESULT.read_text(encoding="utf-8")
    g10_witness = json.loads(G10_WITNESS.read_text(encoding="utf-8"))

    g10_result_blob = git(
        "rev-parse",
        "HEAD:docs/campaigns/partial_basis_retention_profile_001/pressure_runs/"
        "PARTIAL_BASIS_RETENTION_PROFILE_V0_PRESSURE_RESULT_001.md",
    )
    g10_witness_blob = git(
        "rev-parse",
        "HEAD:partial_basis_retention_profile_v0_observation.json",
    )

    b1 = g10_witness["b1"]
    extension = g10_witness["extension"]

    residual = build_partial_basis_residual_conservation(
        source_g10_result_blob_sha=g10_result_blob,
        source_g10_witness_blob_sha=g10_witness_blob,
        basis_id=b1["basis_id"],
        source_profile_id=b1["profile_id"],
        source_extension_id=extension["extension_id"],
        interior_unresolved_members=b1["retention_profile"][
            "unresolved_members"
        ],
        nonresidual_members=sorted(
            b1["retention_profile"]["required_members"]
            + b1["retention_profile"]["not_required_members"]
        ),
        exterior_posture=b1["exterior_posture"],
    )

    assertions = {
        "g10_result_blob_exact": g10_result_blob == EXPECTED_G10_RESULT_BLOB,
        "g10_witness_blob_exact": (
            g10_witness_blob == EXPECTED_G10_WITNESS_BLOB
        ),
        "g10_standing_matched": (
            "DISPOSITION:\nPARTIAL_BASIS_RETENTION_PROFILE_V0_MATCHED"
            in g10_result_text
        ),
        "g10_witness_passed": g10_witness["all_assertions_pass"] is True,
        "interior_residual_exact": (
            residual["interior_unresolved_members"] == ["H_C"]
        ),
        "nonresidual_members_exact": (
            residual["nonresidual_members"] == ["H_A", "H_B"]
        ),
        "exterior_residual_unresolved": (
            residual["exterior_posture"] == "UNRESOLVED"
        ),
        "residual_conserved": residual["residual_conserved"] == "YES",
        "residual_gap_status_not_established": (
            residual["residual_gap_status"] == "NOT_ESTABLISHED"
        ),
        "residual_work_eligibility_not_established": (
            residual["residual_work_eligibility"] == "NOT_ESTABLISHED"
        ),
        "architecture_requirement_not_established": (
            residual["architecture_requirement"] == "NOT_ESTABLISHED"
        ),
        "no_gap_or_work_effects": all(
            residual[key] == "NONE"
            for key in (
                "gap_discovery_effect",
                "gap_selection_effect",
                "work_justification_effect",
                "work_materialization_effect",
            )
        ),
        "no_downstream_consequence_effects": all(
            residual[key] == "NONE"
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
        ),
    }

    obs = {
        "object_type": "PARTIAL_BASIS_RESIDUAL_CONSERVATION_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD"),
        "campaign_id": "PARTIAL_BASIS_RESIDUAL_CONSERVATION_001",
        "gap_id": "G11_PARTIAL_BASIS_RESIDUAL_CONSERVATION",
        "distinction_id": "WORLD_CHANGE_NE_METHOD_CHANGE",
        "basis": {
            "g10_result": (
                "docs/campaigns/partial_basis_retention_profile_001/pressure_runs/"
                "PARTIAL_BASIS_RETENTION_PROFILE_V0_PRESSURE_RESULT_001.md"
            ),
            "g10_result_blob": g10_result_blob,
            "g10_witness": "partial_basis_retention_profile_v0_observation.json",
            "g10_witness_blob": g10_witness_blob,
        },
        "residual": residual,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "The exact unresolved residue exposed by the qualified G10 partial "
            "basis is conserved as a typed carrier containing interior unresolved "
            "{H_C}, unresolved exterior posture, and exact source identity. "
            "H_A and H_B remain classified nonresidual members. Residual gap "
            "standing, work eligibility, architecture requirement, global "
            "coverage, planning, authority, execution, and scientific standing "
            "remain unestablished."
        ),
        "stopped": "YES",
    }

    data = (json.dumps(obs, indent=2) + "\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print("[OK] interior_residual {H_C}")
    print("[OK] exterior_residual UNRESOLVED")
    print("[OK] residual_gap_status NOT_ESTABLISHED")
    print("[OK] residual_work_eligibility NOT_ESTABLISHED")
    print("[OK] architecture_requirement NOT_ESTABLISHED")
    return 0 if obs["all_assertions_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
