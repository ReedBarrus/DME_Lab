from __future__ import annotations

import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from tools.goblin_pool import GoblinPool
from tools.labboib_controller_binding import bind_labboib
from tools.local_semantic_operator_v0 import (
    AUTHORITY_PATH,
    LocalSemanticHarness,
    fixture_provider,
    lm_studio_chat_completion,
)


ROOT = Path(__file__).resolve().parents[2]


def _head() -> str:
    import subprocess
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


class LocalSemanticOperatorPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.controller_db = root / "controller.sqlite3"
        self.semantic_db = root / "semantic.sqlite3"

        self.pool = GoblinPool(self.controller_db, ROOT)
        bind_labboib(self.pool, ROOT, "HEAD")
        self.wake_id = "W-LOCAL-SEMANTIC-001"
        self.pool.start_wake("LABBOIB", self.wake_id)

        self.harness = LocalSemanticHarness(self.pool, self.semantic_db)
        self.resource_id = "QWEN_LOCAL_PRIMARY"
        self.harness.register_resource(
            resource_id=self.resource_id,
            model_id="qwen-fixture",
            base_url="http://127.0.0.1:1234/v1",
            status="AVAILABLE",
        )

        self.head = _head()
        self.seat_version = self.pool.seat_snapshot("LABBOIB")["state_version"]

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def request(self, request_id: str) -> dict:
        return {
            "schema": "local_semantic_request_v0",
            "request_id": request_id,
            "seat_id": "LABBOIB",
            "task_type": "TRIAGE_IMPLEMENTATION_RESULT",
            "seat_basis_version": self.seat_version,
            "environment_basis": self.head,
            "evidence_refs": [
                "realization://D1",
                "applicability://J1",
                "checks://C1",
                "scope://S1",
            ],
            "input": {
                "realization": {
                    "realization_id": "D1",
                    "mechanical_result": "PASS",
                },
                "applicability": {
                    "judgment_id": "J1",
                    "result": "APPLICABLE",
                },
                "mechanical_checks": [
                    {"check_id": "C1", "result": "PASS"},
                ],
                "scope_status": "VALID",
            },
            "authority_ref": AUTHORITY_PATH,
        }

    def current_basis(self) -> tuple[int, str]:
        return (
            self.pool.seat_snapshot("LABBOIB")["state_version"],
            self.head,
        )

    def provider(self, mode: str):
        def call(**kwargs):
            return fixture_provider(mode=mode, **kwargs)
        return call

    def semantic_request_status(self, request_id: str) -> str:
        conn = sqlite3.connect(self.controller_db)
        try:
            row = conn.execute(
                "SELECT status FROM semantic_requests WHERE request_id=?",
                (request_id,),
            ).fetchone()
        finally:
            conn.close()
        self.assertIsNotNone(row)
        return row[0]

    def assert_resource_released(self) -> None:
        resource = self.harness.resource_snapshot(self.resource_id)
        self.assertIsNone(resource["active_lease_id"])
        self.assertIsNone(resource["leased_to"])

    def test_s1_valid_typed_proposal_is_retained_without_seat_transition(self) -> None:
        before = copy.deepcopy(self.pool.seat_snapshot("LABBOIB"))
        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=self.request("SR-S1"),
            resource_id=self.resource_id,
            provider=self.provider("VALID"),
            current_basis=self.current_basis,
        )
        after = self.pool.seat_snapshot("LABBOIB")

        self.assertEqual(outcome["status"], "PROPOSAL_RETAINED")
        self.assertTrue(outcome["proposal_valid"])
        self.assertTrue(outcome["accepted"])
        self.assertEqual(outcome["current_basis_status"], "CURRENT")
        self.assertEqual(outcome["proposal"]["authority_effect"], "NONE")
        self.assertEqual(outcome["proposal"]["action_selection_effect"], "NONE")
        self.assertEqual(outcome["proposal"]["seat_state_effect"], "NONE")
        self.assertTrue(outcome["seat_state_unchanged"])
        self.assertEqual(before, after)
        self.assertEqual(self.semantic_request_status("SR-S1"), "PROPOSAL_RECEIVED")
        self.assert_resource_released()

    def test_s2_malformed_response_is_failure_legible(self) -> None:
        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=self.request("SR-S2"),
            resource_id=self.resource_id,
            provider=self.provider("MALFORMED"),
            current_basis=self.current_basis,
        )

        self.assertEqual(outcome["status"], "NO_VALID_PROPOSAL")
        self.assertEqual(outcome["provider_error"], "MODEL_CONTENT_NOT_JSON")
        self.assertFalse(outcome["proposal_valid"])
        self.assertIsNone(outcome["proposal"])
        self.assertTrue(outcome["seat_state_unchanged"])
        self.assertEqual(self.semantic_request_status("SR-S2"), "INVALID_RESPONSE")
        self.assert_resource_released()

    def test_s3_extra_unsupported_field_is_rejected(self) -> None:
        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=self.request("SR-S3"),
            resource_id=self.resource_id,
            provider=self.provider("EXTRA_FIELD"),
            current_basis=self.current_basis,
        )

        self.assertFalse(outcome["proposal_valid"])
        self.assertIn("MODEL_PAYLOAD_FIELDS_INVALID", outcome["validation_errors"])
        self.assertIsNone(outcome["proposal"])
        self.assertEqual(self.semantic_request_status("SR-S3"), "INVALID_RESPONSE")
        self.assert_resource_released()

    def test_s4_suggested_action_is_not_action_selection(self) -> None:
        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=self.request("SR-S4"),
            resource_id=self.resource_id,
            provider=self.provider("UNAUTHORIZED_SUGGESTION"),
            current_basis=self.current_basis,
        )

        proposal = outcome["proposal"]
        self.assertEqual(proposal["suggested_next_step"], "REVALIDATE")
        self.assertEqual(proposal["action_selection_effect"], "NONE")
        self.assertEqual(outcome["action_selection_effect"], "NONE")
        self.assertTrue(outcome["seat_state_unchanged"])
        self.assert_resource_released()

    def test_s5_provider_failure_releases_lease_and_changes_no_seat_state(self) -> None:
        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=self.request("SR-S5"),
            resource_id=self.resource_id,
            provider=self.provider("FAIL"),
            current_basis=self.current_basis,
        )

        self.assertEqual(outcome["status"], "NO_VALID_PROPOSAL")
        self.assertIn("synthetic provider failure", outcome["provider_error"])
        self.assertIsNone(outcome["proposal"])
        self.assertEqual(self.semantic_request_status("SR-S5"), "PROVIDER_FAILED")
        self.assertTrue(outcome["seat_state_unchanged"])
        self.assert_resource_released()

    def test_s6_false_evidence_reference_is_rejected(self) -> None:
        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=self.request("SR-S6"),
            resource_id=self.resource_id,
            provider=self.provider("FALSE_EVIDENCE"),
            current_basis=self.current_basis,
        )

        self.assertFalse(outcome["proposal_valid"])
        self.assertIn(
            "EVIDENCE_REF_OUTSIDE_REQUEST_BASIS",
            outcome["validation_errors"],
        )
        self.assertIsNone(outcome["proposal"])
        self.assertEqual(self.semantic_request_status("SR-S6"), "INVALID_RESPONSE")
        self.assert_resource_released()

    def test_s7_duplicate_request_does_not_reinvoke_model(self) -> None:
        request = self.request("SR-S7")
        calls = {"count": 0}

        def provider(**kwargs):
            calls["count"] += 1
            return fixture_provider(mode="VALID", **kwargs)

        first = self.harness.invoke(
            wake_id=self.wake_id,
            request=request,
            resource_id=self.resource_id,
            provider=provider,
            current_basis=self.current_basis,
        )
        second = self.harness.invoke(
            wake_id=self.wake_id,
            request=request,
            resource_id=self.resource_id,
            provider=provider,
            current_basis=self.current_basis,
        )

        self.assertEqual(calls["count"], 1)
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertTrue(first["model_invoked"])
        self.assertFalse(second["model_invoked"])
        self.assertEqual(
            first["proposal"]["proposal_id"],
            second["proposal"]["proposal_id"],
        )
        self.assert_resource_released()

    def test_s8_basis_moves_during_cognition_proposal_survives_but_is_stale(self) -> None:
        request = self.request("SR-S8")
        current_environment = {"head": self.head}

        def provider(**kwargs):
            result = fixture_provider(mode="VALID", **kwargs)
            current_environment["head"] = "f" * 40
            return result

        def current_basis() -> tuple[int, str]:
            return (
                self.pool.seat_snapshot("LABBOIB")["state_version"],
                current_environment["head"],
            )

        outcome = self.harness.invoke(
            wake_id=self.wake_id,
            request=request,
            resource_id=self.resource_id,
            provider=provider,
            current_basis=current_basis,
        )

        self.assertIsNotNone(outcome["proposal"])
        self.assertTrue(outcome["proposal_valid"])
        self.assertEqual(outcome["current_basis_status"], "STALE")
        self.assertFalse(outcome["accepted"])
        self.assertTrue(outcome["seat_state_unchanged"])
        self.assertEqual(outcome["proposal"]["environment_basis"], self.head)
        self.assert_resource_released()

    def test_s9_lm_studio_http_transport_shape(self) -> None:
        observed = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                observed["path"] = self.path
                observed["payload"] = payload

                content = json.dumps(
                    {
                        "summary": "Transport contract reached provider.",
                        "anomaly_flags": [],
                        "suggested_next_step": "NONE",
                        "evidence_refs": ["realization://D1"],
                    }
                )
                body = json.dumps(
                    {
                        "choices": [
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": content,
                                }
                            }
                        ]
                    }
                ).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_port}/v1"
            result = lm_studio_chat_completion(
                base_url=base_url,
                model_id="qwen-exact-model-id",
                request=self.request("SR-S9"),
                timeout_seconds=5,
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

        self.assertEqual(observed["path"], "/v1/chat/completions")
        self.assertEqual(observed["payload"]["model"], "qwen-exact-model-id")
        self.assertFalse(observed["payload"]["stream"])
        self.assertEqual(
            observed["payload"]["response_format"]["type"],
            "json_schema",
        )
        self.assertEqual(result["provider_http_status"], 200)
        decoded = json.loads(result["model_content"])
        self.assertEqual(decoded["suggested_next_step"], "NONE")


if __name__ == "__main__":
    unittest.main()
