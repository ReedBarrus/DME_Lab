#!/usr/bin/env python3
"""Observe the bounded one-successor continuation law in disposable fixtures.

No model is invoked. No repository or production control state is mutated.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination import workcycle_v0 as wc


OUT = ROOT / "one_successor_continuation_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def eligible(control: dict, budget: dict) -> dict:
    return wc.evaluate_one_successor_continuation(
        control=control,
        dependency_satisfied=True,
        frame_current=True,
        seat_available=True,
        no_hold=True,
        authority_satisfied=True,
        budget=budget,
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "one_successor_continuation_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    fresh_budget = wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001")

    off_control = {
        "workflow_enabled": False,
        "campaign_enabled": True,
        "seat_work_enabled": True,
        "wake_requested": True,
        "auto_continuation_limit": 1,
    }
    off_case = eligible(off_control, fresh_budget)

    on_control = {
        "workflow_enabled": True,
        "campaign_enabled": True,
        "seat_work_enabled": True,
        "wake_requested": True,
        "auto_continuation_limit": 1,
    }
    one_unit_case = eligible(on_control, fresh_budget)

    reserved_budget = wc.reserve_one_item(fresh_budget)
    second_same_wake_case = eligible(on_control, reserved_budget)

    assertions = {
        "off_case_blocked": off_case["admit_one_successor"] is False,
        "one_unit_case_admitted": one_unit_case["admit_one_successor"] is True,
        "one_unit_max_successors_one": one_unit_case["max_successors_admitted"] == 1,
        "second_same_wake_blocked": second_same_wake_case["admit_one_successor"] is False,
        "second_same_wake_budget_blocker": "budget_reservable" in second_same_wake_case["blockers"],
        "no_execution_performed": all(
            item.get("execution_performed") is False
            for item in (off_case, one_unit_case, second_same_wake_case)
        ),
        "no_authority_effect": all(
            item.get("authority_effect") == "NONE"
            for item in (off_case, one_unit_case, second_same_wake_case)
        ),
    }

    witness = {
        "object_type": "ONE_SUCCESSOR_CONTINUATION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SINGLE_THREADED_FIXTURE",
        "off_case": off_case,
        "one_unit_case": one_unit_case,
        "reserved_budget": reserved_budget,
        "second_same_wake_case": second_same_wake_case,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "max_successors_observed": one_unit_case.get("max_successors_admitted"),
        "claim_ceiling": (
            "Single-threaded one-successor decision law only. "
            "This does not atomically acquire a seat lease, reserve production budget, "
            "bind a work-attempt identity, satisfy production authority, invoke a model, "
            "or establish concurrency-safe production admission."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(witness, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    print(f"[OK] all_assertions_pass {witness['all_assertions_pass']}")
    print(f"[OK] max_successors_observed {witness['max_successors_observed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
