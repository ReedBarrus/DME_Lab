from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.runtime.acoustic_basis_entry_pressure import (
    AMPLITUDE_FULL_SCALE,
    build_excitation,
    carry_through_pipeline,
    derive_capture_measurements,
    make_acoustic_ingest_envelope,
)


def specimen(name: str, ordinal: int) -> dict:
    raw = struct.pack("<hhhhhhhh", 0, 0, 10, 20, -10, -20, 4, 8)
    measurements = derive_capture_measurements(
        raw,
        sample_rate=10,
        channel_count=2,
        nominal_response_offset_seconds=0.1,
        excitation_seconds=0.1,
        post_response_seconds=0.1,
    )
    body = {
        "observation_id": f"acoustic-observation-v0:{name}",
        "trial_id": f"acoustic-trial-v0:{name}",
        "experiment": "acoustic_basis_entry_pressure_v0",
        "specimen": name,
        "trial_ordinal": ordinal,
        "observer": "winmm_acoustic_basis_pressure",
        "observer_version": "acoustic_basis_pressure_v0",
        "command": {
            "requested_playback": name != "C0",
            "requested_output_channel": None if name == "C0" else "left",
            "waveform": None,
            "output_device": None,
            "host_command_submission_at_utc": None,
            "command_submission_offset_seconds": None,
        },
        "capture": {
            "backend": "test metadata only",
            "input_device": {"device_id": 0, "name": "test"},
            "sample_rate_hz": 10,
            "channel_count": 2,
            "sample_format": "signed_16_bit_little_endian_pcm",
            "frame_count": measurements["frame_count"],
            "host_capture_started_at_utc": "2026-01-01T00:00:00Z",
            "host_capture_finished_at_utc": "2026-01-01T00:00:01Z",
            "host_capture_duration_seconds": 1.0,
            "timing_basis": "test host boundary",
        },
        "measurements": measurements,
        "raw_capture": {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_count": len(raw),
            "persisted": False,
            "disposition": "test buffer absent",
        },
        "capture_errors": [],
        "epistemic_limits": {
            "physical_speaker_realization_observed": False,
            "sampled_microphone_waveform_observed": True,
        },
    }
    return body


def contains_key(value: object, forbidden: str) -> bool:
    if isinstance(value, dict):
        return forbidden in value or any(contains_key(item, forbidden) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, forbidden) for item in value)
    return False


