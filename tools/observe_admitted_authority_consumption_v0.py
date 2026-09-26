#!/usr/bin/env python3
"""Observe exact admitted-successor -> one-shot authority consumption."""

from __future__ import annotations

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
from src.coordination.admitted_authority_consumption_v0 import (
    consume_admitted_authority_once,
)
from src.coordination.verified_authority_admission_v0 import (
    successor_authority_coordinates,
    try_verified_authority_atomic_admission,
)
from src.runtime.local_authority_consumption_v0 import (
    AuthorityInvocationError,
    LocalAuthorityStateStore,
)


OUT = ROOT / "admitted_authority_consumption_observation.json"


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


def successor(label: str) -> dict:
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
            "claim_ceiling": "disposable fixture",
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
        "model": "fixture/not-a-model",
        "endpoint_identity": "disposable-fixture-endpoint",
        "executor_sha256": "3" * 64,
        "policy_sha256": "4" * 64,
        "use_limit": 1,
        "remaining_uses": 1,
        "status": "ACTIVE",
        "issued_at": "2026-09-25T00:00:00Z",
        "expires_at": None,
    }


def compose(root: Path, store, env: dict, candidate: dict, attempt_id: str) -> dict:
    decision = try_verified_authority_atomic_admission(
        store_dir=root / "atomic",
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
    if decision["admitted"] is not True:
        raise RuntimeError(f"composition fixture failed: {decision}")
    return decision["receipt"]


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "admitted_authority_consumption_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        candidate = successor("A")
        env = envelope_for(candidate, "CAP.ADMIT.CONSUME.A")
        store = LocalAuthorityStateStore(root / "authority-success")
        store.issue(env)
        composition = compose(root / "success", store, env, candidate, "ATTEMPT-A")
        success_calls: list[str] = []
        success_ticks = iter([
            "2026-09-25T00:00:01Z",
            "2026-09-25T00:00:02Z",
        ])
        success = consume_admitted_authority_once(
            composition_receipt=composition,
            successor_candidate=candidate,
            authority_envelope=env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store,
            invoke=lambda: success_calls.append("invoked") or {
                "fixture_result": "SUCCESS"
            },
            clock=lambda: next(success_ticks),
        )
        success_state = store.read(env["capability_id"])
        replay = consume_admitted_authority_once(
            composition_receipt=composition,
            successor_candidate=candidate,
            authority_envelope=env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store,
            invoke=lambda: success_calls.append("replayed"),
            clock=lambda: "2026-09-25T00:00:03Z",
        )

        mismatch_a = successor("B")
        mismatch_b = successor("C")
        mismatch_env = envelope_for(mismatch_a, "CAP.ADMIT.CONSUME.B")
        mismatch_store = LocalAuthorityStateStore(root / "authority-mismatch")
        mismatch_store.issue(mismatch_env)
        mismatch_comp = compose(
            root / "mismatch",
            mismatch_store,
            mismatch_env,
            mismatch_a,
            "ATTEMPT-B",
        )
        mismatch_calls: list[str] = []
        mismatch = consume_admitted_authority_once(
            composition_receipt=mismatch_comp,
            successor_candidate=mismatch_b,
            authority_envelope=mismatch_env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=mismatch_store,
            invoke=lambda: mismatch_calls.append("wrong"),
            clock=lambda: "2026-09-25T00:00:04Z",
        )
        mismatch_state = mismatch_store.read(mismatch_env["capability_id"])

        failure_candidate = successor("D")
        failure_env = envelope_for(failure_candidate, "CAP.ADMIT.CONSUME.D")
        failure_store = LocalAuthorityStateStore(root / "authority-failure")
        failure_store.issue(failure_env)
        failure_comp = compose(
            root / "failure",
            failure_store,
            failure_env,
            failure_candidate,
            "ATTEMPT-D",
        )
        failure_calls: list[str] = []
        failure_ticks = iter([
            "2026-09-25T00:00:05Z",
            "2026-09-25T00:00:06Z",
        ])

        def fail():
            failure_calls.append("failed-once")
            raise RuntimeError("disposable fixture failure")

        failure_error = None
        try:
            consume_admitted_authority_once(
                composition_receipt=failure_comp,
                successor_candidate=failure_candidate,
                authority_envelope=failure_env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=failure_store,
                invoke=fail,
                clock=lambda: next(failure_ticks),
            )
        except AuthorityInvocationError as exc:
            failure_error = {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        failure_state = failure_store.read(failure_env["capability_id"])
        failure_replay = consume_admitted_authority_once(
            composition_receipt=failure_comp,
            successor_candidate=failure_candidate,
            authority_envelope=failure_env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=failure_store,
            invoke=lambda: failure_calls.append("illegal-retry"),
            clock=lambda: "2026-09-25T00:00:07Z",
        )

    assertions = {
        "exact_admitted_successor_consumed_once": (
            success["consumed"] is True
            and success["invocation_performed"] is True
            and success["receipt"]["invocation_count"] == 1
        ),
        "success_callback_exactly_once": success_calls == ["invoked"],
        "authority_consumed_after_success": (
            success_state["envelope"]["status"] == "CONSUMED"
            and success_state["envelope"]["remaining_uses"] == 0
        ),
        "replay_denied": (
            replay["consumed"] is False
            and replay["blockers"] == ["authority_verification_failed"]
        ),
        "wrong_successor_blocked_before_consumption": (
            mismatch["consumed"] is False
            and mismatch["blockers"] == ["composition_successor_id_mismatch"]
            and mismatch_calls == []
            and mismatch_state["envelope"]["status"] == "ACTIVE"
            and mismatch_state["envelope"]["remaining_uses"] == 1
        ),
        "post_reservation_failure_observed": failure_error is not None,
        "post_reservation_failure_enters_recovery_required": (
            failure_state["envelope"]["status"] == "RECOVERY_REQUIRED"
            and failure_state["envelope"]["remaining_uses"] == 0
        ),
        "failure_replay_denied": (
            failure_replay["consumed"] is False
            and failure_replay["blockers"] == ["authority_verification_failed"]
            and failure_calls == ["failed-once"]
        ),
        "no_authority_grant": success["authority_effect"] == "NONE",
        "no_scientific_standing": (
            success["scientific_standing_effect"] == "NONE"
        ),
    }

    witness = {
        "object_type": "ADMITTED_AUTHORITY_CONSUMPTION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SAME_PROCESS_INVOCATION_CALLBACK_FIXTURE",
        "success_case": {
            "decision": success,
            "authority_status_after": success_state["envelope"]["status"],
            "remaining_uses_after": success_state["envelope"]["remaining_uses"],
            "callback_calls": success_calls,
        },
        "replay_case": replay,
        "wrong_successor_case": {
            "decision": mismatch,
            "authority_status_after": mismatch_state["envelope"]["status"],
            "remaining_uses_after": mismatch_state["envelope"]["remaining_uses"],
            "callback_calls": mismatch_calls,
        },
        "post_reservation_failure_case": {
            "error": failure_error,
            "authority_status_after": failure_state["envelope"]["status"],
            "remaining_uses_after": failure_state["envelope"]["remaining_uses"],
            "callback_calls": failure_calls,
            "replay": failure_replay,
        },
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Same-process disposable composition of one exact admitted successor "
            "with the same current one-use authority through one caller-supplied "
            "invocation callback. Success consumes authority exactly once; replay "
            "is denied; identity mismatch blocks before consumption; post-reservation "
            "failure leaves RECOVERY_REQUIRED and replay denied. This does not "
            "establish model execution, immutable result witnessing, settlement, "
            "cross-process atomicity, or self-moving-workcycle standing."
        ),
        "authority_effect": "NONE",
        "consumption_effect": "CONSUMED_ONE_USE_IN_SUCCESS_CASE",
        "production_execution_effect": "NONE",
        "model_invocation_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(witness, indent=2, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    print(f"[OK] all_assertions_pass {witness['all_assertions_pass']}")
    print(f"[OK] success_consumed {success['consumed']}")
    print(f"[OK] success_callback_calls {len(success_calls)}")
    print(f"[OK] replay_consumed {replay['consumed']}")
    print(f"[OK] failure_status {failure_state['envelope']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
