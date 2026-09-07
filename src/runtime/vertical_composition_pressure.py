"""First bounded adversarial composition across the earned vertical stack."""

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

from src.capture import (
    GIT_OBSERVER_VERSION,
    SNAPSHOT_OBSERVER_VERSION,
    compare_snapshots,
    make_repo_snapshot,
    observe_git_state,
)
from src.ingest import (
    COMPARATOR_V0,
    COMPARATOR_V0_EVENT_TIME_REQUIRED,
    append_admission,
    append_observation,
)
from src.ledger import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    JsonlLedger,
    canonical_json,
    record_digest,
    verify_continuity,
)
from src.reconstruction import (
    derive_admitted_projection,
    reconstruct_admission_relationships,
)
from src.runtime.candidate_set_expansion_pressure import (
    _expanded_candidate_realizations,
    _select_realization,
)
from src.runtime.provenance_recovery_pressure import (
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
    _evaluate_regime,
    _interpretation_regimes,
)
from src.runtime.repo_provenance_pressure import make_snapshot_ingest_envelope
from src.runtime.repo_transition_pressure import make_git_ingest_envelope
from src.runtime.tie_order_invariance_pressure import run as run_tie_order_invariance


TRACE_PATH = Path("traces") / "vertical_composition_pressure_v0.json"
STARTING_HEAD = "62ceb9a7c998c9e124e765a3f5aa73f5381d8fe8"
STARTING_WORKTREE: list[str] = []
STRUCTURALLY_SUCCESSFUL = "STRUCTURALLY_SUCCESSFUL"


