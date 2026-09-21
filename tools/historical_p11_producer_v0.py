#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

RELATION_TYPE = "REFERENCE_RETENTION_STATUS"
PRODUCER = "HISTORICAL_P11_PRODUCER"
VERSION = "v0"

class P11Error(RuntimeError):
    pass

def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise P11Error("root must be object")
    return value

def _sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def reference_set_identity(ref_ids: list[str]) -> str:
    if len(ref_ids) != len(set(ref_ids)):
        raise P11Error("duplicate ref identity")
    return _sha256_json(sorted(ref_ids))

def _invalid(cell_id: str, reason: str, observed_set_identity: str | None = None) -> dict[str, Any]:
    result = {
        "status": "ADMINISTRATION_INVALID",
        "relation_type": RELATION_TYPE,
        "standing": None,
        "basis_ref": f"fixture://{cell_id}",
        "producer": PRODUCER,
        "version": VERSION,
        "reason": reason,
    }
    if observed_set_identity is not None:
        result["observed_set_identity"] = observed_set_identity
    return result

def evaluate_cell(cell_id: str, cell: dict[str, Any]) -> dict[str, Any]:
    required = {
        "p10_set_identity",
        "required_refs",
        "carriers",
        "retrieval_edges",
        "release_delete_carrier_ids",
    }
    if set(cell) != required:
        raise P11Error("cell fields must be exact")

    p10_set_identity = cell["p10_set_identity"]
    refs = cell["required_refs"]
    carriers = cell["carriers"]
    edges = cell["retrieval_edges"]
    deleted = cell["release_delete_carrier_ids"]

    if not isinstance(p10_set_identity, str) or not p10_set_identity.startswith("sha256:"):
        raise P11Error("p10_set_identity malformed")
    if not isinstance(refs, list) or not refs:
        raise P11Error("required_refs must be non-empty list")
    if not isinstance(carriers, list) or not isinstance(edges, list) or not isinstance(deleted, list):
        raise P11Error("carrier topology fields must be lists")

    seen_refs = set()
    normalized_ref_ids = []
    for r in refs:
        if not isinstance(r, dict) or set(r) != {"ref_id", "carrier_id", "content_id"}:
            raise P11Error("required ref fields must be exact")
        rid = r["ref_id"]
        if not isinstance(rid, str) or not rid:
            raise P11Error("ref_id malformed")
        if rid in seen_refs:
            return _invalid(cell_id, "DUPLICATE_REQUIRED_REF")
        seen_refs.add(rid)
        normalized_ref_ids.append(rid)

    observed_set_identity = reference_set_identity(normalized_ref_ids)
    if observed_set_identity != p10_set_identity:
        return _invalid(cell_id, "P10_SET_IDENTITY_MISMATCH", observed_set_identity)

    carrier_map = {}
    for c in carriers:
        if not isinstance(c, dict) or set(c) != {"carrier_id", "content_id"}:
            raise P11Error("carrier fields must be exact")
        if c["carrier_id"] in carrier_map:
            raise P11Error("duplicate carrier_id")
        carrier_map[c["carrier_id"]] = c["content_id"]

    edge_set = set()
    for e in edges:
        if not isinstance(e, dict) or set(e) != {"ref_id", "carrier_id"}:
            raise P11Error("retrieval edge fields must be exact")
        edge_set.add((e["ref_id"], e["carrier_id"]))

    if len(deleted) != len(set(deleted)):
        raise P11Error("duplicate deleted carrier ids")

    failures = []
    for r in refs:
        rid = r["ref_id"]
        cid = r["carrier_id"]
        content = r["content_id"]
        if cid not in carrier_map:
            failures.append({"ref_id": rid, "reason": "CARRIER_ABSENT"})
            continue
        if carrier_map[cid] != content:
            failures.append({"ref_id": rid, "reason": "CONTENT_IDENTITY_MISMATCH"})
        if (rid, cid) not in edge_set:
            failures.append({"ref_id": rid, "reason": "RETRIEVAL_EDGE_ABSENT"})
        if cid in deleted:
            failures.append({"ref_id": rid, "reason": "CARRIER_DELETED_BY_RELEASE"})

    return {
        "status": "VALID",
        "relation_type": RELATION_TYPE,
        "standing": "NOT_RETAINABLE" if failures else "RETAINABLE",
        "basis_ref": f"p10-set://{p10_set_identity}",
        "producer": PRODUCER,
        "version": VERSION,
        "p10_set_identity": p10_set_identity,
        "failures": failures,
    }

def qualify(fixtures: dict[str, Any]) -> dict[str, Any]:
    if fixtures.get("schema") != "historical_p11_raw_fixtures_v0":
        raise P11Error("wrong fixture schema")
    cells = fixtures.get("cells")
    if not isinstance(cells, dict):
        raise P11Error("cells must be object")
    return {cid: evaluate_cell(cid, cell) for cid, cell in cells.items()}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("fixtures")
    args = p.parse_args()
    print(json.dumps(qualify(load_json(args.fixtures)), indent=2, sort_keys=True))
