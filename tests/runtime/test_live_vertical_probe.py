from __future__ import annotations

import unittest

from src.runtime.live_vertical_probe import (
    authoritative_records,
    find_record,
    load_report,
    rebuild_from_report,
)


class LiveVerticalProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_report()
        cls.records = authoritative_records(cls.report)
        cls.rebuild = rebuild_from_report(cls.report)

    def test_live_filesystem_and_git_observations_remain_distinct_source_records(self) -> None:
        sources = [
            record["envelope"].get("source")
            for record in self.records
            if record["envelope"].get("record_type") == "observation"
        ]

        self.assertEqual(sources.count("repository_filesystem_snapshot"), 3)
        self.assertEqual(sources.count("repository_git_state"), 3)

    def test_observations_are_persisted_before_admission_relations(self) -> None:
        records_by_id = {record["record_id"]: record for record in self.records}

        for record in self.records:
            envelope = record["envelope"]
            if envelope.get("record_type") != "admission":
                continue
            subject = records_by_id[envelope["subject_record_id"]]
            self.assertLess(subject["commit_index"], record["commit_index"])

    def test_admission_records_reference_correct_live_observation_ids(self) -> None:
        observation_ids = {
            record["record_id"]
            for record in self.records
            if record["envelope"].get("record_type") == "observation"
        }

        for decision in self.report["admission_decisions"]:
            self.assertIn(decision["observation_record_id"], observation_ids)
            admission = find_record(self.records, decision["admission_record_id"])
            self.assertEqual(admission["envelope"]["subject_record_id"], decision["observation_record_id"])

    def test_replay_preserves_authoritative_history(self) -> None:
        self.assertEqual(self.report["authoritative_history"]["record_count"], len(self.records))
        self.assertEqual(
            self.report["authoritative_history"]["record_ids"],
            [record["record_id"] for record in self.records],
        )
        self.assertEqual(
            self.report["authoritative_history"]["commit_indices"],
            [record["commit_index"] for record in self.records],
        )

    def test_reconstruction_recovers_all_live_observation_admission_relationships(self) -> None:
        reconstruction = self.rebuild["reconstruction_a"]

        self.assertEqual(reconstruction["reconstruction_type"], "admission_relationships_v0")
        self.assertEqual(len(reconstruction["observations"]), 6)
        self.assertEqual(sum(len(item["admissions"]) for item in reconstruction["observations"]), 6)
        self.assertEqual(reconstruction["orphan_admissions"], [])

    def test_projection_consumes_reconstruction(self) -> None:
        projection = self.rebuild["projection_a"]

        self.assertEqual(
            [item["subject_record_id"] for item in projection],
            self.report["projection"]["subject_record_ids"],
        )
        self.assertTrue(all(item["reconstruction_type"] == "admission_relationships_v0" for item in projection))

    def test_projected_subjects_navigate_back_to_source_provenance(self) -> None:
        records_by_id = {record["record_id"]: record for record in self.records}
        reconstruction_by_id = {
            item["observation_record_id"]: item
            for item in self.rebuild["reconstruction_a"]["observations"]
        }

        for projected in self.rebuild["projection_a"]:
            reconstructed = reconstruction_by_id[projected["observation_record_id"]]
            observation_record = records_by_id[reconstructed["observation_record_id"]]
            admission_record = records_by_id[reconstructed["admission_record_ids"][0]]

            self.assertEqual(projected["subject_record_id"], reconstructed["observation_record_id"])
            self.assertEqual(admission_record["envelope"]["subject_record_id"], observation_record["record_id"])
            self.assertIn("observation_point", reconstructed["provenance"])
            self.assertIn("signal", observation_record["envelope"]["observation"])
            self.assertIn("comparison_result", admission_record["envelope"])
            self.assertIn("decision", admission_record["envelope"])
            self.assertIn("decision_basis", admission_record["envelope"])

    def test_reconstruction_rebuild_is_structurally_stable(self) -> None:
        self.assertTrue(self.rebuild["reconstruction_structural_equality"])

    def test_projection_rebuild_is_structurally_stable(self) -> None:
        self.assertTrue(self.rebuild["projection_structural_equality"])

    def test_no_index_required_for_correctness(self) -> None:
        self.assertFalse(self.report["index_pressure"]["appeared"])
        self.assertNotIn("observations_by_id", self.report)
        self.assertNotIn("admissions_by_subject", self.report)

    def test_transition_visibility_remains_bounded(self) -> None:
        visibility = self.report["transition_visibility"]

        self.assertEqual(visibility["pre_probe_clean_status"], [])
        self.assertEqual(visibility["dirty_probe_status"], ["?? tests/fixtures/repo_observation_probe.txt"])
        self.assertEqual(visibility["post_commit_clean_status"], [])
        self.assertFalse(visibility["probe_present_at_T0"])
        self.assertTrue(visibility["probe_present_at_T1"])
        self.assertTrue(visibility["probe_present_at_T2"])


if __name__ == "__main__":
    unittest.main()
