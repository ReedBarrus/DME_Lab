from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from src.runtime.acoustic_positional_transformation_pressure import (
    BLOCK_ORDER,
    FREQUENCY_BINS_HZ,
    MAXIMUM_AMPLITUDE,
    POSITION_DEFINITIONS,
    TRIALS_PER_BLOCK,
    evaluate_primary_blocks,
    frozen_protocol,
    vector_distance,
)


def _trial(position: str, absolute: list[float], endpoint_shift: float = 0.0) -> dict:
    mean = sum(absolute) / len(absolute)
    endpoint = [value + endpoint_shift for value in [0.0, 0.1, -0.1, 0.2, -0.2] * 2]
    endpoint = endpoint[: len(FREQUENCY_BINS_HZ)]
    endpoint_mean = sum(endpoint) / len(endpoint)
    return {
        "position_block": position,
        "trial_status": "paired_observation_complete",
        "paired_signature": {
            "absolute_source_normalized_response_db": absolute,
            "absolute_response_mean_db": mean,
            "level_normalized_spectral_shape_db": [value - mean for value in absolute],
            "endpoint_level_normalized_shape_db": [
                value - endpoint_mean for value in endpoint
            ],
            "endpoint_mean_magnitude_db": -50.0 + endpoint_shift,
        },
    }


def _blocks(a2_like_a: bool = True) -> list[dict]:
    base_a = [-20.0 + index * 0.1 for index in range(len(FREQUENCY_BINS_HZ))]
    base_b = [value + (4.0 if index % 2 else -4.0) for index, value in enumerate(base_a)]
    base_a2 = [value + 0.1 for value in base_a] if a2_like_a else [value + 0.1 for value in base_b]
    result = []
    for position, base in zip(BLOCK_ORDER, (base_a, base_b, base_a2), strict=True):
        trials = []
        for replicate in range(TRIALS_PER_BLOCK):
            shift = (replicate - 2) * 0.02
            trials.append(_trial(position, [value + shift for value in base]))
        result.append({"position_block": position, "trials": trials})
    return result


class AcousticPositionalTransformationPressureTest(unittest.TestCase):
    def test_retained_trace_supports_bounded_recurrence_status(self) -> None:
        trace = json.loads(
            Path(
                "traces/acoustic_positional_transformation_pressure_v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            trace["status"], "positional_acoustic_transformation_recurrent"
        )
        self.assertEqual(
            [block["position_block"] for block in trace["primary_blocks"]],
            list(BLOCK_ORDER),
        )
        trials = [
            trial for block in trace["primary_blocks"] for trial in block["trials"]
        ]
        self.assertEqual(len(trials), 15)
        self.assertTrue(
            all(trial["trial_status"] == "paired_observation_complete" for trial in trials)
        )
        self.assertEqual(
            len({trial["endpoint"]["observation"]["watcher_pid"] for trial in trials}),
            15,
        )
        self.assertTrue(
            all(
                trial["endpoint"]["watcher_process_separate_from_emitter"]
                and not trial["endpoint"]["watcher_received_condition_or_position"]
                and not trial["endpoint"]["watcher_received_waveform_or_frequency"]
                for trial in trials
            )
        )
        self.assertTrue(trace["adjudication"]["source_stability"]["gate_passed"])
        self.assertTrue(
            trace["adjudication"]["cross_position"]["B_discriminated_from_A1"]
        )
        self.assertTrue(
            trace["adjudication"]["cross_position"]["return_recurrent"]
        )
        self.assertFalse(trace["canonical_history"]["changed"])
        self.assertTrue(
            all(
                not trial["endpoint"]["raw_pcm"]["persisted"]
                and not trial["microphone"]["raw_pcm"]["persisted"]
                for trial in trials
            )
        )

    def test_protocol_freezes_A1_B_A2_and_five_trials(self) -> None:
        protocol = frozen_protocol(0.005)
        self.assertEqual(protocol["block_order"], list(BLOCK_ORDER))
        self.assertEqual(protocol["trials_per_block"], 5)
        self.assertTrue(protocol["declared_before_primary_acquisition"])
        self.assertIn("original", POSITION_DEFINITIONS["A"]["role"])

    def test_protocol_rejects_amplitude_above_prior_ceiling(self) -> None:
        with self.assertRaises(ValueError):
            frozen_protocol(MAXIMUM_AMPLITUDE + 0.001)

    def test_measurement_is_named_response_signature_not_transfer_function(self) -> None:
        measurement = frozen_protocol(0.005)["measurement"]
        self.assertIn("not a physical transfer function", measurement["claim"])
        self.assertIn("level_normalized_shape_db", measurement)
        self.assertIn("absolute_source_normalized_db", measurement)

    def test_vector_distance_is_rms_euclidean(self) -> None:
        self.assertAlmostEqual(vector_distance([0.0, 0.0], [3.0, 4.0]), (12.5) ** 0.5)

    def test_synthetic_return_is_recurrent(self) -> None:
        result = evaluate_primary_blocks(_blocks())
        self.assertEqual(result["status"], "positional_acoustic_transformation_recurrent")
        self.assertTrue(result["source_stability"]["gate_passed"])
        self.assertTrue(result["cross_position"]["B_discriminated_from_A1"])
        self.assertTrue(result["cross_position"]["return_recurrent"])

    def test_B_like_return_is_observed_not_recurrent(self) -> None:
        result = evaluate_primary_blocks(_blocks(a2_like_a=False))
        self.assertEqual(
            result["status"],
            "positional_acoustic_transformation_observed_not_recurrent",
        )

    def test_nondiscriminated_B_gets_exact_status(self) -> None:
        blocks = _blocks()
        blocks[1]["trials"] = deepcopy(blocks[0]["trials"])
        for trial in blocks[1]["trials"]:
            trial["position_block"] = "B"
        result = evaluate_primary_blocks(blocks)
        self.assertEqual(
            result["status"], "positional_acoustic_transformation_not_discriminated"
        )

    def test_capture_failure_is_preserved_as_insufficient(self) -> None:
        blocks = _blocks()
        blocks[0]["trials"][0] = {
            "position_block": "A1",
            "trial_status": "paired_observation_failed",
            "failure": "synthetic",
        }
        result = evaluate_primary_blocks(blocks)
        self.assertEqual(
            result["status"],
            "positional_acoustic_transformation_evidence_insufficient",
        )
        self.assertEqual(result["failure_count"], 1)

    def test_source_instability_blocks_positional_attribution(self) -> None:
        blocks = _blocks()
        blocks[2]["trials"][0]["paired_signature"][
            "endpoint_mean_magnitude_db"
        ] += 3.0
        result = evaluate_primary_blocks(blocks)
        self.assertFalse(result["source_stability"]["gate_passed"])
        self.assertEqual(
            result["status"],
            "positional_acoustic_transformation_evidence_insufficient",
        )


if __name__ == "__main__":
    unittest.main()
