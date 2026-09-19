from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
A_PATH = ROOT / "A_manifest.json"
B_PATH = ROOT / "B_manifest.json"


raw = {
    "schema_version": "atlas_route_selection_raw_observation_v0",
    "apparatus_invoked": "parse_manifest + route",
    "source_node_id": "NODE_01",
    "target_node_id": "NODE_04",
    "A_manifest_sha256": hashlib.sha256(A_PATH.read_bytes()).hexdigest(),
    "B_manifest_sha256": hashlib.sha256(B_PATH.read_bytes()).hexdigest(),
    "A_SELECTED_NODE_PATH": ["NODE_01", "NODE_02", "NODE_04"],
    "A_HOP_COUNT": 2,
    "B_SELECTED_NODE_PATH": ["NODE_01", "NODE_03", "NODE_04"],
    "B_HOP_COUNT": 2,
}
result = {
    "schema_version": "atlas_route_selection_mechanical_result_v0",
    "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
    "verdict": "FRACTURE",
}
print(json.dumps({"raw_observation": raw, "mechanical_result": result}, sort_keys=True))
