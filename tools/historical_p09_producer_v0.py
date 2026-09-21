#!/usr/bin/env python3
from __future__ import annotations
import hashlib
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
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise P09Error("root must be object")
    return value

def _sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def _invalid(cell_id: str, reason: str, observed_scope_identity: str | None = None) -> dict[str, Any]:
    result = {
        "status": "ADMINISTRATION_INVALID",
        "relation_type": RELATION_TYPE,
        "standing": None,
        "basis_ref": f"fixture://{cell_id}",
        "producer": PRODUCER,
        "version": VERSION,
        "reason": reason,
    }
    if observed_scope_identity is not None:
        result["observed_scope_identity"] = observed_scope_identity
    return result

def evaluate_cell(cell_id: str, cell: dict[str, Any]) -> dict[str, Any]:
    if set(cell) != {"scope_basis_identity", "scope", "events"}:
        raise P09Error("cell fields must be exact")
    pinned_scope_identity = cell["scope_basis_identity"]
    scope = cell["scope"]
    events = cell["events"]
    if not isinstance(pinned_scope_identity, str) or not pinned_scope_identity.startswith("sha256:"):
        raise P09Error("scope_basis_identity malformed")
    if not isinstance(scope, dict) or set(scope) != {"scope_id", "unit_ids", "event_count", "event_log_sha256"}:
        raise P09Error("scope fields must be exact")
    if not isinstance(events, list):
        raise P09Error("events must be list")
    scope_id = scope["scope_id"]
    units = scope["unit_ids"]
    if not isinstance(scope_id, str) or not scope_id:
        raise P09Error("scope_id malformed")
    if not isinstance(units, list) or not units or len(units) != len(set(units)):
        raise P09Error("unit_ids must be non-empty unique list")
    if any(not isinstance(u, str) or not u for u in units):
        raise P09Error("unit_ids malformed")
    if not isinstance(scope["event_count"], int) or scope["event_count"] < 0:
        raise P09Error("event_count malformed")
    if not isinstance(scope["event_log_sha256"], str) or not scope["event_log_sha256"].startswith("sha256:"):
        raise P09Error("event_log_sha256 malformed")
    observed_scope_identity = _sha256_json({
        "scope_id": scope_id,
        "unit_ids": sorted(units),
        "event_count": scope["event_count"],
        "event_log_sha256": scope["event_log_sha256"],
    })
    if observed_scope_identity != pinned_scope_identity:
        return _invalid(cell_id, "SCOPE_BASIS_IDENTITY_MISMATCH", observed_scope_identity)
    if scope["event_count"] != len(events):
        return _invalid(cell_id, "EVENT_COUNT_MISMATCH", observed_scope_identity)
    if scope["event_log_sha256"] != _sha256_json(events):
        return _invalid(cell_id, "EVENT_LOG_IDENTITY_MISMATCH", observed_scope_identity)
    state = {u: {"latest_start": None, "latest_terminal": None, "latest_independent": None} for u in units}
    expected_index = 1
    for event in events:
        if not isinstance(event, dict) or set(event) != {"scope_id", "unit_id", "event_index", "event_type"}:
            raise P09Error("event fields must be exact")
        if event["scope_id"] != scope_id:
            return _invalid(cell_id, "EVENT_SCOPE_MISMATCH", observed_scope_identity)
        u = event["unit_id"]
        et = event["event_type"]
        idx = event["event_index"]
        if u not in state:
            return _invalid(cell_id, "EVENT_UNIT_OUTSIDE_SCOPE", observed_scope_identity)
        if et not in EVENTS:
            raise P09Error("unknown event_type")
        if not isinstance(idx, int) or idx != expected_index:
            return _invalid(cell_id, "EVENT_ORDER_NOT_CONTIGUOUS", observed_scope_identity)
        expected_index += 1
        if et == "EFFECT_BEARING_UNIT_START":
            state[u]["latest_start"] = idx
        elif et == "TERMINAL_RECEIPT":
            state[u]["latest_terminal"] = idx
        elif et == "OWNERSHIP_INDEPENDENT_CHECKPOINT":
            state[u]["latest_independent"] = idx
    unfinished = []
    for u, posture in state.items():
        start = posture["latest_start"]
        if start is None:
            continue
        closing = max(posture["latest_terminal"] if posture["latest_terminal"] is not None else -1, posture["latest_independent"] if posture["latest_independent"] is not None else -1)
        if closing <= start:
            unfinished.append(u)
    standing = "UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP" if unfinished else "NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP"
    return {
        "status": "VALID",
        "relation_type": RELATION_TYPE,
        "standing": standing,
        "basis_ref": f"scope-basis://{pinned_scope_identity}",
        "producer": PRODUCER,
        "version": VERSION,
        "scope_basis_identity": pinned_scope_identity,
        "unfinished_units": unfinished,
    }

def qualify(fixtures: dict[str, Any]) -> dict[str, Any]:
    if fixtures.get("schema") != "historical_p09_raw_fixtures_v0":
        raise P09Error("wrong fixture schema")
    cells = fixtures.get("cells")
    if not isinstance(cells, dict):
        raise P09Error("cells must be object")
    return {cid: evaluate_cell(cid, cell) for cid, cell in cells.items()}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("fixtures")
    args = p.parse_args()
    print(json.dumps(qualify(load_json(args.fixtures)), indent=2, sort_keys=True))
