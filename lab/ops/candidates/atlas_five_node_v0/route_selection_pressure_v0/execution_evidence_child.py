"""Child wrapper that witnesses calls from the frozen Atlas route-selection producer."""
from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import runpy
import sys
import traceback
from typing import Any

ATLAS_MODULE = "lab.ops.candidates.atlas_five_node_v0.atlas"
ATLAS_REL = Path("lab/ops/candidates/atlas_five_node_v0/atlas.py")
PRODUCER_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/run_pressure.py")
A_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/A_manifest.json")
B_REL = Path("lab/ops/candidates/atlas_five_node_v0/route_selection_pressure_v0/B_manifest.json")
SOURCE_NODE_ID = "NODE_01"
TARGET_NODE_ID = "NODE_04"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())


def _verify(path: Path, *, blob: str | None = None, sha256: str | None = None) -> bytes:
    data = path.read_bytes()
    if blob is not None and _git_blob(data) != blob:
        raise RuntimeError(f"identity mismatch: {path}")
    if sha256 is not None and _sha256(data) != sha256:
        raise RuntimeError(f"sha256 mismatch: {path}")
    return data


def _load_exact_atlas(root: Path, expected_blob: str):
    atlas_path = (root / ATLAS_REL).resolve()
    _verify(atlas_path, blob=expected_blob)
    spec = importlib.util.spec_from_file_location(ATLAS_MODULE, atlas_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen atlas module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[ATLAS_MODULE] = module
    spec.loader.exec_module(module)
    return module, atlas_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--witness", required=True)
    parser.add_argument("--atlas-blob", required=True)
    parser.add_argument("--producer-blob", required=True)
    parser.add_argument("--a-blob", required=True)
    parser.add_argument("--a-sha256", required=True)
    parser.add_argument("--b-blob", required=True)
    parser.add_argument("--b-sha256", required=True)
    parser.add_argument("--child-blob", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    witness_path = Path(args.witness).resolve()
    producer_path = (root / PRODUCER_REL).resolve()
    a_path = (root / A_REL).resolve()
    b_path = (root / B_REL).resolve()
    child_path = Path(__file__).resolve()

    _verify(child_path, blob=args.child_blob)
    _verify(producer_path, blob=args.producer_blob)
    _verify(a_path, blob=args.a_blob, sha256=args.a_sha256)
    _verify(b_path, blob=args.b_blob, sha256=args.b_sha256)

    sys.path.insert(0, str(root))
    atlas, atlas_path = _load_exact_atlas(root, args.atlas_blob)
    original_parse = atlas.parse_manifest
    original_route = atlas.route
    call_events: list[dict[str, Any]] = []

    def _caller_origin() -> str:
        frame = inspect.currentframe()
        assert frame is not None and frame.f_back is not None and frame.f_back.f_back is not None
        return str(Path(frame.f_back.f_back.f_code.co_filename).resolve())

    @functools.wraps(original_parse)
    def witnessed_parse_manifest(raw):
        result = original_parse(raw)
        call_events.append({
            "ordinal": len(call_events) + 1,
            "function": "parse_manifest",
            "caller_origin": _caller_origin(),
            "atlas_code_origin": str(Path(original_parse.__code__.co_filename).resolve()),
            "atlas_blob": args.atlas_blob,
            "manifest_id": result.manifest_id,
            "returned": True,
        })
        return result

    @functools.wraps(original_route)
    def witnessed_route(manifest, source_node_id, target_node_id):
        result = original_route(manifest, source_node_id, target_node_id)
        call_events.append({
            "ordinal": len(call_events) + 1,
            "function": "route",
            "caller_origin": _caller_origin(),
            "atlas_code_origin": str(Path(original_route.__code__.co_filename).resolve()),
            "atlas_blob": args.atlas_blob,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "returned": True,
        })
        return result

    atlas.parse_manifest = witnessed_parse_manifest
    atlas.route = witnessed_route

    completed = False
    error_type: str | None = None
    try:
        runpy.run_path(str(producer_path), run_name="__main__")
        completed = True
        return 0
    except BaseException as exc:
        error_type = type(exc).__name__
        traceback.print_exc()
        return 70
    finally:
        witness = {
            "schema_version": "atlas_route_selection_apparatus_call_witness_v0",
            "producer_completed": completed,
            "producer_error_type": error_type,
            "producer_origin": str(producer_path),
            "producer_blob": args.producer_blob,
            "atlas_origin": str(atlas_path),
            "atlas_blob": args.atlas_blob,
            "child_wrapper_origin": str(child_path),
            "child_wrapper_blob": args.child_blob,
            "source_node_id": SOURCE_NODE_ID,
            "target_node_id": TARGET_NODE_ID,
            "call_events": call_events,
            "python": {
                "implementation": sys.implementation.name,
                "version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro],
                "cache_tag": sys.implementation.cache_tag,
                "isolated": bool(sys.flags.isolated),
                "no_site": bool(sys.flags.no_site),
            },
        }
        try:
            _write_exclusive(witness_path, _canonical(witness))
        except FileExistsError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
