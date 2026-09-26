from __future__ import annotations

import copy
import unittest

from src.control.relational_horizon_v0 import (
    RelationalHorizonError,
    build_relational_horizon,
    validate_relational_horizon,
)


HID = "H1_POST_CONSEQUENCE_PHASE_HANDOFF"
SUBJECT = "post-consequence phase handoff"
SURFACE = "docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md"
PURPOSE = "Enter the control-kernel phase without manufacturing continuation after lawful no-successor closure."


def live_gap():
    return {
        "gap_id": "G1_STALE_SUCCESSOR_3_HANDOFF",
        "statement": (
            "The post-consequence projection requires SUCCESSOR_3 even though "
            "earned law permits SATISFIED -> CLOSE_BASIS -> NO_SUCCESSOR -> STOP."
        ),
        "blocks": ["CONTROL_KERNEL_ACTIVATION", "CAMPAIGN_HANDOFF", "RECONSTRUCTION"],
        "work_eligible": True,
    }


def before_horizon():
    return build_relational_horizon(
        horizon_id=HID,
        subject=SUBJECT,
        counterparty_or_surface=SURFACE,
        declared_purpose=PURPOSE,
        posture="PARTIAL",
        evidence_refs=["repo://235aceddfec91af6826e25baef469c82287fde99"],
        load_bearing_gaps=[live_gap()],
    )


def after_horizon():
    return build_relational_horizon(
        horizon_id=HID,
        subject=SUBJECT,
        counterparty_or_surface=SURFACE,
        declared_purpose=PURPOSE,
        posture="CLOSED",
        evidence_refs=["repo://331578bc44225d2810c9d5604606e83864553d0f"],
        load_bearing_gaps=[],
    )


class RelationalHorizonV0Tests(unittest.TestCase):
    def test_before_and_after_preserve_logical_horizon_identity(self):
        before = before_horizon()
        after = after_horizon()
        self.assertEqual(before["horizon_id"], after["horizon_id"])
        self.assertNotEqual(before["horizon_state_id"], after["horizon_state_id"])
        self.assertNotEqual(before["integrity_sha256"], after["integrity_sha256"])

    def test_before_represents_exactly_one_declared_live_gap(self):
        horizon = before_horizon()
        self.assertEqual(horizon["current_posture"]["state"], "PARTIAL")
        self.assertEqual(len(horizon["load_bearing_gaps"]), 1)
        self.assertEqual(
            horizon["load_bearing_gaps"][0]["gap_id"],
            "G1_STALE_SUCCESSOR_3_HANDOFF",
        )

    def test_after_represents_closed_empty_gap_state(self):
        horizon = after_horizon()
        self.assertEqual(horizon["current_posture"]["state"], "CLOSED")
        self.assertEqual(horizon["load_bearing_gaps"], [])

    def test_closed_horizon_cannot_retain_live_gap(self):
        with self.assertRaisesRegex(RelationalHorizonError, "cannot retain live gaps"):
            build_relational_horizon(
                horizon_id=HID,
                subject=SUBJECT,
                counterparty_or_surface=SURFACE,
                declared_purpose=PURPOSE,
                posture="CLOSED",
                evidence_refs=["fixture://closed"],
                load_bearing_gaps=[live_gap()],
            )

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(before_horizon(), before_horizon())
        self.assertEqual(after_horizon(), after_horizon())

    def test_validation_rejects_tampering(self):
        horizon = before_horizon()
        tampered = copy.deepcopy(horizon)
        tampered["current_posture"]["state"] = "CLOSED"
        with self.assertRaises(Exception):
            validate_relational_horizon(tampered)

    def test_challenge_posture_does_not_create_work(self):
        horizon = build_relational_horizon(
            horizon_id=HID,
            subject=SUBJECT,
            counterparty_or_surface=SURFACE,
            declared_purpose=PURPOSE,
            posture="UNKNOWN",
            evidence_refs=["fixture://challenge"],
            load_bearing_gaps=[],
            anomaly_count=1,
            stale_basis=True,
            external_novelty_present=True,
        )
        self.assertEqual(horizon["gap_selection_effect"], "NONE")
        self.assertEqual(horizon["work_justification_effect"], "NONE")
        self.assertEqual(horizon["work_materialization_effect"], "NONE")

    def test_no_selection_authority_execution_or_standing_effect(self):
        for horizon in (before_horizon(), after_horizon()):
            self.assertEqual(horizon["gap_selection_effect"], "NONE")
            self.assertEqual(horizon["work_justification_effect"], "NONE")
            self.assertEqual(horizon["work_materialization_effect"], "NONE")
            self.assertEqual(horizon["authority_effect"], "NONE")
            self.assertEqual(horizon["execution_effect"], "NONE")
            self.assertEqual(horizon["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
