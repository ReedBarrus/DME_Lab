"""Read-only Action Surface v0 projection over committed conductor artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any


PROCESS_DIR = "lab/processes"
EVENT_PATH = "lab/events/events.jsonl"
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


class ActionSurfaceError(RuntimeError):
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
        raise ActionSurfaceError(
            f"cannot resolve action-surface source ref {source_ref!r}: {detail}"
        )
    commit = result.stdout.decode("utf-8").strip().lower()
    if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
        raise ActionSurfaceError(
            f"action-surface source ref did not resolve to exact commit: {source_ref!r}"
        )
    return commit


def _text(repo: Path, commit: str, path: str) -> str | None:
    result = _git(repo, "show", f"{commit}:{path}")
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


def _process_paths(repo: Path, commit: str) -> list[str]:
    result = _git(repo, "ls-tree", "-r", "--name-only", commit, PROCESS_DIR)
    if result.returncode != 0:
        return []
    return sorted(
        line.strip()
        for line in result.stdout.decode("utf-8").splitlines()
        if line.strip().endswith(".json")
    )


def _events(repo: Path, commit: str) -> list[dict[str, Any]]:
    text = _text(repo, commit, EVENT_PATH)
    if text is None:
        return []
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ActionSurfaceError(
                f"malformed conductor event at {EVENT_PATH}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(event, dict):
            raise ActionSurfaceError(
                f"non-object conductor event at {EVENT_PATH}:{line_number}"
            )
        if event.get("event_type") not in EVENT_TYPES:
            raise ActionSurfaceError(
                f"unknown conductor event_type at {EVENT_PATH}:{line_number}: "
                f"{event.get('event_type')!r}"
            )
        rows.append(event)
    return rows


def _initial(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "registered": False,
        "phase": spec["initial_phase"],
        "status": "UNREGISTERED",
        "next_transition": None,
        "blocker": None,
        "pending_role": None,
        "pending_decision": None,
        "last_event_type": None,
    }


def _apply(state: dict[str, Any], event: dict[str, Any]) -> None:
    et = event.get("event_type")
    state["last_event_type"] = et
    if et == "PROCESS_REGISTERED":
        state["registered"] = True
        state["phase"] = event.get("initial_phase", state["phase"])
        state["status"] = "REGISTERED"
    elif et == "TRANSITION_SUCCEEDED":
        state["phase"] = event["to_phase"]
        state["status"] = "ACTIVE"
        state["next_transition"] = None
        state["blocker"] = None
        state["pending_role"] = None
        state["pending_decision"] = None
    elif et == "ROLE_JUDGMENT_REQUIRED":
        state["status"] = "ROLE_JUDGMENT_REQUIRED"
        state["next_transition"] = event.get("transition_id")
        state["pending_role"] = event.get("recipient_role")
    elif et == "HUMAN_DECISION_REQUIRED":
        state["status"] = "HUMAN_DECISION_REQUIRED"
        state["next_transition"] = event.get("transition_id")
        state["pending_decision"] = event.get("decision")
    elif et == "HUMAN_DECISION_RECORDED":
        state["pending_decision"] = None
        if event.get("choice") == "REJECT":
            state["status"] = "STOPPED_BY_HUMAN"
        else:
            state["status"] = "ACTIVE"
            if event.get("to_phase"):
                state["phase"] = event["to_phase"]
    elif et == "BLOCKED":
        state["status"] = "BLOCKED"
        state["next_transition"] = event.get("transition_id")
        state["blocker"] = event.get("blocker")
    elif et == "TRANSITION_FAILED":
        state["status"] = "FAILED"
        state["next_transition"] = event.get("transition_id")
        state["blocker"] = event.get("error")


def _action_for(spec: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    transition = spec.get("transitions", {}).get(state["phase"])
    if transition is None:
        return {
            "eligibility": "UNRESOLVED",
            "transition_id": None,
            "transition_kind": None,
            "to_phase": None,
            "requires_capability": None,
            "recipient_role": None,
            "decision": None,
            "authority_effect": "NONE_BY_ACTION_SURFACE",
            "execution_effect": "NONE_BY_ACTION_SURFACE",
            "authority_required": None,
            "reason": "no declared transition for reconstructed phase",
        }

    kind = transition.get("kind")
    base = {
        "transition_id": transition.get("transition_id"),
        "transition_kind": kind,
        "to_phase": transition.get("to_phase"),
        "requires_capability": transition.get("requires_capability"),
        "recipient_role": transition.get("recipient_role"),
        "decision": transition.get("decision"),
        "authority_effect": "NONE_BY_ACTION_SURFACE",
        "execution_effect": "NONE_BY_ACTION_SURFACE",
    }

    if not state["registered"]:
        return {
            **base,
            "eligibility": "SPEC_ONLY_UNREGISTERED",
            "authority_required": False,
            "reason": (
                "process specification exists, but no PROCESS_REGISTERED event "
                "exists in the committed routing stream"
            ),
        }
    if state["status"] == "ROLE_JUDGMENT_REQUIRED" or kind == "ROLE_JUDGMENT":
        return {
            **base,
            "eligibility": "REQUIRES_ROLE_JUDGMENT",
            "authority_required": False,
            "reason": "declared routing boundary requires role judgment",
        }
    if state["status"] == "HUMAN_DECISION_REQUIRED" or kind == "HUMAN_DECISION":
        return {
            **base,
            "eligibility": "REQUIRES_EXPLICIT_HUMAN_DECISION",
            "authority_required": True,
            "reason": "declared routing boundary requires explicit human decision",
        }
    if state["status"] == "BLOCKED":
        return {
            **base,
            "eligibility": "BLOCKED",
            "authority_required": False,
            "reason": "recorded routing blocker prevents advancement",
        }
    if state["status"] in {"FAILED", "STOPPED_BY_HUMAN"}:
        return {
            **base,
            "eligibility": state["status"],
            "authority_required": False,
            "reason": "routing state is terminally stopped for automatic advancement",
        }
    if kind == "TERMINAL":
        return {
            **base,
            "eligibility": "TERMINAL",
            "authority_required": False,
            "reason": "declared process terminal",
        }
    if kind == "MECHANICAL":
        required = transition.get("requires_capability")
        return {
            **base,
            "eligibility": (
                "MECHANICAL_CAPABILITY_REQUIRED"
                if required
                else "MECHANICAL_ROUTING_AVAILABLE"
            ),
            "authority_required": False,
            "reason": (
                f"declared mechanical transition requires capability {required}"
                if required
                else "declared mechanical routing transition"
            ),
        }
    return {
        **base,
        "eligibility": "UNRESOLVED",
        "authority_required": None,
        "reason": f"unsupported transition kind {kind!r}",
    }


def _load_specs(
    repo: Path,
    source_commit: str,
) -> list[tuple[str, dict[str, Any]]]:
    loaded: list[tuple[str, dict[str, Any]]] = []
    seen: dict[str, str] = {}
    for process_path in _process_paths(repo, source_commit):
        raw = _text(repo, source_commit, process_path)
        if raw is None:
            continue
        try:
            spec = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ActionSurfaceError(
                f"malformed process specification at {process_path}: {exc.msg}"
            ) from exc
        if not isinstance(spec, dict):
            raise ActionSurfaceError(
                f"process specification is not an object: {process_path}"
            )
        required = {"process_id", "initial_phase", "transitions"}
        missing = sorted(required - spec.keys())
        if missing:
            raise ActionSurfaceError(
                f"process specification {process_path} is missing: "
                + ", ".join(missing)
            )
        if not isinstance(spec["process_id"], str) or not spec["process_id"]:
            raise ActionSurfaceError(
                f"process specification has invalid process_id: {process_path}"
            )
        if not isinstance(spec["initial_phase"], str) or not spec["initial_phase"]:
            raise ActionSurfaceError(
                f"process specification has invalid initial_phase: {process_path}"
            )
        if not isinstance(spec["transitions"], dict):
            raise ActionSurfaceError(
                f"process specification transitions are not an object: {process_path}"
            )
        pid = spec["process_id"]
        if pid in seen:
            raise ActionSurfaceError(
                f"duplicate process_id {pid!r}: {seen[pid]} and {process_path}"
            )
        seen[pid] = process_path
        loaded.append((process_path, spec))
    return loaded


def build_action_surfaces(
    repo_root: str | Path,
    source_commit: str,
) -> list[dict[str, Any]]:
    """Project declared next actions without executing or authorizing them."""
    repo = Path(repo_root).resolve()
    exact_commit = _resolve_commit(repo, source_commit)
    all_events = _events(repo, exact_commit)
    loaded_specs = _load_specs(repo, exact_commit)
    known_process_ids = {spec["process_id"] for _, spec in loaded_specs}

    unknown_event_processes = sorted(
        {
            str(event.get("process_id"))
            for event in all_events
            if event.get("process_id") is not None
            and event.get("process_id") not in known_process_ids
        }
    )
    if unknown_event_processes:
        raise ActionSurfaceError(
            "routing events reference process IDs without a unique committed "
            "process specification: "
            + ", ".join(unknown_event_processes)
        )

    surfaces: list[dict[str, Any]] = []
    for process_path, spec in loaded_specs:
        pid = spec["process_id"]
        state = _initial(spec)
        consumed_events = [
            event for event in all_events if event.get("process_id") == pid
        ]
        if consumed_events and consumed_events[0].get("event_type") != "PROCESS_REGISTERED":
            raise ActionSurfaceError(
                f"process {pid} has routing events before PROCESS_REGISTERED"
            )
        for event in consumed_events:
            _apply(state, event)

        surfaces.append(
            {
                "surface_version": "action_surface_v0",
                "process_id": pid,
                "description": spec.get("description"),
                "runtime_registration": (
                    "PRESENT" if state["registered"] else "ABSENT"
                ),
                "phase": state["phase"],
                "routing_status": state["status"],
                "scientific_standing": spec.get(
                    "scientific_standing",
                    {"tracked": False, "value": None},
                ),
                "declared_next_action": _action_for(spec, state),
                "blocker": state["blocker"],
                "pending_role": state["pending_role"],
                "pending_decision": state["pending_decision"],
                "event_count_consumed": len(consumed_events),
                "last_event_type": state["last_event_type"],
                "projection_boundary": {
                    "read_only": True,
                    "creates_authority": False,
                    "performs_execution": False,
                    "selects_action": False,
                    "advances_cursor": False,
                },
                "provenance": {
                    "process_spec_path": process_path,
                    "event_stream_path": EVENT_PATH,
                    "source_commit": exact_commit,
                },
            }
        )

    return sorted(surfaces, key=lambda item: item["process_id"])
