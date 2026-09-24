#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import local_authority_consumption_v0 as authority_consumption

TRUST_ROOT = Path(__file__).resolve().parent
POLICY_PATH = TRUST_ROOT / "policy.json"
AUTHORITY_MODULE_PATH = TRUST_ROOT / "local_authority_consumption_v0.py"
EXPECTED_AUTHORITY_MODULE_SHA256 = (
    "bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303"
)

REQUEST_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,95}$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(msg: str) -> None:
    raise RuntimeError(msg)


def verify_authority_module_identity() -> str:
    module_path = Path(authority_consumption.__file__).resolve()
    expected_path = AUTHORITY_MODULE_PATH.resolve()
    if module_path != expected_path:
        fail(
            "Authority module loaded outside the installed trust root "
            f"(expected {expected_path}, got {module_path})"
        )
    observed = sha256_bytes(module_path.read_bytes())
    if observed != EXPECTED_AUTHORITY_MODULE_SHA256:
        fail(
            "Installed authority module hash mismatch "
            f"(expected {EXPECTED_AUTHORITY_MODULE_SHA256}, got {observed})"
        )
    return observed


def load_policy() -> dict[str, Any]:
    if not POLICY_PATH.is_file():
        fail(f"Missing local authority policy: {POLICY_PATH}")

    with POLICY_PATH.open("r", encoding="utf-8") as f:
        p = json.load(f)

    required = {
        "policy_version", "default", "repo_root", "remote", "branch",
        "request_prefix", "result_dir", "allowed_input_prefixes",
        "allowed_models", "lmstudio_base_url", "max_prompt_bytes",
        "max_tokens_ceiling", "temperature_min", "temperature_max",
        "require_local_human_approval", "trust_root_auto_update",
        "allow_repo_to_modify_installed_policy",
        "allow_repo_to_modify_installed_executor", "allow_tools",
        "allow_previous_response_state", "allow_external_retrieval",
        "allow_cli", "allow_arbitrary_network", "allow_repo_auto_commit",
        "allow_repo_auto_merge", "allow_force_push",
        "allow_seat_authority_inheritance",
    }
    missing = required - set(p)
    if missing:
        fail(f"Policy missing required keys: {sorted(missing)}")

    if p["policy_version"] != "DME_LOCAL_BRIDGE_POLICY_V0":
        fail("Unsupported policy_version")
    if p["default"] != "DENY":
        fail("V0 requires default=DENY")
    if p["require_local_human_approval"] is not True:
        fail("V0 requires local human approval")
    if p["trust_root_auto_update"] is not False:
        fail("V0 forbids trust-root auto-update")
    if p["allow_repo_to_modify_installed_policy"] is not False:
        fail("Repo may not modify installed policy")
    if p["allow_repo_to_modify_installed_executor"] is not False:
        fail("Repo may not modify installed executor")
    if p["allow_tools"] is not False:
        fail("V0 forbids model tools")
    if p["allow_previous_response_state"] is not False:
        fail("V0 forbids previous-response state")
    if p["allow_external_retrieval"] is not False:
        fail("V0 forbids model external retrieval")
    if p["allow_cli"] is not False:
        fail("V0 forbids request-driven CLI")
    if p["allow_arbitrary_network"] is not False:
        fail("V0 forbids arbitrary network")
    if p["allow_repo_auto_commit"] is not False:
        fail("V0 forbids automatic repo commits")
    if p["allow_repo_auto_merge"] is not False:
        fail("V0 forbids automatic repo merges")
    if p["allow_force_push"] is not False:
        fail("V0 forbids force push")
    if p["allow_seat_authority_inheritance"] is not False:
        fail("V0 forbids inherited seat authority")

    repo = Path(os.path.expandvars(os.path.expanduser(str(p["repo_root"])))).resolve()
    if not repo.is_dir():
        fail(f"Configured repo_root does not exist: {repo}")
    p["_repo_root_resolved"] = str(repo)

    # Result witnesses are experiment artifacts, not authority state.
    # Keep them on the repository working surface while the trust root retains
    # only installed executor/policy/authority-bearing local state.
    result_dir = (repo / "bridge" / "results").resolve()
    result_dir.mkdir(parents=True, exist_ok=True)
    p["_result_dir_resolved"] = str(result_dir)
    return p


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    cmd = ["git", "-C", str(repo), *args]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git command failed: {' '.join(cmd)}\n"
            f"{proc.stderr.decode('utf-8', errors='replace')}"
        )
    return proc


