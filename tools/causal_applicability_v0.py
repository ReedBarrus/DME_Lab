#!/usr/bin/env python3
"""CAUSAL_APPLICABILITY_001 exact-head evaluator.

The evaluator does not mutate realizations, actor memory, authority state, or
successor state. It emits a separate applicability judgment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

SCHEMA_REALIZATION = "causal_applicability_realization_v0"
SCHEMA_JUDGMENT = "causal_applicability_judgment_v0"
RULE = "EXACT_GIT_HEAD_EQUALITY_v0"
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


class CausalApplicabilityError(ValueError):
    pass


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def realization_sha256(realization: dict[str, Any]) -> str:
    validate_realization(realization)
    return hashlib.sha256(_canonical_bytes(realization)).hexdigest()


def validate_realization(realization: dict[str, Any]) -> None:
    required = {
        "schema",
        "realization_id",
        "realization_kind",
        "realization_basis",
        "mechanical_result",
        "payload_ref",
    }
    if set(realization) != required:
        raise CausalApplicabilityError(
            "realization fields differ from causal_applicability_realization_v0"
        )
    if realization["schema"] != SCHEMA_REALIZATION:
        raise CausalApplicabilityError("unexpected realization schema")
    if not isinstance(realization["realization_id"], str) or not realization["realization_id"]:
        raise CausalApplicabilityError("realization_id must be non-empty")
    if not isinstance(realization["realization_kind"], str) or not realization["realization_kind"]:
        raise CausalApplicabilityError("realization_kind must be non-empty")
    if not isinstance(realization["payload_ref"], str) or not realization["payload_ref"]:
        raise CausalApplicabilityError("payload_ref must be non-empty")
    basis = realization["realization_basis"]
    if not isinstance(basis, str) or _SHA1_RE.fullmatch(basis) is None:
        raise CausalApplicabilityError("realization_basis must be a lowercase 40-hex Git commit")
    if realization["mechanical_result"] not in {"PASS", "FAIL"}:
        raise CausalApplicabilityError("mechanical_result must be PASS or FAIL")


def judge(
    realization: dict[str, Any],
    comparison_basis: str,
    judgment_id: str,
) -> dict[str, Any]:
    """Return a separate exact-head applicability judgment.

    No input object is mutated. APPLICABLE says only that the comparison Git
    commit exactly equals the realization basis under v0.
    """
    validate_realization(realization)
    if _SHA1_RE.fullmatch(comparison_basis) is None:
        raise CausalApplicabilityError(
            "comparison_basis must be a lowercase 40-hex Git commit"
        )
    if not judgment_id:
        raise CausalApplicabilityError("judgment_id must be non-empty")

    result = (
        "APPLICABLE"
        if comparison_basis == realization["realization_basis"]
        else "STALE"
    )

    return {
        "schema": SCHEMA_JUDGMENT,
        "judgment_id": judgment_id,
        "realization_id": realization["realization_id"],
        "realization_sha256": realization_sha256(realization),
        "realization_basis": realization["realization_basis"],
        "comparison_basis": comparison_basis,
        "rule": RULE,
        "result": result,
        "authority_effect": "NONE",
        "admission_effect": "NONE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--realization", required=True)
    parser.add_argument("--comparison-basis", required=True)
    parser.add_argument("--judgment-id", required=True)
    args = parser.parse_args(argv)

    realization = json.loads(Path(args.realization).read_text(encoding="utf-8"))
    if not isinstance(realization, dict):
        raise CausalApplicabilityError("realization file must contain a JSON object")

    result = judge(realization, args.comparison_basis, args.judgment_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
