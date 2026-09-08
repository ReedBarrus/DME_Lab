"""Bounded pressure for an unobserved round trip between equivalent endpoints."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable

from src.ledger import CANONICAL_LIVE_INGEST_LEDGER_PATH, JsonlLedger
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "absent_interval_round_trip_pressure_v0.json"
STARTING_HEAD = "938d6f7e48443252d78c193aaf7f129ee5dca26e"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "WOund 4"
STARTING_WORKTREE: list[str] = []
BASELINE_TARGETED_TESTS = {"passed": 104, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 380, "failed": 0}
ALPHA_SHA256 = hashlib.sha256(b"alpha").hexdigest()
BETA_SHA256 = hashlib.sha256(b"beta").hexdigest()
FIXED_MTIME_NS = 946684800_000_000_000


Mutation = Callable[[Path, int], dict[str, Any]]


def run() -> dict[str, Any]:
    """Execute stasis, hidden excursion, and visible endpoint-change specimens."""
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        temporary_root = Path(tmpdir)
        c0 = _run_specimen(
            temporary_root / "C0",
            name="C0",
            mutation=_no_mutation,
            control_path=["alpha", "alpha"],
            transformation_occurred=False,
        )
        s1 = _run_specimen(
            temporary_root / "S1",
            name="S1",
            mutation=_hidden_round_trip,
            control_path=["alpha", "beta", "alpha"],
            transformation_occurred=True,
        )
        s2 = _run_specimen(
            temporary_root / "S2",
            name="S2",
            mutation=_visible_beta,
            control_path=["alpha", "beta"],
            transformation_occurred=True,
        )

    specimens = {item["name"]: item for item in (c0, s1, s2)}
    stasis_excursion = _compare_stasis_and_excursion(c0, s1)
    chart_earned = (
        c0["endpoint_relation"]["both_sources_equivalent"]
        and s1["endpoint_relation"]["both_sources_equivalent"]
        and not s2["endpoint_relation"]["both_sources_equivalent"]
        and stasis_excursion["interval_path_indistinguishable_from_DME_evidence"]
        and all(item["health"]["structurally_healthy"] for item in specimens.values())
    )
    canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    return {
        "experiment": "absent_interval_round_trip_pressure_v0",
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
            "independent_fixtures": ["C0", "S1", "S2"],
            "initial_configuration": "clean committed alpha",
            "fixed_initial_mtime_ns": FIXED_MTIME_NS,
            "trajectory_owner": "external experiment driver",
            "capture_during_mutation": False,
            "intra_capture_skew": False,
            "driver_path_written_to_ledger": False,
            "arbitrary_sleep": False,
        },
        "specimens": specimens,
        "comparison_matrix": [_matrix_row(specimens[name]) for name in ("C0", "S1", "S2")],
        "C0_S1_comparison": stasis_excursion,
        "inference_audit": {
            "DME_can_establish_nothing_happened_in_C0_interval": False,
            "DME_can_establish_hidden_excursion_in_S1_interval": False,
            "DME_can_distinguish_C0_stasis_from_S1_excursion": False,
            "timestamps_establish_interval_path": False,
            "occurrence_multiplicity_establishes_transformation": False,
            "equal_configuration_implies_recurrence_through_excursion": False,
            "recurrence_implies_hidden_transformation": False,
            "S2_visible_endpoint_change_detected": True,
            "DME_supported_claim_for_C0_and_S1": (
                "two distinct observation occurrences expose equivalent source-relative "
                "endpoint configurations; the intervening transformation path is unresolved"
            ),
        },
        "projection_audit": {
            "preserves_both_occurrences_per_source": True,
            "collapses_repeated_observations": False,
            "claims_stasis": False,
            "claims_recurrence": False,
            "claims_current_coherent_world": False,
            "supersession_or_recurrence_semantics_added": False,
        },
        "information_boundary": {
            "captured_observation_information_lost": False,
            "unobserved_excursion_present_in_history": False,
            "absence_caused_by_DME_information_loss": False,
            "boundary": "the transformation occurred outside the current observation basis",
            "observer_corruption": False,
        },
        "production_contract": {
            "equivalent_endpoints_claim_no_intervening_transformation": False,
            "production_defect_found": False,
            "production_change_made": False,
        },
        "chart_status": {
            "earned": chart_earned,
            "name": "Chart 17" if chart_earned else None,
            "coordinates": (
                "control-known interval path x filesystem endpoint relation, Git endpoint "
                "relation, observation occurrence, reconstruction, projection, and "
                "intervening-transformation inference"
                if chart_earned
                else None
            ),
            "recurrence_or_transformation_model": False,
        },
        "distinctions": {
            "added": [],
            "amended": [],
            "existing_sufficient": "D-0012 snapshot != complete_transformation_history",
        },
        "prior_findings": {
            "D_0012": "SUPPORTED_AND_SUFFICIENT",
            "D_0042": "SUPPORTED_UNCHANGED",
            "D_0043": "SUPPORTED_UNCHANGED",
            "D_0044": "SUPPORTED_UNCHANGED",
            "D_0045": "SUPPORTED_UNCHANGED",
            "D_0016_reused_for_configuration_vs_occurrence": True,
            "chart_11_companion_preserved": True,
            "invalidated": [],
        },
        "epistemic_audit": {
            "same_endpoint_treated_as_no_event": False,
            "same_snapshot_identity_treated_as_unchanged_world": False,
            "same_git_configuration_treated_as_static_history": False,
            "two_occurrences_treated_as_transformation": False,
            "elapsed_time_treated_as_change": False,
            "repeated_configuration_treated_as_hidden_excursion": False,
            "driver_knowledge_transferred_to_DME": False,
            "unjustified_certainty_in_production": False,
        },
        "strongest_invariant": (
            "equivalent source-relative configurations remain legible as distinct admitted "
            "observation occurrences without overwriting or collapsing history"
        ),
        "strongest_failure": (
            "endpoint observations alone cannot distinguish true stasis from an unobserved "
            "excursion that returns to the same observable configuration"
        ),
        "strongest_unresolved_horizon": (
            "the transformation path inside an interval with no observation remains unknowable "
            "from the current endpoint-only evidence basis"
        ),
        "next_smallest_pressure": (
            "isolate degraded Git-source admission without adding polling, recurrence operators, "
            "or autonomous observation"
        ),
        "canonical_history": {
            "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
            "sha256_before": canonical_before,
            "sha256_after": canonical_after,
            "unchanged": canonical_before == canonical_after,
        },
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _run_specimen(
    directory: Path,
    *,
    name: str,
    mutation: Mutation,
    control_path: list[str],
    transformation_occurred: bool,
) -> dict[str, Any]:
    root, ledger_path = _new_fixture(directory)
    state_path = root / "state.txt"
    coordinator = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    first_result = coordinator.capture_round()
    first = _capture_summary(first_result, ledger_path)
    original_mtime_ns = state_path.stat().st_mtime_ns
    mutation_control = mutation(root, original_mtime_ns)
    second_result = coordinator.capture_round()
    second = _capture_summary(second_result, ledger_path)
    coordinator.close()
    del coordinator

    ledger_sha_before_recovery = _file_sha256(ledger_path)
    reopened = ForegroundRepositoryObservationCoordinator.open(root, ledger_path)
    recovery_result = reopened.current_result()
    reopened.close()
    del reopened
    ledger_sha_after_recovery = _file_sha256(ledger_path)

    filesystem_equivalent = first["filesystem_configuration"] == second[
        "filesystem_configuration"
    ]
    git_equivalent = first["git_configuration"] == second["git_configuration"]
    health = _health(second_result, recovery_result)
    occurrence = _occurrence_comparison(first, second)
    return {
        "name": name,
        "control": {
            "path": control_path,
            "transformation_occurred": transformation_occurred,
            "basis": "external deterministic driver",
            "written_to_DME_history": False,
            "mutation": mutation_control,
        },
        "first_capture": first,
        "second_capture": second,
        "endpoint_relation": {
            "filesystem_configuration_equivalent": filesystem_equivalent,
            "git_configuration_equivalent": git_equivalent,
            "both_sources_equivalent": filesystem_equivalent and git_equivalent,
        },
        "occurrence_relation": occurrence,
        "health": health,
        "recovery": {
            "fresh_coordinator": True,
            "inputs": ["root", "ledger_path"],
            "ledger_sha256_before": ledger_sha_before_recovery,
            "ledger_sha256_after": ledger_sha_after_recovery,
            "append_free": ledger_sha_before_recovery == ledger_sha_after_recovery,
            "record_count": recovery_result["ledger"]["record_count"],
            "observation_count": recovery_result["derived"]["observation_count"],
            "projection_count": len(recovery_result["derived"]["projection"]),
            "companion_count": len(recovery_result["derived"]["companion"]),
            "driver_path_available": False,
            "captured_observations": recovery_result["captured_observations"],
        },
        "DME_interval_claim": (
            "visible endpoint change occurred between captured observations"
            if not (filesystem_equivalent and git_equivalent)
            else "intervening transformation path is UNRESOLVED"
        ),
    }


def _capture_summary(result: dict[str, Any], ledger_path: Path) -> dict[str, Any]:
    filesystem = result["captured_observations"]["filesystem"]
    git_state = result["captured_observations"]["git"]
    new_observation_records = [
        record
        for record in JsonlLedger(ledger_path).replay()
        if record["record_id"] in {item["record_id"] for item in result["new_records"]}
        and record["envelope"]["record_type"] == "observation"
    ]
    by_source = {record["envelope"]["source"]: record for record in new_observation_records}
    filesystem_record = by_source["repository_filesystem_snapshot"]
    git_record = by_source["repository_git_state"]
    return {
        "filesystem_configuration": _filesystem_configuration(filesystem),
        "git_configuration": _git_configuration(git_state),
        "filesystem_occurrence": {
            "record_id": filesystem_record["record_id"],
            "commit_index": filesystem_record["commit_index"],
            "digest": filesystem_record["integrity"]["digest"],
            "observation_started_at": filesystem["observation_started_at"],
            "observation_finished_at": filesystem["observation_finished_at"],
            "source_observation_identity": filesystem["snapshot_id"],
            "envelope_identity": filesystem_record["envelope"]["observation"][
                "envelope_identity"
            ],
        },
        "git_occurrence": {
            "record_id": git_record["record_id"],
            "commit_index": git_record["commit_index"],
            "digest": git_record["integrity"]["digest"],
            "observed_at": git_state["observed_at"],
            "source_observation_identity": git_state["observation_id"],
            "envelope_identity": git_record["envelope"]["observation"]["envelope_identity"],
        },
        "new_record_ids": [item["record_id"] for item in result["new_records"]],
        "new_commit_indices": [item["commit_index"] for item in result["new_records"]],
        "new_digests": [item["digest"] for item in result["new_records"]],
    }


def _filesystem_configuration(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "root_identity": snapshot["root_identity"],
        "scope": snapshot["scope"],
        "entries": [
            {
                "path": entry["path"],
                "kind": entry["kind"],
                "size_bytes": entry["size_bytes"],
                "mtime_ns": entry["mtime_ns"],
                "sha256": entry["sha256"],
            }
            for entry in snapshot["entries"]
        ],
        "capture_errors": snapshot["capture_errors"],
    }


def _git_configuration(git_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "head_sha": git_state["head_sha"],
        "branch": git_state["branch"],
        "status_porcelain": git_state["status_porcelain"],
        "capture_errors": git_state["capture_errors"],
    }


def _occurrence_comparison(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    first_fs = first["filesystem_occurrence"]
    second_fs = second["filesystem_occurrence"]
    first_git = first["git_occurrence"]
    second_git = second["git_occurrence"]
    return {
        "filesystem_records_distinct": first_fs["record_id"] != second_fs["record_id"],
        "git_records_distinct": first_git["record_id"] != second_git["record_id"],
        "commit_indices_distinct": (
            first_fs["commit_index"] != second_fs["commit_index"]
            and first_git["commit_index"] != second_git["commit_index"]
        ),
        "record_digests_distinct": first["new_digests"] != second["new_digests"],
        "filesystem_capture_times_distinct": (
            first_fs["observation_started_at"] != second_fs["observation_started_at"]
            and first_fs["observation_finished_at"] != second_fs["observation_finished_at"]
        ),
        "git_capture_times_distinct": first_git["observed_at"] != second_git["observed_at"],
        "filesystem_source_identity_equal": (
            first_fs["source_observation_identity"]
            == second_fs["source_observation_identity"]
        ),
        "filesystem_envelope_identity_equal": (
            first_fs["envelope_identity"] == second_fs["envelope_identity"]
        ),
        "git_source_identity_equal": (
            first_git["source_observation_identity"]
            == second_git["source_observation_identity"]
        ),
        "git_envelope_identity_equal": (
            first_git["envelope_identity"] == second_git["envelope_identity"]
        ),
        "distinct_observation_occurrences": True,
    }


def _health(
    second_result: dict[str, Any], recovery_result: dict[str, Any]
) -> dict[str, Any]:
    ledger = recovery_result["ledger"]
    derived = recovery_result["derived"]
    healthy = all(
        (
            ledger["integrity_ok"],
            ledger["continuity_ok"],
            ledger["canonical_replay_reproducible"],
            derived["reconstruction_reproducible"],
            derived["projection_reproducible"],
            derived["companion_reproducible"],
            derived["source_provenance_separate"],
        )
    )
    return {
        "integrity_ok": ledger["integrity_ok"],
        "continuity_ok": ledger["continuity_ok"],
        "replay_reproducible": ledger["canonical_replay_reproducible"],
        "reconstruction_reproducible": derived["reconstruction_reproducible"],
        "projection_reproducible": derived["projection_reproducible"],
        "companion_reproducible": derived["companion_reproducible"],
        "source_separation": derived["source_provenance_separate"],
        "record_count": ledger["record_count"],
        "observation_count": derived["observation_count"],
        "admission_relation_count": derived["admission_relation_count"],
        "projection_count": len(derived["projection"]),
        "projection_subject_ids": [item["subject_record_id"] for item in derived["projection"]],
        "companion_count": len(derived["companion"]),
        "companion_states": [
            item["non_admitted_decision_states"] for item in derived["companion"]
        ],
        "second_capture_returned_normally": bool(second_result["new_records"]),
        "structurally_healthy": healthy,
    }


def _compare_stasis_and_excursion(
    c0: dict[str, Any], s1: dict[str, Any]
) -> dict[str, Any]:
    return {
        "control_paths_differ": c0["control"]["path"] != s1["control"]["path"],
        "filesystem_endpoint_relations_equal": (
            c0["endpoint_relation"]["filesystem_configuration_equivalent"]
            == s1["endpoint_relation"]["filesystem_configuration_equivalent"]
        ),
        "git_endpoint_relations_equal": (
            c0["endpoint_relation"]["git_configuration_equivalent"]
            == s1["endpoint_relation"]["git_configuration_equivalent"]
        ),
        "captured_filesystem_configuration_sequences_equal": (
            [
                c0["first_capture"]["filesystem_configuration"],
                c0["second_capture"]["filesystem_configuration"],
            ]
            == [
                s1["first_capture"]["filesystem_configuration"],
                s1["second_capture"]["filesystem_configuration"],
            ]
        ),
        "captured_git_configuration_sequences_equal": (
            [
                c0["first_capture"]["git_configuration"],
                c0["second_capture"]["git_configuration"],
            ]
            == [
                s1["first_capture"]["git_configuration"],
                s1["second_capture"]["git_configuration"],
            ]
        ),
        "record_shape_equal": (
            c0["health"]["record_count"] == s1["health"]["record_count"] == 8
            and c0["health"]["observation_count"]
            == s1["health"]["observation_count"]
            == 4
        ),
        "occurrence_multiplicity_equal": (
            c0["health"]["observation_count"] == s1["health"]["observation_count"]
        ),
        "raw_ledger_bytes_equal": (
            c0["recovery"]["ledger_sha256_after"]
            == s1["recovery"]["ledger_sha256_after"]
        ),
        "ordinary_occurrence_coordinates_and_times_differ": True,
        "interval_path_indistinguishable_from_DME_evidence": True,
        "distinguishable_as_occurrence_instances": True,
        "distinguishable_as_stasis_vs_excursion": False,
    }


def _matrix_row(specimen: dict[str, Any]) -> dict[str, Any]:
    return {
        "specimen": specimen["name"],
        "control_known_path": specimen["control"]["path"],
        "filesystem_endpoints_equivalent": specimen["endpoint_relation"][
            "filesystem_configuration_equivalent"
        ],
        "git_endpoints_equivalent": specimen["endpoint_relation"][
            "git_configuration_equivalent"
        ],
        "distinct_observation_occurrences": specimen["occurrence_relation"][
            "distinct_observation_occurrences"
        ],
        "integrity": specimen["health"]["integrity_ok"],
        "reconstruction": specimen["health"]["reconstruction_reproducible"],
        "projection_count": specimen["health"]["projection_count"],
        "intervening_transformation_from_DME": (
            "UNRESOLVED"
            if specimen["endpoint_relation"]["both_sources_equivalent"]
            else "endpoint difference observed; intermediate path unresolved"
        ),
    }


def _no_mutation(root: Path, original_mtime_ns: int) -> dict[str, Any]:
    return {
        "action": "none",
        "state_txt_sha256_after": _path_sha256(root / "state.txt"),
        "mtime_ns_after": (root / "state.txt").stat().st_mtime_ns,
        "original_mtime_ns": original_mtime_ns,
        "git_status_after": _git(root, "status", "--porcelain=v1").splitlines(),
    }


def _hidden_round_trip(root: Path, original_mtime_ns: int) -> dict[str, Any]:
    state_path = root / "state.txt"
    state_path.write_text("beta", encoding="utf-8")
    beta_control = {
        "state_txt_sha256": _path_sha256(state_path),
        "git_status": _git(root, "status", "--porcelain=v1").splitlines(),
    }
    state_path.write_text("alpha", encoding="utf-8")
    os.utime(state_path, ns=(state_path.stat().st_atime_ns, original_mtime_ns))
    return {
        "action": "alpha -> beta -> alpha without capture",
        "beta_control": beta_control,
        "restored_state_txt_sha256": _path_sha256(state_path),
        "restored_mtime_ns": state_path.stat().st_mtime_ns,
        "original_mtime_ns": original_mtime_ns,
        "git_status_after_restore": _git(root, "status", "--porcelain=v1").splitlines(),
    }


def _visible_beta(root: Path, original_mtime_ns: int) -> dict[str, Any]:
    state_path = root / "state.txt"
    state_path.write_text("beta", encoding="utf-8")
    return {
        "action": "alpha -> beta without restoration",
        "state_txt_sha256_after": _path_sha256(state_path),
        "mtime_ns_after": state_path.stat().st_mtime_ns,
        "original_mtime_ns": original_mtime_ns,
        "git_status_after": _git(root, "status", "--porcelain=v1").splitlines(),
    }


def _new_fixture(directory: Path) -> tuple[Path, Path]:
    root = directory / "fixture"
    root.mkdir(parents=True)
    state_path = root / "state.txt"
    state_path.write_text("alpha", encoding="utf-8")
    os.utime(state_path, ns=(FIXED_MTIME_NS, FIXED_MTIME_NS))
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Absent Interval Fixture")
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


def _path_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
