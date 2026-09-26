#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from src.control.horizon_gap_selector_v0 import HorizonGapSelectorError, select_gap_or_stop
from src.control.relational_horizon_v0 import build_relational_horizon

OUT=ROOT/"horizon_gap_selector_v0_observation.json"
HID="H1_POST_CONSEQUENCE_PHASE_HANDOFF"
PATH="docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md"
PRE="235aceddfec91af6826e25baef469c82287fde99"
POST="331578bc44225d2810c9d5604606e83864553d0f"

def git(*a):
    return subprocess.run(["git","-C",str(ROOT),*a],capture_output=True,text=True,check=True).stdout.strip()

def gap(i="G1_STALE_SUCCESSOR_3_HANDOFF"):
    return {"gap_id":i,"statement":"declared eligible gap","blocks":["CONTROL_KERNEL_ACTIVATION"],"work_eligible":True}

def hz(posture, ref, gaps):
    return build_relational_horizon(
        horizon_id=HID,
        subject="post-consequence phase handoff",
        counterparty_or_surface=PATH,
        declared_purpose="Enter control-kernel phase after lawful no-successor closure.",
        posture=posture,
        evidence_refs=[f"repo://{ref}"],
        load_bearing_gaps=gaps,
    )

def main():
    if OUT.exists():
        raise SystemExit("remove existing horizon_gap_selector_v0_observation.json first")

    before=hz("PARTIAL",PRE,[gap()])
    after=hz("CLOSED",POST,[])
    one=select_gap_or_stop(before)
    stop=select_gap_or_stop(after)

    multi=None
    try:
        select_gap_or_stop(hz("PARTIAL","fixture://multi",[gap(),gap("G2_SECOND_ELIGIBLE_GAP")]))
    except HorizonGapSelectorError as exc:
        multi={"error_type":type(exc).__name__,"error":str(exc)}

    assertions={
        "before_returns_exact_gap": one["selection_posture"]=="EXACT_ELIGIBLE_GAP" and one["selected_gap_id"]=="G1_STALE_SUCCESSOR_3_HANDOFF",
        "after_returns_no_justified_work": stop["selection_posture"]=="NO_JUSTIFIED_WORK" and stop["stop_required"] is True,
        "same_logical_horizon": one["source_horizon_id"]==stop["source_horizon_id"]==HID,
        "state_specific_binding": one["source_horizon_state_id"]!=stop["source_horizon_state_id"],
        "fixed_inputs_deterministic": one==select_gap_or_stop(before) and stop==select_gap_or_stop(after),
        "multi_gap_rejected_not_ranked": multi is not None,
        "neutral_downstream_effects": all(
            x["ranking_effect"]=="NONE" and x["planning_effect"]=="NONE"
            and x["work_materialization_effect"]=="NONE"
            and x["work_admission_effect"]=="NONE"
            and x["authority_effect"]=="NONE"
            and x["execution_effect"]=="NONE"
            and x["scientific_standing_effect"]=="NONE"
            for x in (one,stop)
        ),
    }
    obs={
        "object_type":"HORIZON_GAP_SELECTOR_V0_OBSERVATION",
        "repo_head":git("rev-parse","HEAD"),
        "campaign_id":"CONTROL_KERNEL_001",
        "cell_id":"CONTROL_KERNEL_CELL_003",
        "before_selection":one,
        "after_selection":stop,
        "multi_gap_pressure":multi,
        "assertions":assertions,
        "all_assertions_pass":all(assertions.values()),
        "claim_ceiling":"One validated represented horizon yields the exact sole declared work-eligible gap, or NO_JUSTIFIED_WORK when none exists. Multiple eligible gaps are rejected rather than ranked. No planning, materialization, admission, authority, execution, or scientific standing is created.",
        "stopped":"YES",
    }
    data=(json.dumps(obs,indent=2)+"\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print(f"[OK] before_returns_exact_gap {assertions['before_returns_exact_gap']}")
    print(f"[OK] after_returns_no_justified_work {assertions['after_returns_no_justified_work']}")
    print(f"[OK] multi_gap_rejected_not_ranked {assertions['multi_gap_rejected_not_ranked']}")
    return 0

if __name__=="__main__": raise SystemExit(main())
