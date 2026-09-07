from __future__ import annotations

import unittest

from src.runtime.historical_relation_pressure import run


class HistoricalRelationPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_all_specimens_pass_integrity_and_continuity(self) -> None:
        for result in self.report["specimens"].values():
            self.assertTrue(result["integrity"]["ok"])
            self.assertTrue(result["continuity"]["ok"])

    def test_h13_relation_results(self) -> None:
        self.assertEqual(
            self.report["pressure_matrix"]["H13_tail_loss"],
            {"equality": False, "lower_bound": False, "prefix": False},
        )

    def test_h14_relation_results(self) -> None:
        self.assertEqual(
            self.report["pressure_matrix"]["H14_control"],
            {"equality": True, "lower_bound": True, "prefix": True},
        )

    def test_h16_extension_relation_results(self) -> None:
        self.assertEqual(
            self.report["pressure_matrix"]["H16_extension"],
            {"equality": False, "lower_bound": True, "prefix": True},
        )

    def test_h16_replacement_relation_results(self) -> None:
        self.assertEqual(
            self.report["pressure_matrix"]["H16_replacement"],
            {"equality": False, "lower_bound": True, "prefix": False},
        )

    def test_prefix_separates_extension_from_replacement(self) -> None:
        extension = self.report["specimens"]["H16_extension"]
        replacement = self.report["specimens"]["H16_replacement"]

        self.assertTrue(extension["relations"]["lower_bound"]["ok"])
        self.assertTrue(replacement["relations"]["lower_bound"]["ok"])
        self.assertTrue(extension["relations"]["prefix"]["ok"])
        self.assertFalse(replacement["relations"]["prefix"]["ok"])

    def test_downstream_state_branches_remain_distinguishable(self) -> None:
        states = {
            name: result["derived_state"]
            for name, result in self.report["specimens"].items()
        }

        self.assertEqual(states["H13_tail_loss"]["projection_subject_count"], 6)
        self.assertEqual(states["H14_control"]["projection_subject_count"], 7)
        self.assertEqual(states["H16_extension"]["projection_subject_count"], 8)
        self.assertEqual(states["H16_replacement"]["orphan_admission_count"], 1)
        self.assertNotEqual(states["H16_extension"], states["H16_replacement"])

    def test_report_preserves_boundaries(self) -> None:
        self.assertEqual(self.report["finding"], "extent growth does not establish historical conservation")
        self.assertTrue(self.report["git_supplied_historical_evidence"])
        self.assertFalse(self.report["new_persistent_witness_architecture_required"])
        self.assertEqual(self.report["persistent_architecture_added"], [])
        self.assertEqual(
            self.report["prior_witnessed_history"]["prefix_source_classification"],
            "Git analytical comparison evidence, not runtime witness authority",
        )


if __name__ == "__main__":
    unittest.main()
