from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.cockpit.repository_temporal_lineage import build_repository_temporal_lineage
from src.cockpit.typed_distinction_registry import (
    CELL_ID,
    REGISTRY_RELATIVE_PATH,
    TypedDistinctionRegistryError,
    build_reconstruction_packet,
    build_typed_distinction_registry_projection,
    build_unavailable_typed_distinction_registry_projection,
    evaluate_distinction_record,
    generate_typed_distinction_registry_projection,
    load_registry_records,
    reconstruct_distinction,
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


class TypedDistinctionRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_path = ROOT / REGISTRY_RELATIVE_PATH
        cls.record = load_registry_records(cls.registry_path)[0]
        cls.temporal = temporal_fixture(cls.record)

    def evaluate(self, record: dict | None = None, temporal: dict | None = None) -> dict:
        return evaluate_distinction_record(
            record or deepcopy(self.record),
            temporal or deepcopy(self.temporal),
        )

    def test_schema_and_exact_cell_are_admitted_bounded(self) -> None:
        result = self.evaluate()
        self.assertEqual(result["distinction_id"], CELL_ID)
        self.assertEqual(result["standing"], "ADMITTED_BOUNDED")
        self.assertEqual(result["admission_reason"], "EXACT_MECHANICAL_SPECIMEN_RESOLVED")
        self.assertEqual(result["relation_type"], "NOT_EQUAL")
        self.assertEqual(result["value"], {
            "left": "PATH_IDENTITY", "right": "CONTENT_IDENTITY",
        })
        self.assertEqual(len(result["resolved_source_handles"]), 2)
        self.assertEqual(result["authority_effect"], "NONE")

    def test_real_committed_history_resolves_the_canonical_cell(self) -> None:
        lineage = build_repository_temporal_lineage(
            ROOT,
            source_ref="HEAD",
            repository_identity="ReedBarrus/DME_Lab",
        )
        result = evaluate_distinction_record(self.record, lineage)
        self.assertEqual(result["standing"], "ADMITTED_BOUNDED")
        self.assertEqual(
            [
                (item["from_commit_sha"], item["to_commit_sha"],
                 item["old_blob_sha"], item["new_blob_sha"])
                for item in result["resolved_source_handles"]
            ],
            [
                (
                    "32b22057af4e38b33d5fe69c2658466281f33e0b",
                    "dd9da1053a9c4d698c417d7c5e6c4a55f613087d",
                    "36f7d4917c32692b5810173a3bee5ad731f46a9c",
                    "55ce3ccb04953c1c5543f3653179322fd524370c",
                ),
                (
                    "e3675ca361fdb19ea5b66c5e5071430cf9cacf5d",
                    "2f3dd79d5d25c79f5ec69cae8767fef2f45e96bc",
                    "55ce3ccb04953c1c5543f3653179322fd524370c",
                    "a13686287296e9e191799c3a999676afb15f2d23",
                ),
            ],
        )

    def test_P01_wrong_subject_is_not_admitted(self) -> None:
        record = deepcopy(self.record)
        record["subject_addresses"][0]["path"] = "src/cockpit/observer/not-the-subject.mjs"
        self.assertEqual(self.evaluate(record)["standing"], "NOT_ADMITTED")

    def test_P02_same_blob_only_is_insufficient(self) -> None:
        record = deepcopy(self.record)
        temporal = temporal_fixture(record)
        handle = record["source_handles"][0]
        handle["new_blob_sha"] = handle["old_blob_sha"]
        event = temporal["transitions"][0]["events"][0]
        event["new_object_sha"] = event["old_object_sha"]
        result = self.evaluate(record, temporal)
        self.assertEqual(result["standing"], "NOT_ADMITTED")
        self.assertEqual(result["admission_reason"], "DISTINCT_CONTENT_IDENTITIES_REQUIRED")

    def test_P03_missing_source_handle_degrades_to_unresolved(self) -> None:
        record = deepcopy(self.record)
        record["source_handles"] = []
        result = self.evaluate(record)
        self.assertEqual(result["standing"], "UNRESOLVED")
        self.assertEqual(result["admission_reason"], "SOURCE_HANDLE_REQUIRED")

    def test_P04_missing_claim_ceiling_fails_admission(self) -> None:
        record = deepcopy(self.record)
        del record["claim_ceiling"]
        self.assertEqual(self.evaluate(record)["standing"], "NOT_ADMITTED")

    def test_P05_historical_specimen_cannot_claim_current(self) -> None:
        record = deepcopy(self.record)
        record["currentness"] = "CURRENT"
        result = self.evaluate(record)
        self.assertEqual(result["standing"], "NOT_ADMITTED")
        self.assertEqual(result["admission_reason"], "HISTORICAL_SPECIMEN_CANNOT_BE_CURRENT")

    def test_P06_path_without_content_comparison_is_unresolved(self) -> None:
        record = deepcopy(self.record)
        del record["source_handles"][0]["old_blob_sha"]
        result = self.evaluate(record)
        self.assertEqual(result["standing"], "UNRESOLVED")
        self.assertEqual(result["admission_reason"], "CONTENT_COMPARISON_OR_FRAME_HANDLE_ABSENT")

    def test_P08_reconstruction_scope_expansion_fails(self) -> None:
        admitted = self.evaluate()
        packet = build_reconstruction_packet(admitted)
        packet["subject_address"] = {
            **packet["subject_address"], "path": "src/cockpit/observer/*.mjs",
        }
        with self.assertRaisesRegex(TypedDistinctionRegistryError, "bounded posture"):
            reconstruct_distinction(packet, [admitted])

    def test_P09_broken_provenance_fails_closed(self) -> None:
        record = deepcopy(self.record)
        record["source_handles"][0]["to_commit_sha"] = "0" * 40
        result = self.evaluate(record)
        self.assertEqual(result["standing"], "UNRESOLVED")
        self.assertEqual(result["admission_reason"], "SOURCE_FRAME_OR_TRANSITION_UNAVAILABLE")

    def test_P10_relation_record_cannot_produce_authority_effect(self) -> None:
        record = deepcopy(self.record)
        record["authority_effect"] = "ACTIVE"
        result = self.evaluate(record)
        self.assertEqual(result["standing"], "NOT_ADMITTED")
        self.assertEqual(result["admission_reason"], "NON_NONE_EFFECT_FORBIDDEN")

    def test_fresh_reconstruction_conserves_operational_posture(self) -> None:
        admitted = self.evaluate()
        packet = build_reconstruction_packet(admitted)
        self.assertEqual(set(packet), {
            "packet_type", "distinction_address", "subject_address", "source_handles",
            "current_standing", "claim_ceiling", "dependencies", "unresolved",
        })
        result = reconstruct_distinction(packet, [admitted])
        self.assertEqual(result["exact_distinction"], "PATH_IDENTITY != CONTENT_IDENTITY")
        self.assertEqual(result["applies_to"], admitted["scope"])
        self.assertEqual(result["current_standing"], "ADMITTED_BOUNDED")
        self.assertEqual(result["unresolved"], admitted["unresolved"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_projection_generation_is_atomic_and_separates_canonical_source(self) -> None:
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "generated" / "registry.json"
            projection = generate_typed_distinction_registry_projection(
                registry_path=self.registry_path,
                temporal_lineage=self.temporal,
                output=output,
            )
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), projection)
            self.assertEqual(projection["counts"]["admitted_bounded"], 1)
            self.assertEqual(projection["authority_effect"], "NONE")
            self.assertFalse(output.with_name("registry.json.tmp").exists())

    def test_unavailable_overlay_preserves_zero_effect_and_temporal_coordinate(self) -> None:
        projection = build_unavailable_typed_distinction_registry_projection(
            registry_path=self.registry_path,
            temporal_lineage=self.temporal,
            reason="fixture unavailable",
        )
        self.assertEqual(projection["projection_standing"], "UNAVAILABLE")
        self.assertEqual(projection["records"], [])
        self.assertEqual(projection["authority_effect"], "NONE")
        self.assertEqual(projection["execution_effect"], "NONE")
        self.assertEqual(projection["control_effect"], "NONE")
        self.assertEqual(
            projection["temporal_source_commit"],
            self.temporal["source_commit"],
        )
        self.assertEqual(
            projection["source_registry"]["path"],
            REGISTRY_RELATIVE_PATH.as_posix(),
        )

    def test_projection_builder_never_mutates_canonical_record(self) -> None:
        before = self.registry_path.read_bytes()
        projection = build_typed_distinction_registry_projection(
            self.registry_path, self.temporal,
        )
        self.assertEqual(self.registry_path.read_bytes(), before)
        self.assertEqual(projection["records"][0]["standing"], "ADMITTED_BOUNDED")


if __name__ == "__main__":
    unittest.main()
