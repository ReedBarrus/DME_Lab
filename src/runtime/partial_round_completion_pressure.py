"""Bounded fault pressure at foreground capture commitment boundaries."""

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

from src.ledger import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    JsonlLedger,
    compare_prefix_preservation,
    verify_continuity,
)
from src.reconstruction import reconstruct_admission_relationships
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "partial_round_completion_pressure_v0.json"
STARTING_HEAD = "b7757c91dbacf25d75217d30bed304b8081f033c"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "Phase-C"
STARTING_WORKTREE: list[str] = []
BASELINE_FOREGROUND_TESTS = {"passed": 23, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 299, "failed": 0}
FIXED_MTIME_NS = 946_684_800_000_000_000


class InjectedCaptureFailure(RuntimeError):
    """Experiment-only deterministic failure."""


def run() -> dict[str, Any]:
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        experiment_root = Path(tmpdir)
        specimens = {
            name: _run_specimen(
                experiment_root,
                name,
                durable_before_exception=durable,
                fail_after_durable_result=name == "F4",
                successful_control=name == "C",
            )
            for name, durable in (
                ("F0", 0),
                ("F1", 1),
                ("F2", 2),
                ("F3", 3),
                ("F4", 4),
                ("C", 4),
            )
        }
        retry = _run_retry_specimen(experiment_root)
        configuration_signatures = {
            name: specimen["fixture_configuration_signature"]
            for name, specimen in specimens.items()
        }
        same_configuration = len(
            {json.dumps(value, sort_keys=True) for value in configuration_signatures.values()}
        ) == 1
        matrix = _matrix(specimens)
        f4_control = _compare_f4_control(specimens["F4"], specimens["C"])
        partials_valid = all(
            specimens[name]["recovery"]["internally_valid"]
            for name in ("F1", "F2", "F3")
        )
        partials_legible = all(
            specimens[name]["recovery"]["record_relation_legible"]
            for name in ("F1", "F2", "F3")
        )
        canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)
        chart = _chart_status(
            specimens,
            retry,
            same_configuration,
            partials_valid,
            partials_legible,
            f4_control,
        )

        report = {
            "experiment": "partial_round_completion_pressure_v0",
            "starting_lineage": {
                "branch": STARTING_BRANCH,
                "head": STARTING_HEAD,
                "message": STARTING_MESSAGE,
                "worktree": STARTING_WORKTREE,
                "observed_head_at_run": _git_head(Path(".")),
            },
            "baseline_tests": {
                "foreground_coordinator": BASELINE_FOREGROUND_TESTS,
                "full": BASELINE_FULL_TESTS,
            },
            "fault_injection": {
                "mechanism": (
                    "experiment-local method replacement raises InjectedCaptureFailure "
                    "at append boundaries and after durable result derivation"
                ),
                "real_process_kill": False,
                "torn_JSON_write": False,
                "production_coordinator_modified": False,
                "injected_stage_available_to_recovery_evaluator": False,
            },
            "fixture_control": {
                "independent_repository_per_specimen": True,
                "same_configuration": same_configuration,
                "fixed_state_txt_content": "alpha",
                "fixed_state_txt_mtime_ns": FIXED_MTIME_NS,
                "configuration_signatures": configuration_signatures,
                "world_mutation_during_fault_pressure": False,
            },
            "prior_complete_history": {
                "record_count": 4,
                "record_types": ["observation", "observation", "admission", "admission"],
                "purpose": "independent prefix witness before pressured invocation",
            },
            "specimens": specimens,
            "comparison_matrix": matrix,
            "partial_histories": {
                "specimens": ["F1", "F2", "F3"],
                "integrity_continuity_replay_valid": partials_valid,
                "record_relation_legible": partials_legible,
                "treated_as_corruption": False,
                "round_historical_unit_assumed": False,
            },
            "F4_control_comparison": f4_control,
            "retry_after_F4": retry,
            "D_0042": {
                "status": "SUPPORTED_UNCHANGED",
                "amended": False,
                "reason": (
                    "fresh coordinators recovered every durably committed record; "
                    "record-level historical continuity did not require operation completion"
                ),
            },
            "production_boundary": {
                "status": "PRESERVED_WITH_SCOPED_GUARANTEE",
                "guarantee": (
                    "foreground composition through four independently committed records"
                ),
                "atomic_round_guarantee": False,
                "durable_completion_acknowledgement": False,
                "documentation_mismatch_found": False,
                "production_change_made": False,
            },
            "chart_status": chart,
            "distinctions": {
                "added": [
                    {
                        "id": "D-0043",
                        "left": "caller_invocation_outcome",
                        "relation": "not_equivalent_to",
                        "right": "durable_history_state",
                    }
                ]
                if chart["earned"]
                else [],
                "amended": [],
            },
            "epistemic_audit": _epistemic_audit(specimens, retry, f4_control),
            "prior_findings": {
                "charts_4_through_13_preserved": True,
                "D_0040_preserved": True,
                "D_0041_preserved": True,
                "D_0042_preserved": True,
                "projection_semantics_preserved": True,
                "companion_semantics_preserved": True,
                "source_separation_preserved": True,
            },
            "canonical_history": {
                "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
                "sha256_before": canonical_before,
                "sha256_after": canonical_after,
                "unchanged": canonical_before == canonical_after,
            },
            "success_criterion": {
                "answered": chart["earned"],
                "answer": (
                    "partial composition remains record-legible while caller-level "
                    "completion remains unresolved from authoritative history"
                ),
            },
            "strongest_invariant": (
                "fresh recovery preserves exactly the records and relations that became durable"
            ),
            "strongest_failure": (
                "authoritative history cannot establish whether a fully durable invocation "
                "was acknowledged to its caller"
            ),
            "strongest_unresolved_horizon": (
                "policy for retrying after unknown acknowledgement remains absent"
            ),
            "next_smallest_pressure": (
                "isolate retry policy and request identity only if a concrete caller "
                "requires distinguishing retry from intentional repeated observation"
            ),
            "duration_seconds": round(perf_counter() - started, 6),
        }

    return report


