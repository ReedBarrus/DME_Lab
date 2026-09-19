from __future__ import annotations

import hashlib
import json
from pathlib import Path

from lab.ops.candidates.atlas_five_node_v0.atlas import parse_manifest, route

ROOT = Path(__file__).resolve().parent
A_PATH = ROOT / "A_manifest.json"
B_PATH = ROOT / "B_manifest.json"
SOURCE_NODE_ID = "NODE_01"
TARGET_NODE_ID = "NODE_04"
EXPECTED_ENDPOINT_PAIRS = {
    ("NODE_01", "NODE_02"),
    ("NODE_01", "NODE_03"),
    ("NODE_02", "NODE_04"),
    ("NODE_03", "NODE_04"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path.name}: manifest root must be an object")
    return value


def _endpoint_pairs(raw: dict) -> set[tuple[str, str]]:
    return {
        (edge["source_node_id"], edge["target_node_id"])
        for edge in raw["edges"]
    }


def _validate_matched_pair(a: dict, b: dict) -> None:
    if a["schema_version"] != b["schema_version"]:
        raise SystemExit("administration invalid: schema_version differs")
    if a["manifest_id"] != b["manifest_id"]:
        raise SystemExit("administration invalid: manifest_id differs")
    if a["nodes"] != b["nodes"]:
        raise SystemExit("administration invalid: node records differ")
    if len(a["nodes"]) != 5:
        raise SystemExit("administration invalid: five-node cardinality lost")
    if len(a["edges"]) != len(b["edges"]):
        raise SystemExit("administration invalid: edge cardinality differs")
    if _endpoint_pairs(a) != EXPECTED_ENDPOINT_PAIRS:
        raise SystemExit("administration invalid: A endpoint relation differs")
    if _endpoint_pairs(b) != EXPECTED_ENDPOINT_PAIRS:
        raise SystemExit("administration invalid: B endpoint relation differs")

    for index, (edge_a, edge_b) in enumerate(zip(a["edges"], b["edges"])):
        for field in (
            "source_node_id",
            "target_node_id",
            "transition_kind",
            "authority_effect",
            "execution_effect",
        ):
            if edge_a[field] != edge_b[field]:
                raise SystemExit(
                    f"administration invalid: edges[{index}].{field} differs"
                )

    if a["edges"][0]["edge_id"] != "EDGE_A" or a["edges"][1]["edge_id"] != "EDGE_B":
        raise SystemExit("administration invalid: A first-hop labels not frozen")
    if b["edges"][0]["edge_id"] != "EDGE_B" or b["edges"][1]["edge_id"] != "EDGE_A":
        raise SystemExit("administration invalid: B first-hop labels not frozen")
    if a["edges"][2:] != b["edges"][2:]:
        raise SystemExit("administration invalid: non-manipulated edges differ")


def _observe(raw: dict) -> dict:
    manifest = parse_manifest(raw)
    selected = route(manifest, SOURCE_NODE_ID, TARGET_NODE_ID)
    node_path = list(selected.node_path)
    hop_count = len(selected.edge_path)
    used_pairs = set(zip(node_path, node_path[1:]))

    valid = (
        node_path[0] == SOURCE_NODE_ID
        and node_path[-1] == TARGET_NODE_ID
        and hop_count == 2
        and used_pairs.issubset(EXPECTED_ENDPOINT_PAIRS)
    )
    if not valid:
        raise SystemExit("administration invalid: selected route failed frozen validity checks")

    return {
        "selected_node_path": node_path,
        "hop_count": hop_count,
    }


def main() -> None:
    a_raw = _load(A_PATH)
    b_raw = _load(B_PATH)
    _validate_matched_pair(a_raw, b_raw)

    a_observation = _observe(a_raw)
    b_observation = _observe(b_raw)

    raw_observation = {
        "schema_version": "atlas_route_selection_raw_observation_v0",
        "apparatus_invoked": "parse_manifest + route",
        "source_node_id": SOURCE_NODE_ID,
        "target_node_id": TARGET_NODE_ID,
        "A_manifest_sha256": _sha256(A_PATH),
        "B_manifest_sha256": _sha256(B_PATH),
        "A_SELECTED_NODE_PATH": a_observation["selected_node_path"],
        "A_HOP_COUNT": a_observation["hop_count"],
        "B_SELECTED_NODE_PATH": b_observation["selected_node_path"],
        "B_HOP_COUNT": b_observation["hop_count"],
    }

    result = {
        "schema_version": "atlas_route_selection_mechanical_result_v0",
        "criterion": "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
        "verdict": (
            "PASS"
            if a_observation["selected_node_path"] == b_observation["selected_node_path"]
            else "FRACTURE"
        ),
    }

    print(json.dumps({"raw_observation": raw_observation, "mechanical_result": result}, sort_keys=True))


if __name__ == "__main__":
    main()
