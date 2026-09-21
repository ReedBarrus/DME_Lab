#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "legacy_lane_succession_fencing_pressure_v0"
RESULT_SCHEMA = "legacy_lane_succession_fencing_result_v0"

class SuccessionError(RuntimeError):
    pass

def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SuccessionError("root must be object")
    return value

def identity(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def _set_overlap(a: list[str], b: list[str]) -> bool:
    return bool(set(a) & set(b))

def _validate_fence(fence: dict[str, Any], predecessor: dict[str, Any], debt_identity: str) -> bool:
    required = {
        "fence_id", "predecessor_instance_id", "predecessor_head",
        "predecessor_claim_id", "predecessor_claim_blob",
        "predecessor_invocation_id", "predecessor_lane_manifest_blob",
        "predecessor_guard_receipt_blob", "predecessor_debt_identity",
        "effect", "historical_disposition_effect", "authority_effect",
        "history_rewrite_effect"
    }
    if not isinstance(fence, dict) or set(fence) != required:
        return False
    return (
        fence["predecessor_instance_id"] == predecessor["instance_id"]
        and fence["predecessor_head"] == predecessor["head"]
        and fence["predecessor_claim_id"] == predecessor["claim_id"]
        and fence["predecessor_claim_blob"] == predecessor["claim_blob"]
        and fence["predecessor_invocation_id"] == predecessor["invocation_id"]
        and fence["predecessor_lane_manifest_blob"] == predecessor["lane_manifest_blob"]
        and fence["predecessor_guard_receipt_blob"] == predecessor["pre_mutation_guard_blob"]
        and fence["predecessor_debt_identity"] == debt_identity
        and fence["effect"] == "FUTURE_EFFECT_EXCLUSION_ONLY"
        and fence["historical_disposition_effect"] == "NONE"
        and fence["authority_effect"] == "NONE"
        and fence["history_rewrite_effect"] == "NONE"
    )

def evaluate_cell(
    cell_id: str,
    cell: dict[str, Any],
    predecessor: dict[str, Any],
    debt_identity: str,
    fences: dict[str, Any],
) -> dict[str, Any]:
    if set(cell) != {"observed_predecessor_head", "fence_registry", "prose_retired", "attempt"}:
        raise SuccessionError(f"{cell_id}: cell fields must be exact")
    registry = cell["fence_registry"]
    attempt = cell["attempt"]
    if not isinstance(registry, list) or len(registry) != len(set(registry)):
        raise SuccessionError(f"{cell_id}: fence_registry must be unique list")
    if not isinstance(attempt, dict):
        raise SuccessionError(f"{cell_id}: attempt must be object")

    effective = []
    invalid = []
    for name in registry:
        if name not in fences:
            raise SuccessionError(f"{cell_id}: unknown fence registry entry")
        fence = fences[name]
        if _validate_fence(fence, predecessor, debt_identity):
            effective.append((name, fence))
        else:
            invalid.append(name)
    if len(effective) > 1:
        return {
            "decision": "ADMINISTRATION_INVALID",
            "reason": "MULTIPLE_EFFECTIVE_FENCES",
            "predecessor_currently_operative": None,
            "coordination_posture": "NOT_EVALUATED",
            "consulted_fence_identity": None,
            "semantic_overlap": None,
            "provenance_overlap": None,
        }

    fence_name = effective[0][0] if effective else None
    fence = effective[0][1] if effective else None
    fence_identity = identity(fence) if fence else None

    # Fence basis invalidation is prior to every other successor decision.
    if fence and cell["observed_predecessor_head"] != fence["predecessor_head"]:
        return {
            "decision": "CONFLICT_STOP",
            "reason": "PREDECESSOR_ADVANCED_AFTER_FENCE",
            "predecessor_currently_operative": None,
            "coordination_posture": "NOT_EVALUATED",
            "consulted_fence_identity": fence_identity,
            "semantic_overlap": None,
            "provenance_overlap": None,
        }

    predecessor_currently_operative = (
        predecessor["claim_status"] == "ACTIVE" and fence is None
    )

    addresses_predecessor = (
        attempt.get("instance_id") == predecessor["instance_id"]
        or attempt.get("claim_id") == predecessor["claim_id"]
        or attempt.get("invocation_id") == predecessor["invocation_id"]
    )

    # Exact fenced predecessor coordinates cannot become operative.
    if fence and addresses_predecessor:
        return {
            "decision": "REJECT",
            "reason": "PREDECESSOR_FENCED",
            "predecessor_currently_operative": False,
            "coordination_posture": "NOT_EVALUATED",
            "consulted_fence_identity": fence_identity,
            "semantic_overlap": None,
            "provenance_overlap": None,
        }

    semantic_overlap = _set_overlap(
        attempt.get("semantic_surfaces", []),
        predecessor["semantic_surfaces"],
    )
    provenance_overlap = (
        attempt.get("target_lineage") == predecessor["target_lineage"]
        and attempt.get("consequence_envelope_id") == predecessor["consequence_envelope_id"]
        and _set_overlap(attempt.get("artifact_scopes", []), predecessor["artifact_scopes"])
    )

    # Current operability is derived before ordinary overlap coordination.
    # A historically ACTIVE but effectively fenced predecessor is excluded.
    if (
        attempt.get("kind") == "SUCCESSOR"
        and attempt.get("claim_status") == "ACTIVE"
        and predecessor_currently_operative
        and (semantic_overlap or provenance_overlap)
    ):
        return {
            "decision": "COORDINATION_HOLD",
            "reason": "ACTIVE_PREDECESSOR_OVERLAP",
            "predecessor_currently_operative": True,
            "coordination_posture": "COORDINATION_HOLD",
            "consulted_fence_identity": None,
            "semantic_overlap": semantic_overlap,
            "provenance_overlap": provenance_overlap,
        }

    coordination_posture = (
        "NO_COORDINATION_BLOCK"
        if attempt.get("kind") == "SUCCESSOR"
        else "NOT_APPLICABLE"
    )

    if attempt.get("kind") == "SUCCESSOR":
        if (
            fence is None
            or attempt.get("predecessor_fence_ref") != fence_identity
            or attempt.get("predecessor_debt_ref") != debt_identity
        ):
            return {
                "decision": "REJECT",
                "reason": "PREDECESSOR_DEBT_REFERENCE_REQUIRED",
                "predecessor_currently_operative": predecessor_currently_operative,
                "coordination_posture": coordination_posture,
                "consulted_fence_identity": fence_identity,
                "semantic_overlap": semantic_overlap,
                "provenance_overlap": provenance_overlap,
            }
        if attempt.get("authority_origin") == "PREDECESSOR":
            return {
                "decision": "REJECT",
                "reason": "AUTHORITY_INHERITANCE_FORBIDDEN",
                "predecessor_currently_operative": False,
                "coordination_posture": coordination_posture,
                "consulted_fence_identity": fence_identity,
                "semantic_overlap": semantic_overlap,
                "provenance_overlap": provenance_overlap,
            }
        if not attempt.get("fresh_basis") or not attempt.get("fresh_coordination"):
            return {
                "decision": "REJECT",
                "reason": "FRESH_SUCCESSOR_BASIS_REQUIRED",
                "predecessor_currently_operative": False,
                "coordination_posture": coordination_posture,
                "consulted_fence_identity": fence_identity,
                "semantic_overlap": semantic_overlap,
                "provenance_overlap": provenance_overlap,
            }
        return {
            "decision": "NORMAL_ADMISSIBILITY_MEMBRANE",
            "reason": "SUCCESSOR_FRESHNESS_AND_DEBT_CONSERVATION_SATISFIED",
            "predecessor_currently_operative": False,
            "coordination_posture": coordination_posture,
            "consulted_fence_identity": fence_identity,
            "semantic_overlap": semantic_overlap,
            "provenance_overlap": provenance_overlap,
        }

    return {
        "decision": "NORMAL_ADMISSIBILITY_MEMBRANE",
        "reason": "NO_OPERATIVE_FENCE_RELATION",
        "predecessor_currently_operative": predecessor_currently_operative,
        "coordination_posture": coordination_posture,
        "consulted_fence_identity": fence_identity,
        "semantic_overlap": semantic_overlap,
        "provenance_overlap": provenance_overlap,
    }

def qualify(fixtures: dict[str, Any]) -> dict[str, Any]:
    if fixtures.get("schema") != SCHEMA:
        raise SuccessionError("wrong fixture schema")
    predecessor = fixtures.get("predecessor")
    debt = fixtures.get("predecessor_debt")
    fences = fixtures.get("fences")
    cells = fixtures.get("cells")
    if not all(isinstance(v, dict) for v in (predecessor, debt, fences, cells)):
        raise SuccessionError("predecessor, debt, fences, and cells must be objects")

    predecessor_identity = identity(predecessor)
    debt_identity = identity(debt)
    fence_identities = {name: identity(value) for name, value in fences.items()}
    observed = {
        cid: evaluate_cell(cid, cell, predecessor, debt_identity, fences)
        for cid, cell in cells.items()
    }
    return {
        "schema": RESULT_SCHEMA,
        "object_id": "LEGACY_LANE_SUCCESSION_FENCING_001",
        "predecessor_identity": predecessor_identity,
        "predecessor_debt_identity": debt_identity,
        "fence_identities": fence_identities,
        "cells": observed,
        "live_lane_mutation": "NONE",
        "predecessor_disposition": "UNCHANGED",
        "successor_activation": "NONE",
        "authority_effect": "NONE",
        "merge": "NONE",
        "stop": "YES",
    }

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("fixtures")
    args = p.parse_args()
    print(json.dumps(qualify(load_json(args.fixtures)), indent=2, sort_keys=True))
