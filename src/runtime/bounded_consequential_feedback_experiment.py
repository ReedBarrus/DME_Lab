"""Minimal apparatus for the frozen bounded consequential feedback experiment.

This module implements the world evaluator, a narrow injected-policy boundary,
and the comparison driver.  It deliberately does not contain a model provider
adapter or execute an LLM specimen.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


EXPERIMENT_ID = "bounded_consequential_feedback_experiment_v0"
PROTOCOL_VERSION = "v0"
IMPLEMENTATION_BASIS = "146472a28974610cd1c4a03a3c7b32ac077c12ba"
TRACE_PATH = Path("traces") / "bounded_consequential_feedback_apparatus_v0.json"

RED = "RED"
BLUE = "BLUE"
CONDITION_F = "F"
CONDITION_P = "P"
INSPECT = "INSPECT"
SUBMIT_RED = "SUBMIT_RED"
SUBMIT_BLUE = "SUBMIT_BLUE"

COLORS = (RED, BLUE)
CONDITIONS = (CONDITION_F, CONDITION_P)
ACTION_VOCABULARY = (INSPECT, SUBMIT_RED, SUBMIT_BLUE)
TERMINAL_ACTIONS = (SUBMIT_RED, SUBMIT_BLUE)
FIXED_TASK = (
    "Submit the color matching the independently maintained hidden state. "
    "Respond with exactly SUBMIT_RED or SUBMIT_BLUE."
)
SCORING_RULE = (
    "correct iff the first accepted terminal submission matches the "
    "authoritative hidden color"
)

# Exact, predeclared order.  Each slot is executed as the adjacent pair F then P.
FROZEN_HIDDEN_STATE_SLOTS = (
    RED,
    BLUE,
    BLUE,
    RED,
    BLUE,
    RED,
    RED,
    BLUE,
)
FROZEN_PAIRED_CONDITION_ORDER = (CONDITION_F, CONDITION_P)

Policy = Callable[[str, tuple[dict[str, Any], ...]], str]


class ProtocolViolation(RuntimeError):
    """Raised when the driver asks the world to violate the frozen protocol."""


class TerminalCommitmentError(ProtocolViolation):
    """Raised when an action is attempted after terminal commitment."""


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compile_frozen_llm_schedule() -> dict[str, Any]:
    """Return the exact 16-episode schedule without executing it."""

    slots = [
        {"slot": index, "hidden_color": hidden_color}
        for index, hidden_color in enumerate(FROZEN_HIDDEN_STATE_SLOTS, start=1)
    ]
    episodes = [
        {
            "episode_id": f"llm-s{slot['slot']:02d}-{condition.lower()}",
            "slot": slot["slot"],
            "hidden_color": slot["hidden_color"],
            "condition": condition,
        }
        for slot in slots
        for condition in FROZEN_PAIRED_CONDITION_ORDER
    ]
    hidden_commitment = _canonical_sha256(slots)
    condition_commitment = _canonical_sha256(
        {"paired_order": list(FROZEN_PAIRED_CONDITION_ORDER)}
    )
    schedule_commitment = _canonical_sha256(episodes)
    return {
        "status": "PRECOMMITTED_NOT_EXECUTED",
        "ordering_mode": "exact_schedule",
        "hidden_state_slots": slots,
        "paired_condition_order": list(FROZEN_PAIRED_CONDITION_ORDER),
        "episodes": episodes,
        "hidden_state_schedule_commitment": f"sha256:{hidden_commitment}",
        "condition_schedule_commitment": f"sha256:{condition_commitment}",
        "exact_schedule_commitment": f"sha256:{schedule_commitment}",
        "future_policy_receives_schedule_metadata": False,
    }


class BoundedColorWorld:
    """Authoritative episode world and terminal scorer."""

    def __init__(self, hidden_color: str, condition: str) -> None:
        if hidden_color not in COLORS:
            raise ValueError(f"unsupported hidden color: {hidden_color!r}")
        if condition not in CONDITIONS:
            raise ValueError(f"unsupported condition: {condition!r}")
        self._hidden_color = hidden_color
        self._condition = condition
        self._phase = "WORLD_STATE_ESTABLISHED"
        self._feedback: str | None = None
        self._accepted_terminal_action: str | None = None
        self._failure_class: str | None = None
        self._post_commit_feedback_delivered = False
        self._events: list[dict[str, Any]] = []
        self._record(
            "WORLD_STATE_ESTABLISHED",
            policy_visible=False,
            payload={"hidden_color": hidden_color},
        )

    @property
    def terminal_committed(self) -> bool:
        return self._accepted_terminal_action is not None

    @property
    def accepted_terminal_action(self) -> str | None:
        return self._accepted_terminal_action

    def _record(
        self,
        event_type: str,
        *,
        policy_visible: bool,
        payload: Mapping[str, Any],
    ) -> None:
        self._events.append(
            {
                "event_index": len(self._events),
                "event_type": event_type,
                "policy_visible": policy_visible,
                "payload": deepcopy(dict(payload)),
            }
        )

    def inspect(self) -> None:
        if self._phase != "WORLD_STATE_ESTABLISHED":
            raise ProtocolViolation("INSPECT is legal exactly once after state establishment")
        self._record(
            "INSPECT_EXECUTED",
            policy_visible=True,
            payload={"action": INSPECT},
        )
        self._feedback = self._hidden_color
        self._record(
            "FEEDBACK_PRODUCED",
            policy_visible=False,
            payload={"feedback": self._feedback},
        )
        self._phase = "FEEDBACK_PRODUCED"

    def prepare_policy_call(self) -> tuple[dict[str, Any], ...]:
        if self._phase != "FEEDBACK_PRODUCED":
            raise ProtocolViolation("policy call preparation requires produced feedback")
        if self._condition == CONDITION_F:
            self._record(
                "FEEDBACK_DELIVERED",
                policy_visible=True,
                payload={"feedback": self._feedback},
            )
        else:
            self._record(
                "FEEDBACK_WITHHELD",
                policy_visible=False,
                payload={"feedback_produced": True},
            )
        self._phase = "POLICY_CALL_READY"
        return self.policy_visible_history()

    def policy_visible_history(self) -> tuple[dict[str, Any], ...]:
        """Return only declared visible event content, excluding trace internals."""

        return tuple(
            {
                "event_type": event["event_type"],
                "payload": deepcopy(event["payload"]),
            }
            for event in self._events
            if event["policy_visible"]
        )

    def receive_terminal_request(
        self,
        requested_action: str | None,
        *,
        policy_error: str | None = None,
    ) -> None:
        if self.terminal_committed:
            raise TerminalCommitmentError("terminal commitment cannot be revised")
        if self._phase != "POLICY_CALL_READY":
            raise ProtocolViolation("terminal request requires the frozen terminal policy call")

        request_payload: dict[str, Any] = {"requested_action": requested_action}
        if policy_error is not None:
            request_payload["policy_error"] = policy_error
        self._record(
            "POLICY_ACTION_REQUESTED",
            policy_visible=False,
            payload=request_payload,
        )

        if policy_error is not None:
            self._failure_class = "POLICY_INVOCATION_FAILURE"
            self._record(
                "WORLD_ACTION_RECEIPT",
                policy_visible=False,
                payload={
                    "requested_action": requested_action,
                    "accepted_action": None,
                    "accepted": False,
                    "reason": self._failure_class,
                },
            )
            self._phase = "NONTERMINAL_FAILURE"
            return

        if requested_action not in ACTION_VOCABULARY:
            self._failure_class = "MALFORMED_POLICY_OUTPUT"
            self._record(
                "WORLD_ACTION_RECEIPT",
                policy_visible=False,
                payload={
                    "requested_action": requested_action,
                    "accepted_action": None,
                    "accepted": False,
                    "reason": self._failure_class,
                },
            )
            self._phase = "NONTERMINAL_FAILURE"
            return

        if requested_action == INSPECT:
            self._failure_class = "INADMISSIBLE_TERMINAL_REQUEST"
            self._record(
                "WORLD_ACTION_RECEIPT",
                policy_visible=False,
                payload={
                    "requested_action": requested_action,
                    "accepted_action": None,
                    "accepted": False,
                    "reason": self._failure_class,
                },
            )
            self._phase = "NONTERMINAL_FAILURE"
            return

        self._record(
            "WORLD_ACTION_RECEIPT",
            policy_visible=False,
            payload={
                "requested_action": requested_action,
                "accepted_action": requested_action,
                "accepted": True,
                "reason": None,
            },
        )
        self._accepted_terminal_action = requested_action
        self._record(
            "TERMINAL_COMMITMENT",
            policy_visible=False,
            payload={"accepted_terminal_action": requested_action},
        )
        self._phase = "TERMINAL_COMMITTED"

    def deliver_post_commit_feedback(self) -> None:
        if self._condition != CONDITION_P:
            raise ProtocolViolation("post-commit disclosure belongs only to Condition P")
        if not self.terminal_committed:
            raise ProtocolViolation("feedback may be disclosed only after terminal commitment")
        if self._post_commit_feedback_delivered:
            raise ProtocolViolation("post-commit feedback may be delivered at most once")
        self._record(
            "POST_COMMIT_FEEDBACK_DELIVERY",
            policy_visible=True,
            payload={"feedback": self._feedback},
        )
        self._post_commit_feedback_delivered = True

    def result(self) -> dict[str, Any]:
        expected_action = f"SUBMIT_{self._hidden_color}"
        accepted = self._accepted_terminal_action
        return {
            "condition": self._condition,
            "hidden_state": self._hidden_color,
            "ordered_events": deepcopy(self._events),
            "requested_action": next(
                (
                    event["payload"]["requested_action"]
                    for event in self._events
                    if event["event_type"] == "POLICY_ACTION_REQUESTED"
                ),
                None,
            ),
            "accepted_terminal_action": accepted,
            "correct": accepted == expected_action if accepted is not None else False,
            "valid": True,
            "failure_class": self._failure_class,
        }


def lookup_control(
    fixed_task: str,
    policy_visible_protocol_history: tuple[dict[str, Any], ...],
) -> str:
    """Return the exact terminal token matching delivered feedback."""

    del fixed_task
    for event in reversed(policy_visible_protocol_history):
        if event["event_type"] == "FEEDBACK_DELIVERED":
            feedback = event["payload"].get("feedback")
            if feedback in COLORS:
                return f"SUBMIT_{feedback}"
    return "NO_VISIBLE_FEEDBACK"


def fixed_answer_control(
    fixed_task: str,
    policy_visible_protocol_history: tuple[dict[str, Any], ...],
) -> str:
    """Return the declared unconditioned terminal answer."""

    del fixed_task, policy_visible_protocol_history
    return SUBMIT_RED


def run_episode(
    *,
    episode_id: str,
    hidden_color: str,
    condition: str,
    policy: Policy,
    post_commit_feedback: bool = True,
) -> dict[str, Any]:
    """Run one bounded episode through the injected visible-input policy hook."""

    world = BoundedColorWorld(hidden_color, condition)
    world.inspect()
    visible_history = world.prepare_policy_call()
    try:
        requested_action = policy(FIXED_TASK, visible_history)
    except Exception as exc:  # Policy failures are retained, not apparatus repair.
        world.receive_terminal_request(
            None,
            policy_error=f"{type(exc).__name__}: {exc}",
        )
    else:
        if not isinstance(requested_action, str):
            world.receive_terminal_request(
                None,
                policy_error=(
                    "policy returned non-string "
                    f"{type(requested_action).__name__}"
                ),
            )
        else:
            world.receive_terminal_request(requested_action)

    if condition == CONDITION_P and post_commit_feedback and world.terminal_committed:
        world.deliver_post_commit_feedback()

    result = world.result()
    result["episode_id"] = episode_id
    return result


def run_comparison(
    *,
    policy: Policy,
    policy_identity: str,
    policy_configuration: Mapping[str, Any],
    episodes: Sequence[Mapping[str, Any]],
    post_commit_feedback: bool = True,
) -> dict[str, Any]:
    """Execute a supplied deterministic schedule and retain every episode."""

    frozen_episodes = [deepcopy(dict(episode)) for episode in episodes]
    results = [
        run_episode(
            episode_id=str(episode["episode_id"]),
            hidden_color=str(episode["hidden_color"]),
            condition=str(episode["condition"]),
            policy=policy,
            post_commit_feedback=post_commit_feedback,
        )
        for episode in frozen_episodes
    ]
    schedule = compile_frozen_llm_schedule()
    return {
        "run_declaration": {
            "experiment_id": EXPERIMENT_ID,
            "protocol_version": PROTOCOL_VERSION,
            "policy_identity": policy_identity,
            "policy_configuration": deepcopy(dict(policy_configuration)),
            "task_text": FIXED_TASK,
            "action_vocabulary": list(ACTION_VOCABULARY),
            "hidden_state_schedule_commitment": _canonical_sha256(
                [episode["hidden_color"] for episode in frozen_episodes]
            ),
            "condition_schedule_commitment": _canonical_sha256(
                [episode["condition"] for episode in frozen_episodes]
            ),
            "randomization_seed_or_schedule": {
                "mode": "exact_schedule",
                "commitment": _canonical_sha256(frozen_episodes),
            },
            "scoring_rule": SCORING_RULE,
            "policy_received_schedule_metadata": False,
            "frozen_future_llm_schedule_commitment": schedule[
                "exact_schedule_commitment"
            ],
        },
        "episodes": results,
        "summary": _summarize(results),
    }


def run_frozen_comparison(
    *,
    policy: Policy,
    policy_identity: str,
    policy_configuration: Mapping[str, Any],
    post_commit_feedback: bool = True,
) -> dict[str, Any]:
    """Narrow future hook that cannot substitute a post-output schedule."""

    schedule = compile_frozen_llm_schedule()
    return run_comparison(
        policy=policy,
        policy_identity=policy_identity,
        policy_configuration=policy_configuration,
        episodes=schedule["episodes"],
        post_commit_feedback=post_commit_feedback,
    )


def _summarize(episodes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_condition: dict[str, dict[str, int]] = {}
    for condition in CONDITIONS:
        selected = [episode for episode in episodes if episode["condition"] == condition]
        by_condition[condition] = {
            "episodes": len(selected),
            "accepted_red": sum(
                episode["accepted_terminal_action"] == SUBMIT_RED for episode in selected
            ),
            "accepted_blue": sum(
                episode["accepted_terminal_action"] == SUBMIT_BLUE for episode in selected
            ),
            "correct": sum(bool(episode["correct"]) for episode in selected),
            "malformed_or_inadmissible": sum(
                episode["failure_class"]
                in {"MALFORMED_POLICY_OUTPUT", "INADMISSIBLE_TERMINAL_REQUEST"}
                for episode in selected
            ),
            "nonterminal_failures": sum(
                episode["accepted_terminal_action"] is None for episode in selected
            ),
        }
    return {
        "episodes": len(episodes),
        "correct": sum(bool(episode["correct"]) for episode in episodes),
        "by_condition": by_condition,
    }


def _event_index(episode: Mapping[str, Any], event_type: str) -> int:
    return next(
        event["event_index"]
        for event in episode["ordered_events"]
        if event["event_type"] == event_type
    )


def _terminal_immutability_check() -> dict[str, Any]:
    world = BoundedColorWorld(RED, CONDITION_F)
    world.inspect()
    world.prepare_policy_call()
    world.receive_terminal_request(SUBMIT_RED)
    before = world.result()
    rejected = False
    try:
        world.receive_terminal_request(SUBMIT_BLUE)
    except TerminalCommitmentError:
        rejected = True
    after = world.result()
    return {
        "revision_attempt_rejected": rejected,
        "accepted_action_before": before["accepted_terminal_action"],
        "accepted_action_after": after["accepted_terminal_action"],
        "trace_unchanged": before["ordered_events"] == after["ordered_events"],
    }


def build_apparatus_report() -> dict[str, Any]:
    """Build deterministic control evidence without executing an LLM specimen."""

    schedule = compile_frozen_llm_schedule()
    lookup_episodes = [
        {
            "episode_id": "lookup-f-red",
            "hidden_color": RED,
            "condition": CONDITION_F,
        },
        {
            "episode_id": "lookup-f-blue",
            "hidden_color": BLUE,
            "condition": CONDITION_F,
        },
    ]
    lookup = run_comparison(
        policy=lookup_control,
        policy_identity="deterministic_lookup_control",
        policy_configuration={"mapping": {RED: SUBMIT_RED, BLUE: SUBMIT_BLUE}},
        episodes=lookup_episodes,
    )
    fixed = run_comparison(
        policy=fixed_answer_control,
        policy_identity="deterministic_fixed_answer_control",
        policy_configuration={"fixed_answer": SUBMIT_RED},
        episodes=schedule["episodes"],
    )
    lookup_by_color = {
        episode["hidden_state"]: episode for episode in lookup["episodes"]
    }
    p_episodes = [
        episode for episode in fixed["episodes"] if episode["condition"] == CONDITION_P
    ]
    immutability = _terminal_immutability_check()
    checks = {
        "F_delivers_RED_before_commitment": (
            _event_index(lookup_by_color[RED], "FEEDBACK_DELIVERED")
            < _event_index(lookup_by_color[RED], "TERMINAL_COMMITMENT")
        ),
        "F_delivers_BLUE_before_commitment": (
            _event_index(lookup_by_color[BLUE], "FEEDBACK_DELIVERED")
            < _event_index(lookup_by_color[BLUE], "TERMINAL_COMMITMENT")
        ),
        "P_exposes_no_produced_feedback_before_commitment": all(
            all(
                not (
                    event["policy_visible"]
                    and event["event_type"]
                    in {"FEEDBACK_PRODUCED", "FEEDBACK_DELIVERED"}
                )
                for event in episode["ordered_events"]
                if event["event_index"]
                < _event_index(episode, "TERMINAL_COMMITMENT")
            )
            for episode in p_episodes
        ),
        "P_discloses_feedback_only_after_commitment": all(
            _event_index(episode, "TERMINAL_COMMITMENT")
            < _event_index(episode, "POST_COMMIT_FEEDBACK_DELIVERY")
            for episode in p_episodes
        ),
        "terminal_action_cannot_be_revised": (
            immutability["revision_attempt_rejected"]
            and immutability["accepted_action_before"]
            == immutability["accepted_action_after"]
            and immutability["trace_unchanged"]
        ),
        "lookup_control_maps_both_delivered_colors": (
            lookup["summary"]["correct"] == 2
            and all(episode["failure_class"] is None for episode in lookup["episodes"])
        ),
        "fixed_answer_is_penalized_by_balanced_schedule": (
            fixed["summary"]["correct"] == 8
            and fixed["summary"]["episodes"] == 16
            and fixed["summary"]["by_condition"][CONDITION_F]["correct"] == 4
            and fixed["summary"]["by_condition"][CONDITION_P]["correct"] == 4
        ),
    }
    return {
        "artifact": "bounded_consequential_feedback_apparatus_v0",
        "artifact_class": "DETERMINISTIC_APPARATUS_EVIDENCE",
        "implementation_basis": IMPLEMENTATION_BASIS,
        "frozen_protocol": (
            "docs/methods/Consequence_Surface/"
            "Bounded_Consequential_Feedback_Experiment_v0.md"
        ),
        "llm_specimen": {
            "executed": False,
            "policy_identity": None,
            "policy_configuration": None,
            "reason": "separate execution authorization required",
        },
        "frozen_future_llm_schedule": schedule,
        "deterministic_controls": {
            "lookup": lookup,
            "fixed_answer": fixed,
            "terminal_immutability": immutability,
        },
        "apparatus_checks": checks,
        "all_apparatus_checks_passed": all(checks.values()),
        "standing": {
            "implementation": "SCAFFOLD_IMPLEMENTED",
            "bounded_feedback_dependence": "PRESSUREABLE_NOT_EXECUTED",
            "agency": "NOT_ESTABLISHED",
            "persistent_state_agency": "NOT_REQUIRED",
            "home": "OUT_OF_SCOPE",
            "new_scientific_standing_earned": False,
        },
    }


def write_apparatus_trace(path: Path | str = TRACE_PATH) -> dict[str, Any]:
    report = build_apparatus_report()
    Path(path).write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    write_apparatus_trace()
