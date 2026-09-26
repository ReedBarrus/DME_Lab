#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.relational_horizon_v0 import build_relational_horizon

OUT = ROOT / "relational_horizon_v0_observation.json"
PATH = "docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md"
PRE = "235aceddfec91af6826e25baef469c82287fde99"
POST = "331578bc44225d2810c9d5604606e83864553d0f"
HID = "H1_POST_CONSEQUENCE_PHASE_HANDOFF"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def gap() -> dict:
    return {
        "gap_id": "G1_STALE_SUCCESSOR_3_HANDOFF",
        "statement": (
            "The post-consequence projection requires SUCCESSOR_3 even though "
            "earned law permits SATISFIED -> CLOSE_BASIS -> NO_SUCCESSOR -> STOP."
        ),
        "blocks": ["CONTROL_KERNEL_ACTIVATION", "CAMPAIGN_HANDOFF", "RECONSTRUCTION"],
        "work_eligible": True,
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit("remove existing relational_horizon_v0_observation.json first")

    before_text = git("show", f"{PRE}:{PATH}")
    after_text = git("show", f"{POST}:{PATH}")

    before_evidence = (
        "DO_NOT_INSTANTIATE_UNTIL_EXACT_CONSEQUENCE_SPINE_IS_FROZEN_THROUGH_SUCCESSOR_3"
        in before_text
    )
    after_evidence = (
        "DO_NOT_INSTANTIATE_UNTIL_EXACT_CONSEQUENCE_SPINE_IS_FROZEN_THROUGH_AN_INDEPENDENTLY_ADJUDICATED_SUCCESSOR_OR_NO_SUCCESSOR_TERMINAL_PROJECTION"
        in after_text
        and "NO_SUCCESSOR" in after_text
    )

    before = build_relational_horizon(
        horizon_id=HID,
        subject="post-consequence phase handoff",
        counterparty_or_surface=PATH,
        declared_purpose=(
            "Enter the control-kernel phase without manufacturing continuation "
            "after lawful no-successor closure."
        ),
        posture="PARTIAL",
        evidence_refs=[f"repo://{PRE}"],
        load_bearing_gaps=[gap()],
    )
    after = build_relational_horizon(
        horizon_id=HID,
        subject="post-consequence phase handoff",
        counterparty_or_surface=PATH,
        declared_purpose=(
            "Enter the control-kernel phase without manufacturing continuation "
            "after lawful no-successor closure."
        ),
        posture="CLOSED",
        evidence_refs=[f"repo://{POST}"],
        load_bearing_gaps=[],
    )

    assertions = {
        "before_evidence_observed": before_evidence,
        "after_evidence_observed": after_evidence,
        "stable_logical_horizon_identity": before["horizon_id"] == after["horizon_id"],
        "state_identity_changes": before["horizon_state_id"] != after["horizon_state_id"],
        "integrity_changes": before["integrity_sha256"] != after["integrity_sha256"],
        "before_partial_with_one_gap": (
            before["current_posture"]["state"] == "PARTIAL"
            and len(before["load_bearing_gaps"]) == 1
        ),
        "after_closed_with_empty_gaps": (
            after["current_posture"]["state"] == "CLOSED"
            and after["load_bearing_gaps"] == []
        ),
        "representation_source_external": (
            before["representation_source"] == "EXTERNALLY_SUPPLIED"
            and after["representation_source"] == "EXTERNALLY_SUPPLIED"
        ),
        "no_selection_or_work_effects": all(
            h["gap_selection_effect"] == "NONE"
            and h["work_justification_effect"] == "NONE"
            and h["work_materialization_effect"] == "NONE"
            and h["authority_effect"] == "NONE"
            and h["execution_effect"] == "NONE"
            and h["scientific_standing_effect"] == "NONE"
            for h in (before, after)
        ),
    }

    observation = {
        "object_type": "RELATIONAL_HORIZON_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD").strip(),
        "campaign_id": "CONTROL_KERNEL_001",
        "cell_id": "CONTROL_KERNEL_CELL_002",
        "source_refs": {"before": PRE, "after": POST},
        "before": before,
        "after": after,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, one externally supplied relational "
            "horizon can mechanically represent the same stable logical horizon "
            "before and after one bounded repository consequence while its state "
            "identity changes from PARTIAL with one declared live gap to CLOSED "
            "with an empty declared gap set. No gap selection, ranking, work "
            "justification, planning, authority, execution, or scientific standing "
            "is established."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(
        "[OK] stable_logical_horizon_identity "
        + str(assertions["stable_logical_horizon_identity"])
    )
    print("[OK] state_identity_changes " + str(assertions["state_identity_changes"]))
    print(
        "[OK] after_closed_with_empty_gaps "
        + str(assertions["after_closed_with_empty_gaps"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
