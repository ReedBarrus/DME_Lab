"""Deterministic Investigator Continuation v0 packet and admission surface.

This module attaches and verifies mechanical coordinates only. Caller-supplied
prior projected standing remains prior projection and never becomes current
authority through packet construction or admission.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from typing import Any, Mapping, Sequence


SCHEMA_NAME = "investigator_continuation_v0"
PACKET_STATUS = "COMPLETE"
CHECK_MATCH = "MATCH"
CHECK_MISMATCH = "MISMATCH"
CHECKED_ABSENT = "CHECKED_ABSENT"
CHECK_FAILED = "CHECK_FAILED"
NOT_CHECKED = "NOT_CHECKED"

_PACKET_FIELDS = {
    "schema",
    "continuation_id",
    "predecessor_id",
    "integrity",
    "mechanical_basis",
    "prior_projected_standing",
}
_INTEGRITY_FIELDS = {"packet_status", "packet_digest", "generated_at"}
_BASIS_FIELDS = {
    "repository",
    "basis_commit",
    "branch",
    "clean_worktree_required",
    "source_manifest",
}
_PRIOR_FIELDS = {
    "prior_objective_projection",
    "prior_established",
    "unresolved",
    "must_revalidate",
    "inflight_attempts",
}
_HEX40 = re.compile(r"[0-9a-f]{40}")
_HEX64 = re.compile(r"[0-9a-f]{64}")
_SOURCE_ID = re.compile(r"source-[0-9]{4}")


class ContinuationError(RuntimeError):
    """Base class for bounded continuation failures."""


class ContinuationBuildError(ContinuationError):
    """The clean committed packet basis cannot be constructed."""


class ContinuationContractError(ContinuationError):
    """Packet structure or caller-supplied projected standing is invalid."""


@dataclass(frozen=True)
class GitObservation:
    returncode: int | None
    stdout: bytes
    stderr: bytes
    failure: str | None = None


def canonical_serialize(value: Any) -> str:
    """Serialize recursively sorted compact UTF-8 JSON for v0 digesting."""

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def packet_digest(packet: Mapping[str, Any]) -> str:
    """Compute the v0 lowercase SHA-256 with packet_digest omitted."""

    value = deepcopy(dict(packet))
    integrity = value.get("integrity")
    if not isinstance(integrity, dict):
        raise ContinuationContractError("integrity must be an object")
    integrity.pop("packet_digest", None)
    return hashlib.sha256(canonical_serialize(value).encode("utf-8")).hexdigest()


def finalize_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Return a complete copy finalized under the declared v0 digest rule."""

    value = deepcopy(dict(packet))
    integrity = value.get("integrity")
    if not isinstance(integrity, dict):
        raise ContinuationContractError("integrity must be an object")
    integrity["packet_status"] = PACKET_STATUS
    integrity.pop("packet_digest", None)
    integrity["packet_digest"] = packet_digest(value)
    return value


