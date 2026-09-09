from __future__ import annotations

import json
import subprocess
import unittest

from src.runtime.stale_current_result_pressure import (
    ALPHA_SHA256,
    BETA_SHA256,
    STARTING_HEAD,
    run,
)


class StaleCurrentResultPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.specimens = cls.report["specimens"]

    def test_starting_lineage_and_baselines_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "Wound 2")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(
            self.report["baseline_tests"]["targeted"], {"passed": 76, "failed": 0}
        )
        self.assertEqual(
            self.report["baseline_tests"]["full"], {"passed": 352, "failed": 0}
        )

    def test_fixture_is_bounded_without_sleep_or_round_trip(self) -> None:
        fixture = self.report["fixture_control"]
        self.assertEqual(fixture["independent_fixtures"], ["C0", "S1/F1", "S2/R1"])
        self.assertFalse(fixture["arbitrary_sleep"])
        self.assertFalse(fixture["round_trip_mutation"])
        self.assertFalse(fixture["mutation_written_to_DME_history_before_recapture"])

    def test_C0_stays_alpha_by_external_control(self) -> None:
        specimen = self.specimens["C0"]
        self.assertEqual(
            specimen["last_captured_evidence"]["filesystem"]["state_txt_sha256"],
            ALPHA_SHA256,
        )
        self.assertEqual(specimen["external_control"]["state_txt_sha256"], ALPHA_SHA256)
        self.assertFalse(specimen["external_control"]["differs_from_last_captured"])
        self.assertTrue(specimen["ground_truth"]["source_matches_last_recorded_at_read"])

    def test_S1_is_dirty_beta_over_clean_alpha_history(self) -> None:
        specimen = self.specimens["S1"]
        self.assertEqual(
            specimen["last_captured_evidence"]["filesystem"]["configuration"], "alpha"
        )
        self.assertEqual(specimen["last_captured_evidence"]["git"]["status_porcelain"], [])
        self.assertEqual(specimen["external_control"]["state_txt_sha256"], BETA_SHA256)
        self.assertEqual(specimen["external_control"]["git_configuration"], "dirty")
        self.assertTrue(specimen["external_control"]["differs_from_last_captured"])

    def test_S2_is_committed_beta_over_clean_alpha_history(self) -> None:
        specimen = self.specimens["S2"]
        last = specimen["last_captured_evidence"]
        external = specimen["external_control"]
        self.assertEqual(last["filesystem"]["configuration"], "alpha")
        self.assertEqual(external["filesystem_configuration"], "beta")
        self.assertEqual(external["git_configuration"], "clean")
        self.assertNotEqual(external["head_sha"], last["git"]["head_sha"])
        self.assertTrue(external["filesystem_differs_from_last_captured"])
        self.assertTrue(external["git_differs_from_last_captured"])

    def test_every_current_result_call_is_byte_and_history_conserving(self) -> None:
        for specimen in self.specimens.values():
            read = specimen["read"]
            self.assertTrue(read["append_free"], specimen["name"])
            self.assertEqual(read["ledger_sha256_before"], read["ledger_sha256_after"])
            self.assertEqual(read["record_count_before"], read["record_count_after"])
            self.assertEqual(read["commit_indices_before"], read["commit_indices_after"])
            self.assertEqual(read["ordered_digests_before"], read["ordered_digests_after"])

    def test_stale_reads_exactly_match_last_captured_historical_surface(self) -> None:
        for name in ("S1", "S2", "R1"):
            self.assertTrue(
                self.specimens[name]["read"]["historical_surface_matches_last_capture"]
            )
        comparison = self.report["critical_comparison"]
        self.assertTrue(comparison["S1_last_capture_equals_current_result_history"])
        self.assertTrue(comparison["S2_last_capture_equals_current_result_history"])
        self.assertFalse(comparison["classified_as_corrupt_or_incorrect_history"])

    def test_external_control_knowledge_is_not_transferred_into_history(self) -> None:
        for name in ("C0", "S1", "S2", "R1"):
            specimen = self.specimens[name]
            self.assertFalse(specimen["ground_truth"]["transferred_into_DME_history"])
            self.assertFalse(
                specimen["external_control"]["written_to_DME_history_by_control_read"]
            )

    def test_every_current_result_remains_structurally_healthy(self) -> None:
        for specimen in self.specimens.values():
            self.assertTrue(specimen["read"]["structurally_healthy"], specimen["name"])

    def test_projection_and_reconstruction_do_not_change_during_reads(self) -> None:
        for row in self.report["comparison_matrix"]:
            self.assertFalse(row["reconstruction_changed"], row["specimen"])
            self.assertFalse(row["projection_changed"], row["specimen"])
            self.assertFalse(row["companion_changed"], row["specimen"])
            self.assertFalse(row["ledger_changed_by_current_result"], row["specimen"])

    def test_chart_11_companion_remains_empty_state_per_projection_subject(self) -> None:
        for specimen in self.specimens.values():
            surface = specimen["read"]["after"]
            self.assertEqual(surface["companion_count"], surface["projection_count"])
            self.assertTrue(all(states == [] for states in surface["companion_states"]))

    def test_source_separation_survives_staleness_and_recapture(self) -> None:
        for specimen in self.specimens.values():
            sources = specimen["read"]["after"]["source_values"]
            self.assertEqual(
                set(sources),
                {"repository_filesystem_snapshot", "repository_git_state"},
            )

    def test_current_result_does_not_directly_expose_observation_timestamps(self) -> None:
        for specimen in self.specimens.values():
            self.assertEqual(specimen["read"]["direct_observation_timing_keys"], [])
        freshness = self.report["freshness_evidence"]
        self.assertFalse(freshness["current_result_exposes_observation_timestamps_directly"])
        self.assertFalse(freshness["age_exposed_by_current_result"])

    def test_observation_timestamps_are_recoverable_from_authoritative_reconstruction(self) -> None:
        for specimen in self.specimens.values():
            evidence = specimen["last_captured_evidence"]
            self.assertTrue(evidence["timestamps_recovered_from_authoritative_reconstruction"])
            self.assertTrue(evidence["filesystem"]["observation_started_at"])
            self.assertTrue(evidence["filesystem"]["observation_finished_at"])
            self.assertTrue(evidence["git"]["observed_at"])
        self.assertTrue(
            self.report["freshness_evidence"][
                "timestamps_recoverable_from_authoritative_reconstruction"
            ]
        )

    def test_age_needs_external_now_and_clock_assumptions(self) -> None:
        freshness = self.report["freshness_evidence"]
        self.assertTrue(freshness["age_computable_with_external_now_and_clock_assumptions"])
        self.assertFalse(freshness["clock_identity_or_precision_contract_recorded"])
        self.assertFalse(freshness["freshness_threshold_added"])

    def test_source_freshness_is_not_recoverable(self) -> None:
        freshness = self.report["freshness_evidence"]
        self.assertFalse(freshness["source_change_since_observation_inferable"])
        self.assertFalse(freshness["method_call_time_adds_world_knowledge"])
        self.assertFalse(freshness["replay_time_adds_world_knowledge"])
        for row in self.report["comparison_matrix"]:
            self.assertFalse(row["external_freshness_inferable_from_result"])

    def test_current_result_introduces_no_observation_or_record(self) -> None:
        for specimen in self.specimens.values():
            read = specimen["read"]
            self.assertIsNone(read["captured_observations"])
            self.assertEqual(read["new_records"], [])
            self.assertFalse(read["world_evidence_introduced"])

    def test_R1_fresh_coordinator_reconstructs_identical_stale_surface(self) -> None:
        comparison = self.specimens["R1"]["reopen_comparison"]
        self.assertTrue(comparison["existing_and_fresh_results_equal"])
        self.assertTrue(comparison["existing_and_fresh_surfaces_equal"])
        self.assertFalse(comparison["process_replacement_changed_freshness"])
        self.assertFalse(
            comparison["reconstruction_or_projection_passed_to_fresh_coordinator"]
        )

    def test_F1_explicit_capture_advances_history(self) -> None:
        recapture = self.specimens["F1"]["recapture"]
        self.assertTrue(recapture["capture_returned"])
        self.assertEqual(recapture["new_commit_indices"], [5, 6, 7, 8])
        self.assertNotEqual(recapture["ledger_sha256_before"], recapture["ledger_sha256_after"])
        self.assertEqual(recapture["record_count_before"], 4)
        self.assertEqual(recapture["record_count_after"], 8)
        self.assertEqual(recapture["observation_count_before"], 2)
        self.assertEqual(recapture["observation_count_after"], 4)
        self.assertEqual(recapture["projection_count_before"], 2)
        self.assertEqual(recapture["projection_count_after"], 4)
        self.assertTrue(recapture["history_advanced"])

    def test_F1_post_capture_current_result_is_again_append_free(self) -> None:
        specimen = self.specimens["F1"]
        self.assertEqual(specimen["last_captured_evidence"]["filesystem"]["configuration"], "beta")
        self.assertEqual(specimen["external_control"]["filesystem_configuration"], "beta")
        self.assertFalse(specimen["external_control"]["differs_from_last_captured"])
        self.assertTrue(specimen["read"]["append_free"])
        self.assertTrue(specimen["read"]["historical_surface_matches_last_capture"])
        self.assertFalse(
            specimen["ground_truth"]["DME_guarantees_continued_equality_after_capture"]
        )

    def test_consumer_can_infer_history_current_but_not_world_current(self) -> None:
        interpretation = self.report["consumer_interpretation"]
        self.assertEqual(
            interpretation["current_DME_derivation_from_recorded_history"], "JUSTIFIED"
        )
        self.assertEqual(
            interpretation["current_external_repository_configuration"], "NOT_JUSTIFIED"
        )
        self.assertEqual(
            interpretation["no_source_change_since_last_observation"], "NOT_JUSTIFIED"
        )
        self.assertEqual(
            interpretation["projection_contains_latest_external_configuration"],
            "NOT_JUSTIFIED",
        )

    def test_production_contract_is_scoped_and_not_renamed(self) -> None:
        contract = self.report["production_contract"]
        self.assertEqual(
            contract["docstring"],
            "Rebuild the current derived state without appending or capturing.",
        )
        self.assertTrue(contract["implementation_matches_docstring"])
        self.assertFalse(contract["world_freshness_claimed"])
        self.assertFalse(contract["overclaimed_freshness"])
        self.assertFalse(contract["renamed"])
        self.assertFalse(contract["production_change_made"])

    def test_unobserved_external_divergence_is_not_information_loss_or_corruption(self) -> None:
        boundary = self.report["information_boundary"]
        self.assertFalse(boundary["authoritative_history_lost"])
        self.assertFalse(boundary["reconstruction_or_projection_information_lost"])
        self.assertFalse(boundary["external_mutation_observed_before_F1"])
        self.assertFalse(boundary["unobserved_external_divergence_present_in_history"])
        self.assertFalse(boundary["absence_is_corruption"])

    def test_chart_16_and_D0045_are_earned(self) -> None:
        chart = self.report["chart_status"]
        self.assertTrue(chart["earned"])
        self.assertEqual(chart["name"], "Chart 16")
        self.assertFalse(chart["freshness_policy_or_latest_state_model"])
        self.assertEqual(
            self.report["distinctions"]["added"],
            [
                {
                    "id": "D-0045",
                    "left": "current_derived_history",
                    "relation": "not_equivalent_to",
                    "right": "current_external_configuration",
                }
            ],
        )

    def test_D0045_is_registered_from_executed_evidence(self) -> None:
        with open("docs/constraints/registry.jsonl", encoding="utf-8") as registry:
            entries = [json.loads(line) for line in registry if line.strip()]
        distinction = next(entry for entry in entries if entry["id"] == "D-0045")
        self.assertEqual(distinction["left"], "current_derived_history")
        self.assertEqual(distinction["right"], "current_external_configuration")
        self.assertEqual(distinction["standing"], "supported")

    def test_D0042_through_D0044_remain_supported(self) -> None:
        prior = self.report["prior_findings"]
        for distinction in ("D_0042", "D_0043", "D_0044"):
            self.assertEqual(prior[distinction], "SUPPORTED_UNCHANGED")
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
