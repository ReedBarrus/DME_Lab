from __future__ import annotations

from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from src.runtime import ForegroundRepositoryObservationCoordinator as ExportedCoordinator
from src.runtime.foreground_persistent_coordinator_pressure import (
    STARTING_HEAD,
    _initialize_fixture,
    run,
)
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


class ForegroundPersistentCoordinatorPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.calls = {item["call"]: item for item in cls.report["capture_calls"]}

    def test_starting_lineage_and_baseline_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "Observational Persistence")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(self.report["baseline_tests"]["chart_12"], {"passed": 21, "failed": 0})
        self.assertEqual(self.report["baseline_tests"]["full"], {"passed": 276, "failed": 0})

    def test_candidate_is_foreground_explicit_and_non_autonomous(self) -> None:
        candidate = self.report["coordinator_candidate"]
        self.assertTrue(candidate["foreground"])
        self.assertTrue(candidate["explicitly_invoked"])
        self.assertTrue(candidate["single_writer"])
        self.assertFalse(candidate["autonomous"])
        self.assertFalse(candidate["schedules_captures"])
        self.assertFalse(candidate["decides_capture_warrant"])
        self.assertFalse(candidate["world_mutation_capability"])
        self.assertFalse(candidate["knows_future_trajectory"])
        self.assertFalse(candidate["knows_total_round_count"])

    def test_promoted_coordinator_is_exported_from_runtime(self) -> None:
        self.assertIs(ExportedCoordinator, ForegroundRepositoryObservationCoordinator)

    def test_candidate_retains_only_locator_and_lifecycle_state(self) -> None:
        process = self.report["process_local_state"]
        self.assertEqual(process["initial"]["fields"], ["_closed", "ledger_path", "root"])
        self.assertEqual(process["reopened"]["fields"], ["_closed", "ledger_path", "root"])
        self.assertFalse(process["cached_reconstruction"])
        self.assertFalse(process["cached_projection"])
        self.assertFalse(process["cached_last_snapshot"])
        self.assertFalse(process["cached_record_count"])
        self.assertFalse(process["cached_previous_git_state"])
        self.assertFalse(process["cached_round_number"])

    def test_capture_does_not_mutate_fixture_world(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "fixture"
            root.mkdir()
            state_path = root / "state.txt"
            state_path.write_text("alpha", encoding="utf-8")
            head_before = _initialize_fixture(root)
            coordinator = ForegroundRepositoryObservationCoordinator(
                root, Path(tmpdir) / "ledger.jsonl"
            )

            coordinator.capture_round()

            head_after = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
            ).strip()
            status_after = subprocess.check_output(
                ["git", "-C", str(root), "status", "--porcelain=v1"], text=True
            ).strip()
            self.assertEqual(state_path.read_text(encoding="utf-8"), "alpha")
            self.assertEqual(head_after, head_before)
            self.assertEqual(status_after, "")

    def test_external_driver_owns_the_world_sequence(self) -> None:
        self.assertEqual(self.report["fixture"]["trajectory_owner"], "external test driver")
        self.assertEqual(
            self.report["external_world_sequence"],
            [
                "create and commit clean alpha",
                "no mutation",
                "rewrite alpha to beta without commit",
                "add and commit beta without rewriting",
                "destroy coordinator",
                "rewrite beta to gamma while coordinator is absent",
                "open fresh coordinator and capture",
            ],
        )

    def test_five_caller_selected_captures_append_expected_ranges(self) -> None:
        self.assertEqual(list(self.calls), ["C1", "C2", "C3", "C4", "C5"])
        for number, call in enumerate(self.calls.values(), start=1):
            self.assertEqual(call["record_range"], [number * 4 - 3, number * 4])
            self.assertEqual(call["result"]["ledger"]["record_count"], number * 4)
            self.assertIsNone(call["result"]["round_number"])

    def test_each_capture_appends_two_observations_and_normal_admissions(self) -> None:
        for call in self.calls.values():
            records = call["result"]["new_records"]
            self.assertEqual(
                [record["record_type"] for record in records],
                ["observation", "observation", "admission", "admission"],
            )
            self.assertEqual(
                [record["decision"] for record in records[2:]],
                ["admitted", "admitted"],
            )

    def test_repeated_alpha_preserves_configuration_and_new_occurrences(self) -> None:
        comparison = self.report["call_comparisons"]["C1_C2"]
        self.assertTrue(comparison["filesystem_configuration_equal"])
        self.assertTrue(comparison["git_configuration_equal"])
        self.assertFalse(comparison["filesystem_observation_record_equal"])
        self.assertFalse(comparison["git_observation_record_equal"])

    def test_external_beta_mutation_is_observed_without_head_change(self) -> None:
        comparison = self.report["call_comparisons"]["C2_C3"]
        self.assertFalse(comparison["filesystem_configuration_equal"])
        self.assertFalse(comparison["git_configuration_equal"])
        self.assertEqual(self.calls["C2"]["git"]["head_sha"], self.calls["C3"]["git"]["head_sha"])
        self.assertEqual(self.calls["C2"]["git"]["status_porcelain"], [])
        self.assertEqual(self.calls["C3"]["git"]["status_porcelain"], ["M state.txt"])

    def test_external_commit_changes_git_without_file_rewrite(self) -> None:
        comparison = self.report["call_comparisons"]["C3_C4"]
        self.assertTrue(comparison["filesystem_configuration_equal"])
        self.assertFalse(comparison["git_configuration_equal"])
        self.assertNotEqual(self.calls["C3"]["git"]["head_sha"], self.calls["C4"]["git"]["head_sha"])
        self.assertEqual(self.calls["C4"]["git"]["status_porcelain"], [])

    def test_absent_gamma_mutation_is_only_an_endpoint_difference(self) -> None:
        absent = self.report["absent_interval"]
        self.assertEqual(absent["records_appended_while_absent"], 0)
        self.assertTrue(absent["observed_endpoint_difference"])
        self.assertEqual(absent["changed_paths_between_observed_endpoints"], ["state.txt"])
        self.assertEqual(absent["known_intermediate_states"], [])
        self.assertIsNone(absent["known_transition_time"])
        self.assertIsNone(absent["known_transition_mechanism"])
        self.assertEqual(absent["invented_transition_records"], [])

    def test_reopen_recovers_old_field_from_disk_before_capture(self) -> None:
        reopen = self.report["reopen"]
        self.assertTrue(reopen["old_coordinator_destroyed"])
        self.assertTrue(reopen["fresh_coordinator_constructed"])
        self.assertFalse(reopen["reconstruction_or_projection_passed_to_fresh_instance"])
        self.assertEqual(reopen["old_record_count_recovered"], 16)
        self.assertEqual(reopen["old_observation_count_recovered"], 8)
        self.assertEqual(reopen["old_projection_count_recovered"], 8)
        self.assertEqual(reopen["continuation_record_count"], 20)

    def test_only_ledger_history_is_durable_coordinator_state(self) -> None:
        durable = self.report["durable_state"]
        self.assertEqual(durable["required"], ["ledger path", "authoritative ledger contents"])
        self.assertEqual(durable["coordinator_metadata_files"], [])
        self.assertEqual(durable["history_derived_state"], [])
        self.assertTrue(durable["ledger_unchanged_by_absent_world_mutation"])
        self.assertTrue(durable["current_result_is_read_only"])

    def test_integrity_continuity_and_replay_hold_for_every_capture(self) -> None:
        for call in self.calls.values():
            ledger = call["result"]["ledger"]
            self.assertTrue(ledger["integrity_ok"])
            self.assertTrue(ledger["continuity_ok"])
            self.assertTrue(ledger["canonical_replay_reproducible"])
            self.assertEqual(ledger["commit_indices"], list(range(1, ledger["record_count"] + 1)))

    def test_early_prefix_survives_all_external_trajectory_calls(self) -> None:
        prefix = self.report["historical_prefix"]
        self.assertEqual(prefix["witness_record_count"], 4)
        self.assertFalse(prefix["persistent_witness_infrastructure_added"])
        self.assertTrue(all(relation["ok"] for relation in prefix["relations"].values()))

    def test_reconstruction_and_projection_remain_derived_and_reproducible(self) -> None:
        for number, call in enumerate(self.calls.values(), start=1):
            derived = call["result"]["derived"]
            self.assertTrue(derived["reconstruction_reproducible"])
            self.assertTrue(derived["projection_reproducible"])
            self.assertEqual(derived["observation_count"], number * 2)
            self.assertEqual(derived["admission_relation_count"], number * 2)
            self.assertEqual(len(derived["projection"]), number * 2)
            self.assertEqual(derived["orphan_admission_count"], 0)

    def test_chart_11_companion_does_not_gain_multiplicity_or_resolution(self) -> None:
        for number, call in enumerate(self.calls.values(), start=1):
            companion = call["result"]["derived"]["companion"]
            self.assertEqual(len(companion), number * 2)
            self.assertTrue(
                all(item["non_admitted_decision_states"] == [] for item in companion)
            )

    def test_filesystem_and_git_sources_remain_separate(self) -> None:
        self.assertTrue(
            all(
                call["result"]["derived"]["source_provenance_separate"]
                for call in self.calls.values()
            )
        )

    def test_epistemic_audit_records_no_forbidden_promotion(self) -> None:
        audit = self.report["epistemic_audit"]
        forbidden = (
            "coordinator_introduced_source_knowledge",
            "process_memory_strengthened_certainty",
            "repeated_capture_aggregated_confidence",
            "restart_lost_evidence",
            "missed_interval_interpreted_as_known_transition",
            "filesystem_and_git_collapsed",
            "projection_membership_became_admission_resolution",
            "current_state_overwrote_history",
        )
        self.assertTrue(all(not audit[key] for key in forbidden))
        self.assertTrue(audit["all_admissions_scoped_to_named_comparator"])

    def test_candidate_boundary_chart_and_distinction_are_earned_by_execution(self) -> None:
        self.assertTrue(self.report["success_criterion"]["coherent"])
        self.assertTrue(self.report["promotion_evaluation"]["candidate_boundary_earned"])
        self.assertTrue(self.report["promotion_evaluation"]["production_promoted"])
        self.assertEqual(self.report["chart_status"]["name"], "Chart 13")
        self.assertTrue(self.report["chart_status"]["earned"])
        self.assertTrue(self.report["distinction_evaluation"]["forced"])

    def test_closed_candidate_rejects_capture_without_persisting_close_state(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "fixture"
            root.mkdir()
            (root / "state.txt").write_text("alpha", encoding="utf-8")
            _initialize_fixture(root)
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            coordinator = ForegroundRepositoryObservationCoordinator(
                root, ledger_path
            )
            coordinator.close()
            with self.assertRaises(RuntimeError):
                coordinator.capture_round()
            self.assertFalse(ledger_path.exists())

    def test_canonical_history_and_persistent_ecology_are_untouched(self) -> None:
        for path in (
            "traces/live_ingest_ledger_v0.jsonl",
            "docs/projection/Persistent_Ecology.md",
        ):
            committed = subprocess.check_output(["git", "show", f"{STARTING_HEAD}:{path}"])
            with open(path, "rb") as current_file:
                current = current_file.read()
            self.assertEqual(current.splitlines(), committed.splitlines())
        canonical = self.report["canonical_history"]
        self.assertTrue(canonical["unchanged"])
        self.assertEqual(canonical["sha256_before"], canonical["sha256_after"])


if __name__ == "__main__":
    unittest.main()
