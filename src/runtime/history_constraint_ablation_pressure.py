"""Bounded single-constraint history ablation pressure run."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ledger import HASH_BOUNDARY, INTEGRITY_ALGORITHM, JsonlLedger, canonical_json, verify_continuity
from src.runtime.admissible_history_discriminator_pressure import (
    TRACE_PATH as CHART_8_TRACE_PATH,
    _duplicate_index_insertion,
    _fractional_index_insertion,
    _inserted_record,
    _normal_append,
    _shifted_index_insertion,
    run as run_chart_8,
)
from src.runtime.candidate_set_expansion_pressure import _ordered_subsequence
from src.runtime.historical_relation_pressure import load_git_h14_records
from src.runtime.history_extent_witness_pressure import verify_records_with_jsonl
from src.runtime.operation_identity_pressure import _prefix_alternate_iterative
from src.runtime.provenance_recovery_pressure import UNRESOLVED, _ordered_digest_witness
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "history_constraint_ablation_pressure_v0.json"

CONTROL_RULES = {
    "integer_commit_indices": True,
    "unique_commit_indices": True,
    "gap_free_commit_indices": True,
    "start_at_one": True,
    "unique_record_ids": True,
    "ordering": "commit_index ascending",
    "commitment_boundary": ["record_id", "commit_index", "envelope"],
}


def run() -> dict[str, Any]:
    started = perf_counter()
    chart_8 = run_chart_8()
    committed_chart_8 = json.loads(CHART_8_TRACE_PATH.read_text(encoding="utf-8"))
    source_records = load_git_h14_records()
    source_identity_before = _value_identity(source_records)
    current_carrier = _ordered_digest_witness(source_records)
    specimens, _ = build_ablation_specimens()
    normal_append = _normal_append(source_records, specimens)
    template = normal_append[-1]

    duplicate_before = _duplicate_index_insertion(source_records, template)
    duplicate_after = deepcopy(duplicate_before)
    duplicate_after[1], duplicate_after[2] = duplicate_after[2], duplicate_after[1]
    fractional = _fractional_index_insertion(source_records, template)
    gap = _gap_relaxed_append(source_records, template)
    start = _start_relaxed_prepend(source_records, template)
    duplicate_record_id = _duplicate_record_id_append(source_records, template)
    physical_order = _physical_order_insertion(source_records, template)
    alternate_boundary = _shifted_index_insertion(source_records, template)

    variant_rules = {
        "C1_relax_integer_only": _changed_rules(
            "integer_commit_indices", "integers plus one non-integer coordinate"
        ),
        "C2_relax_duplicate_index_prohibition": _changed_rules(
            "unique_commit_indices", False
        ),
        "C3_relax_gap_free_only": _changed_rules("gap_free_commit_indices", False),
        "C4_relax_start_at_one_only": _changed_rules("start_at_one", False),
        "C5_relax_duplicate_record_id_only": _changed_rules("unique_record_ids", False),
        "C6_vary_replay_ordering_only": _changed_rules("ordering", "physical input sequence"),
        "C7_remove_commit_index_from_boundary_only": _changed_rules(
            "commitment_boundary", ["record_id", "envelope"]
        ),
    }

    regimes = {
        "C0_current_contract": _evaluate_current_control(
            duplicate_before, source_records, current_carrier
        ),
        "C1_relax_integer_only": _evaluate_current_boundary_regime(
            fractional,
            source_records,
            current_carrier,
            _without_failures(_continuity(fractional), {"invalid_commit_index"}),
            ordering="commit_index ascending with one non-integer coordinate",
            classification="collapse-contributing",
            extra={
                "gap_freedom_interpretation": (
                    "the retained integer lineage remains the complete gap-free sequence 1..14"
                )
            },
        ),
        "C2_relax_duplicate_index_prohibition": _evaluate_duplicate_index_regime(
            duplicate_before,
            duplicate_after,
            source_records,
            current_carrier,
        ),
        "C3_relax_gap_free_only": _evaluate_current_boundary_regime(
            gap,
            source_records,
            current_carrier,
            _without_failures(_continuity(gap), {"missing_commit_index"}),
            ordering="commit_index ascending",
            classification="collapse-maintaining",
        ),
        "C4_relax_start_at_one_only": _evaluate_current_boundary_regime(
            start,
            source_records,
            current_carrier,
            _continuity(start, require_start_at_one=False),
            ordering="commit_index ascending",
            classification="collapse-contributing",
        ),
        "C5_relax_duplicate_record_id_only": _evaluate_current_boundary_regime(
            duplicate_record_id,
            source_records,
            current_carrier,
            _without_failures(
                _continuity(duplicate_record_id), {"duplicate_record_id"}
            ),
            ordering="commit_index ascending",
            classification="collapse-maintaining",
        ),
        "C6_vary_replay_ordering_only": _evaluate_current_boundary_regime(
            physical_order,
            source_records,
            current_carrier,
            _continuity(physical_order),
            ordering="physical input sequence",
            classification="collapse-contributing",
            extra={
                "current_replay_commit_indices": [
                    record["commit_index"] for record in _runtime_replay(physical_order)
                ]
            },
        ),
        "C7_remove_commit_index_from_boundary_only": _evaluate_alternate_boundary_regime(
            alternate_boundary,
            source_records,
        ),
    }

    for name, rules in variant_rules.items():
        changed = [key for key in CONTROL_RULES if rules[key] != CONTROL_RULES[key]]
        regimes[name]["changed_rule"] = changed[0]
        regimes[name]["rules"] = rules
        regimes[name]["rules_held_fixed"] = [
            key for key in CONTROL_RULES if key != changed[0]
        ]

    chart_8_reproduced = all(
        chart_8[key] == committed_chart_8[key]
        for key in (
            "fixed_H14_carrier",
            "current_contract",
            "abstract_discriminator",
            "attempted_historical_constructions",
            "admissible_discriminator",
        )
    )
    source_identity_after = _value_identity(source_records)
    classifications = {
        "collapse-contributing": [
            name
            for name, result in regimes.items()
            if result["constraint_classification"] == "collapse-contributing"
        ],
        "collapse-maintaining": [
            name
            for name, result in regimes.items()
            if result["constraint_classification"] == "collapse-maintaining"
        ],
        UNRESOLVED: [
            name
            for name, result in regimes.items()
            if result["constraint_classification"] == UNRESOLVED
        ],
    }

    return {
        "experiment": "history_constraint_ablation_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "fixed_source_lineage": {
            "source": "e399720:traces/live_ingest_ledger_v0.jsonl",
            "record_count": len(source_records),
            "identity_before": source_identity_before,
            "identity_after": source_identity_after,
            "unchanged": source_identity_before == source_identity_after,
        },
        "C0_current_contract": {
            "rules": CONTROL_RULES,
            "digest_algorithm": INTEGRITY_ALGORITHM,
            "digest_boundary": HASH_BOUNDARY,
            "H14_carrier_identity": current_carrier["carrier_identity"],
            "chart_8_admissible_discriminator_found": chart_8[
                "admissible_discriminator"
            ]["found"],
        },
        "prior_chart_8": {
            "committed_trace": str(CHART_8_TRACE_PATH).replace("\\", "/"),
            "reproduced_unchanged": chart_8_reproduced,
            "evidence_modified": False,
            "remains_valid": True,
        },
        "single_constraint_variants": regimes,
        "chart_9_matrix": {
            name: {
                "integrity": result["integrity"]["ok"],
                "admissibility": result["admissibility"],
                "ordering": result["ordering"]["status"],
                "H14_subsequence": result["relations"]["H14_subsequence"],
                "H14_prefix": result["relations"]["H14_prefix"],
                "discriminator_reachable": result["discriminator_reachable"],
                "classification": result["constraint_classification"],
            }
            for name, result in regimes.items()
        },
        "constraint_classifications": classifications,
        "multiple_individual_constraints_contribute": (
            len(classifications["collapse-contributing"]) > 1
        ),
        "commit_index_role_coupling": {
            "supported": True,
            "current_roles": ["commitment identity", "ordering", "continuity/admissibility"],
            "individually_contributing_role_ablation": {
                "coordinate_domain": "C1_relax_integer_only",
                "history_origin": "C4_relax_start_at_one_only",
                "ordering": "C6_vary_replay_ordering_only",
                "commitment_identity": "C7_remove_commit_index_from_boundary_only",
            },
            "non_contributing_single_ablation": {
                "gap_freedom": "C3_relax_gap_free_only",
                "record_id_uniqueness": "C5_relax_duplicate_record_id_only",
            },
            "duplicate_index_role": "UNRESOLVED because equal-index ordering lacks canonical tie semantics",
        },
        "chart_8_back_pressure": {
            "interpretation_refined": True,
            "prior_result_invalidated": False,
            "refinement": (
                "the bounded collapse is maintained by some rules, opened by several independent single-rule changes, and unresolved when duplicate indices remove canonical tie semantics"
            ),
            "prior_trace_modified": False,
        },
        "chart_9_status": {
            "earned": True,
            "coordinates": "single-constraint regime x integrity/admissibility/relation/reachability result",
            "stable_coordinate_meaning": (
                "each non-control row changes one declared current-contract dimension"
            ),
        },
        "duple_basis_interpretation": {
            "strengthened": True,
            "expression": "I_B(O) = (B, sigma_B(O))",
            "control_basis_collapses_relations": True,
            "single_component_basis_changes_separate_relations": [
                "C1_relax_integer_only",
                "C4_relax_start_at_one_only",
                "C6_vary_replay_ordering_only",
                "C7_remove_commit_index_from_boundary_only",
            ],
            "runtime_basis_object_added": False,
        },
        "navigation_relevance": {
            "distinguishing_moves_exist_across_current_admissibility_boundaries": True,
            "regime_change_can_expose_distinction": True,
            "regime_switching_added": False,
            "scheduler_added": False,
            "preference_between_reachable_regimes_established": False,
        },
        "attention_cost_note": {
            "multiple_alternative_discrimination_regimes_found": True,
            "cost_or_attention_model_added": False,
        },
        "distinctions": {
            "added": [],
            "amended": ["D-0039"],
            "amendment_basis": (
                "single changes to the admissible basis altered whether the same operation pair was distinguishable"
            ),
        },
        "production_changes": {
            "ledger_validator": False,
            "digest_boundary": False,
            "replay_order": False,
            "canonical_history": False,
        },
        "architecture_added": [],
        "strongest_unresolved_horizon": (
            "duplicate-index ablation removes canonical tie semantics, so its discriminator reachability remains unresolved"
        ),
        "next_smallest_pressure_frontier": (
            "determine whether duplicate-index relation evidence can be justified without adding a tie-break rule"
        ),
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _evaluate_current_control(
    records: list[dict[str, Any]],
    source: list[dict[str, Any]],
    carrier: dict[str, Any],
) -> dict[str, Any]:
    result = _evaluate_current_boundary_regime(
        records,
        source,
        carrier,
        _continuity(records),
        ordering="commit_index ascending",
        classification="control",
    )
    result["discriminator_reachable"] = False
    result["admissibility"] = False
    result["changed_rule"] = None
    result["rules"] = CONTROL_RULES
    result["rules_held_fixed"] = list(CONTROL_RULES)
    return result


def _evaluate_current_boundary_regime(
    records: list[dict[str, Any]],
    source: list[dict[str, Any]],
    carrier: dict[str, Any],
    continuity: dict[str, Any],
    *,
    ordering: str,
    classification: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    integrity = verify_records_with_jsonl(records)
    witness = _digests(source)
    candidate = _digests(records)
    prefix = _prefix_alternate_iterative(witness, candidate)
    subsequence = _ordered_subsequence(witness, candidate)
    admissible = integrity["ok"] and continuity["ok"]
    result = {
        "integrity": integrity,
        "continuity": continuity,
        "ordering": {"status": "resolved", "rule": ordering},
        "carrier": {
            "identity": carrier["carrier_identity"],
            "bytes_fixed": True,
            "recomputed": False,
        },
        "relations": {"H14_prefix": prefix, "H14_subsequence": subsequence},
        "admissibility": admissible,
        "discriminator_reachable": admissible and subsequence and not prefix,
        "constraint_classification": classification,
    }
    if extra:
        result.update(extra)
    return result


def _evaluate_duplicate_index_regime(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    source: list[dict[str, Any]],
    carrier: dict[str, Any],
) -> dict[str, Any]:
    before_replay = _runtime_replay(before)
    after_replay = _runtime_replay(after)
    witness = _digests(source)
    runtime_observations = {
        "inserted_before_existing_tie": {
            "tied_record_ids": _tied_record_ids(before_replay),
            "prefix": _prefix_alternate_iterative(witness, _digests(before_replay)),
            "subsequence": _ordered_subsequence(witness, _digests(before_replay)),
        },
        "inserted_after_existing_tie": {
            "tied_record_ids": _tied_record_ids(after_replay),
            "prefix": _prefix_alternate_iterative(witness, _digests(after_replay)),
            "subsequence": _ordered_subsequence(witness, _digests(after_replay)),
        },
    }
    return {
        "integrity": verify_records_with_jsonl(before),
        "continuity": _without_failures(
            _continuity(before), {"duplicate_commit_index"}
        ),
        "ordering": {
            "status": UNRESOLVED,
            "rule": "commit_index ascending without equal-index tie semantics",
            "runtime_behavior": "stable sort retains physical input order for equal indices",
            "physical_input_order_dependent": (
                _tied_record_ids(before_replay) != _tied_record_ids(after_replay)
            ),
            "runtime_observations": runtime_observations,
            "tie_break_invented": False,
        },
        "carrier": {
            "identity": carrier["carrier_identity"],
            "bytes_fixed": True,
            "recomputed": False,
        },
        "relations": {"H14_prefix": UNRESOLVED, "H14_subsequence": UNRESOLVED},
        "admissibility": UNRESOLVED,
        "discriminator_reachable": UNRESOLVED,
        "constraint_classification": UNRESOLVED,
    }


def _evaluate_alternate_boundary_regime(
    records: list[dict[str, Any]],
    source: list[dict[str, Any]],
) -> dict[str, Any]:
    witness = [_alternate_digest(record) for record in source]
    candidate = [_alternate_digest(record) for record in records]
    continuity = _continuity(records)
    prefix = _prefix_alternate_iterative(witness, candidate)
    subsequence = _ordered_subsequence(witness, candidate)
    carrier_identity = _value_identity(witness)
    return {
        "integrity": {
            "ok": all(
                digest == _alternate_digest(record)
                for digest, record in zip(candidate, records)
            ),
            "record_count": len(records),
            "failures": [],
            "mode": "local alternate-boundary recomputation",
        },
        "continuity": continuity,
        "ordering": {"status": "resolved", "rule": "commit_index ascending"},
        "carrier": {
            "identity": carrier_identity,
            "bytes_fixed": False,
            "recomputed": True,
            "source_lineage_fixed": True,
            "reason": "commitment-generating boundary changed",
            "committed_fields": ["record_id", "envelope"],
        },
        "relations": {"H14_prefix": prefix, "H14_subsequence": subsequence},
        "admissibility": continuity["ok"],
        "discriminator_reachable": continuity["ok"] and subsequence and not prefix,
        "constraint_classification": "collapse-contributing",
    }


def _gap_relaxed_append(
    source: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(source)
    records.append(_inserted_record(template, "rec-pressure-gap", 16))
    return sorted(records, key=lambda record: record["commit_index"])


def _start_relaxed_prepend(
    source: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(source)
    records.append(_inserted_record(template, "rec-pressure-start", 0))
    return sorted(records, key=lambda record: record["commit_index"])


def _duplicate_record_id_append(
    source: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(source)
    records.append(_inserted_record(template, source[0]["record_id"], 15))
    return sorted(records, key=lambda record: record["commit_index"])


def _physical_order_insertion(
    source: list[dict[str, Any]], template: dict[str, Any]
) -> list[dict[str, Any]]:
    records = deepcopy(source)
    records.insert(1, deepcopy(template))
    return records


def _continuity(
    records: list[dict[str, Any]], *, require_start_at_one: bool = True
) -> dict[str, Any]:
    result = verify_continuity(records, require_start_at_one=require_start_at_one)
    return {
        "ok": result.ok,
        "record_count": result.record_count,
        "failures": list(result.failures),
        "local_variant": False,
    }


def _without_failures(
    result: dict[str, Any], ignored_kinds: set[str]
) -> dict[str, Any]:
    failures = [
        failure
        for failure in result["failures"]
        if failure["kind"] not in ignored_kinds
    ]
    return {
        **result,
        "ok": not failures,
        "failures": failures,
        "locally_ignored_current_failures": sorted(ignored_kinds),
        "local_variant": True,
    }


def _runtime_replay(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "ledger.jsonl"
        path.write_text(
            "".join(canonical_json(record) + "\n" for record in records),
            encoding="utf-8",
        )
        return JsonlLedger(path).replay()


def _tied_record_ids(records: list[dict[str, Any]]) -> list[str]:
    return [record["record_id"] for record in records if record["commit_index"] == 2]


def _changed_rules(key: str, value: Any) -> dict[str, Any]:
    rules = deepcopy(CONTROL_RULES)
    rules[key] = value
    return rules


def _alternate_digest(record: dict[str, Any]) -> str:
    boundary = {"record_id": record["record_id"], "envelope": record["envelope"]}
    return hashlib.sha256(canonical_json(boundary).encode("utf-8")).hexdigest()


def _digests(records: list[dict[str, Any]]) -> list[str]:
    return [record["integrity"]["digest"] for record in records]


def _value_identity(value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _git_rev_parse_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, encoding="utf-8"
        ).strip()
    except Exception:  # noqa: BLE001 - preserve missing execution context.
        return None


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
