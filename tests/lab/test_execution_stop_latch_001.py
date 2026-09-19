import tempfile
import unittest
from pathlib import Path

from lab.ops.candidates.execution_stop_latch_001.guarded_surface import (
    create_held_out_condition_root,
    emit_experimental_score,
)
from lab.ops.candidates.execution_stop_latch_001.stop_latch import (
    ACTIVE,
    STOPPED,
    ExecutionEnvelopeStopped,
    ExecutionStopLatch,
)


class TestExecutionStopLatch001(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = self.root / "state"
        self.envelope_id = "E-001"
        self.latch = ExecutionStopLatch(self.store, self.envelope_id)
        self.assertEqual(self.latch.materialize_active()["state"], ACTIVE)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_path(self):
        marker = create_held_out_condition_root(self.latch, self.root / "a")
        self.assertTrue(marker.exists())
        self.assertEqual(self.latch.state(), ACTIVE)

    def test_stop_blocks_two_paths(self):
        self.latch.consume_terminal_stop()
        with self.assertRaises(ExecutionEnvelopeStopped):
            create_held_out_condition_root(self.latch, self.root / "b")
        with self.assertRaises(ExecutionEnvelopeStopped):
            emit_experimental_score(self.latch, self.root / "score.json")
        self.assertFalse((self.root / "b").exists())
        self.assertFalse((self.root / "score.json").exists())

    def test_stop_survives_reacquisition(self):
        self.latch.consume_terminal_stop()
        again = ExecutionStopLatch(self.store, self.envelope_id)
        self.assertEqual(again.state(), STOPPED)
        self.assertEqual(again.materialize_active()["state"], STOPPED)
        with self.assertRaises(ExecutionEnvelopeStopped):
            create_held_out_condition_root(again, self.root / "c")

    def test_receipt_allowed_while_stopped(self):
        self.latch.consume_terminal_stop()
        self.assertEqual(self.latch.receipt()["state"], STOPPED)


if __name__ == "__main__":
    unittest.main()
