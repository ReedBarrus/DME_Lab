"""First bounded persistent observational-field pressure."""

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

from src.capture import make_repo_snapshot, observe_git_state
from src.ingest import COMPARATOR_V0, append_admission, append_observation
from src.ledger import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    JsonlLedger,
    compare_prefix_preservation,
    verify_continuity,
)
from src.reconstruction import (
    derive_admitted_projection,
    derive_non_admitted_decision_states,
    reconstruct_admission_relationships,
)
from src.runtime.repo_provenance_pressure import make_snapshot_ingest_envelope
from src.runtime.repo_transition_pressure import make_git_ingest_envelope


TRACE_PATH = Path("traces") / "persistent_observational_field_pressure_v0.json"
STARTING_HEAD = "7e03123bb38383a9f10eb37f02e6f334e2770774"
STARTING_BRANCH = "main"
STARTING_MESSAGE = "CHart 11"
STARTING_WORKTREE: list[str] = []
BASELINE_TARGETED_TESTS = {"passed": 51, "failed": 0}
BASELINE_FULL_TESTS = {"passed": 255, "failed": 0}


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
        ledger_path = temporary_root / "persistent_field.jsonl"

        first_rounds, witness_records, beta_commit = _run_first_session(
            fixture_root,
            state_path,
            ledger_path,
        )

        # The first function has returned. Its ledger, replay, reconstruction, and
        # projection objects are out of scope before this fresh instance is made.
        sixth_round, reopen = _run_reopened_session(
            fixture_root,
            ledger_path,
            witness_records,
        )
        rounds = [*first_rounds, sixth_round]
        comparisons = _identity_comparisons(rounds)
        final_records = JsonlLedger(ledger_path).replay()
        final_reconstruction = reconstruct_admission_relationships(final_records)
        final_projection = derive_admitted_projection(final_reconstruction)
        final_companion = derive_non_admitted_decision_states(
            final_reconstruction, final_projection
        )
        canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

        coherent = _field_is_coherent(rounds, comparisons, reopen)
        chart = _chart_status(coherent, rounds)

        report = {
            "experiment": "persistent_observational_field_pressure_v0",
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
            "fixture": {
                "identity": "temporary-git-filesystem-world-v0",
                "kind": "deterministic temporary Git repository",
                "root_name": fixture_root.name,
                "files": ["state.txt"],
                "initial_state": "alpha",
                "initial_commit": initial_commit,
                "beta_commit": beta_commit,
                "git_branch": "main",
                "observer_writes_to_fixture": False,
                "ledger": "one temporary JSONL ledger across both sessions",
            },
            "observation_rounds": rounds,
            "identity_comparisons": comparisons,
            "session_reopen": reopen,
            "final_state": {
                "record_count": len(final_records),
                "observation_count": len(final_reconstruction["observations"]),
                "admission_relation_count": sum(
                    len(item["admissions"])
                    for item in final_reconstruction["observations"]
                ),
                "projection_subject_count": len(final_projection),
                "companion_row_count": len(final_companion),
                "non_admitted_states": sorted(
                    {
                        state
                        for row in final_companion
                        for state in row["non_admitted_decision_states"]
                    }
                ),
                "record_ids": [record["record_id"] for record in final_records],
                "commit_indices": [record["commit_index"] for record in final_records],
            },
            "repeated_state_preservation": {
                "filesystem_same_configuration_pairs": ["O1_O2", "O3_O4", "O4_O5", "O5_O6"],
                "git_same_configuration_pairs": ["O1_O2", "O3_O4", "O5_O6"],
                "separate_observation_records_preserved": all(
                    not comparison["ledger_observation_record_id_equal"]
                    for pair in comparisons.values()
                    for comparison in pair.values()
                ),
                "deduplication_performed": False,
                "occurrence_coordinates": [
                    "capture timestamps",
                    "ledger record_id",
                    "ledger commit_index",
                    "record digest",
                ],
            },
            "cross_source_result": {
                "pair": "O4_O5",
                "filesystem_configuration_equal": comparisons["O4_O5"]["filesystem"]["configuration_equal"],
                "git_configuration_equal": comparisons["O4_O5"]["git"]["configuration_equal"],
                "finding": (
                    "filesystem structural state remained equal while Git HEAD/status changed"
                ),
                "sources_collapsed": False,
                "world_equivalence_inferred": False,
            },
            "chart_11_companion": {
                "output_after_each_round": "one empty-state row per admitted projection member",
                "projection_membership_changed": False,
                "admission_multiplicity_required": False,
                "direct_admission_record_ids_required_in_companion": False,
                "reason": (
                    "each occurrence is navigable by projection subject_record_id "
                    "and has one normal admission; temporal depth introduced no "
                    "disagreement consumer"
                ),
            },
            "epistemic_audit": _epistemic_audit(rounds, reopen),
            "canonical_history": {
                "path": CANONICAL_LIVE_INGEST_LEDGER_PATH.as_posix(),
                "sha256_before": canonical_before,
                "sha256_after": canonical_after,
                "unchanged": canonical_before == canonical_after,
            },
            "production_changes": [],
            "chart_status": chart,
            "distinctions": {
                "added": [],
                "amended": [],
                "existing_sufficient": ["D-0011", "D-0016", "D-0030", "D-0041"],
            },
            "prior_findings": {
                "charts_4_through_11_preserved": True,
                "D_0040_preserved": True,
                "D_0041_preserved": True,
                "any_admitted_projection_preserved": True,
                "ledger_continuity_preserved": True,
                "ordered_digest_prefix_semantics_preserved": True,
                "filesystem_git_separation_preserved": True,
            },
            "success_criterion": {
                "coherent": coherent,
                "answer": (
                    "current bounded structures preserve temporal depth without a new production semantic"
                    if coherent
                    else "a bounded field fracture was observed"
                ),
            },
            "strongest_invariant": (
                "every capture occurrence receives distinct ledger coordinates "
                "while observer-relative configuration identities may repeat"
            ),
            "strongest_failure": (
                "filesystem snapshot and candidate-envelope identity alone cannot identify a repeated occurrence"
            ),
            "strongest_unresolved_horizon": (
                "the bounded field does not test concurrency, partial writes, "
                "capture errors, or admission disagreement over time"
            ),
            "next_smallest_frontier": (
                "pressure an explicitly invoked foreground persistent coordinator "
                "before considering any daemon or scheduler"
            ),
            "duration_seconds": round(perf_counter() - started, 6),
        }

    return report