def build_packet(
    *,
    repo_root: Path,
    repository: str,
    continuation_id: str,
    predecessor_id: str | None,
    generated_at: str,
    source_paths: Sequence[str],
    prior_projected_standing: Mapping[str, Any],
) -> dict[str, Any]:
    """Build one packet from a clean current HEAD without semantic inference."""

    root = repo_root.resolve(strict=True)
    _require_nonempty(repository, "repository")
    _require_nonempty(continuation_id, "continuation_id")
    if predecessor_id is not None:
        _require_nonempty(predecessor_id, "predecessor_id")
    _require_nonempty(generated_at, "generated_at")

    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.failure or status.returncode != 0:
        raise ContinuationBuildError(
            f"clean-worktree observation failed: {_git_detail(status)}"
        )
    if status.stdout:
        raise ContinuationBuildError("v0 requires a clean worktree")

    head = _required_git_text(root, "rev-parse", "--verify", "HEAD^{commit}")
    branch = _required_git_text(root, "symbolic-ref", "--short", "HEAD")
    manifest = _build_source_manifest(root, head, source_paths)
    source_ids = {entry["source_id"] for entry in manifest}
    prior = deepcopy(dict(prior_projected_standing))
    _validate_prior_projected_standing(prior, source_ids)

    packet = {
        "schema": SCHEMA_NAME,
        "continuation_id": continuation_id,
        "predecessor_id": predecessor_id,
        "integrity": {
            "packet_status": PACKET_STATUS,
            "generated_at": generated_at,
        },
        "mechanical_basis": {
            "repository": repository,
            "basis_commit": head,
            "branch": branch,
            "clean_worktree_required": True,
            "source_manifest": manifest,
        },
        "prior_projected_standing": prior,
    }
    finalized = finalize_packet(packet)
    errors = packet_shape_errors(finalized)
    if errors:
        raise ContinuationContractError("; ".join(errors))
    status_after = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status_after.failure or status_after.returncode != 0:
        raise ContinuationBuildError(
            f"final clean-worktree observation failed: {_git_detail(status_after)}"
        )
    if status_after.stdout:
        raise ContinuationBuildError("worktree changed during packet construction")
    if _required_git_text(root, "rev-parse", "--verify", "HEAD^{commit}") != head:
        raise ContinuationBuildError("HEAD changed during packet construction")
    if _required_git_text(root, "symbolic-ref", "--short", "HEAD") != branch:
        raise ContinuationBuildError("branch changed during packet construction")
    return finalized


