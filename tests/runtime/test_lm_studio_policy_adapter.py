from __future__ import annotations

import json
import hashlib
import unittest

from src.runtime.bounded_consequential_feedback_experiment import (
    BLUE,
    CONDITION_F,
    CONDITION_P,
    FIXED_TASK,
    RED,
    SUBMIT_BLUE,
    SUBMIT_RED,
    BoundedColorWorld,
    run_episode,
)
from src.runtime.lm_studio_policy_adapter import (
    CONSTRAINED_TYPED_ACTION,
    DEFAULT_ENDPOINT,
    STRUCTURED_ACTION_SCHEMA_HASH,
    LMStudioActuationError,
    LMStudioConstrainedActionPolicyAdapter,
    LMStudioEndpointConfig,
    LMStudioPolicyAdapter,
    parse_structured_action,
    structured_action_response_format,
)


SAMPLING = {"temperature": 0.0, "top_p": 1.0, "max_tokens": 16}


def config(*, api_token: str | None = None) -> LMStudioEndpointConfig:
    return LMStudioEndpointConfig(
        endpoint=DEFAULT_ENDPOINT,
        model_identifier="test/local-model",
        sampling_settings=SAMPLING,
        timeout_seconds=10.0,
        api_token=api_token,
    )


def visible_history(hidden_color: str, condition: str) -> tuple[dict, ...]:
    world = BoundedColorWorld(hidden_color, condition)
    world.inspect()
    return world.prepare_policy_call()


class FakeTransport:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def __call__(
        self,
        endpoint: str,
        body: bytes,
        headers: dict[str, str],
        timeout_seconds: float,
    ) -> tuple[int, str]:
        self.calls.append(
            {
                "endpoint": endpoint,
                "body": body.decode("utf-8"),
                "headers": dict(headers),
                "timeout_seconds": timeout_seconds,
            }
        )
        content = self.responses.pop(0)
        return 200, json.dumps(
            {"choices": [{"message": {"role": "assistant", "content": content}}]}
        )


