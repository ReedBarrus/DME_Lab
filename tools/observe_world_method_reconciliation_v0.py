#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from src.control.world_method_reconciliation_v0 import build_world_method_reconciliation

OUT=ROOT/"world_method_reconciliation_v0_observation.json"
SOURCE_WITNESS=ROOT/"materialized_settlement_consequence_reconciliation_observation.json"

def git(*args):
    return subprocess.run(
        ["git","-C",str(ROOT),*args],
        capture_output=True,text=True,check=True,
    ).stdout.strip()

def build(source_id,source_identity,world,method):
    return build_world_method_reconciliation(
        source_reconciliation_id=source_id,
        source_reconciliation_identity_sha256=source_identity,
        world_posture_change=world,
        world_evidence_refs=[f"fixture://world/{world.lower()}"],
        cognitive_method_change=method,
        method_evidence_refs=[f"fixture://method/{method.lower()}"],
    )

def main():
    if OUT.exists():
        raise SystemExit("remove existing world_method_reconciliation_v0_observation.json first")

    predecessor=json.loads(SOURCE_WITNESS.read_text(encoding="utf-8"))
    source_id=predecessor["matched"]["composition_id"]
    source_identity=predecessor["matched"]["reconciliation_identity"]

    cases={
        "WORLD_ONLY":build(source_id,source_identity,"CHANGED","UNCHANGED"),
        "METHOD_ONLY":build(source_id,source_identity,"UNCHANGED","CHANGED"),
        "BOTH":build(source_id,source_identity,"CHANGED","CHANGED"),
        "NEITHER":build(source_id,source_identity,"UNCHANGED","UNCHANGED"),
        "WORLD_UNRESOLVED":build(source_id,source_identity,"UNRESOLVED","UNCHANGED"),
        "METHOD_UNRESOLVED":build(source_id,source_identity,"UNCHANGED","UNRESOLVED"),
    }

    ids=[x["world_method_reconciliation_id"] for x in cases.values()]
    effects=(
        "causal_attribution_effect","gap_selection_effect",
        "work_justification_effect","planning_effect",
        "method_capitalization_effect","policy_mutation_effect",
        "authority_effect","execution_effect","scientific_standing_effect",
    )

    assertions={
        "predecessor_witness_matched_consequence": predecessor["assertions"]["matched_consequence_satisfies"] is True,
        "exact_source_composition_bound": all(x["source_reconciliation_id"]==source_id for x in cases.values()),
        "exact_source_state_identity_bound": all(x["source_reconciliation_identity_sha256"]==source_identity for x in cases.values()),
        "world_only_preserved": cases["WORLD_ONLY"]["world_axis"]["posture_change"]=="CHANGED" and cases["WORLD_ONLY"]["method_axis"]["cognitive_method_change"]=="UNCHANGED",
        "method_only_preserved": cases["METHOD_ONLY"]["world_axis"]["posture_change"]=="UNCHANGED" and cases["METHOD_ONLY"]["method_axis"]["cognitive_method_change"]=="CHANGED",
        "both_preserved": cases["BOTH"]["world_axis"]["posture_change"]=="CHANGED" and cases["BOTH"]["method_axis"]["cognitive_method_change"]=="CHANGED",
        "neither_preserved": cases["NEITHER"]["world_axis"]["posture_change"]=="UNCHANGED" and cases["NEITHER"]["method_axis"]["cognitive_method_change"]=="UNCHANGED",
        "unresolved_axes_remain_explicit": cases["WORLD_UNRESOLVED"]["world_axis"]["posture_change"]=="UNRESOLVED" and cases["METHOD_UNRESOLVED"]["method_axis"]["cognitive_method_change"]=="UNRESOLVED",
        "all_case_identities_distinct": len(ids)==len(set(ids)),
        "fixed_inputs_deterministic": cases["WORLD_ONLY"]==build(source_id,source_identity,"CHANGED","UNCHANGED"),
        "no_causal_learning_or_consequence_effects": all(all(x[e]=="NONE" for e in effects) for x in cases.values()),
    }

    obs={
        "object_type":"WORLD_METHOD_RECONCILIATION_V0_OBSERVATION",
        "repo_head":git("rev-parse","HEAD"),
        "campaign_id":"WORLD_METHOD_RECONCILIATION_001",
        "gap_id":"G4_WORLD_METHOD_RECONCILIATION_FORK",
        "source_witness":{
            "path":"materialized_settlement_consequence_reconciliation_observation.json",
            "blob_note":"repository-frozen predecessor witness",
            "composition_id":source_id,
            "reconciliation_identity":source_identity,
        },
        "cases":cases,
        "assertions":assertions,
        "all_assertions_pass":all(assertions.values()),
        "claim_ceiling":"One exact predecessor reconciliation identity can carry independently supplied world-posture-change and cognitive-method-change axes across WORLD_ONLY, METHOD_ONLY, BOTH, NEITHER, and explicit UNRESOLVED cases. No causal attribution, method improvement or capitalization, policy mutation, gap discovery, work justification, planning, authority, execution, or scientific standing is created.",
        "stopped":"YES",
    }

    data=(json.dumps(obs,indent=2)+"\n").encode()
    OUT.write_bytes(data)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"[OK] all_assertions_pass {obs['all_assertions_pass']}")
    print(f"[OK] world_only_preserved {assertions['world_only_preserved']}")
    print(f"[OK] method_only_preserved {assertions['method_only_preserved']}")
    print(f"[OK] unresolved_axes_remain_explicit {assertions['unresolved_axes_remain_explicit']}")
    return 0 if obs["all_assertions_pass"] else 1

if __name__=="__main__":
    raise SystemExit(main())
