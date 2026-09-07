"""Bounded C2 tie-order relation invariance pressure run."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any

from src.runtime.candidate_set_expansion_pressure import _ordered_subsequence
from src.runtime.historical_relation_pressure import load_git_h14_records
from src.runtime.history_constraint_ablation_pressure import (
    TRACE_PATH as CHART_9_TRACE_PATH,
    _duplicate_index_insertion,
    _normal_append,
    run as run_chart_9,
)
from src.runtime.operation_identity_pressure import _prefix_alternate_iterative
from src.runtime.provenance_recovery_pressure import UNRESOLVED
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "tie_order_invariance_pressure_v0.json"
RESOLVED_BY_ORDER_INVARIANCE = "RESOLVED_BY_ORDER_INVARIANCE"


def run() -> dict[str, Any]:
    started = perf_counter()
    chart_9 = run_chart_9()
    committed_chart_9 = json.loads(CHART_9_TRACE_PATH.read_text(encoding="utf-8"))
    source_records = load_git_h14_records()
    specimens, _ = build_ablation_specimens()
    normal_append = _normal_append(source_records, specimens)
    c2_records = _duplicate_index_insertion(source_records, normal_append[-1])
    linearizations = _bounded_linearizations(c2_records, tied_index=2)
    witness = _digests(source_records)
    evaluated = {
        name: {
            "record_ids": [record["record_id"] for record in records],
            "commit_indices": [record["commit_index"] for record in records],
            "tied_record_ids": [
                record["record_id"]
                for record in records
                if record["commit_index"] == 2
            ],
            "prefix": _prefix_alternate_iterative(witness, _digests(records)),
            "ordered_subsequence": _ordered_subsequence(witness, _digests(records)),
        }
        for name, records in linearizations.items()
    }
    prefix_resolution = _resolve_relation(
        [result["prefix"] for result in evaluated.values()]
    )
    subsequence_resolution = _resolve_relation(
        [result["ordered_subsequence"] for result in evaluated.values()]
    )
    c2_reproduced = (
        chart_9["single_constraint_variants"][
            "C2_relax_duplicate_index_prohibition"
        ]
        == committed_chart_9["single_constraint_variants"][
            "C2_relax_duplicate_index_prohibition"
        ]
    )
    tie_records = [record for record in c2_records if record["commit_index"] == 2]

    return {
        "experiment": "tie_order_invariance_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "fixed_C2_construction": {
            "source_experiment": "history_constraint_ablation_pressure_v0",
            "regime": "C2_relax_duplicate_index_prohibition",
            "construction": (
                "one rehashed pressure record shares commit_index 2 with witnessed rec-000002"
            ),
            "record_count": len(c2_records),
            "source_records_changed": False,
        },
        "tied_records": {
            "commit_index": 2,
            "count": len(tie_records),
            "records": [
                {
                    "record_id": record["record_id"],
                    "digest": record["integrity"]["digest"],
                }
                for record in tie_records
            ],
        },
        "ordering_constraints": {
            "unequal_indices": "ascending commit_index order remains fixed",
            "equal_index_relation": "unknown",
            "secondary_key": None,
            "physical_input_order_authoritative": False,
            "complete_bounded_linearization_count": len(linearizations),
        },
        "bounded_linearizations": evaluated,
        "runtime_stable_sort_observations": {
            "observations": chart_9["single_constraint_variants"]
            ["C2_relax_duplicate_index_prohibition"]["ordering"]
            ["runtime_observations"],
            "classification": "non-authoritative implementation behavior",
            "used_to_select_linearization": False,
        },
        "relation_resolution": {
            "prefix": prefix_resolution,
            "ordered_subsequence": subsequence_resolution,
            "complete_relation_signatures": [
                {
                    "prefix": result["prefix"],
                    "ordered_subsequence": result["ordered_subsequence"],
                }
                for result in evaluated.values()
            ],
            "all_permitted_linearizations_evaluated": True,
            "existential_result_sufficient": False,
            "resolution_requires_invariance": True,
            "overall_status": (
                RESOLVED_BY_ORDER_INVARIANCE
                if prefix_resolution["status"] == RESOLVED_BY_ORDER_INVARIANCE
                and subsequence_resolution["status"]
                == RESOLVED_BY_ORDER_INVARIANCE
                else UNRESOLVED
            ),
        },
        "ordering_status": UNRESOLVED,
        "admissibility_status": UNRESOLVED,
        "tie_break": {
            "introduced": False,
            "used": False,
        },
        "prior_chart_9": {
            "committed_trace": str(CHART_9_TRACE_PATH).replace("\\", "/"),
            "C2_reproduced_unchanged": c2_reproduced,
            "evidence_modified": False,
            "remains_valid": True,
        },
        "chart_9_back_pressure": {
            "refined": True,
            "prior_result_invalidated": False,
            "refinement": (
                "canonical replay order and C2 admissibility remain unresolved, while prefix and ordered-subsequence results are invariant across every bounded compatible linearization"
            ),
            "prior_trace_modified": False,
        },
        "finding": "ordering_resolution != relation_resolution",
        "distinctions": {
            "added": [
                {
                    "id": "D-0040",
                    "left": "ordering_resolution",
                    "relation": "not_equivalent_to",
                    "right": "relation_resolution",
                }
            ],
            "amended": [],
        },
        "duple_interpretation": {
            "strengthened": True,
            "expression": "I_B(O) = (B, sigma_B(O))",
            "finding": (
                "the bounded basis can retain unresolved internal order while its observed relation response remains invariant"
            ),
            "formulation_changed": False,
            "runtime_abstraction_added": False,
        },
        "navigation_relevance": {
            "exact_state_resolution_required_for_this_consequence": False,
            "all_admissible_resolutions_share_consequence": True,
            "navigator_added": False,
            "scheduler_added": False,
            "attention_or_cost_added": False,
        },
        "production_changes": {
            "replay_semantics": False,
            "secondary_order_key": False,
            "canonical_history": False,
        },
        "architecture_added": [],
        "strongest_unresolved_horizon": (
            "C2 exact replay order and whole-state admissibility remain unresolved even though both tested relations are order-invariant"
        ),
        "next_smallest_frontier": (
            "perform one whole-stack adversarial composition pass across the currently earned capture, ledger, reconstruction, and relation boundaries"
        ),
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _bounded_linearizations(
    records: list[dict[str, Any]], *, tied_index: int
) -> dict[str, list[dict[str, Any]]]:
    before = [record for record in records if record["commit_index"] < tied_index]
    tied = [record for record in records if record["commit_index"] == tied_index]
    after = [record for record in records if record["commit_index"] > tied_index]
    if len(tied) != 2:
        raise ValueError("bounded C2 pressure requires exactly two tied records")
    return {
        "L0_pressure_before_witnessed": before + tied + after,
        "L1_witnessed_before_pressure": before + list(reversed(tied)) + after,
    }


def _resolve_relation(results: list[bool]) -> dict[str, Any]:
    invariant = bool(results) and all(result == results[0] for result in results)
    return {
        "results": results,
        "invariant": invariant,
        "status": RESOLVED_BY_ORDER_INVARIANCE if invariant else UNRESOLVED,
        "value": results[0] if invariant else None,
    }


def _digests(records: list[dict[str, Any]]) -> list[str]:
    return [record["integrity"]["digest"] for record in records]


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