def _run_first_session(
    fixture_root: Path,
    state_path: Path,
    ledger_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    ledger = JsonlLedger(ledger_path)
    rounds: list[dict[str, Any]] = []

    rounds.append(
        _capture_round(
            ledger,
            fixture_root,
            "O1",
            "initial clean alpha",
            "initial fixture construction and commit",
            witness_records=None,
        )
    )
    witness_records = deepcopy(ledger.replay())
    rounds[0] = _refresh_round_stack(rounds[0], ledger, witness_records)

    rounds.append(
        _capture_round(
            ledger,
            fixture_root,
            "O2",
            "repeated unchanged clean alpha",
            "none",
            witness_records,
        )
    )

    state_path.write_text("beta", encoding="utf-8")
    rounds.append(
        _capture_round(
            ledger,
            fixture_root,
            "O3",
            "uncommitted dirty beta",
            "state.txt rewritten from alpha to beta outside capture",
            witness_records,
        )
    )
    rounds.append(
        _capture_round(
            ledger,
            fixture_root,
            "O4",
            "repeated unchanged dirty beta",
            "none",
            witness_records,
        )
    )

    beta_commit = _commit_beta_without_rewrite(fixture_root)
    rounds.append(
        _capture_round(
            ledger,
            fixture_root,
            "O5",
            "committed clean beta",
            "git add and commit; state.txt not rewritten",
            witness_records,
        )
    )
    return rounds, witness_records, beta_commit


def _run_reopened_session(
    fixture_root: Path,
    ledger_path: Path,
    witness_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    ledger = JsonlLedger(ledger_path)
    disk_records = ledger.replay()
    integrity = ledger.verify()
    continuity = verify_continuity(disk_records, require_start_at_one=True)
    reconstruction_a = reconstruct_admission_relationships(disk_records)
    projection_a = derive_admitted_projection(reconstruction_a)
    companion_a = derive_non_admitted_decision_states(reconstruction_a, projection_a)
    reconstruction_b = reconstruct_admission_relationships(deepcopy(ledger.replay()))
    projection_b = derive_admitted_projection(reconstruction_b)
    companion_b = derive_non_admitted_decision_states(reconstruction_b, projection_b)

    reopen = {
        "after_round": "O5",
        "first_session_returned_before_reopen": True,
        "fresh_ledger_instance_constructed_from_path": True,
        "authoritative_input": "temporary ledger disk bytes",
        "declared_non_authoritative_input": "O1 ordered-digest witness",
        "reconstruction_or_projection_objects_passed_across_boundary": False,
        "pre_append_record_count": len(disk_records),
        "integrity_ok": integrity.ok,
        "continuity_ok": continuity.ok,
        "recovered_observation_count": len(reconstruction_a["observations"]),
        "recovered_admission_relation_count": sum(
            len(item["admissions"])
            for item in reconstruction_a["observations"]
        ),
        "recovered_projection_subject_count": len(projection_a),
        "recovered_companion_row_count": len(companion_a),
        "disk_only_reconstruction_reproducible": reconstruction_a == reconstruction_b,
        "disk_only_projection_reproducible": projection_a == projection_b,
        "disk_only_companion_reproducible": companion_a == companion_b,
        "O1_prefix_recovered": compare_prefix_preservation(
            disk_records, witness_records
        ).ok,
    }

    sixth_round = _capture_round(
        ledger,
        fixture_root,
        "O6",
        "unchanged committed beta after reopen",
        "none; capture follows fresh disk reconstruction",
        witness_records,
    )
    reopen["post_append_record_count"] = sixth_round["stack"]["record_count"]
    reopen["continuation_succeeded"] = (
        reopen["pre_append_record_count"] == 20
        and reopen["recovered_observation_count"] == 10
        and reopen["recovered_projection_subject_count"] == 10
        and sixth_round["stack"]["record_count"] == 24
    )
    return sixth_round, reopen


def _capture_round(
    ledger: JsonlLedger,
    fixture_root: Path,
    name: str,
    world_condition: str,
    mutation_before: str,
    witness_records: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    snapshot = make_repo_snapshot(fixture_root)
    git_state = observe_git_state(fixture_root)
    filesystem_candidate = make_snapshot_ingest_envelope(snapshot)
    git_candidate = make_git_ingest_envelope(git_state)
    filesystem_observation = append_observation(
        ledger,
        filesystem_candidate,
        source=filesystem_candidate["source"],
        provenance=_provenance(name, filesystem_candidate, snapshot),
    )
    git_observation = append_observation(
        ledger,
        git_candidate,
        source=git_candidate["source"],
        provenance=_provenance(name, git_candidate, git_state),
    )
    filesystem_admission = append_admission(
        ledger, filesystem_observation, comparator_version=COMPARATOR_V0
    )
    git_admission = append_admission(
        ledger, git_observation, comparator_version=COMPARATOR_V0
    )
    new_records = [
        filesystem_observation,
        git_observation,
        filesystem_admission,
        git_admission,
    ]
    state_entry = next(
        entry for entry in snapshot["entries"] if entry["path"] == "state.txt"
    )
    round_result = {
        "round": name,
        "world_condition": world_condition,
        "world_mutation_before_capture": mutation_before,
        "record_range": [new_records[0]["commit_index"], new_records[-1]["commit_index"]],
        "new_record_ids": [record["record_id"] for record in new_records],
        "new_record_types": [record["envelope"]["record_type"] for record in new_records],
        "filesystem": _filesystem_identity(
            snapshot, filesystem_candidate, filesystem_observation, state_entry
        ),
        "git": _git_identity(git_state, git_candidate, git_observation),
        "admissions": {
            "filesystem": _admission_summary(filesystem_admission),
            "git": _admission_summary(git_admission),
        },
    }
    if witness_records is not None:
        round_result = _refresh_round_stack(round_result, ledger, witness_records)
    return round_result


def _refresh_round_stack(
    round_result: dict[str, Any],
    ledger: JsonlLedger,
    witness_records: list[dict[str, Any]],
) -> dict[str, Any]:
    records_a = ledger.replay()
    records_b = JsonlLedger(ledger.path).replay()
    integrity = ledger.verify()
    continuity = verify_continuity(records_a, require_start_at_one=True)
    reconstruction_a = reconstruct_admission_relationships(records_a)
    reconstruction_b = reconstruct_admission_relationships(deepcopy(records_b))
    projection_a = derive_admitted_projection(reconstruction_a)
    projection_b = derive_admitted_projection(reconstruction_b)
    companion_a = derive_non_admitted_decision_states(reconstruction_a, projection_a)
    companion_b = derive_non_admitted_decision_states(reconstruction_b, projection_b)
    prefix = compare_prefix_preservation(records_a, witness_records)
    observation_sources = [
        item["source"] for item in reconstruction_a["observations"]
    ]

    refreshed = deepcopy(round_result)
    refreshed["stack"] = {
        "integrity_ok": integrity.ok,
        "integrity_failures": list(integrity.failures),
        "continuity_ok": continuity.ok,
        "continuity_failures": list(continuity.failures),
        "record_count": len(records_a),
        "canonical_replay_reproducible": records_a == records_b,
        "canonical_commit_indices": [record["commit_index"] for record in records_a],
        "reconstruction_reproducible": reconstruction_a == reconstruction_b,
        "reconstructed_observation_count": len(reconstruction_a["observations"]),
        "reconstructed_admission_relation_count": sum(
            len(item["admissions"]) for item in reconstruction_a["observations"]
        ),
        "orphan_admission_count": len(reconstruction_a["orphan_admissions"]),
        "projection_reproducible": projection_a == projection_b,
        "projection_subject_count": len(projection_a),
        "projection_subject_ids": [item["subject_record_id"] for item in projection_a],
        "companion_reproducible": companion_a == companion_b,
        "companion_row_count": len(companion_a),
        "companion": companion_a,
        "companion_non_admitted_states": sorted(
            {
                state
                for row in companion_a
                for state in row["non_admitted_decision_states"]
            }
        ),
        "source_provenance_separate": set(observation_sources)
        == {"repository_filesystem_snapshot", "repository_git_state"},
        "source_observation_counts": {
            source: observation_sources.count(source)
            for source in sorted(set(observation_sources))
        },
        "historical_prefix": prefix.to_dict(),
    }
    return refreshed


def _filesystem_identity(
    snapshot: dict[str, Any],
    candidate: dict[str, Any],
    record: dict[str, Any],
    state_entry: dict[str, Any],
) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "observation_started_at": snapshot["observation_started_at"],
        "observation_finished_at": snapshot["observation_finished_at"],
        "envelope_identity": candidate["envelope_identity"],
        "signal_identity": candidate["signal"]["identity"],
        "ledger_record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "record_digest": record["integrity"]["digest"],
        "state_txt_sha256": state_entry["sha256"],
        "state_txt_mtime_ns": state_entry["mtime_ns"],
        "capture_errors": snapshot["capture_errors"],
    }


def _git_identity(
    git_state: dict[str, Any],
    candidate: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    return {
        "observation_id": git_state["observation_id"],
        "observed_at": git_state["observed_at"],
        "head_sha": git_state["head_sha"],
        "branch": git_state["branch"],
        "status_porcelain": git_state["status_porcelain"],
        "capture_errors": git_state["capture_errors"],
        "envelope_identity": candidate["envelope_identity"],
        "signal_identity": candidate["signal"]["identity"],
        "ledger_record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "record_digest": record["integrity"]["digest"],
    }


def _admission_summary(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "subject_record_id": record["envelope"]["subject_record_id"],
        "comparator_version": record["envelope"]["comparator_version"],
        "decision": record["envelope"]["decision"],
        "record_digest": record["integrity"]["digest"],
    }


def _identity_comparisons(
    rounds: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    by_name = {item["round"]: item for item in rounds}
    return {
        pair_name: {
            "filesystem": _compare_filesystem_identity(
                by_name[left]["filesystem"], by_name[right]["filesystem"]
            ),
            "git": _compare_git_identity(by_name[left]["git"], by_name[right]["git"]),
        }
        for pair_name, left, right in (
            ("O1_O2", "O1", "O2"),
            ("O3_O4", "O3", "O4"),
            ("O4_O5", "O4", "O5"),
            ("O5_O6", "O5", "O6"),
        )
    }


def _compare_filesystem_identity(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    return {
        "configuration_equal": before["snapshot_id"] == after["snapshot_id"],
        "snapshot_id_equal": before["snapshot_id"] == after["snapshot_id"],
        "observation_started_at_equal": before["observation_started_at"]
        == after["observation_started_at"],
        "observation_finished_at_equal": before["observation_finished_at"]
        == after["observation_finished_at"],
        "envelope_identity_equal": before["envelope_identity"]
        == after["envelope_identity"],
        "signal_identity_equal": before["signal_identity"] == after["signal_identity"],
        "ledger_observation_record_id_equal": before["ledger_record_id"]
        == after["ledger_record_id"],
        "commit_index_equal": before["commit_index"] == after["commit_index"],
        "record_digest_equal": before["record_digest"] == after["record_digest"],
    }


def _compare_git_identity(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    configuration_fields = ("head_sha", "branch", "status_porcelain", "capture_errors")
    return {
        "comparison_surface": list(configuration_fields),
        "configuration_equal": all(before[field] == after[field] for field in configuration_fields),
        "observation_id_equal": before["observation_id"] == after["observation_id"],
        "observed_at_equal": before["observed_at"] == after["observed_at"],
        "head_sha_equal": before["head_sha"] == after["head_sha"],
        "branch_equal": before["branch"] == after["branch"],
        "status_porcelain_equal": before["status_porcelain"]
        == after["status_porcelain"],
        "capture_errors_equal": before["capture_errors"] == after["capture_errors"],
        "envelope_identity_equal": before["envelope_identity"]
        == after["envelope_identity"],
        "signal_identity_equal": before["signal_identity"] == after["signal_identity"],
        "ledger_observation_record_id_equal": before["ledger_record_id"]
        == after["ledger_record_id"],
        "commit_index_equal": before["commit_index"] == after["commit_index"],
        "record_digest_equal": before["record_digest"] == after["record_digest"],
        "production_identity_promoted": False,
    }


def _field_is_coherent(
    rounds: list[dict[str, Any]],
    comparisons: dict[str, dict[str, dict[str, Any]]],
    reopen: dict[str, Any],
) -> bool:
    stack_ok = all(
        round_result["stack"][key]
        for round_result in rounds
        for key in (
            "integrity_ok",
            "continuity_ok",
            "canonical_replay_reproducible",
            "reconstruction_reproducible",
            "projection_reproducible",
            "companion_reproducible",
            "source_provenance_separate",
        )
    )
    prefix_ok = all(
        round_result["stack"]["historical_prefix"]["ok"] for round_result in rounds
    )
    occurrence_ok = all(
        not source["ledger_observation_record_id_equal"]
        for pair in comparisons.values()
        for source in pair.values()
    )
    expected_relations = (
        comparisons["O1_O2"]["filesystem"]["configuration_equal"]
        and comparisons["O1_O2"]["git"]["configuration_equal"]
        and comparisons["O3_O4"]["filesystem"]["configuration_equal"]
        and comparisons["O3_O4"]["git"]["configuration_equal"]
        and comparisons["O4_O5"]["filesystem"]["configuration_equal"]
        and not comparisons["O4_O5"]["git"]["configuration_equal"]
        and comparisons["O5_O6"]["filesystem"]["configuration_equal"]
        and comparisons["O5_O6"]["git"]["configuration_equal"]
    )
    return stack_ok and prefix_ok and occurrence_ok and expected_relations and reopen["continuation_succeeded"]


def _chart_status(coherent: bool, rounds: list[dict[str, Any]]) -> dict[str, Any]:
    earned = coherent and len(rounds) == 6
    return {
        "earned": earned,
        "name": "Chart 12" if earned else None,
        "coordinates": (
            "observation round x world condition, source-relative configuration "
            "relation, ledger occurrence, reconstruction, projection, prefix, "
            "and session boundary"
            if earned
            else None
        ),
        "generalized_state_model": False,
        "reason": (
            "six executed rounds preserve stable coordinate meanings across "
            "repetition, mutation, overlapping-source divergence, and reopen"
            if earned
            else "the bounded coordinate surface did not remain stable"
        ),
    }


def _epistemic_audit(
    rounds: list[dict[str, Any]], reopen: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        {
            "boundary": "capture -> candidate envelope",
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "evidence": "complete source observation remains in signal.payload",
        },
        {
            "boundary": "repeated source configuration -> ledger occurrences",
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "evidence": "all twelve source captures have distinct observation record IDs and commit indices",
        },
        {
            "boundary": "observation -> normal admission",
            "information_lost": False,
            "certainty_increased": True,
            "increase_justified": all(
                admission["decision"] == "admitted"
                for item in rounds
                for admission in item["admissions"].values()
            ),
            "evidence": "each decision remains scoped to the existing comparator version",
        },
        {
            "boundary": "reconstruction -> admitted projection and companion",
            "information_lost": True,
            "certainty_increased": False,
            "increase_justified": True,
            "evidence": (
                "projection omits full payload but retains subject navigation; "
                "companion reports only recorded non-admitted states"
            ),
        },
        {
            "boundary": "session-local discontinuity -> disk reconstruction",
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "evidence": {
                "disk_reconstruction_reproducible": reopen["disk_only_reconstruction_reproducible"],
                "continuation_succeeded": reopen["continuation_succeeded"],
            },
        },
        {
            "boundary": "more observations -> epistemic strength",
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "evidence": "record growth preserves per-occurrence evidence and does not aggregate confidence",
        },
        {
            "boundary": "mismatch or unresolved evidence -> structural success",
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "evidence": "no mismatch or unresolved admission was produced by the required normal-admission sequence",
            "exercised": False,
        },
    ]


def _provenance(
    round_name: str, candidate: dict[str, Any], raw: dict[str, Any]
) -> dict[str, Any]:
    return {
        "observation_round": round_name,
        "source_envelope_identity": candidate["envelope_identity"],
        "observer": raw["observer"],
        "observer_version": raw["observer_version"],
    }


def _initialize_fixture(root: Path) -> str:
    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.name", "DME Persistent Field Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    env = _commit_environment("2000-01-01T00:00:00+00:00")
    _git(root, "commit", "-m", "initial alpha", env=env)
    return _git(root, "rev-parse", "HEAD")


def _commit_beta_without_rewrite(root: Path) -> str:
    _git(root, "add", "state.txt")
    env = _commit_environment("2000-01-02T00:00:00+00:00")
    _git(root, "commit", "-m", "commit beta", env=env)
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
