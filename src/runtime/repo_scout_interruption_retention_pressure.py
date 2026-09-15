"""Synthetic interruption pressure for Repo Scout's pre-call evidence boundary.

No live model is contacted. One child process enters a synthetic client call,
durably marks that boundary, and terminates before Repo Scout can construct its
normal observation. A distinct investigator process then reads only the
retained journal and current repository fingerprint.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Mapping

from src.runtime.repo_scout import (
    APPARATUS_VERSION,
    OUTPUT_CONTRACT,
    _repository_state_fingerprint,
    canonical_json,
    run_repo_scout,
)


PRESSURE_VERSION = "repo_scout_interruption_retention_pressure_v0"
TRACE_PATH = Path("traces") / f"{PRESSURE_VERSION}.json"
SOURCE_PATH = (
    "docs/decisions/local_automation/"
    "turbo_t1_q1_completion_budget_pressure_result_v0.md"
)
QUESTION = (
    "Synthetic interruption-retention pressure. Use only the supplied source "
    "observation and return one candidate evidence packet under the exact "
    "model-proposal contract."
)
SYNTHETIC_INTERRUPTION_EXIT = 75


class SyntheticClientInterruption(BaseException):
    """Terminate the synthetic executor outside Repo Scout's Exception boundary."""


def make_invocation(
    repository_basis: str, *, source_path: str = SOURCE_PATH
) -> dict[str, Any]:
    return {
        "task_id": "repo-scout-synthetic-interruption-retention-v0",
        "repository_basis": repository_basis,
        "question": QUESTION,
        "allowed_paths": [source_path],
        "allowed_operations": ["git_show"],
        "inspection_plan": [
            {
                "operation": "git_show",
                "path": source_path,
                "start_line": 1,
                "end_line": 20,
            }
        ],
        "execution_budget": {
            "max_operations": 1,
            "max_operation_output_bytes": 16384,
            "max_model_response_bytes": 32768,
            "max_model_calls": 1,
            "wall_time_seconds": 30,
        },
        "realization_basis": {
            "identifier": "synthetic-client-interruption-v0",
            "runtime": "deterministic-no-live-model",
            "live_model": False,
        },
        "output_contract": deepcopy(OUTPUT_CONTRACT),
    }


def execute_synthetic_child(
    *, repo_root: Path, invocation: Mapping[str, Any], journal_path: Path
) -> None:
    """Enter one synthetic call after durably retaining the pre-call boundary."""

    expected_attempt_id: str | None = None

    def retain_pre_call(record: Mapping[str, Any]) -> None:
        nonlocal expected_attempt_id
        event = deepcopy(dict(record))
        event["event_index"] = 0
        expected_attempt_id = str(event["attempt_id"])
        _append_jsonl(journal_path, event)

    def interrupted_client(serialized_request: str, _timeout_seconds: float) -> str:
        request_sha256 = "sha256:" + hashlib.sha256(
            serialized_request.encode("utf-8")
        ).hexdigest()
        attempt_id = hashlib.sha256(
            (
                str(invocation["task_id"])
                + "\0"
                + str(invocation["repository_basis"])
                + "\0"
                + request_sha256
            ).encode("utf-8")
        ).hexdigest()
        if expected_attempt_id != attempt_id:
            raise RuntimeError("synthetic call marker does not match frozen attempt")
        _append_jsonl(
            journal_path,
            {
                "artifact": "repo_scout_synthetic_call_marker_v0",
                "event": "CALL_ENTERED",
                "event_index": 1,
                "attempt_id": attempt_id,
                "serialized_policy_visible_request_sha256": request_sha256,
                "consequence_attempted": True,
                "response_observed": False,
                "automatic_retry_authorized": False,
                "live_model_contacted": False,
            },
        )
        raise SyntheticClientInterruption(
            "synthetic client interrupted after call entry"
        )

    run_repo_scout(
        repo_root=repo_root,
        invocation=invocation,
        model_call=interrupted_client,
        attempt_recorder=retain_pre_call,
    )
    raise RuntimeError("synthetic interruption did not terminate Repo Scout")


