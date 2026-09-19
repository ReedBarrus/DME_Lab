from __future__ import annotations

import hashlib
import json
from pathlib import Path

from qualification_wrong_apparatus import parse_manifest, route


ROOT = Path(__file__).resolve().parent
A_PATH = ROOT / "A_manifest.json"
B_PATH = ROOT / "B_manifest.json"


def _observe(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    selected = route(parse_manifest(raw), "NODE_01", "NODE_04")
    return {"node_path": list(selected.node_path), "hop_count": len(selected.edge_path)}


a = _observe(A_PATH)
b = _observe(B_PATH)
raw = {
    "schema_version": "atlas_route_selection_raw_observation_v0",
    "apparatus_invoked": "parse_manifest + route",
    "source_node_id": "NODE_01",
    "target_node_id": "NODE_04",
    "A_manifest_sha256": hashlib.sha256(A_PATH.read_bytes()).hexdigest(),
    "B_manifest_sha256": hashlib.sha256(B_PATH.read_bytes()).hexdigest(),
    "A_SELECTED_NODE_PATH": a["node_path"],
    "A_HOP_COUNT": a["hop_count"],
    "B_SELECTED_NODE_PATH": b["node_path"],
    "B_HOP_COUNT": b["hop_count"],
}
result = {
    "schema_version": "atlas_route_selection_mechanical_result_v0",
    "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
    "verdict": "PASS" if a["node_path"] == b["node_path"] else "FRACTURE",
}
print(json.dumps({"raw_observation": raw, "mechanical_result": result}, sort_keys=True))
