"""Bounded read-only repository inspection apparatus for Repo Scout v0.

The caller declares the complete inspection plan. The scout has no planner,
shell, network surface, retry loop, repository write path, or acceptance
authority. One injected model call may transform retained read-only operation
observations into a strictly validated candidate evidence packet.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from time import monotonic
from typing import Any


APPARATUS_VERSION = "repo_scout_v0.2"
OUTPUT_CONTRACT = {"name": "repo_scout_result", "version": 0}
TERMINAL_ACTIONS = ("STOP", "ESCALATE")
PERMITTED_OPERATIONS = (
    "git_status",
    "git_log",
    "git_show",
    "git_diff",
    "git_grep",
    "git_rev_parse",
)
GIT_COMMAND_PREFIX = (
    "git",
    "--no-pager",
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.untrackedCache=false",
)
RESULT_FIELDS = (
    "task_id",
    "execution_basis",
    "evidence",
    "bounded_interpretation",
    "unresolved",
    "scope_used",
    "operations_used",
    "escalation",
    "terminal_action",
)
MODEL_PROPOSAL_FIELDS = (
    "evidence",
    "bounded_interpretation",
    "unresolved",
    "escalation",
)
INVOCATION_FIELDS = (
    "task_id",
    "repository_basis",
    "question",
    "allowed_paths",
    "allowed_operations",
    "inspection_plan",
    "execution_budget",
    "realization_basis",
    "output_contract",
)
EXECUTION_BUDGET_FIELDS = (
    "max_operations",
    "max_operation_output_bytes",
    "max_model_response_bytes",
    "max_model_calls",
    "wall_time_seconds",
)
_EXACT_COMMIT = re.compile(r"[0-9a-fA-F]{40}")


ModelCall = Callable[[str, float], str]
AttemptRecorder = Callable[[Mapping[str, Any]], None]


class RepoScoutError(RuntimeError):
    """Base class for a rejected scout invocation or operation."""


class RepoScoutContractError(RepoScoutError):
    """The declared invocation or model result violates its exact contract."""


class RepoScoutBasisError(RepoScoutError):
    """The declared repository basis is unresolved or not current HEAD."""


class RepoScoutScopeError(RepoScoutError):
    """An operation requests repository state outside declared scope."""


class RepoScoutOperationError(RepoScoutError):
    """An operation is forbidden, unsupported, or failed mechanically."""


class RepoScoutBudgetError(RepoScoutError):
    """A declared execution limit cannot admit the requested work."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def model_proposal_contract(source_ids: Sequence[str]) -> dict[str, Any]:
    """Return the exact schema for the model-owned transformation surface."""

    return {
        "type": "object",
        "required": list(MODEL_PROPOSAL_FIELDS),
        "additionalProperties": False,
        "properties": {
            "evidence": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["source_id", "location", "observation"],
                    "additionalProperties": False,
                    "properties": {
                        "source_id": {
                            "type": "string",
                            "enum": list(source_ids),
                        },
                        "location": {"type": "string", "minLength": 1},
                        "observation": {"type": "string", "minLength": 1},
                    },
                },
            },
            "bounded_interpretation": {"type": "string", "minLength": 1},
            "unresolved": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "escalation": {
                "type": "object",
                "required": ["required", "reason"],
                "additionalProperties": False,
                "properties": {
                    "required": {"type": "boolean"},
                    "reason": {"type": ["string", "null"]},
                },
            },
        },
    }