class AcousticBasisEntryPressureTest(unittest.TestCase):
    def test_excitation_is_short_conservative_and_channel_specific(self) -> None:
        left_pcm, left_mono, left = build_excitation("left")
        right_pcm, right_mono, right = build_excitation("right")
        self.assertEqual(left_mono, right_mono)
        self.assertLessEqual(AMPLITUDE_FULL_SCALE, 0.05)
        self.assertLess(left["duration_seconds"], 0.25)
        left_frames = list(struct.iter_unpack("<hh", left_pcm))
        right_frames = list(struct.iter_unpack("<hh", right_pcm))
        self.assertTrue(any(frame[0] for frame in left_frames))
        self.assertTrue(all(frame[1] == 0 for frame in left_frames))
        self.assertTrue(all(frame[0] == 0 for frame in right_frames))
        self.assertTrue(any(frame[1] for frame in right_frames))
        self.assertEqual(left["mono_waveform_sha256"], right["mono_waveform_sha256"])
        self.assertNotEqual(left["stereo_command_sha256"], right["stereo_command_sha256"])

    def test_measurement_derivation_is_deterministic(self) -> None:
        raw = b"".join(struct.pack("<hh", index, -index) for index in range(100))
        first = derive_capture_measurements(
            raw, sample_rate=100, channel_count=2, nominal_response_offset_seconds=0.2
        )
        second = derive_capture_measurements(
            raw, sample_rate=100, channel_count=2, nominal_response_offset_seconds=0.2
        )
        self.assertEqual(first, second)
        self.assertEqual(first["frame_count"], 100)
        self.assertIn("not hardware synchronization", first["nominal_response_window"]["basis"])

    def test_envelope_preserves_missing_physical_claims(self) -> None:
        envelope = make_acoustic_ingest_envelope(specimen("C0", 1))
        self.assertIsNone(envelope["event_time"])
        self.assertIsNone(envelope["signal"]["time"])
        self.assertEqual(envelope["missingness"]["physical_speaker_realization"], "unobserved")
        self.assertEqual(envelope["missingness"]["complete_acoustic_field"], "unobserved")
        self.assertFalse(envelope["signal"]["payload"]["raw_capture"]["persisted"])
        self.assertNotIn("raw_pcm", envelope["signal"]["payload"])

    def test_three_metadata_observations_survive_generic_pipeline(self) -> None:
        observations = [specimen(name, index) for index, name in enumerate(("C0", "S1", "S2"), start=1)]
        with TemporaryDirectory() as tmpdir:
            report = carry_through_pipeline(observations, Path(tmpdir) / "pressure.jsonl")
        self.assertEqual(report["record_count"], 6)
        self.assertEqual(report["decisions"], ["admitted", "admitted", "admitted"])
        self.assertTrue(report["integrity_ok"])
        self.assertTrue(report["continuity_ok"])
        self.assertTrue(report["replay_reproducible"])
        self.assertTrue(report["reconstruction_reproducible"])
        self.assertTrue(report["projection_reproducible"])
        self.assertEqual(report["projection_count"], 3)
        self.assertEqual(report["recovered_trial_ids"], [
            "acoustic-trial-v0:C0",
            "acoustic-trial-v0:S1",
            "acoustic-trial-v0:S2",
        ])

    def test_projection_omits_acoustic_detail_but_retains_navigation(self) -> None:
        with TemporaryDirectory() as tmpdir:
            report = carry_through_pipeline(
                [specimen("C0", 1)], Path(tmpdir) / "pressure.jsonl"
            )
        visibility = report["information_visibility"]
        self.assertTrue(visibility["command_direct_in_reconstruction_nested_observation"])
        self.assertTrue(visibility["measurements_direct_in_reconstruction_nested_observation"])
        self.assertFalse(visibility["command_direct_in_projection"])
        self.assertFalse(visibility["measurements_direct_in_projection"])
        self.assertTrue(visibility["projection_retains_subject_navigation"])
        self.assertFalse(visibility["raw_pcm_persisted"])

    def test_physical_trace_records_bounded_real_trials_without_raw_audio(self) -> None:
        trace_path = Path("traces/acoustic_basis_entry_pressure_v0.json")
        report = json.loads(trace_path.read_text(encoding="utf-8"))
        self.assertTrue(report["physical_pressure_executed"])
        self.assertEqual([trial["specimen"] for trial in report["trials"]], ["C0", "S1", "S2"])
        self.assertEqual(
            [trial["command"]["requested_output_channel"] for trial in report["trials"]],
            [None, "left", "right"],
        )
        self.assertTrue(all(trial["capture_errors"] == [] for trial in report["trials"]))
        self.assertTrue(all(not trial["raw_capture"]["persisted"] for trial in report["trials"]))
        self.assertFalse(contains_key(report, "raw_pcm"))

    def test_physical_trace_preserves_scoped_measurement_not_physical_verdict(self) -> None:
        report = json.loads(
            Path("traces/acoustic_basis_entry_pressure_v0.json").read_text(encoding="utf-8")
        )
        comparison = report["measurement_comparison"]
        self.assertEqual(comparison["replicate_trials_per_command"], 1)
        self.assertFalse(comparison["discrimination_threshold_declared"])
        self.assertIn("speaker channel health", comparison["not_licensed"])
        self.assertTrue(
            all(
                not trial["epistemic_limits"]["physical_speaker_realization_observed"]
                for trial in report["trials"]
            )
        )

    def test_physical_trace_survives_temporary_generic_pipeline(self) -> None:
        report = json.loads(
            Path("traces/acoustic_basis_entry_pressure_v0.json").read_text(encoding="utf-8")
        )
        pipeline = report["pipeline"]
        self.assertEqual(pipeline["record_count"], 6)
        self.assertEqual(pipeline["decisions"], ["admitted", "admitted", "admitted"])
        self.assertTrue(pipeline["integrity_ok"])
        self.assertTrue(pipeline["continuity_ok"])
        self.assertTrue(pipeline["reconstruction_reproducible"])
        self.assertTrue(pipeline["projection_reproducible"])
        self.assertEqual(pipeline["projection_count"], 3)

    def test_operator_device_roles_and_gain_limit_remain_provenance(self) -> None:
        report = json.loads(
            Path("traces/acoustic_basis_entry_pressure_v0.json").read_text(encoding="utf-8")
        )
        context = report["operator_provided_context"]
        self.assertEqual(context["epistemic_status"], "unverified operator-provided provenance")
        self.assertEqual(context["device_roles"]["Realtek"], "room stereo playback")
        self.assertFalse(context["encoded_as_machine_verified_hardware_fact"])
        self.assertEqual(context["post_run_audibility_report"], "operator did not hear playback")
        self.assertFalse(context["audibility_report_machine_verified"])
        self.assertFalse(report["safety_boundary"]["system_output_gain_observed"])
        self.assertFalse(report["safety_boundary"]["further_emission_in_this_pass"])


if __name__ == "__main__":
    unittest.main()
