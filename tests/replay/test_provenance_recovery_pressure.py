from __future__ import annotations

import unittest

from src.runtime.provenance_recovery_pressure import MISMATCHED, RECOVERED, UNRESOLVED, run


class ProvenanceRecoveryPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_current_full_semantics_recover_expected_prefix_distinctions(self) -> None:
        self.assertEqual(
            self.report["matrix"]["H14_control"]["R0_full_current_semantics"],
            RECOVERED,
        )
        self.assertEqual(
            self.report["matrix"]["H16_extension"]["R0_full_current_semantics"],
            RECOVERED,
        )
        self.assertEqual(
            self.report["matrix"]["H13_tail_loss"]["R0_full_current_semantics"],
            MISMATCHED,
        )
        self.assertEqual(
            self.report["matrix"]["H16_ID_replacement"]["R0_full_current_semantics"],
            MISMATCHED,
        )
        self.assertEqual(
            self.report["matrix"]["H16_content_replacement"]["R0_full_current_semantics"],
            MISMATCHED,
        )

    def test_missing_interpretation_yields_unresolved_not_false(self) -> None:
        for history in self.report["matrix"].values():
            self.assertEqual(history["R1_digest_carrier_only"], UNRESOLVED)
            self.assertEqual(history["R2_algorithm_only"], UNRESOLVED)
            self.assertEqual(history["R3_algorithm_boundary_no_canonicalization"], UNRESOLVED)

    def test_wrong_but_complete_interpretation_yields_mismatched(self) -> None:
        for history in self.report["matrix"].values():
            self.assertEqual(history["R7_wrong_boundary"], MISMATCHED)
            self.assertEqual(history["R8_wrong_canonicalization"], MISMATCHED)

    def test_extension_and_content_replacement_split_under_correct_semantics(self) -> None:
        self.assertEqual(
            self.report["matrix"]["H16_extension"]["R6_sufficient_bounded_historical_verifier_semantics"],
            RECOVERED,
        )
        self.assertEqual(
            self.report["matrix"]["H16_content_replacement"][
                "R6_sufficient_bounded_historical_verifier_semantics"
            ],
            MISMATCHED,
        )

    def test_digest_carrier_bytes_remain_fixed_across_regimes(self) -> None:
        carrier = self.report["carrier"]

        self.assertEqual(carrier["name"], "W14_ordered_record_digests")
        self.assertEqual(carrier["digest_count"], 14)
        self.assertFalse(carrier["interpretation_included"])
        self.assertTrue(carrier["carrier_identity"].startswith("sha256:"))

    def test_metadata_drift_does_not_become_authoritative_interpretation(self) -> None:
        drift = self.report["metadata_drift_result"]

        self.assertTrue(drift["current_verify_ok"])
        self.assertEqual(drift["current_verify_failures"], [])
        self.assertEqual(
            drift["finding"],
            "stored integrity metadata does not govern current verifier execution",
        )

    def test_outcome_classifications_match_chart_counts(self) -> None:
        counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
        for regime_results in self.report["matrix"].values():
            for outcome in regime_results.values():
                counts[outcome] += 1

        self.assertEqual(self.report["outcome_counts"], counts)
        self.assertEqual(counts, {RECOVERED: 4, MISMATCHED: 16, UNRESOLVED: 25})

    def test_recomputable_commitment_without_prefix_rule_is_unresolved(self) -> None:
        for history in self.report["matrix"].values():
            self.assertEqual(history["R5_commitment_and_ordering_no_prefix_rule"], UNRESOLVED)
        self.assertTrue(self.report["interpretation_survived_while_historical_relation_unresolved"])

    def test_no_persistent_witness_or_provenance_architecture_added(self) -> None:
        self.assertFalse(self.report["new_persistent_witness_architecture_required"])
        self.assertEqual(self.report["persistent_architecture_added"], [])


if __name__ == "__main__":
    unittest.main()
