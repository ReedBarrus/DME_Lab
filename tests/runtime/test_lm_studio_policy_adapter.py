from __future__ import annotations

import json
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
)
from src.runtime.lm_studio_policy_adapter import (
    DEFAULT_ENDPOINT,
    LMStudioEndpointConfig,
    LMStudioPolicyAdapter,
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


if __name__ == "__main__":
    unittest.main()
