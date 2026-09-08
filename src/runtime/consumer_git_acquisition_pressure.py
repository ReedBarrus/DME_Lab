"""Reproduce one consumer-visible collision without changing production surfaces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from src.ledger import CANONICAL_LIVE_INGEST_LEDGER_PATH, JsonlLedger
from src.reconstruction import reconstruct_admission_relationships
from src.runtime.degraded_git_admission_pressure import _initialize_git, _write_alpha
from src.runtime.foreground_repository_observation import (
    ForegroundRepositoryObservationCoordinator,
)


TRACE_PATH = Path("traces") / "consumer_git_acquisition_pressure_v0.json"
STARTING_HEAD = "b9ef1361e87690af03cc8e536c406d8152fd0164"


def serialized(value: object) -> bytes:
    """Serialize every supplied field deterministically without normalization."""
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(serialized(value)).hexdigest()


def run() -> dict[str, Any]:
    """Capture healthy and degraded histories, then compare full recovered views."""
    canonical_before = _file_sha256(CANONICAL_LIVE_INGEST_LEDGER_PATH)
    with TemporaryDirectory(prefix="dme-consumer-git-") as temporary:
        base = Path(temporary)
        cases = {
            "C0": _capture_case(base / "C0", initialize_git=True),
            "S1": _capture_case(base / "S1", initialize_git=False),
        }

    c0 = cases["C0"]
    s1 = cases["S1"]
    surface_equal = c0["current_result"] == s1["current_result"]
    serialized_equal = serialized(c0["current_result"]) == serialized(
        s1["current_result"]
    )
    outcomes_differ = (
        c0["historical_git"]["capture_errors"] == []
        and c0["historical_git"]["head_sha"] is not None
        and s1["historical_git"]["head_sha"] is None
        and s1["historical_git"]["branch"] is None
        and s1["historical_git"]["status_porcelain"] is None
        and len(s1["historical_git"]["capture_errors"]) == 3
    )
    recovered = all(
        case["recovery"]["payload_matches_raw"]
        and case["recovery"]["read_was_append_free"]
        for case in cases.values()
    )

    return {
        "experiment": "consumer_git_acquisition_pressure_v0",
        "starting_head": STARTING_HEAD,
        "surface": (
            "complete unmodified ForegroundRepositoryObservationCoordinator."
            "current_result() return value"
        ),
        "comparison": {
            "normalization_applied": False,
            "complete_object_equality": surface_equal,
            "complete_serialized_equality": serialized_equal,
            "surface_sha256": [
                digest(c0["current_result"]),
                digest(s1["current_result"]),
            ],
            "historical_git_acquisition_outcomes_differ": outcomes_differ,
            "specimen_ledgers_differ": (
                c0["ledger_sha256"] != s1["ledger_sha256"]
            ),
            "underlying_difference_recoverable": recovered,
        },
        "cases": cases,
        "canonical_history": {
            "working_file_sha256_before": canonical_before,
            "working_file_sha256_after": _file_sha256(
                CANONICAL_LIVE_INGEST_LEDGER_PATH
            ),
        },
    }


def _capture_case(directory: Path, *, initialize_git: bool) -> dict[str, Any]:
    root = directory / "fixture"
    root.mkdir(parents=True)
    _write_alpha(root)
    if initialize_git:
        _initialize_git(root)

    ledger_path = directory / "history.jsonl"
    writer = ForegroundRepositoryObservationCoordinator(root, ledger_path)
    immediate = writer.capture_round()
    writer.close()

    ledger_before_read = ledger_path.read_bytes()
    reader = ForegroundRepositoryObservationCoordinator.open(root, ledger_path)
    current = reader.current_result()
    reader.close()
    ledger_after_read = ledger_path.read_bytes()

    reconstruction = reconstruct_admission_relationships(
        JsonlLedger(ledger_path).replay()
    )
    recovered_git = next(
        item
        for item in reconstruction["observations"]
        if item["source"] == "repository_git_state"
    )
    raw_git = immediate["captured_observations"]["git"]
    recovered_payload = recovered_git["observation"]["signal"]["payload"]

    return {
        "fixture": "clean Git repository" if initialize_git else "non-Git directory",
        "current_result": current,
        "current_result_sha256": digest(current),
        "historical_git": {
            "head_sha": raw_git["head_sha"],
            "branch": raw_git["branch"],
            "status_porcelain": raw_git["status_porcelain"],
            "capture_errors": raw_git["capture_errors"],
        },
        "ledger_jsonl": ledger_before_read.decode("utf-8"),
        "ledger_sha256": hashlib.sha256(ledger_before_read).hexdigest(),
        "recovery": {
            "observation_record_id": recovered_git["observation_record_id"],
            "source": recovered_git["source"],
            "decision": recovered_git["admissions"][0]["decision"],
            "payload_matches_raw": recovered_payload == raw_git,
            "capture_errors": recovered_payload["capture_errors"],
            "read_was_append_free": ledger_before_read == ledger_after_read,
        },
    }


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = run()
    TRACE_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["comparison"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