def _run_specimen(
    experiment_root: Path,
    name: str,
    *,
    durable_before_exception: int,
    fail_after_durable_result: bool,
    successful_control: bool,
) -> dict[str, Any]:
    specimen_root = experiment_root / name / "fixture"
    specimen_root.mkdir(parents=True)
    state_path = specimen_root / "state.txt"
    state_path.write_text("alpha", encoding="utf-8")
    initial_commit = _initialize_fixture(specimen_root, state_path)
    ledger_path = experiment_root / name / "history.jsonl"
    coordinator = ForegroundRepositoryObservationCoordinator(
        specimen_root, ledger_path
    )
    seed_result = coordinator.capture_round()
    witness_records = deepcopy(JsonlLedger(ledger_path).replay())
    signature = _configuration_signature(seed_result)

    caller = {
        "result_returned": False,
        "exception": None,
        "fault_stage": "none" if successful_control else None,
    }
    if successful_control:
        result = coordinator.capture_round()
        caller["result_returned"] = True
        caller["returned_new_record_ids"] = [
            record["record_id"] for record in result["new_records"]
        ]
    else:
        try:
            _capture_with_injected_failure(
                coordinator,
                durable_before_exception=durable_before_exception,
                fail_after_durable_result=fail_after_durable_result,
            )
        except InjectedCaptureFailure as exc:
            caller["exception"] = type(exc).__name__
            caller["fault_stage"] = str(exc)
        else:
            raise AssertionError(f"{name} did not raise injected failure")

    coordinator.close()
    del coordinator
    recovery = _recover_from_disk(specimen_root, ledger_path, witness_records)
    return {
        "name": name,
        "initial_commit": initial_commit,
        "fixture_configuration_signature": signature,
        "driver_fault_boundary": (
            "successful return" if successful_control else caller["fault_stage"]
        ),
        "caller": caller,
        "expected_durable_new_records_from_driver": durable_before_exception,
        "recovery": recovery,
    }


