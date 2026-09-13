"""Frozen P2 mapping-meaning versus declaration-row-order pressure.

This module extends only the already-recorded P2 semantic-indirection surface.
It freezes a 16-cell factorial schedule before inference and executes that
schedule once through the existing stateless constrained-action adapter.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from src.runtime.behavioral_coupling_characterization import (
    ACTION_ENUM_RB,
    ALPHA,
    BETA,
    M1,
    M2,
    MODEL_IDENTIFIER,
    P2_MAPPINGS,
    P2_TASKS,
    SAMPLING_SETTINGS,
)
from src.runtime.bounded_consequential_feedback_experiment import (
    CONDITION_F,
    CONDITION_P,
    INSPECT,
    SUBMIT_BLUE,
    SUBMIT_RED,
)
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    structured_action_response_format,
    structured_action_schema_hash,
)


PROTOCOL_VERSION = "behavioral_coupling_mapping_row_order_v0"
REPOSITORY_AUTHORITY_COMMIT = "76ffb23f2f0826dbd0dc13302bcf93091f971d2a"
ADAPTER_AUTHORITY_COMMIT = "d60ce2044fb2215e58eec74de8e311ba42765bc0"
PRIOR_P2_WORLD = "traces/behavioral_coupling_p2_semantic_indirection_world_v0.json"
PRIOR_P2_CALLS = "traces/behavioral_coupling_p2_semantic_indirection_calls_v0.json"

AB = "AB"
BA = "BA"
DECLARATION_ORDERS = (AB, BA)
MAPPINGS = (M1, M2)
SYMBOLS = (ALPHA, BETA)
CONDITIONS = (CONDITION_F, CONDITION_P)

PROTOCOL_PATH = Path("docs/methods/Consequence_Surface") / (
    "Behavioral_Coupling_Mapping_Row_Order_v0.md"
)
FREEZE_PATH = Path("traces/behavioral_coupling_mapping_row_order_freeze_v0.json")
WORLD_PATH = Path("traces/behavioral_coupling_mapping_row_order_world_v0.json")
CALLS_PATH = Path("traces/behavioral_coupling_mapping_row_order_calls_v0.json")
OUTPUT_PATHS = (WORLD_PATH, CALLS_PATH)

SCORING_RULE = (
    "correct iff the accepted action matches the authoritative target color"
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
    return "sha256:" + hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def mapping_rows(mapping: str, declaration_order: str) -> list[dict[str, str]]:
    if mapping not in P2_MAPPINGS:
        raise ValueError(f"unknown mapping: {mapping}")
    if declaration_order not in DECLARATION_ORDERS:
        raise ValueError(f"unknown declaration order: {declaration_order}")
    symbols = SYMBOLS if declaration_order == AB else tuple(reversed(SYMBOLS))
    return [
        {"symbol": symbol, "color": P2_MAPPINGS[mapping][symbol]}
        for symbol in symbols
    ]


def serialized_mapping_text(mapping: str, declaration_order: str) -> str:
    return "; ".join(
        f"{row['symbol']} -> {row['color']}"
        for row in mapping_rows(mapping, declaration_order)
    )


def fixed_task(mapping: str, declaration_order: str) -> str:
    task = (
        "Submit the color matching the authoritative target. INSPECT reports "
        f"a symbol under this declared mapping: "
        f"{serialized_mapping_text(mapping, declaration_order)}. "
        "Respond with exactly SUBMIT_RED or SUBMIT_BLUE."
    )
    if declaration_order == AB and task != P2_TASKS[mapping]:
        raise RuntimeError("AB task no longer reconstructs the committed P2 task")
    return task


def compile_schedule() -> list[dict[str, Any]]:
    return [
        {
            "episode_id": (
                f"p2-row-order-{mapping.lower()}-{declaration_order.lower()}-"
                f"{symbol.lower()}-{condition.lower()}"
            ),
            "mapping": mapping,
            "declaration_order": declaration_order,
            "mapping_rows": mapping_rows(mapping, declaration_order),
            "serialized_mapping_text": serialized_mapping_text(
                mapping, declaration_order
            ),
            "observation_symbol": symbol,
            "hidden_target_color": P2_MAPPINGS[mapping][symbol],
            "condition": condition,
        }
        for mapping in MAPPINGS
        for declaration_order in DECLARATION_ORDERS
        for symbol in SYMBOLS
        for condition in CONDITIONS
    ]


def build_protocol_declaration() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "status": "FROZEN_BEFORE_EMPIRICAL_EXECUTION",
        "repository_authority_commit": REPOSITORY_AUTHORITY_COMMIT,
        "prior_p2_evidence": {
            "world": PRIOR_P2_WORLD,
            "calls": PRIOR_P2_CALLS,
        },
        "research_question": (
            "Holding symbol-to-color meaning fixed, does reversing mapping-row "
            "declaration order change accepted action selection, and holding row "
            "position fixed, does reversing mapping meaning change behavior?"
        ),
        "intervention": {
            "semantic_mappings": deepcopy(P2_MAPPINGS),
            "declaration_orders": {
                AB: [ALPHA, BETA],
                BA: [BETA, ALPHA],
            },
            "presentations": {
                mapping: {
                    order: {
                        "mapping_rows": mapping_rows(mapping, order),
                        "serialized_mapping_text": serialized_mapping_text(
                            mapping, order
                        ),
                        "fixed_task": fixed_task(mapping, order),
                    }
                    for order in DECLARATION_ORDERS
                }
                for mapping in MAPPINGS
            },
            "semantic_mapping_is_not_declaration_order": True,
        },
        "factorial": {
            "mapping": list(MAPPINGS),
            "declaration_order": list(DECLARATION_ORDERS),
            "symbol": list(SYMBOLS),
            "condition": list(CONDITIONS),
            "episodes_per_cell": 1,
            "total_episodes": 16,
        },
        "conditions": {
            CONDITION_F: "symbol delivered before terminal commitment",
            CONDITION_P: "symbol withheld until after terminal commitment",
        },
        "held_fixed": {
            "model_identifier": MODEL_IDENTIFIER,
            "endpoint": DEFAULT_ENDPOINT,
            "sampling": deepcopy(SAMPLING_SETTINGS),
            "actuation": CONSTRAINED_TYPED_ACTION,
            "legal_actions": list(ACTION_ENUM_RB),
            "action_schema_hash": structured_action_schema_hash(ACTION_ENUM_RB),
            "world_scoring": SCORING_RULE,
            "symbol_alphabet": list(SYMBOLS),
            "feedback_timing_semantics": "committed P2 F/P semantics",
            "stateless_episode_requests": True,
            "tools_or_mcp_supplied": False,
            "repository_or_filesystem_supplied": False,
        },
        "validity": {
            "wrong_actions_are_behavior_not_invalidity": True,
            "no_empirical_retries": True,
            "invalidity_conditions": [
                "wrong mapping delivered",
                "wrong row order serialized",
                "hidden target leakage",
                "F/P delivery error",
                "schedule mutation",
                "action-schema mutation",
                "retry replacement",
                "prior episode context leakage",
                "semantic repair",
            ],
        },
        "scientific_boundary": {
            "may_establish": (
                "bounded dependence or independence between declared relation "
                "meaning and declaration position/order for this coupled realization"
            ),
            "does_not_establish": [
                "general relational reasoning",
                "symbolic reasoning",
                "agency",
                "model-internal mechanism",
                "stable cognitive bias",
                "general coordinate invariance",
                "distinction orchestrator",
            ],
            "scientific_adjudication": "NOT_PERFORMED",
        },
        "stop_after_pressure": True,
    }


def protocol_hash() -> str:
    return _sha256(build_protocol_declaration())


def schedule_hash() -> str:
    return _sha256(compile_schedule())


def build_freeze_artifact() -> dict[str, Any]:
    protocol = build_protocol_declaration()
    schedule = compile_schedule()
    return {
        "artifact": "behavioral_coupling_mapping_row_order_freeze_v0",
        "artifact_class": "PRE_EXECUTION_PROTOCOL_AND_SCHEDULE_FREEZE",
        "protocol": protocol,
        "protocol_sha256": _sha256(protocol),
        "schedule": schedule,
        "schedule_sha256": _sha256(schedule),
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
    expected = build_freeze_artifact()
    if freeze != expected:
        raise RuntimeError("committed freeze differs from reconstructed protocol")
    if freeze["protocol_sha256"] != protocol_hash():
        raise RuntimeError("protocol commitment mismatch")
    if freeze["schedule_sha256"] != schedule_hash():
        raise RuntimeError("schedule commitment mismatch")
    if len(freeze["schedule"]) != 16:
        raise RuntimeError("frozen schedule must contain exactly 16 episodes")
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
        action_enum=ACTION_ENUM_RB,
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
    events: list[dict[str, Any]] = []
    hidden = str(spec["hidden_target_color"])
    symbol = str(spec["observation_symbol"])
    condition = str(spec["condition"])
    _append_event(
        events,
        "WORLD_STATE_ESTABLISHED",
        policy_visible=False,
        payload={
            "hidden_target_color": hidden,
            "mapping": spec["mapping"],
            "declaration_order": spec["declaration_order"],
            "mapping_rows": spec["mapping_rows"],
            "serialized_mapping_text": spec["serialized_mapping_text"],
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
            fixed_task(str(spec["mapping"]), str(spec["declaration_order"])),
            _visible_history(events),
        )
    except Exception as exc:
        requested = None
        policy_error = f"{type(exc).__name__}: {exc}"

    failure: str | None = None
    accepted: str | None = None
    if policy_error is not None:
        failure = "POLICY_INVOCATION_FAILURE"
    elif requested not in ACTION_ENUM_RB:
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
            payload={"accepted_terminal_action": accepted},
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
        "requested_action": requested,
        "accepted_terminal_action": accepted,
        "correct": accepted == f"SUBMIT_{hidden}",
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
            str(spec["mapping"]), str(spec["declaration_order"])
        ),
        "policy_visible_protocol_history": history,
        "legal_action_vocabulary": list(ACTION_ENUM_RB),
    }


def validate_evidence(
    schedule: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
    calls: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    wounds: list[str] = []
    if len(schedule) != 16:
        wounds.append("SCHEDULE_COUNT_MISMATCH")
    if len(episodes) != len(schedule):
        wounds.append("EPISODE_COUNT_MISMATCH")
    if len(calls) != len(schedule):
        wounds.append("CALL_COUNT_MISMATCH")
    expected_ids = [str(spec["episode_id"]) for spec in schedule]
    if [episode.get("episode_id") for episode in episodes] != expected_ids:
        wounds.append("EPISODE_ORDER_MISMATCH")
    if [call.get("episode_id") for call in calls] != expected_ids:
        wounds.append("CALL_ASSOCIATION_MISMATCH")

    expected_schema = structured_action_response_format(ACTION_ENUM_RB)
    expected_schema_hash = structured_action_schema_hash(ACTION_ENUM_RB)
    for spec, episode, call in zip(schedule, episodes, calls):
        episode_id = str(spec["episode_id"])
        for key in (
            "mapping",
            "declaration_order",
            "mapping_rows",
            "serialized_mapping_text",
            "observation_symbol",
            "hidden_target_color",
            "condition",
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
                "prior_episode",
            )
        ):
            wounds.append(f"{episode_id}:FORBIDDEN_VISIBLE_METADATA")
        if call.get("action_schema_hash") != expected_schema_hash:
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
            messages = http_request.get("messages", [])
            if messages != [{"role": "user", "content": _canonical_json(expected_visible)}]:
                wounds.append(f"{episode_id}:NONSTATELESS_HTTP_REQUEST")
            if http_request.get("model") != MODEL_IDENTIFIER:
                wounds.append(f"{episode_id}:MODEL_MISMATCH")
            for key, value in SAMPLING_SETTINGS.items():
                if http_request.get(key) != value:
                    wounds.append(f"{episode_id}:SAMPLING_MISMATCH:{key}")
            if http_request.get("response_format") != expected_schema:
                wounds.append(f"{episode_id}:HTTP_SCHEMA_MISMATCH")
            if any(
                key in http_request
                for key in ("tools", "integrations", "previous_response_id")
            ):
                wounds.append(f"{episode_id}:FORBIDDEN_HTTP_SURFACE")
        if call.get("selected_action") != episode.get("requested_action"):
            wounds.append(f"{episode_id}:ACTION_BOUNDARY_MISMATCH")
        if episode.get("accepted_terminal_action") != episode.get("requested_action"):
            if episode.get("accepted_terminal_action") is not None:
                wounds.append(f"{episode_id}:WORLD_RECEIPT_MISMATCH")
        expected_correct = episode.get("accepted_terminal_action") == (
            f"SUBMIT_{spec['hidden_target_color']}"
        )
        if episode.get("correct") is not expected_correct:
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


def _count_actions(episodes: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "episodes": len(episodes),
        "red": sum(e["accepted_terminal_action"] == SUBMIT_RED for e in episodes),
        "blue": sum(e["accepted_terminal_action"] == SUBMIT_BLUE for e in episodes),
        "correct": sum(bool(e["correct"]) for e in episodes),
        "failures": sum(e["accepted_terminal_action"] is None for e in episodes),
        "protocol_invalid": sum(e.get("valid") is not True for e in episodes),
    }


def summarize(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {}
    cells: dict[str, Any] = {}
    for mapping in MAPPINGS:
        aggregate[mapping] = {}
        cells[mapping] = {}
        for order in DECLARATION_ORDERS:
            aggregate[mapping][order] = {}
            cells[mapping][order] = {}
            for condition in CONDITIONS:
                aggregate[mapping][order][condition] = _count_actions(
                    [
                        episode
                        for episode in episodes
                        if episode["mapping"] == mapping
                        and episode["declaration_order"] == order
                        and episode["condition"] == condition
                    ]
                )
            for symbol in SYMBOLS:
                cells[mapping][order][symbol] = {
                    condition: _count_actions(
                        [
                            episode
                            for episode in episodes
                            if episode["mapping"] == mapping
                            and episode["declaration_order"] == order
                            and episode["observation_symbol"] == symbol
                            and episode["condition"] == condition
                        ]
                    )
                    for condition in CONDITIONS
                }
    return {
        "mapping_declaration_order_condition": aggregate,
        "mapping_declaration_order_symbol_condition": cells,
    }


def execute_once(execution_basis_commit: str) -> dict[str, Any]:
    if not execution_basis_commit.strip():
        raise ValueError("execution basis commit must be supplied")
    freeze = load_validated_freeze()
    for path in OUTPUT_PATHS:
        if path.exists():
            raise RuntimeError(f"refusing to overwrite existing evidence: {path}")

    schedule = [deepcopy(row) for row in freeze["schedule"]]
    episodes: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for spec in schedule:
        # A fresh adapter per episode makes retained call state episode-local.
        adapter = _new_adapter()
        episode = _run_episode(spec, adapter)
        records = adapter.call_records
        episodes.append(episode)
        if len(records) == 1:
            calls.append({"episode_id": spec["episode_id"], **records[0]})

    validity = validate_evidence(schedule, episodes, calls)
    descriptive_summary = summarize(episodes)
    common = {
        "pressure": "P2_MAPPING_ROW_ORDER",
        "protocol_version": PROTOCOL_VERSION,
        "protocol_sha256": freeze["protocol_sha256"],
        "schedule_sha256": freeze["schedule_sha256"],
        "freeze_path": str(FREEZE_PATH).replace("\\", "/"),
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
        "P1_revisited": False,
        "P3_status": "BLOCKED_NOT_EXECUTED",
        "P3_empirical_calls": 0,
        "P4_revisited": False,
        "scientific_adjudication": "NOT_PERFORMED",
    }
    world = {
        "artifact": "behavioral_coupling_mapping_row_order_world_v0",
        "artifact_class": "EMPIRICAL_WORLD_TRACE",
        **deepcopy(common),
        "episodes": episodes,
    }
    call_evidence = {
        "artifact": "behavioral_coupling_mapping_row_order_calls_v0",
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
                    "episodes": len(freeze["schedule"]),
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
