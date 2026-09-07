from __future__ import annotations

import unittest

from src.runtime.candidate_set_expansion_pressure import (
    _ordered_subsequence,
    run,
)
from src.runtime.operation_identity_pressure import _prefix_alternate_iterative
from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
)


class CandidateSetExpansionPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_chart_6_behavior_reproduces_before_expansion(self) -> None:
        prior = self.report["prior_chart_6"]

        self.assertTrue(prior["reproduced_before_expansion"])
        self.assertFalse(prior["evidence_changed"])

    def test_ordered_subsequence_is_a_separate_executable_implementation(self) -> None:
        realization = self.report["new_realization"]

        self.assertIsNot(_ordered_subsequence, _prefix_alternate_iterative)
        self.assertFalse(realization["aliases_existing_prefix_implementation"])
        self.assertEqual(
            realization["implementation_path"],
            "src.runtime.candidate_set_expansion_pressure._ordered_subsequence",
        )

    def test_ordered_subsequence_accepts_h14_control(self) -> None:
        outputs = self.report["behavioral_cases"]["B0_H14_control_agreement"][
            "candidate_outputs"
        ]

        self.assertTrue(outputs["ordered_subsequence_v1"])

    def test_ordered_subsequence_accepts_h16_extension(self) -> None:
        outputs = self.report["behavioral_cases"]["B1_H16_extension_discriminator"][
            "candidate_outputs"
        ]

        self.assertTrue(outputs["ordered_subsequence_v1"])

    def test_equality_still_rejects_h16_extension(self) -> None:
        outputs = self.report["behavioral_cases"]["B1_H16_extension_discriminator"][
            "candidate_outputs"
        ]

        self.assertFalse(outputs["sequence_equality_v1"])

    def test_b1_no_longer_uniquely_selects_prefix(self) -> None:
        result = self.report["E6_witness_sufficiency_after_expansion"]

        self.assertFalse(result["remains_uniquely_sufficient"])
        self.assertEqual(result["matching_realization_count"], 2)

    def test_ambiguous_behavioral_selection_is_unresolved(self) -> None:
        self.assertEqual(self.report["behavioral_selection_outcome"], UNRESOLVED)

    def test_candidate_order_does_not_break_the_tie(self) -> None:
        normal = self.report["B1_expanded_selection"]
        reversed_order = self.report["B1_reversed_candidate_order_selection"]

        self.assertEqual(normal, reversed_order)
        self.assertFalse(normal["tie_break_used"])

    def test_ordered_subsequence_outcomes_cover_five_existing_specimens(self) -> None:
        outcomes = self.report["direct_historical_outcomes"][
            "ordered_subsequence_v1"
        ]

        self.assertEqual(len(outcomes), 5)
        self.assertEqual(outcomes, EXPECTED_CORRECT_OUTCOMES)

    def test_prefix_and_subsequence_patterns_are_compared_explicitly(self) -> None:
        comparison = self.report["prefix_ordered_subsequence_comparison"]

        self.assertFalse(comparison["complete_patterns_differ"])
        self.assertIsNone(comparison["first_differing_existing_specimen"])
        self.assertFalse(comparison["universal_behavioral_equivalence_claimed"])

    def test_candidate_set_dependency_is_executable_evidence(self) -> None:
        result = self.report["candidate_set_dependency"]

        self.assertTrue(result["demonstrated"])
        self.assertEqual(result["original_match_count"], 1)
        self.assertEqual(result["expanded_match_count"], 2)

    def test_fixed_surfaces_remain_unchanged(self) -> None:
        fixed = self.report["fixed_surfaces"]

        self.assertEqual(
            fixed["carrier"]["identity"],
            "sha256:09f0f5f3402b1f187b3b09e4417f8e12010b22fe0968aeb2841a0b598553c200",
        )
        self.assertEqual(
            fixed["S9_declaration"]["identity"],
            "sha256:887a849a8a766c69745ee66051261798a2af0f077267a521f371144aff48128d",
        )
        self.assertEqual(fixed["V2a_mapping_only_vocabulary"]["mapping_count"], 8)
        self.assertEqual(fixed["behavioral_case_ids"], [
            "B0_H14_control_agreement",
            "B1_H16_extension_discriminator",
        ])
        self.assertFalse(fixed["canonical_history_changed"])

    def test_d_0037_remains_supported(self) -> None:
        self.assertTrue(self.report["prior_chart_6"]["D_0037_remains_supported"])
        self.assertEqual(
            self.report["direct_historical_outcomes"][
                "alternate_iterative_prefix_v1"
            ],
            EXPECTED_CORRECT_OUTCOMES,
        )
        self.assertEqual(
            self.report["direct_historical_outcomes"]["sequence_equality_v1"][
                "H16_extension"
            ],
            MISMATCHED,
        )

    def test_no_scheduler_registry_or_generalized_architecture_is_added(self) -> None:
        scheduler = self.report["scheduler_relevance"]

        self.assertTrue(scheduler["operation_recognition_must_preserve_ambiguity"])
        self.assertFalse(scheduler["scheduler_added"])
        self.assertFalse(scheduler["schedulable_primitive_established"])
        self.assertEqual(self.report["architecture_added"], [])

    def test_chart_6_back_pressure_is_refinement_not_invalidation(self) -> None:
        back_pressure = self.report["chart_6_back_pressure"]

        self.assertTrue(back_pressure["interpretation_refined"])
        self.assertFalse(back_pressure["prior_result_invalidated"])
        self.assertTrue(back_pressure["prior_evidence_preserved"])

    def test_behavior_outputs_and_outcome_vocabulary_are_expected(self) -> None:
        b0 = self.report["behavioral_cases"]["B0_H14_control_agreement"]
        b1 = self.report["behavioral_cases"]["B1_H16_extension_discriminator"]

        self.assertEqual(set(b0["candidate_outputs"].values()), {True})
        self.assertEqual(sum(b1["candidate_outputs"].values()), 2)
        self.assertEqual(
            set(
                self.report["direct_historical_outcomes"][
                    "ordered_subsequence_v1"
                ].values()
            ),
            {RECOVERED, MISMATCHED},
        )


if __name__ == "__main__":
    unittest.main()
