#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0,str(TOOLS))

import live_completion_controller_adapter_v1 as adapter


def pretty_bytes(value):
    return (json.dumps(value,sort_keys=True,indent=2)+"\n").encode("utf-8")


def git_blob(path):
    proc=subprocess.run(["git","-C",str(ROOT),"hash-object",path],capture_output=True,text=True,check=True)
    return proc.stdout.strip()


def evaluate():
    observed=adapter.evaluate_authoritative_controller(ROOT)
    result=observed["controller_result"]
    expected_predicates=["P01","P02","P03","P04","P05","P06","P07","P08"]
    ok=(
        observed["controller_blob"]==adapter.AUTHORITATIVE_CONTROLLER_BLOB
        and observed["transition_executed"] is False
        and observed["live_lane_mutation"]=="NONE"
        and result.get("admissible") is True
        and result.get("selected_branch")=="COMPLETE"
        and result.get("predicates_consulted",{}).get("admissibility")==expected_predicates
        and result.get("resulting_state")=={
            "claim_status":"COMPLETED",
            "lane_status":"READY_UNCLAIMED",
            "occupant_binding":None,
        }
    )
    return {
        "object_type":"LIVE_COMPLETION_EVIDENCE_REPAIR_FINAL_EVIDENCE",
        "object_id":"LIVE_COMPLETION_EVIDENCE_001-REPAIR-V1-FINAL-001",
        "review_basis":"LIVE_COMPLETION_EVIDENCE_001-INDEPENDENT_REVIEW-001",
        "repaired_fractures":["Q1","Q2","Q3","Q4","Q5","Q6"],
        "implementation_blobs":{
            "raw_evaluator":git_blob("tools/live_completion_raw_evaluator_v1.py"),
            "p07_producer":git_blob("tools/live_unit_completion_standing_producer_v1.py"),
            "p08_producer":git_blob("tools/live_completion_blocker_status_producer_v1.py"),
            "controller_adapter":git_blob("tools/live_completion_controller_adapter_v1.py"),
            "authoritative_controller":git_blob("tools/lane_lifecycle_disposition_v0.py"),
        },
        "relation_basis_blobs":{
            "P07":git_blob("fixtures/live_completion_evidence_v1/P07_RELATION_BASIS_001.json"),
            "P08":git_blob("fixtures/live_completion_evidence_v1/P08_RELATION_BASIS_001.json"),
        },
        "qualification_registry_blob":git_blob("fixtures/live_completion_evidence_v1/PRODUCER_QUALIFICATION_REGISTRY_002.json"),
        "controller_evaluation":observed,
        "pass":ok,
        "lifecycle_execution":"NONE",
        "live_lane_mutation":"NONE",
        "merge":"NONE",
    }


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    args=ap.parse_args(argv)
    result=evaluate()
    data=pretty_bytes(result)
    if args.output:
        Path(args.output).write_bytes(data)
    else:
        print(data.decode(),end="")
    return 0 if result["pass"] else 1


if __name__=="__main__":
    raise SystemExit(main())