def investigate_after_restart(
    *, repo_root: Path, journal_path: Path
) -> dict[str, Any]:
    """Reconstruct the bounded attempt state without invoking Repo Scout again."""

    events = _read_jsonl(journal_path)
    pre_call = events[0] if len(events) >= 1 else None
    call = events[1] if len(events) >= 2 else None
    pre_call_valid = bool(
        pre_call
        and pre_call.get("event") == "PRE_CALL_FROZEN"
        and pre_call.get("call_marker") == "NOT_YET_ENTERED"
    )
    call_valid = bool(
        call
        and call.get("event") == "CALL_ENTERED"
        and call.get("consequence_attempted") is True
        and call.get("response_observed") is False
        and call.get("automatic_retry_authorized") is False
    )
    association_valid = bool(
        pre_call_valid
        and call_valid
        and pre_call["attempt_id"] == call["attempt_id"]
        and pre_call["serialized_policy_visible_request_sha256"]
        == call["serialized_policy_visible_request_sha256"]
    )
    state_at_restart = _repository_state_fingerprint(repo_root.resolve(strict=True))
    fingerprints_conserved = bool(
        pre_call_valid
        and pre_call["repository_state_before"]
        == pre_call["repository_state_pre_call"]
        == state_at_restart
    )
    consequence_attempted = bool(call_valid and association_valid)
    return {
        "artifact": "repo_scout_interruption_restart_investigation_v0",
        "investigator_pid": os.getpid(),
        "journal_event_count": len(events),
        "pre_call_record_valid": pre_call_valid,
        "call_marker_valid": call_valid,
        "attempt_association_valid": association_valid,
        "operation_evidence_recoverable": bool(
            pre_call_valid and pre_call.get("operation_attempts")
        ),
        "serialized_request_recoverable": bool(
            pre_call_valid and pre_call.get("serialized_policy_visible_request")
        ),
        "fingerprints_recoverable": bool(
            pre_call_valid
            and pre_call.get("repository_state_before")
            and pre_call.get("repository_state_pre_call")
        ),
        "repository_fingerprints_conserved_at_restart": fingerprints_conserved,
        "consequence_attempted": consequence_attempted,
        "consequence_completed": "UNKNOWN",
        "response_observed": False,
        "model_call_attempts_reconstructed": 1 if consequence_attempted else 0,
        "automatic_second_invocation_admissible": False,
        "second_invocation_requires_separate_authorization": True,
        "non_admission_basis": (
            "A retained call-entry marker establishes an attempted consequence, "
            "but absence of a response does not establish that the consequence did "
            "not complete. Unknown outcome after attempt cannot authorize repetition."
        ),
        "repository_state_at_restart": state_at_restart,
        "investigation_is_read_only": True,
        "live_model_calls": 0,
    }


