#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"main_merge_qualification_observation.json"

RESULTS={
  "successor_projection":(
    ROOT/"docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_PRESSURE_RESULT_001.md",
    "MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_MATCHED",
  ),
  "control_cell_001":(
    ROOT/"docs/campaigns/control_kernel_001/pressure_runs/CONTROL_KERNEL_CELL_001_PRESSURE_RESULT_001.md",
    "CONTROL_KERNEL_CELL_001_MATCHED",
  ),
  "relational_horizon":(
    ROOT/"docs/campaigns/control_kernel_001/pressure_runs/RELATIONAL_HORIZON_V0_PRESSURE_RESULT_001.md",
    "RELATIONAL_HORIZON_V0_MATCHED",
  ),
  "gap_selector":(
    ROOT/"docs/campaigns/control_kernel_001/pressure_runs/HORIZON_GAP_SELECTOR_V0_PRESSURE_RESULT_001.md",
    "HORIZON_GAP_SELECTOR_V0_MATCHED",
  ),
}

def run(args):
    return subprocess.run(args,cwd=ROOT,capture_output=True,text=True)

def git(*args):
    p=run(["git",*args])
    if p.returncode: raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return p.stdout.strip()

def main():
    if OUT.exists():
        raise SystemExit("remove existing main_merge_qualification_observation.json first")

    source_head=git("rev-parse","HEAD")
    main_ref=git("rev-parse","origin/main")
    clean_before=(git("status","--porcelain")=="")
    ancestor=run(["git","merge-base","--is-ancestor","origin/main","HEAD"]).returncode==0

    standing={}
    for name,(path,token) in RESULTS.items():
        text=path.read_text(encoding="utf-8")
        standing[name]={"path":str(path.relative_to(ROOT)),"required":token,"matched":token in text}

    workcycle=json.loads((ROOT/"docs/campaigns/workcycle_stabilization_001/state/CURRENT_CAMPAIGN_STATE_V0.json").read_text())
    control=json.loads((ROOT/"docs/campaigns/control_kernel_001/state/CURRENT_CAMPAIGN_STATE_V0.json").read_text())

    tests=run([sys.executable,"-m","unittest","discover","-s","tests","-p","test_*.py","-q"])
    combined=(tests.stdout+"\n"+tests.stderr).strip()
    m=re.search(r"Ran\s+(\d+)\s+tests?",combined)
    test_count=int(m.group(1)) if m else None
    clean_after=(git("status","--porcelain")=="")
    head_after=git("rev-parse","HEAD")

    assertions={
      "source_head_stable": source_head==head_after,
      "origin_main_is_ancestor": ancestor,
      "working_tree_clean_before": clean_before,
      "working_tree_clean_after": clean_after,
      "full_test_discovery_passed": tests.returncode==0,
      "full_test_count_observed": test_count is not None,
      "all_required_standings_frozen": all(x["matched"] for x in standing.values()),
      "workcycle_campaign_closed": workcycle.get("campaign_posture")=="CLOSED",
      "control_kernel_checkpoint_closed": control.get("campaign_posture")=="CHECKPOINT_CLOSED_AWAITING_BRANCH_QUALIFICATION",
      "control_kernel_has_no_current_gap": control.get("current_gap") is None,
      "control_kernel_composition_not_prequalified": control.get("checkpoint_closure",{}).get("composition_claim")=="NOT_YET_BRANCH_QUALIFIED",
    }

    obs={
      "object_type":"MAIN_MERGE_QUALIFICATION_OBSERVATION_V0",
      "repo_head":source_head,
      "origin_main":main_ref,
      "branch":"draci-v0-candidate-basis",
      "standing_checks":standing,
      "test_run":{
        "command":"python -m unittest discover -s tests -p test_*.py -q",
        "returncode":tests.returncode,
        "test_count":test_count,
        "output_tail":combined[-4000:],
      },
      "assertions":assertions,
      "all_assertions_pass":all(assertions.values()),
      "qualification_posture":"CANDIDATE_FOR_INDEPENDENT_MERGE_QUALIFICATION" if all(assertions.values()) else "HOLD_NOT_QUALIFIED",
      "merge_effect":"NONE",
      "claim_ceiling":"Exact-head branch-wide merge-qualification witness only. It demonstrates the discovered test suite passed, origin/main is an ancestor, the working tree remained clean, and required frozen component standings are present. It does not itself merge, authorize merge, create scientific standing, or qualify future commits.",
      "stopped":"YES",
    }
    data=(json.dumps(obs,indent=2)+"\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] test_count {test_count}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print(f"[OK] qualification_posture {obs['qualification_posture']}")
    return 0 if obs["all_assertions_pass"] else 1

if __name__=="__main__":
    raise SystemExit(main())
