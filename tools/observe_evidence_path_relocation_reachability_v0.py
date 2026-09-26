#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence" / "for_planner" / "evidence_path_relocation_reachability_v0_observation.json"

PRE_MOVE_SOURCE = "cf2d62f175bfae784d3755dc83ab7ea1d4e33b2f"
RELOCATION_COMMIT = "2ea35acb8d4fb61f55f4725a5af72510746460b5"
PREFIX = "docs/evidence/for_planner/"

CASES = {
    "declaration_work_eligibility_selection_load_v0_observation.json":
        "54ab5157ec936474c6189f2d956127fc5cb1e0c0",
    "distinction_retention_currentness_v0_observation.json":
        "949ff2b9333146ca16e68981123f338f6e4dfd15",
    "distinction_retention_mode_v0_observation.json":
        "1ff52354096371710ccdcdd77dfb9a6b2c1ada3b",
    "partial_basis_residual_conservation_v0_observation.json":
        "1736d63c13c27d37641f3a6f78825c9288428a50",
    "partial_basis_retention_profile_v0_observation.json":
        "4f4c7efef184c1f60ab362420d7ef09a1c43dab1",
    "retention_scope_aggregation_v0_observation.json":
        "212d7a9d4fb7bc982cb83b418ee6d5982008c574",
}


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def blob_at(ref: str, path: str) -> str | None:
    proc = git("rev-parse", f"{ref}:{path}", check=False)
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    rows = []
    for old_path, expected_blob in CASES.items():
        new_path = PREFIX + old_path
        pre_old = blob_at(PRE_MOVE_SOURCE, old_path)
        post_old = blob_at(RELOCATION_COMMIT, old_path)
        post_new = blob_at(RELOCATION_COMMIT, new_path)

        row = {
            "old_path": old_path,
            "new_path": new_path,
            "expected_blob": expected_blob,
            "pre_move_old_path_blob": pre_old,
            "post_move_old_path_blob": post_old,
            "post_move_new_path_blob": post_new,
            "control_old_path_resolves_expected_blob": pre_old == expected_blob,
            "relocation_old_path_absent": post_old is None,
            "relocation_new_path_resolves_expected_blob": post_new == expected_blob,
            "content_identity_preserved": (
                pre_old == expected_blob and post_new == expected_blob
            ),
            "original_path_reachability_preserved": post_old is not None,
        }
        rows.append(row)

    all_control = all(r["control_old_path_resolves_expected_blob"] for r in rows)
    all_old_absent = all(r["relocation_old_path_absent"] for r in rows)
    all_new_exact = all(r["relocation_new_path_resolves_expected_blob"] for r in rows)
    all_content_preserved = all(r["content_identity_preserved"] for r in rows)

    observation = {
        "object_type": "EVIDENCE_PATH_RELOCATION_REACHABILITY_V0_OBSERVATION",
        "campaign_id": "EVIDENCE_PATH_RELOCATION_REACHABILITY_001",
        "pressure_id": "EVIDENCE_PATH_RELOCATION_REACHABILITY_V0_PRESSURE_001",
        "pre_move_source": PRE_MOVE_SOURCE,
        "relocation_commit": RELOCATION_COMMIT,
        "cases": rows,
        "assembly": {
            "all_control_old_paths_resolve_expected_blobs": all_control,
            "all_relocation_old_paths_absent": all_old_absent,
            "all_relocation_new_paths_resolve_expected_blobs": all_new_exact,
            "all_content_identities_preserved": all_content_preserved,
            "original_witness_path_reachability_preserved": not all_old_absent,
            "relocated_witness_path_reachability": all_new_exact,
            "reference_route_break_present": (
                all_control and all_old_absent and all_new_exact and all_content_preserved
            ),
        },
        "candidate_relation": {
            "content_identity_preservation_ne_witness_path_reachability": (
                "YES"
                if all_control and all_old_absent and all_new_exact and all_content_preserved
                else "UNRESOLVED"
            )
        },
        "effects": {
            "evidence_loss_effect": "NONE",
            "claim_falsification_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "automatic_reference_rewrite_effect": "NONE",
            "generic_relocation_resolver_effect": "NONE",
            "archive_policy_effect": "NONE",
            "deletion_permission_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
        },
        "claim_ceiling": (
            "One bounded repository-path relocation pressure over six invariant-ledger "
            "witness references. Exact Git blob identity may remain preserved while "
            "the prior repository-relative path no longer resolves and the relocated "
            "path does resolve. No evidence-loss, claim-falsification, archive-policy, "
            "automatic-rewrite, generic relocation, authority, execution, or scientific-standing "
            "claim is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] cases {len(rows)}")
    print(f"[OK] control {all_control}")
    print(f"[OK] old paths absent {all_old_absent}")
    print(f"[OK] new paths exact {all_new_exact}")
    print(f"[OK] content preserved {all_content_preserved}")
    print(f"[OK] route break {observation['assembly']['reference_route_break_present']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
