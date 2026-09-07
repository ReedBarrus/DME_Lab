"""Narrow history-extent correspondence checks."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any


@dataclass(frozen=True)
class HistoryExtentComparisonResult:
    ok: bool
    current_extent: dict[str, Any]
    witnessed_extent: dict[str, Any]
    mismatches: tuple[dict[str, Any], ...]
    interpretation: str
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "current_extent": self.current_extent,
            "witnessed_extent": self.witnessed_extent,
            "mismatches": list(self.mismatches),
            "interpretation": self.interpretation,
            "duration_seconds": self.duration_seconds,
        }


@dataclass(frozen=True)
class HistoryRelationResult:
    ok: bool
    relation: str
    details: dict[str, Any]
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "relation": self.relation,
            "details": self.details,
            "duration_seconds": self.duration_seconds,
        }


def history_extent(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "record_count": 0,
            "terminal_record_id": None,
            "terminal_commit_index": None,
        }
    terminal = records[-1]
    return {
        "record_count": len(records),
        "terminal_record_id": terminal.get("record_id"),
        "terminal_commit_index": terminal.get("commit_index"),
    }


def compare_history_extent(
    current_extent: dict[str, Any],
    witnessed_extent: dict[str, Any],
) -> HistoryExtentComparisonResult:
    started = perf_counter()
    fields = ("record_count", "terminal_record_id", "terminal_commit_index")
    mismatches = []
    for field in fields:
        current_value = current_extent.get(field)
        witnessed_value = witnessed_extent.get(field)
        if current_value != witnessed_value:
            mismatches.append(
                {
                    "field": field,
                    "current": current_value,
                    "witnessed": witnessed_value,
                }
            )

    return HistoryExtentComparisonResult(
        ok=not mismatches,
        current_extent=current_extent,
        witnessed_extent=witnessed_extent,
        mismatches=tuple(mismatches),
        interpretation="extent_correspondence_only_not_corruption_proof",
        duration_seconds=perf_counter() - started,
    )


def compare_extent_lower_bound(
    current_extent: dict[str, Any],
    witnessed_extent: dict[str, Any],
) -> HistoryRelationResult:
    started = perf_counter()
    comparisons = {
        "record_count": {
            "current": current_extent.get("record_count"),
            "witnessed": witnessed_extent.get("record_count"),
            "ok": current_extent.get("record_count", -1) >= witnessed_extent.get("record_count", 0),
        },
        "terminal_commit_index": {
            "current": current_extent.get("terminal_commit_index"),
            "witnessed": witnessed_extent.get("terminal_commit_index"),
            "ok": current_extent.get("terminal_commit_index", -1)
            >= witnessed_extent.get("terminal_commit_index", 0),
        },
    }
    return HistoryRelationResult(
        ok=all(comparison["ok"] for comparison in comparisons.values()),
        relation="extent_lower_bound",
        details={
            "comparisons": comparisons,
            "interpretation": "current extent has not fallen below witnessed extent",
        },
        duration_seconds=perf_counter() - started,
    )


def prefix_identity(record: dict[str, Any]) -> dict[str, Any]:
    integrity = record.get("integrity", {})
    return {
        "record_id": record.get("record_id"),
        "commit_index": record.get("commit_index"),
        "integrity_algorithm": integrity.get("algorithm"),
        "integrity_boundary": integrity.get("boundary"),
        "integrity_digest": integrity.get("digest"),
    }


def compare_prefix_preservation(
    current_records: list[dict[str, Any]],
    witnessed_records: list[dict[str, Any]],
) -> HistoryRelationResult:
    started = perf_counter()
    current_prefix = [prefix_identity(record) for record in current_records[: len(witnessed_records)]]
    witnessed_prefix = [prefix_identity(record) for record in witnessed_records]
    length_ok = len(current_records) >= len(witnessed_records)
    mismatches = []
    if length_ok:
        for index, (current, witnessed) in enumerate(zip(current_prefix, witnessed_prefix), start=1):
            if current != witnessed:
                mismatches.append({"position": index, "current": current, "witnessed": witnessed})
    else:
        mismatches.append(
            {
                "kind": "current_shorter_than_witness",
                "current_record_count": len(current_records),
                "witnessed_record_count": len(witnessed_records),
            }
        )

    return HistoryRelationResult(
        ok=length_ok and not mismatches,
        relation="prefix_preservation",
        details={
            "identity_fields": [
                "record_id",
                "commit_index",
                "integrity.algorithm",
                "integrity.boundary",
                "integrity.digest",
            ],
            "current_prefix_count_checked": len(current_prefix),
            "witnessed_record_count": len(witnessed_records),
            "mismatches": mismatches,
            "interpretation": "witnessed history remains structurally conserved as current ordered prefix",
        },
        duration_seconds=perf_counter() - started,
    )
