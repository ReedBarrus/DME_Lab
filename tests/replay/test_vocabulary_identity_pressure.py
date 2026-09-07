from __future__ import annotations

import unittest

from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
)
from src.runtime.vocabulary_identity_pressure import run


class VocabularyIdentityPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_ambient_control_reproduces_s9_outcomes(self) -> None:
        self.assertEqual(
            self.report["matrix"]["V0_current_ambient_control"],
            EXPECTED_CORRECT_OUTCOMES,
        )

    def test_tokens_without_interpretation_are_unresolved(self) -> None:
        self.assertEqual(
            set(self.report["matrix"]["V1_tokens_only"].values()),
            {UNRESOLVED},
        )

    def test_correct_explicit_mapping_reproduces_s9_outcomes(self) -> None:
        for regime in (
            "V2_explicit_correct_vocabulary",
            "V2a_mapping_only",
        ):
            with self.subTest(regime=regime):
                self.assertEqual(
                    self.report["matrix"][regime],
                    EXPECTED_CORRECT_OUTCOMES,
                )

    def test_partial_mappings_do_not_inherit_ambient_semantics(self) -> None:
        for regime in (
            "V3a_missing_relation_mapping",
            "V3b_missing_record_id_field_mapping",
            "V3c_missing_serialization_mapping",
            "V3d_missing_algorithm_mapping",
        ):
            with self.subTest(regime=regime):
                self.assertEqual(
                    set(self.report["matrix"][regime].values()),
                    {UNRESOLVED},
                )

    def test_wrong_complete_relation_changes_historical_consequence(self) -> None:
        outcomes = self.report["matrix"]["V4_wrong_complete_relation_mapping"]

        self.assertEqual(outcomes["H14_control"], RECOVERED)
        self.assertEqual(outcomes["H16_extension"], MISMATCHED)
        self.assertNotEqual(outcomes, EXPECTED_CORRECT_OUTCOMES)

    def test_wrong_field_mapping_is_executable_and_mismatched(self) -> None:
        self.assertEqual(
            set(self.report["matrix"]["V5_wrong_field_token_mapping"].values()),
            {MISMATCHED},
        )

    def test_renamed_symbols_with_preserved_mappings_retain_outcomes(self) -> None:
        for regime in (
            "V6_renamed_symbols_preserved_mapping",
            "V7_equivalent_renamed_vocabulary",
        ):
            with self.subTest(regime=regime):
                self.assertEqual(
                    self.report["matrix"][regime],
                    EXPECTED_CORRECT_OUTCOMES,
                )
        renamed = self.report["renamed_token_result"]
        self.assertTrue(renamed["exact_declaration_identity_changed"])
        self.assertTrue(renamed["declaration_shape_identity_preserved"])
        self.assertTrue(renamed["semantic_mapping_preserved"])

    def test_fixed_s9_declaration_structure_survives_all_regimes(self) -> None:
        fixed = self.report["fixed_S9_declaration"]
        shape_identities = {
            regime["declaration_shape_identity"]
            for regime in self.report["vocabulary_regimes"].values()
        }

        self.assertEqual(shape_identities, {fixed["shape_identity"]})
        self.assertEqual(fixed["semantic_component_count"], 10)
        self.assertNotIn("candidate_commitment", fixed["definition"])

    def test_fixed_witness_carrier_is_unchanged(self) -> None:
        carrier = self.report["fixed_witness_carrier"]

        self.assertEqual(carrier["digest_count"], 14)
        self.assertEqual(
            carrier["carrier_identity"],
            "sha256:09f0f5f3402b1f187b3b09e4417f8e12010b22fe0968aeb2841a0b598553c200",
        )

    def test_mapping_only_is_smallest_sufficient_tested_vocabulary(self) -> None:
        smallest = self.report["smallest_sufficient_tested_vocabulary_identity"]
        nearest = self.report["nearest_insufficient_vocabulary_regime"]

        self.assertEqual(smallest["regime"], "V2a_mapping_only")
        self.assertEqual(smallest["mapping_count"], 8)
        self.assertFalse(smallest["vocabulary_identity_metadata_required"])
        self.assertEqual(nearest["selected"], "V3a_missing_relation_mapping")
        self.assertEqual(nearest["mapping_count"], 7)

    def test_chart_5_counts_match_matrix(self) -> None:
        counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
        for outcomes in self.report["matrix"].values():
            for outcome in outcomes.values():
                counts[outcome] += 1

        self.assertEqual(self.report["outcome_counts"], counts)
        self.assertEqual(counts, {RECOVERED: 11, MISMATCHED: 24, UNRESOLVED: 25})

    def test_chart_4_back_pressure_refines_without_invalidating(self) -> None:
        back_pressure = self.report["chart_4_back_pressure"]

        self.assertTrue(back_pressure["necessity_interpretation_refined"])
        self.assertFalse(back_pressure["prior_result_invalidated"])
        self.assertTrue(self.report["chart_fold_pressure"]["supported"])
        self.assertFalse(self.report["chart_fold_pressure"]["folding_machinery_added"])

    def test_residual_interpretation_and_no_architecture_are_explicit(self) -> None:
        self.assertTrue(self.report["remaining_ambient_evaluator_interpretation"])
        self.assertEqual(
            self.report["recursion_limit"],
            "vocabulary interpretation conserved != interpretation eliminated",
        )
        self.assertEqual(self.report["persistent_architecture_added"], [])
        self.assertFalse(
            self.report["cross_chart_correspondence"]["transition_map_implemented"]
        )


if __name__ == "__main__":
    unittest.main()