def parse_model_proposal(
    raw_model_response: str,
    *,
    issued_source_ids: Sequence[str],
) -> dict[str, Any]:
    """Parse model-owned content without prose extraction or repair."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise RepoScoutContractError(f"duplicate field {key!r}")
            value[key] = item
        return value

    try:
        parsed = json.loads(raw_model_response, object_pairs_hook=unique_object)
    except RepoScoutContractError:
        raise
    except (json.JSONDecodeError, TypeError) as exc:
        raise RepoScoutContractError(
            "model response is not one complete JSON value"
        ) from exc
    if type(parsed) is not dict:
        raise RepoScoutContractError("model response must be an object")
    if set(parsed) != set(MODEL_PROPOSAL_FIELDS):
        raise RepoScoutContractError(
            "model proposal must contain exactly the model-owned fields"
        )
    _require_nonempty_string(
        parsed["bounded_interpretation"], "bounded_interpretation"
    )
    _validate_string_list(parsed["unresolved"], "unresolved", allow_empty=True)
    evidence = parsed["evidence"]
    if type(evidence) is not list or not evidence:
        raise RepoScoutContractError("evidence must be a non-empty list")
    issued = set(issued_source_ids)
    for index, entry in enumerate(evidence):
        if type(entry) is not dict or set(entry) != {
            "source_id",
            "location",
            "observation",
        }:
            raise RepoScoutContractError(
                f"evidence[{index}] must contain exactly the required fields"
            )
        source_id = _require_nonempty_string(
            entry["source_id"], f"evidence[{index}].source_id"
        )
        if source_id not in issued:
            raise RepoScoutContractError(
                f"evidence[{index}].source_id was not issued by the apparatus"
            )
        _require_nonempty_string(entry["location"], f"evidence[{index}].location")
        _require_nonempty_string(
            entry["observation"], f"evidence[{index}].observation"
        )
    escalation = parsed["escalation"]
    if type(escalation) is not dict or set(escalation) != {"required", "reason"}:
        raise RepoScoutContractError(
            "escalation must contain exactly required and reason"
        )
    if type(escalation["required"]) is not bool:
        raise RepoScoutContractError("escalation.required must be boolean")
    reason = escalation["reason"]
    if escalation["required"]:
        _require_nonempty_string(reason, "escalation.reason")
    elif reason is not None:
        raise RepoScoutContractError(
            "escalation.reason must be null when escalation is not required"
        )
    return parsed


def _attach_mechanical_result(
    *,
    proposal: Mapping[str, Any],
    task_id: str,
    execution_basis: str,
    scope_used: Sequence[str],
    operations_used: Sequence[str],
    source_catalog: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Attach authoritative envelope fields and resolve selected source IDs."""

    path_by_id = {
        item["source_id"]: item["canonical_source_path"]
        for item in source_catalog
    }
    evidence = [
        {
            "source_path": path_by_id[item["source_id"]],
            "location": item["location"],
            "observation": item["observation"],
        }
        for item in proposal["evidence"]
    ]
    escalation = deepcopy(proposal["escalation"])
    terminal_action = "ESCALATE" if escalation["required"] else "STOP"
    return {
        "task_id": task_id,
        "execution_basis": execution_basis,
        "evidence": evidence,
        "bounded_interpretation": proposal["bounded_interpretation"],
        "unresolved": deepcopy(proposal["unresolved"]),
        "scope_used": list(scope_used),
        "operations_used": list(operations_used),
        "escalation": escalation,
        "terminal_action": terminal_action,
    }


