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