def fetch_remote(repo: Path, p: dict[str, Any]) -> str:
    remote = str(p["remote"])
    branch = str(p["branch"])
    run_git(repo, "fetch", "--quiet", "--no-tags", remote, branch)
    head = run_git(repo, "rev-parse", f"{remote}/{branch}").stdout.decode().strip()
    if not SHA40_RE.fullmatch(head):
        fail(f"Unexpected remote head: {head!r}")
    return head


def safe_repo_path(path: str) -> None:
    if not isinstance(path, str) or not path:
        raise ValueError("repo path must be a non-empty string")
    if path.startswith("/") or path.startswith("\\") or "\\" in path:
        raise ValueError("unsafe repo-relative path")
    if ".." in Path(path).parts or ":" in path:
        raise ValueError("relative traversal / drive syntax forbidden")


def git_show(repo: Path, ref: str, path: str) -> bytes:
    if not SHA40_RE.fullmatch(ref):
        raise ValueError("ref must be exact 40-char lowercase commit SHA")
    safe_repo_path(path)
    return run_git(repo, "show", f"{ref}:{path}").stdout


def resolve_git_blob_sha(repo: Path, ref: str, path: str) -> str:
    """Resolve one immutable ref/path pair to its exact Git blob object id."""
    if not SHA40_RE.fullmatch(ref):
        raise ValueError("ref must be exact 40-char lowercase commit SHA")
    safe_repo_path(path)
    proc = run_git(repo, "ls-tree", "-z", ref, "--", path)
    entries = [entry for entry in proc.stdout.split(b"\x00") if entry]
    if len(entries) != 1:
        raise RuntimeError(
            f"immutable prompt path resolved to {len(entries)} objects: {path}"
        )
    try:
        metadata, resolved_path = entries[0].split(b"\t", 1)
        _mode, object_type, blob_sha = metadata.decode("ascii").split()
        resolved_path_text = resolved_path.decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"unexpected ls-tree response for {path!r}") from exc
    if object_type != "blob":
        raise RuntimeError(f"immutable prompt path is not a blob: {path}")
    if resolved_path_text != path:
        raise RuntimeError(
            f"immutable prompt path mismatch: requested={path!r}, "
            f"resolved={resolved_path_text!r}"
        )
    if not SHA40_RE.fullmatch(blob_sha):
        raise RuntimeError(f"unexpected blob SHA for {path!r}: {blob_sha!r}")
    return blob_sha


def git_blob_bytes(repo: Path, blob_sha: str) -> bytes:
    if not SHA40_RE.fullmatch(blob_sha):
        raise ValueError("blob_sha must be exact 40-char lowercase SHA")
    return run_git(repo, "cat-file", "blob", blob_sha).stdout


def list_request_paths(repo: Path, remote_head: str, p: dict[str, Any]) -> list[str]:
    prefix = str(p["request_prefix"])
    safe_repo_path(prefix.rstrip("/") + "/x")
    proc = run_git(repo, "ls-tree", "-r", "--name-only", remote_head, prefix)
    return sorted(
        line.strip()
        for line in proc.stdout.decode("utf-8", errors="strict").splitlines()
        if line.strip().endswith(".json")
    )


