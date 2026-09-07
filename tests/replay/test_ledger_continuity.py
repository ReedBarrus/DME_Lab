from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.ledger import (
    JsonlLedger,
    canonical_json,
    record_digest,
    replay_canonical_live_ingest,
    verify_canonical_live_ingest,
    verify_canonical_live_ingest_continuity,
    verify_continuity,
)


def _write_records(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="utf-8")


def _rehash(record: dict[str, object]) -> dict[str, object]:
    boundary = {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "envelope": record["envelope"],
    }
    record["integrity"]["digest"] = record_digest(boundary)
    return record


class LedgerContinuityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.canonical_records = replay_canonical_live_ingest()

    def test_control_copy_passes_record_verify_and_continuity(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "control.jsonl"
            _write_records(path, deepcopy(self.canonical_records))

            self.assertTrue(JsonlLedger(path).verify().ok)
            self.assertTrue(verify_continuity(JsonlLedger(path).replay(), require_start_at_one=True).ok)

    def test_whole_record_deletion_preserves_record_integrity_but_fails_continuity(self) -> None:
        records = [deepcopy(record) for record in self.canonical_records if record["record_id"] != "rec-000007"]

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "deleted.jsonl"
            _write_records(path, records)

            record_integrity = JsonlLedger(path).verify()
            continuity = verify_continuity(JsonlLedger(path).replay(), require_start_at_one=True)

        self.assertTrue(record_integrity.ok)
        self.assertFalse(continuity.ok)
        self.assertIn({"kind": "missing_commit_index", "values": [7]}, continuity.failures)

    def test_duplicate_commit_index_with_valid_digest_fails_continuity(self) -> None:
        records = deepcopy(self.canonical_records)
        records[3]["commit_index"] = 2
        _rehash(records[3])

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "duplicate-index.jsonl"
            _write_records(path, records)

            record_integrity = JsonlLedger(path).verify()
            continuity = verify_continuity(JsonlLedger(path).replay(), require_start_at_one=True)

        self.assertTrue(record_integrity.ok)
        self.assertFalse(continuity.ok)
        self.assertIn({"kind": "duplicate_commit_index", "values": [2]}, continuity.failures)
        self.assertIn({"kind": "missing_commit_index", "values": [4]}, continuity.failures)

    def test_duplicate_record_id_with_valid_digest_fails_continuity(self) -> None:
        records = deepcopy(self.canonical_records)
        records[3]["record_id"] = "rec-000002"
        _rehash(records[3])

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "duplicate-record-id.jsonl"
            _write_records(path, records)

            record_integrity = JsonlLedger(path).verify()
            continuity = verify_continuity(JsonlLedger(path).replay(), require_start_at_one=True)

        self.assertTrue(record_integrity.ok)
        self.assertFalse(continuity.ok)
        self.assertIn({"kind": "duplicate_record_id", "values": ["rec-000002"]}, continuity.failures)

    def test_reversed_physical_lines_keep_canonical_continuity(self) -> None:
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "reversed.jsonl"
            _write_records(path, list(reversed(deepcopy(self.canonical_records))))
            ledger = JsonlLedger(path)

            self.assertTrue(ledger.verify().ok)
            self.assertEqual(
                [record["commit_index"] for record in ledger.replay()],
                [record["commit_index"] for record in self.canonical_records],
            )
            self.assertTrue(verify_continuity(ledger.replay(), require_start_at_one=True).ok)

    def test_generic_continuity_does_not_require_start_at_one(self) -> None:
        records = deepcopy(self.canonical_records[1:])

        self.assertTrue(verify_continuity(records).ok)
        self.assertFalse(verify_continuity(records, require_start_at_one=True).ok)

    def test_current_canonical_live_history_passes_continuity(self) -> None:
        record_integrity = verify_canonical_live_ingest()
        continuity = verify_canonical_live_ingest_continuity()

        self.assertTrue(record_integrity.ok)
        self.assertTrue(continuity.ok)
        self.assertEqual(record_integrity.record_count, 14)
        self.assertEqual(continuity.record_count, 14)


if __name__ == "__main__":
    unittest.main()
