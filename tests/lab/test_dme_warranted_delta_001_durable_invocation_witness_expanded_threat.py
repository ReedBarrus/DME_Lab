from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from lab.ops.candidates.dme_warranted_delta_001.apparatus_v0 import durable_invocation_witness as witness


class DurableInvocationWitnessExpandedThreatCharacterization(unittest.TestCase):
    def test_same_process_reflection_can_obtain_valid_completion_without_executor_call(self):
        calls = {"count": 0}

        def executor(fn, state):
            calls["count"] += 1
            return fn(state)

        def transform(state):
            return {**state, "counter": state["counter"] + 1}

        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root = witness.DurableWitnessRoot.fresh(
                journal_path=journal,
                executor=executor,
                executor_identity="QUAL_DURABLE_EXECUTOR",
                transformations={"QUAL_DURABLE_TRANSFORM": transform},
            )
            public_key = root.public_key_bytes
            base = {
                "schema_version": witness.SCHEMA_VERSION,
                "witness_key_id": root.witness_key_id,
                "realization_id": "QUAL-DURABLE-R1",
                "invocation_id": "QUAL-DURABLE-I1",
                "executor_identity": "QUAL_DURABLE_EXECUTOR",
                "transformation_identity": "QUAL_DURABLE_TRANSFORM",
                "input_state_identity": "QUAL_DURABLE_INPUT",
            }
            result_ref = witness._result_ref(
                realization_id="QUAL-DURABLE-R1",
                invocation_id="QUAL-DURABLE-I1",
                executor_identity="QUAL_DURABLE_EXECUTOR",
                transformation_identity="QUAL_DURABLE_TRANSFORM",
                input_state_identity="QUAL_DURABLE_INPUT",
            )

            # Expanded threat model: a same-process caller can reflectively reach
            # the name-mangled signing/append primitive. No executor call occurs.
            append = getattr(root, "_DurableWitnessRoot__append_signed_event")
            append({**base, "event_type": "EXECUTION_ENTERED", "sequence": 1})
            append(
                {
                    **base,
                    "event_type": "EXECUTION_RETURNED",
                    "sequence": 2,
                    "result_state_ref": result_ref,
                }
            )

            verdict = witness.verify_durable_invocation(
                journal.read_bytes(),
                public_key_bytes=public_key,
                expected_realization_id="QUAL-DURABLE-R1",
                expected_invocation_id="QUAL-DURABLE-I1",
                expected_executor_identity="QUAL_DURABLE_EXECUTOR",
                expected_transformation_identity="QUAL_DURABLE_TRANSFORM",
                expected_input_state_identity="QUAL_DURABLE_INPUT",
            )

            self.assertEqual(calls["count"], 0)
            self.assertEqual(verdict.status, witness.ESTABLISHED)


if __name__ == "__main__":
    unittest.main()
