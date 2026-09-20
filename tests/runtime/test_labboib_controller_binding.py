from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest

from tools.goblin_pool import GoblinPool, GoblinPoolError
from tools.labboib_controller_binding import (
    AUTHORITY_REF,
    DECLARED_TEST_ID,
    EXPECTED_ARTIFACT_BLOBS,
    EXPECTED_CURSOR,
    SEAT_ID,
    bind_labboib,
    commit_runtime_successor,
    execute_read,
)


ROOT = Path(__file__).resolve().parents[2]


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
    ).strip()


class LabboibControllerBindingTest(unittest.TestCase):
    def make_pool(
        self,
        workspace: Path | None = None,
    ) -> tuple[TemporaryDirectory, GoblinPool]:
        temporary = TemporaryDirectory()
        db = Path(temporary.name) / "controller.sqlite3"
        pool = GoblinPool(db, workspace or ROOT)
        bind_labboib(pool, workspace or ROOT, "HEAD")
        return temporary, pool

    def test_b1_exact_labboib_basis_binds_without_identity_collapse(self) -> None:
        temporary, pool = self.make_pool()
        self.addCleanup(temporary.cleanup)

        seat = pool.seat_snapshot(SEAT_ID)

        self.assertEqual(seat["cursor_event_id"], EXPECTED_CURSOR)
        self.assertEqual(seat["state_version"], 0)
        self.assertEqual(seat["occupancy_state"], "AVAILABLE")
        self.assertEqual(
            seat["working_state"]["git_seat_basis"]["artifact_blobs"],
            EXPECTED_ARTIFACT_BLOBS,
        )
        self.assertEqual(
            seat["working_state"]["git_working_state"]["seat_id"],
            "LABBOIB",
        )
        self.assertEqual(pool.eligible_events(SEAT_ID), [])

        read = pool.operator_posture(SEAT_ID, "READ_REPO_STATE")
        test = pool.operator_posture(SEAT_ID, "RUN_DECLARED_TEST")
        write = pool.operator_posture(SEAT_ID, "WRITE_PACKET")

        self.assertTrue(read["eligible"])
        self.assertTrue(read["authorized"])
        self.assertEqual(read["authority_ref"], AUTHORITY_REF)

        self.assertTrue(test["eligible"])
        self.assertTrue(test["authorized"])
        self.assertEqual(test["authority_ref"], AUTHORITY_REF)

        self.assertTrue(write["registered"])
        self.assertTrue(write["available"])
        self.assertFalse(write["eligible"])
        self.assertFalse(write["authorized"])

    def test_b2_real_repo_read_is_nonmutating_and_commit_is_runtime_only(self) -> None:
        temporary, pool = self.make_pool()
        self.addCleanup(temporary.cleanup)

        git_cursor_path = ROOT / "continuity" / "cursors" / "labboib.json"
        git_state_path = (
            ROOT
            / "continuity"
            / "current_state"
            / "labboib_working_state_v0.json"
        )
        cursor_before = git_cursor_path.read_bytes()
        state_before = git_state_path.read_bytes()
        head_before = git(ROOT, "rev-parse", "HEAD")
        status_before = git(ROOT, "status", "--porcelain")

        wake = pool.start_wake(SEAT_ID, "W-B2")
        self.assertEqual(wake["status"], "STARTED")

        invocation = execute_read(
            pool,
            "W-B2",
            "OI-B2-READ",
            expected_repo_head=head_before,
        )

        self.assertEqual(invocation["status"], "EXECUTED")
        self.assertTrue(invocation["executed"])
        self.assertEqual(
            invocation["result"]["mutation_effect"],
            "NONE_BY_READ_REPO_STATE",
        )
        self.assertTrue(invocation["result"]["basis_stable_during_operator"])
        self.assertTrue(invocation["result"]["current_basis_applicability"])
        self.assertEqual(
            invocation["result"]["repo_head_at_start"],
            head_before,
        )

        committed = commit_runtime_successor(
            pool,
            "W-B2",
            transition_id="TR-B2",
            output_id="O-B2",
            summary="real repository state read completed",
            accepted_operator_invocation_ids=["OI-B2-READ"],
        )
        self.assertEqual(committed["status"], "COMMITTED")
        self.assertEqual(pool.seat_snapshot(SEAT_ID)["state_version"], 1)

        self.assertEqual(git(ROOT, "rev-parse", "HEAD"), head_before)
        self.assertEqual(git(ROOT, "status", "--porcelain"), status_before)
        self.assertEqual(git_cursor_path.read_bytes(), cursor_before)
        self.assertEqual(git_state_path.read_bytes(), state_before)

    def test_b3_b4_declared_test_ignores_caller_argv_and_adds_no_scientific_standing(self) -> None:
        temporary, pool = self.make_pool()
        self.addCleanup(temporary.cleanup)

        head = git(ROOT, "rev-parse", "HEAD")
        pool.start_wake(SEAT_ID, "W-B3")

        invocation = pool.execute_operator(
            "W-B3",
            "OI-B3-TEST",
            "RUN_DECLARED_TEST",
            {
                "test_id": DECLARED_TEST_ID,
                "expected_repo_head": head,
                "argv": [sys.executable, "-c", "raise SystemExit('ARBITRARY')"],
            },
        )

        result = invocation["result"]
        self.assertEqual(invocation["status"], "EXECUTED")
        self.assertEqual(result["mechanical_result"], "PASS")
        self.assertTrue(result["passed"])
        self.assertEqual(result["scientific_standing_effect"], "NONE")
        self.assertEqual(
            result["argv"][1:],
            [
                "-m",
                "unittest",
                "tests.runtime.test_labboib_temporal_seat",
                "-v",
            ],
        )
        self.assertNotIn("ARBITRARY", result["stdout"] + result["stderr"])
        self.assertTrue(result["current_basis_applicability"])

        committed = commit_runtime_successor(
            pool,
            "W-B3",
            transition_id="TR-B3",
            output_id="O-B3",
            summary="declared LABBOIB focused test completed",
            accepted_operator_invocation_ids=["OI-B3-TEST"],
        )
        self.assertEqual(committed["status"], "COMMITTED")

    def test_b5_write_packet_remains_ineligible_and_unexecuted(self) -> None:
        temporary, pool = self.make_pool()
        self.addCleanup(temporary.cleanup)

        pool.start_wake(SEAT_ID, "W-B5")
        result = pool.execute_operator(
            "W-B5",
            "OI-B5-WRITE",
            "WRITE_PACKET",
            {"packet": {"should": "not exist"}},
        )

        self.assertEqual(result["status"], "NOT_ELIGIBLE")
        self.assertFalse(result["executed"])
        self.assertFalse(
            (ROOT / ".goblin_pool_packets" / "OI-B5-WRITE.json").exists()
        )

    def test_b6_result_survives_repo_drift_but_successor_rejects_applicability(self) -> None:
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        clone = Path(temporary.name) / "workspace"

        subprocess.run(
            ["git", "clone", "--no-hardlinks", str(ROOT), str(clone)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        root_head = git(ROOT, "rev-parse", "HEAD")
        subprocess.run(
            ["git", "-C", str(clone), "checkout", "--detach", root_head],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        git(clone, "config", "user.name", "Binding Pressure")
        git(clone, "config", "user.email", "binding@example.invalid")

        db = Path(temporary.name) / "controller.sqlite3"
        pool = GoblinPool(db, clone)
        bind_labboib(pool, clone, "HEAD")

        started = Path(temporary.name) / "operator-started"
        release = Path(temporary.name) / "operator-release"
        wait_code = (
            "from pathlib import Path; import time, sys; "
            f"s=Path({str(started)!r}); r=Path({str(release)!r}); "
            "s.write_text('started'); "
            "\nfor _ in range(1000):"
            "\n    if r.exists(): break"
            "\n    time.sleep(0.01)"
            "\nelse: sys.exit(9)"
            "\nprint('DECLARED_TEST_COMPLETED')"
        )
        pool.register_declared_test(
            "STALE_ENV_WAIT",
            [sys.executable, "-c", wait_code],
        )

        h1 = git(clone, "rev-parse", "HEAD")
        pool.start_wake(SEAT_ID, "W-B6")

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                pool.execute_operator,
                "W-B6",
                "OI-B6-TEST",
                "RUN_DECLARED_TEST",
                {
                    "test_id": "STALE_ENV_WAIT",
                    "expected_repo_head": h1,
                },
            )

            for _ in range(500):
                if started.exists():
                    break
                time.sleep(0.01)
            self.assertTrue(started.exists())

            (clone / "basis_shift.txt").write_text("H2\n", encoding="utf-8")
            git(clone, "add", "basis_shift.txt")
            git(clone, "commit", "-m", "shift operator basis")
            h2 = git(clone, "rev-parse", "HEAD")
            self.assertNotEqual(h1, h2)

            release.write_text("release\n", encoding="utf-8")
            invocation = future.result(timeout=20)

        result = invocation["result"]
        self.assertEqual(invocation["status"], "EXECUTED")
        self.assertEqual(result["mechanical_result"], "PASS")
        self.assertEqual(result["repo_head_at_start"], h1)
        self.assertEqual(result["repo_head_at_return"], h2)
        self.assertFalse(result["basis_stable_during_operator"])
        self.assertFalse(result["current_basis_applicability"])

        with self.assertRaisesRegex(
            GoblinPoolError,
            "executed but is not applicable to the current repository basis",
        ):
            commit_runtime_successor(
                pool,
                "W-B6",
                transition_id="TR-B6",
                output_id="O-B6",
                summary="must not commit stale test result",
                accepted_operator_invocation_ids=["OI-B6-TEST"],
            )

        seat = pool.seat_snapshot(SEAT_ID)
        self.assertEqual(seat["state_version"], 0)
        self.assertEqual(seat["cursor_event_id"], EXPECTED_CURSOR)
        self.assertEqual(seat["occupancy_state"], "OCCUPIED")

        recovered = pool.recover_lease(SEAT_ID, "W-B6")
        self.assertEqual(recovered["status"], "RECOVERED")

    def test_b7_binding_is_idempotent_for_same_exact_basis(self) -> None:
        temporary, pool = self.make_pool()
        self.addCleanup(temporary.cleanup)

        again = bind_labboib(pool, ROOT, "HEAD")
        self.assertEqual(again["binding_status"], "ALREADY_BOUND")
        self.assertEqual(pool.seat_snapshot(SEAT_ID)["state_version"], 0)


if __name__ == "__main__":
    unittest.main()
