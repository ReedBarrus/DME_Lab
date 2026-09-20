#!/usr/bin/env python3
"""Terminal chain verifier for BOOTSTRAP_ADOPTION_001.

This tool does not create authority, run adoption, merge, or mutate a receipt.
It derives Git-blob identities from supplied bytes and checks that a bootstrap
receipt conserves the exact administration chain that preceded it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EVENT_ID = "BOOTSTRAP_ADOPTION_001"
PROTOCOL_OBJECT_ID = "PROMOTION_PROTOCOL_v0"
PROTOCOL_PATH = "docs/operations/PROMOTION_PROTOCOL_v0.md"
BOOTSTRAP_OBJECT_PATH = (
    "lab/ops/promotions/BOOTSTRAP_ADOPTION_001/bootstrap_adoption_object_v0.json"
)
PREFLIGHT_IMPLEMENTATION_PATH = "tools/bootstrap_adoption_preflight_v0.py"
VERIFIER_IMPLEMENTATION_PATH = "tools/bootstrap_adoption_receipt_verifier_v0.py"


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def read_bytes(root: Path, relative: str) -> bytes:
    return (root / relative).read_bytes()


def parse_json(data: bytes) -> dict[str, Any]:
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def pf(value: bool) -> str:
    return "PASS" if value else "FAIL"


def verify_chain(
    root: Path,
    review_path: str,
    authorization_path: str,
    preflight_path: str,
    receipt_path: str,
) -> dict[str, Any]:
    protocol_bytes = read_bytes(root, PROTOCOL_PATH)
    bootstrap_bytes = read_bytes(root, BOOTSTRAP_OBJECT_PATH)
    review_bytes = read_bytes(root, review_path)
    authorization_bytes = read_bytes(root, authorization_path)
    preflight_bytes = read_bytes(root, preflight_path)
    receipt_bytes = read_bytes(root, receipt_path)
    preflight_impl_bytes = read_bytes(root, PREFLIGHT_IMPLEMENTATION_PATH)
    verifier_impl_bytes = read_bytes(root, VERIFIER_IMPLEMENTATION_PATH)

    protocol_blob = git_blob_sha(protocol_bytes)
    bootstrap_blob = git_blob_sha(bootstrap_bytes)
    review_blob = git_blob_sha(review_bytes)
    authorization_blob = git_blob_sha(authorization_bytes)
    preflight_blob = git_blob_sha(preflight_bytes)
    receipt_blob = git_blob_sha(receipt_bytes)
    preflight_impl_blob = git_blob_sha(preflight_impl_bytes)
    verifier_impl_blob = git_blob_sha(verifier_impl_bytes)

    bootstrap = parse_json(bootstrap_bytes)
    review = parse_json(review_bytes)
    authorization = parse_json(authorization_bytes)
    preflight = parse_json(preflight_bytes)
    receipt = parse_json(receipt_bytes)

    object_identity = bootstrap.get("object", {})
    object_preflight = bootstrap.get("preflight", {})
    object_verifier = bootstrap.get("terminal_chain_verifier", {})

    protocol_matches_bootstrap_object = (
        bootstrap.get("event_id") == EVENT_ID
        and object_identity.get("object_id") == PROTOCOL_OBJECT_ID
        and object_identity.get("path") == PROTOCOL_PATH
        and object_identity.get("git_blob_sha") == protocol_blob
    )

    preflight_implementation_matches_bootstrap_object = (
        object_preflight.get("implementation_path") == PREFLIGHT_IMPLEMENTATION_PATH
        and object_preflight.get("implementation_git_blob_sha") == preflight_impl_blob
    )

    verifier_implementation_matches_bootstrap_object = (
        object_verifier.get("implementation_path") == VERIFIER_IMPLEMENTATION_PATH
        and object_verifier.get("implementation_git_blob_sha") == verifier_impl_blob
    )

    review_matches_chain = (
        review.get("schema") == "bootstrap_adoption_review_v0"
        and review.get("event_id") == EVENT_ID
        and review.get("protocol_object_id") == PROTOCOL_OBJECT_ID
        and review.get("protocol_path") == PROTOCOL_PATH
        and review.get("protocol_git_blob_sha") == protocol_blob
        and review.get("bootstrap_object_git_blob_sha") == bootstrap_blob
        and review.get("disposition") == "ADMIT"
    )

    authorization_matches_chain = (
        authorization.get("schema") == "bootstrap_adoption_authorization_v0"
        and authorization.get("event_id") == EVENT_ID
        and authorization.get("protocol_object_id") == PROTOCOL_OBJECT_ID
        and authorization.get("protocol_path") == PROTOCOL_PATH
        and authorization.get("protocol_git_blob_sha") == protocol_blob
        and authorization.get("bootstrap_object_git_blob_sha") == bootstrap_blob
        and authorization.get("review_git_blob_sha") == review_blob
        and authorization.get("review_disposition") == "ADMIT"
        and authorization.get("decision") == "AUTHORIZE"
    )

    preflight_matches_chain = (
        preflight.get("schema") == "bootstrap_adoption_preflight_v0"
        and preflight.get("event_id") == EVENT_ID
        and preflight.get("protocol_object_id") == PROTOCOL_OBJECT_ID
        and preflight.get("protocol_path") == PROTOCOL_PATH
        and preflight.get("protocol_git_blob_sha") == protocol_blob
        and preflight.get("bootstrap_object_git_blob_sha") == bootstrap_blob
        and preflight.get("review_git_blob_sha") == review_blob
        and preflight.get("authorization_git_blob_sha") == authorization_blob
        and preflight.get("preflight_implementation_git_blob_sha")
        == preflight_impl_blob
    )

    receipt_matches_chain = (
        receipt.get("schema") == "bootstrap_adoption_receipt_v0"
        and receipt.get("event_id") == EVENT_ID
        and receipt.get("protocol_object_id") == PROTOCOL_OBJECT_ID
        and receipt.get("protocol_path") == PROTOCOL_PATH
        and receipt.get("protocol_git_blob_sha") == protocol_blob
        and receipt.get("bootstrap_object_git_blob_sha") == bootstrap_blob
        and receipt.get("review_git_blob_sha") == review_blob
        and receipt.get("authorization_git_blob_sha") == authorization_blob
        and receipt.get("preflight_git_blob_sha") == preflight_blob
        and receipt.get("preflight_result") == preflight.get("result")
        and receipt.get("terminal_chain_verification_required") is True
        and receipt.get("terminal_chain_verifier_git_blob_sha")
        == verifier_impl_blob
    )

    checks = {
        "protocol_matches_bootstrap_object": pf(protocol_matches_bootstrap_object),
        "preflight_implementation_matches_bootstrap_object": pf(
            preflight_implementation_matches_bootstrap_object
        ),
        "verifier_implementation_matches_bootstrap_object": pf(
            verifier_implementation_matches_bootstrap_object
        ),
        "review_matches_protocol_and_bootstrap_object": pf(review_matches_chain),
        "authorization_matches_review_protocol_and_bootstrap_object": pf(
            authorization_matches_chain
        ),
        "preflight_matches_authorization_review_protocol_and_bootstrap_object": pf(
            preflight_matches_chain
        ),
        "receipt_matches_exact_administration_chain": pf(receipt_matches_chain),
    }

    result = "PASS" if all(v == "PASS" for v in checks.values()) else "FAIL"

    return {
        "schema": "bootstrap_adoption_receipt_verification_v0",
        "event_id": EVENT_ID,
        "protocol_object_id": PROTOCOL_OBJECT_ID,
        "protocol_path": PROTOCOL_PATH,
        "derived": {
            "protocol_git_blob_sha": protocol_blob,
            "bootstrap_object_git_blob_sha": bootstrap_blob,
            "review_git_blob_sha": review_blob,
            "authorization_git_blob_sha": authorization_blob,
            "preflight_git_blob_sha": preflight_blob,
            "receipt_git_blob_sha": receipt_blob,
            "preflight_implementation_git_blob_sha": preflight_impl_blob,
            "verifier_implementation_git_blob_sha": verifier_impl_blob,
        },
        "checks": checks,
        "result": result,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--review", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    try:
        record = verify_chain(
            root,
            args.review,
            args.authorization,
            args.preflight,
            args.receipt,
        )
    except Exception as exc:
        failure = {
            "administration": "INVALID",
            "event_id": EVENT_ID,
            "reason": f"{type(exc).__name__}: {exc}",
            "result": "FAIL",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
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
