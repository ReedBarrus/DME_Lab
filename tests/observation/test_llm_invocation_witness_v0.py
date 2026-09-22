from __future__ import annotations

import subprocess
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock

from src.observation.llm_invocation_witness_v0 import (
    MODEL_CLAIM_ABOUT_TOOL_RESULT,
    TOOL_REQUEST,
    TOOL_RESULT,
    UNRESOLVED,
    build_raw_invocation_witness,
)


class RawInvocationWitnessV0Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.specimen = {
            "invocation_id": "INVOCATION-WITNESS-SYNTHETIC-001",
            "input_identity": "sha256:fixed-input-identity",
            "raw_input_ref": "fixture://invocation-001/raw-input",
            "adapter_identity": "repository-local-deterministic-adapter-v0",
            "declared_basis_refs": ["fixture://invocation-001/declared-basis"],
            "tool_trace_refs": [],
            "raw_output_identity": "sha256:fixed-output-identity",
            "raw_output_ref": "fixture://invocation-001/raw-output",
            "external_crossing_refs": [],
            "observer_limitations": [
                "tool-trace completeness is not established",
                "external effects are not observed by this witness",
            ],
        }

    def build(self, **changes: object) -> dict[str, object]:
        supplied = deepcopy(self.specimen)
        supplied.update(changes)
        return build_raw_invocation_witness(**supplied)

    def test_fixed_specimen_is_deterministic(self) -> None:
        self.assertEqual(self.build(), self.build())

    def test_raw_input_identity_and_reference_are_preserved(self) -> None:
        witness = self.build()
        self.assertEqual(witness["input_identity"], self.specimen["input_identity"])
        self.assertEqual(witness["raw_input_ref"], self.specimen["raw_input_ref"])

    def test_raw_output_identity_and_reference_are_preserved(self) -> None:
        witness = self.build()
        self.assertEqual(witness["raw_output_identity"], self.specimen["raw_output_identity"])
        self.assertEqual(witness["raw_output_ref"], self.specimen["raw_output_ref"])

    def test_adapter_identity_is_explicit_and_measured(self) -> None:
        witness = self.build()
        self.assertEqual(
            witness["adapter_identity"],
            "repository-local-deterministic-adapter-v0",
        )
        self.assertIn("adapter_identity", witness["measured_fields"])

    def test_unavailable_model_and_frame_metadata_remain_unresolved(self) -> None:
        witness = self.build()
        self.assertEqual(witness["model_identity"], UNRESOLVED)
        self.assertEqual(witness["start_frame_ref"], UNRESOLVED)
        self.assertEqual(witness["end_frame_ref"], UNRESOLVED)
        self.assertEqual(
            witness["unresolved_fields"],
            [
                "tool_trace_completeness",
                "external_effect",
                "model_identity",
                "start_frame_ref",
                "end_frame_ref",
            ],
        )

    def test_tool_request_result_and_model_claim_remain_distinct(self) -> None:
        traces = [
            {"ordinal": 1, "kind": TOOL_REQUEST, "raw_ref": "trace://request/1"},
            {"ordinal": 2, "kind": TOOL_RESULT, "raw_ref": "trace://result/1"},
            {
                "ordinal": 3,
                "kind": MODEL_CLAIM_ABOUT_TOOL_RESULT,
                "raw_ref": "trace://model-claim/1",
            },
        ]
        witness = self.build(tool_trace_refs=traces)
        self.assertEqual(witness["tool_trace_refs"], traces)
        self.assertEqual(
            [entry["kind"] for entry in witness["tool_trace_refs"]],
            [TOOL_REQUEST, TOOL_RESULT, MODEL_CLAIM_ABOUT_TOOL_RESULT],
        )

    def test_external_effect_is_not_inferred_from_trace_or_model_claim(self) -> None:
        witness = self.build(
            tool_trace_refs=[
                {"ordinal": 1, "kind": TOOL_REQUEST, "raw_ref": "trace://request/1"},
                {"ordinal": 2, "kind": TOOL_RESULT, "raw_ref": "trace://result/1"},
                {
                    "ordinal": 3,
                    "kind": MODEL_CLAIM_ABOUT_TOOL_RESULT,
                    "raw_ref": "trace://model-claim/1",
                },
            ],
            external_crossing_refs=["trace://external-crossing/1"],
        )
        self.assertIn("external_effect", witness["unresolved_fields"])
        self.assertNotIn("external_effect", witness["measured_fields"])
        self.assertNotIn("external_effect", witness)

    def test_observer_limitations_are_retained_without_interpretation(self) -> None:
        witness = self.build()
        self.assertEqual(
            witness["observer_limitations"], self.specimen["observer_limitations"]
        )
        self.assertEqual(witness["derived_fields"], [])
        self.assertEqual(witness["interpreted_fields"], [])

    def test_witness_emits_no_atlas_or_semantic_standing(self) -> None:
        witness = self.build()
        forbidden_fragments = ("atlas", "standing", "semantic", "authority")
        self.assertFalse(
            any(
                fragment in key.lower()
                for key in witness
                for fragment in forbidden_fragments
            )
        )

    def test_constructor_performs_no_io_process_or_input_mutation(self) -> None:
        supplied = deepcopy(self.specimen)
        supplied_before = deepcopy(supplied)

        with (
            mock.patch("builtins.open", side_effect=AssertionError("unexpected I/O")),
            mock.patch.object(
                Path, "write_text", side_effect=AssertionError("unexpected write")
            ),
            mock.patch.object(
                subprocess, "run", side_effect=AssertionError("unexpected process")
            ),
        ):
            first = build_raw_invocation_witness(**supplied)
            second = build_raw_invocation_witness(**supplied)

        self.assertEqual(first, second)
        self.assertEqual(supplied, supplied_before)


if __name__ == "__main__":
    unittest.main()
