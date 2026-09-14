from __future__ import annotations

from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from src.runtime import behavioral_coupling_binding_observability as pressure
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


class BehavioralCouplingBindingObservabilityTest(unittest.TestCase):
    def test_schedule_has_four_repetitions_per_logical_cell(self) -> None:
        schedule = pressure.compile_schedule()
        self.assertEqual(len(schedule), 16)
        self.assertEqual(len({row["episode_id"] for row in schedule}), 16)
        for contract in pressure.CONTRACTS:
            for timing in pressure.DISCLOSURE_TIMINGS:
                rows = [
                    row
                    for row in schedule
                    if row["world_contract"] == contract
                    and row["disclosure_timing"] == timing
                ]
                self.assertEqual([row["repetition_index"] for row in rows], [1, 2, 3, 4])

    def test_late_precommitment_inputs_are_byte_identical(self) -> None:
        equivalence = pressure.late_input_equivalence()
        self.assertTrue(equivalence["serializations_match"])
        self.assertTrue(equivalence["hashes_match"])
        self.assertEqual(
            equivalence["C0_LATE_serialization"],
            equivalence["C1_LATE_serialization"],
        )
        self.assertEqual(
            equivalence["C0_LATE_sha256"], equivalence["C1_LATE_sha256"]
        )
        visible = json.loads(equivalence["C0_LATE_serialization"])
        self.assertEqual(visible["fixed_task"], pressure.FIXED_TASK)
        self.assertEqual(visible["policy_visible_protocol_history"], [])
        serialized = equivalence["C0_LATE_serialization"]
        for forbidden in ("C0", "C1", "repetition", "episode", "produced_color"):
            self.assertNotIn(forbidden, serialized)

    def test_early_discloses_exact_binding_and_late_does_not(self) -> None:
        schedule = pressure.compile_schedule()
        early_spec = schedule[0]
        late_spec = schedule[4]
        early_adapter = _adapter()
        late_adapter = _adapter()
        early = pressure._run_episode(early_spec, early_adapter)
        late = pressure._run_episode(late_spec, late_adapter)
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
                    "event_type": "BINDING_DISCLOSED",
                    "payload": {
                        "binding_rows": pressure.binding_rows(pressure.C0),
                        "serialized_binding_text": pressure.serialized_binding_text(
                            pressure.C0
                        ),
                    },
                }
            ],
        )
        self.assertEqual(late_visible["policy_visible_protocol_history"], [])
        self.assertEqual(
            pressure._event_types(early),
            [
                "WORLD_CONTRACT_ESTABLISHED",
                "BINDING_DISCLOSED",
                "POLICY_ACTION_REQUESTED",
                "WORLD_ACTION_RECEIPT",
                "TERMINAL_COMMITMENT",
                "WORLD_CONSEQUENCE",
                "SCORE",
            ],
        )
        self.assertEqual(
            pressure._event_types(late),
            [
                "WORLD_CONTRACT_ESTABLISHED",
                "POLICY_ACTION_REQUESTED",
                "WORLD_ACTION_RECEIPT",
                "TERMINAL_COMMITMENT",
                "WORLD_CONSEQUENCE",
                "SCORE",
                "BINDING_DISCLOSED",
            ],
        )

    def test_same_action_has_contract_specific_consequence(self) -> None:
        c0_spec = pressure.compile_schedule()[0]
        c1_spec = pressure.compile_schedule()[8]
        c0 = pressure._run_episode(c0_spec, _adapter(pressure.ACT_A))
        c1 = pressure._run_episode(c1_spec, _adapter(pressure.ACT_A))
        self.assertEqual(c0["requested_action"], c1["requested_action"])
        self.assertEqual(c0["committed_action"], c1["committed_action"])
        self.assertEqual(c0["authoritative_produced_color"], "RED")
        self.assertTrue(c0["success"])
        self.assertEqual(c1["authoritative_produced_color"], "BLUE")
        self.assertFalse(c1["success"])

    def test_freeze_reconstructs_hashes_and_zero_calls(self) -> None:
        freeze = pressure.build_freeze_artifact()
        self.assertEqual(freeze["protocol_sha256"], pressure.protocol_hash())
        self.assertEqual(freeze["schedule_sha256"], pressure.schedule_hash())
        self.assertEqual(
            freeze["action_schema_sha256"], pressure.action_schema_hash()
        )
        self.assertEqual(freeze["new_qualification_model_calls_made"], 0)
        self.assertEqual(freeze["empirical_model_calls_made"], 0)
        self.assertTrue(
            freeze["late_precommitment_input_equivalence"]["hashes_match"]
        )

    def test_validator_detects_late_binding_leak(self) -> None:
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
                "event_type": "BINDING_DISCLOSED",
                "payload": {"binding_rows": pressure.binding_rows(pressure.C0)},
            }
        ]
        calls[late_index]["serialized_policy_visible_request"] = json.dumps(visible)
        validity = pressure.validate_evidence(schedule, episodes, calls)
        self.assertEqual(validity["status"], "EXPERIMENT_INVALID")
        self.assertTrue(
            any("POLICY_VISIBILITY_MISMATCH" in wound for wound in validity["invalidity_wounds"])
        )

    def test_offline_execution_retains_exact_16_stateless_calls(self) -> None:
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
        self.assertEqual(result["empirical_call_count"], 16)
        self.assertEqual(result["empirical_retry_count"], 0)
        self.assertEqual(result["new_qualification_call_count"], 0)
        self.assertEqual(result["P3_empirical_calls"], 0)
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
