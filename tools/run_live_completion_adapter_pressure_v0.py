#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import inspect
import json
from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path: sys.path.insert(0,str(TOOLS))

import live_completion_controller_adapter_v2 as adapter
import live_completion_raw_evaluator_v1 as raw
import live_unit_completion_standing_producer_v1 as p07
import lane_lifecycle_disposition_v0 as lifecycle

FIX=ROOT/"fixtures/live_completion_evidence_v1"

def load(name:str)->dict[str,Any]:
    return json.loads((FIX/name).read_text())

@contextmanager
def mutate_json(path:Path, fn):
    original=path.read_text()
    obj=json.loads(original)
    fn(obj)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    try:
        yield
    finally:
        path.write_text(original)

@contextmanager
def mutate_text(path:Path, fn):
    original=path.read_text()
    path.write_text(fn(original))
    try:
        yield
    finally:
        path.write_text(original)

def capture(fn):
    calls={"n":0}
    original=lifecycle.LifecycleController.evaluate_branch
    def wrapped(self,data):
        calls["n"]+=1
        return original(self,data)
    lifecycle.LifecycleController.evaluate_branch=wrapped
    try:
        try:
            value=fn()
            return {"status":"RETURNED","value":value,"controller_calls":calls["n"]}
        except Exception as exc:
            return {"status":"RAISED","error":f"{type(exc).__name__}:{exc}","controller_calls":calls["n"]}
    finally:
        lifecycle.LifecycleController.evaluate_branch=original

