from __future__ import annotations

import json
import subprocess
import unittest

from src.runtime.intra_capture_timing_skew_pressure import (
    ALPHA_SHA256,
    BETA_SHA256,
    STARTING_HEAD,
    run,
)


class IntraCaptureTimingSkewPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.specimens = cls.report["specimens"]
        cls.matrix = cls.report["comparison_matrix"]

    def test_starting_lineage_and_baselines_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "Pre-goblin capstone Super Tetaroni")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(
            self.report["baseline_tests"]["targeted"], {"passed": 50, "failed": 0}
        )
        self.assertEqual(
            self.report["baseline_tests"]["full"], {"passed": 326, "failed": 0}
        )

    def test_intervention_is_deterministic_and_experiment_local(self) -> None:
        timing = self.report["timing_intervention"]
        self.assertEqual(
            timing["deterministic_boundary"], "after filesystem return and before Git call"
        )
        self.assertFalse(timing["arbitrary_sleep"])
        self.assertFalse(timing["race_based"])
        self.assertFalse(timing["mutation_owned_by_production_coordinator"])
        self.assertFalse(timing["production_capture_code_modified"])
        for name in ("S1", "S2"):
            intervention = self.specimens[name]["intervention"]
            self.assertTrue(intervention["intercepted"])
            self.assertTrue(intervention["filesystem_returned_before_driver"])

    def test_fixture_configuration_hashes_are_exact(self) -> None:
        self.assertEqual(self.specimens["C0"]["filesystem"]["state_txt_sha256"], ALPHA_SHA256)
        self.assertEqual(self.specimens["S1"]["filesystem"]["state_txt_sha256"], ALPHA_SHA256)
        self.assertEqual(self.specimens["S2"]["filesystem"]["state_txt_sha256"], ALPHA_SHA256)
        self.assertEqual(self.specimens["C1"]["filesystem"]["state_txt_sha256"], BETA_SHA256)

    def test_C0_is_stable_clean_alpha_control(self) -> None:
        specimen = self.specimens["C0"]
        self.assertEqual(specimen["filesystem"]["configuration"], "alpha")
        self.assertEqual(specimen["git"]["configuration"], "clean alpha")
        self.assertFalse(specimen["ground_truth"]["mutation_between_acquisitions"])
        self.assertTrue(specimen["ground_truth"]["shared_world_configuration"])

    def test_S1_is_dirty_working_tree_skew(self) -> None:
        specimen = self.specimens["S1"]
        self.assertEqual(specimen["filesystem"]["configuration"], "alpha")
        self.assertEqual(specimen["git"]["configuration"], "dirty later state over alpha HEAD")
        self.assertTrue(specimen["git"]["status_porcelain"])
        self.assertTrue(specimen["ground_truth"]["mutation_between_acquisitions"])
        self.assertFalse(specimen["ground_truth"]["shared_world_configuration"])

    def test_S2_is_committed_beta_skew(self) -> None:
        specimen = self.specimens["S2"]
        self.assertEqual(specimen["filesystem"]["configuration"], "alpha")
        self.assertEqual(specimen["git"]["configuration"], "clean committed beta")
        self.assertEqual(specimen["git"]["status_porcelain"], [])
        self.assertEqual(
            specimen["git"]["head_sha"], specimen["intervention"]["post_action_head"]
        )
        self.assertTrue(specimen["ground_truth"]["mutation_between_acquisitions"])
        self.assertFalse(specimen["ground_truth"]["shared_world_configuration"])

    def test_C1_is_fresh_post_skew_beta_control(self) -> None:
        specimen = self.specimens["C1"]
        self.assertEqual(specimen["filesystem"]["configuration"], "beta")
        self.assertEqual(specimen["git"]["configuration"], "clean committed beta")
        self.assertFalse(specimen["ground_truth"]["mutation_between_acquisitions"])
        self.assertTrue(specimen["ground_truth"]["shared_world_configuration"])
        self.assertEqual(
            specimen["git"]["head_sha"], self.specimens["S2"]["git"]["head_sha"]
        )

    def test_driver_ground_truth_is_not_promoted_to_DME_knowledge(self) -> None:
        for specimen in self.specimens.values():
            self.assertFalse(specimen["ground_truth"]["transferred_into_DME_history"])
            self.assertEqual(specimen["DME_knowledge"]["mutation_between_acquisitions"], "UNRESOLVED")
            self.assertEqual(specimen["DME_knowledge"]["same_world_configuration"], "UNRESOLVED")
            self.assertFalse(specimen["DME_knowledge"]["global_snapshot_claim"])

    def test_every_source_observation_is_individually_valid(self) -> None:
        for specimen in self.specimens.values():
            self.assertEqual(specimen["filesystem"]["capture_errors"], [])
            self.assertEqual(specimen["git"]["capture_errors"], [])
            self.assertTrue(specimen["DME_knowledge"]["individual_source_observations_valid"])

    def test_every_composition_is_structurally_healthy(self) -> None:
        for specimen in self.specimens.values():
            health = specimen["health"]
            self.assertTrue(health["integrity_ok"])
            self.assertTrue(health["continuity_ok"])
            self.assertTrue(health["replay_reproducible"])
            self.assertTrue(health["reconstruction_reproducible"])
            self.assertTrue(health["projection_reproducible"])
            self.assertTrue(health["companion_reproducible"])
            self.assertTrue(health["structurally_healthy"])

    def test_each_capture_admits_and_projects_both_source_observations(self) -> None:
        expected = {"C0": 2, "S1": 2, "S2": 2, "C1": 4}
        for name, total in expected.items():
            health = self.specimens[name]["health"]
            self.assertEqual(health["observation_count"], total)
            self.assertEqual(health["admission_relation_count"], total)
            self.assertEqual(health["projection_subject_count"], total)

    def test_chart_11_companion_remains_empty_state_per_projected_subject(self) -> None:
        for specimen in self.specimens.values():
            health = specimen["health"]
            self.assertEqual(health["companion_count"], health["projection_subject_count"])
            self.assertTrue(all(states == [] for states in health["companion_states"]))

    def test_source_separation_survives_every_skew_and_control(self) -> None:
        for specimen in self.specimens.values():
            self.assertTrue(specimen["health"]["source_separation"])
        projection = self.report["projection_audit"]
        self.assertTrue(projection["preserves_admitted_observations_as_separate_subjects"])
        self.assertFalse(projection["silently_fuses_sources"])

    def test_immediate_result_groups_sources_only_process_locally(self) -> None:
        for specimen in self.specimens.values():
            immediate = specimen["immediate"]
            self.assertTrue(immediate["capture_returned"])
            self.assertTrue(immediate["same_invocation"])
            self.assertTrue(immediate["same_acquisition_episode"])
            self.assertTrue(immediate["captured_observations_grouped_on_return"])

    def test_fresh_recovery_is_read_only_and_loses_invocation_grouping(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            self.assertTrue(recovery["read_only"])
            self.assertFalse(recovery["captured_observations_available"])
            self.assertEqual(recovery["durable_grouping_fields"], [])
            self.assertEqual(recovery["same_invocation_from_history"], "UNRESOLVED")

    def test_commit_coordinates_do_not_supply_durable_round_identity(self) -> None:
        for name in ("C0", "S1", "S2"):
            self.assertEqual(self.specimens[name]["immediate"]["commit_indices"], [1, 2, 3, 4])
        self.assertEqual(self.specimens["C1"]["immediate"]["commit_indices"], [5, 6, 7, 8])
        self.assertFalse(
            self.report["together_audit"]["adjacent_commit_indices_license_simultaneity"]
        )

    def test_recorded_timestamp_order_survives_recovery(self) -> None:
        temporal = self.report["temporal_audit"]
        self.assertTrue(temporal["fields_persist_in_observation_payload_and_provenance"])
        self.assertTrue(temporal["recorded_timestamp_order_recoverable"])
        for specimen in self.specimens.values():
            self.assertTrue(
                specimen["temporal_evidence"]["filesystem_finished_before_git_observed"]
            )

    def test_existing_timing_cannot_establish_full_non_overlap_or_simultaneity(self) -> None:
        temporal = self.report["temporal_audit"]
        self.assertFalse(temporal["complete_interval_non_overlap_recoverable"])
        self.assertFalse(temporal["simultaneity_recoverable"])
        self.assertFalse(temporal["shared_world_configuration_recoverable"])
        self.assertFalse(temporal["clock_identity_or_precision_recorded"])

    def test_same_invocation_does_not_license_same_world_configuration(self) -> None:
        audit = self.report["together_audit"]
        self.assertTrue(audit["same_invocation_process_local"])
        self.assertEqual(audit["same_durable_historical_group"], "UNRESOLVED")
        self.assertEqual(audit["same_world_configuration_from_DME_evidence"], "UNRESOLVED")
        self.assertFalse(audit["same_invocation_licenses_same_world_configuration"])

    def test_projection_makes_no_temporal_or_current_world_claim(self) -> None:
        projection = self.report["projection_audit"]
        self.assertFalse(projection["claims_simultaneity"])
        self.assertFalse(projection["claims_current_coherent_repository_state"])
        self.assertFalse(projection["projection_redesigned"])

    def test_information_boundary_distinguishes_evidence_from_grouping(self) -> None:
        boundary = self.report["information_boundary"]
        self.assertFalse(boundary["source_observation_content_lost_on_recovery"])
        self.assertFalse(boundary["source_timing_fields_lost_on_recovery"])
        self.assertTrue(boundary["process_local_invocation_association_lost_on_recovery"])
        self.assertFalse(boundary["external_driver_mutation_fact_durable"])
        self.assertFalse(boundary["loss_is_corruption"])

    def test_chart_15_and_D0044_are_earned(self) -> None:
        chart = self.report["chart_status"]
        self.assertTrue(chart["earned"])
        self.assertEqual(chart["name"], "Chart 15")
        self.assertFalse(chart["generalized_temporal_or_world_state_model"])
        self.assertEqual(
            self.report["distinctions"]["added"],
            [
                {
                    "id": "D-0044",
                    "left": "same_capture_invocation",
                    "relation": "not_equivalent_to",
                    "right": "same_world_configuration",
                }
            ],
        )

    def test_D0044_is_registered_from_executed_evidence(self) -> None:
        with open("docs/constraints/registry.jsonl", encoding="utf-8") as registry:
            entries = [json.loads(line) for line in registry if line.strip()]
        distinction = next(entry for entry in entries if entry["id"] == "D-0044")
        self.assertEqual(distinction["id"], "D-0044")
        self.assertEqual(distinction["left"], "same_capture_invocation")
        self.assertEqual(distinction["right"], "same_world_configuration")
        self.assertEqual(distinction["standing"], "supported")

    def test_epistemic_audit_makes_no_forbidden_inference(self) -> None:
        self.assertTrue(all(value is False for value in self.report["epistemic_audit"].values()))

    def test_prior_findings_and_production_boundary_are_preserved(self) -> None:
        prior = self.report["prior_findings"]
        self.assertTrue(prior["D_0042_preserved"])
        self.assertTrue(prior["D_0043_preserved"])
        self.assertTrue(prior["partial_round_findings_preserved"])
        self.assertEqual(prior["invalidated"], [])
        production = self.report["production_boundary"]
        self.assertEqual(production["status"], "PRESERVED_WITH_SCOPED_GUARANTEE")
        self.assertFalse(production["atomic_or_global_snapshot_guarantee"])
        self.assertFalse(production["production_change_made"])
        changed = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                STARTING_HEAD,
                "--",
                "src/runtime/foreground_repository_observation.py",
                "src/capture/repo_snapshot.py",
                "src/capture/git_state.py",
            ],
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])

    def test_canonical_history_is_untouched(self) -> None:
        committed = subprocess.check_output(
            ["git", "show", f"{STARTING_HEAD}:traces/live_ingest_ledger_v0.jsonl"]
        )
        with open("traces/live_ingest_ledger_v0.jsonl", "rb") as current_file:
            current = current_file.read()
        self.assertEqual(current.splitlines(), committed.splitlines())
        canonical = self.report["canonical_history"]
        self.assertTrue(canonical["unchanged"])
        self.assertEqual(canonical["sha256_before"], canonical["sha256_after"])


if __name__ == "__main__":
    unittest.main()