class LMStudioPolicyAdapterTest(unittest.TestCase):
    def test_serialized_F_request_contains_delivered_feedback(self) -> None:
        adapter = LMStudioPolicyAdapter(config(), transport=FakeTransport([SUBMIT_RED]))
        serialized = adapter.serialize_policy_visible_request(
            FIXED_TASK,
            visible_history(RED, CONDITION_F),
        )
        request = json.loads(serialized)

        self.assertEqual(request["fixed_task"], FIXED_TASK)
        self.assertEqual(request["legal_action_vocabulary"], [SUBMIT_RED, SUBMIT_BLUE])
        self.assertEqual(
            request["policy_visible_protocol_history"][-1],
            {"event_type": "FEEDBACK_DELIVERED", "payload": {"feedback": RED}},
        )

    def test_serialized_P_request_has_no_hidden_color_or_withheld_feedback(self) -> None:
        adapter = LMStudioPolicyAdapter(config(), transport=FakeTransport([SUBMIT_RED]))
        serialized = adapter.serialize_policy_visible_request(
            FIXED_TASK,
            visible_history(BLUE, CONDITION_P),
        )
        request = json.loads(serialized)

        self.assertEqual(
            request["policy_visible_protocol_history"],
            [{"event_type": "INSPECT_EXECUTED", "payload": {"action": "INSPECT"}}],
        )
        serialized_history = json.dumps(
            request["policy_visible_protocol_history"], sort_keys=True
        )
        for forbidden in (RED, BLUE, "FEEDBACK_WITHHELD", "FEEDBACK_PRODUCED"):
            self.assertNotIn(forbidden, serialized_history)

    def test_no_schedule_or_condition_metadata_is_serialized(self) -> None:
        adapter = LMStudioPolicyAdapter(config(), transport=FakeTransport([SUBMIT_RED]))
        serialized = adapter.serialize_policy_visible_request(
            FIXED_TASK,
            visible_history(RED, CONDITION_F),
        )
        request = json.loads(serialized)

        self.assertEqual(
            set(request),
            {
                "fixed_task",
                "policy_visible_protocol_history",
                "legal_action_vocabulary",
            },
        )
        for forbidden in (
            "condition",
            "episode",
            "future",
            "schedule",
            "slot",
            "correct",
            "trace",
            "repository",
        ):
            self.assertNotIn(forbidden, serialized.lower())

    def test_each_episode_uses_one_fresh_message_without_conversation_history(self) -> None:
        transport = FakeTransport(["FIRST_ONLY_RESPONSE", "SECOND_ONLY_RESPONSE"])
        adapter = LMStudioPolicyAdapter(config(), transport=transport)

        first = adapter(FIXED_TASK, visible_history(RED, CONDITION_F))
        second = adapter(FIXED_TASK, visible_history(BLUE, CONDITION_F))

        self.assertEqual((first, second), ("FIRST_ONLY_RESPONSE", "SECOND_ONLY_RESPONSE"))
        self.assertEqual(len(transport.calls), 2)
        first_body, second_body = [json.loads(call["body"]) for call in transport.calls]
        self.assertEqual(len(first_body["messages"]), 1)
        self.assertEqual(len(second_body["messages"]), 1)
        self.assertEqual(first_body["messages"][0]["role"], "user")
        self.assertEqual(second_body["messages"][0]["role"], "user")
        self.assertNotIn("FIRST_ONLY_RESPONSE", second_body["messages"][0]["content"])
        self.assertNotIn("previous_response_id", second_body)
        self.assertEqual(len(adapter.call_records), 2)
        self.assertTrue(
            all(not record["conversation_state_supplied"] for record in adapter.call_records)
        )

    def test_request_has_no_tool_mcp_or_integration_surface(self) -> None:
        transport = FakeTransport([SUBMIT_RED])
        adapter = LMStudioPolicyAdapter(config(), transport=transport)
        adapter(FIXED_TASK, visible_history(RED, CONDITION_F))
        body = json.loads(transport.calls[0]["body"])

        self.assertEqual(
            set(body), {"messages", "model", "temperature", "top_p", "max_tokens", "stream"}
        )
        self.assertFalse(body["stream"])
        for forbidden in ("tools", "tool_choice", "integrations", "mcp"):
            self.assertNotIn(forbidden, body)

    def test_call_record_contains_required_nonsecret_evidence(self) -> None:
        transport = FakeTransport([SUBMIT_RED])
        adapter = LMStudioPolicyAdapter(
            config(api_token="not-recorded-secret"),
            transport=transport,
        )
        requested = adapter(FIXED_TASK, visible_history(RED, CONDITION_F))
        record = adapter.call_records[0]

        self.assertEqual(requested, SUBMIT_RED)
        self.assertEqual(record["model_identifier"], "test/local-model")
        self.assertEqual(record["provider_exposed_sampling_settings"], SAMPLING)
        self.assertEqual(record["raw_model_response"], SUBMIT_RED)
        self.assertEqual(record["parsed_requested_action"], SUBMIT_RED)
        self.assertIn("serialized_policy_visible_request", record)
        self.assertIn("serialized_http_request", record)
        self.assertTrue(record["endpoint_configuration"]["authentication_configured"])
        self.assertNotIn("not-recorded-secret", json.dumps(record))
        self.assertEqual(
            transport.calls[0]["headers"]["Authorization"],
            "Bearer not-recorded-secret",
        )

    def test_strict_action_handling_does_not_repair_prose_or_whitespace(self) -> None:
        for raw in (" SUBMIT_RED", "SUBMIT_BLUE\n", "The answer is RED", "RED"):
            adapter = LMStudioPolicyAdapter(config(), transport=FakeTransport([raw]))
            requested = adapter(FIXED_TASK, visible_history(RED, CONDITION_F))
            record = adapter.call_records[0]
            self.assertEqual(requested, raw)
            self.assertIsNone(record["parsed_requested_action"])

    def test_non_loopback_and_non_chat_endpoints_are_rejected(self) -> None:
        for endpoint in (
            "https://127.0.0.1:1234/v1/chat/completions",
            "http://localhost:1234/v1/chat/completions",
            "http://192.168.1.4:1234/v1/chat/completions",
            "http://127.0.0.1:1234/api/v1/chat",
            "http://user:secret@127.0.0.1:1234/v1/chat/completions",
        ):
            with self.assertRaises(ValueError):
                LMStudioEndpointConfig(
                    endpoint=endpoint,
                    model_identifier="test/local-model",
                    sampling_settings=SAMPLING,
                )

    def test_sampling_settings_cannot_inject_messages_tools_or_state(self) -> None:
        for forbidden in ("messages", "tools", "integrations", "previous_response_id"):
            with self.assertRaises(ValueError):
                LMStudioEndpointConfig(
                    endpoint=DEFAULT_ENDPOINT,
                    model_identifier="test/local-model",
                    sampling_settings={forbidden: []},
                )


