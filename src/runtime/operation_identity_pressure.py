"""Bounded relation-operation identity pressure run."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any, Callable

from src.runtime.declarative_commitment_semantics_pressure import _representation_variants
from src.runtime.historical_relation_pressure import load_git_h14_records
from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
    _ordered_digest_witness,
)
from src.runtime.vocabulary_identity_pressure import (
    _commitment,
    _correct_vocabulary,
    _path_value,
    _resolve_vocabulary,
    _value_identity,
    evaluate_with_vocabulary,
)
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "operation_identity_pressure_v0.json"

RelationImplementation = Callable[[list[str], list[str]], bool]


def run() -> dict[str, Any]:
    started = perf_counter()
    witnessed_records = load_git_h14_records()
    carrier = _ordered_digest_witness(witnessed_records)
    specimens, _ = build_ablation_specimens()
    declaration = deepcopy(
        _representation_variants()["S9_no_candidate_commitment_mode"]["declaration"]
    )
    vocabulary = _correct_vocabulary(include_identity=False)
    commitments = {
        name: _candidate_commitments(
            specimen["records"],
            declaration,
            vocabulary,
        )
        for name, specimen in specimens.items()
    }
    behavior_cases = _behavior_cases(carrier["digests"], commitments)
    regimes = _evaluator_regimes()

    chart = {
        regime_name: {
            history_name: _evaluate_regime(
                regime,
                declaration,
                vocabulary,
                carrier["digests"],
                specimen["records"],
                commitments[history_name],
                behavior_cases,
            )
            for history_name, specimen in specimens.items()
        }
        for regime_name, regime in regimes.items()
    }
    matrix = {
        regime_name: {
            history_name: result["outcome"]
            for history_name, result in history_results.items()
        }
        for regime_name, history_results in chart.items()
    }

    return {
        "experiment": "operation_identity_pressure_v0",
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
            "historical_specimens": {
                name: {
                    "construction": specimen["construction"],
                    "record_count": len(specimen["records"]),
                }
                for name, specimen in specimens.items()
            },
        },
        "operation_descriptor_under_pressure": {
            "declaration_token": "prefix",
            "Chart_5_descriptor": {"kind": "left_sequence_prefix"},
            "operation_orientation": "witnessed digest sequence is a prefix of candidate digest sequence",
        },
        "evaluator_regimes": {
            name: _regime_report(regime, chart[name], behavior_cases)
            for name, regime in regimes.items()
        },
        "behavioral_cases": _behavior_case_report(behavior_cases),
        "matrix": matrix,
        "outcome_counts": _outcome_counts(matrix),
        "first_unresolved_operation_dependency": {
            name: results["H14_control"].get("first_unresolved_dependency")
            for name, results in chart.items()
            if results["H14_control"]["outcome"] == UNRESOLVED
        },
        "first_wrong_implementation_mismatch": {
            history: result.get("first_mismatch_point")
            for history, result in chart["E3_same_descriptor_equality_implementation"].items()
            if result["outcome"] == MISMATCHED
        },
        "H14_prefix_equality_ambiguity": {
            "prefix_result": behavior_cases["B0_H14_control_agreement"]["candidate_outputs"][
                "alternate_iterative_prefix_v1"
            ],
            "equality_result": behavior_cases["B0_H14_control_agreement"]["candidate_outputs"][
                "sequence_equality_v1"
            ],
            "distinguishes_candidates": False,
            "finding": "agreement on H14 control does not identify prefix rather than equality",
        },
        "H16_extension_discrimination": {
            "prefix_result": behavior_cases["B1_H16_extension_discriminator"]["candidate_outputs"][
                "alternate_iterative_prefix_v1"
            ],
            "equality_result": behavior_cases["B1_H16_extension_discriminator"]["candidate_outputs"][
                "sequence_equality_v1"
            ],
            "distinguishes_candidates": True,
            "finding": "H14 witnessed history is a prefix of H16 extension but is not equal to it",
        },
        "equivalent_alternate_implementation_result": {
            "regime": "E2_explicit_equivalent_prefix_implementation",
            "implementation_path": _implementation_path("alternate_iterative_prefix_v1"),
            "outcomes": matrix["E2_explicit_equivalent_prefix_implementation"],
            "behaviorally_equivalent_under_current_bounded_pressure": (
                matrix["E2_explicit_equivalent_prefix_implementation"]
                == EXPECTED_CORRECT_OUTCOMES
            ),
            "universal_equivalence_claimed": False,
        },
        "changed_implementation_result": {
            "regime": "E3_same_descriptor_equality_implementation",
            "implementation_path": _implementation_path("sequence_equality_v1"),
            "outcomes": matrix["E3_same_descriptor_equality_implementation"],
            "same_descriptor_as_control": True,
            "historical_consequence_changed": (
                matrix["E3_same_descriptor_equality_implementation"]
                != EXPECTED_CORRECT_OUTCOMES
            ),
        },
        "renamed_descriptor_result": {
            "regime": "E4_renamed_descriptor_equivalent_implementation",
            "descriptor": {"kind": "relation_q"},
            "implementation_path": _implementation_path("alternate_iterative_prefix_v1"),
            "outcomes": matrix["E4_renamed_descriptor_equivalent_implementation"],
            "historical_consequence_preserved": (
                matrix["E4_renamed_descriptor_equivalent_implementation"]
                == EXPECTED_CORRECT_OUTCOMES
            ),
        },
        "smallest_sufficient_tested_operation_identity_representation": {
            "regime": "E6_minimal_discriminating_behavioral_witness",
            "representation": {
                "behavioral_case_ids": ["B1_H16_extension_discriminator"],
                "expected_results": [True],
            },
            "case_count": 1,
            "candidate_realizations": [
                "alternate_iterative_prefix_v1",
                "sequence_equality_v1",
            ],
            "bounded_scope": "sufficient only to select between the two tested relation realizations",
        },
        "nearest_insufficient_operation_identity_representation": {
            "regime": "E7_misleading_single_case_witness",
            "representation": {
                "behavioral_case_ids": ["B0_H14_control_agreement"],
                "expected_results": [True],
            },
            "case_count": 1,
            "failure": "both tested realizations satisfy the witness",
        },
        "behavioral_witness_compression": {
            "supported": True,
            "full_implementation_identity_required": False,
            "compressed_to": "one actual-domain H14-to-H16-extension expected result",
            "preserves_tested_operation_discrimination": True,
            "candidate_set_dependency": True,
            "finding": (
                "one discriminating case selected the equivalent prefix realization among two tested alternatives"
            ),
        },
        "implementation_identity_finding": (
            "different current and iterative implementations preserved the same bounded historical consequences"
        ),
        "behavioral_identity_finding": (
            "bounded discriminating behavior, not source identity, carried operation equivalence in this pressure"
        ),
        "outcome_semantics": {
            RECOVERED: "evaluator realization supports the intended historical relation",
            MISMATCHED: "executable evaluator realization produces an incompatible historical relation",
            UNRESOLVED: "available operation identity cannot select a justified realization",
        },
        "remaining_ambient_interpretation": [
            "behavioral-witness case format and expected-result meaning",
            "candidate realization set",
            "execution of candidate realizations against behavioral cases",
            "selection rule requiring one matching realization",
            "digest-sequence and boolean semantics",
            "RECOVERED, MISMATCHED, and UNRESOLVED classification",
        ],
        "chart_5_back_pressure": {
            "operation_binding_interpretation_refined": True,
            "prior_result_invalidated": False,
            "refinement": (
                "Chart 5 semantic binding splits into operation descriptor and bounded behavioral identity"
            ),
        },
        "chart_6_status": {
            "earned": True,
            "coordinates": "operation descriptor/evaluator regime x historical specimen",
            "stable_coordinate_meaning": (
                "each row fixes one relation realization or operation-identity representation"
            ),
        },
        "chart_fold_pressure": {
            "second_fold_earned": True,
            "evidence": (
                "Chart 6 splits Chart 5 operation binding into descriptor, implementation, and bounded behavior"
            ),
            "folding_machinery_added": False,
        },
        "cross_chart_correspondence": {
            "path": "R6 <-> S9 <-> V2a <-> E0/E2/E4/E6",
            "outcomes_invariant": all(
                matrix[name] == EXPECTED_CORRECT_OUTCOMES
                for name in (
                    "E0_current_evaluator_control",
                    "E2_explicit_equivalent_prefix_implementation",
                    "E4_renamed_descriptor_equivalent_implementation",
                    "E6_minimal_discriminating_behavioral_witness",
                )
            ),
            "transition_map_implemented": False,
        },
        "proto_scheduler_relevance": {
            "grounding_strengthened": True,
            "basis": "operation recognition survived lexical and implementation change under bounded behavior",
            "schedulable_primitive_established": False,
            "missing": ["preconditions", "effects", "admissibility"],
            "scheduler_added": False,
        },
        "distinctions": {
            "added": ["D-0037 implementation_identity != operation_identity"],
            "amended": [],
            "not_registered": [
                "behavioral_agreement_on_one_case != behavioral_equivalence",
                "descriptor_survival != operation_recoverability",
            ],
        },
        "architecture_added": [],
        "finding": (
            "different implementations with conserved bounded relation behavior preserve historical consequences"
        ),
        "strongest_unresolved_horizon": (
            "the one-case witness is sufficient only against the two tested relation realizations"
        ),
        "next_smallest_pressure_frontier": (
            "test the one-case behavioral witness against one additional executable relation realization"
        ),
        "duration_seconds": perf_counter() - started,
    }


def _candidate_commitments(
    records: list[dict[str, Any]],
    declaration: dict[str, Any],
    vocabulary: dict[str, Any],
) -> list[str]:
    resolved, issues = _resolve_vocabulary(declaration, vocabulary)
    if issues:
        raise ValueError(f"fixed V2a vocabulary did not resolve: {issues}")
    ordered = sorted(
        records,
        key=lambda record: _path_value(record, resolved["ordering_field"]["source_path"]),
        reverse=resolved["ordering"]["reverse"],
    )
    return [_commitment(record, declaration, resolved) for record in ordered]


def _behavior_cases(
    witness: list[str],
    commitments: dict[str, list[str]],
) -> dict[str, dict[str, Any]]:
    cases = {
        "B0_H14_control_agreement": {
            "witness": witness,
            "candidate": commitments["H14_control"],
            "expected": True,
            "domain": "witnessed H14 relation to candidate H14 control",
        },
        "B1_H16_extension_discriminator": {
            "witness": witness,
            "candidate": commitments["H16_extension"],
            "expected": True,
            "domain": "witnessed H14 relation to candidate H16 legitimate extension",
        },
    }
    for case in cases.values():
        case["candidate_outputs"] = {
            name: implementation(case["witness"], case["candidate"])
            for name, implementation in _candidate_realizations().items()
        }
    return cases


def _behavior_case_report(cases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        name: {
            "domain": case["domain"],
            "witness_count": len(case["witness"]),
            "candidate_count": len(case["candidate"]),
            "expected": case["expected"],
            "candidate_outputs": case["candidate_outputs"],
        }
        for name, case in cases.items()
    }


def _evaluator_regimes() -> dict[str, dict[str, Any]]:
    return {
        "E0_current_evaluator_control": {
            "role": "current Chart 5 relation evaluator control",
            "mode": "current",
            "descriptor": {"kind": "left_sequence_prefix"},
            "implementation": "current_chart_5_prefix",
            "behavioral_case_ids": [],
        },
        "E1_descriptor_only_implementation_absent": {
            "role": "descriptor survives without recoverable evaluator meaning",
            "mode": "absent",
            "descriptor": {"kind": "left_sequence_prefix"},
            "implementation": None,
            "behavioral_case_ids": [],
        },
        "E2_explicit_equivalent_prefix_implementation": {
            "role": "separately implemented iterative prefix behavior",
            "mode": "direct",
            "descriptor": {"kind": "left_sequence_prefix"},
            "implementation": "alternate_iterative_prefix_v1",
            "behavioral_case_ids": [],
        },
        "E3_same_descriptor_equality_implementation": {
            "role": "same descriptor realized as sequence equality",
            "mode": "direct",
            "descriptor": {"kind": "left_sequence_prefix"},
            "implementation": "sequence_equality_v1",
            "behavioral_case_ids": [],
        },
        "E4_renamed_descriptor_equivalent_implementation": {
            "role": "renamed descriptor with iterative prefix realization",
            "mode": "direct",
            "descriptor": {"kind": "relation_q"},
            "implementation": "alternate_iterative_prefix_v1",
            "behavioral_case_ids": [],
        },
        "E5_partial_behavioral_specification": {
            "role": "reflexive property stated without extension behavior",
            "mode": "partial",
            "descriptor": {"accepts_equal_sequences": True},
            "implementation": None,
            "behavioral_case_ids": [],
        },
        "E6_minimal_discriminating_behavioral_witness": {
            "role": "one actual-domain case selects among tested realizations",
            "mode": "behavioral_selection",
            "descriptor": {"kind": "behaviorally_selected_relation"},
            "implementation": None,
            "behavioral_case_ids": ["B1_H16_extension_discriminator"],
        },
        "E7_misleading_single_case_witness": {
            "role": "one equal-history case agrees with both tested realizations",
            "mode": "behavioral_selection",
            "descriptor": {"kind": "behaviorally_selected_relation"},
            "implementation": None,
            "behavioral_case_ids": ["B0_H14_control_agreement"],
        },
    }


def _evaluate_regime(
    regime: dict[str, Any],
    declaration: dict[str, Any],
    vocabulary: dict[str, Any],
    witness: list[str],
    candidate_records: list[dict[str, Any]],
    candidate_commitments: list[str],
    behavior_cases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if regime["mode"] == "current":
        return evaluate_with_vocabulary(
            declaration,
            vocabulary,
            witness,
            candidate_records,
        )

    implementation_name, implementation, issue = _resolve_implementation(
        regime,
        behavior_cases,
    )
    if issue is not None:
        return {
            "outcome": UNRESOLVED,
            "reason": "operation realization cannot be justified",
            "first_unresolved_dependency": issue,
        }

    assert implementation is not None
    if implementation(witness, candidate_commitments):
        return {
            "outcome": RECOVERED,
            "reason": "resolved operation realization supports the intended relation",
            "implementation": implementation_name,
            "first_mismatch_point": None,
        }
    return {
        "outcome": MISMATCHED,
        "reason": "executable operation realization rejects the intended relation",
        "implementation": implementation_name,
        "first_mismatch_point": {
            "kind": "relation_result",
            "witness_count": len(witness),
            "candidate_count": len(candidate_commitments),
        },
    }


def _resolve_implementation(
    regime: dict[str, Any],
    behavior_cases: dict[str, dict[str, Any]],
) -> tuple[str | None, RelationImplementation | None, str | None]:
    if regime["mode"] == "absent":
        return None, None, "operation implementation unavailable"
    if regime["mode"] == "partial":
        return None, None, "extension behavior unspecified"
    if regime["mode"] == "direct":
        name = regime["implementation"]
        return name, _candidate_realizations()[name], None
    if regime["mode"] == "behavioral_selection":
        matches = []
        for name, implementation in _candidate_realizations().items():
            if all(
                implementation(
                    behavior_cases[case_id]["witness"],
                    behavior_cases[case_id]["candidate"],
                )
                == behavior_cases[case_id]["expected"]
                for case_id in regime["behavioral_case_ids"]
            ):
                matches.append((name, implementation))
        if len(matches) != 1:
            return None, None, f"behavioral witness matched {len(matches)} candidate realizations"
        name, implementation = matches[0]
        return name, implementation, None
    raise ValueError(f"unknown bounded evaluator mode: {regime['mode']}")


def _candidate_realizations() -> dict[str, RelationImplementation]:
    return {
        "alternate_iterative_prefix_v1": _prefix_alternate_iterative,
        "sequence_equality_v1": _sequence_equality,
    }


def _prefix_alternate_iterative(witness: list[str], candidate: list[str]) -> bool:
    if len(witness) > len(candidate):
        return False
    for index, witnessed_digest in enumerate(witness):
        if candidate[index] != witnessed_digest:
            return False
    return True


def _sequence_equality(witness: list[str], candidate: list[str]) -> bool:
    return len(witness) == len(candidate) and all(
        witnessed_digest == candidate_digest
        for witnessed_digest, candidate_digest in zip(witness, candidate)
    )


def _regime_report(
    regime: dict[str, Any],
    results: dict[str, dict[str, Any]],
    behavior_cases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    implementation = regime["implementation"]
    if regime["mode"] == "current":
        implementation = "current_chart_5_prefix"
    if regime["mode"] == "behavioral_selection":
        selected = {
            result.get("implementation")
            for result in results.values()
            if result.get("implementation") is not None
        }
        implementation = next(iter(selected)) if len(selected) == 1 else None
    unresolved = [
        result.get("first_unresolved_dependency")
        for result in results.values()
        if result["outcome"] == UNRESOLVED
    ]
    return {
        "role": regime["role"],
        "mode": regime["mode"],
        "descriptor": regime["descriptor"],
        "descriptor_identity": _value_identity(regime["descriptor"]),
        "implementation_identity": implementation,
        "implementation_path": _implementation_path(implementation),
        "behavioral_witness": [
            {
                "case_id": case_id,
                "expected": behavior_cases[case_id]["expected"],
            }
            for case_id in regime["behavioral_case_ids"]
        ],
        "first_unresolved_dependency": unresolved[0] if unresolved else None,
        "outcomes": {
            history: result["outcome"]
            for history, result in results.items()
        },
    }


def _implementation_path(name: str | None) -> str | None:
    paths = {
        "current_chart_5_prefix": "src.runtime.vocabulary_identity_pressure._evaluate_relation",
        "alternate_iterative_prefix_v1": (
            "src.runtime.operation_identity_pressure._prefix_alternate_iterative"
        ),
        "sequence_equality_v1": "src.runtime.operation_identity_pressure._sequence_equality",
    }
    return paths.get(name)


def _outcome_counts(matrix: dict[str, dict[str, str]]) -> dict[str, int]:
    counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
    for outcomes in matrix.values():
        for outcome in outcomes.values():
            counts[outcome] += 1
    return counts


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
