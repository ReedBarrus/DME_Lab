#!/usr/bin/env python3
"""LABBOIB Temporal Seat v0.

Reconstructs one bounded temporal seat from exact durable Git state.

WAKE != ACK
WAKE != AUTHORITY
WAKE != EXECUTION
MODEL INSTANCE != SEAT
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SEAT_ID = "LABBOIB"
CONSUMER_ID = "labboib"

MANIFEST_PATH = "continuity/seats/labboib.json"
CURSOR_PATH = "continuity/cursors/labboib.json"
WORKING_STATE_PATH = "continuity/current_state/labboib_working_state_v0.json"
EVENTS_PATH = "continuity/events.jsonl"
INBOX_PATH = "continuity/queues/labboib/inbox.jsonl"
OUTBOX_PATH = "continuity/queues/labboib/outbox.jsonl"

ORIENTATION_CONTRACT = [
    "SINCE_LAST_SEEN",
    "CURRENTLY_RELEVANT",
    "MUST_NOT_ASSUME",
    "MISSING_FOR_THIS_TASK",
]

ALLOWED_OUTPUTS = [
    "STATUS",
    "HANDOFF",
    "REVIEW_REQUEST",
    "ACTION_REQUEST",
    "WAKE_RECEIPT",
]

STOP_CONDITIONS = [
    "explicit human authority is required for a consequential action",
    "required durable basis is missing, stale, malformed, or contradictory",
    "a role judgment or independent review is required",
    "the requested effect exceeds the seat manifest",
    "continuity cannot be reconstructed from the seat's own coordinate",
]

INJECTION_KINDS = {
    "MESSAGE",
    "PRIORITY",
    "PACKET_REF",
    "ACTION_REQUEST",
    "AUTHORITY_OBJECT_REF",
}

OUTPUT_KINDS = set(ALLOWED_OUTPUTS)


class TemporalSeatError(RuntimeError):
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
        raise TemporalSeatError(
            f"cannot resolve source ref {source_ref!r} to an exact commit: {detail}"
        )
    commit = result.stdout.decode("utf-8").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise TemporalSeatError(
            f"source ref {source_ref!r} did not resolve to a 40-hex commit"
        )
    return commit


def _read_committed_bytes(repo: Path, commit: str, path: str) -> bytes:
    result = _git(repo, "show", f"{commit}:{path}")
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise TemporalSeatError(
            f"required committed seat artifact unavailable at {path}: {detail}"
        )
    return result.stdout


def _read_committed_json(repo: Path, commit: str, path: str) -> dict[str, Any]:
    raw = _read_committed_bytes(repo, commit, path)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TemporalSeatError(f"malformed JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TemporalSeatError(f"expected JSON object at {path}")
    return value


def _read_committed_jsonl(repo: Path, commit: str, path: str) -> list[dict[str, Any]]:
    raw = _read_committed_bytes(repo, commit, path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TemporalSeatError(f"non-UTF-8 JSONL at {path}: {exc}") from exc

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TemporalSeatError(
                f"malformed JSONL at {path}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise TemporalSeatError(
                f"non-object JSONL record at {path}:{line_number}"
            )
        rows.append(value)
    return rows


def _validate_manifest(manifest: dict[str, Any]) -> None:
    expected = {
        "schema_version": "temporal_seat_manifest_v0",
        "seat_id": SEAT_ID,
        "consumer_id": CONSUMER_ID,
        "cursor_ref": CURSOR_PATH,
        "working_state_ref": WORKING_STATE_PATH,
        "inbox_ref": INBOX_PATH,
        "outbox_ref": OUTBOX_PATH,
        "authority_effect": "NONE_BY_MANIFEST",
        "execution_effect": "NONE_BY_MANIFEST",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise TemporalSeatError(
                f"manifest {key} mismatch: expected {value!r}, got {manifest.get(key)!r}"
            )

    if manifest.get("seat_class") != "TEMPORAL_REENTRY_SEAT_CANDIDATE":
        raise TemporalSeatError("unexpected seat_class")

    trigger = manifest.get("trigger")
    if not isinstance(trigger, dict) or trigger.get("state") not in {"UNBOUND", "BOUND"}:
        raise TemporalSeatError("manifest trigger state is invalid")

    occupant = manifest.get("occupant")
    if not isinstance(occupant, dict) or occupant.get("binding") not in {"UNBOUND", "BOUND"}:
        raise TemporalSeatError("manifest occupant binding is invalid")


def _validate_working_state(state: dict[str, Any]) -> None:
    if state.get("schema_version") != "temporal_seat_working_state_v0":
        raise TemporalSeatError("working state schema_version mismatch")
    if state.get("seat_id") != SEAT_ID:
        raise TemporalSeatError("working state seat_id mismatch")

    continuity = state.get("continuity")
    if not isinstance(continuity, dict) or continuity.get("consumer") != CONSUMER_ID:
        raise TemporalSeatError("working state continuity consumer mismatch")

    authority = state.get("authority")
    if not isinstance(authority, dict) or authority.get("standing") != "NONE":
        raise TemporalSeatError(
            "Temporal Seat v0 requires working-state authority standing NONE"
        )


def _event_ids(events: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    previous = 0
    for index, event in enumerate(events, 1):
        event_id = event.get("event_id")
        match = re.fullmatch(r"CE-([0-9]{6})", str(event_id))
        if not match:
            raise TemporalSeatError(
                f"continuity event {index} has invalid event_id {event_id!r}"
            )
        numeric = int(match.group(1))
        if numeric <= previous:
            raise TemporalSeatError("continuity event IDs are not strictly increasing")
        previous = numeric
        ids.append(str(event_id))
    return ids


def _continuity_delta(
    cursor: dict[str, Any],
    events: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]], str | None]:
    if cursor.get("consumer") != CONSUMER_ID:
        raise TemporalSeatError("LABBOIB cursor consumer mismatch")

    ids = _event_ids(events)
    head = ids[-1] if ids else None
    cursor_state = cursor.get("cursor_state")

    if cursor_state == "UNINITIALIZED":
        return "BOOTSTRAP_REQUIRED", [], head

    if cursor_state != "POSITIONED":
        raise TemporalSeatError(f"unsupported cursor_state {cursor_state!r}")

    coordinate = cursor.get("last_seen_event_id")
    bootstrap_mode = cursor.get("bootstrap_mode")

    if coordinate is None:
        if bootstrap_mode == "FROM_ORIGIN":
            return "READY", events, head
        if bootstrap_mode == "FROM_HEAD" and not events:
            return "READY", [], head
        raise TemporalSeatError(
            "POSITIONED null cursor is valid only for FROM_ORIGIN or empty FROM_HEAD"
        )

    if coordinate not in ids:
        raise TemporalSeatError(
            f"cursor coordinate {coordinate!r} is not retained in continuity stream"
        )
    index = ids.index(coordinate)
    return "READY", events[index + 1 :], head


def _validate_injection(injection: dict[str, Any], previous: int) -> int:
    if injection.get("schema_version") != "temporal_seat_injection_v0":
        raise TemporalSeatError("inbox contains non-v0 injection")
    if injection.get("target_seat") != SEAT_ID:
        raise TemporalSeatError("inbox injection targets another seat")
    match = re.fullmatch(r"LI-([0-9]{6})", str(injection.get("injection_id")))
    if not match:
        raise TemporalSeatError("inbox injection has invalid injection_id")
    numeric = int(match.group(1))
    if numeric <= previous:
        raise TemporalSeatError("inbox injection IDs are not strictly increasing")
    if injection.get("kind") not in INJECTION_KINDS:
        raise TemporalSeatError("inbox injection has unsupported kind")
    authority = injection.get("authority")
    if not isinstance(authority, dict):
        raise TemporalSeatError("inbox injection authority envelope missing")
    if authority.get("claimed") is True and not authority.get("authority_ref"):
        raise TemporalSeatError(
            "authority-claiming injection requires an authority_ref"
        )
    return numeric


def _pending_injections(
    state: dict[str, Any],
    inbox: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    previous = 0
    ids: list[str] = []
    for injection in inbox:
        previous = _validate_injection(injection, previous)
        ids.append(str(injection["injection_id"]))

    coordinate = (
        state.get("injection_coordinate", {})
        .get("last_consumed_injection_id")
    )
    if coordinate is None:
        return inbox
    if coordinate not in ids:
        raise TemporalSeatError(
            f"injection coordinate {coordinate!r} is not retained in LABBOIB inbox"
        )
    return inbox[ids.index(coordinate) + 1 :]


def build_wake(repo_root: str | Path, source_ref: str = "HEAD") -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    commit = _resolve_commit(repo, source_ref)

    manifest = _read_committed_json(repo, commit, MANIFEST_PATH)
    cursor = _read_committed_json(repo, commit, CURSOR_PATH)
    working_state = _read_committed_json(repo, commit, WORKING_STATE_PATH)
    events = _read_committed_jsonl(repo, commit, EVENTS_PATH)
    inbox = _read_committed_jsonl(repo, commit, INBOX_PATH)
    _read_committed_jsonl(repo, commit, OUTBOX_PATH)

    _validate_manifest(manifest)
    _validate_working_state(working_state)

    status, unread, head = _continuity_delta(cursor, events)
    pending = _pending_injections(working_state, inbox)

    synchronized = working_state["continuity"].get("synchronized_through")
    cursor_coordinate = cursor.get("last_seen_event_id")
    if synchronized != cursor_coordinate:
        raise TemporalSeatError(
            "working-state continuity coordinate disagrees with LABBOIB cursor"
        )

    return {
        "schema_version": "temporal_seat_wake_v0",
        "seat_id": SEAT_ID,
        "source_commit": commit,
        "status": status,
        "seat_manifest": manifest,
        "cursor": cursor,
        "continuity_head": head,
        "unread_continuity_events": unread,
        "working_state": working_state,
        "pending_injections": pending,
        "orientation_contract": ORIENTATION_CONTRACT,
        "allowed_outputs": ALLOWED_OUTPUTS,
        "stop_conditions": STOP_CONDITIONS,
        "authority_effect": "NONE_BY_WAKE",
        "execution_effect": "NONE_BY_WAKE",
    }


def _next_queue_id(rows: list[dict[str, Any]], prefix: str) -> str:
    maximum = 0
    pattern = re.compile(rf"{re.escape(prefix)}-([0-9]{{6}})")
    for row in rows:
        value = row.get("injection_id") if prefix == "LI" else row.get("output_id")
        match = pattern.fullmatch(str(value))
        if not match:
            raise TemporalSeatError(f"malformed {prefix} queue identity {value!r}")
        maximum = max(maximum, int(match.group(1)))
    return f"{prefix}-{maximum + 1:06d}"


def _append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def append_injection(
    repo_root: str | Path,
    *,
    kind: str,
    body: str,
    created_by: str,
    refs: list[str],
    authority_ref: str | None,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    inbox_path = repo / INBOX_PATH
    if kind not in INJECTION_KINDS:
        raise TemporalSeatError(f"unsupported injection kind {kind!r}")

    existing: list[dict[str, Any]] = []
    if inbox_path.exists():
        for line_number, line in enumerate(
            inbox_path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TemporalSeatError(
                    f"malformed local inbox at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(value, dict):
                raise TemporalSeatError("local inbox contains non-object record")
            existing.append(value)

    previous = 0
    for row in existing:
        previous = _validate_injection(row, previous)

    injection = {
        "schema_version": "temporal_seat_injection_v0",
        "injection_id": _next_queue_id(existing, "LI"),
        "target_seat": SEAT_ID,
        "kind": kind,
        "body": body,
        "refs": refs,
        "authority": {
            "claimed": authority_ref is not None,
            "authority_ref": authority_ref,
        },
        "created_by": created_by,
    }
    _validate_injection(injection, previous)
    _append_jsonl(inbox_path, injection)
    return injection


def validate_output(output: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "output_id",
        "seat_id",
        "output_kind",
        "basis_commit",
        "consumed_continuity_through",
        "consumed_injection_through",
        "summary",
        "refs",
        "authority_effect",
        "execution_effect",
    }
    missing = sorted(required - output.keys())
    if missing:
        raise TemporalSeatError("output missing fields: " + ", ".join(missing))
    if output["schema_version"] != "temporal_seat_output_v0":
        raise TemporalSeatError("output schema_version mismatch")
    if output["seat_id"] != SEAT_ID:
        raise TemporalSeatError("output seat_id mismatch")
    if output["output_kind"] not in OUTPUT_KINDS:
        raise TemporalSeatError("output kind unsupported")
    if not re.fullmatch(r"LO-[0-9]{6}", str(output["output_id"])):
        raise TemporalSeatError("output_id malformed")
    if not re.fullmatch(r"[0-9a-f]{40}", str(output["basis_commit"])):
        raise TemporalSeatError("output basis_commit malformed")
    if output["authority_effect"] != "NONE_BY_OUTPUT":
        raise TemporalSeatError("output cannot create authority")
    if output["execution_effect"] != "NONE_BY_OUTPUT":
        raise TemporalSeatError("output cannot create execution effect")


def append_output(repo_root: str | Path, output: dict[str, Any]) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    outbox_path = repo / OUTBOX_PATH
    existing: list[dict[str, Any]] = []
    if outbox_path.exists():
        for line_number, line in enumerate(
            outbox_path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TemporalSeatError(
                    f"local outbox record {line_number} is not an object"
                )
            validate_output(value)
            existing.append(value)

    validate_output(output)
    expected_id = _next_queue_id(existing, "LO")
    if output["output_id"] != expected_id:
        raise TemporalSeatError(
            f"output_id must be the next queue identity {expected_id}"
        )
    _append_jsonl(outbox_path, output)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    p_wake = sub.add_parser("wake")
    p_wake.add_argument("--source-ref", default="HEAD")

    p_inject = sub.add_parser("inject")
    p_inject.add_argument("--kind", required=True, choices=sorted(INJECTION_KINDS))
    p_inject.add_argument("--body", required=True)
    p_inject.add_argument("--created-by", required=True)
    p_inject.add_argument("--ref", action="append", default=[])
    p_inject.add_argument("--authority-ref")

    p_output = sub.add_parser("append-output")
    p_output.add_argument("path", type=Path)

    args = parser.parse_args(argv)

    try:
        if args.command == "wake":
            result = build_wake(args.repo, args.source_ref)
        elif args.command == "inject":
            result = append_injection(
                args.repo,
                kind=args.kind,
                body=args.body,
                created_by=args.created_by,
                refs=list(args.ref),
                authority_ref=args.authority_ref,
            )
        elif args.command == "append-output":
            output = json.loads(args.path.read_text(encoding="utf-8"))
            if not isinstance(output, dict):
                raise TemporalSeatError("output file must contain a JSON object")
            result = append_output(args.repo, output)
        else:
            raise AssertionError(args.command)
    except TemporalSeatError as exc:
        print(json.dumps({
            "status": "BLOCKED",
            "seat_id": SEAT_ID,
            "error": str(exc),
            "authority_effect": "NONE",
            "execution_effect": "NONE",
        }, sort_keys=True))
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
