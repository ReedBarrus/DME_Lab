from __future__ import annotations

import unittest

from src.runtime.operation_identity_pressure import run
from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
)


class OperationIdentityPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_current_evaluator_reproduces_expected_outcomes(self) -> None:
        self.assertEqual(
            self.report["matrix"]["E0_current_evaluator_control"],
            EXPECTED_CORRECT_OUTCOMES,
        )

    def test_descriptor_without_implementation_is_unresolved(self) -> None:
        self.assertEqual(
            set(
                self.report["matrix"][
                    "E1_descriptor_only_implementation_absent"
                ].values()
            ),
            {UNRESOLVED},
        )

    def test_separate_prefix_implementation_reproduces_outcomes(self) -> None:
        result = self.report["equivalent_alternate_implementation_result"]

        self.assertEqual(result["outcomes"], EXPECTED_CORRECT_OUTCOMES)
        self.assertTrue(result["behaviorally_equivalent_under_current_bounded_pressure"])
        self.assertFalse(result["universal_equivalence_claimed"])
        self.assertNotEqual(
            result["implementation_path"],
            self.report["evaluator_regimes"]["E0_current_evaluator_control"][
                "implementation_path"
            ],
        )

    def test_same_descriptor_with_equality_separates_on_extension(self) -> None:
        outcomes = self.report["matrix"][
            "E3_same_descriptor_equality_implementation"
        ]

        self.assertEqual(outcomes["H14_control"], RECOVERED)
        self.assertEqual(outcomes["H16_extension"], MISMATCHED)
        self.assertNotEqual(outcomes, EXPECTED_CORRECT_OUTCOMES)

    def test_renamed_descriptor_with_equivalent_behavior_preserves_outcomes(self) -> None:
        result = self.report["renamed_descriptor_result"]

        self.assertEqual(result["descriptor"], {"kind": "relation_q"})
        self.assertTrue(result["historical_consequence_preserved"])
        self.assertEqual(result["outcomes"], EXPECTED_CORRECT_OUTCOMES)

    def test_h14_alone_is_ambiguous_between_prefix_and_equality(self) -> None:
        result = self.report["H14_prefix_equality_ambiguity"]

        self.assertTrue(result["prefix_result"])
        self.assertTrue(result["equality_result"])
        self.assertFalse(result["distinguishes_candidates"])

    def test_h16_extension_distinguishes_prefix_from_equality(self) -> None:
        result = self.report["H16_extension_discrimination"]

        self.assertTrue(result["prefix_result"])
        self.assertFalse(result["equality_result"])
        self.assertTrue(result["distinguishes_candidates"])

    def test_fixed_carrier_declaration_and_vocabulary_are_unchanged(self) -> None:
        fixed = self.report["fixed_surfaces"]

        self.assertEqual(
            fixed["carrier"]["identity"],
            "sha256:09f0f5f3402b1f187b3b09e4417f8e12010b22fe0968aeb2841a0b598553c200",
        )
        self.assertEqual(
            fixed["S9_declaration"]["identity"],
            "sha256:887a849a8a766c69745ee66051261798a2af0f077267a521f371144aff48128d",
        )
        self.assertEqual(
            fixed["V2a_mapping_only_vocabulary"]["mapping_count"],
            8,
        )
        self.assertNotIn(
            "identity",
            fixed["V2a_mapping_only_vocabulary"]["definition"],
        )

    def test_behavioral_witness_selects_equivalent_prefix_realization(self) -> None:
        regime = "E6_minimal_discriminating_behavioral_witness"
        result = self.report["smallest_sufficient_tested_operation_identity_representation"]

        self.assertEqual(result["regime"], regime)
        self.assertEqual(result["case_count"], 1)
        self.assertEqual(self.report["matrix"][regime], EXPECTED_CORRECT_OUTCOMES)
        self.assertTrue(
            self.report["behavioral_witness_compression"][
                "preserves_tested_operation_discrimination"
            ]
        )

    def test_equal_history_witness_is_nearest_insufficient_case(self) -> None:
        result = self.report["nearest_insufficient_operation_identity_representation"]

        self.assertEqual(result["regime"], "E7_misleading_single_case_witness")
        self.assertEqual(result["case_count"], 1)
        self.assertEqual(
            set(self.report["matrix"][result["regime"]].values()),
            {UNRESOLVED},
        )

    def test_chart_6_counts_match_matrix(self) -> None:
        counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
        for outcomes in self.report["matrix"].values():
            for outcome in outcomes.values():
                counts[outcome] += 1

        self.assertEqual(self.report["outcome_counts"], counts)
        self.assertEqual(counts, {RECOVERED: 9, MISMATCHED: 16, UNRESOLVED: 15})

    def test_chart_5_back_pressure_and_second_fold_are_explicit(self) -> None:
        back_pressure = self.report["chart_5_back_pressure"]

        self.assertTrue(back_pressure["operation_binding_interpretation_refined"])
        self.assertFalse(back_pressure["prior_result_invalidated"])
        self.assertTrue(self.report["chart_fold_pressure"]["second_fold_earned"])
        self.assertFalse(self.report["chart_fold_pressure"]["folding_machinery_added"])

    def test_cross_chart_invariant_and_residual_ambient_layer_are_explicit(self) -> None:
        self.assertTrue(self.report["cross_chart_correspondence"]["outcomes_invariant"])
        self.assertTrue(self.report["remaining_ambient_interpretation"])
        self.assertEqual(
            self.report["strongest_unresolved_horizon"],
            "the one-case witness is sufficient only against the two tested relation realizations",
        )

    def test_no_scheduler_registry_or_other_architecture_is_added(self) -> None:
        relevance = self.report["proto_scheduler_relevance"]

        self.assertTrue(relevance["grounding_strengthened"])
        self.assertFalse(relevance["schedulable_primitive_established"])
        self.assertFalse(relevance["scheduler_added"])
        self.assertEqual(self.report["architecture_added"], [])


if __name__ == "__main__":
    unittest.main()
