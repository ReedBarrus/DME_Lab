from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import src.runtime.behavioral_coupling_characterization as battery

from src.runtime.behavioral_coupling_characterization import (
    ACTION_ENUM_RB,
    ACTION_ENUM_RBD,
    ALPHA,
    ASSOCIATED,
    BETA,
    BR,
    DEFER,
    FIRST,
    M1,
    M2,
    MODEL_IDENTIFIER,
    P2_MAPPINGS,
    RB,
    SECOND,
    UNASSOCIATED,
    _p4_evidence,
    _run_p2_episode,
    _run_p3_episode,
    _run_p4_episode,
    _validate_pressure,
    battery_protocol_hash,
    build_freeze,
    compile_p1_schedule,
    compile_p2_schedule,
    compile_p3_schedule,
    compile_p4_schedule,
    schedule_hashes,
)
from src.runtime.bounded_consequential_feedback_experiment import (
    BLUE,
    CONDITION_F,
    CONDITION_P,
    RED,
    SUBMIT_BLUE,
    SUBMIT_RED,
)
from src.runtime.lm_studio_policy_adapter import (
    DEFAULT_ENDPOINT,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    structured_action_response_format,
    structured_action_schema_hash,
)


class FakeTransport:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)

    def __call__(
        self,
        endpoint: str,
        body: bytes,
        headers: dict[str, str],
        timeout: float,
    ) -> tuple[int, str]:
        del endpoint, body, headers, timeout
        content = self.responses.pop(0)
        return 200, json.dumps(
            {"choices": [{"message": {"content": content}}]}
        )


