from __future__ import annotations

import gc
import json
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from lab.ops.candidates.dme_warranted_delta_001.apparatus_v0.durable_invocation_witness import (
    DurableWitnessRoot,
    ESTABLISHED,
    IdentityMismatch,
    InvocationDidNotReturn,
    NOT_ESTABLISHED,
    canonical_json,
    verify_durable_invocation,
)


EXECUTOR_ID = "QUAL_DURABLE_EXECUTOR"
TRANSFORM_ID = "QUAL_DURABLE_TRANSFORM"
INPUT_ID = "QUAL_DURABLE_INPUT"
REALIZATION_ID = "QUAL-DURABLE-R1"
INVOCATION_ID = "QUAL-DURABLE-I1"


def transform(state):
    return {
        **state,
        "counter": state["counter"] + 1,
        "resource_counter": 999,
        "secret_post_state": "MUST_NOT_ENTER_WITNESS",
    }


class DurableInvocationWitnessQualificationTests(unittest.TestCase):
    def make_root(self, journal: Path, executor=None):
        calls = {"count": 0}

        if executor is None:
            def executor(fn, state):
                calls["count"] += 1
                return fn(state)

        root = DurableWitnessRoot.fresh(
            journal_path=journal,
            executor=executor,
            executor_identity=EXECUTOR_ID,
            transformations={TRANSFORM_ID: transform},
        )
        return root, calls

    def verify(self, journal: Path, public_key: bytes, *, invocation_id=INVOCATION_ID):
        return verify_durable_invocation(
            journal.read_bytes() if journal.exists() else b"",
            public_key_bytes=public_key,
            expected_realization_id=REALIZATION_ID,
            expected_invocation_id=invocation_id,
            expected_executor_identity=EXECUTOR_ID,
            expected_transformation_identity=TRANSFORM_ID,
            expected_input_state_identity=INPUT_ID,
        )

    def invoke(self, root):
        return root.mediate_once(
            realization_id=REALIZATION_ID,
            invocation_id=INVOCATION_ID,
            transformation_identity=TRANSFORM_ID,
            input_state={"counter": 0},
            input_state_identity=INPUT_ID,
        )

    def test_q1_real_mediated_call_verifies_after_live_root_is_gone(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, calls = self.make_root(journal)
            public_key = root.public_key_bytes
            capture = self.invoke(root)
            expected_ref = capture.result_state_ref
            del capture
            del root
            gc.collect()

            verdict = self.verify(journal, public_key)
            self.assertEqual(calls["count"], 1)
            self.assertEqual(verdict.status, ESTABLISHED)
            self.assertEqual(verdict.result_state_ref, expected_ref)

    def test_q2_structurally_perfect_unsigned_story_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "forged.jsonl"
            key = Ed25519PrivateKey.generate()
            public_key = key.public_key().public_bytes_raw()
            base = {
                "schema_version": "dme_durable_invocation_witness_v0",
                "witness_key_id": "0" * 64,
                "realization_id": REALIZATION_ID,
                "invocation_id": INVOCATION_ID,
                "executor_identity": EXECUTOR_ID,
                "transformation_identity": TRANSFORM_ID,
                "input_state_identity": INPUT_ID,
            }
            entered = {**base, "event_type": "EXECUTION_ENTERED", "sequence": 1}
            returned = {
                **base,
                "event_type": "EXECUTION_RETURNED",
                "sequence": 2,
                "result_state_ref": "urn:dme:result:forged",
            }
            journal.write_bytes(
                canonical_json({"payload": entered, "signature_hex": "00"}) + b"\n"
                + canonical_json({"payload": returned, "signature_hex": "00"}) + b"\n"
            )
            self.assertEqual(self.verify(journal, public_key).status, NOT_ESTABLISHED)

    def test_q3_caller_has_no_public_sign_or_close_capability(self):
        with tempfile.TemporaryDirectory() as td:
            root, _ = self.make_root(Path(td) / "witness.jsonl")
            public_callables = {
                name
                for name in dir(root)
                if not name.startswith("_") and callable(getattr(root, name))
            }
            self.assertEqual(public_callables, {"fresh", "mediate_once"})
            self.assertFalse(hasattr(root, "sign"))
            self.assertFalse(hasattr(root, "close_invocation"))
            self.assertFalse(hasattr(root, "append_returned"))

    def test_q4_unknown_transformation_cannot_create_entered_or_returned(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, calls = self.make_root(journal)
            with self.assertRaises(IdentityMismatch):
                root.mediate_once(
                    realization_id=REALIZATION_ID,
                    invocation_id=INVOCATION_ID,
                    transformation_identity="UNKNOWN",
                    input_state={"counter": 0},
                    input_state_identity=INPUT_ID,
                )
            self.assertEqual(calls["count"], 0)
            self.assertFalse(journal.exists())

    def test_q5_crash_after_enter_before_return_is_not_completed(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            calls = {"count": 0}

            def exploding_executor(fn, state):
                calls["count"] += 1
                raise RuntimeError("synthetic crash")

            root = DurableWitnessRoot.fresh(
                journal_path=journal,
                executor=exploding_executor,
                executor_identity=EXECUTOR_ID,
                transformations={TRANSFORM_ID: transform},
            )
            public_key = root.public_key_bytes
            with self.assertRaises(InvocationDidNotReturn):
                self.invoke(root)
            del root
            gc.collect()

            lines = [line for line in journal.read_bytes().splitlines() if line]
            self.assertEqual(calls["count"], 1)
            self.assertEqual(len(lines), 1)
            self.assertEqual(self.verify(journal, public_key).status, NOT_ESTABLISHED)

    def test_q6_tampered_return_event_rejects_even_with_original_signature(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, _ = self.make_root(journal)
            public_key = root.public_key_bytes
            self.invoke(root)
            lines = [json.loads(line) for line in journal.read_text().splitlines()]
            lines[1]["payload"]["result_state_ref"] = "urn:dme:result:foreign"
            journal.write_text("\n".join(json.dumps(x, sort_keys=True, separators=(",", ":")) for x in lines) + "\n")
            self.assertEqual(self.verify(journal, public_key).status, NOT_ESTABLISHED)

    def test_q7_replay_as_different_invocation_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, _ = self.make_root(journal)
            public_key = root.public_key_bytes
            self.invoke(root)
            verdict = self.verify(journal, public_key, invocation_id="QUAL-DURABLE-I2")
            self.assertEqual(verdict.status, NOT_ESTABLISHED)

    def test_q8_duplicate_valid_transcript_rejects_as_not_exactly_one_pair(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, _ = self.make_root(journal)
            public_key = root.public_key_bytes
            self.invoke(root)
            data = journal.read_bytes()
            journal.write_bytes(data + data)
            self.assertEqual(self.verify(journal, public_key).status, NOT_ESTABLISHED)

    def test_q9_durable_witness_contains_no_post_state_content(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, _ = self.make_root(journal)
            public_key = root.public_key_bytes
            capture = self.invoke(root)
            raw = journal.read_text()
            self.assertNotIn("resource_counter", raw)
            self.assertNotIn("secret_post_state", raw)
            self.assertNotIn("MUST_NOT_ENTER_WITNESS", raw)
            self.assertNotIn("999", raw)
            self.assertEqual(self.verify(journal, public_key).status, ESTABLISHED)
            self.assertTrue(capture.result_state_ref.startswith("urn:dme:result:"))

    def test_q10_wrong_pinned_public_key_rejects_real_transcript(self):
        with tempfile.TemporaryDirectory() as td:
            journal = Path(td) / "witness.jsonl"
            root, _ = self.make_root(journal)
            self.invoke(root)
            wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
            self.assertEqual(self.verify(journal, wrong_key).status, NOT_ESTABLISHED)


if __name__ == "__main__":
    unittest.main()
