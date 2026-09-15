"""Deterministic changed-world basis reporting for one Git worktree.

The report contains mechanical repository observations only.  It may refresh
one declared remote-tracking ref, but it never integrates, repairs, or assigns
semantic authority to either side of the comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any


SCHEMA_NAME = "basis_report_v0"

RELATION_SYNCHRONIZED = "SYNCHRONIZED"
RELATION_LOCAL_BEHIND = "LOCAL_BEHIND"
RELATION_LOCAL_AHEAD = "LOCAL_AHEAD"
RELATION_DIVERGED = "DIVERGED"
RELATION_REMOTE_REF_ABSENT = "REMOTE_REF_ABSENT"
RELATION_CHECK_FAILED = "CHECK_FAILED"

WORKTREE_CLEAN = "CLEAN"
WORKTREE_DIRTY = "DIRTY"
WORKTREE_CHECK_FAILED = "CHECK_FAILED"

FETCH_NOT_REQUESTED = "NOT_REQUESTED"
FETCH_SUCCEEDED = "SUCCEEDED"
FETCH_FAILED = "FAILED"


class BasisReportError(RuntimeError):
    """Base class for basis-report contract failures."""


class BasisReportContractError(BasisReportError):
    """The caller supplied an invalid repository or ref coordinate."""


@dataclass(frozen=True)
class GitObservation:
    returncode: int | None
    stdout: str
    stderr: str
    failure: str | None = None


def basis_report(
    *, repository_root: Path, remote: str, branch: str, fetch: bool
) -> dict[str, Any]:
    """Observe one local/remote Git basis without integrating either history."""

    root = Path(repository_root).resolve(strict=True)
    if not root.is_dir():
        raise BasisReportContractError("repository_root must be a directory")
    remote = _ref_coordinate(remote, "remote", allow_slash=False)
    branch = _ref_coordinate(branch, "branch", allow_slash=True)
    if not isinstance(fetch, bool):
        raise BasisReportContractError("fetch must be true or false")

    failures: list[dict[str, Any]] = []
    if fetch:
        fetch_observation = _git(
            root,
            "fetch",
            "--no-tags",
            remote,
            f"+refs/heads/{branch}:refs/remotes/{remote}/{branch}",
        )
        fetch_result = _operation_result(fetch_observation)
        fetch_result["status"] = (
            FETCH_SUCCEEDED
            if _succeeded(fetch_observation)
            else FETCH_FAILED
        )
        if fetch_result["status"] == FETCH_FAILED:
            failures.append(_failure("fetch", fetch_observation))
    else:
        fetch_observation = None
        fetch_result = {
            "status": FETCH_NOT_REQUESTED,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "failure": None,
        }

    status_observation = _git(
        root, "status", "--porcelain=v1", "--untracked-files=all"
    )
    worktree_state = _worktree_state(status_observation)
    if worktree_state["status"] == WORKTREE_CHECK_FAILED:
        failures.append(_failure("worktree_status", status_observation))

    local_observation = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
    local_head = _single_line(local_observation)
    if local_head is None:
        failures.append(_failure("local_head", local_observation))

    branch_observation = _git(root, "branch", "--show-current")
    current_branch = _single_line(branch_observation)
    if not _succeeded(branch_observation):
        failures.append(_failure("current_branch", branch_observation))

    remote_ref = f"refs/remotes/{remote}/{branch}"
    remote_observation = _git(
        root, "rev-parse", "--verify", "--quiet", f"{remote_ref}^{{commit}}"
    )
    remote_absent = (
        remote_observation.returncode == 1 and remote_observation.failure is None
    )
    remote_head = None if remote_absent else _single_line(remote_observation)
    if not remote_absent and remote_head is None:
        failures.append(_failure("remote_head", remote_observation))

    relation = _relation(
        root=root,
        local_head=local_head,
        remote_head=remote_head,
        remote_absent=remote_absent,
        fetch_failed=fetch_result["status"] == FETCH_FAILED,
        failures=failures,
    )

    return {
        "schema": SCHEMA_NAME,
        "request": {
            "repository_root": str(root),
            "remote": remote,
            "branch": branch,
            "fetch": fetch,
        },
        "local_head": local_head,
        "remote_head": remote_head,
        "current_branch": current_branch,
        "worktree_state": worktree_state,
        "relation": relation,
        "fetch_attempted": fetch,
        "fetch_result": fetch_result,
        "observation_failures": failures,
        "mechanical_basis_only": True,
        "integration_performed": False,
    }


def _relation(
    *,
    root: Path,
    local_head: str | None,
    remote_head: str | None,
    remote_absent: bool,
    fetch_failed: bool,
    failures: list[dict[str, Any]],
) -> str:
    if fetch_failed:
        return RELATION_CHECK_FAILED
    if local_head is None:
        return RELATION_CHECK_FAILED
    if remote_absent:
        return RELATION_REMOTE_REF_ABSENT
    if remote_head is None:
        return RELATION_CHECK_FAILED
    if local_head == remote_head:
        return RELATION_SYNCHRONIZED

    local_before_remote = _git(
        root, "merge-base", "--is-ancestor", local_head, remote_head
    )
    remote_before_local = _git(
        root, "merge-base", "--is-ancestor", remote_head, local_head
    )
    if not _is_ancestry_result(local_before_remote):
        failures.append(_failure("local_is_ancestor", local_before_remote))
        return RELATION_CHECK_FAILED
    if not _is_ancestry_result(remote_before_local):
        failures.append(_failure("remote_is_ancestor", remote_before_local))
        return RELATION_CHECK_FAILED
    if local_before_remote.returncode == 0:
        return RELATION_LOCAL_BEHIND
    if remote_before_local.returncode == 0:
        return RELATION_LOCAL_AHEAD
    return RELATION_DIVERGED


def _worktree_state(observation: GitObservation) -> dict[str, Any]:
    if not _succeeded(observation):
        return {
            "status": WORKTREE_CHECK_FAILED,
            "tracked_changes": None,
            "untracked_changes": None,
            "entries": [],
        }
    entries = observation.stdout.splitlines()
    untracked = any(entry.startswith("??") for entry in entries)
    tracked = any(not entry.startswith("??") for entry in entries)
    return {
        "status": WORKTREE_DIRTY if entries else WORKTREE_CLEAN,
        "tracked_changes": tracked,
        "untracked_changes": untracked,
        "entries": entries,
    }


def _operation_result(observation: GitObservation) -> dict[str, Any]:
    return {
        "returncode": observation.returncode,
        "stdout": observation.stdout,
        "stderr": observation.stderr,
        "failure": observation.failure,
    }


def _failure(operation: str, observation: GitObservation) -> dict[str, Any]:
    return {
        "operation": operation,
        "returncode": observation.returncode,
        "stderr": observation.stderr,
        "failure": observation.failure,
    }


def _single_line(observation: GitObservation) -> str | None:
    if not _succeeded(observation):
        return None
    value = observation.stdout.strip()
    if value:
        return value
    return None


def _succeeded(observation: GitObservation) -> bool:
    return observation.failure is None and observation.returncode == 0


def _is_ancestry_result(observation: GitObservation) -> bool:
    return observation.failure is None and observation.returncode in {0, 1}


def _git(root: Path, *args: str) -> GitObservation:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return GitObservation(None, "", "", f"{type(exc).__name__}: {exc}")
    return GitObservation(
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )


def _ref_coordinate(value: str, name: str, *, allow_slash: bool) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise BasisReportContractError(f"{name} must be a non-empty exact string")
    forbidden = {"..", "@{", "\\", "~", "^", ":", "?", "*", "["}
    if value.startswith("-") or any(token in value for token in forbidden):
        raise BasisReportContractError(f"{name} is not a safe Git ref coordinate")
    if any(ord(character) < 32 or character.isspace() for character in value):
        raise BasisReportContractError(f"{name} is not a safe Git ref coordinate")
    if not allow_slash and "/" in value:
        raise BasisReportContractError(f"{name} must name one configured remote")
    if value.startswith("/") or value.endswith("/") or "//" in value:
        raise BasisReportContractError(f"{name} is not a safe Git ref coordinate")
    return value
