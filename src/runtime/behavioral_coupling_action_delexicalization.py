"""Frozen ACT_A/ACT_B delexicalization pressure over the bounded P2 surface."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from src.runtime.behavioral_coupling_characterization import (
    ALPHA,
    BETA,
    M1,
    M2,
    MODEL_IDENTIFIER,
    P2_MAPPINGS,
    SAMPLING_SETTINGS,
)
from src.runtime.behavioral_coupling_mapping_row_order import (
    AB,
    BA,
    DECLARATION_ORDERS,
    mapping_rows,
    serialized_mapping_text,
)
from src.runtime.bounded_consequential_feedback_experiment import (
    BLUE,
    CONDITION_F,
    CONDITION_P,
    INSPECT,
    RED,
)
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    structured_action_response_format,
    structured_action_schema_hash,
)


PROTOCOL_VERSION = "behavioral_coupling_action_delexicalization_v0"
REPOSITORY_AUTHORITY_COMMIT = "4b7b7bbe724380993845ac72ad67a241aeeb47ce"
ADAPTER_AUTHORITY_COMMIT = "d60ce2044fb2215e58eec74de8e311ba42765bc0"

ACT_A = "ACT_A"
ACT_B = "ACT_B"
C1 = "C1"
C2 = "C2"
ACTION_ENUM = (ACT_A, ACT_B)
ACTION_CONTRACTS = {
    C1: {ACT_A: RED, ACT_B: BLUE},
    C2: {ACT_A: BLUE, ACT_B: RED},
}
ACTION_CONTRACTS_ORDER = (C1, C2)
MAPPINGS = (M1, M2)
SYMBOLS = (ALPHA, BETA)
CONDITIONS = (CONDITION_F, CONDITION_P)

PRIOR_P2_WORLD = "traces/behavioral_coupling_p2_semantic_indirection_world_v0.json"
PRIOR_P2_CALLS = "traces/behavioral_coupling_p2_semantic_indirection_calls_v0.json"
PRIOR_ROW_ORDER_FREEZE = "traces/behavioral_coupling_mapping_row_order_freeze_v0.json"
PRIOR_ROW_ORDER_WORLD = "traces/behavioral_coupling_mapping_row_order_world_v0.json"
PRIOR_ROW_ORDER_CALLS = "traces/behavioral_coupling_mapping_row_order_calls_v0.json"

PROTOCOL_PATH = Path("docs/methods/Consequence_Surface") / (
    "Behavioral_Coupling_Action_Delexicalization_v0.md"
)
FREEZE_PATH = Path(
    "traces/behavioral_coupling_action_delexicalization_freeze_v0.json"
)
QUALIFICATION_PATH = Path(
    "traces/behavioral_coupling_action_delexicalization_qualification_v0.json"
)
WORLD_PATH = Path(
    "traces/behavioral_coupling_action_delexicalization_world_v0.json"
)
CALLS_PATH = Path(
    "traces/behavioral_coupling_action_delexicalization_calls_v0.json"
)
EMPIRICAL_PATHS = (WORLD_PATH, CALLS_PATH)

SCORING_RULE = (
    "accepted ACT token -> frozen action-contract target -> authoritative hidden "
    "target; correct iff the two target colors match"
)
QUALIFICATION_TASKS = {
    ACT_A: "Select ACT_A.",
    ACT_B: "Select ACT_B.",
}


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


def action_contract_rows(contract: str) -> list[dict[str, str]]:
    if contract not in ACTION_CONTRACTS:
        raise ValueError(f"unknown action contract: {contract}")
    return [
        {"action": action, "target_color": ACTION_CONTRACTS[contract][action]}
        for action in ACTION_ENUM
    ]


def serialized_action_contract_text(contract: str) -> str:
    return "; ".join(
        f"{row['action']} -> {row['target_color']}"
        for row in action_contract_rows(contract)
    )


def fixed_task(mapping: str, declaration_order: str, contract: str) -> str:
    return (
        "Select the typed action whose declared action contract maps to the "
        "authoritative target. INSPECT reports a symbol under this declared "
        f"mapping: {serialized_mapping_text(mapping, declaration_order)}. "
        "The declared action contract is: "
        f"{serialized_action_contract_text(contract)}. "
        "Respond with exactly ACT_A or ACT_B."
    )


def correct_action_for_target(contract: str, target_color: str) -> str:
    matches = [
        action
        for action, implied_target in ACTION_CONTRACTS[contract].items()
        if implied_target == target_color
    ]
    if len(matches) != 1:
        raise RuntimeError("action contract does not uniquely encode target color")
    return matches[0]


def compile_schedule() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": (
                f"p2-delex-{mapping.lower()}-{order.lower()}-{contract.lower()}-"
                f"{symbol.lower()}-{condition.lower()}"
            ),
            "mapping": mapping,
            "mapping_declaration_order": order,
            "mapping_rows": mapping_rows(mapping, order),
            "serialized_mapping_text": serialized_mapping_text(mapping, order),
            "first_mapping_row_target_color": mapping_rows(mapping, order)[0]["color"],
            "observation_symbol": symbol,
            "hidden_target_color": P2_MAPPINGS[mapping][symbol],
            "condition": condition,
            "action_contract": contract,
            "action_contract_rows": action_contract_rows(contract),
            "serialized_action_contract_text": serialized_action_contract_text(contract),
            "correct_typed_action": correct_action_for_target(
                contract, P2_MAPPINGS[mapping][symbol]
            ),
        }
        for mapping in MAPPINGS
        for order in DECLARATION_ORDERS
        for contract in ACTION_CONTRACTS_ORDER
        for symbol in SYMBOLS
        for condition in CONDITIONS
    ]


def build_protocol_declaration() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "status": "FROZEN_BEFORE_QUALIFICATION_AND_EMPIRICAL_EXECUTION",
        "repository_authority_commit": REPOSITORY_AUTHORITY_COMMIT,
        "prior_evidence": {
            "P2_world": PRIOR_P2_WORLD,
            "P2_calls": PRIOR_P2_CALLS,
            "mapping_row_order_freeze": PRIOR_ROW_ORDER_FREEZE,
            "mapping_row_order_world": PRIOR_ROW_ORDER_WORLD,
            "mapping_row_order_calls": PRIOR_ROW_ORDER_CALLS,
        },
        "earned_residue": [
            "first-row target predicted the no-symbol P action",
            "delivered symbol could override a BLUE-first default",
            "delivered symbol did not override a RED-first default",
            "earlier P1 enum reversal did not remove the RED collapse",
        ],
        "research_question": (
            "Does the observed directional asymmetry follow RED/BLUE target "
            "identity, ACT_A/ACT_B token identity, the declared target-to-action "
            "relation, or an interaction among these surfaces?"
        ),
        "intervention": {
            "typed_action_tokens": list(ACTION_ENUM),
            "action_contracts": deepcopy(ACTION_CONTRACTS),
            "action_contract_declaration_order": list(ACTION_ENUM),
            "observation_mappings": deepcopy(P2_MAPPINGS),
            "mapping_declaration_orders": {
                AB: [ALPHA, BETA],
                BA: [BETA, ALPHA],
            },
            "distinctions": [
                "observation symbol != target color",
                "target color != typed action",
                "typed action != world consequence",
            ],
        },
        "pre_execution_qualification": {
            "calls": 2,
            "tasks": deepcopy(QUALIFICATION_TASKS),
            "protocol_history": [],
            "action_enum": list(ACTION_ENUM),
            "pass_requires_exact_typed_traversal": True,
            "scientific_schedule_entries_consumed": 0,
            "stop_on_failure": True,
        },
        "factorial": {
            "mapping_presentations": [
                f"{mapping}-{order}"
                for mapping in MAPPINGS
                for order in DECLARATION_ORDERS
            ],
            "action_contract": list(ACTION_CONTRACTS_ORDER),
            "symbol": list(SYMBOLS),
            "condition": list(CONDITIONS),
            "episodes_per_cell": 1,
            "total_empirical_episodes": 32,
        },
        "conditions": {
            CONDITION_F: "symbol delivered before terminal commitment",
            CONDITION_P: "symbol withheld until after terminal commitment",
        },
        "held_fixed": {
            "model_identifier": MODEL_IDENTIFIER,
            "endpoint": DEFAULT_ENDPOINT,
            "sampling": deepcopy(SAMPLING_SETTINGS),
            "action_enum_order": list(ACTION_ENUM),
            "action_schema_hash": structured_action_schema_hash(ACTION_ENUM),
            "action_contract_row_order": list(ACTION_ENUM),
            "observation_symbols": list(SYMBOLS),
            "world_targets": [RED, BLUE],
            "adapter_realization": CONSTRAINED_TYPED_ACTION,
            "scoring": SCORING_RULE,
            "stateless_episode_requests": True,
            "tools_or_mcp_supplied": False,
            "repository_or_filesystem_supplied": False,
            "empirical_retries": 0,
        },
        "validity": {
            "wrong_policy_actions_are_behavior_not_invalidity": True,
            "invalidity_conditions": [
                "wrong action contract serialized",
                "wrong mapping serialized",
                "wrong symbol delivered",
                "hidden target leakage",
                "F/P timing error",
                "schema mutation",
                "schedule mutation",
                "retry replacement",
                "prior-episode context leakage",
                "scoring ignores frozen action contract",
            ],
        },
        "scientific_boundary": {
            "may_establish": (
                "bounded action distributions over target identity, typed token "
                "identity, and declared action contract for this realization"
            ),
            "does_not_establish": [
                "internal semantic representation",
                "symbolic reasoning",
                "agency",
                "general abstraction",
                "stable model bias",
                "causal neural mechanism",
                "general symbolic coordinate system",
            ],
            "scientific_adjudication": "NOT_PERFORMED",
        },
        "stop_after_pressure": True,
    }


def protocol_hash() -> str:
    return _sha256(build_protocol_declaration())


def schedule_hash() -> str:
    return _sha256(compile_schedule())


def action_schema_hash() -> str:
    return structured_action_schema_hash(ACTION_ENUM)


def build_freeze_artifact() -> dict[str, Any]:
    protocol = build_protocol_declaration()
    schedule = compile_schedule()
    return {
        "artifact": "behavioral_coupling_action_delexicalization_freeze_v0",
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
        "action_contracts": deepcopy(ACTION_CONTRACTS),
        "observation_mappings": deepcopy(P2_MAPPINGS),
        "qualification_model_calls_made": 0,
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
    if len(freeze["schedule"]) != 32:
        raise RuntimeError("frozen schedule must contain exactly 32 episodes")
    if freeze["protocol_sha256"] != protocol_hash():
        raise RuntimeError("protocol commitment mismatch")
    if freeze["schedule_sha256"] != schedule_hash():
        raise RuntimeError("schedule commitment mismatch")
    if freeze["action_schema_sha256"] != action_schema_hash():
        raise RuntimeError("action schema commitment mismatch")
    return freeze


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


def _qualification_expected_visible(token: str) -> dict[str, Any]:
    return {
        "fixed_task": QUALIFICATION_TASKS[token],
        "policy_visible_protocol_history": [],
        "legal_action_vocabulary": list(ACTION_ENUM),
    }


def validate_qualification(artifact: Mapping[str, Any]) -> dict[str, Any]:
    wounds: list[str] = []
    calls = artifact.get("calls", [])
    if len(calls) != 2:
        wounds.append("QUALIFICATION_CALL_COUNT_MISMATCH")
    if artifact.get("scientific_schedule_entries_consumed") != 0:
        wounds.append("SCIENTIFIC_SCHEDULE_CONSUMED")
    expected_schema = structured_action_response_format(ACTION_ENUM)
    for token, call in zip(ACTION_ENUM, calls):
        qualification_id = f"non-scientific-act-{token[-1].lower()}"
        if call.get("qualification_id") != qualification_id:
            wounds.append(f"{token}:QUALIFICATION_ORDER_MISMATCH")
        try:
            visible = json.loads(str(call["serialized_policy_visible_request"]))
        except Exception:
            wounds.append(f"{token}:UNREADABLE_POLICY_INPUT")
            continue
        if visible != _qualification_expected_visible(token):
            wounds.append(f"{token}:POLICY_INPUT_MISMATCH")
        serialized = str(call["serialized_policy_visible_request"])
        if any(term in serialized for term in (RED, BLUE, ALPHA, BETA, '"F"', '"P"')):
            wounds.append(f"{token}:SCIENTIFIC_SEMANTICS_LEAKED")
        if call.get("actuation_constraint") != expected_schema:
            wounds.append(f"{token}:SCHEMA_MISMATCH")
        if call.get("action_schema_hash") != action_schema_hash():
            wounds.append(f"{token}:SCHEMA_HASH_MISMATCH")
        if call.get("selected_action") != token:
            wounds.append(f"{token}:TOKEN_TRAVERSAL_FAILED")
        if call.get("parsed_requested_action") != token:
            wounds.append(f"{token}:PARSED_TOKEN_MISMATCH")
        if call.get("conversation_state_supplied") is not False:
            wounds.append(f"{token}:CONVERSATION_STATE_SUPPLIED")
        if call.get("tools_supplied") is not False:
            wounds.append(f"{token}:TOOLS_SUPPLIED")
        try:
            http_request = json.loads(str(call["serialized_http_request"]))
        except Exception:
            wounds.append(f"{token}:UNREADABLE_HTTP_REQUEST")
        else:
            expected_message = {
                "role": "user",
                "content": _canonical_json(_qualification_expected_visible(token)),
            }
            if http_request.get("messages") != [expected_message]:
                wounds.append(f"{token}:NONSTATELESS_HTTP_REQUEST")
            if http_request.get("response_format") != expected_schema:
                wounds.append(f"{token}:HTTP_SCHEMA_MISMATCH")
            if http_request.get("model") != MODEL_IDENTIFIER:
                wounds.append(f"{token}:MODEL_MISMATCH")
            for key, value in SAMPLING_SETTINGS.items():
                if http_request.get(key) != value:
                    wounds.append(f"{token}:SAMPLING_MISMATCH:{key}")
    return {
        "status": "PASS" if not wounds else "FAIL",
        "wounds": wounds,
        "calls_retained": len(calls),
        "scientific_schedule_entries_consumed": artifact.get(
            "scientific_schedule_entries_consumed"
        ),
    }


def qualify_once(execution_basis_commit: str) -> dict[str, Any]:
    if not execution_basis_commit.strip():
        raise ValueError("execution basis commit must be supplied")
    freeze = load_validated_freeze()
    if QUALIFICATION_PATH.exists():
        raise RuntimeError(f"refusing to overwrite qualification: {QUALIFICATION_PATH}")
    if any(path.exists() for path in EMPIRICAL_PATHS):
        raise RuntimeError("empirical evidence already exists")

    calls: list[dict[str, Any]] = []
    for token in ACTION_ENUM:
        adapter = _new_adapter()
        selected: str | None = None
        failure: str | None = None
        try:
            selected = adapter(QUALIFICATION_TASKS[token], ())
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
        records = adapter.call_records
        if len(records) == 1:
            calls.append(
                {
                    "qualification_id": f"non-scientific-act-{token[-1].lower()}",
                    "requested_token": token,
                    "selected_token": selected,
                    "qualification_failure": failure,
                    **records[0],
                }
            )

    artifact: dict[str, Any] = {
        "artifact": "behavioral_coupling_action_delexicalization_qualification_v0",
        "artifact_class": "NON_SCIENTIFIC_INTERFACE_QUALIFICATION",
        "protocol_sha256": freeze["protocol_sha256"],
        "schedule_sha256": freeze["schedule_sha256"],
        "action_schema_sha256": freeze["action_schema_sha256"],
        "execution_basis_commit": execution_basis_commit,
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "calls": calls,
        "scientific_schedule_entries_consumed": 0,
        "empirical_model_calls_made": 0,
        "P3_status": "BLOCKED_NOT_EXECUTED",
        "scientific_adjudication": "NOT_PERFORMED",
    }
    result = validate_qualification(artifact)
    artifact["result"] = result
    _write_new_json(QUALIFICATION_PATH, artifact)
    return artifact


def load_validated_qualification() -> dict[str, Any]:
    if not QUALIFICATION_PATH.exists():
        raise RuntimeError("ACT_A/ACT_B qualification evidence is missing")
    artifact = json.loads(QUALIFICATION_PATH.read_text(encoding="utf-8"))
    result = validate_qualification(artifact)
    if result["status"] != "PASS":
        raise RuntimeError("ACT_A/ACT_B qualification did not pass")
    if artifact.get("result") != result:
        raise RuntimeError("qualification result does not reconstruct")
    return artifact


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
    events: list[dict[str, Any]] = []
    symbol = str(spec["observation_symbol"])
    hidden = str(spec["hidden_target_color"])
    condition = str(spec["condition"])
    contract = str(spec["action_contract"])
    _append_event(
        events,
        "WORLD_STATE_ESTABLISHED",
        policy_visible=False,
        payload={
            "hidden_target_color": hidden,
            "mapping": spec["mapping"],
            "mapping_declaration_order": spec["mapping_declaration_order"],
            "mapping_rows": spec["mapping_rows"],
            "serialized_mapping_text": spec["serialized_mapping_text"],
            "action_contract": contract,
            "action_contract_rows": spec["action_contract_rows"],
            "serialized_action_contract_text": spec[
                "serialized_action_contract_text"
            ],
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

    requested: str | None
    policy_error: str | None = None
    try:
        requested = adapter(
            fixed_task(
                str(spec["mapping"]),
                str(spec["mapping_declaration_order"]),
                contract,
            ),
            _visible_history(events),
        )
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
    implied_target = (
        ACTION_CONTRACTS[contract][accepted] if accepted is not None else None
    )

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
            "ACTION_CONTRACT_APPLIED",
            policy_visible=False,
            payload={
                "action_contract": contract,
                "accepted_typed_action": accepted,
                "implied_target_color": implied_target,
            },
        )
        _append_event(
            events,
            "TERMINAL_COMMITMENT",
            policy_visible=False,
            payload={
                "accepted_typed_action": accepted,
                "action_implied_target_color": implied_target,
            },
        )
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
        "typed_requested_action": requested,
        "world_accepted_action": accepted,
        "action_implied_target_color": implied_target,
        "correct": implied_target == hidden,
        "valid": True,
        "failure_class": failure,
    }


def _expected_visible(spec: Mapping[str, Any]) -> dict[str, Any]:
    history = [{"event_type": "INSPECT_EXECUTED", "payload": {"action": INSPECT}}]
    if spec["condition"] == CONDITION_F:
        history.append(
            {
                "event_type": "SYMBOL_OBSERVATION_DELIVERED",
                "payload": {"symbol": spec["observation_symbol"]},
            }
        )
    return {
        "fixed_task": fixed_task(
            str(spec["mapping"]),
            str(spec["mapping_declaration_order"]),
            str(spec["action_contract"]),
        ),
        "policy_visible_protocol_history": history,
        "legal_action_vocabulary": list(ACTION_ENUM),
    }


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

    expected_schema = structured_action_response_format(ACTION_ENUM)
    for spec, episode, call in zip(schedule, episodes, calls):
        episode_id = str(spec["episode_id"])
        for key in (
            "mapping",
            "mapping_declaration_order",
            "mapping_rows",
            "serialized_mapping_text",
            "first_mapping_row_target_color",
            "observation_symbol",
            "hidden_target_color",
            "condition",
            "action_contract",
            "action_contract_rows",
            "serialized_action_contract_text",
            "correct_typed_action",
        ):
            if episode.get(key) != spec[key]:
                wounds.append(f"{episode_id}:EPISODE_SPEC_MISMATCH:{key}")
        try:
            visible = json.loads(str(call["serialized_policy_visible_request"]))
        except Exception:
            wounds.append(f"{episode_id}:UNREADABLE_POLICY_INPUT")
            continue
        expected_visible = _expected_visible(spec)
        if visible != expected_visible:
            wounds.append(f"{episode_id}:POLICY_VISIBILITY_MISMATCH")
        if any(
            forbidden in visible
            for forbidden in (
                "condition",
                "schedule",
                "schedule_position",
                "hidden_target_color",
                "correct_typed_action",
                "prior_episode",
            )
        ):
            wounds.append(f"{episode_id}:FORBIDDEN_VISIBLE_METADATA")
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
                "content": _canonical_json(expected_visible),
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
        if call.get("selected_action") != episode.get("typed_requested_action"):
            wounds.append(f"{episode_id}:TYPED_ACTION_BOUNDARY_MISMATCH")
        accepted = episode.get("world_accepted_action")
        if accepted != episode.get("typed_requested_action") and accepted is not None:
            wounds.append(f"{episode_id}:WORLD_RECEIPT_MISMATCH")
        independently_implied = (
            ACTION_CONTRACTS[str(spec["action_contract"])][str(accepted)]
            if accepted in ACTION_ENUM
            else None
        )
        if episode.get("action_implied_target_color") != independently_implied:
            wounds.append(f"{episode_id}:ACTION_CONTRACT_APPLICATION_MISMATCH")
        independently_correct = independently_implied == spec["hidden_target_color"]
        if episode.get("correct") is not independently_correct:
            wounds.append(f"{episode_id}:SCORING_MISMATCH")
        if episode.get("valid") is not True:
            wounds.append(f"{episode_id}:EPISODE_NOT_RETAINED_VALID")

    return {
        "status": "VALID" if not wounds else "EXPERIMENT_INVALID",
        "invalidity_wounds": wounds,
        "wrong_actions_are_behavior_not_invalidity": True,
        "episodes_retained": len(episodes),
        "calls_retained": len(calls),
        "empirical_retries": 0,
    }


def _action_counts(episodes: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "episodes": len(episodes),
        "ACT_A": sum(e["world_accepted_action"] == ACT_A for e in episodes),
        "ACT_B": sum(e["world_accepted_action"] == ACT_B for e in episodes),
        "correct": sum(bool(e["correct"]) for e in episodes),
        "failures": sum(e["world_accepted_action"] is None for e in episodes),
        "protocol_invalid": sum(e.get("valid") is not True for e in episodes),
    }


def _select(
    episodes: Sequence[Mapping[str, Any]], **coordinates: str
) -> list[Mapping[str, Any]]:
    return [
        episode
        for episode in episodes
        if all(episode[key] == value for key, value in coordinates.items())
    ]


def summarize(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    cells: dict[str, Any] = {}
    presentation_contract: dict[str, Any] = {}
    first_row_target: dict[str, Any] = {}
    world_target: dict[str, Any] = {}
    typed_action: dict[str, Any] = {}

    for mapping in MAPPINGS:
        cells[mapping] = {}
        presentation_contract[mapping] = {}
        for order in DECLARATION_ORDERS:
            cells[mapping][order] = {}
            presentation_contract[mapping][order] = {}
            for contract in ACTION_CONTRACTS_ORDER:
                cells[mapping][order][contract] = {}
                presentation_contract[mapping][order][contract] = {
                    condition: _action_counts(
                        _select(
                            episodes,
                            mapping=mapping,
                            mapping_declaration_order=order,
                            action_contract=contract,
                            condition=condition,
                        )
                    )
                    for condition in CONDITIONS
                }
                for symbol in SYMBOLS:
                    cells[mapping][order][contract][symbol] = {}
                    for condition in CONDITIONS:
                        selected = _select(
                            episodes,
                            mapping=mapping,
                            mapping_declaration_order=order,
                            action_contract=contract,
                            observation_symbol=symbol,
                            condition=condition,
                        )
                        cells[mapping][order][contract][symbol][condition] = [
                            {
                                "target_color": episode["hidden_target_color"],
                                "typed_action": episode["world_accepted_action"],
                                "action_implied_target_color": episode[
                                    "action_implied_target_color"
                                ],
                                "correct": episode["correct"],
                                "valid": episode["valid"],
                                "failure_class": episode["failure_class"],
                            }
                            for episode in selected
                        ][0]

    for color in (RED, BLUE):
        first_row_target[color] = {
            contract: {
                condition: _action_counts(
                    _select(
                        episodes,
                        first_mapping_row_target_color=color,
                        action_contract=contract,
                        condition=condition,
                    )
                )
                for condition in CONDITIONS
            }
            for contract in ACTION_CONTRACTS_ORDER
        }
        world_target[color] = {
            contract: {
                condition: _action_counts(
                    _select(
                        episodes,
                        hidden_target_color=color,
                        action_contract=contract,
                        condition=condition,
                    )
                )
                for condition in CONDITIONS
            }
            for contract in ACTION_CONTRACTS_ORDER
        }

    for action in ACTION_ENUM:
        typed_action[action] = {
            condition: {
                "selected": sum(
                    episode["world_accepted_action"] == action
                    and episode["condition"] == condition
                    for episode in episodes
                ),
                "correct": sum(
                    episode["world_accepted_action"] == action
                    and episode["condition"] == condition
                    and bool(episode["correct"])
                    for episode in episodes
                ),
            }
            for condition in CONDITIONS
        }

    return {
        "individual_cells": cells,
        "by_first_mapping_row_target_color_action_contract_condition": (
            first_row_target
        ),
        "by_world_target_color_action_contract_condition": world_target,
        "by_typed_action_identity_condition": typed_action,
        "by_mapping_presentation_action_contract_condition": presentation_contract,
    }


def execute_once(execution_basis_commit: str) -> dict[str, Any]:
    if not execution_basis_commit.strip():
        raise ValueError("execution basis commit must be supplied")
    freeze = load_validated_freeze()
    qualification = load_validated_qualification()
    for path in EMPIRICAL_PATHS:
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
            calls.append({"episode_id": spec["episode_id"], **records[0]})

    validity = validate_evidence(schedule, episodes, calls)
    descriptive_summary = summarize(episodes)
    common = {
        "pressure": "P2_ACTION_DELEXICALIZATION",
        "protocol_version": PROTOCOL_VERSION,
        "protocol_sha256": freeze["protocol_sha256"],
        "schedule_sha256": freeze["schedule_sha256"],
        "action_schema_sha256": freeze["action_schema_sha256"],
        "freeze_path": str(FREEZE_PATH).replace("\\", "/"),
        "qualification_path": str(QUALIFICATION_PATH).replace("\\", "/"),
        "qualification_result": qualification["result"],
        "execution_basis_commit": execution_basis_commit,
        "adapter_repository_commit": ADAPTER_AUTHORITY_COMMIT,
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "scoring_rule": SCORING_RULE,
        "descriptive_summary": descriptive_summary,
        "validity": validity,
        "empirical_episode_count": len(episodes),
        "empirical_call_count": len(calls),
        "empirical_retry_count": 0,
        "qualification_call_count": 2,
        "P1_revisited": False,
        "P3_status": "BLOCKED_NOT_EXECUTED",
        "P3_empirical_calls": 0,
        "P4_revisited": False,
        "scientific_adjudication": "NOT_PERFORMED",
    }
    world = {
        "artifact": "behavioral_coupling_action_delexicalization_world_v0",
        "artifact_class": "EMPIRICAL_WORLD_TRACE",
        **deepcopy(common),
        "episodes": episodes,
    }
    call_evidence = {
        "artifact": "behavioral_coupling_action_delexicalization_calls_v0",
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
    mode.add_argument("--qualify", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--basis-commit")
    args = parser.parse_args(argv)
    if args.freeze:
        freeze = write_freeze()
        result = {
            "protocol_sha256": freeze["protocol_sha256"],
            "schedule_sha256": freeze["schedule_sha256"],
            "action_schema_sha256": freeze["action_schema_sha256"],
            "episodes": len(freeze["schedule"]),
            "qualification_model_calls_made": 0,
            "empirical_model_calls_made": 0,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if not args.basis_commit:
        parser.error("--qualify and --execute require --basis-commit")
    if args.qualify:
        artifact = qualify_once(args.basis_commit)
        print(json.dumps(artifact["result"], indent=2, sort_keys=True))
        return 0 if artifact["result"]["status"] == "PASS" else 2
    result = execute_once(args.basis_commit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["validity"]["status"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
