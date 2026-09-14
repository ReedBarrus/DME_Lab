from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from src.runtime.local_model_qualification_t1_q2 import (
    DEFAULT_FREEZE_PATH,
    HTTP_BODY_FIELDS,
    PROMPT_TEMPLATE,
    QualificationResponseError,
    SOURCE_SCENARIO_EXCLUSIONS,
    SOURCE_SCENARIO_FIELDS,
    SOURCE_TOP_LEVEL_EXCLUSIONS,
    _load_freeze,
    build_policy_visible_input,
    build_source_packet,
    execute_once,
    parse_response,
    prompt_template_hash,
    response_format,
    response_schema_hash,
    source_packet_hash,
)
from src.runtime.local_model_qualification_t1_q1 import _read_committed_bytes, _sha256_bytes


REPO_ROOT = Path(__file__).resolve().parents[2]
HEAD_COMMIT = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=REPO_ROOT,
    text=True,
    stdout=subprocess.PIPE,
    check=True,
).stdout.strip()
VALID_RESPONSE = {
    "apparatus_execution_state": "The packet retains eleven named observations.",
    "p8_evidence_state": "The damaged output omits retained history.",
    "p11_evidence_state": "Two same-ID nodes remain and diagnostics are absent.",
    "bounded_system_interpretation": "The evidence is bounded to the named scenarios.",
    "unresolved_and_unauthorized": "Broader correctness and follow-up remain unauthorized.",
    "terminal_action": "STOP",
}


