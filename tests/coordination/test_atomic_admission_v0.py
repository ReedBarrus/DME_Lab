from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.coordination import workcycle_v0 as wc
from src.coordination.atomic_admission_v0 import (
    AtomicAdmissionError,
    _acquire_lock,
    try_atomic_admission,
)


def control_on() -> dict:
    return {
        "workflow_enabled": True,
        "campaign_enabled": True,
        "seat_work_enabled": True,
        "wake_requested": True,
        "auto_continuation_limit": 1,
    }


def attempt(root: Path, attempt_id: str) -> dict:
    return try_atomic_admission(
        store_dir=root,
        campaign_id="WORKCYCLE_STABILIZATION_001",
        work_item_id="W-NEXT",
        work_attempt_id=attempt_id,
        seat_id="LABBOIB",
        occupant_id=f"occupant-{attempt_id}",
        wake_generation=1,
        authority_coordinate="AUTH_COORD_TEST_001",
        authority_satisfied=True,
        dependency_satisfied=True,
        frame_current=True,
        no_hold=True,
        control=control_on(),
        initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
    )


class AtomicAdmissionV0Tests(unittest.TestCase):
    def test_atomic_admission_binds_receipt_without_execution(self):
        with TemporaryDirectory() as tmp:
            result = attempt(Path(tmp), "ATTEMPT-A")

        self.assertTrue(result["admitted"])
        self.assertEqual(result["blockers"], [])
        receipt = result["receipt"]
        self.assertEqual(receipt["work_attempt_id"], "ATTEMPT-A")
        self.assertEqual(receipt["work_item_id"], "W-NEXT")
        self.assertEqual(receipt["seat_id"], "LABBOIB")
        self.assertEqual(receipt["authority_coordinate"], "AUTH_COORD_TEST_001")
        self.assertEqual(
            receipt["authority_input_posture"],
            "CALLER_SUPPLIED_PRECONDITION",
        )
        self.assertEqual(receipt["authority_verification"], "NOT_PERFORMED")
        self.assertFalse(result["execution_performed"])
        self.assertEqual(result["model_invocation_effect"], "NONE")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_second_same_wake_is_blocked_after_first_admission(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = attempt(root, "ATTEMPT-A")
            second = attempt(root, "ATTEMPT-B")

        self.assertTrue(first["admitted"])
        self.assertFalse(second["admitted"])
        self.assertIn("active_admission", second["blockers"])
        self.assertIn("seat_available", second["blockers"])
        self.assertIn("budget_reservable", second["blockers"])

    def test_two_racing_callers_produce_exactly_one_admission(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda x: attempt(root, x), ["RACE-A", "RACE-B"]))

        admitted = [item for item in results if item["admitted"]]
        blocked = [item for item in results if not item["admitted"]]
        self.assertEqual(len(admitted), 1)
        self.assertEqual(len(blocked), 1)
        self.assertIn("active_admission", blocked[0]["blockers"])
        self.assertFalse(admitted[0]["execution_performed"])
        self.assertEqual(admitted[0]["model_invocation_effect"], "NONE")

    def test_unsatisfied_authority_fails_closed_without_admission(self):
        with TemporaryDirectory() as tmp:
            result = try_atomic_admission(
                store_dir=Path(tmp),
                campaign_id="WORKCYCLE_STABILIZATION_001",
                work_item_id="W-NEXT",
                work_attempt_id="NO-AUTH",
                seat_id="LABBOIB",
                occupant_id="occupant",
                wake_generation=1,
                authority_coordinate="AUTH_COORD_TEST_001",
                authority_satisfied=False,
                dependency_satisfied=True,
                frame_current=True,
                no_hold=True,
                control=control_on(),
                initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
            )

        self.assertFalse(result["admitted"])
        self.assertIn("authority_satisfied", result["blockers"])
        self.assertIsNone(result["receipt"])

    def test_windows_permission_error_is_bounded_lock_contention(self):
        with TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "atomic_admission.lock"
            with (
                patch(
                    "src.coordination.atomic_admission_v0.os.open",
                    side_effect=[
                        PermissionError(13, "permission denied"),
                        PermissionError(13, "permission denied"),
                        123,
                    ],
                ) as mocked_open,
                patch("src.coordination.atomic_admission_v0.time.sleep"),
            ):
                fd = _acquire_lock(lock_path, attempts=3, delay=0)

        self.assertEqual(fd, 123)
        self.assertEqual(mocked_open.call_count, 3)

    def test_persistent_permission_error_fails_closed(self):
        with TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / "atomic_admission.lock"
            with (
                patch(
                    "src.coordination.atomic_admission_v0.os.open",
                    side_effect=PermissionError(13, "permission denied"),
                ),
                patch("src.coordination.atomic_admission_v0.time.sleep"),
            ):
                with self.assertRaises(AtomicAdmissionError):
                    _acquire_lock(lock_path, attempts=2, delay=0)

    def test_malformed_persisted_state_fails_closed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "atomic_admission_state.json").write_text(
                '{"object_type":"WRONG"}', encoding="utf-8"
            )
            with self.assertRaises(AtomicAdmissionError):
                attempt(root, "ATTEMPT-A")


if __name__ == "__main__":
    unittest.main()
