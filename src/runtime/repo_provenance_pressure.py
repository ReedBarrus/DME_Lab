"""Run the first bounded live repository provenance pressure experiment."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

from src.capture import make_repo_snapshot, observe_git_state
from src.ledger import JsonlLedger, validate_ledger_record


def json_domain_result(value: Any) -> dict[str, Any]:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError) as exc:
        return {"valid": False, "error": type(exc).__name__, "message": str(exc)}
    return {"valid": True, "error": None, "message": None}


def make_snapshot_ingest_envelope(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "envelope_identity": f"repo-snapshot-envelope:{snapshot['snapshot_id']}",
        "source": "repository_filesystem_snapshot",
        "source_sequence": None,
        "event_time": None,
        "arrival_time": snapshot["observation_finished_at"],
        "capture_version": snapshot["observer_version"],
        "provenance": {
            "observer": snapshot["observer"],
            "observer_version": snapshot["observer_version"],
            "root_identity": snapshot["root_identity"],
            "scope": snapshot["scope"],
            "observation_started_at": snapshot["observation_started_at"],
            "observation_finished_at": snapshot["observation_finished_at"],
            "capture_errors": snapshot["capture_errors"],
        },
        "signal": {
            "identity": snapshot["snapshot_id"],
            "time": None,
            "type": "repository_snapshot.v0",
            "payload": snapshot,
        },
        "missingness": {
            "signal.time": "unavailable",
            "source_sequence": "unavailable",
        },
    }


def run(root: Path | str = ".") -> dict[str, Any]:
    started = perf_counter()
    root_path = Path(root)
    snapshot = make_repo_snapshot(root_path)
    git_state = observe_git_state(root_path)
    envelope = make_snapshot_ingest_envelope(snapshot)
    candidate_json = json_domain_result(envelope)

    ledger_result: dict[str, Any] = {"attempted": False}
    if candidate_json["valid"]:
        with TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "repo_provenance_pressure_v0.jsonl"
            ledger = JsonlLedger(ledger_path)
            record = ledger.append(envelope)
            validation = validate_ledger_record(record)
            replayed = ledger.replay()
            verification = ledger.verify()
            ledger_result = {
                "attempted": True,
                "experimental_ledger": "temporary",
                "schema_shadow_validation": validation.to_dict(),
                "record_id": record["record_id"],
                "commit_index": record["commit_index"],
                "replayed_records": len(replayed),
                "integrity_ok": verification.ok,
                "integrity_errors": [failure for failure in verification.failures],
                "bytes_written": ledger_path.stat().st_size,
            }

    report = {
        "experiment": "repo_provenance_pressure_v0",
        "runtime_scope": "bounded DME_Lab repository specimen",
        "filesystem_baseline": {
            "snapshot_id": snapshot["snapshot_id"],
            "observer": snapshot["observer"],
            "observer_version": snapshot["observer_version"],
            "observation_started_at": snapshot["observation_started_at"],
            "observation_finished_at": snapshot["observation_finished_at"],
            "entry_count": len(snapshot["entries"]),
            "capture_error_count": len(snapshot["capture_errors"]),
            "total_size_bytes": sum(entry["size_bytes"] for entry in snapshot["entries"]),
            "duration_seconds": snapshot["duration_seconds"],
            "scope": snapshot["scope"],
        },
        "git_baseline": {
            "observation_id": git_state["observation_id"],
            "observer": git_state["observer"],
            "observer_version": git_state["observer_version"],
            "observed_at": git_state["observed_at"],
            "head_sha": git_state["head_sha"],
            "branch": git_state["branch"],
            "status_count": len(git_state["status_porcelain"] or []),
            "capture_error_count": len(git_state["capture_errors"]),
        },
        "candidate_ingest_envelope": {
            "envelope_identity": envelope["envelope_identity"],
            "source": envelope["source"],
            "provenance_fields": sorted(envelope["provenance"].keys()),
            "payload_snapshot_id": envelope["signal"]["identity"],
            "json_domain": candidate_json,
        },
        "ledger_handshake": ledger_result,
        "observed_mismatches": [],
        "unresolved_pressure": [
            "snapshot captures endpoint structure, not complete transformation history",
            "filesystem and Git observations are separate regimes",
            "observation interval is not event time",
            "mtime is preserved as file metadata but not interpreted as event time",
            "live envelope size may pressure complete-envelope storage as repository grows",
        ],
    }
    report["duration_seconds"] = perf_counter() - started
    return {"snapshot": snapshot, "git_state": git_state, "report": report}


def main() -> None:
    result = run(".")
    traces = Path("traces")
    traces.mkdir(parents=True, exist_ok=True)
    (traces / "repo_snapshot_v0_baseline.json").write_text(
        json.dumps(result["snapshot"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (traces / "git_state_v0_baseline.json").write_text(
        json.dumps(result["git_state"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (traces / "repo_provenance_pressure_v0.json").write_text(
        json.dumps(result["report"], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result["report"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

