#!/usr/bin/env python3
"""Tiny file-backed continuity-delta CLI for CONTINUITY-001.

This tool transports recorded activity. It does not adjudicate scientific standing.
Concurrency and multi-writer conflict resolution are explicitly out of scope for v0.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_DIR = ROOT / "continuity"
EVENTS_PATH = CONTINUITY_DIR / "events.jsonl"
CURSORS_DIR = CONTINUITY_DIR / "cursors"
REGISTRY_PATH = CONTINUITY_DIR / "registry.json"
CURSOR_STATES = {"UNINITIALIZED", "POSITIONED"}
BOOTSTRAP_MODES = {"FROM_ORIGIN", "FROM_HEAD", "AFTER_EVENT"}
REGISTRY_CONSUMERS = {"chatgpt-main", "codex-main"}
ACTIVITY_STATES = {"ACTIVE", "DORMANT", "UNKNOWN"}
MANUAL_ASSOCIATION_BASIS = "MANUAL_ASSERTION"
OPAQUE_RESOLUTION_STATUSES = {"OPAQUE", "UNRESOLVED"}


def _load_events() -> list[dict[str, Any]]:
    if not EVENTS_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    for lineno, raw in enumerate(EVENTS_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON in {EVENTS_PATH}:{lineno}: {exc}") from exc
        if not isinstance(event, dict) or "event_id" not in event:
            raise SystemExit(f"invalid event record in {EVENTS_PATH}:{lineno}")
        events.append(event)
    return events


def _cursor_path(consumer: str) -> Path:
    return CURSORS_DIR / f"{consumer}.json"


def _load_cursor(consumer: str) -> dict[str, Any]:
    path = _cursor_path(consumer)
    if not path.exists():
        raise SystemExit(
            f"missing cursor for consumer {consumer!r}: {path}. "
            "Missing consumer continuity state must remain explicit."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("consumer") != consumer:
        raise SystemExit(f"cursor consumer mismatch in {path}")
    state = data.get("cursor_state")
    if state not in CURSOR_STATES:
        raise SystemExit(f"cursor has invalid or missing cursor_state in {path}")
    if state == "UNINITIALIZED" and data.get("last_seen_event_id") is not None:
        raise SystemExit(f"UNINITIALIZED cursor must have null last_seen_event_id in {path}")
    return data


def _events_after(events: list[dict[str, Any]], cursor: dict[str, Any]) -> list[dict[str, Any]]:
    if cursor["cursor_state"] != "POSITIONED":
        raise SystemExit("cannot compute ordinary delta from an UNINITIALIZED cursor")
    last_seen = cursor.get("last_seen_event_id")
    if last_seen is None:
        if cursor.get("bootstrap_mode") == "FROM_ORIGIN":
            return events
        if cursor.get("bootstrap_mode") == "FROM_HEAD":
            # This is the explicit boundary produced when bootstrapping an empty stream.
            return events
        raise SystemExit("POSITIONED null cursor lacks an explicit bootstrap coordinate")
    ids = [event["event_id"] for event in events]
    if last_seen not in ids:
        raise SystemExit(
            f"cursor references unknown event {last_seen!r}; refusing to infer a replacement coordinate"
        )
    return events[ids.index(last_seen) + 1 :]


def _next_event_id(events: list[dict[str, Any]]) -> str:
    maximum = 0
    for event in events:
        event_id = str(event.get("event_id", ""))
        if event_id.startswith("CE-") and event_id[3:].isdigit():
            maximum = max(maximum, int(event_id[3:]))
    return f"CE-{maximum + 1:06d}"


def _load_registry() -> list[dict[str, Any]]:
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing coordination registry: {REGISTRY_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid coordination registry JSON: {exc}") from exc

    consumers = registry.get("consumers") if isinstance(registry, dict) else None
    if not isinstance(consumers, list):
        raise SystemExit("coordination registry must contain a consumers list")
    ids = [entry.get("consumer_id") for entry in consumers if isinstance(entry, dict)]
    if len(consumers) != 2 or len(ids) != 2 or set(ids) != REGISTRY_CONSUMERS:
        raise SystemExit(
            "coordination registry v0 must contain exactly chatgpt-main and codex-main"
        )
    if len(ids) != len(set(ids)):
        raise SystemExit("coordination registry contains duplicate consumer_id values")
    tether_ids = [
        entry.get("tether_id")
        for entry in consumers
        if isinstance(entry, dict) and entry.get("tether_id") is not None
    ]
    if len(tether_ids) != len(set(tether_ids)):
        raise SystemExit("coordination registry contains duplicate tether_id values")
    opaque_refs = [
        entry.get("invocation_ref")
        for entry in consumers
        if isinstance(entry, dict)
        and entry.get("association_basis") == MANUAL_ASSOCIATION_BASIS
        and entry.get("invocation_ref") is not None
    ]
    if len(opaque_refs) != len(set(opaque_refs)):
        raise SystemExit(
            "coordination registry contains duplicate manually asserted invocation_ref values"
        )
    return consumers


def _repo_ref_status(ref: Any, *, absent: str) -> str:
    if ref is None:
        return absent
    if not isinstance(ref, str) or not ref:
        return "INVALID_REF"
    candidate = (ROOT / ref).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return "OUTSIDE_REPOSITORY"
    return "AVAILABLE" if candidate.exists() else "STALE_REF"


def _invocation_ref_status(ref: Any) -> str:
    if ref is None:
        return "NOT_RETAINED"
    if not isinstance(ref, str) or not ref:
        return "INVALID_REF"
    candidate = Path(ref)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        return "AVAILABLE" if candidate.resolve().is_file() else "STALE_REF"
    except OSError:
        return "CHECK_FAILED"


def _invocation_projection(entry: dict[str, Any]) -> dict[str, Any]:
    tether_id = entry.get("tether_id")
    invocation_kind = entry.get("invocation_kind", "NONE")
    invocation_ref = entry.get("invocation_ref")
    association_basis = entry.get("association_basis")
    resolution_status = entry.get("resolution_status")
    failures: list[str] = []

    if association_basis is None:
        if tether_id is not None or resolution_status is not None:
            failures.append(
                "tether_id and resolution_status require an association_basis"
            )
            ref_status = "INVALID_MANUAL_ASSOCIATION"
        else:
            ref_status = _invocation_ref_status(invocation_ref)
    elif association_basis != MANUAL_ASSOCIATION_BASIS:
        failures.append(f"unsupported association_basis: {association_basis!r}")
        ref_status = "INVALID_ASSOCIATION_BASIS"
    else:
        if entry.get("consumer_id") != "chatgpt-main":
            failures.append("manual ChatGPT tether is valid only for chatgpt-main")
        if not isinstance(tether_id, str) or not tether_id:
            failures.append("manual ChatGPT tether requires a non-empty tether_id")
        if invocation_kind != "chatgpt-thread":
            failures.append("manual ChatGPT tether requires invocation_kind chatgpt-thread")
        if not isinstance(invocation_ref, str) or not invocation_ref:
            failures.append("manual ChatGPT tether requires a non-empty invocation_ref")
        if resolution_status not in OPAQUE_RESOLUTION_STATUSES:
            failures.append(
                "manual ChatGPT tether resolution_status must be OPAQUE or UNRESOLVED"
            )
        if tether_id == invocation_ref:
            failures.append("tether_id must not equal invocation_ref")
        ref_status = (
            "INVALID_MANUAL_ASSOCIATION" if failures else resolution_status
        )

    return {
        "tether_id": tether_id,
        "invocation_ref": invocation_ref,
        "invocation_kind": invocation_kind,
        "association_basis": association_basis,
        "resolution_status": resolution_status,
        "invocation_ref_status": ref_status,
        "invocation_observation_failures": failures,
    }


def _registry_cursor_projection(
    entry: dict[str, Any], events: list[dict[str, Any]]
) -> dict[str, Any]:
    projection = {
        "cursor_state": "UNKNOWN",
        "last_seen_event": None,
        "unread_event_count": None,
        "cursor_observation": "CHECK_FAILED",
        "observation_failures": [],
    }
    cursor_ref = entry.get("cursor_ref")
    if not isinstance(cursor_ref, str) or not cursor_ref:
        projection["observation_failures"].append("invalid cursor_ref")
        return projection

    cursor_path = (ROOT / cursor_ref).resolve()
    try:
        cursor_path.relative_to(ROOT.resolve())
    except ValueError:
        projection["observation_failures"].append("cursor_ref escapes repository")
        return projection
    if not cursor_path.exists():
        projection["cursor_observation"] = "MISSING_CURSOR"
        projection["observation_failures"].append(f"missing cursor: {cursor_ref}")
        return projection

    try:
        cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        projection["observation_failures"].append(f"cursor read failed: {exc}")
        return projection
    state = cursor.get("cursor_state")
    projection["cursor_state"] = state if state in CURSOR_STATES else "UNKNOWN"
    projection["last_seen_event"] = cursor.get("last_seen_event_id")
    if state == "UNINITIALIZED":
        projection["cursor_observation"] = "BOOTSTRAP_REQUIRED"
        if cursor.get("last_seen_event_id") is not None:
            projection["observation_failures"].append(
                "UNINITIALIZED cursor has non-null last_seen_event_id"
            )
        return projection
    if state != "POSITIONED":
        projection["observation_failures"].append("invalid or missing cursor_state")
        return projection

    try:
        projection["unread_event_count"] = len(_events_after(events, cursor))
    except SystemExit as exc:
        projection["cursor_observation"] = "STALE_COORDINATE"
        projection["observation_failures"].append(str(exc))
        return projection
    projection["cursor_observation"] = "OK"
    return projection


def _registry_snapshot() -> dict[str, Any]:
    events = _load_events()
    entries = _load_registry()
    consumers = []
    for entry in entries:
        activity_state = entry.get("activity_state")
        if activity_state not in ACTIVITY_STATES:
            activity_state = "UNKNOWN"
        projected = {
            "consumer_id": entry["consumer_id"],
            "role": entry.get("role"),
            "cursor_ref": entry.get("cursor_ref"),
            **_registry_cursor_projection(entry, events),
            **_invocation_projection(entry),
            "activity_state": activity_state,
            "working_state_ref": entry.get("working_state_ref"),
            "working_state_ref_status": _repo_ref_status(
                entry.get("working_state_ref"), absent="NOT_RETAINED"
            ),
        }
        consumers.append(projected)
    return {
        "continuity_head": events[-1]["event_id"] if events else None,
        "consumers": consumers,
        "authority_changed": False,
        "standing_changed": False,
    }


def command_delta(args: argparse.Namespace) -> None:
    events = _load_events()
    cursor = _load_cursor(args.consumer)
    if cursor["cursor_state"] == "UNINITIALIZED":
        head = events[-1]["event_id"] if events else None
        print(json.dumps({
            "status": "BOOTSTRAP_REQUIRED",
            "consumer": args.consumer,
            "cursor_state": "UNINITIALIZED",
            "current_stream_head": head,
            "legal_bootstrap_modes": [
                "FROM_ORIGIN", "FROM_HEAD", "AFTER_EVENT <event_id>"
            ],
        }, ensure_ascii=False, sort_keys=True))
        return
    delta = _events_after(events, cursor)
    for event in delta:
        print(json.dumps(event, ensure_ascii=False, sort_keys=True))


def command_registry(args: argparse.Namespace) -> None:
    del args
    print(json.dumps(_registry_snapshot(), ensure_ascii=False, sort_keys=True))


def command_bootstrap(args: argparse.Namespace) -> None:
    events = _load_events()
    cursor = _load_cursor(args.consumer)
    if cursor["cursor_state"] != "UNINITIALIZED":
        raise SystemExit("cursor is already POSITIONED; refusing to replace its coordinate")

    mode = args.mode
    if mode not in BOOTSTRAP_MODES:
        raise SystemExit(f"invalid bootstrap mode {mode!r}")
    if mode == "AFTER_EVENT":
        if not args.event_id:
            raise SystemExit("AFTER_EVENT requires --event-id")
        known_ids = {event["event_id"] for event in events}
        if args.event_id not in known_ids:
            raise SystemExit(f"cannot bootstrap after unknown event {args.event_id!r}")
        coordinate = args.event_id
    elif args.event_id is not None:
        raise SystemExit("--event-id is valid only with AFTER_EVENT")
    elif mode == "FROM_HEAD":
        coordinate = events[-1]["event_id"] if events else None
    else:
        coordinate = None

    positioned = {
        "consumer": args.consumer,
        "cursor_state": "POSITIONED",
        "last_seen_event_id": coordinate,
        "bootstrap_mode": mode,
    }
    _cursor_path(args.consumer).write_text(
        json.dumps(positioned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(positioned, ensure_ascii=False, sort_keys=True))


def command_append(args: argparse.Namespace) -> None:
    events = _load_events()
    event = {
        "event_id": _next_event_id(events),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "actor": args.actor,
        "surface": args.surface,
        "kind": args.kind,
        "summary": args.summary,
        "refs": args.ref or [],
        "parent_refs": args.parent or [],
        "reported_standing_delta": args.reported_standing_delta,
        "reported_frontier_delta": args.reported_frontier_delta,
    }
    CONTINUITY_DIR.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps(event, ensure_ascii=False, sort_keys=True))


def command_ack(args: argparse.Namespace) -> None:
    events = _load_events()
    cursor = _load_cursor(args.consumer)
    if cursor["cursor_state"] != "POSITIONED":
        raise SystemExit("cursor must be bootstrapped before it can be advanced")
    if not events:
        raise SystemExit("cannot advance cursor: continuity stream is empty")

    target = events[-1]["event_id"] if args.event_id == "latest" else args.event_id
    known_ids = [event["event_id"] for event in events]
    if target not in known_ids:
        raise SystemExit(f"cannot advance cursor to unknown event {target!r}")

    current = cursor.get("last_seen_event_id")
    current_index = -1
    if current is not None:
        if current not in known_ids:
            raise SystemExit(
                f"cursor references unknown event {current!r}; refusing to infer a replacement coordinate"
            )
        current_index = known_ids.index(current)
        if known_ids.index(target) < current_index:
            raise SystemExit(
                f"cannot acknowledge backward from {current!r} to {target!r}; "
                "acknowledgement is monotonic"
            )

    next_index = current_index + 1
    if next_index >= len(known_ids):
        raise SystemExit("cannot acknowledge: no unread event exists after the current cursor")
    expected = known_ids[next_index]
    if target != expected:
        raise SystemExit(
            f"cannot acknowledge noncontiguous event {target!r}; "
            f"the immediate next unread event is {expected!r}"
        )

    cursor["last_seen_event_id"] = target
    _cursor_path(args.consumer).write_text(
        json.dumps(cursor, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(cursor, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DME_Lab continuity-delta v0")
    sub = parser.add_subparsers(dest="command", required=True)

    delta = sub.add_parser("delta", help="print events after a consumer's cursor")
    delta.add_argument("--consumer", required=True)
    delta.set_defaults(func=command_delta)

    registry = sub.add_parser(
        "registry", help="print the derived two-consumer coordination snapshot"
    )
    registry.set_defaults(func=command_registry)

    bootstrap = sub.add_parser(
        "bootstrap", help="explicitly establish a fresh consumer stream coordinate"
    )
    bootstrap.add_argument("--consumer", required=True)
    bootstrap.add_argument("--mode", required=True, choices=sorted(BOOTSTRAP_MODES))
    bootstrap.add_argument("--event-id")
    bootstrap.set_defaults(func=command_bootstrap)

    append = sub.add_parser("append", help="append one recorded activity event")
    append.add_argument("--actor", required=True)
    append.add_argument("--surface", required=True)
    append.add_argument("--kind", required=True)
    append.add_argument("--summary", required=True)
    append.add_argument("--ref", action="append")
    append.add_argument("--parent", action="append")
    append.add_argument("--reported-standing-delta")
    append.add_argument("--reported-frontier-delta")
    append.set_defaults(func=command_append)

    ack = sub.add_parser("ack", help="advance a consumer cursor after delta consumption")
    ack.add_argument("--consumer", required=True)
    ack.add_argument("--event-id", default="latest")
    ack.set_defaults(func=command_ack)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
