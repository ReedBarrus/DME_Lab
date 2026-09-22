#!/usr/bin/env python3
"""Raw P05/P06 evaluator for LIVE_COMPLETION_EVIDENCE_001.

This module derives only:
- P05 work-unit correspondence
- P06 raw completion-term evaluation

It never produces lifecycle admissibility or executes a lifecycle transition.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping


class AdministrationInvalid(RuntimeError):
    pass


P05_MATCHES = "MATCHES"
P05_DOES_NOT_MATCH = "DOES_NOT_MATCH"
P06_SATISFIED = "SATISFIED"
P06_NOT_ESTABLISHED = "NOT_ESTABLISHED"


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AdministrationInvalid(
            f"git {' '.join(args)} failed: {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def _git_json(repo: Path, ref: str, path: str) -> dict[str, Any]:
    return json.loads(_git(repo, "show", f"{ref}:{path}"))


def _blob(repo: Path, ref: str, path: str) -> str:
    return _git(repo, "rev-parse", f"{ref}:{path}")


def _changed_paths(repo: Path, commit: str) -> list[str]:
    output = _git(
        repo,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        commit,
    )
    return sorted(line for line in output.splitlines() if line)


def _is_ancestor(repo: Path, older: str, newer: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise AdministrationInvalid(
            f"git merge-base --is-ancestor failed: {proc.stderr.decode().strip()}"
        )
    return proc.returncode == 0


def derive_p05(
    repo_root: str | Path,
    frozen: Mapping[str, Any],
    binding: Mapping[str, Any],
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    lane_head = str(frozen["lane_a_head"])
    claim_path = str(frozen["lane_a_claim_path"])
    claim = _git_json(repo, lane_head, claim_path)
    observed_blob = _blob(repo, lane_head, claim_path)

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
        "consequence_envelope_id": (
            binding.get("consequence_envelope_id"),
            claim.get("consequence_envelope_id"),
        ),
        "artifact_scopes": (
            sorted(binding.get("artifact_scopes", [])),
            sorted(claim.get("artifact_scopes", [])),
        ),
        "mutation_paths": (
            sorted(binding.get("mutation_paths", [])),
            sorted(claim.get("mutation_paths", [])),
        ),
    }
    mismatches = sorted(
        key for key, (bound, historical) in correspondence.items()
        if bound != historical
    )
    return {
        "predicate": "P05",
        "status": P05_MATCHES if not mismatches else P05_DOES_NOT_MATCH,
        "mismatches": mismatches,
        "historical_claim_ref": f"git:{lane_head}:{claim_path}@{observed_blob}",
        "work_unit_id": binding.get("work_unit_id"),
    }


def validate_criterion_provenance(
    repo_root: str | Path,
    frozen: Mapping[str, Any],
    criterion: Mapping[str, Any],
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    basis_commit = str(criterion["criterion_basis_commit"])
    first_work = str(criterion["first_work_commit"])
    basis_ref_path = "coordination/active_work_claim.json"
    observed_basis_blob = _blob(repo, basis_commit, basis_ref_path)

    if basis_commit == first_work or not _is_ancestor(repo, basis_commit, first_work):
        raise AdministrationInvalid("CRITERION_PROVENANCE_INVALID")
    if observed_basis_blob != criterion.get("criterion_basis_blob"):
        raise AdministrationInvalid("CRITERION_PROVENANCE_INVALID")
    if basis_commit != frozen.get("activation_commit"):
        raise AdministrationInvalid("CRITERION_PROVENANCE_INVALID")
    if first_work != frozen.get("initial_work_commit"):
        raise AdministrationInvalid("CRITERION_PROVENANCE_INVALID")

    return {
        "basis_commit": basis_commit,
        "basis_blob": observed_basis_blob,
        "first_work_commit": first_work,
        "rule": criterion.get("provenance_rule"),
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
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "MISSING_CRITERION",
        }

    if evidence.get("lane_head") != frozen.get("lane_a_head"):
        raise AdministrationInvalid("STALE_LIVE_BASIS")
    if evidence.get("activation_basis") != frozen.get("activation_basis"):
        raise AdministrationInvalid("STALE_LIVE_BASIS")
    if evidence.get("activation_commit") != frozen.get("activation_commit"):
        raise AdministrationInvalid("STALE_LIVE_BASIS")
    if criterion.get("work_unit_id") != binding.get("work_unit_id"):
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "WORK_UNIT_IDENTITY_MISMATCH",
        }
    if evidence.get("work_unit_id") != binding.get("work_unit_id"):
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "WORK_UNIT_IDENTITY_MISMATCH",
        }

    provenance = validate_criterion_provenance(
        repo_root, frozen, criterion
    )

    repo = Path(repo_root).resolve()
    required_commits = list(criterion.get("required_work_commits", []))
    observed_commits = list(evidence.get("work_commits", []))
    if required_commits != observed_commits:
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "REQUIRED_WORK_COMMIT_MISMATCH",
        }
    if criterion.get("final_work_head") != evidence.get("lane_head"):
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "FINAL_HEAD_MISMATCH",
        }

    allowed = set(criterion.get("allowed_mutation_paths", []))
    unauthorized: list[str] = []
    declared_change_mismatches: list[str] = []
    for commit in required_commits:
        actual = _changed_paths(repo, commit)
        declared = sorted(
            evidence.get("commit_changed_paths", {}).get(commit, [])
        )
        if actual != declared:
            declared_change_mismatches.append(commit)
        unauthorized.extend(path for path in actual if path not in allowed)

    if declared_change_mismatches:
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "WORK_EVIDENCE_PATH_MISMATCH",
            "commits": declared_change_mismatches,
        }
    if unauthorized:
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "UNAUTHORIZED_MUTATION_PRESENT",
            "paths": sorted(set(unauthorized)),
        }

    final_by_path = {
        row["path"]: row["blob"]
        for row in evidence.get("final_artifacts", [])
    }
    missing: list[str] = []
    blob_mismatches: list[str] = []
    for path in criterion.get("required_final_artifacts", []):
        if path not in final_by_path:
            missing.append(path)
            continue
        actual_blob = _blob(repo, str(evidence["lane_head"]), path)
        if final_by_path[path] != actual_blob:
            blob_mismatches.append(path)

    if missing:
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "REQUIRED_ARTIFACT_MISSING",
            "paths": missing,
        }
    if blob_mismatches:
        return {
            "predicate": "P06",
            "status": P06_NOT_ESTABLISHED,
            "reason": "FINAL_ARTIFACT_IDENTITY_MISMATCH",
            "paths": blob_mismatches,
        }

    return {
        "predicate": "P06",
        "status": P06_SATISFIED,
        "reason": "RAW_COMPLETION_TERMS_SATISFIED",
        "criterion_provenance": provenance,
        "evaluated_head": evidence.get("lane_head"),
        "required_work_commits": copy.deepcopy(required_commits),
    }
