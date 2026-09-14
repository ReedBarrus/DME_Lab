"""Frozen consequence-occurrence versus later precommitment-observability pressure."""

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


PROTOCOL_VERSION = "behavioral_coupling_consequence_observability_v0"
REPOSITORY_AUTHORITY_COMMIT = "65f1e881b114a07cafb46fef8875d4b11aeb990b"
ADAPTER_AUTHORITY_COMMIT = "d60ce2044fb2215e58eec74de8e311ba42765bc0"

K_RED = "K_RED"
K_BLUE = "K_BLUE"
EARLY = "EARLY"
LATE = "LATE"
CONSEQUENCE_CASES = {K_RED: RED, K_BLUE: BLUE}
CONSEQUENCE_CASE_ORDER = (K_RED, K_BLUE)
RECEIPT_TIMINGS = (EARLY, LATE)
REPETITIONS = 4

RESPONSE_CONTRACT = {ACT_A: RED, ACT_B: BLUE}
RESPONSE_CONTRACT_ROWS = [
    {"action": action, "implied_color": RESPONSE_CONTRACT[action]}
    for action in ACTION_ENUM
]
SERIALIZED_RESPONSE_CONTRACT = "; ".join(
    f"{row['action']} -> {row['implied_color']}"
    for row in RESPONSE_CONTRACT_ROWS
)
FIXED_TASK = (
    "The previous committed world interaction has already produced one "
    "authoritative consequence: RED or BLUE. Select the legal action "
    "corresponding to that consequence under the fixed response contract: "
    "ACT_A -> RED; ACT_B -> BLUE. Respond with exactly ACT_A or ACT_B."
)
SCORING_RULE = (
    "apply the fixed visible response contract to the committed Stage-2 ACT "
    "token; success iff action-implied color equals the authoritative Stage-1 "
    "consequence"
)

PRIOR_PROTOCOL = (
    "docs/methods/Consequence_Surface/"
    "Behavioral_Coupling_Binding_Observability_v0.md"
)
PRIOR_FREEZE = "traces/behavioral_coupling_binding_observability_freeze_v0.json"
PRIOR_WORLD = "traces/behavioral_coupling_binding_observability_world_v0.json"
PRIOR_CALLS = "traces/behavioral_coupling_binding_observability_calls_v0.json"
QUALIFIED_ACTION_SURFACE = (
    "traces/behavioral_coupling_action_delexicalization_qualification_v0.json"
)

PROTOCOL_PATH = Path("docs/methods/Consequence_Surface") / (
    "Behavioral_Coupling_Consequence_Observability_v0.md"
)
FREEZE_PATH = Path(
    "traces/behavioral_coupling_consequence_observability_freeze_v0.json"
)
WORLD_PATH = Path(
    "traces/behavioral_coupling_consequence_observability_world_v0.json"
)
CALLS_PATH = Path(
    "traces/behavioral_coupling_consequence_observability_calls_v0.json"
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


def policy_visible_request(consequence: str, receipt_timing: str) -> dict[str, Any]:
    if consequence not in (RED, BLUE):
        raise ValueError(f"unknown Stage-1 consequence: {consequence}")
    if receipt_timing not in RECEIPT_TIMINGS:
        raise ValueError(f"unknown receipt timing: {receipt_timing}")
    history: list[dict[str, Any]] = []
    if receipt_timing == EARLY:
        history.append(
            {
                "event_type": "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                "payload": {"authoritative_consequence": consequence},
            }
        )
    return {
        "fixed_task": FIXED_TASK,
        "policy_visible_protocol_history": history,
        "legal_action_vocabulary": list(ACTION_ENUM),
    }


def precommitment_serialization(consequence: str, receipt_timing: str) -> str:
    return _canonical_json(policy_visible_request(consequence, receipt_timing))


def precommitment_input_hash(consequence: str, receipt_timing: str) -> str:
    return _text_sha256(precommitment_serialization(consequence, receipt_timing))


def compile_schedule() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": (
                f"consequence-{case.lower()}-{timing.lower()}-r{repetition:02d}"
            ),
            "stage_1_consequence_schedule_identity": case,
            "authoritative_stage_1_consequence": consequence,
            "receipt_timing": timing,
            "repetition_index": repetition,
            "response_contract_rows": deepcopy(RESPONSE_CONTRACT_ROWS),
            "serialized_response_contract": SERIALIZED_RESPONSE_CONTRACT,
            "receipt_policy_visible_before_stage_2_commitment": timing == EARLY,
            "stage_2_precommitment_policy_serialization": (
                precommitment_serialization(consequence, timing)
            ),
            "stage_2_precommitment_sha256": precommitment_input_hash(
                consequence, timing
            ),
        }
        for case in CONSEQUENCE_CASE_ORDER
        for timing in RECEIPT_TIMINGS
        for repetition in range(1, REPETITIONS + 1)
        for consequence in (CONSEQUENCE_CASES[case],)
    ]


