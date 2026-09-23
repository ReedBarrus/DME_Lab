from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_MODULE_PATH = (
    REPOSITORY_ROOT / "src" / "runtime" / "local_authority_consumption_v0.py"
)
CANDIDATE_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "campaigns"
    / "authority_membrane_security_001"
    / "cell002_bound_installed_bridge_candidate"
    / "bridge.py"
)
PROMOTION_SCRIPT_PATH = CANDIDATE_PATH.with_name("promote.ps1")
INSTALLED_POLICY_PATH = Path.home() / ".dme_lab_bridge" / "policy.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


authority = load_module("local_authority_consumption_v0", AUTHORITY_MODULE_PATH)
bridge = load_module("cell002_bound_bridge_candidate", CANDIDATE_PATH)


PROMPT_A = b"Return exactly: AUTHORITY_MEMBRANE_CELL_002_CONTROL\n"
PROMPT_B = b"Return exactly: AUTHORITY_MEMBRANE_CELL_002_CONTROK\n"
REMOTE_HEAD = "b" * 40
SOURCE_REF = "a" * 40
REQUEST_PATH = "bridge/requests/AUTHORITY_MEMBRANE_SECURITY_CELL_002.json"
PRINCIPAL_P = "CODEX_PRINCIPAL_001"
PRINCIPAL_Q = "CODEX_PRINCIPAL_002"
CAPABILITY_ID = "CELL002.CAP.00000000000000000000000000000001"
APPROVAL_ID = "CELL002.APPROVAL.00000000000000000000000000000001"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Cell002BoundInstalledBridgeCandidateTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.policy_path = self.root / "policy.json"
        self.policy_path.write_bytes(INSTALLED_POLICY_PATH.read_bytes())
        self.policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        self.policy["_repo_root_resolved"] = str(self.root / "repo")
        self.policy["_result_dir_resolved"] = str(self.root / "results")
        Path(self.policy["_repo_root_resolved"]).mkdir()
        Path(self.policy["_result_dir_resolved"]).mkdir()
        self.manifest = {
            "schema_version": "LOCAL_INVOCATION_REQUEST_V0",
            "request_id": "AUTHORITY_MEMBRANE_SECURITY_CELL_002",
            "enabled": True,
            "source_ref": SOURCE_REF,
            "input_path": "bridge/prompts/AUTHORITY_MEMBRANE_SECURITY_CELL_002.txt",
            "input_sha256": sha256_bytes(PROMPT_A),
            "principal_id": PRINCIPAL_P,
            "model": "qwen/qwen3-coder-30b",
            "temperature": 0,
            "max_tokens": 64,
            "purpose": "Bind one declared principal to one governed invocation.",
        }
        self.raw_manifest = json.dumps(
            self.manifest,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    @staticmethod
    def clock(*values: str):
        retained = iter(values)
        return lambda: next(retained)

    def run_case(
        self,
        *,
        attempting_principal_id: str,
        execution_candidate: bytes = PROMPT_A,
        mutate_after_approval: bool = False,
    ) -> dict[str, object]:
        store = authority.LocalAuthorityStateStore(self.root / "authority_state")
        result_path = self.root / "result.json"
        approved: list[dict[str, object]] = []
        consumed_envelopes: list[dict[str, object]] = []
        authority_denials: list[dict[str, object]] = []
        revalidations: list[dict[str, object]] = []

        def git_show(repo: Path, ref: str, path: str) -> bytes:
            del repo
            if (ref, path) == (REMOTE_HEAD, REQUEST_PATH):
                return self.raw_manifest
            if (ref, path) == (SOURCE_REF, self.manifest["input_path"]):
                return PROMPT_A
            raise AssertionError((ref, path))

        def approve(
            manifest: dict[str, object],
            prompt: bytes,
            approval_candidate: dict[str, object],
        ) -> bool:
            self.assertEqual(manifest, self.manifest)
            self.assertEqual(prompt, PROMPT_A)
            approved.append(approval_candidate)
            return True

        def consume(envelope: dict[str, object], **kwargs: object):
            consumed_envelopes.append(envelope)
            return authority.consume_authority_once(envelope, **kwargs)

        def invoke(*args: object, **kwargs: object) -> dict[str, object]:
            del args, kwargs
            retained = store.read(CAPABILITY_ID)
            self.assertEqual(retained["envelope"]["status"], authority.CONSUMING)
            self.assertEqual(retained["envelope"]["remaining_uses"], 0)
            return {
                "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
                "request_id": self.manifest["request_id"],
            }

        invoke_mock = mock.Mock(side_effect=invoke)

        def execution_candidate_provider(
            manifest: dict[str, object], prompt: bytes
        ) -> bytes:
            del prompt
            if mutate_after_approval:
                manifest["max_tokens"] = 65
            return execution_candidate

        with (
            mock.patch.object(bridge, "POLICY_PATH", self.policy_path),
            mock.patch.object(
                bridge, "AUTHORITY_MODULE_PATH", AUTHORITY_MODULE_PATH
            ),
            mock.patch.object(bridge, "fetch_remote", return_value=REMOTE_HEAD),
            mock.patch.object(
                bridge, "list_request_paths", return_value=[REQUEST_PATH]
            ),
            mock.patch.object(bridge, "git_show", side_effect=git_show),
            mock.patch.object(bridge, "result_path_for", return_value=result_path),
            mock.patch.object(bridge, "approve", side_effect=approve) as approve_mock,
            mock.patch.object(bridge, "invoke_lmstudio", invoke_mock),
        ):
            executed = bridge.process_once(
                self.policy,
                attempting_principal_id,
                execution_candidate_provider=execution_candidate_provider,
                revalidation_witness_sink=revalidations.append,
                authority_decision_sink=authority_denials.append,
                authority_store=store,
                authority_clock=self.clock(
                    "2026-09-22T19:00:00+00:00",
                    "2026-09-22T19:00:01+00:00",
                    "2026-09-22T19:00:02+00:00",
                ),
                authority_id_factory=lambda: (CAPABILITY_ID, APPROVAL_ID),
                authority_consumer=consume,
            )

        return {
            "store": store,
            "result_path": result_path,
            "approved": approved,
            "consumed_envelopes": consumed_envelopes,
            "authority_denials": authority_denials,
            "revalidations": revalidations,
            "approve_mock": approve_mock,
            "invoke_mock": invoke_mock,
            "executed": executed,
        }

    def test_control_and_same_capability_instance_replay(self) -> None:
        result = self.run_case(attempting_principal_id=PRINCIPAL_P)
        store = result["store"]
        assert isinstance(store, authority.LocalAuthorityStateStore)
        envelope = result["consumed_envelopes"][0]

        self.assertEqual(result["executed"], 1)
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_called_once()
        self.assertTrue(result["result_path"].exists())
        retained = store.read(CAPABILITY_ID)
        self.assertEqual(retained["envelope"]["status"], authority.CONSUMED)
        self.assertEqual(retained["envelope"]["remaining_uses"], 0)
        receipt = retained["history"][-1]
        self.assertEqual(receipt["principal_id"], PRINCIPAL_P)
        self.assertEqual(receipt["invocation_count"], 1)

        approved = result["approved"][0]
        for field in (
            "capability_id",
            "approval_id",
            "principal_id",
            "request_sha256",
            "input_sha256",
            "model",
            "endpoint_identity",
            "executor_sha256",
            "policy_sha256",
        ):
            self.assertEqual(envelope[field], approved[field])
        self.assertEqual(envelope["request_sha256"], sha256_bytes(self.raw_manifest))
        self.assertEqual(approved["temperature"], self.manifest["temperature"])
        self.assertEqual(approved["max_tokens"], self.manifest["max_tokens"])

        replay_invoke = mock.Mock(side_effect=AssertionError("replay invoked"))
        exact_same_capability_object = envelope
        self.assertIs(exact_same_capability_object, envelope)
        replay = authority.consume_authority_once(
            exact_same_capability_object,
            attempting_principal_id=PRINCIPAL_P,
            store=store,
            invoke=replay_invoke,
            clock=self.clock("2026-09-22T19:00:03+00:00"),
        )
        replay_invoke.assert_not_called()
        self.assertEqual(replay["decision"], "DENY")
        self.assertEqual(replay["witness"]["reason"], "AUTHORITY_EXHAUSTED")

    def test_wrong_principal_denies_before_reservation(self) -> None:
        result = self.run_case(attempting_principal_id=PRINCIPAL_Q)
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["executed"], 0)
        self.assertFalse(result["result_path"].exists())
        denial = result["authority_denials"][0]
        self.assertEqual(denial["reason"], "PRINCIPAL_MISMATCH")
        self.assertEqual(denial["issued_principal_id"], PRINCIPAL_P)
        self.assertEqual(denial["attempting_principal_id"], PRINCIPAL_Q)
        self.assertFalse(denial["lmstudio_invoked"])
        retained = result["store"].read(CAPABILITY_ID)
        self.assertEqual(retained["envelope"]["status"], authority.ACTIVE)
        self.assertEqual(retained["envelope"]["remaining_uses"], 1)
        self.assertFalse(
            any(
                record.get("object_type") == authority.RESERVATION_TYPE
                for record in retained["history"]
            )
        )

    def test_cell001_mutation_rejects_before_authority_issuance(self) -> None:
        self.assertEqual(len(PROMPT_A), len(PROMPT_B))
        result = self.run_case(
            attempting_principal_id=PRINCIPAL_P,
            execution_candidate=PROMPT_B,
        )
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["consumed_envelopes"], [])
        self.assertEqual(result["authority_denials"], [])
        self.assertEqual(result["executed"], 0)
        self.assertEqual(
            result["revalidations"][0]["reason"],
            "POST_APPROVAL_INPUT_SHA256_MISMATCH",
        )
        self.assertFalse(result["store"].state_path(CAPABILITY_ID).exists())

    def test_approved_coordinate_mutation_rejects_before_authority_issuance(self) -> None:
        result = self.run_case(
            attempting_principal_id=PRINCIPAL_P,
            mutate_after_approval=True,
        )
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["consumed_envelopes"], [])
        self.assertEqual(result["executed"], 0)
        self.assertEqual(
            result["revalidations"][0]["reason"],
            "POST_APPROVAL_AUTHORITY_COORDINATE_MISMATCH",
        )
        self.assertFalse(result["store"].state_path(CAPABILITY_ID).exists())

    def test_only_model_call_site_is_inside_authority_consumer_in_process_once(self) -> None:
        source = CANDIDATE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "invoke_lmstudio"
        ]
        self.assertEqual(len(calls), 1)
        process_source = source[source.index("def process_once(") : source.index("def print_identity(")]
        self.assertIn("authority_consumer(", process_source)
        self.assertIn("invoke=lambda: invoke_lmstudio(", process_source)

    def test_promotion_script_is_fixed_hash_copy_only(self) -> None:
        script = PROMOTION_SCRIPT_PATH.read_text(encoding="utf-8")
        for expected_hash in (
            "5a4c466595ec4820bd8430ee3ee91f5a38437e55bfb48a8a756dfa53c87d7fdb",
            "bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303",
            "65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b",
            "0f86b8499c269ee42ed50285e4429c504ff5e6f93a6e65836128e98ef9d2bb21",
        ):
            self.assertIn(expected_hash, script)
        self.assertEqual(script.count("Copy-Item"), 2)
        for forbidden in (
            "git ",
            "Invoke-WebRequest",
            "Start-Process",
            "Remove-Item",
            "New-Item",
            "authority_state_v0",
            "invoke_lmstudio",
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
