from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from src.runtime.acoustic_positional_transformation_pressure import (
    BLOCK_ORDER,
    FREQUENCY_BINS_HZ,
    TRIALS_PER_BLOCK,
)
from src.runtime.acoustic_source_side_positional_return_replication import (
    PRIOR_TRACE_PATH,
    QUIET_SOURCE_DECLARATION,
    TRACE_PATH,
    evaluate_replication_blocks,
    frozen_protocol,
)


def _trial(position: str, absolute: list[float], endpoint_shift: float = 0.0) -> dict:
    mean = sum(absolute) / len(absolute)
    endpoint = [value + endpoint_shift for value in [0.0, 0.1, -0.1, 0.2, -0.2] * 2]
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
    base_b = [
        value + (4.0 if index % 2 else -4.0)
        for index, value in enumerate(base_a)
    ]
    base_a2 = (
        [value + 0.1 for value in base_a]
        if a2_like_a
        else [value + 0.1 for value in base_b]
    )
    result = []
    for position, base in zip(BLOCK_ORDER, (base_a, base_b, base_a2), strict=True):
        trials = []
        for replicate in range(TRIALS_PER_BLOCK):
            shift = (replicate - 2) * 0.02
            trials.append(_trial(position, [value + shift for value in base]))
        result.append({"position_block": position, "trials": trials})
    return result


class AcousticSourceSidePositionalReturnReplicationTest(unittest.TestCase):
    def test_retained_replication_trace_supports_class_E_without_rewriting_prior(self) -> None:
        trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            trace["status"], "source_side_positional_return_replication_recurrent"
        )
        self.assertEqual(trace["adjudication"]["outcome_class"], "E")
        self.assertTrue(trace["adjudication"]["independently_adjudicated"])
        self.assertFalse(trace["adjudication"]["prior_specimen_used_as_calibration"])
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
                and not trial["endpoint"]["raw_pcm"]["persisted"]
                and not trial["microphone"]["raw_pcm"]["persisted"]
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
        self.assertEqual(
            hashlib.sha256(PRIOR_TRACE_PATH.read_bytes()).hexdigest(),
            trace["lineage"]["prior_trace_sha256"],
        )
        implementation = Path(trace["observer_implementation"]["path"])
        self.assertEqual(
            hashlib.sha256(implementation.read_bytes()).hexdigest(),
            trace["observer_implementation"]["sha256_frozen_before_primary"],
        )

    def test_protocol_is_unchanged_and_prior_specimen_is_not_calibration(self) -> None:
        protocol = frozen_protocol()
        self.assertEqual(protocol["waveform"]["amplitude_full_scale"], 0.02)
        self.assertEqual(protocol["waveform"]["duration_seconds"], 0.18)
        self.assertEqual(protocol["block_order"], list(BLOCK_ORDER))
        self.assertEqual(protocol["trials_per_block"], 5)
        self.assertEqual(
            protocol["replication"]["quiet_source_declaration"],
            QUIET_SOURCE_DECLARATION,
        )
        self.assertFalse(protocol["replication"]["prior_specimen_used_as_calibration"])

    def test_class_E_is_recurrent(self) -> None:
        result = evaluate_replication_blocks(_blocks())
        self.assertEqual(result["outcome_class"], "E")
        self.assertEqual(
            result["status"], "source_side_positional_return_replication_recurrent"
        )

    def test_class_D_is_observed_not_recurrent(self) -> None:
        result = evaluate_replication_blocks(_blocks(a2_like_a=False))
        self.assertEqual(result["outcome_class"], "D")
        self.assertEqual(
            result["status"],
            "source_side_positional_return_replication_observed_not_recurrent",
        )

    def test_class_C_is_not_discriminated(self) -> None:
        blocks = _blocks()
        blocks[1]["trials"] = deepcopy(blocks[0]["trials"])
        for trial in blocks[1]["trials"]:
            trial["position_block"] = "B"
        result = evaluate_replication_blocks(blocks)
        self.assertEqual(result["outcome_class"], "C")
        self.assertEqual(
            result["status"],
            "source_side_positional_return_replication_not_discriminated",
        )

    def test_class_B_is_source_gate_failure(self) -> None:
        blocks = _blocks()
        blocks[2]["trials"][0]["paired_signature"][
            "endpoint_mean_magnitude_db"
        ] += 3.0
        result = evaluate_replication_blocks(blocks)
        self.assertEqual(result["outcome_class"], "B")
        self.assertEqual(
            result["status"],
            "source_side_positional_return_replication_source_gate_failed",
        )

    def test_class_A_is_instrumentation_failure(self) -> None:
        blocks = _blocks()
        blocks[0]["trials"][0] = {
            "position_block": "A1",
            "trial_status": "paired_observation_failed",
            "failure": "synthetic",
        }
        result = evaluate_replication_blocks(blocks)
        self.assertEqual(result["outcome_class"], "A")
        self.assertEqual(
            result["status"],
            "source_side_positional_return_replication_instrumentation_failure",
        )


if __name__ == "__main__":
    unittest.main()
