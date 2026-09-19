"""Bounded execution-evidence harness for ATLAS_ROUTE_SELECTION_001.

This module does not select routing policy or instantiate Atlas nodes. It only
establishes a causal execution-evidence chain around the already-frozen
route-selection producer and apparatus.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping

PRESSURE_ID = "ATLAS_ROUTE_SELECTION_001"
SOURCE_NODE_ID = "NODE_01"
TARGET_NODE_ID = "NODE_04"

HARNESS_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/execution_evidence_harness.py")
CHILD_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/execution_evidence_child.py")
ATLAS_REL = Path("lab/ops/candidates/atlas_five_node_v0/atlas.py")
PRODUCER_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/run_pressure.py")
A_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/A_manifest.json")
B_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/B_manifest.json")

ATLAS_BLOB = "15624c5b8a1a42546471fc64d0f7d85ada6d1791"
ATLAS_SHA256 = "97f7b0d83e891692a1d1b7dcc64ececeadc7748615a29ba18d1aaeafb920c352"
PRODUCER_BLOB = "8d133fc5356cadf6ca53f506b01c6a8494cbc18b"
PRODUCER_SHA256 = "9364fc4c6ef30b35d581bbe25d1f018bb0611b1d5c35f4e9b6d2782d4d207a15"
A_BLOB = "af8b1cc3139dcfece37996f7a420fa10d6bc55d8"
A_SHA256 = "8f953cd1611d95e4a3eeb87c10acf49e67fbbb318a760c6c281077707f65db57"
B_BLOB = "f761a391c232c1532418c27ab3ca77603377d02d"
B_SHA256 = "3014440b1cb95d1f12bd3d004ecd60465eae388e14dd4f27b71408096b7d721a"

RUNTIME_IMPLEMENTATION = "cpython"
RUNTIME_VERSION = (3, 13, 5)
RUNTIME_CACHE_TAG = "cpython-313"
RUNTIME_FLAGS = ("-I", "-S")

OBSERVATION_FIELDS = (
    "A_SELECTED_NODE_PATH",
    "A_HOP_COUNT",
    "B_SELECTED_NODE_PATH",
    "B_HOP_COUNT",
)
EXPECTED_CALL_SEQUENCE = ("parse_manifest", "route", "parse_manifest", "route")


class ExecutionEvidenceError(RuntimeError):
    pass


class FrozenIdentityMismatch(ExecutionEvidenceError):
    pass


class ProcessExecutionInvalid(ExecutionEvidenceError):
    pass


class ApparatusWitnessInvalid(ExecutionEvidenceError):
    pass


class CapturedOutputInvalid(ExecutionEvidenceError):
    pass


class MechanicalResultMismatch(ExecutionEvidenceError):
    pass


class ReceiptInvalid(ExecutionEvidenceError):
    pass


@dataclass(frozen=True)
class InputCoordinates:
    a_blob: str
    a_sha256: str
    b_blob: str
    b_sha256: str


FROZEN_INPUTS = InputCoordinates(A_BLOB, A_SHA256, B_BLOB, B_SHA256)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())


def _verify_bytes(path: Path, *, blob: str | None = None, sha256: str | None = None) -> bytes:
    data = Path(path).read_bytes()
    if blob is not None and _git_blob(data) != blob:
        raise FrozenIdentityMismatch(f"git blob mismatch: {path}")
    if sha256 is not None and _sha256(data) != sha256:
        raise FrozenIdentityMismatch(f"sha256 mismatch: {path}")
    return data


def _runtime_coordinate() -> dict[str, Any]:
    return {
        "implementation": sys.implementation.name,
        "version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro],
        "cache_tag": sys.implementation.cache_tag,
        "python_executable": str(Path(sys.executable).resolve()),
        "platform": platform.platform(),
        "subprocess_flags": list(RUNTIME_FLAGS),
    }


def _verify_runtime() -> None:
    observed = (sys.implementation.name, tuple(sys.version_info[:3]), sys.implementation.cache_tag)
    expected = (RUNTIME_IMPLEMENTATION, RUNTIME_VERSION, RUNTIME_CACHE_TAG)
    if observed != expected:
        raise FrozenIdentityMismatch(f"runtime coordinate mismatch: observed={observed!r}, expected={expected!r}")


def _verify_source_tree(
    source_root: Path,
    *,
    expected_harness_blob: str,
    expected_child_blob: str,
    inputs: InputCoordinates,
) -> dict[str, bytes]:
    root = Path(source_root).resolve()
    _verify_runtime()
    verified = {
        "harness": _verify_bytes(root / HARNESS_REL, blob=expected_harness_blob),
        "child": _verify_bytes(root / CHILD_REL, blob=expected_child_blob),
        "producer": _verify_bytes(root / PRODUCER_REL, blob=PRODUCER_BLOB, sha256=PRODUCER_SHA256),
        "atlas": _verify_bytes(root / ATLAS_REL, blob=ATLAS_BLOB, sha256=ATLAS_SHA256),
        "A": _verify_bytes(root / A_REL, blob=inputs.a_blob, sha256=inputs.a_sha256),
        "B": _verify_bytes(root / B_REL, blob=inputs.b_blob, sha256=inputs.b_sha256),
    }
    return verified


def _reconstruct_isolated_tree(source_root: Path, destination: Path) -> None:
    root = Path(source_root).resolve()
    for rel in (ATLAS_REL, PRODUCER_REL, A_REL, B_REL, CHILD_REL):
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, target)


def _validate_witness(
    witness: Mapping[str, Any],
    *,
    exec_root: Path,
    expected_child_blob: str,
) -> dict[str, Any]:
    required_top = {
        "schema_version", "producer_completed", "producer_error_type", "producer_origin",
        "producer_blob", "atlas_origin", "atlas_blob", "child_wrapper_origin",
        "child_wrapper_blob", "source_node_id", "target_node_id", "call_events", "python",
    }
    if set(witness) != required_top:
        raise ApparatusWitnessInvalid("witness schema mismatch")
    if witness["schema_version"] != "atlas_route_selection_apparatus_call_witness_v0":
        raise ApparatusWitnessInvalid("witness schema_version mismatch")
    if witness["producer_completed"] is not True or witness["producer_error_type"] is not None:
        raise ApparatusWitnessInvalid("producer did not complete under witness")
    if witness["producer_blob"] != PRODUCER_BLOB or witness["atlas_blob"] != ATLAS_BLOB:
        raise ApparatusWitnessInvalid("producer/apparatus identity mismatch in witness")
    if witness["child_wrapper_blob"] != expected_child_blob:
        raise ApparatusWitnessInvalid("child-wrapper identity mismatch in witness")
    if witness["source_node_id"] != SOURCE_NODE_ID or witness["target_node_id"] != TARGET_NODE_ID:
        raise ApparatusWitnessInvalid("witness source/target mismatch")

    producer_origin = str((exec_root / PRODUCER_REL).resolve())
    atlas_origin = str((exec_root / ATLAS_REL).resolve())
    child_origin = str((exec_root / CHILD_REL).resolve())
    if witness["producer_origin"] != producer_origin:
        raise ApparatusWitnessInvalid("producer origin mismatch")
    if witness["atlas_origin"] != atlas_origin:
        raise ApparatusWitnessInvalid("atlas origin mismatch")
    if witness["child_wrapper_origin"] != child_origin:
        raise ApparatusWitnessInvalid("child-wrapper origin mismatch")

    events = witness["call_events"]
    if not isinstance(events, list) or tuple(event.get("function") for event in events) != EXPECTED_CALL_SEQUENCE:
        raise ApparatusWitnessInvalid("frozen apparatus call sequence not witnessed")
    for index, event in enumerate(events, start=1):
        if event.get("ordinal") != index or event.get("returned") is not True:
            raise ApparatusWitnessInvalid("incomplete apparatus call event")
        if event.get("caller_origin") != producer_origin:
            raise ApparatusWitnessInvalid("apparatus call did not originate in exact producer")
        if event.get("atlas_code_origin") != atlas_origin or event.get("atlas_blob") != ATLAS_BLOB:
            raise ApparatusWitnessInvalid("apparatus call did not originate in exact atlas.py")
        if event["function"] == "route":
            if event.get("source_node_id") != SOURCE_NODE_ID or event.get("target_node_id") != TARGET_NODE_ID:
                raise ApparatusWitnessInvalid("route source/target mismatch")

    py = witness["python"]
    if py != {
        "implementation": RUNTIME_IMPLEMENTATION,
        "version": list(RUNTIME_VERSION),
        "cache_tag": RUNTIME_CACHE_TAG,
        "isolated": True,
        "no_site": True,
    }:
        raise ApparatusWitnessInvalid("child runtime coordinate mismatch")
    return dict(witness)


def _parse_captured_stdout(stdout: bytes, *, inputs: InputCoordinates) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        root = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CapturedOutputInvalid("captured stdout is not one JSON object") from exc
    if not isinstance(root, dict) or set(root) != {"raw_observation", "mechanical_result"}:
        raise CapturedOutputInvalid("captured producer output schema mismatch")
    raw = root["raw_observation"]
    reported = root["mechanical_result"]
    if not isinstance(raw, dict) or not isinstance(reported, dict):
        raise CapturedOutputInvalid("captured producer output members must be objects")
    required_raw = {
        "schema_version", "apparatus_invoked", "source_node_id", "target_node_id",
        "A_manifest_sha256", "B_manifest_sha256", *OBSERVATION_FIELDS,
    }
    if set(raw) != required_raw:
        raise CapturedOutputInvalid("raw observation schema mismatch")
    if raw["source_node_id"] != SOURCE_NODE_ID or raw["target_node_id"] != TARGET_NODE_ID:
        raise CapturedOutputInvalid("captured source/target mismatch")
    if raw["A_manifest_sha256"] != inputs.a_sha256 or raw["B_manifest_sha256"] != inputs.b_sha256:
        raise CapturedOutputInvalid("captured input digests mismatch")
    return raw, reported


def _independent_mechanical_result(raw: Mapping[str, Any]) -> dict[str, str]:
    a_path = raw["A_SELECTED_NODE_PATH"]
    b_path = raw["B_SELECTED_NODE_PATH"]
    return {
        "schema_version": "atlas_route_selection_mechanical_result_v0",
        "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
        "verdict": "PASS" if a_path == b_path else "FRACTURE",
    }


def _validate_reported_result(raw: Mapping[str, Any], reported: Mapping[str, Any]) -> dict[str, str]:
    independent = _independent_mechanical_result(raw)
    if dict(reported) != independent:
        raise MechanicalResultMismatch("producer mechanical result differs from independent recomputation")
    return independent


def _require_witness_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ApparatusWitnessInvalid("actual subprocess produced no apparatus-call witness")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApparatusWitnessInvalid("apparatus-call witness is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ApparatusWitnessInvalid("apparatus-call witness root must be an object")
    return value


def _execute(
    source_root: Path,
    output_root: Path,
    *,
    expected_harness_blob: str,
    expected_child_blob: str,
    inputs: InputCoordinates,
) -> dict[str, Any]:
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()
    verified = _verify_source_tree(
        source_root,
        expected_harness_blob=expected_harness_blob,
        expected_child_blob=expected_child_blob,
        inputs=inputs,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    if any((output_root / name).exists() for name in ("raw_observation.json", "mechanical_result.json", "runtime_receipt.json")):
        raise ExecutionEvidenceError("evidence output path is not fresh")

    with tempfile.TemporaryDirectory(prefix="atlas_route_selection_exec_") as temp:
        exec_root = Path(temp) / "tree"
        _reconstruct_isolated_tree(source_root, exec_root)

        # Recheck reconstructed bytes immediately before child entry.
        _verify_bytes(exec_root / ATLAS_REL, blob=ATLAS_BLOB, sha256=ATLAS_SHA256)
        _verify_bytes(exec_root / PRODUCER_REL, blob=PRODUCER_BLOB, sha256=PRODUCER_SHA256)
        _verify_bytes(exec_root / A_REL, blob=inputs.a_blob, sha256=inputs.a_sha256)
        _verify_bytes(exec_root / B_REL, blob=inputs.b_blob, sha256=inputs.b_sha256)
        _verify_bytes(exec_root / CHILD_REL, blob=expected_child_blob)

        witness_path = Path(temp) / "apparatus_call_witness.json"
        command = [
            sys.executable, *RUNTIME_FLAGS, str(exec_root / CHILD_REL),
            "--root", str(exec_root),
            "--witness", str(witness_path),
            "--atlas-blob", ATLAS_BLOB,
            "--producer-blob", PRODUCER_BLOB,
            "--a-blob", inputs.a_blob,
            "--a-sha256", inputs.a_sha256,
            "--b-blob", inputs.b_blob,
            "--b-sha256", inputs.b_sha256,
            "--child-blob", expected_child_blob,
        ]
        proc = subprocess.run(command, cwd=exec_root, capture_output=True, check=False, env={"PATH": os.environ.get("PATH", "")})

        capture = {
            "schema_version": "atlas_route_selection_process_capture_v0",
            "exit_status": proc.returncode,
            "stdout_sha256": _sha256(proc.stdout),
            "stderr_sha256": _sha256(proc.stderr),
            "stdout_size": len(proc.stdout),
            "stderr_size": len(proc.stderr),
            "runtime_coordinate": _runtime_coordinate(),
        }
        _write_exclusive(output_root / "capture_stdout.bin", proc.stdout)
        _write_exclusive(output_root / "capture_stderr.bin", proc.stderr)
        _write_exclusive(output_root / "process_capture.json", _canonical(capture))

        if proc.returncode != 0:
            raise ProcessExecutionInvalid(f"producer subprocess exit status {proc.returncode}")

        witness_raw = _require_witness_file(witness_path)
        witness = _validate_witness(witness_raw, exec_root=exec_root, expected_child_blob=expected_child_blob)
        witness_bytes = _canonical(witness)
        _write_exclusive(output_root / "apparatus_call_witness.json", witness_bytes)

        raw, reported = _parse_captured_stdout(proc.stdout, inputs=inputs)
        independent = _validate_reported_result(raw, reported)

        raw_bytes = _canonical(raw)
        result_bytes = _canonical(independent)
        _write_exclusive(output_root / "raw_observation.json", raw_bytes)
        _write_exclusive(output_root / "mechanical_result.json", result_bytes)

        receipt = {
            "schema_version": "atlas_route_selection_execution_evidence_receipt_v0",
            "pressure_id": PRESSURE_ID,
            "status": "MECHANICALLY_ADMISSIBLE_EXECUTION_EVIDENCE",
            "identities": {
                "harness_blob": expected_harness_blob,
                "child_wrapper_blob": expected_child_blob,
                "producer_blob": PRODUCER_BLOB,
                "producer_sha256": PRODUCER_SHA256,
                "atlas_blob": ATLAS_BLOB,
                "atlas_sha256": ATLAS_SHA256,
                "A_blob": inputs.a_blob,
                "A_sha256": inputs.a_sha256,
                "B_blob": inputs.b_blob,
                "B_sha256": inputs.b_sha256,
            },
            "runtime_coordinate": _runtime_coordinate(),
            "runtime_call_provenance": {
                "parse_manifest_call_count": sum(e["function"] == "parse_manifest" for e in witness["call_events"]),
                "route_call_count": sum(e["function"] == "route" for e in witness["call_events"]),
                "route_source_node_id": SOURCE_NODE_ID,
                "route_target_node_id": TARGET_NODE_ID,
                "producer_origin": witness["producer_origin"],
                "atlas_origin": witness["atlas_origin"],
                "call_sequence": [e["function"] for e in witness["call_events"]],
            },
            "capture": {
                "exit_status": proc.returncode,
                "stdout_sha256": _sha256(proc.stdout),
                "stderr_sha256": _sha256(proc.stderr),
                "witness_sha256": _sha256(witness_bytes),
            },
            "raw_observation_sha256": _sha256(raw_bytes),
            "mechanical_result_sha256": _sha256(result_bytes),
            "serialization_order": ["process_capture", "apparatus_call_witness", "raw_observation", "mechanical_result", "runtime_receipt"],
        }
        receipt_bytes = _canonical(receipt)
        _write_exclusive(output_root / "runtime_receipt.json", receipt_bytes)
        return receipt


def run_frozen_execution_evidence(
    source_root: str | Path,
    output_root: str | Path,
    *,
    expected_harness_blob: str,
    expected_child_wrapper_blob: str,
) -> dict[str, Any]:
    """Execute only the exact frozen Atlas producer/apparatus/A/B coordinates.

    No expected observation, path, verdict, caller-authored raw observation, or
    caller-authored mechanical result is accepted by this interface.
    """
    return _execute(
        Path(source_root),
        Path(output_root),
        expected_harness_blob=expected_harness_blob,
        expected_child_blob=expected_child_wrapper_blob,
        inputs=FROZEN_INPUTS,
    )


def validate_runtime_receipt(output_root: str | Path) -> None:
    root = Path(output_root)
    try:
        stdout = (root / "capture_stdout.bin").read_bytes()
        stderr = (root / "capture_stderr.bin").read_bytes()
        witness_bytes = (root / "apparatus_call_witness.json").read_bytes()
        raw_bytes = (root / "raw_observation.json").read_bytes()
        result_bytes = (root / "mechanical_result.json").read_bytes()
        receipt = json.loads((root / "runtime_receipt.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ReceiptInvalid("receipt dependency missing or malformed") from exc

    capture = receipt.get("capture", {})
    if capture.get("stdout_sha256") != _sha256(stdout):
        raise ReceiptInvalid("captured stdout digest mismatch")
    if capture.get("stderr_sha256") != _sha256(stderr):
        raise ReceiptInvalid("captured stderr digest mismatch")
    if capture.get("witness_sha256") != _sha256(witness_bytes):
        raise ReceiptInvalid("witness digest mismatch")
    if receipt.get("raw_observation_sha256") != _sha256(raw_bytes):
        raise ReceiptInvalid("raw observation digest mismatch")
    if receipt.get("mechanical_result_sha256") != _sha256(result_bytes):
        raise ReceiptInvalid("mechanical result digest mismatch")

    try:
        raw = json.loads(raw_bytes)
        result = json.loads(result_bytes)
    except json.JSONDecodeError as exc:
        raise ReceiptInvalid("derived artifact JSON malformed") from exc
    if result != _independent_mechanical_result(raw):
        raise ReceiptInvalid("stored mechanical result differs from independent recomputation")
