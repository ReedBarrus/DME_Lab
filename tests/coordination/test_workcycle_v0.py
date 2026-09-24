from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.coordination import workcycle_v0 as wc


class WorkcycleV0Tests(unittest.TestCase):
    def test_budget_allows_exactly_one_item_per_wake(self):
        budget = wc.new_budget(campaign_id="C1")
        reserved = wc.reserve_one_item(budget)
        with self.assertRaises(wc.WorkcycleError):
            wc.reserve_one_item(reserved)
        settled = wc.settle_one_item(reserved)
        with self.assertRaises(wc.WorkcycleError):
            wc.reserve_one_item(settled)
        reset = wc.reset_wake_budget(settled)
        again = wc.reserve_one_item(reset)
        self.assertEqual(again["work_items"]["reserved"], 1)

    def test_unsettled_budget_cannot_reset(self):
        budget = wc.reserve_one_item(wc.new_budget(campaign_id="C1"))
        with self.assertRaises(wc.WorkcycleError):
            wc.reset_wake_budget(budget)

    def test_eligibility_requires_every_coordinate(self):
        budget = wc.new_budget(campaign_id="C1")
        ok = wc.evaluate_eligibility(
            dependency_satisfied=True,
            frame_current=True,
            seat_available=True,
            no_hold=True,
            authority_satisfied=True,
            budget=budget,
        )
        self.assertTrue(ok["eligible"])
        blocked = wc.evaluate_eligibility(
            dependency_satisfied=True,
            frame_current=False,
            seat_available=True,
            no_hold=True,
            authority_satisfied=True,
            budget=budget,
        )
        self.assertFalse(blocked["eligible"])
        self.assertEqual(blocked["blockers"], ["frame_current"])

    def test_consequence_binds_exact_work_identity(self):
        consequence = wc.observed_consequence(
            consequence_id="K1",
            work_item_id="W1",
            decomposition_id="D1",
            input_state_identity="abc",
            output_artifact_identities=["out"],
            observations={"delta_bytes": -10},
            declared_changes_observed={"size": "DECREASED"},
            unchanged_coordinates_observed={"authority": "NONE"},
            evidence_handles=["e1"],
            unresolved=[],
        )
        wc.verify_seal(consequence)
        work = {"work_item_id": "W1"}
        evaluation = wc.consequence_evaluation(
            evaluation_id="E1",
            work_item=work,
            consequence=consequence,
            disposition="CONSEQUENCE_MATCHED",
            conservation_surfaces={"identity": "MATCHED"},
            load_dimensions={"semantic": "MATCHED"},
            unresolved=[],
        )
        self.assertEqual(evaluation["work_item_id"], "W1")
        with self.assertRaises(wc.WorkcycleError):
            wc.consequence_evaluation(
                evaluation_id="E2",
                work_item={"work_item_id": "OTHER"},
                consequence=consequence,
                disposition="CONSEQUENCE_MATCHED",
                conservation_surfaces={},
                load_dimensions={},
                unresolved=[],
            )

    def test_repair_routing_is_typed(self):
        expected = {
            "OUTPUT_DEFECT": "WORK_OUTPUT_REPAIR",
            "DECOMPOSITION_DEFECT": "REDECOMPOSE_WORK_FAMILY",
            "CAMPAIGN_HORIZON_DEFECT": "HOLD_FOR_CAMPAIGN_REPLAN",
            "APPARATUS_DEFECT": "APPARATUS_REPAIR",
        }
        for defect, destination in expected.items():
            route = wc.route_repair(
                evaluation_id="E1",
                defect_class=defect,
                affected_object="X",
                basis=["B"],
            )
            self.assertEqual(route["repair_destination"], destination)
            self.assertTrue(route["preserve_evidence"])
            self.assertFalse(route["retry_permitted"])

    def test_no_repair_route_for_matched_consequence(self):
        route = wc.route_repair(
            evaluation_id="E1",
            defect_class="NONE",
            affected_object="W1",
            basis=["review"],
        )
        self.assertEqual(route["repair_destination"], "NONE")
        self.assertFalse(route["campaign_replan_required"])

    def test_continuation_gate_blocks_when_workflow_is_off(self):
        budget = wc.new_budget(campaign_id="C1")
        decision = wc.evaluate_one_successor_continuation(
            control={
                "workflow_enabled": False,
                "campaign_enabled": True,
                "seat_work_enabled": True,
                "wake_requested": True,
                "auto_continuation_limit": 1,
            },
            dependency_satisfied=True,
            frame_current=True,
            seat_available=True,
            no_hold=True,
            authority_satisfied=True,
            budget=budget,
        )
        self.assertFalse(decision["admit_one_successor"])
        self.assertIn("workflow_enabled", decision["blockers"])
        self.assertFalse(decision["execution_performed"])

    def test_continuation_gate_admits_one_then_budget_blocks_second(self):
        budget = wc.new_budget(campaign_id="C1")
        control = {
            "workflow_enabled": True,
            "campaign_enabled": True,
            "seat_work_enabled": True,
            "wake_requested": True,
            "auto_continuation_limit": 1,
        }
        first = wc.evaluate_one_successor_continuation(
            control=control,
            dependency_satisfied=True,
            frame_current=True,
            seat_available=True,
            no_hold=True,
            authority_satisfied=True,
            budget=budget,
        )
        self.assertTrue(first["admit_one_successor"])
        self.assertEqual(first["max_successors_admitted"], 1)

        reserved = wc.reserve_one_item(budget)
        second = wc.evaluate_one_successor_continuation(
            control=control,
            dependency_satisfied=True,
            frame_current=True,
            seat_available=True,
            no_hold=True,
            authority_satisfied=True,
            budget=reserved,
        )
        self.assertFalse(second["admit_one_successor"])
        self.assertIn("budget_reservable", second["blockers"])

    def test_progress_projection_reports_missing_evidence_not_standing(self):
        with tempfile.TemporaryDirectory() as tmp:
            projection = wc.derive_campaign_progress(tmp)
            wc.verify_seal(projection)
            self.assertEqual(projection["object_type"], wc.PROGRESS_TYPE)
            self.assertEqual(projection["projection_effect"]["campaign_standing"], "NONE")
            self.assertEqual(projection["cells"]["T0"]["posture"], "UNRESOLVED")
            self.assertEqual(projection["next_pressure"], "T0")


if __name__ == "__main__":
    unittest.main()
