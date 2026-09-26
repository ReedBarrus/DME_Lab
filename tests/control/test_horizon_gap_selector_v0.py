from __future__ import annotations

import unittest

from src.control.horizon_gap_selector_v0 import (
    HorizonGapSelectorError,
    SELECTED,
    STOP,
    select_gap_or_stop,
)
from src.control.relational_horizon_v0 import build_relational_horizon
from tests.control.test_relational_horizon_v0 import (
    HID,
    PURPOSE,
    SUBJECT,
    SURFACE,
    after_horizon,
    before_horizon,
    live_gap,
)


class HorizonGapSelectorV0Tests(unittest.TestCase):
    def test_one_declared_eligible_gap_is_selected_exactly(self):
        horizon = before_horizon()
        result = select_gap_or_stop(horizon)
        self.assertEqual(result["selection_posture"], SELECTED)
        self.assertEqual(result["eligible_gap_count"], 1)
        self.assertEqual(
            result["selected_gap_id"],
            "G1_STALE_SUCCESSOR_3_HANDOFF",
        )
        self.assertEqual(result["selected_gap"], live_gap())
        self.assertFalse(result["stop_required"])

    def test_closed_empty_horizon_returns_no_justified_work(self):
        result = select_gap_or_stop(after_horizon())
        self.assertEqual(result["selection_posture"], STOP)
        self.assertEqual(result["eligible_gap_count"], 0)
        self.assertIsNone(result["selected_gap_id"])
        self.assertIsNone(result["selected_gap"])
        self.assertTrue(result["stop_required"])

    def test_noneligible_declared_gap_does_not_get_selected(self):
        gap = live_gap()
        gap["work_eligible"] = False
        horizon = build_relational_horizon(
            horizon_id=HID,
            subject=SUBJECT,
            counterparty_or_surface=SURFACE,
            declared_purpose=PURPOSE,
            posture="PARTIAL",
            evidence_refs=["fixture://ineligible"],
            load_bearing_gaps=[gap],
        )
        result = select_gap_or_stop(horizon)
        self.assertEqual(result["selection_posture"], STOP)
        self.assertTrue(result["stop_required"])

    def test_multiple_eligible_gaps_are_rejected_not_ranked(self):
        gap2 = {
            "gap_id": "G2_SECOND_ELIGIBLE_GAP",
            "statement": "another eligible gap exists",
            "blocks": ["RECONSTRUCTION"],
            "work_eligible": True,
        }
        horizon = build_relational_horizon(
            horizon_id=HID,
            subject=SUBJECT,
            counterparty_or_surface=SURFACE,
            declared_purpose=PURPOSE,
            posture="PARTIAL",
            evidence_refs=["fixture://multi-gap"],
            load_bearing_gaps=[live_gap(), gap2],
        )
        with self.assertRaisesRegex(
            HorizonGapSelectorError,
            "does not rank or choose",
        ):
            select_gap_or_stop(horizon)

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(
            select_gap_or_stop(before_horizon()),
            select_gap_or_stop(before_horizon()),
        )
        self.assertEqual(
            select_gap_or_stop(after_horizon()),
            select_gap_or_stop(after_horizon()),
        )

    def test_selection_binds_exact_horizon_state(self):
        before = before_horizon()
        after = after_horizon()
        selected = select_gap_or_stop(before)
        stopped = select_gap_or_stop(after)
        self.assertEqual(selected["source_horizon_id"], before["horizon_id"])
        self.assertEqual(
            selected["source_horizon_state_id"],
            before["horizon_state_id"],
        )
        self.assertEqual(
            selected["source_horizon_integrity_sha256"],
            before["integrity_sha256"],
        )
        self.assertNotEqual(
            selected["source_horizon_state_id"],
            stopped["source_horizon_state_id"],
        )

    def test_no_ranking_planning_or_consequence_effects(self):
        for result in (
            select_gap_or_stop(before_horizon()),
            select_gap_or_stop(after_horizon()),
        ):
            self.assertEqual(result["ranking_effect"], "NONE")
            self.assertEqual(result["planning_effect"], "NONE")
            self.assertEqual(result["work_materialization_effect"], "NONE")
            self.assertEqual(result["work_admission_effect"], "NONE")
            self.assertEqual(result["authority_effect"], "NONE")
            self.assertEqual(result["execution_effect"], "NONE")
            self.assertEqual(result["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
