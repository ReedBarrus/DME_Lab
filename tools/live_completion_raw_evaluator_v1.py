#!/usr/bin/env python3
"""Repaired raw P05/P06 evaluator for LIVE_COMPLETION_EVIDENCE_001."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping


class AdministrationInvalid(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AdministrationInvalid(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _git_json(repo: Path, ref: str, path: str) -> dict[str, Any]:
    return json.loads(_git(repo, "show", f"{ref}:{path}"))


def _blob(repo: Path, ref: str, path: str) -> str:
    return _git(repo, "rev-parse", f"{ref}:{path}")


def _is_ancestor(repo: Path, older: str, newer: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise AdministrationInvalid("ANCESTRY_CHECK_FAILED")
    return proc.returncode == 0


def _changed_paths(repo: Path, commit: str) -> list[str]:
    out = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return sorted(x for x in out.splitlines() if x)


def _work_commits(repo: Path, activation_commit: str, lane_head: str) -> list[str]:
    if not _is_ancestor(repo, activation_commit, lane_head):
        raise AdministrationInvalid("STALE_LIVE_BASIS")
    out = _git(repo, "rev-list", "--reverse", f"{activation_commit}..{lane_head}")
    return [x for x in out.splitlines() if x]


def canonical_unit_basis(claim: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "lane_id": claim.get("lane_id"),
        "claim_id": claim.get("claim_id"),
        "basis_head": claim.get("basis_head"),
        "target_lineage": claim.get("target_lineage"),
        "campaign_id": claim.get("campaign_id"),
        "pressure_id": claim.get("pressure_id"),
        "consequence_envelope_id": claim.get("consequence_envelope_id"),
        "artifact_scopes": sorted(claim.get("artifact_scopes", [])),
        "mutation_paths": sorted(claim.get("mutation_paths", [])),
    }


def derive_bounded_unit_id(claim: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical_bytes(canonical_unit_basis(claim))).hexdigest()
    return f"sha256:{digest}"


def expected_criterion_semantics(claim: Mapping[str, Any]) -> dict[str, Any]:
    mutation_paths = sorted(claim.get("mutation_paths", []))
    return {
        "bounded_unit_id": derive_bounded_unit_id(claim),
        "consequence_envelope_id": claim.get("consequence_envelope_id"),
        "required_final_artifacts": mutation_paths,
        "allowed_mutation_paths": mutation_paths,
        "source_derivation_rule": "EXACT_PREWORK_CLAIM_FIELDS",
        "work_interval_rule": "AFTER_ACTIVATION_TO_EVALUATED_HEAD",
    }


def derive_p05(repo_root: str | Path, frozen: Mapping[str, Any], binding: Mapping[str, Any]) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    lane_head = str(frozen["lane_a_head"])
    claim_path = str(frozen["lane_a_claim_path"])
    claim = _git_json(repo, lane_head, claim_path)
    observed_blob = _blob(repo, lane_head, claim_path)
    canonical_unit = derive_bounded_unit_id(claim)

    correspondence = {
        "lane_id": (binding.get("lane_id"), claim.get("lane_id")),
        "claim_id": (binding.get("claim_id"), claim.get("claim_id")),
        "claim_blob": (binding.get("claim_blob"), observed_blob),
        "occupant_id": (binding.get("occupant_id"), claim.get("occupant_id")),
        "invocation_id": (binding.get("invocation_id"), claim.get("invocation_id")),
        "branch": (binding.get("branch"), claim.get("branch")),
        "claim_basis_head": (binding.get("claim_basis_head"), claim.get("basis_head")),
        "target_lineage": (binding.get("target_lineage"), claim.get("target_lineage")),
        "campaign_id": (binding.get("campaign_id"), claim.get("campaign_id")),
        "pressure_id": (binding.get("pressure_id"), claim.get("pressure_id")),
        "consequence_envelope_id": (binding.get("consequence_envelope_id"), claim.get("consequence_envelope_id")),
        "artifact_scopes": (sorted(binding.get("artifact_scopes", [])), sorted(claim.get("artifact_scopes", []))),
        "mutation_paths": (sorted(binding.get("mutation_paths", [])), sorted(claim.get("mutation_paths", []))),
        "bounded_unit_id": (binding.get("bounded_unit_id"), canonical_unit),
    }
    mismatches = sorted(k for k, (a, b) in correspondence.items() if a != b)
    return {
        "predicate": "P05",
        "status": "MATCHES" if not mismatches else "DOES_NOT_MATCH",
        "mismatches": mismatches,
        "historical_claim_ref": f"git:{lane_head}:{claim_path}@{observed_blob}",
        "bounded_unit_id": canonical_unit,
        "canonical_unit_basis": canonical_unit_basis(claim),
    }


def validate_criterion_provenance(
    repo_root: str | Path,
    frozen: Mapping[str, Any],
    criterion: Mapping[str, Any],
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    basis_commit = str(criterion["criterion_basis_commit"])
    basis_path = "coordination/active_work_claim.json"
    if basis_commit != frozen.get("activation_commit"):
        raise AdministrationInvalid("CRITERION_PROVENANCE_INVALID")
    observed_blob = _blob(repo, basis_commit, basis_path)
    if observed_blob != criterion.get("criterion_basis_blob"):
        raise AdministrationInvalid("CRITERION_PROVENANCE_INVALID")
    claim = _git_json(repo, basis_commit, basis_path)
    expected = expected_criterion_semantics(claim)
    observed = {k: criterion.get(k) for k in expected}
    if observed != expected:
        raise AdministrationInvalid("CRITERION_SEMANTICS_NOT_SOURCE_DERIVED")
    return {
        "basis_commit": basis_commit,
        "basis_blob": observed_blob,
        "source_derivation_rule": "EXACT_PREWORK_CLAIM_FIELDS",
        "valid": True,
    }


def derive_p06(
    repo_root: str | Path,
    frozen: Mapping[str, Any],
    binding: Mapping[str, Any],
    criterion: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    if criterion is None:
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "MISSING_CRITERION"}

    if evidence.get("lane_head") != frozen.get("lane_a_head"):
        raise AdministrationInvalid("STALE_LIVE_BASIS")
    if evidence.get("activation_basis") != frozen.get("activation_basis"):
        raise AdministrationInvalid("STALE_LIVE_BASIS")
    if evidence.get("activation_commit") != frozen.get("activation_commit"):
        raise AdministrationInvalid("STALE_LIVE_BASIS")

    provenance = validate_criterion_provenance(repo_root, frozen, criterion)

    if criterion.get("bounded_unit_id") != binding.get("bounded_unit_id"):
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "WORK_UNIT_IDENTITY_MISMATCH"}
    if evidence.get("bounded_unit_id") != binding.get("bounded_unit_id"):
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "WORK_UNIT_IDENTITY_MISMATCH"}

    repo = Path(repo_root).resolve()
    actual_commits = _work_commits(repo, str(evidence["activation_commit"]), str(evidence["lane_head"]))
    declared_commits = list(evidence.get("work_commits", []))
    if actual_commits != declared_commits:
        return {
            "predicate": "P06",
            "status": "NOT_ESTABLISHED",
            "reason": "WORK_EVIDENCE_COMMIT_MISMATCH",
            "actual": actual_commits,
            "declared": declared_commits,
        }

    allowed = set(criterion.get("allowed_mutation_paths", []))
    unauthorized: list[str] = []
    path_mismatch: list[str] = []
    for commit in actual_commits:
        actual = _changed_paths(repo, commit)
        declared = sorted(evidence.get("commit_changed_paths", {}).get(commit, []))
        if actual != declared:
            path_mismatch.append(commit)
        unauthorized.extend(path for path in actual if path not in allowed)

    if path_mismatch:
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "WORK_EVIDENCE_PATH_MISMATCH", "commits": path_mismatch}
    if unauthorized:
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "UNAUTHORIZED_MUTATION_PRESENT", "paths": sorted(set(unauthorized))}

    final_by_path = {row["path"]: row["blob"] for row in evidence.get("final_artifacts", [])}
    required = list(criterion.get("required_final_artifacts", []))
    if sorted(final_by_path) != sorted(required):
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "REQUIRED_ARTIFACT_SET_MISMATCH"}

    mismatched = []
    for path in required:
        actual_blob = _blob(repo, str(evidence["lane_head"]), path)
        if final_by_path.get(path) != actual_blob:
            mismatched.append(path)
    if mismatched:
        return {"predicate": "P06", "status": "NOT_ESTABLISHED", "reason": "FINAL_ARTIFACT_IDENTITY_MISMATCH", "paths": mismatched}

    return {
        "predicate": "P06",
        "status": "SATISFIED",
        "reason": "RAW_COMPLETION_TERMS_SATISFIED",
        "criterion_provenance": provenance,
        "evaluated_head": evidence.get("lane_head"),
        "observed_work_commits": actual_commits,
    }
