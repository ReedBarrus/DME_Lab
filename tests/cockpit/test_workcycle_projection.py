from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.cockpit.workcycle_projection import build_workcycle_projection


class WorkcycleProjectionTests(unittest.TestCase):
    def test_projection_is_read_only_and_tolerates_missing_optional_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            projection = build_workcycle_projection(tmp)
            self.assertEqual(
                projection["projection_schema"],
                "workcycle_cockpit_projection_v0",
            )
            self.assertTrue(projection["projection_boundary"]["read_only"])
            self.assertFalse(
                projection["projection_boundary"]["creates_authority"]
            )
            self.assertFalse(
                projection["projection_boundary"]["performs_execution"]
            )
            self.assertEqual(
                projection["operator_summary"]["workflow"],
                "OFF",
            )

    def test_projection_reads_control_state_without_turning_it_into_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state = (
                repo
                / "docs"
                / "campaigns"
                / "workcycle_stabilization_001"
                / "state"
            )
            state.mkdir(parents=True)
            (state / "WORKCYCLE_CONTROL_V0.json").write_text(
                json.dumps(
                    {
                        "object_type": "WORKCYCLE_CONTROL_V0",
                        "campaign_id": "WORKCYCLE_STABILIZATION_001",
                        "workflow_enabled": True,
                        "campaign_enabled": True,
                        "seat_work_enabled": True,
                        "wake_requested": True,
                        "auto_continuation_limit": 1,
                        "operator_posture": "PRESSURE_FIXTURE",
                        "authority_effect": "NONE",
                        "execution_effect": "NONE",
                    }
                ),
                encoding="utf-8",
            )
            projection = build_workcycle_projection(repo)
            self.assertEqual(projection["operator_summary"]["workflow"], "ON")
            self.assertTrue(projection["operator_summary"]["wake_requested"])
            self.assertFalse(
                projection["projection_boundary"]["creates_authority"]
            )
            self.assertFalse(
                projection["projection_boundary"]["performs_execution"]
            )


if __name__ == "__main__":
    unittest.main()
