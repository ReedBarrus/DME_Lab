"""Specimen-local terminal execution-envelope latch.

Enforces only:

    TERMINAL_STOP(E) -> STOPPED(E)
    STOPPED(E) !-> ACTIVE(E)

This module does not decide what deserves a terminal stop, issue authority,
repair defects, authorize retries, or mutate scientific standing.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "execution_stop_latch_state_v0"
ACTIVE = "ACTIVE"
STOPPED = "STOPPED"
_ALLOWED_STATES = {ACTIVE, STOPPED}


class ExecutionStopLatchError(RuntimeError):
    """Base error for the bounded stop-latch surface."""


class ExecutionEnvelopeStopped(ExecutionStopLatchError):
    code = "EXECUTION_ENVELOPE_STOPPED"

    def __init__(self, execution_envelope_id: str, operation: str) -> None:
        self.execution_envelope_id = execution_envelope_id
        self.operation = operation
        super().__init__(
            f"{self.code}: envelope {execution_envelope_id!r} blocks operation {operation!r}"
        )


class ExecutionEnvelopeStateError(ExecutionStopLatchError):
    """Raised when retained stop-latch state is missing, corrupt, or mismatched."""


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


class ExecutionStopLatch:
    """Identity-bound terminal latch within one bounded execution-state store."""

    def __init__(self, store_root: Path, execution_envelope_id: str) -> None:
        if not isinstance(execution_envelope_id, str) or not execution_envelope_id.strip():
            raise ValueError("execution_envelope_id must be a non-empty string")
        self.store_root = Path(store_root)
        self.execution_envelope_id = execution_envelope_id
        identity_key = hashlib.sha256(execution_envelope_id.encode("utf-8")).hexdigest()
        self.state_path = (
            self.store_root / "execution_envelopes" / f"{identity_key}.json"
        )

    def materialize_active(self) -> dict[str, Any]:
        """Materialize an already-authorized ACTIVE envelope without overwriting state."""
        if self.state_path.exists():
            return self._read_state()

        state = {
            "schema_version": SCHEMA_VERSION,
            "execution_envelope_id": self.execution_envelope_id,
            "state": ACTIVE,
        }
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = _canonical_bytes(state)
        try:
            fd = os.open(
                self.state_path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            return self._read_state()

        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        return state

    def consume_terminal_stop(self) -> dict[str, Any]:
        """Consume TERMINAL_STOP(E) without interpreting its cause."""
        state = self._read_state()
        if state["state"] == STOPPED:
            return state

        stopped = {
            "schema_version": SCHEMA_VERSION,
            "execution_envelope_id": self.execution_envelope_id,
            "state": STOPPED,
        }
        self._replace_state(stopped)
        return stopped

    def state(self) -> str:
        """Inspect current authority state; permitted even while STOPPED."""
        return self._read_state()["state"]

    def receipt(self) -> dict[str, Any]:
        """Emit a deterministic inspection receipt; permitted while STOPPED."""
        state = self._read_state()
        return {
            "schema_version": "execution_stop_latch_receipt_v0",
            "execution_envelope_id": self.execution_envelope_id,
            "state": state["state"],
        }

    def require_active(self, operation: str) -> None:
        """Reject every guarded consequential operation after STOP."""
        if not isinstance(operation, str) or not operation.strip():
            raise ValueError("operation must be a non-empty string")
        if self._read_state()["state"] != ACTIVE:
            raise ExecutionEnvelopeStopped(self.execution_envelope_id, operation)

    def _read_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            raise ExecutionEnvelopeStateError(
                f"execution envelope {self.execution_envelope_id!r} is not materialized"
            )
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExecutionEnvelopeStateError(
                "could not read execution-envelope state"
            ) from exc

        if state.get("schema_version") != SCHEMA_VERSION:
            raise ExecutionEnvelopeStateError(
                "unexpected execution-envelope state schema"
            )
        if state.get("execution_envelope_id") != self.execution_envelope_id:
            raise ExecutionEnvelopeStateError("execution-envelope identity mismatch")
        if state.get("state") not in _ALLOWED_STATES:
            raise ExecutionEnvelopeStateError("unexpected execution-envelope state")
        if set(state) != {"schema_version", "execution_envelope_id", "state"}:
            raise ExecutionEnvelopeStateError(
                "unexpected execution-envelope state fields"
            )
        return state

    def _replace_state(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_path.with_name(self.state_path.name + ".tmp")
        with tmp.open("wb") as fh:
            fh.write(_canonical_bytes(state))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self.state_path)