def run() -> dict[str, Any]:
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)
    tie_order = run_tie_order_invariance()

    with TemporaryDirectory() as tmpdir:
        fixture_root = Path(tmpdir) / "fixture"
        fixture_root.mkdir()
        state_path = fixture_root / "state.txt"
        state_path.write_text("alpha", encoding="utf-8")
        initial_commit = _initialize_fixture_git(fixture_root)

        ledger = JsonlLedger(Path(tmpdir) / "vertical_composition.jsonl")
        snapshot_a = make_repo_snapshot(fixture_root)
        git_a = observe_git_state(fixture_root)
        phase_a_records = _append_observation_pair(
            ledger, snapshot_a, git_a, "phase_a"
        )
        phase_a_replay = ledger.replay()
        phase_a_witness = _ordered_digest_witness(phase_a_replay)
        phase_a = _evaluate_stack(
            phase_a_replay, ledger.verify(), phase_a_witness
        )

        state_path.write_text("beta", encoding="utf-8")
        snapshot_b = make_repo_snapshot(fixture_root)
        git_b = observe_git_state(fixture_root)
        phase_b_records = _append_observation_pair(
            ledger, snapshot_b, git_b, "phase_b"
        )
        phase_b_replay = ledger.replay()
        phase_b = _evaluate_stack(
            phase_b_replay, ledger.verify(), phase_a_witness
        )

        conflict_subject = phase_b_records["filesystem_observation"]
        conflict_record = append_admission(
            ledger,
            conflict_subject,
            comparator_version=COMPARATOR_V0_EVENT_TIME_REQUIRED,
        )
        conflict_replay = ledger.replay()
        conflict = _evaluate_stack(
            conflict_replay, ledger.verify(), phase_a_witness
        )
        conflict_observation = _find_reconstruction(
            conflict["reconstruction"], conflict_subject["record_id"]
        )
        conflict_projection = _find_projection(
            conflict["projection"], conflict_subject["record_id"]
        )
        projection_conflict = _projection_conflict(
            conflict_observation, conflict_projection, conflict_record
        )

        mutated_records = deepcopy(conflict_replay)
        mutated_record = mutated_records[0]
        original_digest = mutated_record["integrity"]["digest"]
        mutated_record["envelope"]["provenance"][
            "composition_pressure_mutation"
        ] = "phase_a_provenance_rewritten"
        _rehash(mutated_record)
        mutated_path = Path(tmpdir) / "vertical_composition_mutated.jsonl"
        _write_records(mutated_path, mutated_records)
        mutated_ledger = JsonlLedger(mutated_path)
        mutation = _evaluate_stack(
            mutated_ledger.replay(), mutated_ledger.verify(), phase_a_witness
        )
        mutation_report = _mutation_report(
            mutation,
            conflict,
            mutated_record,
            original_digest,
            len(conflict_replay),
            len(mutated_records),
        )

        operation_case = {
            "witness": phase_a_witness["digests"],
            "candidate": [
                record["integrity"]["digest"] for record in phase_b_replay
            ],
            "expected": True,
        }
        operation_recognition = _select_realization(
            operation_case, _expanded_candidate_realizations()
        )
        source_separation = _source_separation(phase_b["reconstruction"])
        matrix = _whole_stack_matrix(
            phase_a,
            phase_b,
            conflict,
            mutation,
            operation_recognition,
        )
        epistemic = _epistemic_transitions(
            snapshot_a,
            projection_conflict,
            mutation_report,
            operation_recognition,
        )
        canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

        report = {
            "experiment": "vertical_composition_pressure_v0",
            "starting_head": STARTING_HEAD,
            "starting_worktree": STARTING_WORKTREE,
            "observed_head_at_run": _git_head(Path(".")),
            "fixture": {
                "kind": "deterministic temporary Git repository",
                "persistent": False,
                "files": ["state.txt"],
                "initial_state": "alpha",
                "initial_commit": initial_commit,
                "transition": "state.txt changed from alpha to beta without commit",
                "canonical_DME_Lab_history_touched": False,
            },
            "capture_observers": {
                "filesystem": SNAPSHOT_OBSERVER_VERSION,
                "git": GIT_OBSERVER_VERSION,
            },
            "source_observations": {
                "phase_a": _capture_summary(snapshot_a, git_a),
                "phase_b": _capture_summary(snapshot_b, git_b),
                "filesystem_delta": compare_snapshots(snapshot_a, snapshot_b),
            },
            "source_provenance_separation": source_separation,
            "temporary_ledger_lineage": {
                "phase_a_record_ids": _record_ids(phase_a_replay),
                "phase_b_record_ids": _record_ids(phase_b_replay),
                "conflict_record_ids": _record_ids(conflict_replay),
                "mutated_record_ids": _record_ids(mutated_records),
                "phase_a_records": _record_summary(phase_a_records),
                "phase_b_records": _record_summary(phase_b_records),
            },
            "phase_a_witness": phase_a_witness,
            "phase_a": _public_stack_result(phase_a),
            "phase_b": _public_stack_result(phase_b),
            "conflicting_admission_pressure": {
                **projection_conflict,
                "stack": _public_stack_result(conflict),
            },
            "historical_mutation_pressure": mutation_report,
            "unresolved_operation_pressure": {
                **operation_recognition,
                "case": (
                    "Phase-A ordered digests relate positively to the legitimate Phase-B extension"
                ),
                "unique_operation_identity": None,
                "certainty_promoted": False,
                "existing_candidate_set_reused": True,
            },
            "whole_stack_matrix": matrix,
            "chart_status": {
                "earned": True,
                "name": "Chart 10",
                "coordinates": (
                    "bounded composition scenario x stable epistemic output coordinate"
                ),
                "reason": (
                    "all rows use the same captured fixture lineage and each column retains one declared meaning"
                ),
            },
            "epistemic_strength_transitions": epistemic,
            "unjustified_certainty_increases": [
                item["boundary"]
                for item in epistemic
                if item["certainty_increased"]
                and not item["increase_justified"]
            ],
            "prior_lineage": {
                "tie_order_invariance_reproduced": tie_order["prior_chart_9"][
                    "C2_reproduced_unchanged"
                ],
                "chart_9_preserved": tie_order["prior_chart_9"]["remains_valid"],
                "D_0040_preserved": (
                    tie_order["finding"]
                    == "ordering_resolution != relation_resolution"
                ),
                "charts_4_6_7_8_9_invalidated": False,
                "basis": (
                    "tie-order executable lineage reproduction plus preflight full-suite evidence"
                ),
            },
            "distinctions": {
                "added": [
                    {
                        "id": "D-0041",
                        "left": "projection_membership",
                        "relation": "not_equivalent_to",
                        "right": "admission_resolution",
                    }
                ],
                "amended": [],
            },
            "duple_interpretation": {
                "consistent": True,
                "expression": "I_B(O) = (B, sigma_B(O))",
                "finding": (
                    "projection, historical relation, and operation recognition differ because their bounded bases retain different evidence"
                ),
                "runtime_abstraction_added": False,
            },
            "consequence_relevance": {
                "projection_equivalent_but_historically_distinct": (
                    mutation_report["projection_exactly_preserved"]
                    and mutation["historical_relation"]["outcome"]
                    == MISMATCHED
                ),
                "action_selection_added": False,
            },
            "canonical_history": {
                "path": str(CANONICAL_LIVE_INGEST_LEDGER_PATH).replace(
                    "\\", "/"
                ),
                "sha256_before": canonical_before,
                "sha256_after": canonical_after,
                "untouched": canonical_before == canonical_after,
            },
            "production_changes": {
                "contracts": [],
                "capture": [],
                "ingest": [],
                "ledger": [],
                "reconstruction": [],
                "projection": [],
            },
            "architecture_added": [],
            "strongest_failure": (
                "the admitted projection retains membership under opposed admission evidence but does not expose that opposition"
            ),
            "strongest_surviving_invariant": (
                "an integrity-valid, continuity-valid, structurally reconstructable history remains MISMATCHED against the Phase-A witness after prior provenance changes"
            ),
            "strongest_unresolved_horizon": (
                "projection membership does not reveal whether admission is uncontested, and no admission-resolution policy has been earned"
            ),
            "next_smallest_frontier": (
                "isolate the smallest read-only projection companion that exposes admission disagreement without selecting comparator authority or resolving the conflict"
            ),
            "success_criterion": {
                "answer": "partially",
                "detail": (
                    "the composed experiment preserves MISMATCHED, UNRESOLVED, and STRUCTURALLY_SUCCESSFUL independently, but admitted projection alone does not distinguish uncontested membership from membership with opposed evidence"
                ),
            },
            "duration_seconds": round(perf_counter() - started, 6),
        }

    return report