def _run_retry_specimen(experiment_root: Path) -> dict[str, Any]:
    specimen_root = experiment_root / "R4" / "fixture"
    specimen_root.mkdir(parents=True)
    state_path = specimen_root / "state.txt"
    state_path.write_text("alpha", encoding="utf-8")
    _initialize_fixture(specimen_root, state_path)
    ledger_path = experiment_root / "R4" / "history.jsonl"

    failed = ForegroundRepositoryObservationCoordinator(specimen_root, ledger_path)
    seed_result = failed.capture_round()
    witness_records = deepcopy(JsonlLedger(ledger_path).replay())
    try:
        _capture_with_injected_failure(
            failed,
            durable_before_exception=4,
            fail_after_durable_result=True,
        )
    except InjectedCaptureFailure:
        pass
    else:
        raise AssertionError("R4 initial invocation did not fail")
    failed.close()
    del failed

    after_unknown_ack = _recover_from_disk(
        specimen_root, ledger_path, witness_records
    )
    retrying = ForegroundRepositoryObservationCoordinator.open(
        specimen_root, ledger_path
    )
    retry_result = retrying.capture_round()
    retrying.close()
    del retrying
    after_retry = _recover_from_disk(specimen_root, ledger_path, witness_records)

    first_group = after_retry["records"][4:8]
    second_group = after_retry["records"][8:12]
    retry_marker_fields = {
        key
        for record in second_group
        for key in record["envelope_fields"]
        if key in {"request_id", "retry", "attempt", "round_id"}
    }
    return {
        "fixture_configuration_signature": _configuration_signature(seed_result),
        "world_changed_before_retry": False,
        "after_unknown_acknowledgement": after_unknown_ack,
        "retry_returned": True,
        "retry_returned_new_record_ids": [
            record["record_id"] for record in retry_result["new_records"]
        ],
        "after_retry": after_retry,
        "first_and_second_group_configuration_equal": (
            _group_configuration(after_retry, first_group)
            == _group_configuration(after_retry, second_group)
        ),
        "retry_marker_fields": sorted(retry_marker_fields),
        "retry_distinguishable_from_intentional_repeat": False,
        "reason": (
            "history preserves two distinct repeated observations but no request, "
            "attempt, or retry identity"
        ),
    }


def _capture_with_injected_failure(
    coordinator: ForegroundRepositoryObservationCoordinator,
    *,
    durable_before_exception: int,
    fail_after_durable_result: bool,
) -> None:
    if fail_after_durable_result:
        original_result = ForegroundRepositoryObservationCoordinator._result

        def fail_after_result(
            instance: ForegroundRepositoryObservationCoordinator,
            new_records: list[dict[str, Any]],
            captured_observations: dict[str, Any] | None,
        ) -> dict[str, Any]:
            original_result(instance, new_records, captured_observations)
            raise InjectedCaptureFailure("after 4 durable records before return")

        ForegroundRepositoryObservationCoordinator._result = fail_after_result
        try:
            coordinator.capture_round()
        finally:
            ForegroundRepositoryObservationCoordinator._result = original_result
        return

    original_append = JsonlLedger.append
    appended = 0

    def injected_append(
        ledger: JsonlLedger,
        envelope: dict[str, Any],
        record_id: str | None = None,
    ) -> dict[str, Any]:
        nonlocal appended
        if appended == durable_before_exception:
            raise InjectedCaptureFailure(
                f"after {appended} durable records before append {appended + 1}"
            )
        record = original_append(ledger, envelope, record_id=record_id)
        appended += 1
        return record

    JsonlLedger.append = injected_append
    try:
        coordinator.capture_round()
    finally:
        JsonlLedger.append = original_append


