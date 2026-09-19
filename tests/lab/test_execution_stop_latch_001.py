import tempfile
import unittest
from pathlib import Path

from lab.ops.candidates.execution_stop_latch_001.fixture_setup import (
    DECLARATION_SCHEMA_VERSION,
    InitialAuthorityMaterializationError,
    materialize_declared_initial_authority,
)
from lab.ops.candidates.execution_stop_latch_001.guarded_surface import (
    create_held_out_condition_root,
    emit_experimental_score,
)
from lab.ops.candidates.execution_stop_latch_001.stop_latch import (
    ACTIVE,
    STOPPED,
    ExecutionEnvelopeStateError,
    ExecutionEnvelopeStopped,
    ExecutionStopLatch,
)


class TestExecutionStopLatch001(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = self.root / "state"
        self.envelope_id = "E-001"
        self.authority_declaration = {
            "schema_version": DECLARATION_SCHEMA_VERSION,
            "execution_envelope_id": self.envelope_id,
            "declared_state": ACTIVE,
        }

    def tearDown(self):
        self.tmp.cleanup()

    def materialized_latch(self) -> ExecutionStopLatch:
        materialize_declared_initial_authority(
            self.store, self.authority_declaration
        )
        return ExecutionStopLatch(self.store, self.envelope_id)

    def test_absence_does_not_create_authority(self):
        latch = ExecutionStopLatch(self.store, self.envelope_id)
        self.assertFalse(latch.state_path.exists())

        with self.assertRaises(ExecutionEnvelopeStateError):
            latch.state()
        with self.assertRaises(ExecutionEnvelopeStateError):
            latch.consume_terminal_stop()
        with self.assertRaises(ExecutionEnvelopeStateError):
            create_held_out_condition_root(latch, self.root / "absent-root")
        with self.assertRaises(ExecutionEnvelopeStateError):
            emit_experimental_score(latch, self.root / "absent-score.json")

        self.assertFalse(latch.state_path.exists())
        self.assertFalse((self.root / "absent-root").exists())
        self.assertFalse((self.root / "absent-score.json").exists())

    def test_declared_initial_authority_reaches_clean_path(self):
        latch = self.materialized_latch()
        self.assertEqual(latch.state(), ACTIVE)
        marker = create_held_out_condition_root(latch, self.root / "a")
        self.assertTrue(marker.exists())
        self.assertEqual(latch.state(), ACTIVE)

    def test_stop_blocks_two_paths(self):
        latch = self.materialized_latch()
        latch.consume_terminal_stop()
        with self.assertRaises(ExecutionEnvelopeStopped):
            create_held_out_condition_root(latch, self.root / "b")
        with self.assertRaises(ExecutionEnvelopeStopped):
            emit_experimental_score(latch, self.root / "score.json")
        self.assertFalse((self.root / "b").exists())
        self.assertFalse((self.root / "score.json").exists())

    def test_stop_survives_reacquisition_same_authority_locus(self):
        latch = self.materialized_latch()
        latch.consume_terminal_stop()

        again = ExecutionStopLatch(self.store, self.envelope_id)
        self.assertEqual(again.state(), STOPPED)
        with self.assertRaises(ExecutionEnvelopeStopped):
            create_held_out_condition_root(again, self.root / "c")
        with self.assertRaises(ExecutionEnvelopeStopped):
            emit_experimental_score(again, self.root / "score-after-reacquire.json")

    def test_fixture_materialization_cannot_reactivate_stopped_state(self):
        latch = self.materialized_latch()
        latch.consume_terminal_stop()

        with self.assertRaises(InitialAuthorityMaterializationError):
            materialize_declared_initial_authority(
                self.store, self.authority_declaration
            )
        self.assertEqual(latch.state(), STOPPED)

    def test_receipt_allowed_while_stopped(self):
        latch = self.materialized_latch()
        latch.consume_terminal_stop()
        self.assertEqual(latch.receipt()["state"], STOPPED)


if __name__ == "__main__":
    unittest.main()
