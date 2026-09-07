"""Bounded operation candidate-set expansion pressure run."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any, Callable

from src.runtime.declarative_commitment_semantics_pressure import _representation_variants
from src.runtime.historical_relation_pressure import load_git_h14_records
from src.runtime.operation_identity_pressure import (
    TRACE_PATH as CHART_6_TRACE_PATH,
    _behavior_cases,
    _candidate_commitments,
    _prefix_alternate_iterative,
    _sequence_equality,
    run as run_chart_6,
)
from src.runtime.provenance_recovery_pressure import (
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
    _ordered_digest_witness,
)
from src.runtime.vocabulary_identity_pressure import (
    _correct_vocabulary,
    _value_identity,
)
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "candidate_set_expansion_pressure_v0.json"

RelationImplementation = Callable[[list[str], list[str]], bool]


def run() -> dict[str, Any]:
    started = perf_counter()
    chart_6 = run_chart_6()
    committed_chart_6 = json.loads(CHART_6_TRACE_PATH.read_text(encoding="utf-8"))

    witnessed_records = load_git_h14_records()
    carrier = _ordered_digest_witness(witnessed_records)
    specimens, _ = build_ablation_specimens()
    declaration = deepcopy(
        _representation_variants()["S9_no_candidate_commitment_mode"]["declaration"]
    )
    vocabulary = _correct_vocabulary(include_identity=False)
    commitments = {
        name: _candidate_commitments(specimen["records"], declaration, vocabulary)
        for name, specimen in specimens.items()
    }
    behavior_cases = _behavior_cases(carrier["digests"], commitments)

    original_candidates = _original_candidate_realizations()
    expanded_candidates = _expanded_candidate_realizations()
    behavior_outputs = {
        case_name: {
            realization_name: realization(case["witness"], case["candidate"])
            for realization_name, realization in expanded_candidates.items()
        }
        for case_name, case in behavior_cases.items()
    }
    original_selection = _select_realization(
        behavior_cases["B1_H16_extension_discriminator"],
        original_candidates,
    )
    expanded_selection = _select_realization(
        behavior_cases["B1_H16_extension_discriminator"],
        expanded_candidates,
    )
    reversed_selection = _select_realization(
        behavior_cases["B1_H16_extension_discriminator"],
        dict(reversed(tuple(expanded_candidates.items()))),
    )

    direct_outcomes = {
        realization_name: {
            history_name: (
                RECOVERED
                if realization(carrier["digests"], commitments[history_name])
                else MISMATCHED
            )
            for history_name in specimens
        }
        for realization_name, realization in expanded_candidates.items()
    }
    prefix_outcomes = direct_outcomes["alternate_iterative_prefix_v1"]
    subsequence_outcomes = direct_outcomes["ordered_subsequence_v1"]
    first_difference = next(
        (
            history_name
            for history_name in specimens
            if prefix_outcomes[history_name] != subsequence_outcomes[history_name]
        ),
        None,
    )

    chart_6_reproduced = all(
        chart_6[key] == committed_chart_6[key]
        for key in (
            "fixed_surfaces",
            "behavioral_cases",
            "matrix",
            "outcome_counts",
            "smallest_sufficient_tested_operation_identity_representation",
        )
    )
    candidate_set_dependency = (
        original_selection["outcome"] == RECOVERED
        and original_selection["matching_realization_count"] == 1
        and expanded_selection["outcome"] == UNRESOLVED
        and expanded_selection["matching_realization_count"] == 2
    )

    return {
        "experiment": "candidate_set_expansion_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "fixed_surfaces": {
            "carrier": {
                "identity": carrier["carrier_identity"],
                "digest_count": carrier["digest_count"],
                "definition": "ordered integrity.digest values from witnessed H14 records",
            },
            "S9_declaration": {
                "identity": _value_identity(declaration),
                "definition": declaration,
            },
            "V2a_mapping_only_vocabulary": {
                "identity": _value_identity(vocabulary),
                "mapping_count": 8,
                "definition": vocabulary,
            },
            "historical_specimens": chart_6["fixed_surfaces"]["historical_specimens"],
            "behavioral_case_ids": sorted(behavior_cases),
            "canonical_history_changed": False,
        },
        "prior_chart_6": {
            "committed_trace": str(CHART_6_TRACE_PATH),
            "reproduced_before_expansion": chart_6_reproduced,
            "evidence_changed": False,
            "D_0037_remains_supported": (
                chart_6["equivalent_alternate_implementation_result"]
                ["behaviorally_equivalent_under_current_bounded_pressure"]
                and chart_6["changed_implementation_result"]
                ["historical_consequence_changed"]
            ),
        },
        "original_candidate_set": list(original_candidates),
        "expanded_candidate_set": list(expanded_candidates),
        "new_realization": {
            "name": "ordered_subsequence_v1",
            "implementation_path": (
                "src.runtime.candidate_set_expansion_pressure._ordered_subsequence"
            ),
            "semantics": (
                "witnessed digests occur in candidate order without requiring a contiguous left prefix"
            ),
            "aliases_existing_prefix_implementation": False,
        },
        "behavioral_cases": {
            case_name: {
                "domain": case["domain"],
                "witness_count": len(case["witness"]),
                "candidate_count": len(case["candidate"]),
                "expected": case["expected"],
                "candidate_outputs": behavior_outputs[case_name],
            }
            for case_name, case in behavior_cases.items()
        },
        "B1_original_selection": original_selection,
        "B1_expanded_selection": expanded_selection,
        "B1_reversed_candidate_order_selection": reversed_selection,
        "behavioral_selection_outcome": expanded_selection["outcome"],
        "direct_historical_outcomes": direct_outcomes,
        "prefix_ordered_subsequence_comparison": {
            "prefix_outcomes": prefix_outcomes,
            "ordered_subsequence_outcomes": subsequence_outcomes,
            "complete_patterns_differ": prefix_outcomes != subsequence_outcomes,
            "first_differing_existing_specimen": first_difference,
            "locally_indistinguishable_under_current_historical_specimens": (
                prefix_outcomes == subsequence_outcomes
            ),
            "universal_behavioral_equivalence_claimed": False,
        },
        "E6_witness_sufficiency_after_expansion": {
            "remains_uniquely_sufficient": expanded_selection["outcome"] == RECOVERED,
            "outcome": expanded_selection["outcome"],
            "matching_realization_count": expanded_selection[
                "matching_realization_count"
            ],
            "matching_realizations": expanded_selection["matching_realizations"],
        },
        "candidate_set_dependency": {
            "demonstrated": candidate_set_dependency,
            "original_match_count": original_selection["matching_realization_count"],
            "expanded_match_count": expanded_selection["matching_realization_count"],
            "finding": (
                "the unchanged B1 witness changed from unique selection to unresolved after one candidate was added"
            ),
        },
        "chart_7_status": {
            "earned": True,
            "coordinates": (
                "relation realization x fixed behavioral case or historical specimen"
            ),
            "stable_coordinate_meaning": (
                "each cell records executed boolean behavior or derived recovery outcome"
            ),
        },
        "chart_6_back_pressure": {
            "interpretation_refined": True,
            "prior_result_invalidated": False,
            "refinement": (
                "E6 was sufficient relative to the original two-realization candidate set"
            ),
            "prior_evidence_preserved": True,
        },
        "observer_discriminability": {
            "resolution_limit_exposed": prefix_outcomes == subsequence_outcomes,
            "finding": (
                "prefix and ordered subsequence occupy the same outcome coordinate over all five existing historical specimens"
            ),
            "semantic_identity_claimed": False,
        },
        "scheduler_relevance": {
            "operation_recognition_must_preserve_ambiguity": True,
            "unique_match_recognized": True,
            "multiple_matches_unresolved": True,
            "scheduler_added": False,
            "schedulable_primitive_established": False,
        },
        "distinctions": {
            "added": [
                {
                    "id": "D-0038",
                    "left": "behavioral_witness_sufficiency",
                    "relation": "not_equivalent_to",
                    "right": "candidate_set_independent_identity",
                }
            ],
            "amended": [],
            "D_0037_status": "supported",
        },
        "architecture_added": [],
        "strongest_unresolved_horizon": (
            "the fixed B0/B1 cases and five historical specimens do not distinguish prefix from ordered subsequence"
        ),
        "next_smallest_pressure_frontier": (
            "identify the smallest additional historical specimen that distinguishes prefix from ordered subsequence"
        ),
        "duration_seconds": round(perf_counter() - started, 6),
    }


def _original_candidate_realizations() -> dict[str, RelationImplementation]:
    return {
        "alternate_iterative_prefix_v1": _prefix_alternate_iterative,
        "sequence_equality_v1": _sequence_equality,
    }


def _expanded_candidate_realizations() -> dict[str, RelationImplementation]:
    return {
        **_original_candidate_realizations(),
        "ordered_subsequence_v1": _ordered_subsequence,
    }


def _ordered_subsequence(witness: list[str], candidate: list[str]) -> bool:
    witness_index = 0
    for candidate_digest in candidate:
        if (
            witness_index < len(witness)
            and witness[witness_index] == candidate_digest
        ):
            witness_index += 1
    return witness_index == len(witness)


def _select_realization(
    case: dict[str, Any],
    candidates: dict[str, RelationImplementation],
) -> dict[str, Any]:
    matches = sorted(
        name
        for name, realization in candidates.items()
        if realization(case["witness"], case["candidate"]) == case["expected"]
    )
    return {
        "outcome": RECOVERED if len(matches) == 1 else UNRESOLVED,
        "matching_realization_count": len(matches),
        "matching_realizations": matches,
        "tie_break_used": False,
    }


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
