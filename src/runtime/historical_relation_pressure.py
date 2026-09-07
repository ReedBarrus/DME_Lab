"""Four-way bounded historical relation pressure run."""

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
    compare_extent_lower_bound,
    compare_history_extent,
    compare_prefix_preservation,
    history_extent,
    record_digest,
    replay_canonical_live_ingest,
    verify_continuity,
)
from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships
from src.runtime.history_extent_witness_pressure import (
    extent_from_continuation_witness,
    load_json,
    verify_records_with_jsonl,
)


TRACE_PATH = Path("traces") / "historical_relation_pressure_v0.json"
CONTINUATION_WITNESS_PATH = Path("traces") / "live_ingest_continuation_v0.json"
GIT_H14_COMMIT = "e399720"
PREFIX_IDENTITY_FIELDS = [
    "record_id",
    "commit_index",
    "integrity.algorithm",
    "integrity.boundary",
    "integrity.digest",
]


def load_git_h14_records(commit: str = GIT_H14_COMMIT) -> list[dict[str, Any]]:
    raw = subprocess.check_output(
        ["git", "show", f"{commit}:traces/live_ingest_ledger_v0.jsonl"],
        text=True,
        encoding="utf-8",
    )
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def make_h16_extension(h14_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "ledger.jsonl"
        path.write_text("".join(canonical_json(record) + "\n" for record in h14_records), encoding="utf-8")
        ledger = JsonlLedger(path)
        ledger.append(_extension_observation())
        ledger.append(_extension_admission())
        return ledger.replay()


def make_h16_replacement(h16_extension: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = deepcopy(h16_extension)
    records[0]["record_id"] = "rec-999001"
    _rehash(records[0])
    return records


def build_specimens() -> dict[str, dict[str, Any]]:
    h14 = replay_canonical_live_ingest(CANONICAL_LIVE_INGEST_LEDGER_PATH)
    h16_extension = make_h16_extension(deepcopy(h14))
    return {
        "H13_tail_loss": {
            "construction": "copy canonical H14 records 1..13; omit complete rec-000014",
            "records": deepcopy(h14[:-1]),
        },
        "H14_control": {
            "construction": "current canonical H14 replay records 1..14",
            "records": deepcopy(h14),
        },
        "H16_extension": {
            "construction": "temporary JSONL copy of H14 plus appended rec-000015 observation and rec-000016 admission",
            "records": h16_extension,
        },
        "H16_replacement": {
            "construction": "H16 extension with record 1 record_id changed to rec-999001 and digest recomputed",
            "records": make_h16_replacement(h16_extension),
        },
    }


def evaluate_specimen(
    records: list[dict[str, Any]],
    *,
    witnessed_extent: dict[str, Any],
    witnessed_records: list[dict[str, Any]],
) -> dict[str, Any]:
    integrity = verify_records_with_jsonl(records)
    continuity = verify_continuity(records, require_start_at_one=True)
    extent = history_extent(records)
    equality = compare_history_extent(extent, witnessed_extent)
    lower_bound = compare_extent_lower_bound(extent, witnessed_extent)
    prefix = compare_prefix_preservation(records, witnessed_records)
    reconstruction = reconstruct_admission_relationships(records)
    projection = derive_admitted_projection(reconstruction)
    return {
        "integrity": integrity,
        "continuity": {
            "ok": continuity.ok,
            "record_count": continuity.record_count,
            "failures": list(continuity.failures),
        },
        "extent": extent,
        "relations": {
            "equality": equality.to_dict(),
            "lower_bound": lower_bound.to_dict(),
            "prefix": prefix.to_dict(),
        },
        "derived_state": {
            "observation_count": len(reconstruction["observations"]),
            "admission_relation_count": sum(len(observation["admissions"]) for observation in reconstruction["observations"]),
            "orphan_admission_count": len(reconstruction["orphan_admissions"]),
            "projection_subject_count": len(projection),
            "projection_subject_ids": [item["subject_record_id"] for item in projection],
        },
    }


def run() -> dict[str, Any]:
    started = perf_counter()
    witness_report = load_json(CONTINUATION_WITNESS_PATH)
    witnessed_extent = extent_from_continuation_witness(witness_report)
    witnessed_records = load_git_h14_records()
    specimens = build_specimens()

    specimen_results = {
        name: {
            "construction": specimen["construction"],
            **evaluate_specimen(
                specimen["records"],
                witnessed_extent=witnessed_extent,
                witnessed_records=witnessed_records,
            ),
        }
        for name, specimen in specimens.items()
    }
    matrix = {
        name: {
            "equality": result["relations"]["equality"]["ok"],
            "lower_bound": result["relations"]["lower_bound"]["ok"],
            "prefix": result["relations"]["prefix"]["ok"],
        }
        for name, result in specimen_results.items()
    }

    return {
        "experiment": "historical_relation_pressure_v0",
        "starting_commit": _git_rev_parse_head(),
        "prior_witnessed_history": {
            "extent_source": str(CONTINUATION_WITNESS_PATH).replace("\\", "/"),
            "extent_source_classification": "derived experiment witness",
            "prefix_source": f"{GIT_H14_COMMIT}:traces/live_ingest_ledger_v0.jsonl",
            "prefix_source_classification": "Git analytical comparison evidence, not runtime witness authority",
            "extent": witnessed_extent,
            "prefix_record_count": len(witnessed_records),
        },
        "prefix_identity_fields": PREFIX_IDENTITY_FIELDS,
        "specimens": specimen_results,
        "pressure_matrix": matrix,
        "observer_collapse_findings": {
            "equality": "collapses loss, extension, and replacement into generic mismatch",
            "lower_bound": "separates shrinkage from non-shrinkage, but collapses extension and replacement",
            "prefix": "distinguishes loss, control, extension, and replacement within this bounded append-only pressure",
        },
        "finding": "extent growth does not establish historical conservation",
        "prefix_identity_required_new_information": False,
        "git_supplied_historical_evidence": True,
        "new_persistent_witness_architecture_required": False,
        "persistent_architecture_added": [],
        "observer_relation_pattern": (
            "observer relation partitions historical state space; pressure reveals collapsed distinctions; "
            "refined relation increases distinguishability"
        ),
        "unresolved_horizon": "minimum first-class prefix witness content without creating checkpoint or manifest architecture",
        "duration_seconds": perf_counter() - started,
    }


def _extension_observation() -> dict[str, Any]:
    return {
        "record_type": "observation",
        "source": "pressure_fixture",
        "provenance": {"basis": "temporary_h16_extension"},
        "observation": {
            "source": "pressure_fixture",
            "source_sequence": None,
            "arrival_time": None,
            "event_time": None,
            "capture_version": "temporary_pressure_v0",
            "envelope_identity": "temporary-h16-extension-15",
            "missingness": {},
            "provenance": {"basis": "temporary_h16_extension"},
            "signal": {
                "identity": "temporary-h16-extension-15",
                "time": None,
                "type": "pressure.fixture",
                "payload": {},
            },
        },
    }


def _extension_admission() -> dict[str, Any]:
    return {
        "record_type": "admission",
        "subject_record_id": "rec-000015",
        "comparator_identity": "pressure_fixture",
        "comparator_version": "v0",
        "comparison_result": {"status": "compared", "valid": True, "errors": []},
        "decision": "admitted",
        "decision_basis": "pressure fixture",
    }


def _rehash(record: dict[str, Any]) -> None:
    boundary = {
        "record_id": record["record_id"],
        "commit_index": record["commit_index"],
        "envelope": record["envelope"],
    }
    record["integrity"]["digest"] = record_digest(boundary)


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
