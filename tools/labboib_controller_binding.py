#!/usr/bin/env python3
"""LABBOIB_CONTROLLER_BINDING_001.

Binds the merged LABBOIB temporal-seat basis into the bounded SQLite
controller and exposes the first real local hands:

- READ_REPO_STATE
- RUN_DECLARED_TEST

The binding does not make the controller row identical to the Git seat.
It does not mutate LABBOIB's Git cursor or canonical working-state artifact.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from tools.goblin_pool import GoblinPool, GoblinPoolError


BINDING_ID = "LABBOIB_CONTROLLER_BINDING_001"
SEAT_ID = "LABBOIB"

MANIFEST_PATH = "continuity/seats/labboib.json"
CURSOR_PATH = "continuity/cursors/labboib.json"
WORKING_STATE_PATH = "continuity/current_state/labboib_working_state_v0.json"
EVENTS_PATH = "continuity/events.jsonl"
AUTHORITY_PATH = (
    "lab/ops/candidates/LABBOIB_CONTROLLER_BINDING_001/authority_v0.json"
)

CANONICAL_MAIN_AT_BINDING = "e6b56d12352f9594b25d1db3036afc3d1d0d7ef6"
EXPECTED_ARTIFACT_BLOBS = {
    EVENTS_PATH: "e7b49a380ae85caf7922ccfa9172464f1ecda49f",
    MANIFEST_PATH: "0e147e9d08e5cf611995d3206c2644cf32fe6e08",
    CURSOR_PATH: "256974c906f5d3876f2bf09e0df800470adaa99d",
    WORKING_STATE_PATH: "2fc78b6bb5063dabba98a6f05c3bb65082dc42d7",
}
AUTHORITY_BLOB = "e23595fe63116001720760e6c25eeb9dbdc877e3"
AUTHORITY_REF = f"{AUTHORITY_PATH}@gitblob:{AUTHORITY_BLOB}"

EXPECTED_CURSOR = "CE-000033"
DECLARED_TEST_ID = "LABBOIB_TEMPORAL_SEAT_FOCUSED"


class LabboibBindingError(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def _resolve_commit(repo: Path, source_ref: str) -> str:
    result = _git(repo, "rev-parse", "--verify", f"{source_ref}^{{commit}}")
    if result.returncode != 0:
        raise LabboibBindingError(
            f"cannot resolve source ref {source_ref!r}: {result.stderr.strip()}"
        )
    commit = result.stdout.strip().lower()
    if len(commit) != 40:
        raise LabboibBindingError("source ref did not resolve to exact commit")
    return commit


def _blob_sha(repo: Path, commit: str, path: str) -> str:
    result = _git(repo, "rev-parse", f"{commit}:{path}")
    if result.returncode != 0:
        raise LabboibBindingError(
            f"cannot resolve Git blob for {path}: {result.stderr.strip()}"
        )
    return result.stdout.strip().lower()


def _read_bytes(repo: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise LabboibBindingError(
            f"cannot read committed artifact {path}: "
            + result.stderr.decode("utf-8", errors="replace").strip()
        )
    return result.stdout


def _read_json(repo: Path, commit: str, path: str) -> dict[str, Any]:
    try:
        value = json.loads(_read_bytes(repo, commit, path).decode("utf-8"))
    except Exception as exc:
        raise LabboibBindingError(f"malformed JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LabboibBindingError(f"expected JSON object at {path}")
    return value


def _read_jsonl(repo: Path, commit: str, path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    text = _read_bytes(repo, commit, path).decode("utf-8")
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LabboibBindingError(
                f"malformed JSONL at {path}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise LabboibBindingError(
                f"non-object JSONL record at {path}:{line_number}"
            )
        rows.append(value)
    return rows


def _workspace_head(repo: Path) -> str:
    result = _git(repo, "rev-parse", "HEAD")
    if result.returncode != 0:
        raise LabboibBindingError(
            "workspace HEAD unavailable: " + result.stderr.strip()
        )
    return result.stdout.strip()


def reconstruct_seat_basis(
    repo_root: str | Path,
    source_ref: str = "HEAD",
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    commit = _resolve_commit(repo, source_ref)

    observed_blobs = {
        path: _blob_sha(repo, commit, path)
        for path in EXPECTED_ARTIFACT_BLOBS
    }
    if observed_blobs != EXPECTED_ARTIFACT_BLOBS:
        raise LabboibBindingError(
            "LABBOIB durable artifact identity drifted from the authorized binding basis"
        )

    observed_authority_blob = _blob_sha(repo, commit, AUTHORITY_PATH)
    if observed_authority_blob != AUTHORITY_BLOB:
        raise LabboibBindingError(
            "LABBOIB controller authority object drifted from the authorized binding basis"
        )

    manifest = _read_json(repo, commit, MANIFEST_PATH)
    cursor = _read_json(repo, commit, CURSOR_PATH)
    working_state = _read_json(repo, commit, WORKING_STATE_PATH)
    events = _read_jsonl(repo, commit, EVENTS_PATH)

    if manifest.get("seat_id") != SEAT_ID:
        raise LabboibBindingError("manifest seat_id is not LABBOIB")
    if cursor.get("consumer") != "labboib":
        raise LabboibBindingError("cursor consumer is not labboib")
    if cursor.get("last_seen_event_id") != EXPECTED_CURSOR:
        raise LabboibBindingError("LABBOIB cursor drifted from CE-000033")
    if (
        working_state.get("continuity", {}).get("synchronized_through")
        != EXPECTED_CURSOR
    ):
        raise LabboibBindingError(
            "LABBOIB working-state continuity coordinate disagrees with cursor"
        )
    if not events or events[-1].get("event_id") != EXPECTED_CURSOR:
        raise LabboibBindingError(
            "authorized continuity stream does not end at LABBOIB cursor"
        )

    return {
        "binding_id": BINDING_ID,
        "seat_id": SEAT_ID,
        "source_commit": commit,
        "canonical_main_commit_at_binding": CANONICAL_MAIN_AT_BINDING,
        "artifact_blobs": observed_blobs,
        "continuity_head": events[-1]["event_id"],
        "manifest": manifest,
        "cursor": cursor,
        "working_state": working_state,
        "events": events,
        "authority_ref": AUTHORITY_REF,
    }


def bind_labboib(
    pool: GoblinPool,
    source_repo: str | Path,
    source_ref: str = "HEAD",
) -> dict[str, Any]:
    """Bind exact LABBOIB Git basis into a distinct controller runtime record."""
    basis = reconstruct_seat_basis(source_repo, source_ref)

    # GOBLIN_POOL_001 supplies schema/operators and remains pressure scaffolding.
    pool.initialize_fixture()

    runtime_state = {
        "schema_version": "labboib_controller_runtime_state_v0",
        "binding_id": BINDING_ID,
        "seat_id": SEAT_ID,
        "git_seat_basis": {
            "source_commit": basis["source_commit"],
            "canonical_main_commit_at_binding": basis[
                "canonical_main_commit_at_binding"
            ],
            "artifact_blobs": basis["artifact_blobs"],
            "continuity_head": basis["continuity_head"],
        },
        "git_working_state": basis["working_state"],
        "controller_runtime": {
            "last_operator_invocation_ids": [],
            "last_transition_summary": None,
        },
    }

    binding = pool.bind_external_seat(
        seat_id=SEAT_ID,
        cursor_event_id=basis["cursor"]["last_seen_event_id"],
        working_state=runtime_state,
        source_events=basis["events"],
        policy_ref=(
            "docs/candidates/labboib_temporal_seat_v0/"
            "LABBOIB_TEMPORAL_SEAT_CONTRACT_v0.md"
        ),
        operator_profile_ref=f"{BINDING_ID}:operators:v0",
        authority_profile_ref=AUTHORITY_REF,
    )

    pool.configure_seat_operator(
        SEAT_ID,
        "READ_REPO_STATE",
        eligible=True,
        authorized=True,
        authority_ref=AUTHORITY_REF,
    )
    pool.configure_seat_operator(
        SEAT_ID,
        "RUN_DECLARED_TEST",
        eligible=True,
        authorized=True,
        authority_ref=AUTHORITY_REF,
    )
    pool.configure_seat_operator(
        SEAT_ID,
        "WRITE_PACKET",
        eligible=False,
        authorized=False,
        authority_ref=None,
    )

    pool.register_declared_test(
        DECLARED_TEST_ID,
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.runtime.test_labboib_temporal_seat",
            "-v",
        ],
    )

    return {
        "schema_version": "labboib_controller_binding_result_v0",
        "binding_id": BINDING_ID,
        "seat_id": SEAT_ID,
        "binding_status": binding["status"],
        "seat_basis": {
            "source_commit": basis["source_commit"],
            "canonical_main_commit_at_binding": basis[
                "canonical_main_commit_at_binding"
            ],
            "artifact_blobs": basis["artifact_blobs"],
            "cursor_event_id": basis["cursor"]["last_seen_event_id"],
            "continuity_head": basis["continuity_head"],
        },
        "operator_postures": {
            operator_id: pool.operator_posture(SEAT_ID, operator_id)
            for operator_id in (
                "READ_REPO_STATE",
                "RUN_DECLARED_TEST",
                "WRITE_PACKET",
            )
        },
        "authority_ref": AUTHORITY_REF,
        "git_seat_mutation_effect": "NONE_BY_BINDING",
    }


def commit_runtime_successor(
    pool: GoblinPool,
    wake_id: str,
    *,
    transition_id: str,
    output_id: str,
    summary: str,
    accepted_operator_invocation_ids: list[str],
    consumed_event_ids: list[str] | None = None,
) -> dict[str, Any]:
    seat = pool.seat_snapshot(SEAT_ID)
    current = copy.deepcopy(seat["working_state"])
    current.setdefault("controller_runtime", {})
    current["controller_runtime"]["last_operator_invocation_ids"] = list(
        accepted_operator_invocation_ids
    )
    current["controller_runtime"]["last_transition_summary"] = summary

    return pool.commit_transition(
        wake_id,
        transition_id=transition_id,
        output_id=output_id,
        output_kind="STATUS",
        output_payload={
            "binding_id": BINDING_ID,
            "summary": summary,
            "accepted_operator_invocation_ids": accepted_operator_invocation_ids,
        },
        consumed_event_ids=list(consumed_event_ids or []),
        resulting_working_state=current,
        accepted_operator_invocation_ids=accepted_operator_invocation_ids,
    )


def execute_read(
    pool: GoblinPool,
    wake_id: str,
    invocation_id: str,
    *,
    expected_repo_head: str | None = None,
) -> dict[str, Any]:
    expected = expected_repo_head or _workspace_head(pool.workspace)
    return pool.execute_operator(
        wake_id,
        invocation_id,
        "READ_REPO_STATE",
        {"expected_repo_head": expected},
    )


def execute_declared_test(
    pool: GoblinPool,
    wake_id: str,
    invocation_id: str,
    *,
    expected_repo_head: str | None = None,
) -> dict[str, Any]:
    expected = expected_repo_head or _workspace_head(pool.workspace)
    return pool.execute_operator(
        wake_id,
        invocation_id,
        "RUN_DECLARED_TEST",
        {
            "test_id": DECLARED_TEST_ID,
            "expected_repo_head": expected,
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--seat-source-ref", default="HEAD")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("bind")

    p_wake = sub.add_parser("wake")
    p_wake.add_argument("wake_id")

    p_read = sub.add_parser("read")
    p_read.add_argument("wake_id")
    p_read.add_argument("invocation_id")

    p_test = sub.add_parser("test")
    p_test.add_argument("wake_id")
    p_test.add_argument("invocation_id")

    args = parser.parse_args(argv)
    pool = GoblinPool(args.db, args.workspace)

    if args.command == "bind":
        result = bind_labboib(pool, args.workspace, args.seat_source_ref)
    elif args.command == "wake":
        result = pool.start_wake(SEAT_ID, args.wake_id)
    elif args.command == "read":
        result = execute_read(pool, args.wake_id, args.invocation_id)
    elif args.command == "test":
        result = execute_declared_test(pool, args.wake_id, args.invocation_id)
    else:
        raise AssertionError(args.command)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
