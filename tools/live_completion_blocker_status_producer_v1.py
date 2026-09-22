#!/usr/bin/env python3
"""Repaired P08 producer: blocker values are mechanically derived, never supplied."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

import live_completion_raw_evaluator_v1 as raw
import live_unit_completion_standing_producer_v1 as p07

PRODUCER = "LIVE_COMPLETION_BLOCKER_STATUS_PRODUCER"
VERSION = "v1"
RELATION_TYPE = "COMPLETION_BLOCKER_STATUS"
BASIS_REF = "basis://live-completion-evidence-v1/p08"

EXPECTED_CLASSES = [
    "WORK_UNIT_IDENTITY_MISMATCH",
    "CRITERION_BASIS_STALE",
    "REQUIRED_RAW_TERM_UNSATISFIED",
    "UNAUTHORIZED_MUTATION_PRESENT",
    "REQUIRED_UPSTREAM_STANDING_MISSING_OR_UNQUALIFIED",
]


def _blob(repo: Path, ref: str, path: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "rev-parse", f"{ref}:{path}"], capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def implementation_blob(repo_root: str | Path) -> str:
    repo = Path(repo_root).resolve()
    proc = subprocess.run(["git", "-C", str(repo), "hash-object", "tools/live_completion_blocker_status_producer_v1.py"], capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def _candidate_identity_valid(repo_root: str | Path, registry: Mapping[str, Any]) -> bool:
    row = registry.get("producer_candidates", {}).get(f"{PRODUCER}@{VERSION}")
    return bool(
        row
        and row.get("qualification_status") == "CANDIDATE_UNDER_QUALIFICATION"
        and RELATION_TYPE in row.get("relation_types", [])
        and row.get("implementation_blob") == implementation_blob(repo_root)
    )


def _qualified_identity_valid(repo_root: str | Path, registry: Mapping[str, Any]) -> bool:
    repo = Path(repo_root).resolve()
    row = registry.get("qualified_producers", {}).get(f"{PRODUCER}@{VERSION}")
    if not row or row.get("status") != "QUALIFIED":
        return False
    if RELATION_TYPE not in row.get("relation_types", []):
        return False
    if row.get("implementation_blob") != implementation_blob(repo):
        return False
    for path_key, blob_key in (
        ("qualification_evidence_path", "qualification_evidence_blob"),
        ("qualification_receipt_path", "qualification_receipt_blob"),
    ):
        path = row.get(path_key)
        expected = row.get(blob_key)
        if not path or not expected:
            return False
        try:
            actual = _blob(repo, "HEAD", str(path))
        except subprocess.CalledProcessError:
            return False
        if actual != expected:
            return False
    try:
        evidence = json.loads((repo / str(row["qualification_evidence_path"])).read_text(encoding="utf-8"))
    except Exception:
        return False
    return bool(
        evidence.get("candidate_producer_qualification", {}).get("P08", {}).get("pass") is True
        and evidence.get("implementation_blobs", {}).get("p08_producer") == implementation_blob(repo)
    )


def _source_refs_exist(repo_root: str | Path, scope: Mapping[str, Any]) -> bool:
    repo = Path(repo_root).resolve()
    for ref in scope.get("required_source_refs", []):
        if not str(ref).startswith("repo://"):
            return False
        if not (repo / str(ref).removeprefix("repo://")).is_file():
            return False
    return True


def _derive(
    repo_root: str | Path,
    producer_registry: Mapping[str, Any],
    frozen: Mapping[str, Any],
    binding: Mapping[str, Any],
    criterion: Mapping[str, Any],
    evidence: Mapping[str, Any],
    scope: Mapping[str, Any],
    *,
    candidate_mode: bool,
) -> dict[str, Any]:
    classes = list(scope.get("blocker_classes", []))
    if classes != EXPECTED_CLASSES:
        return {"status": "NOT_ESTABLISHED", "reason": "BLOCKER_SCOPE_NOT_CLOSED", "relation": None}
    if scope.get("scope_closure_rule") != "ALL_DECLARED_CLASSES_MECHANICALLY_DERIVED":
        return {"status": "NOT_ESTABLISHED", "reason": "BLOCKER_SCOPE_NOT_CLOSED", "relation": None}
    if scope.get("evaluated_basis_head") != frozen.get("lane_a_head") or not _source_refs_exist(repo_root, scope):
        return {"status": "NOT_ESTABLISHED", "reason": "BLOCKER_SCOPE_SOURCE_UNRECOVERABLE", "relation": None}

    p05 = raw.derive_p05(repo_root, frozen, binding)
    p06 = None
    p06_admin_reason = None
    try:
        p06 = raw.derive_p06(repo_root, frozen, binding, criterion, evidence)
    except raw.AdministrationInvalid as exc:
        p06_admin_reason = str(exc)

    if candidate_mode:
        p07_result = p07.candidate_produce(repo_root, producer_registry, binding, p05, p06 or {"status": "NOT_ESTABLISHED"})
    else:
        p07_result = p07.produce(repo_root, producer_registry, binding, p05, p06 or {"status": "NOT_ESTABLISHED"})

    evaluations = {
        "WORK_UNIT_IDENTITY_MISMATCH": p05.get("status") != "MATCHES",
        "CRITERION_BASIS_STALE": p06_admin_reason in {"STALE_LIVE_BASIS", "CRITERION_PROVENANCE_INVALID", "CRITERION_SEMANTICS_NOT_SOURCE_DERIVED"},
        "REQUIRED_RAW_TERM_UNSATISFIED": p06 is None or p06.get("status") != "SATISFIED",
        "UNAUTHORIZED_MUTATION_PRESENT": p06 is not None and p06.get("reason") == "UNAUTHORIZED_MUTATION_PRESENT",
        "REQUIRED_UPSTREAM_STANDING_MISSING_OR_UNQUALIFIED": p07_result.get("status") != "ESTABLISHED",
    }
    standing = "FORBIDS_COMPLETION" if any(evaluations.values()) else "NONE_ESTABLISHED"
    return {
        "status": "ESTABLISHED",
        "reason": "CLOSED_BLOCKER_SCOPE_MECHANICALLY_DERIVED",
        "relation": {
            "schema": "LIVE_QUALIFIED_UPSTREAM_RELATION_v0",
            "relation_type": RELATION_TYPE,
            "standing": standing,
            "basis_ref": BASIS_REF,
            "producer": PRODUCER,
            "version": VERSION,
        },
        "derived_evaluations": evaluations,
    }


def candidate_produce(repo_root: str | Path, candidate_registry: Mapping[str, Any], frozen: Mapping[str, Any], binding: Mapping[str, Any], criterion: Mapping[str, Any], evidence: Mapping[str, Any], scope: Mapping[str, Any]) -> dict[str, Any]:
    if not _candidate_identity_valid(repo_root, candidate_registry):
        return {"status": "NOT_ESTABLISHED", "reason": "CANDIDATE_IDENTITY_INVALID", "relation": None}
    return _derive(repo_root, candidate_registry, frozen, binding, criterion, evidence, scope, candidate_mode=True)


def produce(repo_root: str | Path, qualification_registry: Mapping[str, Any], frozen: Mapping[str, Any], binding: Mapping[str, Any], criterion: Mapping[str, Any], evidence: Mapping[str, Any], scope: Mapping[str, Any]) -> dict[str, Any]:
    if not _qualified_identity_valid(repo_root, qualification_registry):
        return {"status": "NOT_ESTABLISHED", "reason": "PRODUCER_VERSION_NOT_QUALIFIED", "relation": None}
    return _derive(repo_root, qualification_registry, frozen, binding, criterion, evidence, scope, candidate_mode=False)