def parse_manifest(raw: bytes) -> dict[str, Any]:
    manifest = json.loads(raw.decode("utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")

    schema_version = manifest.get("schema_version")
    base = {
        "schema_version", "request_id", "enabled", "source_ref", "input_path",
        "principal_id", "model", "temperature", "max_tokens", "purpose",
    }
    if schema_version == "LOCAL_INVOCATION_REQUEST_V0":
        allowed = base | {"input_sha256"}
    elif schema_version == "LOCAL_INVOCATION_REQUEST_V0_1":
        allowed = base | {"input_blob_sha"}
    else:
        raise ValueError("unsupported schema_version")

    if set(manifest) != allowed:
        raise ValueError("manifest key mismatch")
    if not isinstance(manifest["request_id"], str) or not REQUEST_ID_RE.fullmatch(manifest["request_id"]):
        raise ValueError("invalid request_id")
    if not isinstance(manifest["enabled"], bool):
        raise ValueError("enabled must be boolean")
    if not isinstance(manifest["source_ref"], str) or not SHA40_RE.fullmatch(manifest["source_ref"]):
        raise ValueError("source_ref must be exact 40-char lowercase SHA")
    if schema_version == "LOCAL_INVOCATION_REQUEST_V0":
        if not isinstance(manifest["input_sha256"], str) or not SHA256_RE.fullmatch(manifest["input_sha256"]):
            raise ValueError("invalid input_sha256")
    else:
        if not isinstance(manifest["input_blob_sha"], str) or not SHA40_RE.fullmatch(manifest["input_blob_sha"]):
            raise ValueError("invalid input_blob_sha")
    if not isinstance(manifest["principal_id"], str) or not REQUEST_ID_RE.fullmatch(manifest["principal_id"]):
        raise ValueError("invalid principal_id")
    if not isinstance(manifest["model"], str):
        raise ValueError("model must be string")
    if isinstance(manifest["temperature"], bool) or not isinstance(manifest["temperature"], (int, float)):
        raise ValueError("temperature must be numeric")
    if isinstance(manifest["max_tokens"], bool) or not isinstance(manifest["max_tokens"], int):
        raise ValueError("max_tokens must be integer")
    if not isinstance(manifest["purpose"], str) or not (1 <= len(manifest["purpose"]) <= 500):
        raise ValueError("purpose must be 1..500 chars")
    safe_repo_path(manifest["input_path"])
    return manifest

def validate_manifest(manifest: dict[str, Any], p: dict[str, Any]) -> None:
    if manifest["model"] not in p["allowed_models"]:
        raise ValueError(f"model not allowed: {manifest['model']}")
    path = manifest["input_path"]
    prefixes = tuple(str(x) for x in p["allowed_input_prefixes"])
    if not any(path.startswith(prefix) for prefix in prefixes):
        raise ValueError(f"input_path outside allowed prefixes: {path}")
    t = float(manifest["temperature"])
    if not (float(p["temperature_min"]) <= t <= float(p["temperature_max"])):
        raise ValueError("temperature outside policy bounds")
    m = int(manifest["max_tokens"])
    if m < 1 or m > int(p["max_tokens_ceiling"]):
        raise ValueError("max_tokens outside policy bounds")


def result_path_for(request_id: str, p: dict[str, Any]) -> Path:
    base = Path(p["_result_dir_resolved"])
    out = (base / f"{request_id}.json").resolve()
    if out.parent != base:
        fail("result path escaped result directory")
    return out


def lmstudio_endpoint_identity(p: dict[str, Any]) -> str:
    base = str(p["lmstudio_base_url"]).rstrip("/")
    if base not in {"http://127.0.0.1:1234/v1", "http://localhost:1234/v1"}:
        fail("V0 LM Studio endpoint must remain localhost:1234")
    return f"{base}/chat/completions"


def fresh_authority_ids() -> tuple[str, str]:
    capability_nonce = uuid.uuid4().hex.upper()
    approval_nonce = uuid.uuid4().hex.upper()
    return (
        f"CELL003.CAP.{capability_nonce}",
        f"CELL003.APPROVAL.{approval_nonce}",
    )


def build_approval_candidate(
    manifest: dict[str, Any],
    manifest_sha256: str,
    prompt_bytes: bytes,
    p: dict[str, Any],
    capability_id: str,
    approval_id: str,
) -> dict[str, Any]:
    """Freeze the exact consequence coordinates presented for approval.

    ``request_sha256`` commits the exact raw manifest, including temperature,
    max_tokens, source_ref, input_path, purpose, and declared principal.
    """

    return {
        "capability_id": capability_id,
        "approval_id": approval_id,
        "principal_id": manifest["principal_id"],
        "request_sha256": manifest_sha256,
        "input_blob_sha": (
            manifest.get("input_blob_sha")
            if manifest["schema_version"] == "LOCAL_INVOCATION_REQUEST_V0_1"
            else None
        ),
        "input_sha256": sha256_bytes(prompt_bytes),
        "model": manifest["model"],
        "endpoint_identity": lmstudio_endpoint_identity(p),
        "executor_sha256": sha256_bytes(Path(__file__).resolve().read_bytes()),
        "policy_sha256": sha256_bytes(POLICY_PATH.read_bytes()),
        "temperature": float(manifest["temperature"]),
        "max_tokens": int(manifest["max_tokens"]),
        "stream": False,
    }


def approval_coordinates_still_current(
    approved_manifest: dict[str, Any],
    manifest: dict[str, Any],
    execution_candidate_bytes: bytes,
    p: dict[str, Any],
    approved: dict[str, Any],
) -> bool:
    return (
        manifest == approved_manifest
        and sha256_bytes(execution_candidate_bytes) == approved["input_sha256"]
        and manifest["principal_id"] == approved["principal_id"]
        and manifest["model"] == approved["model"]
        and float(manifest["temperature"]) == approved["temperature"]
        and int(manifest["max_tokens"]) == approved["max_tokens"]
        and lmstudio_endpoint_identity(p) == approved["endpoint_identity"]
        and sha256_bytes(Path(__file__).resolve().read_bytes())
        == approved["executor_sha256"]
        and sha256_bytes(POLICY_PATH.read_bytes()) == approved["policy_sha256"]
    )


def mint_authority_envelope(
    approved: dict[str, Any], issued_at: str
) -> dict[str, Any]:
    return {
        "object_type": authority_consumption.ENVELOPE_TYPE,
        "capability_id": approved["capability_id"],
        "approval_id": approved["approval_id"],
        "principal_id": approved["principal_id"],
        "request_sha256": approved["request_sha256"],
        "input_sha256": approved["input_sha256"],
        "model": approved["model"],
        "endpoint_identity": approved["endpoint_identity"],
        "executor_sha256": approved["executor_sha256"],
        "policy_sha256": approved["policy_sha256"],
        "use_limit": 1,
        "remaining_uses": 1,
        "status": authority_consumption.ACTIVE,
        "issued_at": issued_at,
        "expires_at": None,
    }


def default_execution_candidate_provider(
    manifest: dict[str, Any], reviewed_prompt_bytes: bytes
) -> bytes:
    # Production default: execute exactly what was reviewed.
    return reviewed_prompt_bytes


def postapproval_revalidation_witness(
    manifest: dict[str, Any],
    manifest_sha256: str,
    reviewed_prompt_bytes: bytes,
    execution_candidate_bytes: bytes,
) -> dict[str, Any] | None:
    reviewed_sha = sha256_bytes(reviewed_prompt_bytes)
    candidate_sha = sha256_bytes(execution_candidate_bytes)
    if reviewed_sha == candidate_sha:
        return None
    witness = {
        "object_type": "LOCAL_LMSTUDIO_POSTAPPROVAL_REVALIDATION_V0",
        "request_id": manifest["request_id"],
        "request_manifest_sha256": manifest_sha256,
        "source_ref": manifest["source_ref"],
        "input_path": manifest["input_path"],
        "reviewed_input_sha256": reviewed_sha,
        "execution_candidate_sha256": candidate_sha,
        "executor_sha256": sha256_bytes(Path(__file__).resolve().read_bytes()),
        "policy_sha256": sha256_bytes(POLICY_PATH.read_bytes()),
        "approval_occurred": True,
        "rejection_after_approval": True,
        "decision": "REVALIDATE",
        "reason": "POST_APPROVAL_INPUT_SHA256_MISMATCH",
        "lmstudio_invoked": False,
    }
    if manifest["schema_version"] == "LOCAL_INVOCATION_REQUEST_V0":
        witness["declared_input_sha256"] = manifest["input_sha256"]
    else:
        witness["declared_input_blob_sha"] = manifest["input_blob_sha"]
    return witness


def postapproval_coordinate_revalidation_witness(
    manifest: dict[str, Any],
    approved_manifest: dict[str, Any],
    execution_candidate_bytes: bytes,
    p: dict[str, Any],
    approved: dict[str, Any],
) -> dict[str, Any] | None:
    if approval_coordinates_still_current(
        approved_manifest,
        manifest,
        execution_candidate_bytes,
        p,
        approved,
    ):
        return None
    return {
        "object_type": "LOCAL_LMSTUDIO_POSTAPPROVAL_COORDINATE_REVALIDATION_V0",
        "request_id": approved_manifest["request_id"],
        "capability_id": approved["capability_id"],
        "approval_id": approved["approval_id"],
        "principal_id": approved["principal_id"],
        "request_sha256": approved["request_sha256"],
        "input_sha256": approved["input_sha256"],
        "model": approved["model"],
        "endpoint_identity": approved["endpoint_identity"],
        "executor_sha256": approved["executor_sha256"],
        "policy_sha256": approved["policy_sha256"],
        "approval_occurred": True,
        "rejection_after_approval": True,
        "decision": "REVALIDATE",
        "reason": "POST_APPROVAL_AUTHORITY_COORDINATE_MISMATCH",
        "authority_issued": False,
        "lmstudio_invoked": False,
    }


def emit_revalidation_witness(witness: dict[str, Any]) -> None:
    print("[REVALIDATE] " + json.dumps(witness, sort_keys=True, separators=(",", ":")))


def invoke_lmstudio(
    manifest: dict[str, Any],
    prompt_bytes: bytes,
    manifest_sha256: str,
    p: dict[str, Any],
    request_path: str,
) -> dict[str, Any]:
    prompt = prompt_bytes.decode("utf-8")
    body_obj = {
        "model": manifest["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(manifest["temperature"]),
        "max_tokens": int(manifest["max_tokens"]),
        "stream": False,
    }
    body = json.dumps(body_obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    url = lmstudio_endpoint_identity(p)

    started = now_iso()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            response_bytes = resp.read()
            status = int(resp.status)
    except urllib.error.URLError as e:
        raise RuntimeError(f"LM Studio request failed: {e}") from e
    finished = now_iso()

    response_obj = json.loads(response_bytes.decode("utf-8"))
    try:
        assistant_text = response_obj["choices"][0]["message"]["content"]
    except Exception:
        assistant_text = None

    return {
        "object_type": "LOCAL_LMSTUDIO_INVOCATION_WITNESS_V0",
        "executor_path": str(Path(__file__).resolve()),
        "executor_sha256": sha256_bytes(Path(__file__).resolve().read_bytes()),
        "policy_path": str(POLICY_PATH),
        "policy_sha256": sha256_bytes(POLICY_PATH.read_bytes()),
        "request_id": manifest["request_id"],
        "purpose": manifest["purpose"],
        "request_manifest_path": request_path,
        "request_manifest_sha256": manifest_sha256,
        "source_ref": manifest["source_ref"],
        "input_path": manifest["input_path"],
        "input_blob_sha": (
            manifest.get("input_blob_sha")
            if manifest["schema_version"] == "LOCAL_INVOCATION_REQUEST_V0_1"
            else None
        ),
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
        "previous_response_state_supplied": False,
        "repository_context_supplied_to_model": False,
        "connectors_supplied_to_model": False,
        "external_retrieval_supplied_to_model": False,
        "request_body_sha256": sha256_bytes(body),
        "response_body_sha256": sha256_bytes(response_bytes),
        "assistant_text": assistant_text,
        "raw_response": response_obj,
    }


def approve(
    manifest: dict[str, Any],
    prompt_bytes: bytes,
    approved: dict[str, Any],
) -> bool:
    print("\n=== DME LOCAL AUTHORITY REQUEST ===")
    print(f"request_id : {manifest['request_id']}")
    print(f"capability : {approved['capability_id']}")
    print(f"approval   : {approved['approval_id']}")
    print(f"principal  : {approved['principal_id']} (DECLARED, NOT AUTHENTICATED)")
    print(f"purpose    : {manifest['purpose']}")
    print(f"request_sha: {approved['request_sha256']}")
    print(f"model      : {approved['model']}")
    print(f"source_ref : {manifest['source_ref']}")
    print(f"input_path : {manifest['input_path']}")
    if manifest["schema_version"] == "LOCAL_INVOCATION_REQUEST_V0_1":
        print(f"input_blob : {manifest['input_blob_sha']}")
    print(f"input_sha  : {approved['input_sha256']}")
    print(f"bytes      : {len(prompt_bytes)}")
    print(f"temperature: {approved['temperature']}")
    print(f"max_tokens : {approved['max_tokens']}")
    print(f"endpoint   : {approved['endpoint_identity']}")
    print(f"executor   : {approved['executor_sha256']}")
    print(f"policy     : {approved['policy_sha256']}")
    print("tools      : NONE")
    print("history    : NONE")
    print("network    : localhost LM Studio only")
    return input("Authorize this invocation? [y/N] ").strip().lower() == "y"


def emit_authority_decision(witness: dict[str, Any]) -> None:
    print(
        "[AUTHORITY] "
        + json.dumps(witness, sort_keys=True, separators=(",", ":"))
    )


def process_once(
    p: dict[str, Any],
    attempting_principal_id: str,
    execution_candidate_provider: Callable[[dict[str, Any], bytes], bytes] = default_execution_candidate_provider,
    revalidation_witness_sink: Callable[[dict[str, Any]], None] = emit_revalidation_witness,
    authority_decision_sink: Callable[[dict[str, Any]], None] = emit_authority_decision,
    authority_store: authority_consumption.LocalAuthorityStateStore | None = None,
    authority_clock: Callable[[], str] = now_iso,
    authority_id_factory: Callable[[], tuple[str, str]] = fresh_authority_ids,
    authority_consumer: Callable[..., dict[str, Any]] = authority_consumption.consume_authority_once,
) -> int:
    verify_authority_module_identity()
    if not isinstance(attempting_principal_id, str) or not REQUEST_ID_RE.fullmatch(
        attempting_principal_id
    ):
        raise ValueError("invalid attempting principal_id")
    if authority_store is None:
        authority_store = authority_consumption.LocalAuthorityStateStore()

    repo = Path(p["_repo_root_resolved"])
    remote_head = fetch_remote(repo, p)
    executed = 0

    for request_path in list_request_paths(repo, remote_head, p):
        try:
            raw_manifest = git_show(repo, remote_head, request_path)
            manifest_sha = sha256_bytes(raw_manifest)
            manifest = parse_manifest(raw_manifest)
            validate_manifest(manifest, p)
        except Exception as e:
            print(f"[REJECT] {request_path}: {e}")
            continue

        if not manifest["enabled"]:
            continue

        out_path = result_path_for(manifest["request_id"], p)
        if out_path.exists():
            continue

        try:
            observed_blob_sha = resolve_git_blob_sha(
                repo, manifest["source_ref"], manifest["input_path"]
            )
            reviewed_prompt_bytes = git_blob_bytes(repo, observed_blob_sha)
        except Exception as e:
            print(f"[REJECT] {request_path}: immutable prompt unavailable: {e}")
            continue

        observed_sha = sha256_bytes(reviewed_prompt_bytes)
        if manifest["schema_version"] == "LOCAL_INVOCATION_REQUEST_V0":
            if observed_sha != manifest["input_sha256"]:
                print(
                    f"[REJECT] {request_path}: input SHA mismatch "
                    f"(expected {manifest['input_sha256']}, got {observed_sha})"
                )
                continue
        else:
            if observed_blob_sha != manifest["input_blob_sha"]:
                print(
                    f"[REJECT] {request_path}: input blob mismatch "
                    f"(expected {manifest['input_blob_sha']}, got {observed_blob_sha})"
                )
                continue

        if len(reviewed_prompt_bytes) > int(p["max_prompt_bytes"]):
            print(f"[REJECT] {request_path}: prompt exceeds size ceiling")
            continue
        try:
            reviewed_prompt_bytes.decode("utf-8")
        except UnicodeDecodeError:
            print(f"[REJECT] {request_path}: prompt is not UTF-8")
            continue

        capability_id, approval_id = authority_id_factory()
        approved_manifest = copy.deepcopy(manifest)
        approved = build_approval_candidate(
            approved_manifest,
            manifest_sha,
            reviewed_prompt_bytes,
            p,
            capability_id,
            approval_id,
        )

        if not approve(manifest, reviewed_prompt_bytes, approved):
            print(f"[SKIP] {manifest['request_id']}: local authorization denied")
            continue

        execution_candidate_bytes = execution_candidate_provider(
            manifest, reviewed_prompt_bytes
        )
        if not isinstance(execution_candidate_bytes, bytes):
            print(f"[REJECT] {manifest['request_id']}: execution candidate must be bytes")
            continue

        revalidation = postapproval_revalidation_witness(
            manifest,
            manifest_sha,
            reviewed_prompt_bytes,
            execution_candidate_bytes,
        )
        if revalidation is not None:
            revalidation_witness_sink(revalidation)
            continue

        coordinate_revalidation = postapproval_coordinate_revalidation_witness(
            manifest,
            approved_manifest,
            execution_candidate_bytes,
            p,
            approved,
        )
        if coordinate_revalidation is not None:
            revalidation_witness_sink(coordinate_revalidation)
            continue

        envelope = mint_authority_envelope(approved, authority_clock())
        try:
            authority_store.issue(envelope)
            authority_result = authority_consumer(
                envelope,
                attempting_principal_id=attempting_principal_id,
                store=authority_store,
                invoke=lambda: invoke_lmstudio(
                    manifest,
                    execution_candidate_bytes,
                    manifest_sha,
                    p,
                    request_path,
                ),
                clock=authority_clock,
            )
        except Exception as e:
            print(f"[ERROR] {manifest['request_id']}: {e}")
            continue

        if authority_result.get("decision") != "INVOKED":
            authority_decision_sink(authority_result["witness"])
            continue
        witness = authority_result["invocation_result"]

        out_path.write_text(
            json.dumps(witness, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[OK] wrote {out_path}")
        executed += 1

    return executed


def print_identity(p: dict[str, Any]) -> None:
    bridge_path = Path(__file__).resolve()
    authority_module_sha256 = verify_authority_module_identity()
    print("DME LOCAL TRUST ROOT")
    print(f"executor : {bridge_path}")
    print(f"executor_sha256 : {sha256_bytes(bridge_path.read_bytes())}")
    print(f"policy   : {POLICY_PATH}")
    print(f"policy_sha256   : {sha256_bytes(POLICY_PATH.read_bytes())}")
    print(f"authority_module : {AUTHORITY_MODULE_PATH}")
    print(f"authority_module_sha256 : {authority_module_sha256}")
    print(f"repo     : {p['_repo_root_resolved']}")
    print("authority: LOCAL PINNED V0 / HUMAN APPROVAL REQUIRED")
    print("cell001  : POST-APPROVAL INPUT IDENTITY REVALIDATION ENABLED")
    print("cell002  : PRINCIPAL-BOUND ONE-SHOT AUTHORITY CONSUMPTION ENABLED")
    print("cell003  : GIT-BLOB INPUT IDENTITY V0.1 ENABLED; V0 COMPATIBLE")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true")
    mode.add_argument("--watch", action="store_true")
    mode.add_argument("--identity", action="store_true")
    parser.add_argument("--principal-id")
    parser.add_argument("--poll-seconds", type=int, default=120)
    args = parser.parse_args()

    p = load_policy()
    if args.identity:
        print_identity(p)
        return 0
    if not isinstance(args.principal_id, str) or not REQUEST_ID_RE.fullmatch(
        args.principal_id
    ):
        print("--principal-id with bounded identity syntax is required", file=sys.stderr)
        return 2
    if args.once:
        process_once(p, args.principal_id)
        return 0
    if args.poll_seconds < 30:
        print("poll interval must be at least 30 seconds", file=sys.stderr)
        return 2

    print_identity(p)
    print("\nWatching remote request queue.")
    while True:
        try:
            process_once(p, args.principal_id)
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            print(f"[WATCH ERROR] {e}", file=sys.stderr)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
