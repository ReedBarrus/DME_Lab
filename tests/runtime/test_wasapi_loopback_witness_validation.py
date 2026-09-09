from __future__ import annotations

import math
import json
import struct
import unittest
from pathlib import Path

from src.runtime.wasapi_loopback_witness_validation import (
    FREQUENCIES_HZ,
    MEDIAN_DOMINANCE_DB,
    PRIMARY_AMPLITUDE,
    TARGET_FRIENDLY_NAME,
    TRIAL_ORDER,
    _decode_pcm,
    _watcher_command,
    build_tone_pcm,
    derive_pcm_measurements,
    evaluate_primary_trials,
    frozen_discrimination_basis,
    materialize_trial_order,
    parse_mix_format,
    select_realtek_endpoint,
)


def _float_mix() -> dict:
    return {
        "channel_count": 2,
        "sample_rate_hz": 48_000,
        "block_align_bytes": 8,
        "container_bits_per_sample": 32,
        "sample_representation": "float32_little_endian",
    }


def _synthetic_observation(condition: str) -> dict:
    sample_rate = 48_000
    frames = sample_rate // 10
    if condition == "C0":
        frequency = 0.0
        amplitude = 0.000001
    else:
        frequency = FREQUENCIES_HZ[condition]
        amplitude = 0.01
    raw = bytearray()
    for index in range(frames):
        value = amplitude * math.sin(2 * math.pi * frequency * index / sample_rate)
        raw.extend(struct.pack("<ff", value, value))
    measurements = derive_pcm_measurements(bytes(raw), _float_mix())
    return {
        "condition": condition,
        "observation": {"packet_count": 1, "measurements": measurements},
    }


class WasapiLoopbackWitnessValidationTest(unittest.TestCase):
    def test_retained_trace_supports_the_bounded_status(self) -> None:
        trace = json.loads(
            Path("traces/wasapi_loopback_witness_validation_v0.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            trace["primary_status"], "post_mix_loopback_witness_validated"
        )
        self.assertEqual(len(trace["primary_trials"]), 15)
        self.assertTrue(all(trace["primary_analysis"]["criteria"].values()))
        self.assertTrue(trace["fresh_process_reacquisition"]["succeeded"])
        self.assertFalse(
            trace["process_boundary"]["watchers_received_condition_labels"]
        )
        self.assertFalse(
            trace["process_boundary"][
                "watchers_received_playback_frequency_or_waveform"
            ]
        )
        self.assertFalse(trace["canonical_history"]["changed"])
        self.assertFalse(trace["raw_pcm"]["persisted"])

    def test_trial_order_is_frozen_and_balanced(self) -> None:
        self.assertEqual(tuple(materialize_trial_order()), TRIAL_ORDER)
        for condition in ("C0", "S1", "S2"):
            self.assertEqual(TRIAL_ORDER.count(condition), 5)

    def test_primary_level_is_below_prior_acoustic_level(self) -> None:
        self.assertLess(PRIMARY_AMPLITUDE, 0.02)
        raw, parameters = build_tone_pcm(900.0, PRIMARY_AMPLITUDE)
        self.assertTrue(raw)
        self.assertLess(parameters["nominal_level_dbfs"], -50.0)

    def test_tone_builder_rejects_above_bounded_ceiling(self) -> None:
        with self.assertRaises(ValueError):
            build_tone_pcm(900.0, 0.006)

    def test_extensible_float_mix_format_is_parsed(self) -> None:
        subformat = bytes.fromhex("0300000000001000800000aa00389b71")
        raw = struct.pack("<HHIIHHHHI", 0xFFFE, 2, 48_000, 384_000, 8, 32, 22, 32, 3) + subformat
        parsed = parse_mix_format(raw)
        self.assertEqual(parsed["sample_representation"], "float32_little_endian")
        self.assertEqual(parsed["channel_count"], 2)
        self.assertEqual(parsed["sample_rate_hz"], 48_000)

    def test_float_pcm_decoder_preserves_channel_separation(self) -> None:
        raw = struct.pack("<ffff", 0.25, -0.5, 0.75, -1.0)
        channels = _decode_pcm(raw, _float_mix())
        self.assertEqual(channels, [[0.25, 0.75], [-0.5, -1.0]])

    def test_frequency_projection_separates_synthetic_tones(self) -> None:
        s1 = _synthetic_observation("S1")["observation"]["measurements"]
        s2 = _synthetic_observation("S2")["observation"]["measurements"]
        self.assertGreater(s1["combined_single_frequency_rms"]["900"], 1000 * s1["combined_single_frequency_rms"]["1500"])
        self.assertGreater(s2["combined_single_frequency_rms"]["1500"], 1000 * s2["combined_single_frequency_rms"]["900"])

    def test_frozen_evaluator_accepts_synthetic_discrimination(self) -> None:
        trials = [_synthetic_observation(condition) for condition in TRIAL_ORDER]
        result = evaluate_primary_trials(trials)
        self.assertTrue(result["discriminated"])
        self.assertGreaterEqual(min(result["commanded_frequency_dominance_db"]["S1"]), MEDIAN_DOMINANCE_DB)

    def test_packet_absence_in_commanded_trial_prevents_validation(self) -> None:
        trials = [_synthetic_observation(condition) for condition in TRIAL_ORDER]
        next(item for item in trials if item["condition"] == "S1")["observation"]["packet_count"] = 0
        result = evaluate_primary_trials(trials)
        self.assertFalse(result["discriminated"])
        self.assertFalse(result["criteria"]["all_commanded_trials_have_packets"])

    def test_endpoint_selection_requires_exact_active_realtek_name(self) -> None:
        selected = select_realtek_endpoint([
            {"friendly_name": TARGET_FRIENDLY_NAME, "endpoint_state_active": True, "endpoint_id": "realtek"},
            {"friendly_name": "Speakers (XIBERIA)", "endpoint_state_active": True, "endpoint_id": "headset"},
        ])
        self.assertEqual(selected["endpoint_id"], "realtek")
        with self.assertRaises(RuntimeError):
            select_realtek_endpoint([])

    def test_watcher_command_has_no_condition_or_waveform_metadata(self) -> None:
        command = _watcher_command("endpoint", 0.7, __import__("pathlib").Path("ready"), __import__("pathlib").Path("result"), __import__("pathlib").Path("pcm"))
        joined = " ".join(command)
        self.assertNotIn("S1", joined)
        self.assertNotIn("900", joined)
        self.assertNotIn("amplitude", joined)

    def test_frozen_basis_does_not_require_exact_pcm_equality(self) -> None:
        basis = frozen_discrimination_basis()
        self.assertTrue(basis["declared_before_primary_acquisition"])
        self.assertFalse(basis["exact_pcm_equality_required"])


if __name__ == "__main__":
    unittest.main()