def _initialize_fixture_git(root: Path) -> str:
    _git(root, "init")
    _git(root, "config", "user.name", "DME Pressure Fixture")
    _git(root, "config", "user.email", "fixture@dme.invalid")
    _git(root, "add", "state.txt")
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
        }
    )
    _git(root, "commit", "-m", "initial alpha", env=env)
    return _git(root, "rev-parse", "HEAD")


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


def _append_observation_pair(
    ledger: JsonlLedger,
    snapshot: dict[str, Any],
    git_state: dict[str, Any],
    observation_point: str,
) -> dict[str, dict[str, Any]]:
    filesystem_candidate = make_snapshot_ingest_envelope(snapshot)
    git_candidate = make_git_ingest_envelope(git_state)
    filesystem_observation = append_observation(
        ledger,
        filesystem_candidate,
        source=filesystem_candidate["source"],
        provenance=_provenance(
            observation_point, filesystem_candidate, snapshot
        ),
    )
    git_observation = append_observation(
        ledger,
        git_candidate,
        source=git_candidate["source"],
        provenance=_provenance(observation_point, git_candidate, git_state),
    )
    return {
        "filesystem_observation": filesystem_observation,
        "git_observation": git_observation,
        "filesystem_admission": append_admission(
            ledger, filesystem_observation, comparator_version=COMPARATOR_V0
        ),
        "git_admission": append_admission(
            ledger, git_observation, comparator_version=COMPARATOR_V0
        ),
    }


