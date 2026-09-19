from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[6]
CONTRACT_FREEZE_COMMIT = "414d76421fdc6c61334a6bd3a35c5ab37245ef23"
HARNESS_IMPLEMENTATION_COMMIT = "364a0f210d7fd9efe75a8006ca6602549489bcf3"
CONTRACT_PATH = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/recovery_v0/recovery_contract_v0.json")
HARNESS_PATH = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/execution_evidence_harness.py")
CHILD_PATH = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/execution_evidence_child.py")
ATLAS_PATH = Path("lab/ops/candidates/atlas_five_node_v0/atlas.py")
PRODUCER_PATH = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/run_pressure.py")
A_TARGET = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/A_manifest.json")
B_TARGET = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/B_manifest.json")
A2_SOURCE = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/recovery_v0/A2_manifest.json")
B2_SOURCE = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/recovery_v0/B2_manifest.json")

EXPECTED = {
    "contract_blob": "b46362586324b8902d0f53a5e67cd219b4d3ea74",
    "harness_blob": "0f9697cb8a38b317c0a7324f751bcbfbea401b2f",
    "child_blob": "d36603eaa494d83c726487bf3536e8fd4b3e7655",
    "atlas_blob": "15624c5b8a1a42546471fc64d0f7d85ada6d1791",
    "producer_blob": "8d133fc5356cadf6ca53f506b01c6a8494cbc18b",
    "A2_blob": "30350aea95ff995d029c09cb5db9bd63a08c6f0e",
    "A2_sha256": "6dd83edbab294af3cc1b79d42fd561bd1841ef91dd8156a3dc22298a992eb3f7",
    "B2_blob": "8775a109b189e6d0a7bacf37368ab9be921de22a",
    "B2_sha256": "df29c64cb807e476a4dff76d14ebe0f7d4b8308ea1571924eb83a8d9d5bde515",
}


class RealizationAdministrationError(RuntimeError):
    pass


def git_blob_bytes(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_show(commit: str, path: Path) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        cwd=REPO,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RealizationAdministrationError(
            f"git show failed for {commit}:{path}: {proc.stderr.decode(errors='replace')}"
        )
    return proc.stdout


def require_blob(data: bytes, expected: str, label: str) -> None:
    observed = git_blob_bytes(data)
    if observed != expected:
        raise RealizationAdministrationError(
            f"{label} blob mismatch: expected={expected} observed={observed}"
        )


def require_sha256(data: bytes, expected: str, label: str) -> None:
    observed = sha256_bytes(data)
    if observed != expected:
        raise RealizationAdministrationError(
            f"{label} sha256 mismatch: expected={expected} observed={observed}"
        )


def write_exact(root: Path, rel: Path, data: bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def load_harness(source_root: Path):
    path = source_root / HARNESS_PATH
    spec = importlib.util.spec_from_file_location(
        "atlas_route_selection_execution_evidence_harness_frozen", path
    )
    if spec is None or spec.loader is None:
        raise RealizationAdministrationError("cannot load frozen execution-evidence harness")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: recovery_realization_runner_v0.py OUTPUT_ROOT", file=sys.stderr)
        return 64

    output_root = Path(sys.argv[1]).resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise RealizationAdministrationError("realization output root is not fresh")

    contract_bytes = git_show(CONTRACT_FREEZE_COMMIT, CONTRACT_PATH)
    require_blob(contract_bytes, EXPECTED["contract_blob"], "recovery contract")
    contract = json.loads(contract_bytes)
    if contract["recovery_realization_id"] != "c8ccfe6e-7aea-4577-b3ee-66dcdd40c98e":
        raise RealizationAdministrationError("recovery realization id mismatch")
    if contract["authority"]["scientific_realization"] != "NONE":
        raise RealizationAdministrationError("frozen contract unexpectedly contains realization authority")

    harness_bytes = git_show(HARNESS_IMPLEMENTATION_COMMIT, HARNESS_PATH)
    child_bytes = git_show(HARNESS_IMPLEMENTATION_COMMIT, CHILD_PATH)
    atlas_bytes = git_show(HARNESS_IMPLEMENTATION_COMMIT, ATLAS_PATH)
    producer_bytes = git_show(HARNESS_IMPLEMENTATION_COMMIT, PRODUCER_PATH)
    a2_bytes = git_show(CONTRACT_FREEZE_COMMIT, A2_SOURCE)
    b2_bytes = git_show(CONTRACT_FREEZE_COMMIT, B2_SOURCE)

    require_blob(harness_bytes, EXPECTED["harness_blob"], "harness")
    require_blob(child_bytes, EXPECTED["child_blob"], "child wrapper")
    require_blob(atlas_bytes, EXPECTED["atlas_blob"], "atlas")
    require_blob(producer_bytes, EXPECTED["producer_blob"], "producer")
    require_blob(a2_bytes, EXPECTED["A2_blob"], "A2")
    require_sha256(a2_bytes, EXPECTED["A2_sha256"], "A2")
    require_blob(b2_bytes, EXPECTED["B2_blob"], "B2")
    require_sha256(b2_bytes, EXPECTED["B2_sha256"], "B2")

    with tempfile.TemporaryDirectory(prefix="atlas_route_recovery_source_") as temp:
        source_root = Path(temp) / "source"
        write_exact(source_root, HARNESS_PATH, harness_bytes)
        write_exact(source_root, CHILD_PATH, child_bytes)
        write_exact(source_root, ATLAS_PATH, atlas_bytes)
        write_exact(source_root, PRODUCER_PATH, producer_bytes)
        write_exact(source_root, A_TARGET, a2_bytes)
        write_exact(source_root, B_TARGET, b2_bytes)

        harness = load_harness(source_root)
        inputs = harness.InputCoordinates(
            EXPECTED["A2_blob"],
            EXPECTED["A2_sha256"],
            EXPECTED["B2_blob"],
            EXPECTED["B2_sha256"],
        )
        receipt = harness._execute(
            source_root,
            output_root,
            expected_harness_blob=EXPECTED["harness_blob"],
            expected_child_blob=EXPECTED["child_blob"],
            inputs=inputs,
        )
        harness.validate_runtime_receipt(output_root)

    raw = json.loads((output_root / "raw_observation.json").read_text(encoding="utf-8"))
    result = json.loads((output_root / "mechanical_result.json").read_text(encoding="utf-8"))
    file_digests = {
        p.name: sha256_bytes(p.read_bytes())
        for p in sorted(output_root.iterdir())
        if p.is_file()
    }
    summary = {
        "schema_version": "atlas_route_selection_recovery_realization_runner_summary_v0",
        "pressure_id": "ATLAS_ROUTE_SELECTION_001",
        "recovery_realization_id": "c8ccfe6e-7aea-4577-b3ee-66dcdd40c98e",
        "contract_freeze_commit": CONTRACT_FREEZE_COMMIT,
        "contract_blob": EXPECTED["contract_blob"],
        "harness_implementation_commit": HARNESS_IMPLEMENTATION_COMMIT,
        "A2_blob": EXPECTED["A2_blob"],
        "B2_blob": EXPECTED["B2_blob"],
        "runtime_receipt_status": receipt["status"],
        "raw_observation": raw,
        "mechanical_result": result,
        "output_sha256": file_digests,
        "scientific_promotion": "NONE",
        "merge_authority": "NONE",
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