def run_repo_scout(
    *,
    repo_root: Path,
    invocation: Mapping[str, Any],
    model_call: ModelCall,
    attempt_recorder: AttemptRecorder | None = None,
) -> dict[str, Any]:
    """Execute one declared read-only inspection plan and one model call.

    Invalid basis, scope, operations, or preflight budgets raise before the
    model is called. A returned but malformed model response is retained in the
    observation and rejected by the separate mechanical evaluation.
    """

    root = repo_root.resolve(strict=True)
    declared = _validate_invocation(invocation)
    execution_basis = _resolve_exact_commit(root, declared["repository_basis"])
    head_before = _resolve_exact_commit(root, "HEAD")
    if execution_basis != head_before:
        raise RepoScoutBasisError(
            "repository_basis must resolve to current committed HEAD before execution"
        )
    _validate_allowed_paths_exist(root, execution_basis, declared["allowed_paths"])
    validated_plan = _validate_plan(declared)

    budget = declared["execution_budget"]
    if len(validated_plan) > budget["max_operations"]:
        raise RepoScoutBudgetError("inspection plan exceeds max_operations")

    state_before = _repository_state_fingerprint(root)
    started = monotonic()
    attempts: list[dict[str, Any]] = []
    output_bytes_used = 0
    for index, request in enumerate(validated_plan):
        _require_time_remaining(started, budget["wall_time_seconds"])
        attempt = _execute_operation(
            root=root,
            basis=execution_basis,
            request=request,
            index=index,
        )
        output_bytes_used += len(attempt["stdout"].encode("utf-8"))
        if output_bytes_used > budget["max_operation_output_bytes"]:
            raise RepoScoutBudgetError(
                "operation output exceeds max_operation_output_bytes"
            )
        attempts.append(attempt)

    scope_used = _unique_in_order(
        path for attempt in attempts for path in attempt["paths_accessed"]
    )
    operations_used = [attempt["operation"] for attempt in attempts]
    source_catalog = _build_source_catalog(scope_used)
    policy_visible_request = _build_policy_visible_request(
        invocation=declared,
        execution_basis=execution_basis,
        attempts=attempts,
        scope_used=scope_used,
        operations_used=operations_used,
        source_catalog=source_catalog,
    )
    serialized_request = canonical_json(policy_visible_request)
    remaining = _remaining_seconds(started, budget["wall_time_seconds"])
    if remaining <= 0:
        raise RepoScoutBudgetError("wall_time_seconds exhausted before model call")

    if attempt_recorder is not None:
        state_pre_call = _repository_state_fingerprint(root)
        request_sha256 = "sha256:" + hashlib.sha256(
            serialized_request.encode("utf-8")
        ).hexdigest()
        attempt_id = hashlib.sha256(
            (
                declared["task_id"]
                + "\0"
                + execution_basis
                + "\0"
                + request_sha256
            ).encode("utf-8")
        ).hexdigest()
        attempt_recorder(
            {
                "artifact": "repo_scout_pre_call_record_v0",
                "apparatus_version": APPARATUS_VERSION,
                "event": "PRE_CALL_FROZEN",
                "attempt_id": attempt_id,
                "task_id": declared["task_id"],
                "declared_invocation": deepcopy(declared),
                "execution_basis": {
                    "declared": declared["repository_basis"],
                    "resolved_commit": execution_basis,
                    "head_before": head_before,
                },
                "operation_attempts": deepcopy(attempts),
                "issued_source_catalog": deepcopy(source_catalog),
                "scope_used": list(scope_used),
                "operations_used": list(operations_used),
                "operation_output_bytes": output_bytes_used,
                "serialized_policy_visible_request": serialized_request,
                "serialized_policy_visible_request_sha256": request_sha256,
                "repository_state_before": state_before,
                "repository_state_pre_call": state_pre_call,
                "call_marker": "NOT_YET_ENTERED",
                "automatic_retries_authorized": 0,
            }
        )
        remaining = _remaining_seconds(started, budget["wall_time_seconds"])
        if remaining <= 0:
            raise RepoScoutBudgetError(
                "wall_time_seconds exhausted during pre-call retention"
            )

    raw_model_response: str | None = None
    model_failure: str | None = None
    try:
        candidate_response = model_call(serialized_request, remaining)
        if type(candidate_response) is not str:
            raise TypeError("model_call must return a string")
        raw_model_response = candidate_response
    except Exception as exc:
        model_failure = f"{type(exc).__name__}: {exc}"
    model_calls = 1
    duration = monotonic() - started
    state_after = _repository_state_fingerprint(root)

    observation = {
        "artifact": "repo_scout_run_observation_v0",
        "apparatus_version": APPARATUS_VERSION,
        "task_id": declared["task_id"],
        "declared_invocation": deepcopy(declared),
        "execution_basis": {
            "declared": declared["repository_basis"],
            "resolved_commit": execution_basis,
            "head_before": head_before,
        },
        "realization_basis": deepcopy(declared["realization_basis"]),
        "operation_attempts": attempts,
        "issued_source_catalog": source_catalog,
        "scope_used": scope_used,
        "operations_used": operations_used,
        "operation_output_bytes": output_bytes_used,
        "serialized_policy_visible_request": serialized_request,
        "raw_model_response": raw_model_response,
        "model_failure": model_failure,
        "model_calls": model_calls,
        "execution_duration_seconds": duration,
        "repository_state_before": state_before,
        "repository_state_after": state_after,
        "semantic_evaluation": "NOT_PERFORMED",
    }
    mechanical = _mechanical_evaluation(
        observation=observation,
        execution_budget=budget,
        allowed_paths=declared["allowed_paths"],
        allowed_operations=declared["allowed_operations"],
    )
    return {"observation": observation, "mechanical_evaluation": mechanical}


