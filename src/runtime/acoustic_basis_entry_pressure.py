"""Bounded physical acoustic entry pressure over the generic DME v0 pipeline."""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import random
import statistics
import struct
import sys
import time
from copy import deepcopy
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from src.ingest import COMPARATOR_V0, append_admission, append_observation
from src.ledger import JsonlLedger, verify_continuity
from src.reconstruction import (
    derive_admitted_projection,
    derive_non_admitted_decision_states,
    reconstruct_admission_relationships,
)


EXPERIMENT = "acoustic_basis_entry_pressure_v0"
SOURCE = "bounded_physical_acoustic_observation"
OBSERVER = "winmm_acoustic_basis_pressure"
OBSERVER_VERSION = "acoustic_basis_pressure_v0"
SAMPLE_RATE = 48_000
CHANNEL_COUNT = 2
SAMPLE_WIDTH_BYTES = 2
CAPTURE_SECONDS = 0.75
PRE_ROLL_SECONDS = 0.20
EXCITATION_SECONDS = 0.18
POST_RESPONSE_SECONDS = 0.20
AMPLITUDE_FULL_SCALE = 0.02
CHIRP_START_HZ = 700.0
CHIRP_END_HZ = 1_700.0
INPUT_DEVICE_ID = 0
OUTPUT_DEVICE_ID = 0
REPLICATION_EXPERIMENT = "acoustic_replication_pressure_v0"
REPLICATION_OBSERVER_VERSION = "acoustic_replication_pressure_v0"
REPLICATION_RANDOM_SEED = 20_260_903
REPLICATION_PREDECLARED_AT_UTC = "2026-09-08T07:03:37.0280999Z"
REPLICATION_STARTING_HEAD = "c9be23c5a7c3db66d9da677ba01d90952aaef1a3"
REPLICATION_TRIAL_ORDER = (
    "S2",
    "S1",
    "C0",
    "C0",
    "S2",
    "C0",
    "S2",
    "S1",
    "C0",
    "S1",
    "S2",
    "S1",
    "S2",
    "C0",
    "S1",
)
RECURRENCE_EXPERIMENT = "acoustic_relational_recurrence_pressure_v0"
RECURRENCE_OBSERVER_VERSION = "acoustic_relational_recurrence_pressure_v0"
RECURRENCE_RANDOM_SEED = 20_260_910
RECURRENCE_PREDECLARED_AT_UTC = "2026-09-08T07:55:02.0517046Z"
RECURRENCE_STARTING_HEAD = "94543eafd8f6feadc45248e6b5d7861be6526212"
RECURRENCE_TRIAL_ORDER = (
    "S2",
    "C0",
    "C0",
    "S2",
    "C0",
    "S1",
    "S1",
    "S2",
    "S1",
    "C0",
    "S1",
    "S2",
    "S1",
    "S2",
    "C0",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_excitation(
    requested_channel: str,
    *,
    sample_rate: int = SAMPLE_RATE,
    duration_seconds: float = EXCITATION_SECONDS,
    amplitude_full_scale: float = AMPLITUDE_FULL_SCALE,
    start_hz: float = CHIRP_START_HZ,
    end_hz: float = CHIRP_END_HZ,
) -> tuple[bytes, bytes, dict[str, Any]]:
    """Build a conservative stereo PCM chirp with energy in one requested lane."""
    if requested_channel not in {"left", "right"}:
        raise ValueError("requested_channel must be 'left' or 'right'")
    if not 0.0 < amplitude_full_scale <= 0.05:
        raise ValueError("pressure excitation amplitude must be in (0, 0.05]")

    frame_count = round(sample_rate * duration_seconds)
    mono_samples: list[int] = []
    stereo = bytearray()
    sweep_rate = (end_hz - start_hz) / duration_seconds
    for index in range(frame_count):
        t = index / sample_rate
        window = math.sin(math.pi * index / max(frame_count - 1, 1)) ** 2
        phase = 2.0 * math.pi * (start_hz * t + 0.5 * sweep_rate * t * t)
        sample = round(32767 * amplitude_full_scale * window * math.sin(phase))
        mono_samples.append(sample)
        left, right = (sample, 0) if requested_channel == "left" else (0, sample)
        stereo.extend(struct.pack("<hh", left, right))

    mono = b"".join(struct.pack("<h", sample) for sample in mono_samples)
    parameters = {
        "kind": "linear_chirp_hann_windowed",
        "sample_rate_hz": sample_rate,
        "duration_seconds": duration_seconds,
        "frame_count": frame_count,
        "channel_count": CHANNEL_COUNT,
        "sample_format": "signed_16_bit_little_endian_pcm",
        "requested_output_channel": requested_channel,
        "amplitude_full_scale": amplitude_full_scale,
        "nominal_level_dbfs": round(20.0 * math.log10(amplitude_full_scale), 6),
        "start_frequency_hz": start_hz,
        "end_frequency_hz": end_hz,
        "mono_waveform_sha256": hashlib.sha256(mono).hexdigest(),
        "stereo_command_sha256": hashlib.sha256(stereo).hexdigest(),
    }
    return bytes(stereo), mono, parameters


def derive_capture_measurements(
    raw_pcm: bytes,
    *,
    sample_rate: int,
    channel_count: int,
    nominal_response_offset_seconds: float,
    excitation_seconds: float = EXCITATION_SECONDS,
    post_response_seconds: float = POST_RESPONSE_SECONDS,
) -> dict[str, Any]:
    """Derive deterministic, non-semantic measurements from an ephemeral PCM buffer."""
    if channel_count != 2:
        raise ValueError("the bounded pressure expects two captured PCM channels")
    complete_bytes = len(raw_pcm) - (len(raw_pcm) % (channel_count * 2))
    frames = list(struct.iter_unpack("<hh", raw_pcm[:complete_bytes]))
    response_start = max(0, round(nominal_response_offset_seconds * sample_rate))
    response_end = min(
        len(frames),
        response_start
        + round((excitation_seconds + post_response_seconds) * sample_rate),
    )
    baseline_end = min(len(frames), max(1, round(PRE_ROLL_SECONDS * 0.8 * sample_rate)))

    def metrics(values: list[int]) -> dict[str, float | int]:
        if not values:
            return {"frame_count": 0, "rms_pcm": 0.0, "peak_abs_pcm": 0}
        square_mean = sum(value * value for value in values) / len(values)
        return {
            "frame_count": len(values),
            "rms_pcm": round(math.sqrt(square_mean), 6),
            "peak_abs_pcm": max(abs(value) for value in values),
        }

    channels = []
    for channel_index, channel_name in enumerate(("microphone_channel_0", "microphone_channel_1")):
        whole = [frame[channel_index] for frame in frames]
        baseline = whole[:baseline_end]
        response = whole[response_start:response_end]
        baseline_metrics = metrics(baseline)
        response_metrics = metrics(response)
        baseline_rms = float(baseline_metrics["rms_pcm"])
        response_rms = float(response_metrics["rms_pcm"])
        ratio = response_rms / baseline_rms if baseline_rms > 0 else None
        delta_db = 20.0 * math.log10(ratio) if ratio is not None and ratio > 0 else None
        channels.append(
            {
                "channel": channel_name,
                "whole_capture": metrics(whole),
                "baseline_window": baseline_metrics,
                "nominal_response_window": response_metrics,
                "delta_rms_pcm": round(response_rms - baseline_rms, 6),
                "response_to_baseline_ratio": round(ratio, 9) if ratio is not None else None,
                "response_minus_baseline_db": round(delta_db, 6) if delta_db is not None else None,
            }
        )

    return {
        "measurement_version": "pcm_window_energy_v0",
        "frame_count": len(frames),
        "channel_count": channel_count,
        "sample_rate_hz": sample_rate,
        "nominal_response_window": {
            "start_frame": response_start,
            "end_frame_exclusive": response_end,
            "basis": "host command-submission offset plus fixed response window; not hardware synchronization",
        },
        "baseline_window": {
            "start_frame": 0,
            "end_frame_exclusive": baseline_end,
        },
        "channels": channels,
    }


def make_acoustic_ingest_envelope(observation: dict[str, Any]) -> dict[str, Any]:
    """Wrap physical measurement metadata without manufacturing an event time."""
    identity = observation["observation_id"]
    envelope_body = {
        "source": SOURCE,
        "source_sequence": None,
        "event_time": None,
        "arrival_time": observation["capture"]["host_capture_finished_at_utc"],
        "capture_version": observation["observer_version"],
        "provenance": {
            "trial_id": observation["trial_id"],
            "observer": observation["observer"],
            "observer_version": observation["observer_version"],
            "backend": observation["capture"]["backend"],
            "input_device": deepcopy(observation["capture"]["input_device"]),
            "output_device": deepcopy(observation["command"].get("output_device")),
            "capture_errors": deepcopy(observation["capture_errors"]),
        },
        "signal": {
            "identity": identity,
            "time": None,
            "type": "bounded_microphone_capture_measurements",
            "payload": deepcopy(observation),
        },
        "missingness": {
            "event_time": "unavailable: backend provides no warranted physical-event timestamp",
            "physical_speaker_realization": "unobserved",
            "complete_acoustic_field": "unobserved",
            "inferred_source_state": "not inferred",
        },
    }
    return {
        "envelope_identity": f"acoustic-ingest-v0:{canonical_sha256(envelope_body)}",
        **envelope_body,
    }


def carry_through_pipeline(
    observations: list[dict[str, Any]], ledger_path: Path | str
) -> dict[str, Any]:
    """Carry physical metadata through a temporary instance of the current pipeline."""
    ledger = JsonlLedger(ledger_path)
    observation_records = []
    admission_records = []
    for observation in observations:
        envelope = make_acoustic_ingest_envelope(observation)
        observation_record = append_observation(
            ledger,
            envelope,
            source=SOURCE,
            provenance={
                "pressure": EXPERIMENT,
                "trial_id": observation["trial_id"],
                "raw_capture_persisted": False,
            },
        )
        admission_record = append_admission(
            ledger, observation_record, comparator_version=COMPARATOR_V0
        )
        observation_records.append(observation_record)
        admission_records.append(admission_record)

    replay_a = ledger.replay()
    replay_b = JsonlLedger(ledger_path).replay()
    integrity = ledger.verify()
    continuity = verify_continuity(replay_a, require_start_at_one=True)
    reconstruction_a = reconstruct_admission_relationships(replay_a)
    reconstruction_b = reconstruct_admission_relationships(deepcopy(replay_b))
    projection_a = derive_admitted_projection(reconstruction_a)
    projection_b = derive_admitted_projection(reconstruction_b)
    companion_a = derive_non_admitted_decision_states(reconstruction_a, projection_a)
    companion_b = derive_non_admitted_decision_states(reconstruction_b, projection_b)

    recovered = [item["observation"]["signal"]["payload"] for item in reconstruction_a["observations"]]
    return {
        "temporary_ledger": True,
        "record_count": len(replay_a),
        "observation_record_count": len(observation_records),
        "admission_record_count": len(admission_records),
        "decisions": [record["envelope"]["decision"] for record in admission_records],
        "decision_bases": [record["envelope"]["decision_basis"] for record in admission_records],
        "integrity_ok": integrity.ok,
        "integrity_failures": list(integrity.failures),
        "continuity_ok": continuity.ok,
        "continuity_failures": list(continuity.failures),
        "replay_reproducible": replay_a == replay_b,
        "reconstruction_reproducible": reconstruction_a == reconstruction_b,
        "projection_reproducible": projection_a == projection_b,
        "companion_reproducible": companion_a == companion_b,
        "projection_count": len(projection_a),
        "projection": projection_a,
        "companion": companion_a,
        "recovered_trial_ids": [item["trial_id"] for item in recovered],
        "recovered_raw_capture_sha256": [item["raw_capture"]["sha256"] for item in recovered],
        "recovered_measurement_versions": [item["measurements"]["measurement_version"] for item in recovered],
        "information_visibility": {
            "command_direct_in_raw_observation": True,
            "measurements_direct_in_raw_observation": True,
            "raw_hash_direct_in_raw_observation": True,
            "command_direct_in_reconstruction_nested_observation": True,
            "measurements_direct_in_reconstruction_nested_observation": True,
            "raw_hash_direct_in_reconstruction_nested_observation": True,
            "command_direct_in_projection": False,
            "measurements_direct_in_projection": False,
            "raw_hash_direct_in_projection": False,
            "projection_retains_subject_navigation": all(
                bool(row["subject_record_id"]) for row in projection_a
            ),
            "raw_pcm_persisted": False,
        },
    }


def compare_trial_measurements(observations: list[dict[str, Any]]) -> dict[str, Any]:
    by_specimen = {item["specimen"]: item for item in observations}

    def response_vector(specimen: str) -> list[float]:
        return [
            float(channel["nominal_response_window"]["rms_pcm"])
            for channel in by_specimen[specimen]["measurements"]["channels"]
        ]

    c0 = response_vector("C0")
    s1 = response_vector("S1")
    s2 = response_vector("S2")

    def delta(left: list[float], right: list[float]) -> list[float]:
        return [round(a - b, 6) for a, b in zip(left, right)]

    return {
        "measurement_basis": "two-channel nominal-response-window RMS in captured PCM units",
        "C0_response_rms_pcm": c0,
        "S1_response_rms_pcm": s1,
        "S2_response_rms_pcm": s2,
        "S1_minus_C0_rms_pcm": delta(s1, c0),
        "S2_minus_C0_rms_pcm": delta(s2, c0),
        "S1_minus_S2_rms_pcm": delta(s1, s2),
        "S1_S2_measurement_vectors_exactly_equal": s1 == s2,
        "discrimination_threshold_declared": False,
        "replicate_trials_per_command": 1,
        "licensed_claim": "measured microphone-response values under the three commanded conditions",
        "not_licensed": [
            "exact emitted speaker waveform",
            "speaker channel health",
            "complete room acoustic field",
            "command-response causality",
            "repeatability or command-conditioned distribution",
        ],
    }


def materialize_replication_trial_order() -> list[str]:
    """Reproduce the complete order declared before replication acquisition."""
    base = ["C0"] * 5 + ["S1"] * 5 + ["S2"] * 5
    generated = random.Random(REPLICATION_RANDOM_SEED).sample(base, len(base))
    if tuple(generated) != REPLICATION_TRIAL_ORDER:
        raise RuntimeError("declared replication order no longer matches its seed")
    return generated


def predeclared_replication_basis() -> dict[str, Any]:
    """Return the frozen pre-acquisition measurement and discrimination rule."""
    return {
        "declared_before_physical_acquisition": True,
        "randomization": {
            "algorithm": "Python random.Random(seed).sample over five C0, five S1, five S2 labels",
            "seed": REPLICATION_RANDOM_SEED,
            "trial_order": materialize_replication_trial_order(),
        },
        "primary_measurement": {
            "name": "delta_rms_pcm",
            "definition": "nominal_response_window.rms_pcm - that_trial.baseline_window.rms_pcm",
            "evaluated_independently_for": ["microphone_channel_0", "microphone_channel_1"],
            "underlying_values_retained": ["baseline_window.rms_pcm", "nominal_response_window.rms_pcm"],
        },
        "pairwise_comparisons": ["S1_vs_C0", "S2_vs_C0", "S1_vs_S2"],
        "discrimination_rule": {
            "label": "locally_discriminable_under_declared_basis",
            "per_microphone_channel": True,
            "range_condition": "closed observed delta_rms ranges do not overlap",
            "separation_condition": "absolute median separation > 3 * max(MAD_A, MAD_B)",
            "mad_definition": "median(abs(x - median(x)))",
            "both_conditions_required": True,
            "zero_mad_policy": "if either condition MAD is zero, mark criterion_degenerate_insufficient; do not substitute a statistic and do not declare discrimination",
            "mechanism_claimed": False,
        },
        "replicates_per_condition": 5,
        "total_trials": 15,
    }


def materialize_recurrence_trial_order() -> list[str]:
    """Reproduce the new order declared before recurrence acquisition."""
    base = ["C0"] * 5 + ["S1"] * 5 + ["S2"] * 5
    generated = random.Random(RECURRENCE_RANDOM_SEED).sample(base, len(base))
    if tuple(generated) != RECURRENCE_TRIAL_ORDER:
        raise RuntimeError("declared recurrence order no longer matches its seed")
    return generated


def predeclared_recurrence_basis() -> dict[str, Any]:
    """Reuse the exact replication rule and freeze the recurrence criterion."""
    basis = deepcopy(predeclared_replication_basis())
    basis["randomization"] = {
        "algorithm": "Python random.Random(seed).sample over five C0, five S1, five S2 labels",
        "seed": RECURRENCE_RANDOM_SEED,
        "trial_order": materialize_recurrence_trial_order(),
    }
    basis["recurrence_criterion"] = {
        "label": "relationally_recurrent_under_declared_basis",
        "requires_both_microphone_channels": True,
        "expected_pairwise_discriminability": {
            "S1_vs_C0": False,
            "S2_vs_C0": True,
            "S1_vs_S2": True,
        },
        "absolute_S2_magnitude_match_required": False,
        "no_rule_weakening_after_acquisition": True,
    }
    return basis


def evaluate_replication_measurements(
    observations: list[dict[str, Any]],
    *,
    basis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply only the frozen delta/range/MAD basis to preserved occurrences."""
    selected_basis = deepcopy(basis or predeclared_replication_basis())
    expected_order = selected_basis["randomization"]["trial_order"]
    if [item["condition"] for item in observations] != expected_order:
        raise ValueError("observations do not follow the predeclared trial order")

    values: dict[str, dict[str, list[float]]] = {
        condition: {"microphone_channel_0": [], "microphone_channel_1": []}
        for condition in ("C0", "S1", "S2")
    }
    occurrences: dict[str, list[dict[str, Any]]] = {condition: [] for condition in values}
    for observation in observations:
        by_channel = {
            channel["channel"]: float(channel["delta_rms_pcm"])
            for channel in observation["measurements"]["channels"]
        }
        condition = observation["condition"]
        for channel_name, delta in by_channel.items():
            values[condition][channel_name].append(delta)
        occurrences[condition].append(
            {
                "trial_id": observation["trial_id"],
                "trial_sequence_index": observation["trial_sequence_index"],
                "delta_rms_pcm": by_channel,
            }
        )

    summaries: dict[str, dict[str, Any]] = {}
    for condition, channels in values.items():
        summaries[condition] = {}
        for channel_name, channel_values in channels.items():
            median_value = statistics.median(channel_values)
            mad_value = statistics.median(
                abs(value - median_value) for value in channel_values
            )
            summaries[condition][channel_name] = {
                "values": channel_values,
                "minimum": min(channel_values),
                "maximum": max(channel_values),
                "median": median_value,
                "mad": mad_value,
                "range_width": max(channel_values) - min(channel_values),
            }

    pairwise = {}
    for left, right in (("S1", "C0"), ("S2", "C0"), ("S1", "S2")):
        pair_name = f"{left}_vs_{right}"
        channel_results = {}
        for channel_name in ("microphone_channel_0", "microphone_channel_1"):
            a = summaries[left][channel_name]
            b = summaries[right][channel_name]
            ranges_do_not_overlap = bool(
                a["maximum"] < b["minimum"] or b["maximum"] < a["minimum"]
            )
            median_separation = abs(a["median"] - b["median"])
            threshold = 3.0 * max(a["mad"], b["mad"])
            max_mad = max(a["mad"], b["mad"])
            mad_degenerate = bool(a["mad"] == 0.0 or b["mad"] == 0.0)
            separation_exceeds_threshold = bool(median_separation > threshold)
            discriminable = bool(
                not mad_degenerate
                and ranges_do_not_overlap
                and separation_exceeds_threshold
            )
            channel_results[channel_name] = {
                "left_condition": left,
                "right_condition": right,
                "left_range": [a["minimum"], a["maximum"]],
                "right_range": [b["minimum"], b["maximum"]],
                "ranges_do_not_overlap": ranges_do_not_overlap,
                "left_median": a["median"],
                "right_median": b["median"],
                "absolute_median_separation": median_separation,
                "left_mad": a["mad"],
                "right_mad": b["mad"],
                "three_times_max_mad": threshold,
                "descriptive_median_separation_over_max_mad": (
                    median_separation / max_mad if max_mad != 0.0 else None
                ),
                "normalized_separation_is_part_of_rule": False,
                "separation_exceeds_three_times_max_mad": separation_exceeds_threshold,
                "mad_degenerate": mad_degenerate,
                "status": (
                    "criterion_degenerate_insufficient"
                    if mad_degenerate
                    else "locally_discriminable_under_declared_basis"
                    if discriminable
                    else "not_locally_discriminable_under_declared_basis"
                ),
                "locally_discriminable_under_declared_basis": discriminable,
            }
        pairwise[pair_name] = {
            "channels": channel_results,
            "discriminable_channels": [
                name
                for name, result in channel_results.items()
                if result["locally_discriminable_under_declared_basis"]
            ],
            "channel_results_consistent": len(
                {
                    result["status"] for result in channel_results.values()
                }
            )
            == 1,
        }

    return {
        "basis": selected_basis,
        "individual_occurrences": occurrences,
        "within_condition": summaries,
        "pairwise": pairwise,
        "no_mechanism_inferred": True,
    }


def evaluate_relational_recurrence(analysis: dict[str, Any]) -> dict[str, Any]:
    """Apply the frozen cross-run verdict-pattern criterion without weakening it."""
    expected = predeclared_recurrence_basis()["recurrence_criterion"][
        "expected_pairwise_discriminability"
    ]
    actual = {
        pair: {
            channel: analysis["pairwise"][pair]["channels"][channel][
                "locally_discriminable_under_declared_basis"
            ]
            for channel in ("microphone_channel_0", "microphone_channel_1")
        }
        for pair in expected
    }
    matches = {
        pair: {
            channel: actual[pair][channel] is expected_value
            for channel in actual[pair]
        }
        for pair, expected_value in expected.items()
    }
    recurrent = all(
        matches[pair][channel]
        for pair in matches
        for channel in matches[pair]
    )
    return {
        "criterion_declared_before_physical_acquisition": True,
        "expected_pairwise_discriminability": expected,
        "actual_pairwise_discriminability": actual,
        "per_pair_channel_match": matches,
        "relationally_recurrent_under_declared_basis": recurrent,
        "absolute_S2_magnitude_match_required": False,
        "mechanism_claimed": False,
    }


def compare_recurrence_to_prior_block(
    current_analysis: dict[str, Any], prior_analysis: dict[str, Any]
) -> dict[str, Any]:
    """Describe run-relative numerical change without altering either verdict."""
    conditions = {}
    for condition in ("C0", "S1", "S2"):
        conditions[condition] = {}
        for channel in ("microphone_channel_0", "microphone_channel_1"):
            prior = prior_analysis["within_condition"][condition][channel]
            current = current_analysis["within_condition"][condition][channel]
            conditions[condition][channel] = {
                "prior_median": prior["median"],
                "current_median": current["median"],
                "median_shift_current_minus_prior": current["median"] - prior["median"],
                "prior_mad": prior["mad"],
                "current_mad": current["mad"],
                "prior_range": [prior["minimum"], prior["maximum"]],
                "current_range": [current["minimum"], current["maximum"]],
                "range_endpoint_shift_current_minus_prior": [
                    current["minimum"] - prior["minimum"],
                    current["maximum"] - prior["maximum"],
                ],
            }

    pairwise = {}
    for pair in ("S1_vs_C0", "S2_vs_C0", "S1_vs_S2"):
        pairwise[pair] = {}
        for channel in ("microphone_channel_0", "microphone_channel_1"):
            prior = prior_analysis["pairwise"][pair]["channels"][channel]
            current = current_analysis["pairwise"][pair]["channels"][channel]
            pairwise[pair][channel] = {
                "prior_status": prior["status"],
                "current_status": current["status"],
                "status_recurred": prior["status"] == current["status"],
                "current_descriptive_median_separation_over_max_mad": current[
                    "descriptive_median_separation_over_max_mad"
                ],
            }
    return {
        "prior_primary_trace": "traces/acoustic_replication_pressure_v0.json",
        "comparison_is_post_acquisition_and_descriptive": True,
        "conditions": conditions,
        "S2_median_and_range_shift": conditions["S2"],
        "pairwise": pairwise,
        "numerical_realization_changed": any(
            details["median_shift_current_minus_prior"] != 0.0
            for by_channel in conditions.values()
            for details in by_channel.values()
        ),
        "mechanism_claimed": False,
    }


def predeclared_recurrence_trace() -> dict[str, Any]:
    """Materialize the full recurrence commitment before device enumeration."""
    return {
        "experiment": RECURRENCE_EXPERIMENT,
        "status": "predeclared_before_physical_acquisition",
        "physical_pressure_executed": False,
        "predeclaration_record": {
            "materialized_at_utc": RECURRENCE_PREDECLARED_AT_UTC,
            "starting_lineage": {
                "branch": "main",
                "head": RECURRENCE_STARTING_HEAD,
                "message": "Sound Test 1",
                "worktree": [],
            },
            "baseline_tests": {
                "runner": "python -m unittest discover -s tests",
                "passed": 461,
                "failed": 0,
            },
        },
        "predeclaration": predeclared_recurrence_basis(),
        "planned_fresh_initialization": {
            "separate_python_process": True,
            "new_WinMM_backend_instance": True,
            "prior_device_handles_reused": False,
            "complete_physical_or_driver_reset_claimed": False,
        },
        "canonical_live_history_sha256_before": (
            "0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0"
        ),
        "raw_recordings_committed": False,
    }


def _select_named_device(
    devices: list[dict[str, Any]], required_tokens: tuple[str, ...], role: str
) -> dict[str, Any]:
    matches = [
        item
        for item in devices
        if all(token.casefold() in item["name"].casefold() for token in required_tokens)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected exactly one {role} matching {required_tokens}, found {len(matches)}"
        )
    return matches[0]


def _run_replicated_acoustic_pressure(
    *,
    experiment: str,
    observer_version: str,
    identity_prefix: str,
    basis: dict[str, Any],
    predeclared_at_utc: str,
    starting_head: str,
    starting_message: str,
    baseline_test_count: int,
    temporary_ledger_name: str,
) -> dict[str, Any]:
    """Execute one frozen 15-trial block through a fresh WinMM backend."""
    if sys.platform != "win32":
        raise RuntimeError("physical pressure requires the inspected Windows WinMM backend")
    execution_process_started_at_utc = utc_now()
    backend = _WinMMBackend()
    backend_instance_created_at_utc = utc_now()
    input_devices = backend.input_devices()
    output_devices = backend.output_devices()
    input_device = _select_named_device(input_devices, ("XIBERIA",), "capture device")
    output_device = _select_named_device(
        output_devices, ("Speakers", "Realtek"), "room stereo playback device"
    )

    observations = []
    condition_counts = {"C0": 0, "S1": 0, "S2": 0}
    for sequence_index, condition in enumerate(
        basis["randomization"]["trial_order"], start=1
    ):
        condition_counts[condition] += 1
        requested_channel = {"C0": None, "S1": "left", "S2": "right"}[condition]
        command_pcm = None
        parameters = None
        if requested_channel is not None:
            command_pcm, _mono, parameters = build_excitation(requested_channel)
        capture = backend.capture_trial(
            command_pcm=command_pcm,
            input_device_id=input_device["device_id"],
            output_device_id=output_device["device_id"],
            sample_rate=SAMPLE_RATE,
            capture_seconds=CAPTURE_SECONDS,
            pre_roll_seconds=PRE_ROLL_SECONDS,
        )
        raw_pcm = capture.pop("raw_pcm")
        measurements = derive_capture_measurements(
            raw_pcm,
            sample_rate=SAMPLE_RATE,
            channel_count=CHANNEL_COUNT,
            nominal_response_offset_seconds=(
                capture["command_submission_offset_seconds"]
                if capture["command_submission_offset_seconds"] is not None
                else PRE_ROLL_SECONDS
            ),
        )
        body = {
            "experiment": experiment,
            "condition": condition,
            "trial_sequence_index": sequence_index,
            "replicate_index_within_condition": condition_counts[condition],
            "predeclared_trial_order": basis["randomization"]["trial_order"],
            "observer": OBSERVER,
            "observer_version": observer_version,
            "command": {
                "requested_playback": command_pcm is not None,
                "requested_output_channel": requested_channel,
                "waveform": deepcopy(parameters),
                "output_device": deepcopy(output_device) if command_pcm is not None else None,
                "host_command_submission_at_utc": capture["host_command_submission_at_utc"],
                "command_submission_offset_seconds": capture["command_submission_offset_seconds"],
            },
            "capture": {
                "backend": "Windows WinMM waveIn/waveOut",
                "input_device": deepcopy(input_device),
                "sample_rate_hz": SAMPLE_RATE,
                "channel_count": CHANNEL_COUNT,
                "sample_format": "signed_16_bit_little_endian_pcm",
                "frame_count": measurements["frame_count"],
                "host_capture_started_at_utc": capture["host_capture_started_at_utc"],
                "host_capture_finished_at_utc": capture["host_capture_finished_at_utc"],
                "host_capture_duration_seconds": capture["host_capture_duration_seconds"],
                "timing_basis": "host API-call boundaries and monotonic elapsed time; no hardware clock or simultaneity guarantee",
            },
            "measurements": measurements,
            "raw_capture": {
                "sha256": hashlib.sha256(raw_pcm).hexdigest(),
                "byte_count": len(raw_pcm),
                "persisted": False,
                "disposition": "ephemeral buffer discarded after deterministic measurements and hash",
            },
            "capture_errors": deepcopy(capture["capture_errors"]),
            "epistemic_limits": {
                "physical_speaker_realization_observed": False,
                "complete_acoustic_field_observed": False,
                "microphone_transduction_observed_directly": False,
                "sampled_microphone_waveform_observed": True,
                "speaker_channel_health_inferred": False,
                "playback_capture_simultaneity_claimed": False,
                "acoustic_causality_claimed": False,
            },
        }
        body_hash = canonical_sha256(body)
        observation = {
            "observation_id": f"{identity_prefix}-observation-v0:{body_hash}",
            "trial_id": f"{identity_prefix}-trial-v0:{sequence_index:02d}:{condition}:{body_hash[:16]}",
            **body,
        }
        observations.append(observation)
        time.sleep(0.15)

    with TemporaryDirectory() as tmpdir:
        pipeline = carry_through_pipeline(
            observations, Path(tmpdir) / temporary_ledger_name
        )

    return {
        "experiment": experiment,
        "status": "physical_acquisition_complete",
        "physical_pressure_executed": True,
        "primary_adjudication": True,
        "fresh_acquisition_initialization": {
            "new_process_for_block": True,
            "process_id": os.getpid(),
            "process_started_for_block_at_utc": execution_process_started_at_utc,
            "backend_instance_created_at_utc": backend_instance_created_at_utc,
            "prior_process_handles_reused": False,
            "device_handles_opened_and_closed_within_each_trial": True,
            "scope_limit": "does not establish reset of room, hardware, driver, or complete Windows audio state",
        },
        "predeclaration_record": {
            "materialized_at_utc": predeclared_at_utc,
            "starting_lineage": {
                "branch": "main",
                "head": starting_head,
                "message": starting_message,
                "worktree": [],
            },
            "baseline_tests": {
                "runner": "python -m unittest discover -s tests",
                "passed": baseline_test_count,
                "failed": 0,
            },
        },
        "predeclaration": basis,
        "backend_capability_at_execution": {
            "backend": "Windows WinMM",
            "input_devices": input_devices,
            "output_devices": output_devices,
            "selected_input_device": input_device,
            "selected_output_device": output_device,
            "selection_basis": "execution-time device names; numeric WinMM IDs not treated as stable identity",
            "third_party_dependency_added": False,
        },
        "safety_boundary": {
            "open_loop": True,
            "fixed_positions_requested": True,
            "jack_untouched": True,
            "playback_gain_unchanged": True,
            "feedback": False,
            "sustained_tone": False,
            "excitation_seconds": EXCITATION_SECONDS,
            "amplitude_full_scale": AMPLITUDE_FULL_SCALE,
            "nominal_level_dbfs": round(20.0 * math.log10(AMPLITUDE_FULL_SCALE), 6),
            "system_output_gain_observed": False,
            "deliberate_environmental_manipulation": False,
        },
        "operator_provenance": {
            "device_roles": {
                "Realtek": "room stereo playback",
                "XIBERIA": "headphones and headset microphone capture",
            },
            "room_stereo_can_emit_substantial_sound": True,
            "no_intentional_media_playback_requested": True,
            "ambient_silence_machine_verified": False,
            "machine_verified": False,
            "per_trial_listening_required": False,
        },
        "trials": observations,
        "replicated_measurement_analysis": evaluate_replication_measurements(
            observations, basis=basis
        ),
        "pipeline": pipeline,
        "raw_recordings_committed": False,
        "canonical_live_history_used": False,
    }


def run_replication_pressure() -> dict[str, Any]:
    """Execute the original frozen 15-trial acoustic replication pressure."""
    return _run_replicated_acoustic_pressure(
        experiment=REPLICATION_EXPERIMENT,
        observer_version=REPLICATION_OBSERVER_VERSION,
        identity_prefix="acoustic-replication",
        basis=predeclared_replication_basis(),
        predeclared_at_utc=REPLICATION_PREDECLARED_AT_UTC,
        starting_head=REPLICATION_STARTING_HEAD,
        starting_message="Horizontal Expansion- Soundscape",
        baseline_test_count=451,
        temporary_ledger_name="acoustic_replication_pressure.jsonl",
    )


def run_relational_recurrence_pressure() -> dict[str, Any]:
    """Execute the new-order recurrence block in a fresh bounded process."""
    basis = predeclared_recurrence_basis()
    prior_trace_path = Path("traces") / "acoustic_replication_pressure_v0.json"
    prior_trace = json.loads(prior_trace_path.read_text(encoding="utf-8"))
    if not prior_trace.get("primary_adjudication"):
        raise RuntimeError("prior primary replication trace is not marked authoritative")
    report = _run_replicated_acoustic_pressure(
        experiment=RECURRENCE_EXPERIMENT,
        observer_version=RECURRENCE_OBSERVER_VERSION,
        identity_prefix="acoustic-relational-recurrence",
        basis=basis,
        predeclared_at_utc=RECURRENCE_PREDECLARED_AT_UTC,
        starting_head=RECURRENCE_STARTING_HEAD,
        starting_message="Sound Test 1",
        baseline_test_count=461,
        temporary_ledger_name="acoustic_relational_recurrence_pressure.jsonl",
    )
    analysis = report["replicated_measurement_analysis"]
    report["relational_recurrence"] = evaluate_relational_recurrence(analysis)
    report["run_to_run_comparison"] = compare_recurrence_to_prior_block(
        analysis, prior_trace["replicated_measurement_analysis"]
    )
    return report


def run_physical_pressure() -> dict[str, Any]:
    """Execute the bounded C0/S1/S2 physical trial set using Windows WinMM."""
    if sys.platform != "win32":
        raise RuntimeError("physical pressure requires the inspected Windows WinMM backend")
    backend = _WinMMBackend()
    input_devices = backend.input_devices()
    output_devices = backend.output_devices()
    if not input_devices or not output_devices:
        raise RuntimeError("physical pressure not executed because acquisition capability is absent")

    input_device = input_devices[INPUT_DEVICE_ID]
    output_device = output_devices[OUTPUT_DEVICE_ID]
    commands: list[tuple[str, str | None, bytes | None, dict[str, Any] | None]] = [
        ("C0", None, None, None),
    ]
    for specimen, channel in (("S1", "left"), ("S2", "right")):
        stereo, _mono, parameters = build_excitation(channel)
        commands.append((specimen, channel, stereo, parameters))

    observations = []
    for ordinal, (specimen, requested_channel, command_pcm, parameters) in enumerate(commands, start=1):
        capture = backend.capture_trial(
            command_pcm=command_pcm,
            input_device_id=INPUT_DEVICE_ID,
            output_device_id=OUTPUT_DEVICE_ID,
            sample_rate=SAMPLE_RATE,
            capture_seconds=CAPTURE_SECONDS,
            pre_roll_seconds=PRE_ROLL_SECONDS,
        )
        raw_pcm = capture.pop("raw_pcm")
        measurements = derive_capture_measurements(
            raw_pcm,
            sample_rate=SAMPLE_RATE,
            channel_count=CHANNEL_COUNT,
            nominal_response_offset_seconds=(
                capture["command_submission_offset_seconds"]
                if capture["command_submission_offset_seconds"] is not None
                else PRE_ROLL_SECONDS
            ),
        )
        raw_hash = hashlib.sha256(raw_pcm).hexdigest()
        observation_body = {
            "experiment": EXPERIMENT,
            "specimen": specimen,
            "trial_ordinal": ordinal,
            "observer": OBSERVER,
            "observer_version": OBSERVER_VERSION,
            "command": {
                "requested_playback": command_pcm is not None,
                "requested_output_channel": requested_channel,
                "waveform": deepcopy(parameters),
                "output_device": deepcopy(output_device) if command_pcm is not None else None,
                "host_command_submission_at_utc": capture["host_command_submission_at_utc"],
                "command_submission_offset_seconds": capture["command_submission_offset_seconds"],
            },
            "capture": {
                "backend": "Windows WinMM waveIn/waveOut",
                "input_device": deepcopy(input_device),
                "sample_rate_hz": SAMPLE_RATE,
                "channel_count": CHANNEL_COUNT,
                "sample_format": "signed_16_bit_little_endian_pcm",
                "frame_count": measurements["frame_count"],
                "host_capture_started_at_utc": capture["host_capture_started_at_utc"],
                "host_capture_finished_at_utc": capture["host_capture_finished_at_utc"],
                "host_capture_duration_seconds": capture["host_capture_duration_seconds"],
                "timing_basis": "host API-call boundaries and monotonic elapsed time; no hardware clock or simultaneity guarantee",
            },
            "measurements": measurements,
            "raw_capture": {
                "sha256": raw_hash,
                "byte_count": len(raw_pcm),
                "persisted": False,
                "disposition": "ephemeral buffer discarded after deterministic measurements and hash",
            },
            "capture_errors": deepcopy(capture["capture_errors"]),
            "epistemic_limits": {
                "physical_speaker_realization_observed": False,
                "complete_acoustic_field_observed": False,
                "microphone_transduction_observed_directly": False,
                "sampled_microphone_waveform_observed": True,
                "speaker_channel_health_inferred": False,
                "playback_capture_simultaneity_claimed": False,
            },
        }
        observation = {
            "observation_id": f"acoustic-observation-v0:{canonical_sha256(observation_body)}",
            "trial_id": f"acoustic-trial-v0:{specimen}:{canonical_sha256(observation_body)[:16]}",
            **observation_body,
        }
        observations.append(observation)
        time.sleep(0.15)

    with TemporaryDirectory() as tmpdir:
        pipeline = carry_through_pipeline(observations, Path(tmpdir) / "acoustic_pressure.jsonl")

    return {
        "experiment": EXPERIMENT,
        "physical_pressure_executed": True,
        "operator_provided_context": {
            "report": "predominantly only the left output is physically realized; the other channel may intermittently return when the jack is moved",
            "epistemic_status": "unverified operator-provided provenance",
            "encoded_as_machine_verified_hardware_fact": False,
            "jack_moved_during_pressure": False,
            "device_roles": {
                "Realtek": "room stereo playback",
                "XIBERIA": "headphones and headset microphone capture",
            },
            "volume_warning": "room stereo can emit substantial sound; begin future range finding below established levels and increase only gradually",
            "post_run_audibility_report": "operator did not hear playback",
            "audibility_report_machine_verified": False,
        },
        "backend_capability": {
            "backend": "Windows WinMM",
            "input_devices": input_devices,
            "output_devices": output_devices,
            "selected_input_device_id": INPUT_DEVICE_ID,
            "selected_output_device_id": OUTPUT_DEVICE_ID,
            "third_party_dependency_added": False,
        },
        "safety_boundary": {
            "open_loop": True,
            "fixed_positions_requested": True,
            "feedback": False,
            "sustained_tone": False,
            "excitation_seconds": EXCITATION_SECONDS,
            "amplitude_full_scale": AMPLITUDE_FULL_SCALE,
            "nominal_level_dbfs": round(20.0 * math.log10(AMPLITUDE_FULL_SCALE), 6),
            "system_output_gain_observed": False,
            "further_emission_in_this_pass": False,
        },
        "trials": observations,
        "measurement_comparison": compare_trial_measurements(observations),
        "pipeline": pipeline,
        "raw_recordings_committed": False,
        "canonical_live_history_used": False,
    }


class WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", wintypes.WORD),
        ("nChannels", wintypes.WORD),
        ("nSamplesPerSec", wintypes.DWORD),
        ("nAvgBytesPerSec", wintypes.DWORD),
        ("nBlockAlign", wintypes.WORD),
        ("wBitsPerSample", wintypes.WORD),
        ("cbSize", wintypes.WORD),
    ]


class WAVEHDR(ctypes.Structure):
    _fields_ = [
        ("lpData", ctypes.c_void_p),
        ("dwBufferLength", wintypes.DWORD),
        ("dwBytesRecorded", wintypes.DWORD),
        ("dwUser", ctypes.c_size_t),
        ("dwFlags", wintypes.DWORD),
        ("dwLoops", wintypes.DWORD),
        ("lpNext", ctypes.c_void_p),
        ("reserved", ctypes.c_size_t),
    ]


class WAVEINCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", wintypes.WORD),
        ("wPid", wintypes.WORD),
        ("vDriverVersion", wintypes.DWORD),
        ("szPname", wintypes.WCHAR * 32),
        ("dwFormats", wintypes.DWORD),
        ("wChannels", wintypes.WORD),
        ("wReserved1", wintypes.WORD),
    ]


class WAVEOUTCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", wintypes.WORD),
        ("wPid", wintypes.WORD),
        ("vDriverVersion", wintypes.DWORD),
        ("szPname", wintypes.WCHAR * 32),
        ("dwFormats", wintypes.DWORD),
        ("wChannels", wintypes.WORD),
        ("wReserved1", wintypes.WORD),
        ("dwSupport", wintypes.DWORD),
    ]


class _WinMMBackend:
    WAVE_FORMAT_PCM = 1
    CALLBACK_NULL = 0
    WHDR_DONE = 0x00000001

    def __init__(self) -> None:
        self.winmm = ctypes.WinDLL("winmm")

    def input_devices(self) -> list[dict[str, Any]]:
        return self._devices("input")

    def output_devices(self) -> list[dict[str, Any]]:
        return self._devices("output")

    def _devices(self, kind: str) -> list[dict[str, Any]]:
        if kind == "input":
            count = self.winmm.waveInGetNumDevs()
            function = self.winmm.waveInGetDevCapsW
            caps_type = WAVEINCAPSW
        else:
            count = self.winmm.waveOutGetNumDevs()
            function = self.winmm.waveOutGetDevCapsW
            caps_type = WAVEOUTCAPSW
        devices = []
        for device_id in range(count):
            caps = caps_type()
            self._check(function(device_id, ctypes.byref(caps), ctypes.sizeof(caps)), f"{kind} device caps")
            devices.append(
                {
                    "device_id": device_id,
                    "name": caps.szPname,
                    "reported_max_channels": caps.wChannels,
                    "reported_format_mask": f"0x{caps.dwFormats:08x}",
                }
            )
        return devices

    @staticmethod
    def _format(sample_rate: int) -> WAVEFORMATEX:
        block_align = CHANNEL_COUNT * SAMPLE_WIDTH_BYTES
        return WAVEFORMATEX(
            _WinMMBackend.WAVE_FORMAT_PCM,
            CHANNEL_COUNT,
            sample_rate,
            sample_rate * block_align,
            block_align,
            SAMPLE_WIDTH_BYTES * 8,
            0,
        )

    def capture_trial(
        self,
        *,
        command_pcm: bytes | None,
        input_device_id: int,
        output_device_id: int,
        sample_rate: int,
        capture_seconds: float,
        pre_roll_seconds: float,
    ) -> dict[str, Any]:
        fmt = self._format(sample_rate)
        frame_count = round(sample_rate * capture_seconds)
        capture_buffer = ctypes.create_string_buffer(frame_count * fmt.nBlockAlign)
        capture_header = WAVEHDR(
            ctypes.cast(capture_buffer, ctypes.c_void_p),
            len(capture_buffer),
            0,
            0,
            0,
            0,
            None,
            0,
        )
        input_handle = ctypes.c_void_p()
        errors: list[dict[str, Any]] = []
        input_prepared = False
        host_command_submission_at_utc = None
        command_submission_offset_seconds = None
        started_at = None
        finished_at = None
        start_perf = None
        try:
            self._check(
                self.winmm.waveInOpen(
                    ctypes.byref(input_handle),
                    input_device_id,
                    ctypes.byref(fmt),
                    0,
                    0,
                    self.CALLBACK_NULL,
                ),
                "waveInOpen",
            )
            self._check(
                self.winmm.waveInPrepareHeader(
                    input_handle, ctypes.byref(capture_header), ctypes.sizeof(capture_header)
                ),
                "waveInPrepareHeader",
            )
            input_prepared = True
            self._check(
                self.winmm.waveInAddBuffer(
                    input_handle, ctypes.byref(capture_header), ctypes.sizeof(capture_header)
                ),
                "waveInAddBuffer",
            )
            started_at = utc_now()
            start_perf = time.perf_counter()
            self._check(self.winmm.waveInStart(input_handle), "waveInStart")
            self._wait_until(start_perf + pre_roll_seconds)
            if command_pcm is not None:
                host_command_submission_at_utc = utc_now()
                command_submission_offset_seconds = time.perf_counter() - start_perf
                self._play(command_pcm, output_device_id, fmt)
            deadline = start_perf + max(capture_seconds + 2.0, 3.0)
            while not capture_header.dwFlags & self.WHDR_DONE:
                if time.perf_counter() > deadline:
                    raise RuntimeError("waveIn capture timed out")
                time.sleep(0.005)
            finished_at = utc_now()
        except Exception as exc:
            errors.append({"stage": "winmm_capture_or_playback", "error": str(exc)})
            raise
        finally:
            if input_handle.value:
                self.winmm.waveInStop(input_handle)
                self.winmm.waveInReset(input_handle)
                if input_prepared:
                    self.winmm.waveInUnprepareHeader(
                        input_handle, ctypes.byref(capture_header), ctypes.sizeof(capture_header)
                    )
                self.winmm.waveInClose(input_handle)

        duration = time.perf_counter() - start_perf if start_perf is not None else None
        byte_count = int(capture_header.dwBytesRecorded)
        return {
            "raw_pcm": bytes(capture_buffer.raw[:byte_count]),
            "host_capture_started_at_utc": started_at,
            "host_capture_finished_at_utc": finished_at,
            "host_capture_duration_seconds": round(duration, 6) if duration is not None else None,
            "host_command_submission_at_utc": host_command_submission_at_utc,
            "command_submission_offset_seconds": (
                round(command_submission_offset_seconds, 9)
                if command_submission_offset_seconds is not None
                else None
            ),
            "capture_errors": errors,
        }

    def _play(self, pcm: bytes, output_device_id: int, fmt: WAVEFORMATEX) -> None:
        output_buffer = ctypes.create_string_buffer(pcm)
        output_header = WAVEHDR(
            ctypes.cast(output_buffer, ctypes.c_void_p),
            len(pcm),
            0,
            0,
            0,
            0,
            None,
            0,
        )
        output_handle = ctypes.c_void_p()
        prepared = False
        try:
            self._check(
                self.winmm.waveOutOpen(
                    ctypes.byref(output_handle),
                    output_device_id,
                    ctypes.byref(fmt),
                    0,
                    0,
                    self.CALLBACK_NULL,
                ),
                "waveOutOpen",
            )
            self._check(
                self.winmm.waveOutPrepareHeader(
                    output_handle, ctypes.byref(output_header), ctypes.sizeof(output_header)
                ),
                "waveOutPrepareHeader",
            )
            prepared = True
            self._check(
                self.winmm.waveOutWrite(
                    output_handle, ctypes.byref(output_header), ctypes.sizeof(output_header)
                ),
                "waveOutWrite",
            )
            deadline = time.perf_counter() + EXCITATION_SECONDS + 2.0
            while not output_header.dwFlags & self.WHDR_DONE:
                if time.perf_counter() > deadline:
                    raise RuntimeError("waveOut playback timed out")
                time.sleep(0.002)
        finally:
            if output_handle.value:
                self.winmm.waveOutReset(output_handle)
                if prepared:
                    self.winmm.waveOutUnprepareHeader(
                        output_handle, ctypes.byref(output_header), ctypes.sizeof(output_header)
                    )
                self.winmm.waveOutClose(output_handle)

    @staticmethod
    def _wait_until(deadline: float) -> None:
        while True:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                return
            time.sleep(min(remaining, 0.005))

    @staticmethod
    def _check(result: int, operation: str) -> None:
        if result != 0:
            raise RuntimeError(f"{operation} failed with WinMM result {result}")


def main() -> None:
    mode = sys.argv[1:]
    if mode == ["recurrence"]:
        report = run_relational_recurrence_pressure()
        output_name = "acoustic_relational_recurrence_pressure_v0.json"
    elif mode == ["replication"]:
        report = run_replication_pressure()
        output_name = "acoustic_replication_pressure_v0.json"
    elif not mode:
        report = run_physical_pressure()
        output_name = "acoustic_basis_entry_pressure_v0.json"
    else:
        raise SystemExit("usage: acoustic_basis_entry_pressure.py [replication|recurrence]")
    output_path = Path("traces") / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
