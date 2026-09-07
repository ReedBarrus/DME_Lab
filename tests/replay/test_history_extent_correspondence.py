from __future__ import annotations

from copy import deepcopy
import unittest

from src.ledger import (
    compare_history_extent,
    history_extent,
    replay_canonical_live_ingest,
    verify_canonical_live_ingest,
    verify_continuity,
)
from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships
from src.runtime.history_extent_witness_pressure import (
    extent_from_continuation_witness,
    load_json,
    run,
    verify_records_with_jsonl,
)


class HistoryExtentCorrespondenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = replay_canonical_live_ingest()
        cls.witness = load_json("traces/live_ingest_continuation_v0.json")
        cls.witness_extent = extent_from_continuation_witness(cls.witness)

    def test_canonical_h14_corresponds_to_existing_continuation_witness(self) -> None:
        integrity = verify_canonical_live_ingest()
        continuity = verify_continuity(self.records, require_start_at_one=True)
        correspondence = compare_history_extent(history_extent(self.records), self.witness_extent)

        self.assertTrue(integrity.ok)
        self.assertEqual(integrity.record_count, 14)
        self.assertTrue(continuity.ok)
        self.assertEqual(continuity.record_count, 14)
        self.assertTrue(correspondence.ok)
        self.assertEqual(correspondence.mismatches, ())

    def test_tail_loss_passes_local_checks_but_fails_witness_correspondence(self) -> None:
        h13 = deepcopy(self.records[:-1])
        integrity = verify_records_with_jsonl(h13)
        continuity = verify_continuity(h13, require_start_at_one=True)
        correspondence = compare_history_extent(history_extent(h13), self.witness_extent)

        self.assertTrue(integrity["ok"])
        self.assertEqual(integrity["record_count"], 13)
        self.assertTrue(continuity.ok)
        self.assertEqual(continuity.record_count, 13)
        self.assertFalse(correspondence.ok)
        self.assertIn({"field": "record_count", "current": 13, "witnessed": 14}, correspondence.mismatches)
        self.assertIn({"field": "terminal_record_id", "current": "rec-000013", "witnessed": "rec-000014"}, correspondence.mismatches)
        self.assertIn({"field": "terminal_commit_index", "current": 13, "witnessed": 14}, correspondence.mismatches)

    def test_correspondence_mismatch_preserves_ambiguity(self) -> None:
        h13 = deepcopy(self.records[:-1])
        result = compare_history_extent(history_extent(h13), self.witness_extent).to_dict()

        self.assertFalse(result["ok"])
        self.assertEqual(result["interpretation"], "extent_correspondence_only_not_corruption_proof")
        self.assertNotIn("ledger_corrupt", result)

    def test_tail_loss_changes_reconstruction_and_projection(self) -> None:
        h13 = deepcopy(self.records[:-1])
        h14_reconstruction = reconstruct_admission_relationships(self.records)
        h13_reconstruction = reconstruct_admission_relationships(h13)
        h14_projection = derive_admitted_projection(h14_reconstruction)
        h13_projection = derive_admitted_projection(h13_reconstruction)
        h13_observation = next(
            observation
            for observation in h13_reconstruction["observations"]
            if observation["observation_record_id"] == "rec-000013"
        )

        self.assertEqual(len(h14_reconstruction["observations"]), 7)
        self.assertEqual(sum(len(observation["admissions"]) for observation in h14_reconstruction["observations"]), 7)
        self.assertEqual(len(h14_projection), 7)
        self.assertEqual(len(h13_reconstruction["observations"]), 7)
        self.assertEqual(sum(len(observation["admissions"]) for observation in h13_reconstruction["observations"]), 6)
        self.assertEqual(len(h13_projection), 6)
        self.assertEqual(h13_observation["admissions"], [])
        self.assertIn("rec-000013", [item["subject_record_id"] for item in h14_projection])
        self.assertNotIn("rec-000013", [item["subject_record_id"] for item in h13_projection])

    def test_pressure_report_preserves_witness_boundary(self) -> None:
        report = run()

        self.assertEqual(report["selected_witness_classification"], "derived experiment witness")
        self.assertTrue(report["h14"]["witness_correspondence"]["ok"])
        self.assertTrue(report["h13_tail_loss_specimen"]["record_integrity"]["ok"])
        self.assertTrue(report["h13_tail_loss_specimen"]["continuity"]["ok"])
        self.assertFalse(report["h13_tail_loss_specimen"]["witness_correspondence"]["ok"])
        self.assertFalse(report["ambiguity_preserved"]["corruption_proven"])
        self.assertFalse(report["new_persistent_architecture_required"])
        self.assertEqual(report["persistent_architecture_added"], [])
        self.assertEqual(report["git_h14_witness"]["classification"], "direct historical representation, not canonical runtime authority")


if __name__ == "__main__":
    unittest.main()
