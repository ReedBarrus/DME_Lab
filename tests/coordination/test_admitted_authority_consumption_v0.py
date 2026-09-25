from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

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


def compose(
    root: Path,
    store: LocalAuthorityStateStore,
    env: dict,
    candidate: dict,
    attempt_id: str = "ATTEMPT-001",
) -> dict:
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
        raise AssertionError(f"fixture composition failed: {decision}")
    return decision["receipt"]


class AdmittedAuthorityConsumptionV0Tests(unittest.TestCase):
    def test_exact_admission_consumes_once_and_invokes_once(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor("A")
            env = envelope_for(candidate, "CAP.CONSUME.A")
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            composition = compose(root, store, env, candidate)

            calls: list[str] = []
            ticks = iter([
                "2026-09-25T00:00:01Z",
                "2026-09-25T00:00:02Z",
            ])
            result = consume_admitted_authority_once(
                composition_receipt=composition,
                successor_candidate=candidate,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("invoked") or {"ok": True},
                clock=lambda: next(ticks),
            )
            after = store.read(env["capability_id"])

        self.assertTrue(result["consumed"])
        self.assertTrue(result["invocation_performed"])
        self.assertEqual(calls, ["invoked"])
        self.assertEqual(result["invocation_result"], {"ok": True})
        self.assertEqual(result["receipt"]["authority_status_after"], "CONSUMED")
        self.assertEqual(result["receipt"]["authority_remaining_uses_after"], 0)
        self.assertEqual(result["receipt"]["authority_effect"], "NONE")
        self.assertEqual(
            result["receipt"]["consumption_effect"],
            "CONSUMED_ONE_USE",
        )
        self.assertEqual(after["envelope"]["status"], "CONSUMED")
        self.assertEqual(after["envelope"]["remaining_uses"], 0)

    def test_replay_is_denied_without_second_invocation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor("B")
            env = envelope_for(candidate, "CAP.CONSUME.B")
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            composition = compose(root, store, env, candidate)

            calls: list[str] = []
            ticks = iter([
                "2026-09-25T00:00:01Z",
                "2026-09-25T00:00:02Z",
            ])
            first = consume_admitted_authority_once(
                composition_receipt=composition,
                successor_candidate=candidate,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("first") or {"ok": True},
                clock=lambda: next(ticks),
            )
            second = consume_admitted_authority_once(
                composition_receipt=composition,
                successor_candidate=candidate,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("second") or {"bad": True},
                clock=lambda: "2026-09-25T00:00:03Z",
            )

        self.assertTrue(first["consumed"])
        self.assertFalse(second["consumed"])
        self.assertEqual(second["blockers"], ["authority_verification_failed"])
        self.assertEqual(calls, ["first"])

    def test_wrong_successor_is_blocked_before_consumption(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_a = successor("C")
            candidate_b = successor("D")
            env = envelope_for(candidate_a, "CAP.CONSUME.C")
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            composition = compose(root, store, env, candidate_a)

            calls: list[str] = []
            result = consume_admitted_authority_once(
                composition_receipt=composition,
                successor_candidate=candidate_b,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("wrong"),
                clock=lambda: "2026-09-25T00:00:01Z",
            )
            after = store.read(env["capability_id"])

        self.assertFalse(result["consumed"])
        self.assertEqual(
            result["blockers"],
            ["composition_successor_id_mismatch"],
        )
        self.assertEqual(calls, [])
        self.assertEqual(after["envelope"]["status"], "ACTIVE")
        self.assertEqual(after["envelope"]["remaining_uses"], 1)

    def test_tampered_composition_receipt_is_blocked(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor("E")
            env = envelope_for(candidate, "CAP.CONSUME.E")
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            composition = compose(root, store, env, candidate)
            tampered = dict(composition)
            tampered["atomic_admission_id"] = (
                "atomic-admission:sha256:" + "9" * 64
            )

            calls: list[str] = []
            result = consume_admitted_authority_once(
                composition_receipt=tampered,
                successor_candidate=candidate,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("tampered"),
                clock=lambda: "2026-09-25T00:00:01Z",
            )
            after = store.read(env["capability_id"])

        self.assertFalse(result["consumed"])
        self.assertEqual(result["blockers"], ["admission_or_successor_invalid"])
        self.assertEqual(calls, [])
        self.assertEqual(after["envelope"]["status"], "ACTIVE")

    def test_post_reservation_failure_enters_recovery_required_and_replay_denied(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor("F")
            env = envelope_for(candidate, "CAP.CONSUME.F")
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            composition = compose(root, store, env, candidate)

            calls: list[str] = []
            ticks = iter([
                "2026-09-25T00:00:01Z",
                "2026-09-25T00:00:02Z",
            ])

            def fail():
                calls.append("failed-once")
                raise RuntimeError("fixture failure")

            with self.assertRaises(AuthorityInvocationError):
                consume_admitted_authority_once(
                    composition_receipt=composition,
                    successor_candidate=candidate,
                    authority_envelope=env,
                    attempting_principal_id="CODEX_PRINCIPAL_001",
                    authority_store=store,
                    invoke=fail,
                    clock=lambda: next(ticks),
                )

            after_failure = store.read(env["capability_id"])
            retry = consume_admitted_authority_once(
                composition_receipt=composition,
                successor_candidate=candidate,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("illegal-retry"),
                clock=lambda: "2026-09-25T00:00:03Z",
            )

        self.assertEqual(after_failure["envelope"]["status"], "RECOVERY_REQUIRED")
        self.assertEqual(after_failure["envelope"]["remaining_uses"], 0)
        self.assertFalse(retry["consumed"])
        self.assertEqual(retry["blockers"], ["authority_verification_failed"])
        self.assertEqual(calls, ["failed-once"])


if __name__ == "__main__":
    unittest.main()
