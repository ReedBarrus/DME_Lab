from __future__ import annotations

import unittest

from src.runtime.witness_content_ablation_pressure import EXPECTED_CAPABILITY, run


class WitnessContentAblationPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_all_specimens_pass_integrity_and_continuity(self) -> None:
        for specimen in self.report["specimens"].values():
            self.assertTrue(specimen["integrity"]["ok"])
            self.assertTrue(specimen["continuity"]["ok"])

    def test_capability_matrix_is_recorded(self) -> None:
        matrix = self.report["capability_matrix"]

        self.assertEqual(
            matrix["H13_tail_loss"],
            {
                "extent_only": False,
                "terminal_digest_only": False,
                "ordered_record_ids": False,
                "ordered_record_ids_commit_indices": False,
                "ordered_record_digests": False,
                "ordered_commit_index_digest": False,
                "five_field_prefix_identity": False,
                "full_canonical_prior_records": False,
            },
        )
        self.assertEqual(
            matrix["H14_control"],
            {
                "extent_only": True,
                "terminal_digest_only": True,
                "ordered_record_ids": True,
                "ordered_record_ids_commit_indices": True,
                "ordered_record_digests": True,
                "ordered_commit_index_digest": True,
                "five_field_prefix_identity": True,
                "full_canonical_prior_records": True,
            },
        )
        self.assertTrue(matrix["H16_extension"]["ordered_record_digests"])
        self.assertFalse(matrix["H16_ID_replacement"]["ordered_record_digests"])
        self.assertFalse(matrix["H16_content_replacement"]["ordered_record_digests"])

    def test_content_replacement_preserves_ids_and_indices_but_breaks_digest_identity(self) -> None:
        matrix = self.report["capability_matrix"]
        mutation = self.report["h16_content_replacement_mutation"]

        self.assertTrue(mutation["record_ids_preserved"])
        self.assertTrue(mutation["commit_indices_preserved"])
        self.assertTrue(mutation["digest_recomputed"])
        self.assertTrue(matrix["H16_content_replacement"]["ordered_record_ids"])
        self.assertTrue(matrix["H16_content_replacement"]["ordered_record_ids_commit_indices"])
        self.assertFalse(matrix["H16_content_replacement"]["ordered_record_digests"])

    def test_terminal_digest_does_not_commit_to_prefix(self) -> None:
        matrix = self.report["capability_matrix"]

        self.assertTrue(matrix["H16_ID_replacement"]["terminal_digest_only"])
        self.assertTrue(matrix["H16_content_replacement"]["terminal_digest_only"])
        self.assertFalse(self.report["projection_findings"]["terminal_digest_only"]["sufficient_in_bounded_pressure"])

    def test_ordered_digests_are_smallest_sufficient_tested_projection(self) -> None:
        matrix = self.report["capability_matrix"]

        observed = {name: matrix[name]["ordered_record_digests"] for name in EXPECTED_CAPABILITY}
        self.assertEqual(observed, EXPECTED_CAPABILITY)
        self.assertEqual(self.report["smallest_sufficient_tested_projection"], "ordered_record_digests")
        self.assertFalse(
            self.report["projection_findings"]["ordered_record_ids_commit_indices"][
                "sufficient_in_bounded_pressure"
            ]
        )

    def test_commit_indices_do_not_add_discriminating_power_over_ordered_digests(self) -> None:
        matrix = self.report["capability_matrix"]

        digest_pattern = {name: result["ordered_record_digests"] for name, result in matrix.items()}
        index_digest_pattern = {name: result["ordered_commit_index_digest"] for name, result in matrix.items()}
        self.assertEqual(digest_pattern, index_digest_pattern)

    def test_content_replacement_can_leave_derived_shape_unchanged(self) -> None:
        extension_state = self.report["specimens"]["H16_extension"]["derived_state"]
        content_replacement_state = self.report["specimens"]["H16_content_replacement"]["derived_state"]

        self.assertEqual(extension_state, content_replacement_state)
        self.assertTrue(self.report["historical_identity_difference_without_derived_shape_change"])

    def test_no_witness_architecture_added(self) -> None:
        self.assertFalse(self.report["new_persistent_witness_architecture_required"])
        self.assertEqual(self.report["persistent_architecture_added"], [])


if __name__ == "__main__":
    unittest.main()
