#!/usr/bin/env python3
"""
Deterministic evidence-bundle assembler for Local LM Studio bridge testing.

This helper does not invoke a model and does not grant repository access to a
model. It resolves exact immutable Git objects named by a manifest, verifies
their SHA-256 identities, assembles one deterministic UTF-8 bundle, and writes
a local witness.

Usage:
    python tools/bridge_evidence_bundle_v0.py bridge/evidence_manifests/EXAMPLE.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "bridge" / "policy_v0.json"

SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
LABEL_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{0,63}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(*args: str) -> subprocess.CompletedProcess[bytes]:
    cmd = ["git", "-C", str(ROOT), *args]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(
            f"git command failed: {' '.join(cmd)}\n"
            f"{proc.stderr.decode('utf-8', errors='replace')}"
        )
    return proc


def load_policy() -> dict[str, Any]:
    with POLICY_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_repo_path(path: str, allowed_prefixes: tuple[str, ...]) -> None:
    if not isinstance(path, str):
        raise ValueError("path must be string")
    if path.startswith("/") or "\\" in path or ".." in Path(path).parts:
        raise ValueError(f"unsafe repo-relative path: {path!r}")
    if not path.startswith(allowed_prefixes):
        raise ValueError(f"path outside allowed prefixes: {path}")


def read_immutable_blob(ref: str, path: str) -> bytes:
    if not SHA40_RE.fullmatch(ref):
        raise ValueError("source_ref must be exact 40-char lowercase SHA")

    proc = run_git("ls-tree", "-z", ref, "--", path)
    entries = [entry for entry in proc.stdout.split(b"\x00") if entry]
    if len(entries) != 1:
        raise RuntimeError(
            f"immutable path resolved to {len(entries)} objects: {ref}:{path}"
        )

    metadata, resolved_path = entries[0].split(b"\t", 1)
    _mode, object_type, blob_sha = metadata.decode("ascii").split()
    resolved_path_text = resolved_path.decode("utf-8")

    if object_type != "blob":
        raise RuntimeError(f"path is not a blob: {path}")
    if resolved_path_text != path:
        raise RuntimeError(
            f"path mismatch: requested={path!r}, resolved={resolved_path_text!r}"
        )
    if not SHA40_RE.fullmatch(blob_sha):
        raise RuntimeError(f"unexpected blob SHA: {blob_sha!r}")

    return run_git("cat-file", "blob", blob_sha).stdout


def parse_object(
    obj: Any,
    *,
    kind: str,
    allowed_prefixes: tuple[str, ...],
) -> dict[str, str]:
    if not isinstance(obj, dict):
        raise ValueError(f"{kind} must be an object")

    expected = {"source_ref", "path", "sha256"}
    if kind == "evidence":
        expected |= {"label", "mode"}

    if set(obj) != expected:
        raise ValueError(
            f"{kind} key mismatch; extra={sorted(set(obj)-expected)}, "
            f"missing={sorted(expected-set(obj))}"
        )

    ref = obj["source_ref"]
    path = obj["path"]
    digest = obj["sha256"]

    if not isinstance(ref, str) or not SHA40_RE.fullmatch(ref):
        raise ValueError(f"{kind}.source_ref must be exact SHA")
    validate_repo_path(path, allowed_prefixes)
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ValueError(f"{kind}.sha256 must be exact lowercase SHA-256")

    result = {
        "source_ref": ref,
        "path": path,
        "sha256": digest,
    }

    if kind == "evidence":
        label = obj["label"]
        mode = obj["mode"]
        if not isinstance(label, str) or not LABEL_RE.fullmatch(label):
            raise ValueError("invalid evidence label")
        if mode != "full_text":
            raise ValueError("V0 supports only mode=full_text")
        result["label"] = label
        result["mode"] = mode

    return result


def load_manifest(path: Path, policy: dict[str, Any]) -> dict[str, Any]:
    raw = path.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))

    expected = {
        "schema_version",
        "bundle_id",
        "instruction",
        "evidence",
    }
    if set(manifest) != expected:
        raise ValueError(
            f"manifest key mismatch; extra={sorted(set(manifest)-expected)}, "
            f"missing={sorted(expected-set(manifest))}"
        )

    if manifest["schema_version"] != "BRIDGE_EVIDENCE_BUNDLE_REQUEST_V0":
        raise ValueError("unsupported schema_version")

    bundle_id = manifest["bundle_id"]
    if not isinstance(bundle_id, str) or not LABEL_RE.fullmatch(bundle_id):
        raise ValueError("invalid bundle_id")

    prefixes = tuple(str(p) for p in policy["allowed_input_prefixes"])
    instruction = parse_object(
        manifest["instruction"],
        kind="instruction",
        allowed_prefixes=prefixes,
    )

    evidence_raw = manifest["evidence"]
    if not isinstance(evidence_raw, list) or not evidence_raw:
        raise ValueError("evidence must be a non-empty list")

    max_items = int(policy.get("max_evidence_items", 16))
    if len(evidence_raw) > max_items:
        raise ValueError(f"evidence item count exceeds policy ceiling: {max_items}")

    evidence = [
        parse_object(item, kind="evidence", allowed_prefixes=prefixes)
        for item in evidence_raw
    ]
    labels = [item["label"] for item in evidence]
    if len(labels) != len(set(labels)):
        raise ValueError("duplicate evidence labels")

    return {
        "bundle_id": bundle_id,
        "instruction": instruction,
        "evidence": evidence,
        "manifest_sha256": sha256_bytes(raw),
    }


def resolve_item(item: dict[str, str]) -> tuple[bytes, dict[str, Any]]:
    raw = read_immutable_blob(item["source_ref"], item["path"])
    observed = sha256_bytes(raw)
    if observed != item["sha256"]:
        raise ValueError(
            "identity mismatch for "
            f"{item['path']}: declared={item['sha256']} observed={observed}"
        )
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"item is not UTF-8 text: {item['path']}") from e

    witness = {
        "source_ref": item["source_ref"],
        "path": item["path"],
        "declared_sha256": item["sha256"],
        "observed_sha256": observed,
        "bytes": len(raw),
    }
    if "label" in item:
        witness["label"] = item["label"]
        witness["mode"] = item["mode"]
    return raw, witness


def assemble_bundle(
    manifest: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    instruction_bytes, instruction_witness = resolve_item(manifest["instruction"])

    chunks = [
        b"=== INSTRUCTION ===\n",
        instruction_bytes,
        b"\n",
    ]

    evidence_witnesses = []
    for index, item in enumerate(manifest["evidence"], start=1):
        raw, witness = resolve_item(item)
        evidence_witnesses.append(witness)
        header = (
            f"\n=== EVIDENCE {index:03d}: {item['label']} ===\n"
            f"SOURCE_REF: {item['source_ref']}\n"
            f"PATH: {item['path']}\n"
            f"SHA256: {item['sha256']}\n\n"
        ).encode("utf-8")
        chunks.extend([header, raw, b"\n"])

    bundle = b"".join(chunks)

    max_bytes = int(policy.get("max_bundle_bytes", policy["max_prompt_bytes"]))
    if len(bundle) > max_bytes:
        raise ValueError(f"assembled bundle exceeds byte ceiling: {max_bytes}")

    witness = {
        "object_type": "BRIDGE_EVIDENCE_BUNDLE_WITNESS_V0",
        "bundle_id": manifest["bundle_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "bundle_sha256": sha256_bytes(bundle),
        "bundle_bytes": len(bundle),
        "instruction": instruction_witness,
        "evidence_count": len(evidence_witnesses),
        "evidence_items": evidence_witnesses,
        "model_repository_access": False,
        "model_tools": False,
        "model_network_access": False,
        "scientific_interpretation_performed": False,
    }
    return bundle, witness


def output_paths(bundle_id: str) -> tuple[Path, Path]:
    out_dir = ROOT / "bridge" / "bundles"
    out_dir.mkdir(parents=True, exist_ok=True)
    return (
        out_dir / f"{bundle_id}.md",
        out_dir / f"{bundle_id}.witness.json",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", help="path to BRIDGE_EVIDENCE_BUNDLE_REQUEST_V0 JSON")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path

    policy = load_policy()
    manifest = load_manifest(manifest_path, policy)
    bundle, witness = assemble_bundle(manifest, policy)
    bundle_path, witness_path = output_paths(manifest["bundle_id"])

    if bundle_path.exists() or witness_path.exists():
        raise RuntimeError(
            "bundle output already exists; use a new bundle_id rather than overwriting"
        )

    bundle_path.write_bytes(bundle)
    witness_path.write_text(
        json.dumps(witness, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"[OK] bundle  : {bundle_path.relative_to(ROOT)}")
    print(f"[OK] witness : {witness_path.relative_to(ROOT)}")
    print(f"[OK] sha256  : {witness['bundle_sha256']}")
    print(f"[OK] bytes   : {witness['bundle_bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
