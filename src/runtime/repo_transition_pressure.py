"""Second live repository transition pressure experiment."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from time import perf_counter, sleep
from typing import Any

from src.capture import compare_snapshots, make_repo_snapshot
from src.ledger import JsonlLedger, validate_ledger_record
from src.runtime.repo_provenance_pressure import json_domain_result, make_snapshot_ingest_envelope


def load_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def make_git_ingest_envelope(git_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "envelope_identity": f"git-state-envelope:{git_state['observation_id']}",
        "source": "repository_git_state",
        "source_sequence": None,
        "event_time": None,
        "arrival_time": git_state["observed_at"],
        "capture_version": git_state["observer_version"],
        "provenance": {
            "observer": git_state["observer"],
            "observer_version": git_state["observer_version"],
            "root_identity": git_state["root_identity"],
            "observed_at": git_state["observed_at"],
            "capture_errors": git_state["capture_errors"],
        },
        "signal": {
            "identity": git_state["observation_id"],
            "time": None,
            "type": "repository_git_state.v0",
            "payload": git_state,
        },
        "missingness": {
            "signal.time": "unavailable",
            "source_sequence": "unavailable",
        },
    }


def filesystem_transition(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    comparison = compare_snapshots(before, after)
    before_total = sum(entry["size_bytes"] for entry in before.get("entries", []))
    after_total = sum(entry["size_bytes"] for entry in after.get("entries", []))
    comparison["entry_count_delta"] = len(after.get("entries", [])) - len(before.get("entries", []))
    comparison["total_byte_delta"] = after_total - before_total
    comparison["capture_error_delta"] = len(after.get("capture_errors", [])) - len(before.get("capture_errors", []))
    comparison["observation_intervals"] = {
        "before": [before.get("observation_started_at"), before.get("observation_finished_at")],
        "after": [after.get("observation_started_at"), after.get("observation_finished_at")],
    }
    return comparison


def git_observation_transition(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_status = set(before.get("status_porcelain") or [])
    after_status = set(after.get("status_porcelain") or [])
    return {
        "before_head": before.get("head_sha"),
        "after_head": after.get("head_sha"),
        "head_changed": before.get("head_sha") != after.get("head_sha"),
        "before_branch": before.get("branch"),
        "after_branch": after.get("branch"),
        "branch_changed": before.get("branch") != after.get("branch"),
        "before_observed_at": before.get("observed_at"),
        "after_observed_at": after.get("observed_at"),
        "before_status_count": len(before_status),
        "after_status_count": len(after_status),
        "status_added": sorted(after_status - before_status),
        "status_removed": sorted(before_status - after_status),
        "status_current": sorted(after_status),
        "before_capture_errors": before.get("capture_errors", []),
        "after_capture_errors": after.get("capture_errors", []),
    }


def git_history_between(root: Path | str, before_head: str, after_head: str) -> list[dict[str, Any]]:
    log = _git(
        root,
        [
            "log",
            "--reverse",
            "--format=%H%x1f%P%x1f%cI%x1f%s",
            f"{before_head}..{after_head}",
        ],
    )
    commits: list[dict[str, Any]] = []
    for line in log.splitlines():
        sha, parents, committed_at, message = line.split("\x1f", 3)
        name_status = _git(root, ["diff-tree", "--no-commit-id", "--name-status", "-r", sha])
        changed_paths = []
        for status_line in name_status.splitlines():
            if not status_line.strip():
                continue
            status, path = status_line.split("\t", 1)
            changed_paths.append({"status": status, "path": path})
        commits.append(
            {
                "sha": sha,
                "parent_shas": parents.split() if parents else [],
                "commit_timestamp": committed_at,
                "message": message,
                "changed_paths": changed_paths,
                "evidence_basis": "retrospective_git_history",
            }
        )
    return commits


def path_correspondence(
    fs_delta: dict[str, Any],
    git_delta: dict[str, Any],
    git_history: list[dict[str, Any]],
    before_snapshot: dict[str, Any],
    after_snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    before_entries = {entry["path"]: entry for entry in before_snapshot.get("entries", [])}
    after_entries = {entry["path"]: entry for entry in after_snapshot.get("entries", [])}
    fs_paths = set(before_entries) | set(after_entries)
    git_status_paths = {status_path(entry) for entry in (git_delta["status_removed"] + git_delta["status_added"] + git_delta["status_current"])}
    git_commit_paths = {
        item["path"]
        for commit in git_history
        for item in commit["changed_paths"]
    }
    all_paths = sorted(fs_paths | git_status_paths | git_commit_paths)
    changed = {item["path"] for item in fs_delta["changed_paths"]}
    added = {item["path"] for item in fs_delta["added_paths"]}
    removed = {item["path"] for item in fs_delta["removed_paths"]}

    rows = []
    for path in all_paths:
        rows.append(
            {
                "path": path,
                "filesystem": {
                    "in_scope": path in fs_paths,
                    "added": path in added,
                    "removed": path in removed,
                    "content_changed": path in changed,
                    "old_sha256": before_entries.get(path, {}).get("sha256"),
                    "new_sha256": after_entries.get(path, {}).get("sha256"),
                },
                "git_working_state": {
                    "baseline_status": statuses_for_path(git_delta["status_removed"], path),
                    "current_status": statuses_for_path(git_delta["status_current"], path),
                },
                "git_historical": {
                    "commit_touches": [
                        commit["sha"]
                        for commit in git_history
                        if any(item["path"] == path for item in commit["changed_paths"])
                    ],
                    "commit_statuses": [
                        item["status"]
                        for commit in git_history
                        for item in commit["changed_paths"]
                        if item["path"] == path
                    ],
                },
            }
        )
    return rows


def status_path(status_entry: str) -> str:
    if len(status_entry) > 3 and status_entry[2] == " ":
        return status_entry[3:]
    if len(status_entry) > 2 and status_entry[1] == " ":
        return status_entry[2:]
    return status_entry


def statuses_for_path(status_entries: list[str], path: str) -> list[str]:
    return [entry[:2].strip() or entry[:2] for entry in status_entries if status_path(entry) == path]


def same_bytes_later_committed(correspondence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": row["path"],
            "sha256": row["filesystem"]["old_sha256"],
            "commit_touches": row["git_historical"]["commit_touches"],
            "baseline_status": row["git_working_state"]["baseline_status"],
        }
        for row in correspondence
        if row["filesystem"]["in_scope"]
        and row["filesystem"]["old_sha256"] is not None
        and row["filesystem"]["old_sha256"] == row["filesystem"]["new_sha256"]
        and row["git_historical"]["commit_touches"]
    ]


def git_visible_filesystem_out_of_scope(correspondence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": row["path"],
            "baseline_status": row["git_working_state"]["baseline_status"],
            "current_status": row["git_working_state"]["current_status"],
            "commit_touches": row["git_historical"]["commit_touches"],
        }
        for row in correspondence
        if not row["filesystem"]["in_scope"]
        and (
            row["git_working_state"]["baseline_status"]
            or row["git_working_state"]["current_status"]
            or row["git_historical"]["commit_touches"]
        )
    ]


def multi_source_ledger_handshake(fs_snapshot: dict[str, Any], git_state: dict[str, Any]) -> dict[str, Any]:
    envelopes = [
        ("filesystem", make_snapshot_ingest_envelope(fs_snapshot)),
        ("git", make_git_ingest_envelope(git_state)),
    ]
    json_results = {source: json_domain_result(envelope) for source, envelope in envelopes}
    with TemporaryDirectory() as tmpdir:
        ledger_path = Path(tmpdir) / "repo_transition_pressure_v0.jsonl"
        ledger = JsonlLedger(ledger_path)
        records = []
        for source, envelope in envelopes:
            record = ledger.append(envelope)
            validation = validate_ledger_record(record)
            records.append(
                {
                    "source": source,
                    "record_id": record["record_id"],
                    "commit_index": record["commit_index"],
                    "schema_shadow_validation": validation.to_dict(),
                    "record_size_bytes": len(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")),
                    "payload_observer": record["envelope"]["signal"]["payload"]["observer"],
                }
            )
        replayed = ledger.replay()
        verification = ledger.verify()
        bytes_written = ledger_path.stat().st_size

    return {
        "append_order": ["filesystem", "git"],
        "append_order_claim": "experimental handling order, not source chronology",
        "json_domain": json_results,
        "records": records,
        "replayed_sources": [record["envelope"]["source"] for record in replayed],
        "replayed_payload_observers": [record["envelope"]["signal"]["payload"]["observer"] for record in replayed],
        "integrity_ok": verification.ok,
        "integrity_errors": [failure for failure in verification.failures],
        "bytes_written": bytes_written,
    }


def repeated_identity_pressure() -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "stable.txt").write_text("stable", encoding="utf-8")
        first = make_repo_snapshot(root)
        sleep(0.01)
        second = make_repo_snapshot(root)
        first_envelope = make_snapshot_ingest_envelope(first)
        second_envelope = make_snapshot_ingest_envelope(second)
    return {
        "same_snapshot_id": first["snapshot_id"] == second["snapshot_id"],
        "same_envelope_identity": first_envelope["envelope_identity"] == second_envelope["envelope_identity"],
        "different_observation_interval": (
            first["observation_started_at"],
            first["observation_finished_at"],
        )
        != (
            second["observation_started_at"],
            second["observation_finished_at"],
        ),
        "first_interval": [first["observation_started_at"], first["observation_finished_at"]],
        "second_interval": [second["observation_started_at"], second["observation_finished_at"]],
    }


def metadata_only_pressure() -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        target = root / "same-bytes.txt"
        target.write_text("same-bytes", encoding="utf-8")
        first = make_repo_snapshot(root)
        stat = target.stat()
        os.utime(target, ns=(stat.st_atime_ns + 1_000_000_000, stat.st_mtime_ns + 1_000_000_000))
        second = make_repo_snapshot(root)
        comparison = compare_snapshots(first, second)
    return {
        "snapshot_id_changed": first["snapshot_id"] != second["snapshot_id"],
        "changed_paths_count": len(comparison["changed_paths"]),
        "unchanged_paths": comparison["unchanged_paths"],
        "finding": "metadata changed snapshot identity while content-change classification remained unchanged"
        if first["snapshot_id"] != second["snapshot_id"] and not comparison["changed_paths"]
        else "no divergence observed",
    }


def timing_surface(
    fs_snapshot: dict[str, Any],
    git_state: dict[str, Any],
    git_history: list[dict[str, Any]],
    ledger_handshake: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {"claim": "filesystem observation_started_at", "basis": "observer-produced", "value": fs_snapshot["observation_started_at"]},
        {"claim": "filesystem observation_finished_at", "basis": "observer-produced", "value": fs_snapshot["observation_finished_at"]},
        {"claim": "file mtime_ns", "basis": "source-provided metadata", "value": "per file entry"},
        {"claim": "Git observed_at", "basis": "observer-produced", "value": git_state["observed_at"]},
        {"claim": "Git commit timestamps", "basis": "retrospectively reconstructed", "value": [commit["commit_timestamp"] for commit in git_history]},
        {"claim": "candidate arrival_time mapping", "basis": "handling-produced provisional mapping", "value": "capture completion or Git observed_at"},
        {"claim": "ledger append commit_index", "basis": "ledger-produced", "value": [record["commit_index"] for record in ledger_handshake["records"]]},
    ]


def run(
    root: Path | str = ".",
    *,
    baseline_snapshot_path: Path | str = Path("traces") / "repo_snapshot_v0_baseline.json",
    baseline_git_path: Path | str = Path("traces") / "git_state_v0_baseline.json",
    current_snapshot_path: Path | str = Path("traces") / "repo_snapshot_v0_post_cleanup.json",
    current_git_path: Path | str = Path("traces") / "git_state_v0_post_cleanup.json",
) -> dict[str, Any]:
    started = perf_counter()
    s0 = load_json(baseline_snapshot_path)
    g0 = load_json(baseline_git_path)
    s1 = load_json(current_snapshot_path)
    g1 = load_json(current_git_path)
    fs_delta = filesystem_transition(s0, s1)
    git_delta = git_observation_transition(g0, g1)
    history = git_history_between(root, g0["head_sha"], g1["head_sha"])
    correspondence = path_correspondence(fs_delta, git_delta, history, s0, s1)
    ledger_handshake = multi_source_ledger_handshake(s1, g1)
    repeat_identity = repeated_identity_pressure()
    metadata_pressure = metadata_only_pressure()
    report = {
        "experiment": "repo_transition_pressure_v0",
        "baseline": {
            "snapshot_id": s0["snapshot_id"],
            "git_observation_id": g0["observation_id"],
            "git_head": g0["head_sha"],
        },
        "current": {
            "snapshot_id": s1["snapshot_id"],
            "git_observation_id": g1["observation_id"],
            "git_head": g1["head_sha"],
        },
        "root_identity_pressure": {
            "baseline_filesystem_root_identity": s0.get("root_identity"),
            "current_filesystem_root_identity": s1.get("root_identity"),
            "baseline_git_root_identity": g0.get("root_identity"),
            "current_git_root_identity": g1.get("root_identity"),
            "finding": "observer invocation with '.' leaves root_identity.name empty in v0 observations",
        },
        "filesystem_delta": fs_delta,
        "git_observation_delta": git_delta,
        "git_retrospective_history": history,
        "path_correspondence": correspondence,
        "path_correspondence_summary": {
            "rows": len(correspondence),
            "filesystem_added": len(fs_delta["added_paths"]),
            "filesystem_removed": len(fs_delta["removed_paths"]),
            "filesystem_content_changed": len(fs_delta["changed_paths"]),
            "git_status_removed": len(git_delta["status_removed"]),
            "git_status_added": len(git_delta["status_added"]),
            "git_commit_touched_paths": len({item["path"] for commit in history for item in commit["changed_paths"]}),
            "git_visible_filesystem_out_of_scope": len(git_visible_filesystem_out_of_scope(correspondence)),
            "same_filesystem_bytes_later_committed": len(same_bytes_later_committed(correspondence)),
        },
        "git_visible_filesystem_out_of_scope": git_visible_filesystem_out_of_scope(correspondence),
        "same_filesystem_bytes_later_committed": same_bytes_later_committed(correspondence),
        "candidate_envelopes": {
            "filesystem": {
                "json_domain": json_domain_result(make_snapshot_ingest_envelope(s1)),
                "envelope_identity": make_snapshot_ingest_envelope(s1)["envelope_identity"],
            },
            "git": {
                "json_domain": json_domain_result(make_git_ingest_envelope(g1)),
                "envelope_identity": make_git_ingest_envelope(g1)["envelope_identity"],
            },
        },
        "multi_source_ledger_handshake": ledger_handshake,
        "repeated_observation_identity_pressure": repeat_identity,
        "metadata_only_snapshot_pressure": metadata_pressure,
        "timing_surface": timing_surface(s1, g1, history, ledger_handshake),
        "derived_artifacts_not_ingested": [
            "filesystem_delta",
            "git_observation_delta",
            "git_retrospective_history",
            "path_correspondence",
        ],
        "unresolved_pressure": [
            "filesystem scope and Git scope are overlapping but non-coextensive",
            "snapshot identity includes metadata while compare_snapshots changed_paths uses content hash only",
            "candidate filesystem envelope identity collapses same structural state observations",
            "capture completion is only provisionally mapped to arrival_time",
            "retrospective Git history is not contemporaneous filesystem history",
            "root identity remains ambiguous when observer is invoked with '.'",
        ],
    }
    report["duration_seconds"] = perf_counter() - started
    return report


def _git(root: Path | str, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def main() -> None:
    report = run(".")
    output_path = Path("traces") / "repo_transition_pressure_v0.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