def verify_packet_integrity(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Return structured finalization/digest evidence without repairing a packet."""

    if not isinstance(packet, Mapping):
        return _check(CHECK_FAILED, detail="packet is not an object")
    integrity = packet.get("integrity")
    if not isinstance(integrity, Mapping):
        return _check(CHECKED_ABSENT, detail="integrity object is absent")
    if "packet_digest" not in integrity:
        return _check(CHECKED_ABSENT, detail="packet_digest is absent")
    observed = integrity.get("packet_digest")
    if not isinstance(observed, str):
        return _check(CHECK_MISMATCH, expected="lowercase SHA-256", observed=observed)
    try:
        expected = packet_digest(packet)
    except (ContinuationError, TypeError, ValueError) as exc:
        return _check(CHECK_FAILED, observed=observed, detail=str(exc))
    return _check(
        CHECK_MATCH if observed == expected else CHECK_MISMATCH,
        expected=expected,
        observed=observed,
    )


def admit_packet(
    *, repo_root: Path, expected_repository: str, packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Mechanically admit a packet against current clean repository state."""

    root = repo_root.resolve(strict=True)
    errors = packet_shape_errors(packet)
    checks: dict[str, Any] = {
        "schema": _check(
            CHECK_MATCH if not errors else CHECK_MISMATCH,
            expected=SCHEMA_NAME,
            observed=packet.get("schema") if isinstance(packet, Mapping) else None,
            detail=None if not errors else "; ".join(errors),
        ),
        "packet_status": _packet_status_check(packet),
        "packet_digest": verify_packet_integrity(packet),
        "repository_identity": _value_check(
            expected_repository,
            _nested(packet, "mechanical_basis", "repository"),
        ),
        "clean_worktree_required": _value_check(
            True,
            _nested(packet, "mechanical_basis", "clean_worktree_required"),
        ),
        "generated_at_age": _check(
            NOT_CHECKED,
            observed=_nested(packet, "integrity", "generated_at"),
            detail="generated_at is diagnostic provenance, not freshness",
        ),
    }

    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status.failure or status.returncode != 0:
        checks["worktree_clean"] = _check(
            CHECK_FAILED, detail=_git_detail(status)
        )
    else:
        observed_status = status.stdout.decode("utf-8", errors="replace")
        checks["worktree_clean"] = _check(
            CHECK_MATCH if not status.stdout else CHECK_MISMATCH,
            expected="",
            observed=observed_status,
        )

    head_observation = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
    current_head = _optional_git_text(head_observation)
    checks["basis_commit"] = (
        _check(CHECK_FAILED, detail=_git_detail(head_observation))
        if current_head is None
        else _value_check(_nested(packet, "mechanical_basis", "basis_commit"), current_head)
    )

    branch_observation = _git(root, "symbolic-ref", "--short", "HEAD")
    current_branch = _optional_git_text(branch_observation)
    checks["branch"] = (
        _check(CHECKED_ABSENT, detail=_git_detail(branch_observation))
        if branch_observation.returncode not in (None, 0)
        and not branch_observation.failure
        else _check(CHECK_FAILED, detail=_git_detail(branch_observation))
        if current_branch is None
        else _value_check(_nested(packet, "mechanical_basis", "branch"), current_branch)
    )

    manifest = _nested(packet, "mechanical_basis", "source_manifest")
    checks["semantic_source_refs"] = _semantic_ref_check(packet, manifest)
    checks["source_manifest"] = _admit_sources(root, current_head, manifest)

    required = [
        checks[name]["status"]
        for name in (
            "schema",
            "packet_status",
            "packet_digest",
            "repository_identity",
            "clean_worktree_required",
            "worktree_clean",
            "basis_commit",
            "branch",
            "semantic_source_refs",
        )
    ]
    source_statuses = [item["status"] for item in checks["source_manifest"]]
    return {
        "schema": SCHEMA_NAME,
        "admissible": all(status == CHECK_MATCH for status in required + source_statuses),
        "checks": checks,
        "current_admission_only": True,
        "prior_projected_standing_promoted": False,
        "repair_performed": False,
    }


def write_packet_atomic(
    packet: Mapping[str, Any], *, target: Path, source_worktree: Path
) -> None:
    """Atomically write a packet only outside the tested source worktree."""

    root = source_worktree.resolve(strict=True)
    destination = target.resolve(strict=False)
    if destination == root or root in destination.parents:
        raise ContinuationBuildError(
            "packet artifacts must remain outside the tested source worktree"
        )
    if not destination.parent.is_dir():
        raise ContinuationBuildError("packet target parent must already exist")
    errors = packet_shape_errors(packet)
    if errors:
        raise ContinuationContractError("cannot write invalid packet: " + "; ".join(errors))
    integrity = verify_packet_integrity(packet)
    if integrity["status"] != CHECK_MATCH:
        raise ContinuationContractError("cannot write packet with invalid integrity")
    payload = canonical_serialize(packet).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def packet_shape_errors(packet: Mapping[str, Any]) -> list[str]:
    """Validate the exact v0 structural surface without semantic adjudication."""

    if not isinstance(packet, Mapping):
        return ["packet must be an object"]
    errors: list[str] = []
    _exact_keys(packet, _PACKET_FIELDS, "packet", errors)
    if packet.get("schema") != SCHEMA_NAME:
        errors.append("schema is unsupported")
    if not _is_nonempty(packet.get("continuation_id")):
        errors.append("continuation_id must be a non-empty string")
    predecessor = packet.get("predecessor_id")
    if predecessor is not None and not _is_nonempty(predecessor):
        errors.append("predecessor_id must be null or a non-empty string")

    integrity = packet.get("integrity")
    if isinstance(integrity, Mapping):
        _exact_keys(integrity, _INTEGRITY_FIELDS, "integrity", errors)
        if integrity.get("packet_status") != PACKET_STATUS:
            errors.append("integrity.packet_status must be COMPLETE")
        if not _is_nonempty(integrity.get("generated_at")):
            errors.append("integrity.generated_at must be a non-empty string")
        digest = integrity.get("packet_digest")
        if not isinstance(digest, str) or not _HEX64.fullmatch(digest):
            errors.append("integrity.packet_digest must be lowercase SHA-256")
    else:
        errors.append("integrity must be an object")

    basis = packet.get("mechanical_basis")
    if isinstance(basis, Mapping):
        _exact_keys(basis, _BASIS_FIELDS, "mechanical_basis", errors)
        for field in ("repository", "branch"):
            if not _is_nonempty(basis.get(field)):
                errors.append(f"mechanical_basis.{field} must be a non-empty string")
        if not isinstance(basis.get("basis_commit"), str) or not _HEX40.fullmatch(
            basis["basis_commit"]
        ):
            errors.append("mechanical_basis.basis_commit must be lowercase Git SHA-1")
        if basis.get("clean_worktree_required") is not True:
            errors.append("mechanical_basis.clean_worktree_required must be true")
        _manifest_errors(basis.get("source_manifest"), errors)
    else:
        errors.append("mechanical_basis must be an object")

    prior = packet.get("prior_projected_standing")
    if isinstance(prior, Mapping):
        _prior_shape_errors(prior, errors)
    else:
        errors.append("prior_projected_standing must be an object")
    return errors


def _build_source_manifest(
    root: Path, head: str, source_paths: Sequence[str]
) -> list[dict[str, str]]:
    if not isinstance(source_paths, Sequence) or isinstance(source_paths, (str, bytes)):
        raise ContinuationContractError("source_paths must be a sequence")
    canonical_paths = [_canonical_path(path) for path in source_paths]
    if len(set(canonical_paths)) != len(canonical_paths):
        raise ContinuationContractError("source_paths must not contain duplicates")
    paths = sorted(canonical_paths)
    manifest: list[dict[str, str]] = []
    for index, path in enumerate(paths, start=1):
        entry = _observe_source(root, head, path)
        if entry["status"] == CHECKED_ABSENT:
            raise ContinuationBuildError(f"committed source is absent: {path}")
        if entry["status"] != CHECK_MATCH:
            raise ContinuationBuildError(
                f"committed source observation failed for {path}: {entry.get('detail')}"
            )
        manifest.append(
            {
                "source_id": f"source-{index:04d}",
                "path": path,
                "git_blob": entry["observed"],
            }
        )
    return manifest


def _validate_prior_projected_standing(
    prior: Mapping[str, Any], source_ids: set[str]
) -> None:
    errors: list[str] = []
    _prior_shape_errors(prior, errors)
    if errors:
        raise ContinuationContractError("; ".join(errors))
    unknown = sorted(_semantic_refs(prior) - source_ids)
    if unknown:
        raise ContinuationContractError(
            f"unknown semantic source_ref: {unknown[0]}"
        )


def _prior_shape_errors(prior: Mapping[str, Any], errors: list[str]) -> None:
    _exact_keys(prior, _PRIOR_FIELDS, "prior_projected_standing", errors)
    objective = prior.get("prior_objective_projection")
    _claim_errors(objective, "prior_objective_projection", errors, {"statement", "source_refs"})
    _claim_list_errors(
        prior.get("prior_established"),
        "prior_established",
        errors,
        {"statement", "standing_at_generation", "source_refs"},
    )
    _claim_list_errors(
        prior.get("unresolved"),
        "unresolved",
        errors,
        {"statement", "source_refs", "missing_basis", "next_discriminator"},
    )
    _claim_list_errors(
        prior.get("must_revalidate"),
        "must_revalidate",
        errors,
        {"coordinate", "reason", "evidence_refs"},
    )
    inflight = prior.get("inflight_attempts")
    if inflight != []:
        errors.append("inflight_attempts must be empty for the first clean pressure")


def _claim_list_errors(
    value: Any, name: str, errors: list[str], keys: set[str]
) -> None:
    if not isinstance(value, list):
        errors.append(f"{name} must be an array")
        return
    for index, item in enumerate(value):
        _claim_errors(item, f"{name}[{index}]", errors, keys)


def _claim_errors(
    value: Any, name: str, errors: list[str], keys: set[str]
) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return
    _exact_keys(value, keys, name, errors)
    for key, item in value.items():
        if key in {"source_refs", "evidence_refs", "missing_basis"}:
            if not isinstance(item, list) or any(not _is_nonempty(x) for x in item):
                errors.append(f"{name}.{key} must be an array of non-empty strings")
        elif not _is_nonempty(item):
            errors.append(f"{name}.{key} must be a non-empty string")


def _manifest_errors(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append("mechanical_basis.source_manifest must be an array")
        return
    ids: set[str] = set()
    paths: set[str] = set()
    for index, entry in enumerate(value):
        name = f"source_manifest[{index}]"
        if not isinstance(entry, Mapping):
            errors.append(f"{name} must be an object")
            continue
        _exact_keys(entry, {"source_id", "path", "git_blob"}, name, errors)
        for field in ("source_id", "path", "git_blob"):
            if not _is_nonempty(entry.get(field)):
                errors.append(f"{name}.{field} must be a non-empty string")
        source_id = entry.get("source_id")
        path = entry.get("path")
        if not isinstance(source_id, str) or not _SOURCE_ID.fullmatch(source_id):
            errors.append(f"{name}.source_id must match source-NNNN")
        if not isinstance(entry.get("git_blob"), str) or not _HEX40.fullmatch(
            entry["git_blob"]
        ):
            errors.append(f"{name}.git_blob must be lowercase Git SHA-1")
        if isinstance(path, str):
            try:
                _canonical_path(path)
            except ContinuationContractError as exc:
                errors.append(f"{name}.path is invalid: {exc}")
        if isinstance(source_id, str):
            if source_id in ids:
                errors.append(f"duplicate source_id: {source_id}")
            ids.add(source_id)
        if isinstance(path, str):
            if path in paths:
                errors.append(f"duplicate source path: {path}")
            paths.add(path)


def _semantic_refs(prior: Mapping[str, Any]) -> set[str]:
    refs: set[str] = set()
    objective = prior.get("prior_objective_projection", {})
    if isinstance(objective, Mapping):
        refs.update(_string_items(objective.get("source_refs")))
    for section, field in (
        ("prior_established", "source_refs"),
        ("unresolved", "source_refs"),
        ("must_revalidate", "evidence_refs"),
    ):
        values = prior.get(section, [])
        if isinstance(values, list):
            for item in values:
                if isinstance(item, Mapping) and isinstance(item.get(field), list):
                    refs.update(_string_items(item[field]))
    return refs


def _semantic_ref_check(packet: Mapping[str, Any], manifest: Any) -> dict[str, Any]:
    if not isinstance(packet, Mapping):
        return _check(NOT_CHECKED, detail="packet is structurally invalid")
    if not isinstance(manifest, list):
        return _check(NOT_CHECKED, detail="source manifest is structurally invalid")
    issued = {
        entry.get("source_id")
        for entry in manifest
        if isinstance(entry, Mapping) and _is_nonempty(entry.get("source_id"))
    }
    prior = packet.get("prior_projected_standing")
    if not isinstance(prior, Mapping):
        return _check(NOT_CHECKED, detail="prior projected standing is invalid")
    unknown = sorted(_semantic_refs(prior) - issued)
    return _check(
        CHECK_MATCH if not unknown else CHECK_MISMATCH,
        expected=sorted(issued),
        observed=sorted(_semantic_refs(prior)),
        detail=None if not unknown else f"unknown refs: {unknown}",
    )


def _admit_sources(root: Path, head: str | None, manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, list):
        return [_check(NOT_CHECKED, detail="source manifest is structurally invalid")]
    if head is None:
        return [
            {
                "source_id": entry.get("source_id") if isinstance(entry, Mapping) else None,
                "path": entry.get("path") if isinstance(entry, Mapping) else None,
                **_check(CHECK_FAILED, detail="current HEAD observation failed"),
            }
            for entry in manifest
        ]
    results: list[dict[str, Any]] = []
    for entry in manifest:
        if not isinstance(entry, Mapping):
            results.append(_check(NOT_CHECKED, detail="source entry is invalid"))
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            results.append(
                {"source_id": entry.get("source_id"), "path": path, **_check(NOT_CHECKED)}
            )
            continue
        try:
            _canonical_path(path)
        except ContinuationContractError as exc:
            results.append(
                {
                    "source_id": entry.get("source_id"),
                    "path": path,
                    **_check(NOT_CHECKED, detail=str(exc)),
                }
            )
            continue
        observed = _observe_source(root, head, path)
        observed.update(
            {
                "source_id": entry.get("source_id"),
                "path": path,
                "expected": entry.get("git_blob"),
            }
        )
        if observed["status"] == CHECK_MATCH:
            observed["status"] = (
                CHECK_MATCH
                if observed["observed"] == entry.get("git_blob")
                else CHECK_MISMATCH
            )
        results.append(observed)
    return results


def _observe_source(root: Path, commit: str, path: str) -> dict[str, Any]:
    observation = _git(root, "ls-tree", "-z", commit, "--", path)
    if observation.failure or observation.returncode != 0:
        return _check(CHECK_FAILED, detail=_git_detail(observation))
    if not observation.stdout:
        return _check(CHECKED_ABSENT, observed=None)
    records = [record for record in observation.stdout.split(b"\0") if record]
    if len(records) != 1:
        return _check(CHECK_FAILED, detail="source lookup returned multiple entries")
    try:
        metadata, encoded_path = records[0].split(b"\t", 1)
        _mode, object_type, object_id = metadata.decode("ascii").split(" ")
        observed_path = encoded_path.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        return _check(CHECK_FAILED, detail=f"cannot parse source identity: {exc}")
    if observed_path != path or object_type != "blob":
        return _check(
            CHECK_MISMATCH,
            observed={"path": observed_path, "type": object_type, "object": object_id},
            detail="source did not resolve as the exact committed blob",
        )
    return _check(CHECK_MATCH, observed=object_id)


def _packet_status_check(packet: Mapping[str, Any]) -> dict[str, Any]:
    integrity = packet.get("integrity") if isinstance(packet, Mapping) else None
    if not isinstance(integrity, Mapping) or "packet_status" not in integrity:
        return _check(CHECKED_ABSENT, expected=PACKET_STATUS)
    return _value_check(PACKET_STATUS, integrity.get("packet_status"))


def _value_check(expected: Any, observed: Any) -> dict[str, Any]:
    if observed is None:
        return _check(CHECKED_ABSENT, expected=expected, observed=None)
    return _check(
        CHECK_MATCH if observed == expected else CHECK_MISMATCH,
        expected=expected,
        observed=observed,
    )


def _check(
    status: str,
    *,
    expected: Any = None,
    observed: Any = None,
    detail: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "expected": expected,
        "observed": observed,
        "detail": detail,
    }


def _git(root: Path, *args: str) -> GitObservation:
    try:
        completed = subprocess.run(
            [
                "git",
                "--no-pager",
                "-c",
                "core.fsmonitor=false",
                "-c",
                "core.untrackedCache=false",
                *args,
            ],
            cwd=root,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        return GitObservation(None, b"", b"", f"{type(exc).__name__}: {exc}")
    return GitObservation(
        completed.returncode, completed.stdout, completed.stderr, None
    )


def _required_git_text(root: Path, *args: str) -> str:
    observation = _git(root, *args)
    value = _optional_git_text(observation)
    if value is None:
        raise ContinuationBuildError(_git_detail(observation))
    return value


def _optional_git_text(observation: GitObservation) -> str | None:
    if observation.failure or observation.returncode != 0:
        return None
    try:
        return observation.stdout.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None


def _git_detail(observation: GitObservation) -> str:
    if observation.failure:
        return observation.failure
    return observation.stderr.decode("utf-8", errors="replace").strip() or (
        f"git returned {observation.returncode}"
    )


def _canonical_path(value: Any) -> str:
    if not _is_nonempty(value) or "\\" in value:
        raise ContinuationContractError("source path must be canonical POSIX text")
    pure = PurePosixPath(value)
    if pure.is_absolute() or value != pure.as_posix() or any(
        part in {"", ".", "..", ".git"} for part in pure.parts
    ):
        raise ContinuationContractError("source path is not canonical or safe")
    return value


def _nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _exact_keys(
    value: Mapping[str, Any], expected: set[str], name: str, errors: list[str]
) -> None:
    if set(value) != expected:
        errors.append(f"{name} must contain exactly {sorted(expected)}")


def _require_nonempty(value: Any, name: str) -> str:
    if not _is_nonempty(value):
        raise ContinuationContractError(f"{name} must be a non-empty string")
    return value


def _is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