def _validate_invocation(invocation: Mapping[str, Any]) -> dict[str, Any]:
    if type(invocation) is not dict:
        raise RepoScoutContractError("invocation must be an object")
    if set(invocation) != set(INVOCATION_FIELDS):
        raise RepoScoutContractError(
            "invocation must contain exactly the required fields"
        )
    value = deepcopy(invocation)
    task_id = _require_nonempty_string(value["task_id"], "task_id")
    if len(task_id) > 128:
        raise RepoScoutContractError("task_id exceeds 128 characters")
    basis = _require_nonempty_string(value["repository_basis"], "repository_basis")
    if not _EXACT_COMMIT.fullmatch(basis):
        raise RepoScoutBasisError("repository_basis must be a 40-character commit")
    question = _require_nonempty_string(value["question"], "question")
    if len(question) > 8000:
        raise RepoScoutContractError("question exceeds 8000 characters")

    allowed_paths = _validate_string_list(
        value["allowed_paths"], "allowed_paths", allow_empty=False
    )
    if len(allowed_paths) > 32 or len(set(allowed_paths)) != len(allowed_paths):
        raise RepoScoutScopeError("allowed_paths must be unique and contain at most 32 paths")
    value["allowed_paths"] = [
        _canonical_path(path, "allowed_paths entry") for path in allowed_paths
    ]

    allowed_operations = _validate_string_list(
        value["allowed_operations"], "allowed_operations", allow_empty=False
    )
    if len(set(allowed_operations)) != len(allowed_operations):
        raise RepoScoutOperationError("allowed_operations must be unique")
    forbidden = [item for item in allowed_operations if item not in PERMITTED_OPERATIONS]
    if forbidden:
        raise RepoScoutOperationError(
            f"forbidden or unsupported operation declared: {forbidden[0]}"
        )
    value["allowed_operations"] = allowed_operations

    if type(value["inspection_plan"]) is not list or not value["inspection_plan"]:
        raise RepoScoutContractError("inspection_plan must be a non-empty list")
    budget = value["execution_budget"]
    if type(budget) is not dict or set(budget) != set(EXECUTION_BUDGET_FIELDS):
        raise RepoScoutContractError(
            "execution_budget must contain exactly the required fields"
        )
    _bounded_int(budget["max_operations"], "max_operations", 1, 32)
    _bounded_int(
        budget["max_operation_output_bytes"],
        "max_operation_output_bytes",
        1,
        1_048_576,
    )
    _bounded_int(
        budget["max_model_response_bytes"],
        "max_model_response_bytes",
        1,
        262_144,
    )
    if budget["max_model_calls"] != 1 or type(budget["max_model_calls"]) is not int:
        raise RepoScoutBudgetError("Repo Scout v0 requires max_model_calls equal to 1")
    seconds = budget["wall_time_seconds"]
    if type(seconds) not in (int, float) or isinstance(seconds, bool) or not (0 < seconds <= 600):
        raise RepoScoutBudgetError("wall_time_seconds must be greater than 0 and at most 600")
    if type(value["realization_basis"]) is not dict:
        raise RepoScoutContractError("realization_basis must be an object")
    _require_nonempty_string(
        value["realization_basis"].get("identifier"),
        "realization_basis.identifier",
    )
    if value["output_contract"] != OUTPUT_CONTRACT:
        raise RepoScoutContractError("output_contract is not repo_scout_result v0")
    return value


def _validate_allowed_paths_exist(
    root: Path, basis: str, allowed_paths: Sequence[str]
) -> None:
    for path in allowed_paths:
        if path == ".":
            continue
        completed = _git(root, ["cat-file", "-e", f"{basis}:{path}"])
        if completed.returncode != 0:
            raise RepoScoutScopeError(
                f"allowed path does not exist at repository basis: {path}"
            )


