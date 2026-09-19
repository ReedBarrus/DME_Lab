"""Bounded initial ACTIVE materialization gated by exact AO↔E correspondence."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from lab.ops.candidates.execution_stop_latch_001.stop_latch import (
    ACTIVE,
    SCHEMA_VERSION,
    ExecutionStopLatch,
)

from .correspondence import corresponds


class AuthorizationMaterializationError(RuntimeError):
    """Raised when a realization does not begin from a mechanically clean state."""


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def materialize_active_if_corresponding(
    store_root: Path,
    envelope: dict[str, Any],
    authorization: dict[str, Any] | None,
) -> Path | None:
    """Materialize ACTIVE(E) only from derived exact correspondence on a clean root."""
    envelope_id = envelope.get("execution_envelope_id")
    if not isinstance(envelope_id, str) or not envelope_id:
        # Full shape validation still occurs inside corresponds; this prevents constructing
        # a latch from malformed identity before that validation can run.
        corresponds(authorization, envelope)
        raise AssertionError("unreachable")

    latch = ExecutionStopLatch(Path(store_root), envelope_id)
    if latch.state_path.exists():
        raise AuthorizationMaterializationError(
            "execution-envelope state must be absent before authorization realization"
        )

    if not corresponds(authorization, envelope):
        return None

    state = {
        "schema_version": SCHEMA_VERSION,
        "execution_envelope_id": envelope_id,
        "state": ACTIVE,
    }
    latch.state_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(latch.state_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise AuthorizationMaterializationError(
            "execution-envelope state appeared during materialization"
        ) from exc

    with os.fdopen(fd, "wb") as fh:
        fh.write(_canonical_bytes(state))
        fh.flush()
        os.fsync(fh.fileno())
    return latch.state_path
