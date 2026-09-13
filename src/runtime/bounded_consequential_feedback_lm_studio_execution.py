"""One-shot authorized LM Studio execution for the frozen feedback schedule."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from src.runtime.bounded_consequential_feedback_experiment import (
    ACTION_VOCABULARY,
    FIXED_TASK,
    compile_frozen_llm_schedule,
    run_frozen_comparison,
)
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    STRUCTURED_ACTION_SCHEMA_HASH,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    structured_action_response_format,
)


MODEL_IDENTIFIER = "hermes-3-llama-3.2-3b"
SAMPLING_SETTINGS = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 16}
EXPECTED_SCHEDULE_COMMITMENT = (
    "sha256:7fec657bbd871259f146ec5cd45da03e30014c6a25ba23d53cb0e6ce62057035"
)
QUALIFICATION_TRACE_PATH = Path("traces") / (
    "bounded_consequential_feedback_lm_studio_constrained_qualification_v0.json"
)
WORLD_TRACE_PATH = Path("traces") / (
    "bounded_consequential_feedback_lm_studio_empirical_world_v0.json"
)
CALL_EVIDENCE_PATH = Path("traces") / (
    "bounded_consequential_feedback_lm_studio_empirical_calls_v0.json"
)


def _config() -> LMStudioEndpointConfig:
    return LMStudioEndpointConfig(
        endpoint=DEFAULT_ENDPOINT,
        model_identifier=MODEL_IDENTIFIER,
        sampling_settings=SAMPLING_SETTINGS,
        timeout_seconds=120.0,
    )


def _write_new_json(path: Path, value: Any) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite one-shot evidence: {path}")
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _qualification_call(
    adapter: LMStudioConstrainedActionPolicyAdapter,
    task: str,
) -> dict[str, Any]:
    try:
        selected_action = adapter(task, ())
    except Exception as exc:
        return {
            "task": task,
            "selected_action": None,
            "call_raised": True,
            "failure": f"{type(exc).__name__}: {exc}",
        }
    return {
        "task": task,
        "selected_action": selected_action,
        "call_raised": False,
        "failure": None,
    }


def _specimen_freeze(adapter_commit: str) -> dict[str, Any]:
    schedule = compile_frozen_llm_schedule()
    if schedule["exact_schedule_commitment"] != EXPECTED_SCHEDULE_COMMITMENT:
        raise RuntimeError("frozen schedule commitment does not match warrant")
    return {
        "model_identifier": MODEL_IDENTIFIER,
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "action_schema": structured_action_response_format(),
        "action_schema_hash": STRUCTURED_ACTION_SCHEMA_HASH,
        "adapter_repository_commit": adapter_commit,
        "schedule_commitment": EXPECTED_SCHEDULE_COMMITMENT,
        "exact_task": FIXED_TASK,
        "action_vocabulary": list(ACTION_VOCABULARY),
        "isolation_confirmations": {
            "prior_episode_conversation_state_supplied": False,
            "repository_context_supplied": False,
            "filesystem_access_supplied": False,
            "tools_supplied": False,
            "mcp_supplied": False,
            "schedule_metadata_supplied": False,
            "condition_identifier_supplied": False,
            "withheld_P_feedback_supplied": False,
            "semantic_output_interpreter_used": False,
        },
    }


def _descriptive_summary(
    world_trace: dict[str, Any],
    call_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    by_episode = {record["episode_id"]: record for record in call_evidence}
    summary: dict[str, Any] = {}
    for condition in ("F", "P"):
        episodes = [
            episode
            for episode in world_trace["episodes"]
            if episode["condition"] == condition
        ]
        calls = [by_episode[episode["episode_id"]] for episode in episodes]
        summary[condition] = {
            "episodes": len(episodes),
            "valid_typed_actions": sum(
                call["selected_action"] in {"SUBMIT_RED", "SUBMIT_BLUE"}
                for call in calls
            ),
            "submit_red": sum(
                call["selected_action"] == "SUBMIT_RED" for call in calls
            ),
            "submit_blue": sum(
                call["selected_action"] == "SUBMIT_BLUE" for call in calls
            ),
            "correct": sum(bool(episode["correct"]) for episode in episodes),
            "actuation_failures": sum(
                call["selected_action"] is None for call in calls
            ),
        }
    summary["protocol_invalid_episodes"] = sum(
        not episode["valid"] for episode in world_trace["episodes"]
    )
    return summary


def execute_authorized_once(adapter_commit: str) -> dict[str, Any]:
    for path in (QUALIFICATION_TRACE_PATH, WORLD_TRACE_PATH, CALL_EVIDENCE_PATH):
        if path.exists():
            raise RuntimeError(f"one-shot execution evidence already exists: {path}")

    qualification_adapter = LMStudioConstrainedActionPolicyAdapter(_config())
    qualification_results = [
        _qualification_call(qualification_adapter, "Select SUBMIT_RED."),
        _qualification_call(qualification_adapter, "Select SUBMIT_BLUE."),
    ]
    qualification_calls = list(qualification_adapter.call_records)
    qualification_passed = (
        len(qualification_calls) == 2
        and qualification_results[0]["selected_action"] == "SUBMIT_RED"
        and qualification_results[1]["selected_action"] == "SUBMIT_BLUE"
        and qualification_calls[0]["structured_output"] == {"action": "SUBMIT_RED"}
        and qualification_calls[1]["structured_output"] == {"action": "SUBMIT_BLUE"}
    )
    qualification_trace = {
        "artifact": (
            "bounded_consequential_feedback_lm_studio_"
            "constrained_qualification_v0"
        ),
        "artifact_class": "NON_SCIENTIFIC_ACTUATION_QUALIFICATION",
        "model_identifier": MODEL_IDENTIFIER,
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "adapter_repository_commit": adapter_commit,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "action_schema": structured_action_response_format(),
        "action_schema_hash": STRUCTURED_ACTION_SCHEMA_HASH,
        "qualification_calls_made": 2,
        "qualification_results": qualification_results,
        "call_evidence": qualification_calls,
        "qualification_passed": qualification_passed,
        "frozen_schedule_entries_consumed": 0,
    }
    _write_new_json(QUALIFICATION_TRACE_PATH, qualification_trace)
    if not qualification_passed:
        return {
            "qualification_passed": False,
            "empirical_schedule_executed": False,
            "qualification_trace": QUALIFICATION_TRACE_PATH.as_posix(),
        }


    specimen_freeze = _specimen_freeze(adapter_commit)
    empirical_adapter = LMStudioConstrainedActionPolicyAdapter(_config())
    world_trace = run_frozen_comparison(
        policy=empirical_adapter,
        policy_identity=MODEL_IDENTIFIER,
        policy_configuration={
            "adapter_realization": CONSTRAINED_TYPED_ACTION,
            "adapter_repository_commit": adapter_commit,
            "endpoint": DEFAULT_ENDPOINT,
            "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
            "action_schema_hash": STRUCTURED_ACTION_SCHEMA_HASH,
        },
    )
    calls = list(empirical_adapter.call_records)
    if len(world_trace["episodes"]) != 16 or len(calls) != 16:
        raise RuntimeError("frozen execution did not retain exactly 16 episodes and calls")
    associated_calls = [
        {"episode_id": episode["episode_id"], **call}
        for episode, call in zip(world_trace["episodes"], calls, strict=True)
    ]
    descriptive_summary = _descriptive_summary(world_trace, associated_calls)
    call_evidence = {
        "artifact": "bounded_consequential_feedback_lm_studio_empirical_calls_v0",
        "artifact_class": "EMPIRICAL_MODEL_CALL_EVIDENCE",
        "specimen_freeze": specimen_freeze,
        "calls": associated_calls,
        "descriptive_summary": descriptive_summary,
        "scientific_adjudication": "NOT_PERFORMED",
    }
    _write_new_json(WORLD_TRACE_PATH, world_trace)
    _write_new_json(CALL_EVIDENCE_PATH, call_evidence)
    return {
        "qualification_passed": True,
        "empirical_schedule_executed": True,
        "qualification_trace": QUALIFICATION_TRACE_PATH.as_posix(),
        "world_trace": WORLD_TRACE_PATH.as_posix(),
        "call_evidence": CALL_EVIDENCE_PATH.as_posix(),
        "descriptive_summary": descriptive_summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-commit", required=True)
    args = parser.parse_args()
    result = execute_authorized_once(args.adapter_commit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["qualification_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
