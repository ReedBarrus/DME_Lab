"""Bounded consequence-bearing adapter for WORKSHOP_AUTHORITY_GATE_001.

This adapter is intentionally specimen-local. It exposes one externally
observable consequence: exclusive creation of one fresh filesystem target.
It does not inspect or decide execution authority; the Workshop runner must
admit dispatch before any adapter interaction.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
from typing import Any, Mapping

ADAPTER_ID = "workshop_authority_gate_001_exclusive_file_v0"
TARGET_BYTES = b"WORKSHOP_AUTHORITY_GATE_001\n"
RETURN_BYTES = b"TARGET_CREATED\n"


@dataclass
class ExclusiveFileConsequenceAdapter:
    """Create exactly one fresh file when invoked through the Workshop runner."""

    target_path: Path
    invocation_count: int = 0
    surface_observation_count: int = 0

    def observe_surface(self) -> Mapping[str, Any]:
        self.surface_observation_count += 1
        return {
            "adapter_id": ADAPTER_ID,
            "consequence_kind": "exclusive_file_creation",
        }

    def invoke(self, payload: bytes) -> bytes:
        self.invocation_count += 1
        target = Path(self.target_path)
        if not target.parent.exists():
            raise RuntimeError("consequence target parent must already exist")
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as fh:
            fh.write(TARGET_BYTES)
            fh.flush()
            os.fsync(fh.fileno())
        return RETURN_BYTES


def observe_target(target_path: Path) -> dict[str, Any]:
    """Read the target independently from the adapter/runner report."""
    target = Path(target_path)
    if not target.exists():
        return {
            "exists": False,
            "sha256": None,
            "bytes": None,
        }
    payload = target.read_bytes()
    return {
        "exists": True,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }
