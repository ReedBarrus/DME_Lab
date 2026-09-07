from __future__ import annotations

import unittest

from src.runtime.declarative_commitment_semantics_pressure import run
from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
)


class DeclarativeCommitmentSemanticsPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_full_explicit_semantics_reproduce_chart_3_r6(self) -> None:
        correspondence = self.report["chart_3_R6_correspondence"]

        self.assertTrue(correspondence["S0_reproduces_R6"])
        self.assertEqual(correspondence["S0_outcomes"], EXPECTED_CORRECT_OUTCOMES)

    def test_fixed_witness_carrier_is_unchanged(self) -> None:
        carrier = self.report["witness_carrier"]

        self.assertEqual(carrier["name"], "W14_ordered_record_digests")
        self.assertEqual(carrier["digest_count"], 14)
        self.assertEqual(
            carrier["carrier_identity"],
            "sha256:09f0f5f3402b1f187b3b09e4417f8e12010b22fe0968aeb2841a0b598553c200",
        )
        self.assertFalse(carrier["interpretation_included"])

    def test_each_missing_required_component_is_unresolved(self) -> None:
        reduced = [
            "S1_no_algorithm",
            "S2_no_boundary",
            "S3_no_canonicalization",
            "S3a_no_canonicalization_format",
            "S3b_no_canonicalization_sort_keys",
            "S3c_no_canonicalization_separators",
            "S3d_no_canonicalization_ensure_ascii",
            "S3e_no_canonicalization_encoding",
            "S4_no_ordering",
            "S4a_no_ordering_field",
            "S5_no_relation",
            "S10_no_ordering_direction",
        ]
        for name in reduced:
            with self.subTest(representation=name):
                self.assertEqual(
                    set(self.report["matrix"][name].values()),
                    {UNRESOLVED},
                )

    def test_wrong_but_complete_semantics_are_mismatched(self) -> None:
        for name in (
            "S7_wrong_complete_boundary",
            "S8_wrong_complete_canonicalization",
        ):
            with self.subTest(representation=name):
                self.assertEqual(
                    set(self.report["matrix"][name].values()),
                    {MISMATCHED},
                )

    def test_sufficient_semantics_preserve_extension_and_reject_content_replacement(self) -> None:
        for name in (
            "S0_full_explicit_semantics",
            "S9_no_candidate_commitment_mode",
        ):
            with self.subTest(representation=name):
                self.assertEqual(self.report["matrix"][name]["H16_extension"], RECOVERED)
                self.assertEqual(
                    self.report["matrix"][name]["H16_content_replacement"],
                    MISMATCHED,
                )

    def test_opaque_aliases_are_not_recoverable_descriptions(self) -> None:
        name = "S6_opaque_aliases_only"

        self.assertEqual(set(self.report["matrix"][name].values()), {UNRESOLVED})
        analysis = self.report["representations"][name]["analysis"]
        self.assertEqual(
            analysis["opaque_aliases"],
            {"boundary": "current_record", "canonicalization": "current"},
        )
        self.assertIn(
            "boundary semantic description unavailable; opaque alias supplied",
            analysis["issues"],
        )

    def test_candidate_recomputation_mode_is_redundant_in_bounded_operation(self) -> None:
        full = self.report["matrix"]["S0_full_explicit_semantics"]
        compressed = self.report["matrix"]["S9_no_candidate_commitment_mode"]

        self.assertEqual(compressed, full)
        self.assertEqual(compressed, EXPECTED_CORRECT_OUTCOMES)
        self.assertEqual(
            self.report["smallest_sufficient_tested_representation"],
            "S9_no_candidate_commitment_mode",
        )

    def test_minimality_and_nearest_insufficient_result_are_reproducible(self) -> None:
        smallest = self.report["representations"]["S9_no_candidate_commitment_mode"]
        nearest = self.report["nearest_smaller_insufficient_representation"]

        self.assertEqual(smallest["analysis"]["semantic_component_count"], 10)
        self.assertEqual(nearest["selected"], "S5_no_relation")
        self.assertEqual(nearest["semantic_component_count"], 9)
        self.assertEqual(
            set(self.report["matrix"][nearest["selected"]].values()),
            {UNRESOLVED},
        )

    def test_chart_4_outcome_counts_match_matrix(self) -> None:
        counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
        for outcomes in self.report["matrix"].values():
            for outcome in outcomes.values():
                counts[outcome] += 1

        self.assertEqual(self.report["outcome_counts"], counts)
        self.assertEqual(counts, {RECOVERED: 4, MISMATCHED: 16, UNRESOLVED: 65})

    def test_no_persistent_semantics_or_provenance_architecture_is_added(self) -> None:
        self.assertEqual(self.report["persistent_architecture_added"], [])
        self.assertEqual(
            self.report["declaration_scope"],
            "local in-memory pressure value; no schema or persistence format",
        )
        self.assertFalse(self.report["chart_overlap"]["transition_maps_implemented"])


if __name__ == "__main__":
    unittest.main()
