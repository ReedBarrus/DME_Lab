#!/usr/bin/env python3
"""P08 completion-blocker status producer v0."""
from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Mapping


PRODUCER = "LIVE_COMPLETION_BLOCKER_STATUS_PRODUCER"
VERSION = "v0"
RELATION_TYPE = "COMPLETION_BLOCKER_STATUS"


def implementation_blob(repo_root: str | Path) -> str:
    repo = Path(repo_root).resolve()
    proc = subprocess.run(
        ["git", "-C", str(repo), "hash-object", "tools/live_completion_blocker_status_producer_v0.py"],
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
    scope: Mapping[str, Any] | None,
    evaluations: Mapping[str, bool] | None,
) -> dict[str, Any]:
    if not candidate_identity_qualified(repo_root, registry):
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "PRODUCER_VERSION_NOT_QUALIFIED",
            "relation": None,
        }
    if scope is None or evaluations is None:
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "BLOCKER_SCOPE_NOT_CLOSED",
            "relation": None,
        }

    classes = list(scope.get("blocker_classes", []))
    if (
        scope.get("scope_closure_rule")
        != "ALL_DECLARED_CLASSES_EXPLICITLY_EVALUATED"
        or set(evaluations) != set(classes)
        or any(not isinstance(evaluations[key], bool) for key in classes)
    ):
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "BLOCKER_SCOPE_NOT_CLOSED",
            "relation": None,
        }

    for ref in scope.get("required_source_refs", []):
        if not ref.startswith("repo://"):
            return {
                "status": "NOT_ESTABLISHED",
                "reason": "BLOCKER_SCOPE_SOURCE_UNRECOVERABLE",
                "relation": None,
            }
        path = Path(repo_root) / ref.removeprefix("repo://")
        if not path.is_file():
            return {
                "status": "NOT_ESTABLISHED",
                "reason": "BLOCKER_SCOPE_SOURCE_UNRECOVERABLE",
                "relation": None,
            }

    standing = (
        "FORBIDS_COMPLETION"
        if any(evaluations[key] for key in classes)
        else "NONE_ESTABLISHED"
    )
    return {
        "status": "ESTABLISHED",
        "reason": "CLOSED_BLOCKER_SCOPE_EVALUATED",
        "relation": {
            "schema": "LIVE_QUALIFIED_UPSTREAM_RELATION_v0",
            "relation_type": RELATION_TYPE,
            "standing": standing,
            "basis_ref": "repo://fixtures/live_completion_evidence_v0/RAW_BLOCKER_SCOPE.json",
            "producer": PRODUCER,
            "version": VERSION,
        },
        "evaluated_classes": classes,
    }
