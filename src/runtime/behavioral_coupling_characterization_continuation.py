"""One-shot executor for the independently qualified P1/P2/P4 subset."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from src.runtime.behavioral_coupling_characterization import (
    ACTION_ENUM_BR,
    ACTION_ENUM_RB,
    BR,
    FREEZE_PATH,
    MODEL_IDENTIFIER,
    P1_CALLS_PATH,
    P1_SCORING,
    P1_WORLD_PATH,
    P2_CALLS_PATH,
    P2_SCORING,
    P2_WORLD_PATH,
    P3_CALLS_PATH,
    P3_WORLD_PATH,
    P4_CALLS_PATH,
    P4_SCORING,
    P4_WORLD_PATH,
    QUALIFICATION_PATH,
    RB,
    SAMPLING_SETTINGS,
    _run_custom_pressure,
    _run_p1,
    _run_p2_episode,
    _run_p4_episode,
    _sha256,
    _summarize_p2,
    _summarize_p4,
    _write_new_json,
)
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    structured_action_response_format,
    structured_action_schema_hash,
)


CONTINUATION_DOCUMENT = (
    "docs/methods/Consequence_Surface/"
    "Behavioral_Coupling_Characterization_Continuation_v0.md"
)
CONTINUATION_SUMMARY_PATH = Path(
    "traces/behavioral_coupling_qualified_subset_summary_v0.json"
)
CONTINUATION_MATRIX_PATH = Path(
    "traces/behavioral_coupling_qualified_subset_matrix_v0.json"
)
BASELINE_QUALIFICATION_PATH = Path(
    "traces/bounded_consequential_feedback_lm_studio_"
    "constrained_qualification_v0.json"
)

EXPECTED_PROTOCOL_HASH = (
    "sha256:fc4c1d8a32f1dd9c844bcaa12b4edb3057ae72d716be517a38c9d15ab5524b68"
)
EXPECTED_SCHEDULE_HASHES = {
    "P1": "sha256:6c442c4d81ed10024a1115b1ab9a8119d9690aa1683ec6de81011d460395b98f",
    "P2": "sha256:3514df11e5a119ac36b8a787f5abd8a0d03d2ab1d270fab0c0ba29d9bc62fc3f",
    "P3": "sha256:049938ca737f44f2455c7de3dd89cccb5358104eb1acd50ff6688fe07786cdc5",
    "P4": "sha256:f4168239b66f9cbed3e6553a71b9a6cdb49cb2cebb76f7e5d4637d8af0bb976c",
}
EXPECTED_ADAPTER_COMMIT = "d60ce2044fb2215e58eec74de8e311ba42765bc0"

OUTPUT_PATHS = (
    P1_WORLD_PATH,
    P1_CALLS_PATH,
    P2_WORLD_PATH,
    P2_CALLS_PATH,
    P4_WORLD_PATH,
    P4_CALLS_PATH,
    CONTINUATION_SUMMARY_PATH,
    CONTINUATION_MATRIX_PATH,
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_continuation_basis() -> dict[str, Any]:
    freeze = _load_json(FREEZE_PATH)
    qualification = _load_json(QUALIFICATION_PATH)
    baseline_qualification = _load_json(BASELINE_QUALIFICATION_PATH)

    if freeze["battery_protocol_sha256"] != EXPECTED_PROTOCOL_HASH:
        raise RuntimeError("original battery protocol commitment differs")
    if freeze["schedule_commitments"] != EXPECTED_SCHEDULE_HASHES:
        raise RuntimeError("original schedule commitments differ")
    if freeze["adapter_repository_commit"] != EXPECTED_ADAPTER_COMMIT:
        raise RuntimeError("frozen adapter commit differs")
    for pressure, expected_hash in EXPECTED_SCHEDULE_HASHES.items():
        if _sha256(freeze["schedules"][pressure]) != expected_hash:
            raise RuntimeError(f"{pressure} committed schedule cannot be reconstructed")
    if {key: len(value) for key, value in freeze["schedules"].items()} != {
        "P1": 32,
        "P2": 16,
        "P3": 16,
        "P4": 16,
    }:
        raise RuntimeError("frozen schedule cardinality differs")

    if not baseline_qualification.get("qualification_passed"):
        raise RuntimeError("ordinary RB qualification is not reconstructable")
    if qualification.get("qualification_calls_made") != 5:
        raise RuntimeError("stopped qualification call count differs")
    if qualification.get("frozen_schedule_entries_consumed") != 0:
        raise RuntimeError("stopped qualification consumed schedule entries")
    if qualification.get("BR_passed") is not True:
        raise RuntimeError("BR qualified status is absent")
    if qualification.get("RBD_passed") is not False:
        raise RuntimeError("RBD blocked status is absent")

    results = qualification["qualification_results"]
    br_results = [row for row in results if row["schema_realization"] == BR]
    if [row["expected_action"] for row in br_results] != [
        "SUBMIT_BLUE",
        "SUBMIT_RED",
    ]:
        raise RuntimeError("BR qualification task order differs")
    if not all(row["passed"] for row in br_results):
        raise RuntimeError("BR traversal qualification is incomplete")
    for row in br_results:
        call = row["call_evidence"]
        visible = json.loads(call["serialized_policy_visible_request"])
        if visible["legal_action_vocabulary"] != list(ACTION_ENUM_RB):
            raise RuntimeError("BR visible legal vocabulary differs")
        if call["actuation_constraint"] != structured_action_response_format(
            ACTION_ENUM_BR
        ):
            raise RuntimeError("BR constrained enum differs")
        if call["action_schema_hash"] != structured_action_schema_hash(
            ACTION_ENUM_BR
        ):
            raise RuntimeError("BR schema hash differs")

    defer_result = next(
        row for row in results if row["expected_action"] == "DEFER"
    )
    if (
        defer_result["schema_realization"] != "RBD"
        or defer_result["selected_action"] != "SUBMIT_RED"
        or defer_result["passed"] is not False
    ):
        raise RuntimeError("P3 qualification wound differs")

    if P3_WORLD_PATH.exists() or P3_CALLS_PATH.exists():
        raise RuntimeError("P3 empirical evidence exists despite blocked status")

    return {
        "freeze": freeze,
        "qualification": qualification,
        "eligible_pressures": ["P1", "P2", "P4"],
        "blocked_pressure": "P3",
        "blocked_reason": (
            "RBD actuation realization failed pre-execution DEFER traversal "
            "qualification"
        ),
    }


def _add_continuation_commit(
    artifacts: tuple[dict[str, Any], dict[str, Any]],
    continuation_commit: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    for artifact in artifacts:
        artifact["continuation_authorization"] = CONTINUATION_DOCUMENT
        artifact["continuation_execution_commit"] = continuation_commit
        artifact["P3_status"] = "BLOCKED_AT_QUALIFICATION_NOT_EXECUTED"
    return artifacts


def _p2_symbol_summary(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for mapping in ("M1", "M2"):
        summary[mapping] = {}
        for symbol in ("ALPHA", "BETA"):
            summary[mapping][symbol] = {}
            for condition in ("F", "P"):
                selected = [
                    episode
                    for episode in episodes
                    if episode["mapping"] == mapping
                    and episode["observation_symbol"] == symbol
                    and episode["condition"] == condition
                ]
                summary[mapping][symbol][condition] = {
                    "episodes": len(selected),
                    "red": sum(
                        row["accepted_terminal_action"] == "SUBMIT_RED"
                        for row in selected
                    ),
                    "blue": sum(
                        row["accepted_terminal_action"] == "SUBMIT_BLUE"
                        for row in selected
                    ),
                    "correct": sum(bool(row["correct"]) for row in selected),
                    "failures": sum(
                        row["accepted_terminal_action"] is None for row in selected
                    ),
                }
    return summary


def _matrix(
    p1: dict[str, Any],
    p2: dict[str, Any],
    p4: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact": "behavioral_coupling_qualified_subset_matrix_v0",
        "artifact_class": "DESCRIPTIVE_CONTINUATION_CROSS_REFERENCE",
        "original_battery_protocol_sha256": EXPECTED_PROTOCOL_HASH,
        "rows": [
            {
                "pressure": "P1",
                "intervention": "RB versus BR structured enum order",
                "held_fixed": (
                    "world, task, feedback, scoring, visible legal vocabulary, "
                    "model, and sampling"
                ),
                "action_distribution": p1["descriptive_summary"],
                "outcome_distribution": {
                    schema: {
                        condition: counts["correct"]
                        for condition, counts in by_condition.items()
                    }
                    for schema, by_condition in p1["descriptive_summary"].items()
                },
                "validity": p1["validity"],
            },
            {
                "pressure": "P2",
                "intervention": "M1 versus M2 visible symbol-to-color mapping",
                "held_fixed": (
                    "target balance, RB action surface, model, sampling, and "
                    "F/P timing"
                ),
                "action_distribution": p2["descriptive_summary"],
                "outcome_distribution": {
                    mapping: {
                        condition: counts["correct"]
                        for condition, counts in by_condition.items()
                    }
                    for mapping, by_condition in p2["descriptive_summary"].items()
                },
                "validity": p2["validity"],
            },
            {
                "pressure": "P4",
                "intervention": (
                    "supplied CURRENT/FOREIGN role association present versus absent"
                ),
                "held_fixed": (
                    "conflicting values, value order, CURRENT target, RB action "
                    "surface, model, and sampling"
                ),
                "action_distribution": p4["descriptive_summary"],
                "outcome_distribution": {
                    regime: counts["correct"]
                    for regime, counts in p4["descriptive_summary"].items()
                },
                "validity": p4["validity"],
            },
            {
                "pressure": "P3",
                "status": "BLOCKED_AT_QUALIFICATION",
                "empirical_evidence_included": False,
                "reason": (
                    "RBD actuation realization failed pre-execution DEFER "
                    "traversal qualification"
                ),
            },
        ],
        "scientific_adjudication": "NOT_PERFORMED",
    }


def _summary(
    continuation_commit: str,
    completed: list[str],
    *,
    stopped_at: str | None,
    p1: dict[str, Any] | None = None,
    p2: dict[str, Any] | None = None,
    p4: dict[str, Any] | None = None,
) -> dict[str, Any]:
    pressure_artifacts = [artifact for artifact in (p1, p2, p4) if artifact]
    return {
        "artifact": "behavioral_coupling_qualified_subset_summary_v0",
        "artifact_class": "EMPIRICAL_CONTINUATION_SUMMARY",
        "continuation_authorization": CONTINUATION_DOCUMENT,
        "continuation_execution_commit": continuation_commit,
        "original_battery_protocol_sha256": EXPECTED_PROTOCOL_HASH,
        "schedule_commitments": {
            key: EXPECTED_SCHEDULE_HASHES[key] for key in ("P1", "P2", "P4")
        },
        "model_identifier": MODEL_IDENTIFIER,
        "endpoint": DEFAULT_ENDPOINT,
        "provider_exposed_sampling_settings": deepcopy(SAMPLING_SETTINGS),
        "adapter_realization": CONSTRAINED_TYPED_ACTION,
        "adapter_repository_commit": EXPECTED_ADAPTER_COMMIT,
        "completed_pressures": completed,
        "stopped_at": stopped_at,
        "empirical_episode_count": sum(
            len(artifact["episodes"]) for artifact in pressure_artifacts
        ),
        "empirical_call_count": sum(
            artifact["validity"]["calls_retained"]
            for artifact in pressure_artifacts
        ),
        "retry_calls": 0,
        "new_qualification_calls": 0,
        "P3": {
            "status": "BLOCKED_NOT_EXECUTED",
            "empirical_calls": 0,
            "reason": (
                "RBD actuation realization failed pre-execution DEFER traversal "
                "qualification"
            ),
        },
        "descriptive_summaries": {
            key: artifact["descriptive_summary"]
            for key, artifact in (("P1", p1), ("P2", p2), ("P4", p4))
            if artifact is not None
        },
        "scientific_adjudication": "NOT_PERFORMED",
    }


def execute_qualified_subset_once(continuation_commit: str) -> dict[str, Any]:
    basis = validate_continuation_basis()
    for path in OUTPUT_PATHS:
        if path.exists():
            raise RuntimeError(f"one-shot continuation evidence exists: {path}")

    freeze = basis["freeze"]
    schedules = freeze["schedules"]
    completed: list[str] = []

    p1_pair = _add_continuation_commit(
        _run_p1(
            EXPECTED_ADAPTER_COMMIT,
            frozen_schedule=schedules["P1"],
        ),
        continuation_commit,
    )
    _write_new_json(P1_WORLD_PATH, p1_pair[0])
    _write_new_json(P1_CALLS_PATH, p1_pair[1])
    if p1_pair[0]["validity"]["status"] != "VALID":
        summary = _summary(
            continuation_commit, completed, stopped_at="P1", p1=p1_pair[0]
        )
        _write_new_json(CONTINUATION_SUMMARY_PATH, summary)
        return summary
    completed.append("P1")

    p2_pair = _add_continuation_commit(
        _run_custom_pressure(
            "P2",
            [deepcopy(row) for row in schedules["P2"]],
            ACTION_ENUM_RB,
            _run_p2_episode,
            _summarize_p2,
            P2_SCORING,
            EXPECTED_ADAPTER_COMMIT,
        ),
        continuation_commit,
    )
    symbol_summary = _p2_symbol_summary(p2_pair[0]["episodes"])
    p2_pair[0]["descriptive_symbol_summary"] = deepcopy(symbol_summary)
    p2_pair[1]["descriptive_symbol_summary"] = deepcopy(symbol_summary)
    _write_new_json(P2_WORLD_PATH, p2_pair[0])
    _write_new_json(P2_CALLS_PATH, p2_pair[1])
    if p2_pair[0]["validity"]["status"] != "VALID":
        summary = _summary(
            continuation_commit,
            completed,
            stopped_at="P2",
            p1=p1_pair[0],
            p2=p2_pair[0],
        )
        _write_new_json(CONTINUATION_SUMMARY_PATH, summary)
        return summary
    completed.append("P2")

    p4_pair = _add_continuation_commit(
        _run_custom_pressure(
            "P4",
            [deepcopy(row) for row in schedules["P4"]],
            ACTION_ENUM_RB,
            _run_p4_episode,
            _summarize_p4,
            P4_SCORING,
            EXPECTED_ADAPTER_COMMIT,
        ),
        continuation_commit,
    )
    _write_new_json(P4_WORLD_PATH, p4_pair[0])
    _write_new_json(P4_CALLS_PATH, p4_pair[1])
    if p4_pair[0]["validity"]["status"] != "VALID":
        summary = _summary(
            continuation_commit,
            completed,
            stopped_at="P4",
            p1=p1_pair[0],
            p2=p2_pair[0],
            p4=p4_pair[0],
        )
        _write_new_json(CONTINUATION_SUMMARY_PATH, summary)
        return summary
    completed.append("P4")

    matrix = _matrix(p1_pair[0], p2_pair[0], p4_pair[0])
    _write_new_json(CONTINUATION_MATRIX_PATH, matrix)
    summary = _summary(
        continuation_commit,
        completed,
        stopped_at=None,
        p1=p1_pair[0],
        p2=p2_pair[0],
        p4=p4_pair[0],
    )
    summary["cross_reference_matrix"] = CONTINUATION_MATRIX_PATH.as_posix()
    _write_new_json(CONTINUATION_SUMMARY_PATH, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--continuation-commit", required=True)
    args = parser.parse_args()
    result = execute_qualified_subset_once(args.continuation_commit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["completed_pressures"] == ["P1", "P2", "P4"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
