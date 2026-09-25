from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.coordination import workcycle_v0 as wc
from src.coordination.verified_authority_admission_v0 import (
    successor_authority_coordinates,
    try_verified_authority_atomic_admission,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    consume_authority_once,
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
            "reconciliation_identity": f"{label.lower()}" * 64,
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


def envelope_for(candidate: dict, capability: str = "CAP.COMP.001") -> dict:
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


def attempt(
    atomic_root: Path,
    authority_store: LocalAuthorityStateStore,
    env: dict,
    candidate: dict,
    attempt_id: str,
) -> dict:
    return try_verified_authority_atomic_admission(
        store_dir=atomic_root,
        authority_store=authority_store,
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


class VerifiedAuthorityAtomicAdmissionV0Tests(unittest.TestCase):
    def test_exact_verified_authority_and_successor_admit_without_consumption(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor()
            env = envelope_for(candidate)
            store = LocalAuthorityStateStore(root / "authority")
            before = store.issue(env)
            result = attempt(root / "atomic", store, env, candidate, "ATTEMPT-A")
            after = store.read(env["capability_id"])

        self.assertTrue(result["admitted"])
        self.assertEqual(result["blockers"], [])
        receipt = result["receipt"]
        self.assertEqual(receipt["successor_id"], candidate["successor_id"])
        self.assertEqual(
            receipt["authority_verification"],
            "VERIFIED_CURRENT_ACTIVE_ONE_USE",
        )
        self.assertEqual(
            receipt["authority_input_posture"],
            "VERIFIED_CURRENT_BINDING",
        )
        self.assertFalse(receipt["authority_consumed"])
        self.assertTrue(receipt["underlying_atomic_receipt_claim_unchanged"])
        self.assertEqual(before, after)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["consumption_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["model_invocation_effect"], "NONE")

    def test_authority_for_different_successor_fails_closed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_a = successor("A")
            candidate_b = successor("B")
            env = envelope_for(candidate_a)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            result = attempt(root / "atomic", store, env, candidate_b, "WRONG-SUCCESSOR")

        self.assertFalse(result["admitted"])
        self.assertIn("authority_request_successor_mismatch", result["blockers"])
        self.assertIsNone(result["receipt"])
        self.assertFalse((root / "atomic" / "atomic_admission_state.json").exists())

    def test_tampered_successor_fails_before_admission(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor()
            env = envelope_for(candidate)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            tampered = dict(candidate)
            tampered["basis_id"] = "B-TAMPERED"
            result = attempt(root / "atomic", store, env, tampered, "TAMPERED")

        self.assertFalse(result["admitted"])
        self.assertEqual(result["blockers"], ["successor_candidate_invalid"])
        self.assertFalse((root / "atomic" / "atomic_admission_state.json").exists())

    def test_consumed_authority_fails_before_admission(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor()
            env = envelope_for(candidate)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            ticks = iter([
                "2026-09-25T00:00:01Z",
                "2026-09-25T00:00:02Z",
            ])
            consume_authority_once(
                env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                store=store,
                invoke=lambda: {"ok": True},
                clock=lambda: next(ticks),
            )
            result = attempt(root / "atomic", store, env, candidate, "CONSUMED")

        self.assertFalse(result["admitted"])
        self.assertEqual(result["blockers"], ["authority_verification_failed"])
        self.assertFalse((root / "atomic" / "atomic_admission_state.json").exists())

    def test_two_same_process_callers_still_produce_one_atomic_admission(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = successor()
            env = envelope_for(candidate)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(
                    pool.map(
                        lambda attempt_id: attempt(
                            root / "atomic",
                            store,
                            env,
                            candidate,
                            attempt_id,
                        ),
                        ["RACE-A", "RACE-B"],
                    )
                )

            after = store.read(env["capability_id"])

        admitted = [item for item in results if item["admitted"]]
        blocked = [item for item in results if not item["admitted"]]
        self.assertEqual(len(admitted), 1)
        self.assertEqual(len(blocked), 1)
        self.assertIn("active_admission", blocked[0]["blockers"])
        self.assertEqual(after["envelope"]["status"], "ACTIVE")
        self.assertEqual(after["envelope"]["remaining_uses"], 1)


if __name__ == "__main__":
    unittest.main()
