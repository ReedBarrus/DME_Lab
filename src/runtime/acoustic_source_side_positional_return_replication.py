"""Independent clean-source replication of the bounded PR-019 pressure."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any

from src.runtime.acoustic_basis_entry_pressure import utc_now
from src.runtime.acoustic_positional_transformation_pressure import (
    BLOCK_ORDER,
    CANONICAL_LEDGER_PATH,
    TRIALS_PER_BLOCK,
    _atomic_write_json,
    _sha256_file,
    evaluate_preflight,
)
from src.runtime.acoustic_source_side_positional_return_pressure import (
    OBSERVER_VERSION,
    POSITION_DEFINITIONS,
    PRIMARY_AMPLITUDE,
    _capture,
    evaluate_source_side_primary_blocks,
    frozen_protocol as source_side_frozen_protocol,
)


EXPERIMENT = "acoustic_source_side_positional_return_replication_v1"
TRACE_PATH = Path("traces") / f"{EXPERIMENT}.json"
PRIOR_TRACE_PATH = (
    Path("traces") / "acoustic_source_side_positional_return_pressure_v0.json"
)
PRIOR_DECISION_PATH = (
    Path("docs")
    / "decisions"
    / "acoustic_source_side_positional_return_pressure_v0.md"
)
STARTING_HEAD = "dbaa52a043bde027bb7dfeabde8422a685338149"
QUIET_SOURCE_DECLARATION = (
    "no known intentional unrelated endpoint playback initiated by the operator"
)


def frozen_protocol() -> dict[str, Any]:
    protocol = source_side_frozen_protocol()
    protocol["replication"] = {
        "independently_selected": True,
        "prior_specimen_used_as_calibration": False,
        "prior_measurements_used_to_change_protocol": False,
        "quiet_source_declaration": QUIET_SOURCE_DECLARATION,
    }
    return protocol


def _load_trace() -> dict[str, Any]:
    if not TRACE_PATH.exists():
        raise RuntimeError(f"missing staged trace {TRACE_PATH}")
    return json.loads(TRACE_PATH.read_text(encoding="utf-8"))


def _initial_trace(operator_setup_note: str) -> dict[str, Any]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if head != STARTING_HEAD:
        raise RuntimeError(f"expected starting HEAD {STARTING_HEAD}, observed {head}")
    prior = json.loads(PRIOR_TRACE_PATH.read_text(encoding="utf-8"))
    return {
        "experiment": EXPERIMENT,
        "status": "preflight_pending",
        "repository_starting_ref": head,
        "created_at_utc": utc_now(),
        "host": {
            "platform": platform.platform(),
            "python": sys.version,
            "process": sys.version_info[:3],
        },
        "lineage": {
            "prior_trace_path": PRIOR_TRACE_PATH.as_posix(),
            "prior_trace_sha256": _sha256_file(PRIOR_TRACE_PATH),
            "prior_decision_path": PRIOR_DECISION_PATH.as_posix(),
            "prior_status": prior["status"],
            "prior_specimen_preserved": True,
            "prior_measurements_used_as_calibration": False,
            "contamination_comparison_is_primary": False,
        },
        "quiet_source_declaration": QUIET_SOURCE_DECLARATION,
        "operator_setup_confirmation": operator_setup_note,
        "position_definitions_marked_before_primary": deepcopy(POSITION_DEFINITIONS),
        "preflight": {
            "classification": "single pre-primary instrumentation and response check",
            "attempts": [],
            "result_driven_retry_allowed": False,
        },
        "frozen_protocol": None,
        "primary_blocks": [],
        "adjudication": None,
        "process_failures": [],
        "canonical_history": {
            "path": CANONICAL_LEDGER_PATH.as_posix(),
            "sha256_before": _sha256_file(CANONICAL_LEDGER_PATH),
            "sha256_after": None,
            "changed": None,
        },
    }


def run_preflight(operator_setup_note: str) -> dict[str, Any]:
    if TRACE_PATH.exists():
        raise RuntimeError(f"replication trace already exists: {TRACE_PATH}")
    trace = _initial_trace(operator_setup_note)
    try:
        trial = _capture()
        evaluation = evaluate_preflight(trial)
        attempt = {
            "attempt_index": 1,
            "amplitude_full_scale": PRIMARY_AMPLITUDE,
            "trial": trial,
            "evaluation": evaluation,
        }
    except Exception as exc:
        attempt = {
            "attempt_index": 1,
            "trial_status": "preflight_instrumentation_failed",
            "failure_type": type(exc).__name__,
            "failure": str(exc),
            "retained": True,
        }
        trace["process_failures"].append(deepcopy(attempt))
        trace["preflight"]["attempts"].append(attempt)
        trace["status"] = "replication_preflight_instrumentation_failure"
        _atomic_write_json(TRACE_PATH, trace)
        return {"sufficient_to_freeze": False, "instrumentation_failure": attempt}
    trace["preflight"]["attempts"].append(attempt)
    if evaluation["sufficient_to_freeze"]:
        trace["frozen_protocol"] = frozen_protocol()
        trace["protocol_frozen_at_utc"] = utc_now()
        trace["status"] = "primary_A1_ready"
    else:
        trace["status"] = "replication_preflight_response_inadequate"
    _atomic_write_json(TRACE_PATH, trace)
    return evaluation


def _expected_next_block(trace: dict[str, Any]) -> str | None:
    completed = [block["position_block"] for block in trace["primary_blocks"]]
    if completed != list(BLOCK_ORDER[: len(completed)]):
        raise RuntimeError(f"invalid retained block order {completed}")
    return BLOCK_ORDER[len(completed)] if len(completed) < len(BLOCK_ORDER) else None


def run_primary_block(position: str, operator_note: str) -> dict[str, Any]:
    trace = _load_trace()
    if trace["frozen_protocol"] is None:
        raise RuntimeError("preflight did not freeze the primary protocol")
    expected = _expected_next_block(trace)
    if position != expected:
        raise RuntimeError(f"expected block {expected}, received {position}")
    if "observer_implementation" not in trace:
        implementation_path = Path(__file__)
        trace["observer_implementation"] = {
            "path": implementation_path.as_posix(),
            "sha256_frozen_before_primary": _sha256_file(implementation_path),
            "version": f"{OBSERVER_VERSION}_replication_v1",
            "reuses": [
                "paired endpoint/microphone capture from PR-019",
                "frozen PR-016/PR-019 evaluator",
            ],
        }
    block = {
        "position_block": position,
        "position_role": "A" if position in {"A1", "A2"} else "B",
        "intervention_locus": "physical_speaker_position",
        "operator_confirmation": operator_note,
        "started_at_utc": utc_now(),
        "trials": [],
        "completed_at_utc": None,
    }
    trace["primary_blocks"].append(block)
    trace["status"] = f"primary_{position}_in_progress"
    _atomic_write_json(TRACE_PATH, trace)
    for replicate in range(1, TRIALS_PER_BLOCK + 1):
        try:
            trial = _capture()
            trial.update(
                {
                    "position_block": position,
                    "position_role": block["position_role"],
                    "replicate_index": replicate,
                    "position_label_joined_after_capture": True,
                    "trial_status": "paired_observation_complete",
                }
            )
        except Exception as exc:
            trial = {
                "position_block": position,
                "position_role": block["position_role"],
                "replicate_index": replicate,
                "trial_status": "paired_observation_failed",
                "failure_type": type(exc).__name__,
                "failure": str(exc),
                "retained": True,
            }
            trace["process_failures"].append(deepcopy(trial))
        block["trials"].append(trial)
        _atomic_write_json(TRACE_PATH, trace)
        time.sleep(0.15)
    block["completed_at_utc"] = utc_now()
    trace["status"] = (
        "primary_complete_ready_for_adjudication"
        if position == "A2"
        else f"primary_{_expected_next_block(trace)}_awaiting_operator"
    )
    _atomic_write_json(TRACE_PATH, trace)
    return {
        "position_block": position,
        "trial_statuses": [trial["trial_status"] for trial in block["trials"]],
        "next_block": _expected_next_block(trace),
    }


def evaluate_replication_blocks(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    result = evaluate_source_side_primary_blocks(blocks)
    base_status = result["status"]
    if result["failure_count"]:
        status = "source_side_positional_return_replication_instrumentation_failure"
        outcome_class = "A"
    elif not result["source_stability"]["gate_passed"]:
        status = "source_side_positional_return_replication_source_gate_failed"
        outcome_class = "B"
    elif not result["cross_position"]["B_discriminated_from_A1"]:
        status = "source_side_positional_return_replication_not_discriminated"
        outcome_class = "C"
    elif not result["cross_position"]["return_recurrent"]:
        status = "source_side_positional_return_replication_observed_not_recurrent"
        outcome_class = "D"
    else:
        status = "source_side_positional_return_replication_recurrent"
        outcome_class = "E"
    result["source_side_evaluator_status"] = base_status
    result["status"] = status
    result["outcome_class"] = outcome_class
    result["independently_adjudicated"] = True
    result["prior_specimen_used_as_calibration"] = False
    return result


def adjudicate() -> dict[str, Any]:
    trace = _load_trace()
    if _expected_next_block(trace) is not None:
        raise RuntimeError("all three primary blocks must complete before adjudication")
    result = evaluate_replication_blocks(trace["primary_blocks"])
    canonical_after = _sha256_file(CANONICAL_LEDGER_PATH)
    trace["canonical_history"]["sha256_after"] = canonical_after
    trace["canonical_history"]["changed"] = (
        canonical_after != trace["canonical_history"]["sha256_before"]
    )
    trace["adjudication"] = result
    trace["status"] = result["status"]
    trace["finished_at_utc"] = utc_now()
    trace["epistemic_boundary"] = {
        "directly_observed": [
            "post-mix endpoint PCM packets and derived spectral magnitudes",
            "sampled XIBERIA microphone PCM before deletion and derived spectra",
            "source stability, within-block variation, separation, and return distances",
        ],
        "operator_provenance_only": [
            "no known intentional unrelated endpoint playback",
            "microphone configuration remained fixed",
            "speaker A1 -> B -> A2 movement and approximate displacement",
            "speaker height and orientation preservation and return to A",
        ],
        "not_observed_or_not_licensed": [
            "physical silence or perfectly isolated render path",
            "causal explanation of the prior failed-basis specimen",
            "machine-measured speaker or microphone geometry",
            "driver receipt, DAC behavior, speaker mechanics, or pure airborne causality",
            "physical transfer function, tomography, or cross-domain prediction",
        ],
    }
    _atomic_write_json(TRACE_PATH, trace)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight_parser = subparsers.add_parser("preflight")
    preflight_parser.add_argument("--operator-note", required=True)
    block_parser = subparsers.add_parser("block")
    block_parser.add_argument("position", choices=BLOCK_ORDER)
    block_parser.add_argument("--operator-note", required=True)
    subparsers.add_parser("adjudicate")
    args = parser.parse_args()
    if args.command == "preflight":
        result = run_preflight(args.operator_note)
    elif args.command == "block":
        result = run_primary_block(args.position, args.operator_note)
    else:
        result = adjudicate()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
