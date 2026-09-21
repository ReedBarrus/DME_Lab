#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

RELATION_TYPE = "ACTIVE_OWNERSHIP_EFFECT_STATUS"
PRODUCER = "HISTORICAL_P09_PRODUCER"
VERSION = "v0"
EVENTS = {
    "EFFECT_BEARING_UNIT_START",
    "TERMINAL_RECEIPT",
    "OWNERSHIP_INDEPENDENT_CHECKPOINT",
}

class P09Error(RuntimeError):
    pass

def load_json(path: str | Path) -> dict[str, Any]:
    value=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value,dict):
        raise P09Error("root must be object")
    return value

def evaluate_cell(cell_id: str, cell: dict[str, Any]) -> dict[str, Any]:
    if set(cell) != {"closed_scope","unit_ids","events"}:
        raise P09Error("cell fields must be exact")
    units=cell["unit_ids"]
    events=cell["events"]
    if not isinstance(units,list) or not units or len(units)!=len(set(units)):
        raise P09Error("unit_ids must be non-empty unique list")
    if any(not isinstance(u,str) or not u for u in units):
        raise P09Error("unit_ids malformed")
    if not isinstance(events,list):
        raise P09Error("events must be list")
    if cell["closed_scope"] is not True:
        return {
            "status":"ADMINISTRATION_INVALID",
            "relation_type":RELATION_TYPE,
            "standing":None,
            "basis_ref":f"fixture://{cell_id}",
            "producer":PRODUCER,
            "version":VERSION,
            "reason":"SCOPE_NOT_CLOSED",
        }
    state={u:{"started":False,"terminal":False,"independent":False} for u in units}
    for event in events:
        if not isinstance(event,dict) or set(event)!={"unit_id","event_type"}:
            raise P09Error("event fields must be exact")
        u=event["unit_id"]; et=event["event_type"]
        if u not in state:
            raise P09Error("event references unit outside closed scope")
        if et not in EVENTS:
            raise P09Error("unknown event_type")
        if et=="EFFECT_BEARING_UNIT_START":
            state[u]["started"]=True
        elif et=="TERMINAL_RECEIPT":
            state[u]["terminal"]=True
        elif et=="OWNERSHIP_INDEPENDENT_CHECKPOINT":
            state[u]["independent"]=True
    unfinished=[
        u for u,s in state.items()
        if s["started"] and not s["terminal"] and not s["independent"]
    ]
    standing=(
        "UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP"
        if unfinished else
        "NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP"
    )
    return {
        "status":"VALID",
        "relation_type":RELATION_TYPE,
        "standing":standing,
        "basis_ref":f"fixture://{cell_id}",
        "producer":PRODUCER,
        "version":VERSION,
        "unfinished_units":unfinished,
    }

def qualify(fixtures: dict[str, Any]) -> dict[str, Any]:
    if fixtures.get("schema")!="historical_p09_raw_fixtures_v0":
        raise P09Error("wrong fixture schema")
    cells=fixtures.get("cells")
    if not isinstance(cells,dict):
        raise P09Error("cells must be object")
    return {cid:evaluate_cell(cid,cell) for cid,cell in cells.items()}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("fixtures")
    args=p.parse_args()
    print(json.dumps(qualify(load_json(args.fixtures)),indent=2,sort_keys=True))
