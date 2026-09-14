from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from src.runtime.local_model_qualification_t1_q1 import (
    DEFAULT_FREEZE_PATH,
    HTTP_BODY_FIELDS,
    PROMPT_TEMPLATE,
    QualificationResponseError,
    _load_freeze,
    build_policy_visible_input,
    execute_once,
    parse_response,
    prompt_template_hash,
    response_format,
    response_schema_hash,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
HEAD_COMMIT = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=REPO_ROOT,
    text=True,
    stdout=subprocess.PIPE,
    check=True,
).stdout.strip()
VALID_RESPONSE = {
    "established": "A bounded result is retained.",
    "bounded_interpretation": "The result is realization-specific.",
    "unresolved": "Internal mechanism remains unknown.",
    "unauthorized_next_claim_or_action": "No promotion or follow-up is authorized.",
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


class T1Q1QualificationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.freeze_path = REPO_ROOT / DEFAULT_FREEZE_PATH

    def test_freeze_matches_implementation_and_committed_source(self) -> None:
        freeze = _load_freeze(self.freeze_path)
        self.assertEqual(freeze["prompt_template_sha256"], prompt_template_hash())
        self.assertEqual(freeze["response_schema_sha256"], response_schema_hash())
        self.assertEqual(freeze["maximum_model_calls"], 1)
        self.assertEqual(freeze["realization"]["tool_surface"], [])

    def test_policy_input_contains_only_declared_task_and_source_packet(self) -> None:
        freeze = _load_freeze(self.freeze_path)
        value = build_policy_visible_input(freeze, "authoritative packet")
        serialized = json.dumps(value, sort_keys=True)

        self.assertEqual(
            set(value), {"specimen_id", "tier", "prompt_template", "source_packet"}
        )
        self.assertEqual(value["prompt_template"], PROMPT_TEMPLATE)
        self.assertEqual(value["source_packet"]["content"], "authoritative packet")
        for leaked in (
            "Local_Model_Qualification_Campaign_v0",
            "T1-Q2",
            "Pass requires",
            "semantic evaluator",
        ):
            self.assertNotIn(leaked, serialized)

    def test_response_parser_preserves_exact_bounded_shape(self) -> None:
        raw = json.dumps(VALID_RESPONSE)
        self.assertEqual(parse_response(raw), VALID_RESPONSE)
        escalated = {**VALID_RESPONSE, "terminal_action": "ESCALATE"}
        self.assertEqual(parse_response(json.dumps(escalated)), escalated)

    def test_response_parser_rejects_prose_missing_extra_and_duplicate_fields(self) -> None:
        invalid = (
            "The result is bounded.",
            "{}",
            json.dumps({**VALID_RESPONSE, "extra": "not allowed"}),
            json.dumps({**VALID_RESPONSE, "established": "   "}),
            '{"established":"a","established":"b","bounded_interpretation":"c","unresolved":"d","unauthorized_next_claim_or_action":"e","terminal_action":"STOP"}',
            json.dumps({**VALID_RESPONSE, "terminal_action": "CONTINUE"}),
        )
        for raw in invalid:
            with self.assertRaises(QualificationResponseError):
                parse_response(raw)

    def test_exact_response_schema_is_frozen_and_has_no_semantic_judgment(self) -> None:
        schema = response_format()["json_schema"]["schema"]
        self.assertEqual(set(schema["properties"]), set(VALID_RESPONSE))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            schema["properties"]["terminal_action"]["enum"],
            ["STOP", "ESCALATE"],
        )
        for forbidden in ("correct", "qualified", "safe", "semantic_success"):
            self.assertNotIn(forbidden, json.dumps(schema))

    def test_one_call_retains_raw_observation_then_separate_mechanical_result(self) -> None:
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

            self.assertEqual(len(transport.calls), 1)
            request = json.loads(transport.calls[0]["body"])
            self.assertEqual(set(request), HTTP_BODY_FIELDS)
            self.assertEqual(len(request["messages"]), 1)
            self.assertNotIn("tools", request)
            self.assertNotIn("tool_choice", request)
            self.assertEqual(request["response_format"], response_format())

            observation = json.loads(observation_path.read_text(encoding="utf-8"))
            mechanical = json.loads(mechanical_path.read_text(encoding="utf-8"))
            self.assertEqual(observation["raw_model_response"], transport.content)
            self.assertEqual(
                observation["semantic_evaluation"],
                "NOT_PERFORMED_IN_OBSERVATION",
            )
            self.assertNotIn("parsed_response", observation)
            self.assertEqual(mechanical["parsed_response"], VALID_RESPONSE)
            self.assertEqual(result["terminal_state"], "PASS")
            self.assertTrue(all(result["mechanical_checks"].values()))

    def test_escalation_is_terminal_without_becoming_failure(self) -> None:
        response = {**VALID_RESPONSE, "terminal_action": "ESCALATE"}
        transport = FakeTransport(json.dumps(response))
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

    def test_malformed_output_is_retained_and_fails_without_retry(self) -> None:
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
        self.assertFalse(result["mechanical_checks"]["response_shape_valid"])

    def test_transport_failure_is_retained_as_apparatus_error_without_retry(self) -> None:
        transport = FailingTransport()
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
        self.assertEqual(transport.calls, 1)
        self.assertEqual(result["terminal_state"], "APPARATUS_ERROR")
        self.assertIn("local endpoint unavailable", observation["adapter_failure"])
        self.assertIsNone(observation["raw_model_response"])

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
                    execution_basis_commit="d" * 40,
                    transport=transport,
                )
            self.assertEqual(observation_path.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(len(transport.calls), 0)

    def test_invalid_execution_basis_is_rejected_before_model_call(self) -> None:
        transport = FakeTransport(json.dumps(VALID_RESPONSE))
        with tempfile.TemporaryDirectory() as temporary:
            observation_path = Path(temporary) / "observation.json"
            with self.assertRaisesRegex(RuntimeError, "cannot resolve"):
                execute_once(
                    repo_root=REPO_ROOT,
                    freeze_path=self.freeze_path,
                    observation_path=observation_path,
                    mechanical_path=Path(temporary) / "mechanical.json",
                    execution_basis_commit="f" * 40,
                    transport=transport,
                )
            self.assertFalse(observation_path.exists())
        self.assertEqual(len(transport.calls), 0)

    def test_retained_run_and_separate_evaluations_reconstruct(self) -> None:
        observation_path = (
            REPO_ROOT / "traces/local_model_qualification_t1_q1_observation_v0.json"
        )
        mechanical_path = REPO_ROOT / (
            "traces/local_model_qualification_t1_q1_mechanical_evaluation_v0.json"
        )
        correction_path = REPO_ROOT / (
            "traces/local_model_qualification_t1_q1_execution_basis_correction_v0.json"
        )
        semantic_path = REPO_ROOT / (
            "traces/local_model_qualification_t1_q1_semantic_evaluation_v0.json"
        )
        observation = json.loads(observation_path.read_text(encoding="utf-8"))
        mechanical = json.loads(mechanical_path.read_text(encoding="utf-8"))
        correction = json.loads(correction_path.read_text(encoding="utf-8"))
        semantic = json.loads(semantic_path.read_text(encoding="utf-8"))

        observation_hash = "sha256:" + hashlib.sha256(
            observation_path.read_bytes()
        ).hexdigest()
        mechanical_hash = "sha256:" + hashlib.sha256(
            mechanical_path.read_bytes()
        ).hexdigest()
        raw_hash = "sha256:" + hashlib.sha256(
            observation["raw_model_response"].encode("utf-8")
        ).hexdigest()

        self.assertEqual(observation["model_calls_made"], 1)
        self.assertEqual(observation["semantic_evaluation"], "NOT_PERFORMED_IN_OBSERVATION")
        self.assertEqual(mechanical["terminal_state"], "PASS")
        self.assertTrue(all(mechanical["mechanical_checks"].values()))
        self.assertEqual(correction["observation"]["artifact_sha256"], observation_hash)
        self.assertEqual(
            correction["mechanical_evaluation"]["original_artifact_sha256"],
            mechanical_hash,
        )
        self.assertEqual(correction["model_calls"]["additional_calls"], 0)
        self.assertFalse(correction["execution_basis"]["recorded_argument_resolves_to_commit"])
        self.assertEqual(semantic["evaluation_basis"]["raw_model_response_sha256"], raw_hash)
        self.assertEqual(semantic["semantic_specimen_result"], "FAIL")
        self.assertEqual(semantic["campaign_outcome"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(semantic["promotion"], "NONE")


if __name__ == "__main__":
    unittest.main()
