#!/usr/bin/env python3
"""Freeze one bounded temporal-horizon closure observation.

Reads the current local generated temporal lineage plus the current repository
workcycle projection, derives ATLAS_TEMPORAL_HORIZON_CLOSURE_V0, and writes one
compact witness. No authority, admission, execution, or repository source
mutation is performed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cockpit.workcycle_projection import build_workcycle_projection
from src.cockpit.temporal_horizon_closure import derive_temporal_horizon_closure


TEMPORAL_PATH = ROOT / "generated" / "repository_temporal_lineage.json"
OUT = ROOT / "temporal_horizon_closure_observation.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "temporal_horizon_closure_observation.json already exists; move/remove it before a fresh observation"
        )
    if not TEMPORAL_PATH.is_file():
        raise SystemExit(
            "generated/repository_temporal_lineage.json is missing; launch/regenerate the Cockpit temporal projection first"
        )

    temporal_bytes = TEMPORAL_PATH.read_bytes()
    temporal = json.loads(temporal_bytes.decode("utf-8"))
    workcycle = build_workcycle_projection(ROOT)
    closure = derive_temporal_horizon_closure(
        temporal_lineage=temporal,
        workcycle=workcycle,
    )

    transitions = temporal.get("transitions") or []
    recent = transitions[-1] if transitions else None

    witness = {
        "object_type": "ATLAS_TEMPORAL_HORIZON_CLOSURE_OBSERVATION_V0",
        "repo_head": git_head(),
        "temporal_lineage": {
            "path": "generated/repository_temporal_lineage.json",
            "sha256": sha256_bytes(temporal_bytes),
            "source_commit": temporal.get("source_commit"),
            "transition_count": len(transitions),
            "recent_transition": recent,
        },
        "workcycle_currentness": {
            "campaign_id": workcycle.get("campaign_id"),
            "active_horizon": workcycle.get("active_horizon"),
            "active_work_item": workcycle.get("active_work_item"),
            "latest_completed_work_item": workcycle.get("latest_completed_work_item"),
            "next_eligible_work_item": workcycle.get("next_eligible_work_item"),
            "next_pressure": workcycle.get("next_pressure"),
            "current_unresolved": workcycle.get("current_unresolved"),
            "projection_errors": workcycle.get("projection_errors"),
            "eligibility": workcycle.get("eligibility"),
            "operative_control": workcycle.get("operative_control"),
            "seat_ecology": workcycle.get("seat_ecology"),
            "latest_consequence": workcycle.get("latest_consequence"),
            "latest_consequence_evaluation": workcycle.get("latest_consequence_evaluation"),
            "campaign_progress": workcycle.get("campaign_progress"),
            "projection_boundary": workcycle.get("projection_boundary"),
        },
        "closure": closure,
        "claim_ceiling": (
            "One bounded observation of temporal lineage + current workcycle + "
            "declared next pressure under current repository code. It does not "
            "establish semantic causation, work admission, authority, execution, "
            "campaign progress, or scientific standing."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(witness, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    print(f"[OK] disposition {closure.get('disposition')}")
    print(f"[OK] horizon {closure.get('primary_horizon', {}).get('family')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
