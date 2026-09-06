"""Tiny JSONL append/replay/integrity harness for synthetic ledger pressure."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Any


INTEGRITY_ALGORITHM = "sha256"
HASH_BOUNDARY = (
    "canonical JSON of the ledger record without its integrity field, "
    "using sort_keys=True and compact separators"
)


def canonical_json(value: Any) -> str:
    """Serialize the hash boundary in a stable local form."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_digest(record_without_integrity: dict[str, Any]) -> str:
    payload = canonical_json(record_without_integrity).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    record_count: int
    failures: tuple[dict[str, Any], ...]
    duration_seconds: float


class JsonlLedger:
    """Single-writer, complete-envelope JSONL ledger for synthetic tests."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def append(self, envelope: dict[str, Any], record_id: str | None = None) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        commit_index = self._next_commit_index()
        record_without_integrity = {
            "record_id": record_id or f"rec-{commit_index:06d}",
            "commit_index": commit_index,
            "envelope": envelope,
        }
        record = {
            **record_without_integrity,
            "integrity": {
                "algorithm": INTEGRITY_ALGORITHM,
                "boundary": HASH_BOUNDARY,
                "digest": record_digest(record_without_integrity),
            },
        }
        with self.path.open("a", encoding="utf-8", newline="\n") as ledger_file:
            ledger_file.write(canonical_json(record) + "\n")
        return record

    def replay(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = self._read_records()
        return sorted(records, key=lambda record: record["commit_index"])

    def verify(self) -> VerificationResult:
        started = perf_counter()
        failures: list[dict[str, Any]] = []
        count = 0
        if not self.path.exists():
            return VerificationResult(True, 0, (), perf_counter() - started)

        with self.path.open("r", encoding="utf-8") as ledger_file:
            for line_number, line in enumerate(ledger_file, start=1):
                count += 1
                try:
                    record = json.loads(line)
                    stored = record["integrity"]["digest"]
                    boundary = {
                        "record_id": record["record_id"],
                        "commit_index": record["commit_index"],
                        "envelope": record["envelope"],
                    }
                    actual = record_digest(boundary)
                except Exception as exc:  # noqa: BLE001 - corruption evidence should stay visible.
                    failures.append({"line": line_number, "error": type(exc).__name__})
                    continue
                if stored != actual:
                    failures.append(
                        {
                            "line": line_number,
                            "record_id": record.get("record_id"),
                            "expected": stored,
                            "actual": actual,
                        }
                    )
        return VerificationResult(not failures, count, tuple(failures), perf_counter() - started)

    def _next_commit_index(self) -> int:
        if not self.path.exists():
            return 1
        max_index = 0
        for record in self._read_records():
            max_index = max(max_index, int(record["commit_index"]))
        return max_index + 1

    def _read_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as ledger_file:
            for line in ledger_file:
                if line.strip():
                    records.append(json.loads(line))
        return records

