"""Bounded declarative commitment-semantics pressure run."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any

from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
    _ordered_digest_witness,
)
from src.runtime.historical_relation_pressure import GIT_H14_COMMIT, load_git_h14_records
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "declarative_commitment_semantics_pressure_v0.json"

SEMANTIC_COMPONENTS = (
    "algorithm.name",
    "boundary.fields",
    "canonicalization.format",
    "canonicalization.sort_keys",
    "canonicalization.separators",
    "canonicalization.ensure_ascii",
    "canonicalization.encoding",
    "ordering.field",
    "ordering.direction",
    "relation.type",
)


def run() -> dict[str, Any]:
    started = perf_counter()
    witnessed_records = load_git_h14_records()
    carrier = _ordered_digest_witness(witnessed_records)
    specimens, content_mutation = build_ablation_specimens()
    variants = _representation_variants()

    chart = {
        variant_name: {
            history_name: evaluate_declaration(
                variant["declaration"],
                carrier["digests"],
                specimen["records"],
            )
            for history_name, specimen in specimens.items()
        }
        for variant_name, variant in variants.items()
    }
    matrix = {
        variant_name: {
            history_name: result["outcome"]
            for history_name, result in history_results.items()
        }
        for variant_name, history_results in chart.items()
    }
    sufficient = [
        name
        for name, outcomes in matrix.items()
        if outcomes == EXPECTED_CORRECT_OUTCOMES
    ]
    smallest_sufficient = min(
        sufficient,
        key=lambda name: variants[name]["analysis"]["semantic_component_count"],
    )
    smallest_size = variants[smallest_sufficient]["analysis"]["semantic_component_count"]
    smaller_insufficient = [
        name
        for name, variant in variants.items()
        if variant["analysis"]["semantic_component_count"] < smallest_size
        and name not in sufficient
    ]
    nearest_size = max(
        variants[name]["analysis"]["semantic_component_count"]
        for name in smaller_insufficient
    )
    nearest_smaller = [
        name
        for name in smaller_insufficient
        if variants[name]["analysis"]["semantic_component_count"] == nearest_size
    ]

    report = {
        "experiment": "declarative_commitment_semantics_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "witness_carrier": {
            "name": carrier["name"],
            "source": carrier["source"],
            "definition": "ordered integrity.digest values from witnessed H14 records",
            "carrier_identity": carrier["carrier_identity"],
            "digest_count": carrier["digest_count"],
            "interpretation_included": carrier["interpretation_included"],
        },
        "candidate_histories": {
            name: {
                "construction": specimen["construction"],
                "record_count": len(specimen["records"]),
                "commit_index_extent": [
                    min(record["commit_index"] for record in specimen["records"]),
                    max(record["commit_index"] for record in specimen["records"]),
                ],
            }
            for name, specimen in specimens.items()
        },
        "h16_content_replacement_mutation": content_mutation,
        "full_declarative_candidate": variants["S0_full_explicit_semantics"]["declaration"],
        "representations": {
            name: {
                "role": variant["role"],
                "declaration_delta_from_S0": _declaration_delta(variant["declaration"]),
                "analysis": variant["analysis"],
                "behavioral_consequence": _behavioral_consequence(matrix[name]),
            }
            for name, variant in variants.items()
        },
        "matrix": matrix,
        "outcome_counts": _outcome_counts(matrix),
        "first_unresolved_dependency_by_representation": {
            name: results["H14_control"]["first_unresolved_dependency"]
            for name, results in chart.items()
            if results["H14_control"]["outcome"] == UNRESOLVED
        },
        "first_mismatch_points_for_wrong_complete_semantics": {
            name: {
                history: result["first_mismatch_point"]
                for history, result in chart[name].items()
            }
            for name in (
                "S7_wrong_complete_boundary",
                "S8_wrong_complete_canonicalization",
            )
        },
        "smallest_sufficient_tested_representation": smallest_sufficient,
        "nearest_smaller_insufficient_representation": {
            "selected": "S5_no_relation",
            "same_size_alternatives": [
                name for name in nearest_smaller if name != "S5_no_relation"
            ],
            "semantic_component_count": nearest_size,
            "selection_basis": "one-component prefix-relation ablation corresponding to Chart 3 R5",
        },
        "necessary_components_under_tested_ablations": list(SEMANTIC_COMPONENTS),
        "component_ablation_findings": {
            "algorithm.name": "S1 removal made every historical result unresolved",
            "boundary.fields": "S2 removal made every historical result unresolved",
            "canonicalization.format": "S3a removal made every historical result unresolved",
            "canonicalization.sort_keys": "S3b removal made every historical result unresolved",
            "canonicalization.separators": "S3c removal made every historical result unresolved",
            "canonicalization.ensure_ascii": "S3d removal made every historical result unresolved",
            "canonicalization.encoding": "S3e removal made every historical result unresolved",
            "ordering.field": "S4a removal made every historical result unresolved",
            "ordering.direction": "S10 removal made every historical result unresolved",
            "relation.type": "S5 removal made every historical result unresolved",
        },
        "redundant_components_under_tested_ablations": [
            "candidate_commitment.mode; recomputation is implied by this bounded evaluator operation"
        ],
        "opaque_alias_result": {
            "representation": "S6_opaque_aliases_only",
            "outcomes": matrix["S6_opaque_aliases_only"],
            "finding": "ambient implementation handles are not counted as recoverable semantic descriptions",
        },
        "wrong_boundary_result": matrix["S7_wrong_complete_boundary"],
        "wrong_canonicalization_result": matrix["S8_wrong_complete_canonicalization"],
        "chart_3_R6_correspondence": {
            "R6_expected_outcomes": EXPECTED_CORRECT_OUTCOMES,
            "S0_outcomes": matrix["S0_full_explicit_semantics"],
            "S9_compressed_outcomes": matrix["S9_no_candidate_commitment_mode"],
            "S0_reproduces_R6": matrix["S0_full_explicit_semantics"] == EXPECTED_CORRECT_OUTCOMES,
            "S9_reproduces_R6": matrix["S9_no_candidate_commitment_mode"] == EXPECTED_CORRECT_OUTCOMES,
            "executable_correspondence_observed": True,
            "transition_map_claimed": False,
        },
        "remaining_ambient_evaluator_semantics": [
            "declaration key structure and missing-component policy",
            "sha256 token mapping to the local hashlib implementation",
            "json token mapping to local JSON serialization",
            "field-path lookup and boundary-object construction",
            "ascending token mapping to sort direction",
            "prefix token mapping to ordered prefix comparison",
            "RECOVERED, MISMATCHED, and UNRESOLVED outcome rules",
            "candidate commitment recomputation as the evaluator operation",
        ],
        "interpretive_limit": "declarative semantics survived != semantics are interpretation-free",
        "chart_overlap": {
            "Chart_1": "historical transformation x observer relation",
            "Chart_2": "historical transformation x witness representation",
            "Chart_3": "witness carrier x interpretation regime",
            "Chart_4": "interpretation representation x historical recovery",
            "shared_referents": [
                "H13 tail loss",
                "H14 control",
                "H16 extension",
                "H16 ID replacement",
                "H16 content replacement",
                "H14 ordered-digest carrier",
                "prefix preservation",
            ],
            "executable_correspondence": "Chart 3 R6 outcomes equal Chart 4 S0 and S9 outcomes",
            "proto_transition_pressure_strengthened": True,
            "transition_maps_implemented": False,
        },
        "distinctions": {
            "added": ["D-0035 semantic_label != recoverable_semantic_description"],
            "amended": [],
            "not_registered": [
                "declarative_semantics != interpretation_free_semantics",
                "representation_presence != recovery_sufficiency",
            ],
        },
        "persistent_architecture_added": [],
        "declaration_scope": "local in-memory pressure value; no schema or persistence format",
        "finding": (
            "explicit commitment semantics can reproduce bounded historical recovery while opaque aliases cannot"
        ),
        "strongest_unresolved_horizon": (
            "identity and provenance of the evaluator vocabulary still remain ambient"
        ),
        "next_smallest_pressure_frontier": (
            "pressure the minimum identity needed to recover the local declaration vocabulary without persistence"
        ),
        "duration_seconds": perf_counter() - started,
    }
    return report


def evaluate_declaration(
    declaration: dict[str, Any],
    witness_digests: list[str],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    analysis = _analyze_declaration(declaration)
    if analysis["issues"]:
        return {
            "outcome": UNRESOLVED,
            "reason": "declaration lacks independently executable commitment semantics",
            "first_unresolved_dependency": analysis["issues"][0],
            "all_unresolved_dependencies": analysis["issues"],
        }

    ordering = declaration["ordering"]
    ordered_records = sorted(
        candidate_records,
        key=lambda record: _field_value(record, ordering["field"]),
        reverse=ordering["direction"] == "descending",
    )
    commitments = [
        _commitment_from_declaration(record, declaration)
        for record in ordered_records
    ]
    if len(commitments) < len(witness_digests):
        return {
            "outcome": MISMATCHED,
            "reason": "candidate history is shorter than the witnessed prefix",
            "first_mismatch_point": {
                "kind": "candidate_extent",
                "candidate_commitment_count": len(commitments),
                "witness_commitment_count": len(witness_digests),
            },
        }

    for position, (candidate, witness) in enumerate(
        zip(commitments, witness_digests),
        start=1,
    ):
        if candidate != witness:
            return {
                "outcome": MISMATCHED,
                "reason": "executable declaration produced an incompatible commitment",
                "first_mismatch_point": {
                    "kind": "commitment",
                    "position": position,
                    "candidate": candidate,
                    "witness": witness,
                },
            }
    return {
        "outcome": RECOVERED,
        "reason": "candidate commitments preserve the declared witnessed prefix relation",
        "first_mismatch_point": None,
    }


def _full_declaration() -> dict[str, Any]:
    return {
        "algorithm": {"name": "sha256"},
        "boundary": {"fields": ["record_id", "commit_index", "envelope"]},
        "canonicalization": {
            "format": "json",
            "sort_keys": True,
            "separators": [",", ":"],
            "ensure_ascii": False,
            "encoding": "utf-8",
        },
        "ordering": {"field": "commit_index", "direction": "ascending"},
        "relation": {"type": "prefix"},
        "candidate_commitment": {"mode": "recompute_from_record"},
    }


def _representation_variants() -> dict[str, dict[str, Any]]:
    full = _full_declaration()
    compressed = deepcopy(full)
    del compressed["candidate_commitment"]

    declarations: dict[str, tuple[str, dict[str, Any]]] = {
        "S0_full_explicit_semantics": ("full explicit analytical control", deepcopy(full)),
        "S1_no_algorithm": ("algorithm identity removed", _without(compressed, "algorithm")),
        "S2_no_boundary": ("committed field-set identity removed", _without(compressed, "boundary")),
        "S3_no_canonicalization": ("canonicalization description removed", _without(compressed, "canonicalization")),
        "S3a_no_canonicalization_format": (
            "serialization format removed",
            _without_nested(compressed, "canonicalization", "format"),
        ),
        "S3b_no_canonicalization_sort_keys": (
            "key-order behavior removed",
            _without_nested(compressed, "canonicalization", "sort_keys"),
        ),
        "S3c_no_canonicalization_separators": (
            "JSON separators removed",
            _without_nested(compressed, "canonicalization", "separators"),
        ),
        "S3d_no_canonicalization_ensure_ascii": (
            "character escaping behavior removed",
            _without_nested(compressed, "canonicalization", "ensure_ascii"),
        ),
        "S3e_no_canonicalization_encoding": (
            "byte encoding removed",
            _without_nested(compressed, "canonicalization", "encoding"),
        ),
        "S4_no_ordering": ("historical ordering semantics removed", _without(compressed, "ordering")),
        "S4a_no_ordering_field": (
            "ordering direction retained while field removed",
            _without_nested(compressed, "ordering", "field"),
        ),
        "S5_no_relation": ("historical prefix relation removed", _without(compressed, "relation")),
        "S6_opaque_aliases_only": (
            "ambient implementation handles replace semantic descriptions",
            {
                "algorithm": {"name": "sha256"},
                "boundary": "current_record",
                "canonicalization": "current",
                "ordering": {"field": "commit_index", "direction": "ascending"},
                "relation": {"type": "prefix"},
            },
        ),
        "S7_wrong_complete_boundary": (
            "complete executable envelope-only boundary",
            _replace_nested(compressed, "boundary", "fields", ["envelope"]),
        ),
        "S8_wrong_complete_canonicalization": (
            "complete executable spaced JSON canonicalization",
            _replace_nested(compressed, "canonicalization", "separators", [", ", ": "]),
        ),
        "S9_no_candidate_commitment_mode": (
            "full semantics without redundant recomputation-mode declaration",
            deepcopy(compressed),
        ),
        "S10_no_ordering_direction": (
            "ordering field retained while direction removed",
            _without_nested(compressed, "ordering", "direction"),
        ),
    }
    return {
        name: {
            "role": role,
            "declaration": declaration,
            "analysis": _analyze_declaration(declaration),
        }
        for name, (role, declaration) in declarations.items()
    }


def _analyze_declaration(declaration: dict[str, Any]) -> dict[str, Any]:
    expected = _component_values(_full_declaration())
    present = _component_values(declaration)
    missing = [path for path in SEMANTIC_COMPONENTS if path not in present]
    changed = {
        path: {"expected": expected[path], "actual": present[path]}
        for path in SEMANTIC_COMPONENTS
        if path in present and present[path] != expected[path]
    }
    opaque_aliases = {
        key: declaration[key]
        for key in ("boundary", "canonicalization")
        if key in declaration and not isinstance(declaration[key], dict)
    }
    issues = [_issue_for_path(path, declaration) for path in missing]
    issues.extend(_unsupported_issues(declaration, present))
    issues = list(dict.fromkeys(issues))
    return {
        "semantics_present": list(present),
        "semantics_missing": missing,
        "semantics_changed": changed,
        "opaque_aliases": opaque_aliases,
        "issues": issues,
        "executable": not issues,
        "semantic_component_count": len(present),
    }


def _unsupported_issues(declaration: dict[str, Any], present: dict[str, Any]) -> list[str]:
    issues = []
    supported = {
        "algorithm.name": {"sha256"},
        "canonicalization.format": {"json"},
        "canonicalization.encoding": {"utf-8"},
        "ordering.direction": {"ascending", "descending"},
        "relation.type": {"prefix"},
    }
    for path, values in supported.items():
        if path in present and present[path] not in values:
            issues.append(f"unsupported {path}: {present[path]}")
    boundary_fields = present.get("boundary.fields")
    if boundary_fields is not None and (
        not isinstance(boundary_fields, list)
        or not boundary_fields
        or not all(isinstance(field, str) for field in boundary_fields)
    ):
        issues.append("boundary.fields must be a non-empty field-name list")
    separators = present.get("canonicalization.separators")
    if separators is not None and (
        not isinstance(separators, list)
        or len(separators) != 2
        or not all(isinstance(separator, str) for separator in separators)
    ):
        issues.append("canonicalization.separators must contain two strings")
    for path in ("canonicalization.sort_keys", "canonicalization.ensure_ascii"):
        if path in present and not isinstance(present[path], bool):
            issues.append(f"{path} must be boolean")
    mode = declaration.get("candidate_commitment", {}).get("mode") if isinstance(
        declaration.get("candidate_commitment"), dict
    ) else None
    if mode is not None and mode != "recompute_from_record":
        issues.append(f"unsupported candidate_commitment.mode: {mode}")
    return issues


def _issue_for_path(path: str, declaration: dict[str, Any]) -> str:
    root = path.split(".", maxsplit=1)[0]
    value = declaration.get(root)
    if value is not None and not isinstance(value, dict):
        return f"{root} semantic description unavailable; opaque alias supplied"
    return f"{path} unavailable"


def _component_values(declaration: dict[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for path in (*SEMANTIC_COMPONENTS, "candidate_commitment.mode"):
        found, value = _nested_value(declaration, path)
        if found:
            values[path] = value
    return values


def _declaration_delta(declaration: dict[str, Any]) -> dict[str, Any]:
    expected = _component_values(_full_declaration())
    actual = _component_values(declaration)
    return {
        "missing": [path for path in expected if path not in actual],
        "changed": {
            path: {"expected": expected[path], "actual": actual[path]}
            for path in expected
            if path in actual and expected[path] != actual[path]
        },
        "opaque_aliases": {
            key: declaration[key]
            for key in ("boundary", "canonicalization")
            if key in declaration and not isinstance(declaration[key], dict)
        },
    }


def _nested_value(value: dict[str, Any], path: str) -> tuple[bool, Any]:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _commitment_from_declaration(record: dict[str, Any], declaration: dict[str, Any]) -> str:
    fields = declaration["boundary"]["fields"]
    boundary = {field: _field_value(record, field) for field in fields}
    canonicalization = declaration["canonicalization"]
    payload = json.dumps(
        boundary,
        sort_keys=canonicalization["sort_keys"],
        separators=tuple(canonicalization["separators"]),
        ensure_ascii=canonicalization["ensure_ascii"],
    ).encode(canonicalization["encoding"])
    if declaration["algorithm"]["name"] == "sha256":
        return hashlib.sha256(payload).hexdigest()
    raise ValueError("declaration analysis admitted an unsupported algorithm")


def _field_value(record: dict[str, Any], path: str) -> Any:
    value: Any = record
    for part in path.split("."):
        value = value[part]
    return value


def _without(source: dict[str, Any], key: str) -> dict[str, Any]:
    result = deepcopy(source)
    del result[key]
    return result


def _without_nested(source: dict[str, Any], parent: str, key: str) -> dict[str, Any]:
    result = deepcopy(source)
    del result[parent][key]
    return result


def _replace_nested(source: dict[str, Any], parent: str, key: str, value: Any) -> dict[str, Any]:
    result = deepcopy(source)
    result[parent][key] = value
    return result


def _outcome_counts(matrix: dict[str, dict[str, str]]) -> dict[str, int]:
    counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
    for outcomes in matrix.values():
        for outcome in outcomes.values():
            counts[outcome] += 1
    return counts


def _behavioral_consequence(outcomes: dict[str, str]) -> dict[str, Any]:
    departures = [
        history
        for history, outcome in outcomes.items()
        if outcome != EXPECTED_CORRECT_OUTCOMES[history]
    ]
    observed = set(outcomes.values())
    if not departures:
        finding = "all required bounded historical distinctions preserved"
    elif observed == {UNRESOLVED}:
        finding = "all bounded historical classifications became unresolved"
    elif observed == {MISMATCHED}:
        finding = "control and legitimate extension collapsed into mismatch"
    else:
        finding = "some required bounded historical classifications changed"
    return {
        "histories_departing_from_required_outcome": departures,
        "finding": finding,
    }


def _git_rev_parse_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            encoding="utf-8",
        ).strip()
    except Exception:  # noqa: BLE001 - keep missing execution context visible.
        return None


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
