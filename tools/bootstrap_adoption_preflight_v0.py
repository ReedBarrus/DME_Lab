#!/usr/bin/env python3
"""Mechanical preflight for BOOTSTRAP_ADOPTION_001.

This tool does not merge, authorize, adopt, or write a receipt.
It derives a bootstrap_adoption_preflight_v0 witness from exact local bytes
and Git repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

EVENT_ID = "BOOTSTRAP_ADOPTION_001"
PROTOCOL_OBJECT_ID = "PROMOTION_PROTOCOL_v0"
PROTOCOL_PATH = "docs/operations/PROMOTION_PROTOCOL_v0.md"
BOOTSTRAP_OBJECT_PATH = (
    "lab/ops/promotions/BOOTSTRAP_ADOPTION_001/bootstrap_adoption_object_v0.json"
)
EXPECTED_PROTOCOL_BLOB = "c6cebdc70c07816167ff9499b5690fcb16b4354e"
TARGET_REPOSITORY = "ReedBarrus/DME_Lab"
TARGET_REF = "main"
WORK_REF = "promotion-protocol-v0"
PULL_REQUEST = 30
PREFLIGHT_IMPLEMENTATION_PATH = "tools/bootstrap_adoption_preflight_v0.py"


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def read_bytes(root: Path, relative: str) -> bytes:
    return (root / relative).read_bytes()


def read_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads(read_bytes(root, relative).decode("utf-8"))


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def git_head(root: Path, ref: str) -> str:
    return git(root, "rev-parse", ref).stdout.strip()


def path_present_at_ref(root: Path, ref: str, path: str) -> bool:
    result = git(root, "cat-file", "-e", f"{ref}:{path}", check=False)
    return result.returncode == 0


def pf(value: bool) -> str:
    return "PASS" if value else "FAIL"


def build_preflight(
    root: Path,
    review_path: str,
    authorization_path: str,
    target_ref: str,
    work_ref: str,
) -> dict[str, Any]:
    protocol_bytes = read_bytes(root, PROTOCOL_PATH)
    bootstrap_bytes = read_bytes(root, BOOTSTRAP_OBJECT_PATH)
    review_bytes = read_bytes(root, review_path)
    authorization_bytes = read_bytes(root, authorization_path)
    preflight_implementation_bytes = read_bytes(root, PREFLIGHT_IMPLEMENTATION_PATH)

    protocol_blob = git_blob_sha(protocol_bytes)
    bootstrap_blob = git_blob_sha(bootstrap_bytes)
    review_blob = git_blob_sha(review_bytes)
    authorization_blob = git_blob_sha(authorization_bytes)
    preflight_implementation_blob = git_blob_sha(preflight_implementation_bytes)

    bootstrap = json.loads(bootstrap_bytes.decode("utf-8"))
    review = json.loads(review_bytes.decode("utf-8"))
    authorization = json.loads(authorization_bytes.decode("utf-8"))

    observed_target_head = git_head(root, target_ref)
    observed_pr_head = git_head(root, work_ref)
    protocol_present_on_target = path_present_at_ref(root, target_ref, PROTOCOL_PATH)

    preflight_implementation_matches_bootstrap = (
        bootstrap.get("preflight", {}).get("implementation_path")
        == PREFLIGHT_IMPLEMENTATION_PATH
        and bootstrap.get("preflight", {}).get("implementation_git_blob_sha")
        == preflight_implementation_blob
    )

    protocol_matches_bootstrap = (
        protocol_blob == EXPECTED_PROTOCOL_BLOB
        and bootstrap.get("event_id") == EVENT_ID
        and bootstrap.get("object", {}).get("object_id") == PROTOCOL_OBJECT_ID
        and bootstrap.get("object", {}).get("path") == PROTOCOL_PATH
        and bootstrap.get("object", {}).get("git_blob_sha") == protocol_blob
    )

    review_matches_protocol = (
        review.get("event_id") == EVENT_ID
        and review.get("protocol_object_id") == PROTOCOL_OBJECT_ID
        and review.get("protocol_path") == PROTOCOL_PATH
        and review.get("protocol_git_blob_sha") == protocol_blob
    )
    review_matches_bootstrap = (
        review.get("bootstrap_object_git_blob_sha") == bootstrap_blob
    )
    review_independence_valid = (
        review.get("schema") == "bootstrap_adoption_review_v0"
        and review.get("independence", {}).get("protocol_author") is False
        and review.get("independence", {}).get("bootstrap_object_author") is False
    )

    authorization_matches_protocol = (
        authorization.get("schema") == "bootstrap_adoption_authorization_v0"
        and authorization.get("event_id") == EVENT_ID
        and authorization.get("protocol_object_id") == PROTOCOL_OBJECT_ID
        and authorization.get("protocol_path") == PROTOCOL_PATH
        and authorization.get("protocol_git_blob_sha") == protocol_blob
    )
    authorization_matches_bootstrap = (
        authorization.get("bootstrap_object_git_blob_sha") == bootstrap_blob
    )
    authorization_matches_review = (
        authorization.get("review_git_blob_sha") == review_blob
        and authorization.get("review_disposition") == review.get("disposition")
        and review.get("disposition") == "ADMIT"
    )

    authorization_effect_matches = (
        authorization.get("authorized_effect")
        == "ADOPT_EXACT_PROMOTION_PROTOCOL_v0_AS_DURABLE_OPERATING_PROCEDURE"
    )

    target = authorization.get("target", {})
    target_matches_authorization = (
        target.get("repository") == TARGET_REPOSITORY
        and target.get("target_ref") == TARGET_REF
        and target.get("pull_request") == PULL_REQUEST
        and target_ref == TARGET_REF
        and work_ref == WORK_REF
    )
    target_head_matches_authorization = (
        target.get("authorized_target_head") == observed_target_head
    )
    pr_head_matches_authorization = (
        target.get("authorized_pr_head") == observed_pr_head
    )

    identity_checks = {
        "preflight_implementation_matches_bootstrap_object": pf(preflight_implementation_matches_bootstrap),
        "protocol_matches_bootstrap_object": pf(protocol_matches_bootstrap),
        "review_matches_protocol": pf(review_matches_protocol),
        "review_matches_bootstrap_object": pf(review_matches_bootstrap),
        "review_independence_valid": pf(review_independence_valid),
        "authorization_matches_protocol": pf(authorization_matches_protocol),
        "authorization_matches_bootstrap_object": pf(authorization_matches_bootstrap),
        "authorization_matches_review": pf(authorization_matches_review),
        "authorization_effect_matches": pf(authorization_effect_matches),
        "target_matches_authorization": pf(target_matches_authorization),
        "target_head_matches_authorization": pf(target_head_matches_authorization),
        "pr_head_matches_authorization": pf(pr_head_matches_authorization),
    }

    observed_precondition = "FALSE" if protocol_present_on_target else "TRUE"

    all_identity_pass = all(v == "PASS" for v in identity_checks.values())
    review_admit = review.get("disposition") == "ADMIT"
    authorization_authorize = authorization.get("decision") == "AUTHORIZE"

    result = (
        "PASS"
        if all_identity_pass
        and review_admit
        and authorization_authorize
        and observed_precondition == "TRUE"
        else "FAIL"
    )

    return {
        "schema": "bootstrap_adoption_preflight_v0",
        "event_id": EVENT_ID,
        "protocol_object_id": PROTOCOL_OBJECT_ID,
        "protocol_path": PROTOCOL_PATH,
        "protocol_git_blob_sha": protocol_blob,
        "bootstrap_object_git_blob_sha": bootstrap_blob,
        "review_git_blob_sha": review_blob,
        "authorization_git_blob_sha": authorization_blob,
        "preflight_implementation_git_blob_sha": preflight_implementation_blob,
        "review_disposition": review.get("disposition", "HOLD"),
        "authorization_decision": authorization.get("decision", "DENY"),
        "target": {
            "repository": TARGET_REPOSITORY,
            "target_ref": TARGET_REF,
            "pull_request": PULL_REQUEST,
            "authorized_target_head": target.get("authorized_target_head", "0" * 40),
            "observed_target_head": observed_target_head,
            "authorized_pr_head": target.get("authorized_pr_head", "0" * 40),
            "observed_pr_head": observed_pr_head,
        },
        "observed_precondition": observed_precondition,
        "identity_checks": identity_checks,
        "repository_witness": {
            "observed_main_head": observed_target_head,
            "protocol_path_present_on_main": protocol_present_on_target,
            "witness_method": (
                f"git rev-parse {target_ref}; "
                f"git cat-file -e {target_ref}:{PROTOCOL_PATH}; "
                f"git rev-parse {work_ref}"
            ),
        },
        "result": result,
        "execution_admitted": result == "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--review", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--target-ref", default=TARGET_REF)
    parser.add_argument("--work-ref", default=WORK_REF)
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    try:
        record = build_preflight(
            root,
            args.review,
            args.authorization,
            args.target_ref,
            args.work_ref,
        )
    except Exception as exc:
        failure = {
            "administration": "INVALID",
            "event_id": EVENT_ID,
            "reason": f"{type(exc).__name__}: {exc}",
            "execution_admitted": False,
        }
        print(json.dumps(failure, sort_keys=True, separators=(",", ":")))
        return 2

    rendered = json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if record["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
