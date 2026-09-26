#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"main_merge_qualification_observation.json"
TIMEOUT_SECONDS=60

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

# Bounded matrix = active repo CI regressions + exact promoted consequence/control chain.
PY_MODULES=[
  # current control kernel
  "tests.control.test_control_kernel_cell_001_v0",
  "tests.control.test_relational_horizon_v0",
  "tests.control.test_horizon_gap_selector_v0",
  # promoted workcycle / consequence chain
  "tests.coordination.test_workcycle_v0",
  "tests.coordination.test_basis_workcycle_v1",
  "tests.coordination.test_authority_binding_v0",
  "tests.coordination.test_atomic_admission_v0",
  "tests.coordination.test_verified_authority_admission_v0",
  "tests.coordination.test_admitted_authority_consumption_v0",
  "tests.coordination.test_invocation_result_settlement_v0",
  "tests.coordination.test_settlement_consequence_reconciliation_v0",
  "tests.coordination.test_successor_work_unit_materialization_v0",
  "tests.coordination.test_materialized_unit_authority_admission_v0",
  "tests.coordination.test_materialized_admitted_authority_consumption_v0",
  "tests.coordination.test_materialized_invocation_result_settlement_v0",
  "tests.coordination.test_materialized_settlement_consequence_reconciliation_v0",
  "tests.coordination.test_materialized_reconciliation_successor_projection_v0",
  "tests.observation.test_invocation_result_witness_v0",
  "tests.observation.test_materialized_invocation_result_witness_v0",
  # established CI surfaces on this repo
  "tests.cockpit.test_action_surface",
  "tests.lab.test_lab_conductor",
  "tests.cockpit.test_projection_adapter",
  "tests.runtime.test_cockpit_online_read_integration",
  "tests.runtime.test_historical_p09_producer_v0",
  "tests.runtime.test_historical_p11_producer_v0",
  "tests.runtime.test_labboib_temporal_seat",
  "tests.runtime.test_quiet_peer_coordination_v1",
  "tests.runtime.test_legacy_lane_succession_fencing_v0",
  "tests.runtime.test_two_lane_coordination_v0",
  "tests.runtime.test_live_predecessor_fence_v0",
  "tests.runtime.test_primary_ecology_v0",
]

HISTORICAL_BRANCH_SCOPED_EXCLUSIONS=[
  {
    "modules":[
      "tests.runtime.test_lane_b_successor_engagement_v0",
      "tests.runtime.test_lane_b_successor_engagement_repressure_v1",
    ],
    "workflows":[
      ".github/workflows/lane-b-successor-engagement-001.yml",
      ".github/workflows/lane-b-successor-engagement-repressure-001.yml",
    ],
    "required_branch_tokens":[
      "lane-b-successor-engagement-qualification-v0",
      "lane-b-successor-engagement-repressure-v1",
      "lane-b-successor-engagement-repressure-repair-v1",
    ],
    "historical_basis":"f6d033068c2df18c3261dae3e1769517a4762ae5",
    "historical_fixture_paths":[
      "coordination/lane_manifest.json",
      "coordination/succession/LANE_B_SUCCESSOR_INSTANCE_001.json",
    ],
    "reason":"Dedicated historical Lane-B qualification apparatus requires historical successor fixtures intentionally absent from the current DRACI branch.",
  }
]

NODE_FILES=[
  "tests/cockpit/test_observer.mjs",
  "tests/cockpit/test_perceptual_instrument.mjs",
  "tests/cockpit/test_control_adapter.mjs",
  "tests/cockpit/test_online_integration.mjs",
]

def run(args, timeout=TIMEOUT_SECONDS):
    try:
        return subprocess.run(
            args,cwd=ROOT,capture_output=True,text=True,timeout=timeout
        ), None
    except subprocess.TimeoutExpired as exc:
        return None, f"TIMEOUT_AFTER_{timeout}s"

def git(*args):
    p,e=run(["git",*args],timeout=15)
    if e: raise RuntimeError(e)
    if p.returncode: raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return p.stdout.strip()

def git_path_exists(ref,path):
    p,e=run(["git","cat-file","-e",f"{ref}:{path}"],timeout=15)
    return e is None and p is not None and p.returncode==0

def verify_historical_exclusions():
    rows=[]
    for spec in HISTORICAL_BRANCH_SCOPED_EXCLUSIONS:
        workflow_text="\n".join((ROOT/p).read_text(encoding="utf-8") for p in spec["workflows"])
        branch_scope_verified=all(token in workflow_text for token in spec["required_branch_tokens"])
        fixture_rows=[]
        for path in spec["historical_fixture_paths"]:
            fixture_rows.append({
              "path":path,
              "absent_at_head":not git_path_exists("HEAD",path),
              "present_at_historical_basis":git_path_exists(spec["historical_basis"],path),
            })
        rows.append({
          "modules":spec["modules"],
          "reason":spec["reason"],
          "branch_scope_verified":branch_scope_verified,
          "historical_basis":spec["historical_basis"],
          "fixtures":fixture_rows,
          "verified":branch_scope_verified and all(x["absent_at_head"] and x["present_at_historical_basis"] for x in fixture_rows),
        })
    return rows

