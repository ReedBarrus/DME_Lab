#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import live_completion_raw_evaluator_v1 as raw
import live_unit_completion_standing_producer_v1 as p07
import live_completion_blocker_status_producer_v1 as p08

FIX = ROOT / "fixtures" / "live_completion_evidence_v1"


def load(name: str):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: str) -> str:
    proc = subprocess.run(["git", "-C", str(ROOT), "hash-object", path], capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def observe_exception(fn):
    try:
        value = fn()
    except raw.AdministrationInvalid as exc:
        return {"status": "ADMINISTRATION_INVALID", "reason": str(exc)}
    return {"status": "NO_EXCEPTION", "value": value}


def evaluate_candidate() -> dict[str, Any]:
    frozen=load("FROZEN_LANE_A_SPECIMEN.json")
    binding=load("RAW_LIVE_WORK_BINDING.json")
    criterion=load("RAW_COMPLETION_CRITERION.json")
    evidence=load("RAW_WORK_EVIDENCE.json")
    scope=load("RAW_BLOCKER_SCOPE.json")
    candidates=load("PRODUCER_CANDIDATES.json")

    p05=raw.derive_p05(ROOT,frozen,binding)
    p06=raw.derive_p06(ROOT,frozen,binding,criterion,evidence)
    p07_good=p07.candidate_produce(ROOT,candidates,binding,p05,p06)
    p08_clear=p08.candidate_produce(ROOT,candidates,frozen,binding,criterion,evidence,scope)

    cells={}
    cells["A"]={"P05":p05["status"],"P06":p06["status"]}
    bad_binding=copy.deepcopy(binding); bad_binding["claim_id"]="DIFFERENT-CLAIM"
    cells["B"]={"P05":raw.derive_p05(ROOT,frozen,bad_binding)["status"]}
    stale=copy.deepcopy(evidence); stale["lane_head"]=frozen["initial_work_commit"]
    cells["C"]=observe_exception(lambda: raw.derive_p06(ROOT,frozen,binding,criterion,stale))
    cells["D"]=raw.derive_p06(ROOT,frozen,binding,None,evidence)

    posthoc_semantics=copy.deepcopy(criterion)
    posthoc_semantics["allowed_mutation_paths"]=["docs/candidates/live_two_lane_trial_lane_a_v0/RESULT_OBSERVED_ONLY.md"]
    posthoc_semantics["required_final_artifacts"]=["docs/candidates/live_two_lane_trial_lane_a_v0/RESULT_OBSERVED_ONLY.md"]
    cells["K"]=observe_exception(lambda: raw.derive_p06(ROOT,frozen,binding,posthoc_semantics,evidence))

    renamed_binding=copy.deepcopy(binding)
    renamed_criterion=copy.deepcopy(criterion)
    renamed_evidence=copy.deepcopy(evidence)
    renamed_scope=copy.deepcopy(scope)
    renamed="sha256:"+"0"*64
    renamed_binding["bounded_unit_id"]=renamed
    renamed_criterion["bounded_unit_id"]=renamed
    renamed_evidence["bounded_unit_id"]=renamed
    renamed_scope["bounded_unit_id"]=renamed
    cells["L"]={"P05":raw.derive_p05(ROOT,frozen,renamed_binding)["status"]}

    cells["M"]={"P07":p07.produce(ROOT,{},binding,p05,p06)["status"]}

    bad_scope=copy.deepcopy(scope); bad_scope["blocker_classes"]=bad_scope["blocker_classes"][:-1]
    cells["G"]={"P08":p08.candidate_produce(ROOT,candidates,frozen,binding,criterion,evidence,bad_scope)["status"]}

    blocker_from_raw=p08.candidate_produce(ROOT,candidates,frozen,bad_binding,criterion,evidence,scope)
    cells["H"]={
        "P08":blocker_from_raw.get("relation",{}).get("standing"),
        "identity_blocker":blocker_from_raw.get("derived_evaluations",{}).get("WORK_UNIT_IDENTITY_MISMATCH"),
    }
    cells["I"]={
        "P08":p08_clear.get("relation",{}).get("standing"),
        "derived_evaluations":p08_clear.get("derived_evaluations"),
    }

    tampered_candidates=copy.deepcopy(candidates)
    tampered_candidates["producer_candidates"]["LIVE_UNIT_COMPLETION_STANDING_PRODUCER@v1"]["implementation_blob"]="0"*40
    p07_tampered=p07.candidate_produce(ROOT,tampered_candidates,binding,p05,p06)

    tampered_p08=copy.deepcopy(candidates)
    tampered_p08["producer_candidates"]["LIVE_COMPLETION_BLOCKER_STATUS_PRODUCER@v1"]["implementation_blob"]="0"*40
    p08_tampered=p08.candidate_produce(ROOT,tampered_p08,frozen,binding,criterion,evidence,scope)

    expected={
        "A": cells["A"]=={"P05":"MATCHES","P06":"SATISFIED"},
        "B": cells["B"]["P05"]=="DOES_NOT_MATCH",
        "C": cells["C"]=={"status":"ADMINISTRATION_INVALID","reason":"STALE_LIVE_BASIS"},
        "D": cells["D"].get("status")=="NOT_ESTABLISHED" and cells["D"].get("reason")=="MISSING_CRITERION",
        "G": cells["G"]["P08"]=="NOT_ESTABLISHED",
        "H": cells["H"]["P08"]=="FORBIDS_COMPLETION" and cells["H"]["identity_blocker"] is True,
        "I": cells["I"]["P08"]=="NONE_ESTABLISHED" and not any(cells["I"]["derived_evaluations"].values()),
        "K": cells["K"]=={"status":"ADMINISTRATION_INVALID","reason":"CRITERION_SEMANTICS_NOT_SOURCE_DERIVED"},
        "L": cells["L"]["P05"]=="DOES_NOT_MATCH",
        "M": cells["M"]["P07"]=="NOT_ESTABLISHED",
    }

    p07_pass=(
        p07_good.get("status")=="ESTABLISHED"
        and p07_good.get("relation",{}).get("standing")=="QUALIFIED"
        and p07_tampered.get("status")=="NOT_ESTABLISHED"
    )
    p08_pass=(
        p08_clear.get("status")=="ESTABLISHED"
        and p08_clear.get("relation",{}).get("standing")=="NONE_ESTABLISHED"
        and p08_tampered.get("status")=="NOT_ESTABLISHED"
        and cells["H"]["P08"]=="FORBIDS_COMPLETION"
    )

    result={
        "object_type":"LIVE_COMPLETION_EVIDENCE_REPAIR_CANDIDATE_QUALIFICATION",
        "object_id":"LIVE_COMPLETION_EVIDENCE_001-REPAIR-V1-CANDIDATE-QUALIFICATION-001",
        "base":"f36261e17790b853a91c81bc2f7d0e63e8ee8436",
        "frozen_lane_a":frozen["lane_a_head"],
        "frozen_lane_b":frozen["lane_b_head"],
        "implementation_blobs":{
            "raw_evaluator":git_blob("tools/live_completion_raw_evaluator_v1.py"),
            "p07_producer":git_blob("tools/live_unit_completion_standing_producer_v1.py"),
            "p08_producer":git_blob("tools/live_completion_blocker_status_producer_v1.py"),
        },
        "fixture_sha256":{name:sha256_file(FIX/name) for name in [
            "FROZEN_LANE_A_SPECIMEN.json","RAW_LIVE_WORK_BINDING.json","RAW_COMPLETION_CRITERION.json",
            "RAW_WORK_EVIDENCE.json","RAW_BLOCKER_SCOPE.json","PRODUCER_CANDIDATES.json"
        ]},
        "raw_derivation":{"P05":p05,"P06":p06},
        "candidate_producer_qualification":{
            "P07":{"pass":p07_pass,"positive":p07_good,"tampered":p07_tampered},
            "P08":{"pass":p08_pass,"clear":p08_clear,"tampered":p08_tampered},
        },
        "cells":cells,
        "cell_checks":expected,
        "pass":all(expected.values()) and p07_pass and p08_pass,
        "lifecycle_execution":"NONE",
        "lane_mutation":"NONE",
        "merge":"NONE",
    }
    return result


def main(argv=None)->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    args=ap.parse_args(argv)
    result=evaluate_candidate()
    data=pretty_bytes(result)
    if args.output:
        Path(args.output).write_bytes(data)
    else:
        print(data.decode(),end="")
    return 0 if result["pass"] else 1


if __name__=="__main__":
    raise SystemExit(main())
