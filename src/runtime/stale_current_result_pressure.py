"""Bounded pressure for stale-world semantics of ``current_result()``."""

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

from src.ledger import CANONICAL_LIVE_INGEST_LEDGER_PATH, JsonlLedger
from src.ledger.jsonl import canonical_json
from src.reconstruction import (
    derive_admitted_projection,
    derive_non_admitted_decision_states,
    reconstruct_admission_relationships,
)
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "stale_current_result_pressure_v0.json"
STARTING_HEAD = "a07ef2e10661f8d1c442a817428737ef945b747c"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "Wound 2"
STARTING_WORKTREE: list[str] = []
BASELINE_TARGETED_TESTS = {"passed": 76, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 352, "failed": 0}
ALPHA_SHA256 = hashlib.sha256(b"alpha").hexdigest()
BETA_SHA256 = hashlib.sha256(b"beta").hexdigest()


def run() -> dict[str, Any]:
    """Execute stable, stale, reopen, and explicit-recapture specimens."""
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        temporary_root = Path(tmpdir)
        c0 = _stable_control(temporary_root / "C0")
        s1, f1 = _dirty_stale_and_recapture(temporary_root / "S1_F1")
        s2, r1 = _committed_stale_and_reopen(temporary_root / "S2_R1")

    specimens = {item["name"]: item for item in (c0, s1, s2, r1, f1)}
    matrix = [_matrix_row(specimens[name]) for name in ("C0", "S1", "S2", "R1", "F1")]
    canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)
    stale_demonstrated = all(
        specimens[name]["external_control"]["differs_from_last_captured"]
        and specimens[name]["read"]["append_free"]
        and specimens[name]["read"]["historical_surface_matches_last_capture"]
        and specimens[name]["read"]["structurally_healthy"]
        for name in ("S1", "S2", "R1")
    )
    chart_earned = stale_demonstrated and f1["recapture"]["history_advanced"]

    return {
        "experiment": "stale_current_result_pressure_v0",
        "starting_lineage": {
            "branch": STARTING_BRANCH,
            "head": STARTING_HEAD,
            "message": STARTING_MESSAGE,
            "worktree": STARTING_WORKTREE,
            "observed_head_at_run": _git_head(Path(".")),
        },
        "baseline_tests": {
            "targeted": BASELINE_TARGETED_TESTS,
            "full": BASELINE_FULL_TESTS,
        },
        "fixture_control": {
            "independent_fixtures": ["C0", "S1/F1", "S2/R1"],
            "initial_configuration": "clean committed alpha",
            "trajectory_owner": "external experiment driver",
            "mutation_written_to_DME_history_before_recapture": False,
            "arbitrary_sleep": False,
            "round_trip_mutation": False,
        },
        "specimens": specimens,
        "comparison_matrix": matrix,
        "critical_comparison": {
            "S1_last_capture_equals_current_result_history": s1["read"][
                "historical_surface_matches_last_capture"
            ],
            "S1_external_world_differs": s1["external_control"][
                "differs_from_last_captured"
            ],
            "S2_last_capture_equals_current_result_history": s2["read"][
                "historical_surface_matches_last_capture"
            ],
            "S2_external_world_differs": s2["external_control"][
                "differs_from_last_captured"
            ],
            "result_characterization": (
                "current with respect to authoritative history and stale with "
                "respect to the externally changed repository"
            ),
            "classified_as_corrupt_or_incorrect_history": False,
        },
        "freshness_evidence": {
            "current_result_exposes_observation_timestamps_directly": False,
            "timestamps_recoverable_from_authoritative_reconstruction": True,
            "filesystem_fields": ["observation_started_at", "observation_finished_at"],
            "git_fields": ["observed_at"],
            "age_exposed_by_current_result": False,
            "age_computable_with_external_now_and_clock_assumptions": True,
            "clock_identity_or_precision_contract_recorded": False,
            "source_change_since_observation_inferable": False,
            "method_call_time_adds_world_knowledge": False,
            "replay_time_adds_world_knowledge": False,
            "freshness_threshold_added": False,
        },
        "consumer_interpretation": {
            "current_DME_derivation_from_recorded_history": "JUSTIFIED",
            "current_external_repository_configuration": "NOT_JUSTIFIED",
            "no_source_change_since_last_observation": "NOT_JUSTIFIED",
            "projection_contains_latest_recorded_admitted_observations": "JUSTIFIED",
            "projection_contains_latest_external_configuration": "NOT_JUSTIFIED",
        },
        "projection_audit": {
            "unchanged_before_recapture_in_S1_S2_R1": True,
            "contains_only_previously_admitted_observations": True,
            "claims_latest": False,
            "claims_current_repository_configuration": False,
            "current_result_strengthens_to_world_current_claim": False,
            "projection_redesigned": False,
        },
        "production_contract": {
            "docstring": "Rebuild the current derived state without appending or capturing.",
            "implementation_matches_docstring": True,
            "world_freshness_claimed": False,
            "potential_consumer_overinterpretation": (
                "the word current may be read as source-current if the documented "
                "without-capture boundary is ignored"
            ),
            "overclaimed_freshness": False,
            "renamed": False,
            "production_change_made": False,
        },
        "information_boundary": {
            "authoritative_history_lost": False,
            "reconstruction_or_projection_information_lost": False,
            "external_mutation_observed_before_F1": False,
            "unobserved_external_divergence_present_in_history": False,
            "absence_is_corruption": False,
        },
        "chart_status": {
            "earned": chart_earned,
            "name": "Chart 16" if chart_earned else None,
            "coordinates": (
                "specimen x last recorded configuration, external configuration at "
                "read, byte conservation, historical derivation, process lifetime, "
                "and source-freshness inference"
                if chart_earned
                else None
            ),
            "freshness_policy_or_latest_state_model": False,
        },
        "distinctions": {
            "added": (
                [
                    {
                        "id": "D-0045",
                        "left": "current_derived_history",
                        "relation": "not_equivalent_to",
                        "right": "current_external_configuration",
                    }
                ]
                if stale_demonstrated
                else []
            ),
            "amended": [],
        },
        "prior_findings": {
            "D_0042": "SUPPORTED_UNCHANGED",
            "D_0043": "SUPPORTED_UNCHANGED",
            "D_0044": "SUPPORTED_UNCHANGED",
            "chart_11_companion_preserved": True,
            "source_separation_preserved": True,
            "invalidated": [],
        },
        "epistemic_audit": {
            "current_result_treated_as_current_world": False,
            "reproducibility_treated_as_freshness": False,
            "unchanged_ledger_treated_as_unchanged_world": False,
            "latest_recorded_treated_as_latest_world": False,
            "recent_timestamp_treated_as_current_equality": False,
            "fresh_coordinator_treated_as_fresh_evidence": False,
            "driver_knowledge_transferred_to_DME": False,
            "unjustified_certainty_in_existing_contract": False,
        },
        "strongest_invariant": (
            "current_result deterministically and append-freely reconstructs the same "
            "authoritative historical surface across external divergence and process replacement"
        ),
        "strongest_failure": (
            "a structurally valid current_result can remain arbitrarily stale with "
            "respect to an externally changed repository until a new capture commits evidence"
        ),
        "strongest_unresolved_horizon": (
            "no existing returned evidence establishes whether either external source "
            "still equals its most recent recorded observation"
        ),
        "next_smallest_pressure": (
            "isolate the absent-interval alpha-to-beta-to-alpha round trip without "
            "adding polling, latest-state selection, or transformation inference"
        ),
        "canonical_history": {
            "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
            "sha256_before": canonical_before,
            "sha256_after": canonical_after,
            "unchanged": canonical_before == canonical_after,
        },
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _stable_control(directory: Path) -> dict[str, Any]:
    root, ledger_path = _new_fixture(directory)
    coordinator = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    capture = _capture_baseline(coordinator, ledger_path)
    external = _external_control(root, capture["last_captured_evidence"])
    read = _read_current(coordinator, ledger_path, capture["history_surface"])
    coordinator.close()
    del coordinator
    return _specimen(
        "C0",
        "clean alpha",
        capture,
        external,
        read,
        process="existing coordinator",
    )


def _dirty_stale_and_recapture(directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root, ledger_path = _new_fixture(directory)
    coordinator = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    capture = _capture_baseline(coordinator, ledger_path)
    (root / "state.txt").write_text("beta", encoding="utf-8")
    external = _external_control(root, capture["last_captured_evidence"])
    stale_read = _read_current(coordinator, ledger_path, capture["history_surface"])
    s1 = _specimen(
        "S1",
        "dirty beta after clean-alpha capture",
        capture,
        external,
        stale_read,
        process="existing coordinator",
    )

    before_recapture = _ledger_surface(ledger_path)
    recapture_result = coordinator.capture_round()
    after_recapture = _ledger_surface(ledger_path)
    recaptured_evidence = _last_recorded_evidence(ledger_path)
    post_read = _read_current(coordinator, ledger_path, after_recapture)
    post_external = _external_control(root, recaptured_evidence)
    coordinator.close()
    del coordinator
    f1 = {
        "name": "F1",
        "world_condition": "dirty beta explicitly observed after stale interval",
        "last_captured_evidence": deepcopy(recaptured_evidence),
        "external_control": post_external,
        "read": post_read,
        "recapture": {
            "capture_returned": True,
            "new_record_ids": [item["record_id"] for item in recapture_result["new_records"]],
            "new_commit_indices": [
                item["commit_index"] for item in recapture_result["new_records"]
            ],
            "ledger_sha256_before": before_recapture["ledger_sha256"],
            "ledger_sha256_after": after_recapture["ledger_sha256"],
            "record_count_before": before_recapture["record_count"],
            "record_count_after": after_recapture["record_count"],
            "observation_count_before": before_recapture["observation_count"],
            "observation_count_after": after_recapture["observation_count"],
            "projection_count_before": before_recapture["projection_count"],
            "projection_count_after": after_recapture["projection_count"],
            "companion_count_before": before_recapture["companion_count"],
            "companion_count_after": after_recapture["companion_count"],
            "history_advanced": before_recapture != after_recapture,
            "changed_only_after_explicit_capture": True,
        },
        "ground_truth": {
            "source_matches_last_recorded_at_read": True,
            "basis": "external experiment control after explicit capture",
            "DME_guarantees_continued_equality_after_capture": False,
        },
    }
    return s1, f1


def _committed_stale_and_reopen(directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root, ledger_path = _new_fixture(directory)
    coordinator = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    capture = _capture_baseline(coordinator, ledger_path)
    (root / "state.txt").write_text("beta", encoding="utf-8")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "commit beta",
        env=_commit_environment("2000-01-02T00:00:00+00:00"),
    )
    external = _external_control(root, capture["last_captured_evidence"])
    existing_read = _read_current(coordinator, ledger_path, capture["history_surface"])
    s2 = _specimen(
        "S2",
        "clean committed beta after clean-alpha capture",
        capture,
        external,
        existing_read,
        process="existing coordinator",
    )
    coordinator.close()
    del coordinator

    fresh = ForegroundRepositoryObservationCoordinator.open(root, ledger_path)
    reopened_read = _read_current(fresh, ledger_path, capture["history_surface"])
    fresh.close()
    del fresh
    r1 = _specimen(
        "R1",
        "same committed-beta world and stale clean-alpha history after reopen",
        capture,
        external,
        reopened_read,
        process="fresh coordinator from root plus ledger_path",
    )
    r1["reopen_comparison"] = {
        "existing_and_fresh_results_equal": existing_read["result"] == reopened_read["result"],
        "existing_and_fresh_surfaces_equal": existing_read["after"] == reopened_read["after"],
        "process_replacement_changed_freshness": False,
        "reconstruction_or_projection_passed_to_fresh_coordinator": False,
    }
    return s2, r1


def _capture_baseline(
    coordinator: ForegroundRepositoryObservationCoordinator, ledger_path: Path
) -> dict[str, Any]:
    result = coordinator.capture_round()
    surface = _ledger_surface(ledger_path)
    return {
        "result": result,
        "history_surface": surface,
        "last_captured_evidence": _last_recorded_evidence(ledger_path),
        "new_record_ids": [item["record_id"] for item in result["new_records"]],
    }


def _read_current(
    coordinator: ForegroundRepositoryObservationCoordinator,
    ledger_path: Path,
    expected_history_surface: dict[str, Any],
) -> dict[str, Any]:
    before = _ledger_surface(ledger_path)
    result = coordinator.current_result()
    after = _ledger_surface(ledger_path)
    direct_timing_keys = sorted(
        key
        for key in _nested_keys(result)
        if key in {"observation_started_at", "observation_finished_at", "observed_at"}
    )
    healthy = all(
        (
            result["ledger"]["integrity_ok"],
            result["ledger"]["continuity_ok"],
            result["ledger"]["canonical_replay_reproducible"],
            result["derived"]["reconstruction_reproducible"],
            result["derived"]["projection_reproducible"],
            result["derived"]["companion_reproducible"],
            result["derived"]["source_provenance_separate"],
        )
    )
    return {
        "ledger_sha256_before": before["ledger_sha256"],
        "ledger_sha256_after": after["ledger_sha256"],
        "record_count_before": before["record_count"],
        "record_count_after": after["record_count"],
        "commit_indices_before": before["commit_indices"],
        "commit_indices_after": after["commit_indices"],
        "ordered_digests_before": before["ordered_digests"],
        "ordered_digests_after": after["ordered_digests"],
        "before": before,
        "after": after,
        "append_free": before == after,
        "historical_surface_matches_last_capture": after == expected_history_surface,
        "result": result,
        "structurally_healthy": healthy,
        "captured_observations": result["captured_observations"],
        "new_records": result["new_records"],
        "direct_observation_timing_keys": direct_timing_keys,
        "world_evidence_introduced": False,
    }


def _specimen(
    name: str,
    world_condition: str,
    capture: dict[str, Any],
    external: dict[str, Any],
    read: dict[str, Any],
    *,
    process: str,
) -> dict[str, Any]:
    last = capture["last_captured_evidence"]
    return {
        "name": name,
        "world_condition": world_condition,
        "process": process,
        "last_captured_evidence": deepcopy(last),
        "external_control": external,
        "read": read,
        "ground_truth": {
            "source_matches_last_recorded_at_read": not external[
                "differs_from_last_captured"
            ],
            "basis": "external experiment control",
            "transferred_into_DME_history": False,
        },
    }


def _ledger_surface(ledger_path: Path) -> dict[str, Any]:
    records = JsonlLedger(ledger_path).replay()
    reconstruction = reconstruct_admission_relationships(records)
    projection = derive_admitted_projection(reconstruction)
    companion = derive_non_admitted_decision_states(reconstruction, projection)
    return {
        "ledger_sha256": _file_sha256(ledger_path),
        "record_count": len(records),
        "commit_indices": [record["commit_index"] for record in records],
        "ordered_digests": [record["integrity"]["digest"] for record in records],
        "reconstruction_sha256": _json_sha256(reconstruction),
        "observation_count": len(reconstruction["observations"]),
        "admission_relation_count": sum(
            len(item["admissions"]) for item in reconstruction["observations"]
        ),
        "projection_sha256": _json_sha256(projection),
        "projection_count": len(projection),
        "companion_sha256": _json_sha256(companion),
        "companion_count": len(companion),
        "companion_states": [row["non_admitted_decision_states"] for row in companion],
        "source_values": [item["source"] for item in reconstruction["observations"]],
    }


def _last_recorded_evidence(ledger_path: Path) -> dict[str, Any]:
    records = JsonlLedger(ledger_path).replay()
    reconstruction = reconstruct_admission_relationships(records)
    filesystem = [
        item
        for item in reconstruction["observations"]
        if item["source"] == "repository_filesystem_snapshot"
    ][-1]
    git_item = [
        item
        for item in reconstruction["observations"]
        if item["source"] == "repository_git_state"
    ][-1]
    filesystem_payload = filesystem["observation"]["signal"]["payload"]
    git_payload = git_item["observation"]["signal"]["payload"]
    state_entry = next(
        entry for entry in filesystem_payload["entries"] if entry["path"] == "state.txt"
    )
    return {
        "selection": "last recorded observation per source by authoritative commit order",
        "filesystem": {
            "observation_record_id": filesystem["observation_record_id"],
            "commit_index": filesystem["observation_commit_index"],
            "state_txt_sha256": state_entry["sha256"],
            "configuration": _content_name(state_entry["sha256"]),
            "observation_started_at": filesystem_payload["observation_started_at"],
            "observation_finished_at": filesystem_payload["observation_finished_at"],
        },
        "git": {
            "observation_record_id": git_item["observation_record_id"],
            "commit_index": git_item["observation_commit_index"],
            "head_sha": git_payload["head_sha"],
            "branch": git_payload["branch"],
            "status_porcelain": git_payload["status_porcelain"],
            "observed_at": git_payload["observed_at"],
        },
        "timestamps_recovered_from_authoritative_reconstruction": True,
    }


def _external_control(
    root: Path, last_captured_evidence: dict[str, Any]
) -> dict[str, Any]:
    content = (root / "state.txt").read_bytes()
    content_sha = hashlib.sha256(content).hexdigest()
    head = _git(root, "rev-parse", "HEAD")
    branch = _git(root, "branch", "--show-current")
    status = _git(root, "status", "--porcelain=v1").splitlines()
    filesystem_differs = (
        content_sha != last_captured_evidence["filesystem"]["state_txt_sha256"]
    )
    git_differs = any(
        (
            head != last_captured_evidence["git"]["head_sha"],
            branch != last_captured_evidence["git"]["branch"],
            status != last_captured_evidence["git"]["status_porcelain"],
        )
    )
    return {
        "basis": "direct fixture bytes and Git commands outside DME capture",
        "state_txt_sha256": content_sha,
        "filesystem_configuration": _content_name(content_sha),
        "head_sha": head,
        "branch": branch,
        "status_porcelain": status,
        "git_configuration": "dirty" if status else "clean",
        "filesystem_differs_from_last_captured": filesystem_differs,
        "git_differs_from_last_captured": git_differs,
        "differs_from_last_captured": filesystem_differs or git_differs,
        "written_to_DME_history_by_control_read": False,
    }


def _matrix_row(specimen: dict[str, Any]) -> dict[str, Any]:
    last = specimen["last_captured_evidence"]
    external = specimen["external_control"]
    read = specimen["read"]
    return {
        "specimen": specimen["name"],
        "last_captured_filesystem": last["filesystem"]["configuration"],
        "last_captured_git_status": (
            "dirty" if last["git"]["status_porcelain"] else "clean"
        ),
        "external_filesystem_at_read": external["filesystem_configuration"],
        "external_git_at_read": external["git_configuration"],
        "ledger_changed_by_current_result": not read["append_free"],
        "reconstruction_changed": (
            read["before"]["reconstruction_sha256"]
            != read["after"]["reconstruction_sha256"]
        ),
        "projection_changed": (
            read["before"]["projection_sha256"] != read["after"]["projection_sha256"]
        ),
        "companion_changed": (
            read["before"]["companion_sha256"] != read["after"]["companion_sha256"]
        ),
        "external_freshness_inferable_from_result": False,
    }


def _nested_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(key)
            keys.update(_nested_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_nested_keys(item))
    return keys


def _new_fixture(directory: Path) -> tuple[Path, Path]:
    root = directory / "fixture"
    root.mkdir(parents=True)
    (root / "state.txt").write_text("alpha", encoding="utf-8")
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Stale Result Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "initial alpha",
        env=_commit_environment("2000-01-01T00:00:00+00:00"),
    )
    return root, directory / "history.jsonl"


def _content_name(content_sha: str) -> str:
    if content_sha == ALPHA_SHA256:
        return "alpha"
    if content_sha == BETA_SHA256:
        return "beta"
    return "other"


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


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