def run_case(name,args):
    print(f"[RUN] {name}",flush=True)
    p,err=run(args)
    if err:
        print(f"[FAIL] {name} {err}",flush=True)
        return {"name":name,"command":args,"returncode":None,"timeout":True,"passed":False,"output_tail":err}
    output=(p.stdout+"\n"+p.stderr).strip()
    passed=p.returncode==0
    print(f"[{'OK' if passed else 'FAIL'}] {name}",flush=True)
    return {
      "name":name,"command":args,"returncode":p.returncode,"timeout":False,
      "passed":passed,"output_tail":output[-2000:]
    }

def main():
    if OUT.exists():
        raise SystemExit("remove existing main_merge_qualification_observation.json first")

    source_head=git("rev-parse","HEAD")
    main_ref=git("rev-parse","origin/main")
    clean_before=(git("status","--porcelain")=="")
    ancestor=run(["git","merge-base","--is-ancestor","origin/main","HEAD"],timeout=15)[0]
    ancestor_ok=ancestor is not None and ancestor.returncode==0

    standing={}
    for name,(path,token) in RESULTS.items():
        text=path.read_text(encoding="utf-8")
        standing[name]={"path":str(path.relative_to(ROOT)),"required":token,"matched":token in text}

    workcycle=json.loads((ROOT/"docs/campaigns/workcycle_stabilization_001/state/CURRENT_CAMPAIGN_STATE_V0.json").read_text())
    control=json.loads((ROOT/"docs/campaigns/control_kernel_001/state/CURRENT_CAMPAIGN_STATE_V0.json").read_text())

    historical_exclusions=verify_historical_exclusions()

    cases=[]
    for module in PY_MODULES:
        cases.append(run_case(module,[sys.executable,"-m","unittest",module,"-q"]))
    for file in NODE_FILES:
        cases.append(run_case(file,["node","--test",file]))

    clean_after=(git("status","--porcelain")=="")
    head_after=git("rev-parse","HEAD")
    passed_count=sum(1 for x in cases if x["passed"])

    assertions={
      "source_head_stable": source_head==head_after,
      "origin_main_is_ancestor": ancestor_ok,
      "working_tree_clean_before": clean_before,
      "working_tree_clean_after": clean_after,
      "bounded_regression_matrix_passed": all(x["passed"] for x in cases),
      "historical_branch_scoped_exclusions_verified": all(x["verified"] for x in historical_exclusions),
      "bounded_regression_case_count_observed": len(cases)==len(PY_MODULES)+len(NODE_FILES),
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
      "historical_branch_scoped_exclusions":historical_exclusions,
      "regression_matrix":{
        "basis":"applicable active repo CI modules plus exact promoted consequence/control chain; dedicated historical branch-scoped apparatus is separately verified and excluded",
        "timeout_seconds_per_case":TIMEOUT_SECONDS,
        "case_count":len(cases),
        "passed_count":passed_count,
        "cases":cases,
      },
      "assertions":assertions,
      "all_assertions_pass":all(assertions.values()),
      "qualification_posture":"CANDIDATE_FOR_INDEPENDENT_MERGE_QUALIFICATION" if all(assertions.values()) else "HOLD_NOT_QUALIFIED",
      "merge_effect":"NONE",
      "claim_ceiling":"Exact-head bounded merge-qualification witness. It demonstrates a cross-surface regression matrix derived from applicable active repo CI plus the promoted consequence/control chain passed with per-case timeouts; dedicated historical branch-scoped Lane-B apparatus was separately verified as non-applicable because its historical successor fixtures are absent at HEAD and present at its frozen basis; origin/main is an ancestor, the working tree remained clean, and required frozen standings are present. It is not exhaustive proof over every historical test, does not itself merge or authorize merge, creates no scientific standing, and does not qualify future commits.",
      "stopped":"YES",
    }
    data=(json.dumps(obs,indent=2)+"\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}",flush=True)
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}",flush=True)
    print(f"[OK] regression_cases {len(cases)}",flush=True)
    print(f"[OK] regression_passed {passed_count}",flush=True)
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}",flush=True)
    print(f"[OK] qualification_posture {obs['qualification_posture']}",flush=True)
    return 0 if obs["all_assertions_pass"] else 1

if __name__=="__main__":
    raise SystemExit(main())
