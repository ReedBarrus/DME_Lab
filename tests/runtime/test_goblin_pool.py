from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from tools.goblin_pool import GoblinPool, GoblinPoolError, InjectedCrash


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
    ).strip()


class GoblinPoolPressureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        git(self.workspace, "init")
        git(self.workspace, "config", "user.name", "Goblin Test")
        git(self.workspace, "config", "user.email", "goblin@example.invalid")
        (self.workspace / "README.md").write_text("fixture\n", encoding="utf-8")
        git(self.workspace, "add", ".")
        git(self.workspace, "commit", "-m", "fixture")

        self.db = self.root / "goblin.sqlite3"
        self.pool = GoblinPool(self.db, self.workspace)
        self.pool.initialize_fixture()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def commit_simple(
        self,
        wake_id: str,
        *,
        transition_id: str,
        output_id: str,
        seat_id: str,
        consumed: list[str] | None = None,
        invocations: list[str] | None = None,
        counter: int = 1,
        inject_failure: bool = False,
    ) -> dict[str, object]:
        return self.pool.commit_transition(
            wake_id,
            transition_id=transition_id,
            output_id=output_id,
            output_kind="STATUS",
            output_payload={"seat_id": seat_id, "counter": counter},
            consumed_event_ids=list(consumed or []),
            resulting_working_state={
                "seat_id": seat_id,
                "counter": counter,
                "mode": "ACTIVE",
            },
            accepted_operator_invocation_ids=list(invocations or []),
            inject_failure_before_commit=inject_failure,
        )

    def test_p1_simultaneous_different_seat_wakes_are_independent(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(self.pool.start_wake, "GOB_A", "W-P1-A")
            b = pool.submit(self.pool.start_wake, "GOB_B", "W-P1-B")
            results = [a.result(), b.result()]

        self.assertEqual({result["status"] for result in results}, {"STARTED"})
        seat_a = self.pool.seat_snapshot("GOB_A")
        seat_b = self.pool.seat_snapshot("GOB_B")
        seat_c = self.pool.seat_snapshot("GOB_C")

        self.assertEqual(seat_a["current_wake_id"], "W-P1-A")
        self.assertEqual(seat_b["current_wake_id"], "W-P1-B")
        self.assertEqual(seat_c["occupancy_state"], "AVAILABLE")
        self.assertEqual(seat_a["working_state"]["seat_id"], "GOB_A")
        self.assertEqual(seat_b["working_state"]["seat_id"], "GOB_B")

    def test_p2_same_seat_overlap_yields_one_started_and_one_conflict(self) -> None:
        with ThreadPoolExecutor(max_workers=2) as pool:
            one = pool.submit(self.pool.start_wake, "GOB_A", "W-P2-1")
            two = pool.submit(self.pool.start_wake, "GOB_A", "W-P2-2")
            results = [one.result(), two.result()]

        statuses = sorted(result["status"] for result in results)
        self.assertEqual(statuses, ["OCCUPANCY_CONFLICT", "STARTED"])

        seat = self.pool.seat_snapshot("GOB_A")
        started = next(result for result in results if result["status"] == "STARTED")
        self.assertEqual(seat["occupancy_state"], "OCCUPIED")
        self.assertEqual(seat["current_wake_id"], started["wake_id"])

    def test_p3_stale_submission_rejected_after_new_successor_commits(self) -> None:
        first = self.pool.start_wake("GOB_A", "W-P3-OLD")
        self.assertEqual(first["basis_version"], 0)
        self.pool.recover_lease("GOB_A", "W-P3-OLD", reason="LEASE_EXPIRED")

        second = self.pool.start_wake("GOB_A", "W-P3-NEW")
        self.assertEqual(second["basis_version"], 0)
        committed = self.commit_simple(
            "W-P3-NEW",
            transition_id="TR-P3-NEW",
            output_id="O-P3-NEW",
            seat_id="GOB_A",
        )
        self.assertEqual(committed["status"], "COMMITTED")
        self.assertEqual(self.pool.seat_snapshot("GOB_A")["state_version"], 1)

        stale = self.commit_simple(
            "W-P3-OLD",
            transition_id="TR-P3-OLD",
            output_id="O-P3-OLD",
            seat_id="GOB_A",
        )
        self.assertEqual(stale["status"], "STALE_BASIS")
        self.assertFalse(stale["accepted"])
        self.assertEqual(self.pool.counts()["outputs"], 1)
        self.assertEqual(self.pool.seat_snapshot("GOB_A")["state_version"], 1)

    def test_p4_duplicate_output_identity_has_one_durable_consequence(self) -> None:
        self.pool.start_wake("GOB_A", "W-P4-1")
        first = self.commit_simple(
            "W-P4-1",
            transition_id="TR-P4-1",
            output_id="O-P4-DUP",
            seat_id="GOB_A",
        )
        self.assertEqual(first["status"], "COMMITTED")

        self.pool.start_wake("GOB_A", "W-P4-2")
        with self.assertRaisesRegex(GoblinPoolError, "duplicate output_id"):
            self.commit_simple(
                "W-P4-2",
                transition_id="TR-P4-2",
                output_id="O-P4-DUP",
                seat_id="GOB_A",
                counter=2,
            )

        self.assertEqual(self.pool.counts()["outputs"], 1)
        self.assertEqual(self.pool.counts()["transitions"], 1)
        self.assertEqual(self.pool.seat_snapshot("GOB_A")["state_version"], 1)

    def test_p5_deterministic_only_wake_executes_without_semantic_request(self) -> None:
        self.pool.start_wake("GOB_B", "W-P5")
        posture = self.pool.operator_posture("GOB_B", "RUN_DECLARED_TEST")
        self.assertEqual(
            {
                "registered": posture["registered"],
                "available": posture["available"],
                "eligible": posture["eligible"],
                "authorized": posture["authorized"],
            },
            {
                "registered": True,
                "available": True,
                "eligible": True,
                "authorized": True,
            },
        )

        invocation = self.pool.execute_operator(
            "W-P5",
            "OI-P5-TEST",
            "RUN_DECLARED_TEST",
            {"test_id": "SMOKE_TRUE"},
        )
        self.assertEqual(invocation["status"], "EXECUTED")
        self.assertTrue(invocation["result"]["passed"])
        self.assertIn("GOBLIN_DECLARED_TEST_PASS", invocation["result"]["stdout"])

        committed = self.commit_simple(
            "W-P5",
            transition_id="TR-P5",
            output_id="O-P5",
            seat_id="GOB_B",
            invocations=["OI-P5-TEST"],
        )
        self.assertEqual(committed["status"], "COMMITTED")
        self.assertEqual(self.pool.counts()["semantic_requests"], 0)

    def test_p6_semantic_escalation_proposal_cannot_mutate_seat(self) -> None:
        self.pool.start_wake("GOB_A", "W-P6")
        before = self.pool.seat_snapshot("GOB_A")

        request = self.pool.emit_semantic_request(
            "W-P6",
            "SR-P6",
            "Novel fracture: propose one bounded candidate repair.",
        )
        proposal = self.pool.submit_semantic_proposal(
            "SR-P6",
            "SP-P6",
            {
                "candidate_operator": "WRITE_PACKET",
                "claim": "proposal only",
            },
        )

        after = self.pool.seat_snapshot("GOB_A")
        self.assertEqual(request["status"], "PENDING")
        self.assertEqual(proposal["status"], "PROPOSAL_RECEIVED")
        self.assertFalse(request["seat_state_changed"])
        self.assertFalse(proposal["seat_state_changed"])
        self.assertEqual(after["state_version"], before["state_version"])
        self.assertEqual(after["cursor_event_id"], before["cursor_event_id"])
        self.assertEqual(after["working_state"], before["working_state"])

    def test_p7_authority_stop_emits_request_and_does_not_execute(self) -> None:
        self.pool.start_wake("GOB_C", "W-P7")
        posture = self.pool.operator_posture("GOB_C", "WRITE_PACKET")
        self.assertTrue(posture["registered"])
        self.assertTrue(posture["available"])
        self.assertTrue(posture["eligible"])
        self.assertFalse(posture["authorized"])

        result = self.pool.execute_operator(
            "W-P7",
            "OI-P7-WRITE",
            "WRITE_PACKET",
            {"packet": {"hello": "goblin"}},
        )

        self.assertEqual(result["status"], "AUTHORITY_REQUIRED")
        self.assertFalse(result["executed"])
        self.assertEqual(self.pool.counts()["action_requests"], 1)
        packet_path = self.workspace / ".goblin_pool_packets" / "OI-P7-WRITE.json"
        self.assertFalse(packet_path.exists())

    def test_p8_crash_before_commit_rolls_back_successor_and_lease_recovers(self) -> None:
        self.pool.start_wake("GOB_A", "W-P8")
        before = self.pool.seat_snapshot("GOB_A")
        counts_before = self.pool.counts()

        with self.assertRaisesRegex(InjectedCrash, "synthetic controller crash"):
            self.commit_simple(
                "W-P8",
                transition_id="TR-P8",
                output_id="O-P8",
                seat_id="GOB_A",
                counter=8,
                inject_failure=True,
            )

        after_crash = self.pool.seat_snapshot("GOB_A")
        counts_after = self.pool.counts()
        self.assertEqual(after_crash["state_version"], before["state_version"])
        self.assertEqual(after_crash["cursor_event_id"], before["cursor_event_id"])
        self.assertEqual(after_crash["working_state"], before["working_state"])
        self.assertEqual(counts_after["outputs"], counts_before["outputs"])
        self.assertEqual(counts_after["transitions"], counts_before["transitions"])
        self.assertEqual(after_crash["occupancy_state"], "OCCUPIED")

        recovered = self.pool.recover_lease("GOB_A", "W-P8")
        self.assertEqual(recovered["status"], "RECOVERED")
        final = self.pool.seat_snapshot("GOB_A")
        self.assertEqual(final["occupancy_state"], "AVAILABLE")
        self.assertIsNone(final["current_wake_id"])

    def test_p9_retry_after_commit_is_idempotent_not_duplicate_consequence(self) -> None:
        self.pool.start_wake("GOB_A", "W-P9")
        first = self.commit_simple(
            "W-P9",
            transition_id="TR-P9",
            output_id="O-P9",
            seat_id="GOB_A",
            counter=9,
        )

        retry = self.commit_simple(
            "W-P9",
            transition_id="TR-P9",
            output_id="O-P9",
            seat_id="GOB_A",
            counter=9,
        )

        self.assertEqual(first["status"], "COMMITTED")
        self.assertEqual(retry["status"], "ALREADY_COMMITTED")
        self.assertTrue(retry["idempotent_replay"])
        self.assertEqual(self.pool.counts()["outputs"], 1)
        self.assertEqual(self.pool.counts()["transitions"], 1)
        self.assertEqual(self.pool.seat_snapshot("GOB_A")["state_version"], 1)

    def test_operator_layers_do_not_collapse(self) -> None:
        posture = self.pool.operator_posture("GOB_B", "RUN_DECLARED_TEST")
        self.assertTrue(posture["registered"])
        self.assertTrue(posture["available"])
        self.assertTrue(posture["eligible"])
        self.assertTrue(posture["authorized"])

        self.pool.set_operator_availability("RUN_DECLARED_TEST", False)
        unavailable = self.pool.operator_posture("GOB_B", "RUN_DECLARED_TEST")
        self.assertTrue(unavailable["registered"])
        self.assertFalse(unavailable["available"])
        self.assertFalse(unavailable["eligible"])
        self.assertFalse(unavailable["authorized"])

        unknown = self.pool.operator_posture("GOB_B", "NOT_AN_OPERATOR")
        self.assertFalse(unknown["registered"])
        self.assertFalse(unknown["available"])
        self.assertFalse(unknown["eligible"])
        self.assertFalse(unknown["authorized"])

    def test_cursor_and_working_state_commit_as_one_transition(self) -> None:
        self.pool.append_event(
            "EV-000002",
            seat_id="GOB_A",
            event_kind="TASK",
            payload={"task": "A"},
        )
        self.pool.append_event(
            "EV-000003",
            seat_id="GOB_B",
            event_kind="TASK",
            payload={"task": "B"},
        )

        self.assertEqual(
            [event["event_id"] for event in self.pool.eligible_events("GOB_A")],
            ["EV-000002"],
        )
        self.assertEqual(
            [event["event_id"] for event in self.pool.eligible_events("GOB_B")],
            ["EV-000003"],
        )

        self.pool.start_wake("GOB_A", "W-TX")
        receipt = self.commit_simple(
            "W-TX",
            transition_id="TR-TX",
            output_id="O-TX",
            seat_id="GOB_A",
            consumed=["EV-000002"],
            counter=42,
        )

        seat = self.pool.seat_snapshot("GOB_A")
        self.assertEqual(receipt["prior_cursor_event_id"], "EV-000001")
        self.assertEqual(receipt["resulting_cursor_event_id"], "EV-000002")
        self.assertEqual(receipt["resulting_version"], 1)
        self.assertEqual(seat["cursor_event_id"], "EV-000002")
        self.assertEqual(seat["working_state"]["counter"], 42)
        self.assertEqual(seat["state_version"], 1)
        self.assertEqual(seat["occupancy_state"], "AVAILABLE")


if __name__ == "__main__":
    unittest.main()
