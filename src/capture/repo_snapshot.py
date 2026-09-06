"""Deterministic structural snapshots of a repository working tree."""

from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path
from time import perf_counter
from datetime import datetime, timezone
from typing import Any


SNAPSHOT_OBSERVER_VERSION = "repo_snapshot_v0"
DEFAULT_EXCLUDED_DIRS = (".git", "__pycache__", "traces")
DEFAULT_EXCLUDED_GLOBS = ("*.pyc",)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def make_repo_snapshot(
    root: Path | str,
    *,
    excluded_dirs: tuple[str, ...] = DEFAULT_EXCLUDED_DIRS,
    excluded_globs: tuple[str, ...] = DEFAULT_EXCLUDED_GLOBS,
) -> dict[str, Any]:
    root_path = Path(root)
    started_at = utc_now()
    started = perf_counter()
    entries: list[dict[str, Any]] = []
    capture_errors: list[dict[str, str]] = []

    for path in sorted(root_path.rglob("*"), key=lambda item: _relative_path(root_path, item)):
        relative = _relative_path(root_path, path)
        if _is_excluded(relative, excluded_dirs, excluded_globs):
            continue
        if not path.is_file():
            continue
        before = _stat(path, relative, capture_errors)
        if before is None:
            continue
        digest = _hash_file(path, relative, capture_errors)
        after = _stat(path, relative, capture_errors)
        if digest is None or after is None:
            continue
        if before.st_mtime_ns != after.st_mtime_ns or before.st_size != after.st_size:
            capture_errors.append({"path": relative, "stage": "hash", "error": "changed_during_capture"})
        entries.append(
            {
                "path": relative,
                "kind": "file",
                "size_bytes": after.st_size,
                "mtime_ns": after.st_mtime_ns,
                "sha256": digest,
            }
        )

    scope = {
        "root": ".",
        "included": ["working_tree_files"],
        "excluded_dirs": list(excluded_dirs),
        "excluded_globs": list(excluded_globs),
    }
    structural_content = {
        "observer": "repo_snapshot",
        "observer_version": SNAPSHOT_OBSERVER_VERSION,
        "root_identity": _root_identity(root_path),
        "scope": scope,
        "entries": entries,
        "capture_errors": capture_errors,
    }
    structural_hash = hashlib.sha256(canonical_json(structural_content).encode("utf-8")).hexdigest()
    finished_at = utc_now()
    return {
        "snapshot_id": f"repo-snapshot-v0:{structural_hash}",
        "observer": "repo_snapshot",
        "observer_version": SNAPSHOT_OBSERVER_VERSION,
        "observation_started_at": started_at,
        "observation_finished_at": finished_at,
        "root_identity": _root_identity(root_path),
        "scope": scope,
        "entries": entries,
        "capture_errors": capture_errors,
        "duration_seconds": perf_counter() - started,
    }


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_entries = {entry["path"]: entry for entry in before.get("entries", [])}
    after_entries = {entry["path"]: entry for entry in after.get("entries", [])}
    before_paths = set(before_entries)
    after_paths = set(after_entries)

    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    common = sorted(before_paths & after_paths)
    changed = [
        path
        for path in common
        if before_entries[path].get("sha256") != after_entries[path].get("sha256")
    ]
    unchanged = [path for path in common if path not in changed]
    return {
        "before_snapshot_id": before.get("snapshot_id"),
        "after_snapshot_id": after.get("snapshot_id"),
        "added_paths": [{"path": path, "new": after_entries[path]} for path in added],
        "removed_paths": [{"path": path, "old": before_entries[path]} for path in removed],
        "changed_paths": [
            {"path": path, "old": before_entries[path], "new": after_entries[path]}
            for path in changed
        ],
        "unchanged_paths": unchanged,
    }


def _relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_excluded(relative: str, excluded_dirs: tuple[str, ...], excluded_globs: tuple[str, ...]) -> bool:
    parts = relative.split("/")
    if any(part in excluded_dirs for part in parts):
        return True
    return any(fnmatch.fnmatch(parts[-1], pattern) for pattern in excluded_globs)


def _root_identity(root: Path) -> dict[str, str]:
    return {"kind": "repository_working_tree", "name": root.name}


def _stat(path: Path, relative: str, errors: list[dict[str, str]]):
    try:
        return path.stat()
    except OSError as exc:
        errors.append({"path": relative, "stage": "stat", "error": type(exc).__name__})
        return None


def _hash_file(path: Path, relative: str, errors: list[dict[str, str]]) -> str | None:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        errors.append({"path": relative, "stage": "hash", "error": type(exc).__name__})
        return None
    return digest.hexdigest()

