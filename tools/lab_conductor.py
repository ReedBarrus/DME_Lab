#!/usr/bin/env python3
"""Minimal DME Lab Conductor v0.

The conductor transports and projects admitted process events. It does not
adjudicate scientific claims, select scientific pressures, invoke roles, replay
external side effects, or infer transitions from prose.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
EVENT_TYPES = {
    "PROCESS_REGISTERED",
    "TRANSITION_REQUESTED",
    "TRANSITION_STARTED",
    "TRANSITION_SUCCEEDED",
    "TRANSITION_FAILED",
    "ROLE_JUDGMENT_REQUIRED",
    "HUMAN_DECISION_REQUIRED",
    "HUMAN_DECISION_RECORDED",
    "BLOCKED",
    "PACKET_ACCEPTED_FOR_TRANSPORT",
}


class ConductorError(RuntimeError):
    pass


@dataclass(frozen=True)
class Paths:
    events: Path
    state: Path
    process_dir: Path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def iter_events(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        event = json.loads(raw)
        if event.get("event_type") not in EVENT_TYPES:
            raise ConductorError(f"unknown event_type at line {n}: {event.get('event_type')!r}")
        rows.append(event)
    return rows


def append_event(path: Path, event: dict[str, Any]) -> None:
    if event.get("event_type") not in EVENT_TYPES:
        raise ConductorError(f"unsupported event_type: {event.get('event_type')!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")


def load_process(process_id: str, process_dir: Path) -> dict[str, Any]:
    matches = []
    for path in process_dir.glob("*.json"):
        obj = _read_json(path)
        if obj.get("process_id") == process_id:
            matches.append((path, obj))
    if len(matches) != 1:
        raise ConductorError(
            f"expected exactly one process definition for {process_id}, found {len(matches)}"
        )
    return matches[0][1]


def initial_process_projection(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "process_id": spec["process_id"],
        "phase": spec["initial_phase"],
        "status": "REGISTERED",
        "next_transition": None,
        "blocker": None,
        "pending_role": None,
        "pending_decision": None,
        "scientific_standing": {"tracked": False, "value": None},
        "last_event_type": "PROCESS_REGISTERED",
    }


def apply_event(proc: dict[str, Any], event: dict[str, Any]) -> None:
    et = event["event_type"]
    proc["last_event_type"] = et
    if et == "TRANSITION_SUCCEEDED":
        proc["phase"] = event["to_phase"]
        proc["status"] = "ACTIVE"
        proc["next_transition"] = None
        proc["blocker"] = None
        proc["pending_role"] = None
        proc["pending_decision"] = None
    elif et == "ROLE_JUDGMENT_REQUIRED":
        proc["status"] = "ROLE_JUDGMENT_REQUIRED"
        proc["next_transition"] = event["transition_id"]
        proc["pending_role"] = event["recipient_role"]
    elif et == "HUMAN_DECISION_REQUIRED":
        proc["status"] = "HUMAN_DECISION_REQUIRED"
        proc["next_transition"] = event["transition_id"]
        proc["pending_decision"] = event["decision"]
    elif et == "HUMAN_DECISION_RECORDED":
        proc["status"] = "ACTIVE"
        proc["pending_decision"] = None
        proc["last_human_decision"] = {
            "decision_id": event["decision_id"],
            "choice": event["choice"],
        }
        if event["choice"] == "APPROVE" and event.get("to_phase"):
            proc["phase"] = event["to_phase"]
        elif event["choice"] == "REJECT":
            proc["status"] = "STOPPED_BY_HUMAN"
    elif et == "BLOCKED":
        proc["status"] = "BLOCKED"
        proc["next_transition"] = event["transition_id"]
        proc["blocker"] = event["blocker"]
    elif et == "TRANSITION_FAILED":
        proc["status"] = "FAILED"
        proc["next_transition"] = event["transition_id"]
        proc["blocker"] = event.get("error")


def replay(paths: Paths) -> dict[str, Any]:
    """Reconstruct routing state only. Never re-perform external consequences."""
    state = {
        "schema_version": "lab_state_v0",
        "projection_kind": "PROCESS_ROUTING",
        "projection_warning": (
            "Process position only. This file is not scientific standing, evidence "
            "adjudication, or universal Lab state."
        ),
        "processes": {},
    }
    for event in iter_events(paths.events):
        pid = event.get("process_id")
        if event["event_type"] == "PROCESS_REGISTERED":
            spec = load_process(pid, paths.process_dir)
            state["processes"][pid] = initial_process_projection(spec)
            continue
        if pid not in state["processes"]:
            raise ConductorError(f"event references unregistered process {pid}")
        apply_event(state["processes"][pid], event)
    _write_json(paths.state, state)
    return state


def ensure_registered(process_id: str, paths: Paths) -> dict[str, Any]:
    state = replay(paths)
    if process_id not in state["processes"]:
        spec = load_process(process_id, paths.process_dir)
        append_event(
            paths.events,
            {
                "event_type": "PROCESS_REGISTERED",
                "process_id": process_id,
                "initial_phase": spec["initial_phase"],
            },
        )
        state = replay(paths)
    return state


def advance(process_id: str, paths: Paths, capabilities: set[str]) -> dict[str, Any]:
    """Advance only mechanically declared transitions; stop at judgment/authority/boundary."""
    state = ensure_registered(process_id, paths)
    while True:
        proc = state["processes"][process_id]
        spec = load_process(process_id, paths.process_dir)
        phase = proc["phase"]
        transition = spec["transitions"].get(phase)
        if transition is None:
            raise ConductorError(f"no declared transition for phase {phase}")

        kind = transition["kind"]
        tid = transition["transition_id"]

        if kind == "TERMINAL":
            proc["status"] = "COMPLETE"
            _write_json(paths.state, state)
            return state

        if proc["status"] in {
            "ROLE_JUDGMENT_REQUIRED",
            "HUMAN_DECISION_REQUIRED",
            "BLOCKED",
            "STOPPED_BY_HUMAN",
            "FAILED",
        }:
            return state

        if kind == "ROLE_JUDGMENT":
            append_event(
                paths.events,
                {
                    "event_type": "ROLE_JUDGMENT_REQUIRED",
                    "process_id": process_id,
                    "transition_id": tid,
                    "recipient_role": transition["recipient_role"],
                },
            )
            return replay(paths)

        if kind == "HUMAN_DECISION":
            append_event(
                paths.events,
                {
                    "event_type": "HUMAN_DECISION_REQUIRED",
                    "process_id": process_id,
                    "transition_id": tid,
                    "decision": transition["decision"],
                },
            )
            return replay(paths)

        if kind != "MECHANICAL":
            raise ConductorError(f"unsupported transition kind {kind!r}")

        required = transition.get("requires_capability")
        if required and required not in capabilities:
            append_event(
                paths.events,
                {
                    "event_type": "BLOCKED",
                    "process_id": process_id,
                    "transition_id": tid,
                    "blocker": {"missing_capability": required},
                },
            )
            return replay(paths)

        append_event(
            paths.events,
            {
                "event_type": "TRANSITION_REQUESTED",
                "process_id": process_id,
                "transition_id": tid,
            },
        )
        append_event(
            paths.events,
            {
                "event_type": "TRANSITION_STARTED",
                "process_id": process_id,
                "transition_id": tid,
            },
        )
        # v0 mechanical transitions are projection-only and have no external side effect.
        append_event(
            paths.events,
            {
                "event_type": "TRANSITION_SUCCEEDED",
                "process_id": process_id,
                "transition_id": tid,
                "to_phase": transition["to_phase"],
            },
        )
        state = replay(paths)


def record_decision(
    process_id: str, decision_id: str, choice: str, paths: Paths
) -> dict[str, Any]:
    state = replay(paths)
    proc = state["processes"].get(process_id)
    if not proc or proc.get("status") != "HUMAN_DECISION_REQUIRED":
        raise ConductorError("no human decision is currently required for this process")
    decision = proc["pending_decision"]
    if decision["decision_id"] != decision_id:
        raise ConductorError("decision_id does not match pending decision")
    if choice not in decision["allowed_choices"]:
        raise ConductorError(f"choice {choice!r} not allowed")
    to_phase = "AUTHORIZED" if choice == "APPROVE" else None
    append_event(
        paths.events,
        {
            "event_type": "HUMAN_DECISION_RECORDED",
            "process_id": process_id,
            "decision_id": decision_id,
            "choice": choice,
            "to_phase": to_phase,
        },
    )
    return replay(paths)


def validate_packet(packet: dict[str, Any]) -> list[str]:
    """Transport checks only; substantive claims remain UNADJUDICATED."""
    required = {
        "schema_version",
        "packet_id",
        "packet_type",
        "process_id",
        "sender_role",
        "recipient_role",
        "basis",
        "requested_transition",
        "authority",
        "status",
        "payload",
        "receipts",
        "claim_status",
    }
    errors = []
    missing = sorted(required - packet.keys())
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if packet.get("schema_version") != "lab_packet_v0":
        errors.append("schema_version must be lab_packet_v0")
    if packet.get("claim_status") != "UNADJUDICATED":
        errors.append("claim_status must remain UNADJUDICATED")
    basis = packet.get("basis")
    if not isinstance(basis, dict) or not basis.get("repo") or not basis.get("ref"):
        errors.append("basis must contain repo and ref")
    authority = packet.get("authority")
    if (
        not isinstance(authority, dict)
        or not {"required", "present"} <= authority.keys()
    ):
        errors.append("authority must contain required and present")
    return errors


def cli() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("replay")

    p_adv = sub.add_parser("advance")
    p_adv.add_argument("process_id")
    p_adv.add_argument("--capability", action="append", default=[])

    p_dec = sub.add_parser("decide")
    p_dec.add_argument("process_id")
    p_dec.add_argument("decision_id")
    p_dec.add_argument("choice")

    p_packet = sub.add_parser("validate-packet")
    p_packet.add_argument("path", type=Path)

    args = parser.parse_args()
    root = args.root.resolve()
    paths = Paths(
        root / "lab/events/events.jsonl",
        root / "lab/state/LAB_STATE_v0.json",
        root / "lab/processes",
    )

    if args.command == "replay":
        result = replay(paths)
    elif args.command == "advance":
        result = advance(args.process_id, paths, set(args.capability))
    elif args.command == "decide":
        result = record_decision(
            args.process_id, args.decision_id, args.choice, paths
        )
    elif args.command == "validate-packet":
        packet = _read_json(args.path)
        errors = validate_packet(packet)
        result = {
            "valid_for_transport": not errors,
            "claim_accepted": False,
            "errors": errors,
        }
    else:
        raise AssertionError(args.command)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
