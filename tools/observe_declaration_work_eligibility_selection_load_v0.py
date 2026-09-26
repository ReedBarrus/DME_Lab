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
from src.control.horizon_gap_selector_v0 import select_gap_or_stop


OUT = ROOT / "declaration_work_eligibility_selection_load_v0_observation.json"
HORIZON_ID = "H1_POST_CONSEQUENCE_PHASE_HANDOFF"
GAP_ID = "G1_STALE_SUCCESSOR_3_HANDOFF"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def horizon(work_eligible: bool) -> dict:
    return build_relational_horizon(
        horizon_id=HORIZON_ID,
        subject="post-consequence phase handoff",
        counterparty_or_surface=(
            "docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md"
        ),
        declared_purpose=(
            "Enter the control-kernel phase without manufacturing continuation "
            "after lawful no-successor closure."
        ),
        posture="PARTIAL",
        evidence_refs=["repo://G14_DECLARATION_ELIGIBILITY_PRESSURE"],
        load_bearing_gaps=[
            {
                "gap_id": GAP_ID,
                "statement": "declared eligible gap",
                "blocks": ["CONTROL_KERNEL_ACTIVATION"],
                "work_eligible": work_eligible,
            }
        ],
        representation_source="EXTERNALLY_SUPPLIED",
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing declaration_work_eligibility_selection_load_v0_observation.json first"
        )

    control_horizon = horizon(True)
    intervention_horizon = horizon(False)

    control_selection = select_gap_or_stop(control_horizon)
    intervention_selection = select_gap_or_stop(intervention_horizon)

    control_gap = control_horizon["load_bearing_gaps"][0]
    intervention_gap = intervention_horizon["load_bearing_gaps"][0]

    assertions = {
        "same_logical_horizon_id": (
            control_horizon["horizon_id"] == intervention_horizon["horizon_id"] == HORIZON_ID
        ),
        "same_gap_id": (
            control_gap["gap_id"] == intervention_gap["gap_id"] == GAP_ID
        ),
        "same_statement": control_gap["statement"] == intervention_gap["statement"],
        "same_blocks": control_gap["blocks"] == intervention_gap["blocks"],
        "declared_gap_persists_control": len(control_horizon["load_bearing_gaps"]) == 1,
        "declared_gap_persists_intervention": (
            len(intervention_horizon["load_bearing_gaps"]) == 1
        ),
        "control_work_eligible_true": control_gap["work_eligible"] is True,
        "intervention_work_eligible_false": intervention_gap["work_eligible"] is False,
        "control_exact_gap_selected": (
            control_selection["selection_posture"] == "EXACT_ELIGIBLE_GAP"
            and control_selection["selected_gap_id"] == GAP_ID
            and control_selection["eligible_gap_count"] == 1
            and control_selection["stop_required"] is False
        ),
        "intervention_no_justified_work": (
            intervention_selection["selection_posture"] == "NO_JUSTIFIED_WORK"
            and intervention_selection["selected_gap_id"] is None
            and intervention_selection["eligible_gap_count"] == 0
            and intervention_selection["stop_required"] is True
        ),
        "no_downstream_effects": all(
            selection[field] == "NONE"
            for selection in (control_selection, intervention_selection)
            for field in (
                "planning_effect",
                "work_materialization_effect",
                "work_admission_effect",
                "authority_effect",
                "execution_effect",
                "scientific_standing_effect",
            )
        ),
    }

    observation = {
        "object_type": "DECLARATION_WORK_ELIGIBILITY_SELECTION_LOAD_V0_OBSERVATION",
        "repo_head": git("rev-parse", "HEAD").strip(),
        "campaign_id": "DECLARATION_WORK_ELIGIBILITY_SELECTION_LOAD_001",
        "pressure_id": "DECLARATION_WORK_ELIGIBILITY_SELECTION_LOAD_V0_PRESSURE_001",
        "control": {
            "horizon": control_horizon,
            "selection": control_selection,
        },
        "intervention": {
            "horizon": intervention_horizon,
            "selection": intervention_selection,
        },
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "candidate_relation": {
            "declaration_standing_ne_work_eligibility": "YES",
            "work_eligibility_selection_load": "YES",
        },
        "claim_ceiling": (
            "At this bounded selector intervention, the same declared gap remains "
            "represented in the same logical horizon while changing only work_eligible "
            "from true to false changes selector posture from EXACT_ELIGIBLE_GAP to "
            "NO_JUSTIFIED_WORK. This does not establish criteria for granting eligibility, "
            "gap discovery, work admission, planning, authority, execution, or scientific standing."
        ),
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(
        "[OK] control selection",
        control_selection["selection_posture"],
        control_selection["selected_gap_id"],
    )
    print(
        "[OK] intervention selection",
        intervention_selection["selection_posture"],
        intervention_selection["selected_gap_id"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