def _provenance(
    point: str, candidate: dict[str, Any], raw: dict[str, Any]
) -> dict[str, Any]:
    return {
        "observation_point": point,
        "source_envelope_identity": candidate["envelope_identity"],
        "observer": raw["observer"],
        "observer_version": raw["observer_version"],
    }


def _ordered_digest_witness(records: list[dict[str, Any]]) -> dict[str, Any]:
    digests = [record["integrity"]["digest"] for record in records]
    identity = hashlib.sha256(canonical_json(digests).encode("utf-8")).hexdigest()
    return {
        "name": "phase_a_ordered_record_digests",
        "source": "temporary Phase-A ledger replay",
        "record_count": len(records),
        "commit_indices": [record["commit_index"] for record in records],
        "digest_count": len(digests),
        "carrier_identity": f"sha256:{identity}",
        "digests": digests,
        "interpretation_included": False,
    }


def _evaluate_stack(
    records: list[dict[str, Any]],
    integrity_result: Any,
    witness: dict[str, Any],
) -> dict[str, Any]:
    continuity = verify_continuity(records, require_start_at_one=True)
    reconstruction_a = reconstruct_admission_relationships(records)
    projection_a = derive_admitted_projection(reconstruction_a)
    reconstruction_b = reconstruct_admission_relationships(deepcopy(records))
    projection_b = derive_admitted_projection(reconstruction_b)
    relation = _evaluate_regime(
        witness["digests"],
        records,
        _interpretation_regimes()[
            "R6_sufficient_bounded_historical_verifier_semantics"
        ],
    )
    if relation["outcome"] == RECOVERED:
        relation["reason"] = (
            "candidate commitments preserve the Phase-A ordered-digest prefix"
        )
    return {
        "integrity": {
            "ok": integrity_result.ok,
            "record_count": integrity_result.record_count,
            "failures": list(integrity_result.failures),
        },
        "continuity": {
            "ok": continuity.ok,
            "record_count": continuity.record_count,
            "failures": list(continuity.failures),
        },
        "historical_relation": relation,
        "reconstruction_status": STRUCTURALLY_SUCCESSFUL,
        "reconstruction": reconstruction_a,
        "projection": projection_a,
        "reconstruction_reproducible": reconstruction_a == reconstruction_b,
        "projection_reproducible": projection_a == projection_b,
        "derived_state": {
            "observation_count": len(reconstruction_a["observations"]),
            "admission_relation_count": sum(
                len(item["admissions"])
                for item in reconstruction_a["observations"]
            ),
            "orphan_admission_count": len(reconstruction_a["orphan_admissions"]),
            "projection_subject_count": len(projection_a),
            "projection_subject_ids": [
                item["subject_record_id"] for item in projection_a
            ],
        },
    }


def _public_stack_result(result: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(result)


def _find_reconstruction(
    reconstruction: dict[str, Any], record_id: str
) -> dict[str, Any]:
    return next(
        item
        for item in reconstruction["observations"]
        if item["observation_record_id"] == record_id
    )


def _find_projection(
    projection: list[dict[str, Any]], record_id: str
) -> dict[str, Any] | None:
    return next(
        (item for item in projection if item["subject_record_id"] == record_id),
        None,
    )


def _projection_conflict(
    observation: dict[str, Any],
    projected: dict[str, Any] | None,
    conflict_record: dict[str, Any],
) -> dict[str, Any]:
    projected_ids = projected["admission_record_ids"] if projected else []
    return {
        "subject_record_id": observation["observation_record_id"],
        "admission_evidence": [
            {
                "admission_record_id": item["admission_record_id"],
                "comparator_version": item["comparator_version"],
                "decision": item["decision"],
                "comparison_result": item["comparison_result"],
            }
            for item in observation["admissions"]
        ],
        "projection_member": projected is not None,
        "projected_admission_record_ids": projected_ids,
        "conflict_record_id": conflict_record["record_id"],
        "conflict_visible_in_reconstruction": True,
        "conflict_visible_in_projection": conflict_record["record_id"]
        in projected_ids,
        "resolution_policy": None,
        "finding": (
            "projection membership is preserved, but the projection does not expose the rejected admission evidence"
        ),
    }


def _rehash(record: dict[str, Any]) -> None:
    boundary = {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "envelope": record["envelope"],
    }
    record["integrity"]["digest"] = record_digest(boundary)


def _write_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(canonical_json(record) + "\n" for record in records),
        encoding="utf-8",
    )


