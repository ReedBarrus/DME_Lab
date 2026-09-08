from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from src.runtime.acoustic_basis_entry_pressure import (
    RECURRENCE_RANDOM_SEED,
    RECURRENCE_TRIAL_ORDER,
    evaluate_relational_recurrence,
    evaluate_replication_measurements,
    materialize_recurrence_trial_order,
    predeclared_recurrence_basis,
    predeclared_recurrence_trace,
    predeclared_replication_basis,
)


def recurrence_observations(
    values: dict[str, tuple[list[float], list[float]]]
) -> list[dict]:
    offsets = {"C0": 0, "S1": 0, "S2": 0}
    observations = []
    for sequence, condition in enumerate(materialize_recurrence_trial_order(), 1):
        replicate = offsets[condition]
        offsets[condition] += 1
        observations.append(
            {
                "condition": condition,
                "trial_id": f"recurrence-{sequence:02d}",
                "trial_sequence_index": sequence,
                "measurements": {
                    "channels": [
                        {
                            "channel": "microphone_channel_0",
                            "delta_rms_pcm": values[condition][0][replicate],
                        },
                        {
                            "channel": "microphone_channel_1",
                            "delta_rms_pcm": values[condition][1][replicate],
                        },
                    ]
                },
            }
        )
    return observations


