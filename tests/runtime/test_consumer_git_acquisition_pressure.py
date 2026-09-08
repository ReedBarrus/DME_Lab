from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.ledger import JsonlLedger
from src.reconstruction import reconstruct_admission_relationships
from src.runtime.consumer_git_acquisition_pressure import digest, run, serialized
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


class ConsumerGitAcquisitionPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.c0 = cls.report["cases"]["C0"]
        cls.s1 = cls.report["cases"]["S1"]

    def test_opposite_acquisition_outcomes_have_equal_complete_results(self) -> None:
        self.assertEqual(
            serialized(self.c0["current_result"]),
            serialized(self.s1["current_result"]),
        )
        self.assertTrue(self.report["comparison"]["complete_object_equality"])
        self.assertFalse(self.report["comparison"]["normalization_applied"])
        self.assertEqual(self.c0["historical_git"]["capture_errors"], [])
        self.assertTrue(self.c0["historical_git"]["head_sha"])
        self.assertEqual(self.c0["historical_git"]["branch"], "main")
        self.assertEqual(self.c0["historical_git"]["status_porcelain"], [])
        self.assertEqual(len(self.s1["historical_git"]["capture_errors"]), 3)
        for field in ("head_sha", "branch", "status_porcelain"):
            self.assertIsNone(self.s1["historical_git"][field])

    def test_distinguishing_history_is_recoverable_without_append(self) -> None:
        self.assertNotEqual(self.c0["ledger_sha256"], self.s1["ledger_sha256"])
        for case in (self.c0, self.s1):
            recovery = case["recovery"]
            self.assertEqual(recovery["observation_record_id"], "rec-000002")
            self.assertEqual(recovery["source"], "repository_git_state")
            self.assertEqual(recovery["decision"], "admitted")
            self.assertTrue(recovery["payload_matches_raw"])
            self.assertTrue(recovery["read_was_append_free"])
        canonical = self.report["canonical_history"]
        self.assertEqual(
            canonical["working_file_sha256_before"],
            canonical["working_file_sha256_after"],
        )

    def test_recorded_ledgers_reproduce_results_and_git_payloads(self) -> None:
        trace = json.loads(
            Path("traces/consumer_git_acquisition_pressure_v0.json").read_text(
                encoding="utf-8"
            )
        )
        with TemporaryDirectory(prefix="dme-consumer-replay-") as temporary:
            for label, case in trace["cases"].items():
                history = Path(temporary) / f"{label}.jsonl"
                original = case["ledger_jsonl"].encode("utf-8")
                history.write_bytes(original)
                self.assertEqual(
                    hashlib.sha256(original).hexdigest(), case["ledger_sha256"]
                )
                self.assertTrue(JsonlLedger(history).verify().ok)
                coordinator = ForegroundRepositoryObservationCoordinator.open(
                    Path(temporary) / "absent", history
                )
                replayed = coordinator.current_result()
                coordinator.close()
                self.assertEqual(replayed, case["current_result"])
                self.assertEqual(digest(replayed), case["current_result_sha256"])
                self.assertEqual(history.read_bytes(), original)

                reconstruction = reconstruct_admission_relationships(
                    JsonlLedger(history).replay()
                )
                git = next(
                    item
                    for item in reconstruction["observations"]
                    if item["source"] == "repository_git_state"
                )
                self.assertEqual(
                    git["observation"]["signal"]["payload"]["capture_errors"],
                    case["recovery"]["capture_errors"],
                )


if __name__ == "__main__":
    unittest.main()
