"""Bounded pressure for timing skew inside one foreground capture invocation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable
from unittest.mock import patch

from src.ledger import CANONICAL_LIVE_INGEST_LEDGER_PATH, JsonlLedger
from src.runtime import foreground_repository_observation as foreground_module
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "intra_capture_timing_skew_pressure_v0.json"
STARTING_HEAD = "249cde3783a528018269c7b7f08a7a9dfe245c9b"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "Pre-goblin capstone Super Tetaroni"
STARTING_WORKTREE: list[str] = []
BASELINE_TARGETED_TESTS = {"passed": 50, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 326, "failed": 0}
ALPHA_SHA256 = hashlib.sha256(b"alpha").hexdigest()
BETA_SHA256 = hashlib.sha256(b"beta").hexdigest()


Mutation = Callable[[Path], dict[str, Any]]


def run() -> dict[str, Any]:
    """Execute C0, S1, S2, and C1 without changing production capture code."""
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        temporary_root = Path(tmpdir)
        c0 = _independent_specimen(
            temporary_root / "C0",
            name="C0",
            intervention=None,
            ground_truth_mutation=False,
            ground_truth_shared_configuration=True,
        )
        s1 = _independent_specimen(
            temporary_root / "S1",
            name="S1",
            intervention=_dirty_beta,
            ground_truth_mutation=True,
            ground_truth_shared_configuration=False,
        )
        s2, c1 = _commit_skew_and_post_control(temporary_root / "S2_C1")

    specimens = {item["name"]: item for item in (c0, s1, s2, c1)}
    matrix = [_matrix_row(specimens[name]) for name in ("C0", "S1", "S2", "C1")]
    canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    skew_counterexample = all(
        specimens[name]["ground_truth"]["mutation_between_acquisitions"]
        and not specimens[name]["ground_truth"]["shared_world_configuration"]
        and specimens[name]["immediate"]["same_invocation"]
        and specimens[name]["health"]["structurally_healthy"]
        for name in ("S1", "S2")
    )
    chart_earned = skew_counterexample and all(
        specimen["health"]["structurally_healthy"] for specimen in specimens.values()
    )

    return {
        "experiment": "intra_capture_timing_skew_pressure_v0",
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
        "timing_intervention": {
            "mechanism": (
                "experiment-local replacement of the coordinator module's "
                "make_repo_snapshot reference; the wrapper calls the real observer "
                "to completion, then an external-driver callback mutates the fixture "
                "before production control reaches observe_git_state"
            ),
            "deterministic_boundary": "after filesystem return and before Git call",
            "arbitrary_sleep": False,
            "race_based": False,
            "mutation_owned_by_production_coordinator": False,
            "production_capture_code_modified": False,
        },
        "fixture_control": {
            "independent_fixtures": ["C0", "S1", "S2/C1"],
            "C1_reuses_settled_S2_world": True,
            "initial_file": {"path": "state.txt", "content": "alpha", "sha256": ALPHA_SHA256},
            "later_file": {"path": "state.txt", "content": "beta", "sha256": BETA_SHA256},
            "trajectory_owner": "external experiment driver",
        },
        "specimens": specimens,
        "comparison_matrix": matrix,
        "temporal_audit": {
            "filesystem_evidence": ["observation_started_at", "observation_finished_at"],
            "git_evidence": ["observed_at"],
            "fields_persist_in_observation_payload_and_provenance": True,
            "recorded_timestamp_order_recoverable": all(
                item["temporal_evidence"]["filesystem_finished_before_git_observed"]
                for item in specimens.values()
            ),
            "complete_interval_non_overlap_recoverable": False,
            "complete_interval_non_overlap_reason": (
                "Git records one observed_at marker, not a start/finish interval"
            ),
            "simultaneity_recoverable": False,
            "shared_world_configuration_recoverable": False,
            "clock_identity_or_precision_recorded": False,
        },
        "together_audit": {
            "same_invocation_process_local": True,
            "same_acquisition_episode_process_local": True,
            "same_durable_historical_group": "UNRESOLVED",
            "same_world_configuration_from_DME_evidence": "UNRESOLVED",
            "same_invocation_licenses_same_world_configuration": False,
            "adjacent_commit_indices_license_simultaneity": False,
            "successful_reconstruction_licenses_global_snapshot": False,
        },
        "projection_audit": {
            "preserves_admitted_observations_as_separate_subjects": True,
            "silently_fuses_sources": False,
            "claims_simultaneity": False,
            "claims_current_coherent_repository_state": False,
            "projection_redesigned": False,
        },
        "chart_status": {
            "earned": chart_earned,
            "name": "Chart 15" if chart_earned else None,
            "coordinates": (
                "specimen x source-relative configuration, external mutation, "
                "structural health, process-local grouping, durable grouping, and "
                "world-configuration justification"
                if chart_earned
                else None
            ),
            "generalized_temporal_or_world_state_model": False,
        },
        "distinctions": {
            "added": (
                [
                    {
                        "id": "D-0044",
                        "left": "same_capture_invocation",
                        "relation": "not_equivalent_to",
                        "right": "same_world_configuration",
                    }
                ]
                if skew_counterexample
                else []
            ),
            "amended": [],
        },
        "epistemic_audit": {
            "driver_mutation_written_to_history": False,
            "transition_record_manufactured": False,
            "same_invocation_treated_as_same_world": False,
            "adjacency_treated_as_simultaneity": False,
            "admission_treated_as_mutual_contemporaneity": False,
            "reconstruction_treated_as_global_coherence": False,
            "successful_return_treated_as_one_instant": False,
            "handling_order_treated_as_proof_of_mutation": False,
            "unjustified_certainty_exposed_by_existing_result": False,
        },
        "information_boundary": {
            "source_observation_content_lost_on_recovery": False,
            "source_timing_fields_lost_on_recovery": False,
            "process_local_invocation_association_lost_on_recovery": True,
            "external_driver_mutation_fact_durable": False,
            "loss_is_corruption": False,
        },
        "production_boundary": {
            "status": "PRESERVED_WITH_SCOPED_GUARANTEE",
            "guarantee": (
                "one explicit call sequentially acquires, admits, and returns two "
                "source-relative observations"
            ),
            "atomic_or_global_snapshot_guarantee": False,
            "production_change_made": False,
        },
        "prior_findings": {
            "D_0042_preserved": True,
            "D_0043_preserved": True,
            "partial_round_findings_preserved": True,
            "chart_11_companion_preserved": True,
            "source_separation_preserved": True,
            "invalidated": [],
        },
        "strongest_invariant": (
            "individually valid source-relative observations remain durable, separate, "
            "reconstructible, and projectable despite intra-capture world change"
        ),
        "strongest_failure": (
            "one successful capture can return a structurally healthy pair that, by "
            "experiment control, never described one shared repository configuration"
        ),
        "strongest_unresolved_horizon": (
            "authoritative history lacks durable invocation grouping and cannot decide "
            "whether independently timed source observations share a world configuration"
        ),
        "next_smallest_pressure": (
            "pressure stale current_result semantics without adding a latest-state or "
            "temporal-fusion abstraction"
        ),
        "canonical_history": {
            "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
            "sha256_before": canonical_before,
            "sha256_after": canonical_after,
            "unchanged": canonical_before == canonical_after,
        },
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _independent_specimen(
    directory: Path,
    *,
    name: str,
    intervention: Mutation | None,
    ground_truth_mutation: bool,
    ground_truth_shared_configuration: bool,
) -> dict[str, Any]:
    root, ledger_path, alpha_head = _new_fixture(directory)
    immediate, event = _capture(root, ledger_path, intervention)
    return _summarize_specimen(
        name,
        immediate,
        event,
        _fresh_recovery(root, ledger_path),
        alpha_head=alpha_head,
        beta_head=None,
        ground_truth_mutation=ground_truth_mutation,
        ground_truth_shared_configuration=ground_truth_shared_configuration,
    )


def _commit_skew_and_post_control(directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root, ledger_path, alpha_head = _new_fixture(directory)
    s2_immediate, s2_event = _capture(root, ledger_path, _committed_beta)
    beta_head = _git(root, "rev-parse", "HEAD")
    s2_recovery = _fresh_recovery(root, ledger_path)
    s2 = _summarize_specimen(
        "S2",
        s2_immediate,
        s2_event,
        s2_recovery,
        alpha_head=alpha_head,
        beta_head=beta_head,
        ground_truth_mutation=True,
        ground_truth_shared_configuration=False,
    )

    c1_immediate, c1_event = _capture(root, ledger_path, None)
    c1 = _summarize_specimen(
        "C1",
        c1_immediate,
        c1_event,
        _fresh_recovery(root, ledger_path),
        alpha_head=alpha_head,
        beta_head=beta_head,
        ground_truth_mutation=False,
        ground_truth_shared_configuration=True,
    )
    return s2, c1


def _capture(
    root: Path, ledger_path: Path, intervention: Mutation | None
) -> tuple[dict[str, Any], dict[str, Any]]:
    coordinator = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    event: dict[str, Any] = {
        "intercepted": intervention is not None,
        "filesystem_returned_before_driver": None,
        "driver_action": "none",
    }
    if intervention is None:
        result = coordinator.capture_round()
    else:
        real_snapshot = foreground_module.make_repo_snapshot

        def snapshot_then_external_action(capture_root: Path | str) -> dict[str, Any]:
            snapshot = real_snapshot(capture_root)
            event["filesystem_returned_before_driver"] = True
            event.update(intervention(Path(capture_root)))
            return snapshot

        with patch.object(
            foreground_module, "make_repo_snapshot", snapshot_then_external_action
        ):
            result = coordinator.capture_round()
    coordinator.close()
    del coordinator
    return result, event


def _fresh_recovery(root: Path, ledger_path: Path) -> dict[str, Any]:
    before = _file_sha256(ledger_path)
    coordinator = ForegroundRepositoryObservationCoordinator.open(root, ledger_path)
    result = coordinator.current_result()
    coordinator.close()
    del coordinator
    after = _file_sha256(ledger_path)
    records = JsonlLedger(ledger_path).replay()
    observation_records = [
        record for record in records if record["envelope"]["record_type"] == "observation"
    ]
    durable_keys = sorted(
        {
            key
            for record in records
            for key in record["envelope"]
            if key in {"round_id", "request_id", "invocation_id", "group_id"}
        }
    )
    return {
        "result": result,
        "read_only": before == after,
        "record_count": len(records),
        "observation_count": len(observation_records),
        "record_ids": [record["record_id"] for record in records],
        "commit_indices": [record["commit_index"] for record in records],
        "durable_grouping_fields": durable_keys,
        "same_invocation_from_history": "UNRESOLVED",
        "captured_observations_available": result["captured_observations"] is not None,
    }


def _summarize_specimen(
    name: str,
    immediate: dict[str, Any],
    event: dict[str, Any],
    recovery: dict[str, Any],
    *,
    alpha_head: str,
    beta_head: str | None,
    ground_truth_mutation: bool,
    ground_truth_shared_configuration: bool,
) -> dict[str, Any]:
    filesystem = immediate["captured_observations"]["filesystem"]
    git_state = immediate["captured_observations"]["git"]
    state_entry = next(entry for entry in filesystem["entries"] if entry["path"] == "state.txt")
    derived = immediate["derived"]
    ledger = immediate["ledger"]
    fs_finished = filesystem["observation_finished_at"]
    git_observed = git_state["observed_at"]
    return {
        "name": name,
        "intervention": event,
        "filesystem": {
            "state_txt_sha256": state_entry["sha256"],
            "configuration": "alpha" if state_entry["sha256"] == ALPHA_SHA256 else "beta",
            "snapshot_id": filesystem["snapshot_id"],
            "observation_started_at": filesystem["observation_started_at"],
            "observation_finished_at": fs_finished,
            "capture_errors": filesystem["capture_errors"],
        },
        "git": {
            "configuration": _git_configuration(git_state, alpha_head, beta_head),
            "observed_at": git_observed,
            "head_sha": git_state["head_sha"],
            "branch": git_state["branch"],
            "status_porcelain": git_state["status_porcelain"],
            "capture_errors": git_state["capture_errors"],
        },
        "temporal_evidence": {
            "filesystem_finished_before_git_observed": fs_finished < git_observed,
            "recorded_order": "filesystem interval then Git marker" if fs_finished < git_observed else "unresolved",
            "full_non_overlap_established": False,
            "simultaneity_established": False,
        },
        "ground_truth": {
            "basis": "external deterministic experiment control",
            "mutation_between_acquisitions": ground_truth_mutation,
            "shared_world_configuration": ground_truth_shared_configuration,
            "transferred_into_DME_history": False,
        },
        "DME_knowledge": {
            "individual_source_observations_valid": (
                not filesystem["capture_errors"] and not git_state["capture_errors"]
            ),
            "same_world_configuration": "UNRESOLVED",
            "mutation_between_acquisitions": "UNRESOLVED",
            "global_snapshot_claim": False,
        },
        "immediate": {
            "capture_returned": True,
            "same_invocation": True,
            "same_acquisition_episode": True,
            "record_ids": [record["record_id"] for record in immediate["new_records"]],
            "commit_indices": [record["commit_index"] for record in immediate["new_records"]],
            "captured_observations_grouped_on_return": True,
        },
        "recovery": recovery,
        "health": {
            "integrity_ok": ledger["integrity_ok"],
            "continuity_ok": ledger["continuity_ok"],
            "replay_reproducible": ledger["canonical_replay_reproducible"],
            "reconstruction_reproducible": derived["reconstruction_reproducible"],
            "projection_reproducible": derived["projection_reproducible"],
            "companion_reproducible": derived["companion_reproducible"],
            "source_separation": derived["source_provenance_separate"],
            "observation_count": derived["observation_count"],
            "admission_relation_count": derived["admission_relation_count"],
            "projection_subject_count": len(derived["projection"]),
            "companion_count": len(derived["companion"]),
            "companion_states": [
                row["non_admitted_decision_states"] for row in derived["companion"]
            ],
            "structurally_healthy": all(
                (
                    ledger["integrity_ok"],
                    ledger["continuity_ok"],
                    ledger["canonical_replay_reproducible"],
                    derived["reconstruction_reproducible"],
                    derived["projection_reproducible"],
                    derived["companion_reproducible"],
                    derived["source_provenance_separate"],
                )
            ),
        },
    }


def _matrix_row(specimen: dict[str, Any]) -> dict[str, Any]:
    return {
        "specimen": specimen["name"],
        "filesystem_configuration": specimen["filesystem"]["configuration"],
        "git_configuration": specimen["git"]["configuration"],
        "mutation_between_acquisition_ground_truth": specimen["ground_truth"][
            "mutation_between_acquisitions"
        ],
        "integrity": specimen["health"]["integrity_ok"],
        "reconstruction": specimen["health"]["reconstruction_reproducible"],
        "same_invocation_immediate": specimen["immediate"]["same_invocation"],
        "same_invocation_from_history": specimen["recovery"]["same_invocation_from_history"],
        "shared_world_configuration_ground_truth": specimen["ground_truth"][
            "shared_world_configuration"
        ],
        "shared_world_configuration_from_DME_evidence": specimen["DME_knowledge"][
            "same_world_configuration"
        ],
    }


def _git_configuration(
    git_state: dict[str, Any], alpha_head: str, beta_head: str | None
) -> str:
    if git_state["head_sha"] == alpha_head and git_state["status_porcelain"] == []:
        return "clean alpha"
    if git_state["head_sha"] == alpha_head and git_state["status_porcelain"]:
        return "dirty later state over alpha HEAD"
    if beta_head is not None and git_state["head_sha"] == beta_head and git_state["status_porcelain"] == []:
        return "clean committed beta"
    return "other observed Git configuration"


def _new_fixture(directory: Path) -> tuple[Path, Path, str]:
    root = directory / "fixture"
    root.mkdir(parents=True)
    (root / "state.txt").write_text("alpha", encoding="utf-8")
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Timing Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "initial alpha",
        env=_commit_environment("2000-01-01T00:00:00+00:00"),
    )
    return root, directory / "history.jsonl", _git(root, "rev-parse", "HEAD")


def _dirty_beta(root: Path) -> dict[str, Any]:
    (root / "state.txt").write_text("beta", encoding="utf-8")
    return {
        "driver_action": "rewrite state.txt from alpha to beta without commit",
        "post_action_head": _git(root, "rev-parse", "HEAD"),
        "post_action_status": _git(root, "status", "--porcelain=v1").splitlines(),
    }


def _committed_beta(root: Path) -> dict[str, Any]:
    (root / "state.txt").write_text("beta", encoding="utf-8")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "commit beta",
        env=_commit_environment("2000-01-02T00:00:00+00:00"),
    )
    return {
        "driver_action": "rewrite state.txt from alpha to beta, add, and commit",
        "post_action_head": _git(root, "rev-parse", "HEAD"),
        "post_action_status": _git(root, "status", "--porcelain=v1").splitlines(),
    }


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
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
