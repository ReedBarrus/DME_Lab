"""Compare v0 runtime ledger records against the shadow record schema."""

from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ledger import (
    HASH_BOUNDARY,
    JsonlLedger,
    SCHEMA_PATH,
    amendment_pair,
    canonical_json,
    identity_collision_envelopes,
    load_schema,
    missingness_envelopes,
    ordering_conflict_envelopes,
    preservation_envelope,
    record_digest,
    validate_ledger_record,
)


def _runtime_records() -> list[dict[str, Any]]:
    envelopes = (
        ordering_conflict_envelopes()
        + identity_collision_envelopes()
        + [preservation_envelope()]
        + missingness_envelopes()
        + amendment_pair()
    )
    with TemporaryDirectory() as tmpdir:
        ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
        return [ledger.append(envelope) for envelope in envelopes]


def _validation_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    details = []
    for index, record in enumerate(records, start=1):
        result = validate_ledger_record(record)
        details.append(
            {
                "index": index,
                "record_id": record.get("record_id"),
                "valid": result.valid,
                "errors": [error.to_dict() for error in result.errors],
            }
        )
    return {
        "records_tested": len(records),
        "conforming_count": sum(1 for detail in details if detail["valid"]),
        "nonconforming_count": sum(1 for detail in details if not detail["valid"]),
        "details": details,
    }


def _edge_record(envelope: Any) -> dict[str, Any]:
    boundary = {
        "record_id": "edge-000001",
        "commit_index": 1,
        "envelope": envelope,
    }
    return {
        **boundary,
        "integrity": {
            "algorithm": "sha256",
            "boundary": HASH_BOUNDARY,
            "digest": record_digest(boundary),
        },
    }


def _json_domain_cases() -> list[dict[str, Any]]:
    cases = [
        ("string", {"value": "text"}),
        ("integer", {"value": 7}),
        ("float", {"value": 7.25}),
        ("boolean", {"value": True}),
        ("null", {"value": None}),
        ("array", {"value": [1, "two", False]}),
        ("nested_object", {"value": {"inner": "kept"}}),
        ("empty_string", {"value": ""}),
        ("empty_array", {"value": []}),
        ("empty_object", {}),
        ("nan", {"value": math.nan}),
        ("infinity", {"value": math.inf}),
        ("negative_infinity", {"value": -math.inf}),
        ("non_string_key", {1: "numeric key"}),
    ]
    results = []
    for name, envelope in cases:
        try:
            record = _edge_record(envelope)
            runtime_error = None
        except Exception as exc:  # noqa: BLE001 - boundary pressure should remain visible.
            record = None
            runtime_error = type(exc).__name__
        validation = validate_ledger_record(record) if record is not None else None
        results.append(
            {
                "case": name,
                "runtime_record_created": record is not None,
                "runtime_error": runtime_error,
                "schema_valid": validation.valid if validation else False,
                "schema_errors": [error.to_dict() for error in validation.errors] if validation else [],
            }
        )
    return results


def _runtime_possible_schema_rejected() -> list[dict[str, Any]]:
    cases = [
        ("array_envelope", ["runtime can hash this list envelope"]),
        ("nan_envelope_value", {"value": math.nan}),
    ]
    results = []
    with TemporaryDirectory() as tmpdir:
        ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
        for name, envelope in cases:
            try:
                record = ledger.append(envelope)  # type: ignore[arg-type]
                verification = ledger.verify()
                validation = validate_ledger_record(record)
                results.append(
                    {
                        "case": name,
                        "runtime_produced": True,
                        "runtime_verification_ok": verification.ok,
                        "schema_valid": validation.valid,
                        "schema_errors": [error.to_dict() for error in validation.errors],
                    }
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "case": name,
                        "runtime_produced": False,
                        "runtime_error": type(exc).__name__,
                        "schema_valid": False,
                        "schema_errors": [],
                    }
                )
    return results


def _schema_allowed_runtime_problematic() -> list[dict[str, Any]]:
    record = _edge_record({"value": "schema-valid structure"})
    record["integrity"]["digest"] = "0" * 64
    validation = validate_ledger_record(record)

    with TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "ledger.jsonl"
        ledger_path.write_text(canonical_json(record) + "\n", encoding="utf-8")
        ledger = JsonlLedger(ledger_path)
        replayed = ledger.replay()
        verification = ledger.verify()

    return [
        {
            "case": "schema_valid_bad_digest",
            "schema_valid": validation.valid,
            "runtime_serialized": True,
            "runtime_replayed": len(replayed) == 1,
            "runtime_integrity_ok": verification.ok,
            "runtime_pressure": "schema validity does not establish integrity validity",
        }
    ]


def _missingness_cases() -> list[dict[str, Any]]:
    records = []
    with TemporaryDirectory() as tmpdir:
        ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
        for synthetic_envelope in missingness_envelopes():
            records.append(ledger.append(synthetic_envelope))

    results = []
    for record in records:
        validation = validate_ledger_record(record)
        state = next(iter(record["envelope"]["missingness"].values()))
        results.append(
            {
                "record_id": record["record_id"],
                "missingness_state": state,
                "schema_valid": validation.valid,
                "schema_visible_distinction": "envelope object preserves member structure only",
                "convention_dependent": True,
            }
        )
    return results


def _mutated_schema_valid_integrity_invalid() -> dict[str, Any]:
    record = _edge_record({"value": "before"})
    mutated = deepcopy(record)
    mutated["envelope"]["value"] = "after"
    validation = validate_ledger_record(mutated)

    with TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "ledger.jsonl"
        ledger_path.write_text(canonical_json(mutated) + "\n", encoding="utf-8")
        verification = JsonlLedger(ledger_path).verify()

    return {
        "schema_valid": validation.valid,
        "integrity_valid": verification.ok,
        "finding": "mutated record remains schema-valid while failing integrity verification",
    }


def run() -> dict[str, Any]:
    started = perf_counter()
    schema = load_schema()
    records = _runtime_records()
    conformance = _validation_summary(records)
    report = {
        "schema_path": str(SCHEMA_PATH).replace("\\", "/"),
        "schema_title": schema.get("title"),
        "schema_status": "descriptive shadow-only hypothesis",
        "schema_boundary": "one LedgerRecord with record_id, commit_index, envelope, and integrity",
        "runtime_records": conformance,
        "json_domain_edge_cases": _json_domain_cases(),
        "runtime_possible_schema_rejected": _runtime_possible_schema_rejected(),
        "schema_allowed_runtime_problematic": _schema_allowed_runtime_problematic(),
        "missingness_cases": _missingness_cases(),
        "structural_validity_vs_integrity_validity": _mutated_schema_valid_integrity_invalid(),
        "unsupported_cross_record_guarantees": [
            "unique record_id",
            "monotonic commit_index",
            "append-only history",
            "deterministic replay order",
            "amendment relationship behavior",
            "history integrity",
        ],
    }
    report["duration_seconds"] = perf_counter() - started
    return report


def main() -> None:
    report = run()
    output_path = Path("traces") / "ledger_schema_pressure_v0.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

