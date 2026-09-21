#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.legacy_lane_succession_fencing_v0 import evaluate_cell, identity
LIVE_FENCE_PATH = ROOT / "coordination/predecessor_fences/LANE_B_LEGACY_INSTANCE_001.json"
QUALIFIED_EVALUATOR_BLOB = "9b17d812e8a8c339f4a952b8fed05f17cb37e1b0"
QUALIFIED_FENCE_IDENTITY = "sha256:2cced34cedccb4d763031fdfe3b271a8146473f9995b437fb9f0b894f0fabb86"
QUALIFIED_DEBT_IDENTITY = "sha256:b42da029e9d0daccb6a486150e420cde5510c023ffe9b6bcd73a3b5ad4a399d5"
QUALIFIED_PREDECESSOR_IDENTITY = "sha256:5b443ba71741f9ed5745035f5db4bfb88e3a9f599572be608da4e2d5764f4672"


class LiveFenceError(RuntimeError):
    pass


def load_live_fence(path: Path = LIVE_FENCE_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LiveFenceError("live fence must be object")
    return value


def validate_live_fence(doc: dict[str, Any]) -> dict[str, str]:
    if doc.get("schema") != "live_predecessor_fence_v0":
        raise LiveFenceError("wrong live fence schema")
    if doc.get("effect") != "FUTURE_EFFECT_EXCLUSION_ONLY":
        raise LiveFenceError("live fence effect mismatch")
    for field in (
        "historical_disposition_effect","authority_effect","completion_effect",
        "release_effect","history_rewrite_effect"
    ):
        if doc.get(field) != "NONE":
            raise LiveFenceError(f"{field} must be NONE")

    law = doc.get("qualified_fence_law_ref")
    if not isinstance(law, dict) or law.get("evaluator_blob") != QUALIFIED_EVALUATOR_BLOB:
        raise LiveFenceError("qualified evaluator identity mismatch")

    predecessor = doc.get("predecessor_snapshot")
    debt = doc.get("predecessor_debt")
    payload = doc.get("qualified_fence_payload")
    if not all(isinstance(x, dict) for x in (predecessor, debt, payload)):
        raise LiveFenceError("predecessor/debt/payload missing")

    predecessor_identity = identity(predecessor)
    debt_identity = identity(debt)
    fence_payload_identity = identity(payload)
    if predecessor_identity != QUALIFIED_PREDECESSOR_IDENTITY:
        raise LiveFenceError("predecessor identity mismatch")
    if debt_identity != QUALIFIED_DEBT_IDENTITY or doc.get("predecessor_debt_identity") != debt_identity:
        raise LiveFenceError("debt identity mismatch")
    if fence_payload_identity != QUALIFIED_FENCE_IDENTITY:
        raise LiveFenceError("qualified fence payload identity mismatch")
    if law.get("qualified_fence_payload_identity") != fence_payload_identity:
        raise LiveFenceError("law ref fence identity mismatch")

    pins = {
        "predecessor_instance_id": "instance_id",
        "predecessor_branch": "branch",
        "predecessor_head": "head",
        "predecessor_claim_id": "claim_id",
        "predecessor_claim_blob": "claim_blob",
        "predecessor_invocation_id": "invocation_id",
        "predecessor_lane_manifest_blob": "lane_manifest_blob",
        "predecessor_guard_receipt_blob": "pre_mutation_guard_blob",
    }
    for top, nested in pins.items():
        if doc.get(top) != predecessor.get(nested):
            raise LiveFenceError(f"pin mismatch: {top}")

    hist_claim = doc.get("historical_claim_object")
    hist_lane = doc.get("historical_lane_manifest_object")
    if not isinstance(hist_claim, dict) or hist_claim.get("status") != "ACTIVE":
        raise LiveFenceError("historical claim ACTIVE not preserved")
    if not isinstance(hist_lane, dict) or hist_lane.get("status") != "ACTIVE":
        raise LiveFenceError("historical lane ACTIVE not preserved")
    if hist_lane.get("occupant_binding") is None:
        raise LiveFenceError("historical occupant unexpectedly null")

    return {
        "fence_object_identity": identity(doc),
        "qualified_fence_payload_identity": fence_payload_identity,
        "predecessor_identity": predecessor_identity,
        "debt_identity": debt_identity,
    }


def predecessor_attempt_from_claim(doc: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    predecessor = doc["predecessor_snapshot"]
    return {
        "kind":"PREDECESSOR",
        "instance_id":predecessor["instance_id"],
        "claim_id":claim["claim_id"],
        "claim_status":claim["status"],
        "occupant_id":claim["occupant_id"],
        "invocation_id":claim["invocation_id"],
        "target_lineage":claim["target_lineage"],
        "consequence_envelope_id":claim["consequence_envelope_id"],
        "semantic_surfaces":list(claim["semantic_surfaces"]),
        "artifact_scopes":list(claim["artifact_scopes"]),
        "predecessor_fence_ref":None,
        "predecessor_debt_ref":None,
        "authority_origin":"NONE",
        "fresh_basis":False,
        "fresh_coordination":False,
    }


def evaluate_attempt(
    *,
    attempt: dict[str, Any],
    observed_predecessor_head: str,
    include_fence: bool = True,
    doc: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doc = load_live_fence() if doc is None else doc
    ids = validate_live_fence(doc)
    cell = {
        "observed_predecessor_head": observed_predecessor_head,
        "fence_registry": ["LIVE"] if include_fence else [],
        "prose_retired": False,
        "attempt": attempt,
    }
    result = evaluate_cell(
        "LIVE",
        cell,
        doc["predecessor_snapshot"],
        ids["debt_identity"],
        {"LIVE": doc["qualified_fence_payload"]},
    )
    result["live_fence_object_identity"] = ids["fence_object_identity"]
    result["qualified_fence_payload_identity"] = ids["qualified_fence_payload_identity"]
    return result


def evaluate_peer_current_operability(
    peer_claim: dict[str, Any],
    observed_predecessor_head: str,
    *,
    include_fence: bool = True,
) -> dict[str, Any]:
    doc = load_live_fence()
    predecessor = doc["predecessor_snapshot"]
    applicable = (
        peer_claim.get("branch") == predecessor["branch"]
        and peer_claim.get("claim_id") == predecessor["claim_id"]
        and peer_claim.get("invocation_id") == predecessor["invocation_id"]
    )
    if not applicable:
        return {"applicable": False}
    result = evaluate_attempt(
        attempt=predecessor_attempt_from_claim(doc, peer_claim),
        observed_predecessor_head=observed_predecessor_head,
        include_fence=include_fence,
        doc=doc,
    )
    return {"applicable": True, **result}


def overlapping_successor_candidate(doc: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = load_live_fence() if doc is None else doc
    ids = validate_live_fence(doc)
    p = doc["predecessor_snapshot"]
    return {
        "kind":"SUCCESSOR",
        "instance_id":"LANE_B_SUCCESSOR_CANDIDATE_001",
        "claim_id":"LANE_B_SUCCESSOR_CANDIDATE_001-CLAIM",
        "claim_status":"ACTIVE",
        "occupant_id":"SYNTHETIC_SUCCESSOR_OCCUPANT",
        "invocation_id":"LANE_B_SUCCESSOR_CANDIDATE_001-INVOCATION",
        "target_lineage":p["target_lineage"],
        "consequence_envelope_id":p["consequence_envelope_id"],
        "semantic_surfaces":[p["semantic_surfaces"][0]],
        "artifact_scopes":[p["artifact_scopes"][0]],
        "predecessor_fence_ref":ids["qualified_fence_payload_identity"],
        "predecessor_debt_ref":ids["debt_identity"],
        "authority_origin":"FRESH",
        "fresh_basis":True,
        "fresh_coordination":True,
    }


def verify_live_fence(observed_predecessor_head: str) -> dict[str, Any]:
    doc = load_live_fence()
    ids = validate_live_fence(doc)
    direct = evaluate_attempt(
        attempt=predecessor_attempt_from_claim(doc, doc["historical_claim_object"]),
        observed_predecessor_head=observed_predecessor_head,
        include_fence=True,
        doc=doc,
    )
    successor = overlapping_successor_candidate(doc)
    zombie = evaluate_attempt(
        attempt=successor,
        observed_predecessor_head=observed_predecessor_head,
        include_fence=True,
        doc=doc,
    )
    counterfactual = evaluate_attempt(
        attempt=successor,
        observed_predecessor_head=observed_predecessor_head,
        include_fence=False,
        doc=doc,
    )
    return {
        "schema":"live_predecessor_fence_verification_v0",
        "fence_object_identity":ids["fence_object_identity"],
        "qualified_fence_payload_identity":ids["qualified_fence_payload_identity"],
        "predecessor_head":doc["predecessor_head"],
        "historical_claim_status":doc["historical_claim_object"]["status"],
        "historical_occupant_binding":doc["historical_lane_manifest_object"]["occupant_binding"],
        "debt":doc["predecessor_debt"],
        "direct_predecessor_effect_attempt":direct,
        "zombie_overlap_with_fence":zombie,
        "zombie_overlap_counterfactual_without_fence":counterfactual,
        "successor_created":False,
        "successor_activated":False,
        "authority_created":False,
        "external_consequence":"NONE",
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("command", choices=["verify"])
    p.add_argument("--observed-head", required=True)
    args=p.parse_args()
    result=verify_live_fence(args.observed_head)
    print(json.dumps(result, indent=2, sort_keys=True))
    ok=(
        result["direct_predecessor_effect_attempt"]["decision"]=="REJECT"
        and result["direct_predecessor_effect_attempt"]["reason"]=="PREDECESSOR_FENCED"
        and result["zombie_overlap_with_fence"]["coordination_posture"]=="NO_COORDINATION_BLOCK"
        and result["zombie_overlap_counterfactual_without_fence"]["coordination_posture"]=="COORDINATION_HOLD"
        and result["historical_claim_status"]=="ACTIVE"
    )
    return 0 if ok else 1

if __name__=="__main__":
    raise SystemExit(main())