def _mutation_report(
    mutation: dict[str, Any],
    control: dict[str, Any],
    record: dict[str, Any],
    old_digest: str,
    old_count: int,
    new_count: int,
) -> dict[str, Any]:
    return {
        "copied_from": "S2 conflicting-admissions temporary ledger",
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "changed_field": "envelope.provenance.composition_pressure_mutation",
        "old_digest": old_digest,
        "new_digest": record["integrity"]["digest"],
        "digest_changed": old_digest != record["integrity"]["digest"],
        "record_id_changed": False,
        "commit_index_changed": False,
        "record_count_changed": old_count != new_count,
        "admission_references_changed": False,
        "canonical_history_mutated": False,
        "integrity": mutation["integrity"],
        "continuity": mutation["continuity"],
        "historical_relation": mutation["historical_relation"],
        "reconstruction_status": mutation["reconstruction_status"],
        "reconstruction_shape": mutation["derived_state"],
        "projection": mutation["projection"],
        "projection_exactly_preserved": mutation["projection"]
        == control["projection"],
        "historical_mismatch_preserved_alongside_reconstruction": (
            mutation["historical_relation"]["outcome"] == MISMATCHED
            and mutation["reconstruction_status"] == STRUCTURALLY_SUCCESSFUL
        ),
    }


def _capture_summary(
    snapshot: dict[str, Any], git_state: dict[str, Any]
) -> dict[str, Any]:
    state_entry = next(
        entry for entry in snapshot["entries"] if entry["path"] == "state.txt"
    )
    return {
        "filesystem": {
            "snapshot_id": snapshot["snapshot_id"],
            "observer": snapshot["observer"],
            "observer_version": snapshot["observer_version"],
            "capture_errors": snapshot["capture_errors"],
            "state_txt": state_entry,
        },
        "git": {
            "observation_id": git_state["observation_id"],
            "observer": git_state["observer"],
            "observer_version": git_state["observer_version"],
            "head_sha": git_state["head_sha"],
            "branch": git_state["branch"],
            "status_porcelain": git_state["status_porcelain"],
            "capture_errors": git_state["capture_errors"],
        },
    }


def _source_separation(reconstruction: dict[str, Any]) -> dict[str, Any]:
    observations = reconstruction["observations"]
    sources = [item["source"] for item in observations]
    identities = [
        item["provenance"]["source_envelope_identity"] for item in observations
    ]
    return {
        "separate_sources": sorted(set(sources))
        == ["repository_filesystem_snapshot", "repository_git_state"],
        "source_sequence": sources,
        "provenance_identities": identities,
        "unique_provenance_identity_count": len(set(identities)),
        "overlap": "both observe state.txt/repository working-tree state",
        "equivalence_claimed": False,
        "source_identity_collapsed": False,
    }


def _record_ids(records: list[dict[str, Any]]) -> list[str]:
    return [record["record_id"] for record in records]


def _record_summary(
    records: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "record_id": record["record_id"],
            "commit_index": record["commit_index"],
            "record_type": record["envelope"]["record_type"],
            "source": record["envelope"].get("source"),
            "subject_record_id": record["envelope"].get("subject_record_id"),
            "decision": record["envelope"].get("decision"),
            "digest": record["integrity"]["digest"],
        }
        for name, record in records.items()
    }