def evaluate()->dict[str,Any]:
    out={}

    # A clean path
    a=adapter.evaluate(ROOT)
    consulted=a["controller_result"]["predicates_consulted"]["admissibility"]
    out["A"]={
      "exact_controller":a["authoritative_controller"]["blob"]==adapter.CONTROLLER_BLOB,
      "consulted":consulted,
      "admissible":a["controller_result"]["admissible"],
      "selected_branch":a["controller_result"]["selected_branch"],
      "transition_executed":a["transition_executed"]
    }

    # B raw evidence mutation
    p=FIX/"RAW_WORK_EVIDENCE.json"
    with mutate_json(p,lambda o:o["final_artifacts"][0].__setitem__("blob","0"*40)):
        out["B"]=capture(lambda:adapter.evaluate(ROOT))

    # C criterion semantic laundering
    p=FIX/"RAW_COMPLETION_CRITERION.json"
    with mutate_json(p,lambda o:o.__setitem__("consequence_envelope_id","LAUNDERED")):
        out["C"]=capture(lambda:adapter.evaluate(ROOT))

    # D consistent unit-id rename, plus raw P05 check
    binding=load("RAW_LIVE_WORK_BINDING.json")
    frozen=load("FROZEN_LANE_A_SPECIMEN.json")
    changed=copy.deepcopy(binding); changed["bounded_unit_id"]="sha256:"+"f"*64
    p05=raw.derive_p05(ROOT,frozen,changed)
    paths=[FIX/"RAW_LIVE_WORK_BINDING.json",FIX/"RAW_COMPLETION_CRITERION.json",FIX/"RAW_WORK_EVIDENCE.json",FIX/"RAW_BLOCKER_SCOPE.json"]
    originals=[x.read_text() for x in paths]
    try:
        for path,txt in zip(paths,originals):
            obj=json.loads(txt)
            if "bounded_unit_id" in obj: obj["bounded_unit_id"]="sha256:"+"f"*64
            path.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
        attempt=capture(lambda:adapter.evaluate(ROOT))
    finally:
        for path,txt in zip(paths,originals): path.write_text(txt)
    out["D"]={"p05_status":p05["status"],"p05_mismatches":p05["mismatches"],"adapter_attempt":attempt}

    # E no caller outcome surface
    sig=str(inspect.signature(adapter.evaluate))
    try:
        adapter.evaluate(ROOT, controller_receipt_outcome="ARBITRARY")
        e={"accepted":true}
    except TypeError as exc:
        e={"accepted":false,"error":str(exc)}
    out["E"]={"signature":sig,"caller_outcome_accepted":e["accepted"]}

    # F exact candidate producer bytes but no qualified runtime registry
    candidate=load("PRODUCER_CANDIDATES.json")
    binding=load("RAW_LIVE_WORK_BINDING.json")
    criterion=load("RAW_COMPLETION_CRITERION.json")
    evidence=load("RAW_WORK_EVIDENCE.json")
    p05clean=raw.derive_p05(ROOT,frozen,binding)
    p06clean=raw.derive_p06(ROOT,frozen,binding,criterion,evidence)
    f=p07.produce(ROOT,candidate,binding,p05clean,p06clean)
    out["F"]={"status":f["status"],"reason":f["reason"]}

    # G/H basis tamper
    for cell,name in [("G","P07_RELATION_BASIS_001.json"),("H","P08_RELATION_BASIS_001.json")]:
        p=FIX/name
        with mutate_json(p,lambda o:o.__setitem__("bounded_unit_id","sha256:"+"e"*64)):
            out[cell]=capture(lambda:adapter.evaluate(ROOT))

    # I controller drift
    p=ROOT/adapter.CONTROLLER_PATH
    with mutate_text(p,lambda s:s+"\n# qualification-drift\n"):
        out["I"]=capture(lambda:adapter.evaluate(ROOT))

    # J internal post-projection tamper is rejected by digest guard before controller
    contract=adapter._verify_contract(ROOT)
    derived=adapter._derive(ROOT,contract)
    derived["controller_input"]["receipt"]["outcome"]="ARBITRARY_MATCHED_OUTCOME"
    out["J"]=capture(lambda:adapter._invoke_atomic(ROOT,derived))

    # K source/projection separation
    k=adapter.evaluate(ROOT)
    out["K"]={
      "objects_differ":k["historical_claim_object"]!=k["controller_claim_projection"],
      "source_has_bounded_unit_id":"bounded_unit_id" in k["historical_claim_object"],
      "projection_has_bounded_unit_id":"bounded_unit_id" in k["controller_claim_projection"],
      "controller_result_has_historical_claim":"historical_claim" in k["controller_result"],
      "separate_returned_projection":k["controller_returned_claim_projection"]==k["controller_claim_projection"],
      "historical_claim_ref":k["historical_claim_ref"]
    }

    # L membrane
    l=adapter.evaluate(ROOT)
    out["L"]={
      "admissible":l["controller_result"]["admissible"],
      "selected_branch":l["controller_result"]["selected_branch"],
      "transition_executed":l["transition_executed"],
      "lane_mutation":l["lane_mutation"],
      "claim_mutation":l["claim_mutation"],
      "occupant_mutation":l["occupant_mutation"]
    }

    checks={
      "A":out["A"]["exact_controller"] and out["A"]["consulted"]==["P01","P02","P03","P04","P05","P06","P07","P08"] and out["A"]["admissible"] and out["A"]["selected_branch"]=="COMPLETE" and not out["A"]["transition_executed"],
      "B":out["B"]["status"]=="RAISED" and out["B"]["controller_calls"]==0,
      "C":out["C"]["status"]=="RAISED" and out["C"]["controller_calls"]==0,
      "D":out["D"]["p05_status"]=="DOES_NOT_MATCH" and "bounded_unit_id" in out["D"]["p05_mismatches"] and out["D"]["adapter_attempt"]["status"]=="RAISED" and out["D"]["adapter_attempt"]["controller_calls"]==0,
      "E":out["E"]["signature"]=="(repo_root: 'str | Path') -> 'dict[str, Any]'" and not out["E"]["caller_outcome_accepted"],
      "F":out["F"]["status"]=="NOT_ESTABLISHED",
      "G":out["G"]["status"]=="RAISED" and out["G"]["controller_calls"]==0,
      "H":out["H"]["status"]=="RAISED" and out["H"]["controller_calls"]==0,
      "I":out["I"]["status"]=="RAISED" and out["I"]["controller_calls"]==0,
      "J":out["J"]["status"]=="RAISED" and "PROJECTED_INPUT_DIGEST_MISMATCH_PRE_INVOKE" in out["J"]["error"] and out["J"]["controller_calls"]==0,
      "K":out["K"]["objects_differ"] and not out["K"]["source_has_bounded_unit_id"] and out["K"]["projection_has_bounded_unit_id"] and not out["K"]["controller_result_has_historical_claim"] and out["K"]["separate_returned_projection"],
      "L":out["L"]=={"admissible":True,"selected_branch":"COMPLETE","transition_executed":False,"lane_mutation":"NONE","claim_mutation":"NONE","occupant_mutation":"NONE"}
    }
    return {
      "object_type":"BOUNDED_ADAPTER_QUALIFICATION_EVIDENCE",
      "object_id":"LIVE_COMPLETION_ADAPTER_QUALIFICATION_001",
      "adapter_blob":adapter._blob(ROOT,"tools/live_completion_controller_adapter_v2.py"),
      "projection_contract_blob":adapter._blob(ROOT,"fixtures/live_completion_adapter_v0/PROJECTION_CONTRACT_001.json"),
      "controller_blob":adapter._blob(ROOT,adapter.CONTROLLER_PATH),
      "cells":out,
      "cell_checks":checks,
      "pass":all(checks.values()),
      "transition_executed":False,
      "live_lane_mutation":"NONE",
      "merge":"NONE"
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output")
    args=ap.parse_args()
    result=evaluate()
    data=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output: Path(args.output).write_text(data)
    else: print(data,end="")
    return 0 if result["pass"] else 1

if __name__=="__main__": raise SystemExit(main())
