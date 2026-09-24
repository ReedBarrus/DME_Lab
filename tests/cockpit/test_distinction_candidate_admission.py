from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from src.cockpit.distinction_candidate_admission import (
    ADMISSION_REGISTRY_RELATIVE_PATH,
    DistinctionAdmissionBindingError,
    build_admission_record,
    build_candidate_admission_cell,
    candidate_digest,
    derive_admitted_distinction,
    load_admission_records,
)
from src.cockpit.typed_distinction_registry import (
    REGISTRY_RELATIVE_PATH,
    evaluate_distinction_record,
    load_registry_records,
)


ROOT = Path(__file__).resolve().parents[2]


def temporal_fixture(record: dict) -> dict:
    frames = []
    transitions = []
    for index, handle in enumerate(record["source_handles"]):
        before = {
            "frame_id": f"frame-{index}-before",
            "commit_sha": handle["from_commit_sha"],
            "tree_sha": handle["from_tree_sha"],
        }
        after = {
            "frame_id": f"frame-{index}-after",
            "commit_sha": handle["to_commit_sha"],
            "tree_sha": handle["to_tree_sha"],
        }
        frames.extend((before, after))
        transitions.append({
            "transition_id": f"transition-{index}",
            "from_commit_sha": before["commit_sha"],
            "to_commit_sha": after["commit_sha"],
            "events": [{
                "event_id": f"event-{index}",
                "old_path": handle["path"],
                "new_path": handle["path"],
                "old_object_sha": handle["old_blob_sha"],
                "new_object_sha": handle["new_blob_sha"],
                "identity_basis": "SAME_PATH_ADJACENT_FIRST_PARENT_FRAMES",
                "classifications": ["PERSISTED", "CONTENT_CHANGED"],
            }],
        })
    return {
        "object_type": "REPOSITORY_TEMPORAL_LINEAGE_V0",
        "repository_identity": "ReedBarrus/DME_Lab",
        "source_commit": "f" * 40,
        "frames": frames,
        "transitions": transitions,
    }


class CandidateAdmissionCell001Test(unittest.TestCase):
    """Focused D001 binding pressure. Source seat: LABBOIB / QWEN."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.candidate = load_registry_records(ROOT / REGISTRY_RELATIVE_PATH)[0]
        cls.admission_record = load_admission_records(
            ROOT / ADMISSION_REGISTRY_RELATIVE_PATH
        )[0]
        cls.temporal = temporal_fixture(cls.candidate)
        cls.evaluation = evaluate_distinction_record(
            deepcopy(cls.candidate),
            deepcopy(cls.temporal),
        )

    def test_admission_record_matches_unchanged_evaluator(self) -> None:
        expected = build_admission_record(self.candidate, self.evaluation)
        self.assertEqual(self.admission_record, expected)
        self.assertEqual(
            self.admission_record["candidate_digest"],
            candidate_digest(self.candidate),
        )
        self.assertEqual(
            self.admission_record["materialized_by"],
            {"seat": "LABBOIB", "model": "QWEN"},
        )

    def test_candidate_remains_candidate_and_admitted_is_derived(self) -> None:
        self.assertEqual(
            self.candidate["standing"],
            "CANDIDATE_FOR_BOUNDED_ADMISSION",
        )
        admitted = derive_admitted_distinction(
            self.candidate,
            self.admission_record,
        )
        self.assertEqual(admitted["candidate_standing"], "CANDIDATE_FOR_BOUNDED_ADMISSION")
        self.assertEqual(admitted["standing"], "ADMITTED_BOUNDED")
        self.assertEqual(admitted["authority_effect"], "NONE")

    def test_fresh_reconstruction_equivalent_to_legacy_path(self) -> None:
        result = build_candidate_admission_cell(
            candidate=self.candidate,
            admission_record=self.admission_record,
            temporal_lineage=self.temporal,
        )
        self.assertEqual(
            result["conservation"]["result"],
            "SAME_BOUNDED_POSTURE",
        )
        self.assertEqual(result["conservation"]["mismatches"], [])
        self.assertEqual(
            result["reconstruction_result"]["exact_distinction"],
            "PATH_IDENTITY != CONTENT_IDENTITY",
        )
        self.assertEqual(
            result["reconstruction_result"]["does_not_establish"],
            self.candidate["claim_ceiling"],
        )
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["control_effect"], "NONE")

    def assert_binding_rejected(self, candidate: dict, admission: dict, pattern: str) -> None:
        with self.assertRaisesRegex(DistinctionAdmissionBindingError, pattern):
            derive_admitted_distinction(candidate, admission)

    def test_negative_wrong_candidate_digest_fails_closed(self) -> None:
        admission = deepcopy(self.admission_record)
        admission["candidate_digest"] = "sha256:" + "0" * 64
        self.assert_binding_rejected(
            deepcopy(self.candidate),
            admission,
            "candidate digest binding mismatch",
        )

    def test_negative_mutated_candidate_after_admission_fails_closed(self) -> None:
        candidate = deepcopy(self.candidate)
        candidate["unresolved"] = candidate["unresolved"] + ["POST_ADMISSION_MUTATION"]
        self.assert_binding_rejected(
            candidate,
            deepcopy(self.admission_record),
            "candidate digest binding mismatch",
        )

    def test_negative_non_admitted_decision_fails_closed(self) -> None:
        admission = deepcopy(self.admission_record)
        admission["decision"] = "NOT_ADMITTED"
        self.assert_binding_rejected(
            deepcopy(self.candidate),
            admission,
            "admission decision is not ADMITTED_BOUNDED",
        )

    def test_negative_unresolved_decision_fails_closed(self) -> None:
        admission = deepcopy(self.admission_record)
        admission["decision"] = "UNRESOLVED"
        self.assert_binding_rejected(
            deepcopy(self.candidate),
            admission,
            "admission decision is not ADMITTED_BOUNDED",
        )

    def test_negative_record_for_wrong_candidate_fails_closed(self) -> None:
        admission = deepcopy(self.admission_record)
        admission["distinction_id"] = "DISTINCTION_OTHER_001"
        self.assert_binding_rejected(
            deepcopy(self.candidate),
            admission,
            "admission record targets wrong candidate",
        )

    def test_negative_changed_claim_ceiling_after_admission_fails_closed(self) -> None:
        candidate = deepcopy(self.candidate)
        candidate["claim_ceiling"] += " broadened"
        self.assert_binding_rejected(
            candidate,
            deepcopy(self.admission_record),
            "candidate digest binding mismatch",
        )


if __name__ == "__main__":
    unittest.main()
