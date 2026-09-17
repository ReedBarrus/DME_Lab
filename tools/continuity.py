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
    return data


def _events_after(events: list[dict[str, Any]], last_seen: str | None) -> list[dict[str, Any]]:
    if last_seen is None:
        return events
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


def command_delta(args: argparse.Namespace) -> None:
    events = _load_events()
    cursor = _load_cursor(args.consumer)
    delta = _events_after(events, cursor.get("last_seen_event_id"))
    for event in delta:
        print(json.dumps(event, ensure_ascii=False, sort_keys=True))


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
    if not events:
        raise SystemExit("cannot advance cursor: continuity stream is empty")

    target = events[-1]["event_id"] if args.event_id == "latest" else args.event_id
    known_ids = {event["event_id"] for event in events}
    if target not in known_ids:
        raise SystemExit(f"cannot advance cursor to unknown event {target!r}")

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
