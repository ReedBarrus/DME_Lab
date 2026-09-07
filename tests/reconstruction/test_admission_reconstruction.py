from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.ingest import (
    COMPARATOR_V0,
    COMPARATOR_V0_EVENT_TIME_REQUIRED,
    append_admission,
    append_observation,
)
from src.ledger import JsonlLedger
from src.reconstruction import (
    derive_admitted_projection,
    derive_non_admitted_decision_states,
    reconstruct_admission_relationships,
)
from tests.ingest.test_admission import filesystem_candidate, git_candidate


def replay_pressure_records() -> list[dict[str, object]]:
    with TemporaryDirectory() as tmpdir:
        ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
        filesystem = append_observation(ledger, filesystem_candidate(), source="repository_filesystem_snapshot", provenance={"fixture": "fs"})
        append_admission(ledger, filesystem, comparator_version=COMPARATOR_V0)
        append_admission(ledger, filesystem, comparator_version=COMPARATOR_V0_EVENT_TIME_REQUIRED)
        git = append_observation(ledger, git_candidate(), source="repository_git_state", provenance={"fixture": "git"})
        append_admission(ledger, git, comparator_version=COMPARATOR_V0)
        malformed = append_observation(ledger, {"envelope_identity": "bad"}, source="malformed_fixture", provenance={"fixture": "bad"})
        append_admission(ledger, malformed, comparator_version=COMPARATOR_V0)
        append_admission(ledger, git, comparator_version="unknown_v0")
        return ledger.replay()


class AdmissionReconstructionTest(unittest.TestCase):
    def test_same_replay_rebuilds_same_reconstruction_and_projection(self) -> None:
        replayed = replay_pressure_records()

        first = reconstruct_admission_relationships(replayed)
        first_projection = derive_admitted_projection(first)
        second = reconstruct_admission_relationships(replayed)
        second_projection = derive_admitted_projection(second)

        self.assertEqual(first, second)
        self.assertEqual(first_projection, second_projection)

    def test_reconstruction_preserves_authoritative_record_references(self) -> None:
        replayed = replay_pressure_records()

        reconstruction = reconstruct_admission_relationships(replayed)

        self.assertEqual(reconstruction["authoritative_record_ids"], [record["record_id"] for record in replayed])
        for observation in reconstruction["observations"]:
            self.assertIn(observation["observation_record_id"], reconstruction["authoritative_record_ids"])
            for admission in observation["admissions"]:
                self.assertIn(admission["admission_record_id"], reconstruction["authoritative_record_ids"])
                self.assertEqual(admission["subject_record_id"], observation["observation_record_id"])

    def test_provenance_navigation_survives_reconstruction(self) -> None:
        replayed = replay_pressure_records()

        reconstruction = reconstruct_admission_relationships(replayed)
        filesystem = reconstruction["observations"][0]
        admission = filesystem["admissions"][0]

        self.assertEqual(filesystem["observation_record_id"], "rec-000001")
        self.assertEqual(filesystem["source"], "repository_filesystem_snapshot")
        self.assertEqual(filesystem["provenance"], {"fixture": "fs"})
        self.assertEqual(filesystem["admission_record_ids"], ["rec-000002", "rec-000003"])
        self.assertEqual(admission["comparator_identity"], "ingest_candidate_envelope_minimum")
        self.assertEqual(admission["comparator_version"], COMPARATOR_V0)
        self.assertTrue(admission["comparison_result"]["valid"])
        self.assertEqual(admission["decision"], "admitted")
        self.assertEqual(admission["decision_basis"], "comparison valid under comparator")
        self.assertTrue(filesystem["participates_in_admitted_projection"])

    def test_multiple_comparator_versions_are_preserved_without_conflict_resolution(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())
        filesystem = reconstruction["observations"][0]

        self.assertEqual(
            [(admission["comparator_version"], admission["decision"]) for admission in filesystem["admissions"]],
            [
                (COMPARATOR_V0, "admitted"),
                (COMPARATOR_V0_EVENT_TIME_REQUIRED, "rejected"),
            ],
        )
        self.assertTrue(filesystem["participates_in_admitted_projection"])

    def test_projection_consumes_reconstruction(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())

        projection = derive_admitted_projection(reconstruction)

        self.assertEqual([item["subject_record_id"] for item in projection], ["rec-000001", "rec-000004"])
        self.assertEqual([item["reconstruction_type"] for item in projection], ["admission_relationships_v0", "admission_relationships_v0"])

    def test_rejected_and_unresolved_relations_remain_reconstructed_but_not_projected(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())
        projection_ids = {item["subject_record_id"] for item in derive_admitted_projection(reconstruction)}
        malformed = next(item for item in reconstruction["observations"] if item["source"] == "malformed_fixture")
        git = next(item for item in reconstruction["observations"] if item["source"] == "repository_git_state")

        self.assertEqual(malformed["admissions"][0]["decision"], "rejected")
        self.assertEqual(git["admissions"][1]["decision"], "unresolved")
        self.assertNotIn(malformed["observation_record_id"], projection_ids)

    def test_reconstruction_is_not_raw_replay(self) -> None:
        replayed = replay_pressure_records()

        reconstruction = reconstruct_admission_relationships(replayed)

        self.assertNotEqual(reconstruction, replayed)
        self.assertEqual(reconstruction["reconstruction_type"], "admission_relationships_v0")
        self.assertNotIn("integrity", reconstruction["observations"][0])

    def test_non_admitted_decision_states_expose_rejected_and_unresolved(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())
        projection = derive_admitted_projection(reconstruction)

        companion = derive_non_admitted_decision_states(reconstruction, projection)

        self.assertEqual(
            companion,
            [
                {
                    "subject_record_id": "rec-000001",
                    "non_admitted_decision_states": ["rejected"],
                },
                {
                    "subject_record_id": "rec-000004",
                    "non_admitted_decision_states": ["unresolved"],
                },
            ],
        )

    def test_decision_states_companion_does_not_expand_projection(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())
        projection = derive_admitted_projection(reconstruction)

        companion = derive_non_admitted_decision_states(reconstruction, projection)

        self.assertEqual(
            [item["subject_record_id"] for item in companion],
            [item["subject_record_id"] for item in projection],
        )
        self.assertNotIn("rec-000006", [item["subject_record_id"] for item in companion])

    def test_decision_states_companion_is_deterministic_and_read_only(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())
        projection = derive_admitted_projection(reconstruction)
        reconstruction_before = deepcopy(reconstruction)
        projection_before = deepcopy(projection)

        first = derive_non_admitted_decision_states(reconstruction, projection)
        second = derive_non_admitted_decision_states(reconstruction, projection)

        self.assertEqual(first, second)
        self.assertEqual(reconstruction, reconstruction_before)
        self.assertEqual(projection, projection_before)

    def test_decision_states_subject_id_navigates_to_full_evidence(self) -> None:
        reconstruction = reconstruct_admission_relationships(replay_pressure_records())
        projection = derive_admitted_projection(reconstruction)
        companion = derive_non_admitted_decision_states(reconstruction, projection)
        by_id = {
            item["observation_record_id"]: item
            for item in reconstruction["observations"]
        }

        for item in companion:
            recovered = by_id[item["subject_record_id"]]["admissions"]
            self.assertTrue(recovered)
            self.assertTrue(
                all(
                    admission["subject_record_id"] == item["subject_record_id"]
                    for admission in recovered
                )
            )


if __name__ == "__main__":
    unittest.main()
