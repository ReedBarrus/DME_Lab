from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.runtime import basis_report as basis_report_module
from src.runtime.basis_report import (
    FETCH_FAILED,
    FETCH_NOT_REQUESTED,
    FETCH_SUCCEEDED,
    RELATION_CHECK_FAILED,
    RELATION_DIVERGED,
    RELATION_LOCAL_AHEAD,
    RELATION_LOCAL_BEHIND,
    RELATION_REMOTE_REF_ABSENT,
    RELATION_SYNCHRONIZED,
    WORKTREE_CLEAN,
    WORKTREE_DIRTY,
    basis_report,
)


def git(cwd: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


class BasisReportTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.remote = self.base / "remote.git"
        self.repo = self.base / "repo"
        git(self.base, "init", "--bare", str(self.remote))
        self.repo.mkdir()
        git(self.repo, "init", "--initial-branch=main")
        git(self.repo, "config", "user.email", "basis@example.invalid")
        git(self.repo, "config", "user.name", "Basis Report Test")
        (self.repo / "source.txt").write_text("alpha\n", encoding="utf-8")
        git(self.repo, "add", "source.txt")
        git(self.repo, "commit", "-m", "initial")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-u", "origin", "main")

    def clone_peer(self) -> Path:
        peer = self.base / "peer"
        git(self.base, "clone", "--branch", "main", str(self.remote), str(peer))
        git(peer, "config", "user.email", "peer@example.invalid")
        git(peer, "config", "user.name", "Basis Report Peer")
        return peer

    def commit(self, repo: Path, content: str, message: str) -> str:
        (repo / "source.txt").write_text(content, encoding="utf-8")
        git(repo, "add", "source.txt")
        git(repo, "commit", "-m", message)
        return git(repo, "rev-parse", "HEAD")

    def report(self, *, fetch: bool = False, branch: str = "main") -> dict:
        return basis_report(
            repository_root=self.repo,
            remote="origin",
            branch=branch,
            fetch=fetch,
        )

    def test_matching_basis_is_synchronized(self) -> None:
        result = self.report(fetch=False)

        self.assertEqual(result["relation"], RELATION_SYNCHRONIZED)
        self.assertEqual(result["local_head"], result["remote_head"])
        self.assertEqual(result["current_branch"], "main")
        self.assertEqual(result["worktree_state"]["status"], WORKTREE_CLEAN)
        self.assertFalse(result["fetch_attempted"])
        self.assertEqual(result["fetch_result"]["status"], FETCH_NOT_REQUESTED)
        self.assertEqual(result["observation_failures"], [])
        self.assertTrue(result["mechanical_basis_only"])
        self.assertFalse(result["integration_performed"])

    def test_remote_advance_is_local_behind_after_requested_fetch(self) -> None:
        peer = self.clone_peer()
        remote_head = self.commit(peer, "remote\n", "remote advance")
        git(peer, "push", "origin", "main")

        result = self.report(fetch=True)

        self.assertEqual(result["relation"], RELATION_LOCAL_BEHIND)
        self.assertEqual(result["remote_head"], remote_head)
        self.assertEqual(result["fetch_result"]["status"], FETCH_SUCCEEDED)

    def test_local_commit_is_local_ahead(self) -> None:
        local_head = self.commit(self.repo, "local\n", "local advance")

        result = self.report(fetch=False)

        self.assertEqual(result["relation"], RELATION_LOCAL_AHEAD)
        self.assertEqual(result["local_head"], local_head)

    def test_independent_commits_are_diverged(self) -> None:
        peer = self.clone_peer()
        self.commit(self.repo, "local\n", "local advance")
        self.commit(peer, "remote\n", "remote advance")
        git(peer, "push", "origin", "main")

        result = self.report(fetch=True)

        self.assertEqual(result["relation"], RELATION_DIVERGED)

    def test_dirty_state_preserves_tracked_and_untracked_entries(self) -> None:
        (self.repo / "source.txt").write_text("dirty\n", encoding="utf-8")
        (self.repo / "untracked.txt").write_text("new\n", encoding="utf-8")

        result = self.report(fetch=False)

        state = result["worktree_state"]
        self.assertEqual(state["status"], WORKTREE_DIRTY)
        self.assertTrue(state["tracked_changes"])
        self.assertTrue(state["untracked_changes"])
        self.assertTrue(any(entry.startswith(" M") for entry in state["entries"]))
        self.assertTrue(any(entry.startswith("??") for entry in state["entries"]))
        self.assertEqual(result["relation"], RELATION_SYNCHRONIZED)

    def test_absent_remote_ref_is_not_observation_failure(self) -> None:
        result = self.report(fetch=False, branch="absent")

        self.assertEqual(result["relation"], RELATION_REMOTE_REF_ABSENT)
        self.assertIsNone(result["remote_head"])
        self.assertEqual(result["observation_failures"], [])

    def test_fetch_failure_is_check_failed_not_remote_absence(self) -> None:
        git(self.repo, "remote", "set-url", "origin", str(self.base / "missing.git"))

        result = self.report(fetch=True)

        self.assertEqual(result["fetch_result"]["status"], FETCH_FAILED)
        self.assertEqual(result["relation"], RELATION_CHECK_FAILED)
        self.assertEqual(result["observation_failures"][0]["operation"], "fetch")

    def test_fetch_false_does_not_contact_invalid_remote(self) -> None:
        git(self.repo, "remote", "set-url", "origin", str(self.base / "missing.git"))

        result = self.report(fetch=False)

        self.assertEqual(result["relation"], RELATION_SYNCHRONIZED)
        self.assertEqual(result["fetch_result"]["status"], FETCH_NOT_REQUESTED)

    def test_report_does_not_mutate_worktree_head_branch_or_files(self) -> None:
        peer = self.clone_peer()
        self.commit(peer, "remote\n", "remote advance")
        git(peer, "push", "origin", "main")
        before_head = git(self.repo, "rev-parse", "HEAD")
        before_branch = git(self.repo, "branch", "--show-current")
        before_status = git(self.repo, "status", "--porcelain=v1")
        before_bytes = (self.repo / "source.txt").read_bytes()

        result = self.report(fetch=True)

        self.assertEqual(result["relation"], RELATION_LOCAL_BEHIND)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), before_head)
        self.assertEqual(git(self.repo, "branch", "--show-current"), before_branch)
        self.assertEqual(git(self.repo, "status", "--porcelain=v1"), before_status)
        self.assertEqual((self.repo / "source.txt").read_bytes(), before_bytes)
        self.assertFalse(result["integration_performed"])

    def test_requested_fetch_occurs_once_and_no_integration_command_runs(self) -> None:
        with patch.object(
            basis_report_module, "_git", wraps=basis_report_module._git
        ) as observed_git:
            result = self.report(fetch=True)

        commands = [call.args[1] for call in observed_git.call_args_list]
        self.assertEqual(commands.count("fetch"), 1)
        self.assertFalse(
            {
                "pull",
                "merge",
                "rebase",
                "checkout",
                "switch",
                "reset",
                "stash",
                "clean",
                "commit",
                "push",
            }.intersection(commands)
        )
        self.assertFalse(result["integration_performed"])


if __name__ == "__main__":
    unittest.main()
