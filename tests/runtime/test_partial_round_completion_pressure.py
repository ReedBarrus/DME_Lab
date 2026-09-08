from __future__ import annotations

import json
import subprocess
import unittest

from src.runtime.partial_round_completion_pressure import STARTING_HEAD, run


class PartialRoundCompletionPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.specimens = cls.report["specimens"]
        cls.matrix = cls.report["comparison_matrix"]

    def test_starting_lineage_and_baseline_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "Phase-C")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(
            self.report["baseline_tests"]["foreground_coordinator"],
            {"passed": 23, "failed": 0},
        )
        self.assertEqual(
            self.report["baseline_tests"]["full"],
            {"passed": 299, "failed": 0},
        )

    def test_faults_are_injected_without_process_kill_or_torn_write(self) -> None:
        injection = self.report["fault_injection"]
        self.assertIn("InjectedCaptureFailure", injection["mechanism"])
        self.assertFalse(injection["real_process_kill"])
        self.assertFalse(injection["torn_JSON_write"])
        self.assertFalse(injection["production_coordinator_modified"])
        self.assertFalse(injection["injected_stage_available_to_recovery_evaluator"])

    def test_every_independent_specimen_uses_same_world_configuration(self) -> None:
        fixture = self.report["fixture_control"]
        self.assertTrue(fixture["independent_repository_per_specimen"])
        self.assertTrue(fixture["same_configuration"])
        self.assertFalse(fixture["world_mutation_during_fault_pressure"])
        self.assertEqual(fixture["fixed_state_txt_content"], "alpha")
        self.assertEqual(len(fixture["configuration_signatures"]), 6)

    def test_fault_boundaries_preserve_exact_number_of_new_records(self) -> None:
        expected = {"F0": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "C": 4}
        for name, durable in expected.items():
            recovery = self.specimens[name]["recovery"]
            self.assertEqual(recovery["durable_new_record_count"], durable)
            self.assertEqual(recovery["record_count"], 4 + durable)
            self.assertEqual(self.specimens[name]["expected_durable_new_records_from_driver"], durable)

    def test_caller_outcomes_are_exceptions_F0_through_F4_and_success_for_control(self) -> None:
        for name in ("F0", "F1", "F2", "F3", "F4"):
            caller = self.specimens[name]["caller"]
            self.assertFalse(caller["result_returned"])
            self.assertEqual(caller["exception"], "InjectedCaptureFailure")
        self.assertTrue(self.specimens["C"]["caller"]["result_returned"])
        self.assertIsNone(self.specimens["C"]["caller"]["exception"])

    def test_new_record_shapes_follow_actual_commitment_boundaries(self) -> None:
        expected = {
            "F0": [],
            "F1": ["observation"],
            "F2": ["observation", "observation"],
            "F3": ["observation", "observation", "admission"],
            "F4": ["observation", "observation", "admission", "admission"],
            "C": ["observation", "observation", "admission", "admission"],
        }
        for name, shape in expected.items():
            self.assertEqual(self.specimens[name]["recovery"]["new_record_types"], shape)

    def test_record_ids_and_commit_indices_remain_canonical(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            count = recovery["record_count"]
            self.assertEqual(recovery["commit_indices"], list(range(1, count + 1)))
            self.assertEqual(
                recovery["record_ids"],
                [f"rec-{index:06d}" for index in range(1, count + 1)],
            )

    def test_every_specimen_is_integrity_valid_continuity_valid_and_replayable(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            self.assertTrue(recovery["integrity_ok"])
            self.assertTrue(recovery["continuity_ok"])
            self.assertTrue(recovery["replay_reproducible"])
            self.assertTrue(recovery["current_result_read_only"])

    def test_F0_contains_only_the_prior_complete_prefix(self) -> None:
        recovery = self.specimens["F0"]["recovery"]
        self.assertEqual(recovery["record_count"], 4)
        self.assertEqual(recovery["reconstructed_observation_count"], 2)
        self.assertEqual(recovery["admission_relation_count"], 2)
        self.assertEqual(len(recovery["projection_subject_ids"]), 2)

    def test_F1_preserves_one_unadmitted_filesystem_observation(self) -> None:
        recovery = self.specimens["F1"]["recovery"]
        self.assertEqual(recovery["reconstructed_observation_count"], 3)
        self.assertEqual(recovery["admission_relation_count"], 2)
        self.assertEqual(len(recovery["projection_subject_ids"]), 2)
        self.assertEqual(recovery["admission_states_by_subject"]["rec-000005"], [])
        self.assertEqual(recovery["records"][-1]["source"], "repository_filesystem_snapshot")

    def test_F2_preserves_two_observations_without_new_admissions(self) -> None:
        recovery = self.specimens["F2"]["recovery"]
        self.assertEqual(recovery["reconstructed_observation_count"], 4)
        self.assertEqual(recovery["admission_relation_count"], 2)
        self.assertEqual(len(recovery["projection_subject_ids"]), 2)
        self.assertEqual(recovery["admission_states_by_subject"]["rec-000005"], [])
        self.assertEqual(recovery["admission_states_by_subject"]["rec-000006"], [])

    def test_F3_preserves_one_new_admitted_and_one_unadmitted_subject(self) -> None:
        recovery = self.specimens["F3"]["recovery"]
        self.assertEqual(recovery["reconstructed_observation_count"], 4)
        self.assertEqual(recovery["admission_relation_count"], 3)
        self.assertEqual(len(recovery["projection_subject_ids"]), 3)
        self.assertEqual(recovery["admission_states_by_subject"]["rec-000005"], ["admitted"])
        self.assertEqual(recovery["admission_states_by_subject"]["rec-000006"], [])

    def test_F4_and_control_each_preserve_complete_durable_composition(self) -> None:
        for name in ("F4", "C"):
            recovery = self.specimens[name]["recovery"]
            self.assertEqual(recovery["record_count"], 8)
            self.assertEqual(recovery["reconstructed_observation_count"], 4)
            self.assertEqual(recovery["admission_relation_count"], 4)
            self.assertEqual(len(recovery["projection_subject_ids"]), 4)

    def test_partial_histories_are_valid_and_legible_not_declared_corrupt(self) -> None:
        partials = self.report["partial_histories"]
        self.assertTrue(partials["integrity_continuity_replay_valid"])
        self.assertTrue(partials["record_relation_legible"])
        self.assertFalse(partials["treated_as_corruption"])
        self.assertFalse(partials["round_historical_unit_assumed"])

    def test_every_recovery_uses_only_disk_and_declared_prefix_witness(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            self.assertEqual(
                recovery["evaluator_inputs"],
                ["root", "ledger_path", "prior complete prefix witness"],
            )
            self.assertFalse(recovery["failed_process_state_used"])

    def test_prior_complete_prefix_survives_every_fault_and_control(self) -> None:
        for specimen in self.specimens.values():
            relation = specimen["recovery"]["prior_prefix"]
            self.assertTrue(relation["ok"])
            self.assertEqual(relation["relation"], "prefix_preservation")
            self.assertEqual(relation["details"]["witnessed_record_count"], 4)

    def test_chart_11_companion_tracks_only_projected_admitted_subjects(self) -> None:
        expected_counts = {"F0": 2, "F1": 2, "F2": 2, "F3": 3, "F4": 4, "C": 4}
        for name, count in expected_counts.items():
            recovery = self.specimens[name]["recovery"]
            self.assertEqual(len(recovery["companion"]), count)
            self.assertTrue(
                all(row["non_admitted_decision_states"] == [] for row in recovery["companion"])
            )

    def test_source_provenance_remains_separate_in_all_partial_histories(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            self.assertFalse(recovery["source_provenance_collapsed"])
            self.assertTrue(
                set(recovery["source_values"])
                <= {"repository_filesystem_snapshot", "repository_git_state"}
            )

    def test_completion_is_unresolved_from_authoritative_history_for_all_specimens(self) -> None:
        for specimen in self.specimens.values():
            recovery = specimen["recovery"]
            inference = recovery["completion_inference"]
            self.assertEqual(recovery["production_completion_fields"], [])
            self.assertEqual(inference["outcome"], "UNRESOLVED")
            self.assertFalse(inference["complete_established"])
            self.assertFalse(inference["incomplete_established"])

    def test_F4_and_control_differ_at_caller_but_not_durable_completion_surface(self) -> None:
        comparison = self.report["F4_control_comparison"]
        self.assertTrue(comparison["caller_outcomes_differ"])
        self.assertFalse(comparison["ledger_bytes_equal"])
        self.assertTrue(comparison["independent_occurrence_bytes_expected_to_differ"])
        self.assertTrue(comparison["durable_completion_surfaces_equal"])
        self.assertTrue(comparison["production_acknowledgement_fields_equal"])
        self.assertFalse(comparison["caller_outcome_inferable_from_either_history"])

    def test_retry_after_unknown_F4_success_appends_another_valid_observation(self) -> None:
        retry = self.report["retry_after_F4"]
        self.assertFalse(retry["world_changed_before_retry"])
        self.assertTrue(retry["retry_returned"])
        self.assertEqual(
            retry["retry_returned_new_record_ids"],
            ["rec-000009", "rec-000010", "rec-000011", "rec-000012"],
        )
        self.assertEqual(retry["after_retry"]["record_count"], 12)
        self.assertTrue(retry["after_retry"]["internally_valid"])
        self.assertTrue(retry["first_and_second_group_configuration_equal"])
        self.assertEqual(retry["retry_marker_fields"], [])
        self.assertFalse(retry["retry_distinguishable_from_intentional_repeat"])

    def test_D0042_remains_supported_without_amendment(self) -> None:
        status = self.report["D_0042"]
        self.assertEqual(status["status"], "SUPPORTED_UNCHANGED")
        self.assertFalse(status["amended"])

    def test_promoted_coordinator_is_preserved_with_scoped_guarantee(self) -> None:
        boundary = self.report["production_boundary"]
        self.assertEqual(boundary["status"], "PRESERVED_WITH_SCOPED_GUARANTEE")
        self.assertFalse(boundary["atomic_round_guarantee"])
        self.assertFalse(boundary["durable_completion_acknowledgement"])
        self.assertFalse(boundary["documentation_mismatch_found"])
        self.assertFalse(boundary["production_change_made"])
        changed = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                STARTING_HEAD,
                "--",
                "src/runtime/foreground_repository_observation.py",
                "src/runtime/__init__.py",
            ],
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])

    def test_chart_14_and_D0043_are_earned(self) -> None:
        chart = self.report["chart_status"]
        self.assertTrue(chart["earned"])
        self.assertEqual(chart["name"], "Chart 14")
        self.assertFalse(chart["generalized_transaction_model"])
        self.assertEqual(
            self.report["distinctions"]["added"],
            [
                {
                    "id": "D-0043",
                    "left": "caller_invocation_outcome",
                    "relation": "not_equivalent_to",
                    "right": "durable_history_state",
                }
            ],
        )

    def test_D0043_is_registered_from_executed_evidence(self) -> None:
        with open("docs/distinctions/registry.jsonl", encoding="utf-8") as registry:
            entries = [json.loads(line) for line in registry if line.strip()]
        distinction = next(entry for entry in entries if entry["id"] == "D-0043")
        self.assertEqual(distinction["id"], "D-0043")
        self.assertEqual(distinction["left"], "caller_invocation_outcome")
        self.assertEqual(distinction["right"], "durable_history_state")
        self.assertEqual(distinction["standing"], "supported")

    def test_epistemic_audit_makes_no_forbidden_inference(self) -> None:
        audit = self.report["epistemic_audit"]
        self.assertEqual(audit["all_completion_outcomes_from_history"], ["UNRESOLVED"])
        for key, value in audit.items():
            if key == "all_completion_outcomes_from_history":
                continue
            self.assertFalse(value, key)

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
