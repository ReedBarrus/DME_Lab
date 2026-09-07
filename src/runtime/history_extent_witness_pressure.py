"""Bounded history-extent witness pressure run."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ledger import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    JsonlLedger,
    canonical_json,
    compare_history_extent,
    history_extent,
    replay_canonical_live_ingest,
    verify_canonical_live_ingest,
    verify_continuity,
)
from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships


TRACE_PATH = Path("traces") / "history_extent_witness_pressure_v0.json"
PRIMARY_WITNESS_PATH = Path("traces") / "live_ingest_continuation_v0.json"
GIT_H14_COMMIT = "e399720"


def load_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def extent_from_continuation_witness(report: dict[str, Any]) -> dict[str, Any]:
    enlarged = report["enlarged_history"]
    return {
        "record_count": enlarged["record_count"],
        "terminal_record_id": enlarged["record_ids"][-1],
        "terminal_commit_index": enlarged["commit_indices"][-1],
    }


def summarize_derived_state(records: list[dict[str, Any]]) -> dict[str, Any]:
    reconstruction = reconstruct_admission_relationships(records)
    projection = derive_admitted_projection(reconstruction)
    return {
        "reconstruction": {
            "observation_count": len(reconstruction["observations"]),
            "admission_relation_count": sum(len(observation["admissions"]) for observation in reconstruction["observations"]),
            "orphan_admission_count": len(reconstruction["orphan_admissions"]),
            "authoritative_record_ids": reconstruction["authoritative_record_ids"],
        },
        "projection": {
            "subject_count": len(projection),
            "subject_record_ids": [item["subject_record_id"] for item in projection],
        },
    }


def verify_records_with_jsonl(records: list[dict[str, Any]]) -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "ledger.jsonl"
        path.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="utf-8")
        result = JsonlLedger(path).verify()
    return {
        "ok": result.ok,
        "record_count": result.record_count,
        "failures": list(result.failures),
    }


def continuity_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    result = verify_continuity(records, require_start_at_one=True)
    return {
        "ok": result.ok,
        "record_count": result.record_count,
        "failures": list(result.failures),
    }


def git_h14_summary() -> dict[str, Any]:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{GIT_H14_COMMIT}:traces/live_ingest_ledger_v0.jsonl"],
            text=True,
            encoding="utf-8",
        )
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except Exception as exc:  # noqa: BLE001 - Git is witness evidence, not required runtime storage.
        return {
            "checked": True,
            "preserves_h14": False,
            "classification": "direct historical representation, not canonical runtime authority",
            "error": type(exc).__name__,
        }

    extent = history_extent(records)
    return {
        "checked": True,
        "commit": GIT_H14_COMMIT,
        "preserves_h14": extent
        == {
            "record_count": 14,
            "terminal_record_id": "rec-000014",
            "terminal_commit_index": 14,
        },
        "classification": "direct historical representation, not canonical runtime authority",
        "extent": extent,
    }


def run() -> dict[str, Any]:
    started = perf_counter()
    witness_report = load_json(PRIMARY_WITNESS_PATH)
    witness_extent = extent_from_continuation_witness(witness_report)

    h14_records = replay_canonical_live_ingest(CANONICAL_LIVE_INGEST_LEDGER_PATH)
    h13_records = deepcopy(h14_records[:-1])

    h14_extent = history_extent(h14_records)
    h13_extent = history_extent(h13_records)
    h14_correspondence = compare_history_extent(h14_extent, witness_extent)
    h13_correspondence = compare_history_extent(h13_extent, witness_extent)
    h14_state = summarize_derived_state(h14_records)
    h13_state = summarize_derived_state(h13_records)

    missing_subjects = sorted(
        set(h14_state["projection"]["subject_record_ids"]) - set(h13_state["projection"]["subject_record_ids"])
    )

    return {
        "experiment": "history_extent_witness_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "canonical_ledger_path": str(CANONICAL_LIVE_INGEST_LEDGER_PATH).replace("\\", "/"),
        "selected_witness_artifact": str(PRIMARY_WITNESS_PATH).replace("\\", "/"),
        "selected_witness_classification": "derived experiment witness",
        "extent_fields": ["record_count", "terminal_record_id", "terminal_commit_index"],
        "h14": {
            "extent": h14_extent,
            "record_integrity": _verification_summary(verify_canonical_live_ingest(CANONICAL_LIVE_INGEST_LEDGER_PATH)),
            "continuity": continuity_summary(h14_records),
            "witness_correspondence": h14_correspondence.to_dict(),
            **h14_state,
        },
        "h13_tail_loss_specimen": {
            "specimen_policy": "temporary in-memory records derived from H14 without rec-000014; canonical ledger not mutated",
            "extent": h13_extent,
            "record_integrity": verify_records_with_jsonl(h13_records),
            "continuity": continuity_summary(h13_records),
            "witness_correspondence": h13_correspondence.to_dict(),
            **h13_state,
        },
        "exact_missing_relation": {
            "surviving_observation_record_id": "rec-000013",
            "missing_admission_record_id": "rec-000014",
            "missing_admission_subject_record_id": "rec-000013",
            "lost_projection_subject_ids": missing_subjects,
        },
        "ambiguity_preserved": {
            "corruption_proven": False,
            "claim": "current ledger extent conflicts with previously preserved witness evidence",
            "repair_attempted": False,
        },
        "git_h14_witness": git_h14_summary(),
        "new_persistent_architecture_required": False,
        "persistent_architecture_added": [],
        "hash_chain_pressure": {
            "earned": False,
            "finding": "existing witness evidence detects this bounded tail-loss mismatch without hash chaining",
        },
        "unresolved_horizon": "whether DME_Lab should conserve first-class extent witnesses rather than rely on incidental experiment traces",
        "duration_seconds": perf_counter() - started,
    }


def _verification_summary(result: Any) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "record_count": result.record_count,
        "failures": list(result.failures),
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