def late_input_equivalence() -> dict[str, Any]:
    red_serialization = precommitment_serialization(RED, LATE)
    blue_serialization = precommitment_serialization(BLUE, LATE)
    red_hash = _text_sha256(red_serialization)
    blue_hash = _text_sha256(blue_serialization)
    return {
        "RED_LATE_serialization": red_serialization,
        "BLUE_LATE_serialization": blue_serialization,
        "RED_LATE_sha256": red_hash,
        "BLUE_LATE_sha256": blue_hash,
        "serializations_match": red_serialization == blue_serialization,
        "hashes_match": red_hash == blue_hash,
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
            "world": PRIOR_WORLD,
            "calls": PRIOR_CALLS,
            "qualified_action_surface": QUALIFIED_ACTION_SURFACE,
        },
        "research_question": [
            "Holding Stage-1 consequence occurrence fixed before Stage 2, does precommitment receipt visibility change accepted Stage-2 action selection?",
            "Can a consequence exist before Stage 2 while remaining behaviorally unavailable because its receipt has not crossed the observation boundary?",
        ],
        "critical_distinction": [
            "consequence occurred != consequence receipt exists",
            "receipt exists != receipt is policy-visible",
            "receipt is policy-visible != receipt is visible before commitment",
            "precommitment receipt visibility != changed later selection",
        ],
        "fixed_stage_2_task": FIXED_TASK,
        "fixed_stage_2_response_contract": deepcopy(RESPONSE_CONTRACT),
        "serialized_stage_2_response_contract": SERIALIZED_RESPONSE_CONTRACT,
        "stage_1": {
            "interaction": "FIRST_INTERACTION_COMMITTED",
            "model_selectable_action": False,
            "consequence_cases": deepcopy(CONSEQUENCE_CASES),
            "consequence_occurs_before_stage_2_inference_in_all_conditions": True,
        },
        "receipt_timings": {
            EARLY: (
                "consequence occurs, receipt is delivered, then Stage-2 policy request and commitment"
            ),
            LATE: (
                "consequence occurs, receipt is withheld through Stage-2 commitment and score, then delivered"
            ),
        },
        "design": {
            "logical_cells": [
                f"{consequence}/{timing}"
                for consequence in (RED, BLUE)
                for timing in RECEIPT_TIMINGS
            ],
            "repetitions_per_logical_cell": REPETITIONS,
            "total_stage_2_policy_decisions": 16,
            "execution_order": (
                "RED/EARLY repetitions 1-4; RED/LATE repetitions 1-4; "
                "BLUE/EARLY repetitions 1-4; BLUE/LATE repetitions 1-4"
            ),
        },
        "critical_late_input_equivalence": late_input_equivalence(),
        "held_fixed": {
            "model_identifier": MODEL_IDENTIFIER,
            "endpoint": DEFAULT_ENDPOINT,
            "sampling": deepcopy(SAMPLING_SETTINGS),
            "action_enum_order": list(ACTION_ENUM),
            "action_schema_sha256": action_schema_hash(),
            "stage_2_response_contract_rows": deepcopy(RESPONSE_CONTRACT_ROWS),
            "stage_1_consequence_occurrence_position": (
                "before Stage-2 inference"
            ),
            "adapter_realization": CONSTRAINED_TYPED_ACTION,
            "stateless_stage_2_requests": True,
            "tools_or_mcp_supplied": False,
            "repository_or_filesystem_supplied": False,
            "prior_episode_results_supplied": False,
            "empirical_retries": 0,
        },
        "scoring": {
            "rule": SCORING_RULE,
            "separate_values": [
                "authoritative Stage-1 consequence",
                "Stage-2 requested action",
                "Stage-2 action-implied color",
                "success",
            ],
        },
        "validity": {
            "wrong_legal_stage_2_actions_are_behavior_not_invalidity": True,
            "invalidity_conditions": [
                "RED/LATE and BLUE/LATE policy-input mismatch",
                "consequence identity leaks before commitment in LATE",
                "consequence does not occur before Stage-2 inference",
                "EARLY receipt contains wrong consequence",
                "response-contract mutation",
                "action-schema mutation",
                "retry or replacement",
                "prior-episode leakage",
                "schedule mutation",
                "late receipt changes commitment or score",
                "score ignores authoritative Stage-1 consequence",
            ],
        },
        "scientific_boundary": {
            "may_establish": [
                "bounded association between precommitment evidence of an already-occurred consequence and useful later action discrimination",
                "bounded existence of an authoritative consequence before a policy decision without behavioral availability before its receipt crosses the observation boundary",
            ],
            "does_not_establish": [
                "reinforcement learning",
                "memory architecture",
                "general temporal cognition",
                "causal understanding",
                "agency",
                "learning across episodes",
                "general consequence geometry",
                "generalized feedback control",
            ],
            "scientific_adjudication": "NOT_PERFORMED",
        },
        "actual_consequence_timing_varied": False,
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
        raise RuntimeError("RED/LATE and BLUE/LATE precommitment inputs differ")
    return {
        "artifact": "behavioral_coupling_consequence_observability_freeze_v0",
        "artifact_class": "PRE_EXECUTION_PROTOCOL_AND_SCHEDULE_FREEZE",
        "protocol": protocol,
        "protocol_sha256": _sha256(protocol),
        "schedule": schedule,
        "schedule_sha256": _sha256(schedule),
        "response_action_schema": structured_action_response_format(ACTION_ENUM),
        "response_action_schema_sha256": action_schema_hash(),
        "fixed_stage_2_response_contract": deepcopy(RESPONSE_CONTRACT),
        "serialized_stage_2_response_contract": SERIALIZED_RESPONSE_CONTRACT,
        "stage_1_consequence_schedule": deepcopy(CONSEQUENCE_CASES),
        "event_order": {
            EARLY: [
                "FIRST_INTERACTION_COMMITTED",
                "WORLD_CONSEQUENCE_OCCURRED",
                "CONSEQUENCE_RECEIPT_GENERATED",
                "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                "STAGE_2_POLICY_REQUEST",
                "WORLD_ACCEPTANCE",
                "STAGE_2_TERMINAL_COMMITMENT",
                "STAGE_2_ACTION_COLOR_DERIVED",
                "SCORE",
            ],
            LATE: [
                "FIRST_INTERACTION_COMMITTED",
                "WORLD_CONSEQUENCE_OCCURRED",
                "CONSEQUENCE_RECEIPT_GENERATED",
                "CONSEQUENCE_RECEIPT_WITHHELD",
                "STAGE_2_POLICY_REQUEST",
                "WORLD_ACCEPTANCE",
                "STAGE_2_TERMINAL_COMMITMENT",
                "STAGE_2_ACTION_COLOR_DERIVED",
                "SCORE",
                "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
            ],
        },
        "repetitions_per_logical_cell": REPETITIONS,
        "late_precommitment_input_equivalence": equivalence,
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "scoring_rule": SCORING_RULE,
        "existing_action_qualification": QUALIFIED_ACTION_SURFACE,
        "new_qualification_model_calls_made": 0,
        "empirical_model_calls_made": 0,
        "actual_consequence_timing_varied": False,
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
    if freeze["response_action_schema_sha256"] != action_schema_hash():
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


def _event_index(events: Sequence[Mapping[str, Any]], event_type: str) -> int:
    matches = [int(event["event_index"]) for event in events if event["event_type"] == event_type]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {event_type} event")
    return matches[0]


def _run_episode(
    spec: Mapping[str, Any],
    adapter: LMStudioConstrainedActionPolicyAdapter,
) -> dict[str, Any]:
    consequence = str(spec["authoritative_stage_1_consequence"])
    timing = str(spec["receipt_timing"])
    events: list[dict[str, Any]] = []
    _append_event(
        events,
        "FIRST_INTERACTION_COMMITTED",
        policy_visible=False,
        payload={"apparatus_controlled": True},
    )
    _append_event(
        events,
        "WORLD_CONSEQUENCE_OCCURRED",
        policy_visible=False,
        payload={"authoritative_consequence": consequence},
    )
    _append_event(
        events,
        "CONSEQUENCE_RECEIPT_GENERATED",
        policy_visible=False,
        payload={"authoritative_consequence": consequence},
    )
    if timing == EARLY:
        _append_event(
            events,
            "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
            policy_visible=True,
            payload={"authoritative_consequence": consequence},
        )
    else:
        _append_event(
            events,
            "CONSEQUENCE_RECEIPT_WITHHELD",
            policy_visible=False,
            payload={"receipt_generated": True},
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
        "STAGE_2_POLICY_REQUEST",
        policy_visible=False,
        payload=request_payload,
    )
    receipt = {
        "requested_action": requested,
        "accepted_action": accepted,
        "accepted": accepted is not None,
        "reason": failure,
    }
    _append_event(
        events,
        "WORLD_ACCEPTANCE",
        policy_visible=False,
        payload=receipt,
    )
    if accepted is not None:
        _append_event(
            events,
            "STAGE_2_TERMINAL_COMMITMENT",
            policy_visible=False,
            payload={"committed_action": accepted},
        )
    action_implied_color = RESPONSE_CONTRACT.get(str(accepted)) if accepted is not None else None
    _append_event(
        events,
        "STAGE_2_ACTION_COLOR_DERIVED",
        policy_visible=False,
        payload={
            "committed_action": accepted,
            "action_implied_color": action_implied_color,
            "response_contract": deepcopy(RESPONSE_CONTRACT),
        },
    )
    success = action_implied_color == consequence
    _append_event(
        events,
        "SCORE",
        policy_visible=False,
        payload={
            "authoritative_stage_1_consequence": consequence,
            "action_implied_color": action_implied_color,
            "success": success,
        },
    )
    if timing == LATE:
        _append_event(
            events,
            "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
            policy_visible=True,
            payload={"authoritative_consequence": consequence},
        )

    precommit_serialization = precommitment_serialization(consequence, timing)
    commitment_index = (
        _event_index(events, "STAGE_2_TERMINAL_COMMITMENT")
        if accepted is not None
        else None
    )
    return {
        **deepcopy(dict(spec)),
        "ordered_events": events,
        "consequence_occurrence_event_index": _event_index(
            events, "WORLD_CONSEQUENCE_OCCURRED"
        ),
        "receipt_generation_event_index": _event_index(
            events, "CONSEQUENCE_RECEIPT_GENERATED"
        ),
        "receipt_delivery_event_index": _event_index(
            events, "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY"
        ),
        "stage_2_commitment_event_index": commitment_index,
        "exact_stage_2_precommitment_policy_serialization": precommit_serialization,
        "observed_stage_2_precommitment_sha256": _text_sha256(
            precommit_serialization
        ),
        "stage_2_requested_action": requested,
        "world_acceptance_receipt": receipt,
        "stage_2_committed_action": accepted,
        "stage_2_action_implied_color": action_implied_color,
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

    late_serializations: dict[str, set[str]] = {RED: set(), BLUE: set()}
    late_hashes: dict[str, set[str]] = {RED: set(), BLUE: set()}
    expected_schema = structured_action_response_format(ACTION_ENUM)
    for spec, episode, call in zip(schedule, episodes, calls):
        episode_id = str(spec["episode_id"])
        for key in (
            "stage_1_consequence_schedule_identity",
            "authoritative_stage_1_consequence",
            "receipt_timing",
            "repetition_index",
            "response_contract_rows",
            "serialized_response_contract",
            "receipt_policy_visible_before_stage_2_commitment",
            "stage_2_precommitment_policy_serialization",
            "stage_2_precommitment_sha256",
        ):
            if episode.get(key) != spec[key]:
                wounds.append(f"{episode_id}:EPISODE_SPEC_MISMATCH:{key}")
        consequence = str(spec["authoritative_stage_1_consequence"])
        timing = str(spec["receipt_timing"])
        expected_visible = policy_visible_request(consequence, timing)
        expected_serialization = _canonical_json(expected_visible)
        expected_hash = _text_sha256(expected_serialization)
        try:
            visible = json.loads(str(call["serialized_policy_visible_request"]))
        except Exception:
            wounds.append(f"{episode_id}:UNREADABLE_POLICY_INPUT")
            continue
        if visible != expected_visible:
            wounds.append(f"{episode_id}:POLICY_VISIBILITY_MISMATCH")
        if call.get("serialized_policy_visible_request") != expected_serialization:
            wounds.append(f"{episode_id}:NONCANONICAL_POLICY_SERIALIZATION")
        if episode.get("exact_stage_2_precommitment_policy_serialization") != expected_serialization:
            wounds.append(f"{episode_id}:TRACE_SERIALIZATION_MISMATCH")
        if episode.get("observed_stage_2_precommitment_sha256") != expected_hash:
            wounds.append(f"{episode_id}:TRACE_INPUT_HASH_MISMATCH")
        if visible.get("fixed_task") != FIXED_TASK:
            wounds.append(f"{episode_id}:TASK_MUTATION")
        if timing == LATE:
            late_serializations[consequence].add(expected_serialization)
            late_hashes[consequence].add(expected_hash)
            if visible["policy_visible_protocol_history"]:
                wounds.append(f"{episode_id}:LATE_CONSEQUENCE_LEAK")
        else:
            expected_receipt = [
                {
                    "event_type": "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                    "payload": {"authoritative_consequence": consequence},
                }
            ]
            if visible["policy_visible_protocol_history"] != expected_receipt:
                wounds.append(f"{episode_id}:WRONG_EARLY_RECEIPT")
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
            if http_request.get("messages") != [
                {"role": "user", "content": expected_serialization}
            ]:
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
        if call.get("selected_action") != episode.get("stage_2_requested_action"):
            wounds.append(f"{episode_id}:REQUESTED_ACTION_MISMATCH")
        receipt = episode.get("world_acceptance_receipt", {})
        if receipt.get("accepted_action") != episode.get("stage_2_committed_action"):
            wounds.append(f"{episode_id}:WORLD_ACCEPTANCE_MISMATCH")
        committed = episode.get("stage_2_committed_action")
        expected_implied = RESPONSE_CONTRACT.get(str(committed)) if committed is not None else None
        if episode.get("stage_2_action_implied_color") != expected_implied:
            wounds.append(f"{episode_id}:RESPONSE_CONTRACT_MISMATCH")
        if episode.get("success") is not (expected_implied == consequence):
            wounds.append(f"{episode_id}:SCORING_MISMATCH")
        if committed is not None:
            expected_types = (
                [
                    "FIRST_INTERACTION_COMMITTED",
                    "WORLD_CONSEQUENCE_OCCURRED",
                    "CONSEQUENCE_RECEIPT_GENERATED",
                    "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                    "STAGE_2_POLICY_REQUEST",
                    "WORLD_ACCEPTANCE",
                    "STAGE_2_TERMINAL_COMMITMENT",
                    "STAGE_2_ACTION_COLOR_DERIVED",
                    "SCORE",
                ]
                if timing == EARLY
                else [
                    "FIRST_INTERACTION_COMMITTED",
                    "WORLD_CONSEQUENCE_OCCURRED",
                    "CONSEQUENCE_RECEIPT_GENERATED",
                    "CONSEQUENCE_RECEIPT_WITHHELD",
                    "STAGE_2_POLICY_REQUEST",
                    "WORLD_ACCEPTANCE",
                    "STAGE_2_TERMINAL_COMMITMENT",
                    "STAGE_2_ACTION_COLOR_DERIVED",
                    "SCORE",
                    "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                ]
            )
            if _event_types(episode) != expected_types:
                wounds.append(f"{episode_id}:EVENT_ORDER_MISMATCH")
            occurrence = episode.get("consequence_occurrence_event_index")
            delivery = episode.get("receipt_delivery_event_index")
            commitment = episode.get("stage_2_commitment_event_index")
            if timing == EARLY and not (occurrence < delivery < commitment):
                wounds.append(f"{episode_id}:EARLY_TEMPORAL_ORDER_INVALID")
            if timing == LATE and not (occurrence < commitment < delivery):
                wounds.append(f"{episode_id}:LATE_TEMPORAL_ORDER_INVALID")
        if episode.get("valid") is not True:
            wounds.append(f"{episode_id}:EPISODE_NOT_RETAINED_VALID")

    red_late = late_serializations[RED]
    blue_late = late_serializations[BLUE]
    if len(red_late) != 1 or len(blue_late) != 1 or red_late != blue_late:
        wounds.append("LATE_POLICY_VISIBLE_INPUT_MISMATCH")
    if len(late_hashes[RED]) != 1 or len(late_hashes[BLUE]) != 1 or late_hashes[RED] != late_hashes[BLUE]:
        wounds.append("LATE_POLICY_VISIBLE_HASH_MISMATCH")

    return {
        "status": "VALID" if not wounds else "EXPERIMENT_INVALID",
        "invalidity_wounds": wounds,
        "wrong_legal_stage_2_actions_are_behavior_not_invalidity": True,
        "episodes_retained": len(episodes),
        "calls_retained": len(calls),
        "empirical_retries": 0,
        "late_input_equivalence": {
            "RED_LATE_serializations": sorted(red_late),
            "BLUE_LATE_serializations": sorted(blue_late),
            "RED_LATE_hashes": sorted(late_hashes[RED]),
            "BLUE_LATE_hashes": sorted(late_hashes[BLUE]),
            "match": red_late == blue_late and late_hashes[RED] == late_hashes[BLUE],
        },
        "event_order_validation": {
            "EARLY_consequence_before_receipt_before_commitment": not any(
                "EARLY_TEMPORAL_ORDER_INVALID" in wound for wound in wounds
            ),
            "LATE_consequence_before_commitment_before_receipt": not any(
                "LATE_TEMPORAL_ORDER_INVALID" in wound for wound in wounds
            ),
        },
    }


def _count(episodes: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "episodes": len(episodes),
        "ACT_A": sum(e["stage_2_committed_action"] == ACT_A for e in episodes),
        "ACT_B": sum(e["stage_2_committed_action"] == ACT_B for e in episodes),
        "RED_implied": sum(e["stage_2_action_implied_color"] == RED for e in episodes),
        "BLUE_implied": sum(e["stage_2_action_implied_color"] == BLUE for e in episodes),
        "success": sum(bool(e["success"]) for e in episodes),
        "failures": sum(e["stage_2_committed_action"] is None for e in episodes),
        "protocol_invalid": sum(e.get("valid") is not True for e in episodes),
    }


def summarize(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        consequence: {
            timing: _count(
                [
                    episode
                    for episode in episodes
                    if episode["authoritative_stage_1_consequence"] == consequence
                    and episode["receipt_timing"] == timing
                ]
            )
            for timing in RECEIPT_TIMINGS
        }
        for consequence in (RED, BLUE)
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
                    "stage_2_precommitment_policy_serialization": spec[
                        "stage_2_precommitment_policy_serialization"
                    ],
                    "stage_2_precommitment_sha256": spec[
                        "stage_2_precommitment_sha256"
                    ],
                    **records[0],
                }
            )

    validity = validate_evidence(schedule, episodes, calls)
    descriptive_summary = summarize(episodes)
    common = {
        "pressure": "CONSEQUENCE_OCCURRENCE_VS_PRECOMMITMENT_OBSERVABILITY",
        "protocol_version": PROTOCOL_VERSION,
        "protocol_sha256": freeze["protocol_sha256"],
        "schedule_sha256": freeze["schedule_sha256"],
        "action_schema_sha256": freeze["response_action_schema_sha256"],
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
        "fixed_stage_2_response_contract": deepcopy(RESPONSE_CONTRACT),
        "serialized_stage_2_response_contract": SERIALIZED_RESPONSE_CONTRACT,
        "scoring_rule": SCORING_RULE,
        "descriptive_summary": descriptive_summary,
        "validity": validity,
        "empirical_episode_count": len(episodes),
        "empirical_call_count": len(calls),
        "empirical_retry_count": 0,
        "stage_2_policy_decision_count": len(calls),
        "stage_1_policy_decision_count": 0,
        "actual_consequence_timing_varied": False,
        "P1_revisited": False,
        "P3_status": "BLOCKED_NOT_EXECUTED",
        "P3_empirical_calls": 0,
        "P4_revisited": False,
        "scientific_adjudication": "NOT_PERFORMED",
    }
    world = {
        "artifact": "behavioral_coupling_consequence_observability_world_v0",
        "artifact_class": "EMPIRICAL_WORLD_TRACE",
        **deepcopy(common),
        "episodes": episodes,
    }
    call_evidence = {
        "artifact": "behavioral_coupling_consequence_observability_calls_v0",
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
        equivalence = freeze["late_precommitment_input_equivalence"]
        print(
            json.dumps(
                {
                    "protocol_sha256": freeze["protocol_sha256"],
                    "schedule_sha256": freeze["schedule_sha256"],
                    "action_schema_sha256": freeze[
                        "response_action_schema_sha256"
                    ],
                    "RED_LATE_sha256": equivalence["RED_LATE_sha256"],
                    "BLUE_LATE_sha256": equivalence["BLUE_LATE_sha256"],
                    "late_inputs_match": equivalence["hashes_match"],
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
