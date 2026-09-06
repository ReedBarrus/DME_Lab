from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.ledger import (
    HASH_BOUNDARY,
    JsonlLedger,
    amendment_pair,
    identity_collision_envelopes,
    missingness_envelopes,
    ordering_conflict_envelopes,
    preservation_envelope,
)


class LedgerHarnessTest(unittest.TestCase):
    def test_ordering_conflict_replays_in_commit_order(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            for synthetic_envelope in ordering_conflict_envelopes():
                ledger.append(synthetic_envelope)

            replayed = ledger.replay()

        self.assertEqual([record["commit_index"] for record in replayed], [1, 2])
        self.assertEqual([record["envelope"]["source_sequence"] for record in replayed], [2, 1])
        self.assertEqual(
            [record["envelope"]["event_time"] for record in replayed],
            ["2026-09-05T00:00:02Z", "2026-09-05T00:00:01Z"],
        )

    def test_identity_collision_does_not_merge_records(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            for synthetic_envelope in identity_collision_envelopes():
                ledger.append(synthetic_envelope)

            replayed = ledger.replay()

        self.assertEqual(len(replayed), 2)
        self.assertEqual({record["envelope"]["envelope_identity"] for record in replayed}, {"env-dup"})
        self.assertEqual([record["record_id"] for record in replayed], ["rec-000001", "rec-000002"])

    def test_envelope_preservation_does_not_fill_or_drop_structural_distinctions(self) -> None:
        source = preservation_envelope()
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            ledger.append(source)

            replayed = ledger.replay()

        preserved = replayed[0]["envelope"]
        self.assertEqual(preserved, source)
        self.assertIsNone(preserved["signal"]["payload"]["explicit_null"])
        self.assertNotIn("absent_field", preserved["signal"]["payload"])

    def test_integrity_mutation_is_detected(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger = JsonlLedger(ledger_path)
            record = ledger.append(preservation_envelope())
            self.assertEqual(record["integrity"]["boundary"], HASH_BOUNDARY)
            self.assertTrue(ledger.verify().ok)

            text = ledger_path.read_text(encoding="utf-8")
            ledger_path.write_text(text.replace("sig-preserve", "sig-mutated", 1), encoding="utf-8")

            verification = ledger.verify()

        self.assertFalse(verification.ok)
        self.assertEqual(verification.record_count, 1)
        self.assertEqual(len(verification.failures), 1)

    def test_missingness_states_remain_distinct(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            for synthetic_envelope in missingness_envelopes():
                ledger.append(synthetic_envelope)

            replayed = ledger.replay()

        states = [
            next(iter(record["envelope"]["missingness"].values()))
            for record in replayed
        ]
        self.assertEqual(states, ["absent", "explicit_null", "unavailable", "malformed"])

    def test_append_only_amendment_exposes_original_and_later_record(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            for synthetic_envelope in amendment_pair():
                ledger.append(synthetic_envelope)

            replayed = ledger.replay()

        self.assertEqual([record["commit_index"] for record in replayed], [1, 2])
        self.assertEqual(replayed[0]["envelope"]["envelope_identity"], "env-amend-original")
        self.assertEqual(replayed[1]["envelope"]["amendment"]["target_record_id"], "rec-000001")
        self.assertNotIn("resolved", replayed[1]["envelope"]["amendment"])


if __name__ == "__main__":
    unittest.main()

