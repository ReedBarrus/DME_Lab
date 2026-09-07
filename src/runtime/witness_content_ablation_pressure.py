"""Bounded witness-content ablation pressure run."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any, Callable

from src.ledger import (
    HASH_BOUNDARY,
    INTEGRITY_ALGORITHM,
    compare_prefix_preservation,
    history_extent,
    prefix_identity,
    record_digest,
    verify_continuity,
)
from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships
from src.runtime.historical_relation_pressure import (
    GIT_H14_COMMIT,
    build_specimens,
    load_git_h14_records,
    make_h16_replacement,
)
from src.runtime.history_extent_witness_pressure import verify_records_with_jsonl


TRACE_PATH = Path("traces") / "witness_content_ablation_pressure_v0.json"

EXPECTED_CAPABILITY = {
    "H13_tail_loss": False,
    "H14_control": True,
    "H16_extension": True,
    "H16_ID_replacement": False,
    "H16_content_replacement": False,
}


def make_h16_content_replacement(h16_extension: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records = deepcopy(h16_extension)
    target = records[0]
    before = target["envelope"]["provenance"]["observation_point"]
    after = f"{before}_content_replaced"
    target["envelope"]["provenance"]["observation_point"] = after
    _rehash(target)
    return records, {
        "record_id": target["record_id"],
        "commit_index": target["commit_index"],
        "field": "envelope.provenance.observation_point",
        "before": before,
        "after": after,
        "record_ids_preserved": True,
        "commit_indices_preserved": True,
        "digest_recomputed": True,
    }


def build_ablation_specimens() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    base = build_specimens()
    h16_extension = deepcopy(base["H16_extension"]["records"])
    h16_content_replacement, mutation = make_h16_content_replacement(h16_extension)
    return {
        "H13_tail_loss": base["H13_tail_loss"],
        "H14_control": base["H14_control"],
        "H16_extension": base["H16_extension"],
        "H16_ID_replacement": {
            "construction": base["H16_replacement"]["construction"],
            "records": make_h16_replacement(h16_extension),
        },
        "H16_content_replacement": {
            "construction": (
                "H16 extension with record 1 envelope.provenance.observation_point changed and digest recomputed"
            ),
            "records": h16_content_replacement,
        },
    }, mutation


def evaluate_projection(
    projection_name: str,
    witnessed_records: list[dict[str, Any]],
    current_records: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluator = _projection_evaluators()[projection_name]
    return evaluator(witnessed_records, current_records)


def run() -> dict[str, Any]:
    started = perf_counter()
    witnessed_records = load_git_h14_records()
    specimens, content_mutation = build_ablation_specimens()
    projection_names = list(_projection_evaluators().keys())

    specimen_results = {
        name: _evaluate_specimen(specimen["records"], specimen["construction"])
        for name, specimen in specimens.items()
    }
    capability_matrix = {
        specimen_name: {
            projection: evaluate_projection(projection, witnessed_records, specimen["records"])["ok"]
            for projection in projection_names
        }
        for specimen_name, specimen in specimens.items()
    }
    projection_findings = {
        projection: _projection_finding(projection, capability_matrix, specimen_results)
        for projection in projection_names
    }

    sufficient = [
        projection
        for projection in projection_names
        if {name: capability_matrix[name][projection] for name in EXPECTED_CAPABILITY} == EXPECTED_CAPABILITY
    ]

    return {
        "experiment": "witness_content_ablation_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "prior_history_source": f"{GIT_H14_COMMIT}:traces/live_ingest_ledger_v0.jsonl",
        "prior_history_source_classification": "Git analytical comparison evidence, not runtime witness infrastructure",
        "specimens": specimen_results,
        "h16_content_replacement_mutation": content_mutation,
        "witness_projections": _projection_descriptions(),
        "capability_matrix": capability_matrix,
        "projection_findings": projection_findings,
        "current_digest_boundary": {
            "algorithm_constant": INTEGRITY_ALGORITHM,
            "boundary_constant": HASH_BOUNDARY,
            "committed_fields": ["record_id", "commit_index", "envelope"],
            "algorithm_boundary_checked_by_verify": False,
            "finding": "verify recomputes digest over record_id, commit_index, and envelope; integrity metadata is stored but not checked",
        },
        "smallest_sufficient_tested_projection": sufficient[0] if sufficient else None,
        "smallest_tested_insufficient_projection_immediately_below": "ordered_record_ids_commit_indices",
        "fields_redundant_for_discrimination": [
            "record_id when ordered digests are available and current integrity passes",
            "commit_index when ordered digests are available and current integrity passes",
            "integrity.algorithm and integrity.boundary under fixed bounded v0 runtime assumptions",
        ],
        "diagnostic_vs_discrimination": (
            "redundant fields can still locate and explain disagreement without adding branch-discrimination power"
        ),
        "historical_identity_difference_without_derived_shape_change": (
            specimen_results["H16_content_replacement"]["derived_state"]
            == specimen_results["H16_extension"]["derived_state"]
        ),
        "new_persistent_witness_architecture_required": False,
        "persistent_architecture_added": [],
        "finding": "record identity sequence does not establish record content identity",
        "memory_interpretation": "memory capacity is which prior distinctions remain recoverable under allowed transformation",
        "unresolved_horizon": (
            "interpretation and provenance required for a minimal ordered-digest prefix witness without creating "
            "checkpoint or manifest architecture"
        ),
        "duration_seconds": perf_counter() - started,
    }


def _evaluate_specimen(records: list[dict[str, Any]], construction: str) -> dict[str, Any]:
    integrity = verify_records_with_jsonl(records)
    continuity = verify_continuity(records, require_start_at_one=True)
    reconstruction = reconstruct_admission_relationships(records)
    projection = derive_admitted_projection(reconstruction)
    return {
        "construction": construction,
        "integrity": integrity,
        "continuity": {
            "ok": continuity.ok,
            "record_count": continuity.record_count,
            "failures": list(continuity.failures),
        },
        "extent": history_extent(records),
        "derived_state": {
            "observation_count": len(reconstruction["observations"]),
            "admission_relation_count": sum(
                len(observation["admissions"]) for observation in reconstruction["observations"]
            ),
            "orphan_admission_count": len(reconstruction["orphan_admissions"]),
            "projection_subject_count": len(projection),
            "projection_subject_ids": [item["subject_record_id"] for item in projection],
        },
    }


def _projection_evaluators() -> dict[str, Callable[[list[dict[str, Any]], list[dict[str, Any]]], dict[str, Any]]]:
    return {
        "extent_only": _extent_only,
        "terminal_digest_only": _terminal_digest_only,
        "ordered_record_ids": _ordered_record_ids,
        "ordered_record_ids_commit_indices": _ordered_record_ids_commit_indices,
        "ordered_record_digests": _ordered_record_digests,
        "ordered_commit_index_digest": _ordered_commit_index_digest,
        "five_field_prefix_identity": _five_field_prefix_identity,
        "full_canonical_prior_records": _full_canonical_prior_records,
    }


def _projection_descriptions() -> dict[str, str]:
    return {
        "extent_only": "record_count and terminal_commit_index lower-bound comparison",
        "terminal_digest_only": "witnessed terminal commit_index and its digest",
        "ordered_record_ids": "ordered record_id prefix",
        "ordered_record_ids_commit_indices": "ordered record_id and commit_index prefix",
        "ordered_record_digests": "ordered existing integrity.digest prefix",
        "ordered_commit_index_digest": "ordered commit_index and integrity.digest prefix",
        "five_field_prefix_identity": "record_id, commit_index, algorithm, boundary, and digest prefix",
        "full_canonical_prior_records": "full prior record prefix equality analytical control",
    }


def _extent_only(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    witnessed_extent = history_extent(witnessed)
    current_extent = history_extent(current)
    ok = (
        current_extent["record_count"] >= witnessed_extent["record_count"]
        and current_extent["terminal_commit_index"] >= witnessed_extent["terminal_commit_index"]
    )
    return {"ok": ok, "witnessed": witnessed_extent, "current": current_extent}


def _terminal_digest_only(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    terminal = witnessed[-1]
    current_match = next((record for record in current if record.get("commit_index") == terminal["commit_index"]), None)
    return {
        "ok": current_match is not None
        and current_match.get("integrity", {}).get("digest") == terminal["integrity"]["digest"],
        "witnessed": _terminal_digest_projection(terminal),
        "current": None if current_match is None else _terminal_digest_projection(current_match),
    }


def _ordered_record_ids(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    return _compare_prefix(_record_id_projection, witnessed, current)


def _ordered_record_ids_commit_indices(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    return _compare_prefix(_record_id_commit_index_projection, witnessed, current)


def _ordered_record_digests(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    return _compare_prefix(_digest_projection, witnessed, current)


def _ordered_commit_index_digest(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    return _compare_prefix(_commit_index_digest_projection, witnessed, current)


def _five_field_prefix_identity(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    result = compare_prefix_preservation(current, witnessed)
    return result.to_dict()


def _full_canonical_prior_records(witnessed: list[dict[str, Any]], current: list[dict[str, Any]]) -> dict[str, Any]:
    return _compare_prefix(lambda record: record, witnessed, current)


def _compare_prefix(
    projection: Callable[[dict[str, Any]], Any],
    witnessed: list[dict[str, Any]],
    current: list[dict[str, Any]],
) -> dict[str, Any]:
    witnessed_projection = [projection(record) for record in witnessed]
    current_projection = [projection(record) for record in current[: len(witnessed)]]
    length_ok = len(current) >= len(witnessed)
    mismatches = []
    if length_ok:
        for index, (current_value, witnessed_value) in enumerate(
            zip(current_projection, witnessed_projection),
            start=1,
        ):
            if current_value != witnessed_value:
                mismatches.append({"position": index, "current": current_value, "witnessed": witnessed_value})
    else:
        mismatches.append(
            {
                "kind": "current_shorter_than_witness",
                "current_record_count": len(current),
                "witnessed_record_count": len(witnessed),
            }
        )
    return {
        "ok": length_ok and not mismatches,
        "mismatches": mismatches,
        "witnessed_count": len(witnessed_projection),
        "current_prefix_count_checked": len(current_projection),
    }


def _projection_finding(
    projection: str,
    matrix: dict[str, dict[str, bool]],
    specimen_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    observed = {name: matrix[name][projection] for name in EXPECTED_CAPABILITY}
    lost = []
    if observed["H16_extension"] and observed["H16_ID_replacement"]:
        lost.append("legitimate extension vs ID replacement")
    if observed["H16_extension"] and observed["H16_content_replacement"]:
        lost.append("legitimate extension vs content replacement")
    if not observed["H16_extension"]:
        lost.append("control vs legitimate extension")
    if observed["H13_tail_loss"]:
        lost.append("control/extension vs tail loss")
    return {
        "sufficient_in_bounded_pressure": observed == EXPECTED_CAPABILITY,
        "lost_distinctions": lost,
        "result_pattern": observed,
        "derived_shape_note": (
            "H16 content replacement and H16 extension have identical derived-state shape"
            if specimen_results["H16_content_replacement"]["derived_state"]
            == specimen_results["H16_extension"]["derived_state"]
            else "H16 content replacement changes derived-state shape"
        ),
    }


def _terminal_digest_projection(record: dict[str, Any]) -> dict[str, Any]:
    integrity = record["integrity"]
    return {
        "commit_index": record["commit_index"],
        "algorithm": integrity["algorithm"],
        "boundary": integrity["boundary"],
        "digest": integrity["digest"],
    }


def _record_id_projection(record: dict[str, Any]) -> str:
    return record["record_id"]


def _record_id_commit_index_projection(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
    }


def _digest_projection(record: dict[str, Any]) -> str:
    return record["integrity"]["digest"]


def _commit_index_digest_projection(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "commit_index": record["commit_index"],
        "digest": record["integrity"]["digest"],
    }


def _rehash(record: dict[str, Any]) -> None:
    boundary = {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "envelope": record["envelope"],
    }
    record["integrity"]["digest"] = record_digest(boundary)


def _git_rev_parse_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, encoding="utf-8").strip()
    except Exception:  # noqa: BLE001 - report absence without blocking the pressure run.
        return None


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
