from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
A_PATH = ROOT / "A_manifest.json"
B_PATH = ROOT / "B_manifest.json"
APPARATUS_PATH = ROOT / "qualification_apparatus.py"


def _load_apparatus():
    spec = importlib.util.spec_from_file_location("qualification_apparatus", APPARATUS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load qualification apparatus")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


APPARATUS = _load_apparatus()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _observe(path: Path) -> dict:
    manifest = APPARATUS.parse_manifest(_load(path))
    selected = APPARATUS.route(manifest, "NODE_01", "NODE_04")
    return {
        "node_path": list(selected.node_path),
        "hop_count": len(selected.edge_path),
    }


def main() -> None:
    a = _observe(A_PATH)
    b = _observe(B_PATH)
    raw = {
        "schema_version": "atlas_route_selection_raw_observation_v0",
        "apparatus_invoked": "parse_manifest + route",
        "source_node_id": "NODE_01",
        "target_node_id": "NODE_04",
        "A_manifest_sha256": _sha256(A_PATH),
        "B_manifest_sha256": _sha256(B_PATH),
        "A_SELECTED_NODE_PATH": a["node_path"],
        "A_HOP_COUNT": a["hop_count"],
        "B_SELECTED_NODE_PATH": b["node_path"],
        "B_HOP_COUNT": b["hop_count"],
    }
    result = {
        "schema_version": "atlas_route_selection_mechanical_result_v0",
        "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
        "verdict": (
            "PASS"
            if a["node_path"] == b["node_path"]
            else "FRACTURE"
        ),
    }
    print(json.dumps({"raw_observation": raw, "mechanical_result": result}, sort_keys=True))


if __name__ == "__main__":
    main()
