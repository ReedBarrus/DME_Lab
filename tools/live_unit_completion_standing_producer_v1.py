#!/usr/bin/env python3
"""Repaired P07 producer: candidate testing is separate from runtime qualification."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

PRODUCER = "LIVE_UNIT_COMPLETION_STANDING_PRODUCER"
VERSION = "v1"
RELATION_TYPE = "UNIT_COMPLETION_STANDING"
BASIS_REF = "basis://live-completion-evidence-v1/p07"


def _blob(repo: Path, ref: str, path: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "rev-parse", f"{ref}:{path}"], capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def implementation_blob(repo_root: str | Path) -> str:
    repo = Path(repo_root).resolve()
    proc = subprocess.run(["git", "-C", str(repo), "hash-object", "tools/live_unit_completion_standing_producer_v1.py"], capture_output=True, text=True, check=True)
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
        evidence.get("candidate_producer_qualification", {}).get("P07", {}).get("pass") is True
        and evidence.get("implementation_blobs", {}).get("p07_producer") == implementation_blob(repo)
    )


def _emit(binding: Mapping[str, Any], p05: Mapping[str, Any], p06: Mapping[str, Any]) -> dict[str, Any]:
    if p05.get("status") != "MATCHES":
        return {"status": "NOT_ESTABLISHED", "reason": "P05_NOT_MATCHED", "relation": None}
    if p06.get("status") != "SATISFIED":
        return {"status": "NOT_ESTABLISHED", "reason": "P06_NOT_SATISFIED", "relation": None}
    return {
        "status": "ESTABLISHED",
        "reason": "LIVE_UNIT_COMPLETION_STANDING_PRODUCED",
        "relation": {
            "schema": "LIVE_QUALIFIED_UPSTREAM_RELATION_v0",
            "relation_type": RELATION_TYPE,
            "standing": "QUALIFIED",
            "basis_ref": BASIS_REF,
            "producer": PRODUCER,
            "version": VERSION,
        },
        "bounded_unit_id": binding.get("bounded_unit_id"),
    }


def candidate_produce(repo_root: str | Path, candidate_registry: Mapping[str, Any], binding: Mapping[str, Any], p05: Mapping[str, Any], p06: Mapping[str, Any]) -> dict[str, Any]:
    if not _candidate_identity_valid(repo_root, candidate_registry):
        return {"status": "NOT_ESTABLISHED", "reason": "CANDIDATE_IDENTITY_INVALID", "relation": None}
    return _emit(binding, p05, p06)


def produce(repo_root: str | Path, qualification_registry: Mapping[str, Any], binding: Mapping[str, Any], p05: Mapping[str, Any], p06: Mapping[str, Any]) -> dict[str, Any]:
    if not _qualified_identity_valid(repo_root, qualification_registry):
        return {"status": "NOT_ESTABLISHED", "reason": "PRODUCER_VERSION_NOT_QUALIFIED", "relation": None}
    return _emit(binding, p05, p06)
