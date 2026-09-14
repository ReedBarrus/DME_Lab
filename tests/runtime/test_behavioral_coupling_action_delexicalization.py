from __future__ import annotations

from copy import deepcopy
import json
import unittest
from unittest.mock import MagicMock, patch

from src.runtime import behavioral_coupling_action_delexicalization as pressure
from src.runtime.bounded_consequential_feedback_experiment import (
    CONDITION_F,
    CONDITION_P,
)
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


class BehavioralCouplingActionDelexicalizationTest(unittest.TestCase):
    def test_schedule_is_exact_32_cell_factorial(self) -> None:
        schedule = pressure.compile_schedule()
        self.assertEqual(len(schedule), 32)
        cells = {
            (
                row["mapping"],
                row["mapping_declaration_order"],
                row["action_contract"],
                row["observation_symbol"],
                row["condition"],
            )
            for row in schedule
        }
        self.assertEqual(len(cells), 32)
        self.assertEqual(len({row["episode_id"] for row in schedule}), 32)

    def test_contracts_delexicalize_actions_and_keep_fixed_row_order(self) -> None:
        self.assertEqual(pressure.ACTION_ENUM, ("ACT_A", "ACT_B"))
        self.assertEqual(
            pressure.action_contract_rows(pressure.C1),
            [
                {"action": "ACT_A", "target_color": "RED"},
                {"action": "ACT_B", "target_color": "BLUE"},
            ],
        )
        self.assertEqual(
            pressure.action_contract_rows(pressure.C2),
            [
                {"action": "ACT_A", "target_color": "BLUE"},
                {"action": "ACT_B", "target_color": "RED"},
            ],
        )
        self.assertNotIn("SUBMIT_RED", json.dumps(pressure.build_protocol_declaration()))
        self.assertNotIn("SUBMIT_BLUE", json.dumps(pressure.build_protocol_declaration()))

    def test_world_scoring_uses_action_contract(self) -> None:
        base = next(
            row
            for row in pressure.compile_schedule()
            if row["mapping"] == "M1"
            and row["mapping_declaration_order"] == "AB"
            and row["observation_symbol"] == "BETA"
            and row["condition"] == CONDITION_F
        )
        c1 = deepcopy(base)
        c1.update(
            {
                "action_contract": pressure.C1,
                "action_contract_rows": pressure.action_contract_rows(pressure.C1),
                "serialized_action_contract_text": (
                    pressure.serialized_action_contract_text(pressure.C1)
                ),
                "correct_typed_action": pressure.ACT_B,
            }
        )
        c2 = deepcopy(base)
        c2.update(
            {
                "action_contract": pressure.C2,
                "action_contract_rows": pressure.action_contract_rows(pressure.C2),
                "serialized_action_contract_text": (
                    pressure.serialized_action_contract_text(pressure.C2)
                ),
                "correct_typed_action": pressure.ACT_A,
            }
        )
        c1_episode = pressure._run_episode(c1, _adapter(pressure.ACT_A))
        c2_episode = pressure._run_episode(c2, _adapter(pressure.ACT_A))
        self.assertEqual(c1_episode["action_implied_target_color"], "RED")
        self.assertFalse(c1_episode["correct"])
        self.assertEqual(c2_episode["action_implied_target_color"], "BLUE")
        self.assertTrue(c2_episode["correct"])

    def test_f_and_p_visibility_preserve_mapping_and_contract_only(self) -> None:
        schedule = pressure.compile_schedule()
        f_spec = schedule[0]
        p_spec = schedule[1]
        f_adapter = _adapter()
        p_adapter = _adapter()
        pressure._run_episode(f_spec, f_adapter)
        pressure._run_episode(p_spec, p_adapter)
        f_visible = json.loads(
            f_adapter.call_records[0]["serialized_policy_visible_request"]
        )
        p_visible = json.loads(
            p_adapter.call_records[0]["serialized_policy_visible_request"]
        )
        self.assertEqual(
            f_visible["policy_visible_protocol_history"][-1]["payload"],
            {"symbol": "ALPHA"},
        )
        self.assertEqual(len(p_visible["policy_visible_protocol_history"]), 1)
        for visible in (f_visible, p_visible):
            self.assertEqual(visible["legal_action_vocabulary"], ["ACT_A", "ACT_B"])
            self.assertIn("ALPHA -> RED; BETA -> BLUE", visible["fixed_task"])
            self.assertIn("ACT_A -> RED; ACT_B -> BLUE", visible["fixed_task"])
            for forbidden in (
                "hidden_target_color",
                "schedule_position",
                "prior_episode",
                '"condition"',
            ):
                self.assertNotIn(forbidden, json.dumps(visible))

    def test_qualification_is_exactly_two_non_scientific_stateless_calls(self) -> None:
        freeze = pressure.build_freeze_artifact()
        actions = iter(pressure.ACTION_ENUM)
        retained = {}

        def write(path, value):
            retained[str(path)] = deepcopy(value)

        qualification_path = MagicMock()
        qualification_path.exists.return_value = False
        with (
            patch.object(pressure, "load_validated_freeze", return_value=freeze),
            patch.object(pressure, "_new_adapter", side_effect=lambda: _adapter(next(actions))),
            patch.object(pressure, "_write_new_json", side_effect=write),
            patch.object(pressure, "QUALIFICATION_PATH", qualification_path),
            patch.object(pressure, "EMPIRICAL_PATHS", ()),
        ):
            artifact = pressure.qualify_once("basis-commit")

        self.assertEqual(artifact["result"]["status"], "PASS")
        self.assertEqual(len(artifact["calls"]), 2)
        self.assertEqual(artifact["scientific_schedule_entries_consumed"], 0)
        for token, call in zip(pressure.ACTION_ENUM, artifact["calls"]):
            visible = json.loads(call["serialized_policy_visible_request"])
            self.assertEqual(visible["fixed_task"], f"Select {token}.")
            self.assertEqual(visible["policy_visible_protocol_history"], [])
            self.assertNotIn("RED", call["serialized_policy_visible_request"])
            self.assertNotIn("BLUE", call["serialized_policy_visible_request"])

    def test_freeze_reconstructs_hashes_and_zero_calls(self) -> None:
        freeze = pressure.build_freeze_artifact()
        self.assertEqual(freeze["protocol_sha256"], pressure.protocol_hash())
        self.assertEqual(freeze["schedule_sha256"], pressure.schedule_hash())
        self.assertEqual(freeze["action_schema_sha256"], pressure.action_schema_hash())
        self.assertEqual(freeze["qualification_model_calls_made"], 0)
        self.assertEqual(freeze["empirical_model_calls_made"], 0)
        self.assertEqual(freeze["P3_status"], "BLOCKED_NOT_EXECUTED")

    def test_offline_execution_retains_32_stateless_calls_and_all_summaries(self) -> None:
        freeze = pressure.build_freeze_artifact()
        qualification = {
            "result": {
                "status": "PASS",
                "wounds": [],
                "calls_retained": 2,
                "scientific_schedule_entries_consumed": 0,
            }
        }
        retained = {}
        actions = iter(
            pressure.ACT_A if index % 2 == 0 else pressure.ACT_B
            for index in range(32)
        )

        def write(path, value):
            retained[str(path)] = deepcopy(value)

        with (
            patch.object(pressure, "load_validated_freeze", return_value=freeze),
            patch.object(
                pressure,
                "load_validated_qualification",
                return_value=qualification,
            ),
            patch.object(pressure, "_new_adapter", side_effect=lambda: _adapter(next(actions))),
            patch.object(pressure, "_write_new_json", side_effect=write),
            patch.object(pressure, "EMPIRICAL_PATHS", ()),
        ):
            result = pressure.execute_once("basis-commit")

        self.assertEqual(result["empirical_episode_count"], 32)
        self.assertEqual(result["empirical_call_count"], 32)
        self.assertEqual(result["empirical_retry_count"], 0)
        self.assertEqual(result["P3_empirical_calls"], 0)
        self.assertEqual(result["validity"]["status"], "VALID")
        calls = retained[str(pressure.CALLS_PATH)]["calls"]
        self.assertEqual(len(calls), 32)
        for call in calls:
            request = json.loads(call["serialized_http_request"])
            self.assertEqual(len(request["messages"]), 1)
            self.assertNotIn("previous_response_id", request)
            self.assertNotIn("tools", request)
            self.assertEqual(
                request["response_format"],
                structured_action_response_format(pressure.ACTION_ENUM),
            )
        summary = result["descriptive_summary"]
        self.assertIn("individual_cells", summary)
        self.assertIn(
            "by_first_mapping_row_target_color_action_contract_condition", summary
        )
        self.assertIn("by_world_target_color_action_contract_condition", summary)
        self.assertIn("by_typed_action_identity_condition", summary)
        self.assertIn(
            "by_mapping_presentation_action_contract_condition", summary
        )


if __name__ == "__main__":
    unittest.main()
