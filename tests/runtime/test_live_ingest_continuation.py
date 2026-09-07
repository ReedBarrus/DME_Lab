from __future__ import annotations

import unittest

from src.runtime.live_ingest_continuation import (
    canonical_records,
    load_report,
    rebuild_from_canonical_ledger,
    verify_canonical_ledger,
)


class LiveIngestContinuationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_report()
        cls.records = canonical_records(cls.report)
        cls.rebuild = rebuild_from_canonical_ledger(cls.report)

    def test_canonical_history_extends_existing_prefix_without_mutation(self) -> None:
        prefix = self.report["historical_non_mutation"]

        self.assertTrue(prefix["h0_before_equals_h1_prefix"])
        self.assertEqual(prefix["h0_before_sha256"], prefix["h1_prefix_sha256"])
        self.assertTrue(prefix["old_record_ids_unchanged"])
        self.assertTrue(prefix["old_commit_indices_unchanged"])
        self.assertTrue(prefix["old_integrity_fields_unchanged"])

    def test_new_records_continue_existing_identity_and_commit_indices(self) -> None:
        self.assertEqual(
            [(record["record_id"], record["commit_index"]) for record in self.records[-2:]],
            [("rec-000013", 13), ("rec-000014", 14)],
        )
        self.assertEqual([item["record_id"] for item in self.report["new_records"]], ["rec-000013", "rec-000014"])
        self.assertTrue(self.report["enlarged_history"]["new_commit_indices_continue_after_12"])
        self.assertTrue(self.report["enlarged_history"]["new_record_ids_continue_bounded_sequence"])

    def test_process_discontinuity_recovers_from_disk_state(self) -> None:
        discontinuity = self.report["process_discontinuity"]

        self.assertTrue(discontinuity["exercised"])
        self.assertTrue(discontinuity["disk_state_alone_recovered_continuation"])
        self.assertTrue(self.rebuild["disk_replay_structural_equality"])

    def test_integrity_verifies_before_and_after_continuation(self) -> None:
        self.assertTrue(self.report["starting_history"]["integrity"]["ok"])
        self.assertTrue(self.report["enlarged_history"]["integrity"]["ok"])

        verification = verify_canonical_ledger(self.report)
        self.assertTrue(verification.ok)
        self.assertEqual(verification.record_count, 14)
        self.assertEqual(verification.failures, ())

    def test_reconstruction_covers_old_and_new_relationships(self) -> None:
        continuity = self.report["derived_state_continuity"]
        reconstruction = self.rebuild["reconstruction_a"]

        self.assertEqual(continuity["before_reconstruction"]["observation_count"], 6)
        self.assertEqual(continuity["after_reconstruction"]["observation_count"], 7)
        self.assertEqual(continuity["after_reconstruction"]["admission_relation_count"], 7)
        self.assertTrue(continuity["old_reconstruction_survives"])
        self.assertTrue(continuity["new_reconstruction_appears"])
        self.assertEqual(len(reconstruction["observations"]), 7)

    def test_projection_covers_old_and_new_admitted_subjects(self) -> None:
        continuity = self.report["derived_state_continuity"]
        projection_ids = [item["subject_record_id"] for item in self.rebuild["projection_a"]]

        self.assertTrue(continuity["old_projection_survives"])
        self.assertTrue(continuity["new_projection_appears"])
        self.assertIn("rec-000013", projection_ids)
        self.assertEqual(projection_ids, continuity["after_projection_subject_ids"])

    def test_deterministic_rebuilds_from_fresh_replay(self) -> None:
        self.assertTrue(self.report["derived_state_continuity"]["reconstruction_rebuild_structural_equal"])
        self.assertTrue(self.report["derived_state_continuity"]["projection_rebuild_structural_equal"])
        self.assertTrue(self.rebuild["reconstruction_structural_equality"])
        self.assertTrue(self.rebuild["projection_structural_equality"])

    def test_projection_and_reconstruction_remain_derived_not_authoritative_records(self) -> None:
        record_types = [record["envelope"].get("record_type") for record in self.records]

        self.assertEqual(set(record_types), {"observation", "admission"})
        self.assertTrue(self.report["derived_state_continuity"]["projection_not_appended_to_history"])
        self.assertTrue(self.report["derived_state_continuity"]["reconstruction_not_appended_to_history"])

    def test_new_provenance_navigation_reaches_authoritative_records(self) -> None:
        path = self.report["provenance_navigation_example"]
        records_by_id = {record["record_id"]: record for record in self.records}
        observation = records_by_id[path["observation_record_id"]]
        admission = records_by_id[path["admission_record_id"]]

        self.assertEqual(path["projection_subject_record_id"], "rec-000013")
        self.assertEqual(observation["envelope"]["source"], "repository_filesystem_snapshot")
        self.assertEqual(admission["envelope"]["subject_record_id"], observation["record_id"])
        self.assertEqual(path["decision"], "admitted")
        self.assertIn("capture_started_at", path["provenance"])
        self.assertIn("raw_signal_identity", path)

    def test_no_index_required_for_continuation_correctness(self) -> None:
        self.assertFalse(self.report["index_pressure"]["appeared"])
        self.assertNotIn("observations_by_id", self.report)
        self.assertNotIn("admissions_by_subject", self.report)


if __name__ == "__main__":
    unittest.main()
