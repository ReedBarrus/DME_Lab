from __future__ import annotations

import unittest

from src.control.relational_horizon_v0 import build_relational_horizon
from src.control.horizon_gap_selector_v0 import select_gap_or_stop


HORIZON_ID = "H1_POST_CONSEQUENCE_PHASE_HANDOFF"
GAP_ID = "G1_STALE_SUCCESSOR_3_HANDOFF"


def horizon(work_eligible: bool) -> dict:
    return build_relational_horizon(
        horizon_id=HORIZON_ID,
        subject="post-consequence phase handoff",
        counterparty_or_surface=(
            "docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md"
        ),
        declared_purpose=(
            "Enter the control-kernel phase without manufacturing continuation "
            "after lawful no-successor closure."
        ),
        posture="PARTIAL",
        evidence_refs=["repo://G14_DECLARATION_ELIGIBILITY_PRESSURE"],
        load_bearing_gaps=[
            {
                "gap_id": GAP_ID,
                "statement": "declared eligible gap",
                "blocks": ["CONTROL_KERNEL_ACTIVATION"],
                "work_eligible": work_eligible,
            }
        ],
        representation_source="EXTERNALLY_SUPPLIED",
    )


class DeclarationWorkEligibilitySelectionLoadV0Tests(unittest.TestCase):
    def test_control_selects_declared_eligible_gap(self):
        h = horizon(True)
        result = select_gap_or_stop(h)
        self.assertEqual(len(h["load_bearing_gaps"]), 1)
        self.assertTrue(h["load_bearing_gaps"][0]["work_eligible"])
        self.assertEqual(result["selection_posture"], "EXACT_ELIGIBLE_GAP")
        self.assertEqual(result["selected_gap_id"], GAP_ID)
        self.assertEqual(result["eligible_gap_count"], 1)
        self.assertFalse(result["stop_required"])

    def test_intervention_preserves_declared_gap_but_stops_selection(self):
        h = horizon(False)
        result = select_gap_or_stop(h)
        self.assertEqual(len(h["load_bearing_gaps"]), 1)
        self.assertEqual(h["load_bearing_gaps"][0]["gap_id"], GAP_ID)
        self.assertFalse(h["load_bearing_gaps"][0]["work_eligible"])
        self.assertEqual(result["selection_posture"], "NO_JUSTIFIED_WORK")
        self.assertIsNone(result["selected_gap_id"])
        self.assertEqual(result["eligible_gap_count"], 0)
        self.assertTrue(result["stop_required"])

    def test_only_work_eligibility_changes_in_gap_coordinates(self):
        a = horizon(True)["load_bearing_gaps"][0]
        b = horizon(False)["load_bearing_gaps"][0]
        self.assertEqual(a["gap_id"], b["gap_id"])
        self.assertEqual(a["statement"], b["statement"])
        self.assertEqual(a["blocks"], b["blocks"])
        self.assertNotEqual(a["work_eligible"], b["work_eligible"])

    def test_logical_horizon_identity_preserved(self):
        self.assertEqual(horizon(True)["horizon_id"], horizon(False)["horizon_id"])

    def test_no_downstream_authority_created(self):
        for eligible in (True, False):
            result = select_gap_or_stop(horizon(eligible))
            self.assertEqual(result["planning_effect"], "NONE")
            self.assertEqual(result["work_materialization_effect"], "NONE")
            self.assertEqual(result["work_admission_effect"], "NONE")
            self.assertEqual(result["authority_effect"], "NONE")
            self.assertEqual(result["execution_effect"], "NONE")
            self.assertEqual(result["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
