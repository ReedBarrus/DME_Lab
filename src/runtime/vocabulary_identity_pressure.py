"""Bounded evaluator-vocabulary identity pressure run."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any

from src.ledger import canonical_json
from src.runtime.declarative_commitment_semantics_pressure import (
    _representation_variants,
    evaluate_declaration,
)
from src.runtime.historical_relation_pressure import load_git_h14_records
from src.runtime.provenance_recovery_pressure import (
    EXPECTED_CORRECT_OUTCOMES,
    MISMATCHED,
    RECOVERED,
    UNRESOLVED,
    _ordered_digest_witness,
)
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "vocabulary_identity_pressure_v0.json"

MAPPING_CATEGORIES = (
    "algorithm_tokens",
    "field_tokens",
    "serialization_tokens",
    "encoding_tokens",
    "ordering_tokens",
    "relation_tokens",
)


def run() -> dict[str, Any]:
    started = perf_counter()
    witnessed_records = load_git_h14_records()
    carrier = _ordered_digest_witness(witnessed_records)
    specimens, _ = build_ablation_specimens()
    s9 = deepcopy(
        _representation_variants()["S9_no_candidate_commitment_mode"]["declaration"]
    )
    regimes = _vocabulary_regimes(s9)

    chart = {
        regime_name: {
            history_name: _evaluate_regime(
                regime,
                carrier["digests"],
                specimen["records"],
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
    explicit_sufficient = [
        name
        for name, outcomes in matrix.items()
        if regimes[name]["mode"] == "explicit" and outcomes == EXPECTED_CORRECT_OUTCOMES
    ]
    smallest_sufficient = min(
        explicit_sufficient,
        key=lambda name: (
            _mapping_count(regimes[name]["vocabulary"]),
            len(regimes[name]["vocabulary"].get("identity", {})),
        ),
    )
    smallest_count = _mapping_count(regimes[smallest_sufficient]["vocabulary"])
    insufficient_explicit = [
        name
        for name, regime in regimes.items()
        if regime["mode"] == "explicit"
        and matrix[name] != EXPECTED_CORRECT_OUTCOMES
        and _mapping_count(regime["vocabulary"]) < smallest_count
    ]
    nearest_count = max(
        _mapping_count(regimes[name]["vocabulary"])
        for name in insufficient_explicit
    )
    nearest = [
        name
        for name in insufficient_explicit
        if _mapping_count(regimes[name]["vocabulary"]) == nearest_count
    ]

    shape_identities = {
        name: _declaration_shape_identity(regime["declaration"])
        for name, regime in regimes.items()
    }
    exact_identities = {
        name: _value_identity(regime["declaration"])
        for name, regime in regimes.items()
    }

    return {
        "experiment": "vocabulary_identity_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "fixed_witness_carrier": {
            "name": carrier["name"],
            "source": carrier["source"],
            "definition": "ordered integrity.digest values from witnessed H14 records",
            "carrier_identity": carrier["carrier_identity"],
            "digest_count": carrier["digest_count"],
        },
        "fixed_S9_declaration": {
            "definition": s9,
            "exact_identity": _value_identity(s9),
            "shape_identity": _declaration_shape_identity(s9),
            "semantic_component_count": 10,
        },
        "historical_specimens": {
            name: {
                "construction": specimen["construction"],
                "record_count": len(specimen["records"]),
            }
            for name, specimen in specimens.items()
        },
        "correct_vocabulary_candidate": _correct_vocabulary(include_identity=True),
        "vocabulary_regimes": {
            name: _regime_report(regime, chart[name])
            for name, regime in regimes.items()
        },
        "matrix": matrix,
        "outcome_counts": _outcome_counts(matrix),
        "outcome_semantics": {
            RECOVERED: "resolved vocabulary executes the declared relation and the candidate preserves it",
            MISMATCHED: "resolved vocabulary executes the declared relation and rejects the candidate",
            UNRESOLVED: "required vocabulary meaning is unavailable",
        },
        "wrong_vocabulary_limit": "wrong vocabulary != corrupt history",
        "first_unresolved_vocabulary_dependency": {
            name: results["H14_control"].get("first_unresolved_dependency")
            for name, results in chart.items()
            if results["H14_control"]["outcome"] == UNRESOLVED
        },
        "first_mismatch_under_wrong_vocabulary": {
            name: {
                history: result.get("first_mismatch_point")
                for history, result in chart[name].items()
                if result["outcome"] == MISMATCHED
            }
            for name in (
                "V4_wrong_complete_relation_mapping",
                "V5_wrong_field_token_mapping",
            )
        },
        "smallest_sufficient_tested_vocabulary_identity": {
            "regime": smallest_sufficient,
            "mapping_count": smallest_count,
            "vocabulary_identity_metadata_required": False,
            "finding": "eight explicit semantic bindings suffice under the local descriptor evaluator",
        },
        "nearest_insufficient_vocabulary_regime": {
            "selected": "V3a_missing_relation_mapping",
            "same_size_alternatives": [
                name for name in nearest if name != "V3a_missing_relation_mapping"
            ],
            "mapping_count": nearest_count,
        },
        "necessary_vocabulary_dimensions_under_tested_ablations": [
            "algorithm-token operation binding",
            "record_id field-token binding",
            "serialization-token operation binding",
            "relation-token operation binding",
        ],
        "retained_not_independently_ablated": [
            "commit_index and envelope field-token bindings",
            "encoding-token operation binding",
            "ordering-token operation binding",
            "operation-version identity",
        ],
        "redundant_vocabulary_dimensions_in_bounded_execution": [
            "original token spelling when semantic bindings are conserved",
            "vocabulary name, version, and provenance metadata",
        ],
        "renamed_token_result": {
            "partial_rename_regime": "V6_renamed_symbols_preserved_mapping",
            "full_rename_regime": "V7_equivalent_renamed_vocabulary",
            "partial_outcomes": matrix["V6_renamed_symbols_preserved_mapping"],
            "full_outcomes": matrix["V7_equivalent_renamed_vocabulary"],
            "exact_declaration_identity_changed": (
                exact_identities["V7_equivalent_renamed_vocabulary"]
                != _value_identity(s9)
            ),
            "declaration_shape_identity_preserved": len(set(shape_identities.values())) == 1,
            "semantic_mapping_preserved": True,
            "finding": "lexical coordinates changed while bounded historical outcomes remained invariant",
        },
        "lexical_identity_finding": "token spelling did not carry operation identity in the bounded renamed regimes",
        "semantic_mapping_finding": "conserved token-to-descriptor bindings preserved historical outcomes",
        "remaining_ambient_evaluator_interpretation": [
            "vocabulary-description category and descriptor structure",
            "SHA-2 family and 256-bit descriptor execution",
            "record path traversal and boundary-key construction",
            "JSON text descriptor execution and literal canonicalization parameters",
            "UTF-8 descriptor execution",
            "reverse boolean interpretation for ordering",
            "left-sequence-prefix and sequence-equality descriptor execution",
            "RECOVERED, MISMATCHED, and UNRESOLVED classification",
        ],
        "recursion_limit": "vocabulary interpretation conserved != interpretation eliminated",
        "chart_4_back_pressure": {
            "necessity_interpretation_refined": True,
            "prior_result_invalidated": False,
            "refinement": (
                "Chart 4 components were necessary under its fixed evaluator vocabulary; "
                "Chart 5 separates component role from token spelling and recoverable binding"
            ),
            "axis_split": "declaration component presence separates from vocabulary binding recoverability",
            "conditionality": (
                "the original lexical values are not phenomenon-level necessities when equivalent mappings survive"
            ),
        },
        "cross_chart_correspondence": {
            "Chart_3": "R6 sufficient bounded historical verifier semantics",
            "Chart_4": "S9 smallest sufficient declarative representation",
            "Chart_5": [
                "V2_explicit_correct_vocabulary",
                "V2a_mapping_only",
                "V6_renamed_symbols_preserved_mapping",
                "V7_equivalent_renamed_vocabulary",
            ],
            "outcomes_invariant": all(
                matrix[name] == EXPECTED_CORRECT_OUTCOMES
                for name in (
                    "V2_explicit_correct_vocabulary",
                    "V2a_mapping_only",
                    "V6_renamed_symbols_preserved_mapping",
                    "V7_equivalent_renamed_vocabulary",
                )
            ),
            "transition_map_implemented": False,
        },
        "chart_5_status": {
            "earned": True,
            "coordinates": "vocabulary interpretation regime x historical specimen",
            "stable_coordinate_meaning": (
                "each row fixes one vocabulary availability or binding transformation over fixed declaration structure"
            ),
        },
        "chart_fold_pressure": {
            "supported": True,
            "evidence": (
                "Chart 5 split Chart 4 declaration-component necessity into semantic role, lexical token, and binding"
            ),
            "folding_machinery_added": False,
        },
        "proto_transition_pressure_strengthened": True,
        "distinctions": {
            "added": ["D-0036 token_identity != semantic_operation_identity"],
            "amended": [],
            "not_registered": [
                "lexical_equivalence != semantic_equivalence",
                "vocabulary_interpretation_conserved != interpretation_eliminated",
            ],
        },
        "persistent_architecture_added": [],
        "finding": (
            "renamed tokens preserve bounded historical recovery when their semantic descriptor bindings survive"
        ),
        "strongest_unresolved_horizon": (
            "identity and provenance of the operation descriptors remain ambient in the local evaluator"
        ),
        "next_smallest_pressure_frontier": (
            "pressure one operation descriptor identity across evaluator-version change without persistence"
        ),
        "duration_seconds": perf_counter() - started,
    }


def _evaluate_regime(
    regime: dict[str, Any],
    witness_digests: list[str],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    if regime["mode"] == "ambient_control":
        result = evaluate_declaration(
            regime["declaration"],
            witness_digests,
            candidate_records,
        )
        return {**result, "vocabulary_source": "ambient Chart 4 evaluator"}
    return evaluate_with_vocabulary(
        regime["declaration"],
        regime["vocabulary"],
        witness_digests,
        candidate_records,
    )


def evaluate_with_vocabulary(
    declaration: dict[str, Any],
    vocabulary: dict[str, Any],
    witness_digests: list[str],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    resolved, issues = _resolve_vocabulary(declaration, vocabulary)
    if issues:
        return {
            "outcome": UNRESOLVED,
            "reason": "declaration tokens lack executable vocabulary bindings",
            "first_unresolved_dependency": issues[0],
            "all_unresolved_dependencies": issues,
        }

    ordered_records = sorted(
        candidate_records,
        key=lambda record: _path_value(record, resolved["ordering_field"]["source_path"]),
        reverse=resolved["ordering"]["reverse"],
    )
    commitments = [
        _commitment(record, declaration, resolved)
        for record in ordered_records
    ]
    return _evaluate_relation(
        resolved["relation"]["kind"],
        commitments,
        witness_digests,
    )


def _resolve_vocabulary(
    declaration: dict[str, Any],
    vocabulary: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []

    algorithm = _resolve_token(
        vocabulary,
        "algorithm_tokens",
        declaration["algorithm"]["name"],
        issues,
    )
    boundary_fields = [
        _resolve_token(vocabulary, "field_tokens", token, issues)
        for token in declaration["boundary"]["fields"]
    ]
    serialization = _resolve_token(
        vocabulary,
        "serialization_tokens",
        declaration["canonicalization"]["format"],
        issues,
    )
    encoding = _resolve_token(
        vocabulary,
        "encoding_tokens",
        declaration["canonicalization"]["encoding"],
        issues,
    )
    ordering_field = _resolve_token(
        vocabulary,
        "field_tokens",
        declaration["ordering"]["field"],
        issues,
    )
    ordering = _resolve_token(
        vocabulary,
        "ordering_tokens",
        declaration["ordering"]["direction"],
        issues,
    )
    relation = _resolve_token(
        vocabulary,
        "relation_tokens",
        declaration["relation"]["type"],
        issues,
    )

    if algorithm is not None and algorithm != {"family": "sha-2", "digest_bits": 256}:
        issues.append("algorithm descriptor operation unavailable")
    if serialization is not None and serialization != {"data_model": "json", "output": "text"}:
        issues.append("serialization descriptor operation unavailable")
    if encoding is not None and encoding != {"unicode_encoding": "utf-8"}:
        issues.append("encoding descriptor operation unavailable")
    for binding in [*boundary_fields, ordering_field]:
        if binding is not None and not _valid_field_binding(binding):
            issues.append("field descriptor operation unavailable")
    if ordering is not None and (
        set(ordering) != {"reverse"} or not isinstance(ordering["reverse"], bool)
    ):
        issues.append("ordering descriptor operation unavailable")
    if relation is not None and relation.get("kind") not in {
        "left_sequence_prefix",
        "sequence_equality",
    }:
        issues.append("relation descriptor operation unavailable")

    return {
        "algorithm": algorithm,
        "boundary_fields": boundary_fields,
        "serialization": serialization,
        "encoding": encoding,
        "ordering_field": ordering_field,
        "ordering": ordering,
        "relation": relation,
    }, list(dict.fromkeys(issues))


def _resolve_token(
    vocabulary: dict[str, Any],
    category: str,
    token: str,
    issues: list[str],
) -> dict[str, Any] | None:
    mapping = vocabulary.get(category, {})
    if token not in mapping:
        issues.append(f"{category}.{token} mapping unavailable")
        return None
    return mapping[token]


def _valid_field_binding(binding: dict[str, Any]) -> bool:
    return (
        set(binding) == {"source_path", "boundary_key"}
        and isinstance(binding["source_path"], list)
        and bool(binding["source_path"])
        and all(isinstance(part, str) for part in binding["source_path"])
        and isinstance(binding["boundary_key"], str)
    )


def _commitment(
    record: dict[str, Any],
    declaration: dict[str, Any],
    resolved: dict[str, Any],
) -> str:
    boundary = {
        binding["boundary_key"]: _path_value(record, binding["source_path"])
        for binding in resolved["boundary_fields"]
    }
    canonicalization = declaration["canonicalization"]
    payload = json.dumps(
        boundary,
        sort_keys=canonicalization["sort_keys"],
        separators=tuple(canonicalization["separators"]),
        ensure_ascii=canonicalization["ensure_ascii"],
    ).encode(resolved["encoding"]["unicode_encoding"])
    return hashlib.sha256(payload).hexdigest()


def _evaluate_relation(
    relation_kind: str,
    candidate: list[str],
    witness: list[str],
) -> dict[str, Any]:
    if relation_kind == "left_sequence_prefix":
        if len(candidate) < len(witness):
            return _extent_mismatch(candidate, witness)
        compared = candidate[: len(witness)]
    elif relation_kind == "sequence_equality":
        if len(candidate) != len(witness):
            return _extent_mismatch(candidate, witness)
        compared = candidate
    else:
        raise ValueError("vocabulary resolution admitted an unsupported relation")

    for position, (candidate_digest, witness_digest) in enumerate(
        zip(compared, witness),
        start=1,
    ):
        if candidate_digest != witness_digest:
            return {
                "outcome": MISMATCHED,
                "reason": "executable vocabulary produced an incompatible commitment",
                "first_mismatch_point": {
                    "kind": "commitment",
                    "position": position,
                    "candidate": candidate_digest,
                    "witness": witness_digest,
                },
            }
    return {
        "outcome": RECOVERED,
        "reason": "resolved vocabulary preserves the declared historical relation",
        "first_mismatch_point": None,
    }


def _extent_mismatch(candidate: list[str], witness: list[str]) -> dict[str, Any]:
    return {
        "outcome": MISMATCHED,
        "reason": "resolved relation rejects candidate history extent",
        "first_mismatch_point": {
            "kind": "candidate_extent",
            "candidate_commitment_count": len(candidate),
            "witness_commitment_count": len(witness),
        },
    }


def _correct_vocabulary(*, include_identity: bool) -> dict[str, Any]:
    vocabulary = {
        "algorithm_tokens": {
            "sha256": {"family": "sha-2", "digest_bits": 256},
        },
        "field_tokens": {
            "record_id": {"source_path": ["record_id"], "boundary_key": "record_id"},
            "commit_index": {"source_path": ["commit_index"], "boundary_key": "commit_index"},
            "envelope": {"source_path": ["envelope"], "boundary_key": "envelope"},
        },
        "serialization_tokens": {
            "json": {"data_model": "json", "output": "text"},
        },
        "encoding_tokens": {
            "utf-8": {"unicode_encoding": "utf-8"},
        },
        "ordering_tokens": {
            "ascending": {"reverse": False},
        },
        "relation_tokens": {
            "prefix": {"kind": "left_sequence_prefix"},
        },
    }
    if include_identity:
        vocabulary["identity"] = {
            "name": "dme_lab.bounded_commitment_vocabulary",
            "version": "v0",
            "provenance": "local Chart 5 pressure",
        }
    return vocabulary


def _vocabulary_regimes(s9: dict[str, Any]) -> dict[str, dict[str, Any]]:
    correct = _correct_vocabulary(include_identity=True)
    mapping_only = _correct_vocabulary(include_identity=False)

    partial_renames = {
        "algorithm": {"sha256": "op_a"},
        "field": {"record_id": "field_1"},
        "serialization": {},
        "encoding": {},
        "ordering": {},
        "relation": {"prefix": "rel_z"},
    }
    full_renames = {
        "algorithm": {"sha256": "op_a"},
        "field": {
            "record_id": "field_1",
            "commit_index": "field_2",
            "envelope": "field_3",
        },
        "serialization": {"json": "ser_q"},
        "encoding": {"utf-8": "enc_u"},
        "ordering": {"ascending": "ord_up"},
        "relation": {"prefix": "rel_z"},
    }

    return {
        "V0_current_ambient_control": _regime(
            "ambient Chart 4 evaluator control",
            "ambient_control",
            s9,
            {},
        ),
        "V1_tokens_only": _regime(
            "S9 symbols survive without vocabulary interpretation",
            "explicit",
            s9,
            {},
        ),
        "V2_explicit_correct_vocabulary": _regime(
            "complete correct mappings with local identity metadata",
            "explicit",
            s9,
            correct,
        ),
        "V2a_mapping_only": _regime(
            "correct mappings without vocabulary identity metadata",
            "explicit",
            s9,
            mapping_only,
        ),
        "V3a_missing_relation_mapping": _regime(
            "relation-token mapping removed",
            "explicit",
            s9,
            _without_token(correct, "relation_tokens", "prefix"),
        ),
        "V3b_missing_record_id_field_mapping": _regime(
            "record_id field-token mapping removed",
            "explicit",
            s9,
            _without_token(correct, "field_tokens", "record_id"),
        ),
        "V3c_missing_serialization_mapping": _regime(
            "serialization-token mapping removed",
            "explicit",
            s9,
            _without_token(correct, "serialization_tokens", "json"),
        ),
        "V3d_missing_algorithm_mapping": _regime(
            "algorithm-token mapping removed",
            "explicit",
            s9,
            _without_token(correct, "algorithm_tokens", "sha256"),
        ),
        "V4_wrong_complete_relation_mapping": _regime(
            "prefix token mapped to sequence equality",
            "explicit",
            s9,
            _replace_token(
                correct,
                "relation_tokens",
                "prefix",
                {"kind": "sequence_equality"},
            ),
        ),
        "V5_wrong_field_token_mapping": _regime(
            "record_id token bound to envelope content",
            "explicit",
            s9,
            _replace_token(
                correct,
                "field_tokens",
                "record_id",
                {"source_path": ["envelope"], "boundary_key": "record_id"},
            ),
        ),
        "V6_renamed_symbols_preserved_mapping": _renamed_regime(
            "selected symbols renamed with descriptor bindings preserved",
            s9,
            correct,
            partial_renames,
        ),
        "V7_equivalent_renamed_vocabulary": _renamed_regime(
            "all semantic symbols and vocabulary identity renamed with bindings preserved",
            s9,
            _replace_identity(
                correct,
                name="local.alt_coordinates",
                version="renamed-v0",
                provenance="local equivalent-mapping pressure",
            ),
            full_renames,
        ),
    }


def _regime(
    role: str,
    mode: str,
    declaration: dict[str, Any],
    vocabulary: dict[str, Any],
    *,
    token_renames: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "role": role,
        "mode": mode,
        "declaration": deepcopy(declaration),
        "vocabulary": deepcopy(vocabulary),
        "token_renames": token_renames or {},
    }


def _renamed_regime(
    role: str,
    declaration: dict[str, Any],
    vocabulary: dict[str, Any],
    renames: dict[str, dict[str, str]],
) -> dict[str, Any]:
    return _regime(
        role,
        "explicit",
        _rename_declaration_tokens(declaration, renames),
        _rename_vocabulary_tokens(vocabulary, renames),
        token_renames=renames,
    )


def _rename_declaration_tokens(
    declaration: dict[str, Any],
    renames: dict[str, dict[str, str]],
) -> dict[str, Any]:
    result = deepcopy(declaration)
    result["algorithm"]["name"] = renames["algorithm"].get(
        result["algorithm"]["name"], result["algorithm"]["name"]
    )
    result["boundary"]["fields"] = [
        renames["field"].get(token, token)
        for token in result["boundary"]["fields"]
    ]
    result["canonicalization"]["format"] = renames["serialization"].get(
        result["canonicalization"]["format"], result["canonicalization"]["format"]
    )
    result["canonicalization"]["encoding"] = renames["encoding"].get(
        result["canonicalization"]["encoding"], result["canonicalization"]["encoding"]
    )
    result["ordering"]["field"] = renames["field"].get(
        result["ordering"]["field"], result["ordering"]["field"]
    )
    result["ordering"]["direction"] = renames["ordering"].get(
        result["ordering"]["direction"], result["ordering"]["direction"]
    )
    result["relation"]["type"] = renames["relation"].get(
        result["relation"]["type"], result["relation"]["type"]
    )
    return result


def _rename_vocabulary_tokens(
    vocabulary: dict[str, Any],
    renames: dict[str, dict[str, str]],
) -> dict[str, Any]:
    result = deepcopy(vocabulary)
    category_names = {
        "algorithm_tokens": "algorithm",
        "field_tokens": "field",
        "serialization_tokens": "serialization",
        "encoding_tokens": "encoding",
        "ordering_tokens": "ordering",
        "relation_tokens": "relation",
    }
    for category, rename_category in category_names.items():
        result[category] = {
            renames[rename_category].get(token, token): descriptor
            for token, descriptor in result[category].items()
        }
    return result


def _regime_report(
    regime: dict[str, Any],
    results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    vocabulary = regime["vocabulary"]
    unresolved = [
        result.get("first_unresolved_dependency")
        for result in results.values()
        if result["outcome"] == UNRESOLVED
    ]
    return {
        "role": regime["role"],
        "mode": regime["mode"],
        "vocabulary_identity": vocabulary.get("identity"),
        "token_renames": regime["token_renames"],
        "exact_token_mappings": _flatten_mappings(vocabulary),
        "mapping_delta_from_V2": _mapping_delta(vocabulary),
        "mapping_count": _mapping_count(vocabulary),
        "declaration_exact_identity": _value_identity(regime["declaration"]),
        "declaration_shape_identity": _declaration_shape_identity(regime["declaration"]),
        "first_unresolved_dependency": unresolved[0] if unresolved else None,
        "behavioral_outcomes": {
            history: result["outcome"]
            for history, result in results.items()
        },
    }


def _flatten_mappings(vocabulary: dict[str, Any]) -> dict[str, Any]:
    return {
        f"{category}.{token}": descriptor
        for category in MAPPING_CATEGORIES
        for token, descriptor in vocabulary.get(category, {}).items()
    }


def _mapping_count(vocabulary: dict[str, Any]) -> int:
    return sum(len(vocabulary.get(category, {})) for category in MAPPING_CATEGORIES)


def _mapping_delta(vocabulary: dict[str, Any]) -> dict[str, Any]:
    expected = _flatten_mappings(_correct_vocabulary(include_identity=False))
    actual = _flatten_mappings(vocabulary)
    return {
        "missing": [path for path in expected if path not in actual],
        "added": {
            path: value
            for path, value in actual.items()
            if path not in expected
        },
        "changed": {
            path: {"expected": expected[path], "actual": actual[path]}
            for path in expected
            if path in actual and expected[path] != actual[path]
        },
    }


def _declaration_shape_identity(declaration: dict[str, Any]) -> str:
    shape = {
        "algorithm": {"name": "<algorithm-token>"},
        "boundary": {"fields": ["<field-token>"] * len(declaration["boundary"]["fields"])},
        "canonicalization": {
            "format": "<serialization-token>",
            "sort_keys": declaration["canonicalization"]["sort_keys"],
            "separators": declaration["canonicalization"]["separators"],
            "ensure_ascii": declaration["canonicalization"]["ensure_ascii"],
            "encoding": "<encoding-token>",
        },
        "ordering": {"field": "<field-token>", "direction": "<ordering-token>"},
        "relation": {"type": "<relation-token>"},
    }
    return _value_identity(shape)


def _value_identity(value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _path_value(record: dict[str, Any], path: list[str]) -> Any:
    value: Any = record
    for part in path:
        value = value[part]
    return value


def _without_token(
    vocabulary: dict[str, Any],
    category: str,
    token: str,
) -> dict[str, Any]:
    result = deepcopy(vocabulary)
    del result[category][token]
    return result


def _replace_token(
    vocabulary: dict[str, Any],
    category: str,
    token: str,
    descriptor: dict[str, Any],
) -> dict[str, Any]:
    result = deepcopy(vocabulary)
    result[category][token] = descriptor
    return result


def _replace_identity(
    vocabulary: dict[str, Any],
    *,
    name: str,
    version: str,
    provenance: str,
) -> dict[str, Any]:
    result = deepcopy(vocabulary)
    result["identity"] = {
        "name": name,
        "version": version,
        "provenance": provenance,
    }
    return result


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
    except Exception:  # noqa: BLE001 - keep unavailable execution context visible.
        return None


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
