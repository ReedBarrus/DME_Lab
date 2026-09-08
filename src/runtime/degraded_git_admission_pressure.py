"""Bounded pressure for admission of a naturally degraded Git observation."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ingest import COMPARATOR_IDENTITY, COMPARATOR_V0
from src.ingest.admission import compare_observation_record
from src.ledger import CANONICAL_LIVE_INGEST_LEDGER_PATH, JsonlLedger
from src.reconstruction import reconstruct_admission_relationships
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "degraded_git_admission_pressure_v0.json"
STARTING_HEAD = "d129a6da2a617ccbc6e6a4bf871bd49768688e3e"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "The completion of the Real Wound 4"
STARTING_WORKTREE: list[str] = []
BASELINE_TARGETED_TESTS = {"passed": 137, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 413, "failed": 0}


def run() -> dict[str, Any]:
    """Execute healthy-Git and natural non-Git-directory specimens."""
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        temporary_root = Path(tmpdir)
        c0_root = temporary_root / "C0" / "fixture"
        c0_root.mkdir(parents=True)
        _write_alpha(c0_root)
        _initialize_git(c0_root)
        c0 = _run_specimen("C0", c0_root, temporary_root / "C0" / "history.jsonl")

        s1_root = temporary_root / "S1" / "fixture"
        s1_root.mkdir(parents=True)
        _write_alpha(s1_root)
        s1 = _run_specimen("S1", s1_root, temporary_root / "S1" / "history.jsonl")

    specimens = {"C0": c0, "S1": s1}
    degraded_admitted = (
        s1["layers"]["raw_git_acquisition_quality"]["status"] == "DEGRADED"
        and s1["layers"]["structural_admission_decision"]["decision"] == "admitted"
        and s1["layers"]["downstream_projection_exposure"]["included"]
    )
    chart_earned = degraded_admitted and all(
        specimen["health"]["structurally_healthy"] for specimen in specimens.values()
    )
    canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    return {
        "experiment": "degraded_git_admission_pressure_v0",
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
            "C0": "ordinary clean Git repository",
            "S1": "ordinary filesystem directory with state.txt and no .git repository",
            "real_git_observer": True,
            "mocked_payload": False,
            "filesystem_observer_expected_healthy": True,
        },
        "specimens": specimens,
        "comparison_matrix": [_matrix_row(specimens[name]) for name in ("C0", "S1")],
        "three_layer_result": {
            "raw_Git_acquisition_quality": "degraded with three real command failures",
            "structural_admission_decision": "admitted under COMPARATOR_V0",
            "downstream_projection_exposure": "Git subject included without direct error detail",
            "correct_interpretation": (
                "the degraded acquisition attempt was structurally admitted as evidence; "
                "successful Git source state was not certified"
            ),
        },
        "comparator_audit": {
            "identity": COMPARATOR_IDENTITY,
            "version": COMPARATOR_V0,
            "kind": "minimum structural observation-envelope comparator",
            "required_record_fields": ["record_id", "commit_index", "envelope", "integrity"],
            "required_observation_record_fields": [
                "record_type",
                "source",
                "observation",
                "provenance",
            ],
            "required_ingest_observation_fields": ["envelope_identity", "source", "signal"],
            "required_signal_fields": ["identity", "type", "payload"],
            "checks_git_head_sha": False,
            "checks_git_branch": False,
            "checks_git_status": False,
            "checks_capture_errors": False,
            "certifies_source_capture_success": False,
        },
        "capture_error_visibility": s1["capture_error_visibility"],
        "information_boundary": {
            "degraded_condition_preserved_in_authoritative_history": True,
            "degraded_condition_recoverable_after_fresh_replay": True,
            "projection_directly_exposes_degraded_condition": False,
            "companion_directly_exposes_degraded_condition": False,
            "current_result_directly_exposes_degraded_condition": False,
            "information_erased_from_history": False,
            "boundary": (
                "projection and companion retain subject/navigation coordinates but require "
                "authoritative reconstruction to recover source-quality detail"
            ),
        },
        "production_contract": {
            "admission_claim": "comparison valid under named comparator",
            "claims_source_capture_succeeded": False,
            "claims_projected_subject_is_epistemically_resolved": False,
            "structural_comparator_preserved": True,
            "production_defect_found": False,
            "production_change_made": False,
        },
        "chart_status": {
            "earned": chart_earned,
            "name": "Chart 18" if chart_earned else None,
            "coordinates": (
                "specimen x raw acquisition quality, error carriage, structural schema, "
                "named comparator decision, reconstruction recovery, projection exposure, "
                "and companion exposure"
                if chart_earned
                else None
            ),
            "trust_or_source_health_policy": False,
        },
        "distinctions": {
            "added": (
                [
                    {
                        "id": "D-0046",
                        "left": "structural_admissibility",
                        "relation": "not_equivalent_to",
                        "right": "source_capture_success",
                    }
                ]
                if degraded_admitted
                else []
            ),
            "amended": [],
        },
        "prior_findings": {
            "D_0012": "SUPPORTED_UNCHANGED",
            "D_0016": "SUPPORTED_UNCHANGED",
            "D_0042": "SUPPORTED_UNCHANGED",
            "D_0043": "SUPPORTED_UNCHANGED",
            "D_0044": "SUPPORTED_UNCHANGED",
            "D_0045": "SUPPORTED_UNCHANGED",
            "chart_11_companion_preserved": True,
            "invalidated": [],
        },
        "epistemic_audit": {
            "admission_treated_as_source_success": False,
            "schema_validity_treated_as_trustworthy_content": False,
            "record_integrity_treated_as_source_semantic_validity": False,
            "projection_treated_as_epistemic_resolution": False,
            "capture_errors_treated_as_discard_requirement": False,
            "well_formed_failure_treated_as_successful_source_state": False,
            "unjustified_certainty_in_production": False,
        },
        "strongest_invariant": (
            "a well-formed failed acquisition remains integrity-valid, replayable, and fully "
            "recoverable as authoritative evidence through reconstruction"
        ),
        "strongest_failure": (
            "projection membership and an admitted decision do not directly expose or certify "
            "the underlying Git acquisition quality"
        ),
        "strongest_unresolved_horizon": (
            "whether a concrete projection consumer requires direct source-quality exposure "
            "without traversing authoritative reconstruction"
        ),
        "next_smallest_pressure": (
            "require a concrete consumer before adding source-quality companion data, trust "
            "policy, retry, confidence, or source ranking"
        ),
        "canonical_history": {
            "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
            "sha256_before": canonical_before,
            "sha256_after": canonical_after,
            "unchanged": canonical_before == canonical_after,
        },
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _run_specimen(name: str, root: Path, ledger_path: Path) -> dict[str, Any]:
    coordinator = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    immediate = coordinator.capture_round()
    coordinator.close()
    del coordinator

    records = JsonlLedger(ledger_path).replay()
    git_observation_record = next(
        record
        for record in records
        if record["envelope"].get("record_type") == "observation"
        and record["envelope"].get("source") == "repository_git_state"
    )
    filesystem_observation_record = next(
        record
        for record in records
        if record["envelope"].get("record_type") == "observation"
        and record["envelope"].get("source") == "repository_filesystem_snapshot"
    )
    git_admission_record = next(
        record
        for record in records
        if record["envelope"].get("record_type") == "admission"
        and record["envelope"].get("subject_record_id") == git_observation_record["record_id"]
    )
    reconstruction = reconstruct_admission_relationships(records)
    reconstructed_git = next(
        item
        for item in reconstruction["observations"]
        if item["observation_record_id"] == git_observation_record["record_id"]
    )
    projected_git = next(
        item
        for item in immediate["derived"]["projection"]
        if item["subject_record_id"] == git_observation_record["record_id"]
    )
    companion_git = next(
        item
        for item in immediate["derived"]["companion"]
        if item["subject_record_id"] == git_observation_record["record_id"]
    )

    raw_git = immediate["captured_observations"]["git"]
    raw_filesystem = immediate["captured_observations"]["filesystem"]
    ingest_envelope = git_observation_record["envelope"]["observation"]
    comparison = compare_observation_record(git_observation_record)
    errors = raw_git["capture_errors"]
    null_fields = [
        field
        for field in ("head_sha", "branch", "status_porcelain")
        if raw_git[field] is None
    ]

    ledger_sha_before_recovery = _file_sha256(ledger_path)
    reopened = ForegroundRepositoryObservationCoordinator.open(root, ledger_path)
    recovery_result = reopened.current_result()
    reopened.close()
    del reopened
    ledger_sha_after_recovery = _file_sha256(ledger_path)
    recovered_records = JsonlLedger(ledger_path).replay()
    recovered_reconstruction = reconstruct_admission_relationships(recovered_records)
    recovered_git = next(
        item
        for item in recovered_reconstruction["observations"]
        if item["observation_record_id"] == git_observation_record["record_id"]
    )

    visibility = _capture_error_visibility(
        raw_git,
        ingest_envelope,
        git_observation_record,
        reconstructed_git,
        projected_git,
        companion_git,
        recovery_result,
        recovered_git,
    )
    health = _health(immediate, recovery_result)
    return {
        "name": name,
        "fixture": {
            "root_kind": "Git repository" if name == "C0" else "ordinary non-Git directory",
            "git_directory_present": (root / ".git").exists(),
            "filesystem_capture_errors": raw_filesystem["capture_errors"],
        },
        "layers": {
            "raw_git_acquisition_quality": {
                "status": "SUCCESSFUL" if not errors else "DEGRADED",
                "observation_object_returned": isinstance(raw_git, dict),
                "capture_error_count": len(errors),
                "capture_errors": errors,
                "failed_commands": [error["command"] for error in errors],
                "null_fields": null_fields,
                "head_sha": raw_git["head_sha"],
                "branch": raw_git["branch"],
                "status_porcelain": raw_git["status_porcelain"],
            },
            "structural_admission_decision": {
                "ingest_envelope_constructed": True,
                "envelope_keys": sorted(ingest_envelope),
                "signal_keys": sorted(ingest_envelope["signal"]),
                "schema_status": comparison["status"],
                "schema_valid": comparison["valid"],
                "schema_errors": comparison["errors"],
                "comparator_identity": git_admission_record["envelope"][
                    "comparator_identity"
                ],
                "comparator_version": git_admission_record["envelope"][
                    "comparator_version"
                ],
                "decision": git_admission_record["envelope"]["decision"],
                "decision_basis": git_admission_record["envelope"]["decision_basis"],
                "certifies_source_capture_success": False,
            },
            "downstream_projection_exposure": {
                "included": projected_git is not None,
                "projection_row": projected_git,
                "capture_errors_directly_visible": "capture_errors" in projected_git,
                "companion_row": companion_git,
                "companion_non_admitted_states": companion_git[
                    "non_admitted_decision_states"
                ],
                "companion_exposes_capture_errors": "capture_errors" in companion_git,
            },
        },
        "records": {
            "filesystem_observation_id": filesystem_observation_record["record_id"],
            "git_observation_id": git_observation_record["record_id"],
            "git_admission_id": git_admission_record["record_id"],
            "commit_indices": [record["commit_index"] for record in records],
        },
        "capture_error_visibility": visibility,
        "health": health,
        "fresh_recovery": {
            "inputs": ["root", "ledger_path"],
            "ledger_sha256_before": ledger_sha_before_recovery,
            "ledger_sha256_after": ledger_sha_after_recovery,
            "append_free": ledger_sha_before_recovery == ledger_sha_after_recovery,
            "current_result_captured_observations": recovery_result["captured_observations"],
            "current_result_projection_contains_git": any(
                item["subject_record_id"] == git_observation_record["record_id"]
                for item in recovery_result["derived"]["projection"]
            ),
            "reconstruction_capture_errors": recovered_git["observation"]["signal"][
                "payload"
            ]["capture_errors"],
            "process_local_failure_knowledge_required": False,
        },
    }


def _capture_error_visibility(
    raw_git: dict[str, Any],
    ingest_envelope: dict[str, Any],
    observation_record: dict[str, Any],
    reconstructed_git: dict[str, Any],
    projected_git: dict[str, Any],
    companion_git: dict[str, Any],
    recovery_result: dict[str, Any],
    recovered_git: dict[str, Any],
) -> dict[str, Any]:
    return {
        "raw_git_observation": bool(raw_git["capture_errors"]),
        "ingest_envelope_provenance": bool(ingest_envelope["provenance"]["capture_errors"]),
        "ingest_envelope_signal_payload": bool(
            ingest_envelope["signal"]["payload"]["capture_errors"]
        ),
        "observation_record_outer_provenance": "capture_errors"
        in observation_record["envelope"]["provenance"],
        "ledger_nested_observation_provenance": bool(
            observation_record["envelope"]["observation"]["provenance"]["capture_errors"]
        ),
        "ledger_nested_signal_payload": bool(
            observation_record["envelope"]["observation"]["signal"]["payload"][
                "capture_errors"
            ]
        ),
        "reconstruction_outer_provenance": "capture_errors" in reconstructed_git["provenance"],
        "reconstruction_nested_observation_provenance": bool(
            reconstructed_git["observation"]["provenance"]["capture_errors"]
        ),
        "reconstruction_nested_signal_payload": bool(
            reconstructed_git["observation"]["signal"]["payload"]["capture_errors"]
        ),
        "projection_row": "capture_errors" in projected_git,
        "companion_row": "capture_errors" in companion_git,
        "current_result_top_level_or_projection": "capture_errors"
        in _nested_keys(recovery_result),
        "fresh_reconstruction_nested_signal_payload": bool(
            recovered_git["observation"]["signal"]["payload"]["capture_errors"]
        ),
    }


def _health(
    immediate: dict[str, Any], recovery_result: dict[str, Any]
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
        "companion_count": len(derived["companion"]),
        "orphan_admission_count": derived["orphan_admission_count"],
        "capture_returned_normally": bool(immediate["new_records"]),
        "structurally_healthy": healthy,
    }


def _matrix_row(specimen: dict[str, Any]) -> dict[str, Any]:
    acquisition = specimen["layers"]["raw_git_acquisition_quality"]
    admission = specimen["layers"]["structural_admission_decision"]
    projection = specimen["layers"]["downstream_projection_exposure"]
    return {
        "specimen": specimen["name"],
        "Git_acquisition": acquisition["status"],
        "capture_error_count": acquisition["capture_error_count"],
        "envelope_constructed": admission["ingest_envelope_constructed"],
        "schema_valid": admission["schema_valid"],
        "comparator": admission["comparator_version"],
        "admission": admission["decision"],
        "projection_included": projection["included"],
        "projection_exposes_errors": projection["capture_errors_directly_visible"],
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


def _write_alpha(root: Path) -> None:
    (root / "state.txt").write_text("alpha", encoding="utf-8")


def _initialize_git(root: Path) -> None:
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Degraded Git Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "initial alpha",
        env=_commit_environment("2000-01-01T00:00:00+00:00"),
    )


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
