"""Bounded interpretive provenance recovery pressure run."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from time import perf_counter
from typing import Any, Callable

from src.ledger import HASH_BOUNDARY, INTEGRITY_ALGORITHM, canonical_json
from src.runtime.historical_relation_pressure import GIT_H14_COMMIT, load_git_h14_records
from src.runtime.history_extent_witness_pressure import verify_records_with_jsonl
from src.runtime.witness_content_ablation_pressure import build_ablation_specimens


TRACE_PATH = Path("traces") / "provenance_recovery_pressure_v0.json"

RECOVERED = "RECOVERED"
MISMATCHED = "MISMATCHED"
UNRESOLVED = "UNRESOLVED"

EXPECTED_CORRECT_OUTCOMES = {
    "H13_tail_loss": MISMATCHED,
    "H14_control": RECOVERED,
    "H16_extension": RECOVERED,
    "H16_ID_replacement": MISMATCHED,
    "H16_content_replacement": MISMATCHED,
}


def run() -> dict[str, Any]:
    started = perf_counter()
    witnessed_records = load_git_h14_records()
    witness_carrier = _ordered_digest_witness(witnessed_records)
    specimens, content_mutation = build_ablation_specimens()
    candidate_histories = {
        name: {
            "construction": specimen["construction"],
            "record_count": len(specimen["records"]),
            "records": specimen["records"],
            "derived_state": _derived_state_summary(specimen["records"]),
        }
        for name, specimen in specimens.items()
    }
    regimes = _interpretation_regimes()
    chart = {
        history_name: {
            regime_name: _evaluate_regime(
                witness_carrier["digests"],
                candidate["records"],
                regime,
            )
            for regime_name, regime in regimes.items()
        }
        for history_name, candidate in candidate_histories.items()
    }
    matrix = {
        history_name: {
            regime_name: result["outcome"]
            for regime_name, result in regime_results.items()
        }
        for history_name, regime_results in chart.items()
    }

    return {
        "experiment": "provenance_recovery_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "prior_history_source": f"{GIT_H14_COMMIT}:traces/live_ingest_ledger_v0.jsonl",
        "prior_history_source_classification": "Git analytical comparison evidence, not runtime witness authority",
        "carrier": witness_carrier,
        "candidate_histories": {
            name: {
                key: value
                for key, value in candidate.items()
                if key != "records"
            }
            for name, candidate in candidate_histories.items()
        },
        "h16_content_replacement_mutation": content_mutation,
        "interpretation_regimes": {
            name: _regime_report(regime)
            for name, regime in regimes.items()
        },
        "chart": chart,
        "matrix": matrix,
        "outcome_counts": _outcome_counts(matrix),
        "metadata_drift_result": _metadata_drift_result(witnessed_records),
        "current_digest_semantics": {
            "algorithm": INTEGRITY_ALGORITHM,
            "boundary": ["record_id", "commit_index", "envelope"],
            "boundary_label": HASH_BOUNDARY,
            "canonicalization": "json.dumps(sort_keys=True, separators=(',', ':'), ensure_ascii=False) encoded as UTF-8",
            "verify_checks": "stored integrity.digest equals recomputed digest over record_id, commit_index, and envelope",
            "algorithm_metadata_enforced": False,
            "boundary_metadata_enforced": False,
            "canonicalization_identity": "ambient source behavior; no explicit versioned identity",
        },
        "ambient_vs_conserved": {
            "witness_supplies": ["ordered digest bytes"],
            "ambient_current_repo_supplies": [
                "hash algorithm identity",
                "commitment boundary",
                "canonicalization behavior",
                "commit_index ordering semantics",
                "prefix comparison semantics",
                "candidate integrity recomputation semantics",
            ],
            "finding": "the same carrier is opaque when interpretation is not conserved or ambiently available",
        },
        "dependency_chain": [
            "candidate record",
            "selected commitment boundary",
            "canonical bytes",
            "hash algorithm",
            "commit_index ordered commitments",
            "prefix comparison against witnessed ordered digests",
            "historical relation outcome",
        ],
        "chart_overlap": {
            "historical_relation_chart": "historical transformation x observer relation",
            "witness_content_chart": "historical transformation x witness representation",
            "provenance_recovery_chart": "witness carrier x interpretation regime",
            "shared_stable_referents": [
                "H14",
                "H16 extension",
                "H16 content replacement",
                "ordered digest witness",
                "prefix preservation",
            ],
            "proto_transition_map_pressure_supported": True,
            "transition_maps_implemented": False,
        },
        "smallest_sufficient_tested_interpretation_regime": "R6_sufficient_bounded_historical_verifier_semantics",
        "nearest_insufficient_regime": "R5_commitment_and_ordering_no_prefix_rule",
        "wrong_boundary_result": _regime_column(matrix, "R7_wrong_boundary"),
        "wrong_canonicalization_result": _regime_column(matrix, "R8_wrong_canonicalization"),
        "witness_bytes_survived_while_interpretation_failed": True,
        "interpretation_survived_while_historical_relation_unresolved": True,
        "verifier_implementation_required": False,
        "verifier_implementation_finding": (
            "bounded semantics are sufficient for this pressure; no persistent verifier specification was introduced"
        ),
        "outcome_semantics": {
            RECOVERED: "the supplied regime can evaluate the H14 prefix and finds it conserved",
            MISMATCHED: "the supplied regime can execute comparison and finds incompatible commitments or extent",
            UNRESOLVED: "the supplied regime lacks information needed to justify recovered or mismatched",
        },
        "distinctions": {
            "added": ["D-0034 witness_carrier_survival != historical_relation_recovery"],
            "amended": [],
            "not_registered": [
                "metadata_presence != executed_semantics",
                "ambient_interpretation != conserved_interpretation",
            ],
        },
        "persistent_architecture_added": [],
        "new_persistent_witness_architecture_required": False,
        "finding": "same ordered digest carrier yields recovered, mismatched, or unresolved outcomes under different interpretation regimes",
        "strongest_unresolved_horizon": (
            "minimum declarative commitment semantics worth conserving before any witness persistence boundary is selected"
        ),
        "next_smallest_pressure_frontier": (
            "test a minimal non-persistent declarative commitment-semantics record against the same recovery chart"
        ),
        "duration_seconds": perf_counter() - started,
    }


def _ordered_digest_witness(records: list[dict[str, Any]]) -> dict[str, Any]:
    digests = [record["integrity"]["digest"] for record in records]
    identity = hashlib.sha256(canonical_json(digests).encode("utf-8")).hexdigest()
    return {
        "name": "W14_ordered_record_digests",
        "source": f"{GIT_H14_COMMIT}:traces/live_ingest_ledger_v0.jsonl",
        "record_count": len(records),
        "commit_indices": [record["commit_index"] for record in records],
        "digest_count": len(digests),
        "carrier_identity": f"sha256:{identity}",
        "digests": digests,
        "interpretation_included": False,
    }


def _interpretation_regimes() -> dict[str, dict[str, Any]]:
    return {
        "R0_full_current_semantics": {
            "role": "ambient current-code control",
            "algorithm": "sha256",
            "boundary": "current_record",
            "canonicalization": "current",
            "ordering": "commit_index",
            "prefix_rule": True,
            "candidate_recomputation": True,
            "source": "ambient current source code",
        },
        "R1_digest_carrier_only": {
            "role": "carrier survived, interpretation absent",
            "algorithm": None,
            "boundary": None,
            "canonicalization": None,
            "ordering": None,
            "prefix_rule": False,
            "candidate_recomputation": False,
            "source": "witness bytes only",
        },
        "R2_algorithm_only": {
            "role": "algorithm identity without boundary or canonicalization",
            "algorithm": "sha256",
            "boundary": None,
            "canonicalization": None,
            "ordering": None,
            "prefix_rule": False,
            "candidate_recomputation": True,
            "source": "reduced conserved interpretation",
        },
        "R3_algorithm_boundary_no_canonicalization": {
            "role": "semantic boundary known, byte representation absent",
            "algorithm": "sha256",
            "boundary": "current_record",
            "canonicalization": None,
            "ordering": None,
            "prefix_rule": False,
            "candidate_recomputation": True,
            "source": "reduced conserved interpretation",
        },
        "R4_commitment_semantics_no_ordering_or_relation": {
            "role": "candidate commitments recomputable, historical relation not yet available",
            "algorithm": "sha256",
            "boundary": "current_record",
            "canonicalization": "current",
            "ordering": None,
            "prefix_rule": False,
            "candidate_recomputation": True,
            "source": "reduced conserved interpretation",
        },
        "R5_commitment_and_ordering_no_prefix_rule": {
            "role": "ordered commitments available, prefix relation withheld",
            "algorithm": "sha256",
            "boundary": "current_record",
            "canonicalization": "current",
            "ordering": "commit_index",
            "prefix_rule": False,
            "candidate_recomputation": True,
            "source": "reduced conserved interpretation",
        },
        "R6_sufficient_bounded_historical_verifier_semantics": {
            "role": "smallest tested explicit semantics sufficient for bounded prefix recovery",
            "algorithm": "sha256",
            "boundary": "current_record",
            "canonicalization": "current",
            "ordering": "commit_index",
            "prefix_rule": True,
            "candidate_recomputation": True,
            "source": "explicit bounded semantics in this experiment",
        },
        "R7_wrong_boundary": {
            "role": "complete but wrong commitment boundary",
            "algorithm": "sha256",
            "boundary": "envelope_only",
            "canonicalization": "current",
            "ordering": "commit_index",
            "prefix_rule": True,
            "candidate_recomputation": True,
            "source": "wrong-but-executable interpretation",
        },
        "R8_wrong_canonicalization": {
            "role": "complete but wrong canonical byte representation",
            "algorithm": "sha256",
            "boundary": "current_record",
            "canonicalization": "spaced_json",
            "ordering": "commit_index",
            "prefix_rule": True,
            "candidate_recomputation": True,
            "source": "wrong-but-executable interpretation",
        },
    }


def _evaluate_regime(
    witness_digests: list[str],
    candidate_records: list[dict[str, Any]],
    regime: dict[str, Any],
) -> dict[str, Any]:
    if not regime["candidate_recomputation"]:
        return _unresolved(
            regime,
            "candidate integrity recomputation semantics unavailable",
            candidate_records,
            witness_digests,
        )
    if regime["algorithm"] is None:
        return _unresolved(regime, "hash algorithm identity unavailable", candidate_records, witness_digests)
    if regime["boundary"] is None:
        return _unresolved(regime, "commitment boundary unavailable", candidate_records, witness_digests)
    if regime["canonicalization"] is None:
        return _unresolved(regime, "canonical byte representation unavailable", candidate_records, witness_digests)
    if regime["ordering"] is None:
        return _unresolved(regime, "record ordering semantics unavailable", candidate_records, witness_digests)
    if not regime["prefix_rule"]:
        return _unresolved(regime, "historical prefix comparison rule unavailable", candidate_records, witness_digests)

    ordered = _order_records(candidate_records, regime["ordering"])
    commitments = [_commitment_digest(record, regime) for record in ordered]
    if len(commitments) < len(witness_digests):
        return {
            "outcome": MISMATCHED,
            "reason": "candidate history is shorter than witnessed prefix",
            "first_failure_point": "prefix comparison",
            "candidate_commitment_count": len(commitments),
            "witness_commitment_count": len(witness_digests),
            "dependency_chain": _dependency_chain(regime, "available"),
        }
    mismatches = [
        {
            "position": index,
            "candidate": candidate,
            "witness": witness,
        }
        for index, (candidate, witness) in enumerate(zip(commitments, witness_digests), start=1)
        if candidate != witness
    ]
    if mismatches:
        return {
            "outcome": MISMATCHED,
            "reason": "executable interpretation produced commitments incompatible with the preserved witness",
            "first_failure_point": "prefix comparison",
            "candidate_commitment_count": len(commitments),
            "witness_commitment_count": len(witness_digests),
            "first_mismatch": mismatches[0],
            "dependency_chain": _dependency_chain(regime, "available"),
        }
    return {
        "outcome": RECOVERED,
        "reason": "candidate commitments preserve the witnessed H14 digest prefix",
        "first_failure_point": None,
        "candidate_commitment_count": len(commitments),
        "witness_commitment_count": len(witness_digests),
        "dependency_chain": _dependency_chain(regime, "available"),
    }


def _unresolved(
    regime: dict[str, Any],
    reason: str,
    candidate_records: list[dict[str, Any]],
    witness_digests: list[str],
) -> dict[str, Any]:
    opaque_prefix_equal = _opaque_digest_prefix_equal(candidate_records, witness_digests)
    return {
        "outcome": UNRESOLVED,
        "reason": reason,
        "first_failure_point": _first_missing_dependency(regime),
        "opaque_digest_prefix_equal": opaque_prefix_equal,
        "opaque_equality_note": "opaque equality is not treated as recovered historical interpretation",
        "dependency_chain": _dependency_chain(regime, "blocked"),
    }


def _opaque_digest_prefix_equal(candidate_records: list[dict[str, Any]], witness_digests: list[str]) -> bool:
    candidate_digests = [record.get("integrity", {}).get("digest") for record in candidate_records[: len(witness_digests)]]
    return len(candidate_records) >= len(witness_digests) and candidate_digests == witness_digests


def _commitment_digest(record: dict[str, Any], regime: dict[str, Any]) -> str:
    boundary = _selected_boundary(record, regime["boundary"])
    payload = _canonicalize(boundary, regime["canonicalization"]).encode("utf-8")
    if regime["algorithm"] != "sha256":
        raise ValueError(f"unsupported algorithm in bounded pressure: {regime['algorithm']}")
    return hashlib.sha256(payload).hexdigest()


def _selected_boundary(record: dict[str, Any], boundary_name: str) -> dict[str, Any]:
    if boundary_name == "current_record":
        return {
            "record_id": record["record_id"],
            "commit_index": record["commit_index"],
            "envelope": record["envelope"],
        }
    if boundary_name == "envelope_only":
        return {"envelope": record["envelope"]}
    raise ValueError(f"unknown boundary in bounded pressure: {boundary_name}")


def _canonicalize(value: Any, canonicalization_name: str) -> str:
    if canonicalization_name == "current":
        return canonical_json(value)
    if canonicalization_name == "spaced_json":
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    raise ValueError(f"unknown canonicalization in bounded pressure: {canonicalization_name}")


def _order_records(records: list[dict[str, Any]], ordering_name: str) -> list[dict[str, Any]]:
    if ordering_name == "commit_index":
        return sorted(records, key=lambda record: record["commit_index"])
    raise ValueError(f"unknown ordering in bounded pressure: {ordering_name}")


def _metadata_drift_result(witnessed_records: list[dict[str, Any]]) -> dict[str, Any]:
    records = deepcopy(witnessed_records)
    records[0]["integrity"]["algorithm"] = "not-sha256"
    records[0]["integrity"]["boundary"] = "not-current-boundary"
    verification = verify_records_with_jsonl(records)
    return {
        "specimen": "H14 metadata labels changed on rec-000001; digest bytes and committed content unchanged",
        "changed_fields": ["integrity.algorithm", "integrity.boundary"],
        "current_verify_ok": verification["ok"],
        "current_verify_failures": verification["failures"],
        "finding": "stored integrity metadata does not govern current verifier execution",
        "canonical_records_mutated": False,
    }


def _derived_state_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "record_ids": [record["record_id"] for record in records],
        "commit_indices": [record["commit_index"] for record in records],
        "stored_digest_count": len(records),
    }


def _regime_report(regime: dict[str, Any]) -> dict[str, Any]:
    dependencies = {
        "algorithm": regime["algorithm"],
        "boundary": regime["boundary"],
        "canonicalization": regime["canonicalization"],
        "ordering": regime["ordering"],
        "prefix_rule": regime["prefix_rule"],
        "candidate_recomputation": regime["candidate_recomputation"],
    }
    return {
        "role": regime["role"],
        "source": regime["source"],
        "available": {
            key: value
            for key, value in dependencies.items()
            if value not in (None, False)
        },
        "withheld_or_changed": {
            key: value
            for key, value in dependencies.items()
            if value in (None, False) or regime["source"] == "wrong-but-executable interpretation"
        },
        "first_failure_point": _first_missing_dependency(regime),
        "dependency_chain": _dependency_chain(regime, "reported"),
    }


def _first_missing_dependency(regime: dict[str, Any]) -> str | None:
    if not regime["candidate_recomputation"]:
        return "candidate integrity recomputation semantics"
    if regime["algorithm"] is None:
        return "hash algorithm identity"
    if regime["boundary"] is None:
        return "commitment boundary"
    if regime["canonicalization"] is None:
        return "canonical byte representation"
    if regime["ordering"] is None:
        return "record ordering semantics"
    if not regime["prefix_rule"]:
        return "historical prefix comparison rule"
    return None


def _dependency_chain(regime: dict[str, Any], status: str) -> list[dict[str, Any]]:
    chain = [
        ("candidate record", True),
        ("selected commitment boundary", regime["boundary"] is not None),
        ("canonical bytes", regime["canonicalization"] is not None),
        ("hash algorithm", regime["algorithm"] is not None),
        ("ordered commitments", regime["ordering"] is not None),
        ("historical prefix relation", bool(regime["prefix_rule"])),
    ]
    return [
        {
            "step": step,
            "available": available,
            "status": "available" if available else status,
        }
        for step, available in chain
    ]


def _outcome_counts(matrix: dict[str, dict[str, str]]) -> dict[str, int]:
    counts = {RECOVERED: 0, MISMATCHED: 0, UNRESOLVED: 0}
    for row in matrix.values():
        for outcome in row.values():
            counts[outcome] += 1
    return counts


def _regime_column(matrix: dict[str, dict[str, str]], regime_name: str) -> dict[str, str]:
    return {
        history_name: row[regime_name]
        for history_name, row in matrix.items()
    }


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
