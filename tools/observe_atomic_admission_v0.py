#!/usr/bin/env python3
"""Observe atomic admission V0 in disposable local fixtures.

Exercises single admission, same-wake blocking, authority fail-closed behavior,
and a two-caller race. No model invocation or production control mutation.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination import workcycle_v0 as wc
from src.coordination.atomic_admission_v0 import try_atomic_admission


OUT = ROOT / "atomic_admission_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def control_on() -> dict:
    return {
        "workflow_enabled": True,
        "campaign_enabled": True,
        "seat_work_enabled": True,
        "wake_requested": True,
        "auto_continuation_limit": 1,
    }


def attempt(root: Path, attempt_id: str, *, authority_satisfied: bool = True) -> dict:
    return try_atomic_admission(
        store_dir=root,
        campaign_id="WORKCYCLE_STABILIZATION_001",
        work_item_id="W-NEXT",
        work_attempt_id=attempt_id,
        seat_id="LABBOIB",
        occupant_id=f"occupant-{attempt_id}",
        wake_generation=1,
        authority_coordinate="AUTH_COORD_OBS_001",
        authority_satisfied=authority_satisfied,
        dependency_satisfied=True,
        frame_current=True,
        no_hold=True,
        control=control_on(),
        initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "atomic_admission_observation.json already exists; move/remove it before a fresh observation"
        )

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = attempt(root, "SERIAL-A")
        second = attempt(root, "SERIAL-B")

    with TemporaryDirectory() as tmp:
        no_auth = attempt(Path(tmp), "NO-AUTH", authority_satisfied=False)

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        with ThreadPoolExecutor(max_workers=2) as pool:
            race = list(pool.map(lambda x: attempt(root, x), ["RACE-A", "RACE-B"]))

    race_admitted = [item for item in race if item["admitted"]]
    race_blocked = [item for item in race if not item["admitted"]]

    assertions = {
        "first_serial_admitted": first["admitted"] is True,
        "second_serial_blocked": second["admitted"] is False,
        "second_serial_active_admission_blocker": "active_admission" in second["blockers"],
        "second_serial_budget_blocker": "budget_reservable" in second["blockers"],
        "unsatisfied_authority_blocked": no_auth["admitted"] is False,
        "unsatisfied_authority_named": "authority_satisfied" in no_auth["blockers"],
        "race_exactly_one_admitted": len(race_admitted) == 1,
        "race_exactly_one_blocked": len(race_blocked) == 1,
        "no_model_invocation": all(
            item.get("model_invocation_effect") == "NONE"
            for item in [first, second, no_auth, *race]
        ),
        "no_execution_performed": all(
            item.get("execution_performed") is False
            for item in [first, second, no_auth, *race]
        ),
        "no_new_authority": all(
            item.get("authority_effect") == "NONE"
            for item in [first, second, no_auth, *race]
        ),
    }

    witness = {
        "object_type": "ATOMIC_ADMISSION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_LOCAL_CONCURRENCY_FIXTURE",
        "serial_first": first,
        "serial_second": second,
        "unsatisfied_authority_case": no_auth,
        "race_results": race,
        "race_admitted_count": len(race_admitted),
        "race_blocked_count": len(race_blocked),
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Repo-local concurrency-safe admission candidate only. "
            "This fixture does not establish distributed/process-independent locking across arbitrary filesystems, "
            "does not grant authority, does not invoke a model, and does not execute admitted work."
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
    print(f"[OK] race_admitted_count {witness['race_admitted_count']}")
    print(f"[OK] race_blocked_count {witness['race_blocked_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
