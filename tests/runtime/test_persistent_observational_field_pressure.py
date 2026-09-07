from __future__ import annotations

import subprocess
import unittest

from src.runtime.persistent_observational_field_pressure import STARTING_HEAD, run


class PersistentObservationalFieldPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.rounds = {item["round"]: item for item in cls.report["observation_rounds"]}
        cls.comparisons = cls.report["identity_comparisons"]

    def test_starting_lineage_and_baseline_are_recorded(self) -> None:
        starting = self.report["starting_lineage"]
        self.assertEqual(starting["branch"], "main")
        self.assertEqual(starting["head"], STARTING_HEAD)
        self.assertEqual(starting["message"], "CHart 11")
        self.assertEqual(starting["worktree"], [])
        self.assertEqual(self.report["baseline_tests"]["targeted"], {"passed": 51, "failed": 0})
        self.assertEqual(self.report["baseline_tests"]["full"], {"passed": 255, "failed": 0})

    def test_required_six_round_world_sequence_is_executed(self) -> None:
        self.assertEqual(
            list(self.rounds),
            ["O1", "O2", "O3", "O4", "O5", "O6"],
        )
        self.assertEqual(self.rounds["O1"]["world_condition"], "initial clean alpha")
        self.assertEqual(self.rounds["O3"]["world_condition"], "uncommitted dirty beta")
        self.assertEqual(self.rounds["O5"]["world_condition"], "committed clean beta")
        self.assertIn("after reopen", self.rounds["O6"]["world_condition"])

    def test_each_round_appends_two_observations_then_two_normal_admissions(self) -> None:
        for number, round_name in enumerate(self.rounds, start=1):
            item = self.rounds[round_name]
            self.assertEqual(item["record_range"], [number * 4 - 3, number * 4])
            self.assertEqual(
                item["new_record_types"],
                ["observation", "observation", "admission", "admission"],
            )
            self.assertEqual(item["admissions"]["filesystem"]["decision"], "admitted")
            self.assertEqual(item["admissions"]["git"]["decision"], "admitted")

    def test_every_round_preserves_integrity_continuity_and_canonical_replay(self) -> None:
        for number, item in enumerate(self.rounds.values(), start=1):
            stack = item["stack"]
            self.assertTrue(stack["integrity_ok"])
            self.assertTrue(stack["continuity_ok"])
            self.assertTrue(stack["canonical_replay_reproducible"])
            self.assertEqual(stack["record_count"], number * 4)
            self.assertEqual(stack["canonical_commit_indices"], list(range(1, number * 4 + 1)))

    def test_every_round_reconstructs_and_projects_reproducibly(self) -> None:
        for number, item in enumerate(self.rounds.values(), start=1):
            stack = item["stack"]
            expected_observations = number * 2
            self.assertTrue(stack["reconstruction_reproducible"])
            self.assertTrue(stack["projection_reproducible"])
            self.assertEqual(stack["reconstructed_observation_count"], expected_observations)
            self.assertEqual(stack["reconstructed_admission_relation_count"], expected_observations)
            self.assertEqual(stack["projection_subject_count"], expected_observations)
            self.assertEqual(stack["orphan_admission_count"], 0)

    def test_chart_11_companion_remains_reproducible_and_non_adjudicating(self) -> None:
        for number, item in enumerate(self.rounds.values(), start=1):
            stack = item["stack"]
            self.assertTrue(stack["companion_reproducible"])
            self.assertEqual(stack["companion_row_count"], number * 2)
            self.assertEqual(stack["companion_non_admitted_states"], [])
            self.assertTrue(
                all(row["non_admitted_decision_states"] == [] for row in stack["companion"])
            )
        companion = self.report["chart_11_companion"]
        self.assertFalse(companion["projection_membership_changed"])
        self.assertFalse(companion["admission_multiplicity_required"])
        self.assertFalse(companion["direct_admission_record_ids_required_in_companion"])

    def test_filesystem_reuses_structural_identity_for_repeated_state(self) -> None:
        for pair in ("O1_O2", "O3_O4", "O4_O5", "O5_O6"):
            filesystem = self.comparisons[pair]["filesystem"]
            self.assertTrue(filesystem["snapshot_id_equal"])
            self.assertTrue(filesystem["envelope_identity_equal"])
            self.assertTrue(filesystem["signal_identity_equal"])

    def test_filesystem_repeated_captures_preserve_occurrence_coordinates(self) -> None:
        for pair in ("O1_O2", "O3_O4", "O4_O5", "O5_O6"):
            filesystem = self.comparisons[pair]["filesystem"]
            self.assertFalse(filesystem["observation_started_at_equal"])
            self.assertFalse(filesystem["observation_finished_at_equal"])
            self.assertFalse(filesystem["ledger_observation_record_id_equal"])
            self.assertFalse(filesystem["commit_index_equal"])
            self.assertFalse(filesystem["record_digest_equal"])

    def test_git_uses_new_occurrence_identity_for_equivalent_state(self) -> None:
        for pair in ("O1_O2", "O3_O4", "O5_O6"):
            git = self.comparisons[pair]["git"]
            self.assertTrue(git["configuration_equal"])
            self.assertFalse(git["observation_id_equal"])
            self.assertFalse(git["observed_at_equal"])
            self.assertFalse(git["envelope_identity_equal"])
            self.assertFalse(git["signal_identity_equal"])
            self.assertFalse(git["ledger_observation_record_id_equal"])
            self.assertFalse(git["production_identity_promoted"])

    def test_uncommitted_beta_changes_both_source_configurations(self) -> None:
        o2 = self.rounds["O2"]
        o3 = self.rounds["O3"]
        self.assertNotEqual(o2["filesystem"]["snapshot_id"], o3["filesystem"]["snapshot_id"])
        self.assertNotEqual(o2["filesystem"]["state_txt_sha256"], o3["filesystem"]["state_txt_sha256"])
        self.assertEqual(o2["git"]["head_sha"], o3["git"]["head_sha"])
        self.assertEqual(o2["git"]["status_porcelain"], [])
        self.assertEqual(o3["git"]["status_porcelain"], ["M state.txt"])

    def test_commit_beta_changes_git_without_changing_filesystem_configuration(self) -> None:
        comparison = self.comparisons["O4_O5"]
        self.assertTrue(comparison["filesystem"]["configuration_equal"])
        self.assertFalse(comparison["git"]["configuration_equal"])
        self.assertFalse(comparison["git"]["head_sha_equal"])
        self.assertFalse(comparison["git"]["status_porcelain_equal"])
        self.assertFalse(self.report["cross_source_result"]["sources_collapsed"])

    def test_all_source_occurrences_have_unique_ledger_coordinates(self) -> None:
        observation_ids = []
        commit_indices = []
        for item in self.rounds.values():
            for source in ("filesystem", "git"):
                observation_ids.append(item[source]["ledger_record_id"])
                commit_indices.append(item[source]["commit_index"])
        self.assertEqual(len(observation_ids), 12)
        self.assertEqual(len(set(observation_ids)), 12)
        self.assertEqual(len(set(commit_indices)), 12)
        self.assertFalse(self.report["repeated_state_preservation"]["deduplication_performed"])

    def test_source_provenance_never_collapses(self) -> None:
        for number, item in enumerate(self.rounds.values(), start=1):
            stack = item["stack"]
            self.assertTrue(stack["source_provenance_separate"])
            self.assertEqual(
                stack["source_observation_counts"],
                {
                    "repository_filesystem_snapshot": number,
                    "repository_git_state": number,
                },
            )

    def test_O1_ordered_digest_prefix_survives_every_later_round(self) -> None:
        for item in self.rounds.values():
            relation = item["stack"]["historical_prefix"]
            self.assertTrue(relation["ok"])
            self.assertEqual(relation["relation"], "prefix_preservation")
            self.assertEqual(relation["details"]["witnessed_record_count"], 4)

    def test_reopen_reconstructs_O1_through_O5_from_disk_before_continuing(self) -> None:
        reopen = self.report["session_reopen"]
        self.assertTrue(reopen["first_session_returned_before_reopen"])
        self.assertTrue(reopen["fresh_ledger_instance_constructed_from_path"])
        self.assertFalse(reopen["reconstruction_or_projection_objects_passed_across_boundary"])
        self.assertEqual(reopen["pre_append_record_count"], 20)
        self.assertEqual(reopen["recovered_observation_count"], 10)
        self.assertEqual(reopen["recovered_admission_relation_count"], 10)
        self.assertEqual(reopen["recovered_projection_subject_count"], 10)
        self.assertTrue(reopen["disk_only_reconstruction_reproducible"])
        self.assertTrue(reopen["disk_only_projection_reproducible"])
        self.assertTrue(reopen["continuation_succeeded"])

    def test_final_field_has_exact_append_only_shape(self) -> None:
        final = self.report["final_state"]
        self.assertEqual(final["record_count"], 24)
        self.assertEqual(final["observation_count"], 12)
        self.assertEqual(final["admission_relation_count"], 12)
        self.assertEqual(final["projection_subject_count"], 12)
        self.assertEqual(final["companion_row_count"], 12)
        self.assertEqual(final["non_admitted_states"], [])
        self.assertEqual(final["commit_indices"], list(range(1, 25)))

    def test_more_observations_do_not_promote_epistemic_certainty(self) -> None:
        audit = {item["boundary"]: item for item in self.report["epistemic_audit"]}
        growth = audit["more observations -> epistemic strength"]
        self.assertFalse(growth["certainty_increased"])
        self.assertFalse(growth["information_lost"])
        mismatch = audit["mismatch or unresolved evidence -> structural success"]
        self.assertFalse(mismatch["exercised"])
        self.assertFalse(mismatch["certainty_increased"])

    def test_current_structures_are_coherent_without_new_distinction(self) -> None:
        self.assertTrue(self.report["success_criterion"]["coherent"])
        self.assertEqual(self.report["distinctions"]["added"], [])
        self.assertEqual(self.report["distinctions"]["amended"], [])
        self.assertEqual(self.report["production_changes"], [])

    def test_chart_12_is_earned_as_bounded_coordinate_surface(self) -> None:
        chart = self.report["chart_status"]
        self.assertTrue(chart["earned"])
        self.assertEqual(chart["name"], "Chart 12")
        self.assertFalse(chart["generalized_state_model"])

    def test_canonical_live_history_and_non_authoritative_projection_are_untouched(self) -> None:
        for path in (
            "traces/live_ingest_ledger_v0.jsonl",
            "docs/projection/Persistent_Ecology.md",
        ):
            committed = subprocess.check_output(["git", "show", f"{STARTING_HEAD}:{path}"])
            with open(path, "rb") as current_file:
                current = current_file.read()
            self.assertEqual(current.splitlines(), committed.splitlines())
        self.assertTrue(self.report["canonical_history"]["unchanged"])
        self.assertEqual(
            self.report["canonical_history"]["sha256_before"],
            self.report["canonical_history"]["sha256_after"],
        )

    def test_existing_production_semantics_are_untouched(self) -> None:
        changed = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                STARTING_HEAD,
                "--",
                "src/capture",
                "src/ingest",
                "src/ledger",
                "src/reconstruction",
            ],
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])


if __name__ == "__main__":
    unittest.main()
