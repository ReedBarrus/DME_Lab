from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from src.runtime.local_model_qualification_t1_cross_realization import (
    COMPLETION_BUDGET_PRESSURE_FREEZE_PATH,
    DEADLINE_PRESSURE_FREEZE_PATH,
    DEFAULT_FREEZE_PATH,
    _load_freeze,
    build_exact_policy_visible_input,
    execute_once,
)
from src.runtime.local_model_qualification_t1_q1 import _sha256_bytes


REPO_ROOT = Path(__file__).resolve().parents[2]
HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True,
    stdout=subprocess.PIPE, check=True,
).stdout.strip()
VALID_RESPONSE = {
    "established": "Bounded evidence was observed.",
    "bounded_interpretation": "Only the tested apparatus is supported.",
    "unresolved": "Generalization remains unresolved.",
    "unauthorized_next_claim_or_action": "No promotion is authorized.",
    "terminal_action": "STOP",
}


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def __call__(self, endpoint, body, headers, timeout_seconds):
        self.calls.append({
            "endpoint": endpoint,
            "body": json.loads(body.decode("utf-8")),
            "timeout_seconds": timeout_seconds,
        })
        return 200, json.dumps({
            "model": "qwen3.8-27b-turbo-fable-cold-fusion-735-882-heretic-uncensored-neo-coder-max-mtp",
            "system_fingerprint": None,
            "choices": [{
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": json.dumps(VALID_RESPONSE, separators=(",", ":")),
                },
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        })


class TurboDeadlinePressureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.base = _load_freeze(REPO_ROOT / DEFAULT_FREEZE_PATH)
        self.pressure = _load_freeze(REPO_ROOT / DEADLINE_PRESSURE_FREEZE_PATH)

    def runtime_payload(self):
        realization = self.pressure["realization"]
        return {"models": [{
            "key": realization["requested_model_identifier"],
            "display_name": realization["display_name"],
            "architecture": realization["architecture"],
            "quantization": realization["quantization"],
            "size_bytes": realization["size_bytes"],
            "params_string": realization["params_string"],
            "format": realization["format"],
            "max_context_length": realization["model_supported_maximum_context"],
            "loaded_instances": [{
                "id": realization["loaded_model_instance_identifier"],
                "config": deepcopy(realization["loaded_instance_config"]),
            }],
        }]}

    def test_only_declared_timeout_coordinate_changes(self):
        base_realization = deepcopy(self.base["realization"])
        pressure_realization = deepcopy(self.pressure["realization"])
        self.assertEqual(base_realization.pop("timeout_seconds"), 120.0)
        self.assertEqual(pressure_realization.pop("timeout_seconds"), 600.0)
        self.assertEqual(pressure_realization, base_realization)
        self.assertEqual(tuple(self.pressure["authorized_specimens"]), ("Q1",))
        self.assertFalse(self.pressure["q4_authorized"])
        self.assertTrue(self.pressure["comparison_boundary"]["new_pressure_not_retry"])

    def test_q1_policy_visible_request_and_interface_are_unchanged(self):
        base_q1 = self.base["specimens"]["Q1"]
        pressure_q1 = self.pressure["specimens"]["Q1"]
        for field in (
            "source_specimen",
            "context_admission",
            "prompt_template_sha256",
            "response_schema_sha256",
            "specimen_id",
            "historical_freeze_path",
        ):
            self.assertEqual(pressure_q1[field], base_q1[field])
        _, base_serialized, _ = build_exact_policy_visible_input(
            repo_root=REPO_ROOT, cross_freeze=self.base, specimen_key="Q1"
        )
        _, pressure_serialized, _ = build_exact_policy_visible_input(
            repo_root=REPO_ROOT, cross_freeze=self.pressure, specimen_key="Q1"
        )
        self.assertEqual(pressure_serialized, base_serialized)

    def test_fake_execution_uses_one_fresh_call_and_600_second_timeout(self):
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as temporary:
            observation_path = Path(temporary) / "observation.json"
            mechanical_path = Path(temporary) / "mechanical.json"
            result = execute_once(
                repo_root=REPO_ROOT,
                freeze_path=REPO_ROOT / DEADLINE_PRESSURE_FREEZE_PATH,
                specimen_key="Q1",
                observation_path=observation_path,
                mechanical_path=mechanical_path,
                execution_basis_commit=HEAD,
                transport=transport,
                runtime_inspector=lambda endpoint, timeout: self.runtime_payload(),
            )
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.calls[0]["timeout_seconds"], 600.0)
        self.assertEqual(len(transport.calls[0]["body"]["messages"]), 1)
        self.assertNotIn("tools", transport.calls[0]["body"])
        self.assertEqual(observation["automatic_retries"], 0)
        self.assertEqual(
            observation["artifact"],
            "local_model_qualification_t1_turbo_q1_deadline_pressure_observation_v0",
        )
        self.assertEqual(result["terminal_state"], "PASS")

    def test_retained_pressure_result_reconstructs_without_semantic_repair(self):
        outputs = self.pressure["specimens"]["Q1"]["output_paths"]
        observation_path = REPO_ROOT / outputs["observation"]
        mechanical_path = REPO_ROOT / outputs["mechanical_evaluation"]
        semantic_path = REPO_ROOT / outputs["semantic_evaluation"]
        observation = json.loads(observation_path.read_text(encoding="utf-8"))
        mechanical = json.loads(mechanical_path.read_text(encoding="utf-8"))
        semantic = json.loads(semantic_path.read_text(encoding="utf-8"))

        self.assertIsNone(observation["adapter_failure"])
        self.assertEqual(observation["http_status"], 200)
        self.assertEqual(observation["finish_reason"], "length")
        self.assertEqual(observation["model_calls_made"], 1)
        self.assertEqual(observation["automatic_retries"], 0)
        self.assertEqual(
            observation["realization"]["provider_usage"]["completion_tokens"],
            1024,
        )
        self.assertEqual(
            observation["realization"]["provider_usage"]["completion_tokens_details"]["reasoning_tokens"],
            940,
        )
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertIsNone(mechanical["parsed_response"])
        self.assertIn("not one complete JSON value", mechanical["parse_failure"])
        self.assertEqual(
            semantic["evaluation_basis"]["observation"]["artifact_sha256"],
            _sha256_bytes(observation_path.read_bytes()),
        )
        self.assertEqual(
            semantic["evaluation_basis"]["mechanical_evaluation"]["artifact_sha256"],
            _sha256_bytes(mechanical_path.read_bytes()),
        )
        self.assertEqual(semantic["semantic_specimen_result"], "FAIL_INCOMPLETE_RESPONSE")
        self.assertFalse(semantic["dimensions"]["mechanical_success"])
        self.assertFalse(semantic["dimensions"]["semantic_completeness"])
        self.assertFalse(semantic["dimensions"]["stop_compliance"])
        self.assertEqual(semantic["promotion"], "NONE")
        self.assertFalse(semantic["q2_executed"])
        self.assertFalse(semantic["q3_executed"])
        self.assertFalse(semantic["q4_executed"])


class TurboCompletionBudgetPressureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.deadline = _load_freeze(REPO_ROOT / DEADLINE_PRESSURE_FREEZE_PATH)
        self.pressure = _load_freeze(
            REPO_ROOT / COMPLETION_BUDGET_PRESSURE_FREEZE_PATH
        )

    def runtime_payload(self):
        realization = self.pressure["realization"]
        return {"models": [{
            "key": realization["requested_model_identifier"],
            "display_name": realization["display_name"],
            "architecture": realization["architecture"],
            "quantization": realization["quantization"],
            "size_bytes": realization["size_bytes"],
            "params_string": realization["params_string"],
            "format": realization["format"],
            "max_context_length": realization["model_supported_maximum_context"],
            "loaded_instances": [{
                "id": realization["loaded_model_instance_identifier"],
                "config": deepcopy(realization["loaded_instance_config"]),
            }],
        }]}

    def test_only_completion_budget_changes_from_deadline_pressure(self):
        before = deepcopy(self.deadline["realization"])
        after = deepcopy(self.pressure["realization"])
        before_sampling = before.pop("provider_exposed_sampling_settings")
        after_sampling = after.pop("provider_exposed_sampling_settings")
        self.assertEqual(before, after)
        self.assertEqual(before_sampling.pop("max_tokens"), 1024)
        self.assertEqual(after_sampling.pop("max_tokens"), 2048)
        self.assertEqual(before_sampling, after_sampling)
        self.assertEqual(tuple(self.pressure["authorized_specimens"]), ("Q1",))
        self.assertTrue(self.pressure["comparison_boundary"]["new_pressure_not_retry"])
        self.assertFalse(self.pressure["q4_authorized"])

    def test_policy_visible_request_is_identical_and_reserve_is_admitted(self):
        _, before_serialized, _ = build_exact_policy_visible_input(
            repo_root=REPO_ROOT, cross_freeze=self.deadline, specimen_key="Q1"
        )
        _, after_serialized, _ = build_exact_policy_visible_input(
            repo_root=REPO_ROOT, cross_freeze=self.pressure, specimen_key="Q1"
        )
        self.assertEqual(after_serialized, before_serialized)
        before_q1 = self.deadline["specimens"]["Q1"]
        after_q1 = self.pressure["specimens"]["Q1"]
        for field in (
            "source_specimen",
            "prompt_template_sha256",
            "response_schema_sha256",
            "specimen_id",
            "historical_freeze_path",
        ):
            self.assertEqual(after_q1[field], before_q1[field])
        admission = after_q1["context_admission"]
        self.assertEqual(admission["rendered_input_tokens"], 3705)
        self.assertEqual(admission["reserved_output_tokens"], 2048)
        self.assertEqual(admission["total_required_tokens"], 5753)
        self.assertLessEqual(admission["total_required_tokens"], 8192)

    def test_fake_execution_uses_2048_tokens_one_call_and_same_deadline(self):
        transport = FakeTransport()
        with tempfile.TemporaryDirectory() as temporary:
            result = execute_once(
                repo_root=REPO_ROOT,
                freeze_path=REPO_ROOT / COMPLETION_BUDGET_PRESSURE_FREEZE_PATH,
                specimen_key="Q1",
                observation_path=Path(temporary) / "observation.json",
                mechanical_path=Path(temporary) / "mechanical.json",
                execution_basis_commit=HEAD,
                transport=transport,
                runtime_inspector=lambda endpoint, timeout: self.runtime_payload(),
            )
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.calls[0]["timeout_seconds"], 600.0)
        self.assertEqual(transport.calls[0]["body"]["max_tokens"], 2048)
        self.assertEqual(len(transport.calls[0]["body"]["messages"]), 1)
        self.assertNotIn("tools", transport.calls[0]["body"])
        self.assertEqual(result["terminal_state"], "PASS")


if __name__ == "__main__":
    unittest.main()
