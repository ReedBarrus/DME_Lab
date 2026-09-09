"""Staged A1 -> B -> A2 physical-position pressure instrumentation.

This module is pressure-only.  The WASAPI watcher is a separate process which
receives endpoint identity and capture paths only.  Position and playback
metadata are joined after endpoint and microphone acquisition.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
from tempfile import TemporaryDirectory
from typing import Any

from src.runtime.acoustic_basis_entry_pressure import (
    CAPTURE_SECONDS,
    CHANNEL_COUNT,
    CHIRP_END_HZ,
    CHIRP_START_HZ,
    EXCITATION_SECONDS,
    POST_RESPONSE_SECONDS,
    PRE_ROLL_SECONDS,
    SAMPLE_RATE,
    _WinMMBackend,
    _select_named_device,
    build_excitation,
    utc_now,
)
from src.runtime.wasapi_loopback_witness_validation import (
    TARGET_FRIENDLY_NAME,
    _decode_pcm,
    _watcher_command,
    enumerate_render_endpoints,
    select_realtek_endpoint,
)


EXPERIMENT = "acoustic_positional_transformation_pressure_v0"
OBSERVER_VERSION = "paired_endpoint_microphone_position_pressure_v0"
TRACE_PATH = Path("traces") / "acoustic_positional_transformation_pressure_v0.json"
CANONICAL_LEDGER_PATH = Path("traces") / "live_ingest_ledger_v0.jsonl"
STARTING_HEAD = "a7ea13d45b60f7109dd0abe35bf23fc695ed30c5"
PREFLIGHT_AMPLITUDE = 0.005
MAXIMUM_AMPLITUDE = 0.02
REQUESTED_OUTPUT_CHANNEL = "right"
TRIALS_PER_BLOCK = 5
BLOCK_ORDER = ("A1", "B", "A2")
FREQUENCY_BINS_HZ = tuple(float(value) for value in range(750, 1_651, 100))
SPECTRAL_FLOOR = 1e-12

# Frozen before primary acquisition.  The endpoint gate is deliberately tight
# because prior loopback trials were nearly byte-recurrent.  The physical
# response rule uses robust within-block median radius without deleting outliers.
MAX_ENDPOINT_SHAPE_DISTANCE_DB = 0.75
MAX_ENDPOINT_MEAN_LEVEL_RANGE_DB = 1.0
MINIMUM_POSITION_CENTROID_DISTANCE_DB = 1.5
SEPARATION_TO_WITHIN_MEDIAN_MULTIPLIER = 3.0
MAXIMUM_RETURN_TO_SEPARATION_RATIO = 0.5
MINIMUM_A2_TRIALS_CLOSER_TO_A1 = 4

POSITION_DEFINITIONS = {
    "A": {
        "role": "operator-confirmed original microphone position",
        "marking": "physical location marked before primary evidence",
    },
    "B": {
        "role": "lateral displacement approximately one headphone length from A",
        "constraints": "microphone height and orientation held fixed",
        "marking": "defined before primary evidence; displacement is operator-reported",
    },
    "fixed": {
        "speaker_position": "unchanged",
        "system_gain": "unchanged",
        "routing": "unchanged",
        "hardware_settings": "unchanged",
    },
}


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False),
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_trace() -> dict[str, Any]:
    if not TRACE_PATH.exists():
        raise RuntimeError(f"missing staged trace {TRACE_PATH}")
    return json.loads(TRACE_PATH.read_text(encoding="utf-8"))


def _initial_trace() -> dict[str, Any]:
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
        "position_definitions_marked_before_primary": deepcopy(POSITION_DEFINITIONS),
        "preflight": {
            "classification": "exploratory; excluded from primary adjudication",
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


def frozen_protocol(amplitude: float) -> dict[str, Any]:
    if not 0.0 < amplitude <= MAXIMUM_AMPLITUDE:
        raise ValueError(f"amplitude must be in (0, {MAXIMUM_AMPLITUDE}]")
    return {
        "declared_before_primary_acquisition": True,
        "block_order": list(BLOCK_ORDER),
        "trials_per_block": TRIALS_PER_BLOCK,
        "position_definitions": deepcopy(POSITION_DEFINITIONS),
        "waveform": {
            "kind": "linear_chirp_hann_windowed",
            "requested_output_channel": REQUESTED_OUTPUT_CHANNEL,
            "start_frequency_hz": CHIRP_START_HZ,
            "end_frequency_hz": CHIRP_END_HZ,
            "duration_seconds": EXCITATION_SECONDS,
            "amplitude_full_scale": amplitude,
            "nominal_level_dbfs": round(20.0 * math.log10(amplitude), 6),
        },
        "paired_capture": {
            "duration_seconds": CAPTURE_SECONDS,
            "pre_roll_seconds": PRE_ROLL_SECONDS,
            "endpoint_observer": "separate-process WASAPI shared-mode loopback",
            "microphone_observer": "Windows WinMM waveIn",
            "condition_joined_after_capture": True,
            "raw_pcm_persisted": False,
        },
        "measurement": {
            "name": "source_normalized_microphone_spectral_signature_v0",
            "frequency_bins_hz": list(FREQUENCY_BINS_HZ),
            "endpoint": "whole-capture single-frequency RMS, channels RMS-combined",
            "microphone": (
                "nominal response-window single-frequency RMS, channels RMS-combined"
            ),
            "absolute_source_normalized_db": "20*log10(microphone/endpoint) per bin",
            "level_normalized_shape_db": "absolute vector minus its arithmetic mean",
            "response_distance": "RMS Euclidean distance between absolute dB vectors",
            "shape_distance": "RMS Euclidean distance between level-normalized vectors",
            "claim": "bounded response signature; not a physical transfer function",
        },
        "source_stability_gate": {
            "maximum_endpoint_shape_pair_distance_db": MAX_ENDPOINT_SHAPE_DISTANCE_DB,
            "maximum_endpoint_mean_level_range_db": MAX_ENDPOINT_MEAN_LEVEL_RANGE_DB,
            "required_across": "all retained A1, B, and A2 primary trials",
        },
        "position_discrimination": {
            "centroid": "coordinate-wise median absolute source-normalized dB vector",
            "within_position_scale": "median trial distance to that block centroid",
            "B_from_A1_requires": (
                "centroid distance > max(minimum distance, multiplier * maximum "
                "within-position median scale)"
            ),
            "minimum_centroid_distance_db": MINIMUM_POSITION_CENTROID_DISTANCE_DB,
            "separation_to_within_median_multiplier": (
                SEPARATION_TO_WITHIN_MEDIAN_MULTIPLIER
            ),
        },
        "return_recurrence": {
            "centroid_requirement": (
                "A2-to-A1 distance < A2-to-B distance and <= frozen fraction of "
                "A1-to-B separation"
            ),
            "maximum_A2_to_A1_over_A1_to_B": MAXIMUM_RETURN_TO_SEPARATION_RATIO,
            "minimum_A2_trials_closer_to_A1_than_B": (
                MINIMUM_A2_TRIALS_CLOSER_TO_A1
            ),
        },
        "trial_retention": "all primary trials retained; no exclusion rule",
    }


def _single_frequency_rms(
    samples: list[float], sample_rate: int, frequency_hz: float
) -> float:
    if not samples:
        return 0.0
    omega = 2.0 * math.pi * frequency_hz / sample_rate
    cosine = 0.0
    sine = 0.0
    for index, sample in enumerate(samples):
        cosine += sample * math.cos(omega * index)
        sine += sample * math.sin(omega * index)
    return (2.0 * math.hypot(cosine, sine) / len(samples)) / math.sqrt(2.0)


def _spectral_magnitudes(
    channels: list[list[float]], sample_rate: int
) -> dict[str, Any]:
    per_channel = []
    for channel_index, samples in enumerate(channels):
        magnitudes = {
            str(int(frequency)): _single_frequency_rms(
                samples, sample_rate, frequency
            )
            for frequency in FREQUENCY_BINS_HZ
        }
        per_channel.append(
            {"channel_index": channel_index, "magnitude_rms": magnitudes}
        )
    combined = {}
    for frequency in FREQUENCY_BINS_HZ:
        key = str(int(frequency))
        values = [item["magnitude_rms"][key] for item in per_channel]
        combined[key] = math.sqrt(sum(value * value for value in values) / len(values))
    return {"per_channel": per_channel, "combined_magnitude_rms": combined}


def derive_paired_signature(
    endpoint_raw: bytes,
    endpoint_mix: dict[str, Any],
    microphone_raw: bytes,
    command_submission_offset_seconds: float,
) -> dict[str, Any]:
    endpoint_channels = _decode_pcm(endpoint_raw, endpoint_mix)
    complete = len(microphone_raw) - (len(microphone_raw) % (CHANNEL_COUNT * 2))
    microphone_frames = list(
        __import__("struct").iter_unpack("<hh", microphone_raw[:complete])
    )
    microphone_channels = [
        [frame[index] / 32768.0 for frame in microphone_frames]
        for index in range(CHANNEL_COUNT)
    ]
    response_start = max(0, round(command_submission_offset_seconds * SAMPLE_RATE))
    response_end = min(
        len(microphone_frames),
        response_start
        + round((EXCITATION_SECONDS + POST_RESPONSE_SECONDS) * SAMPLE_RATE),
    )
    baseline_end = min(
        len(microphone_frames), round(PRE_ROLL_SECONDS * 0.8 * SAMPLE_RATE)
    )
    response_channels = [
        values[response_start:response_end] for values in microphone_channels
    ]
    baseline_channels = [values[:baseline_end] for values in microphone_channels]
    endpoint = _spectral_magnitudes(
        endpoint_channels, int(endpoint_mix["sample_rate_hz"])
    )
    microphone_response = _spectral_magnitudes(response_channels, SAMPLE_RATE)
    microphone_baseline = _spectral_magnitudes(baseline_channels, SAMPLE_RATE)

    absolute = []
    response_over_baseline = []
    endpoint_db = []
    for frequency in FREQUENCY_BINS_HZ:
        key = str(int(frequency))
        endpoint_value = max(endpoint["combined_magnitude_rms"][key], SPECTRAL_FLOOR)
        response_value = max(
            microphone_response["combined_magnitude_rms"][key], SPECTRAL_FLOOR
        )
        baseline_value = max(
            microphone_baseline["combined_magnitude_rms"][key], SPECTRAL_FLOOR
        )
        endpoint_db.append(20.0 * math.log10(endpoint_value))
        absolute.append(20.0 * math.log10(response_value / endpoint_value))
        response_over_baseline.append(20.0 * math.log10(response_value / baseline_value))
    mean_absolute = statistics.fmean(absolute)
    mean_endpoint = statistics.fmean(endpoint_db)
    return {
        "measurement_version": "source_normalized_microphone_spectral_signature_v0",
        "frequency_bins_hz": list(FREQUENCY_BINS_HZ),
        "microphone_windows": {
            "baseline": {"start_frame": 0, "end_frame_exclusive": baseline_end},
            "response": {
                "start_frame": response_start,
                "end_frame_exclusive": response_end,
                "basis": "host command-submission offset; not hardware synchronization",
            },
        },
        "endpoint_spectrum": endpoint,
        "endpoint_combined_magnitude_db": endpoint_db,
        "endpoint_mean_magnitude_db": mean_endpoint,
        "endpoint_level_normalized_shape_db": [
            value - mean_endpoint for value in endpoint_db
        ],
        "microphone_response_spectrum": microphone_response,
        "microphone_baseline_spectrum": microphone_baseline,
        "microphone_response_over_baseline_db": response_over_baseline,
        "absolute_source_normalized_response_db": absolute,
        "absolute_response_mean_db": mean_absolute,
        "level_normalized_spectral_shape_db": [
            value - mean_absolute for value in absolute
        ],
        "not_a_physical_transfer_function": True,
    }


def _wait_for_ready(watcher: subprocess.Popen[str], ready_path: Path) -> dict[str, Any]:
    deadline = time.perf_counter() + 8.0
    while not ready_path.exists() and watcher.poll() is None:
        if time.perf_counter() > deadline:
            watcher.kill()
            raise RuntimeError("WASAPI watcher did not reach ready state")
        time.sleep(0.01)
    if not ready_path.exists():
        stdout, stderr = watcher.communicate(timeout=2)
        raise RuntimeError(
            f"WASAPI watcher failed before ready: stdout={stdout!r}; stderr={stderr!r}"
        )
    return json.loads(ready_path.read_text(encoding="utf-8"))


def capture_paired_trial(amplitude: float) -> dict[str, Any]:
    endpoints = enumerate_render_endpoints()
    endpoint = select_realtek_endpoint(endpoints)
    backend = _WinMMBackend()
    input_device = _select_named_device(
        backend.input_devices(), ("XIBERIA",), "capture device"
    )
    output_device = _select_named_device(
        backend.output_devices(), ("Speakers", "Realtek"), "room stereo device"
    )
    command_pcm, _mono, waveform = build_excitation(
        REQUESTED_OUTPUT_CHANNEL, amplitude_full_scale=amplitude
    )
    with TemporaryDirectory(prefix="dme-position-pair-") as directory:
        base = Path(directory)
        ready_path = base / "endpoint.ready.json"
        result_path = base / "endpoint.result.json"
        pcm_path = base / "endpoint.pcm"
        watcher_command = _watcher_command(
            endpoint["endpoint_id"], CAPTURE_SECONDS, ready_path, result_path, pcm_path
        )
        watcher = subprocess.Popen(
            watcher_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        ready = _wait_for_ready(watcher, ready_path)
        microphone = backend.capture_trial(
            command_pcm=command_pcm,
            input_device_id=input_device["device_id"],
            output_device_id=output_device["device_id"],
            sample_rate=SAMPLE_RATE,
            capture_seconds=CAPTURE_SECONDS,
            pre_roll_seconds=PRE_ROLL_SECONDS,
        )
        stdout, stderr = watcher.communicate(timeout=CAPTURE_SECONDS + 8.0)
        if watcher.returncode != 0:
            raise RuntimeError(
                f"WASAPI watcher failed: stdout={stdout!r}; stderr={stderr!r}"
            )
        endpoint_observation = json.loads(result_path.read_text(encoding="utf-8"))
        endpoint_raw = pcm_path.read_bytes()
        if _sha256_bytes(endpoint_raw) != endpoint_observation["pcm_sha256"]:
            raise RuntimeError("endpoint PCM hash mismatch")
        microphone_raw = microphone.pop("raw_pcm")
        offset = microphone["command_submission_offset_seconds"]
        if offset is None:
            raise RuntimeError("microphone observer did not record command offset")
        signature = derive_paired_signature(
            endpoint_raw,
            endpoint_observation["mix_format"],
            microphone_raw,
            float(offset),
        )
        pcm_path.unlink()
    body = {
        "captured_at_utc": utc_now(),
        "observer_version": OBSERVER_VERSION,
        "endpoint": {
            "ready": ready,
            "observation": endpoint_observation,
            "watcher_process_separate_from_emitter": watcher.pid != __import__("os").getpid(),
            "watcher_received_condition_or_position": False,
            "watcher_received_waveform_or_frequency": False,
            "raw_pcm": {
                "sha256": _sha256_bytes(endpoint_raw),
                "byte_count": len(endpoint_raw),
                "persisted": False,
            },
        },
        "microphone": {
            "observer_process_id": __import__("os").getpid(),
            "capture": microphone,
            "input_device": input_device,
            "raw_pcm": {
                "sha256": _sha256_bytes(microphone_raw),
                "byte_count": len(microphone_raw),
                "persisted": False,
            },
        },
        "emitter": {
            "process_id": __import__("os").getpid(),
            "output_device": output_device,
            "waveform": waveform,
            "completion_is_not_witness": True,
        },
        "paired_signature": signature,
        "position_joined_after_capture": True,
        "capture_failures": deepcopy(microphone["capture_errors"]),
    }
    body["paired_observation_sha256"] = _sha256_bytes(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return body


def evaluate_preflight(trial: dict[str, Any]) -> dict[str, Any]:
    signature = trial["paired_signature"]
    endpoint_packets = trial["endpoint"]["observation"]["packet_count"]
    response_db = signature["microphone_response_over_baseline_db"]
    criteria = {
        "endpoint_packets_present": endpoint_packets > 0,
        "microphone_capture_complete": (
            trial["microphone"]["raw_pcm"]["byte_count"]
            == round(SAMPLE_RATE * CAPTURE_SECONDS) * CHANNEL_COUNT * 2
        ),
        "no_capture_failures": not trial["capture_failures"],
        "median_microphone_band_response_over_baseline_at_least_6_db": (
            statistics.median(response_db) >= 6.0
        ),
    }
    return {
        "criteria": criteria,
        "sufficient_to_freeze": all(criteria.values()),
        "median_microphone_band_response_over_baseline_db": statistics.median(
            response_db
        ),
        "minimum_microphone_band_response_over_baseline_db": min(response_db),
        "maximum_microphone_band_response_over_baseline_db": max(response_db),
    }


def run_preflight(amplitude: float) -> dict[str, Any]:
    if TRACE_PATH.exists():
        trace = _load_trace()
        if trace["primary_blocks"]:
            raise RuntimeError("primary evidence already exists; preflight is frozen")
        if trace["frozen_protocol"] is not None:
            raise RuntimeError("protocol already frozen")
    else:
        trace = _initial_trace()
    trial = capture_paired_trial(amplitude)
    evaluation = evaluate_preflight(trial)
    trace["preflight"]["attempts"].append(
        {
            "attempt_index": len(trace["preflight"]["attempts"]) + 1,
            "amplitude_full_scale": amplitude,
            "trial": trial,
            "evaluation": evaluation,
        }
    )
    if evaluation["sufficient_to_freeze"]:
        trace["frozen_protocol"] = frozen_protocol(amplitude)
        trace["protocol_frozen_at_utc"] = utc_now()
        trace["status"] = "primary_A1_ready"
    else:
        trace["status"] = "preflight_inadequate"
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
        raise RuntimeError("preflight has not frozen a primary protocol")
    expected = _expected_next_block(trace)
    if position != expected:
        raise RuntimeError(f"expected block {expected}, received {position}")
    if "observer_implementation" not in trace:
        implementation_path = Path(__file__)
        trace["observer_implementation"] = {
            "path": implementation_path.as_posix(),
            "sha256_frozen_before_primary": _sha256_file(implementation_path),
            "version": OBSERVER_VERSION,
        }
    block = {
        "position_block": position,
        "position_role": "A" if position in {"A1", "A2"} else "B",
        "operator_confirmation": operator_note,
        "started_at_utc": utc_now(),
        "trials": [],
        "completed_at_utc": None,
    }
    trace["primary_blocks"].append(block)
    trace["status"] = f"primary_{position}_in_progress"
    _atomic_write_json(TRACE_PATH, trace)
    amplitude = trace["frozen_protocol"]["waveform"]["amplitude_full_scale"]
    for replicate in range(1, TRIALS_PER_BLOCK + 1):
        try:
            trial = capture_paired_trial(float(amplitude))
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


def vector_distance(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("distance vectors must have the same nonzero length")
    return math.sqrt(
        sum((a - b) ** 2 for a, b in zip(left, right, strict=True)) / len(left)
    )


def _centroid(vectors: list[list[float]]) -> list[float]:
    return [statistics.median(values) for values in zip(*vectors, strict=True)]


def evaluate_primary_blocks(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    if [block["position_block"] for block in blocks] != list(BLOCK_ORDER):
        raise ValueError("complete A1, B, A2 blocks are required")
    trials = [trial for block in blocks for trial in block["trials"]]
    failures = [trial for trial in trials if trial["trial_status"] != "paired_observation_complete"]
    if failures:
        return {
            "status": "positional_acoustic_transformation_evidence_insufficient",
            "failure_count": len(failures),
            "source_stability": None,
            "positions": None,
        }
    by_position = {
        block["position_block"]: block["trials"] for block in blocks
    }
    endpoint_vectors = [
        trial["paired_signature"]["endpoint_level_normalized_shape_db"]
        for trial in trials
    ]
    endpoint_levels = [
        trial["paired_signature"]["endpoint_mean_magnitude_db"] for trial in trials
    ]
    endpoint_pair_distances = [
        vector_distance(endpoint_vectors[left], endpoint_vectors[right])
        for left in range(len(endpoint_vectors))
        for right in range(left + 1, len(endpoint_vectors))
    ]
    source_stability = {
        "maximum_shape_pair_distance_db": max(endpoint_pair_distances),
        "mean_level_range_db": max(endpoint_levels) - min(endpoint_levels),
    }
    source_stability["criteria"] = {
        "shape_stable": source_stability["maximum_shape_pair_distance_db"]
        <= MAX_ENDPOINT_SHAPE_DISTANCE_DB,
        "level_stable": source_stability["mean_level_range_db"]
        <= MAX_ENDPOINT_MEAN_LEVEL_RANGE_DB,
    }
    source_stability["gate_passed"] = all(source_stability["criteria"].values())

    position_results: dict[str, Any] = {}
    for position, position_trials in by_position.items():
        absolute = [
            trial["paired_signature"]["absolute_source_normalized_response_db"]
            for trial in position_trials
        ]
        shapes = [
            trial["paired_signature"]["level_normalized_spectral_shape_db"]
            for trial in position_trials
        ]
        centroid = _centroid(absolute)
        shape_centroid = _centroid(shapes)
        absolute_distances = [vector_distance(value, centroid) for value in absolute]
        shape_distances = [vector_distance(value, shape_centroid) for value in shapes]
        position_results[position] = {
            "absolute_centroid_db": centroid,
            "level_normalized_shape_centroid_db": shape_centroid,
            "within_absolute_distances_db": absolute_distances,
            "within_shape_distances_db": shape_distances,
            "within_absolute_median_distance_db": statistics.median(absolute_distances),
            "within_absolute_maximum_distance_db": max(absolute_distances),
            "absolute_response_mean_db_values": [
                trial["paired_signature"]["absolute_response_mean_db"]
                for trial in position_trials
            ],
        }

    a1 = position_results["A1"]["absolute_centroid_db"]
    b = position_results["B"]["absolute_centroid_db"]
    a2 = position_results["A2"]["absolute_centroid_db"]
    a1_b = vector_distance(a1, b)
    a1_a2 = vector_distance(a1, a2)
    a2_b = vector_distance(a2, b)
    within_scale = max(
        position_results["A1"]["within_absolute_median_distance_db"],
        position_results["B"]["within_absolute_median_distance_db"],
    )
    required_separation = max(
        MINIMUM_POSITION_CENTROID_DISTANCE_DB,
        SEPARATION_TO_WITHIN_MEDIAN_MULTIPLIER * within_scale,
    )
    b_discriminated = a1_b > required_separation
    a2_trial_distances = []
    for trial in by_position["A2"]:
        vector = trial["paired_signature"]["absolute_source_normalized_response_db"]
        a2_trial_distances.append(
            {
                "to_A1_centroid_db": vector_distance(vector, a1),
                "to_B_centroid_db": vector_distance(vector, b),
            }
        )
    closer_count = sum(
        item["to_A1_centroid_db"] < item["to_B_centroid_db"]
        for item in a2_trial_distances
    )
    return_criteria = {
        "A2_centroid_closer_to_A1_than_B": a1_a2 < a2_b,
        "A2_to_A1_within_frozen_fraction_of_A1_to_B": (
            a1_a2 <= MAXIMUM_RETURN_TO_SEPARATION_RATIO * a1_b
        ),
        "at_least_four_A2_trials_closer_to_A1": (
            closer_count >= MINIMUM_A2_TRIALS_CLOSER_TO_A1
        ),
    }
    recurrent = all(return_criteria.values())
    if not source_stability["gate_passed"]:
        status = "positional_acoustic_transformation_evidence_insufficient"
    elif not b_discriminated:
        status = "positional_acoustic_transformation_not_discriminated"
    elif recurrent:
        status = "positional_acoustic_transformation_recurrent"
    else:
        status = "positional_acoustic_transformation_observed_not_recurrent"
    return {
        "status": status,
        "failure_count": 0,
        "source_stability": source_stability,
        "positions": position_results,
        "cross_position": {
            "A1_to_B_centroid_distance_db": a1_b,
            "A1_to_A2_centroid_distance_db": a1_a2,
            "A2_to_B_centroid_distance_db": a2_b,
            "B_discrimination_required_distance_db": required_separation,
            "B_discriminated_from_A1": b_discriminated,
            "A2_trial_distances": a2_trial_distances,
            "A2_trials_closer_to_A1_count": closer_count,
            "return_criteria": return_criteria,
            "return_recurrent": recurrent,
        },
    }


def adjudicate() -> dict[str, Any]:
    trace = _load_trace()
    if _expected_next_block(trace) is not None:
        raise RuntimeError("all three primary blocks must complete before adjudication")
    result = evaluate_primary_blocks(trace["primary_blocks"])
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
            "operator-confirmed position block and physical intervention order",
            "source stability, within-position variation, separation, and return distances",
        ],
        "not_observed_or_not_licensed": [
            "specific driver receipt or DAC behavior",
            "pure airborne causality or complete room state",
            "physical transfer function",
            "general acoustic law or tomography",
            "microphone causality beyond the declared operator intervention basis",
        ],
    }
    _atomic_write_json(TRACE_PATH, trace)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight_parser = subparsers.add_parser("preflight")
    preflight_parser.add_argument(
        "--amplitude", type=float, default=PREFLIGHT_AMPLITUDE
    )
    block_parser = subparsers.add_parser("block")
    block_parser.add_argument("position", choices=BLOCK_ORDER)
    block_parser.add_argument("--operator-note", required=True)
    subparsers.add_parser("adjudicate")
    args = parser.parse_args()
    if args.command == "preflight":
        result = run_preflight(args.amplitude)
    elif args.command == "block":
        result = run_primary_block(args.position, args.operator_note)
    else:
        result = adjudicate()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
