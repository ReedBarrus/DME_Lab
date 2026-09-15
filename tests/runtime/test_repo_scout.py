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
        source_id = next(
            item["source_id"]
            for item in observed["issued_source_catalog"]
            if item["canonical_source_path"] == "note.txt"
        )
        proposal = {
            "evidence": [
                {
                    "source_id": source_id,
                    "location": "note.txt:1",
                    "observation": "The committed specimen contains bounded evidence.",
                }
            ],
            "bounded_interpretation": "The observation supports only this repository basis.",
            "unresolved": [],
            "escalation": {"required": False, "reason": None},
        }
        return json.dumps(proposal, separators=(",", ":"))


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
        proposal = mechanical["parsed_model_proposal"]
        attached = mechanical["parsed_result"]
        for field in (
            "task_id",
            "execution_basis",
            "scope_used",
            "operations_used",
            "terminal_action",
        ):
            self.assertNotIn(field, proposal)
        self.assertEqual(attached["task_id"], self.invocation()["task_id"])
        self.assertEqual(attached["execution_basis"], self.head)
        self.assertEqual(attached["scope_used"], [".", "note.txt"])
        self.assertEqual(
            attached["operations_used"],
            [item["operation"] for item in self.invocation()["inspection_plan"]],
        )
        self.assertEqual(attached["terminal_action"], "STOP")
        self.assertEqual(attached["evidence"][0]["source_path"], "note.txt")

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

    def test_model_cannot_regenerate_terminal_action(self) -> None:
        valid = json.loads(StubModel()(self.serialized_request(), 10))
        valid["terminal_action"] = "STOP"
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(json.dumps(valid)),
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertIn("exactly the model-owned fields", mechanical["response_error"])

    def test_model_cannot_regenerate_mechanical_envelope_fields(self) -> None:
        additions = {
            "task_id": "invented-task",
            "execution_basis": "0" * 40,
            "scope_used": ["invented.txt"],
            "operations_used": ["git_log"],
        }
        for field, value in additions.items():
            with self.subTest(field=field):
                proposal = json.loads(StubModel()(self.serialized_request(), 10))
                proposal[field] = value
                result = run_repo_scout(
                    repo_root=self.repo,
                    invocation=self.narrow_invocation(),
                    model_call=StubModel(json.dumps(proposal)),
                )
                mechanical = result["mechanical_evaluation"]
                self.assertEqual(mechanical["terminal_state"], "FAIL")
                self.assertIn(
                    "exactly the model-owned fields", mechanical["response_error"]
                )

    def test_unknown_source_id_is_rejected(self) -> None:
        valid = json.loads(StubModel()(self.serialized_request(), 10))
        valid["evidence"][0]["source_id"] = "source-9999"
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(json.dumps(valid)),
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertIn(
            "source_id was not issued",
            mechanical["response_error"],
        )

    def test_free_form_source_path_is_rejected(self) -> None:
        valid = json.loads(StubModel()(self.serialized_request(), 10))
        valid["evidence"][0]["source_path"] = "invented.txt"
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(json.dumps(valid)),
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "FAIL")
        self.assertIn("evidence[0]", mechanical["response_error"])

    def test_issued_source_id_resolves_to_canonical_path(self) -> None:
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(),
        )

        mechanical = result["mechanical_evaluation"]
        proposal = mechanical["parsed_model_proposal"]
        attached = mechanical["parsed_result"]
        self.assertEqual(proposal["evidence"][0]["source_id"], "source-0001")
        self.assertNotIn("source_path", proposal["evidence"][0])
        self.assertEqual(attached["evidence"][0]["source_path"], "note.txt")

    def test_escalation_required_derives_terminal_action(self) -> None:
        proposal = json.loads(StubModel()(self.serialized_request(), 10))
        proposal["escalation"] = {
            "required": True,
            "reason": "The supplied observation leaves a bounded residue.",
        }
        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=StubModel(json.dumps(proposal)),
        )

        mechanical = result["mechanical_evaluation"]
        self.assertEqual(mechanical["terminal_state"], "ESCALATED")
        self.assertEqual(
            mechanical["parsed_result"]["terminal_action"], "ESCALATE"
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

    def test_optional_attempt_recorder_receives_complete_pre_call_evidence(self) -> None:
        records: list[dict] = []
        model = StubModel()

        result = run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=model,
            attempt_recorder=lambda record: records.append(deepcopy(record)),
        )

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["event"], "PRE_CALL_FROZEN")
        self.assertEqual(record["call_marker"], "NOT_YET_ENTERED")
        self.assertEqual(record["automatic_retries_authorized"], 0)
        self.assertEqual(record["task_id"], self.narrow_invocation()["task_id"])
        self.assertEqual(record["execution_basis"]["resolved_commit"], self.head)
        self.assertEqual(record["operations_used"], ["git_show"])
        self.assertEqual(record["scope_used"], ["note.txt"])
        self.assertEqual(len(record["operation_attempts"]), 1)
        self.assertEqual(record["operation_attempts"][0]["return_code"], 0)
        self.assertIn("1:beta", record["operation_attempts"][0]["stdout"])
        self.assertEqual(
            record["serialized_policy_visible_request"],
            model.calls[0]["serialized_request"],
        )
        self.assertEqual(
            record["repository_state_before"],
            record["repository_state_pre_call"],
        )
        self.assertEqual(result["mechanical_evaluation"]["terminal_state"], "PASS")

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

    def test_model_contract_contains_only_transformation_fields(self) -> None:
        model = StubModel()
        run_repo_scout(
            repo_root=self.repo,
            invocation=self.narrow_invocation(),
            model_call=model,
        )
        request = model.calls[0]["request"]
        serialized = model.calls[0]["serialized_request"]
        contract = request["model_proposal_contract"]

        self.assertNotIn("result_contract", request)
        self.assertEqual(
            set(contract["properties"]),
            {"evidence", "bounded_interpretation", "unresolved", "escalation"},
        )
        for mechanical_field in (
            "task_id",
            "execution_basis",
            "scope_used",
            "operations_used",
            "terminal_action",
        ):
            self.assertNotIn(mechanical_field, contract["properties"])
        self.assertNotIn("non-empty string equal to the declared task_id", serialized)
        self.assertNotIn("canonical repository-relative path", serialized)
        self.assertNotIn(
            "exact apparatus-recorded operations in order", serialized
        )
        evidence_schema = contract["properties"]["evidence"]["items"]
        self.assertIn(
            "source-0001",
            evidence_schema["properties"]["source_id"]["enum"],
        )
        observation = request["observed_inspection"]["observations"][0]
        self.assertEqual(observation["source_ids"], ["source-0001"])
        self.assertNotIn("paths_accessed", observation)

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
