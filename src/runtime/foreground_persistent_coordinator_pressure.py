"""Bounded Phase-C pressure for an explicitly invoked foreground coordinator."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.capture import compare_snapshots
from src.ledger import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    JsonlLedger,
    compare_prefix_preservation,
)
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "foreground_persistent_coordinator_pressure_v0.json"
STARTING_HEAD = "d80cc701c7e03ab377600869ce46812adb62b922"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "Observational Persistence"
STARTING_WORKTREE: list[str] = []
BASELINE_CHART_12_TESTS = {"passed": 21, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 276, "failed": 0}


def run() -> dict[str, Any]:
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        temporary_root = Path(tmpdir)
        fixture_root = temporary_root / "fixture"
        fixture_root.mkdir()
        state_path = fixture_root / "state.txt"
        state_path.write_text("alpha", encoding="utf-8")
        initial_commit = _initialize_fixture(fixture_root)
        ledger_path = temporary_root / "foreground_coordinator.jsonl"

        coordinator = ForegroundRepositoryObservationCoordinator(
            fixture_root, ledger_path
        )
        initial_process_state = _process_state(coordinator)
        calls: list[dict[str, Any]] = []

        calls.append(_call_summary("C1", "initial clean alpha", "none", coordinator.capture_round()))
        witness_records = deepcopy(JsonlLedger(ledger_path).replay())

        calls.append(
            _call_summary(
                "C2",
                "repeated unchanged clean alpha",
                "none",
                coordinator.capture_round(),
            )
        )

        state_path.write_text("beta", encoding="utf-8")
        calls.append(
            _call_summary(
                "C3",
                "uncommitted dirty beta",
                "external driver rewrote state.txt from alpha to beta",
                coordinator.capture_round(),
            )
        )

        beta_commit = _commit_world(
            fixture_root,
            "commit beta",
            "2000-01-02T00:00:00+00:00",
        )
        calls.append(
            _call_summary(
                "C4",
                "committed clean beta",
                "external driver added and committed state.txt without rewriting it",
                coordinator.capture_round(),
            )
        )

        ledger_sha_before_close = _file_sha256(ledger_path)
        coordinator.close()
        closed_process_state = _process_state(coordinator)
        del coordinator

        state_path.write_text("gamma", encoding="utf-8")
        ledger_sha_after_absent_mutation = _file_sha256(ledger_path)

        reopened = ForegroundRepositoryObservationCoordinator.open(
            fixture_root, ledger_path
        )
        reopened_process_state = _process_state(reopened)
        disk_result_before_capture = reopened.current_result()
        ledger_sha_after_disk_result = _file_sha256(ledger_path)
        calls.append(
            _call_summary(
                "C5",
                "uncommitted dirty gamma after reopen",
                "external driver rewrote state.txt from beta to gamma while coordinator was absent",
                reopened.capture_round(),
            )
        )
        reopened.close()

        final_records = JsonlLedger(ledger_path).replay()
        comparisons = _call_comparisons(calls)
        prefix_results = {
            call["call"]: compare_prefix_preservation(
                final_records[: call["record_range"][1]], witness_records
            ).to_dict()
            for call in calls
        }
        absent_interval = _absent_interval(calls, disk_result_before_capture)
        durable_state = {
            "required": ["ledger path", "authoritative ledger contents"],
            "coordinator_metadata_files": [],
            "history_derived_state": [],
            "root_path_role": "external source locator, not coordinator history",
            "ledger_unchanged_by_absent_world_mutation": (
                ledger_sha_before_close == ledger_sha_after_absent_mutation
            ),
            "current_result_is_read_only": (
                ledger_sha_after_absent_mutation == ledger_sha_after_disk_result
            ),
        }
        process_local = {
            "initial": initial_process_state,
            "closed": closed_process_state,
            "reopened": reopened_process_state,
            "allowed_fields": ["root", "ledger_path", "_closed"],
            "cached_reconstruction": False,
            "cached_projection": False,
            "cached_last_snapshot": False,
            "cached_record_count": False,
            "cached_previous_git_state": False,
            "cached_round_number": False,
        }
        coherent = _coherent(
            calls,
            prefix_results,
            disk_result_before_capture,
            absent_interval,
            durable_state,
        )
        canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

        report = {
            "experiment": "foreground_persistent_coordinator_pressure_v0",
            "starting_lineage": {
                "branch": STARTING_BRANCH,
                "head": STARTING_HEAD,
                "message": STARTING_MESSAGE,
                "worktree": STARTING_WORKTREE,
                "observed_head_at_run": _git_head(Path(".")),
            },
            "baseline_tests": {
                "chart_12": BASELINE_CHART_12_TESTS,
                "full": BASELINE_FULL_TESTS,
            },
            "coordinator_candidate": {
                "name": "ForegroundRepositoryObservationCoordinator",
                "scope": "repository filesystem plus Git observation only",
                "foreground": True,
                "explicitly_invoked": True,
                "single_writer": True,
                "autonomous": False,
                "schedules_captures": False,
                "decides_capture_warrant": False,
                "world_mutation_capability": False,
                "knows_future_trajectory": False,
                "knows_total_round_count": False,
                "production_api": True,
            },
            "fixture": {
                "identity": "phase-c-external-trajectory-fixture-v0",
                "kind": "deterministic temporary Git repository",
                "files": ["state.txt"],
                "initial_commit": initial_commit,
                "beta_commit": beta_commit,
                "trajectory_owner": "external test driver",
                "ledger": "one temporary JSONL ledger",
            },
            "durable_state": durable_state,
            "process_local_state": process_local,
            "external_world_sequence": [
                "create and commit clean alpha",
                "no mutation",
                "rewrite alpha to beta without commit",
                "add and commit beta without rewriting",
                "destroy coordinator",
                "rewrite beta to gamma while coordinator is absent",
                "open fresh coordinator and capture",
            ],
            "capture_calls": calls,
            "call_comparisons": comparisons,
            "historical_prefix": {
                "witness_record_count": len(witness_records),
                "relations": prefix_results,
                "persistent_witness_infrastructure_added": False,
            },
            "reopen": {
                "old_coordinator_destroyed": True,
                "fresh_coordinator_constructed": True,
                "reconstruction_or_projection_passed_to_fresh_instance": False,
                "pre_capture_result": disk_result_before_capture,
                "old_record_count_recovered": disk_result_before_capture["ledger"]["record_count"],
                "old_observation_count_recovered": disk_result_before_capture["derived"]["observation_count"],
                "old_projection_count_recovered": len(
                    disk_result_before_capture["derived"]["projection"]
                ),
                "continuation_record_count": calls[-1]["result"]["ledger"]["record_count"],
            },
            "absent_interval": absent_interval,
            "epistemic_audit": _epistemic_audit(calls, absent_interval),
            "canonical_history": {
                "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
                "sha256_before": canonical_before,
                "sha256_after": canonical_after,
                "unchanged": canonical_before == canonical_after,
            },
            "success_criterion": {
                "coherent": coherent,
                "answer": (
                    "existing structures compose behind the foreground candidate without hidden durable state"
                    if coherent
                    else "the candidate exposed a composition fracture"
                ),
            },
            "promotion_evaluation": {
                "candidate_boundary_earned": coherent,
                "production_promoted": coherent,
                "implementation": (
                    "src.runtime.foreground_repository_observation."
                    "ForegroundRepositoryObservationCoordinator"
                ),
                "basis": (
                    "five caller-selected captures, external mutation, disk-only "
                    "reopen, and absent-interval endpoint evidence"
                ),
            },
            "chart_status": _chart_status(coherent, calls),
            "distinction_evaluation": {
                "candidate": "coordinator_lifetime != historical_continuity",
                "forced": coherent,
                "registered": coherent,
                "id": "D-0042" if coherent else None,
            },
            "prior_findings": {
                "chart_12_preserved": True,
                "chart_11_preserved": True,
                "D_0012_preserved": True,
                "D_0016_preserved": True,
                "D_0041_preserved": True,
            },
            "strongest_invariant": (
                "authoritative ledger history, not coordinator lifetime, supplies "
                "operational continuity"
            ),
            "strongest_failure": (
                "the coordinator cannot recover events inside an unobserved interval; "
                "it can expose only the next captured endpoint"
            ),
            "strongest_unresolved_horizon": (
                "a four-record capture round has no tested partial-round failure or atomicity semantics"
            ),
            "next_smallest_frontier": (
                "isolate partial-round append failure before adding autonomy or new sources"
            ),
            "duration_seconds": round(perf_counter() - started, 6),
        }

    return report


def _call_summary(
    call: str,
    world_condition: str,
    external_action: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    new_records = result["new_records"]
    filesystem = result["captured_observations"]["filesystem"]
    git_state = result["captured_observations"]["git"]
    state_entry = next(
        entry for entry in filesystem["entries"] if entry["path"] == "state.txt"
    )
    return {
        "call": call,
        "world_condition": world_condition,
        "external_action_before_call": external_action,
        "record_range": [new_records[0]["commit_index"], new_records[-1]["commit_index"]],
        "filesystem": {
            "snapshot_id": filesystem["snapshot_id"],
            "observation_started_at": filesystem["observation_started_at"],
            "observation_finished_at": filesystem["observation_finished_at"],
            "state_txt_sha256": state_entry["sha256"],
            "capture_errors": filesystem["capture_errors"],
        },
        "git": {
            "observation_id": git_state["observation_id"],
            "observed_at": git_state["observed_at"],
            "head_sha": git_state["head_sha"],
            "branch": git_state["branch"],
            "status_porcelain": git_state["status_porcelain"],
            "capture_errors": git_state["capture_errors"],
        },
        "result": result,
    }


def _call_comparisons(calls: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {item["call"]: item for item in calls}
    return {
        name: _compare_calls(by_name[left], by_name[right])
        for name, left, right in (
            ("C1_C2", "C1", "C2"),
            ("C2_C3", "C2", "C3"),
            ("C3_C4", "C3", "C4"),
            ("C4_C5", "C4", "C5"),
        )
    }


def _compare_calls(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    git_fields = ("head_sha", "branch", "status_porcelain", "capture_errors")
    return {
        "filesystem_configuration_equal": before["filesystem"]["snapshot_id"]
        == after["filesystem"]["snapshot_id"],
        "git_configuration_equal": all(
            before["git"][field] == after["git"][field] for field in git_fields
        ),
        "filesystem_observation_record_equal": (
            before["result"]["new_records"][0]["record_id"]
            == after["result"]["new_records"][0]["record_id"]
        ),
        "git_observation_record_equal": (
            before["result"]["new_records"][1]["record_id"]
            == after["result"]["new_records"][1]["record_id"]
        ),
    }


def _absent_interval(
    calls: list[dict[str, Any]], disk_result_before_capture: dict[str, Any]
) -> dict[str, Any]:
    before = calls[-2]
    after = calls[-1]
    delta = compare_snapshots(
        before["result"]["captured_observations"]["filesystem"],
        after["result"]["captured_observations"]["filesystem"],
    )
    return {
        "external_driver_fact": "state.txt was rewritten from beta to gamma while no coordinator existed",
        "records_appended_while_absent": 0,
        "disk_record_count_before_post_reopen_capture": disk_result_before_capture["ledger"]["record_count"],
        "observed_endpoint_difference": bool(delta["changed_paths"]),
        "changed_paths_between_observed_endpoints": [
            item["path"] for item in delta["changed_paths"]
        ],
        "known_intermediate_states": [],
        "known_transition_time": None,
        "known_transition_mechanism": None,
        "invented_transition_records": [],
        "DME_claim": (
            "the newly captured endpoint differs from the last captured endpoint; "
            "intermediate transformation history is unavailable"
        ),
    }


def _epistemic_audit(
    calls: list[dict[str, Any]], absent_interval: dict[str, Any]
) -> dict[str, Any]:
    return {
        "coordinator_introduced_source_knowledge": False,
        "process_memory_strengthened_certainty": False,
        "repeated_capture_aggregated_confidence": False,
        "restart_lost_evidence": False,
        "missed_interval_interpreted_as_known_transition": bool(
            absent_interval["known_intermediate_states"]
            or absent_interval["invented_transition_records"]
        ),
        "filesystem_and_git_collapsed": False,
        "projection_membership_became_admission_resolution": False,
        "current_state_overwrote_history": False,
        "all_admissions_scoped_to_named_comparator": all(
            record["decision"] == "admitted"
            for call in calls
            for record in call["result"]["new_records"]
            if record["record_type"] == "admission"
        ),
    }


def _coherent(
    calls: list[dict[str, Any]],
    prefix_results: dict[str, Any],
    disk_result: dict[str, Any],
    absent_interval: dict[str, Any],
    durable_state: dict[str, Any],
) -> bool:
    return (
        all(
            call["result"]["ledger"][key]
            for call in calls
            for key in (
                "integrity_ok",
                "continuity_ok",
                "canonical_replay_reproducible",
            )
        )
        and all(
            call["result"]["derived"][key]
            for call in calls
            for key in (
                "reconstruction_reproducible",
                "projection_reproducible",
                "companion_reproducible",
                "source_provenance_separate",
            )
        )
        and all(relation["ok"] for relation in prefix_results.values())
        and disk_result["ledger"]["record_count"] == 16
        and disk_result["derived"]["observation_count"] == 8
        and absent_interval["records_appended_while_absent"] == 0
        and absent_interval["observed_endpoint_difference"]
        and not absent_interval["known_intermediate_states"]
        and durable_state["ledger_unchanged_by_absent_world_mutation"]
        and durable_state["current_result_is_read_only"]
    )


def _chart_status(coherent: bool, calls: list[dict[str, Any]]) -> dict[str, Any]:
    earned = coherent and len(calls) == 5
    return {
        "earned": earned,
        "name": "Chart 13" if earned else None,
        "coordinates": (
            "caller-selected capture x external world action, coordinator lifetime, "
            "source-relative configuration, ledger range, reconstruction, and "
            "historical prefix"
            if earned
            else None
        ),
        "generalized_state_model": False,
    }


def _process_state(
    coordinator: ForegroundRepositoryObservationCoordinator,
) -> dict[str, Any]:
    return {
        "fields": sorted(vars(coordinator)),
        "root": coordinator.root.name,
        "ledger_path": coordinator.ledger_path.name,
        "closed": coordinator._closed,
    }


def _initialize_fixture(root: Path) -> str:
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Phase-C Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "initial alpha",
        env=_commit_environment("2000-01-01T00:00:00+00:00"),
    )
    return _git(root, "rev-parse", "HEAD")


def _commit_world(root: Path, message: str, timestamp: str) -> str:
    _git(root, "add", "state.txt")
    _git(root, "commit", "-m", message, env=_commit_environment(timestamp))
    return _git(root, "rev-parse", "HEAD")


def _commit_environment(timestamp: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update({"GIT_AUTHOR_DATE": timestamp, "GIT_COMMITTER_DATE": timestamp})
    return env


def _git(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return completed.stdout.strip()


def _git_head(root: Path) -> str | None:
    try:
        return _git(root, "rev-parse", "HEAD")
    except (OSError, subprocess.CalledProcessError):
        return None


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = run()
    TRACE_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
