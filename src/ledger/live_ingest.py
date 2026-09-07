"""Canonical bounded live ingest ledger access."""

from __future__ import annotations

from pathlib import Path

from .jsonl import JsonlLedger, VerificationResult


CANONICAL_LIVE_INGEST_LEDGER_PATH = Path("traces") / "live_ingest_ledger_v0.jsonl"


def canonical_live_ingest_ledger(
    path: Path | str = CANONICAL_LIVE_INGEST_LEDGER_PATH,
) -> JsonlLedger:
    return JsonlLedger(path)


def replay_canonical_live_ingest(
    path: Path | str = CANONICAL_LIVE_INGEST_LEDGER_PATH,
) -> list[dict[str, object]]:
    return canonical_live_ingest_ledger(path).replay()


def verify_canonical_live_ingest(
    path: Path | str = CANONICAL_LIVE_INGEST_LEDGER_PATH,
) -> VerificationResult:
    return canonical_live_ingest_ledger(path).verify()
