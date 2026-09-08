from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from src.runtime.acoustic_basis_entry_pressure import (
    REPLICATION_RANDOM_SEED,
    REPLICATION_TRIAL_ORDER,
    evaluate_replication_measurements,
    materialize_replication_trial_order,
    predeclared_replication_basis,
)


def observations_with_deltas(values: dict[str, tuple[list[float], list[float]]]) -> list[dict]:
    condition_offsets = {"C0": 0, "S1": 0, "S2": 0}
    observations = []
    for sequence_index, condition in enumerate(materialize_replication_trial_order(), start=1):
        replicate = condition_offsets[condition]
        condition_offsets[condition] += 1
        observations.append(
            {
                "condition": condition,
                "trial_id": f"trial-{sequence_index:02d}",
                "trial_sequence_index": sequence_index,
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


class AcousticReplicationPressureTest(unittest.TestCase):
    def test_seed_materializes_exact_frozen_interleaved_order(self) -> None:
        self.assertEqual(REPLICATION_RANDOM_SEED, 20260903)
        self.assertEqual(
            materialize_replication_trial_order(),
            ["S2", "S1", "C0", "C0", "S2", "C0", "S2", "S1", "C0", "S1", "S2", "S1", "S2", "C0", "S1"],
        )
        self.assertEqual(tuple(materialize_replication_trial_order()), REPLICATION_TRIAL_ORDER)
        for condition in ("C0", "S1", "S2"):
            self.assertEqual(materialize_replication_trial_order().count(condition), 5)

    def test_predeclared_basis_freezes_delta_and_both_criteria(self) -> None:
        basis = predeclared_replication_basis()
        self.assertTrue(basis["declared_before_physical_acquisition"])
        self.assertEqual(basis["primary_measurement"]["name"], "delta_rms_pcm")
        rule = basis["discrimination_rule"]
        self.assertTrue(rule["both_conditions_required"])
        self.assertIn("ranges do not overlap", rule["range_condition"])
        self.assertIn("3 * max", rule["separation_condition"])
        self.assertIn("mark criterion_degenerate_insufficient", rule["zero_mad_policy"])

    def test_nonoverlap_and_mad_separation_pass_when_mad_is_nonzero(self) -> None:
        values = {
            "C0": ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
            "S1": ([20, 21, 22, 23, 24], [20, 21, 22, 23, 24]),
            "S2": ([40, 41, 42, 43, 44], [40, 41, 42, 43, 44]),
        }
        report = evaluate_replication_measurements(observations_with_deltas(values))
        for pair in report["pairwise"].values():
            for channel in pair["channels"].values():
                self.assertTrue(channel["ranges_do_not_overlap"])
                self.assertTrue(channel["separation_exceeds_three_times_max_mad"])
                self.assertFalse(channel["mad_degenerate"])
                self.assertTrue(channel["locally_discriminable_under_declared_basis"])

    def test_overlapping_ranges_do_not_discriminate(self) -> None:
        values = {
            "C0": ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
            "S1": ([3, 4, 5, 6, 7], [3, 4, 5, 6, 7]),
            "S2": ([6, 7, 8, 9, 10], [6, 7, 8, 9, 10]),
        }
        report = evaluate_replication_measurements(observations_with_deltas(values))
        result = report["pairwise"]["S1_vs_C0"]["channels"]["microphone_channel_0"]
        self.assertFalse(result["ranges_do_not_overlap"])
        self.assertFalse(result["locally_discriminable_under_declared_basis"])

    def test_zero_mad_is_degenerate_without_substitute(self) -> None:
        values = {
            "C0": ([1, 1, 1, 1, 1], [1, 1, 1, 1, 1]),
            "S1": ([10, 11, 12, 13, 14], [10, 11, 12, 13, 14]),
            "S2": ([20, 21, 22, 23, 24], [20, 21, 22, 23, 24]),
        }
        report = evaluate_replication_measurements(observations_with_deltas(values))
        result = report["pairwise"]["S1_vs_C0"]["channels"]["microphone_channel_0"]
        self.assertTrue(result["ranges_do_not_overlap"])
        self.assertTrue(result["mad_degenerate"])
        self.assertEqual(result["status"], "criterion_degenerate_insufficient")
        self.assertFalse(result["locally_discriminable_under_declared_basis"])

    def test_wrong_trial_order_is_rejected(self) -> None:
        values = {condition: ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]) for condition in ("C0", "S1", "S2")}
        observations = observations_with_deltas(values)
        wrong = deepcopy(observations)
        wrong[0], wrong[1] = wrong[1], wrong[0]
        with self.assertRaisesRegex(ValueError, "predeclared trial order"):
            evaluate_replication_measurements(wrong)

    def test_completed_trace_preserves_predeclaration_and_each_occurrence(self) -> None:
        trace = json.loads(Path("traces/acoustic_replication_pressure_v0.json").read_text(encoding="utf-8"))
        self.assertEqual(trace["status"], "physical_acquisition_complete")
        self.assertTrue(trace["physical_pressure_executed"])
        self.assertTrue(trace["primary_adjudication"])
        self.assertEqual(trace["predeclaration"], predeclared_replication_basis())
        self.assertEqual([trial["condition"] for trial in trace["trials"]], list(REPLICATION_TRIAL_ORDER))
        self.assertEqual(len(trace["trials"]), 15)
        self.assertEqual(len({trial["trial_id"] for trial in trace["trials"]}), 15)
        self.assertTrue(all(not trial["capture_errors"] for trial in trace["trials"]))
        self.assertFalse(trace["raw_recordings_committed"])
        self.assertTrue(all(not trial["raw_capture"]["persisted"] for trial in trace["trials"]))

    def test_completed_trace_matches_frozen_delta_and_rule_results(self) -> None:
        trace = json.loads(Path("traces/acoustic_replication_pressure_v0.json").read_text(encoding="utf-8"))
        for trial in trace["trials"]:
            for channel in trial["measurements"]["channels"]:
                expected = round(
                    channel["nominal_response_window"]["rms_pcm"]
                    - channel["baseline_window"]["rms_pcm"],
                    6,
                )
                self.assertEqual(channel["delta_rms_pcm"], expected)

        pairwise = trace["replicated_measurement_analysis"]["pairwise"]
        for channel in ("microphone_channel_0", "microphone_channel_1"):
            self.assertFalse(
                pairwise["S1_vs_C0"]["channels"][channel]["locally_discriminable_under_declared_basis"]
            )
            self.assertTrue(
                pairwise["S2_vs_C0"]["channels"][channel]["locally_discriminable_under_declared_basis"]
            )
            self.assertTrue(
                pairwise["S1_vs_S2"]["channels"][channel]["locally_discriminable_under_declared_basis"]
            )

    def test_completed_trace_preserves_all_trials_through_temporary_pipeline(self) -> None:
        trace = json.loads(Path("traces/acoustic_replication_pressure_v0.json").read_text(encoding="utf-8"))
        pipeline = trace["pipeline"]
        self.assertTrue(pipeline["temporary_ledger"])
        self.assertEqual(pipeline["observation_record_count"], 15)
        self.assertEqual(pipeline["admission_record_count"], 15)
        self.assertEqual(pipeline["record_count"], 30)
        self.assertEqual(pipeline["projection_count"], 15)
        self.assertEqual(pipeline["decisions"], ["admitted"] * 15)
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
        visibility = pipeline["information_visibility"]
        self.assertTrue(visibility["measurements_direct_in_raw_observation"])
        self.assertTrue(visibility["measurements_direct_in_reconstruction_nested_observation"])
        self.assertFalse(visibility["measurements_direct_in_projection"])
        self.assertFalse(visibility["raw_pcm_persisted"])

    def test_video_contaminated_block_is_retained_and_not_primary(self) -> None:
        trace = json.loads(
            Path("traces/acoustic_replication_pressure_v0_observer_reported_video_contaminated.json").read_text(
                encoding="utf-8"
            )
        )
        provenance = trace["operator_provenance"]
        self.assertFalse(trace["primary_adjudication"])
        self.assertIn("video audio", provenance["post_capture_report"])
        self.assertIn("excluded", provenance["analysis_disposition"])
        self.assertEqual(len(trace["trials"]), 15)


if __name__ == "__main__":
    unittest.main()
