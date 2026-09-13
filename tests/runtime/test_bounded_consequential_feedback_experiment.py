from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.runtime.bounded_consequential_feedback_experiment import (
    ACTION_VOCABULARY,
    BLUE,
    CONDITION_F,
    CONDITION_P,
    FIXED_TASK,
    RED,
    SUBMIT_BLUE,
    SUBMIT_RED,
    TRACE_PATH,
    BoundedColorWorld,
    ProtocolViolation,
    TerminalCommitmentError,
    build_apparatus_report,
    compile_frozen_llm_schedule,
    fixed_answer_control,
    lookup_control,
    run_comparison,
    run_episode,
    run_frozen_comparison,
)


class BoundedConsequentialFeedbackExperimentTest(unittest.TestCase):
    def test_frozen_schedule_is_exact_balanced_and_paired(self) -> None:
        schedule = compile_frozen_llm_schedule()
        slots = schedule["hidden_state_slots"]
        episodes = schedule["episodes"]

        self.assertEqual(schedule["status"], "PRECOMMITTED_NOT_EXECUTED")
        self.assertEqual(len(slots), 8)
        self.assertEqual(sum(slot["hidden_color"] == RED for slot in slots), 4)
        self.assertEqual(sum(slot["hidden_color"] == BLUE for slot in slots), 4)
        self.assertEqual(len(episodes), 16)
        for slot in slots:
            paired = [episode for episode in episodes if episode["slot"] == slot["slot"]]
            self.assertEqual([episode["condition"] for episode in paired], ["F", "P"])
            self.assertEqual(
                [episode["hidden_color"] for episode in paired],
                [slot["hidden_color"], slot["hidden_color"]],
            )
        self.assertFalse(schedule["future_policy_receives_schedule_metadata"])
        self.assertTrue(schedule["exact_schedule_commitment"].startswith("sha256:"))
        self.assertEqual(schedule, compile_frozen_llm_schedule())

    def test_F_lookup_receives_each_feedback_before_terminal_commitment(self) -> None:
        for hidden, expected in ((RED, SUBMIT_RED), (BLUE, SUBMIT_BLUE)):
            episode = run_episode(
                episode_id=f"f-{hidden.lower()}",
                hidden_color=hidden,
                condition=CONDITION_F,
                policy=lookup_control,
            )
            event_types = [event["event_type"] for event in episode["ordered_events"]]
            self.assertLess(
                event_types.index("FEEDBACK_DELIVERED"),
                event_types.index("POLICY_ACTION_REQUESTED"),
            )
            self.assertLess(
                event_types.index("POLICY_ACTION_REQUESTED"),
                event_types.index("TERMINAL_COMMITMENT"),
            )
            self.assertEqual(episode["requested_action"], expected)
            self.assertEqual(episode["accepted_terminal_action"], expected)
            self.assertTrue(episode["correct"])

    def test_P_policy_input_excludes_hidden_feedback_and_schedule_metadata(self) -> None:
        calls: list[tuple[str, tuple[dict[str, object], ...]]] = []

        def recording_policy(
            task: str, history: tuple[dict[str, object], ...]
        ) -> str:
            calls.append((task, history))
            return SUBMIT_RED

        episode = run_episode(
            episode_id="p-blue",
            hidden_color=BLUE,
            condition=CONDITION_P,
            policy=recording_policy,
        )

        self.assertEqual(len(calls), 1)
        task, history = calls[0]
        self.assertEqual(task, FIXED_TASK)
        self.assertEqual(
            history,
            ({"event_type": "INSPECT_EXECUTED", "payload": {"action": "INSPECT"}},),
        )
        visible_serialized = json.dumps(history, sort_keys=True)
        for forbidden in (BLUE, "hidden_state", "condition", "schedule", "seed", "score"):
            self.assertNotIn(forbidden, visible_serialized)
        self.assertEqual(episode["accepted_terminal_action"], SUBMIT_RED)
        self.assertFalse(episode["correct"])

    def test_P_withholds_feedback_until_after_terminal_commitment(self) -> None:
        episode = run_episode(
            episode_id="p-red",
            hidden_color=RED,
            condition=CONDITION_P,
            policy=fixed_answer_control,
        )
        events = episode["ordered_events"]
        types = [event["event_type"] for event in events]
        self.assertIn("FEEDBACK_PRODUCED", types)
        self.assertIn("FEEDBACK_WITHHELD", types)
        self.assertNotIn("FEEDBACK_DELIVERED", types)
        self.assertLess(
            types.index("TERMINAL_COMMITMENT"),
            types.index("POST_COMMIT_FEEDBACK_DELIVERY"),
        )
        precommit = events[: types.index("TERMINAL_COMMITMENT")]
        self.assertFalse(
            any(
                event["policy_visible"]
                and event["event_type"] in {"FEEDBACK_PRODUCED", "FEEDBACK_DELIVERED"}
                for event in precommit
            )
        )

    def test_P_postcommit_feedback_is_optional(self) -> None:
        episode = run_episode(
            episode_id="p-no-disclosure",
            hidden_color=RED,
            condition=CONDITION_P,
            policy=fixed_answer_control,
            post_commit_feedback=False,
        )
        self.assertNotIn(
            "POST_COMMIT_FEEDBACK_DELIVERY",
            [event["event_type"] for event in episode["ordered_events"]],
        )

    def test_terminal_commitment_cannot_be_revised(self) -> None:
        world = BoundedColorWorld(RED, CONDITION_F)
        world.inspect()
        world.prepare_policy_call()
        world.receive_terminal_request(SUBMIT_RED)
        before = world.result()

        with self.assertRaises(TerminalCommitmentError):
            world.receive_terminal_request(SUBMIT_BLUE)

        after = world.result()
        self.assertEqual(after["accepted_terminal_action"], SUBMIT_RED)
        self.assertEqual(after["ordered_events"], before["ordered_events"])

    def test_postcommit_delivery_cannot_happen_before_commitment_or_under_F(self) -> None:
        p_world = BoundedColorWorld(RED, CONDITION_P)
        p_world.inspect()
        p_world.prepare_policy_call()
        with self.assertRaises(ProtocolViolation):
            p_world.deliver_post_commit_feedback()

        f_world = BoundedColorWorld(RED, CONDITION_F)
        f_world.inspect()
        f_world.prepare_policy_call()
        f_world.receive_terminal_request(SUBMIT_RED)
        with self.assertRaises(ProtocolViolation):
            f_world.deliver_post_commit_feedback()

    def test_action_parsing_is_strict_and_does_not_repair_prose(self) -> None:
        malformed = (
            " SUBMIT_RED",
            "SUBMIT_RED\n",
            "submit_red",
            "I think the answer is RED",
            "RED",
        )
        for index, token in enumerate(malformed):
            episode = run_episode(
                episode_id=f"malformed-{index}",
                hidden_color=RED,
                condition=CONDITION_F,
                policy=lambda task, history, token=token: token,
            )
            self.assertEqual(episode["requested_action"], token)
            self.assertIsNone(episode["accepted_terminal_action"])
            self.assertEqual(episode["failure_class"], "MALFORMED_POLICY_OUTPUT")
            self.assertTrue(episode["valid"])
            self.assertFalse(episode["correct"])

    def test_requested_action_remains_distinct_from_world_acceptance(self) -> None:
        episode = run_episode(
            episode_id="inadmissible-inspect",
            hidden_color=RED,
            condition=CONDITION_F,
            policy=lambda task, history: "INSPECT",
        )
        receipt = next(
            event
            for event in episode["ordered_events"]
            if event["event_type"] == "WORLD_ACTION_RECEIPT"
        )
        self.assertEqual(episode["requested_action"], "INSPECT")
        self.assertIsNone(episode["accepted_terminal_action"])
        self.assertFalse(receipt["payload"]["accepted"])
        self.assertIsNone(receipt["payload"]["accepted_action"])
        self.assertEqual(episode["failure_class"], "INADMISSIBLE_TERMINAL_REQUEST")

    def test_policy_failure_is_retained_without_invalidating_apparatus(self) -> None:
        def failed_policy(task: str, history: tuple[dict[str, object], ...]) -> str:
            raise RuntimeError("deterministic control failure")

        episode = run_episode(
            episode_id="policy-failure",
            hidden_color=RED,
            condition=CONDITION_F,
            policy=failed_policy,
        )
        self.assertIsNone(episode["accepted_terminal_action"])
        self.assertEqual(episode["failure_class"], "POLICY_INVOCATION_FAILURE")
        self.assertTrue(episode["valid"])

    def test_fixed_answer_control_is_penalized_by_balanced_schedule(self) -> None:
        run = run_frozen_comparison(
            policy=fixed_answer_control,
            policy_identity="deterministic_fixed_answer_control",
            policy_configuration={"fixed_answer": SUBMIT_RED},
        )
        self.assertEqual(run["summary"]["episodes"], 16)
        self.assertEqual(run["summary"]["correct"], 8)
        self.assertEqual(run["summary"]["by_condition"]["F"]["correct"], 4)
        self.assertEqual(run["summary"]["by_condition"]["P"]["correct"], 4)
        self.assertEqual(
            {episode["accepted_terminal_action"] for episode in run["episodes"]},
            {SUBMIT_RED},
        )
        self.assertFalse(run["run_declaration"]["policy_received_schedule_metadata"])

    def test_world_scoring_uses_hidden_state_and_accepted_submission_only(self) -> None:
        correct = run_episode(
            episode_id="blue-correct",
            hidden_color=BLUE,
            condition=CONDITION_F,
            policy=lambda task, history: SUBMIT_BLUE,
        )
        narrated = run_episode(
            episode_id="blue-narrated",
            hidden_color=BLUE,
            condition=CONDITION_F,
            policy=lambda task, history: "BLUE is certainly correct",
        )
        self.assertTrue(correct["correct"])
        self.assertFalse(narrated["correct"])
        self.assertIsNone(narrated["accepted_terminal_action"])

    def test_trace_events_have_minimum_shape(self) -> None:
        episode = run_episode(
            episode_id="shape",
            hidden_color=RED,
            condition=CONDITION_F,
            policy=lookup_control,
        )
        for expected_index, event in enumerate(episode["ordered_events"]):
            self.assertEqual(event["event_index"], expected_index)
            self.assertEqual(
                set(event), {"event_index", "event_type", "policy_visible", "payload"}
            )

    def test_invalid_world_coordinates_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            BoundedColorWorld("GREEN", CONDITION_F)
        with self.assertRaises(ValueError):
            BoundedColorWorld(RED, "UNKNOWN")

    def test_committed_trace_matches_deterministic_regeneration(self) -> None:
        committed = json.loads(Path(TRACE_PATH).read_text(encoding="utf-8"))
        regenerated = build_apparatus_report()
        self.assertEqual(committed, regenerated)
        self.assertTrue(committed["all_apparatus_checks_passed"])
        self.assertFalse(committed["llm_specimen"]["executed"])
        self.assertFalse(committed["standing"]["new_scientific_standing_earned"])
        self.assertEqual(tuple(committed["deterministic_controls"]["lookup"]["run_declaration"]["action_vocabulary"]), ACTION_VOCABULARY)


if __name__ == "__main__":
    unittest.main()