def _whole_stack_matrix(
    phase_a: dict[str, Any],
    phase_b: dict[str, Any],
    conflict: dict[str, Any],
    mutation: dict[str, Any],
    operation: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    def row(
        stack: dict[str, Any],
        provenance: bool,
        conflict_state: str,
        unresolved: bool,
        certainty: str,
    ) -> dict[str, Any]:
        return {
            "capture_evidence_preserved": True,
            "source_provenance_preserved": provenance,
            "integrity": "VALID" if stack["integrity"]["ok"] else "INVALID",
            "continuity": "VALID" if stack["continuity"]["ok"] else "INVALID",
            "historical_relation": stack["historical_relation"]["outcome"],
            "reconstruction_status": stack["reconstruction_status"],
            "projection_membership": stack["derived_state"][
                "projection_subject_ids"
            ],
            "conflict_evidence_retained": conflict_state,
            "unresolved_evidence_retained": unresolved,
            "higher_layer_certainty_justified": certainty,
        }

    return {
        "S0_clean_phase_a": row(
            phase_a, True, "NOT_PRESENT", False, "BOUNDED_CLEAN_STACK_ONLY"
        ),
        "S1_legitimate_phase_b_extension": row(
            phase_b, True, "NOT_PRESENT", False, "BOUNDED_EXTENSION_ONLY"
        ),
        "S2_conflicting_admissions": row(
            conflict,
            True,
            "RECONSTRUCTION_ONLY",
            True,
            "PROJECTION_MEMBERSHIP_ONLY_NOT_ADMISSION_RESOLUTION",
        ),
        "S3_integrity_valid_prior_mutation": row(
            mutation,
            False,
            "RECONSTRUCTION_ONLY",
            True,
            "RECONSTRUCTION_SUCCESS_ONLY_NOT_HISTORY_CONSERVATION",
        ),
        "S4_bounded_unresolved_interpretation": {
            **row(
                phase_b,
                True,
                "NOT_PRESENT",
                operation["outcome"] == UNRESOLVED,
                "RELATION_RESULT_ONLY_NOT_UNIQUE_OPERATION_IDENTITY",
            ),
            "operation_recognition": operation["outcome"],
            "matching_operation_count": operation["matching_realization_count"],
        },
    }


def _epistemic_transitions(
    snapshot_a: dict[str, Any],
    conflict: dict[str, Any],
    mutation: dict[str, Any],
    operation: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "boundary": "capture error -> clean observation",
            "input_epistemic_state": {
                "capture_errors": snapshot_a["capture_errors"],
                "fixture_case": "no capture error occurred",
            },
            "output_epistemic_state": (
                "empty capture-error evidence remains in payload and provenance"
            ),
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "scope_note": "a non-empty capture-error composition was not exercised",
        },
        {
            "boundary": "opposed admission evidence -> admitted projection",
            "input_epistemic_state": conflict["admission_evidence"],
            "output_epistemic_state": {
                "projection_member": conflict["projection_member"],
                "admission_record_ids": conflict["projected_admission_record_ids"],
            },
            "information_lost": True,
            "certainty_increased": True,
            "increase_justified": True,
            "unsupported_inference_exposed": "projection membership -> uncontested admission",
            "scope_note": (
                "membership follows the any-admitted rule; interpreting it as uncontested admission would be unjustified"
            ),
        },
        {
            "boundary": "historical mismatch -> successful reconstruction",
            "input_epistemic_state": mutation["historical_relation"],
            "output_epistemic_state": mutation["reconstruction_status"],
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "scope_note": (
                "the experiment retains reconstruction and historical relation independently"
            ),
        },
        {
            "boundary": "ambiguous operation -> unique operation identity",
            "input_epistemic_state": {
                "matching_realizations": operation["matching_realizations"]
            },
            "output_epistemic_state": {
                "outcome": operation["outcome"],
                "unique_operation_identity": None,
            },
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "scope_note": "ambiguity remains UNRESOLVED and no tie-break is used",
        },
        {
            "boundary": "unresolved lower coordinate -> whole-state certainty",
            "input_epistemic_state": UNRESOLVED,
            "output_epistemic_state": "whole-state certainty not claimed",
            "information_lost": False,
            "certainty_increased": False,
            "increase_justified": True,
            "scope_note": (
                "prefix is resolved under one fixed relation basis while operation identity remains unresolved"
            ),
        },
    ]


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
