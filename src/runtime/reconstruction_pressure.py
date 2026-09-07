"""Bounded admission reconstruction pressure run."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.ingest import (
    COMPARATOR_V0,
    COMPARATOR_V0_EVENT_TIME_REQUIRED,
    append_admission,
    append_observation,
)
from src.ledger import JsonlLedger
from src.reconstruction import derive_admitted_projection, reconstruct_admission_relationships
from src.runtime.repo_provenance_pressure import make_snapshot_ingest_envelope
from src.runtime.repo_transition_pressure import load_json, make_git_ingest_envelope


def run() -> dict[str, Any]:
    started = perf_counter()
    replayed, integrity_ok, integrity_errors = _build_pressure_history()

    reconstruction_a = reconstruct_admission_relationships(replayed)
    projection_a = derive_admitted_projection(reconstruction_a)
    reconstruction_b = reconstruct_admission_relationships(replayed)
    projection_b = derive_admitted_projection(reconstruction_b)

    return {
        "experiment": "reconstruction_pressure_v0",
        "runtime_scope": "bounded admission relationships from temporary ledger replay",
        "authoritative_history": {
            "record_ids": [record["record_id"] for record in replayed],
            "record_count": len(replayed),
            "integrity_ok": integrity_ok,
            "integrity_errors": integrity_errors,
        },
        "reconstruction": {
            "type": reconstruction_a["reconstruction_type"],
            "observation_count": len(reconstruction_a["observations"]),
            "orphan_admission_count": len(reconstruction_a["orphan_admissions"]),
            "authoritative_record_ids": reconstruction_a["authoritative_record_ids"],
            "rebuild_structural_equal": reconstruction_a == reconstruction_b,
        },
        "projection": {
            "type": "admitted_projection_v0",
            "subject_record_ids": [item["subject_record_id"] for item in projection_a],
            "rebuild_structural_equal": projection_a == projection_b,
        },
        "navigation_paths": [
            {
                "projection_subject_record_id": item["subject_record_id"],
                "reconstruction_type": item["reconstruction_type"],
                "admission_record_ids": item["admission_record_ids"],
                "observation_record_id": item["observation_record_id"],
                "source": item["source"],
            }
            for item in projection_a
        ],
        "lineage_summary": [
            {
                "observation_record_id": observation["observation_record_id"],
                "source": observation["source"],
                "provenance": observation["provenance"],
                "admission_record_ids": observation["admission_record_ids"],
                "decisions": [admission["decision"] for admission in observation["admissions"]],
                "comparator_versions": [admission["comparator_version"] for admission in observation["admissions"]],
                "participates_in_admitted_projection": observation["participates_in_admitted_projection"],
            }
            for observation in reconstruction_a["observations"]
        ],
        "unresolved_pressure": [
            "projection still uses any admitted decision without conflict resolution",
            "no index or acceleration surface exists",
            "no generalized topology exists",
            "reconstruction only covers admission relationships",
        ],
        "duration_seconds": perf_counter() - started,
    }


def _build_pressure_history() -> tuple[list[dict[str, Any]], bool, list[dict[str, Any]]]:
    snapshot = load_json(Path("traces") / "repo_snapshot_v0_post_cleanup.json")
    git_state = load_json(Path("traces") / "git_state_v0_post_cleanup.json")
    with TemporaryDirectory() as tmpdir:
        ledger = JsonlLedger(Path(tmpdir) / "reconstruction_pressure_v0.jsonl")
        filesystem = append_observation(
            ledger,
            make_snapshot_ingest_envelope(snapshot),
            source="repository_filesystem_snapshot",
            provenance={"basis": "post_cleanup_trace"},
        )
        append_admission(ledger, filesystem, comparator_version=COMPARATOR_V0)
        append_admission(ledger, filesystem, comparator_version=COMPARATOR_V0_EVENT_TIME_REQUIRED)
        git = append_observation(
            ledger,
            make_git_ingest_envelope(git_state),
            source="repository_git_state",
            provenance={"basis": "post_cleanup_trace"},
        )
        append_admission(ledger, git, comparator_version=COMPARATOR_V0)
        malformed = append_observation(
            ledger,
            {"envelope_identity": "malformed-required-field", "source": "pressure_fixture"},
            source="malformed_pressure_fixture",
            provenance={"basis": "deterministic_fixture"},
        )
        append_admission(ledger, malformed, comparator_version=COMPARATOR_V0)
        append_admission(ledger, git, comparator_version="unknown_v0")
        replayed = ledger.replay()
        verification = ledger.verify()
    return replayed, verification.ok, [failure for failure in verification.failures]


def main() -> None:
    report = run()
    output_path = Path("traces") / "reconstruction_pressure_v0.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
