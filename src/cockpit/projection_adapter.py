"""Build the bounded Cockpit v0 model from one exact committed Git tree."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any


ADAPTER_VERSION = "cockpit_projection_adapter_v0"

REQUIRED_SOURCE_PATHS = (
    "PROJECT_STATE.md",
    "PRESSURE_RESOLUTION_MAP.md",
    "docs/constraints/README.md",
    "docs/constraints/registry.jsonl",
)

PROJECTION_DOCUMENT_PATHS = (
    "docs/projection/Controller.md",
    "docs/projection/Persistent_Ecology.md",
    "docs/projection/Persistent_Research_Autonomy.md",
)

KNOWN_PRESSURE_STANDINGS = frozenset(
    {
        "ACTIVE",
        "BASIS_INSUFFICIENT",
        "BLOCKER_REMOVED",
        "BOUNDED_RESOLUTION",
        "CANDIDATE_SURVIVED",
        "EQUIVALENT_UNDER_CURRENT_PRESSURE",
        "OPEN",
        "PARTIAL_RESOLUTION",
    }
)

PRESSURE_HEADING_RE = re.compile(r"^### (PR-\d{3})\s+(?:\u2014|-)\s+(.+?)\s*$")
HISTORY_HEADING_RE = re.compile(r"^#### (PR-\d{3})\s+(?:\u2014|-)\s+Resolution history\s*$")
FIELD_RE = re.compile(r"^- \*\*([^:]+):\*\*\s*(.*)$")
HISTORY_ENTRY_RE = re.compile(
    r"^- \*\*(R\d+)\s+(?:\u2014|-)\s+`([^`]+)`:\*\*\s*(.*)$"
)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PRESSURE_ID_RE = re.compile(r"\bPR-\d{3}\b")


class ProjectionAdapterError(RuntimeError):
    """Raised when no exact committed projection basis can be established."""


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _git_text(repo_root: Path, *args: str) -> tuple[int, str, str]:
    completed = _git(repo_root, *args)
    return (
        completed.returncode,
        completed.stdout.decode("utf-8", errors="replace").strip(),
        completed.stderr.decode("utf-8", errors="replace").strip(),
    )


def _resolve_commit(repo_root: Path, source_ref: str) -> str:
    code, output, error = _git_text(
        repo_root, "rev-parse", "--verify", f"{source_ref}^{{commit}}"
    )
    if code != 0 or not re.fullmatch(r"[0-9a-fA-F]{40}", output):
        detail = error or output or "no commit returned"
        raise ProjectionAdapterError(
            f"cannot resolve source ref {source_ref!r} to an exact commit: {detail}"
        )
    return output.lower()


def _read_committed_text(
    repo_root: Path,
    source_commit: str,
    source_path: str,
) -> tuple[str | None, str | None]:
    completed = _git(repo_root, "show", f"{source_commit}:{source_path}")
    if completed.returncode != 0:
        return None, completed.stderr.decode("utf-8", errors="replace").strip()
    try:
        return completed.stdout.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"source is not valid UTF-8: {exc}"


def _committed_path_exists(repo_root: Path, source_commit: str, source_path: str) -> bool:
    return _git(repo_root, "cat-file", "-e", f"{source_commit}:{source_path}").returncode == 0


def _provenance(
    source_path: str,
    source_commit: str,
    source_kind: str,
    source_anchor: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "source_path": source_path,
        "source_commit": source_commit,
        "source_kind": source_kind,
    }
    if source_anchor is not None:
        value["source_anchor"] = source_anchor
    return value


def _diagnostic(
    diagnostics: list[dict[str, Any]],
    *,
    kind: str,
    source_commit: str,
    message: str,
    severity: str,
    source_path: str | None = None,
    source_kind: str = "projection_adapter",
    source_anchor: str | None = None,
    object_id: str | None = None,
    field: str | None = None,
    raw_value: Any = None,
) -> None:
    affected: dict[str, Any] = {}
    if source_path is not None:
        affected["source_path"] = source_path
    if object_id is not None:
        affected["object_id"] = object_id
    if field is not None:
        affected["field"] = field
    item: dict[str, Any] = {
        "kind": kind,
        "affected": affected,
        "message": message,
        "severity": severity,
        "provenance": _provenance(
            source_path or "git",
            source_commit,
            source_kind,
            source_anchor,
        ),
    }
    if raw_value is not None:
        item["raw_value"] = raw_value
    diagnostics.append(item)


def _section(lines: list[str], heading: str) -> tuple[list[str] | None, int | None]:
    try:
        start = lines.index(heading)
    except ValueError:
        return None, None
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = re.match(r"^(#+)\s", lines[index])
        if match and len(match.group(1)) <= level:
            end = index
            break
    return lines[start + 1 : end], start + 1


def _normalize_wrapped(parts: list[str]) -> tuple[str, str]:
    raw = "\n".join(part.rstrip() for part in parts).strip()
    normalized = " ".join(part.strip() for part in parts if part.strip())
    return raw, normalized


def _parse_explicit_fields(lines: list[str]) -> dict[str, dict[str, str]]:
    fields: dict[str, dict[str, str]] = {}
    current_name: str | None = None
    current_parts: list[str] = []

    def finish() -> None:
        nonlocal current_name, current_parts
        if current_name is None:
            return
        raw, normalized = _normalize_wrapped(current_parts)
        fields[current_name] = {"raw_value": raw, "value": normalized}
        current_name = None
        current_parts = []

    for line in lines:
        match = FIELD_RE.match(line)
        if match:
            finish()
            current_name = match.group(1).strip().lower().replace(" ", "_")
            current_parts = [match.group(2)]
        elif current_name is not None and (line.startswith("  ") or not line.strip()):
            if line.strip():
                current_parts.append(line.strip())
        elif current_name is not None:
            finish()
    finish()
    return fields


def _strip_status_token(raw_value: str) -> str:
    value = raw_value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    return value.strip().rstrip(".")


def _standing_value(
    raw_value: str,
    *,
    diagnostics: list[dict[str, Any]],
    source_commit: str,
    source_path: str,
    source_anchor: str,
    object_id: str,
    field: str,
) -> dict[str, Any]:
    token = _strip_status_token(raw_value)
    status = "known_value" if token in KNOWN_PRESSURE_STANDINGS else "unknown_standing"
    if status == "unknown_standing":
        _diagnostic(
            diagnostics,
            kind="unknown_standing",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="pressure_map",
            source_anchor=source_anchor,
            object_id=object_id,
            field=field,
            raw_value=raw_value,
            message=f"unrecognized pressure standing {token!r} was preserved",
            severity="warning",
        )
    return {"raw_value": raw_value, "value": token, "status": status}


def _is_explicit_absence(value: str) -> bool:
    return value.strip() in {"-", "\u2013", "\u2014"}


def _field_or_missing(
    fields: dict[str, dict[str, str]],
    name: str,
    *,
    diagnostics: list[dict[str, Any]],
    source_commit: str,
    source_path: str,
    source_anchor: str,
    object_id: str,
) -> dict[str, Any]:
    item = fields.get(name)
    if item is None:
        _diagnostic(
            diagnostics,
            kind="parse_failure",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="pressure_map",
            source_anchor=source_anchor,
            object_id=object_id,
            field=name,
            message=f"required pressure field {name!r} is missing",
            severity="error",
        )
        return {"raw_value": None, "value": None, "status": "missing"}
    if _is_explicit_absence(item["value"]):
        return {**item, "value": None, "status": "explicit_absent"}
    return {**item, "status": "known_value"}


def _parse_history(
    lines: list[str],
    *,
    pressure_id: str,
    source_path: str,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    heading_index: int | None = None
    heading_text: str | None = None
    for index, line in enumerate(lines):
        match = HISTORY_HEADING_RE.match(line)
        if match and match.group(1) == pressure_id:
            heading_index = index
            heading_text = line.removeprefix("#### ")
            break
    if heading_index is None or heading_text is None:
        return []

    history: list[dict[str, Any]] = []
    index = heading_index + 1
    while index < len(lines):
        match = HISTORY_ENTRY_RE.match(lines[index])
        if not match:
            index += 1
            continue
        label, standing_raw, first_summary = match.groups()
        parts = [first_summary]
        index += 1
        while index < len(lines) and lines[index].startswith("  "):
            parts.append(lines[index].strip())
            index += 1
        raw_summary, summary = _normalize_wrapped(parts)
        anchor = f"{heading_text} / {label}"
        history.append(
            {
                "id": label,
                "standing": _standing_value(
                    standing_raw,
                    diagnostics=diagnostics,
                    source_commit=source_commit,
                    source_path=source_path,
                    source_anchor=anchor,
                    object_id=pressure_id,
                    field=f"resolution_history.{label}.standing",
                ),
                "summary": summary,
                "raw_summary": raw_summary,
                "provenance": _provenance(
                    source_path, source_commit, "pressure_map", anchor
                ),
            }
        )
    return history


def _reference_kind(target: str) -> str:
    lowered = target.lower()
    if lowered.startswith(("http://", "https://")):
        return "commit" if "/commit/" in lowered else "external"
    path = target.split("#", 1)[0].split("::", 1)[0].replace("\\", "/")
    rules = (
        ("docs/decisions/", "decision"),
        ("traces/", "trace"),
        ("tests/", "test"),
        ("docs/contracts/", "contract"),
        ("docs/projection/", "projection"),
        ("src/", "implementation"),
        ("schemas/", "schema"),
    )
    for prefix, kind in rules:
        if path.startswith(prefix):
            return kind
    return "repository_path" if path else "unsupported"


def _reference_path(target: str) -> str | None:
    if target.lower().startswith(("http://", "https://")):
        return None
    path = target.split("#", 1)[0].split("::", 1)[0].replace("\\", "/").strip()
    if not path or path.startswith("/"):
        return None
    pure = PurePosixPath(path)
    if ".." in pure.parts:
        return None
    return pure.as_posix()


def _make_reference(
    *,
    repo_root: Path,
    source_commit: str,
    origin_kind: str,
    origin_id: str,
    source_path: str,
    source_anchor: str,
    target: str,
    label: str | None,
    occurrence: int,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    identity_basis = json.dumps(
        [origin_kind, origin_id, source_path, source_anchor, target, label, occurrence],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    reference_id = "evidence-" + hashlib.sha256(identity_basis.encode("utf-8")).hexdigest()[:16]
    target_kind = _reference_kind(target)
    committed_path = _reference_path(target)
    if target.lower().startswith(("http://", "https://")):
        resolution_status = "external_unchecked"
    elif committed_path is None:
        resolution_status = "unsupported"
    elif _committed_path_exists(repo_root, source_commit, committed_path):
        resolution_status = "resolved"
    else:
        resolution_status = "broken"
        _diagnostic(
            diagnostics,
            kind="broken_reference",
            source_commit=source_commit,
            source_path=source_path,
            source_kind=origin_kind,
            source_anchor=source_anchor,
            object_id=origin_id,
            field="evidence_reference",
            raw_value=target,
            message=f"committed evidence target {committed_path!r} does not exist",
            severity="warning",
        )
    return {
        "id": reference_id,
        "origin": {"kind": origin_kind, "id": origin_id},
        "original_target": target,
        "label": label,
        "target_kind": target_kind,
        "resolution_status": resolution_status,
        "committed_path_checked": committed_path,
        "provenance": _provenance(
            source_path, source_commit, origin_kind, source_anchor
        ),
    }


def _parse_pressure_map(
    text: str,
    *,
    repo_root: Path,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source_path = "PRESSURE_RESOLUTION_MAP.md"
    lines = text.splitlines()
    nodes: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []

    headings: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(lines):
        match = PRESSURE_HEADING_RE.match(line)
        if match:
            headings.append((index, match))

    for heading_position, (start, match) in enumerate(headings):
        end = headings[heading_position + 1][0] if heading_position + 1 < len(headings) else len(lines)
        for index in range(start + 1, end):
            if lines[index].startswith("## "):
                end = index
                break
        pressure_id, title = match.groups()
        anchor = f"{pressure_id} \u2014 {title}"
        node_lines = lines[start + 1 : end]
        history_start = next(
            (i for i, line in enumerate(node_lines) if HISTORY_HEADING_RE.match(line)),
            len(node_lines),
        )
        fields = _parse_explicit_fields(node_lines[:history_start])
        standing_field = _field_or_missing(
            fields,
            "standing",
            diagnostics=diagnostics,
            source_commit=source_commit,
            source_path=source_path,
            source_anchor=anchor,
            object_id=pressure_id,
        )
        if standing_field["status"] == "missing":
            standing = standing_field
        else:
            standing = _standing_value(
                standing_field["raw_value"],
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
                field="standing",
            )

        node: dict[str, Any] = {
            "id": pressure_id,
            "title": title,
            "pressure": _field_or_missing(
                fields,
                "pressure",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "standing": standing,
            "missing_discriminator": _field_or_missing(
                fields,
                "missing_discriminator",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "resolution_so_far": _field_or_missing(
                fields,
                "resolution_so_far",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "residue": _field_or_missing(
                fields,
                "residue",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "blocked_by": _field_or_missing(
                fields,
                "blocked_by",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "unlocks": _field_or_missing(
                fields,
                "unlocks",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "evidence": _field_or_missing(
                fields,
                "evidence",
                diagnostics=diagnostics,
                source_commit=source_commit,
                source_path=source_path,
                source_anchor=anchor,
                object_id=pressure_id,
            ),
            "evidence_ref_ids": [],
            "resolution_history": _parse_history(
                node_lines,
                pressure_id=pressure_id,
                source_path=source_path,
                source_commit=source_commit,
                diagnostics=diagnostics,
            ),
            "provenance": _provenance(
                source_path, source_commit, "pressure_map", anchor
            ),
        }

        for relation_field, relation_kind in (
            ("blocked_by", "blocked_by"),
            ("unlocks", "unlocks"),
        ):
            field_value = node[relation_field]
            if field_value["status"] != "known_value":
                continue
            raw_value = field_value["value"]
            targets = list(dict.fromkeys(PRESSURE_ID_RE.findall(raw_value)))
            if targets:
                for target in targets:
                    relations.append(
                        {
                            "relation_kind": relation_kind,
                            "source_pressure_id": pressure_id,
                            "target_kind": "pressure",
                            "target_pressure_id": target,
                            "condition_text": None,
                            "raw_source_field": field_value["raw_value"],
                            "provenance": _provenance(
                                source_path,
                                source_commit,
                                "pressure_map",
                                f"{anchor} / {relation_field}",
                            ),
                        }
                    )
            else:
                relations.append(
                    {
                        "relation_kind": relation_kind,
                        "source_pressure_id": pressure_id,
                        "target_kind": "declared_condition",
                        "target_pressure_id": None,
                        "condition_text": raw_value,
                        "raw_source_field": field_value["raw_value"],
                        "provenance": _provenance(
                            source_path,
                            source_commit,
                            "pressure_map",
                            f"{anchor} / {relation_field}",
                        ),
                    }
                )

        if node["evidence"]["status"] == "known_value":
            for occurrence, link in enumerate(
                MARKDOWN_LINK_RE.finditer(node["evidence"]["value"])
            ):
                reference = _make_reference(
                    repo_root=repo_root,
                    source_commit=source_commit,
                    origin_kind="pressure_node",
                    origin_id=pressure_id,
                    source_path=source_path,
                    source_anchor=f"{anchor} / evidence",
                    target=link.group(2),
                    label=link.group(1),
                    occurrence=occurrence,
                    diagnostics=diagnostics,
                )
                references.append(reference)
                node["evidence_ref_ids"].append(reference["id"])
        nodes.append(node)

    navigation = _parse_current_navigation(
        lines,
        source_path=source_path,
        source_commit=source_commit,
        diagnostics=diagnostics,
    )
    nodes.sort(key=lambda item: int(item["id"].split("-")[1]))
    relations.sort(
        key=lambda item: (
            int(item["source_pressure_id"].split("-")[1]),
            item["relation_kind"],
            item["target_pressure_id"] or item["condition_text"] or "",
        )
    )
    return nodes, relations, references, navigation


def _declared_pressure_list(
    entries: list[tuple[str, str]],
    *,
    source_path: str,
    source_commit: str,
    source_anchor: str,
) -> dict[str, Any]:
    return {
        "values": [pressure_id for pressure_id, _ in entries],
        "entries": [
            {
                "pressure_id": pressure_id,
                "raw_value": raw_value,
                "provenance": _provenance(
                    source_path, source_commit, "pressure_map", source_anchor
                ),
            }
            for pressure_id, raw_value in entries
        ],
    }


def _parse_current_navigation(
    lines: list[str],
    *,
    source_path: str,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    section_lines, _ = _section(lines, "## Current Navigation")
    anchor = "Current Navigation"
    if section_lines is None:
        _diagnostic(
            diagnostics,
            kind="parse_failure",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="pressure_map",
            source_anchor=anchor,
            field="current_navigation",
            message="Current Navigation section is missing",
            severity="error",
        )
        return {
            "active_pressure": {"raw_value": None, "value": None, "status": "missing"},
            "newly_reachable_open": {"values": [], "entries": [], "status": "missing"},
            "shelved": {"values": [], "entries": [], "status": "missing"},
        }

    active: dict[str, Any] | None = None
    lists: dict[str, list[tuple[str, str]]] = {"newly_reachable_open": [], "shelved": []}
    list_state: str | None = None
    for line in section_lines:
        active_match = re.match(r"^Active pressure:\s*(.+?)\s*$", line)
        if active_match:
            raw = active_match.group(1)
            if raw.lower() == "none":
                active = {"raw_value": raw, "value": None, "status": "explicit_none"}
            else:
                active = {"raw_value": raw, "value": raw, "status": "known_value"}
            continue
        if line.strip() == "Newly reachable / open:":
            list_state = "newly_reachable_open"
            continue
        if line.strip() == "Shelved:":
            list_state = "shelved"
            continue
        item_match = re.match(r"^- (PR-\d{3})\s+(?:\u2014|-)\s+(.+)$", line)
        if list_state and item_match:
            lists[list_state].append((item_match.group(1), line[2:]))

    if active is None:
        active = {"raw_value": None, "value": None, "status": "missing"}
        _diagnostic(
            diagnostics,
            kind="parse_failure",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="pressure_map",
            source_anchor=anchor,
            field="active_pressure",
            message="explicit Active pressure declaration is missing",
            severity="error",
        )
    active["provenance"] = _provenance(
        source_path, source_commit, "pressure_map", f"{anchor} / Active pressure"
    )
    return {
        "active_pressure": active,
        "newly_reachable_open": {
            **_declared_pressure_list(
                lists["newly_reachable_open"],
                source_path=source_path,
                source_commit=source_commit,
                source_anchor=f"{anchor} / Newly reachable / open",
            ),
            "status": "known_value",
        },
        "shelved": {
            **_declared_pressure_list(
                lists["shelved"],
                source_path=source_path,
                source_commit=source_commit,
                source_anchor=f"{anchor} / Shelved",
            ),
            "status": "known_value",
        },
    }


def _parse_project_state(
    text: str,
    *,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    source_path = "PROJECT_STATE.md"
    anchor = "Current Navigation and Development Standing"
    section_lines, _ = _section(text.splitlines(), f"## {anchor}")
    if section_lines is None:
        _diagnostic(
            diagnostics,
            kind="parse_failure",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="project_state",
            source_anchor=anchor,
            field="current_navigation_and_development_standing",
            message="bounded current/development section is missing",
            severity="error",
        )
        return {
            "active_pressure": {"raw_value": None, "value": None, "status": "missing"},
            "open_pressures": [],
            "next_experimental_pressure": {"value": None, "status": "missing"},
            "development_notes": [],
        }

    active: dict[str, Any] | None = None
    open_pressures: list[dict[str, Any]] = []
    next_pressure: dict[str, Any] = {"value": None, "status": "missing"}
    for line in section_lines:
        active_match = re.match(r"^- Active experimental pressure:\s*(.+?)\.?\s*$", line)
        if active_match:
            raw = active_match.group(1).rstrip(".")
            active = {
                "raw_value": raw,
                "value": None if raw.lower() == "none" else raw,
                "status": "explicit_none" if raw.lower() == "none" else "known_value",
                "provenance": _provenance(
                    source_path, source_commit, "project_state", f"{anchor} / active pressure"
                ),
            }
        open_match = re.match(r"^- (PR-\d{3}) remains `([^`]+)`", line)
        if open_match:
            open_pressures.append(
                {
                    "pressure_id": open_match.group(1),
                    "standing": open_match.group(2),
                    "raw_value": line[2:],
                    "provenance": _provenance(
                        source_path,
                        source_commit,
                        "project_state",
                        f"{anchor} / {open_match.group(1)}",
                    ),
                }
            )
        if re.match(r"^- No next experimental pressure has been selected\.?\s*$", line):
            next_pressure = {
                "value": None,
                "status": "explicit_none",
                "raw_value": line[2:],
                "provenance": _provenance(
                    source_path, source_commit, "project_state", f"{anchor} / next pressure"
                ),
            }

    if active is None:
        active = {"raw_value": None, "value": None, "status": "missing"}
        _diagnostic(
            diagnostics,
            kind="parse_failure",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="project_state",
            source_anchor=anchor,
            field="active_pressure",
            message="explicit active experimental pressure declaration is missing",
            severity="error",
        )

    paragraphs: list[str] = []
    current: list[str] = []
    for line in section_lines:
        if not line.strip():
            if current:
                paragraphs.append(" ".join(part.strip() for part in current))
                current = []
        elif not line.startswith("-"):
            current.append(line)
    if current:
        paragraphs.append(" ".join(part.strip() for part in current))
    development_notes = [
        {
            "text": paragraph,
            "provenance": _provenance(
                source_path, source_commit, "project_state", anchor
            ),
        }
        for paragraph in paragraphs
        if "DME Cockpit" in paragraph or "Controller" in paragraph
    ]
    return {
        "active_pressure": active,
        "open_pressures": sorted(open_pressures, key=lambda item: item["pressure_id"]),
        "next_experimental_pressure": next_pressure,
        "development_notes": development_notes,
        "provenance": _provenance(source_path, source_commit, "project_state", anchor),
    }


def _compare_navigation(
    map_navigation: dict[str, Any],
    project_state: dict[str, Any],
    *,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    map_active = map_navigation["active_pressure"]
    project_active = project_state["active_pressure"]
    declarations = [map_active, project_active]
    comparable = all(item["status"] in {"explicit_none", "known_value"} for item in declarations)
    if comparable and map_active["value"] == project_active["value"]:
        active_status = "agreement"
        active_value = map_active["value"]
        semantic_status = map_active["status"]
    elif comparable:
        active_status = "conflicting"
        active_value = None
        semantic_status = "conflicting"
        _diagnostic(
            diagnostics,
            kind="source_conflict",
            source_commit=source_commit,
            source_path="PRESSURE_RESOLUTION_MAP.md",
            source_kind="projection_normalization",
            source_anchor="Current Navigation / Active pressure",
            field="active_pressure",
            raw_value=[map_active["raw_value"], project_active["raw_value"]],
            message="Pressure Map and PROJECT_STATE active-pressure declarations disagree",
            severity="error",
        )
    else:
        active_status = "partial"
        active_value = next(
            (item["value"] for item in declarations if item["status"] in {"explicit_none", "known_value"}),
            None,
        )
        semantic_status = "missing"

    map_open = map_navigation["newly_reachable_open"]["values"]
    project_open = [
        item["pressure_id"]
        for item in project_state["open_pressures"]
        if item["standing"] == "OPEN"
    ]
    if map_open == project_open:
        open_status = "agreement"
    else:
        open_status = "conflicting"
        _diagnostic(
            diagnostics,
            kind="source_conflict",
            source_commit=source_commit,
            source_path="PRESSURE_RESOLUTION_MAP.md",
            source_kind="projection_normalization",
            source_anchor="Current Navigation / Newly reachable / open",
            field="newly_reachable_open",
            raw_value={"pressure_map": map_open, "project_state": project_open},
            message="Pressure Map and PROJECT_STATE open-pressure declarations disagree",
            severity="error",
        )

    return {
        "active_pressure": {
            "value": active_value,
            "status": active_status,
            "semantic_status": semantic_status,
            "declarations": declarations,
        },
        "newly_reachable_open_pressures": {
            "values": map_open if open_status == "agreement" else [],
            "status": open_status,
            "declarations": [
                {
                    "source_path": "PRESSURE_RESOLUTION_MAP.md",
                    "values": map_open,
                    "entries": map_navigation["newly_reachable_open"]["entries"],
                },
                {
                    "source_path": "PROJECT_STATE.md",
                    "values": project_open,
                    "entries": project_state["open_pressures"],
                },
            ],
        },
        "shelved_pressures": map_navigation["shelved"],
        "next_experimental_pressure": project_state["next_experimental_pressure"],
    }


def _parse_constraints(
    text: str,
    *,
    repo_root: Path,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_path = "docs/constraints/registry.jsonl"
    required_fields = (
        "id",
        "left",
        "relation",
        "right",
        "scope",
        "basis",
        "provenance",
        "standing",
    )
    constraints: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        anchor = f"line {line_number}"
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            _diagnostic(
                diagnostics,
                kind="parse_failure",
                source_commit=source_commit,
                source_path=source_path,
                source_kind="constraint_registry",
                source_anchor=anchor,
                object_id=f"line-{line_number}",
                raw_value=line,
                message=f"malformed constraint JSONL record: {exc.msg}",
                severity="error",
            )
            continue
        if not isinstance(record, dict):
            _diagnostic(
                diagnostics,
                kind="unsupported_structure",
                source_commit=source_commit,
                source_path=source_path,
                source_kind="constraint_registry",
                source_anchor=anchor,
                object_id=f"line-{line_number}",
                raw_value=record,
                message="constraint JSONL record is not an object",
                severity="error",
            )
            continue
        missing = [field for field in required_fields if field not in record]
        if missing:
            _diagnostic(
                diagnostics,
                kind="unsupported_structure",
                source_commit=source_commit,
                source_path=source_path,
                source_kind="constraint_registry",
                source_anchor=anchor,
                object_id=str(record.get("id", f"line-{line_number}")),
                field=",".join(missing),
                raw_value=record,
                message=f"constraint record is missing required fields: {', '.join(missing)}",
                severity="error",
            )
            continue
        constraint = {
            "classification": "constraint",
            **{field: record[field] for field in required_fields},
            "adapter_provenance": _provenance(
                source_path,
                source_commit,
                "constraint_registry",
                f"{anchor} / {record['id']}",
            ),
            "evidence_ref_ids": [],
        }
        if "note" in record:
            constraint["note"] = record["note"]
        if isinstance(record["provenance"], list):
            for occurrence, target in enumerate(record["provenance"]):
                if not isinstance(target, str):
                    _diagnostic(
                        diagnostics,
                        kind="unsupported_structure",
                        source_commit=source_commit,
                        source_path=source_path,
                        source_kind="constraint_registry",
                        source_anchor=anchor,
                        object_id=str(record["id"]),
                        field="provenance",
                        raw_value=target,
                        message="constraint provenance target is not a string",
                        severity="warning",
                    )
                    continue
                reference = _make_reference(
                    repo_root=repo_root,
                    source_commit=source_commit,
                    origin_kind="constraint",
                    origin_id=str(record["id"]),
                    source_path=source_path,
                    source_anchor=f"{anchor} / {record['id']} / provenance",
                    target=target,
                    label=None,
                    occurrence=occurrence,
                    diagnostics=diagnostics,
                )
                references.append(reference)
                constraint["evidence_ref_ids"].append(reference["id"])
        else:
            _diagnostic(
                diagnostics,
                kind="unsupported_structure",
                source_commit=source_commit,
                source_path=source_path,
                source_kind="constraint_registry",
                source_anchor=anchor,
                object_id=str(record["id"]),
                field="provenance",
                raw_value=record["provenance"],
                message="constraint provenance is not a list",
                severity="warning",
            )
        constraints.append(constraint)
    constraints.sort(key=lambda item: item["id"])
    return constraints, references


def _first_paragraph(lines: list[str]) -> str | None:
    parts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if parts:
                break
            continue
        if stripped.startswith(("#", "```")):
            if parts:
                break
            continue
        parts.append(stripped.lstrip("> "))
    return " ".join(parts) if parts else None


def _parse_projection_document(
    text: str,
    *,
    source_path: str,
    source_commit: str,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    lines = text.splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), None)
    declaration_lines: list[str] = []
    for line in lines[1:]:
        if line.startswith(">"):
            value = line[1:].strip()
            if value:
                declaration_lines.append(value)
        elif declaration_lines and line.strip():
            break
    declaration = " ".join(declaration_lines) or None
    explicit_non_authority = bool(
        declaration and "non-authoritative projection" in declaration.lower()
    )

    standing_heading = None
    standing_text = None
    for heading in ("## Standing", "## Current Standing", "## Epistemic Status"):
        section_lines, _ = _section(lines, heading)
        if section_lines is not None:
            standing_heading = heading.removeprefix("## ")
            standing_text = _first_paragraph(section_lines)
            break
    if standing_text is None:
        _diagnostic(
            diagnostics,
            kind="unsupported_structure",
            source_commit=source_commit,
            source_path=source_path,
            source_kind="projection_document",
            source_anchor=title,
            field="standing",
            message="projection document has no supported explicit standing/status section",
            severity="warning",
        )
    exact_standing = None
    if standing_text:
        candidate = standing_text.strip().rstrip(".")
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", candidate):
            exact_standing = candidate
    return {
        "source_path": source_path,
        "title": title,
        "source_commit": source_commit,
        "classification": "projection_document",
        "explicit_non_authority": {
            "declared": explicit_non_authority,
            "text": declaration,
        },
        "standing": {
            "value": exact_standing or standing_text,
            "raw_value": standing_text,
            "status": "known_value" if standing_text is not None else "unknown",
            "source_heading": standing_heading,
        },
        "provenance": _provenance(
            source_path,
            source_commit,
            "projection_document",
            standing_heading or title,
        ),
    }


def _origin_identity(raw_origin: str | None) -> dict[str, Any]:
    if raw_origin is None:
        return {
            "raw_origin": None,
            "status": "unknown",
            "host": None,
            "owner": None,
            "repository": None,
        }
    patterns = (
        r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
    )
    for pattern in patterns:
        match = re.match(pattern, raw_origin)
        if match:
            return {
                "raw_origin": raw_origin,
                "status": "known_value",
                "host": "github.com",
                "owner": match.group(1),
                "repository": match.group(2),
            }
    return {
        "raw_origin": raw_origin,
        "status": "unknown",
        "host": None,
        "owner": None,
        "repository": None,
    }


def _branch(repo_root: Path, source_ref: str) -> dict[str, Any]:
    if source_ref == "HEAD":
        code, output, _ = _git_text(repo_root, "symbolic-ref", "--quiet", "--short", "HEAD")
        if code == 0 and output:
            return {"value": output, "status": "known_value"}
    code, output, _ = _git_text(repo_root, "rev-parse", "--abbrev-ref", source_ref)
    if code == 0 and output and output != "HEAD":
        return {"value": output, "status": "known_value"}
    return {"value": None, "status": "unknown"}


def _freshness(
    repo_root: Path,
    *,
    source_commit: str,
    freshness_ref: str | None,
    check_time: str,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    if freshness_ref is None:
        return {
            "freshness_ref": None,
            "observed_tail": None,
            "check_time": None,
            "status": "unknown",
        }
    try:
        observed_tail = _resolve_commit(repo_root, freshness_ref)
    except ProjectionAdapterError as exc:
        _diagnostic(
            diagnostics,
            kind="stale_projection_basis",
            source_commit=source_commit,
            source_path="git",
            source_kind="git_metadata",
            source_anchor=freshness_ref,
            field="freshness_ref",
            raw_value=freshness_ref,
            message=str(exc),
            severity="warning",
        )
        return {
            "freshness_ref": freshness_ref,
            "observed_tail": None,
            "check_time": check_time,
            "status": "unknown",
        }
    return {
        "freshness_ref": freshness_ref,
        "observed_tail": observed_tail,
        "check_time": check_time,
        "status": "current" if observed_tail == source_commit else "stale",
    }


def _sort_diagnostics(diagnostics: list[dict[str, Any]]) -> None:
    diagnostics.sort(
        key=lambda item: (
            item["kind"],
            item["affected"].get("source_path", ""),
            item["affected"].get("object_id", ""),
            item["affected"].get("field", ""),
            item["message"],
        )
    )


def build_projection(
    repo_root: str | Path,
    source_ref: str = "HEAD",
    freshness_ref: str | None = None,
    projection_time: str | None = None,
) -> dict[str, Any]:
    """Build a read-only normalized projection from one exact committed tree."""
    root = Path(repo_root).resolve()
    source_commit = _resolve_commit(root, source_ref)
    runtime_time = projection_time or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    diagnostics: list[dict[str, Any]] = []

    texts: dict[str, str] = {}
    source_surfaces: list[dict[str, Any]] = []
    for source_path in REQUIRED_SOURCE_PATHS:
        text, error = _read_committed_text(root, source_commit, source_path)
        if text is None:
            source_surfaces.append({"source_path": source_path, "status": "missing"})
            _diagnostic(
                diagnostics,
                kind="missing_required_source",
                source_commit=source_commit,
                source_path=source_path,
                source_kind="repository_artifact",
                message=f"required committed source is unavailable: {error}",
                severity="error",
            )
        else:
            texts[source_path] = text
            source_surfaces.append({"source_path": source_path, "status": "available"})

    pressure_nodes: list[dict[str, Any]] = []
    pressure_relations: list[dict[str, Any]] = []
    evidence_refs: list[dict[str, Any]] = []
    map_navigation: dict[str, Any] = {
        "active_pressure": {"raw_value": None, "value": None, "status": "missing"},
        "newly_reachable_open": {"values": [], "entries": [], "status": "missing"},
        "shelved": {"values": [], "entries": [], "status": "missing"},
    }
    map_text = texts.get("PRESSURE_RESOLUTION_MAP.md")
    if map_text is not None:
        pressure_nodes, pressure_relations, map_refs, map_navigation = _parse_pressure_map(
            map_text,
            repo_root=root,
            source_commit=source_commit,
            diagnostics=diagnostics,
        )
        evidence_refs.extend(map_refs)

    project_state_text = texts.get("PROJECT_STATE.md")
    project_state = (
        _parse_project_state(
            project_state_text,
            source_commit=source_commit,
            diagnostics=diagnostics,
        )
        if project_state_text is not None
        else {
            "active_pressure": {"raw_value": None, "value": None, "status": "missing"},
            "open_pressures": [],
            "next_experimental_pressure": {"value": None, "status": "missing"},
            "development_notes": [],
        }
    )
    current_navigation = _compare_navigation(
        map_navigation,
        project_state,
        source_commit=source_commit,
        diagnostics=diagnostics,
    )

    constraints: list[dict[str, Any]] = []
    registry_text = texts.get("docs/constraints/registry.jsonl")
    if registry_text is not None:
        constraints, constraint_refs = _parse_constraints(
            registry_text,
            repo_root=root,
            source_commit=source_commit,
            diagnostics=diagnostics,
        )
        evidence_refs.extend(constraint_refs)

    constraints_readme = texts.get("docs/constraints/README.md")
    if constraints_readme is not None and not (
        "constraint" in constraints_readme.lower()
        and "local distinction" in constraints_readme.lower()
    ):
        _diagnostic(
            diagnostics,
            kind="unsupported_structure",
            source_commit=source_commit,
            source_path="docs/constraints/README.md",
            source_kind="constraint_contract",
            message="constraint/local-distinction boundary is not explicitly recoverable",
            severity="error",
        )

    projection_documents: list[dict[str, Any]] = []
    for source_path in PROJECTION_DOCUMENT_PATHS:
        text, _ = _read_committed_text(root, source_commit, source_path)
        if text is None:
            continue
        projection_documents.append(
            _parse_projection_document(
                text,
                source_path=source_path,
                source_commit=source_commit,
                diagnostics=diagnostics,
            )
        )
    projection_documents.sort(key=lambda item: item["source_path"])
    evidence_refs.sort(
        key=lambda item: (
            item["origin"]["kind"],
            item["origin"]["id"],
            item["provenance"].get("source_anchor", ""),
            item["original_target"],
            item["id"],
        )
    )

    origin_code, raw_origin, _ = _git_text(root, "config", "--get", "remote.origin.url")
    identity = _origin_identity(raw_origin if origin_code == 0 and raw_origin else None)
    if identity["status"] == "unknown":
        _diagnostic(
            diagnostics,
            kind="unsupported_structure",
            source_commit=source_commit,
            source_path="git",
            source_kind="git_metadata",
            source_anchor="remote.origin.url",
            field="repository_identity",
            raw_value=identity["raw_origin"],
            message="repository origin could not be normalized by the bounded GitHub parser",
            severity="warning",
        )

    freshness = _freshness(
        root,
        source_commit=source_commit,
        freshness_ref=freshness_ref,
        check_time=runtime_time,
        diagnostics=diagnostics,
    )
    missing_required = sum(
        1 for item in source_surfaces if item["status"] == "missing"
    )
    has_operational_error = any(
        item["severity"] == "error" for item in diagnostics
    )
    if missing_required == len(REQUIRED_SOURCE_PATHS):
        projection_status = "failed"
    elif missing_required or has_operational_error:
        projection_status = "partial"
    else:
        projection_status = "complete"

    repository_state = {
        "projection_classification": "derived_read_only",
        "projection_status": projection_status,
        "repository_identity": identity,
        "branch": _branch(root, source_ref),
        "source_ref": source_ref,
        "source_commit": source_commit,
        "adapter_version": ADAPTER_VERSION,
        "projection_time": runtime_time,
        "freshness": freshness,
        "source_surfaces": source_surfaces,
        "current_navigation": current_navigation,
        "bounded_development_standing": project_state.get("development_notes", []),
    }

    _sort_diagnostics(diagnostics)
    return {
        "repository_state": repository_state,
        "pressure_nodes": pressure_nodes,
        "pressure_relations": pressure_relations,
        "constraints": constraints,
        "evidence_refs": evidence_refs,
        "projection_documents": projection_documents,
        "projection_diagnostics": diagnostics,
    }


def _write_projection(model: dict[str, Any], output: str | None) -> None:
    serialized = json.dumps(model, ensure_ascii=False, indent=2) + "\n"
    if output is None:
        print(serialized, end="")
        return
    Path(output).write_text(serialized, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Git repository root")
    parser.add_argument("--source-ref", default="HEAD", help="committed source ref")
    parser.add_argument("--freshness-ref", help="optional locally available comparison ref")
    parser.add_argument("--projection-time", help="explicit runtime projection timestamp")
    parser.add_argument("--output", help="derived JSON output path; stdout when omitted")
    args = parser.parse_args(argv)
    try:
        model = build_projection(
            args.repo,
            source_ref=args.source_ref,
            freshness_ref=args.freshness_ref,
            projection_time=args.projection_time,
        )
    except ProjectionAdapterError as exc:
        parser.error(str(exc))
    _write_projection(model, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
