"""Workshop Frozen Cell v0: deterministic one-cell execution boundary.

Phase A intentionally contains no provider API and no experiment semantics.
The runner verifies bytes and declared transitions, invokes one supplied adapter
at most once, retains output through a supplied sink, and halts on deviation.

Manifest != receipt != fault.
Declared invocation state != observed invocation state != unobservable state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Protocol

from lab.ops.candidates.execution_stop_latch_001.stop_latch import (
    ExecutionStopLatch,
    ExecutionStopLatchError,
)


MANIFEST_SCHEMA = "workshop_frozen_cell_manifest_v0"
RECEIPT_SCHEMA = "workshop_cell_receipt_v0"
FAULT_SCHEMA = "workshop_fault_v0"

VERIFY_REQUIRED = "VERIFIABLE_REQUIRED"
DECLARED_ONLY = "DECLARED_ONLY"
UNOBSERVABLE = "UNOBSERVABLE"
VERIFICATION_CLASSES = {VERIFY_REQUIRED, DECLARED_ONLY, UNOBSERVABLE}

STATE_LOADED = "LOADED"
STATE_MANIFEST_VERIFIED = "MANIFEST_VERIFIED"
STATE_INPUTS_VERIFIED = "INPUTS_VERIFIED"
STATE_PAYLOAD_VERIFIED = "PAYLOAD_VERIFIED"
STATE_AUTHORITY_ADMITTED = "AUTHORITY_ADMITTED"
STATE_INVOCATION_VERIFIED = "INVOCATION_VERIFIED"
STATE_INVOKED = "INVOKED"
STATE_OUTPUT_CAPTURED = "OUTPUT_CAPTURED"
STATE_OUTPUT_RETAINED = "OUTPUT_RETAINED"
STATE_RECEIPT_COMMITTED = "RECEIPT_COMMITTED"
STATE_HALTED = "HALTED"

E001 = "E001_MANIFEST_SCHEMA_INVALID"
E002 = "E002_MANIFEST_IDENTITY_MISMATCH"
E003 = "E003_CONDITION_PACKET_MISMATCH"
E004 = "E004_SPECIMEN_MISMATCH"
E005 = "E005_PAYLOAD_ASSEMBLY_MISMATCH"
E006 = "E006_INVOCATION_SURFACE_MISMATCH"
E007 = "E007_UNDECLARED_CONTEXT_DETECTED"
E008 = "E008_EVIDENCE_ACCESS_MISMATCH"
E009 = "E009_INVOCATION_ALREADY_CONSUMED"
E010 = "E010_MODEL_INVOCATION_FAILURE"
E011 = "E011_OUTPUT_CAPTURE_FAILURE"
E012 = "E012_OUTPUT_HASH_FAILURE"
E013 = "E013_ANONYMIZATION_FAILURE"
E014 = "E014_RECEIPT_WRITE_FAILURE"
E015 = "E015_AUTHORIZATION_MISMATCH"
E016 = "E016_FORBIDDEN_RETRY_REQUEST"
E017 = "E017_UNSPECIFIED_DEVIATION"

_HEX64 = set("0123456789abcdef")
_TOP_LEVEL = {
    "schema",
    "manifest_id",
    "experiment_id",
    "cell_id",
    "basis",
    "inputs",
    "assembly",
    "invocation",
    "execution",
    "output",
}
_BASIS_FIELDS = {"contract_commit", "authorization_ref"}
_INPUT_FIELDS = {"path", "sha256"}
_ASSEMBLY_FIELDS = {
    "encoding",
    "newline",
    "separator",
    "order",
    "expected_payload_sha256",
}
_INVOCATION_FIELDS = {"adapter", "surface"}
_SURFACE_FIELDS = {"expected", "verification"}
_EXECUTION_FIELDS = {
    "max_invocations",
    "retry_allowed",
    "repair_allowed",
    "skip_allowed",
    "best_effort_allowed",
}
_OUTPUT_FIELDS = {"retain_raw", "hash_raw", "anonymize"}


class InvocationAdapter(Protocol):
    invocation_count: int

    def observe_surface(self) -> Mapping[str, Any]:
        """Return independently observable invocation coordinates."""

    def invoke(self, payload: bytes) -> bytes:
        """Execute exactly one invocation and return raw output bytes."""


class OutputSink(Protocol):
    def write_raw(self, cell_id: str, payload: bytes) -> str:
        """Retain raw output and return an opaque reference."""

    def read_raw(self, ref: str) -> bytes:
        """Read retained output bytes for identity verification."""


class InvocationFailure(RuntimeError):
    """Known invocation failure."""


class OutputCaptureFailure(RuntimeError):
    """Known output-retention failure."""


@dataclass
class MockInvocationAdapter:
    """Deterministic Phase A adapter keyed only by assembled payload SHA-256."""

    observed_surface: dict[str, Any]
    responses_by_payload_sha256: dict[str, bytes]
    invocation_count: int = 0
    observe_error: Exception | None = None
    invoke_error: Exception | None = None

    def observe_surface(self) -> Mapping[str, Any]:
        if self.observe_error is not None:
            raise self.observe_error
        return dict(self.observed_surface)

    def invoke(self, payload: bytes) -> bytes:
        self.invocation_count += 1
        if self.invoke_error is not None:
            raise self.invoke_error
        digest = sha256_bytes(payload)
        if digest not in self.responses_by_payload_sha256:
            raise InvocationFailure(f"no deterministic response for payload {digest}")
        return bytes(self.responses_by_payload_sha256[digest])


@dataclass
class MemoryOutputSink:
    """In-memory retention surface used only for deterministic Phase A pressure."""

    fail_write: bool = False
    corrupt_after_write: bool = False
    _items: dict[str, bytes] = field(default_factory=dict)

    def write_raw(self, cell_id: str, payload: bytes) -> str:
        if self.fail_write:
            raise OutputCaptureFailure("simulated output capture failure")
        ref = f"memory://{cell_id}/raw"
        stored = bytes(payload)
        if self.corrupt_after_write:
            stored += b"!"
        self._items[ref] = stored
        return ref

    def read_raw(self, ref: str) -> bytes:
        return self._items[ref]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run_frozen_cell(
    *,
    manifest_bytes: bytes,
    authorized_manifest_sha256: str,
    root: Path,
    adapter: InvocationAdapter,
    output_sink: OutputSink,
    execution_stop_latch: ExecutionStopLatch | None = None,
) -> dict[str, Any]:
    """Run one frozen cell or return one terminal fault.

    v0 has no transition out of HALTED and no retry path.
    """

    trace = [STATE_LOADED]
    actual_manifest_sha = sha256_bytes(manifest_bytes)

    if actual_manifest_sha != authorized_manifest_sha256:
        return _fault(
            code=E002,
            stage=STATE_LOADED,
            transition_blocked=STATE_MANIFEST_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=None,
            adapter=adapter,
            expected={"sha256": authorized_manifest_sha256},
            observed={"sha256": actual_manifest_sha},
        )

    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _fault(
            code=E001,
            stage=STATE_LOADED,
            transition_blocked=STATE_MANIFEST_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=None,
            adapter=adapter,
            observed={"error": str(exc)},
        )

    shape_errors = manifest_shape_errors(manifest)
    if shape_errors:
        return _fault(
            code=E001,
            stage=STATE_LOADED,
            transition_blocked=STATE_MANIFEST_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=_safe_cell_id(manifest),
            adapter=adapter,
            observed={"errors": shape_errors},
        )

    cell_id = manifest["cell_id"]
    trace.append(STATE_MANIFEST_VERIFIED)

    if manifest["basis"]["authorization_ref"] == "":
        return _fault(
            code=E015,
            stage=STATE_MANIFEST_VERIFIED,
            transition_blocked=STATE_INPUTS_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"authorization_ref": ""},
        )

    try:
        component_bytes: dict[str, bytes] = {}
        for name in manifest["assembly"]["order"]:
            entry = manifest["inputs"][name]
            payload = _read_relative(root, entry["path"])
            observed_sha = sha256_bytes(payload)
            if observed_sha != entry["sha256"]:
                code = E004 if name == "specimen" else E003
                return _fault(
                    code=code,
                    stage=STATE_MANIFEST_VERIFIED,
                    transition_blocked=STATE_INPUTS_VERIFIED,
                    trace=trace,
                    manifest_sha256=actual_manifest_sha,
                    cell_id=cell_id,
                    adapter=adapter,
                    expected={"component": name, "sha256": entry["sha256"]},
                    observed={"component": name, "sha256": observed_sha},
                )
            payload.decode("utf-8")
            component_bytes[name] = payload
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return _fault(
            code=E004 if _exception_mentions_specimen(exc) else E003,
            stage=STATE_MANIFEST_VERIFIED,
            transition_blocked=STATE_INPUTS_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error": str(exc)},
        )

    trace.append(STATE_INPUTS_VERIFIED)

    separator = manifest["assembly"]["separator"].encode("utf-8")
    payload = separator.join(component_bytes[name] for name in manifest["assembly"]["order"])
    payload_sha = sha256_bytes(payload)
    expected_payload_sha = manifest["assembly"]["expected_payload_sha256"]
    if payload_sha != expected_payload_sha:
        return _fault(
            code=E005,
            stage=STATE_INPUTS_VERIFIED,
            transition_blocked=STATE_PAYLOAD_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            expected={"sha256": expected_payload_sha},
            observed={"sha256": payload_sha},
        )

    trace.append(STATE_PAYLOAD_VERIFIED)

    if adapter.invocation_count != 0:
        return _fault(
            code=E009,
            stage=STATE_PAYLOAD_VERIFIED,
            transition_blocked=STATE_INVOCATION_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            expected={"invocation_count": 0},
            observed={"invocation_count": adapter.invocation_count},
        )

    if execution_stop_latch is not None:
        try:
            execution_stop_latch.require_active(
                "run_frozen_cell.adapter_dispatch"
            )
        except ExecutionStopLatchError as exc:
            return _fault(
                code=E015,
                stage=STATE_PAYLOAD_VERIFIED,
                transition_blocked=STATE_INVOCATION_VERIFIED,
                trace=trace,
                manifest_sha256=actual_manifest_sha,
                cell_id=cell_id,
                adapter=adapter,
                expected={
                    "execution_authority_state": "ACTIVE",
                    "execution_envelope_id": execution_stop_latch.execution_envelope_id,
                },
                observed={
                    "execution_authority_state": "BLOCKED",
                    "execution_envelope_id": execution_stop_latch.execution_envelope_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )
        except Exception as exc:
            return _fault(
                code=E017,
                stage=STATE_PAYLOAD_VERIFIED,
                transition_blocked=STATE_INVOCATION_VERIFIED,
                trace=trace,
                manifest_sha256=actual_manifest_sha,
                cell_id=cell_id,
                adapter=adapter,
                observed={
                    "execution_envelope_id": execution_stop_latch.execution_envelope_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )
        trace.append(STATE_AUTHORITY_ADMITTED)

    try:
        observed_surface = dict(adapter.observe_surface())
    except Exception as exc:
        return _fault(
            code=E017,
            stage=STATE_PAYLOAD_VERIFIED,
            transition_blocked=STATE_INVOCATION_VERIFIED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error_type": type(exc).__name__, "error": str(exc)},
        )

    surface = manifest["invocation"]["surface"]
    declared: dict[str, Any] = {}
    observed: dict[str, Any] = {}
    unverified: list[str] = []
    unobservable: list[str] = []
    for field_name, field_contract in surface.items():
        expected = field_contract["expected"]
        verification = field_contract["verification"]
        declared[field_name] = expected
        if verification == VERIFY_REQUIRED:
            if field_name not in observed_surface or observed_surface[field_name] != expected:
                return _fault(
                    code=E006,
                    stage=STATE_PAYLOAD_VERIFIED,
                    transition_blocked=STATE_INVOCATION_VERIFIED,
                    trace=trace,
                    manifest_sha256=actual_manifest_sha,
                    cell_id=cell_id,
                    adapter=adapter,
                    expected={"field": field_name, "value": expected},
                    observed={
                        "field": field_name,
                        "value": observed_surface.get(field_name),
                        "available": field_name in observed_surface,
                    },
                )
            observed[field_name] = observed_surface[field_name]
        elif verification == DECLARED_ONLY:
            unverified.append(field_name)
        else:
            unobservable.append(field_name)

    trace.append(STATE_INVOCATION_VERIFIED)

    try:
        raw_output = adapter.invoke(payload)
    except InvocationFailure as exc:
        return _fault(
            code=E010,
            stage=STATE_INVOCATION_VERIFIED,
            transition_blocked=STATE_INVOKED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error": str(exc)},
        )
    except Exception as exc:
        return _fault(
            code=E017,
            stage=STATE_INVOCATION_VERIFIED,
            transition_blocked=STATE_INVOKED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error_type": type(exc).__name__, "error": str(exc)},
        )

    if adapter.invocation_count != 1:
        return _fault(
            code=E009,
            stage=STATE_INVOCATION_VERIFIED,
            transition_blocked=STATE_INVOKED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            expected={"invocation_count": 1},
            observed={"invocation_count": adapter.invocation_count},
        )

    trace.append(STATE_INVOKED)

    if not isinstance(raw_output, (bytes, bytearray)):
        return _fault(
            code=E011,
            stage=STATE_INVOKED,
            transition_blocked=STATE_OUTPUT_CAPTURED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"output_type": type(raw_output).__name__},
        )

    raw_output = bytes(raw_output)
    raw_sha = sha256_bytes(raw_output)
    trace.append(STATE_OUTPUT_CAPTURED)

    try:
        raw_ref = output_sink.write_raw(cell_id, raw_output)
    except OutputCaptureFailure as exc:
        return _fault(
            code=E011,
            stage=STATE_OUTPUT_CAPTURED,
            transition_blocked=STATE_OUTPUT_RETAINED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error": str(exc), "raw_sha256": raw_sha},
        )
    except Exception as exc:
        return _fault(
            code=E017,
            stage=STATE_OUTPUT_CAPTURED,
            transition_blocked=STATE_OUTPUT_RETAINED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error_type": type(exc).__name__, "error": str(exc)},
        )

    try:
        retained = output_sink.read_raw(raw_ref)
    except Exception as exc:
        return _fault(
            code=E011,
            stage=STATE_OUTPUT_CAPTURED,
            transition_blocked=STATE_OUTPUT_RETAINED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"error_type": type(exc).__name__, "error": str(exc), "raw_ref": raw_ref},
        )

    retained_sha = sha256_bytes(retained)
    if retained_sha != raw_sha:
        return _fault(
            code=E012,
            stage=STATE_OUTPUT_CAPTURED,
            transition_blocked=STATE_OUTPUT_RETAINED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            expected={"sha256": raw_sha},
            observed={"sha256": retained_sha, "raw_ref": raw_ref},
        )

    trace.append(STATE_OUTPUT_RETAINED)

    if manifest["output"]["anonymize"]:
        return _fault(
            code=E013,
            stage=STATE_OUTPUT_RETAINED,
            transition_blocked=STATE_RECEIPT_COMMITTED,
            trace=trace,
            manifest_sha256=actual_manifest_sha,
            cell_id=cell_id,
            adapter=adapter,
            observed={"detail": "Phase A v0 does not implement anonymization"},
        )

    trace.append(STATE_RECEIPT_COMMITTED)
    return {
        "schema": RECEIPT_SCHEMA,
        "cell_id": cell_id,
        "manifest_sha256": actual_manifest_sha,
        "authorization_ref": manifest["basis"]["authorization_ref"],
        "terminal": True,
        "execution_status": "COMPLETED",
        "state_trace": trace,
        "verified_inputs": {
            name: manifest["inputs"][name]["sha256"]
            for name in manifest["assembly"]["order"]
        },
        "assembled_payload_sha256": payload_sha,
        "invocation_surface": {
            "declared": declared,
            "observed": observed,
            "unverified": sorted(unverified),
            "unobservable": sorted(unobservable),
        },
        "execution": {
            "model_invoked": True,
            "invocation_count": adapter.invocation_count,
        },
        "output": {
            "raw_sha256": raw_sha,
            "raw_ref": raw_ref,
        },
        "deviations": [],
    }


def manifest_shape_errors(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["manifest must be an object"]
    _exact_keys(value, _TOP_LEVEL, "manifest", errors)
    if value.get("schema") != MANIFEST_SCHEMA:
        errors.append(f"schema must equal {MANIFEST_SCHEMA}")
    for name in ("manifest_id", "experiment_id", "cell_id"):
        _nonempty(value.get(name), name, errors)

    basis = value.get("basis")
    if isinstance(basis, dict):
        _exact_keys(basis, _BASIS_FIELDS, "basis", errors)
        _nonempty(basis.get("contract_commit"), "basis.contract_commit", errors)
        _nonempty(basis.get("authorization_ref"), "basis.authorization_ref", errors)
    else:
        errors.append("basis must be an object")

    inputs = value.get("inputs")
    if not isinstance(inputs, dict) or not inputs:
        errors.append("inputs must be a non-empty object")
    else:
        for name, item in inputs.items():
            if not isinstance(item, dict):
                errors.append(f"inputs.{name} must be an object")
                continue
            _exact_keys(item, _INPUT_FIELDS, f"inputs.{name}", errors)
            _nonempty(item.get("path"), f"inputs.{name}.path", errors)
            _sha64(item.get("sha256"), f"inputs.{name}.sha256", errors)

    assembly = value.get("assembly")
    if isinstance(assembly, dict):
        _exact_keys(assembly, _ASSEMBLY_FIELDS, "assembly", errors)
        if assembly.get("encoding") != "utf-8":
            errors.append("assembly.encoding must equal utf-8")
        if assembly.get("newline") != "lf":
            errors.append("assembly.newline must equal lf")
        if not isinstance(assembly.get("separator"), str):
            errors.append("assembly.separator must be a string")
        order = assembly.get("order")
        if not isinstance(order, list) or not order or not all(isinstance(x, str) and x for x in order):
            errors.append("assembly.order must be a non-empty string array")
        elif len(order) != len(set(order)):
            errors.append("assembly.order must not contain duplicates")
        elif isinstance(inputs, dict) and set(order) != set(inputs):
            errors.append("assembly.order must contain every input exactly once")
        _sha64(assembly.get("expected_payload_sha256"), "assembly.expected_payload_sha256", errors)
    else:
        errors.append("assembly must be an object")

    invocation = value.get("invocation")
    if isinstance(invocation, dict):
        _exact_keys(invocation, _INVOCATION_FIELDS, "invocation", errors)
        _nonempty(invocation.get("adapter"), "invocation.adapter", errors)
        surface = invocation.get("surface")
        if not isinstance(surface, dict) or not surface:
            errors.append("invocation.surface must be a non-empty object")
        else:
            for name, contract in surface.items():
                if not isinstance(contract, dict):
                    errors.append(f"invocation.surface.{name} must be an object")
                    continue
                _exact_keys(contract, _SURFACE_FIELDS, f"invocation.surface.{name}", errors)
                if contract.get("verification") not in VERIFICATION_CLASSES:
                    errors.append(
                        f"invocation.surface.{name}.verification must be one of "
                        f"{sorted(VERIFICATION_CLASSES)}"
                    )
    else:
        errors.append("invocation must be an object")

    execution = value.get("execution")
    if isinstance(execution, dict):
        _exact_keys(execution, _EXECUTION_FIELDS, "execution", errors)
        if execution.get("max_invocations") != 1:
            errors.append("execution.max_invocations must equal 1")
        for name in ("retry_allowed", "repair_allowed", "skip_allowed", "best_effort_allowed"):
            if execution.get(name) is not False:
                errors.append(f"execution.{name} must equal false")
    else:
        errors.append("execution must be an object")

    output = value.get("output")
    if isinstance(output, dict):
        _exact_keys(output, _OUTPUT_FIELDS, "output", errors)
        if output.get("retain_raw") is not True:
            errors.append("output.retain_raw must equal true")
        if output.get("hash_raw") is not True:
            errors.append("output.hash_raw must equal true")
        if not isinstance(output.get("anonymize"), bool):
            errors.append("output.anonymize must be boolean")
    else:
        errors.append("output must be an object")

    return errors


def _fault(
    *,
    code: str,
    stage: str,
    transition_blocked: str,
    trace: list[str],
    manifest_sha256: str,
    cell_id: str | None,
    adapter: InvocationAdapter,
    expected: Mapping[str, Any] | None = None,
    observed: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    terminal_trace = list(trace)
    if not terminal_trace or terminal_trace[-1] != STATE_HALTED:
        terminal_trace.append(STATE_HALTED)
    return {
        "schema": FAULT_SCHEMA,
        "fault_id": f"{cell_id or 'UNKNOWN'}:{code}",
        "code": code,
        "stage": stage,
        "terminal": True,
        "cell_id": cell_id,
        "manifest_sha256": manifest_sha256,
        "expected": dict(expected or {}),
        "observed": dict(observed or {}),
        "transition_blocked": transition_blocked,
        "execution_started": adapter.invocation_count > 0,
        "model_invoked": adapter.invocation_count > 0,
        "invocation_count": adapter.invocation_count,
        "state_trace": terminal_trace,
    }


def _read_relative(root: Path, relative: str) -> bytes:
    base = root.resolve(strict=True)
    candidate = (base / relative).resolve(strict=True)
    if candidate == base or base not in candidate.parents:
        raise ValueError(f"path escapes frozen root: {relative}")
    return candidate.read_bytes()


def _exception_mentions_specimen(exc: Exception) -> bool:
    return "specimen" in str(exc).lower()


def _safe_cell_id(value: Any) -> str | None:
    if isinstance(value, Mapping):
        cell_id = value.get("cell_id")
        if isinstance(cell_id, str):
            return cell_id
    return None


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str, errors: list[str]) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{label} missing keys: {missing}")
    if extra:
        errors.append(f"{label} unexpected keys: {extra}")


def _nonempty(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty string")


def _sha64(value: Any, label: str, errors: list[str]) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(ch not in _HEX64 for ch in value)
    ):
        errors.append(f"{label} must be lowercase SHA-256")
