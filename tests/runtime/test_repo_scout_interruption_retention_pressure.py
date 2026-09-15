from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from src.runtime.repo_scout_interruption_retention_pressure import run_pressure


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


class RepoScoutInterruptionRetentionPressureTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        git(self.repo, "init")
        git(self.repo, "config", "user.email", "interruption@example.invalid")
        git(self.repo, "config", "user.name", "Interruption Pressure Test")
        (self.repo / "note.txt").write_text("retained source\n", encoding="utf-8")
        git(self.repo, "add", "note.txt")
        git(self.repo, "commit", "-m", "initial")
        self.report = run_pressure(repo_root=self.repo, source_path="note.txt")

    def test_synthetic_interruption_retains_pre_call_evidence(self) -> None:
        self.assertEqual(self.report["status"], "PASS")
        events = self.report["retained_journal_events"]
        self.assertEqual(
            [event["event"] for event in events],
            ["PRE_CALL_FROZEN", "CALL_ENTERED"],
        )
        pre_call = events[0]
        self.assertEqual(pre_call["operations_used"], ["git_show"])
        self.assertEqual(pre_call["scope_used"], ["note.txt"])
        self.assertEqual(len(pre_call["operation_attempts"]), 1)
        self.assertIn(
            "1:retained source", pre_call["operation_attempts"][0]["stdout"]
        )
        self.assertTrue(pre_call["serialized_policy_visible_request"])
        self.assertEqual(
            pre_call["repository_state_before"],
            pre_call["repository_state_pre_call"],
        )

    def test_fresh_investigator_reconstructs_attempt_without_inventing_completion(
        self,
    ) -> None:
        process = self.report["process_boundary"]
        self.assertTrue(process["distinct_executor_and_investigator"])
        self.assertNotEqual(process["parent_pid"], process["executor_pid"])
        self.assertNotEqual(process["parent_pid"], process["investigator_pid"])
        reconstruction = self.report["restart_investigation"]
        self.assertTrue(reconstruction["consequence_attempted"])
        self.assertEqual(reconstruction["consequence_completed"], "UNKNOWN")
        self.assertFalse(reconstruction["response_observed"])
        self.assertEqual(reconstruction["model_call_attempts_reconstructed"], 1)

    def test_restart_does_not_admit_or_execute_second_invocation(self) -> None:
        reconstruction = self.report["restart_investigation"]
        self.assertFalse(reconstruction["automatic_second_invocation_admissible"])
        self.assertTrue(
            reconstruction["second_invocation_requires_separate_authorization"]
        )
        self.assertEqual(self.report["model_calls"]["second_invocation"], 0)
        self.assertEqual(self.report["model_calls"]["automatic_retries"], 0)
        self.assertEqual(
            self.report["journal_sha256_before_restart"],
            self.report["journal_sha256_after_restart"],
        )

    def test_pressure_uses_no_live_model_and_preserves_repository(self) -> None:
        self.assertEqual(self.report["model_calls"]["live"], 0)
        self.assertEqual(self.report["model_calls"]["synthetic_call_entries"], 1)
        self.assertTrue(self.report["checks"]["no_live_model_contact"])
        self.assertEqual(
            self.report["repository_state_before"],
            self.report["repository_state_after"],
        )


if __name__ == "__main__":
    unittest.main()
