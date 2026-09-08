from __future__ import annotations

import subprocess
import unittest

from src.runtime.absent_interval_round_trip_pressure import (
    ALPHA_SHA256,
    BETA_SHA256,
    FIXED_MTIME_NS,
    STARTING_HEAD,
    run,
)


class AbsentIntervalRoundTripPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.specimens = cls.report["specimens"]

    def test_starting_lineage_and_baselines_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "WOund 4")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(
            self.report["baseline_tests"]["targeted"], {"passed": 104, "failed": 0}
        )
        self.assertEqual(
            self.report["baseline_tests"]["full"], {"passed": 380, "failed": 0}
        )

    def test_fixture_is_bounded_and_external(self) -> None:
        fixture = self.report["fixture_control"]
        self.assertEqual(fixture["independent_fixtures"], ["C0", "S1", "S2"])
        self.assertFalse(fixture["capture_during_mutation"])
        self.assertFalse(fixture["intra_capture_skew"])
        self.assertFalse(fixture["driver_path_written_to_ledger"])
        self.assertFalse(fixture["arbitrary_sleep"])

    def test_C0_control_path_contains_no_transformation(self) -> None:
        control = self.specimens["C0"]["control"]
        self.assertEqual(control["path"], ["alpha", "alpha"])
        self.assertFalse(control["transformation_occurred"])
        self.assertEqual(control["mutation"]["state_txt_sha256_after"], ALPHA_SHA256)
        self.assertEqual(control["mutation"]["git_status_after"], [])

    def test_S1_control_proves_hidden_beta_excursion(self) -> None:
        control = self.specimens["S1"]["control"]
        mutation = control["mutation"]
        self.assertEqual(control["path"], ["alpha", "beta", "alpha"])
        self.assertTrue(control["transformation_occurred"])
        self.assertEqual(mutation["beta_control"]["state_txt_sha256"], BETA_SHA256)
        self.assertTrue(mutation["beta_control"]["git_status"])
        self.assertEqual(mutation["restored_state_txt_sha256"], ALPHA_SHA256)
        self.assertEqual(mutation["git_status_after_restore"], [])
        self.assertFalse(control["written_to_DME_history"])

    def test_S1_restores_filesystem_metadata_participating_in_identity(self) -> None:
        mutation = self.specimens["S1"]["control"]["mutation"]
        self.assertEqual(mutation["original_mtime_ns"], FIXED_MTIME_NS)
        self.assertEqual(mutation["restored_mtime_ns"], FIXED_MTIME_NS)

    def test_S2_control_leaves_visible_beta_endpoint(self) -> None:
        control = self.specimens["S2"]["control"]
        self.assertEqual(control["path"], ["alpha", "beta"])
        self.assertTrue(control["transformation_occurred"])
        self.assertEqual(control["mutation"]["state_txt_sha256_after"], BETA_SHA256)
        self.assertTrue(control["mutation"]["git_status_after"])

    def test_C0_filesystem_endpoints_are_exactly_equivalent(self) -> None:
        specimen = self.specimens["C0"]
        self.assertEqual(
            specimen["first_capture"]["filesystem_configuration"],
            specimen["second_capture"]["filesystem_configuration"],
        )
        self.assertTrue(specimen["endpoint_relation"]["filesystem_configuration_equivalent"])

    def test_S1_filesystem_endpoints_are_exactly_equivalent(self) -> None:
        specimen = self.specimens["S1"]
        first = specimen["first_capture"]["filesystem_configuration"]
        second = specimen["second_capture"]["filesystem_configuration"]
        self.assertEqual(first, second)
        self.assertEqual(first["snapshot_id"], second["snapshot_id"])
        self.assertEqual(first["entries"][0]["mtime_ns"], FIXED_MTIME_NS)
        self.assertEqual(first["entries"][0]["sha256"], ALPHA_SHA256)
        self.assertEqual(first["capture_errors"], [])

    def test_C0_and_S1_git_endpoints_are_exactly_equivalent(self) -> None:
        for name in ("C0", "S1"):
            specimen = self.specimens[name]
            self.assertEqual(
                specimen["first_capture"]["git_configuration"],
                specimen["second_capture"]["git_configuration"],
            )
            self.assertTrue(specimen["endpoint_relation"]["git_configuration_equivalent"])
            self.assertTrue(specimen["endpoint_relation"]["both_sources_equivalent"])

    def test_S2_observers_detect_ordinary_endpoint_difference(self) -> None:
        specimen = self.specimens["S2"]
        self.assertFalse(specimen["endpoint_relation"]["filesystem_configuration_equivalent"])
        self.assertFalse(specimen["endpoint_relation"]["git_configuration_equivalent"])
        self.assertFalse(specimen["endpoint_relation"]["both_sources_equivalent"])
        self.assertEqual(
            specimen["DME_interval_claim"],
            "visible endpoint change occurred between captured observations",
        )

    def test_equivalent_filesystem_configuration_reuses_source_and_envelope_identity(self) -> None:
        for name in ("C0", "S1"):
            occurrence = self.specimens[name]["occurrence_relation"]
            self.assertTrue(occurrence["filesystem_source_identity_equal"])
            self.assertTrue(occurrence["filesystem_envelope_identity_equal"])

    def test_visible_filesystem_change_changes_source_and_envelope_identity(self) -> None:
        occurrence = self.specimens["S2"]["occurrence_relation"]
        self.assertFalse(occurrence["filesystem_source_identity_equal"])
        self.assertFalse(occurrence["filesystem_envelope_identity_equal"])

    def test_git_occurrence_identity_changes_even_when_configuration_repeats(self) -> None:
        for specimen in self.specimens.values():
            occurrence = specimen["occurrence_relation"]
            self.assertFalse(occurrence["git_source_identity_equal"])
            self.assertFalse(occurrence["git_envelope_identity_equal"])

    def test_every_second_capture_is_a_distinct_ledger_occurrence(self) -> None:
        for specimen in self.specimens.values():
            occurrence = specimen["occurrence_relation"]
            self.assertTrue(occurrence["filesystem_records_distinct"])
            self.assertTrue(occurrence["git_records_distinct"])
            self.assertTrue(occurrence["commit_indices_distinct"])
            self.assertTrue(occurrence["record_digests_distinct"])
            self.assertTrue(occurrence["distinct_observation_occurrences"])

    def test_capture_timestamps_distinguish_occurrences_not_interval_paths(self) -> None:
        for specimen in self.specimens.values():
            occurrence = specimen["occurrence_relation"]
            self.assertTrue(occurrence["filesystem_capture_times_distinct"])
            self.assertTrue(occurrence["git_capture_times_distinct"])
        self.assertFalse(self.report["inference_audit"]["timestamps_establish_interval_path"])

    def test_every_history_is_integrity_and_continuity_valid(self) -> None:
        for specimen in self.specimens.values():
            health = specimen["health"]
            self.assertTrue(health["integrity_ok"])
            self.assertTrue(health["continuity_ok"])
            self.assertTrue(health["replay_reproducible"])
            self.assertTrue(health["structurally_healthy"])

    def test_every_history_reconstructs_four_admitted_observations(self) -> None:
        for specimen in self.specimens.values():
            health = specimen["health"]
            self.assertEqual(health["record_count"], 8)
            self.assertEqual(health["observation_count"], 4)
            self.assertEqual(health["admission_relation_count"], 4)
            self.assertTrue(health["reconstruction_reproducible"])

    def test_projection_preserves_all_distinct_occurrence_subjects(self) -> None:
        expected = ["rec-000001", "rec-000002", "rec-000005", "rec-000006"]
        for specimen in self.specimens.values():
            health = specimen["health"]
            self.assertTrue(health["projection_reproducible"])
            self.assertEqual(health["projection_count"], 4)
            self.assertEqual(health["projection_subject_ids"], expected)
        projection = self.report["projection_audit"]
        self.assertTrue(projection["preserves_both_occurrences_per_source"])
        self.assertFalse(projection["collapses_repeated_observations"])

    def test_projection_claims_neither_stasis_nor_recurrence(self) -> None:
        projection = self.report["projection_audit"]
        self.assertFalse(projection["claims_stasis"])
        self.assertFalse(projection["claims_recurrence"])
        self.assertFalse(projection["claims_current_coherent_world"])
        self.assertFalse(projection["supersession_or_recurrence_semantics_added"])

    def test_chart_11_companion_remains_empty_state_per_subject(self) -> None:
        for specimen in self.specimens.values():
            health = specimen["health"]
            self.assertTrue(health["companion_reproducible"])
            self.assertEqual(health["companion_count"], 4)
            self.assertEqual(health["companion_states"], [[], [], [], []])

    def test_source_separation_survives_every_specimen(self) -> None:
        for specimen in self.specimens.values():
            self.assertTrue(specimen["health"]["source_separation"])

    def test_fresh_recovery_is_append_free_and_has_no_driver_path(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            self.assertTrue(recovery["fresh_coordinator"])
            self.assertEqual(recovery["inputs"], ["root", "ledger_path"])
            self.assertTrue(recovery["append_free"])
            self.assertEqual(recovery["ledger_sha256_before"], recovery["ledger_sha256_after"])
            self.assertFalse(recovery["driver_path_available"])
            self.assertIsNone(recovery["captured_observations"])

    def test_C0_and_S1_have_equal_captured_configuration_sequences(self) -> None:
        comparison = self.report["C0_S1_comparison"]
        self.assertTrue(comparison["control_paths_differ"])
        self.assertTrue(comparison["captured_filesystem_configuration_sequences_equal"])
        self.assertTrue(comparison["captured_git_configuration_sequences_equal"])
        self.assertTrue(comparison["record_shape_equal"])
        self.assertTrue(comparison["occurrence_multiplicity_equal"])

    def test_C0_and_S1_raw_histories_differ_only_as_independent_occurrences(self) -> None:
        comparison = self.report["C0_S1_comparison"]
        self.assertFalse(comparison["raw_ledger_bytes_equal"])
        self.assertTrue(comparison["ordinary_occurrence_coordinates_and_times_differ"])
        self.assertTrue(comparison["distinguishable_as_occurrence_instances"])
        self.assertFalse(comparison["distinguishable_as_stasis_vs_excursion"])

    def test_DME_cannot_establish_stasis_or_hidden_excursion(self) -> None:
        audit = self.report["inference_audit"]
        self.assertFalse(audit["DME_can_establish_nothing_happened_in_C0_interval"])
        self.assertFalse(audit["DME_can_establish_hidden_excursion_in_S1_interval"])
        self.assertFalse(audit["DME_can_distinguish_C0_stasis_from_S1_excursion"])
        self.assertTrue(
            self.report["C0_S1_comparison"][
                "interval_path_indistinguishable_from_DME_evidence"
            ]
        )

    def test_occurrence_multiplicity_does_not_establish_transformation(self) -> None:
        audit = self.report["inference_audit"]
        self.assertFalse(audit["occurrence_multiplicity_establishes_transformation"])
        self.assertFalse(audit["equal_configuration_implies_recurrence_through_excursion"])
        self.assertFalse(audit["recurrence_implies_hidden_transformation"])

    def test_unobserved_excursion_is_observability_boundary_not_information_loss(self) -> None:
        boundary = self.report["information_boundary"]
        self.assertFalse(boundary["captured_observation_information_lost"])
        self.assertFalse(boundary["unobserved_excursion_present_in_history"])
        self.assertFalse(boundary["absence_caused_by_DME_information_loss"])
        self.assertFalse(boundary["observer_corruption"])

    def test_production_contract_contains_no_no_change_claim(self) -> None:
        contract = self.report["production_contract"]
        self.assertFalse(contract["equivalent_endpoints_claim_no_intervening_transformation"])
        self.assertFalse(contract["production_defect_found"])
        self.assertFalse(contract["production_change_made"])

    def test_chart_17_is_earned_without_recurrence_model(self) -> None:
        chart = self.report["chart_status"]
        self.assertTrue(chart["earned"])
        self.assertEqual(chart["name"], "Chart 17")
        self.assertFalse(chart["recurrence_or_transformation_model"])

    def test_D0012_is_sufficient_and_no_distinction_is_added(self) -> None:
        distinctions = self.report["distinctions"]
        self.assertEqual(distinctions["added"], [])
        self.assertEqual(distinctions["amended"], [])
        self.assertEqual(
            distinctions["existing_sufficient"],
            "D-0012 snapshot != complete_transformation_history",
        )
        self.assertEqual(self.report["prior_findings"]["D_0012"], "SUPPORTED_AND_SUFFICIENT")

    def test_D0042_through_D0045_remain_supported(self) -> None:
        prior = self.report["prior_findings"]
        for identifier in ("D_0042", "D_0043", "D_0044", "D_0045"):
            self.assertEqual(prior[identifier], "SUPPORTED_UNCHANGED")
        self.assertEqual(prior["invalidated"], [])

    def test_epistemic_audit_makes_no_forbidden_inference(self) -> None:
        self.assertTrue(all(value is False for value in self.report["epistemic_audit"].values()))

    def test_production_code_and_canonical_history_are_untouched(self) -> None:
        paths = (
            "src/runtime/foreground_repository_observation.py",
            "src/capture/repo_snapshot.py",
            "src/capture/git_state.py",
            "docs/projection/Persistent_Ecology.md",
            "traces/live_ingest_ledger_v0.jsonl",
        )
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", STARTING_HEAD, "--", *paths], text=True
        ).splitlines()
        self.assertEqual(changed, [])
        canonical = self.report["canonical_history"]
        self.assertTrue(canonical["unchanged"])
        self.assertEqual(canonical["sha256_before"], canonical["sha256_after"])


if __name__ == "__main__":
    unittest.main()
