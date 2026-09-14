from __future__ import annotations

from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from src.runtime import behavioral_coupling_consequence_observability as pressure
from src.runtime.lm_studio_policy_adapter import (
    LMStudioConstrainedActionPolicyAdapter,
    structured_action_response_format,
)


def _transport_for(action: str):
    def transport(endpoint, body, headers, timeout):
        del endpoint, body, headers, timeout
        return 200, json.dumps(
            {"choices": [{"message": {"content": json.dumps({"action": action})}}]}
        )

    return transport


def _adapter(action: str = pressure.ACT_A) -> LMStudioConstrainedActionPolicyAdapter:
    return LMStudioConstrainedActionPolicyAdapter(
        pressure._config(),
        action_enum=pressure.ACTION_ENUM,
        transport=_transport_for(action),
    )


class BehavioralCouplingConsequenceObservabilityTest(unittest.TestCase):
    def test_schedule_has_four_repetitions_per_logical_cell(self) -> None:
        schedule = pressure.compile_schedule()
        self.assertEqual(len(schedule), 16)
        self.assertEqual(len({row["episode_id"] for row in schedule}), 16)
        for consequence in (pressure.RED, pressure.BLUE):
            for timing in pressure.RECEIPT_TIMINGS:
                rows = [
                    row
                    for row in schedule
                    if row["authoritative_stage_1_consequence"] == consequence
                    and row["receipt_timing"] == timing
                ]
                self.assertEqual([row["repetition_index"] for row in rows], [1, 2, 3, 4])

    def test_late_stage_2_inputs_are_byte_identical(self) -> None:
        equivalence = pressure.late_input_equivalence()
        self.assertTrue(equivalence["serializations_match"])
        self.assertTrue(equivalence["hashes_match"])
        self.assertEqual(
            equivalence["RED_LATE_serialization"],
            equivalence["BLUE_LATE_serialization"],
        )
        self.assertEqual(
            equivalence["RED_LATE_sha256"], equivalence["BLUE_LATE_sha256"]
        )
        visible = json.loads(equivalence["RED_LATE_serialization"])
        self.assertEqual(visible["fixed_task"], pressure.FIXED_TASK)
        self.assertEqual(visible["policy_visible_protocol_history"], [])

    def test_consequence_occurs_before_inference_in_both_timings(self) -> None:
        early = pressure._run_episode(pressure.compile_schedule()[0], _adapter())
        late = pressure._run_episode(pressure.compile_schedule()[4], _adapter())
        self.assertEqual(early["consequence_occurrence_event_index"], 1)
        self.assertEqual(late["consequence_occurrence_event_index"], 1)
        self.assertLess(
            early["consequence_occurrence_event_index"],
            early["receipt_delivery_event_index"],
        )
        self.assertLess(
            early["receipt_delivery_event_index"],
            early["stage_2_commitment_event_index"],
        )
        self.assertLess(
            late["consequence_occurrence_event_index"],
            late["stage_2_commitment_event_index"],
        )
        self.assertLess(
            late["stage_2_commitment_event_index"],
            late["receipt_delivery_event_index"],
        )

    def test_early_receipt_is_visible_and_late_receipt_is_withheld(self) -> None:
        schedule = pressure.compile_schedule()
        early_adapter = _adapter()
        late_adapter = _adapter()
        early = pressure._run_episode(schedule[0], early_adapter)
        late = pressure._run_episode(schedule[4], late_adapter)
        early_visible = json.loads(
            early_adapter.call_records[0]["serialized_policy_visible_request"]
        )
        late_visible = json.loads(
            late_adapter.call_records[0]["serialized_policy_visible_request"]
        )
        self.assertEqual(
            early_visible["policy_visible_protocol_history"],
            [
                {
                    "event_type": "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                    "payload": {"authoritative_consequence": "RED"},
                }
            ],
        )
        self.assertEqual(late_visible["policy_visible_protocol_history"], [])
        self.assertEqual(
            pressure._event_types(early),
            pressure.build_freeze_artifact()["event_order"][pressure.EARLY],
        )
        self.assertEqual(
            pressure._event_types(late),
            pressure.build_freeze_artifact()["event_order"][pressure.LATE],
        )

    def test_fixed_response_contract_scores_against_stage_1_consequence(self) -> None:
        red_spec = pressure.compile_schedule()[0]
        blue_spec = pressure.compile_schedule()[8]
        red = pressure._run_episode(red_spec, _adapter(pressure.ACT_A))
        blue = pressure._run_episode(blue_spec, _adapter(pressure.ACT_A))
        self.assertEqual(red["stage_2_action_implied_color"], "RED")
        self.assertTrue(red["success"])
        self.assertEqual(blue["stage_2_action_implied_color"], "RED")
        self.assertFalse(blue["success"])
        self.assertEqual(red["response_contract_rows"], blue["response_contract_rows"])

    def test_freeze_reconstructs_hashes_and_zero_calls(self) -> None:
        freeze = pressure.build_freeze_artifact()
        self.assertEqual(freeze["protocol_sha256"], pressure.protocol_hash())
        self.assertEqual(freeze["schedule_sha256"], pressure.schedule_hash())
        self.assertEqual(
            freeze["response_action_schema_sha256"], pressure.action_schema_hash()
        )
        self.assertEqual(freeze["new_qualification_model_calls_made"], 0)
        self.assertEqual(freeze["empirical_model_calls_made"], 0)
        self.assertFalse(freeze["actual_consequence_timing_varied"])

    def test_validator_detects_late_consequence_leak(self) -> None:
        schedule = pressure.compile_schedule()
        episodes = []
        calls = []
        for spec in schedule:
            adapter = _adapter()
            episode = pressure._run_episode(spec, adapter)
            episodes.append(episode)
            calls.append({"episode_id": spec["episode_id"], **adapter.call_records[0]})
        late_index = 4
        visible = json.loads(calls[late_index]["serialized_policy_visible_request"])
        visible["policy_visible_protocol_history"] = [
            {
                "event_type": "CONSEQUENCE_RECEIPT_DELIVERED_TO_POLICY",
                "payload": {"authoritative_consequence": "RED"},
            }
        ]
        calls[late_index]["serialized_policy_visible_request"] = json.dumps(visible)
        validity = pressure.validate_evidence(schedule, episodes, calls)
        self.assertEqual(validity["status"], "EXPERIMENT_INVALID")
        self.assertTrue(
            any("POLICY_VISIBILITY_MISMATCH" in wound for wound in validity["invalidity_wounds"])
        )

    def test_offline_execution_retains_exact_16_stage_2_calls(self) -> None:
        freeze = pressure.build_freeze_artifact()
        qualification = {
            "action_schema_sha256": pressure.action_schema_hash(),
            "scientific_schedule_entries_consumed": 0,
            "result": {"status": "PASS"},
        }
        retained = {}
        actions = iter(
            pressure.ACT_A if index % 2 == 0 else pressure.ACT_B
            for index in range(16)
        )

        def write(path, value):
            retained[str(path)] = deepcopy(value)

        with (
            patch.object(pressure, "load_validated_freeze", return_value=freeze),
            patch.object(
                pressure,
                "load_qualified_action_surface",
                return_value=qualification,
            ),
            patch.object(pressure, "_new_adapter", side_effect=lambda: _adapter(next(actions))),
            patch.object(pressure, "_write_new_json", side_effect=write),
            patch.object(pressure, "OUTPUT_PATHS", ()),
        ):
            result = pressure.execute_once("basis-commit")

        self.assertEqual(result["empirical_episode_count"], 16)
        self.assertEqual(result["stage_2_policy_decision_count"], 16)
        self.assertEqual(result["stage_1_policy_decision_count"], 0)
        self.assertEqual(result["empirical_retry_count"], 0)
        self.assertEqual(result["new_qualification_call_count"], 0)
        self.assertFalse(result["actual_consequence_timing_varied"])
        self.assertEqual(result["validity"]["status"], "VALID")
        calls = retained[str(pressure.CALLS_PATH)]["calls"]
        self.assertEqual(len(calls), 16)
        for call in calls:
            request = json.loads(call["serialized_http_request"])
            self.assertEqual(len(request["messages"]), 1)
            self.assertNotIn("previous_response_id", request)
            self.assertNotIn("tools", request)
            self.assertEqual(
                request["response_format"],
                structured_action_response_format(pressure.ACTION_ENUM),
            )


if __name__ == "__main__":
    unittest.main()