def run_pressure(
    *, repo_root: Path = Path("."), source_path: str = SOURCE_PATH
) -> dict[str, Any]:
    """Run the executor and restarted investigator as separate processes."""

    root = repo_root.resolve(strict=True)
    repository_basis = _git_head(root)
    invocation = make_invocation(repository_basis, source_path=source_path)
    state_before = _repository_state_fingerprint(root)
    started = perf_counter()
    project_root = Path(__file__).resolve().parents[2]

    with TemporaryDirectory() as temporary:
        directory = Path(temporary)
        invocation_path = directory / "synthetic_invocation.json"
        journal_path = directory / "attempt_journal.jsonl"
        invocation_path.write_text(
            json.dumps(invocation, indent=2, sort_keys=True), encoding="utf-8"
        )

        executor = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.runtime.repo_scout_interruption_retention_pressure",
                "_execute",
                str(root),
                str(invocation_path),
                str(journal_path),
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if executor.returncode != SYNTHETIC_INTERRUPTION_EXIT:
            raise RuntimeError(
                "synthetic executor did not stop at the declared interruption boundary: "
                f"{executor.returncode}: {executor.stderr.strip()}"
            )
        journal_before_restart = journal_path.read_bytes()
        journal_sha256_before_restart = hashlib.sha256(
            journal_before_restart
        ).hexdigest()

        investigator = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.runtime.repo_scout_interruption_retention_pressure",
                "_investigate",
                str(root),
                str(journal_path),
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        reconstruction = json.loads(investigator.stdout)
        journal_after_restart = journal_path.read_bytes()
        journal_sha256_after_restart = hashlib.sha256(
            journal_after_restart
        ).hexdigest()
        events = _read_jsonl(journal_path)

    state_after = _repository_state_fingerprint(root)
    checks = {
        "executor_stopped_at_synthetic_interruption": (
            executor.returncode == SYNTHETIC_INTERRUPTION_EXIT
        ),
        "pre_call_record_retained": len(events) == 2
        and events[0].get("event") == "PRE_CALL_FROZEN",
        "operation_evidence_retained": reconstruction[
            "operation_evidence_recoverable"
        ],
        "serialized_request_retained": reconstruction[
            "serialized_request_recoverable"
        ],
        "call_marker_retained": reconstruction["call_marker_valid"],
        "fingerprints_retained": reconstruction["fingerprints_recoverable"],
        "attempt_reconstructable_after_restart": reconstruction[
            "consequence_attempted"
        ],
        "outcome_not_invented": reconstruction["consequence_completed"]
        == "UNKNOWN",
        "second_invocation_not_automatically_admissible": not reconstruction[
            "automatic_second_invocation_admissible"
        ],
        "investigator_did_not_mutate_journal": (
            journal_sha256_before_restart == journal_sha256_after_restart
        ),
        "repository_fingerprint_conserved": state_before == state_after,
        "no_live_model_contact": reconstruction["live_model_calls"] == 0,
    }
    return {
        "artifact": PRESSURE_VERSION,
        "apparatus_version": APPARATUS_VERSION,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "repository_basis": repository_basis,
        "synthetic_invocation": invocation,
        "process_boundary": {
            "parent_pid": os.getpid(),
            "executor_pid": _pid_from_stdout(executor.stdout),
            "investigator_pid": reconstruction["investigator_pid"],
            "executor_return_code": executor.returncode,
            "executor_stderr": executor.stderr,
            "distinct_executor_and_investigator": (
                _pid_from_stdout(executor.stdout)
                != reconstruction["investigator_pid"]
            ),
        },
        "retained_journal_events": events,
        "journal_sha256_before_restart": journal_sha256_before_restart,
        "journal_sha256_after_restart": journal_sha256_after_restart,
        "restart_investigation": reconstruction,
        "checks": checks,
        "repository_state_before": state_before,
        "repository_state_after": state_after,
        "model_calls": {
            "live": 0,
            "synthetic_call_entries": 1,
            "automatic_retries": 0,
            "second_invocation": 0,
        },
        "bounded_result": (
            "The retained call-entry marker and its request association establish "
            "that the synthetic consequence boundary was attempted. No retained "
            "response establishes completion, so completion remains unknown and a "
            "second invocation is not automatically admissible."
        ),
        "distinctions": [
            "pre_call_frozen != consequence_attempted",
            "consequence_attempted != response_observed",
            "response_absent != consequence_not_completed",
            "unknown_outcome_after_attempt != authority_to_repeat",
        ],
        "scientific_standing": "NONE",
        "qualification_or_promotion": "NONE",
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as handle:
        handle.write(canonical_json(dict(value)).encode("utf-8") + b"\n")
        handle.flush()
        os.fsync(handle.fileno())


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _git_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="ascii",
    )
    return completed.stdout.strip()


def _pid_from_stdout(stdout: str) -> int:
    for line in stdout.splitlines():
        if line.startswith("executor_pid="):
            return int(line.split("=", 1)[1])
    raise RuntimeError("synthetic executor did not report its process identity")


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "_execute":
        root = Path(sys.argv[2])
        invocation = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
        journal = Path(sys.argv[4])
        print(f"executor_pid={os.getpid()}", flush=True)
        try:
            execute_synthetic_child(
                repo_root=root, invocation=invocation, journal_path=journal
            )
        except SyntheticClientInterruption:
            raise SystemExit(SYNTHETIC_INTERRUPTION_EXIT)
        raise SystemExit(1)
    if len(sys.argv) >= 2 and sys.argv[1] == "_investigate":
        report = investigate_after_restart(
            repo_root=Path(sys.argv[2]), journal_path=Path(sys.argv[3])
        )
        print(json.dumps(report, sort_keys=True))
        return

    report = run_pressure()
    TRACE_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
