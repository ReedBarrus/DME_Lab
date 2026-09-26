#!/usr/bin/env python3
"""ChatGPT-main temporal seat wake v0.

Reconstructs the bounded ChatGPT-main seat from committed durable state.

WAKE != ACK
WAKE != AUTHORITY
WAKE != EXECUTION
MODEL INSTANCE != SEAT
REGISTRY BINDING != LIVE INVOCATION BINDING
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any

SEAT_ID = "CHATGPT_MAIN"
REGISTRY_CONSUMER_ID = "chatgpt-main"
CONTINUITY_CONSUMER = "chatgpt"

MANIFEST_PATH = "continuity/seats/chatgpt-main.json"
CURSOR_PATH = "continuity/cursors/chatgpt.json"
WORKING_STATE_PATH = "continuity/current_state/chatgpt_main_working_state_v0.json"
REGISTRY_PATH = "continuity/registry.json"
EVENTS_PATH = "continuity/events.jsonl"
INBOX_PATH = "continuity/queues/chatgpt-main/inbox.jsonl"
OUTBOX_PATH = "continuity/queues/chatgpt-main/outbox.jsonl"

ORIENTATION_CONTRACT = [
    "SINCE_LAST_SEEN",
    "CURRENTLY_RELEVANT",
    "MUST_NOT_ASSUME",
    "MISSING_FOR_THIS_TASK",
]

STOP_CONDITIONS = [
    "required durable seat basis is missing, malformed, or contradictory",
    "working-state cursor coordinate disagrees with the durable cursor",
    "working-state inspected-through coordinate is not retained in the continuity stream",
    "registry working_state_ref no longer points at the seat working state",
    "a requested consequence requires authority not present in the seat",
]


class ChatGPTMainSeatError(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _resolve_commit(repo: Path, source_ref: str) -> str:
    result = _git(repo, "rev-parse", "--verify", f"{source_ref}^{{commit}}")
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ChatGPTMainSeatError(
            f"cannot resolve source ref {source_ref!r}: {detail}"
        )
    commit = result.stdout.decode("utf-8").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ChatGPTMainSeatError("resolved source is not a 40-hex commit")
    return commit


def _read_bytes(repo: Path, commit: str, path: str) -> bytes:
    result = _git(repo, "show", f"{commit}:{path}")
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ChatGPTMainSeatError(
            f"required committed artifact unavailable at {path}: {detail}"
        )
    return result.stdout


def _read_json(repo: Path, commit: str, path: str) -> dict[str, Any]:
    raw = _read_bytes(repo, commit, path)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChatGPTMainSeatError(f"malformed JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ChatGPTMainSeatError(f"expected JSON object at {path}")
    return value


def _read_jsonl(repo: Path, commit: str, path: str) -> list[dict[str, Any]]:
    raw = _read_bytes(repo, commit, path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ChatGPTMainSeatError(f"non-UTF-8 JSONL at {path}") from exc

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ChatGPTMainSeatError(
                f"malformed JSONL at {path}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise ChatGPTMainSeatError(
                f"non-object JSONL record at {path}:{line_number}"
            )
        rows.append(value)
    return rows


def _event_ids(events: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    previous = 0
    for index, event in enumerate(events, 1):
        event_id = str(event.get("event_id"))
        match = re.fullmatch(r"CE-([0-9]{6})", event_id)
        if not match:
            raise ChatGPTMainSeatError(
                f"continuity event {index} has invalid event_id {event_id!r}"
            )
        numeric = int(match.group(1))
        if numeric <= previous:
            raise ChatGPTMainSeatError("continuity event IDs are not strictly increasing")
        previous = numeric
        ids.append(event_id)
    return ids


def _after(ids: list[str], rows: list[dict[str, Any]], coordinate: str) -> list[dict[str, Any]]:
    if coordinate not in ids:
        raise ChatGPTMainSeatError(
            f"continuity coordinate {coordinate!r} is not retained"
        )
    return rows[ids.index(coordinate) + 1 :]


def _through(
    ids: list[str],
    rows: list[dict[str, Any]],
    start_exclusive: str,
    end_inclusive: str,
) -> list[dict[str, Any]]:
    if start_exclusive not in ids or end_inclusive not in ids:
        raise ChatGPTMainSeatError("working-state delta coordinates are not retained")
    start = ids.index(start_exclusive) + 1
    end = ids.index(end_inclusive) + 1
    if end < start:
        raise ChatGPTMainSeatError("working-state inspected-through precedes cursor")
    return rows[start:end]


def _validate_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "schema_version": "chatgpt_main_temporal_seat_manifest_v0",
        "seat_id": SEAT_ID,
        "registry_consumer_id": REGISTRY_CONSUMER_ID,
        "continuity_consumer": CONTINUITY_CONSUMER,
        "cursor_ref": CURSOR_PATH,
        "working_state_ref": WORKING_STATE_PATH,
        "inbox_ref": INBOX_PATH,
        "outbox_ref": OUTBOX_PATH,
        "authority_effect": "NONE_BY_MANIFEST",
        "execution_effect": "NONE_BY_MANIFEST",
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            raise ChatGPTMainSeatError(
                f"manifest {key} mismatch: expected {expected_value!r}, "
                f"got {manifest.get(key)!r}"
            )


def _validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    consumers = registry.get("consumers")
    if not isinstance(consumers, list):
        raise ChatGPTMainSeatError("registry consumers missing")
    matches = [
        row
        for row in consumers
        if isinstance(row, dict)
        and row.get("consumer_id") == REGISTRY_CONSUMER_ID
    ]
    if len(matches) != 1:
        raise ChatGPTMainSeatError("chatgpt-main registry identity is not unique")
    row = matches[0]
    if row.get("cursor_ref") != CURSOR_PATH:
        raise ChatGPTMainSeatError("registry cursor_ref mismatch")
    if row.get("working_state_ref") != WORKING_STATE_PATH:
        raise ChatGPTMainSeatError("registry working_state_ref mismatch")
    return row


def build_wake(repo_root: str | Path, source_ref: str = "HEAD") -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    commit = _resolve_commit(repo, source_ref)

    manifest = _read_json(repo, commit, MANIFEST_PATH)
    cursor = _read_json(repo, commit, CURSOR_PATH)
    working_state = _read_json(repo, commit, WORKING_STATE_PATH)
    registry = _read_json(repo, commit, REGISTRY_PATH)
    events = _read_jsonl(repo, commit, EVENTS_PATH)
    inbox = _read_jsonl(repo, commit, INBOX_PATH)
    outbox = _read_jsonl(repo, commit, OUTBOX_PATH)

    _validate_manifest(manifest)
    registry_row = _validate_registry(registry)

    if cursor.get("consumer") != CONTINUITY_CONSUMER:
        raise ChatGPTMainSeatError("cursor consumer mismatch")
    if cursor.get("cursor_state") != "POSITIONED":
        raise ChatGPTMainSeatError("chatgpt cursor is not POSITIONED")

    if working_state.get("schema_version") != "chatgpt_main_working_state_v0":
        raise ChatGPTMainSeatError("working-state schema mismatch")
    if working_state.get("seat_id") != SEAT_ID:
        raise ChatGPTMainSeatError("working-state seat_id mismatch")

    continuity = working_state.get("continuity")
    if not isinstance(continuity, dict):
        raise ChatGPTMainSeatError("working-state continuity missing")
    if continuity.get("consumer") != CONTINUITY_CONSUMER:
        raise ChatGPTMainSeatError("working-state continuity consumer mismatch")

    cursor_coordinate = cursor.get("last_seen_event_id")
    if continuity.get("cursor_acknowledged_through") != cursor_coordinate:
        raise ChatGPTMainSeatError(
            "working-state acknowledged coordinate disagrees with durable cursor"
        )
    if not isinstance(cursor_coordinate, str):
        raise ChatGPTMainSeatError("chatgpt cursor coordinate must be explicit")

    ids = _event_ids(events)
    head = ids[-1] if ids else None
    if head is None:
        raise ChatGPTMainSeatError("continuity stream is empty")

    inspected_through = continuity.get("delta_inspected_through")
    if not isinstance(inspected_through, str):
        raise ChatGPTMainSeatError("working-state inspected-through coordinate missing")

    unread = _after(ids, events, cursor_coordinate)
    prepared = _through(ids, events, cursor_coordinate, inspected_through)
    newer = _after(ids, events, inspected_through)

    checks = {
        "manifest_valid": True,
        "registry_binding_valid": True,
        "cursor_positioned": True,
        "working_state_cursor_matches": True,
        "inspected_coordinate_retained": inspected_through in ids,
        "cursor_not_advanced_past_working_state": cursor_coordinate != inspected_through,
        "manual_invocation_remains_opaque": (
            registry_row.get("association_basis") == "MANUAL_ASSERTION"
            and registry_row.get("resolution_status") == "OPAQUE"
        ),
        "authority_neutral": (
            manifest.get("authority_effect") == "NONE_BY_MANIFEST"
            and working_state.get("authority_effect") == "NONE_BY_WORKING_STATE"
        ),
    }

    return {
        "schema_version": "chatgpt_main_seat_wake_v0",
        "seat_id": SEAT_ID,
        "source_commit": commit,
        "status": "READY" if all(checks.values()) else "BLOCKED",
        "registry_identity": registry_row,
        "seat_manifest": manifest,
        "cursor": cursor,
        "continuity_head": head,
        "working_state": working_state,
        "unread_continuity_events": unread,
        "working_state_prepared_delta_events": prepared,
        "newer_than_working_state_events": newer,
        "pending_injections": inbox,
        "prior_outputs": outbox,
        "orientation_contract": ORIENTATION_CONTRACT,
        "stop_conditions": STOP_CONDITIONS,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "fresh_occupant_reconstruction_required": True,
        "cursor_advancement_authorized": False,
        "planning_activation_effect": "NONE",
        "authority_effect": "NONE_BY_WAKE",
        "execution_effect": "NONE_BY_WAKE",
        "claim_ceiling": (
            "This wake proves only that the durable ChatGPT-main seat basis can be "
            "reconstructed from committed repository state. It does not prove a live "
            "native ChatGPT invocation binding, semantic reconstruction by a fresh "
            "occupant, cursor acknowledgement, planner-role qualification, authority, "
            "execution, or subjective/model-instance continuity."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--source-ref", default="HEAD")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        wake = build_wake(args.repo, args.source_ref)
    except ChatGPTMainSeatError as exc:
        print(json.dumps({
            "status": "BLOCKED",
            "seat_id": SEAT_ID,
            "error": str(exc),
            "authority_effect": "NONE",
            "execution_effect": "NONE",
        }, sort_keys=True))
        return 2

    if args.output is not None:
        output = args.output
        if not output.is_absolute():
            output = Path(args.repo).resolve() / output
        if output.exists():
            raise SystemExit(f"remove existing {output} first")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(wake, indent=2) + "\n", encoding="utf-8")
        print(f"[OK] wrote {output.relative_to(Path(args.repo).resolve())}")

    print(f"[OK] seat {wake['seat_id']} status {wake['status']}")
    print(f"[OK] cursor {wake['cursor']['last_seen_event_id']}")
    print(f"[OK] continuity head {wake['continuity_head']}")
    print(f"[OK] unread events {len(wake['unread_continuity_events'])}")
    print(
        "[OK] prepared delta events "
        f"{len(wake['working_state_prepared_delta_events'])}"
    )
    print(
        "[OK] newer-than-working-state events "
        f"{len(wake['newer_than_working_state_events'])}"
    )
    print(f"[OK] cursor advancement authorized {wake['cursor_advancement_authorized']}")
    print(f"[OK] all_checks_pass {wake['all_checks_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
