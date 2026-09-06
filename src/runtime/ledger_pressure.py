"""Run synthetic ledger pressure scenarios and emit a small evidence artifact."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable

from src.ledger import (
    HASH_BOUNDARY,
    JsonlLedger,
    amendment_pair,
    identity_collision_envelopes,
    missingness_envelopes,
    ordering_conflict_envelopes,
    preservation_envelope,
)


EnvelopeFactory = Callable[[], list[dict[str, Any]]]


def _append_all(ledger: JsonlLedger, envelopes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float]:
    started = perf_counter()
    records = [ledger.append(envelope) for envelope in envelopes]
    return records, perf_counter() - started


def _scenario(name: str, guarantee: str, mechanism: str, factory: EnvelopeFactory) -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / f"{name}.jsonl"
        ledger = JsonlLedger(ledger_path)
        records, append_duration = _append_all(ledger, factory())

        replay_started = perf_counter()
        replayed = ledger.replay()
        replay_duration = perf_counter() - replay_started

        verification = ledger.verify()
        passed = verification.ok and [record["record_id"] for record in replayed] == [
            record["record_id"] for record in records
        ]
        return {
            "name": name,
            "guarantee": guarantee,
            "mechanism": mechanism,
            "passed": passed,
            "outcome": "survived" if passed else "failed",
            "what_happened": f"{len(replayed)} records appended and replayed in canonical commit order",
            "records": len(replayed),
            "bytes_written": ledger_path.stat().st_size,
            "append_duration_seconds": append_duration,
            "replay_duration_seconds": replay_duration,
            "verification_duration_seconds": verification.duration_seconds,
            "pressure": "none observed in synthetic local run" if passed else "guarantee weakened",
        }


def _integrity_mutation_scenario() -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "integrity.jsonl"
        ledger = JsonlLedger(ledger_path)
        ledger.append(preservation_envelope())
        before = ledger.verify()

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace("sig-preserve", "sig-mutated", 1), encoding="utf-8")

        after = ledger.verify()
        return {
            "name": "integrity_mutation",
            "guarantee": "integrity",
            "mechanism": "append one record, mutate persisted content, then verify per-record hash",
            "passed": before.ok and not after.ok,
            "outcome": "survived" if before.ok and not after.ok else "failed",
            "what_happened": "verification passed before mutation and failed after persisted content changed",
            "records": after.record_count,
            "bytes_written": ledger_path.stat().st_size,
            "append_duration_seconds": None,
            "replay_duration_seconds": None,
            "verification_duration_seconds": after.duration_seconds,
            "pressure": "mutation detected by per-record hash",
            "failure_count_after_mutation": len(after.failures),
        }


def run() -> dict[str, Any]:
    scenarios = [
        _scenario(
            "ordering_conflict",
            "deterministic order",
            "append envelopes whose source sequence and event time disagree with commit order",
            ordering_conflict_envelopes,
        ),
        _scenario(
            "identity_collision",
            "stable identity",
            "append records with duplicate envelope identity and distinct ledger record identities",
            identity_collision_envelopes,
        ),
        _scenario(
            "envelope_preservation",
            "envelope preservation",
            "append and replay a complete envelope containing opaque payload, explicit null, and missing field evidence",
            lambda: [preservation_envelope()],
        ),
        _integrity_mutation_scenario(),
        _scenario(
            "missingness",
            "missingness preservation",
            "append separate envelopes for absent, explicit null, unavailable, and malformed states",
            missingness_envelopes,
        ),
        _scenario(
            "append_only_amendment",
            "append-only amendment",
            "append original record and later amendment record pointing at the original",
            amendment_pair,
        ),
    ]
    return {
        "runtime_scope": "synthetic ledger append/replay/integrity only",
        "integrity_hash_boundary": HASH_BOUNDARY,
        "scenarios": scenarios,
        "passed": sum(1 for scenario in scenarios if scenario["passed"]),
        "failed": sum(1 for scenario in scenarios if not scenario["passed"]),
    }


def main() -> None:
    report = run()
    output_path = Path("traces") / "ledger_runtime_pressure_v0.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
