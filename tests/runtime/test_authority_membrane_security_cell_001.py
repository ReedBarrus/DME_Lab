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
MUTATED_PROMPT = b"Return exactly: AUTHORITY_MEMBRANE_CELL_001_CONTROM\n"
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
        execution_candidate_bytes: bytes | None,
        result_path: Path,
        rejection_path: Path,
    ) -> tuple[int, str, mock.Mock, mock.Mock, mock.Mock | None, mock.Mock, list[str]]:
        events: list[str] = []

        def invoke_side_effect(*args: object, **kwargs: object) -> dict[str, str]:
            del args, kwargs
            events.append("invoke")
            return {
                "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
                "request_id": self.manifest["request_id"],
            }

        invoke = mock.Mock(side_effect=invoke_side_effect)

        def approve_side_effect(*args: object, **kwargs: object) -> bool:
            del args, kwargs
            events.append("approve")
            return True

        approve = mock.Mock(side_effect=approve_side_effect)

        def candidate_provider(
            manifest: dict[str, object],
            reviewed_prompt_bytes: bytes,
        ) -> bytes:
            self.assertEqual(manifest, self.manifest)
            self.assertEqual(reviewed_prompt_bytes, REVIEWED_PROMPT)
            events.append("execution_candidate")
            return execution_candidate_bytes

        candidate = (
            None
            if execution_candidate_bytes is None
            else mock.Mock(side_effect=candidate_provider)
        )

        original_revalidate = bridge.postapproval_input_identity_rejection_witness

        def revalidate_side_effect(*args: object, **kwargs: object) -> object:
            events.append("revalidate")
            return original_revalidate(*args, **kwargs)

        revalidate = mock.Mock(side_effect=revalidate_side_effect)

        def rejection_sink(witness: dict[str, object]) -> None:
            events.append("reject")
            rejection_path.write_text(
                json.dumps(witness, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        def git_show(ref: str, path: str) -> bytes:
            if (ref, path) == (REMOTE_HEAD, REQUEST_PATH):
                return self.raw_manifest
            if (ref, path) == (
                self.manifest["source_ref"],
                self.manifest["input_path"],
            ):
                return REVIEWED_PROMPT
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
            mock.patch.object(
                bridge,
                "postapproval_input_identity_rejection_witness",
                revalidate,
            ),
            redirect_stdout(output),
        ):
            process_options: dict[str, object] = {
                "rejection_witness_sink": rejection_sink,
            }
            if candidate is not None:
                process_options["execution_candidate_provider"] = candidate
            executed = bridge.process_once(self.policy, **process_options)

        return (
            executed,
            output.getvalue(),
            approve,
            invoke,
            candidate,
            revalidate,
            events,
        )

    def test_control_exact_reviewed_input_reaches_existing_invocation_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "control.json"
            rejection_path = Path(temp_dir) / "control-rejection.json"
            executed, output, approve, invoke, candidate, revalidate, events = self.run_cell(
                None,
                result_path,
                rejection_path,
            )

            self.assertEqual(executed, 1)
            approve.assert_called_once()
            self.assertIsNone(candidate)
            revalidate.assert_called_once()
            invoke.assert_called_once()
            self.assertEqual(events, ["approve", "revalidate", "invoke"])
            self.assertEqual(revalidate.call_args.args[1], REVIEWED_PROMPT)
            self.assertEqual(revalidate.call_args.args[2], REVIEWED_PROMPT)
            self.assertEqual(
                bridge.sha256_bytes(invoke.call_args.args[1]),
                bridge.sha256_bytes(REVIEWED_PROMPT),
            )
            self.assertNotIn("[REJECT]", output)
            self.assertFalse(rejection_path.exists())
            self.assertEqual(
                json.loads(result_path.read_text(encoding="utf-8"))["request_id"],
                self.manifest["request_id"],
            )

    def test_postapproval_mutation_is_rejected_before_lmstudio(self) -> None:
        self.assertEqual(len(REVIEWED_PROMPT), len(MUTATED_PROMPT))
        self.assertEqual(
            sum(left != right for left, right in zip(REVIEWED_PROMPT, MUTATED_PROMPT)),
            1,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "pressure.json"
            rejection_path = Path(temp_dir) / "pressure-rejection.json"
            executed, output, approve, invoke, candidate, revalidate, events = self.run_cell(
                MUTATED_PROMPT,
                result_path,
                rejection_path,
            )

            self.assertEqual(executed, 0)
            approve.assert_called_once()
            self.assertIsNotNone(candidate)
            assert candidate is not None
            candidate.assert_called_once()
            revalidate.assert_called_once()
            invoke.assert_not_called()
            self.assertEqual(
                events,
                ["approve", "execution_candidate", "revalidate", "reject"],
            )
            self.assertEqual(revalidate.call_args.args[1], REVIEWED_PROMPT)
            self.assertEqual(revalidate.call_args.args[2], MUTATED_PROMPT)
            self.assertFalse(result_path.exists())
            self.assertEqual(output, "")
            self.assertTrue(rejection_path.exists())
            witness = json.loads(rejection_path.read_text(encoding="utf-8"))
            self.assertEqual(
                witness,
                {
                    "object_type": "LOCAL_LMSTUDIO_POSTAPPROVAL_REVALIDATION_V0",
                    "request_id": self.manifest["request_id"],
                    "request_manifest_sha256": bridge.sha256_bytes(self.raw_manifest),
                    "source_ref": self.manifest["source_ref"],
                    "input_path": self.manifest["input_path"],
                    "declared_input_sha256": bridge.sha256_bytes(REVIEWED_PROMPT),
                    "reviewed_input_sha256": bridge.sha256_bytes(REVIEWED_PROMPT),
                    "execution_candidate_sha256": bridge.sha256_bytes(
                        MUTATED_PROMPT
                    ),
                    "executor_sha256": bridge.sha256_bytes(
                        Path(bridge.__file__).resolve().read_bytes()
                    ),
                    "policy_sha256": bridge.sha256_bytes(
                        bridge.POLICY_PATH.read_bytes()
                    ),
                    "approval_occurred": True,
                    "rejection_after_approval": True,
                    "decision": "REVALIDATE",
                    "reason": "POST_APPROVAL_INPUT_SHA256_MISMATCH",
                    "lmstudio_invoked": False,
                },
            )


if __name__ == "__main__":
    unittest.main()
