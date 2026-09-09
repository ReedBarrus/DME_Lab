"""Staged speaker A1 -> B -> A2 return pressure with a fixed microphone.

This pressure-only runner reuses the paired endpoint/microphone acquisition and
frozen evaluator from PR-016. Physical position is operator provenance joined
after capture; neither observer machine-measures speaker or microphone geometry.
"""

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
    MAXIMUM_AMPLITUDE,
    TRIALS_PER_BLOCK,
    _atomic_write_json,
    _sha256_file,
    capture_paired_trial,
    evaluate_preflight,
    evaluate_primary_blocks,
    frozen_protocol as positional_frozen_protocol,
)


EXPERIMENT = "acoustic_source_side_positional_return_pressure_v0"
OBSERVER_VERSION = "paired_endpoint_microphone_source_side_position_pressure_v0"
TRACE_PATH = Path("traces") / f"{EXPERIMENT}.json"
STARTING_HEAD = "fbf73bd2d8de2e58f0dd209c1d1cc4408c4a1e31"
PRIMARY_AMPLITUDE = 0.02

POSITION_DEFINITIONS = {
    "A": {
        "role": "operator-confirmed original physical speaker position",
        "marking": "speaker location marked before primary evidence",
    },
    "B": {
        "role": "operator-marked lateral physical speaker displacement from A",
        "constraints": "speaker height and orientation held fixed where practical",
        "marking": "defined before primary evidence; displacement is operator-reported",
    },
    "fixed": {
        "microphone_position": "unchanged by operator report",
        "microphone_orientation": "unchanged by operator report",
        "microphone_support": "unchanged by operator report",
        "microphone_cable": "not touched except for unavoidable safety",
        "system_gain": "unchanged",
        "routing": "unchanged",
        "hardware_settings": "unchanged",
    },
}

STATUS_MAP = {
    "positional_acoustic_transformation_evidence_insufficient": (
        "source_side_positional_return_evidence_insufficient"
    ),
    "positional_acoustic_transformation_not_discriminated": (
        "source_side_position_not_discriminated"
    ),
    "positional_acoustic_transformation_observed_not_recurrent": (
        "source_side_position_observed_not_recurrent"
    ),
    "positional_acoustic_transformation_recurrent": (
        "source_side_positional_return_recurrent"
    ),
}


def frozen_protocol() -> dict[str, Any]:
    protocol = positional_frozen_protocol(PRIMARY_AMPLITUDE)
    protocol["position_definitions"] = deepcopy(POSITION_DEFINITIONS)
    protocol["intervention_locus"] = "physical_speaker_position"
    protocol["fixed_observer_configuration"] = (
        "microphone position, orientation, support, and cable unchanged by operator report"
    )
    protocol["reused_from"] = "acoustic_positional_transformation_pressure_v0"
    return protocol


def _load_trace() -> dict[str, Any]:
    if not TRACE_PATH.exists():
        raise RuntimeError(f"missing staged trace {TRACE_PATH}")
    return json.loads(TRACE_PATH.read_text(encoding="utf-8"))


def _initial_trace(operator_setup_note: str) -> dict[str, Any]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if head != STARTING_HEAD:
        raise RuntimeError(f"expected starting HEAD {STARTING_HEAD}, observed {head}")
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
        "operator_setup_confirmation": operator_setup_note,
        "position_definitions_marked_before_primary": deepcopy(POSITION_DEFINITIONS),
        "preflight": {
            "classification": "pre-primary instrumentation and response check",
            "attempts": [],
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


def _capture() -> dict[str, Any]:
    trial = capture_paired_trial(PRIMARY_AMPLITUDE)
    trial["observer_version"] = OBSERVER_VERSION
    trial["intervention_locus"] = "physical_speaker_position"
    trial["microphone_configuration_joined_after_capture"] = True
    return trial


def run_preflight(operator_setup_note: str) -> dict[str, Any]:
    if TRACE_PATH.exists():
        trace = _load_trace()
        if trace["primary_blocks"]:
            raise RuntimeError("primary evidence already exists; preflight is frozen")
        if trace["frozen_protocol"] is not None:
            raise RuntimeError("protocol already frozen")
        if "operator_setup_confirmations" not in trace:
            trace["operator_setup_confirmations"] = [
                trace["operator_setup_confirmation"]
            ]
            trace["process_failures"].append(
                {
                    "stage": "preflight_retry_before_capture",
                    "failure_type": "KeyError",
                    "failure": "'operator_setup_confirmations'",
                    "sound_emitted": False,
                    "retained": True,
                    "note": (
                        "first retry invocation aborted before capture while "
                        "loading a trace created before the confirmations list"
                    ),
                    "recorded_at_utc": utc_now(),
                }
            )
        trace["operator_setup_confirmations"].append(operator_setup_note)
    else:
        trace = _initial_trace(operator_setup_note)
        trace["operator_setup_confirmations"] = [operator_setup_note]
    trial = _capture()
    evaluation = evaluate_preflight(trial)
    trace["preflight"]["attempts"].append(
        {
            "attempt_index": len(trace["preflight"]["attempts"]) + 1,
            "amplitude_full_scale": PRIMARY_AMPLITUDE,
            "trial": trial,
            "evaluation": evaluation,
        }
    )
    if evaluation["sufficient_to_freeze"]:
        trace["frozen_protocol"] = frozen_protocol()
        trace["protocol_frozen_at_utc"] = utc_now()
        trace["status"] = "primary_A1_ready"
    else:
        trace["status"] = "preflight_instrumentation_or_response_inadequate"
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
            "version": OBSERVER_VERSION,
            "reuses_paired_capture_and_evaluator_from": (
                "src/runtime/acoustic_positional_transformation_pressure.py"
            ),
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


def evaluate_source_side_primary_blocks(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    result = evaluate_primary_blocks(blocks)
    positional_status = result["status"]
    if positional_status not in STATUS_MAP:
        raise RuntimeError(f"unexpected reused evaluator status {positional_status}")
    result["reused_evaluator_status"] = positional_status
    result["status"] = STATUS_MAP[positional_status]
    result["intervention_locus"] = "physical_speaker_position"
    result["fixed_observer_configuration"] = "operator-reported fixed microphone"
    return result


def adjudicate() -> dict[str, Any]:
    trace = _load_trace()
    if _expected_next_block(trace) is not None:
        raise RuntimeError("all three primary blocks must complete before adjudication")
    result = evaluate_source_side_primary_blocks(trace["primary_blocks"])
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
            "microphone position, orientation, support, and cable remained fixed",
            "speaker A1 -> B -> A2 movement and approximate displacement",
            "speaker height and orientation preservation and return to the A mark",
            "unchanged physical settings",
        ],
        "not_observed_or_not_licensed": [
            "machine-measured speaker or microphone geometry",
            "specific driver receipt, DAC behavior, or speaker mechanics",
            "pure airborne causality or complete room state",
            "physical transfer function or general acoustic law",
            "tomography or prospective cross-domain prediction",
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
