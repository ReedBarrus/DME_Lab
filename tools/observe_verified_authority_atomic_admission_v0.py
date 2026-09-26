#!/usr/bin/env python3
"""Observe verified-current-authority + successor + atomic-admission composition."""

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
from src.coordination.verified_authority_admission_v0 import (
    successor_authority_coordinates,
    try_verified_authority_atomic_admission,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    consume_authority_once,
)


OUT = ROOT / "verified_authority_atomic_admission_observation.json"


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


def successor(label: str = "A") -> dict:
    return wc.seal_object(
        {
            "object_type": "SUCCESSOR_CANDIDATE_V1",
            "campaign_id": "WORKCYCLE_STABILIZATION_001",
            "parent_work_item_id": "W-PARENT",
            "basis_id": "B-H-OPERATE-001",
            "operative_frame_ref": "FRAME-H-OPERATE-001",
            "successor_posture": "RESOLVE_LOAD_BEARING_GAP",
            "reconciliation_identity": label.lower() * 64,
            "next_pressure_basis": f"pressure-{label}",
            "successor_id": f"successor:sha256:{label.lower() * 64}",
            "candidate_posture": "PROPOSED_NOT_ADMITTED",
            "selection_basis": "active basis has one admissible load-bearing pressure",
            "claim_ceiling": "fixture",
            "work_admission_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def envelope_for(candidate: dict, capability: str) -> dict:
    coordinates = successor_authority_coordinates(candidate)
    return {
        "object_type": "LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0",
        "capability_id": capability,
        "approval_id": capability.replace("CAP", "APP", 1),
        "principal_id": "CODEX_PRINCIPAL_001",
        "request_sha256": coordinates["request_sha256"],
        "input_sha256": coordinates["input_sha256"],
        "model": "test/model",
        "endpoint_identity": "local-test-endpoint",
        "executor_sha256": "3" * 64,
        "policy_sha256": "4" * 64,
        "use_limit": 1,
        "remaining_uses": 1,
        "status": "ACTIVE",
        "issued_at": "2026-09-25T00:00:00Z",
        "expires_at": None,
    }


def attempt(root: Path, store, env, candidate, attempt_id: str) -> dict:
    return try_verified_authority_atomic_admission(
        store_dir=root,
        authority_store=store,
        authority_envelope=env,
        attempting_principal_id="CODEX_PRINCIPAL_001",
        successor_candidate=candidate,
        work_attempt_id=attempt_id,
        seat_id="LABBOIB",
        occupant_id=f"occupant-{attempt_id}",
        wake_generation=1,
        dependency_satisfied=True,
        frame_current=True,
        no_hold=True,
        control=control_on(),
        initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "verified_authority_atomic_admission_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        exact_candidate = successor("A")
        exact_env = envelope_for(exact_candidate, "CAP.COMP.EXACT")
        exact_store = LocalAuthorityStateStore(root / "authority-exact")
        exact_before = exact_store.issue(exact_env)
        exact = attempt(
            root / "atomic-exact",
            exact_store,
            exact_env,
            exact_candidate,
            "ATTEMPT-EXACT",
        )
        exact_after = exact_store.read(exact_env["capability_id"])

        wrong_candidate = successor("B")
        mismatch = attempt(
            root / "atomic-mismatch",
            exact_store,
            exact_env,
            wrong_candidate,
            "ATTEMPT-MISMATCH",
        )

        tampered_candidate = dict(exact_candidate)
        tampered_candidate["basis_id"] = "B-TAMPERED"
        tampered = attempt(
            root / "atomic-tampered",
            exact_store,
            exact_env,
            tampered_candidate,
            "ATTEMPT-TAMPERED",
        )

        consumed_candidate = successor("C")
        consumed_env = envelope_for(consumed_candidate, "CAP.COMP.CONSUMED")
        consumed_store = LocalAuthorityStateStore(root / "authority-consumed")
        consumed_store.issue(consumed_env)
        ticks = iter([
            "2026-09-25T00:00:01Z",
            "2026-09-25T00:00:02Z",
        ])
        consume_authority_once(
            consumed_env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            store=consumed_store,
            invoke=lambda: {"ok": True},
            clock=lambda: next(ticks),
        )
        consumed = attempt(
            root / "atomic-consumed",
            consumed_store,
            consumed_env,
            consumed_candidate,
            "ATTEMPT-CONSUMED",
        )

        race_candidate = successor("D")
        race_env = envelope_for(race_candidate, "CAP.COMP.RACE")
        race_store = LocalAuthorityStateStore(root / "authority-race")
        race_store.issue(race_env)
        with ThreadPoolExecutor(max_workers=2) as pool:
            race_results = list(
                pool.map(
                    lambda attempt_id: attempt(
                        root / "atomic-race",
                        race_store,
                        race_env,
                        race_candidate,
                        attempt_id,
                    ),
                    ["RACE-A", "RACE-B"],
                )
            )
        race_after = race_store.read(race_env["capability_id"])

    admitted_race = [item for item in race_results if item["admitted"]]
    blocked_race = [item for item in race_results if not item["admitted"]]

    assertions = {
        "exact_composition_admitted": exact["admitted"] is True,
        "exact_binding_posture_verified": (
            exact["receipt"]["authority_verification"]
            == "VERIFIED_CURRENT_ACTIVE_ONE_USE"
        ),
        "exact_successor_bound": (
            exact["receipt"]["successor_id"] == exact_candidate["successor_id"]
        ),
        "exact_authority_not_consumed": exact_before == exact_after,
        "wrong_successor_blocked": (
            mismatch["admitted"] is False
            and "authority_request_successor_mismatch" in mismatch["blockers"]
        ),
        "tampered_successor_blocked": (
            tampered["admitted"] is False
            and tampered["blockers"] == ["successor_candidate_invalid"]
        ),
        "consumed_authority_blocked": (
            consumed["admitted"] is False
            and consumed["blockers"] == ["authority_verification_failed"]
        ),
        "two_callers_exactly_one_admitted": (
            len(admitted_race) == 1 and len(blocked_race) == 1
        ),
        "race_authority_unconsumed": (
            race_after["envelope"]["status"] == "ACTIVE"
            and race_after["envelope"]["remaining_uses"] == 1
        ),
        "no_execution": (
            exact["execution_effect"] == "NONE"
            and exact["receipt"]["execution_performed"] is False
        ),
        "no_model_invocation": exact["model_invocation_effect"] == "NONE",
        "no_authority_grant_or_consumption": (
            exact["authority_effect"] == "NONE"
            and exact["consumption_effect"] == "NONE"
        ),
    }

    witness = {
        "object_type": "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SAME_PROCESS_COMPOSITION_FIXTURE",
        "exact_case": exact,
        "wrong_successor_case": mismatch,
        "tampered_successor_case": tampered,
        "consumed_authority_case": consumed,
        "race_case": {
            "results": race_results,
            "admitted_count": len(admitted_race),
            "blocked_count": len(blocked_race),
        },
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Same-process composition of current verified one-use local authority "
            "issued for the exact sealed successor candidate into one atomic local "
            "admission transition. Authority remains unconsumed and no model invocation "
            "or work execution occurs. Cross-process authority/admission atomicity, "
            "crash safety, durability, and execution standing remain unestablished."
        ),
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(witness, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    print(f"[OK] all_assertions_pass {witness['all_assertions_pass']}")
    print(f"[OK] exact_admitted {exact['admitted']}")
    print(f"[OK] race_admitted_count {len(admitted_race)}")
    print(f"[OK] race_blocked_count {len(blocked_race)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
