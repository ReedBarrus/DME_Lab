from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "atlas_route_selection_execution_evidence_v0"
IDENTITY_MANIFEST_NAME = "frozen_identities_v0.json"


class HarnessError(RuntimeError):
    """Raised when the bounded evidence chain cannot be established."""


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"JSON root must be an object: {path}")
    return value


def verify_git_blob_identity(path: Path, expected_sha1: str, label: str) -> None:
    observed = git_blob_sha1(path)
    if observed != expected_sha1:
        raise HarnessError(
            f"{label} identity mismatch: expected {expected_sha1}, observed {observed}"
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _harness_dir() -> Path:
    return Path(__file__).resolve().parent


def load_identities() -> dict[str, Any]:
    identities = _load_json(_harness_dir() / IDENTITY_MANIFEST_NAME)
    if identities.get("schema_version") != "atlas_route_selection_execution_identities_v0":
        raise HarnessError("identity manifest schema_version mismatch")
    return identities


def verify_frozen_identities(identities: dict[str, Any]) -> dict[str, Path]:
    root = _repo_root()
    paths = {
        "harness": Path(__file__).resolve(),
        "child_wrapper": root / identities["child_wrapper"]["path"],
        "apparatus": root / identities["apparatus"]["path"],
        "producer": root / identities["producer"]["path"],
        "A": root / identities["A"]["path"],
        "B": root / identities["B"]["path"],
    }
    for key, path in paths.items():
        verify_git_blob_identity(path, identities[key]["blob_sha1"], key)
    return paths


def _validate_child_capture(
    capture: dict[str, Any],
    *,
    identities: dict[str, Any],
    paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if capture.get("schema_version") != "atlas_route_selection_child_capture_v0":
        raise HarnessError("child capture schema_version mismatch")

    producer_stdout = capture.get("producer_stdout")
    producer_stderr = capture.get("producer_stderr")
    if not isinstance(producer_stdout, str):
        raise HarnessError("child capture missing producer_stdout string")
    if producer_stderr != "":
        raise HarnessError("child capture producer_stderr must be empty")

    stdout_sha256 = sha256_bytes(producer_stdout.encode("utf-8"))
    stderr_sha256 = sha256_bytes(producer_stderr.encode("utf-8"))
    if capture.get("producer_stdout_sha256") != stdout_sha256:
        raise HarnessError("producer stdout digest mismatch inside child capture")
    if capture.get("producer_stderr_sha256") != stderr_sha256:
        raise HarnessError("producer stderr digest mismatch inside child capture")

    witness = capture.get("apparatus_witness")
    if not isinstance(witness, dict):
        raise HarnessError("child capture missing apparatus_witness")

    if witness.get("parse_manifest_calls") != 2 or witness.get("parse_manifest_returns") != 2:
        raise HarnessError("child witness does not establish two parse_manifest calls/returns")

    route_calls = witness.get("route_calls")
    route_returns = witness.get("route_returns")
    if not isinstance(route_calls, list) or len(route_calls) != 2:
        raise HarnessError("child witness does not establish two route calls")
    if not isinstance(route_returns, list) or len(route_returns) != 2:
        raise HarnessError("child witness does not establish two route returns")

    for index, call in enumerate(route_calls):
        if not isinstance(call, dict):
            raise HarnessError(f"route call {index} witness is malformed")
        if call.get("source_node_id") != "NODE_01":
            raise HarnessError(f"route call {index} source mismatch")
        if call.get("target_node_id") != "NODE_04":
            raise HarnessError(f"route call {index} target mismatch")

    try:
        emitted = json.loads(producer_stdout)
    except json.JSONDecodeError as exc:
        raise HarnessError(f"captured producer stdout is not JSON: {exc}") from exc
    if not isinstance(emitted, dict):
        raise HarnessError("captured producer stdout JSON root must be an object")

    raw = emitted.get("raw_observation")
    producer_result = emitted.get("mechanical_result")
    if not isinstance(raw, dict):
        raise HarnessError("captured stdout lacks raw_observation object")
    if not isinstance(producer_result, dict):
        raise HarnessError("captured stdout lacks mechanical_result object")

    expected_from_witness = {
        "A_SELECTED_NODE_PATH": route_returns[0].get("node_path"),
        "A_HOP_COUNT": route_returns[0].get("hop_count"),
        "B_SELECTED_NODE_PATH": route_returns[1].get("node_path"),
        "B_HOP_COUNT": route_returns[1].get("hop_count"),
    }
    for field, witnessed in expected_from_witness.items():
        if raw.get(field) != witnessed:
            raise HarnessError(
                f"captured observation not bound to witnessed apparatus return for {field}"
            )

    a_sha256 = sha256_bytes(paths["A"].read_bytes())
    b_sha256 = sha256_bytes(paths["B"].read_bytes())
    if raw.get("A_manifest_sha256") != a_sha256:
        raise HarnessError("captured observation A hash mismatch")
    if raw.get("B_manifest_sha256") != b_sha256:
        raise HarnessError("captured observation B hash mismatch")

    recomputed = {
        "schema_version": "atlas_route_selection_mechanical_result_v0",
        "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
        "verdict": (
            "PASS"
            if raw.get("A_SELECTED_NODE_PATH") == raw.get("B_SELECTED_NODE_PATH")
            else "FRACTURE"
        ),
    }
    if producer_result != recomputed:
        raise HarnessError(
            "producer mechanical result differs from independent recomputation"
        )

    return raw, recomputed


def validate_evidence(evidence: dict[str, Any]) -> None:
    if evidence.get("schema_version") != SCHEMA_VERSION:
        raise HarnessError("evidence schema_version mismatch")

    capture = evidence.get("capture")
    raw = evidence.get("raw_observation")
    result = evidence.get("mechanical_result")
    receipt = evidence.get("receipt")
    if not isinstance(capture, dict):
        raise HarnessError("evidence capture missing")
    if not isinstance(raw, dict):
        raise HarnessError("evidence raw_observation missing")
    if not isinstance(result, dict):
        raise HarnessError("evidence mechanical_result missing")
    if not isinstance(receipt, dict):
        raise HarnessError("evidence receipt missing")

    child_stdout = capture.get("child_stdout")
    child_stderr = capture.get("child_stderr")
    if not isinstance(child_stdout, str) or not isinstance(child_stderr, str):
        raise HarnessError("capture stdout/stderr must be strings")

    if capture.get("child_stdout_sha256") != sha256_bytes(child_stdout.encode("utf-8")):
        raise HarnessError("captured child stdout digest mismatch")
    if capture.get("child_stderr_sha256") != sha256_bytes(child_stderr.encode("utf-8")):
        raise HarnessError("captured child stderr digest mismatch")

    producer_stdout = receipt.get("producer_stdout")
    if not isinstance(producer_stdout, str):
        raise HarnessError("receipt missing producer_stdout")
    if receipt.get("producer_stdout_sha256") != sha256_bytes(
        producer_stdout.encode("utf-8")
    ):
        raise HarnessError("receipt producer stdout digest mismatch")

    try:
        emitted = json.loads(producer_stdout)
    except json.JSONDecodeError as exc:
        raise HarnessError("receipt producer stdout is not JSON") from exc
    if emitted.get("raw_observation") != raw:
        raise HarnessError("receipt producer stdout raw observation mismatch")

    recomputed = {
        "schema_version": "atlas_route_selection_mechanical_result_v0",
        "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
        "verdict": (
            "PASS"
            if raw.get("A_SELECTED_NODE_PATH") == raw.get("B_SELECTED_NODE_PATH")
            else "FRACTURE"
        ),
    }
    if result != recomputed:
        raise HarnessError("mechanical result mismatch with independent recomputation")
    if receipt.get("mechanical_result") != recomputed:
        raise HarnessError("receipt mechanical result mismatch")

    if receipt.get("raw_observation_sha256") != sha256_bytes(
        json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ):
        raise HarnessError("receipt raw observation digest mismatch")

    if receipt.get("mechanical_result_sha256") != sha256_bytes(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ):
        raise HarnessError("receipt mechanical result digest mismatch")


def run_once() -> dict[str, Any]:
    identities = load_identities()
    paths = verify_frozen_identities(identities)

    env = {
        "PYTHONPATH": str(_repo_root()),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if "SYSTEMROOT" in os.environ:
        env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    if "WINDIR" in os.environ:
        env["WINDIR"] = os.environ["WINDIR"]

    command = [sys.executable, "-S", str(paths["child_wrapper"])]
    completed = subprocess.run(
        command,
        cwd=_repo_root(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    child_stdout = completed.stdout
    child_stderr = completed.stderr
    if completed.returncode != 0:
        raise HarnessError(
            "child execution failed: "
            f"exit={completed.returncode}, stderr={child_stderr.strip()!r}"
        )
    if child_stderr:
        raise HarnessError("child wrapper wrote to stderr on successful execution")

    try:
        child_capture = json.loads(child_stdout)
    except json.JSONDecodeError as exc:
        raise HarnessError(f"child stdout is not one JSON object: {exc}") from exc
    if not isinstance(child_capture, dict):
        raise HarnessError("child stdout JSON root must be an object")

    raw, mechanical_result = _validate_child_capture(
        child_capture,
        identities=identities,
        paths=paths,
    )

    raw_canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"))
    result_canonical = json.dumps(mechanical_result, sort_keys=True, separators=(",", ":"))
    producer_stdout = child_capture["producer_stdout"]

    evidence = {
        "schema_version": SCHEMA_VERSION,
        "capture": {
            "child_process_started": True,
            "child_exit_code": completed.returncode,
            "child_command": [
                "<python>",
                "-S",
                identities["child_wrapper"]["path"],
            ],
            "child_stdout": child_stdout,
            "child_stderr": child_stderr,
            "child_stdout_sha256": sha256_bytes(child_stdout.encode("utf-8")),
            "child_stderr_sha256": sha256_bytes(child_stderr.encode("utf-8")),
        },
        "raw_observation": raw,
        "mechanical_result": mechanical_result,
        "receipt": {
            "schema_version": "atlas_route_selection_execution_receipt_v0",
            "contract_freeze_commit": identities["contract_freeze_commit"],
            "identity_manifest_id": identities["identity_manifest_id"],
            "frozen_blob_identities": {
                key: identities[key]["blob_sha1"]
                for key in ("harness", "child_wrapper", "apparatus", "producer", "A", "B")
            },
            "producer_stdout": producer_stdout,
            "producer_stdout_sha256": sha256_bytes(producer_stdout.encode("utf-8")),
            "raw_observation_sha256": sha256_bytes(raw_canonical.encode("utf-8")),
            "mechanical_result": mechanical_result,
            "mechanical_result_sha256": sha256_bytes(result_canonical.encode("utf-8")),
            "apparatus_witness": child_capture["apparatus_witness"],
            "scientific_promotion": "NONE",
            "merge_authority": "NONE",
        },
    }
    validate_evidence(evidence)
    return evidence


def main() -> int:
    if len(sys.argv) != 1:
        print(
            json.dumps(
                {
                    "schema_version": "atlas_route_selection_harness_error_v0",
                    "error": "harness accepts no expected vector, raw observation, or verdict input",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 64

    try:
        evidence = run_once()
    except HarnessError as exc:
        print(
            json.dumps(
                {
                    "schema_version": "atlas_route_selection_harness_error_v0",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 65

    print(json.dumps(evidence, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
