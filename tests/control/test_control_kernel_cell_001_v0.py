from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from src.control.control_kernel_cell_001_v0 import (
    ControlKernelCell001Error,
    evaluate_supplied_single_gap,
)


def specimen() -> dict:
    path = (
        Path(__file__).resolve().parents[2]
        / "docs/campaigns/control_kernel_001/state/"
        "CONTROL_KERNEL_CELL_001_SPECIMEN_V0.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def resolved_observation() -> dict:
    return {
        "precondition_present_before": True,
        "postcondition_present_after": True,
        "bounded_delta_observed": True,
        "pre_change_ref": "235aceddfec91af6826e25baef469c82287fde99",
        "post_change_ref": "331578bc44225d2810c9d5604606e83864553d0f",
        "target_path": "docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md",
    }


class ControlKernelCell001V0Tests(unittest.TestCase):
    def test_resolved_supplied_gap_stops(self):
        result = evaluate_supplied_single_gap(
            specimen=specimen(),
            repository_observation=resolved_observation(),
            remaining_gap_ids=[],
        )
        self.assertEqual(result["horizon_posture"], "HORIZON_SATISFIED")
        self.assertEqual(result["terminal_posture"], "NO_JUSTIFIED_WORK")
        self.assertTrue(result["stop_required"])

    def test_unresolved_gap_remains_live(self):
        obs = resolved_observation()
        obs["postcondition_present_after"] = False
        gap_id = specimen()["supplied_live_gaps"][0]["gap_id"]
        result = evaluate_supplied_single_gap(
            specimen=specimen(),
            repository_observation=obs,
            remaining_gap_ids=[gap_id],
        )
        self.assertEqual(result["horizon_posture"], "HORIZON_UNRESOLVED")
        self.assertEqual(result["terminal_posture"], "LIVE_GAP_REMAINS")
        self.assertFalse(result["stop_required"])

    def test_machine_selection_claim_is_rejected(self):
        s = specimen()
        s["machine_selection_claimed"] = True
        with self.assertRaisesRegex(
            ControlKernelCell001Error,
            "machine selection must remain unclaimed",
        ):
            evaluate_supplied_single_gap(
                specimen=s,
                repository_observation=resolved_observation(),
                remaining_gap_ids=[],
            )

    def test_competing_gaps_are_rejected(self):
        s = specimen()
        s["competing_gaps"] = [{"gap_id": "G2"}]
        with self.assertRaisesRegex(ControlKernelCell001Error, "competing gaps"):
            evaluate_supplied_single_gap(
                specimen=s,
                repository_observation=resolved_observation(),
                remaining_gap_ids=[],
            )

    def test_cell_cannot_invent_new_gap(self):
        with self.assertRaisesRegex(ControlKernelCell001Error, "cannot introduce new gaps"):
            evaluate_supplied_single_gap(
                specimen=specimen(),
                repository_observation=resolved_observation(),
                remaining_gap_ids=["G999"],
            )

    def test_fixed_inputs_are_deterministic(self):
        args = {
            "specimen": specimen(),
            "repository_observation": resolved_observation(),
            "remaining_gap_ids": [],
        }
        self.assertEqual(
            evaluate_supplied_single_gap(**copy.deepcopy(args)),
            evaluate_supplied_single_gap(**copy.deepcopy(args)),
        )

    def test_inputs_are_not_mutated(self):
        s = specimen()
        o = resolved_observation()
        s0 = copy.deepcopy(s)
        o0 = copy.deepcopy(o)
        evaluate_supplied_single_gap(
            specimen=s,
            repository_observation=o,
            remaining_gap_ids=[],
        )
        self.assertEqual(s, s0)
        self.assertEqual(o, o0)

    def test_no_selection_materialization_authority_or_execution_effect(self):
        result = evaluate_supplied_single_gap(
            specimen=specimen(),
            repository_observation=resolved_observation(),
            remaining_gap_ids=[],
        )
        self.assertEqual(result["gap_selection_effect"], "NONE")
        self.assertEqual(result["work_materialization_effect"], "NONE")
        self.assertEqual(result["work_admission_effect"], "NONE")
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