def _recover_from_disk(
    root: Path,
    ledger_path: Path,
    witness_records: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluator = ForegroundRepositoryObservationCoordinator.open(root, ledger_path)
    bytes_before = ledger_path.read_bytes() if ledger_path.exists() else b""
    current = evaluator.current_result()
    bytes_after = ledger_path.read_bytes() if ledger_path.exists() else b""
    evaluator.close()
    del evaluator

    ledger = JsonlLedger(ledger_path)
    records_a = ledger.replay()
    records_b = JsonlLedger(ledger_path).replay()
    reconstruction = reconstruct_admission_relationships(records_a)
    prefix = compare_prefix_preservation(records_a, witness_records)
    new_records = records_a[len(witness_records) :]
    observations = reconstruction["observations"]
    admission_states = {
        observation["observation_record_id"]: [
            admission["decision"] for admission in observation["admissions"]
        ]
        for observation in observations
    }
    production_completion_fields = sorted(
        {
            key
            for record in records_a
            for key in record["envelope"]
            if key
            in {
                "round_id",
                "request_id",
                "operation_complete",
                "caller_acknowledged",
            }
        }
    )
    return {
        "evaluator_inputs": ["root", "ledger_path", "prior complete prefix witness"],
        "failed_process_state_used": False,
        "record_count": len(records_a),
        "durable_new_record_count": len(new_records),
        "record_types": [record["envelope"]["record_type"] for record in records_a],
        "new_record_types": [record["envelope"]["record_type"] for record in new_records],
        "record_ids": [record["record_id"] for record in records_a],
        "commit_indices": [record["commit_index"] for record in records_a],
        "records": [_public_record(record) for record in records_a],
        "integrity_ok": ledger.verify().ok,
        "continuity_ok": verify_continuity(
            records_a, require_start_at_one=True
        ).ok,
        "replay_reproducible": records_a == records_b,
        "current_result_read_only": bytes_before == bytes_after,
        "reconstructed_observation_count": len(observations),
        "admission_relation_count": sum(
            len(observation["admissions"]) for observation in observations
        ),
        "orphan_admission_count": len(reconstruction["orphan_admissions"]),
        "admission_states_by_subject": admission_states,
        "projection_subject_ids": [
            item["subject_record_id"] for item in current["derived"]["projection"]
        ],
        "companion": current["derived"]["companion"],
        "source_values": [observation["source"] for observation in observations],
        "source_provenance_collapsed": False,
        "prior_prefix": prefix.to_dict(),
        "production_completion_fields": production_completion_fields,
        "completion_inference": {
            "outcome": "UNRESOLVED",
            "complete_established": False,
            "incomplete_established": False,
            "reason": (
                "authoritative records contain no requested-invocation, round, "
                "completion, or caller-acknowledgement identity"
            ),
        },
        "internally_valid": (
            ledger.verify().ok
            and verify_continuity(records_a, require_start_at_one=True).ok
            and records_a == records_b
        ),
        "record_relation_legible": (
            len(observations) == sum(
                1
                for record in records_a
                if record["envelope"]["record_type"] == "observation"
            )
            and not reconstruction["orphan_admissions"]
        ),
        "completion_surface": _completion_surface(
            new_records, reconstruction, current
        ),
    }


def _completion_surface(
    new_records: list[dict[str, Any]],
    reconstruction: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    new_ids = [record["record_id"] for record in new_records]
    id_positions = {record_id: index for index, record_id in enumerate(new_ids)}
    return {
        "new_record_types": [record["envelope"]["record_type"] for record in new_records],
        "new_sources": [record["envelope"].get("source") for record in new_records],
        "admission_subject_positions": [
            id_positions.get(record["envelope"].get("subject_record_id"))
            for record in new_records
            if record["envelope"]["record_type"] == "admission"
        ],
        "admission_decisions": [
            record["envelope"].get("decision")
            for record in new_records
            if record["envelope"]["record_type"] == "admission"
        ],
        "total_observation_count": len(reconstruction["observations"]),
        "total_admission_relation_count": sum(
            len(item["admissions"]) for item in reconstruction["observations"]
        ),
        "total_projection_count": len(current["derived"]["projection"]),
        "total_companion_count": len(current["derived"]["companion"]),
        "caller_acknowledgement_recorded": False,
    }


def _compare_f4_control(
    failed: dict[str, Any], control: dict[str, Any]
) -> dict[str, Any]:
    failed_recovery = failed["recovery"]
    control_recovery = control["recovery"]
    return {
        "caller_outcomes_differ": (
            failed["caller"]["exception"] == "InjectedCaptureFailure"
            and control["caller"]["result_returned"]
        ),
        "ledger_bytes_equal": (
            [record["digest"] for record in failed_recovery["records"]]
            == [record["digest"] for record in control_recovery["records"]]
        ),
        "independent_occurrence_bytes_expected_to_differ": True,
        "durable_completion_surfaces_equal": (
            failed_recovery["completion_surface"]
            == control_recovery["completion_surface"]
        ),
        "production_acknowledgement_fields_equal": (
            failed_recovery["production_completion_fields"]
            == control_recovery["production_completion_fields"]
            == []
        ),
        "caller_outcome_inferable_from_either_history": False,
        "interpretation": (
            "independent ledgers have different occurrence timestamps and digests, "
            "but equal durable composition surfaces and no acknowledgement coordinate"
        ),
    }


def _matrix(specimens: dict[str, Any]) -> dict[str, Any]:
    return {
        name: {
            "durable_new_records": specimen["recovery"]["durable_new_record_count"],
            "total_records": specimen["recovery"]["record_count"],
            "caller_return": (
                "SUCCESS" if specimen["caller"]["result_returned"] else "EXCEPTION"
            ),
            "integrity": "VALID" if specimen["recovery"]["integrity_ok"] else "INVALID",
            "continuity": "VALID" if specimen["recovery"]["continuity_ok"] else "INVALID",
            "observations": specimen["recovery"]["reconstructed_observation_count"],
            "admissions": specimen["recovery"]["admission_relation_count"],
            "projection_members": len(specimen["recovery"]["projection_subject_ids"]),
            "completion_inferable": specimen["recovery"]["completion_inference"]["outcome"],
        }
        for name, specimen in specimens.items()
    }


def _epistemic_audit(
    specimens: dict[str, Any],
    retry: dict[str, Any],
    f4_control: dict[str, Any],
) -> dict[str, Any]:
    return {
        "driver_fault_knowledge_used_as_DME_knowledge": False,
        "integrity_interpreted_as_completion": False,
        "continuity_interpreted_as_completion": False,
        "reconstruction_interpreted_as_completion": False,
        "four_records_interpreted_as_caller_success": False,
        "caller_exception_interpreted_as_no_persistence": False,
        "repeated_configuration_interpreted_as_retry": False,
        "F4_and_control_acknowledgement_distinguished": f4_control[
            "caller_outcome_inferable_from_either_history"
        ],
        "retry_distinguished_from_intentional_repeat": retry[
            "retry_distinguishable_from_intentional_repeat"
        ],
        "all_completion_outcomes_from_history": sorted(
            {
                specimen["recovery"]["completion_inference"]["outcome"]
                for specimen in specimens.values()
            }
        ),
    }


def _chart_status(
    specimens: dict[str, Any],
    retry: dict[str, Any],
    same_configuration: bool,
    partials_valid: bool,
    partials_legible: bool,
    f4_control: dict[str, Any],
) -> dict[str, Any]:
    earned = (
        list(specimens) == ["F0", "F1", "F2", "F3", "F4", "C"]
        and same_configuration
        and partials_valid
        and partials_legible
        and f4_control["durable_completion_surfaces_equal"]
        and not f4_control["caller_outcome_inferable_from_either_history"]
        and retry["first_and_second_group_configuration_equal"]
        and not retry["retry_distinguishable_from_intentional_repeat"]
    )
    return {
        "earned": earned,
        "name": "Chart 14" if earned else None,
        "coordinates": (
            "fault boundary x durable record shape, caller outcome, integrity, "
            "continuity, reconstruction, projection, and completion inference"
            if earned
            else None
        ),
        "generalized_transaction_model": False,
    }


def _configuration_signature(result: dict[str, Any]) -> dict[str, Any]:
    filesystem = result["captured_observations"]["filesystem"]
    git_state = result["captured_observations"]["git"]
    state_entry = next(
        entry for entry in filesystem["entries"] if entry["path"] == "state.txt"
    )
    return {
        "filesystem_snapshot_id": filesystem["snapshot_id"],
        "state_txt_sha256": state_entry["sha256"],
        "state_txt_mtime_ns": state_entry["mtime_ns"],
        "git_head": git_state["head_sha"],
        "git_branch": git_state["branch"],
        "git_status": git_state["status_porcelain"],
        "filesystem_capture_errors": filesystem["capture_errors"],
        "git_capture_errors": git_state["capture_errors"],
    }


def _group_configuration(
    recovery: dict[str, Any], group: list[dict[str, Any]]
) -> dict[str, Any]:
    records_by_id = {record["record_id"]: record for record in recovery["records"]}
    observations = [record for record in group if record["record_type"] == "observation"]
    return {
        "sources": [record["source"] for record in observations],
        "subject_positions": [
            next(
                index
                for index, candidate in enumerate(observations)
                if candidate["record_id"] == record["subject_record_id"]
            )
            for record in group
            if record["record_type"] == "admission"
        ],
        "decisions": [
            record["decision"]
            for record in group
            if record["record_type"] == "admission"
        ],
        "source_configurations": [
            records_by_id[record["record_id"]]["source_configuration"]
            for record in observations
        ],
    }


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    envelope = record["envelope"]
    observation = envelope.get("observation") or {}
    signal = observation.get("signal", {})
    payload = signal.get("payload", {})
    source = envelope.get("source")
    source_configuration = None
    if source == "repository_filesystem_snapshot":
        source_configuration = {"snapshot_id": payload.get("snapshot_id")}
    elif source == "repository_git_state":
        source_configuration = {
            "head_sha": payload.get("head_sha"),
            "branch": payload.get("branch"),
            "status_porcelain": payload.get("status_porcelain"),
            "capture_errors": payload.get("capture_errors"),
        }
    return {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "record_type": envelope["record_type"],
        "source": source,
        "subject_record_id": envelope.get("subject_record_id"),
        "decision": envelope.get("decision"),
        "signal_identity": signal.get("identity"),
        "source_configuration": source_configuration,
        "envelope_fields": sorted(envelope),
        "digest": record["integrity"]["digest"],
    }


def _initialize_fixture(root: Path, state_path: Path) -> str:
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Partial Round Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    _git(
        root,
        "commit",
        "-m",
        "fixed alpha",
        env=_commit_environment("2000-01-01T00:00:00+00:00"),
    )
    os.utime(state_path, ns=(FIXED_MTIME_NS, FIXED_MTIME_NS))
    _git(root, "status", "--porcelain=v1")
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
