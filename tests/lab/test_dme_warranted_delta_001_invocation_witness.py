from __future__ import annotations

from dataclasses import replace
import json
import unittest

from lab.ops.candidates.dme_warranted_delta_001.apparatus_v0.invocation_witness import (
    ExecutionEntered,
    ExecutionProvenance,
    ExecutionReturned,
    IdentityMismatch,
    InvocationDidNotReturn,
    InvocationHarness,
    invocation_established,
    serialize_provenance,
    validate_event_story,
)


EXECUTOR_ID = "QUAL_EXECUTOR_ID"
TRANSFORM_ID = "QUAL_TRANSFORM_ID"
INPUT_ID = "QUAL_INPUT_ID"


def increment_counter(state):
    return {**state, "counter": state["counter"] + 1, "secret_post_state": "POST"}


class InvocationWitnessQualificationTests(unittest.TestCase):
    def setUp(self):
        self.executor_calls = 0

        def executor(transformation, state):
            self.executor_calls += 1
            return transformation(state)

        self.harness = InvocationHarness(
            executor=executor,
            executor_identity=EXECUTOR_ID,
            transformations={TRANSFORM_ID: increment_counter},
        )

    def invoke(self, realization_id="QUAL-R1", invocation_id="QUAL-I1"):
        return self.harness.invoke_once(
            realization_id=realization_id,
            invocation_id=invocation_id,
            transformation_identity=TRANSFORM_ID,
            input_state={"counter": 0},
            input_state_identity=INPUT_ID,
        )

    def assert_established(self, capture):
        self.assertTrue(
            invocation_established(
                capture,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )

    def test_q1_actual_call_is_witnessed_exactly_once(self):
        capture = self.invoke()
        self.assertEqual(self.executor_calls, 1)
        self.assertEqual(capture.provenance.invocation_count, 1)
        self.assert_established(capture)

    def test_q2_complete_forged_story_is_not_invocation_evidence(self):
        entered = ExecutionEntered(
            realization_id="QUAL-RX",
            invocation_id="QUAL-IX",
            executor_identity=EXECUTOR_ID,
            transformation_identity=TRANSFORM_ID,
            input_state_identity=INPUT_ID,
        )
        returned = ExecutionReturned(
            realization_id="QUAL-RX",
            invocation_id="QUAL-IX",
            executor_identity=EXECUTOR_ID,
            transformation_identity=TRANSFORM_ID,
            input_state_identity=INPUT_ID,
            result_state_ref="QUAL-RX:QUAL-IX:result:0",
        )
        story = ExecutionProvenance(
            realization_id="QUAL-RX",
            invocation_id="QUAL-IX",
            executor_identity=EXECUTOR_ID,
            transformation_identity=TRANSFORM_ID,
            input_state_identity=INPUT_ID,
            entered_event=entered,
            returned_event=returned,
            result_state_ref=returned.result_state_ref,
            invocation_count=1,
        )
        self.assertTrue(
            validate_event_story(
                story,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )
        self.assertFalse(
            invocation_established(
                story,  # type: ignore[arg-type]
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )
        self.assertEqual(self.executor_calls, 0)

    def test_q3_wrong_executor_identity_rejects_story(self):
        capture = self.invoke()
        p = capture.provenance
        forged = replace(
            p,
            executor_identity="WRONG_EXECUTOR",
            entered_event=replace(p.entered_event, executor_identity="WRONG_EXECUTOR"),
            returned_event=replace(p.returned_event, executor_identity="WRONG_EXECUTOR"),
        )
        self.assertFalse(
            validate_event_story(
                forged,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )

    def test_q4_unknown_transformation_rejects_before_executor_call(self):
        with self.assertRaises(IdentityMismatch):
            self.harness.invoke_once(
                realization_id="QUAL-R1",
                invocation_id="QUAL-I1",
                transformation_identity="WRONG_TRANSFORM",
                input_state={"counter": 0},
                input_state_identity=INPUT_ID,
            )
        self.assertEqual(self.executor_calls, 0)

    def test_q5_mismatched_return_pair_rejects(self):
        capture = self.invoke()
        p = capture.provenance
        forged = replace(
            p,
            returned_event=replace(p.returned_event, invocation_id="OTHER"),
        )
        self.assertFalse(
            validate_event_story(
                forged,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )

    def test_q6_double_invocation_story_rejects(self):
        capture = self.invoke()
        forged = replace(capture.provenance, invocation_count=2)
        self.assertFalse(
            validate_event_story(
                forged,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )

    def test_q7_foreign_result_ref_rejects(self):
        a = self.invoke(realization_id="QUAL-RA", invocation_id="QUAL-IA")
        b = self.invoke(realization_id="QUAL-RB", invocation_id="QUAL-IB")
        forged = replace(
            a.provenance,
            returned_event=replace(
                a.provenance.returned_event,
                result_state_ref=b.provenance.result_state_ref,
            ),
        )
        self.assertFalse(
            validate_event_story(
                forged,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )

    def test_q8_entered_without_return_is_not_established(self):
        def exploding_executor(transformation, state):
            self.executor_calls += 1
            raise RuntimeError("qualification failure")

        harness = InvocationHarness(
            executor=exploding_executor,
            executor_identity=EXECUTOR_ID,
            transformations={TRANSFORM_ID: increment_counter},
        )
        with self.assertRaises(InvocationDidNotReturn) as ctx:
            harness.invoke_once(
                realization_id="QUAL-R1",
                invocation_id="QUAL-I1",
                transformation_identity=TRANSFORM_ID,
                input_state={"counter": 0},
                input_state_identity=INPUT_ID,
            )
        self.assertEqual(ctx.exception.entered_event.event_type, "EXECUTION_ENTERED")
        self.assertEqual(self.executor_calls, 1)

    def test_q9_executor_self_report_does_not_enter_provenance(self):
        def self_reporting_transform(state):
            return {
                **state,
                "executed": True,
                "resource_counter": 999,
                "secret_post_state": "LEAK_ME_IF_BROKEN",
            }

        calls = {"count": 0}

        def executor(transformation, state):
            calls["count"] += 1
            return transformation(state)

        harness = InvocationHarness(
            executor=executor,
            executor_identity=EXECUTOR_ID,
            transformations={TRANSFORM_ID: self_reporting_transform},
        )
        capture = harness.invoke_once(
            realization_id="QUAL-R1",
            invocation_id="QUAL-I1",
            transformation_identity=TRANSFORM_ID,
            input_state={"counter": 0},
            input_state_identity=INPUT_ID,
        )
        encoded = json.dumps(serialize_provenance(capture), sort_keys=True)
        self.assertEqual(calls["count"], 1)
        self.assertNotIn("executed", encoded)
        self.assertNotIn("resource_counter", encoded)
        self.assertNotIn("LEAK_ME_IF_BROKEN", encoded)
        self.assertFalse(hasattr(capture, "result"))

    def test_q10_story_validation_does_not_upgrade_to_invocation_establishment(self):
        capture = self.invoke()
        story = capture.provenance
        self.assertTrue(
            validate_event_story(
                story,
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )
        self.assertFalse(
            invocation_established(
                story,  # type: ignore[arg-type]
                expected_executor_identity=EXECUTOR_ID,
                expected_transformation_identity=TRANSFORM_ID,
                expected_input_state_identity=INPUT_ID,
            )
        )


if __name__ == "__main__":
    unittest.main()