class AcousticRelationalRecurrencePressureTest(unittest.TestCase):
    def test_new_seed_materializes_new_frozen_interleaved_order(self) -> None:
        self.assertEqual(RECURRENCE_RANDOM_SEED, 20260910)
        self.assertEqual(tuple(materialize_recurrence_trial_order()), RECURRENCE_TRIAL_ORDER)
        self.assertNotEqual(
            materialize_recurrence_trial_order(),
            predeclared_replication_basis()["randomization"]["trial_order"],
        )
        for condition in ("C0", "S1", "S2"):
            self.assertEqual(materialize_recurrence_trial_order().count(condition), 5)

    def test_recurrence_reuses_measurement_and_discrimination_semantics_exactly(self) -> None:
        old = predeclared_replication_basis()
        new = predeclared_recurrence_basis()
        self.assertEqual(new["primary_measurement"], old["primary_measurement"])
        self.assertEqual(new["discrimination_rule"], old["discrimination_rule"])
        self.assertEqual(new["pairwise_comparisons"], old["pairwise_comparisons"])

    def test_frozen_pattern_passes_only_when_every_pair_and_channel_matches(self) -> None:
        values = {
            "C0": ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
            "S1": ([3, 4, 5, 6, 7], [3, 4, 5, 6, 7]),
            "S2": ([20, 21, 22, 23, 24], [20, 21, 22, 23, 24]),
        }
        analysis = evaluate_replication_measurements(
            recurrence_observations(values), basis=predeclared_recurrence_basis()
        )
        result = evaluate_relational_recurrence(analysis)
        self.assertTrue(result["relationally_recurrent_under_declared_basis"])

        changed = deepcopy(analysis)
        changed["pairwise"]["S2_vs_C0"]["channels"]["microphone_channel_1"][
            "locally_discriminable_under_declared_basis"
        ] = False
        self.assertFalse(
            evaluate_relational_recurrence(changed)[
                "relationally_recurrent_under_declared_basis"
            ]
        )

    def test_normalized_separation_is_descriptive_not_a_rule_substitute(self) -> None:
        values = {
            "C0": ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
            "S1": ([3, 4, 5, 6, 7], [3, 4, 5, 6, 7]),
            "S2": ([20, 21, 22, 23, 24], [20, 21, 22, 23, 24]),
        }
        analysis = evaluate_replication_measurements(
            recurrence_observations(values), basis=predeclared_recurrence_basis()
        )
        result = analysis["pairwise"]["S2_vs_C0"]["channels"]["microphone_channel_0"]
        self.assertEqual(result["descriptive_median_separation_over_max_mad"], 20.0)
        self.assertFalse(result["normalized_separation_is_part_of_rule"])

    def test_completed_trace_preserves_preacquisition_commitment(self) -> None:
        trace = json.loads(
            Path("traces/acoustic_relational_recurrence_pressure_v0.json").read_text(
                encoding="utf-8"
            )
        )
        predeclared = predeclared_recurrence_trace()
        self.assertEqual(trace["predeclaration"], predeclared["predeclaration"])
        self.assertEqual(
            trace["predeclaration_record"], predeclared["predeclaration_record"]
        )
        self.assertTrue(trace["physical_pressure_executed"])
        self.assertEqual(len(trace["trials"]), 15)
        self.assertEqual(
            [trial["condition"] for trial in trace["trials"]],
            materialize_recurrence_trial_order(),
        )

    def test_completed_trace_satisfies_frozen_relational_criterion(self) -> None:
        trace = json.loads(
            Path("traces/acoustic_relational_recurrence_pressure_v0.json").read_text(
                encoding="utf-8"
            )
        )
        recurrence = trace["relational_recurrence"]
        self.assertTrue(recurrence["relationally_recurrent_under_declared_basis"])
        self.assertTrue(
            all(
                matched
                for pair in recurrence["per_pair_channel_match"].values()
                for matched in pair.values()
            )
        )
        self.assertTrue(trace["run_to_run_comparison"]["numerical_realization_changed"])

    def test_completed_trace_preserves_occurrences_through_temporary_pipeline(self) -> None:
        trace = json.loads(
            Path("traces/acoustic_relational_recurrence_pressure_v0.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len({trial["trial_id"] for trial in trace["trials"]}), 15)
        self.assertEqual(len({trial["raw_capture"]["sha256"] for trial in trace["trials"]}), 15)
        self.assertTrue(all(not trial["capture_errors"] for trial in trace["trials"]))
        self.assertTrue(all(not trial["raw_capture"]["persisted"] for trial in trace["trials"]))
        for trial in trace["trials"]:
            self.assertEqual(trial["capture"]["sample_rate_hz"], 48_000)
            self.assertEqual(trial["capture"]["frame_count"], 36_000)
            for channel in trial["measurements"]["channels"]:
                self.assertEqual(
                    channel["delta_rms_pcm"],
                    round(
                        channel["nominal_response_window"]["rms_pcm"]
                        - channel["baseline_window"]["rms_pcm"],
                        6,
                    ),
                )
            if trial["condition"] == "C0":
                self.assertFalse(trial["command"]["requested_playback"])
            else:
                waveform = trial["command"]["waveform"]
                self.assertEqual(waveform["duration_seconds"], 0.18)
                self.assertEqual(waveform["start_frequency_hz"], 700.0)
                self.assertEqual(waveform["end_frequency_hz"], 1700.0)
                self.assertEqual(waveform["amplitude_full_scale"], 0.02)
        pipeline = trace["pipeline"]
        self.assertEqual(pipeline["record_count"], 30)
        self.assertEqual(pipeline["observation_record_count"], 15)
        self.assertEqual(pipeline["admission_record_count"], 15)
        self.assertEqual(pipeline["projection_count"], 15)
        self.assertEqual(len(set(pipeline["recovered_trial_ids"])), 15)
        for key in (
            "integrity_ok",
            "continuity_ok",
            "replay_reproducible",
            "reconstruction_reproducible",
            "projection_reproducible",
            "companion_reproducible",
        ):
            self.assertTrue(pipeline[key])

    def test_completed_trace_records_fresh_process_boundary_without_overclaim(self) -> None:
        trace = json.loads(
            Path("traces/acoustic_relational_recurrence_pressure_v0.json").read_text(
                encoding="utf-8"
            )
        )
        boundary = trace["fresh_acquisition_initialization"]
        self.assertTrue(boundary["new_process_for_block"])
        self.assertFalse(boundary["prior_process_handles_reused"])
        self.assertTrue(boundary["device_handles_opened_and_closed_within_each_trial"])
        self.assertIn("does not establish reset", boundary["scope_limit"])
        self.assertFalse(trace["operator_provenance"]["ambient_silence_machine_verified"])


if __name__ == "__main__":
    unittest.main()
