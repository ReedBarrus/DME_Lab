"""Bounded v0 ingest admission pressure run."""

from __future__ import annotations

import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ingest import (
    COMPARATOR_V0,
    COMPARATOR_V0_EVENT_TIME_REQUIRED,
    append_admission,
    append_observation,
    derive_admitted_projection,
    reconstruct_admission_lineage,
)
from src.ledger import JsonlLedger
from src.runtime.repo_provenance_pressure import make_snapshot_ingest_envelope
from src.runtime.repo_transition_pressure import load_json, make_git_ingest_envelope


def run() -> dict[str, Any]:
    started = perf_counter()
    snapshot = load_json(Path("traces") / "repo_snapshot_v0_post_cleanup.json")
    git_state = load_json(Path("traces") / "git_state_v0_post_cleanup.json")
    filesystem_candidate = make_snapshot_ingest_envelope(snapshot)
    git_candidate = make_git_ingest_envelope(git_state)
    malformed_candidate = {"envelope_identity": "malformed-required-field", "source": "pressure_fixture"}
    non_json_candidate = make_snapshot_ingest_envelope(snapshot)
    non_json_candidate["signal"]["payload"] = {"non_json_number": math.nan}

    with TemporaryDirectory() as tmpdir:
        ledger = JsonlLedger(Path(tmpdir) / "ingest_admission_pressure_v0.jsonl")
        filesystem_observation = append_observation(
            ledger,
            filesystem_candidate,
            source="repository_filesystem_snapshot",
            provenance={"basis": "post_cleanup_trace"},
        )
        filesystem_admission = append_admission(ledger, filesystem_observation)
        filesystem_second_admission = append_admission(
            ledger,
            filesystem_observation,
            comparator_version=COMPARATOR_V0_EVENT_TIME_REQUIRED,
        )
        git_observation = append_observation(
            ledger,
            git_candidate,
            source="repository_git_state",
            provenance={"basis": "post_cleanup_trace"},
        )
        git_admission = append_admission(ledger, git_observation)
        malformed_observation = append_observation(
            ledger,
            malformed_candidate,
            source="malformed_pressure_fixture",
            provenance={"basis": "deterministic_fixture"},
        )
        malformed_admission = append_admission(ledger, malformed_observation)
        non_json_observation = append_observation(
            ledger,
            non_json_candidate,
            source="non_json_pressure_fixture",
            provenance={"basis": "deterministic_fixture", "non_json_value": "math.nan"},
        )
        non_json_admission = append_admission(ledger, non_json_observation)
        unresolved_admission = append_admission(ledger, git_observation, comparator_version="unknown_v0")
        replayed = ledger.replay()
        verification = ledger.verify()

    projection = derive_admitted_projection(replayed)
    lineage = reconstruct_admission_lineage(replayed)
    admission_records = [
        filesystem_admission,
        filesystem_second_admission,
        git_admission,
        malformed_admission,
        non_json_admission,
        unresolved_admission,
    ]
    report = {
        "experiment": "ingest_admission_pressure_v0",
        "runtime_scope": "bounded v0 temporary ledger",
        "logical_layers": {
            "L0": "observation / provenance record",
            "L1": "comparison / admission record referring to L0",
            "L2": "admitted projection derived from replay",
        },
        "admission_record_shape": [
            "record_type",
            "subject_record_id",
            "comparator_identity",
            "comparator_version",
            "comparison_result",
            "decision",
            "decision_basis",
        ],
        "record_counts": {
            "replayed": len(replayed),
            "observations": sum(1 for record in replayed if record["envelope"].get("record_type") == "observation"),
            "admissions": sum(1 for record in replayed if record["envelope"].get("record_type") == "admission"),
            "admitted_projection": len(projection),
        },
        "cases": {
            "filesystem_candidate": _case(filesystem_observation, [filesystem_admission, filesystem_second_admission], projection),
            "git_candidate": _case(git_observation, [git_admission, unresolved_admission], projection),
            "malformed_required_field": _case(malformed_observation, [malformed_admission], projection),
            "non_json_admissible_value": {
                **_case(non_json_observation, [non_json_admission], projection),
                "raw_value_preserved_in_temporary_ledger": "math.nan",
                "json_trace_note": "raw non-JSON value summarized here rather than serialized into trace",
            },
        },
        "lineage_summary": [
            {
                "subject_record_id": item["subject_record_id"],
                "observation_source": item["observation_source"],
                "admission_decisions": [
                    {
                        "admission_record_id": admission["admission_record_id"],
                        "comparator_version": admission["comparator_version"],
                        "comparison_status": admission["comparison_result"]["status"],
                        "comparison_valid": admission["comparison_result"]["valid"],
                        "decision": admission["decision"],
                        "decision_basis": admission["decision_basis"],
                    }
                    for admission in item["admission_records"]
                ],
                "participates_in_admitted_projection": item["participates_in_admitted_projection"],
            }
            for item in lineage
        ],
        "admitted_projection": projection,
        "integrity_ok": verification.ok,
        "integrity_errors": [failure for failure in verification.failures],
        "unresolved_pressure": [
            "projection uses any admitted decision without conflict resolution",
            "strict comparator version exists only as pressure fixture",
            "non-JSON value preservation relies on current Python JSON behavior in a temporary ledger",
            "no generalized admission policy engine exists",
            "no topology or reconstruction engine consumes admission records yet",
        ],
    }
    report["duration_seconds"] = perf_counter() - started
    return report


def _case(observation_record: dict[str, Any], admission_records: list[dict[str, Any]], projection: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "observation_record_id": observation_record["record_id"],
        "observation_persisted": True,
        "admission_record_ids": [record["record_id"] for record in admission_records],
        "decisions": [record["envelope"]["decision"] for record in admission_records],
        "comparison_valid": [record["envelope"]["comparison_result"]["valid"] for record in admission_records],
        "participates_in_admitted_projection": any(
            item["subject_record_id"] == observation_record["record_id"] for item in projection
        ),
    }


def main() -> None:
    report = run()
    output_path = Path("traces") / "ingest_admission_pressure_v0.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
