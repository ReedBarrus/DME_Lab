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
    / "cell003_git_blob_input_identity_candidate"
    / "bridge.py"
)
INSTALLED_POLICY_PATH = Path.home() / ".dme_lab_bridge" / "policy.json"

PROMPT_A = b"Return exactly: CELL003_GIT_BLOB_IDENTITY_CONTROL\n"
PROMPT_B = b"Return exactly: CELL003_GIT_BLOB_IDENTITY_MUTATED\n"
REMOTE_HEAD = "b" * 40
SOURCE_REF = "a" * 40
BLOB_A = "c" * 40
BLOB_WRONG = "d" * 40
REQUEST_PATH = "bridge/requests/CELL003_GIT_BLOB_IDENTITY_CONTROL.json"
PRINCIPAL_P = "CODEX_PRINCIPAL_001"
PRINCIPAL_Q = "CODEX_PRINCIPAL_002"
CAPABILITY_ID = "CELL003.CAP.00000000000000000000000000000001"
APPROVAL_ID = "CELL003.APPROVAL.00000000000000000000000000000001"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


authority = load_module("local_authority_consumption_v0", AUTHORITY_MODULE_PATH)
bridge = load_module("cell003_git_blob_bridge_candidate", CANDIDATE_PATH)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Cell003GitBlobInputIdentityCandidateTest(unittest.TestCase):
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

    @staticmethod
    def clock(*values: str):
        retained = iter(values)
        return lambda: next(retained)

    def manifest_v01(self, *, blob_sha: str = BLOB_A) -> dict[str, object]:
        return {
            "schema_version": "LOCAL_INVOCATION_REQUEST_V0_1",
            "request_id": "CELL003_GIT_BLOB_IDENTITY_CONTROL",
            "enabled": True,
            "source_ref": SOURCE_REF,
            "input_path": "bridge/prompts/CELL003_GIT_BLOB_IDENTITY_CONTROL.txt",
            "input_blob_sha": blob_sha,
            "principal_id": PRINCIPAL_P,
            "model": "qwen/qwen3-coder-30b",
            "temperature": 0,
            "max_tokens": 64,
            "purpose": "Bind invocation to an immutable Git blob object id.",
        }

    def manifest_v0(self) -> dict[str, object]:
        return {
            "schema_version": "LOCAL_INVOCATION_REQUEST_V0",
            "request_id": "CELL003_V0_COMPAT_CONTROL",
            "enabled": True,
            "source_ref": SOURCE_REF,
            "input_path": "bridge/prompts/CELL003_GIT_BLOB_IDENTITY_CONTROL.txt",
            "input_sha256": sha256_bytes(PROMPT_A),
            "principal_id": PRINCIPAL_P,
            "model": "qwen/qwen3-coder-30b",
            "temperature": 0,
            "max_tokens": 64,
            "purpose": "Preserve V0 SHA256 request compatibility.",
        }

    def run_case(
        self,
        manifest: dict[str, object],
        *,
        attempting_principal_id: str = PRINCIPAL_P,
        observed_blob_sha: str = BLOB_A,
        execution_candidate: bytes = PROMPT_A,
        mutate_manifest_after_approval: bool = False,
    ) -> dict[str, object]:
        raw_manifest = json.dumps(
            manifest,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        store = authority.LocalAuthorityStateStore(self.root / "authority_state")
        result_path = self.root / "result.json"
        approved: list[dict[str, object]] = []
        consumed: list[dict[str, object]] = []
        denials: list[dict[str, object]] = []
        revalidations: list[dict[str, object]] = []

        def git_show(repo: Path, ref: str, path: str) -> bytes:
            del repo
            if (ref, path) == (REMOTE_HEAD, REQUEST_PATH):
                return raw_manifest
            raise AssertionError((ref, path))

        def approve(
            got_manifest: dict[str, object],
            prompt: bytes,
            approval_candidate: dict[str, object],
        ) -> bool:
            self.assertEqual(prompt, PROMPT_A)
            approved.append(approval_candidate)
            return True

        def consume(envelope: dict[str, object], **kwargs: object):
            consumed.append(envelope)
            return authority.consume_authority_once(envelope, **kwargs)

        def invoke(*args: object, **kwargs: object) -> dict[str, object]:
            del args, kwargs
            return {
                "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
                "request_id": manifest["request_id"],
            }

        invoke_mock = mock.Mock(side_effect=invoke)

        def execution_candidate_provider(
            got_manifest: dict[str, object], prompt: bytes
        ) -> bytes:
            del prompt
            if mutate_manifest_after_approval:
                got_manifest["max_tokens"] = 65
            return execution_candidate

        with (
            mock.patch.object(bridge, "POLICY_PATH", self.policy_path),
            mock.patch.object(bridge, "AUTHORITY_MODULE_PATH", AUTHORITY_MODULE_PATH),
            mock.patch.object(bridge, "fetch_remote", return_value=REMOTE_HEAD),
            mock.patch.object(bridge, "list_request_paths", return_value=[REQUEST_PATH]),
            mock.patch.object(bridge, "git_show", side_effect=git_show),
            mock.patch.object(
                bridge, "resolve_git_blob_sha", return_value=observed_blob_sha
            ),
            mock.patch.object(bridge, "git_blob_bytes", return_value=PROMPT_A),
            mock.patch.object(bridge, "result_path_for", return_value=result_path),
            mock.patch.object(bridge, "approve", side_effect=approve) as approve_mock,
            mock.patch.object(bridge, "invoke_lmstudio", invoke_mock),
        ):
            executed = bridge.process_once(
                self.policy,
                attempting_principal_id,
                execution_candidate_provider=execution_candidate_provider,
                revalidation_witness_sink=revalidations.append,
                authority_decision_sink=denials.append,
                authority_store=store,
                authority_clock=self.clock(
                    "2026-09-24T12:00:00+00:00",
                    "2026-09-24T12:00:01+00:00",
                    "2026-09-24T12:00:02+00:00",
                ),
                authority_id_factory=lambda: (CAPABILITY_ID, APPROVAL_ID),
                authority_consumer=consume,
            )

        return {
            "executed": executed,
            "approved": approved,
            "consumed": consumed,
            "denials": denials,
            "revalidations": revalidations,
            "approve_mock": approve_mock,
            "invoke_mock": invoke_mock,
            "store": store,
            "result_path": result_path,
            "raw_manifest": raw_manifest,
        }

    def test_v01_control_binds_blob_and_locally_derived_sha256(self) -> None:
        manifest = self.manifest_v01()
        result = self.run_case(manifest)
        self.assertEqual(result["executed"], 1)
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_called_once()
        approved = result["approved"][0]
        self.assertEqual(approved["input_blob_sha"], BLOB_A)
        self.assertEqual(approved["input_sha256"], sha256_bytes(PROMPT_A))
        envelope = result["consumed"][0]
        self.assertNotIn("input_blob_sha", envelope)
        self.assertEqual(envelope["input_sha256"], sha256_bytes(PROMPT_A))
        self.assertEqual(envelope["request_sha256"], sha256_bytes(result["raw_manifest"]))

    def test_v01_blob_mismatch_rejects_before_approval_or_authority(self) -> None:
        manifest = self.manifest_v01(blob_sha=BLOB_WRONG)
        result = self.run_case(manifest, observed_blob_sha=BLOB_A)
        self.assertEqual(result["executed"], 0)
        result["approve_mock"].assert_not_called()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["consumed"], [])
        self.assertFalse(result["result_path"].exists())

    def test_v01_postapproval_content_mutation_rejects_before_authority(self) -> None:
        manifest = self.manifest_v01()
        result = self.run_case(manifest, execution_candidate=PROMPT_B)
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["consumed"], [])
        self.assertEqual(result["executed"], 0)
        self.assertEqual(
            result["revalidations"][0]["reason"],
            "POST_APPROVAL_INPUT_SHA256_MISMATCH",
        )
        self.assertEqual(
            result["revalidations"][0]["declared_input_blob_sha"],
            BLOB_A,
        )

    def test_v01_postapproval_coordinate_mutation_rejects_before_authority(self) -> None:
        manifest = self.manifest_v01()
        result = self.run_case(manifest, mutate_manifest_after_approval=True)
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["consumed"], [])
        self.assertEqual(result["executed"], 0)
        self.assertEqual(
            result["revalidations"][0]["reason"],
            "POST_APPROVAL_AUTHORITY_COORDINATE_MISMATCH",
        )

    def test_principal_mismatch_preserves_cell002_denial(self) -> None:
        manifest = self.manifest_v01()
        result = self.run_case(manifest, attempting_principal_id=PRINCIPAL_Q)
        result["approve_mock"].assert_called_once()
        result["invoke_mock"].assert_not_called()
        self.assertEqual(result["executed"], 0)
        self.assertEqual(result["denials"][0]["reason"], "PRINCIPAL_MISMATCH")
        retained = result["store"].read(CAPABILITY_ID)
        self.assertEqual(retained["envelope"]["status"], authority.ACTIVE)
        self.assertEqual(retained["envelope"]["remaining_uses"], 1)

    def test_one_shot_authority_replay_still_denied(self) -> None:
        manifest = self.manifest_v01()
        result = self.run_case(manifest)
        envelope = result["consumed"][0]
        replay_invoke = mock.Mock(side_effect=AssertionError("replay invoked"))
        replay = authority.consume_authority_once(
            envelope,
            attempting_principal_id=PRINCIPAL_P,
            store=result["store"],
            invoke=replay_invoke,
            clock=self.clock("2026-09-24T12:00:03+00:00"),
        )
        replay_invoke.assert_not_called()
        self.assertEqual(replay["decision"], "DENY")
        self.assertEqual(replay["witness"]["reason"], "AUTHORITY_EXHAUSTED")

    def test_v0_manifest_remains_compatible(self) -> None:
        manifest = self.manifest_v0()
        parsed = bridge.parse_manifest(
            json.dumps(manifest, separators=(",", ":"), sort_keys=True).encode("utf-8")
        )
        self.assertEqual(parsed["schema_version"], "LOCAL_INVOCATION_REQUEST_V0")
        result = self.run_case(manifest)
        self.assertEqual(result["executed"], 1)
        self.assertIsNone(result["approved"][0]["input_blob_sha"])
        self.assertEqual(result["approved"][0]["input_sha256"], sha256_bytes(PROMPT_A))

    def test_result_witness_path_is_repo_bridge_results(self) -> None:
        repo_root = self.root / "repo"
        repo_root.mkdir(exist_ok=True)
        policy = dict(self.policy)
        policy["_repo_root_resolved"] = str(repo_root)
        out = bridge.result_path_for("CELL003_RESULT_ROUTE", policy)
        self.assertEqual(
            out,
            (repo_root / "bridge" / "results" / "CELL003_RESULT_ROUTE.json").resolve(),
        )

    def test_only_model_call_site_remains_inside_authority_consumer(self) -> None:
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
        process_source = source[
            source.index("def process_once(") : source.index("def print_identity(")
        ]
        self.assertIn("authority_consumer(", process_source)
        self.assertIn("invoke=lambda: invoke_lmstudio(", process_source)

    def test_promotion_script_is_fixed_hash_copy_only(self) -> None:
        script = CANDIDATE_PATH.with_name("promote.ps1").read_text(encoding="utf-8")
        for expected_hash in (
            "98a380044712bfd04e4f64c1a1982dbb0662aa3f646beda3dfdc882ab7ef8918",
            "bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303",
            "65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b",
            "0241a20a948119ed710d485d29f04bad284b965faa245ca5d9b38f3a84aad879",
        ):
            self.assertIn(expected_hash, script)
        self.assertEqual(script.count("Copy-Item"), 2)
        for forbidden in (
            "git ",
            "Invoke-WebRequest",
            "Start-Process",
            "Remove-Item",
            "New-Item",
            "invoke_lmstudio",
        ):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
