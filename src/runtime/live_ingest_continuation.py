"""Replay helpers for bounded canonical live ingest continuation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ledger import replay_canonical_live_ingest, verify_canonical_live_ingest
from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships


TRACE_PATH = Path("traces") / "live_ingest_continuation_v0.json"


def load_report(path: Path | str = TRACE_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    return replay_canonical_live_ingest(report["canonical_ledger_path"])


def rebuild_from_canonical_ledger(report: dict[str, Any]) -> dict[str, Any]:
    records_a = canonical_records(report)
    reconstruction_a = reconstruct_admission_relationships(records_a)
    projection_a = derive_admitted_projection(reconstruction_a)
    records_b = canonical_records(report)
    reconstruction_b = reconstruct_admission_relationships(records_b)
    projection_b = derive_admitted_projection(reconstruction_b)
    return {
        "records_a": records_a,
        "records_b": records_b,
        "reconstruction_a": reconstruction_a,
        "projection_a": projection_a,
        "reconstruction_b": reconstruction_b,
        "projection_b": projection_b,
        "reconstruction_structural_equality": reconstruction_a == reconstruction_b,
        "projection_structural_equality": projection_a == projection_b,
        "disk_replay_structural_equality": records_a == records_b,
    }


def verify_canonical_ledger(report: dict[str, Any]):
    return verify_canonical_live_ingest(report["canonical_ledger_path"])