def _validate_plan(invocation: Mapping[str, Any]) -> list[dict[str, Any]]:
    allowed_operations = invocation["allowed_operations"]
    allowed_paths = invocation["allowed_paths"]
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(invocation["inspection_plan"]):
        if type(raw) is not dict:
            raise RepoScoutContractError(f"inspection_plan[{index}] must be an object")
        operation = raw.get("operation")
        if operation not in PERMITTED_OPERATIONS:
            raise RepoScoutOperationError(
                f"forbidden or unsupported operation requested: {operation}"
            )
        if operation not in allowed_operations:
            raise RepoScoutOperationError(
                f"operation requested outside allowed_operations: {operation}"
            )
        request = deepcopy(raw)
        if operation in {"git_status", "git_rev_parse"}:
            _require_root_scope(allowed_paths, operation)
        if operation == "git_status":
            _require_exact_keys(request, {"operation"}, index)
        elif operation == "git_rev_parse":
            _require_exact_keys(request, {"operation", "ref"}, index)
            ref = _require_nonempty_string(request["ref"], "git_rev_parse.ref")
            if ref not in {"HEAD", invocation["repository_basis"]}:
                raise RepoScoutOperationError(
                    "git_rev_parse may inspect only HEAD or repository_basis"
                )
        elif operation == "git_log":
            _require_exact_keys(request, {"operation", "path", "max_count"}, index)
            request["path"] = _validate_request_path(request["path"], allowed_paths)
            _bounded_int(request["max_count"], "git_log.max_count", 1, 50)
        elif operation == "git_show":
            _require_exact_keys(
                request,
                {"operation", "path", "start_line", "end_line"},
                index,
            )
            request["path"] = _validate_request_path(request["path"], allowed_paths)
            if request["path"] == ".":
                raise RepoScoutOperationError("git_show requires a file path")
            start = _bounded_int(request["start_line"], "git_show.start_line", 1, 1_000_000)
            end = _bounded_int(request["end_line"], "git_show.end_line", start, 1_000_000)
            if end - start + 1 > 500:
                raise RepoScoutBudgetError("git_show may return at most 500 lines")
        elif operation == "git_diff":
            _require_exact_keys(
                request, {"operation", "from_commit", "path"}, index
            )
            if not isinstance(request["from_commit"], str) or not _EXACT_COMMIT.fullmatch(
                request["from_commit"]
            ):
                raise RepoScoutOperationError("git_diff.from_commit must be exact")
            request["path"] = _validate_request_path(request["path"], allowed_paths)
        elif operation == "git_grep":
            _require_exact_keys(
                request,
                {"operation", "pattern", "path", "max_matches_per_file"},
                index,
            )
            pattern = _require_nonempty_string(request["pattern"], "git_grep.pattern")
            if len(pattern) > 512 or "\x00" in pattern:
                raise RepoScoutOperationError("git_grep.pattern exceeds its boundary")
            request["path"] = _validate_request_path(request["path"], allowed_paths)
            _bounded_int(
                request["max_matches_per_file"],
                "git_grep.max_matches_per_file",
                1,
                20,
            )
        validated.append(request)
    return validated


def _execute_operation(
    *, root: Path, basis: str, request: Mapping[str, Any], index: int
) -> dict[str, Any]:
    operation = request["operation"]
    paths = [request.get("path", ".")]
    observation_basis = basis
    if operation == "git_status":
        args = ["status", "--porcelain=v1", "--untracked-files=all"]
        observation_basis = "execution_worktree"
    elif operation == "git_rev_parse":
        args = ["rev-parse", "--verify", f"{request['ref']}^{{commit}}"]
    elif operation == "git_log":
        args = [
            "log",
            "--format=%H%x09%aI%x09%s",
            f"--max-count={request['max_count']}",
            basis,
            "--",
            request["path"],
        ]
    elif operation == "git_show":
        args = ["show", f"{basis}:{request['path']}"]
    elif operation == "git_diff":
        _require_ancestor(root, request["from_commit"], basis)
        args = [
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--unified=3",
            request["from_commit"],
            basis,
            "--",
            request["path"],
        ]
        observation_basis = f"{request['from_commit']}..{basis}"
    elif operation == "git_grep":
        args = [
            "grep",
            "-n",
            "--full-name",
            "-F",
            "-m",
            str(request["max_matches_per_file"]),
            "-e",
            request["pattern"],
            basis,
            "--",
            request["path"],
        ]
    else:  # pragma: no cover - preflight makes this unreachable
        raise RepoScoutOperationError(f"unsupported operation: {operation}")

    completed = _git(root, args)
    acceptable = completed.returncode == 0 or (
        operation == "git_grep" and completed.returncode == 1
    )
    if not acceptable:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RepoScoutOperationError(f"{operation} failed: {detail}")
    try:
        stdout = completed.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RepoScoutOperationError(
            f"{operation} produced non-UTF-8 output"
        ) from exc
    if "\x00" in stdout:
        raise RepoScoutOperationError(f"{operation} produced binary output")
    if operation == "git_show":
        stdout = _numbered_line_slice(
            stdout, request["start_line"], request["end_line"]
        )
    return {
        "index": index,
        "operation": operation,
        "request": deepcopy(dict(request)),
        "command": [*GIT_COMMAND_PREFIX, *args],
        "paths_accessed": paths,
        "observation_basis": observation_basis,
        "return_code": completed.returncode,
        "stdout": stdout,
    }


