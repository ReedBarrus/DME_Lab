from __future__ import annotations

import unittest

from src.runtime.admissible_history_discriminator_pressure import run


class AdmissibleHistoryDiscriminatorPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.constructions = cls.report["attempted_historical_constructions"]

    def test_chart_7_evidence_reproduces_unchanged(self) -> None:
        prior = self.report["prior_chart_7"]

        self.assertTrue(prior["reproduced_unchanged"])
        self.assertFalse(prior["evidence_modified"])
        self.assertTrue(prior["remains_valid"])

    def test_abstract_sequence_distinguishes_relations_only_as_control(self) -> None:
        abstract = self.report["abstract_discriminator"]

        self.assertFalse(abstract["prefix"])
        self.assertTrue(abstract["ordered_subsequence"])
        self.assertTrue(abstract["distinguishes_relations"])
        self.assertFalse(abstract["valid_historical_specimen"])

    def test_duplicate_index_insertion_fails_continuity(self) -> None:
        result = self.constructions["A_duplicate_integer_index"]

        self.assertTrue(result["integrity"]["ok"])
        self.assertFalse(result["continuity"]["ok"])
        self.assertIn(
            {"kind": "duplicate_commit_index", "values": [2]},
            result["continuity"]["failures"],
        )

    def test_non_integer_insertion_fails_continuity(self) -> None:
        result = self.constructions["B_fractional_non_integer_index"]

        self.assertTrue(result["integrity"]["ok"])
        self.assertFalse(result["continuity"]["ok"])
        self.assertIn(
            {"kind": "invalid_commit_index", "values": [1.5]},
            result["continuity"]["failures"],
        )

    def test_shifted_indices_change_commitment_identities(self) -> None:
        preservation = self.constructions["C_shift_subsequent_indices"][
            "witness_digest_preservation"
        ]

        self.assertEqual(preservation["preserved_count"], 1)
        self.assertEqual(preservation["witness_count"], 14)
        self.assertFalse(preservation["all_preserved"])

    def test_shifted_history_fails_exact_h14_subsequence_preservation(self) -> None:
        result = self.constructions["C_shift_subsequent_indices"]

        self.assertTrue(result["integrity"]["ok"])
        self.assertTrue(result["continuity"]["ok"])
        self.assertFalse(result["relations"]["H14_ordered_digest_subsequence"])

    def test_normal_append_preserves_subsequence_and_prefix(self) -> None:
        result = self.constructions["D_normal_append"]

        self.assertTrue(result["integrity"]["ok"])
        self.assertTrue(result["continuity"]["ok"])
        self.assertTrue(result["relations"]["H14_ordered_digest_subsequence"])
        self.assertTrue(result["relations"]["H14_ordered_digest_prefix"])

    def test_no_tested_admissible_construction_is_a_discriminator(self) -> None:
        self.assertFalse(self.report["admissible_discriminator"]["found"])
        self.assertEqual(self.report["admissible_discriminator"]["constructions"], [])
        self.assertFalse(
            any(
                result["admissible_discriminator"]
                for result in self.constructions.values()
            )
        )

    def test_integrity_and_continuity_are_separate_coordinates(self) -> None:
        for name in (
            "A_duplicate_integer_index",
            "B_fractional_non_integer_index",
        ):
            self.assertTrue(self.constructions[name]["integrity"]["ok"])
            self.assertFalse(self.constructions[name]["continuity"]["ok"])

    def test_duplicate_and_fractional_shapes_distinguish_but_are_inadmissible(self) -> None:
        for name in (
            "A_duplicate_integer_index",
            "B_fractional_non_integer_index",
        ):
            result = self.constructions[name]
            self.assertTrue(result["relations"]["distinguishes_relations"])
            self.assertFalse(result["admissible_under_current_bounded_rules"])

    def test_all_constructions_use_current_canonical_order(self) -> None:
        self.assertTrue(
            all(result["ordering"]["ok"] for result in self.constructions.values())
        )

    def test_current_contract_was_not_weakened(self) -> None:
        contract = self.report["current_contract"]

        self.assertEqual(
            contract["digest"]["committed_fields"],
            ["record_id", "commit_index", "envelope"],
        )
        self.assertTrue(contract["continuity"]["require_start_at_one"])
        self.assertFalse(contract["continuity"]["duplicate_commit_indices_allowed"])
        self.assertFalse(contract["continuity"]["missing_internal_commit_indices_allowed"])
        self.assertEqual(contract["validator_modifications"], [])
        self.assertEqual(contract["digest_boundary_modifications"], [])

    def test_contract_induced_equivalence_is_bounded_and_caveated(self) -> None:
        result = self.report["contract_induced_bounded_equivalence"]

        self.assertTrue(result["supported"])
        self.assertTrue(result["strengthened_beyond_existing_specimen_coincidence"])
        self.assertIn("no digest collision is constructed", result["assumptions"])
        self.assertFalse(result["universal_append_only_or_SHA256_theorem_claimed"])

    def test_chart_7_is_refined_not_invalidated(self) -> None:
        back_pressure = self.report["chart_7_back_pressure"]

        self.assertTrue(back_pressure["interpretation_refined"])
        self.assertFalse(back_pressure["prior_result_invalidated"])
        self.assertFalse(back_pressure["prior_trace_modified"])

    def test_no_scheduler_admissibility_or_generalized_architecture_added(self) -> None:
        relevance = self.report["navigation_admissibility_relevance"]

        self.assertTrue(
            relevance[
                "discriminating_pressure_differs_from_admissible_discriminating_pressure"
            ]
        )
        self.assertTrue(relevance["ambiguity_must_be_preserved"])
        self.assertFalse(relevance["tie_breaker_added"])
        self.assertFalse(relevance["scheduler_added"])
        self.assertEqual(self.report["architecture_added"], [])


if __name__ == "__main__":
    unittest.main()
