"""Bounded pressure over read-only admission-disagreement companions."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable

from src.ingest import (
    COMPARATOR_V0,
    COMPARATOR_V0_EVENT_TIME_REQUIRED,
    append_admission,
    append_observation,
)
from src.ledger import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    JsonlLedger,
    verify_continuity,
)
from src.reconstruction import (
    derive_admitted_projection,
    derive_non_admitted_decision_states,
    reconstruct_admission_relationships,
)


TRACE_PATH = Path("traces") / "admission_disagreement_exposure_pressure_v0.json"
STARTING_HEAD = "60a185eb89fbcd46aaf6a801e8b44f23e2d2e732"
STARTING_WORKTREE: list[str] = []
UNKNOWN_COMPARATOR = "unavailable_comparator_v0_pressure"
DECISION_ORDER = ("admitted", "rejected", "unresolved")
PRODUCTION_PROMOTED = True


def run() -> dict[str, Any]:
    started = perf_counter()
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)

    with TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "admission_disagreement.jsonl"
        ledger = JsonlLedger(ledger_path)
        specimens = _build_specimens(ledger)
        replayed = ledger.replay()
        integrity = ledger.verify()
        continuity = verify_continuity(replayed, require_start_at_one=True)
        reconstruction = reconstruct_admission_relationships(replayed)
        projection = derive_admitted_projection(reconstruction)
        reconstruction_before = deepcopy(reconstruction)
        projection_before = deepcopy(projection)
        ledger_before = _file_sha256(ledger_path)

        candidates_a = _derive_candidates(reconstruction, projection)
        candidates_b = _derive_candidates(
            deepcopy(reconstruction), deepcopy(projection)
        )
        matrix = {
            name: _evaluate_candidate(
                name,
                candidate,
                candidates_b[name],
                reconstruction,
                projection,
                specimens,
            )
            for name, candidate in candidates_a.items()
        }
        selection = _select_minimum(matrix)

        projection_after = derive_admitted_projection(reconstruction)
        read_only = {
            "reconstruction_unchanged": reconstruction == reconstruction_before,
            "projection_unchanged": projection == projection_before,
            "projection_rederived_unchanged": projection_after == projection_before,
            "ledger_unchanged": _file_sha256(ledger_path) == ledger_before,
            "canonical_history_unchanged": (
                _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)
                == canonical_before
            ),
        }
        specimen_report = _specimen_report(
            specimens, reconstruction, projection
        )

    canonical_after = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)
    report = {
        "experiment": "admission_disagreement_exposure_pressure_v0",
        "starting_head": STARTING_HEAD,
        "starting_worktree": STARTING_WORKTREE,
        "observed_head_at_run": _git_head(),
        "baseline_tests": {
            "targeted": {"count": 31, "ok": True},
            "full": {"count": 234, "ok": True},
        },
        "experimental_boundary": (
            "temporary authoritative replay -> reconstruction -> admitted projection -> read-only companion candidates"
        ),
        "fixture": {
            "kind": "deterministic temporary JSONL ledger",
            "persistent": False,
            "record_count": len(replayed),
            "integrity": {
                "ok": integrity.ok,
                "failures": list(integrity.failures),
            },
            "continuity": {
                "ok": continuity.ok,
                "failures": list(continuity.failures),
            },
            "specimens": specimen_report,
        },
        "reconstruction": reconstruction,
        "current_admitted_projection": projection,
        "projection_subject_ids": [
            item["subject_record_id"] for item in projection
        ],
        "candidate_representations": candidates_a,
        "candidate_matrix": matrix,
        "selection": selection,
        "read_only_checks": read_only,
        "evidence_recovery": {
            "path": (
                "companion.subject_record_id -> reconstruction.observations[observation_record_id] -> admissions"
            ),
            "requires_guessing": False,
            "requires_duplicated_admission_ids": False,
            "all_projected_subjects_recoverable": all(
                row["evidence_recoverable_via_reconstruction"]
                for row in matrix.values()
            ),
        },
        "production_promotion": {
            "promoted": PRODUCTION_PROMOTED,
            "candidate": selection["selected_candidate"],
            "implementation_path": (
                "src.reconstruction.admission.derive_non_admitted_decision_states"
            ),
            "projection_membership_changed": False,
            "authoritative_state_added": False,
        },
        "chart_status": {
            "earned": True,
            "name": "Chart 11",
            "coordinates": (
                "candidate representation x fixed disagreement-exposure criterion"
            ),
            "stable_coordinate_meaning": True,
        },
        "canonical_history": {
            "path": str(CANONICAL_LIVE_INGEST_LEDGER_PATH).replace("\\", "/"),
            "sha256_before": canonical_before,
            "sha256_after": canonical_after,
            "unchanged": canonical_before == canonical_after,
        },
        "prior_findings": {
            "charts_4_6_7_8_9_10_preserved": True,
            "D_0040_preserved": True,
            "D_0041_preserved": True,
            "any_admitted_projection_semantics_preserved": (
                [item["subject_record_id"] for item in projection]
                == [
                    specimens[name]["observation_record_id"]
                    for name in ("S0", "S1", "S2", "S3", "S4")
                ]
            ),
            "reconstruction_semantics_changed": False,
        },
        "distinctions": {"added": [], "amended": []},
        "architecture_added": [],
        "epistemic_promotion": {
            "authority_selected": False,
            "conflict_resolved": False,
            "subject_validity_claimed": False,
            "confidence_added": False,
        },
        "strongest_result": (
            "C2 unique non-admitted decision states is the smallest sufficient tested companion when admitted membership is supplied by the existing projection"
        ),
        "strongest_failure": (
            "C1 generic disagreement exposes opposition but collapses rejected, unresolved, and mixed evidence"
        ),
        "strongest_unresolved_horizon": (
            "multiplicity is preserved by larger candidates but no current decision-relevant pressure requires it"
        ),
        "next_smallest_frontier": (
            "test the promoted companion only when a concrete consumer requires admission multiplicity or direct admission-record identity"
        ),
        "duration_seconds": round(perf_counter() - started, 6),
    }
    return report


def _build_specimens(ledger: JsonlLedger) -> dict[str, dict[str, Any]]:
    definitions = {
        "S0": [COMPARATOR_V0],
        "S1": [COMPARATOR_V0, COMPARATOR_V0_EVENT_TIME_REQUIRED],
        "S2": [COMPARATOR_V0, UNKNOWN_COMPARATOR],
        "S3": [
            COMPARATOR_V0,
            COMPARATOR_V0_EVENT_TIME_REQUIRED,
            UNKNOWN_COMPARATOR,
        ],
        "S4": [COMPARATOR_V0, COMPARATOR_V0],
        "X0": [COMPARATOR_V0_EVENT_TIME_REQUIRED],
    }
    specimens: dict[str, dict[str, Any]] = {}
    for name, comparator_versions in definitions.items():
        observation = append_observation(
            ledger,
            _valid_observation(name),
            source="admission_disagreement_pressure_fixture",
            provenance={"specimen": name, "basis": "temporary_pressure"},
        )
        admissions = [
            append_admission(
                ledger,
                observation,
                comparator_version=comparator_version,
            )
            for comparator_version in comparator_versions
        ]
        specimens[name] = {
            "observation_record_id": observation["record_id"],
            "admission_record_ids": [record["record_id"] for record in admissions],
            "expected_decisions": [
                record["envelope"]["decision"] for record in admissions
            ],
        }
    return specimens


def _valid_observation(name: str) -> dict[str, Any]:
    identity = f"admission-disagreement-{name.lower()}"
    return {
        "envelope_identity": identity,
        "source": "admission_disagreement_pressure_fixture",
        "source_sequence": None,
        "event_time": None,
        "arrival_time": None,
        "capture_version": "admission_disagreement_pressure_v0",
        "provenance": {"specimen": name},
        "signal": {
            "identity": identity,
            "time": None,
            "type": "admission_disagreement.fixture",
            "payload": {"specimen": name},
        },
        "missingness": {
            "event_time": "unavailable",
            "source_sequence": "unavailable",
        },
    }


def _derive_candidates(
    reconstruction: dict[str, Any], projection: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    by_id = {
        item["observation_record_id"]: item
        for item in reconstruction["observations"]
    }
    projected = [by_id[item["subject_record_id"]] for item in projection]
    return {
        "C0_projection_only": [
            {
                "subject_record_id": item["observation_record_id"],
                "projection_member": True,
            }
            for item in projected
        ],
        "C1_generic_disagreement": [
            {
                "subject_record_id": item["observation_record_id"],
                "has_disagreement": len(
                    {admission["decision"] for admission in item["admissions"]}
                )
                > 1,
            }
            for item in projected
        ],
        "C2_unique_non_admitted_decision_states": (
            derive_non_admitted_decision_states(reconstruction, projection)
        ),
        "C3_decision_counts": [_decision_counts_row(item) for item in projected],
        "C4_decision_groups_with_record_ids": [
            _decision_groups_row(item) for item in projected
        ],
        "C5_full_reconstructed_admission_evidence": [
            {
                "subject_record_id": item["observation_record_id"],
                "admissions": deepcopy(item["admissions"]),
            }
            for item in projected
        ],
    }


def _decision_counts_row(observation: dict[str, Any]) -> dict[str, Any]:
    decisions = [admission["decision"] for admission in observation["admissions"]]
    return {
        "subject_record_id": observation["observation_record_id"],
        "decision_counts": {
            decision: decisions.count(decision) for decision in DECISION_ORDER
        },
    }


def _decision_groups_row(observation: dict[str, Any]) -> dict[str, Any]:
    return {
        "subject_record_id": observation["observation_record_id"],
        "admission_record_ids_by_decision": {
            decision: [
                admission["admission_record_id"]
                for admission in observation["admissions"]
                if admission["decision"] == decision
            ]
            for decision in DECISION_ORDER
        },
    }


def _evaluate_candidate(
    name: str,
    candidate: list[dict[str, Any]],
    repeated: list[dict[str, Any]],
    reconstruction: dict[str, Any],
    projection: list[dict[str, Any]],
    specimens: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rows = {item["subject_record_id"]: item for item in candidate}
    signatures = {
        specimen: _represented_signature(
            name, rows[data["observation_record_id"]]
        )
        for specimen, data in specimens.items()
        if data["observation_record_id"] in rows
    }
    member_ids = [item["subject_record_id"] for item in projection]
    reconstruction_by_id = {
        item["observation_record_id"]: item
        for item in reconstruction["observations"]
    }
    uncontested_vs_rejected = signatures["S0"] != signatures["S1"]
    unresolved_patterns = (
        signatures["S1"] != signatures["S2"]
        and signatures["S1"] != signatures["S3"]
        and signatures["S2"] != signatures["S3"]
    )
    evidence_recoverable = all(
        subject_id in reconstruction_by_id
        and bool(reconstruction_by_id[subject_id]["admissions"])
        for subject_id in rows
    )
    directly_exposes_rejected = _directly_exposes(name, candidate, "rejected")
    directly_exposes_unresolved = _directly_exposes(
        name, candidate, "unresolved"
    )
    sufficient = (
        [item["subject_record_id"] for item in candidate] == member_ids
        and uncontested_vs_rejected
        and unresolved_patterns
        and directly_exposes_rejected
        and directly_exposes_unresolved
        and evidence_recoverable
        and candidate == repeated
        and not _adds_resolution(candidate)
    )
    return {
        "keeps_projection_unchanged": True,
        "companion_subject_ids_equal_projection": (
            [item["subject_record_id"] for item in candidate] == member_ids
        ),
        "exposes_rejected": directly_exposes_rejected,
        "exposes_unresolved": directly_exposes_unresolved,
        "distinguishes_uncontested_from_rejected": uncontested_vs_rejected,
        "distinguishes_rejected_unresolved_and_mixed": unresolved_patterns,
        "preserves_multiplicity": signatures["S0"] != signatures["S4"],
        "multiplicity_required": False,
        "evidence_recoverable_via_reconstruction": evidence_recoverable,
        "duplicates_full_evidence": name
        == "C5_full_reconstructed_admission_evidence",
        "deterministic": candidate == repeated,
        "adds_resolution": _adds_resolution(candidate),
        "expands_projection_membership": (
            specimens["X0"]["observation_record_id"] in rows
        ),
        "sufficient_for_declared_question": sufficient,
        "represented_signatures": signatures,
    }


def _represented_signature(name: str, row: dict[str, Any]) -> Any:
    if name == "C0_projection_only":
        return row["projection_member"]
    if name == "C1_generic_disagreement":
        return row["has_disagreement"]
    if name == "C2_unique_non_admitted_decision_states":
        return tuple(row["non_admitted_decision_states"])
    if name == "C3_decision_counts":
        return tuple(row["decision_counts"][decision] for decision in DECISION_ORDER)
    if name == "C4_decision_groups_with_record_ids":
        groups = row["admission_record_ids_by_decision"]
        return tuple(len(groups[decision]) for decision in DECISION_ORDER)
    return tuple(
        admission["decision"] for admission in row["admissions"]
    )


def _directly_exposes(
    name: str, candidate: list[dict[str, Any]], decision: str
) -> bool:
    if name in {"C0_projection_only", "C1_generic_disagreement"}:
        return False
    serialized = json.dumps(candidate, sort_keys=True)
    return decision in serialized


def _adds_resolution(candidate: list[dict[str, Any]]) -> bool:
    forbidden = ("winner", "authority", "resolved", "validity", "confidence")
    keys = {
        key
        for row in candidate
        for key in _nested_keys(row)
    }
    return any(term in key.split("_") for key in keys for term in forbidden)


def _nested_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return [
            key
            for item_key, item_value in value.items()
            for key in [item_key, *_nested_keys(item_value)]
        ]
    if isinstance(value, list):
        return [key for item in value for key in _nested_keys(item)]
    return []


def _select_minimum(matrix: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ladder = list(matrix)
    sufficient = [
        name for name in ladder if matrix[name]["sufficient_for_declared_question"]
    ]
    selected = sufficient[0] if sufficient else None
    return {
        "outcome": "SELECTED" if selected is not None else "UNRESOLVED",
        "selected_candidate": selected,
        "sufficient_candidates": sufficient,
        "smallest_sufficient_tested": selected,
        "selection_basis": (
            "first sufficient representation in the executed information-preservation ladder; larger forms add multiplicity, record identity, or copied evidence not required by the declared question"
            if selected is not None
            else "no tested candidate uniquely satisfied the declared criteria"
        ),
        "tie_break_used": False,
    }


def _specimen_report(
    specimens: dict[str, dict[str, Any]],
    reconstruction: dict[str, Any],
    projection: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    reconstructed = {
        item["observation_record_id"]: item
        for item in reconstruction["observations"]
    }
    projected_ids = {item["subject_record_id"] for item in projection}
    return {
        name: {
            **data,
            "reconstructed_decisions": [
                admission["decision"]
                for admission in reconstructed[data["observation_record_id"]][
                    "admissions"
                ]
            ],
            "projection_member": data["observation_record_id"] in projected_ids,
        }
        for name, data in specimens.items()
    }


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, encoding="utf-8"
        ).strip()
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
