from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.ingest import (
    COMPARATOR_IDENTITY,
    COMPARATOR_V0,
    COMPARATOR_V0_EVENT_TIME_REQUIRED,
    append_admission,
    append_observation,
    derive_admitted_projection,
    make_admission_envelope,
    reconstruct_admission_lineage,
)
from src.ledger import JsonlLedger
from src.runtime.repo_provenance_pressure import make_snapshot_ingest_envelope
from src.runtime.repo_transition_pressure import make_git_ingest_envelope


def filesystem_candidate() -> dict[str, object]:
    return make_snapshot_ingest_envelope(
        {
            "snapshot_id": "repo-snapshot-v0:test",
            "observer": "repo_snapshot",
            "observer_version": "repo_snapshot_v0",
            "observation_started_at": "t0",
            "observation_finished_at": "t1",
            "root_identity": {"kind": "repository_working_tree", "name": "fixture"},
            "scope": {"root": ".", "included": ["working_tree_files"], "excluded_dirs": [], "excluded_globs": []},
            "entries": [],
            "capture_errors": [],
            "duration_seconds": 0.0,
        }
    )


def git_candidate() -> dict[str, object]:
    return make_git_ingest_envelope(
        {
            "observation_id": "git-state-v0:test",
            "observer": "git_state",
            "observer_version": "git_state_v0",
            "observed_at": "t1",
            "root_identity": {"kind": "repository_working_tree", "name": "fixture"},
            "head_sha": "abc",
            "branch": "main",
            "status_porcelain": [],
            "capture_errors": [],
        }
    )


class IngestAdmissionTest(unittest.TestCase):
    def test_structurally_valid_filesystem_candidate_enters_admitted_projection(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            observation = append_observation(ledger, filesystem_candidate(), source="repository_filesystem_snapshot")
            admission = append_admission(ledger, observation)
            replayed = ledger.replay()

        projection = derive_admitted_projection(replayed)
        lineage = reconstruct_admission_lineage(replayed)

        self.assertEqual(observation["envelope"]["record_type"], "observation")
        self.assertEqual(admission["envelope"]["record_type"], "admission")
        self.assertEqual(admission["envelope"]["decision"], "admitted")
        self.assertEqual(projection[0]["subject_record_id"], observation["record_id"])
        self.assertTrue(lineage[0]["participates_in_admitted_projection"])

    def test_structurally_valid_git_candidate_enters_admitted_projection(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            observation = append_observation(ledger, git_candidate(), source="repository_git_state")
            admission = append_admission(ledger, observation)
            replayed = ledger.replay()

        self.assertEqual(admission["envelope"]["decision"], "admitted")
        self.assertEqual(derive_admitted_projection(replayed)[0]["subject_record_id"], observation["record_id"])

    def test_malformed_required_field_is_rejected_without_deleting_observation(self) -> None:
        malformed = {"envelope_identity": "malformed", "source": "fixture"}
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            observation = append_observation(ledger, malformed, source="malformed_fixture")
            admission = append_admission(ledger, observation)
            replayed = ledger.replay()

        lineage = reconstruct_admission_lineage(replayed)

        self.assertEqual([record["envelope"]["record_type"] for record in replayed], ["observation", "admission"])
        self.assertEqual(admission["envelope"]["decision"], "rejected")
        self.assertFalse(derive_admitted_projection(replayed))
        self.assertEqual(lineage[0]["observation"], malformed)
        self.assertFalse(lineage[0]["participates_in_admitted_projection"])

    def test_non_json_admissible_value_is_preserved_and_rejected_by_comparison(self) -> None:
        candidate = filesystem_candidate()
        candidate["signal"]["payload"] = {"non_json_number": math.nan}  # type: ignore[index]
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            observation = append_observation(ledger, candidate, source="non_json_fixture")
            admission = append_admission(ledger, observation)
            replayed = ledger.replay()

        replayed_value = replayed[0]["envelope"]["observation"]["signal"]["payload"]["non_json_number"]

        self.assertTrue(math.isnan(replayed_value))
        self.assertEqual(admission["envelope"]["decision"], "rejected")
        self.assertEqual(admission["envelope"]["comparison_result"]["errors"][0]["validator"], "json_domain")
        self.assertFalse(derive_admitted_projection(replayed))

    def test_same_observation_can_have_two_comparator_version_records(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            observation = append_observation(ledger, filesystem_candidate(), source="repository_filesystem_snapshot")
            first = append_admission(ledger, observation, comparator_version=COMPARATOR_V0)
            second = append_admission(ledger, observation, comparator_version=COMPARATOR_V0_EVENT_TIME_REQUIRED)
            replayed = ledger.replay()

        lineage = reconstruct_admission_lineage(replayed)[0]

        self.assertEqual(first["envelope"]["decision"], "admitted")
        self.assertEqual(second["envelope"]["decision"], "rejected")
        self.assertEqual(len(lineage["admission_records"]), 2)
        self.assertEqual(lineage["subject_record_id"], observation["record_id"])
        self.assertEqual(replayed[0]["envelope"]["observation"], filesystem_candidate())

    def test_unknown_comparator_version_records_unresolved_decision(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            observation = append_observation(ledger, filesystem_candidate(), source="repository_filesystem_snapshot")
            admission = append_admission(ledger, observation, comparator_version="unknown_v0")
            replayed = ledger.replay()

        self.assertEqual(admission["envelope"]["decision"], "unresolved")
        self.assertEqual(admission["envelope"]["comparison_result"]["status"], "unavailable")
        self.assertFalse(derive_admitted_projection(replayed))

    def test_admission_record_shape_is_minimal(self) -> None:
        envelope = make_admission_envelope(
            {
                "record_id": "rec-000001",
                "commit_index": 1,
                "envelope": {
                    "record_type": "observation",
                    "source": "fixture",
                    "observation": filesystem_candidate(),
                    "provenance": {},
                },
                "integrity": {},
            }
        )

        self.assertEqual(
            set(envelope),
            {
                "record_type",
                "subject_record_id",
                "comparator_identity",
                "comparator_version",
                "comparison_result",
                "decision",
                "decision_basis",
            },
        )
        self.assertEqual(envelope["comparator_identity"], COMPARATOR_IDENTITY)


if __name__ == "__main__":
    unittest.main()
