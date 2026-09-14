"""Frozen latent-world-binding versus precommitment-observability pressure."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from src.runtime.behavioral_coupling_action_delexicalization import (
    ACT_A,
    ACT_B,
    ACTION_ENUM,
    MODEL_IDENTIFIER,
    SAMPLING_SETTINGS,
    action_schema_hash,
    load_validated_qualification,
)
from src.runtime.bounded_consequential_feedback_experiment import BLUE, RED
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    structured_action_response_format,
)


PROTOCOL_VERSION = "behavioral_coupling_binding_observability_v0"
REPOSITORY_AUTHORITY_COMMIT = "6bf358389ddbb85b7e6c56062f8d339686824859"
ADAPTER_AUTHORITY_COMMIT = "d60ce2044fb2215e58eec74de8e311ba42765bc0"

C0 = "C0"
C1 = "C1"
EARLY = "EARLY"
LATE = "LATE"
WORLD_CONTRACTS = {
    C0: {ACT_A: RED, ACT_B: BLUE},
    C1: {ACT_A: BLUE, ACT_B: RED},
}
CONTRACTS = (C0, C1)
DISCLOSURE_TIMINGS = (EARLY, LATE)
VISIBLE_TARGET = RED
REPETITIONS = 4

FIXED_TASK = (
    "Select the legal action whose authoritative world consequence is RED. "
    "ACT_A and ACT_B are the only legal actions. The world uses one fixed "
    "bijection between ACT_A / ACT_B and RED / BLUE; exactly one legal action "
    "produces RED. Respond with exactly ACT_A or ACT_B."
)
SCORING_RULE = (
    "authoritative produced color is obtained by applying the active hidden "
    "world contract to the committed ACT token; success iff produced color is RED"
)

PRIOR_PROTOCOL = (
    "docs/methods/Consequence_Surface/"
    "Behavioral_Coupling_Action_Delexicalization_v0.md"
)
PRIOR_FREEZE = "traces/behavioral_coupling_action_delexicalization_freeze_v0.json"
QUALIFIED_ACTION_SURFACE = (
    "traces/behavioral_coupling_action_delexicalization_qualification_v0.json"
)
PRIOR_WORLD = "traces/behavioral_coupling_action_delexicalization_world_v0.json"
PRIOR_CALLS = "traces/behavioral_coupling_action_delexicalization_calls_v0.json"

PROTOCOL_PATH = Path("docs/methods/Consequence_Surface") / (
    "Behavioral_Coupling_Binding_Observability_v0.md"
)
FREEZE_PATH = Path(
    "traces/behavioral_coupling_binding_observability_freeze_v0.json"
)
WORLD_PATH = Path(
    "traces/behavioral_coupling_binding_observability_world_v0.json"
)
CALLS_PATH = Path(
    "traces/behavioral_coupling_binding_observability_calls_v0.json"
)
OUTPUT_PATHS = (WORLD_PATH, CALLS_PATH)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _text_sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def binding_rows(contract: str) -> list[dict[str, str]]:
    if contract not in WORLD_CONTRACTS:
        raise ValueError(f"unknown world contract: {contract}")
    return [
        {"action": action, "produced_color": WORLD_CONTRACTS[contract][action]}
        for action in ACTION_ENUM
    ]


def serialized_binding_text(contract: str) -> str:
    return "; ".join(
        f"{row['action']} -> {row['produced_color']}"
        for row in binding_rows(contract)
    )


def policy_visible_request(contract: str, disclosure_timing: str) -> dict[str, Any]:
    if contract not in CONTRACTS:
        raise ValueError(f"unknown world contract: {contract}")
    if disclosure_timing not in DISCLOSURE_TIMINGS:
        raise ValueError(f"unknown disclosure timing: {disclosure_timing}")
    history: list[dict[str, Any]] = []
    if disclosure_timing == EARLY:
        history.append(
            {
                "event_type": "BINDING_DISCLOSED",
                "payload": {
                    "binding_rows": binding_rows(contract),
                    "serialized_binding_text": serialized_binding_text(contract),
                },
            }
        )
    return {
        "fixed_task": FIXED_TASK,
        "policy_visible_protocol_history": history,
        "legal_action_vocabulary": list(ACTION_ENUM),
    }


def precommitment_serialization(contract: str, disclosure_timing: str) -> str:
    return _canonical_json(policy_visible_request(contract, disclosure_timing))


def precommitment_input_hash(contract: str, disclosure_timing: str) -> str:
    return _text_sha256(precommitment_serialization(contract, disclosure_timing))


def compile_schedule() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": (
                f"binding-{contract.lower()}-{timing.lower()}-r{repetition:02d}"
            ),
            "world_contract": contract,
            "world_contract_rows": binding_rows(contract),
            "serialized_world_contract_text": serialized_binding_text(contract),
            "disclosure_timing": timing,
            "repetition_index": repetition,
            "visible_target": VISIBLE_TARGET,
            "binding_policy_visible_before_commitment": timing == EARLY,
            "precommitment_policy_visible_serialization": (
                precommitment_serialization(contract, timing)
            ),
            "precommitment_input_sha256": precommitment_input_hash(
                contract, timing
            ),
        }
        for contract in CONTRACTS
        for timing in DISCLOSURE_TIMINGS
        for repetition in range(1, REPETITIONS + 1)
    ]


def late_input_equivalence() -> dict[str, Any]:
    c0_serialization = precommitment_serialization(C0, LATE)
    c1_serialization = precommitment_serialization(C1, LATE)
    c0_hash = _text_sha256(c0_serialization)
    c1_hash = _text_sha256(c1_serialization)
    return {
        "C0_LATE_serialization": c0_serialization,
        "C1_LATE_serialization": c1_serialization,
        "C0_LATE_sha256": c0_hash,
        "C1_LATE_sha256": c1_hash,
        "serializations_match": c0_serialization == c1_serialization,
        "hashes_match": c0_hash == c1_hash,
        "required": True,
    }


def build_protocol_declaration() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "status": "FROZEN_BEFORE_EMPIRICAL_EXECUTION",
        "repository_authority_commit": REPOSITORY_AUTHORITY_COMMIT,
        "prior_evidence": {
            "protocol": PRIOR_PROTOCOL,
            "freeze": PRIOR_FREEZE,
            "qualified_action_surface": QUALIFIED_ACTION_SURFACE,
            "world": PRIOR_WORLD,
            "calls": PRIOR_CALLS,
        },
        "research_question": [
            "Does precommitment availability of the authoritative action-to-color binding change accepted action selection?",
            "Can a hidden world relation change consequence without changing actor-available information?",
        ],
        "fixed_task": FIXED_TASK,
        "visible_target": VISIBLE_TARGET,
        "world_contracts": deepcopy(WORLD_CONTRACTS),
        "world_contract_declaration_order": list(ACTION_ENUM),
        "observability_conditions": {
            EARLY: (
                "actual binding disclosed before policy request and terminal commitment"
            ),
            LATE: (
                "binding disclosed only after world acceptance, terminal commitment, consequence, and score"
            ),
        },
        "design": {
            "logical_cells": [
                f"{contract}/{timing}"
                for contract in CONTRACTS
                for timing in DISCLOSURE_TIMINGS
            ],
            "repetitions_per_logical_cell": REPETITIONS,
            "total_empirical_episodes": 16,
            "execution_order": (
                "C0/EARLY repetitions 1-4; C0/LATE repetitions 1-4; "
                "C1/EARLY repetitions 1-4; C1/LATE repetitions 1-4"
            ),
        },
        "critical_hidden_input_equivalence": late_input_equivalence(),
        "held_fixed": {
            "model_identifier": MODEL_IDENTIFIER,
            "endpoint": DEFAULT_ENDPOINT,
            "sampling": deepcopy(SAMPLING_SETTINGS),
            "action_enum_order": list(ACTION_ENUM),
            "action_schema_sha256": action_schema_hash(),
            "adapter_realization": CONSTRAINED_TYPED_ACTION,
            "visible_target": VISIBLE_TARGET,
            "task": FIXED_TASK,
            "consequence_timing": (
                "world acceptance, commitment, consequence, then score"
            ),
            "stateless_episode_requests": True,
            "tools_or_mcp_supplied": False,
            "repository_or_filesystem_supplied": False,
            "prior_episode_history_supplied": False,
            "empirical_retries": 0,
        },
        "consequence_separation": [
            "requested action",
            "committed action",
            "produced color under authoritative world contract",
            "success iff produced color equals RED",
        ],
        "validity": {
            "wrong_legal_actions_are_behavior_not_invalidity": True,
            "invalidity_conditions": [
                "C0/LATE and C1/LATE visible-input mismatch",
                "world contract enters decoder schema or policy-visible metadata",
                "previous episode history exposure",
                "consequence revealed before commitment",
                "binding revealed before commitment in LATE",
                "wrong binding shown in EARLY",
                "retry or replacement",
                "late disclosure changes commitment",
                "world scoring ignores authoritative contract",
                "schedule mutation",
                "task or target differs across cells",
            ],
        },
        "scientific_boundary": {
            "may_establish": [
                "bounded association between precommitment binding availability and useful action discrimination",
                "bounded consequence change under latent contract reversal without observed-binding use being required to explain selection",
            ],
            "does_not_establish": [
                "agency",
                "symbolic reasoning",
                "hidden world-model representation",
                "internal causal mechanism",
                "general relation understanding",
                "general temporal cognition",
                "generalized symbolic coordinate system",
            ],
            "scientific_adjudication": "NOT_PERFORMED",
        },
        "reuse_existing_action_qualification": True,
        "new_qualification_calls": 0,
        "stop_after_pressure": True,
    }


def protocol_hash() -> str:
    return _sha256(build_protocol_declaration())


def schedule_hash() -> str:
    return _sha256(compile_schedule())


def build_freeze_artifact() -> dict[str, Any]:
    protocol = build_protocol_declaration()
    schedule = compile_schedule()
    equivalence = late_input_equivalence()
    if not equivalence["serializations_match"] or not equivalence["hashes_match"]:
        raise RuntimeError("C0/LATE and C1/LATE precommitment inputs differ")
    return {
        "artifact": "behavioral_coupling_binding_observability_freeze_v0",
        "artifact_class": "PRE_EXECUTION_PROTOCOL_AND_SCHEDULE_FREEZE",
        "protocol": protocol,
        "protocol_sha256": _sha256(protocol),
        "schedule": schedule,
        "schedule_sha256": _sha256(schedule),
        "action_schema": structured_action_response_format(ACTION_ENUM),
        "action_schema_sha256": action_schema_hash(),
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "world_contracts": deepcopy(WORLD_CONTRACTS),
        "visible_target": VISIBLE_TARGET,
        "repetitions_per_logical_cell": REPETITIONS,
        "late_precommitment_input_equivalence": equivalence,
        "existing_action_qualification": QUALIFIED_ACTION_SURFACE,
        "new_qualification_model_calls_made": 0,
        "empirical_model_calls_made": 0,
        "P1_revisited": False,
        "P3_status": "BLOCKED_NOT_EXECUTED",
        "P4_revisited": False,
        "scientific_adjudication": "NOT_PERFORMED",
    }


def _write_new_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_freeze() -> dict[str, Any]:
    freeze = build_freeze_artifact()
    _write_new_json(FREEZE_PATH, freeze)
    return freeze


def load_validated_freeze() -> dict[str, Any]:
    if not FREEZE_PATH.exists():
        raise RuntimeError("pre-execution freeze is missing")
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    if freeze != build_freeze_artifact():
        raise RuntimeError("committed freeze differs from reconstructed protocol")
    if len(freeze["schedule"]) != 16:
        raise RuntimeError("frozen schedule must contain exactly 16 episodes")
    if freeze["protocol_sha256"] != protocol_hash():
        raise RuntimeError("protocol commitment mismatch")
    if freeze["schedule_sha256"] != schedule_hash():
        raise RuntimeError("schedule commitment mismatch")
    if freeze["action_schema_sha256"] != action_schema_hash():
        raise RuntimeError("action schema commitment mismatch")
    equivalence = freeze["late_precommitment_input_equivalence"]
    if not equivalence["serializations_match"] or not equivalence["hashes_match"]:
        raise RuntimeError("late hidden-input equivalence is not established")
    return freeze


def load_qualified_action_surface() -> dict[str, Any]:
    qualification = load_validated_qualification()
    if qualification.get("action_schema_sha256") != action_schema_hash():
        raise RuntimeError("qualified action schema differs")
    if qualification.get("result", {}).get("status") != "PASS":
        raise RuntimeError("ACT_A/ACT_B action surface is not qualified")
    if qualification.get("scientific_schedule_entries_consumed") != 0:
        raise RuntimeError("action qualification consumed scientific schedule")
    return qualification


def _config() -> LMStudioEndpointConfig:
    return LMStudioEndpointConfig(
        endpoint=DEFAULT_ENDPOINT,
        model_identifier=MODEL_IDENTIFIER,
        sampling_settings=SAMPLING_SETTINGS,
        timeout_seconds=120.0,
    )


def _new_adapter() -> LMStudioConstrainedActionPolicyAdapter:
    return LMStudioConstrainedActionPolicyAdapter(
        _config(),
        action_enum=ACTION_ENUM,
    )


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


def _run_episode(
    spec: Mapping[str, Any],
    adapter: LMStudioConstrainedActionPolicyAdapter,
) -> dict[str, Any]:
    contract = str(spec["world_contract"])
    timing = str(spec["disclosure_timing"])
    events: list[dict[str, Any]] = []
    _append_event(
        events,
        "WORLD_CONTRACT_ESTABLISHED",
        policy_visible=False,
        payload={
            "world_contract": contract,
            "binding_rows": binding_rows(contract),
            "serialized_binding_text": serialized_binding_text(contract),
        },
    )
    if timing == EARLY:
        _append_event(
            events,
            "BINDING_DISCLOSED",
            policy_visible=True,
            payload={
                "binding_rows": binding_rows(contract),
                "serialized_binding_text": serialized_binding_text(contract),
            },
        )

    requested: str | None
    policy_error: str | None = None
    try:
        requested = adapter(FIXED_TASK, _visible_history(events))
    except Exception as exc:
        requested = None
        policy_error = f"{type(exc).__name__}: {exc}"

    accepted: str | None = None
    failure: str | None = None
    if policy_error is not None:
        failure = "POLICY_INVOCATION_FAILURE"
    elif requested not in ACTION_ENUM:
        failure = "MALFORMED_POLICY_OUTPUT"
    else:
        accepted = requested

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
            payload={"committed_action": accepted},
        )
    produced_color = (
        WORLD_CONTRACTS[contract][accepted] if accepted is not None else None
    )
    _append_event(
        events,
        "WORLD_CONSEQUENCE",
        policy_visible=False,
        payload={
            "committed_action": accepted,
            "produced_color": produced_color,
        },
    )
    success = produced_color == VISIBLE_TARGET
    _append_event(
        events,
        "SCORE",
        policy_visible=False,
        payload={
            "produced_color": produced_color,
            "target_color": VISIBLE_TARGET,
            "success": success,
        },
    )
    if timing == LATE:
        _append_event(
            events,
            "BINDING_DISCLOSED",
            policy_visible=True,
            payload={
                "binding_rows": binding_rows(contract),
                "serialized_binding_text": serialized_binding_text(contract),
            },
        )

    visible_serialization = precommitment_serialization(contract, timing)
    return {
        **deepcopy(dict(spec)),
        "ordered_events": events,
        "exact_precommitment_policy_visible_serialization": visible_serialization,
        "observed_precommitment_input_sha256": _text_sha256(visible_serialization),
        "requested_action": requested,
        "world_acceptance_receipt": {
            "requested_action": requested,
            "accepted_action": accepted,
            "accepted": accepted is not None,
            "reason": failure,
        },
        "committed_action": accepted,
        "authoritative_produced_color": produced_color,
        "success": success,
        "valid": True,
        "failure_class": failure,
    }


def _event_types(episode: Mapping[str, Any]) -> list[str]:
    return [str(event["event_type"]) for event in episode["ordered_events"]]


def validate_evidence(
    schedule: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
    calls: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    wounds: list[str] = []
    if list(schedule) != compile_schedule():
        wounds.append("SCHEDULE_MUTATION")
    if len(episodes) != len(schedule):
        wounds.append("EPISODE_COUNT_MISMATCH")
    if len(calls) != len(schedule):
        wounds.append("CALL_COUNT_MISMATCH")
    expected_ids = [spec["episode_id"] for spec in schedule]
    if [episode.get("episode_id") for episode in episodes] != expected_ids:
        wounds.append("EPISODE_ORDER_MISMATCH")
    if [call.get("episode_id") for call in calls] != expected_ids:
        wounds.append("CALL_ASSOCIATION_MISMATCH")

    late_serializations: dict[str, set[str]] = {C0: set(), C1: set()}
    late_hashes: dict[str, set[str]] = {C0: set(), C1: set()}
    expected_schema = structured_action_response_format(ACTION_ENUM)
    for spec, episode, call in zip(schedule, episodes, calls):
        episode_id = str(spec["episode_id"])
        for key in (
            "world_contract",
            "world_contract_rows",
            "serialized_world_contract_text",
            "disclosure_timing",
            "repetition_index",
            "visible_target",
            "binding_policy_visible_before_commitment",
            "precommitment_policy_visible_serialization",
            "precommitment_input_sha256",
        ):
            if episode.get(key) != spec[key]:
                wounds.append(f"{episode_id}:EPISODE_SPEC_MISMATCH:{key}")
        try:
            visible = json.loads(str(call["serialized_policy_visible_request"]))
        except Exception:
            wounds.append(f"{episode_id}:UNREADABLE_POLICY_INPUT")
            continue
        expected_visible = policy_visible_request(
            str(spec["world_contract"]), str(spec["disclosure_timing"])
        )
        expected_serialization = _canonical_json(expected_visible)
        expected_hash = _text_sha256(expected_serialization)
        if visible != expected_visible:
            wounds.append(f"{episode_id}:POLICY_VISIBILITY_MISMATCH")
        if call.get("serialized_policy_visible_request") != expected_serialization:
            wounds.append(f"{episode_id}:NONCANONICAL_POLICY_SERIALIZATION")
        if episode.get("exact_precommitment_policy_visible_serialization") != expected_serialization:
            wounds.append(f"{episode_id}:TRACE_SERIALIZATION_MISMATCH")
        if episode.get("observed_precommitment_input_sha256") != expected_hash:
            wounds.append(f"{episode_id}:TRACE_INPUT_HASH_MISMATCH")
        if str(spec["disclosure_timing"]) == LATE:
            contract = str(spec["world_contract"])
            late_serializations[contract].add(expected_serialization)
            late_hashes[contract].add(expected_hash)
            if visible["policy_visible_protocol_history"]:
                wounds.append(f"{episode_id}:LATE_BINDING_LEAK")
            serialized_visible = str(call["serialized_policy_visible_request"])
            if contract in serialized_visible or serialized_binding_text(contract) in serialized_visible:
                wounds.append(f"{episode_id}:HIDDEN_CONTRACT_METADATA_LEAK")
        if call.get("action_schema_hash") != action_schema_hash():
            wounds.append(f"{episode_id}:SCHEMA_HASH_MISMATCH")
        if call.get("actuation_constraint") != expected_schema:
            wounds.append(f"{episode_id}:SCHEMA_CONTENT_MISMATCH")
        if call.get("conversation_state_supplied") is not False:
            wounds.append(f"{episode_id}:CONVERSATION_STATE_SUPPLIED")
        if call.get("tools_supplied") is not False:
            wounds.append(f"{episode_id}:TOOLS_SUPPLIED")
        try:
            http_request = json.loads(str(call["serialized_http_request"]))
        except Exception:
            wounds.append(f"{episode_id}:UNREADABLE_HTTP_REQUEST")
        else:
            expected_message = {
                "role": "user",
                "content": expected_serialization,
            }
            if http_request.get("messages") != [expected_message]:
                wounds.append(f"{episode_id}:NONSTATELESS_HTTP_REQUEST")
            if http_request.get("response_format") != expected_schema:
                wounds.append(f"{episode_id}:HTTP_SCHEMA_MISMATCH")
            if http_request.get("model") != MODEL_IDENTIFIER:
                wounds.append(f"{episode_id}:MODEL_MISMATCH")
            for key, value in SAMPLING_SETTINGS.items():
                if http_request.get(key) != value:
                    wounds.append(f"{episode_id}:SAMPLING_MISMATCH:{key}")
            if any(
                key in http_request
                for key in ("tools", "integrations", "previous_response_id")
            ):
                wounds.append(f"{episode_id}:FORBIDDEN_HTTP_SURFACE")
        if call.get("selected_action") != episode.get("requested_action"):
            wounds.append(f"{episode_id}:REQUESTED_ACTION_MISMATCH")
        receipt = episode.get("world_acceptance_receipt", {})
        if receipt.get("accepted_action") != episode.get("committed_action"):
            wounds.append(f"{episode_id}:WORLD_RECEIPT_MISMATCH")
        committed = episode.get("committed_action")
        expected_color = (
            WORLD_CONTRACTS[str(spec["world_contract"])][str(committed)]
            if committed in ACTION_ENUM
            else None
        )
        if episode.get("authoritative_produced_color") != expected_color:
            wounds.append(f"{episode_id}:WORLD_CONSEQUENCE_MISMATCH")
        expected_success = expected_color == VISIBLE_TARGET
        if episode.get("success") is not expected_success:
            wounds.append(f"{episode_id}:SCORING_MISMATCH")
        types = _event_types(episode)
        expected_types = (
            [
                "WORLD_CONTRACT_ESTABLISHED",
                "BINDING_DISCLOSED",
                "POLICY_ACTION_REQUESTED",
                "WORLD_ACTION_RECEIPT",
                "TERMINAL_COMMITMENT",
                "WORLD_CONSEQUENCE",
                "SCORE",
            ]
            if str(spec["disclosure_timing"]) == EARLY and committed is not None
            else [
                "WORLD_CONTRACT_ESTABLISHED",
                "POLICY_ACTION_REQUESTED",
                "WORLD_ACTION_RECEIPT",
                "TERMINAL_COMMITMENT",
                "WORLD_CONSEQUENCE",
                "SCORE",
                "BINDING_DISCLOSED",
            ]
            if committed is not None
            else types
        )
        if committed is not None and types != expected_types:
            wounds.append(f"{episode_id}:EVENT_ORDER_MISMATCH")
        if episode.get("valid") is not True:
            wounds.append(f"{episode_id}:EPISODE_NOT_RETAINED_VALID")

    c0_late = late_serializations[C0]
    c1_late = late_serializations[C1]
    if len(c0_late) != 1 or len(c1_late) != 1 or c0_late != c1_late:
        wounds.append("LATE_POLICY_VISIBLE_INPUT_MISMATCH")
    if len(late_hashes[C0]) != 1 or len(late_hashes[C1]) != 1 or late_hashes[C0] != late_hashes[C1]:
        wounds.append("LATE_POLICY_VISIBLE_HASH_MISMATCH")

    return {
        "status": "VALID" if not wounds else "EXPERIMENT_INVALID",
        "invalidity_wounds": wounds,
        "wrong_legal_actions_are_behavior_not_invalidity": True,
        "episodes_retained": len(episodes),
        "calls_retained": len(calls),
        "empirical_retries": 0,
        "late_input_equivalence": {
            "C0_LATE_serializations": sorted(c0_late),
            "C1_LATE_serializations": sorted(c1_late),
            "C0_LATE_hashes": sorted(late_hashes[C0]),
            "C1_LATE_hashes": sorted(late_hashes[C1]),
            "match": c0_late == c1_late and late_hashes[C0] == late_hashes[C1],
        },
    }


def _count(episodes: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "episodes": len(episodes),
        "ACT_A": sum(e["committed_action"] == ACT_A for e in episodes),
        "ACT_B": sum(e["committed_action"] == ACT_B for e in episodes),
        "RED_produced": sum(
            e["authoritative_produced_color"] == RED for e in episodes
        ),
        "BLUE_produced": sum(
            e["authoritative_produced_color"] == BLUE for e in episodes
        ),
        "success": sum(bool(e["success"]) for e in episodes),
        "failures": sum(e["committed_action"] is None for e in episodes),
        "protocol_invalid": sum(e.get("valid") is not True for e in episodes),
    }


def summarize(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        contract: {
            timing: _count(
                [
                    episode
                    for episode in episodes
                    if episode["world_contract"] == contract
                    and episode["disclosure_timing"] == timing
                ]
            )
            for timing in DISCLOSURE_TIMINGS
        }
        for contract in CONTRACTS
    }


def execute_once(execution_basis_commit: str) -> dict[str, Any]:
    if not execution_basis_commit.strip():
        raise ValueError("execution basis commit must be supplied")
    freeze = load_validated_freeze()
    qualification = load_qualified_action_surface()
    for path in OUTPUT_PATHS:
        if path.exists():
            raise RuntimeError(f"refusing to overwrite existing evidence: {path}")

    schedule = [deepcopy(row) for row in freeze["schedule"]]
    episodes: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for spec in schedule:
        adapter = _new_adapter()
        episode = _run_episode(spec, adapter)
        records = adapter.call_records
        episodes.append(episode)
        if len(records) == 1:
            calls.append(
                {
                    "episode_id": spec["episode_id"],
                    "precommitment_policy_visible_serialization": spec[
                        "precommitment_policy_visible_serialization"
                    ],
                    "precommitment_input_sha256": spec[
                        "precommitment_input_sha256"
                    ],
                    **records[0],
                }
            )

    validity = validate_evidence(schedule, episodes, calls)
    descriptive_summary = summarize(episodes)
    common = {
        "pressure": "LATENT_WORLD_BINDING_PRECOMMITMENT_OBSERVABILITY",
        "protocol_version": PROTOCOL_VERSION,
        "protocol_sha256": freeze["protocol_sha256"],
        "schedule_sha256": freeze["schedule_sha256"],
        "action_schema_sha256": freeze["action_schema_sha256"],
        "freeze_path": str(FREEZE_PATH).replace("\\", "/"),
        "reused_action_qualification_path": QUALIFIED_ACTION_SURFACE,
        "reused_action_qualification_result": qualification["result"],
        "new_qualification_call_count": 0,
        "execution_basis_commit": execution_basis_commit,
        "adapter_repository_commit": ADAPTER_AUTHORITY_COMMIT,
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "visible_target": VISIBLE_TARGET,
        "scoring_rule": SCORING_RULE,
        "descriptive_summary": descriptive_summary,
        "validity": validity,
        "empirical_episode_count": len(episodes),
        "empirical_call_count": len(calls),
        "empirical_retry_count": 0,
        "P1_revisited": False,
        "P3_status": "BLOCKED_NOT_EXECUTED",
        "P3_empirical_calls": 0,
        "P4_revisited": False,
        "consequence_timing_varied": False,
        "scientific_adjudication": "NOT_PERFORMED",
    }
    world = {
        "artifact": "behavioral_coupling_binding_observability_world_v0",
        "artifact_class": "EMPIRICAL_WORLD_TRACE",
        **deepcopy(common),
        "episodes": episodes,
    }
    call_evidence = {
        "artifact": "behavioral_coupling_binding_observability_calls_v0",
        "artifact_class": "EMPIRICAL_MODEL_CALL_EVIDENCE",
        **deepcopy(common),
        "calls": calls,
    }
    _write_new_json(WORLD_PATH, world)
    _write_new_json(CALLS_PATH, call_evidence)
    return common


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--freeze", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--basis-commit")
    args = parser.parse_args(argv)
    if args.freeze:
        freeze = write_freeze()
        print(
            json.dumps(
                {
                    "protocol_sha256": freeze["protocol_sha256"],
                    "schedule_sha256": freeze["schedule_sha256"],
                    "action_schema_sha256": freeze["action_schema_sha256"],
                    "C0_LATE_sha256": freeze[
                        "late_precommitment_input_equivalence"
                    ]["C0_LATE_sha256"],
                    "C1_LATE_sha256": freeze[
                        "late_precommitment_input_equivalence"
                    ]["C1_LATE_sha256"],
                    "late_inputs_match": freeze[
                        "late_precommitment_input_equivalence"
                    ]["hashes_match"],
                    "episodes": len(freeze["schedule"]),
                    "new_qualification_model_calls_made": 0,
                    "empirical_model_calls_made": 0,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if not args.basis_commit:
        parser.error("--execute requires --basis-commit")
    result = execute_once(args.basis_commit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["validity"]["status"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
