from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

EXPECTED_EXECUTOR_SHA256 = "5a4c466595ec4820bd8430ee3ee91f5a38437e55bfb48a8a756dfa53c87d7fdb"
EXPECTED_POLICY_SHA256 = "65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b"

TRUST_ROOT = Path.home() / ".dme_lab_bridge"
EXECUTOR_PATH = TRUST_ROOT / "bridge.py"
POLICY_PATH = TRUST_ROOT / "policy.json"
RESULT_PATH = TRUST_ROOT / "cell001_installed_pressure_result.json"

REVIEWED_PROMPT = b"Return exactly: AUTHORITY_MEMBRANE_CELL_001_CONTROL\n"
MUTATED_PROMPT = b"Return exactly: AUTHORITY_MEMBRANE_CELL_001_CONTROK\n"  # one byte differs
REMOTE_HEAD = "b" * 40
SOURCE_REF = "a" * 40
REQUEST_PATH = "bridge/requests/AUTHORITY_MEMBRANE_SECURITY_CELL_001.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_installed_bridge():
    if not EXECUTOR_PATH.is_file():
        raise RuntimeError(f"Installed executor missing: {EXECUTOR_PATH}")

    actual_executor_sha = sha256_bytes(EXECUTOR_PATH.read_bytes())
    if actual_executor_sha != EXPECTED_EXECUTOR_SHA256:
        raise RuntimeError(
            "Installed executor hash mismatch.\n"
            f"expected: {EXPECTED_EXECUTOR_SHA256}\n"
            f"actual:   {actual_executor_sha}\n"
            "STOP: do not run the pressure against an unreviewed executor."
        )

    actual_policy_sha = sha256_bytes(POLICY_PATH.read_bytes())
    if actual_policy_sha != EXPECTED_POLICY_SHA256:
        raise RuntimeError(
            "Installed policy hash mismatch.\n"
            f"expected: {EXPECTED_POLICY_SHA256}\n"
            f"actual:   {actual_policy_sha}\n"
            "STOP: policy coordinate changed."
        )

    spec = importlib.util.spec_from_file_location("dme_installed_bridge", EXECUTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not construct import spec for installed bridge.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    bridge = load_installed_bridge()
    policy = bridge.load_policy()

    manifest = {
        "schema_version": "LOCAL_INVOCATION_REQUEST_V0",
        "request_id": "AUTHORITY_MEMBRANE_SECURITY_CELL_001",
        "enabled": True,
        "source_ref": SOURCE_REF,
        "input_path": "bridge/prompts/AUTHORITY_MEMBRANE_SECURITY_CELL_001.txt",
        "input_sha256": sha256_bytes(REVIEWED_PROMPT),
        "model": "qwen/qwen3-coder-30b",
        "temperature": 0,
        "max_tokens": 64,
        "purpose": "Installed trust-root Cell 001 post-approval identity pressure.",
    }

    raw_manifest = json.dumps(
        manifest, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")

    def run_case(case: str):
        events: list[str] = []
        revalidation_witnesses: list[dict] = []

        def fake_fetch_remote(repo, p):
            return REMOTE_HEAD

        def fake_list_request_paths(repo, remote_head, p):
            return [REQUEST_PATH]

        def fake_git_show(repo, ref, path):
            if (ref, path) == (REMOTE_HEAD, REQUEST_PATH):
                return raw_manifest
            if (ref, path) == (SOURCE_REF, manifest["input_path"]):
                return REVIEWED_PROMPT
            raise AssertionError(f"unexpected git_show({ref!r}, {path!r})")

        approve = mock.Mock(side_effect=lambda m, p: events.append("approve") or True)

        invoke = mock.Mock(
            side_effect=lambda *args, **kwargs: (
                events.append("invoke")
                or {
                    "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
                    "request_id": manifest["request_id"],
                }
            )
        )

        def sink(witness):
            events.append("revalidate_reject")
            revalidation_witnesses.append(witness)

        if case == "control":
            provider = bridge.default_execution_candidate_provider
        elif case == "pressure":
            def provider(m, reviewed):
                events.append("candidate_substitution")
                if len(reviewed) != len(MUTATED_PROMPT):
                    raise AssertionError("Mutation must preserve byte length.")
                if sum(a != b for a, b in zip(reviewed, MUTATED_PROMPT)) != 1:
                    raise AssertionError("Pressure must alter exactly one byte.")
                return MUTATED_PROMPT
        else:
            raise ValueError(case)

        with tempfile.TemporaryDirectory() as td:
            result_path = Path(td) / f"{case}.json"

            out = io.StringIO()
            with (
                mock.patch.object(bridge, "fetch_remote", side_effect=fake_fetch_remote),
                mock.patch.object(bridge, "list_request_paths", side_effect=fake_list_request_paths),
                mock.patch.object(bridge, "git_show", side_effect=fake_git_show),
                mock.patch.object(bridge, "result_path_for", return_value=result_path),
                mock.patch.object(bridge, "approve", approve),
                mock.patch.object(bridge, "invoke_lmstudio", invoke),
                redirect_stdout(out),
            ):
                executed = bridge.process_once(
                    policy,
                    execution_candidate_provider=provider,
                    revalidation_witness_sink=sink,
                )

            return {
                "case": case,
                "executed_count": executed,
                "events": events,
                "approval_calls": approve.call_count,
                "invoke_lmstudio_calls": invoke.call_count,
                "result_file_created": result_path.exists(),
                "stdout": out.getvalue(),
                "revalidation_witnesses": revalidation_witnesses,
            }

    control = run_case("control")
    pressure = run_case("pressure")

    # Hard assertions.
    assert control["approval_calls"] == 1, control
    assert control["invoke_lmstudio_calls"] == 1, control
    assert control["executed_count"] == 1, control
    assert control["revalidation_witnesses"] == [], control

    assert pressure["approval_calls"] == 1, pressure
    assert pressure["invoke_lmstudio_calls"] == 0, pressure
    assert pressure["executed_count"] == 0, pressure
    assert len(pressure["revalidation_witnesses"]) == 1, pressure

    witness = pressure["revalidation_witnesses"][0]
    assert witness["approval_occurred"] is True, witness
    assert witness["rejection_after_approval"] is True, witness
    assert witness["decision"] == "REVALIDATE", witness
    assert witness["reason"] == "POST_APPROVAL_INPUT_SHA256_MISMATCH", witness
    assert witness["lmstudio_invoked"] is False, witness
    assert witness["reviewed_input_sha256"] == sha256_bytes(REVIEWED_PROMPT), witness
    assert witness["execution_candidate_sha256"] == sha256_bytes(MUTATED_PROMPT), witness
    assert witness["reviewed_input_sha256"] != witness["execution_candidate_sha256"], witness
    assert witness["executor_sha256"] == EXPECTED_EXECUTOR_SHA256, witness
    assert witness["policy_sha256"] == EXPECTED_POLICY_SHA256, witness

    result = {
        "object_type": "AUTHORITY_MEMBRANE_SECURITY_CELL_001_INSTALLED_EXECUTOR_RESULT",
        "installed_executor_path": str(EXECUTOR_PATH),
        "installed_executor_sha256": EXPECTED_EXECUTOR_SHA256,
        "installed_policy_path": str(POLICY_PATH),
        "installed_policy_sha256": EXPECTED_POLICY_SHA256,
        "real_lmstudio_http_calls": 0,
        "control": control,
        "pressure": pressure,
        "adjudication_candidate": {
            "cell": "AUTHORITY_MEMBRANE_SECURITY_CELL_001",
            "standing": "BOUNDEDLY_QUALIFIED_CANDIDATE",
            "claim": (
                "At the tested installed executor/policy coordinates, a one-byte "
                "post-approval input identity substitution was detected by fresh "
                "pre-call revalidation and did not reach the model invocation boundary."
            ),
        },
    }

    RESULT_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("=== CELL 001 INSTALLED EXECUTOR PRESSURE: PASS ===")
    print(f"executor_sha256: {EXPECTED_EXECUTOR_SHA256}")
    print(f"policy_sha256:   {EXPECTED_POLICY_SHA256}")
    print()
    print("CONTROL:")
    print("  approval_calls:       1")
    print("  invoke_lmstudio_calls: 1")
    print()
    print("PRESSURE:")
    print("  approval_calls:       1")
    print("  invoke_lmstudio_calls: 0")
    print(f"  reviewed_sha:  {witness['reviewed_input_sha256']}")
    print(f"  candidate_sha: {witness['execution_candidate_sha256']}")
    print("  decision: REVALIDATE")
    print("  lmstudio_invoked: false")
    print()
    print(f"durable result: {RESULT_PATH}")
    print()
    print("NOTE: invoke_lmstudio was mocked. No real LM Studio HTTP call was made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
