from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from src.runtime.repo_scout import (
    OUTPUT_CONTRACT,
    PERMITTED_OPERATIONS,
    RepoScoutBasisError,
    RepoScoutBudgetError,
    RepoScoutOperationError,
    RepoScoutScopeError,
    run_repo_scout,
)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    return completed.stdout.strip()


class StubModel:
    def __init__(self, raw_response: str | None = None, *, mutate=None) -> None:
        self.raw_response = raw_response
        self.mutate = mutate
        self.calls: list[dict] = []

    def __call__(self, serialized_request: str, timeout_seconds: float) -> str:
        request = json.loads(serialized_request)
        self.calls.append(
            {
                "request": request,
                "serialized_request": serialized_request,
                "timeout_seconds": timeout_seconds,
            }
        )
        if self.mutate is not None:
            self.mutate()
        if self.raw_response is not None:
            return self.raw_response
        observed = request["observed_inspection"]
        result = {
            "task_id": request["task"]["task_id"],
            "execution_basis": request["task"]["repository_basis"],
            "evidence": [
                {
                    "source_path": "note.txt",
                    "location": "note.txt:1",
                    "observation": "The committed specimen contains bounded evidence.",
                }
            ],
            "bounded_interpretation": "The observation supports only this repository basis.",
            "unresolved": [],
            "scope_used": observed["scope_used"],
            "operations_used": observed["operations_used"],
            "escalation": {"required": False, "reason": None},
            "terminal_action": "STOP",
        }
        return json.dumps(result, separators=(",", ":"))


class RepoScoutTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        git(self.repo, "init")
        git(self.repo, "config", "user.email", "repo-scout@example.invalid")
        git(self.repo, "config", "user.name", "Repo Scout Test")
        (self.repo / "note.txt").write_text("alpha\nneedle one\n", encoding="utf-8")
        git(self.repo, "add", "note.txt")
        git(self.repo, "commit", "-m", "initial")
        self.first_commit = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "note.txt").write_text(
            "beta\nneedle two\nthird line\n", encoding="utf-8"
        )
        git(self.repo, "add", "note.txt")
        git(self.repo, "commit", "-m", "second")
        self.head = git(self.repo, "rev-parse", "HEAD")

    def invocation(self) -> dict:
        return {
            "task_id": "SCOUT-TEST-001",
            "repository_basis": self.head,
            "question": "What bounded evidence is present in note.txt?",
            "allowed_paths": [".", "note.txt"],
            "allowed_operations": list(PERMITTED_OPERATIONS),
            "inspection_plan": [
                {"operation": "git_status"},
                {"operation": "git_rev_parse", "ref": "HEAD"},
                {"operation": "git_log", "path": ".", "max_count": 2},
                {
                    "operation": "git_show",
                    "path": "note.txt",
                    "start_line": 1,
                    "end_line": 3,
                },
                {
                    "operation": "git_diff",
                    "from_commit": self.first_commit,
                    "path": "note.txt",
                },
                {
                    "operation": "git_grep",
                    "pattern": "needle",
                    "path": "note.txt",
                    "max_matches_per_file": 5,
                },
            ],
            "execution_budget": {
                "max_operations": 6,
                "max_operation_output_bytes": 100_000,
                "max_model_response_bytes": 20_000,
                "max_model_calls": 1,
                "wall_time_seconds": 30,
            },
            "realization_basis": {
                "identifier": "deterministic-stub-v0",
                "runtime": "unittest",
            },
            "output_contract": deepcopy(OUTPUT_CONTRACT),
        }

    def narrow_invocation(self) -> dict:
        value = self.invocation()
        value["allowed_paths"] = ["note.txt"]
        value["allowed_operations"] = ["git_show"]
        value["inspection_plan"] = [
            {
                "operation": "git_show",
                "path": "note.txt",
                "start_line": 1,
                "end_line": 3,
            }
        ]
        value["execution_budget"]["max_operations"] = 1
        return value

    def test_valid_bounded_repository_inspection_succeeds(self) -> None:
        model = StubModel()
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.invocation(),
            model_call=model,
        )

        observation = result["observation"]
        mechanical = result["mechanical_evaluation"]
        self.assertEqual(len(model.calls), 1)
        self.assertEqual(observation["model_calls"], 1)
        self.assertEqual(
            observation["operations_used"],
            [item["operation"] for item in self.invocation()["inspection_plan"]],
        )
        self.assertEqual(observation["scope_used"], [".", "note.txt"])
        self.assertEqual(mechanical["terminal_state"], "PASS")
        self.assertTrue(all(mechanical["mechanical_checks"].values()))
        self.assertEqual(mechanical["semantic_evaluation"], "NOT_PERFORMED")

    def test_stale_basis_is_rejected_before_worker_execution(self) -> None:
        invocation = self.narrow_invocation()
        invocation["repository_basis"] = self.first_commit
        model = StubModel()

        with self.assertRaisesRegex(RepoScoutBasisError, "current committed HEAD"):
            run_repo_scout(
                repo_root=self.repo,
                invocation=invocation,
                model_call=model,
            )
        self.assertEqual(model.calls, [])

    def test_out_of_scope_path_access_is_rejected(self) -> None:
        invocation = self.narrow_invocation()
        invocation["inspection_plan"][0]["path"] = "other.txt"
        model = StubModel()

        with self.assertRaisesRegex(RepoScoutScopeError, "outside allowed_paths"):
            run_repo_scout(
                repo_root=self.repo,
                invocation=invocation,
                model_call=model,
            )
        self.assertEqual(model.calls, [])

    def test_write_or_mutation_operation_is_rejected(self) -> None:
        for operation in ("write_file", "git_commit"):
            with self.subTest(operation=operation):
                invocation = self.narrow_invocation()
                invocation["allowed_operations"] = [operation]
                invocation["inspection_plan"] = [{"operation": operation}]
                model = StubModel()
                with self.assertRaisesRegex(
                    RepoScoutOperationError, "forbidden or unsupported"
                ):
                    run_repo_scout(
                        repo_root=self.repo,
                        invocation=invocation,
                        model_call=model,
                    )
                self.assertEqual(model.calls, [])

    def test_unsupported_git_or_network_operation_is_rejected(self) -> None:
        for operation in ("git_fetch", "network_get"):
            with self.subTest(operation=operation):
                invocation = self.narrow_invocation()
                invocation["allowed_operations"] = [operation]
                invocation["inspection_plan"] = [{"operation": operation}]
                model = StubModel()
                with self.assertRaisesRegex(
                    RepoScoutOperationError, "forbidden or unsupported"
                ):
                    run_repo_scout(
                        repo_root=self.repo,
                        invocation=invocation,
                        model_call=model,
                    )
                self.assertEqual(model.calls, [])

    def test_malformed_worker_response_remains_raw_and_fails(self) -> None:
        model = StubModel("not JSON and not repaired")
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=model,
        )

        self.assertEqual(
            result["observation"]["raw_model_response"],
            "not JSON and not repaired",
        )
        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertIsNone(mechanical["parsed_result"])
        self.assertFalse(mechanical["mechanical_checks"]["response_shape_valid"])

    def test_missing_terminal_action_fails_exact_contract(self) -> None:
        valid = json.loads(StubModel()(self.serialized_request(), 10))
        del valid["terminal_action"]
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(json.dumps(valid)),
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertIn("exactly the required fields", mechanical["response_error"])

    def test_recorded_operations_must_match_apparatus_operations(self) -> None:
        valid = json.loads(StubModel()(self.serialized_request(), 10))
        valid["operations_used"] = ["git_log"]
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(json.dumps(valid)),
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertFalse(
            mechanical["mechanical_checks"]["result_operations_match"]
        )

    def test_repository_state_remains_unchanged_across_read_only_run(self) -> None:
        before = git(self.repo, "status", "--porcelain=v1", "--untracked-files=all")
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(),
        )
        after = git(self.repo, "status", "--porcelain=v1", "--untracked-files=all")

        self.assertEqual(before, after)
        observation = result["observation"]
        self.assertEqual(
            observation["repository_state_before"],
            observation["repository_state_after"],
        )
        self.assertTrue(
            result["mechanical_evaluation"]["mechanical_checks"][
                "repository_state_unchanged"
            ]
        )

    def test_model_side_mutation_is_detected_and_not_accepted(self) -> None:
        changed = self.repo / "model-created.txt"
        model = StubModel(mutate=lambda: changed.write_text("mutation", encoding="utf-8"))
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=model,
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertFalse(
            mechanical["mechanical_checks"]["repository_state_unchanged"]
        )

    def test_operation_output_budget_rejects_before_model_call(self) -> None:
        invocation = self.narrow_invocation()
        invocation["execution_budget"]["max_operation_output_bytes"] = 1
        model = StubModel()
        with self.assertRaisesRegex(RepoScoutBudgetError, "operation output"):
            run_repo_scout(
                repo_root=self.repo,
                invocation=invocation,
                model_call=model,
            )
        self.assertEqual(model.calls, [])

    def test_model_receives_observations_without_tools_or_repository_handle(self) -> None:
        model = StubModel()
        run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=model,
        )
        request = model.calls[0]["request"]
        serialized = model.calls[0]["serialized_request"]

        self.assertEqual(request["authority"]["commit"], "NONE")
        self.assertNotIn("tools", request)
        self.assertNotIn("repo_root", serialized)
        self.assertNotIn(str(self.repo), serialized)
        self.assertIn("1:beta", serialized)

    def serialized_request(self) -> str:
        """Build the result echo basis used by malformed-result tests."""

        model = StubModel()
        run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=model,
        )
        return model.calls[0]["serialized_request"]


if __name__ == "__main__":
    unittest.main()
