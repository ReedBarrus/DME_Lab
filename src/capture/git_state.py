"""Separate Git state observation for the repository specimen."""

from __future__ import annotations

import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


GIT_OBSERVER_VERSION = "git_state_v0"


def observe_git_state(root: Path | str) -> dict[str, Any]:
    root_path = Path(root)
    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    errors: list[dict[str, str]] = []
    head_sha = _git(root_path, ["rev-parse", "HEAD"], errors)
    branch = _git(root_path, ["branch", "--show-current"], errors)
    status = _git(root_path, ["status", "--porcelain=v1"], errors)
    return {
        "observation_id": f"git-state-v0:{observed_at}",
        "observer": "git_state",
        "observer_version": GIT_OBSERVER_VERSION,
        "observed_at": observed_at,
        "root_identity": {"kind": "repository_working_tree", "name": root_path.name},
        "head_sha": head_sha,
        "branch": branch,
        "status_porcelain": status.splitlines() if status is not None else None,
        "capture_errors": errors,
    }


def _git(root: Path, args: list[str], errors: list[dict[str, str]]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        errors.append({"command": " ".join(args), "error": type(exc).__name__})
        return None
    if completed.returncode != 0:
        errors.append({"command": " ".join(args), "error": completed.stderr.strip()})
        return None
    return completed.stdout.strip()

