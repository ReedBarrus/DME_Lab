from __future__ import annotations

from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from src.runtime import behavioral_coupling_mapping_row_order as pressure
from src.runtime.behavioral_coupling_characterization import (
    ACTION_ENUM_RB,
    P2_MAPPINGS,
    P2_TASKS,
)
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


def _adapter(action: str = "SUBMIT_RED") -> LMStudioConstrainedActionPolicyAdapter:
    return LMStudioConstrainedActionPolicyAdapter(
        pressure._config(),
        action_enum=ACTION_ENUM_RB,
        transport=_transport_for(action),
    )


class BehavioralCouplingMappingRowOrderTest(unittest.TestCase):
    def test_schedule_is_exact_minimum_factorial(self) -> None:
        schedule = pressure.compile_schedule()
        self.assertEqual(len(schedule), 16)
        cells = {
            (
                row["mapping"],
                row["declaration_order"],
                row["observation_symbol"],
                row["condition"],
            )
            for row in schedule
        }
        self.assertEqual(len(cells), 16)
        self.assertEqual(len({row["episode_id"] for row in schedule}), 16)

    def test_order_changes_rows_not_semantic_mapping(self) -> None:
        for mapping in pressure.MAPPINGS:
            ab = pressure.mapping_rows(mapping, pressure.AB)
            ba = pressure.mapping_rows(mapping, pressure.BA)
            self.assertEqual([row["symbol"] for row in ab], ["ALPHA", "BETA"])
            self.assertEqual([row["symbol"] for row in ba], ["BETA", "ALPHA"])
            self.assertEqual(
                {row["symbol"]: row["color"] for row in ab},
                P2_MAPPINGS[mapping],
            )
            self.assertEqual(
                {row["symbol"]: row["color"] for row in ba},
                P2_MAPPINGS[mapping],
            )
            self.assertEqual(pressure.fixed_task(mapping, pressure.AB), P2_TASKS[mapping])

    def test_f_and_p_visibility_preserve_boundary_and_row_order(self) -> None:
        schedule = pressure.compile_schedule()
        for order in pressure.DECLARATION_ORDERS:
            f_spec = next(
                row
                for row in schedule
                if row["mapping"] == "M1"
                and row["declaration_order"] == order
                and row["observation_symbol"] == "ALPHA"
                and row["condition"] == CONDITION_F
            )
            p_spec = next(
                row
                for row in schedule
                if row["mapping"] == "M1"
                and row["declaration_order"] == order
                and row["observation_symbol"] == "ALPHA"
                and row["condition"] == CONDITION_P
            )
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
            self.assertEqual(
                f_visible["fixed_task"], pressure.fixed_task("M1", order)
            )
            self.assertEqual(
                p_visible["fixed_task"], pressure.fixed_task("M1", order)
            )
            serialized = f_adapter.call_records[0]["serialized_policy_visible_request"]
            for forbidden in (
                "schedule_position",
                "hidden_target_color",
                '"condition"',
                "prior_episode",
            ):
                self.assertNotIn(forbidden, serialized)

    def test_freeze_reconstructs_exact_protocol_and_schedule(self) -> None:
        freeze = pressure.build_freeze_artifact()
        self.assertEqual(freeze["protocol_sha256"], pressure.protocol_hash())
        self.assertEqual(freeze["schedule_sha256"], pressure.schedule_hash())
        self.assertEqual(len(freeze["schedule"]), 16)
        self.assertEqual(freeze["empirical_model_calls_made"], 0)
        self.assertEqual(freeze["P3_status"], "BLOCKED_NOT_EXECUTED")

    def test_evidence_validator_rejects_wrong_serialized_order(self) -> None:
        schedule = pressure.compile_schedule()
        episodes = []
        calls = []
        for row in schedule:
            local = _adapter()
            result = pressure._run_episode(row, local)
            episodes.append(result)
            calls.append({"episode_id": row["episode_id"], **local.call_records[0]})
        visible = json.loads(calls[0]["serialized_policy_visible_request"])
        visible["fixed_task"] = pressure.fixed_task("M1", pressure.BA)
        calls[0]["serialized_policy_visible_request"] = json.dumps(visible)
        wounded = pressure.validate_evidence(schedule, episodes, calls)
        self.assertIn(
            f"{schedule[0]['episode_id']}:POLICY_VISIBILITY_MISMATCH",
            wounded["invalidity_wounds"],
        )

    def test_offline_execution_retains_exact_16_stateless_calls(self) -> None:
        freeze = pressure.build_freeze_artifact()
        retained = {}

        def write(path, value):
            retained[str(path)] = deepcopy(value)

        actions = iter(
            "SUBMIT_RED" if index % 2 == 0 else "SUBMIT_BLUE"
            for index in range(16)
        )

        def new_adapter():
            return _adapter(next(actions))

        with (
            patch.object(pressure, "load_validated_freeze", return_value=freeze),
            patch.object(pressure, "_new_adapter", side_effect=new_adapter),
            patch.object(pressure, "_write_new_json", side_effect=write),
            patch.object(pressure, "OUTPUT_PATHS", ()),
        ):
            result = pressure.execute_once("basis-commit")

        self.assertEqual(result["empirical_episode_count"], 16)
        self.assertEqual(result["empirical_call_count"], 16)
        self.assertEqual(result["empirical_retry_count"], 0)
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
                structured_action_response_format(ACTION_ENUM_RB),
            )


if __name__ == "__main__":
    unittest.main()
