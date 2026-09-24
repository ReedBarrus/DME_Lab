from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.workcycle_control import (
    LocalWorkcycleControlStore,
    WorkcycleControlError,
)


class WorkcycleControlTests(unittest.TestCase):
    def test_enable_wake_pause_stop_are_real_local_state_transitions(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            store = LocalWorkcycleControlStore(
                path=root / "control.json",
                repo=repo,
            )

            initial = store.read()
            self.assertFalse(initial["workflow_enabled"])
            self.assertEqual(initial["lifecycle_state"], "PAUSED")

            enable = store.preview({
                "verb": "ENABLE",
                "gesture_id": "G1",
                "reason": "operator enable",
            })
            enabled = store.commit(
                preview=enable["preview"],
                preview_sha256=enable["preview_sha256"],
                confirmed_by="REED",
            )["state"]
            self.assertTrue(enabled["workflow_enabled"])
            self.assertTrue(enabled["seat_work_enabled"])
            self.assertEqual(enabled["lifecycle_state"], "ACTIVE")

            wake = store.preview({
                "verb": "WAKE",
                "gesture_id": "G2",
            })
            woken = store.commit(
                preview=wake["preview"],
                preview_sha256=wake["preview_sha256"],
                confirmed_by="REED",
            )["state"]
            self.assertTrue(woken["wake_requested"])
            self.assertEqual(woken["wake_generation"], 1)

            pause = store.preview({
                "verb": "PAUSE",
                "gesture_id": "G3",
            })
            paused = store.commit(
                preview=pause["preview"],
                preview_sha256=pause["preview_sha256"],
                confirmed_by="REED",
            )["state"]
            self.assertFalse(paused["workflow_enabled"])
            self.assertFalse(paused["wake_requested"])
            self.assertEqual(paused["lifecycle_state"], "PAUSED")

            enable2 = store.preview({"verb": "ENABLE", "gesture_id": "G4"})
            store.commit(
                preview=enable2["preview"],
                preview_sha256=enable2["preview_sha256"],
                confirmed_by="REED",
            )
            stop = store.preview({"verb": "STOP", "gesture_id": "G5"})
            stopped = store.commit(
                preview=stop["preview"],
                preview_sha256=stop["preview_sha256"],
                confirmed_by="REED",
            )["state"]
            self.assertEqual(stopped["lifecycle_state"], "STOPPED")
            self.assertFalse(stopped["workflow_enabled"])
            self.assertFalse(stopped["seat_work_enabled"])
            self.assertFalse(stopped["wake_requested"])

    def test_wake_requires_enabled_workflow(self):
        with TemporaryDirectory() as tmp:
            store = LocalWorkcycleControlStore(
                path=Path(tmp) / "control.json",
                repo=Path(tmp),
            )
            store.read()
            with self.assertRaisesRegex(WorkcycleControlError, "WAKE requires"):
                store.preview({"verb": "WAKE", "gesture_id": "G1"})

    def test_preview_identity_and_current_state_are_revalidated(self):
        with TemporaryDirectory() as tmp:
            store = LocalWorkcycleControlStore(
                path=Path(tmp) / "control.json",
                repo=Path(tmp),
            )
            first = store.preview({"verb": "ENABLE", "gesture_id": "G1"})

            with self.assertRaisesRegex(WorkcycleControlError, "preview identity mismatch"):
                store.commit(
                    preview=first["preview"],
                    preview_sha256="0" * 64,
                    confirmed_by="REED",
                )

            second = store.preview({"verb": "ENABLE", "gesture_id": "G2"})
            store.commit(
                preview=second["preview"],
                preview_sha256=second["preview_sha256"],
                confirmed_by="REED",
            )

            with self.assertRaisesRegex(WorkcycleControlError, "state changed after preview"):
                store.commit(
                    preview=first["preview"],
                    preview_sha256=first["preview_sha256"],
                    confirmed_by="REED",
                )

    def test_non_operator_confirmation_is_rejected(self):
        with TemporaryDirectory() as tmp:
            store = LocalWorkcycleControlStore(
                path=Path(tmp) / "control.json",
                repo=Path(tmp),
            )
            preview = store.preview({"verb": "ENABLE", "gesture_id": "G1"})
            with self.assertRaisesRegex(
                WorkcycleControlError,
                "explicit local operator confirmation required",
            ):
                store.commit(
                    preview=preview["preview"],
                    preview_sha256=preview["preview_sha256"],
                    confirmed_by="NOT_REED",
                )

    def test_admit_one_fails_closed_without_source_bound_eligibility(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalWorkcycleControlStore(
                path=root / "control.json",
                repo=root,
            )
            enable = store.preview({"verb": "ENABLE", "gesture_id": "G1"})
            store.commit(
                preview=enable["preview"],
                preview_sha256=enable["preview_sha256"],
                confirmed_by="REED",
            )
            wake = store.preview({"verb": "WAKE", "gesture_id": "G2"})
            store.commit(
                preview=wake["preview"],
                preview_sha256=wake["preview_sha256"],
                confirmed_by="REED",
            )
            with self.assertRaisesRegex(
                WorkcycleControlError,
                "no source-bound next eligible work item exists",
            ):
                store.preview({"verb": "ADMIT_ONE", "gesture_id": "G3"})


if __name__ == "__main__":
    unittest.main()