class LMStudioConstrainedActionPolicyAdapterTest(unittest.TestCase):
    def test_response_format_is_exactly_the_frozen_action_schema(self) -> None:
        expected = {
            "type": "json_schema",
            "json_schema": {
                "name": "bounded_terminal_action",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": [SUBMIT_RED, SUBMIT_BLUE],
                        }
                    },
                    "required": ["action"],
                    "additionalProperties": False,
                },
            },
        }
        response_format = structured_action_response_format()
        canonical = json.dumps(
            response_format,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        self.assertEqual(response_format, expected)
        self.assertEqual(
            STRUCTURED_ACTION_SCHEMA_HASH,
            "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def test_sampling_settings_cannot_override_response_format(self) -> None:
        with self.assertRaises(ValueError):
            LMStudioEndpointConfig(
                endpoint=DEFAULT_ENDPOINT,
                model_identifier="test/local-model",
                sampling_settings={"response_format": {}},
            )

    def test_typed_request_adds_only_fixed_response_format(self) -> None:
        transport = FakeTransport(['{"action":"SUBMIT_RED"}'])
        adapter = LMStudioConstrainedActionPolicyAdapter(
            config(), transport=transport
        )
        adapter(FIXED_TASK, visible_history(RED, CONDITION_F))
        body = json.loads(transport.calls[0]["body"])

        self.assertEqual(body["response_format"], structured_action_response_format())
        self.assertEqual(
            json.loads(body["messages"][0]["content"]),
            {
                "fixed_task": FIXED_TASK,
                "policy_visible_protocol_history": [
                    {"event_type": "INSPECT_EXECUTED", "payload": {"action": "INSPECT"}},
                    {
                        "event_type": "FEEDBACK_DELIVERED",
                        "payload": {"feedback": RED},
                    },
                ],
                "legal_action_vocabulary": [SUBMIT_RED, SUBMIT_BLUE],
            },
        )
        self.assertEqual(adapter.call_records[0]["actuation_realization"], CONSTRAINED_TYPED_ACTION)

    def test_typed_P_input_remains_hidden_and_schedule_free(self) -> None:
        transport = FakeTransport(['{"action":"SUBMIT_RED"}'])
        adapter = LMStudioConstrainedActionPolicyAdapter(
            config(), transport=transport
        )
        adapter(FIXED_TASK, visible_history(BLUE, CONDITION_P))
        body = json.loads(transport.calls[0]["body"])
        visible = json.loads(body["messages"][0]["content"])

        self.assertEqual(
            visible["policy_visible_protocol_history"],
            [{"event_type": "INSPECT_EXECUTED", "payload": {"action": "INSPECT"}}],
        )
        serialized_history = json.dumps(visible["policy_visible_protocol_history"])
        for forbidden in (RED, BLUE, "FEEDBACK_WITHHELD", "condition", "schedule", "slot"):
            self.assertNotIn(forbidden, serialized_history)
        self.assertEqual(len(body["messages"]), 1)
        self.assertNotIn("tools", body)
        self.assertNotIn("integrations", body)

    def test_valid_structures_extract_each_exact_action(self) -> None:
        for action in (SUBMIT_RED, SUBMIT_BLUE):
            structured, selected = parse_structured_action(
                json.dumps({"action": action})
            )
            self.assertEqual(structured, {"action": action})
            self.assertEqual(selected, action)

    def test_malformed_duplicate_and_prose_outputs_are_rejected(self) -> None:
        malformed = (
            "not json",
            '{"action":"SUBMIT_RED"',
            '```json\n{"action":"SUBMIT_RED"}\n```',
            '{"action":"SUBMIT_RED","action":"SUBMIT_BLUE"}',
            "The action is SUBMIT_RED",
        )
        for raw in malformed:
            with self.assertRaises(LMStudioActuationError):
                parse_structured_action(raw)

    def test_extra_fields_and_invalid_enums_are_rejected(self) -> None:
        invalid = (
            '{"action":"SUBMIT_RED","reason":"feedback said RED"}',
            '{"action":"RED"}',
            '{"action":"submit_red"}',
            '{"action":null}',
            '{"action":["SUBMIT_RED"]}',
            '{}',
            '[{"action":"SUBMIT_RED"}]',
        )
        for raw in invalid:
            with self.assertRaises(LMStudioActuationError):
                parse_structured_action(raw)

    def test_actuation_failure_is_recorded_without_default_or_repair(self) -> None:
        raw = '{"action":"SUBMIT_RED","explanation":"chosen"}'
        adapter = LMStudioConstrainedActionPolicyAdapter(
            config(), transport=FakeTransport([raw])
        )
        with self.assertRaises(LMStudioActuationError):
            adapter(FIXED_TASK, visible_history(RED, CONDITION_F))
        record = adapter.call_records[0]
        self.assertEqual(record["raw_model_response"], raw)
        self.assertIsNone(record["structured_output"])
        self.assertIsNone(record["selected_action"])
        self.assertEqual(record["actuation_failure"], "SCHEMA_VALIDATION_FAILURE")

    def test_world_independently_accepts_and_scores_extracted_action(self) -> None:
        adapter = LMStudioConstrainedActionPolicyAdapter(
            config(), transport=FakeTransport(['{"action":"SUBMIT_BLUE"}'])
        )
        episode = run_episode(
            episode_id="typed-blue-control",
            hidden_color=BLUE,
            condition=CONDITION_F,
            policy=adapter,
        )
        record = adapter.call_records[0]

        self.assertEqual(record["raw_model_response"], '{"action":"SUBMIT_BLUE"}')
        self.assertEqual(record["structured_output"], {"action": SUBMIT_BLUE})
        self.assertEqual(record["selected_action"], SUBMIT_BLUE)
        self.assertEqual(episode["requested_action"], SUBMIT_BLUE)
        self.assertEqual(episode["accepted_terminal_action"], SUBMIT_BLUE)
        self.assertTrue(episode["correct"])


if __name__ == "__main__":
    unittest.main()
