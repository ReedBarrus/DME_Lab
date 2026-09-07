from __future__ import annotations

import subprocess
import unittest

from src.runtime.admission_disagreement_exposure_pressure import STARTING_HEAD, run


class AdmissionDisagreementExposurePressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.specimens = cls.report["fixture"]["specimens"]
        cls.matrix = cls.report["candidate_matrix"]

    def test_required_specimens_use_existing_admission_semantics(self) -> None:
        self.assertEqual(self.specimens["S0"]["reconstructed_decisions"], ["admitted"])
        self.assertEqual(
            self.specimens["S1"]["reconstructed_decisions"],
            ["admitted", "rejected"],
        )
        self.assertEqual(
            self.specimens["S2"]["reconstructed_decisions"],
            ["admitted", "unresolved"],
        )
        self.assertEqual(
            self.specimens["S3"]["reconstructed_decisions"],
            ["admitted", "rejected", "unresolved"],
        )
        self.assertEqual(
            self.specimens["S4"]["reconstructed_decisions"],
            ["admitted", "admitted"],
        )

    def test_exclusion_control_does_not_expand_projection(self) -> None:
        self.assertEqual(self.specimens["X0"]["reconstructed_decisions"], ["rejected"])
        self.assertFalse(self.specimens["X0"]["projection_member"])
        self.assertTrue(
            all(not result["expands_projection_membership"] for result in self.matrix.values())
        )

    def test_current_any_admitted_projection_is_exactly_preserved(self) -> None:
        projected = self.report["projection_subject_ids"]
        expected = [self.specimens[name]["observation_record_id"] for name in ("S0", "S1", "S2", "S3", "S4")]
        self.assertEqual(projected, expected)
        self.assertTrue(
            all(result["keeps_projection_unchanged"] for result in self.matrix.values())
        )

    def test_c0_projection_only_fails_disagreement_exposure(self) -> None:
        result = self.matrix["C0_projection_only"]
        self.assertFalse(result["distinguishes_uncontested_from_rejected"])
        self.assertFalse(result["exposes_rejected"])
        self.assertFalse(result["exposes_unresolved"])

    def test_c1_generic_flag_collapses_rejected_unresolved_and_mixed(self) -> None:
        result = self.matrix["C1_generic_disagreement"]
        signatures = result["represented_signatures"]
        self.assertTrue(result["distinguishes_uncontested_from_rejected"])
        self.assertEqual(signatures["S1"], signatures["S2"])
        self.assertEqual(signatures["S2"], signatures["S3"])
        self.assertFalse(result["distinguishes_rejected_unresolved_and_mixed"])

    def test_c2_preserves_required_decision_categories(self) -> None:
        result = self.matrix["C2_unique_non_admitted_decision_states"]
        self.assertTrue(result["exposes_rejected"])
        self.assertTrue(result["exposes_unresolved"])
        self.assertTrue(result["distinguishes_uncontested_from_rejected"])
        self.assertTrue(result["distinguishes_rejected_unresolved_and_mixed"])

    def test_c2_omits_admitted_as_redundant_with_projection_membership(self) -> None:
        rows = self.report["candidate_representations"][
            "C2_unique_non_admitted_decision_states"
        ]
        self.assertTrue(
            all("admitted" not in row["non_admitted_decision_states"] for row in rows)
        )

    def test_c2_outputs_exact_non_admitted_states(self) -> None:
        rows = {
            row["subject_record_id"]: row["non_admitted_decision_states"]
            for row in self.report["candidate_representations"][
                "C2_unique_non_admitted_decision_states"
            ]
        }
        self.assertEqual(rows[self.specimens["S0"]["observation_record_id"]], [])
        self.assertEqual(
            rows[self.specimens["S1"]["observation_record_id"]], ["rejected"]
        )
        self.assertEqual(
            rows[self.specimens["S2"]["observation_record_id"]], ["unresolved"]
        )
        self.assertEqual(
            rows[self.specimens["S3"]["observation_record_id"]],
            ["rejected", "unresolved"],
        )
        self.assertEqual(rows[self.specimens["S4"]["observation_record_id"]], [])

    def test_multiplicity_is_observed_but_not_required(self) -> None:
        self.assertFalse(
            self.matrix["C2_unique_non_admitted_decision_states"][
                "preserves_multiplicity"
            ]
        )
        self.assertTrue(self.matrix["C3_decision_counts"]["preserves_multiplicity"])
        self.assertTrue(
            all(not result["multiplicity_required"] for result in self.matrix.values())
        )

    def test_subject_identity_recovers_full_admission_evidence(self) -> None:
        self.assertTrue(
            all(
                result["evidence_recoverable_via_reconstruction"]
                for result in self.matrix.values()
            )
        )
        self.assertFalse(self.report["evidence_recovery"]["requires_guessing"])
        self.assertFalse(
            self.report["evidence_recovery"]["requires_duplicated_admission_ids"]
        )

    def test_grouped_ids_and_full_evidence_are_not_required(self) -> None:
        self.assertTrue(
            self.matrix["C2_unique_non_admitted_decision_states"][
                "sufficient_for_declared_question"
            ]
        )
        self.assertTrue(
            self.matrix["C4_decision_groups_with_record_ids"][
                "sufficient_for_declared_question"
            ]
        )
        self.assertTrue(
            self.matrix["C5_full_reconstructed_admission_evidence"][
                "duplicates_full_evidence"
            ]
        )

    def test_all_candidates_are_deterministic_and_non_adjudicating(self) -> None:
        self.assertTrue(
            all(result["deterministic"] for result in self.matrix.values())
        )
        self.assertTrue(
            all(not result["adds_resolution"] for result in self.matrix.values())
        )

    def test_candidate_derivation_is_read_only(self) -> None:
        checks = self.report["read_only_checks"]
        self.assertTrue(all(checks.values()))

    def test_c2_is_selected_without_tie_break(self) -> None:
        selection = self.report["selection"]
        self.assertEqual(selection["outcome"], "SELECTED")
        self.assertEqual(
            selection["selected_candidate"],
            "C2_unique_non_admitted_decision_states",
        )
        self.assertFalse(selection["tie_break_used"])

    def test_selected_companion_is_promoted_as_narrow_read_only_derivation(self) -> None:
        promotion = self.report["production_promotion"]
        self.assertTrue(promotion["promoted"])
        self.assertEqual(
            promotion["implementation_path"],
            "src.reconstruction.admission.derive_non_admitted_decision_states",
        )
        self.assertFalse(promotion["projection_membership_changed"])
        self.assertFalse(promotion["authoritative_state_added"])

    def test_canonical_history_and_prior_findings_are_preserved(self) -> None:
        committed = subprocess.check_output(
            [
                "git",
                "show",
                f"{STARTING_HEAD}:traces/live_ingest_ledger_v0.jsonl",
            ]
        )
        with open("traces/live_ingest_ledger_v0.jsonl", "rb") as current_file:
            current = current_file.read()
        self.assertTrue(self.report["canonical_history"]["unchanged"])
        self.assertEqual(current.splitlines(), committed.splitlines())
        self.assertTrue(
            self.report["prior_findings"]["charts_4_6_7_8_9_10_preserved"]
        )
        self.assertTrue(self.report["prior_findings"]["D_0040_preserved"])
        self.assertTrue(self.report["prior_findings"]["D_0041_preserved"])

    def test_no_new_distinction_or_architecture_is_added(self) -> None:
        self.assertEqual(self.report["distinctions"], {"added": [], "amended": []})
        self.assertEqual(self.report["architecture_added"], [])
        self.assertTrue(
            all(not value for value in self.report["epistemic_promotion"].values())
        )


if __name__ == "__main__":
    unittest.main()
