#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.control_kernel_cell_001_v0 import evaluate_supplied_single_gap

SPEC = ROOT / "docs/campaigns/control_kernel_001/state/CONTROL_KERNEL_CELL_001_SPECIMEN_V0.json"
OUT = ROOT / "control_kernel_cell_001_observation.json"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def main() -> int:
    if OUT.exists():
        raise SystemExit("remove existing control_kernel_cell_001_observation.json first")

    specimen = json.loads(SPEC.read_text(encoding="utf-8"))
    tx = specimen["bounded_transformation"]
    path = tx["target_path"]
    pre = git("show", f"{tx['pre_change_ref']}:{path}")
    post = git("show", f"{tx['post_change_ref']}:{path}")
    changed_paths = [
        line.strip()
        for line in git(
            "diff", "--name-only", tx["pre_change_ref"], tx["post_change_ref"]
        ).splitlines()
        if line.strip()
    ]

    precondition_present = tx["precondition_fragment"] in pre
    postcondition_present = all(
        fragment in post
        for fragment in tx["required_postcondition_fragments"]
    )
    bounded_delta = changed_paths == [path]

    repository_observation = {
        "precondition_present_before": precondition_present,
        "postcondition_present_after": postcondition_present,
        "bounded_delta_observed": bounded_delta,
        "pre_change_ref": tx["pre_change_ref"],
        "post_change_ref": tx["post_change_ref"],
        "target_path": path,
        "changed_paths": changed_paths,
    }

    result = evaluate_supplied_single_gap(
        specimen=specimen,
        repository_observation=repository_observation,
        remaining_gap_ids=[] if postcondition_present and bounded_delta else [
            specimen["supplied_live_gaps"][0]["gap_id"]
        ],
    )
    repeat = evaluate_supplied_single_gap(
        specimen=specimen,
        repository_observation=repository_observation,
        remaining_gap_ids=[] if postcondition_present and bounded_delta else [
            specimen["supplied_live_gaps"][0]["gap_id"]
        ],
    )

    assertions = {
        "externally_supplied_horizon": specimen["selection_source"] == "EXTERNALLY_SUPPLIED",
        "machine_selection_unclaimed": specimen["machine_selection_claimed"] is False,
        "exactly_one_supplied_gap": len(specimen["supplied_live_gaps"]) == 1,
        "no_competing_gaps": specimen["competing_gaps"] == [],
        "precondition_observed": precondition_present,
        "postcondition_observed": postcondition_present,
        "bounded_repository_delta": bounded_delta,
        "fixed_inputs_deterministic": result == repeat,
        "horizon_satisfied": result["horizon_posture"] == "HORIZON_SATISFIED",
        "gap_set_empty": result["remaining_gap_ids"] == [],
        "no_justified_work": result["terminal_posture"] == "NO_JUSTIFIED_WORK",
        "stop_required": result["stop_required"] is True,
        "no_machine_selection_or_consequence_capacity_created": (
            result["gap_selection_effect"] == "NONE"
            and result["work_materialization_effect"] == "NONE"
            and result["work_admission_effect"] == "NONE"
            and result["authority_effect"] == "NONE"
            and result["execution_effect"] == "NONE"
            and result["scientific_standing_effect"] == "NONE"
        ),
    }

    observation = {
        "object_type": "CONTROL_KERNEL_CELL_001_OBSERVATION_V0",
        "repo_head": git("rev-parse", "HEAD").strip(),
        "campaign_id": specimen["campaign_id"],
        "cell_id": specimen["cell_id"],
        "supplied_horizon": specimen["operative_horizon"],
        "supplied_gap": specimen["supplied_live_gaps"][0],
        "repository_observation": repository_observation,
        "result": result,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, one externally supplied operative horizon "
            "with exactly one externally supplied live gap and no competing gaps can "
            "be reconciled against one bounded observed repository repair. Once that "
            "repair removes the supplied gap, the cell returns HORIZON_SATISFIED, "
            "an empty supplied gap set, NO_JUSTIFIED_WORK, and STOP. The cell does "
            "not establish generalized relational-horizon representation, machine "
            "gap selection, multi-gap ranking, planning automation, authority, "
            "execution, or scientific standing."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(f"[OK] horizon_satisfied {assertions['horizon_satisfied']}")
    print(f"[OK] no_justified_work {assertions['no_justified_work']}")
    print(f"[OK] stop_required {assertions['stop_required']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
