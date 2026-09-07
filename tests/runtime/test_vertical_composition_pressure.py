from __future__ import annotations

import subprocess
import unittest

from src.runtime.provenance_recovery_pressure import MISMATCHED, RECOVERED, UNRESOLVED
from src.runtime.vertical_composition_pressure import (
    STARTING_HEAD,
    STRUCTURALLY_SUCCESSFUL,
    run,
)


class VerticalCompositionPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()

    def test_prior_tie_order_invariance_evidence_reproduces_unchanged(self) -> None:
        lineage = self.report["prior_lineage"]
        self.assertTrue(lineage["tie_order_invariance_reproduced"])
        self.assertTrue(lineage["chart_9_preserved"])
        self.assertTrue(lineage["D_0040_preserved"])

    def test_filesystem_and_git_capture_remain_separate_sources(self) -> None:
        separation = self.report["source_provenance_separation"]
        self.assertTrue(separation["separate_sources"])
        self.assertFalse(separation["equivalence_claimed"])
        self.assertFalse(separation["source_identity_collapsed"])

    def test_phase_a_clean_stack_passes_integrity_and_continuity(self) -> None:
        phase = self.report["phase_a"]
        self.assertTrue(phase["integrity"]["ok"])
        self.assertTrue(phase["continuity"]["ok"])

    def test_phase_a_reconstruction_is_deterministic(self) -> None:
        phase = self.report["phase_a"]
        self.assertTrue(phase["reconstruction_reproducible"])
        self.assertEqual(phase["reconstruction_status"], STRUCTURALLY_SUCCESSFUL)

    def test_phase_a_projection_is_reproducible(self) -> None:
        phase = self.report["phase_a"]
        self.assertTrue(phase["projection_reproducible"])
        self.assertEqual(phase["derived_state"]["projection_subject_count"], 2)

    def test_legitimate_phase_b_extension_preserves_phase_a_witness(self) -> None:
        relation = self.report["phase_b"]["historical_relation"]
        self.assertEqual(relation["outcome"], RECOVERED)

    def test_source_provenance_survives_reconstruction(self) -> None:
        observations = self.report["phase_b"]["reconstruction"]["observations"]
        self.assertEqual(len(observations), 4)
        self.assertTrue(
            all("source_envelope_identity" in item["provenance"] for item in observations)
        )
        self.assertEqual(
            self.report["source_provenance_separation"]["unique_provenance_identity_count"],
            4,
        )

    def test_conflicting_admissions_both_survive_reconstruction(self) -> None:
        pressure = self.report["conflicting_admission_pressure"]
        self.assertEqual(
            [item["decision"] for item in pressure["admission_evidence"]],
            ["admitted", "rejected"],
        )
        self.assertTrue(pressure["conflict_visible_in_reconstruction"])

    def test_projection_behavior_under_conflict_is_exact(self) -> None:
        pressure = self.report["conflicting_admission_pressure"]
        self.assertTrue(pressure["projection_member"])
        self.assertEqual(len(pressure["projected_admission_record_ids"]), 1)
        self.assertNotIn(
            pressure["conflict_record_id"], pressure["projected_admission_record_ids"]
        )

    def test_projection_does_not_preserve_conflict_information(self) -> None:
        pressure = self.report["conflicting_admission_pressure"]
        self.assertFalse(pressure["conflict_visible_in_projection"])
        self.assertIn("does not expose", pressure["finding"])

    def test_no_conflict_resolution_policy_is_invented(self) -> None:
        pressure = self.report["conflicting_admission_pressure"]
        self.assertIsNone(pressure["resolution_policy"])

    def test_integrity_valid_mutation_passes_record_integrity(self) -> None:
        mutation = self.report["historical_mutation_pressure"]
        self.assertTrue(mutation["digest_changed"])
        self.assertTrue(mutation["integrity"]["ok"])

    def test_integrity_valid_mutation_passes_continuity(self) -> None:
        mutation = self.report["historical_mutation_pressure"]
        self.assertTrue(mutation["continuity"]["ok"])
        self.assertFalse(mutation["record_id_changed"])
        self.assertFalse(mutation["commit_index_changed"])
        self.assertFalse(mutation["record_count_changed"])

    def test_phase_a_witness_detects_mutation(self) -> None:
        relation = self.report["historical_mutation_pressure"]["historical_relation"]
        self.assertEqual(relation["outcome"], MISMATCHED)
        self.assertEqual(relation["first_mismatch"]["position"], 1)

    def test_mutated_reconstruction_and_projection_are_independent(self) -> None:
        mutation = self.report["historical_mutation_pressure"]
        self.assertEqual(mutation["reconstruction_status"], STRUCTURALLY_SUCCESSFUL)
        self.assertTrue(mutation["projection_exactly_preserved"])
        self.assertEqual(mutation["historical_relation"]["outcome"], MISMATCHED)

    def test_successful_reconstruction_cannot_overwrite_historical_mismatch(self) -> None:
        mutation = self.report["historical_mutation_pressure"]
        self.assertTrue(
            mutation["historical_mismatch_preserved_alongside_reconstruction"]
        )

    def test_unresolved_operation_evidence_never_becomes_unique_certainty(self) -> None:
        pressure = self.report["unresolved_operation_pressure"]
        self.assertEqual(pressure["outcome"], UNRESOLVED)
        self.assertEqual(pressure["matching_realization_count"], 2)
        self.assertIsNone(pressure["unique_operation_identity"])
        self.assertFalse(pressure["certainty_promoted"])

    def test_epistemic_leak_is_recorded_without_policy_claim(self) -> None:
        self.assertEqual(self.report["unjustified_certainty_increases"], [])
        transition = next(
            item
            for item in self.report["epistemic_strength_transitions"]
            if item["boundary"]
            == "opposed admission evidence -> admitted projection"
        )
        self.assertTrue(transition["information_lost"])
        self.assertEqual(
            transition["unsupported_inference_exposed"],
            "projection membership -> uncontested admission",
        )
        self.assertEqual(self.report["distinctions"]["added"][0]["id"], "D-0041")

    def test_prior_scoped_findings_are_not_modified(self) -> None:
        self.assertFalse(
            self.report["prior_lineage"]["charts_4_6_7_8_9_invalidated"]
        )

    def test_canonical_history_is_untouched(self) -> None:
        history = self.report["canonical_history"]
        committed = subprocess.check_output(
            [
                "git",
                "show",
                f"{STARTING_HEAD}:traces/live_ingest_ledger_v0.jsonl",
            ]
        )
        with open("traces/live_ingest_ledger_v0.jsonl", "rb") as current_file:
            current = current_file.read()
        self.assertTrue(history["untouched"])
        self.assertEqual(history["sha256_before"], history["sha256_after"])
        self.assertEqual(current.splitlines(), committed.splitlines())
        self.assertFalse(
            self.report["historical_mutation_pressure"]["canonical_history_mutated"]
        )

    def test_production_contracts_and_implementation_are_untouched(self) -> None:
        changed = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                STARTING_HEAD,
                "--",
                "docs/contracts",
                "src/capture",
                "src/ingest",
                "src/ledger",
                "src/reconstruction",
            ],
            text=True,
            encoding="utf-8",
        ).splitlines()
        self.assertTrue(
            all(not paths for paths in self.report["production_changes"].values())
        )
        self.assertEqual(changed, [])

    def test_no_generalized_architecture_is_added(self) -> None:
        self.assertEqual(self.report["architecture_added"], [])
        self.assertFalse(self.report["duple_interpretation"]["runtime_abstraction_added"])
        self.assertFalse(self.report["consequence_relevance"]["action_selection_added"])

    def test_projection_equivalence_can_hide_historical_consequence(self) -> None:
        self.assertTrue(
            self.report["consequence_relevance"][
                "projection_equivalent_but_historically_distinct"
            ]
        )

    def test_matrix_retains_independent_epistemic_coordinates(self) -> None:
        matrix = self.report["whole_stack_matrix"]
        self.assertEqual(
            matrix["S3_integrity_valid_prior_mutation"]["integrity"], "VALID"
        )
        self.assertEqual(
            matrix["S3_integrity_valid_prior_mutation"]["historical_relation"],
            MISMATCHED,
        )
        self.assertEqual(
            matrix["S4_bounded_unresolved_interpretation"]["operation_recognition"],
            UNRESOLVED,
        )


if __name__ == "__main__":
    unittest.main()
