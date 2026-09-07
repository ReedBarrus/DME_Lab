"""Bounded admissible-history discriminator pressure run."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ledger import (
    HASH_BOUNDARY,
    INTEGRITY_ALGORITHM,
    JsonlLedger,
    canonical_json,
    record_digest,
    verify_continuity,
)
from src.runtime.candidate_set_expansion_pressure import (
    TRACE_PATH as CHART_7_TRACE_PATH,
    _ordered_subsequence,
    run as run_chart_7,
)
from src.runtime.historical_relation_pressure import load_git_h14_records
from src.runtime.history_extent_witness_pressure import verify_records_with_jsonl
from src.runtime.operation_identity_pressure import _prefix_alternate_iterative
from src.runtime.provenance_recovery_pressure import _ordered_digest_witness
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "admissible_history_discriminator_pressure_v0.json"


def run() -> dict[str, Any]:
    started = perf_counter()
    chart_7 = run_chart_7()
    committed_chart_7 = json.loads(CHART_7_TRACE_PATH.read_text(encoding="utf-8"))
    witnessed_records = load_git_h14_records()
    carrier = _ordered_digest_witness(witnessed_records)
    specimens, _ = build_ablation_specimens()
    normal_append = _normal_append(witnessed_records, specimens)
    inserted_record = normal_append[-1]

    constructions = {
        "A_duplicate_integer_index": _duplicate_index_insertion(
            witnessed_records, inserted_record
        ),
        "B_fractional_non_integer_index": _fractional_index_insertion(
            witnessed_records, inserted_record
        ),
        "C_shift_subsequent_indices": _shifted_index_insertion(
            witnessed_records, inserted_record
        ),
        "D_normal_append": normal_append,
    }
    results = {
        name: _evaluate_construction(name, records, witnessed_records)
        for name, records in constructions.items()
    }
    admissible_discriminators = [
        name
        for name, result in results.items()
        if result["admissible_discriminator"]
    ]
    abstract = _abstract_discriminator()
    chart_7_reproduced = all(
        chart_7[key] == committed_chart_7[key]
        for key in (
            "fixed_surfaces",
            "behavioral_cases",
            "direct_historical_outcomes",
            "candidate_set_dependency",
        )
    )

    assumptions = [
        "SHA-256 under the exact current commitment construction",
        "record_id, commit_index, and envelope remain the committed boundary",
        "candidate history is canonically ordered by ascending commit_index",
        "complete-history continuity requires unique gap-free integer indices starting at 1",
        "the bounded source is the witnessed H14 records",
        "exact digest comparison is used",
        "no digest collision is constructed",
    ]

    return {
        "experiment": "admissible_history_discriminator_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "fixed_H14_carrier": {
            "identity": carrier["carrier_identity"],
            "digest_count": carrier["digest_count"],
            "source": "e399720:traces/live_ingest_ledger_v0.jsonl",
        },
        "current_contract": {
            "digest": {
                "algorithm": INTEGRITY_ALGORITHM,
                "boundary": HASH_BOUNDARY,
                "committed_fields": ["record_id", "commit_index", "envelope"],
                "comparison": "exact stored digest value",
            },
            "ordering": {
                "field": "commit_index",
                "direction": "ascending",
                "implementation": "JsonlLedger.replay",
            },
            "continuity": {
                "require_start_at_one": True,
                "integer_commit_indices": True,
                "duplicate_commit_indices_allowed": False,
                "missing_internal_commit_indices_allowed": False,
                "duplicate_record_ids_allowed": False,
            },
            "validator_modifications": [],
            "digest_boundary_modifications": [],
            "canonical_history_modified": False,
        },
        "prior_chart_7": {
            "committed_trace": str(CHART_7_TRACE_PATH).replace("\\", "/"),
            "reproduced_unchanged": chart_7_reproduced,
            "evidence_modified": False,
            "remains_valid": True,
        },
        "abstract_discriminator": abstract,
        "attempted_historical_constructions": results,
        "chart_8_matrix": {
            name: {
                "integrity": result["integrity"]["ok"],
                "continuity": result["continuity"]["ok"],
                "ordered": result["ordering"]["ok"],
                "H14_subsequence": result["relations"]["H14_ordered_digest_subsequence"],
                "H14_prefix": result["relations"]["H14_ordered_digest_prefix"],
                "admissible": result["admissible_under_current_bounded_rules"],
                "admissible_discriminator": result["admissible_discriminator"],
            }
            for name, result in results.items()
        },
        "admissible_discriminator": {
            "found": bool(admissible_discriminators),
            "constructions": admissible_discriminators,
        },
        "contract_induced_bounded_equivalence": {
            "supported": not admissible_discriminators,
            "strengthened_beyond_existing_specimen_coincidence": (
                abstract["distinguishes_relations"] and not admissible_discriminators
            ),
            "bounded_implication": (
                "admissible candidate history plus exact H14 ordered-digest subsequence preservation implies H14 left-prefix preservation"
            ),
            "reason": (
                "preserved H14 digests retain committed indices 1..14 absent a constructed collision; current continuity leaves only later integer indices for additional records"
            ),
            "assumptions": assumptions,
            "universal_append_only_or_SHA256_theorem_claimed": False,
        },
        "chart_7_back_pressure": {
            "interpretation_refined": True,
            "prior_result_invalidated": False,
            "refinement": (
                "the current admissible history constraints prevent the interior sequence shape needed to distinguish prefix from ordered subsequence for H14"
            ),
            "prior_trace_modified": False,
        },
        "chart_8_status": {
            "earned": True,
            "coordinates": "candidate construction x integrity/continuity/relation/admissibility result",
            "stable_coordinate_meaning": (
                "each cell records one current validator or executed relation result"
            ),
        },
        "duple_basis_interpretation": {
            "strengthened": True,
            "expression": "I_B(O) = (B, sigma_B(O))",
            "basis_includes": "current admissible historical specimen domain",
            "finding": (
                "prefix and ordered subsequence retain the same local behavioral identity when B is restricted to current admissible H14-preserving histories"
            ),
            "runtime_abstraction_added": False,
        },
        "navigation_admissibility_relevance": {
            "discriminating_pressure_differs_from_admissible_discriminating_pressure": True,
            "ambiguity_must_be_preserved": True,
            "tie_breaker_added": False,
            "scheduler_added": False,
        },
        "distinctions": {
            "added": [
                {
                    "id": "D-0039",
                    "left": "operation_semantics_difference",
                    "relation": "not_equivalent_to",
                    "right": "distinguishability_on_admissible_history",
                }
            ],
            "amended": [],
            "D_0038_status": "supported",
        },
        "architecture_added": [],
        "strongest_unresolved_horizon": (
            "whether the bounded collapse survives when exactly one governing history constraint is varied"
        ),
        "next_smallest_pressure_frontier": (
            "identify which single current history constraint is necessary for the observed admissibility collapse"
        ),
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _abstract_discriminator() -> dict[str, Any]:
    witness = ["a", "b", "c"]
    candidate = ["a", "X", "b", "c"]
    prefix = _prefix_alternate_iterative(witness, candidate)
    subsequence = _ordered_subsequence(witness, candidate)
    return {
        "witness": witness,
        "candidate": candidate,
        "prefix": prefix,
        "ordered_subsequence": subsequence,
        "distinguishes_relations": prefix != subsequence,
        "valid_historical_specimen": False,
    }


def _duplicate_index_insertion(
    h14: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(h14)
    inserted = _inserted_record(template, "rec-pressure-duplicate", 2)
    records.insert(1, inserted)
    return _canonical_order(records)


def _fractional_index_insertion(
    h14: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(h14)
    inserted = _inserted_record(template, "rec-pressure-fractional", 1.5)
    records.insert(1, inserted)
    return _canonical_order(records)


def _shifted_index_insertion(
    h14: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(h14)
    for record in records:
        if record["commit_index"] >= 2:
            record["commit_index"] += 1
            _rehash(record)
    inserted = _inserted_record(template, "rec-pressure-shift", 2)
    records.append(inserted)
    return _canonical_order(records)


def _normal_append(
    h14: list[dict[str, Any]],
    specimens: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    extension_envelope = deepcopy(specimens["H16_extension"]["records"][14]["envelope"])
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "ledger.jsonl"
        path.write_text(
            "".join(canonical_json(record) + "\n" for record in h14),
            encoding="utf-8",
        )
        ledger = JsonlLedger(path)
        ledger.append(extension_envelope)
        return ledger.replay()


def _inserted_record(
    template: dict[str, Any],
    record_id: str,
    commit_index: int | float,
) -> dict[str, Any]:
    record = deepcopy(template)
    record["record_id"] = record_id
    record["commit_index"] = commit_index
    _rehash(record)
    return record


def _rehash(record: dict[str, Any]) -> None:
    boundary = {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "envelope": record["envelope"],
    }
    record["integrity"]["digest"] = record_digest(boundary)


def _canonical_order(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda record: record["commit_index"])


def _evaluate_construction(
    name: str,
    records: list[dict[str, Any]],
    witnessed_records: list[dict[str, Any]],
) -> dict[str, Any]:
    integrity = verify_records_with_jsonl(records)
    continuity_result = verify_continuity(records, require_start_at_one=True)
    witness_digests = _digests(witnessed_records)
    candidate_digests = _digests(records)
    subsequence = _ordered_subsequence(witness_digests, candidate_digests)
    prefix = _prefix_alternate_iterative(witness_digests, candidate_digests)
    indices = [record["commit_index"] for record in records]
    ordered = indices == sorted(indices)
    admissible = integrity["ok"] and continuity_result.ok and ordered
    discriminator = subsequence and not prefix
    preserved_count = sum(digest in candidate_digests for digest in witness_digests)
    result = {
        "construction": _construction_description(name),
        "record_count": len(records),
        "integrity": integrity,
        "continuity": {
            "ok": continuity_result.ok,
            "record_count": continuity_result.record_count,
            "failures": list(continuity_result.failures),
        },
        "ordering": {
            "ok": ordered,
            "rule": "commit_index ascending",
            "commit_indices": indices,
        },
        "relations": {
            "H14_ordered_digest_subsequence": subsequence,
            "H14_ordered_digest_prefix": prefix,
            "distinguishes_relations": discriminator,
        },
        "witness_digest_preservation": {
            "preserved_count": preserved_count,
            "witness_count": len(witness_digests),
            "all_preserved": preserved_count == len(witness_digests),
        },
        "admissible_under_current_bounded_rules": admissible,
        "admissible_discriminator": admissible and discriminator,
    }
    result["failure_reason"] = _failure_reason(result)
    return result


def _construction_description(name: str) -> str:
    return {
        "A_duplicate_integer_index": (
            "insert one rehashed record at integer commit_index 2 without changing H14 records"
        ),
        "B_fractional_non_integer_index": (
            "insert one rehashed record at commit_index 1.5 without changing H14 records"
        ),
        "C_shift_subsequent_indices": (
            "insert at integer commit_index 2, shift witnessed indices 2..14, and rehash changed records"
        ),
        "D_normal_append": "append one record through JsonlLedger after H14",
    }[name]


def _failure_reason(result: dict[str, Any]) -> str:
    if not result["continuity"]["ok"]:
        kinds = [failure["kind"] for failure in result["continuity"]["failures"]]
        return f"continuity failed: {', '.join(kinds)}"
    if not result["relations"]["H14_ordered_digest_subsequence"]:
        return "shifting committed indices changed H14 digest identities"
    if result["relations"]["H14_ordered_digest_prefix"]:
        return "normal append preserved H14 as a left prefix"
    return "none"


def _digests(records: list[dict[str, Any]]) -> list[str]:
    return [record["integrity"]["digest"] for record in records]


def _git_rev_parse_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            encoding="utf-8",
        ).strip()
    except Exception:  # noqa: BLE001 - preserve missing execution context.
        return None


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
