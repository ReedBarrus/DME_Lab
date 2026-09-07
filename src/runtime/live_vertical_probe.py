"""Replay helpers for the bounded live vertical probe trace."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships


TRACE_PATH = Path("traces") / "live_vertical_probe_v0.json"


def load_report(path: Path | str = TRACE_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def authoritative_records(report: dict[str, Any]) -> list[dict[str, Any]]:
    return deepcopy(report["authoritative_history"]["records"])


def rebuild_from_report(report: dict[str, Any]) -> dict[str, Any]:
    records = authoritative_records(report)
    reconstruction_a = reconstruct_admission_relationships(records)
    projection_a = derive_admitted_projection(reconstruction_a)
    reconstruction_b = reconstruct_admission_relationships(authoritative_records(report))
    projection_b = derive_admitted_projection(reconstruction_b)
    return {
        "reconstruction_a": reconstruction_a,
        "projection_a": projection_a,
        "reconstruction_b": reconstruction_b,
        "projection_b": projection_b,
        "reconstruction_structural_equality": reconstruction_a == reconstruction_b,
        "projection_structural_equality": projection_a == projection_b,
    }


def find_record(records: list[dict[str, Any]], record_id: str) -> dict[str, Any]:
    for record in records:
        if record["record_id"] == record_id:
            return record
    raise KeyError(record_id)
