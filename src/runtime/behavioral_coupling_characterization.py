"""Frozen four-pressure behavioral-coupling characterization battery.

This module is a bounded experiment fixture, not an agent or orchestration
framework.  It compiles predeclared schedules, records a pre-execution freeze,
and executes each pressure once through the existing stateless LM Studio
typed-action boundary.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from src.runtime.bounded_consequential_feedback_experiment import (
    BLUE,
    CONDITION_F,
    CONDITION_P,
    FIXED_TASK,
    FROZEN_HIDDEN_STATE_SLOTS,
    INSPECT,
    RED,
    SUBMIT_BLUE,
    SUBMIT_RED,
    run_episode,
)
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    structured_action_response_format,
    structured_action_schema_hash,
)


PROTOCOL_VERSION = "behavioral_coupling_characterization_v0"
BASELINE_AUTHORITY_COMMIT = "a6a8bd5b7c59ed22d3504b3538ffc5e634684483"
BASELINE_WORLD_TRACE = (
    "traces/bounded_consequential_feedback_lm_studio_empirical_world_v0.json"
)
BASELINE_CALL_EVIDENCE = (
    "traces/bounded_consequential_feedback_lm_studio_empirical_calls_v0.json"
)
MODEL_IDENTIFIER = "hermes-3-llama-3.2-3b"
SAMPLING_SETTINGS = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 16}

ALPHA = "ALPHA"
BETA = "BETA"
DEFER = "DEFER"
ASSOCIATED = "ASSOCIATED"
UNASSOCIATED = "UNASSOCIATED"
CURRENT = "CURRENT"
FOREIGN = "FOREIGN"
FIRST = "FIRST"
SECOND = "SECOND"
M1 = "M1"
M2 = "M2"
RB = "RB"
BR = "BR"

ACTION_ENUM_RB = (SUBMIT_RED, SUBMIT_BLUE)
ACTION_ENUM_BR = (SUBMIT_BLUE, SUBMIT_RED)
ACTION_ENUM_RBD = (SUBMIT_RED, SUBMIT_BLUE, DEFER)

P2_MAPPINGS = {
    M1: {ALPHA: RED, BETA: BLUE},
    M2: {ALPHA: BLUE, BETA: RED},
}

P2_TASKS = {
    M1: (
        "Submit the color matching the authoritative target. INSPECT reports "
        "a symbol under this declared mapping: ALPHA -> RED; BETA -> BLUE. "
        "Respond with exactly SUBMIT_RED or SUBMIT_BLUE."
    ),
    M2: (
        "Submit the color matching the authoritative target. INSPECT reports "
        "a symbol under this declared mapping: ALPHA -> BLUE; BETA -> RED. "
        "Respond with exactly SUBMIT_RED or SUBMIT_BLUE."
    ),
}
P3_TASK = (
    "If distinguishing color feedback is present before commitment, submit the "
    "matching color. If no distinguishing color feedback is present before "
    "commitment, select DEFER. Respond with exactly SUBMIT_RED, SUBMIT_BLUE, "
    "or DEFER."
)
P4_TASK = (
    "Submit the color value associated with role CURRENT in the delivered "
    "evidence. Respond with exactly SUBMIT_RED or SUBMIT_BLUE."
)

P1_SCORING = (
    "correct iff the accepted action matches the authoritative hidden color"
)
P2_SCORING = (
    "correct iff the accepted action matches the authoritative target color"
)
P3_SCORING = (
    "F correct iff accepted action matches hidden color; P correct iff accepted "
    "action is DEFER"
)
P4_SCORING = "correct iff the accepted action matches CURRENT color"

PROTOCOL_DOCUMENT_PATH = Path("docs/methods/Consequence_Surface") / (
    "Behavioral_Coupling_Characterization_v0.md"
)
FREEZE_PATH = Path("traces/behavioral_coupling_characterization_freeze_v0.json")
QUALIFICATION_PATH = Path(
    "traces/behavioral_coupling_schema_qualification_v0.json"
)
P1_WORLD_PATH = Path(
    "traces/behavioral_coupling_p1_actuation_prior_world_v0.json"
)
P1_CALLS_PATH = Path(
    "traces/behavioral_coupling_p1_actuation_prior_calls_v0.json"
)
P2_WORLD_PATH = Path(
    "traces/behavioral_coupling_p2_semantic_indirection_world_v0.json"
)
P2_CALLS_PATH = Path(
    "traces/behavioral_coupling_p2_semantic_indirection_calls_v0.json"
)
P3_WORLD_PATH = Path(
    "traces/behavioral_coupling_p3_uncertainty_action_world_v0.json"
)
P3_CALLS_PATH = Path(
    "traces/behavioral_coupling_p3_uncertainty_action_calls_v0.json"
)
P4_WORLD_PATH = Path(
    "traces/behavioral_coupling_p4_association_world_v0.json"
)
P4_CALLS_PATH = Path(
    "traces/behavioral_coupling_p4_association_calls_v0.json"
)
MATRIX_PATH = Path("traces/behavioral_coupling_cross_reference_matrix_v0.json")

EMPIRICAL_PATHS = (
    QUALIFICATION_PATH,
    P1_WORLD_PATH,
    P1_CALLS_PATH,
    P2_WORLD_PATH,
    P2_CALLS_PATH,
    P3_WORLD_PATH,
    P3_CALLS_PATH,
    P4_WORLD_PATH,
    P4_CALLS_PATH,
    MATRIX_PATH,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _write_new_json(path: Path, value: Any) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite frozen evidence: {path}")
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def compile_p1_schedule() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": f"p1-{schema.lower()}-s{slot:02d}-{condition.lower()}",
            "schema_order": schema,
            "slot": slot,
            "hidden_color": hidden,
            "condition": condition,
        }
        for schema in (RB, BR)
        for slot, hidden in enumerate(FROZEN_HIDDEN_STATE_SLOTS, start=1)
        for condition in (CONDITION_F, CONDITION_P)
    ]


def compile_p2_schedule() -> list[dict[str, Any]]:
    slots = (
        (M1, RED),
        (M2, BLUE),
        (M1, BLUE),
        (M2, RED),
        (M2, RED),
        (M1, BLUE),
        (M2, BLUE),
        (M1, RED),
    )
    return [
        {
            "episode_id": f"p2-s{slot:02d}-{condition.lower()}",
            "slot": slot,
            "mapping": mapping,
            "hidden_target_color": hidden,
            "observation_symbol": next(
                symbol
                for symbol, color in P2_MAPPINGS[mapping].items()
                if color == hidden
            ),
            "condition": condition,
        }
        for slot, (mapping, hidden) in enumerate(slots, start=1)
        for condition in (CONDITION_F, CONDITION_P)
    ]


def compile_p3_schedule() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": f"p3-s{slot:02d}-{condition.lower()}",
            "slot": slot,
            "hidden_color": hidden,
            "condition": condition,
        }
        for slot, hidden in enumerate(FROZEN_HIDDEN_STATE_SLOTS, start=1)
        for condition in (CONDITION_F, CONDITION_P)
    ]


def compile_p4_schedule() -> list[dict[str, Any]]:
    situations = (
        (RED, FIRST),
        (BLUE, SECOND),
        (BLUE, FIRST),
        (RED, SECOND),
        (BLUE, SECOND),
        (RED, FIRST),
        (RED, SECOND),
        (BLUE, FIRST),
    )
    return [
        {
            "episode_id": f"p4-s{slot:02d}-{regime.lower()}",
            "slot": slot,
            "regime": regime,
            "current_color": current,
            "foreign_color": BLUE if current == RED else RED,
            "current_position": position,
        }
        for slot, (current, position) in enumerate(situations, start=1)
        for regime in (ASSOCIATED, UNASSOCIATED)
    ]


def schedules() -> dict[str, list[dict[str, Any]]]:
    return {
        "P1": compile_p1_schedule(),
        "P2": compile_p2_schedule(),
        "P3": compile_p3_schedule(),
        "P4": compile_p4_schedule(),
    }


def schedule_hashes() -> dict[str, str]:
    return {pressure: _sha256(schedule) for pressure, schedule in schedules().items()}


def build_protocol_declaration() -> dict[str, Any]:
    frozen_schedules = schedules()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "baseline": {
            "authority_commit": BASELINE_AUTHORITY_COMMIT,
            "world_trace": BASELINE_WORLD_TRACE,
            "call_evidence": BASELINE_CALL_EVIDENCE,
            "observed_counts": {
                "F": {"episodes": 8, "correct": 8, "red": 4, "blue": 4},
                "P": {"episodes": 8, "correct": 4, "red": 8, "blue": 0},
                "actuation_failures": 0,
                "protocol_invalid": 0,
            },
        },
        "common_specimen": {
            "model": MODEL_IDENTIFIER,
            "endpoint": DEFAULT_ENDPOINT,
            "sampling": deepcopy(SAMPLING_SETTINGS),
            "adapter_realization": CONSTRAINED_TYPED_ACTION,
            "episode_requests_are_stateless": True,
            "repository_context_supplied": False,
            "filesystem_exposure_supplied": False,
            "mcp_supplied": False,
            "tools_supplied": False,
            "prior_episode_outcomes_supplied": False,
            "schedule_metadata_supplied": False,
        },
        "pressures": {
            "P1": {
                "question": "whether action-schema enum order alters action selection",
                "intervention": "RB versus BR enum order only",
                "fixed_visible_action_vocabulary": list(ACTION_ENUM_RB),
                "schemas": {
                    RB: structured_action_response_format(ACTION_ENUM_RB),
                    BR: structured_action_response_format(ACTION_ENUM_BR),
                },
                "scoring": P1_SCORING,
                "schedule": frozen_schedules["P1"],
                "may_earn": "literal order-conditioned action and outcome distributions",
                "cannot_earn": "a mechanism for any observed action preference",
            },
            "P2": {
                "question": "whether selection follows a visible mutable symbol-to-color relation",
                "intervention": deepcopy(P2_MAPPINGS),
                "tasks": deepcopy(P2_TASKS),
                "schema": structured_action_response_format(ACTION_ENUM_RB),
                "scoring": P2_SCORING,
                "schedule": frozen_schedules["P2"],
                "may_earn": "mapping-conditioned action and outcome distributions",
                "cannot_earn": "general semantic reasoning",
            },
            "P3": {
                "question": "whether legal noncommitment changes behavior when feedback is absent",
                "intervention": "add terminal DEFER under one evidence-availability rule",
                "task": P3_TASK,
                "schema": structured_action_response_format(ACTION_ENUM_RBD),
                "scoring": P3_SCORING,
                "schedule": frozen_schedules["P3"],
                "may_earn": "availability-conditioned commit/defer distributions",
                "cannot_earn": "rationality, caution, uncertainty awareness, or agency",
            },
            "P4": {
                "question": "whether source-role association changes selection over conflicting values",
                "intervention": "retain value order while removing CURRENT/FOREIGN labels",
                "task": P4_TASK,
                "schema": structured_action_response_format(ACTION_ENUM_RB),
                "scoring": P4_SCORING,
                "schedule": frozen_schedules["P4"],
                "may_earn": "association-conditioned action and outcome distributions",
                "cannot_earn": "general provenance reasoning or irrationality under missing association",
            },
        },
        "pressure_order": ["P1", "P2", "P3", "P4"],
        "common_invalidity": [
            "undeclared hidden information enters policy visibility",
            "observation condition delivered incorrectly",
            "schema or action semantics mutate outside a predeclared intervention",
            "schedule mutates after execution begins",
            "prior episode information reaches the model",
            "malformed output is repaired",
            "semantic translator is introduced",
            "world scoring derives from model narration",
            "unsuccessful episode is omitted",
            "retry replaces an empirical episode",
        ],
        "stop_rule": (
            "qualify only new schemas; then execute P1, close traces, P2, close "
            "traces, P3, close traces, P4, close traces, and stop; any "
            "EXPERIMENT_INVALID stops the remaining battery"
        ),
        "scientific_adjudication": "NOT_PERFORMED",
    }


def battery_protocol_hash() -> str:
    return _sha256(build_protocol_declaration())


def build_freeze(adapter_commit: str) -> dict[str, Any]:
    protocol = build_protocol_declaration()
    hashes = schedule_hashes()
    return {
        "artifact": "behavioral_coupling_characterization_freeze_v0",
        "status": "FROZEN_BEFORE_EMPIRICAL_EXECUTION",
        "protocol_document": PROTOCOL_DOCUMENT_PATH.as_posix(),
        "battery_protocol": protocol,
        "battery_protocol_sha256": _sha256(protocol),
        "schedules": schedules(),
        "schedule_commitments": hashes,
        "action_schema_commitments": {
            RB: structured_action_schema_hash(ACTION_ENUM_RB),
            BR: structured_action_schema_hash(ACTION_ENUM_BR),
            "RBD": structured_action_schema_hash(ACTION_ENUM_RBD),
        },
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "adapter_repository_commit": adapter_commit,
        "empirical_model_calls_made": 0,
    }


def _config() -> LMStudioEndpointConfig:
    return LMStudioEndpointConfig(
        endpoint=DEFAULT_ENDPOINT,
        model_identifier=MODEL_IDENTIFIER,
        sampling_settings=SAMPLING_SETTINGS,
        timeout_seconds=120.0,
    )


def _call_policy(
    adapter: LMStudioConstrainedActionPolicyAdapter,
    task: str,
    visible_history: tuple[dict[str, Any], ...],
) -> tuple[str | None, str | None]:
    try:
        return adapter(task, visible_history), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _terminal_outcome(
    requested_action: str | None,
    policy_error: str | None,
    legal_actions: tuple[str, ...],
) -> tuple[str | None, str | None]:
    if policy_error is not None:
        return None, "POLICY_INVOCATION_FAILURE"
    if requested_action not in legal_actions:
        return None, "MALFORMED_POLICY_OUTPUT"
    return requested_action, None


def _append_event(
    events: list[dict[str, Any]],
    event_type: str,
    *,
    policy_visible: bool,
    payload: Mapping[str, Any],
) -> None:
    events.append(
        {
            "event_index": len(events),
            "event_type": event_type,
            "policy_visible": policy_visible,
            "payload": deepcopy(dict(payload)),
        }
    )


def _visible_history(events: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "event_type": event["event_type"],
            "payload": deepcopy(event["payload"]),
        }
        for event in events
        if event["policy_visible"]
    )


def _finish_request_events(
    events: list[dict[str, Any]],
    requested: str | None,
    policy_error: str | None,
    accepted: str | None,
    failure: str | None,
) -> None:
    request_payload: dict[str, Any] = {"requested_action": requested}
    if policy_error is not None:
        request_payload["policy_error"] = policy_error
    _append_event(
        events,
        "POLICY_ACTION_REQUESTED",
        policy_visible=False,
        payload=request_payload,
    )
    _append_event(
        events,
        "WORLD_ACTION_RECEIPT",
        policy_visible=False,
        payload={
            "requested_action": requested,
            "accepted_action": accepted,
            "accepted": accepted is not None,
            "reason": failure,
        },
    )
    if accepted is not None:
        _append_event(
            events,
            "TERMINAL_COMMITMENT",
            policy_visible=False,
            payload={"accepted_terminal_action": accepted},
        )


def _run_p2_episode(
    spec: Mapping[str, Any],
    adapter: LMStudioConstrainedActionPolicyAdapter,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    hidden = str(spec["hidden_target_color"])
    symbol = str(spec["observation_symbol"])
    condition = str(spec["condition"])
    _append_event(
        events,
        "WORLD_STATE_ESTABLISHED",
        policy_visible=False,
        payload={"hidden_target_color": hidden, "mapping": spec["mapping"]},
    )
    _append_event(
        events,
        "INSPECT_EXECUTED",
        policy_visible=True,
        payload={"action": INSPECT},
    )
    _append_event(
        events,
        "SYMBOL_OBSERVATION_PRODUCED",
        policy_visible=False,
        payload={"symbol": symbol},
    )
    if condition == CONDITION_F:
        _append_event(
            events,
            "SYMBOL_OBSERVATION_DELIVERED",
            policy_visible=True,
            payload={"symbol": symbol},
        )
    else:
        _append_event(
            events,
            "SYMBOL_OBSERVATION_WITHHELD",
            policy_visible=False,
            payload={"symbol_produced": True},
        )
    requested, policy_error = _call_policy(
        adapter,
        P2_TASKS[str(spec["mapping"])],
        _visible_history(events),
    )
    accepted, failure = _terminal_outcome(requested, policy_error, ACTION_ENUM_RB)
    _finish_request_events(events, requested, policy_error, accepted, failure)
    if condition == CONDITION_P and accepted is not None:
        _append_event(
            events,
            "POST_COMMIT_SYMBOL_DELIVERY",
            policy_visible=True,
            payload={"symbol": symbol},
        )
    return {
        **deepcopy(dict(spec)),
        "ordered_events": events,
        "requested_action": requested,
        "accepted_terminal_action": accepted,
        "correct": accepted == f"SUBMIT_{hidden}",
        "valid": True,
        "failure_class": failure,
    }


def _run_p3_episode(
    spec: Mapping[str, Any],
    adapter: LMStudioConstrainedActionPolicyAdapter,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    hidden = str(spec["hidden_color"])
    condition = str(spec["condition"])
    _append_event(
        events,
        "WORLD_STATE_ESTABLISHED",
        policy_visible=False,
        payload={"hidden_color": hidden},
    )
    _append_event(
        events,
        "INSPECT_EXECUTED",
        policy_visible=True,
        payload={"action": INSPECT},
    )
    _append_event(
        events,
        "FEEDBACK_PRODUCED",
        policy_visible=False,
        payload={"feedback": hidden},
    )
    if condition == CONDITION_F:
        _append_event(
            events,
            "FEEDBACK_DELIVERED",
            policy_visible=True,
            payload={"feedback": hidden},
        )
    else:
        _append_event(
            events,
            "FEEDBACK_WITHHELD",
            policy_visible=False,
            payload={"feedback_produced": True},
        )
    requested, policy_error = _call_policy(
        adapter,
        P3_TASK,
        _visible_history(events),
    )
    accepted, failure = _terminal_outcome(requested, policy_error, ACTION_ENUM_RBD)
    _finish_request_events(events, requested, policy_error, accepted, failure)
    if condition == CONDITION_P and accepted is not None:
        _append_event(
            events,
            "POST_COMMIT_FEEDBACK_DELIVERY",
            policy_visible=True,
            payload={"feedback": hidden},
        )
    expected = f"SUBMIT_{hidden}" if condition == CONDITION_F else DEFER
    return {
        **deepcopy(dict(spec)),
        "ordered_events": events,
        "requested_action": requested,
        "accepted_terminal_action": accepted,
        "correct": accepted == expected,
        "valid": True,
        "failure_class": failure,
    }


def _p4_evidence(spec: Mapping[str, Any], *, associated: bool) -> list[dict[str, str]]:
    current = str(spec["current_color"])
    foreign = str(spec["foreign_color"])
    ordered_roles = (
        ((CURRENT, current), (FOREIGN, foreign))
        if spec["current_position"] == FIRST
        else ((FOREIGN, foreign), (CURRENT, current))
    )
    if associated:
        return [{"role": role, "value": value} for role, value in ordered_roles]
    return [{"value": value} for _, value in ordered_roles]


def _run_p4_episode(
    spec: Mapping[str, Any],
    adapter: LMStudioConstrainedActionPolicyAdapter,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    associated = spec["regime"] == ASSOCIATED
    evidence = _p4_evidence(spec, associated=associated)
    _append_event(
        events,
        "WORLD_STATE_ESTABLISHED",
        policy_visible=False,
        payload={
            "current_color": spec["current_color"],
            "foreign_color": spec["foreign_color"],
            "current_position": spec["current_position"],
        },
    )
    _append_event(
        events,
        "INSPECT_EXECUTED",
        policy_visible=True,
        payload={"action": INSPECT},
    )
    _append_event(
        events,
        "CONFLICTING_EVIDENCE_DELIVERED",
        policy_visible=True,
        payload={"evidence": evidence},
    )
    requested, policy_error = _call_policy(
        adapter,
        P4_TASK,
        _visible_history(events),
    )
    accepted, failure = _terminal_outcome(requested, policy_error, ACTION_ENUM_RB)
    _finish_request_events(events, requested, policy_error, accepted, failure)
    return {
        **deepcopy(dict(spec)),
        "delivered_evidence": evidence,
        "ordered_events": events,
        "requested_action": requested,
        "accepted_terminal_action": accepted,
        "correct": accepted == f"SUBMIT_{spec['current_color']}",
        "valid": True,
        "failure_class": failure,
    }


def _associate_call(
    episode_id: str,
    adapter: LMStudioConstrainedActionPolicyAdapter,
    prior_count: int,
) -> dict[str, Any] | None:
    records = adapter.call_records
    if len(records) != prior_count + 1:
        return None
    return {"episode_id": episode_id, **records[-1]}


def _count_actions(episodes: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "episodes": len(episodes),
        "red": sum(e["accepted_terminal_action"] == SUBMIT_RED for e in episodes),
        "blue": sum(e["accepted_terminal_action"] == SUBMIT_BLUE for e in episodes),
        "defer": sum(e["accepted_terminal_action"] == DEFER for e in episodes),
        "correct": sum(bool(e["correct"]) for e in episodes),
        "failures": sum(e["accepted_terminal_action"] is None for e in episodes),
    }


def _summarize_p1(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        schema: {
            condition: _count_actions(
                [
                    e
                    for e in episodes
                    if e["schema_order"] == schema and e["condition"] == condition
                ]
            )
            for condition in (CONDITION_F, CONDITION_P)
        }
        for schema in (RB, BR)
    }


def _summarize_p2(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for mapping in (M1, M2):
        summary[mapping] = {}
        for condition in (CONDITION_F, CONDITION_P):
            selected = [
                e
                for e in episodes
                if e["mapping"] == mapping and e["condition"] == condition
            ]
            summary[mapping][condition] = {
                **_count_actions(selected),
                "symbols": {
                    ALPHA: sum(e["observation_symbol"] == ALPHA for e in selected),
                    BETA: sum(e["observation_symbol"] == BETA for e in selected),
                },
            }
    return summary


def _summarize_p3(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        condition: _count_actions([e for e in episodes if e["condition"] == condition])
        for condition in (CONDITION_F, CONDITION_P)
    }


def _summarize_p4(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for regime in (ASSOCIATED, UNASSOCIATED):
        selected = [e for e in episodes if e["regime"] == regime]
        summary[regime] = {
            **_count_actions(selected),
            "current_first": {
                "episodes": sum(e["current_position"] == FIRST for e in selected),
                "correct": sum(
                    e["current_position"] == FIRST and bool(e["correct"])
                    for e in selected
                ),
            },
            "current_second": {
                "episodes": sum(e["current_position"] == SECOND for e in selected),
                "correct": sum(
                    e["current_position"] == SECOND and bool(e["correct"])
                    for e in selected
                ),
            },
        }
    return summary


def _expected_visible(pressure: str, spec: Mapping[str, Any]) -> dict[str, Any]:
    if pressure == "P1":
        history = [{"event_type": "INSPECT_EXECUTED", "payload": {"action": INSPECT}}]
        if spec["condition"] == CONDITION_F:
            history.append(
                {
                    "event_type": "FEEDBACK_DELIVERED",
                    "payload": {"feedback": spec["hidden_color"]},
                }
            )
        task = FIXED_TASK
        actions = ACTION_ENUM_RB
    elif pressure == "P2":
        history = [{"event_type": "INSPECT_EXECUTED", "payload": {"action": INSPECT}}]
        if spec["condition"] == CONDITION_F:
            history.append(
                {
                    "event_type": "SYMBOL_OBSERVATION_DELIVERED",
                    "payload": {"symbol": spec["observation_symbol"]},
                }
            )
        task = P2_TASKS[str(spec["mapping"])]
        actions = ACTION_ENUM_RB
    elif pressure == "P3":
        history = [{"event_type": "INSPECT_EXECUTED", "payload": {"action": INSPECT}}]
        if spec["condition"] == CONDITION_F:
            history.append(
                {
                    "event_type": "FEEDBACK_DELIVERED",
                    "payload": {"feedback": spec["hidden_color"]},
                }
            )
        task = P3_TASK
        actions = ACTION_ENUM_RBD
    else:
        history = [
            {"event_type": "INSPECT_EXECUTED", "payload": {"action": INSPECT}},
            {
                "event_type": "CONFLICTING_EVIDENCE_DELIVERED",
                "payload": {
                    "evidence": _p4_evidence(
                        spec,
                        associated=spec["regime"] == ASSOCIATED,
                    )
                },
            },
        ]
        task = P4_TASK
        actions = ACTION_ENUM_RB
    return {
        "fixed_task": task,
        "policy_visible_protocol_history": history,
        "legal_action_vocabulary": list(actions),
    }


def _expected_schema_action_enum(
    pressure: str,
    spec: Mapping[str, Any],
) -> tuple[str, ...]:
    if pressure == "P1" and spec["schema_order"] == BR:
        return ACTION_ENUM_BR
    if pressure == "P3":
        return ACTION_ENUM_RBD
    return ACTION_ENUM_RB


def _validate_pressure(
    pressure: str,
    schedule: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
    calls: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    wounds: list[str] = []
    if len(episodes) != len(schedule):
        wounds.append("EPISODE_COUNT_MISMATCH")
    if len(calls) != len(schedule):
        wounds.append("CALL_COUNT_MISMATCH")
    if [e["episode_id"] for e in episodes] != [e["episode_id"] for e in schedule]:
        wounds.append("EPISODE_ORDER_MISMATCH")
    if [c.get("episode_id") for c in calls] != [e["episode_id"] for e in schedule]:
        wounds.append("CALL_ASSOCIATION_MISMATCH")
    for spec, episode, call in zip(schedule, episodes, calls):
        expected_visible = _expected_visible(pressure, spec)
        try:
            actual_visible = json.loads(str(call["serialized_policy_visible_request"]))
        except Exception:
            wounds.append(f"{spec['episode_id']}:UNREADABLE_POLICY_INPUT")
            continue
        if actual_visible != expected_visible:
            wounds.append(f"{spec['episode_id']}:POLICY_VISIBILITY_MISMATCH")
        action_enum = _expected_schema_action_enum(pressure, spec)
        expected_schema = structured_action_response_format(action_enum)
        if call.get("action_schema_hash") != structured_action_schema_hash(action_enum):
            wounds.append(f"{spec['episode_id']}:SCHEMA_MISMATCH")
        if call.get("actuation_constraint") != expected_schema:
            wounds.append(f"{spec['episode_id']}:SCHEMA_CONTENT_MISMATCH")
        if call.get("conversation_state_supplied") is not False:
            wounds.append(f"{spec['episode_id']}:CONVERSATION_STATE_SUPPLIED")
        if call.get("tools_supplied") is not False:
            wounds.append(f"{spec['episode_id']}:TOOLS_SUPPLIED")
        try:
            http_request = json.loads(str(call["serialized_http_request"]))
        except Exception:
            wounds.append(f"{spec['episode_id']}:UNREADABLE_HTTP_REQUEST")
        else:
            if len(http_request.get("messages", [])) != 1:
                wounds.append(f"{spec['episode_id']}:NONSTATELESS_MESSAGE_COUNT")
            if http_request.get("response_format") != expected_schema:
                wounds.append(f"{spec['episode_id']}:HTTP_SCHEMA_MISMATCH")
            if http_request.get("model") != MODEL_IDENTIFIER:
                wounds.append(f"{spec['episode_id']}:MODEL_MISMATCH")
            for key, value in SAMPLING_SETTINGS.items():
                if http_request.get(key) != value:
                    wounds.append(f"{spec['episode_id']}:SAMPLING_MISMATCH:{key}")
            if any(key in http_request for key in ("tools", "integrations", "previous_response_id")):
                wounds.append(f"{spec['episode_id']}:FORBIDDEN_REQUEST_SURFACE")
        if call.get("selected_action") != episode.get("requested_action"):
            wounds.append(f"{spec['episode_id']}:ACTION_BOUNDARY_MISMATCH")
        if episode.get("accepted_terminal_action") != episode.get("requested_action"):
            if episode.get("accepted_terminal_action") is not None:
                wounds.append(f"{spec['episode_id']}:WORLD_RECEIPT_MISMATCH")
        if pressure in {"P1", "P3"}:
            hidden = str(spec["hidden_color"])
        elif pressure == "P2":
            hidden = str(spec["hidden_target_color"])
        else:
            hidden = str(spec["current_color"])
        expected_action = (
            DEFER
            if pressure == "P3" and spec["condition"] == CONDITION_P
            else f"SUBMIT_{hidden}"
        )
        independently_scored = episode.get("accepted_terminal_action") == expected_action
        if episode.get("correct") is not independently_scored:
            wounds.append(f"{spec['episode_id']}:SCORING_MISMATCH")
        if episode.get("valid") is not True:
            wounds.append(f"{spec['episode_id']}:EPISODE_NOT_RETAINED_VALID")
    return {
        "status": "VALID" if not wounds else "EXPERIMENT_INVALID",
        "invalidity_wounds": wounds,
        "wrong_actions_are_behavior_not_invalidity": True,
        "episodes_retained": len(episodes),
        "calls_retained": len(calls),
    }


def _pressure_artifacts(
    pressure: str,
    schedule: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    calls: list[dict[str, Any]],
    summary: dict[str, Any],
    scoring: str,
    adapter_commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validity = _validate_pressure(pressure, schedule, episodes, calls)
    common = {
        "pressure": pressure,
        "protocol_version": PROTOCOL_VERSION,
        "battery_protocol_sha256": battery_protocol_hash(),
        "schedule_commitment": _sha256(schedule),
        "model_identifier": MODEL_IDENTIFIER,
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "adapter_repository_commit": adapter_commit,
        "scoring_rule": scoring,
        "descriptive_summary": summary,
        "validity": validity,
        "scientific_adjudication": "NOT_PERFORMED",
    }
    return (
        {
            "artifact": f"behavioral_coupling_{pressure.lower()}_world_v0",
            "artifact_class": "EMPIRICAL_WORLD_TRACE",
            **deepcopy(common),
            "episodes": episodes,
        },
        {
            "artifact": f"behavioral_coupling_{pressure.lower()}_calls_v0",
            "artifact_class": "EMPIRICAL_MODEL_CALL_EVIDENCE",
            **deepcopy(common),
            "calls": calls,
        },
    )


def _run_p1(adapter_commit: str) -> tuple[dict[str, Any], dict[str, Any]]:
    schedule = compile_p1_schedule()
    episodes: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    adapters = {
        RB: LMStudioConstrainedActionPolicyAdapter(_config(), action_enum=ACTION_ENUM_RB),
        BR: LMStudioConstrainedActionPolicyAdapter(
            _config(),
            action_enum=ACTION_ENUM_BR,
            visible_action_vocabulary=ACTION_ENUM_RB,
        ),
    }
    for spec in schedule:
        adapter = adapters[str(spec["schema_order"])]
        prior = len(adapter.call_records)
        episode = run_episode(
            episode_id=str(spec["episode_id"]),
            hidden_color=str(spec["hidden_color"]),
            condition=str(spec["condition"]),
            policy=adapter,
        )
        episode.update(
            {
                "slot": spec["slot"],
                "schema_order": spec["schema_order"],
                "schema_hash": structured_action_schema_hash(
                    ACTION_ENUM_RB if spec["schema_order"] == RB else ACTION_ENUM_BR
                ),
            }
        )
        call = _associate_call(str(spec["episode_id"]), adapter, prior)
        episodes.append(episode)
        if call is not None:
            calls.append(call)
    return _pressure_artifacts(
        "P1", schedule, episodes, calls, _summarize_p1(episodes), P1_SCORING, adapter_commit
    )


def _run_custom_pressure(
    pressure: str,
    schedule: list[dict[str, Any]],
    action_enum: tuple[str, ...],
    episode_runner: Any,
    summarizer: Any,
    scoring: str,
    adapter_commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    adapter = LMStudioConstrainedActionPolicyAdapter(_config(), action_enum=action_enum)
    episodes: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for spec in schedule:
        prior = len(adapter.call_records)
        episode = episode_runner(spec, adapter)
        call = _associate_call(str(spec["episode_id"]), adapter, prior)
        episodes.append(episode)
        if call is not None:
            calls.append(call)
    return _pressure_artifacts(
        pressure,
        schedule,
        episodes,
        calls,
        summarizer(episodes),
        scoring,
        adapter_commit,
    )


def _qualification_call(
    adapter: LMStudioConstrainedActionPolicyAdapter,
    task: str,
    expected: str,
) -> dict[str, Any]:
    prior = len(adapter.call_records)
    selected, failure = _call_policy(adapter, task, ())
    records = adapter.call_records
    call = records[-1] if len(records) == prior + 1 else None
    return {
        "task": task,
        "expected_action": expected,
        "selected_action": selected,
        "failure": failure,
        "call_evidence": call,
        "passed": selected == expected and call is not None,
    }


def _qualify_new_schemas(adapter_commit: str) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    br_adapter = LMStudioConstrainedActionPolicyAdapter(
        _config(),
        action_enum=ACTION_ENUM_BR,
        visible_action_vocabulary=ACTION_ENUM_RB,
    )
    for action in ACTION_ENUM_BR:
        result = _qualification_call(br_adapter, f"Select {action}.", action)
        result["schema_realization"] = BR
        results.append(result)
    br_passed = all(result["passed"] for result in results)
    rbd_passed = False
    if br_passed:
        rbd_adapter = LMStudioConstrainedActionPolicyAdapter(
            _config(), action_enum=ACTION_ENUM_RBD
        )
        for action in ACTION_ENUM_RBD:
            result = _qualification_call(rbd_adapter, f"Select {action}.", action)
            result["schema_realization"] = "RBD"
            results.append(result)
        rbd_passed = all(
            result["passed"]
            for result in results
            if result["schema_realization"] == "RBD"
        )
    return {
        "artifact": "behavioral_coupling_schema_qualification_v0",
        "artifact_class": "NON_SCIENTIFIC_ACTUATION_QUALIFICATION",
        "adapter_repository_commit": adapter_commit,
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "existing_RB_schema_requalified": False,
        "existing_RB_qualification_evidence": (
            "traces/bounded_consequential_feedback_lm_studio_"
            "constrained_qualification_v0.json"
        ),
        "schema_commitments": {
            BR: structured_action_schema_hash(ACTION_ENUM_BR),
            "RBD": structured_action_schema_hash(ACTION_ENUM_RBD),
        },
        "qualification_results": results,
        "qualification_calls_made": len(results),
        "frozen_schedule_entries_consumed": 0,
        "BR_passed": br_passed,
        "RBD_passed": rbd_passed,
        "qualification_passed": br_passed and rbd_passed,
    }


def _write_pressure_pair(
    world_path: Path,
    calls_path: Path,
    artifacts: tuple[dict[str, Any], dict[str, Any]],
) -> bool:
    world, calls = artifacts
    _write_new_json(world_path, world)
    _write_new_json(calls_path, calls)
    return world["validity"]["status"] == "VALID"


def _cross_reference_matrix(
    p1: Mapping[str, Any],
    p2: Mapping[str, Any],
    p3: Mapping[str, Any],
    p4: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "artifact": "behavioral_coupling_cross_reference_matrix_v0",
        "artifact_class": "DESCRIPTIVE_CROSS_REFERENCE",
        "battery_protocol_sha256": battery_protocol_hash(),
        "rows": [
            {
                "coordinate": "action-order",
                "intervention": "RB versus BR enum order",
                "held_fixed": "world, task, feedback, scoring, model, and sampling",
                "observed_action_distribution": p1["descriptive_summary"],
                "observed_outcome_distribution": {
                    schema: {
                        condition: counts["correct"]
                        for condition, counts in by_condition.items()
                    }
                    for schema, by_condition in p1["descriptive_summary"].items()
                },
            },
            {
                "coordinate": "semantic mapping",
                "intervention": "M1 versus M2 visible symbol-to-color relation",
                "held_fixed": "target colors, action schema, model, sampling, and F/P timing",
                "observed_action_distribution": p2["descriptive_summary"],
                "observed_outcome_distribution": {
                    mapping: {
                        condition: counts["correct"]
                        for condition, counts in by_condition.items()
                    }
                    for mapping, by_condition in p2["descriptive_summary"].items()
                },
            },
            {
                "coordinate": "information availability",
                "intervention": "feedback present versus withheld with DEFER legal",
                "held_fixed": "world distribution, task, schema order, model, and sampling",
                "observed_action_distribution": p3["descriptive_summary"],
                "observed_outcome_distribution": {
                    condition: counts["correct"]
                    for condition, counts in p3["descriptive_summary"].items()
                },
            },
            {
                "coordinate": "provenance/association",
                "intervention": "CURRENT/FOREIGN role labels present versus absent",
                "held_fixed": "two values, value order, target, schema, model, and sampling",
                "observed_action_distribution": p4["descriptive_summary"],
                "observed_outcome_distribution": {
                    regime: counts["correct"]
                    for regime, counts in p4["descriptive_summary"].items()
                },
            },
        ],
        "causal_mechanism_assigned": False,
        "scientific_adjudication": "NOT_PERFORMED",
    }


def execute_battery_once(adapter_commit: str) -> dict[str, Any]:
    if not FREEZE_PATH.exists():
        raise RuntimeError("pre-execution freeze artifact is absent")
    actual_freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    expected_freeze = build_freeze(adapter_commit)
    if actual_freeze != expected_freeze:
        raise RuntimeError("pre-execution freeze does not match current declaration")
    for path in EMPIRICAL_PATHS:
        if path.exists():
            raise RuntimeError(f"one-shot evidence already exists: {path}")

    qualification = _qualify_new_schemas(adapter_commit)
    _write_new_json(QUALIFICATION_PATH, qualification)
    if not qualification["qualification_passed"]:
        return {
            "qualification_passed": False,
            "completed_pressures": [],
            "stopped_before": "P1",
        }

    completed: list[str] = []
    p1 = _run_p1(adapter_commit)
    if not _write_pressure_pair(P1_WORLD_PATH, P1_CALLS_PATH, p1):
        return {"qualification_passed": True, "completed_pressures": completed, "stopped_at": "P1"}
    completed.append("P1")

    p2 = _run_custom_pressure(
        "P2",
        compile_p2_schedule(),
        ACTION_ENUM_RB,
        _run_p2_episode,
        _summarize_p2,
        P2_SCORING,
        adapter_commit,
    )
    if not _write_pressure_pair(P2_WORLD_PATH, P2_CALLS_PATH, p2):
        return {"qualification_passed": True, "completed_pressures": completed, "stopped_at": "P2"}
    completed.append("P2")

    p3 = _run_custom_pressure(
        "P3",
        compile_p3_schedule(),
        ACTION_ENUM_RBD,
        _run_p3_episode,
        _summarize_p3,
        P3_SCORING,
        adapter_commit,
    )
    if not _write_pressure_pair(P3_WORLD_PATH, P3_CALLS_PATH, p3):
        return {"qualification_passed": True, "completed_pressures": completed, "stopped_at": "P3"}
    completed.append("P3")

    p4 = _run_custom_pressure(
        "P4",
        compile_p4_schedule(),
        ACTION_ENUM_RB,
        _run_p4_episode,
        _summarize_p4,
        P4_SCORING,
        adapter_commit,
    )
    if not _write_pressure_pair(P4_WORLD_PATH, P4_CALLS_PATH, p4):
        return {"qualification_passed": True, "completed_pressures": completed, "stopped_at": "P4"}
    completed.append("P4")

    matrix = _cross_reference_matrix(p1[0], p2[0], p3[0], p4[0])
    _write_new_json(MATRIX_PATH, matrix)
    return {
        "qualification_passed": True,
        "completed_pressures": completed,
        "P1": p1[0]["descriptive_summary"],
        "P2": p2[0]["descriptive_summary"],
        "P3": p3[0]["descriptive_summary"],
        "P4": p4[0]["descriptive_summary"],
        "cross_reference_matrix": MATRIX_PATH.as_posix(),
        "scientific_adjudication": "NOT_PERFORMED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-freeze", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--adapter-commit", required=True)
    args = parser.parse_args()
    if args.write_freeze:
        if FREEZE_PATH.exists():
            raise RuntimeError(f"freeze already exists: {FREEZE_PATH}")
        freeze = build_freeze(args.adapter_commit)
        _write_new_json(FREEZE_PATH, freeze)
        print(json.dumps({
            "freeze_path": FREEZE_PATH.as_posix(),
            "battery_protocol_sha256": freeze["battery_protocol_sha256"],
            "schedule_commitments": freeze["schedule_commitments"],
        }, indent=2, sort_keys=True))
        return 0
    result = execute_battery_once(args.adapter_commit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("completed_pressures") == ["P1", "P2", "P3", "P4"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
