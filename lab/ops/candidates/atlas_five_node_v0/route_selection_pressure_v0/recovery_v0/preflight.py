from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "recovery_contract_v0.json"

EXPECTED_ENDPOINT_PAIRS = {
    ("NODE_01", "NODE_02"),
    ("NODE_01", "NODE_03"),
    ("NODE_02", "NODE_04"),
    ("NODE_03", "NODE_04"),
}

FORBIDDEN_KEYS = {
    "expected_vector",
    "expected_selected_path",
    "expected_node_path",
    "expected_verdict",
    "expected_mechanical_verdict",
}


class PreflightError(RuntimeError):
    pass


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PreflightError(f"JSON root is not an object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PreflightError(message)


def verify_file_identity(spec: dict[str, Any], label: str) -> None:
    path = ROOT / spec["path"]
    require(path.exists(), f"{label}: missing {path}")
    require(git_blob(path) == spec["blob_sha1"], f"{label}: git blob mismatch")
    if "sha256" in spec:
        require(sha256(path) == spec["sha256"], f"{label}: sha256 mismatch")


def endpoint_pairs(raw: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (edge["source_node_id"], edge["target_node_id"])
        for edge in raw["edges"]
    }


def walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def path_absent_at_commit(commit: str, path: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    return completed.returncode != 0


def main() -> int:
    contract = load_json(CONTRACT)
    checks: list[str] = []

    require(
        contract["schema_version"] == "atlas_route_selection_recovery_contract_v0",
        "contract schema mismatch",
    )
    require(contract["pressure_id"] == "ATLAS_ROUTE_SELECTION_001", "pressure id mismatch")
    checks.append("contract_schema_and_pressure")

    for label in (
        "atlas",
        "producer",
        "harness",
        "child_wrapper",
        "qualification_test",
        "original_contract",
        "second_wound_evidence",
    ):
        verify_file_identity(contract["frozen_identities"][label], label)
    checks.append("frozen_mechanical_identities")

    a_spec = contract["recovery_cells"]["A2"]
    b_spec = contract["recovery_cells"]["B2"]
    verify_file_identity(a_spec, "A2")
    verify_file_identity(b_spec, "B2")
    require(a_spec["blob_sha1"] != b_spec["blob_sha1"], "A2/B2 blobs must differ")
    require(
        a_spec["blob_sha1"] not in {
            contract["historical_cells"]["A"]["blob_sha1"],
            contract["historical_cells"]["B"]["blob_sha1"],
        },
        "A2 reuses historical scientific cell bytes",
    )
    require(
        b_spec["blob_sha1"] not in {
            contract["historical_cells"]["A"]["blob_sha1"],
            contract["historical_cells"]["B"]["blob_sha1"],
        },
        "B2 reuses historical scientific cell bytes",
    )
    checks.append("fresh_cell_byte_identities")

    freshness_basis = contract["freshness_basis_commit"]
    require(
        path_absent_at_commit(freshness_basis, a_spec["path"]),
        "A2 path already existed at freshness basis",
    )
    require(
        path_absent_at_commit(freshness_basis, b_spec["path"]),
        "B2 path already existed at freshness basis",
    )
    checks.append("fresh_cell_paths_absent_at_basis")

    a = load_json(ROOT / a_spec["path"])
    b = load_json(ROOT / b_spec["path"])

    require(a["schema_version"] == b["schema_version"] == "atlas_five_node_manifest_v0", "cell schema mismatch")
    require(a["manifest_id"] == b["manifest_id"] == "ATLAS_ROUTE_SELECTION_RECOVERY_001", "recovery manifest id mismatch")
    require(a["nodes"] == b["nodes"], "A2/B2 node records differ")
    require(len(a["nodes"]) == 5, "five-node cardinality lost")
    for node in a["nodes"]:
        require(node["role_id"] is None, "role binding entered recovery cell")
        require(node["binding_state"] == "UNBOUND", "binding state changed")
        require(node["runtime_state"] == "NOT_INSTANTIATED", "runtime instantiated")
        require(node["authority_ref"] is None, "authority binding entered recovery cell")
    checks.append("node_geometry_and_nonbinding")

    require(endpoint_pairs(a) == EXPECTED_ENDPOINT_PAIRS, "A2 endpoint relation changed")
    require(endpoint_pairs(b) == EXPECTED_ENDPOINT_PAIRS, "B2 endpoint relation changed")
    require(len(a["edges"]) == len(b["edges"]) == 4, "edge cardinality changed")
    for index, (ea, eb) in enumerate(zip(a["edges"], b["edges"])):
        for field in (
            "source_node_id",
            "target_node_id",
            "transition_kind",
            "authority_effect",
            "execution_effect",
        ):
            require(ea[field] == eb[field], f"edges[{index}].{field} differs")
        require(ea["transition_kind"] == "TRANSFER_ONLY", "transition kind changed")
        require(ea["authority_effect"] == "NONE", "authority effect changed")
        require(ea["execution_effect"] == "NONE", "execution effect changed")
    require(a["edges"][0]["edge_id"] == "EDGE_A", "A2 first edge id not EDGE_A")
    require(a["edges"][1]["edge_id"] == "EDGE_B", "A2 second edge id not EDGE_B")
    require(b["edges"][0]["edge_id"] == "EDGE_B", "B2 first edge id not EDGE_B")
    require(b["edges"][1]["edge_id"] == "EDGE_A", "B2 second edge id not EDGE_A")
    require(a["edges"][2:] == b["edges"][2:], "non-manipulated edges differ")
    checks.append("matched_route_selection_pressure_geometry")

    all_keys = set(walk_keys(contract))
    require(not (all_keys & FORBIDDEN_KEYS), "forbidden expected-result key present")
    require(
        contract["observation_surface"] == [
            "A_SELECTED_NODE_PATH",
            "A_HOP_COUNT",
            "B_SELECTED_NODE_PATH",
            "B_HOP_COUNT",
        ],
        "observation surface changed",
    )
    require(
        contract["mechanical_criterion"] == "A_SELECTED_NODE_PATH == B_SELECTED_NODE_PATH",
        "mechanical criterion changed",
    )
    checks.append("no_expected_vector_and_frozen_scoring_surface")

    qual = contract["qualification_witness"]
    successful = qual["successful_witness"]
    require(successful["run_id"] == 35461430111, "qualification witness run mismatch")
    require(successful["job_id"] == 105945884236, "qualification witness job mismatch")
    require(successful["conclusion"] == "success", "qualification witness not successful")
    verify_file_identity(qual["receipt"], "qualification witness receipt")
    checks.append("qualified_harness_witness_bound")

    authority = contract["authority"]
    require(authority["contract_freeze"] == "AUTHORIZED_BY_USER", "contract freeze authority missing")
    require(authority["preflight"] == "AUTHORIZED_BY_USER", "preflight authority missing")
    require(authority["scientific_realization"] == "NONE", "scientific realization authority minted")
    require(authority["scientific_promotion"] == "NONE", "scientific promotion authority minted")
    require(authority["merge_to_main"] == "NONE", "merge authority minted")
    checks.append("authority_wall")

    for artifact in contract["prospective_realization_artifacts"].values():
        require(not (ROOT / artifact["path"]).exists(), f"prospective output already exists: {artifact['path']}")
    checks.append("prospective_realization_outputs_absent")

    result = {
        "schema_version": "atlas_route_selection_recovery_preflight_result_v0",
        "pressure_id": contract["pressure_id"],
        "recovery_realization_id": contract["recovery_realization_id"],
        "status": "PASS",
        "checks": checks,
        "scientific_A2_B2_consumed": False,
        "scientific_result": "NONE",
        "scientific_promotion": "NONE",
        "execution_authority": "NONE",
        "next_state": "STOP_FOR_HUMAN_REALIZATION_AUTHORIZATION",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