class DeterministicAdapter:
    """Offline typed-action stand-in for exercising all frozen driver paths."""

    def __init__(
        self,
        config: LMStudioEndpointConfig,
        *,
        action_enum: tuple[str, ...],
        visible_action_vocabulary: tuple[str, ...] | None = None,
    ) -> None:
        del config
        self.action_enum = action_enum
        self.visible = visible_action_vocabulary or action_enum
        self.records: list[dict[str, object]] = []

    @property
    def call_records(self) -> tuple[dict[str, object], ...]:
        return tuple(self.records)

    def __call__(self, task: str, history: tuple[dict[str, object], ...]) -> str:
        action = SUBMIT_RED
        for event in history:
            payload = event["payload"]
            if "feedback" in payload:
                action = f"SUBMIT_{payload['feedback']}"
            if "symbol" in payload:
                symbol = payload["symbol"]
                if symbol == ALPHA:
                    action = SUBMIT_RED if "ALPHA -> RED" in task else SUBMIT_BLUE
                else:
                    action = SUBMIT_BLUE if "BETA -> BLUE" in task else SUBMIT_RED
            for item in payload.get("evidence", []):
                if item.get("role") == "CURRENT":
                    action = f"SUBMIT_{item['value']}"
        if DEFER in self.action_enum and not any(
            "feedback" in event["payload"] for event in history
        ):
            action = DEFER
        schema = structured_action_response_format(self.action_enum)
        visible = {
            "fixed_task": task,
            "policy_visible_protocol_history": list(history),
            "legal_action_vocabulary": list(self.visible),
        }
        serialized_visible = json.dumps(
            visible, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
        body = {
            "messages": [{"role": "user", "content": serialized_visible}],
            "model": battery.MODEL_IDENTIFIER,
            **battery.SAMPLING_SETTINGS,
            "response_format": schema,
            "stream": False,
        }
        self.records.append(
            {
                "serialized_policy_visible_request": serialized_visible,
                "serialized_http_request": json.dumps(
                    body, ensure_ascii=False, separators=(",", ":"), sort_keys=True
                ),
                "actuation_constraint": schema,
                "action_schema_hash": structured_action_schema_hash(self.action_enum),
                "conversation_state_supplied": False,
                "tools_supplied": False,
                "selected_action": action,
                "structured_output": {"action": action},
                "raw_model_response": json.dumps({"action": action}),
            }
        )
        return action


def adapter(action_enum: tuple[str, ...], responses: list[str]) -> LMStudioConstrainedActionPolicyAdapter:
    return LMStudioConstrainedActionPolicyAdapter(
        LMStudioEndpointConfig(
            endpoint=DEFAULT_ENDPOINT,
            model_identifier=MODEL_IDENTIFIER,
            sampling_settings={"temperature": 0.0, "top_p": 1.0, "max_tokens": 16},
        ),
        action_enum=action_enum,
        transport=FakeTransport(responses),
    )


class BehavioralCouplingCharacterizationTest(unittest.TestCase):
    def test_schedule_commitments_are_exact_and_independent(self) -> None:
        self.assertEqual(
            schedule_hashes(),
            {
                "P1": "sha256:6c442c4d81ed10024a1115b1ab9a8119d9690aa1683ec6de81011d460395b98f",
                "P2": "sha256:3514df11e5a119ac36b8a787f5abd8a0d03d2ab1d270fab0c0ba29d9bc62fc3f",
                "P3": "sha256:049938ca737f44f2455c7de3dd89cccb5358104eb1acd50ff6688fe07786cdc5",
                "P4": "sha256:f4168239b66f9cbed3e6553a71b9a6cdb49cb2cebb76f7e5d4637d8af0bb976c",
            },
        )
        self.assertEqual(
            battery_protocol_hash(),
            "sha256:fc4c1d8a32f1dd9c844bcaa12b4edb3057ae72d716be517a38c9d15ab5524b68",
        )

    def test_p1_is_32_episodes_over_both_orders_and_paired_conditions(self) -> None:
        schedule = compile_p1_schedule()
        self.assertEqual(len(schedule), 32)
        self.assertEqual(
            {(row["schema_order"], row["condition"]) for row in schedule},
            {(RB, CONDITION_F), (RB, CONDITION_P), (BR, CONDITION_F), (BR, CONDITION_P)},
        )
        for index in range(0, len(schedule), 2):
            first, second = schedule[index : index + 2]
            self.assertEqual(first["slot"], second["slot"])
            self.assertEqual(first["hidden_color"], second["hidden_color"])
            self.assertEqual((first["condition"], second["condition"]), (CONDITION_F, CONDITION_P))

    def test_p2_covers_each_mapping_target_combination_twice(self) -> None:
        schedule = compile_p2_schedule()
        self.assertEqual(len(schedule), 16)
        slots = [row for row in schedule if row["condition"] == CONDITION_F]
        for mapping in (M1, M2):
            for hidden in (RED, BLUE):
                self.assertEqual(
                    sum(row["mapping"] == mapping and row["hidden_target_color"] == hidden for row in slots),
                    2,
                )
        for row in slots:
            self.assertEqual(P2_MAPPINGS[row["mapping"]][row["observation_symbol"]], row["hidden_target_color"])

    def test_p3_reuses_the_balanced_paired_hidden_slots(self) -> None:
        schedule = compile_p3_schedule()
        self.assertEqual(len(schedule), 16)
        self.assertEqual(sum(row["hidden_color"] == RED for row in schedule), 8)
        self.assertEqual(sum(row["hidden_color"] == BLUE for row in schedule), 8)
        self.assertEqual(sum(row["condition"] == CONDITION_F for row in schedule), 8)
        self.assertEqual(sum(row["condition"] == CONDITION_P for row in schedule), 8)

    def test_p4_balance_and_value_order_are_paired_without_position_signal(self) -> None:
        schedule = compile_p4_schedule()
        self.assertEqual(len(schedule), 16)
        associated = [row for row in schedule if row["regime"] == ASSOCIATED]
        self.assertEqual(sum(row["current_color"] == RED for row in associated), 4)
        self.assertEqual(sum(row["current_color"] == BLUE for row in associated), 4)
        self.assertEqual(sum(row["current_position"] == FIRST for row in associated), 4)
        self.assertEqual(sum(row["current_position"] == SECOND for row in associated), 4)
        for index in range(0, len(schedule), 2):
            a, u = schedule[index : index + 2]
            self.assertEqual((a["regime"], u["regime"]), (ASSOCIATED, UNASSOCIATED))
            self.assertEqual(
                [item["value"] for item in _p4_evidence(a, associated=True)],
                [item["value"] for item in _p4_evidence(u, associated=False)],
            )

    def test_p2_visibility_separates_mapping_target_and_symbol(self) -> None:
        f_spec, p_spec = compile_p2_schedule()[:2]
        f_adapter = adapter(ACTION_ENUM_RB, ['{"action":"SUBMIT_RED"}'])
        p_adapter = adapter(ACTION_ENUM_RB, ['{"action":"SUBMIT_BLUE"}'])
        f_episode = _run_p2_episode(f_spec, f_adapter)
        p_episode = _run_p2_episode(p_spec, p_adapter)
        f_visible = json.loads(f_adapter.call_records[0]["serialized_policy_visible_request"])
        p_visible = json.loads(p_adapter.call_records[0]["serialized_policy_visible_request"])

        self.assertEqual(f_spec["observation_symbol"], ALPHA)
        self.assertIn("ALPHA -> RED", f_visible["fixed_task"])
        self.assertEqual(f_visible["policy_visible_protocol_history"][-1]["payload"], {"symbol": ALPHA})
        self.assertEqual(len(p_visible["policy_visible_protocol_history"]), 1)
        self.assertNotIn(RED, json.dumps(p_visible["policy_visible_protocol_history"]))
        self.assertEqual(f_episode["hidden_target_color"], RED)
        self.assertNotEqual(p_episode["accepted_terminal_action"], f_episode["accepted_terminal_action"])

    def test_p3_defer_is_terminal_and_scored_only_under_P(self) -> None:
        f_spec, p_spec = compile_p3_schedule()[:2]
        typed = adapter(
            ACTION_ENUM_RBD,
            ['{"action":"SUBMIT_RED"}', '{"action":"DEFER"}'],
        )
        f_episode = _run_p3_episode(f_spec, typed)
        p_episode = _run_p3_episode(p_spec, typed)

        self.assertEqual(f_episode["accepted_terminal_action"], SUBMIT_RED)
        self.assertTrue(f_episode["correct"])
        self.assertEqual(p_episode["accepted_terminal_action"], DEFER)
        self.assertTrue(p_episode["correct"])

    def test_p4_removes_only_role_fields_from_paired_visible_evidence(self) -> None:
        a_spec, u_spec = compile_p4_schedule()[:2]
        a_adapter = adapter(ACTION_ENUM_RB, ['{"action":"SUBMIT_RED"}'])
        u_adapter = adapter(ACTION_ENUM_RB, ['{"action":"SUBMIT_BLUE"}'])
        a_episode = _run_p4_episode(a_spec, a_adapter)
        u_episode = _run_p4_episode(u_spec, u_adapter)

        self.assertEqual(
            [item["value"] for item in a_episode["delivered_evidence"]],
            [item["value"] for item in u_episode["delivered_evidence"]],
        )
        self.assertTrue(all(set(item) == {"role", "value"} for item in a_episode["delivered_evidence"]))
        self.assertTrue(all(set(item) == {"value"} for item in u_episode["delivered_evidence"]))

    def test_freeze_contains_all_schedules_and_zero_empirical_calls(self) -> None:
        freeze = build_freeze("adapter-commit")
        self.assertEqual(freeze["schedule_commitments"], schedule_hashes())
        self.assertEqual(freeze["empirical_model_calls_made"], 0)
        self.assertEqual(freeze["adapter_repository_commit"], "adapter-commit")
        self.assertEqual(sum(len(rows) for rows in freeze["schedules"].values()), 80)

    def test_visibility_wound_marks_pressure_invalid_but_wrong_action_does_not(self) -> None:
        schedule = [compile_p3_schedule()[0]]
        typed = adapter(ACTION_ENUM_RBD, ['{"action":"SUBMIT_BLUE"}'])
        episode = _run_p3_episode(schedule[0], typed)
        call = {"episode_id": schedule[0]["episode_id"], **typed.call_records[0]}
        validity = _validate_pressure("P3", schedule, [episode], [call])
        self.assertEqual(validity["status"], "VALID")
        wounded = dict(call)
        visible = json.loads(wounded["serialized_policy_visible_request"])
        visible["condition"] = CONDITION_F
        wounded["serialized_policy_visible_request"] = json.dumps(visible)
        invalid = _validate_pressure("P3", schedule, [episode], [wounded])
        self.assertEqual(invalid["status"], "EXPERIMENT_INVALID")

    def test_all_four_pressure_drivers_close_validly_offline(self) -> None:
        with patch.object(
            battery,
            "LMStudioConstrainedActionPolicyAdapter",
            DeterministicAdapter,
        ):
            p1 = battery._run_p1("adapter-commit")
            p2 = battery._run_custom_pressure(
                "P2",
                battery.compile_p2_schedule(),
                battery.ACTION_ENUM_RB,
                battery._run_p2_episode,
                battery._summarize_p2,
                battery.P2_SCORING,
                "adapter-commit",
            )
            p3 = battery._run_custom_pressure(
                "P3",
                battery.compile_p3_schedule(),
                battery.ACTION_ENUM_RBD,
                battery._run_p3_episode,
                battery._summarize_p3,
                battery.P3_SCORING,
                "adapter-commit",
            )
            p4 = battery._run_custom_pressure(
                "P4",
                battery.compile_p4_schedule(),
                battery.ACTION_ENUM_RB,
                battery._run_p4_episode,
                battery._summarize_p4,
                battery.P4_SCORING,
                "adapter-commit",
            )

        for world, calls in (p1, p2, p3, p4):
            self.assertEqual(world["validity"]["status"], "VALID")
            self.assertEqual(calls["validity"]["status"], "VALID")
            self.assertEqual(len(world["episodes"]), len(calls["calls"]))

    def test_continuation_basis_preserves_qualified_subset_and_blocked_p3(self) -> None:
        import src.runtime.behavioral_coupling_characterization_continuation as continuation

        basis = continuation.validate_continuation_basis()
        self.assertEqual(basis["eligible_pressures"], ["P1", "P2", "P4"])
        self.assertEqual(basis["blocked_pressure"], "P3")
        self.assertEqual(
            {key: len(value) for key, value in basis["freeze"]["schedules"].items()},
            {"P1": 32, "P2": 16, "P3": 16, "P4": 16},
        )
        self.assertTrue(basis["qualification"]["BR_passed"])
        self.assertFalse(basis["qualification"]["RBD_passed"])

    def test_continuation_executes_exact_64_episode_subset_offline(self) -> None:
        import src.runtime.behavioral_coupling_characterization_continuation as continuation

        written: dict[str, dict[str, object]] = {}

        def retain(path: object, value: dict[str, object]) -> None:
            written[str(path)] = value

        with (
            patch.object(
                battery,
                "LMStudioConstrainedActionPolicyAdapter",
                DeterministicAdapter,
            ),
            patch.object(continuation, "_write_new_json", side_effect=retain),
        ):
            result = continuation.execute_qualified_subset_once(
                "continuation-commit"
            )

        self.assertEqual(result["completed_pressures"], ["P1", "P2", "P4"])
        self.assertEqual(result["empirical_episode_count"], 64)
        self.assertEqual(result["empirical_call_count"], 64)
        self.assertEqual(result["retry_calls"], 0)
        self.assertEqual(result["new_qualification_calls"], 0)
        self.assertEqual(result["P3"]["status"], "BLOCKED_NOT_EXECUTED")
        self.assertEqual(result["P3"]["empirical_calls"], 0)
        self.assertEqual(len(written), 8)


if __name__ == "__main__":
    unittest.main()
