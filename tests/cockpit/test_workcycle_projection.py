from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.cockpit.workcycle_projection import build_workcycle_projection
from src.coordination import workcycle_v0 as wc


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

    def test_projection_labels_partial_eligibility_and_completed_work_truthfully(self):
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

            consequence = wc.observed_consequence(
                consequence_id="K1",
                work_item_id="W1",
                decomposition_id="D1",
                input_state_identity="S1",
                output_artifact_identities=["O1"],
                observations={"delta_bytes": -5},
                declared_changes_observed={"size": "DECREASED"},
                unchanged_coordinates_observed={"authority": "NONE"},
                evidence_handles=["E1"],
                unresolved=["historical review debt"],
            )
            evaluation = wc.consequence_evaluation(
                evaluation_id="E1",
                work_item={"work_item_id": "W1"},
                consequence=consequence,
                disposition="CONSEQUENCE_MATCHED",
                conservation_surfaces={"identity": "MATCHED"},
                load_dimensions={"semantic": "MATCHED"},
                unresolved=["bounded claim ceiling remains"],
            )
            budget = wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001")

            (state / "WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_OBSERVED_CONSEQUENCE.json").write_text(
                json.dumps(consequence), encoding="utf-8"
            )
            (state / "WORKCYCLE_STABILIZATION_001_COMPRESSION_W1_CONSEQUENCE_EVALUATION.json").write_text(
                json.dumps(evaluation), encoding="utf-8"
            )
            (state / "WAKE_BUDGET_V0.json").write_text(
                json.dumps(budget), encoding="utf-8"
            )

            projection = build_workcycle_projection(repo)
            self.assertIsNone(projection["active_work_item"])
            self.assertEqual(projection["latest_completed_work_item"], "W1")
            self.assertIsNone(projection["next_eligible_work_item"])
            self.assertEqual(
                projection["eligibility"]["posture"],
                "PARTIAL_COORDINATES_ONLY",
            )
            self.assertIsNone(projection["eligibility"]["eligible"])
            self.assertIn(
                "seat_available",
                projection["eligibility"]["unresolved_coordinates"],
            )
            self.assertEqual(
                projection["current_unresolved"],
                ["bounded claim ceiling remains"],
            )
            self.assertEqual(
                projection["historical_unresolved"],
                ["historical review debt"],
            )
            self.assertEqual(
                projection["wake_budget"]["object_type"],
                "WAKE_BUDGET_V0",
            )
            self.assertEqual(
                projection["campaign_cumulative_budget"]["status"],
                "NOT_IMPLEMENTED",
            )

    def test_malformed_optional_state_is_visible_as_projection_error(self):
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
            (state / "WAKE_BUDGET_V0.json").write_text(
                '{"object_type":"WAKE_BUDGET_V0","integrity_sha256":"bad"}',
                encoding="utf-8",
            )
            projection = build_workcycle_projection(repo)
            self.assertTrue(projection["projection_errors"])
            self.assertTrue(projection["current_unresolved"])
            self.assertIsNone(projection["wake_budget"])

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
            self.assertEqual(projection["operator_summary"]["workflow"], "OFF")
            self.assertFalse(projection["operator_summary"]["wake_requested"])
            self.assertEqual(projection["operator_summary"]["requested_workflow"], "ON")
            self.assertTrue(projection["operator_summary"]["requested_wake"])
            self.assertFalse(projection["operator_summary"]["local_control_admitted"])
            self.assertFalse(
                projection["operative_control"]["repo_control_has_execution_effect"]
            )
            self.assertFalse(
                projection["projection_boundary"]["creates_authority"]
            )
            self.assertFalse(
                projection["projection_boundary"]["performs_execution"]
            )


if __name__ == "__main__":
    unittest.main()
