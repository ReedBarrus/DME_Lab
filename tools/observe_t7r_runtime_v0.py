#!/usr/bin/env python3
"""Bounded T7R runtime observation witness.

Exercises current workcycle control/projection behavior in a disposable local
fixture. It does not mutate repository source or the operator's real Cockpit
control store.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from src.cockpit.workcycle_control import LocalWorkcycleControlStore, WorkcycleControlError
from src.cockpit.workcycle_projection import build_workcycle_projection
from src.coordination import workcycle_v0 as wc


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "t7r_runtime_observation.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(store: LocalWorkcycleControlStore) -> dict:
    state = store.read()
    return {
        "state": state,
        "state_sha256": store.state_sha256(),
    }


def confirmed_commit(store: LocalWorkcycleControlStore, verb: str, gesture: str) -> dict:
    preview = store.preview({"verb": verb, "gesture_id": gesture, "reason": "T7R bounded runtime observation"})
    answer = input(f"Confirm disposable T7R {verb} transition as REED? [y/N] ").strip().lower()
    if answer != "y":
        raise SystemExit(f"T7R observation aborted before {verb}")
    result = store.commit(
        preview=preview["preview"],
        preview_sha256=preview["preview_sha256"],
        confirmed_by="REED",
    )
    return {
        "verb": verb,
        "preview_sha256": preview["preview_sha256"],
        "result_status": result["status"],
        "state": result["state"],
        "state_sha256": result["state_sha256"],
        "model_invocation_effect": result["model_invocation_effect"],
        "repository_mutation_effect": result["repository_mutation_effect"],
    }


def malformed_optional_state_observation() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        state_dir = repo / "docs" / "campaigns" / "workcycle_stabilization_001" / "state"
        state_dir.mkdir(parents=True)
        bad = state_dir / "WAKE_BUDGET_V0.json"
        bad.write_text(
            '{"object_type":"WAKE_BUDGET_V0","integrity_sha256":"bad"}',
            encoding="utf-8",
        )
        projection = build_workcycle_projection(repo)
        return {
            "projection_errors": projection["projection_errors"],
            "current_unresolved": projection["current_unresolved"],
            "wake_budget": projection["wake_budget"],
            "projection_boundary": projection["projection_boundary"],
        }


def current_state_without_full_replay_observation() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        current_dir = root / "continuity" / "current_state"
        current_dir.mkdir(parents=True)
        state_path = current_dir / "materialized_state.json"
        materialized = {
            "CURRENT_STATE_ID": "T7R-CURRENT-001",
            "ACTIVE_OPERATOR": "O0",
            "TARGET": "P0",
            "STATUS": "RESOLVED",
            "VALUE": True,
            "STANDING": "REPORTED",
            "VERIFICATION_STANDING": "NOT_VERIFIED",
            "SOURCE_EVENT": "CE-000003",
            "SOURCE_BASIS_REF": "base_state_artifact.json",
        }
        state_path.write_text(json.dumps(materialized, indent=2) + "\n", encoding="utf-8")
        recovered = json.loads(state_path.read_text(encoding="utf-8"))
        return {
            "current_state_file_count": len(list(current_dir.iterdir())),
            "recovered": recovered,
            "history_replay_performed": False,
        }


def main() -> int:
    if OUT.exists():
        raise SystemExit("t7r_runtime_observation.json already exists; move/remove it before a fresh observation")

    head = __import__("subprocess").run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    with tempfile.TemporaryDirectory() as tmp:
        fixture_root = Path(tmp)
        control_path = fixture_root / "workcycle_control.json"
        store = LocalWorkcycleControlStore(path=control_path, repo=ROOT)

        observations = {
            "initial": snapshot(store),
            "transitions": [],
        }
        observations["transitions"].append(confirmed_commit(store, "ENABLE", "T7R-G1"))
        observations["transitions"].append(confirmed_commit(store, "WAKE", "T7R-G2"))

        try:
            store.preview({"verb": "ADMIT_ONE", "gesture_id": "T7R-G3"})
            admit = {"posture": "UNEXPECTEDLY_PREVIEWED"}
        except WorkcycleControlError as exc:
            admit = {
                "posture": "FAILED_CLOSED",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        observations["admit_one"] = admit

        observations["transitions"].append(confirmed_commit(store, "PAUSE", "T7R-G4"))
        observations["transitions"].append(confirmed_commit(store, "ENABLE", "T7R-G5"))
        observations["transitions"].append(confirmed_commit(store, "STOP", "T7R-G6"))
        observations["final"] = snapshot(store)

    projection = build_workcycle_projection(ROOT)

    witness = {
        "object_type": "T7R_RUNTIME_OBSERVATION_V0",
        "repo_head": head,
        "fixture_posture": "DISPOSABLE_LOCAL_RUNTIME_FIXTURE",
        "real_operator_control_store_mutated": False,
        "repository_source_mutated": False,
        "control_transition_observation": observations,
        "current_projection_observation": {
            "campaign_id": projection.get("campaign_id"),
            "active_horizon": projection.get("active_horizon"),
            "active_work_item": projection.get("active_work_item"),
            "latest_completed_work_item": projection.get("latest_completed_work_item"),
            "next_eligible_work_item": projection.get("next_eligible_work_item"),
            "eligibility": projection.get("eligibility"),
            "projection_boundary": projection.get("projection_boundary"),
        },
        "malformed_optional_state_observation": malformed_optional_state_observation(),
        "current_state_without_full_replay_observation": current_state_without_full_replay_observation(),
        "claim_ceiling": (
            "This witness observes current code in bounded disposable runtime fixtures. "
            "It does not prove the packaged desktop UI exercised these exact paths, "
            "does not mutate real operator control, does not create execution authority, "
            "and does not establish scientific standing."
        ),
        "authority_effect": "NONE",
        "execution_effect": "DISPOSABLE_FIXTURE_ONLY",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(witness, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