class FakeTransport:
    def __init__(self, content: str, *, finish_reason: str = "stop") -> None:
        self.content = content
        self.finish_reason = finish_reason
        self.calls: list[dict] = []

    def __call__(self, endpoint, body, headers, timeout_seconds):
        self.calls.append(
            {
                "endpoint": endpoint,
                "body": body.decode("utf-8"),
                "headers": dict(headers),
                "timeout_seconds": timeout_seconds,
            }
        )
        return 200, json.dumps(
            {
                "id": "fake-call",
                "model": "test-local-realization",
                "system_fingerprint": None,
                "choices": [
                    {
                        "finish_reason": self.finish_reason,
                        "message": {"role": "assistant", "content": self.content},
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            }
        )


class FailingTransport:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, endpoint, body, headers, timeout_seconds):
        self.calls += 1
        raise OSError("local endpoint unavailable")


class T1Q2QualificationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.freeze_path = REPO_ROOT / DEFAULT_FREEZE_PATH
        self.freeze = _load_freeze(self.freeze_path)
        source = self.freeze["source_specimen"]
        self.source_bytes = _read_committed_bytes(
            REPO_ROOT, source["commit"], source["path"]
        )
        self.source_packet = build_source_packet(self.source_bytes)

    def test_freeze_matches_implementation_and_historical_source(self) -> None:
        source = self.freeze["source_specimen"]
        self.assertEqual(self.freeze["prompt_template_sha256"], prompt_template_hash())
        self.assertEqual(self.freeze["response_schema_sha256"], response_schema_hash())
        self.assertEqual(source["sha256"], _sha256_bytes(self.source_bytes))
        self.assertEqual(
            source["selected_packet_sha256"], source_packet_hash(self.source_packet)
        )
        self.assertEqual(self.freeze["maximum_model_calls"], 1)
        self.assertEqual(self.freeze["realization"]["tool_surface"], [])

    def test_same_realization_basis_as_q1_with_unknowns_preserved(self) -> None:
        q1 = json.loads(
            (REPO_ROOT / "traces/local_model_qualification_t1_q1_freeze_v0.json")
            .read_text(encoding="utf-8")
        )
        for field in (
            "endpoint",
            "requested_model_identifier",
            "provider_exposed_sampling_settings",
            "timeout_seconds",
            "model_artifact_digest",
            "quantization",
            "runtime_version",
        ):
            self.assertEqual(self.freeze["realization"].get(field), q1["realization"].get(field))
        self.assertIsNone(self.freeze["realization"]["context_limit"])

    def test_selected_packet_retains_observations_but_omits_answer_fields(self) -> None:
        ids = [item["id"] for item in self.source_packet["scenario_observations"]]
        self.assertEqual(ids, [f"P{number}" for number in range(1, 12)])
        for scenario in self.source_packet["scenario_observations"]:
            self.assertEqual(tuple(scenario), SOURCE_SCENARIO_FIELDS)
            for excluded in SOURCE_SCENARIO_EXCLUSIONS:
                self.assertNotIn(excluded, scenario)
        serialized = json.dumps(self.source_packet, sort_keys=True)
        for excluded in SOURCE_TOP_LEVEL_EXCLUSIONS:
            self.assertNotIn(excluded, self.source_packet)
        for answer in (
            "CONTRACT_VIOLATION",
            "CONTRACT_AMBIGUITY",
            "adapter generally reliable",
            "semantic success",
        ):
            self.assertNotIn(answer, serialized)
        self.assertIn('"id": "P8"', serialized)
        self.assertIn('"id": "P11"', serialized)
        self.assertIn('"damaged_history": []', serialized)
        self.assertIn('"matching_node_count": 2', serialized)

    def test_policy_input_contains_only_declared_task_and_selected_packet(self) -> None:
        value = build_policy_visible_input(self.freeze, self.source_packet)
        serialized = json.dumps(value, sort_keys=True)
        self.assertEqual(
            set(value), {"specimen_id", "tier", "prompt_template", "source_packet"}
        )
        self.assertEqual(value["prompt_template"], PROMPT_TEMPLATE)
        self.assertEqual(value["source_packet"]["content"], self.source_packet)
        for leaked in (
            "Local_Model_Qualification_Campaign_v0",
            "T1-Q1_BEHAVIORAL_COUPLING_CHECKPOINT",
            "CONTRACT_VIOLATION",
            "CONTRACT_AMBIGUITY",
            "classification_counts",
            "adjudication",
        ):
            self.assertNotIn(leaked, serialized)

    def test_response_parser_preserves_exact_shape_without_repair(self) -> None:
        raw = json.dumps(VALID_RESPONSE)
        self.assertEqual(parse_response(raw), VALID_RESPONSE)
        for invalid in (
            "A prose answer",
            "{}",
            json.dumps({**VALID_RESPONSE, "extra": "not allowed"}),
            json.dumps({**VALID_RESPONSE, "p8_evidence_state": "   "}),
            json.dumps({**VALID_RESPONSE, "terminal_action": "CONTINUE"}),
            '{"apparatus_execution_state":"a","apparatus_execution_state":"b","p8_evidence_state":"c","p11_evidence_state":"d","bounded_system_interpretation":"e","unresolved_and_unauthorized":"f","terminal_action":"STOP"}',
        ):
            with self.assertRaises(QualificationResponseError):
                parse_response(invalid)

    def test_response_schema_has_shape_but_no_semantic_answer(self) -> None:
        schema = response_format()["json_schema"]["schema"]
        self.assertEqual(set(schema["properties"]), set(VALID_RESPONSE))
        self.assertFalse(schema["additionalProperties"])
        serialized = json.dumps(schema)
        for answer in (
            "CONTRACT_VIOLATION",
            "CONTRACT_AMBIGUITY",
            "qualified",
            "correct",
        ):
            self.assertNotIn(answer, serialized)

    def test_one_call_retains_raw_observation_and_separate_mechanical_result(self) -> None:
        transport = FakeTransport(json.dumps(VALID_RESPONSE, separators=(",", ":")))
        with tempfile.TemporaryDirectory() as temporary:
            observation_path = Path(temporary) / "observation.json"
            mechanical_path = Path(temporary) / "mechanical.json"
            result = execute_once(
                repo_root=REPO_ROOT,
                freeze_path=self.freeze_path,
                observation_path=observation_path,
                mechanical_path=mechanical_path,
                execution_basis_commit=HEAD_COMMIT,
                transport=transport,
            )
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
            mechanical = json.loads(mechanical_path.read_text(encoding="utf-8"))
        self.assertEqual(len(transport.calls), 1)
        request = json.loads(transport.calls[0]["body"])
        self.assertEqual(set(request), HTTP_BODY_FIELDS)
        self.assertEqual(len(request["messages"]), 1)
        self.assertNotIn("tools", request)
        self.assertNotIn("previous_response_id", request)
        self.assertEqual(observation["raw_model_response"], transport.content)
        self.assertNotIn("parsed_response", observation)
        self.assertEqual(observation["semantic_evaluation"], "NOT_PERFORMED_IN_OBSERVATION")
        self.assertEqual(mechanical["parsed_response"], VALID_RESPONSE)
        self.assertEqual(result["terminal_state"], "PASS")
        self.assertTrue(all(result["mechanical_checks"].values()))

    def test_escalation_is_terminal_without_semantic_judgment(self) -> None:
        transport = FakeTransport(json.dumps({**VALID_RESPONSE, "terminal_action": "ESCALATE"}))
        with tempfile.TemporaryDirectory() as temporary:
            result = execute_once(
                repo_root=REPO_ROOT,
                freeze_path=self.freeze_path,
                observation_path=Path(temporary) / "observation.json",
                mechanical_path=Path(temporary) / "mechanical.json",
                execution_basis_commit=HEAD_COMMIT,
                transport=transport,
            )
        self.assertEqual(result["terminal_state"], "ESCALATED")
        self.assertEqual(result["semantic_success"], "NOT_EVALUATED")

    def test_malformed_output_is_retained_without_retry(self) -> None:
        transport = FakeTransport("not json")
        with tempfile.TemporaryDirectory() as temporary:
            observation_path = Path(temporary) / "observation.json"
            result = execute_once(
                repo_root=REPO_ROOT,
                freeze_path=self.freeze_path,
                observation_path=observation_path,
                mechanical_path=Path(temporary) / "mechanical.json",
                execution_basis_commit=HEAD_COMMIT,
                transport=transport,
            )
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(observation["raw_model_response"], "not json")
        self.assertEqual(result["terminal_state"], "FAIL")

    def test_transport_failure_is_retained_without_retry(self) -> None:
        transport = FailingTransport()
        with tempfile.TemporaryDirectory() as temporary:
            result = execute_once(
                repo_root=REPO_ROOT,
                freeze_path=self.freeze_path,
                observation_path=Path(temporary) / "observation.json",
                mechanical_path=Path(temporary) / "mechanical.json",
                execution_basis_commit=HEAD_COMMIT,
                transport=transport,
            )
        self.assertEqual(transport.calls, 1)
        self.assertEqual(result["terminal_state"], "APPARATUS_ERROR")

    def test_unresolved_or_non_head_execution_basis_blocks_before_call(self) -> None:
        for execution_basis in ("f" * 40, self.freeze["source_specimen"]["commit"]):
            transport = FakeTransport(json.dumps(VALID_RESPONSE))
            with tempfile.TemporaryDirectory() as temporary:
                with self.assertRaises(RuntimeError):
                    execute_once(
                        repo_root=REPO_ROOT,
                        freeze_path=self.freeze_path,
                        observation_path=Path(temporary) / "observation.json",
                        mechanical_path=Path(temporary) / "mechanical.json",
                        execution_basis_commit=execution_basis,
                        transport=transport,
                    )
            self.assertEqual(len(transport.calls), 0)

    def test_existing_observation_is_never_overwritten(self) -> None:
        transport = FakeTransport(json.dumps(VALID_RESPONSE))
        with tempfile.TemporaryDirectory() as temporary:
            observation_path = Path(temporary) / "observation.json"
            observation_path.write_text("preserve", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                execute_once(
                    repo_root=REPO_ROOT,
                    freeze_path=self.freeze_path,
                    observation_path=observation_path,
                    mechanical_path=Path(temporary) / "mechanical.json",
                    execution_basis_commit=HEAD_COMMIT,
                    transport=transport,
                )
            self.assertEqual(observation_path.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(len(transport.calls), 0)

    def test_retained_run_and_independent_evaluations_reconstruct(self) -> None:
        observation_path = REPO_ROOT / self.freeze["output_paths"]["observation"]
        mechanical_path = REPO_ROOT / self.freeze["output_paths"]["mechanical_evaluation"]
        semantic_path = REPO_ROOT / self.freeze["output_paths"]["semantic_evaluation"]
        comparison_path = REPO_ROOT / self.freeze["output_paths"]["comparison"]
        observation = json.loads(observation_path.read_text(encoding="utf-8"))
        mechanical = json.loads(mechanical_path.read_text(encoding="utf-8"))
        semantic = json.loads(semantic_path.read_text(encoding="utf-8"))
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))

        self.assertEqual(observation["model_calls_made"], 1)
        self.assertTrue(observation["execution_basis"]["valid"])
        self.assertEqual(
            observation["semantic_evaluation"], "NOT_PERFORMED_IN_OBSERVATION"
        )
        visible = observation["serialized_policy_visible_input"]
        for withheld in (
            "CONTRACT_VIOLATION",
            "CONTRACT_AMBIGUITY",
            "classification_counts",
            '"adjudication"',
        ):
            self.assertNotIn(withheld, visible)
        self.assertEqual(mechanical["terminal_state"], "PASS")
        self.assertTrue(all(mechanical["mechanical_checks"].values()))
        self.assertEqual(
            semantic["evaluation_basis"]["observation"]["artifact_sha256"],
            _sha256_bytes(observation_path.read_bytes()),
        )
        self.assertEqual(
            semantic["evaluation_basis"]["mechanical_evaluation"]["artifact_sha256"],
            _sha256_bytes(mechanical_path.read_bytes()),
        )
        self.assertEqual(
            semantic["evaluation_basis"]["raw_model_response_sha256"],
            _sha256_bytes(observation["raw_model_response"].encode("utf-8")),
        )
        self.assertEqual(semantic["semantic_specimen_result"], "FAIL")
        self.assertEqual(semantic["campaign_outcome"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(semantic["promotion"], "NONE")
        for dimension in (
            "promotion_error",
            "semantic_violation",
            "semantic_completeness",
            "scope_violation",
            "authority_violation",
            "stop_compliance",
        ):
            self.assertIn(dimension, semantic["dimensions"])
        self.assertEqual(comparison["q1_retained_result"]["mechanical_result"], "PASS")
        self.assertEqual(comparison["q1_retained_result"]["semantic_specimen_result"], "FAIL")
        self.assertEqual(comparison["promotion"], "NONE")
        self.assertFalse(comparison["subsequent_specimens_authorized"])


if __name__ == "__main__":
    unittest.main()
