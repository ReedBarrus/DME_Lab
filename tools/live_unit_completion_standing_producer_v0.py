#!/usr/bin/env python3
"""P07 live unit-completion standing producer v0."""
from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Mapping


PRODUCER = "LIVE_UNIT_COMPLETION_STANDING_PRODUCER"
VERSION = "v0"
RELATION_TYPE = "UNIT_COMPLETION_STANDING"


def implementation_blob(repo_root: str | Path) -> str:
    repo = Path(repo_root).resolve()
    proc = subprocess.run(
        ["git", "-C", str(repo), "hash-object", "tools/live_unit_completion_standing_producer_v0.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def candidate_identity_qualified(
    repo_root: str | Path,
    registry: Mapping[str, Any],
) -> bool:
    row = registry.get("producer_candidates", {}).get(f"{PRODUCER}@{VERSION}")
    return bool(
        row
        and RELATION_TYPE in row.get("relation_types", [])
        and row.get("implementation_blob") == implementation_blob(repo_root)
    )


def produce(
    repo_root: str | Path,
    registry: Mapping[str, Any],
    binding: Mapping[str, Any],
    p05: Mapping[str, Any],
    p06: Mapping[str, Any],
) -> dict[str, Any]:
    if not candidate_identity_qualified(repo_root, registry):
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "PRODUCER_VERSION_NOT_QUALIFIED",
            "relation": None,
        }
    if p05.get("status") != "MATCHES":
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "P05_NOT_MATCHED",
            "relation": None,
        }
    if p06.get("status") != "SATISFIED":
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "P06_NOT_SATISFIED",
            "relation": None,
        }

    return {
        "status": "ESTABLISHED",
        "reason": "LIVE_UNIT_COMPLETION_STANDING_PRODUCED",
        "relation": {
            "schema": "LIVE_QUALIFIED_UPSTREAM_RELATION_v0",
            "relation_type": RELATION_TYPE,
            "standing": "QUALIFIED",
            "basis_ref": "repo://fixtures/live_completion_evidence_v0/RAW_WORK_EVIDENCE.json",
            "producer": PRODUCER,
            "version": VERSION,
        },
        "work_unit_id": binding.get("work_unit_id"),
    }
