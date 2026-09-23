from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import tools.local_lmstudio_bridge_v0 as bridge


REVIEWED_PROMPT = b"Return exactly: AUTHORITY_MEMBRANE_CELL_001_CONTROL\n"
MUTATED_PROMPT = b"Return exactly: AUTHORITY_MEMBRANE_CELL_001_MUTATED\n"
REMOTE_HEAD = "b" * 40
SOURCE_REF = "a" * 40
REQUEST_PATH = "bridge/requests/AUTHORITY_MEMBRANE_SECURITY_CELL_001.json"


class AuthorityMembraneSecurityCell001Test(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = bridge.load_policy()
        self.manifest = {
            "schema_version": "LOCAL_INVOCATION_REQUEST_V0",
            "request_id": "AUTHORITY_MEMBRANE_SECURITY_CELL_001",
            "enabled": True,
            "source_ref": SOURCE_REF,
            "input_path": "bridge/prompts/AUTHORITY_MEMBRANE_SECURITY_CELL_001.txt",
            "input_sha256": bridge.sha256_bytes(REVIEWED_PROMPT),
            "model": "qwen/qwen3-coder-30b",
            "temperature": 0,
            "max_tokens": 64,
            "purpose": "Pressure only post-review input identity mutation.",
        }
        self.raw_manifest = json.dumps(
            self.manifest,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def run_cell(
        self,
        prompt_bytes: bytes,
        result_path: Path,
    ) -> tuple[int, str, mock.Mock, mock.Mock]:
        invoke = mock.Mock(
            return_value={
                "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
                "request_id": self.manifest["request_id"],
            }
        )
        approve = mock.Mock(return_value=True)

        def git_show(ref: str, path: str) -> bytes:
            if (ref, path) == (REMOTE_HEAD, REQUEST_PATH):
                return self.raw_manifest
            if (ref, path) == (
                self.manifest["source_ref"],
                self.manifest["input_path"],
            ):
                return prompt_bytes
            raise AssertionError(f"unexpected git_show({ref!r}, {path!r})")

        output = io.StringIO()
        with (
            mock.patch.object(bridge, "fetch_remote", return_value=REMOTE_HEAD),
            mock.patch.object(
                bridge,
                "list_request_paths",
                return_value=[REQUEST_PATH],
            ),
            mock.patch.object(bridge, "git_show", side_effect=git_show),
            mock.patch.object(bridge, "result_path_for", return_value=result_path),
            mock.patch.object(bridge, "ROOT", result_path.parent),
            mock.patch.object(bridge, "approve", approve),
            mock.patch.object(bridge, "invoke_lmstudio", invoke),
            redirect_stdout(output),
        ):
            executed = bridge.process_once(self.policy)

        return executed, output.getvalue(), approve, invoke

    def test_control_exact_reviewed_input_reaches_existing_invocation_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "control.json"
            executed, output, approve, invoke = self.run_cell(
                REVIEWED_PROMPT,
                result_path,
            )

            self.assertEqual(executed, 1)
            approve.assert_called_once()
            invoke.assert_called_once()
            self.assertNotIn("[REJECT]", output)
            self.assertEqual(
                json.loads(result_path.read_text(encoding="utf-8"))["request_id"],
                self.manifest["request_id"],
            )

    def test_mutated_input_is_rejected_before_approval_or_lmstudio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "pressure.json"
            executed, output, approve, invoke = self.run_cell(
                MUTATED_PROMPT,
                result_path,
            )

            self.assertEqual(executed, 0)
            approve.assert_not_called()
            invoke.assert_not_called()
            self.assertFalse(result_path.exists())

            rejection_lines = [
                line.removeprefix("[REJECT] ")
                for line in output.splitlines()
                if line.startswith("[REJECT] ")
            ]
            self.assertEqual(len(rejection_lines), 1)
            witness = json.loads(rejection_lines[0])
            self.assertEqual(
                witness,
                {
                    "object_type": "LOCAL_LMSTUDIO_INPUT_IDENTITY_REJECTION_V0",
                    "request_id": self.manifest["request_id"],
                    "declared_input_sha256": bridge.sha256_bytes(REVIEWED_PROMPT),
                    "observed_input_sha256": bridge.sha256_bytes(MUTATED_PROMPT),
                    "executor_sha256": bridge.sha256_bytes(
                        Path(bridge.__file__).resolve().read_bytes()
                    ),
                    "policy_sha256": bridge.sha256_bytes(
                        bridge.POLICY_PATH.read_bytes()
                    ),
                    "decision": "REJECT",
                    "reason": "INPUT_SHA256_MISMATCH",
                    "lmstudio_invoked": False,
                },
            )


if __name__ == "__main__":
    unittest.main()
