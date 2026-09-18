from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.runtime.workshop_frozen_cell import (
    E003,
    E004,
    E005,
    E006,
    E011,
    E017,
    FAULT_SCHEMA,
    RECEIPT_SCHEMA,
    STATE_HALTED,
    STATE_RECEIPT_COMMITTED,
    MemoryOutputSink,
    MockInvocationAdapter,
    run_frozen_cell,
    sha256_bytes,
)


def h(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class WorkshopFrozenCellPhaseATest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

        self.parts = {
            "role_header": b"ROLE\nmechanical reviewer",
            "condition_packet": b"CONDITION\nhistorical packet bytes",
            "specimen": b"SPECIMEN\nfrozen challenge bytes",
            "task": b"TASK\nanswer the frozen question",
            "response_schema": b"SCHEMA\nreturn fields exactly",
        }
        for name, payload in self.parts.items():
            (self.root / f"{name}.txt").write_bytes(payload)

        order = [
            "role_header",
            "condition_packet",
            "specimen",
            "task",
            "response_schema",
        ]
        separator = b"\n\n"
        self.payload = separator.join(self.parts[name] for name in order)
        self.payload_sha = h(self.payload)
        self.raw_output = b"SUFFICIENCY: UNRESOLVED\nACTION: MORE EVIDENCE REQUIRED\n"

        self.manifest = {
            "schema": "workshop_frozen_cell_manifest_v0",
            "manifest_id": "WP001-T00",
            "experiment_id": "WP-001",
            "cell_id": "RUN01",
            "basis": {
                "contract_commit": "a" * 40,
                "authorization_ref": "executive:test:RUN01",
            },
            "inputs": {
                name: {
                    "path": f"{name}.txt",
                    "sha256": h(payload),
                }
                for name, payload in self.parts.items()
            },
            "assembly": {
                "encoding": "utf-8",
                "newline": "lf",
                "separator": "\n\n",
                "order": order,
                "expected_payload_sha256": self.payload_sha,
            },
            "invocation": {
                "adapter": "mock_sha256_v0",
                "surface": {
                    "model_label": {
                        "expected": "mock-fixed-v0",
                        "verification": "VERIFIABLE_REQUIRED",
                    },
                    "tools_allowed": {
                        "expected": False,
                        "verification": "VERIFIABLE_REQUIRED",
                    },
                    "reasoning_mode": {
                        "expected": "fixed",
                        "verification": "DECLARED_ONLY",
                    },
                    "provider_backend_revision": {
                        "expected": None,
                        "verification": "UNOBSERVABLE",
                    },
                },
            },
            "execution": {
                "max_invocations": 1,
                "retry_allowed": False,
                "repair_allowed": False,
                "skip_allowed": False,
                "best_effort_allowed": False,
            },
            "output": {
                "retain_raw": True,
                "hash_raw": True,
                "anonymize": False,
            },
        }

    def manifest_bytes(self, manifest: dict | None = None) -> bytes:
        value = self.manifest if manifest is None else manifest
        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        ).encode("utf-8")

    def adapter(self, *, model_label: str = "mock-fixed-v0") -> MockInvocationAdapter:
        return MockInvocationAdapter(
            observed_surface={
                "model_label": model_label,
                "tools_allowed": False,
            },
            responses_by_payload_sha256={
                self.payload_sha: self.raw_output,
            },
        )

    def run_case(
        self,
        *,
        manifest: dict | None = None,
        adapter: MockInvocationAdapter | None = None,
        sink: MemoryOutputSink | None = None,
    ) -> tuple[dict, MockInvocationAdapter]:
        manifest_bytes = self.manifest_bytes(manifest)
        actual_adapter = self.adapter() if adapter is None else adapter
        result = run_frozen_cell(
            manifest_bytes=manifest_bytes,
            authorized_manifest_sha256=sha256_bytes(manifest_bytes),
            root=self.root,
            adapter=actual_adapter,
            output_sink=MemoryOutputSink() if sink is None else sink,
        )
        return result, actual_adapter

    def assert_preinvoke_halt(self, result: dict, adapter: MockInvocationAdapter, code: str) -> None:
        self.assertEqual(result["schema"], FAULT_SCHEMA)
        self.assertEqual(result["code"], code)
        self.assertTrue(result["terminal"])
        self.assertEqual(result["state_trace"][-1], STATE_HALTED)
        self.assertFalse(result["model_invoked"])
        self.assertEqual(result["invocation_count"], 0)
        self.assertEqual(adapter.invocation_count, 0)

    def test_T00_clean_world_commits_one_success_receipt(self) -> None:
        result, adapter = self.run_case()

        self.assertEqual(result["schema"], RECEIPT_SCHEMA)
        self.assertEqual(result["execution_status"], "COMPLETED")
        self.assertEqual(result["state_trace"][-1], STATE_RECEIPT_COMMITTED)
        self.assertTrue(result["execution"]["model_invoked"])
        self.assertEqual(result["execution"]["invocation_count"], 1)
        self.assertEqual(adapter.invocation_count, 1)
        self.assertEqual(result["assembled_payload_sha256"], self.payload_sha)
        self.assertEqual(result["output"]["raw_sha256"], h(self.raw_output))
        self.assertEqual(result["invocation_surface"]["observed"]["model_label"], "mock-fixed-v0")
        self.assertIn("reasoning_mode", result["invocation_surface"]["unverified"])
        self.assertIn("provider_backend_revision", result["invocation_surface"]["unobservable"])

    def test_T01_bad_condition_hash_halts_before_invocation(self) -> None:
        (self.root / "condition_packet.txt").write_bytes(b"CORRUPTED")
        result, adapter = self.run_case()
        self.assert_preinvoke_halt(result, adapter, E003)
        self.assertEqual(result["transition_blocked"], "INPUTS_VERIFIED")

    def test_T02_bad_specimen_hash_halts_before_invocation(self) -> None:
        (self.root / "specimen.txt").write_bytes(b"CORRUPTED")
        result, adapter = self.run_case()
        self.assert_preinvoke_halt(result, adapter, E004)
        self.assertEqual(result["transition_blocked"], "INPUTS_VERIFIED")

    def test_T03_payload_drift_halts_before_invocation(self) -> None:
        manifest = deepcopy(self.manifest)
        manifest["assembly"]["expected_payload_sha256"] = "f" * 64
        result, adapter = self.run_case(manifest=manifest)
        self.assert_preinvoke_halt(result, adapter, E005)
        self.assertEqual(result["transition_blocked"], "PAYLOAD_VERIFIED")

    def test_T04_invocation_surface_drift_halts_before_model_call(self) -> None:
        adapter = self.adapter(model_label="mock-drift-v1")
        result, adapter = self.run_case(adapter=adapter)
        self.assert_preinvoke_halt(result, adapter, E006)
        self.assertEqual(result["transition_blocked"], "INVOCATION_VERIFIED")

    def test_T05_output_capture_failure_retains_execution_fact_without_success(self) -> None:
        sink = MemoryOutputSink(fail_write=True)
        result, adapter = self.run_case(sink=sink)

        self.assertEqual(result["schema"], FAULT_SCHEMA)
        self.assertEqual(result["code"], E011)
        self.assertTrue(result["terminal"])
        self.assertEqual(result["state_trace"][-1], STATE_HALTED)
        self.assertIn("INVOKED", result["state_trace"])
        self.assertIn("OUTPUT_CAPTURED", result["state_trace"])
        self.assertNotIn(STATE_RECEIPT_COMMITTED, result["state_trace"])
        self.assertTrue(result["model_invoked"])
        self.assertEqual(result["invocation_count"], 1)
        self.assertEqual(adapter.invocation_count, 1)
        self.assertEqual(result["transition_blocked"], "OUTPUT_RETAINED")

    def test_T06_unknown_deviation_falls_back_to_E017_without_improvising(self) -> None:
        adapter = self.adapter()
        adapter.observe_error = RuntimeError("unclassified mock telemetry rupture")
        result, adapter = self.run_case(adapter=adapter)

        self.assert_preinvoke_halt(result, adapter, E017)
        self.assertEqual(result["transition_blocked"], "INVOCATION_VERIFIED")
        self.assertEqual(result["observed"]["error_type"], "RuntimeError")


if __name__ == "__main__":
    unittest.main()