def _build_source_catalog(scope_used: Sequence[str]) -> list[dict[str, str]]:
    return [
        {
            "source_id": f"source-{index:04d}",
            "canonical_source_path": path,
        }
        for index, path in enumerate(scope_used, start=1)
    ]


def _build_policy_visible_request(
    *,
    invocation: Mapping[str, Any],
    execution_basis: str,
    attempts: Sequence[Mapping[str, Any]],
    scope_used: Sequence[str],
    operations_used: Sequence[str],
    source_catalog: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    source_id_by_path = {
        item["canonical_source_path"]: item["source_id"]
        for item in source_catalog
    }
    observations = [
        {
            "index": attempt["index"],
            "operation": attempt["operation"],
            "source_ids": [
                source_id_by_path[path] for path in attempt["paths_accessed"]
            ],
            "observation_basis": attempt["observation_basis"],
            "stdout": attempt["stdout"],
        }
        for attempt in attempts
    ]
    return {
        "protocol": APPARATUS_VERSION,
        "task": {
            "task_id": invocation["task_id"],
            "repository_basis": execution_basis,
            "question": invocation["question"],
        },
        "authority": {
            "attempt": "DECLARED_READ_ONLY_INSPECTION_ONLY",
            "proposal": "CANDIDATE_EVIDENCE_PACKET_ONLY",
            "commit": "NONE",
            "acceptance": "EXTERNAL_CODEX_FRONTIER_HUMAN_REVIEW",
        },
        "declared_scope": {
            "allowed_paths": deepcopy(invocation["allowed_paths"]),
            "allowed_operations": deepcopy(invocation["allowed_operations"]),
        },
        "observed_inspection": {
            "scope_used": list(scope_used),
            "operations_used": list(operations_used),
            "issued_source_catalog": deepcopy(list(source_catalog)),
            "observations": observations,
        },
        "instructions": [
            "Use only the supplied repository observations.",
            "Keep observed evidence, bounded interpretation, and unresolved state distinct.",
            "Do not claim repository mutation, tool access, acceptance, scientific authority, or commit authority.",
            "For each evidence claim, select one source_id from issued_source_catalog; do not return a source path.",
            "Return exactly one object satisfying model_proposal_contract.",
            "Do not return task_id, execution_basis, scope_used, operations_used, or terminal_action; the apparatus owns those fields.",
            "Set escalation.required and escalation.reason consistently; the apparatus derives terminal_action.",
        ],
        "model_proposal_contract": model_proposal_contract(
            [item["source_id"] for item in source_catalog]
        ),
    }


def _mechanical_evaluation(
    *,
    observation: Mapping[str, Any],
    execution_budget: Mapping[str, Any],
    allowed_paths: Sequence[str],
    allowed_operations: Sequence[str],
) -> dict[str, Any]:
    raw = observation["raw_model_response"]
    response_received = type(raw) is str
    response_within_budget = response_received and (
        len(raw.encode("utf-8")) <= execution_budget["max_model_response_bytes"]
    )
    proposal: dict[str, Any] | None = None
    parsed_result: dict[str, Any] | None = None
    response_error: str | None = None
    if response_within_budget:
        try:
            source_catalog = observation["issued_source_catalog"]
            proposal = parse_model_proposal(
                raw,
                issued_source_ids=[item["source_id"] for item in source_catalog],
            )
            parsed_result = _attach_mechanical_result(
                proposal=proposal,
                task_id=observation["task_id"],
                execution_basis=observation["execution_basis"]["resolved_commit"],
                scope_used=observation["scope_used"],
                operations_used=observation["operations_used"],
                source_catalog=source_catalog,
            )
        except RepoScoutError as exc:
            response_error = f"{type(exc).__name__}: {exc}"
    elif not response_received:
        response_error = observation["model_failure"] or "model response missing"
    else:
        response_error = "RepoScoutBudgetError: model response exceeds max_model_response_bytes"

    attempts = observation["operation_attempts"]
    scope_used = observation["scope_used"]
    operations_used = observation["operations_used"]
    checks = {
        "execution_basis_valid": (
            observation["execution_basis"]["resolved_commit"]
            == observation["execution_basis"]["head_before"]
        ),
        "model_calls_exactly_one": observation["model_calls"] == 1,
        "operation_count_within_budget": (
            len(attempts) <= execution_budget["max_operations"]
        ),
        "operation_output_within_budget": (
            observation["operation_output_bytes"]
            <= execution_budget["max_operation_output_bytes"]
        ),
        "wall_time_within_budget": (
            observation["execution_duration_seconds"]
            <= execution_budget["wall_time_seconds"]
        ),
        "operations_permitted": all(
            operation in allowed_operations for operation in operations_used
        ),
        "paths_in_scope": all(
            _is_within_any_scope(path, allowed_paths) for path in scope_used
        ),
        "repository_state_unchanged": (
            observation["repository_state_before"]
            == observation["repository_state_after"]
        ),
        "model_response_received": response_received,
        "model_response_within_budget": response_within_budget,
        "response_shape_valid": proposal is not None,
        "model_owned_fields_only": proposal is not None
        and set(proposal) == set(MODEL_PROPOSAL_FIELDS),
        "evidence_source_ids_were_issued": proposal is not None,
        "final_result_fields_exact": parsed_result is not None
        and set(parsed_result) == set(RESULT_FIELDS),
        "result_task_attached": parsed_result is not None
        and parsed_result["task_id"] == observation["task_id"],
        "result_basis_attached": parsed_result is not None
        and parsed_result["execution_basis"]
        == observation["execution_basis"]["resolved_commit"],
        "result_scope_attached": parsed_result is not None
        and parsed_result["scope_used"] == scope_used,
        "result_operations_attached": parsed_result is not None
        and parsed_result["operations_used"] == operations_used,
        "terminal_action_derived": parsed_result is not None
        and parsed_result["terminal_action"]
        == ("ESCALATE" if proposal["escalation"]["required"] else "STOP"),
        "evidence_paths_were_accessed": parsed_result is not None
        and all(
            item["source_path"] in scope_used
            for item in parsed_result["evidence"]
        ),
    }
    if all(checks.values()):
        terminal_state = (
            "ESCALATED"
            if parsed_result["terminal_action"] == "ESCALATE"
            else "PASS"
        )
    else:
        terminal_state = "FAIL"
    return {
        "artifact": "repo_scout_mechanical_evaluation_v0",
        "apparatus_version": APPARATUS_VERSION,
        "task_id": observation["task_id"],
        "observation_sha256": "sha256:"
        + hashlib.sha256(canonical_json(observation).encode("utf-8")).hexdigest(),
        "parsed_model_proposal": proposal,
        "parsed_result": parsed_result,
        "response_error": response_error,
        "mechanical_checks": checks,
        "terminal_state": terminal_state,
        "semantic_evaluation": "NOT_PERFORMED",
        "acceptance_authority": "EXTERNAL_CODEX_FRONTIER_HUMAN_REVIEW",
    }


def _repository_state_fingerprint(root: Path) -> dict[str, str]:
    head = _resolve_exact_commit(root, "HEAD")
    status = _git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    diff = _git(root, ["diff", "--binary", "HEAD"])
    staged = _git(root, ["diff", "--cached", "--binary", "HEAD"])
    untracked = _git(root, ["ls-files", "--others", "--exclude-standard", "-z"])
    for name, completed in (("status", status), ("diff", diff), ("staged", staged), ("untracked", untracked)):
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()
            raise RepoScoutOperationError(f"cannot fingerprint repository {name}: {detail}")
    untracked_hashes: list[dict[str, str]] = []
    for encoded in untracked.stdout.split(b"\0"):
        if not encoded:
            continue
        relative = encoded.decode("utf-8")
        path = root / relative
        digest = "MISSING"
        if path.is_symlink():
            digest = "sha256:" + hashlib.sha256(
                os.readlink(path).encode("utf-8")
            ).hexdigest()
        elif path.is_file():
            digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        untracked_hashes.append({"path": relative, "sha256": digest})
    return {
        "head": head,
        "status_sha256": _sha256(status.stdout),
        "working_diff_sha256": _sha256(diff.stdout),
        "staged_diff_sha256": _sha256(staged.stdout),
        "untracked_manifest_sha256": _sha256(
            canonical_json(untracked_hashes).encode("utf-8")
        ),
    }


def _resolve_exact_commit(root: Path, ref: str) -> str:
    completed = _git(root, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RepoScoutBasisError(f"cannot resolve commit {ref!r}: {detail}")
    return completed.stdout.decode("ascii").strip()


def _require_ancestor(root: Path, ancestor: str, descendant: str) -> None:
    resolved = _resolve_exact_commit(root, ancestor)
    completed = _git(root, ["merge-base", "--is-ancestor", resolved, descendant])
    if completed.returncode != 0:
        raise RepoScoutOperationError(
            "git_diff.from_commit must be an ancestor of repository_basis"
        )


def _git(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["GIT_NO_LAZY_FETCH"] = "1"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    try:
        return subprocess.run(
            [*GIT_COMMAND_PREFIX, *args],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            shell=False,
            env=environment,
        )
    except OSError as exc:
        raise RepoScoutOperationError(f"cannot execute git: {type(exc).__name__}") from exc


def _canonical_path(value: Any, field: str) -> str:
    path = _require_nonempty_string(value, field)
    if path == ".":
        return path
    if "\\" in path or path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        raise RepoScoutScopeError(f"{field} must be canonical repository-relative POSIX path")
    pure = PurePosixPath(path)
    if any(part in {"", ".", "..", ".git"} for part in pure.parts):
        raise RepoScoutScopeError(f"{field} contains forbidden path components")
    canonical = pure.as_posix()
    if canonical != path or any(part.startswith("-") for part in pure.parts):
        raise RepoScoutScopeError(f"{field} is not canonical")
    return canonical


def _validate_request_path(value: Any, allowed_paths: Sequence[str]) -> str:
    path = _canonical_path(value, "operation path")
    if not _is_within_any_scope(path, allowed_paths):
        raise RepoScoutScopeError(f"operation path is outside allowed_paths: {path}")
    return path


def _is_within_any_scope(path: str, scopes: Sequence[str]) -> bool:
    return any(
        scope == "." or path == scope or path.startswith(scope.rstrip("/") + "/")
        for scope in scopes
    )


def _require_root_scope(allowed_paths: Sequence[str], operation: str) -> None:
    if "." not in allowed_paths:
        raise RepoScoutScopeError(f"{operation} requires explicit '.' repository scope")


def _require_exact_keys(
    request: Mapping[str, Any], expected: set[str], index: int
) -> None:
    if set(request) != expected:
        raise RepoScoutContractError(
            f"inspection_plan[{index}] has fields outside the {request.get('operation')} contract"
        )


def _require_nonempty_string(value: Any, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise RepoScoutContractError(f"{field} must be a non-empty string")
    return value


def _validate_string_list(value: Any, field: str, *, allow_empty: bool) -> list[str]:
    if type(value) is not list or (not allow_empty and not value):
        qualifier = "a list" if allow_empty else "a non-empty list"
        raise RepoScoutContractError(f"{field} must be {qualifier}")
    for item in value:
        _require_nonempty_string(item, f"{field} entry")
    return value


def _bounded_int(value: Any, field: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise RepoScoutBudgetError(
            f"{field} must be an integer from {minimum} through {maximum}"
        )
    return value


def _numbered_line_slice(text: str, start_line: int, end_line: int) -> str:
    lines = text.splitlines()
    selected = lines[start_line - 1 : end_line]
    return "\n".join(
        f"{line_number}:{line}"
        for line_number, line in enumerate(selected, start=start_line)
    )


def _unique_in_order(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _remaining_seconds(started: float, budget_seconds: float) -> float:
    return max(0.0, budget_seconds - (monotonic() - started))


def _require_time_remaining(started: float, budget_seconds: float) -> None:
    if _remaining_seconds(started, budget_seconds) <= 0:
        raise RepoScoutBudgetError("wall_time_seconds exhausted during inspection")


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()
