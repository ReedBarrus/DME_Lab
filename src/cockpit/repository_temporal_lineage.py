from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Any, Sequence

from src.cockpit.repository_address_fabric import infer_repository_identity


DEFAULT_OUTPUT = Path("generated/repository_temporal_lineage.json")
OBJECT_TYPE = "REPOSITORY_TEMPORAL_LINEAGE_V0"
WOUND_PATH = "src/cockpit/observer/repository_fabric_app.mjs"
LABBOIB_SEAT_PATH = "continuity/seats/labboib.json"


class RepositoryTemporalLineageError(RuntimeError):
    pass


def _git(repo: Path, *args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RepositoryTemporalLineageError(
            f"git {' '.join(args)} failed: {detail or 'unknown git failure'}"
        )
    return completed.stdout


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _identity(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()
    return f"{prefix}:sha256:{digest}"


def _branch_coordinate(repo: Path, source_ref: str) -> str | None:
    if source_ref != "HEAD":
        return source_ref.removeprefix("refs/heads/") if source_ref.startswith("refs/heads/") else None
    value = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    return value.decode("utf-8").strip() or None


def _commit_rows(repo: Path, commit: str) -> list[dict[str, Any]]:
    format_string = "%H%x1f%T%x1f%P%x1f%an%x1f%ae%x1f%aI%x1f%cn%x1f%ce%x1f%cI%x1f%s"
    raw = _git(
        repo,
        "log",
        "--first-parent",
        "--reverse",
        f"--format={format_string}",
        commit,
    )
    rows: list[dict[str, Any]] = []
    for raw_row in raw.decode("utf-8", errors="replace").splitlines():
        values = raw_row.split("\x1f")
        if len(values) != 10:
            raise RepositoryTemporalLineageError("unexpected first-parent log record shape")
        sha, tree, parents, author_name, author_email, authored_at, committer_name, committer_email, committed_at, subject = values
        rows.append(
            {
                "commit_sha": sha,
                "tree_sha": tree,
                "parent_commit_shas": parents.split() if parents else [],
                "first_parent_commit_sha": parents.split()[0] if parents else None,
                "git_author": {
                    "name": author_name,
                    "email": author_email,
                    "timestamp": authored_at,
                    "standing": "GIT_METADATA_ONLY",
                },
                "git_committer": {
                    "name": committer_name,
                    "email": committer_email,
                    "timestamp": committed_at,
                    "standing": "GIT_METADATA_ONLY",
                },
                "subject": subject,
            }
        )
    return rows


def _tree_entries(repo: Path, commit: str) -> list[dict[str, str]]:
    raw = _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit)
    entries: list[dict[str, str]] = []
    for row in raw.split(b"\0"):
        if not row:
            continue
        metadata, raw_path = row.split(b"\t", 1)
        mode, git_type, object_sha = metadata.decode("ascii").split(" ")
        entries.append(
            {
                "path": raw_path.decode("utf-8"),
                "git_mode": mode,
                "git_object_type": git_type,
                "git_object_sha": object_sha,
            }
        )
    return sorted(entries, key=lambda item: item["path"])


def _raw_diff(repo: Path, before: str, after: str) -> list[dict[str, str | None]]:
    raw = _git(
        repo,
        "diff-tree",
        "--no-commit-id",
        "--raw",
        "-z",
        "-r",
        "-M50%",
        before,
        after,
    )
    parts = raw.split(b"\0")
    while parts and parts[-1] == b"":
        parts.pop()
    result: list[dict[str, str | None]] = []
    index = 0
    while index < len(parts):
        metadata = parts[index].decode("ascii")
        index += 1
        if not metadata.startswith(":"):
            raise RepositoryTemporalLineageError("unexpected raw diff record")
        old_mode, new_mode, old_sha, new_sha, status = metadata[1:].split(" ")
        old_path = parts[index].decode("utf-8")
        index += 1
        new_path = old_path
        if status.startswith(("R", "C")):
            if index >= len(parts):
                raise RepositoryTemporalLineageError("truncated rename/copy record")
            new_path = parts[index].decode("utf-8")
            index += 1
        if status == "A":
            old_path = None
        if status == "D":
            new_path = None
        result.append(
            {
                "status": status,
                "old_path": old_path,
                "new_path": new_path,
                "old_mode": old_mode,
                "new_mode": new_mode,
                "old_object_sha": None if set(old_sha) == {"0"} else old_sha,
                "new_object_sha": None if set(new_sha) == {"0"} else new_sha,
            }
        )
    return result


def _object_contents(repo: Path, identities: set[str]) -> dict[str, bytes]:
    ordered = sorted(identity for identity in identities if identity)
    if not ordered:
        return {}
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", "cat-file", "--batch"],
        cwd=repo,
        input=("\n".join(ordered) + "\n").encode("ascii"),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise RepositoryTemporalLineageError("git cat-file --batch failed")
    result: dict[str, bytes] = {}
    offset = 0
    for requested in ordered:
        header_end = completed.stdout.find(b"\n", offset)
        header = completed.stdout[offset:header_end].decode("ascii").split(" ")
        if len(header) != 3 or header[1] == "missing":
            raise RepositoryTemporalLineageError(f"Git object unavailable: {requested}")
        returned, _object_type, size_text = header
        start = header_end + 1
        end = start + int(size_text)
        result[returned] = completed.stdout[start:end]
        offset = end + 1
    return result


def _lineage_id(repository: str, origin_commit: str, path: str, discriminator: str) -> str:
    return _identity(
        "temporal-object",
        {
            "repository": repository,
            "origin_commit": origin_commit,
            "origin_path": path,
            "discriminator": discriminator,
        },
    )


def _classifications(row: dict[str, str | None]) -> tuple[list[str], str]:
    status = str(row["status"])
    if status == "A":
        return ["APPEARED", "RELATION_ADDED"], "NEW_PATH_AT_TO_FRAME"
    if status == "D":
        return ["DISAPPEARED", "RELATION_REMOVED"], "PATH_ABSENT_AT_TO_FRAME"
    if status.startswith("R"):
        score = int(status[1:] or "0")
        if score == 100:
            return ["PERSISTED", "PATH_CHANGED"], "EXACT_BLOB_RENAME_R100"
        return ["IDENTITY_UNRESOLVED"], f"GIT_RENAME_SIMILARITY_{score}_INSUFFICIENT_FOR_IDENTITY"
    categories = ["PERSISTED"]
    if row["old_object_sha"] != row["new_object_sha"]:
        categories.extend(["CONTENT_CHANGED", "RELATION_REMOVED", "RELATION_ADDED"])
    return categories, "SAME_PATH_ADJACENT_FIRST_PARENT_FRAMES"


def _actor_path(path: str) -> bool:
    return path == LABBOIB_SEAT_PATH or (
        path.startswith("continuity/cursors/") and path.endswith(".json")
    )


def _actor_source_versions(
    frames: list[dict[str, Any]],
    initial_entries: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    contents: dict[str, bytes],
) -> list[dict[str, Any]]:
    actor_paths = {entry["path"] for entry in initial_entries if _actor_path(entry["path"])}
    for transition in transitions:
        for event in transition["events"]:
            for key in ("old_path", "new_path"):
                path = event.get(key)
                if path and _actor_path(path):
                    actor_paths.add(path)
    state = {entry["path"]: dict(entry) for entry in initial_entries}
    active: dict[str, dict[str, Any]] = {}
    versions: list[dict[str, Any]] = []

    def observe(frame_index: int) -> None:
        for path in sorted(actor_paths):
            entry = state.get(path)
            blob = entry.get("git_object_sha") if entry else None
            current = active.get(path)
            if current and current["git_object_sha"] == blob:
                continue
            if current:
                current["end_frame_index_exclusive"] = frame_index
                active.pop(path, None)
            if not blob:
                continue
            raw = contents.get(blob, b"")
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = None
            kind = "SEAT_SOURCE" if path == LABBOIB_SEAT_PATH else "CURSOR_SOURCE"
            valid = isinstance(payload, dict) and (
                (kind == "SEAT_SOURCE" and payload.get("schema_version") == "temporal_seat_manifest_v0" and isinstance(payload.get("seat_id"), str))
                or (kind == "CURSOR_SOURCE" and isinstance(payload.get("consumer"), str) and isinstance(payload.get("cursor_state"), str))
            )
            version = {
                "source_version_id": _identity("actor-source-version", {"path": path, "blob": blob}),
                "source_kind": kind,
                "path": path,
                "start_frame_index": frame_index,
                "end_frame_index_exclusive": None,
                "git_object_sha": blob,
                "content_identity": f"sha256:{hashlib.sha256(raw).hexdigest()}",
                "admission_standing": "SOURCE_BOUND" if valid else "REJECTED_MALFORMED",
                "payload": payload if valid else None,
            }
            versions.append(version)
            active[path] = version

    observe(0)
    for index, transition in enumerate(transitions, start=1):
        for event in transition["events"]:
            old_path = event.get("old_path")
            new_path = event.get("new_path")
            if old_path:
                state.pop(old_path, None)
            if new_path and event.get("after"):
                state[new_path] = dict(event["after"])
        observe(index)
    return versions


def _wound_replay(
    frames: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    for transition in transitions:
        for event in transition["events"]:
            if WOUND_PATH not in {event.get("old_path"), event.get("new_path")}:
                continue
            distinctions = [
                {
                    "classification": category,
                    "source_handles": event["source_handles"],
                }
                for category in event["classifications"]
                if category in {"APPEARED", "PERSISTED", "CONTENT_CHANGED", "PATH_CHANGED", "IDENTITY_UNRESOLVED"}
            ]
            distinctions.extend(
                [
                    {
                        "classification": "GIT_AUTHORSHIP_METADATA_ONLY",
                        "source_handles": [
                            {
                                "handle_kind": "GIT_COMMIT_METADATA",
                                "commit_sha": transition["to_commit_sha"],
                            }
                        ],
                    },
                    {
                        "classification": "SEAT_ACTOR_UNRESOLVED",
                        "source_handles": [
                            {
                                "handle_kind": "ABSENCE_IN_ADMITTED_TRANSITION_EVIDENCE",
                                "transition_id": transition["transition_id"],
                            }
                        ],
                    },
                    {
                        "classification": "SEMANTIC_CAUSE_UNRESOLVED",
                        "source_handles": [
                            {
                                "handle_kind": "NO_EXPLICIT_SOURCE_TO_RESULT_RELATION",
                                "transition_id": transition["transition_id"],
                            }
                        ],
                    },
                ]
            )
            steps.append(
                {
                    "step_id": _identity("wound-step", {"event": event["event_id"]}),
                    "transition_id": transition["transition_id"],
                    "event_id": event["event_id"],
                    "from_frame_id": transition["from_frame_id"],
                    "to_frame_id": transition["to_frame_id"],
                    "mechanical_diff": event,
                    "distinctions": distinctions,
                    "actor_lineage": "UNRESOLVED",
                    "semantic_lineage": "UNRESOLVED",
                }
            )
    return {
        "wound_id": "PATH_IDENTITY_VS_CONTENT_IDENTITY_ATLAS_APP_001",
        "family": "PATH_IDENTITY != CONTENT_IDENTITY",
        "target_path": WOUND_PATH,
        "steps": steps,
        "claim_ceiling": (
            "The replay establishes exact path, blob, commit, and adjacent-frame change relations. "
            "Git authorship remains metadata; seat actor and semantic cause remain unresolved."
        ),
    }


def build_repository_temporal_lineage(
    repo: str | Path,
    *,
    source_ref: str,
    repository_identity: str | None = None,
) -> dict[str, Any]:
    root = Path(repo).resolve()
    repository = repository_identity or infer_repository_identity(root)
    commit = _git(root, "rev-parse", f"{source_ref}^{{commit}}").decode("ascii").strip()
    branch = _branch_coordinate(root, source_ref)
    commit_rows = _commit_rows(root, commit)
    if not commit_rows:
        raise RepositoryTemporalLineageError("first-parent history is empty")
    ref_context = {"requested_ref": source_ref, "source_branch": branch, "resolved_head": commit}
    frames: list[dict[str, Any]] = []
    for index, row in enumerate(commit_rows):
        frame_id = _identity(
            "temporal-frame",
            {
                "repository": repository,
                "commit": row["commit_sha"],
                "tree": row["tree_sha"],
                "ref_context": ref_context,
            },
        )
        frames.append(
            {
                **row,
                "frame_index": index,
                "frame_id": frame_id,
                "repository_identity": repository,
                "source_ref_context": ref_context,
                "actor_lineage_standing": "UNRESOLVED_UNLESS_EXPLICIT_SOURCE_BINDS_TRANSITION",
                "semantic_lineage_standing": "UNRESOLVED_UNLESS_EXPLICIT_SOURCE_BINDS_TRANSITION",
            }
        )

    initial_entries = _tree_entries(root, frames[0]["commit_sha"])
    state: dict[str, dict[str, Any]] = {}
    for entry in initial_entries:
        enriched = {
            **entry,
            "lineage_id": _lineage_id(repository, frames[0]["commit_sha"], entry["path"], "ROOT_TREE"),
        }
        state[entry["path"]] = enriched
    initial_entries = [state[path] for path in sorted(state)]

    transitions: list[dict[str, Any]] = []
    object_ids: set[str] = {entry["git_object_sha"] for entry in initial_entries}
    for index in range(1, len(frames)):
        before = frames[index - 1]
        after = frames[index]
        transition_id = _identity(
            "temporal-transition",
            {"repository": repository, "from": before["frame_id"], "to": after["frame_id"]},
        )
        events: list[dict[str, Any]] = []
        for ordinal, row in enumerate(_raw_diff(root, before["commit_sha"], after["commit_sha"])):
            status = str(row["status"])
            old_path = row["old_path"]
            new_path = row["new_path"]
            old_entry = state.get(str(old_path)) if old_path else None
            categories, identity_basis = _classifications(row)
            exact_rename = status == "R100"
            if exact_rename and old_entry:
                lineage_id = old_entry["lineage_id"]
            elif status not in {"A", "D"} and not status.startswith("R") and old_entry:
                lineage_id = old_entry["lineage_id"]
            elif new_path:
                lineage_id = _lineage_id(repository, after["commit_sha"], str(new_path), f"EVENT_{ordinal}")
            else:
                lineage_id = old_entry["lineage_id"] if old_entry else None
            after_entry = None
            if new_path:
                after_entry = {
                    "path": new_path,
                    "git_mode": row["new_mode"],
                    "git_object_type": "commit" if row["new_mode"] == "160000" else "blob",
                    "git_object_sha": row["new_object_sha"],
                    "lineage_id": lineage_id,
                }
            event_id = _identity(
                "temporal-event",
                {
                    "transition": transition_id,
                    "ordinal": ordinal,
                    "status": status,
                    "old_path": old_path,
                    "new_path": new_path,
                    "old_object_sha": row["old_object_sha"],
                    "new_object_sha": row["new_object_sha"],
                },
            )
            event = {
                "event_id": event_id,
                "ordinal": ordinal,
                **row,
                "lineage_id_before": old_entry.get("lineage_id") if old_entry else None,
                "lineage_id_after": lineage_id if new_path else None,
                "identity_basis": identity_basis,
                "classifications": categories,
                "before": old_entry,
                "after": after_entry,
                "relation_changes": {
                    "added": ["CONTAINS", "HAS_VERSION"] if "RELATION_ADDED" in categories else [],
                    "removed": ["CONTAINS", "HAS_VERSION"] if "RELATION_REMOVED" in categories else [],
                },
                "actor_lineage": "UNRESOLVED",
                "semantic_lineage": "UNRESOLVED",
                "source_handles": [
                    {
                        "handle_kind": "GIT_ADJACENT_DIFF",
                        "from_commit_sha": before["commit_sha"],
                        "to_commit_sha": after["commit_sha"],
                    },
                    {
                        "handle_kind": "GIT_OBJECT_PAIR",
                        "old_object_sha": row["old_object_sha"],
                        "new_object_sha": row["new_object_sha"],
                    },
                ],
            }
            events.append(event)
            if old_path:
                state.pop(str(old_path), None)
            if new_path and after_entry:
                state[str(new_path)] = after_entry
            for object_sha in (row["old_object_sha"], row["new_object_sha"]):
                if object_sha:
                    object_ids.add(str(object_sha))
        transitions.append(
            {
                "transition_id": transition_id,
                "transition_index": index - 1,
                "from_frame_id": before["frame_id"],
                "to_frame_id": after["frame_id"],
                "from_commit_sha": before["commit_sha"],
                "to_commit_sha": after["commit_sha"],
                "events": events,
                "event_count": len(events),
                "git_authorship": after["git_author"],
                "seat_actor": "UNRESOLVED",
                "semantic_cause": "UNRESOLVED",
                "source_handles": [
                    {"handle_kind": "GIT_COMMIT", "commit_sha": after["commit_sha"], "tree_sha": after["tree_sha"]},
                    {"handle_kind": "GIT_PARENT", "commit_sha": before["commit_sha"]},
                ],
            }
        )

    contents = _object_contents(root, object_ids)
    content_sha256 = {
        object_sha: hashlib.sha256(content).hexdigest()
        for object_sha, content in contents.items()
    }
    for entry in initial_entries:
        entry["content_identity"] = f"sha256:{content_sha256[entry['git_object_sha']]}"
    for transition in transitions:
        for event in transition["events"]:
            for side in ("before", "after"):
                entry = event.get(side)
                if entry and entry.get("git_object_sha"):
                    digest = content_sha256.get(entry["git_object_sha"])
                    if digest:
                        entry["content_identity"] = f"sha256:{digest}"
            event["declared_operational_relations"] = []
            old_path = event.get("old_path")
            new_path = event.get("new_path")
            if (
                old_path
                and old_path == new_path
                and old_path.startswith("continuity/cursors/")
                and old_path.endswith(".json")
                and event.get("old_object_sha") in contents
                and event.get("new_object_sha") in contents
            ):
                try:
                    before_cursor = json.loads(contents[event["old_object_sha"]].decode("utf-8"))
                    after_cursor = json.loads(contents[event["new_object_sha"]].decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    before_cursor = after_cursor = None
                if (
                    isinstance(before_cursor, dict)
                    and isinstance(after_cursor, dict)
                    and before_cursor.get("consumer") == after_cursor.get("consumer")
                    and before_cursor.get("last_seen_event_id") != after_cursor.get("last_seen_event_id")
                ):
                    event["actor_lineage"] = "EXPLICIT_CURSOR_TRANSITION"
                    event["declared_operational_relations"].append(
                        {
                            "relation": "CURSOR_ADVANCED_TO",
                            "consumer": after_cursor.get("consumer"),
                            "from_event_id": before_cursor.get("last_seen_event_id"),
                            "to_event_id": after_cursor.get("last_seen_event_id"),
                            "source_path": old_path,
                            "source_handles": event["source_handles"],
                        }
                    )

    actor_sources = _actor_source_versions(frames, initial_entries, transitions, contents)
    wound = _wound_replay(frames, transitions)
    return {
        "object_type": OBJECT_TYPE,
        "projection_standing": "DERIVED_READ_ONLY",
        "repository_identity": repository,
        "requested_ref": source_ref,
        "source_branch": branch,
        "source_commit": commit,
        "history_order": "FIRST_PARENT_ROOT_TO_HEAD",
        "frame_identity_rule": "SHA256(repository identity + exact commit + exact tree + source ref context)",
        "object_persistence_rule": "same lineage only for adjacent same-path persistence or exact R100 blob rename",
        "rename_ambiguity_rule": "R100 carries identity; lower similarity starts a new identity and emits IDENTITY_UNRESOLVED",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
        "frames": frames,
        "initial_entries": initial_entries,
        "transitions": transitions,
        "actor_source_versions": actor_sources,
        "wound_replay": wound,
        "counts": {
            "frames": len(frames),
            "transitions": len(transitions),
            "events": sum(item["event_count"] for item in transitions),
            "actor_source_versions": len(actor_sources),
            "wound_steps": len(wound["steps"]),
        },
        "claim_ceiling": (
            "This projection establishes deterministic first-parent Git frames, adjacent mechanical diffs, "
            "and explicit seat/cursor source projection. Temporal succession is not causation; Git author "
            "metadata is not seat identity; absent semantic or actor lineage remains unresolved."
        ),
    }


def generate_repository_temporal_lineage(
    *,
    repo: str | Path,
    source_ref: str,
    output: str | Path,
    repository_identity: str | None = None,
) -> dict[str, Any]:
    output_path = Path(output)
    temporary = output_path.with_name(output_path.name + ".tmp")
    output_path.unlink(missing_ok=True)
    temporary.unlink(missing_ok=True)
    model = build_repository_temporal_lineage(
        repo,
        source_ref=source_ref,
        repository_identity=repository_identity,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        temporary.write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(output_path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        raise
    return model


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the source-bound temporal Atlas lineage V0.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--repository-identity", default=None)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    model = generate_repository_temporal_lineage(
        repo=args.repo,
        source_ref=args.source_ref,
        repository_identity=args.repository_identity,
        output=args.output,
    )
    print(json.dumps({"output": args.output, "source_commit": model["source_commit"], "counts": model["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
