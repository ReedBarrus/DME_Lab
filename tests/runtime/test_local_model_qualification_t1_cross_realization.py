from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from src.runtime.local_model_qualification_t1_cross_realization import (
    DEFAULT_FREEZE_PATH,
    SPECIMEN_MODULES,
    _load_freeze,
    build_exact_policy_visible_input,
    execute_once,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True,
    stdout=subprocess.PIPE, check=True,
).stdout.strip()
VALID = {
    "Q1": {
        "established": "Bounded evidence was observed.",
        "bounded_interpretation": "Only the tested apparatus is supported.",
        "unresolved": "Generalization remains unresolved.",
        "unauthorized_next_claim_or_action": "No promotion is authorized.",
        "terminal_action": "STOP",
    },
    "Q2": {
        "apparatus_execution_state": "The pressure apparatus executed.",
        "p8_evidence_state": "A bounded history wound is visible.",
        "p11_evidence_state": "Duplicate identity remains ambiguous.",
        "bounded_system_interpretation": "General reliability is not established.",
        "unresolved_and_unauthorized": "Broader correctness remains unresolved.",
        "terminal_action": "STOP",
    },
    "Q3": {
        "apparatus_execution_state": "The re-pressure apparatus executed.",
        "named_specimen_result": "The named specimens satisfy the supplied rule.",
        "strongest_bounded_result": "Only the named set survived.",
        "explicit_residue_and_nonclaims": "General robustness is not established.",
        "authority_and_next_action_boundary": "No next action is authorized.",
        "terminal_action": "STOP",
    },
}


class FakeTransport:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = []

    def __call__(self, endpoint, body, headers, timeout_seconds):
        self.calls.append(json.loads(body.decode("utf-8")))
        return 200, json.dumps({
            "model": "qwen3.8-27b-turbo-fable-cold-fusion-735-882-heretic-uncensored-neo-coder-max-mtp",
            "system_fingerprint": None,
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": self.content},
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        })


class CrossRealizationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.freeze_path = REPO_ROOT / DEFAULT_FREEZE_PATH
        self.freeze = _load_freeze(self.freeze_path)

    def runtime_payload(self, *, context_length: int = 8192):
        realization = self.freeze["realization"]
        config = deepcopy(realization["loaded_instance_config"])
        config["context_length"] = context_length
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
                "config": config,
            }],
        }]}

    def test_freeze_reuses_exact_prompts_schemas_and_sources(self):
        for key, module in SPECIMEN_MODULES.items():
            specimen = self.freeze["specimens"][key]
            self.assertEqual(specimen["prompt_template_sha256"], module.prompt_template_hash())
            self.assertEqual(specimen["response_schema_sha256"], module.response_schema_hash())
            _, serialized, source = build_exact_policy_visible_input(
                repo_root=REPO_ROOT, cross_freeze=self.freeze, specimen_key=key
            )
            self.assertEqual(
                specimen["context_admission"]["serialized_policy_visible_input_sha256"],
                "sha256:" + __import__("hashlib").sha256(serialized.encode()).hexdigest(),
            )
            self.assertEqual(source["sha256"], source["observed_sha256"])

    def test_context_refreeze_precedes_calls_and_admits_all_three(self):
        refreeze = self.freeze["context_refreeze"]
        self.assertTrue(refreeze["before_scientific_inference"])
        self.assertEqual(refreeze["initial_configuration"]["configured_context_length"], 4096)
        self.assertEqual(refreeze["refrozen_configuration"]["configured_context_length"], 8192)
        self.assertFalse(refreeze["post_result_context_change_authorized"])
        for specimen in self.freeze["specimens"].values():
            admission = specimen["context_admission"]
            self.assertTrue(admission["admitted"])
            self.assertLessEqual(admission["total_required_tokens"], 8192)

    def test_policy_visible_inputs_exclude_cross_realization_answer_surfaces(self):
        for key in SPECIMEN_MODULES:
            value, serialized, _ = build_exact_policy_visible_input(
                repo_root=REPO_ROOT, cross_freeze=self.freeze, specimen_key=key
            )
            self.assertEqual(set(value), {"specimen_id", "tier", "prompt_template", "source_packet"})
            for forbidden in (
                "hermes_t1_qualification_checkpoint",
                "local_model_qualification_t1_q1_observation",
                "local_model_qualification_t1_q2_observation",
                "local_model_qualification_t1_q3_observation",
                "campaign_expected_answer",
            ):
                self.assertNotIn(forbidden, serialized.lower())

    def test_each_specimen_is_one_fresh_no_tools_request(self):
        for key in SPECIMEN_MODULES:
            transport = FakeTransport(json.dumps(VALID[key], separators=(",", ":")))
            inspector_calls = []

            def inspector(endpoint, timeout):
                inspector_calls.append((endpoint, timeout))
                return self.runtime_payload()

            with tempfile.TemporaryDirectory() as temporary:
                result = execute_once(
                    repo_root=REPO_ROOT,
                    freeze_path=self.freeze_path,
                    specimen_key=key,
                    observation_path=Path(temporary) / "observation.json",
                    mechanical_path=Path(temporary) / "mechanical.json",
                    execution_basis_commit=HEAD,
                    transport=transport,
                    runtime_inspector=inspector,
                )
            self.assertEqual(len(inspector_calls), 1)
            self.assertEqual(len(transport.calls), 1)
            request = transport.calls[0]
            self.assertEqual(len(request["messages"]), 1)
            self.assertNotIn("tools", request)
            self.assertNotIn("previous_response_id", request)
            self.assertEqual(result["terminal_state"], "PASS")
            self.assertTrue(all(result["mechanical_checks"].values()))

    def test_runtime_configuration_drift_blocks_before_inference(self):
        transport = FakeTransport(json.dumps(VALID["Q3"]))
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "configuration drifted"):
                execute_once(
                    repo_root=REPO_ROOT,
                    freeze_path=self.freeze_path,
                    specimen_key="Q3",
                    observation_path=Path(temporary) / "observation.json",
                    mechanical_path=Path(temporary) / "mechanical.json",
                    execution_basis_commit=HEAD,
                    transport=transport,
                    runtime_inspector=lambda endpoint, timeout: self.runtime_payload(context_length=4096),
                )
        self.assertEqual(len(transport.calls), 0)

    def test_invalid_execution_basis_blocks_before_runtime_or_inference(self):
        transport = FakeTransport(json.dumps(VALID["Q1"]))
        inspector_calls = []
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(RuntimeError):
                execute_once(
                    repo_root=REPO_ROOT,
                    freeze_path=self.freeze_path,
                    specimen_key="Q1",
                    observation_path=Path(temporary) / "observation.json",
                    mechanical_path=Path(temporary) / "mechanical.json",
                    execution_basis_commit="f" * 40,
                    transport=transport,
                    runtime_inspector=lambda endpoint, timeout: inspector_calls.append(1),
                )
        self.assertEqual(inspector_calls, [])
        self.assertEqual(len(transport.calls), 0)

    def test_q4_is_not_authorized(self):
        self.assertFalse(self.freeze["q4_authorized"])
        self.assertEqual(tuple(self.freeze["authorized_specimens"]), ("Q1", "Q2", "Q3"))


if __name__ == "__main__":
    unittest.main()
