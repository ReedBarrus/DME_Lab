"""Ledger-wide continuity checks kept separate from per-record integrity."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any


@dataclass(frozen=True)
class ContinuityVerificationResult:
    ok: bool
    record_count: int
    failures: tuple[dict[str, Any], ...]
    duration_seconds: float


def verify_continuity(
    records: list[dict[str, Any]],
    *,
    require_start_at_one: bool = False,
) -> ContinuityVerificationResult:
    started = perf_counter()
    failures: list[dict[str, Any]] = []
    commit_indices = [record.get("commit_index") for record in records]
    record_ids = [record.get("record_id") for record in records]

    duplicate_commit_indices = _duplicates(commit_indices)
    if duplicate_commit_indices:
        failures.append({"kind": "duplicate_commit_index", "values": duplicate_commit_indices})

    duplicate_record_ids = _duplicates(record_ids)
    if duplicate_record_ids:
        failures.append({"kind": "duplicate_record_id", "values": duplicate_record_ids})

    int_indices = [index for index in commit_indices if isinstance(index, int)]
    if len(int_indices) != len(commit_indices):
        failures.append(
            {
                "kind": "invalid_commit_index",
                "values": [index for index in commit_indices if not isinstance(index, int)],
            }
        )
    elif int_indices:
        expected_start = 1 if require_start_at_one else min(int_indices)
        if require_start_at_one and min(int_indices) != 1:
            failures.append({"kind": "unexpected_start_index", "expected": 1, "actual": min(int_indices)})
        missing = sorted(set(range(expected_start, max(int_indices) + 1)) - set(int_indices))
        if missing:
            failures.append({"kind": "missing_commit_index", "values": missing})
    elif records:
        failures.append({"kind": "missing_commit_index", "values": ["all"]})

    return ContinuityVerificationResult(
        ok=not failures,
        record_count=len(records),
        failures=tuple(failures),
        duration_seconds=perf_counter() - started,
    )


def _duplicates(values: list[Any]) -> list[Any]:
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)
