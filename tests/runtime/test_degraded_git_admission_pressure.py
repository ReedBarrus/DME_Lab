from __future__ import annotations

import json
import subprocess
import unittest

from src.runtime.degraded_git_admission_pressure import STARTING_HEAD, run


class DegradedGitAdmissionPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.c0 = cls.report["specimens"]["C0"]
        cls.s1 = cls.report["specimens"]["S1"]

    def test_starting_lineage_and_baselines_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "The completion of the Real Wound 4")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(
            self.report["baseline_tests"]["targeted"], {"passed": 137, "failed": 0}
        )
        self.assertEqual(
            self.report["baseline_tests"]["full"], {"passed": 413, "failed": 0}
        )

    def test_fixtures_use_real_observer_without_mocked_payload(self) -> None:
        fixture = self.report["fixture_control"]
        self.assertTrue(fixture["real_git_observer"])
        self.assertFalse(fixture["mocked_payload"])
        self.assertEqual(fixture["C0"], "ordinary clean Git repository")
        self.assertEqual(
            fixture["S1"], "ordinary filesystem directory with state.txt and no .git repository"
        )

    def test_C0_has_healthy_filesystem_and_git_acquisition(self) -> None:
        self.assertTrue(self.c0["fixture"]["git_directory_present"])
        self.assertEqual(self.c0["fixture"]["filesystem_capture_errors"], [])
        raw = self.c0["layers"]["raw_git_acquisition_quality"]
        self.assertEqual(raw["status"], "SUCCESSFUL")
        self.assertEqual(raw["capture_error_count"], 0)
        self.assertEqual(raw["null_fields"], [])
        self.assertTrue(raw["head_sha"])
        self.assertEqual(raw["branch"], "main")
        self.assertEqual(raw["status_porcelain"], [])

    def test_S1_is_natural_non_git_directory_with_healthy_filesystem(self) -> None:
        self.assertFalse(self.s1["fixture"]["git_directory_present"])
        self.assertEqual(self.s1["fixture"]["root_kind"], "ordinary non-Git directory")
        self.assertEqual(self.s1["fixture"]["filesystem_capture_errors"], [])

    def test_S1_observer_returns_degraded_observation_object(self) -> None:
        raw = self.s1["layers"]["raw_git_acquisition_quality"]
        self.assertEqual(raw["status"], "DEGRADED")
        self.assertTrue(raw["observation_object_returned"])
        self.assertEqual(raw["capture_error_count"], 3)
        self.assertEqual(raw["null_fields"], ["head_sha", "branch", "status_porcelain"])
        self.assertIsNone(raw["head_sha"])
        self.assertIsNone(raw["branch"])
        self.assertIsNone(raw["status_porcelain"])

    def test_S1_capture_errors_name_all_real_failed_git_commands(self) -> None:
        raw = self.s1["layers"]["raw_git_acquisition_quality"]
        self.assertEqual(
            raw["failed_commands"],
            ["rev-parse HEAD", "branch --show-current", "status --porcelain=v1"],
        )
        self.assertTrue(
            all("not a git repository" in error["error"] for error in raw["capture_errors"])
        )

    def test_three_layers_remain_independent(self) -> None:
        result = self.report["three_layer_result"]
        self.assertIn("degraded", result["raw_Git_acquisition_quality"])
        self.assertEqual(
            result["structural_admission_decision"], "admitted under COMPARATOR_V0"
        )
        self.assertEqual(
            result["downstream_projection_exposure"],
            "Git subject included without direct error detail",
        )
        self.assertIn("successful Git source state was not certified", result["correct_interpretation"])

    def test_S1_ingest_envelope_is_constructed_with_expected_shape(self) -> None:
        admission = self.s1["layers"]["structural_admission_decision"]
        self.assertTrue(admission["ingest_envelope_constructed"])
        self.assertTrue(
            {"envelope_identity", "source", "signal", "provenance"}
            <= set(admission["envelope_keys"])
        )
        self.assertEqual(set(admission["signal_keys"]), {"identity", "payload", "time", "type"})

    def test_both_specimens_are_schema_valid_under_same_comparator(self) -> None:
        for specimen in (self.c0, self.s1):
            admission = specimen["layers"]["structural_admission_decision"]
            self.assertEqual(admission["schema_status"], "compared")
            self.assertTrue(admission["schema_valid"])
            self.assertEqual(admission["schema_errors"], [])
            self.assertEqual(admission["comparator_identity"], "ingest_candidate_envelope_minimum")
            self.assertEqual(
                admission["comparator_version"], "ingest_candidate_envelope_minimum_v0"
            )

    def test_comparator_is_minimum_structural_not_git_success_validator(self) -> None:
        comparator = self.report["comparator_audit"]
        self.assertEqual(comparator["kind"], "minimum structural observation-envelope comparator")
        self.assertFalse(comparator["checks_git_head_sha"])
        self.assertFalse(comparator["checks_git_branch"])
        self.assertFalse(comparator["checks_git_status"])
        self.assertFalse(comparator["checks_capture_errors"])
        self.assertFalse(comparator["certifies_source_capture_success"])

    def test_both_healthy_and_degraded_git_observations_are_admitted(self) -> None:
        for specimen in (self.c0, self.s1):
            admission = specimen["layers"]["structural_admission_decision"]
            self.assertEqual(admission["decision"], "admitted")
            self.assertEqual(admission["decision_basis"], "comparison valid under comparator")
            self.assertFalse(admission["certifies_source_capture_success"])

    def test_every_history_is_structurally_healthy(self) -> None:
        for specimen in (self.c0, self.s1):
            health = specimen["health"]
            self.assertTrue(health["integrity_ok"])
            self.assertTrue(health["continuity_ok"])
            self.assertTrue(health["replay_reproducible"])
            self.assertTrue(health["reconstruction_reproducible"])
            self.assertTrue(health["projection_reproducible"])
            self.assertTrue(health["companion_reproducible"])
            self.assertTrue(health["structurally_healthy"])

    def test_every_history_has_two_observations_two_admissions_and_two_projection_subjects(self) -> None:
        for specimen in (self.c0, self.s1):
            health = specimen["health"]
            self.assertEqual(health["record_count"], 4)
            self.assertEqual(health["observation_count"], 2)
            self.assertEqual(health["admission_relation_count"], 2)
            self.assertEqual(health["projection_count"], 2)
            self.assertEqual(health["companion_count"], 2)
            self.assertEqual(health["orphan_admission_count"], 0)

    def test_source_provenance_remains_separate(self) -> None:
        self.assertTrue(self.c0["health"]["source_separation"])
        self.assertTrue(self.s1["health"]["source_separation"])

    def test_capture_errors_exist_in_raw_and_both_ingest_envelope_locations(self) -> None:
        visibility = self.s1["capture_error_visibility"]
        self.assertTrue(visibility["raw_git_observation"])
        self.assertTrue(visibility["ingest_envelope_provenance"])
        self.assertTrue(visibility["ingest_envelope_signal_payload"])

    def test_capture_errors_survive_ledger_in_both_nested_locations(self) -> None:
        visibility = self.s1["capture_error_visibility"]
        self.assertTrue(visibility["ledger_nested_observation_provenance"])
        self.assertTrue(visibility["ledger_nested_signal_payload"])
        self.assertFalse(visibility["observation_record_outer_provenance"])

    def test_capture_errors_survive_reconstruction_in_nested_observation(self) -> None:
        visibility = self.s1["capture_error_visibility"]
        self.assertTrue(visibility["reconstruction_nested_observation_provenance"])
        self.assertTrue(visibility["reconstruction_nested_signal_payload"])
        self.assertFalse(visibility["reconstruction_outer_provenance"])

    def test_projection_includes_degraded_git_subject_without_error_detail(self) -> None:
        projection = self.s1["layers"]["downstream_projection_exposure"]
        self.assertTrue(projection["included"])
        self.assertFalse(projection["capture_errors_directly_visible"])
        self.assertEqual(projection["projection_row"]["source"], "repository_git_state")

    def test_chart_11_companion_exposes_no_non_admitted_or_error_state(self) -> None:
        projection = self.s1["layers"]["downstream_projection_exposure"]
        self.assertEqual(projection["companion_non_admitted_states"], [])
        self.assertFalse(projection["companion_exposes_capture_errors"])

    def test_fresh_recovery_is_append_free_and_recovers_degraded_evidence(self) -> None:
        recovery = self.s1["fresh_recovery"]
        self.assertEqual(recovery["inputs"], ["root", "ledger_path"])
        self.assertTrue(recovery["append_free"])
        self.assertEqual(recovery["ledger_sha256_before"], recovery["ledger_sha256_after"])
        self.assertTrue(recovery["current_result_projection_contains_git"])
        self.assertEqual(len(recovery["reconstruction_capture_errors"]), 3)
        self.assertFalse(recovery["process_local_failure_knowledge_required"])

    def test_current_result_does_not_directly_expose_capture_errors(self) -> None:
        recovery = self.s1["fresh_recovery"]
        self.assertIsNone(recovery["current_result_captured_observations"])
        self.assertFalse(
            self.s1["capture_error_visibility"]["current_result_top_level_or_projection"]
        )

    def test_degradation_is_preserved_in_history_not_direct_projection(self) -> None:
        boundary = self.report["information_boundary"]
        self.assertTrue(boundary["degraded_condition_preserved_in_authoritative_history"])
        self.assertTrue(boundary["degraded_condition_recoverable_after_fresh_replay"])
        self.assertFalse(boundary["projection_directly_exposes_degraded_condition"])
        self.assertFalse(boundary["companion_directly_exposes_degraded_condition"])
        self.assertFalse(boundary["current_result_directly_exposes_degraded_condition"])
        self.assertFalse(boundary["information_erased_from_history"])

    def test_admission_does_not_certify_source_success(self) -> None:
        self.assertEqual(
            self.s1["layers"]["structural_admission_decision"]["decision"], "admitted"
        )
        self.assertEqual(
            self.s1["layers"]["raw_git_acquisition_quality"]["status"], "DEGRADED"
        )
        self.assertFalse(self.report["comparator_audit"]["certifies_source_capture_success"])

    def test_production_contract_is_scoped_without_defect(self) -> None:
        contract = self.report["production_contract"]
        self.assertEqual(contract["admission_claim"], "comparison valid under named comparator")
        self.assertFalse(contract["claims_source_capture_succeeded"])
        self.assertFalse(contract["claims_projected_subject_is_epistemically_resolved"])
        self.assertTrue(contract["structural_comparator_preserved"])
        self.assertFalse(contract["production_defect_found"])
        self.assertFalse(contract["production_change_made"])

    def test_chart_18_and_D0046_are_earned(self) -> None:
        chart = self.report["chart_status"]
        self.assertTrue(chart["earned"])
        self.assertEqual(chart["name"], "Chart 18")
        self.assertFalse(chart["trust_or_source_health_policy"])
        self.assertEqual(
            self.report["distinctions"]["added"],
            [
                {
                    "id": "D-0046",
                    "left": "structural_admissibility",
                    "relation": "not_equivalent_to",
                    "right": "source_capture_success",
                }
            ],
        )

    def test_D0046_is_registered_from_executed_evidence(self) -> None:
        with open("docs/constraints/registry.jsonl", encoding="utf-8") as registry:
            entries = [json.loads(line) for line in registry if line.strip()]
        distinction = next(entry for entry in entries if entry["id"] == "D-0046")
        self.assertEqual(distinction["left"], "structural_admissibility")
        self.assertEqual(distinction["right"], "source_capture_success")
        self.assertEqual(distinction["standing"], "supported")

    def test_prior_distinctions_remain_supported(self) -> None:
        prior = self.report["prior_findings"]
        for identifier in ("D_0012", "D_0016", "D_0042", "D_0043", "D_0044", "D_0045"):
            self.assertEqual(prior[identifier], "SUPPORTED_UNCHANGED")
        self.assertEqual(prior["invalidated"], [])

    def test_epistemic_audit_makes_no_forbidden_inference(self) -> None:
        self.assertTrue(all(value is False for value in self.report["epistemic_audit"].values()))

    def test_production_code_and_canonical_history_are_untouched(self) -> None:
        paths = (
            "src/runtime/foreground_repository_observation.py",
            "src/capture/git_state.py",
            "src/ingest/admission.py",
            "src/reconstruction/admission.py",
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
