#!/usr/bin/env python3
"""
Trusted local LM Studio invocation bridge, V0.

Security model:
- Reads declarative request manifests from a fixed GitHub branch via git object access.
- Never executes repo-provided shell commands.
- Only reads prompt artifacts from allowlisted repo-relative prefixes.
- Requires exact immutable commit SHA + prompt SHA256.
- Only calls LM Studio chat completions with one user message.
- Supplies no tools, no previous_response_id, no connectors, no repo access.
- Requires local human approval before invocation.
- Writes witnessed JSON results to a fixed result directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "bridge" / "policy_v0.json"

REQUEST_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,95}$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def input_identity_rejection_witness(
    manifest: dict[str, Any],
    prompt_bytes: bytes,
) -> dict[str, Any] | None:
    """Return a deterministic apparatus rejection for an input mismatch.

    A matching identity returns ``None`` and leaves the existing approval and
    invocation path unchanged.  The witness is authored before approval or any
    LM Studio call and contains no model-produced evidence.
    """

    declared_input_sha256 = str(manifest["input_sha256"])
    observed_input_sha256 = sha256_bytes(prompt_bytes)
    if observed_input_sha256 == declared_input_sha256:
        return None

    return {
        "object_type": "LOCAL_LMSTUDIO_INPUT_IDENTITY_REJECTION_V0",
        "request_id": str(manifest["request_id"]),
        "declared_input_sha256": declared_input_sha256,
        "observed_input_sha256": observed_input_sha256,
        "executor_sha256": sha256_bytes(Path(__file__).resolve().read_bytes()),
        "policy_sha256": sha256_bytes(POLICY_PATH.read_bytes()),
        "decision": "REJECT",
        "reason": "INPUT_SHA256_MISMATCH",
        "lmstudio_invoked": False,
    }


def emit_rejection_witness(witness: dict[str, Any]) -> None:
    print(
        "[REJECT] "
        + json.dumps(witness, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    )


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    cmd = ["git", "-C", str(ROOT), *args]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git command failed: {' '.join(cmd)}\n"
            f"{proc.stderr.decode('utf-8', errors='replace')}"
        )
    return proc


def load_policy() -> dict[str, Any]:
    with POLICY_PATH.open("r", encoding="utf-8") as f:
        policy = json.load(f)

    if policy.get("policy_version") != "LOCAL_LMSTUDIO_BRIDGE_POLICY_V0":
        raise RuntimeError("Unsupported bridge policy version")

    if policy.get("allow_tools") is not False:
        raise RuntimeError("V0 requires allow_tools=false")

    if policy.get("allow_previous_response_id") is not False:
        raise RuntimeError("V0 requires allow_previous_response_id=false")

    if policy.get("require_local_approval") is not True:
        raise RuntimeError("V0 requires require_local_approval=true")

    return policy


def fetch_remote(policy: dict[str, Any]) -> str:
    remote = str(policy["remote"])
    branch = str(policy["branch"])
    run_git("fetch", "--quiet", remote, branch)
    remote_ref = f"{remote}/{branch}"
    head = run_git("rev-parse", remote_ref).stdout.decode().strip()
    if not SHA40_RE.fullmatch(head):
        raise RuntimeError(f"Unexpected remote head: {head!r}")
    return head


def git_show(ref: str, path: str) -> bytes:
    if not SHA40_RE.fullmatch(ref):
        raise ValueError("source_ref must be an exact 40-character lowercase commit SHA")
    if path.startswith("/") or "\\" in path or ".." in Path(path).parts:
        raise ValueError("unsafe repo-relative path")
    return run_git("show", f"{ref}:{path}").stdout


def list_request_paths(remote_head: str, policy: dict[str, Any]) -> list[str]:
    prefix = str(policy["request_prefix"])
    proc = run_git("ls-tree", "-r", "--name-only", remote_head, prefix)
    paths = [
        line.strip()
        for line in proc.stdout.decode("utf-8", errors="strict").splitlines()
        if line.strip().endswith(".json")
    ]
    return sorted(paths)


def parse_manifest(raw: bytes) -> dict[str, Any]:
    manifest = json.loads(raw.decode("utf-8"))

    allowed_keys = {
        "schema_version",
        "request_id",
        "enabled",
        "source_ref",
        "input_path",
        "input_sha256",
        "model",
        "temperature",
        "max_tokens",
        "purpose",
    }
    if set(manifest) != allowed_keys:
        extra = sorted(set(manifest) - allowed_keys)
        missing = sorted(allowed_keys - set(manifest))
        raise ValueError(f"manifest key mismatch; extra={extra}, missing={missing}")

    if manifest["schema_version"] != "LOCAL_INVOCATION_REQUEST_V0":
        raise ValueError("unsupported schema_version")

    request_id = manifest["request_id"]
    if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
        raise ValueError("invalid request_id")

    if not isinstance(manifest["enabled"], bool):
        raise ValueError("enabled must be boolean")

    if not isinstance(manifest["source_ref"], str) or not SHA40_RE.fullmatch(manifest["source_ref"]):
        raise ValueError("source_ref must be exact 40-char lowercase SHA")

    if not isinstance(manifest["input_sha256"], str) or not SHA256_RE.fullmatch(manifest["input_sha256"]):
        raise ValueError("invalid input_sha256")

    if not isinstance(manifest["temperature"], (int, float)):
        raise ValueError("temperature must be numeric")

    if not isinstance(manifest["max_tokens"], int):
        raise ValueError("max_tokens must be integer")

    if not isinstance(manifest["purpose"], str) or not (1 <= len(manifest["purpose"]) <= 500):
        raise ValueError("purpose must be 1..500 chars")

    return manifest


def validate_manifest(manifest: dict[str, Any], policy: dict[str, Any]) -> None:
    model = manifest["model"]
    if model not in policy["allowed_models"]:
        raise ValueError(f"model not allowed: {model}")

    path = manifest["input_path"]
    if not isinstance(path, str):
        raise ValueError("input_path must be string")
    if path.startswith("/") or "\\" in path or ".." in Path(path).parts:
        raise ValueError("unsafe input_path")
    prefixes = tuple(str(p) for p in policy["allowed_input_prefixes"])
    if not path.startswith(prefixes):
        raise ValueError(f"input_path outside allowed prefixes: {path}")

    temp = float(manifest["temperature"])
    if not (float(policy["temperature_min"]) <= temp <= float(policy["temperature_max"])):
        raise ValueError("temperature outside policy bounds")

    max_tokens = int(manifest["max_tokens"])
    if max_tokens < 1 or max_tokens > int(policy["max_tokens_ceiling"]):
        raise ValueError("max_tokens outside policy bounds")


def result_path_for(request_id: str, policy: dict[str, Any]) -> Path:
    prefix = Path(str(policy["result_prefix"]))
    out = ROOT / prefix / f"{request_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def invoke_lmstudio(
    manifest: dict[str, Any],
    prompt_bytes: bytes,
    manifest_sha256: str,
    policy: dict[str, Any],
    request_path: str,
) -> dict[str, Any]:
    prompt = prompt_bytes.decode("utf-8")

    body_obj = {
        "model": manifest["model"],
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": float(manifest["temperature"]),
        "max_tokens": int(manifest["max_tokens"]),
        "stream": False,
    }
    body = json.dumps(body_obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    base = str(policy["lmstudio_base_url"]).rstrip("/")
    url = f"{base}/chat/completions"

    started = now_iso()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            response_bytes = resp.read()
            status = resp.status
    except urllib.error.URLError as e:
        raise RuntimeError(f"LM Studio request failed: {e}") from e

    finished = now_iso()

    response_obj = json.loads(response_bytes.decode("utf-8"))
    assistant_text = None
    try:
        assistant_text = response_obj["choices"][0]["message"]["content"]
    except Exception:
        pass

    witness = {
        "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
        "request_id": manifest["request_id"],
        "purpose": manifest["purpose"],
        "request_manifest_path": request_path,
        "request_manifest_sha256": manifest_sha256,
        "source_ref": manifest["source_ref"],
        "input_path": manifest["input_path"],
        "input_sha256": sha256_bytes(prompt_bytes),
        "model_requested": manifest["model"],
        "temperature": float(manifest["temperature"]),
        "max_tokens": int(manifest["max_tokens"]),
        "lmstudio_url": url,
        "http_status": status,
        "observed_started_at_utc": started,
        "observed_finished_at_utc": finished,
        "messages_count": 1,
        "tools_supplied": False,
        "previous_response_id_supplied": False,
        "repository_context_supplied_to_model": False,
        "connectors_supplied_to_model": False,
        "external_retrieval_supplied_to_model": False,
        "request_body_sha256": sha256_bytes(body),
        "response_body_sha256": sha256_bytes(response_bytes),
        "assistant_text": assistant_text,
        "raw_response": response_obj,
    }
    return witness


def approve(manifest: dict[str, Any], prompt_bytes: bytes) -> bool:
    print("\n=== LOCAL INVOCATION REQUEST ===")
    print(f"request_id : {manifest['request_id']}")
    print(f"purpose    : {manifest['purpose']}")
    print(f"model      : {manifest['model']}")
    print(f"source_ref : {manifest['source_ref']}")
    print(f"input_path : {manifest['input_path']}")
    print(f"input_sha  : {manifest['input_sha256']}")
    print(f"bytes      : {len(prompt_bytes)}")
    print(f"temperature: {manifest['temperature']}")
    print(f"max_tokens : {manifest['max_tokens']}")
    print("tools      : NONE")
    print("history    : NONE")
    answer = input("Execute this local LM Studio invocation? [y/N] ").strip().lower()
    return answer == "y"


def process_once(policy: dict[str, Any]) -> int:
    remote_head = fetch_remote(policy)
    request_paths = list_request_paths(remote_head, policy)
    executed = 0

    for request_path in request_paths:
        raw_manifest = git_show(remote_head, request_path)
        manifest_sha = sha256_bytes(raw_manifest)

        try:
            manifest = parse_manifest(raw_manifest)
            validate_manifest(manifest, policy)
        except Exception as e:
            print(f"[REJECT] {request_path}: {e}")
            continue

        if not manifest["enabled"]:
            continue

        out_path = result_path_for(manifest["request_id"], policy)
        if out_path.exists():
            continue

        try:
            prompt_bytes = git_show(manifest["source_ref"], manifest["input_path"])
        except Exception as e:
            print(f"[REJECT] {request_path}: cannot read immutable prompt: {e}")
            continue

        identity_rejection = input_identity_rejection_witness(
            manifest,
            prompt_bytes,
        )
        if identity_rejection is not None:
            emit_rejection_witness(identity_rejection)
            continue

        if len(prompt_bytes) > int(policy["max_prompt_bytes"]):
            print(f"[REJECT] {request_path}: prompt exceeds size ceiling")
            continue

        try:
            prompt_bytes.decode("utf-8")
        except UnicodeDecodeError:
            print(f"[REJECT] {request_path}: prompt is not UTF-8 text")
            continue

        if not approve(manifest, prompt_bytes):
            print(f"[SKIP] {manifest['request_id']}: local authorization not granted")
            continue

        try:
            witness = invoke_lmstudio(
                manifest,
                prompt_bytes,
                manifest_sha,
                policy,
                request_path,
            )
        except Exception as e:
            print(f"[ERROR] {manifest['request_id']}: {e}")
            continue

        out_path.write_text(
            json.dumps(witness, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[OK] wrote {out_path.relative_to(ROOT)}")
        executed += 1

    return executed


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="fetch and process queue once")
    mode.add_argument("--watch", action="store_true", help="poll continuously")
    parser.add_argument("--poll-seconds", type=int, default=120)
    args = parser.parse_args()

    policy = load_policy()

    if args.once:
        process_once(policy)
        return 0

    if args.poll_seconds < 30:
        print("poll interval must be at least 30 seconds", file=sys.stderr)
        return 2

    print("DME local LM Studio bridge V0 watching.")
    print("Remote requests are proposals only; every invocation requires local approval.")
    while True:
        try:
            process_once(policy)
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            print(f"[WATCH ERROR] {e}", file=sys.stderr)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
