#!/usr/bin/env python3
"""Synthetic qualification apparatus for LANE_B_SUCCESSOR_ENGAGEMENT_001.

This module never mutates lane-b-successor-v1. It evaluates synthetic engagement
bundles against the pinned successor state and the authoritative coordination
and predecessor-fence apparatus inherited from the successor basis.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.live_predecessor_fence_v0 import LiveFenceError, load_live_fence, validate_live_fence, verify_live_fence
from tools.two_lane_coordination_v0 import (
    CoordinationError,
    acknowledge,
    pre_mutation_guard,
    validate_claim,
    validate_cursor,
)

ROOT = Path(__file__).resolve().parents[1]

SUCCESSOR_INSTANCE = "LANE_B_SUCCESSOR_INSTANCE_001"
SUCCESSOR_BRANCH = "lane-b-successor-v1"
SUCCESSOR_BASIS = "5c2318b12317298345dbd71f0df735a7c4f376c5"
SUCCESSOR_MANIFEST_BLOB = "37708df7b2f0b8431c7eb84a8eebdbdd8a08b26a"
SUCCESSOR_ANCESTRY_BLOB = "9ad3e12a0d395046a26fdc29419ddda6510d1afd"

PREDECESSOR_INSTANCE = "LANE_B_LEGACY_INSTANCE_001"
PREDECESSOR_HEAD = "41316921b211c1daf75c9b71b8147e0eb67d372d"
PREDECESSOR_CLAIM_ID = "SEAT_ENGAGEMENT_HANDSHAKE_001-LANE_B-CLAIM-001"
PREDECESSOR_INVOCATION = "SEAT_ENGAGEMENT_HANDSHAKE_001-WORKSHOP-INVOCATION-001"
PREDECESSOR_OCCUPANT = "WORKSHOP"
PREDECESSOR_DEBT = "sha256:b42da029e9d0daccb6a486150e420cde5510c023ffe9b6bcd73a3b5ad4a399d5"
FENCE_PAYLOAD = "sha256:2cced34cedccb4d763031fdfe3b271a8146473f9995b437fb9f0b894f0fabb86"

LANE_A_BRANCH = "lane-a-cockpit-coordination-v0"
LANE_A_HEAD = "de667390d81c1219abfee063d2a3b1fe13d1ba71"

BINDING_FIELDS = {
    "schema","binding_id","lane_instance_id","lane_id","branch","seat_id",
    "occupant_id","invocation_id","engagement_id","basis_head",
    "successor_ancestry_ref","predecessor_fence_ref","predecessor_debt_ref",
    "authority_effect","execution_effect"
}

MANIFEST_FIELDS = {
    "schema","lane_id","branch","intended_horizon","coordination_contract_ref",
    "status","occupant_binding","active_work_claim_path","peer_cursor_path",
    "authority_effect","execution_effect","integration_effect"
}


class EngagementError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EngagementError(f"{path} must contain an object")
    return value


def binding_ref(binding: Mapping[str, Any]) -> str:
    return f"binding://{binding['binding_id']}"


def validate_binding(binding: Mapping[str, Any]) -> None:
    if not isinstance(binding, Mapping) or set(binding) != BINDING_FIELDS:
        raise EngagementError("binding fields must be exact")
    if binding["schema"] != "LANE_ENGAGEMENT_BINDING_v0":
        raise EngagementError("wrong binding schema")
    for key in (
        "binding_id","lane_instance_id","lane_id","branch","seat_id",
        "occupant_id","invocation_id","engagement_id","basis_head",
        "successor_ancestry_ref","predecessor_fence_ref","predecessor_debt_ref",
    ):
        if not isinstance(binding[key], str) or not binding[key]:
            raise EngagementError(f"{key} must be a non-empty string")
    if len(binding["basis_head"]) != 40 or any(c not in "0123456789abcdef" for c in binding["basis_head"]):
        raise EngagementError("basis_head must be exact lowercase 40-hex")
    if binding["authority_effect"] != "NONE":
        raise EngagementError("BINDING_AUTHORITY_EFFECT_NOT_NONE")
    if binding["execution_effect"] != "NONE":
        raise EngagementError("BINDING_EXECUTION_EFFECT_NOT_NONE")


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if not isinstance(manifest, Mapping) or set(manifest) != MANIFEST_FIELDS:
        raise EngagementError("manifest fields must be exact")
    if manifest["schema"] != "two_lane_lane_manifest_v0":
        raise EngagementError("wrong manifest schema")
    if manifest["lane_id"] not in {"LANE_A","LANE_B"}:
        raise EngagementError("invalid lane_id")
    if manifest["status"] not in {"READY_UNCLAIMED","ACTIVE","HELD","CLOSED"}:
        raise EngagementError("invalid manifest status")
    if manifest["authority_effect"] != "NONE" or manifest["execution_effect"] != "NONE" or manifest["integration_effect"] != "NONE":
        raise EngagementError("manifest effects must remain NONE")


def validate_subject(initial_manifest: Mapping[str, Any], ancestry: Mapping[str, Any]) -> None:
    validate_manifest(initial_manifest)
    if initial_manifest["lane_id"] != "LANE_B":
        raise EngagementError("successor lane_id mismatch")
    if initial_manifest["branch"] != SUCCESSOR_BRANCH:
        raise EngagementError("successor branch mismatch")
    if initial_manifest["status"] != "READY_UNCLAIMED":
        raise EngagementError("successor initial status must be READY_UNCLAIMED")
    if initial_manifest["occupant_binding"] is not None:
        raise EngagementError("successor initial occupant must be null")

    required_ancestry = {
        "successor_instance_id": SUCCESSOR_INSTANCE,
        "lane_id": "LANE_B",
        "successor_branch": SUCCESSOR_BRANCH,
        "predecessor_instance_id": PREDECESSOR_INSTANCE,
        "predecessor_head": PREDECESSOR_HEAD,
        "predecessor_fence_content_identity": "sha256:25b8a646b0f2a536b3dba5572da008499632e5b0c1a51865a8b43cf62f785723",
        "qualified_fence_payload_identity": FENCE_PAYLOAD,
        "predecessor_debt_identity": PREDECESSOR_DEBT,
        "predecessor_historical_status": "ACTIVE",
        "predecessor_current_operability": "FENCED",
        "successor_initial_status": "READY_UNCLAIMED",
        "successor_initial_active_claim": "ABSENT",
        "successor_initial_invocation": "ABSENT",
        "successor_initial_authority": "ABSENT",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "historical_disposition_effect": "NONE",
    }
    for key, expected in required_ancestry.items():
        if ancestry.get(key) != expected:
            raise EngagementError(f"ancestry mismatch: {key}")


def validate_fence_for_engagement(fence_doc: dict[str, Any]) -> None:
    try:
        validate_live_fence(fence_doc)
    except LiveFenceError as exc:
        raise EngagementError(f"PREDECESSOR_FENCE_INVALID: {exc}") from exc
    if fence_doc.get("predecessor_head") != PREDECESSOR_HEAD:
        raise EngagementError("PREDECESSOR_FENCE_INVALID: head mismatch")
    if fence_doc.get("predecessor_debt_identity") != PREDECESSOR_DEBT:
        raise EngagementError("PREDECESSOR_FENCE_INVALID: debt mismatch")
    if fence_doc.get("qualified_fence_law_ref", {}).get("qualified_fence_payload_identity") != FENCE_PAYLOAD:
        raise EngagementError("PREDECESSOR_FENCE_INVALID: payload mismatch")


def fresh_identity_checks(binding: Mapping[str, Any], claim: Mapping[str, Any]) -> str | None:
    if claim.get("claim_id") == PREDECESSOR_CLAIM_ID:
        return "OLD_CLAIM_REUSE"
    if binding.get("invocation_id") == PREDECESSOR_INVOCATION or claim.get("invocation_id") == PREDECESSOR_INVOCATION:
        return "OLD_INVOCATION_REUSE"
    if binding.get("occupant_id") == PREDECESSOR_OCCUPANT or claim.get("occupant_id") == PREDECESSOR_OCCUPANT:
        return "OLD_OCCUPANT_IDENTITY_REUSE"
    if binding.get("basis_head") != SUCCESSOR_BASIS or claim.get("basis_head") != SUCCESSOR_BASIS:
        return "SUCCESSOR_BASIS_MISMATCH"
    if binding.get("lane_instance_id") != SUCCESSOR_INSTANCE:
        return "SUCCESSOR_INSTANCE_MISMATCH"
    if binding.get("lane_id") != "LANE_B" or claim.get("lane_id") != "LANE_B":
        return "SUCCESSOR_LANE_MISMATCH"
    if binding.get("branch") != SUCCESSOR_BRANCH or claim.get("branch") != SUCCESSOR_BRANCH:
        return "SUCCESSOR_BRANCH_MISMATCH"
    return None


def correspondence_error(binding: Mapping[str, Any], claim: Mapping[str, Any]) -> str | None:
    expected = {
        "lane_id": binding["lane_id"],
        "occupant_id": binding["occupant_id"],
        "invocation_id": binding["invocation_id"],
        "branch": binding["branch"],
        "basis_head": binding["basis_head"],
        "binding_ref": binding_ref(binding),
    }
    for key, value in expected.items():
        if claim.get(key) != value:
            return f"CLAIM_BINDING_MISMATCH:{key}"
    return None


def evaluate_engagement(
    *,
    initial_manifest: dict[str, Any],
    ancestry: dict[str, Any],
    fence_doc: dict[str, Any],
    binding: dict[str, Any] | None,
    claim: dict[str, Any] | None,
    cursor: dict[str, Any] | None,
    engaged_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    try:
        validate_subject(initial_manifest, ancestry)
        validate_fence_for_engagement(fence_doc)
    except EngagementError as exc:
        return {
            "decision":"STOP",
            "reason":"PREDECESSOR_FENCE_INVALID" if "PREDECESSOR_FENCE_INVALID" in str(exc) else "SUBJECT_INVALID",
            "detail":str(exc),
            "authority_effect":"NONE",
            "execution_effect":"NONE",
            "integration_effect":"NONE",
        }

    if binding is None and claim is not None:
        return {
            "decision":"REJECT",
            "reason":"CLAIM_WITHOUT_BINDING",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if binding is None:
        return {
            "decision":"NOT_FULLY_ENGAGED",
            "reason":"BINDING_ABSENT",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    try:
        validate_binding(binding)
    except EngagementError as exc:
        return {
            "decision":"REJECT",
            "reason":str(exc),
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    if claim is None:
        return {
            "decision":"NOT_FULLY_ENGAGED",
            "reason":"ACTIVE_CLAIM_ABSENT",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    try:
        validate_claim(claim)
    except CoordinationError as exc:
        return {
            "decision":"REJECT",
            "reason":f"CLAIM_INVALID:{exc}",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    if claim["status"] != "ACTIVE":
        return {
            "decision":"REJECT",
            "reason":"CLAIM_NOT_ACTIVE",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    freshness = fresh_identity_checks(binding, claim)
    if freshness:
        return {
            "decision":"REJECT","reason":freshness,
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    mismatch = correspondence_error(binding, claim)
    if mismatch:
        return {
            "decision":"REJECT","reason":mismatch,
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    if binding.get("successor_ancestry_ref") != f"coordination/succession/{SUCCESSOR_INSTANCE}.json@{SUCCESSOR_ANCESTRY_BLOB}":
        return {
            "decision":"REJECT","reason":"SUCCESSOR_ANCESTRY_REF_MISMATCH",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if binding.get("predecessor_debt_ref") != PREDECESSOR_DEBT:
        return {
            "decision":"REJECT","reason":"PREDECESSOR_DEBT_REF_MISMATCH",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if binding.get("predecessor_fence_ref") != "coordination/predecessor_fences/LANE_B_LEGACY_INSTANCE_001.json@0b2ec2312dd9feaf81ffb7ac9b21e6256952d8fd":
        return {
            "decision":"REJECT","reason":"PREDECESSOR_FENCE_REF_MISMATCH",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    if cursor is None:
        return {
            "decision":"NOT_FULLY_ENGAGED",
            "reason":"CURSOR_ABSENT",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    try:
        validate_cursor(cursor)
    except CoordinationError as exc:
        return {
            "decision":"REJECT",
            "reason":f"CURSOR_INVALID:{exc}",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if cursor["consumer_lane_id"] != "LANE_B":
        return {
            "decision":"REJECT","reason":"CURSOR_CONSUMER_MISMATCH",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    if engaged_manifest is None:
        return {
            "decision":"NOT_FULLY_ENGAGED",
            "reason":"ENGAGED_MANIFEST_ABSENT",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    try:
        validate_manifest(engaged_manifest)
    except EngagementError as exc:
        return {
            "decision":"REJECT","reason":f"MANIFEST_INVALID:{exc}",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if engaged_manifest["status"] != "ACTIVE":
        return {
            "decision":"REJECT","reason":"MANIFEST_NOT_ACTIVE",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if engaged_manifest["occupant_binding"] != binding_ref(binding):
        return {
            "decision":"REJECT","reason":"MANIFEST_BINDING_MISMATCH",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }
    if engaged_manifest["lane_id"] != "LANE_B" or engaged_manifest["branch"] != SUCCESSOR_BRANCH:
        return {
            "decision":"REJECT","reason":"MANIFEST_SUCCESSOR_IDENTITY_MISMATCH",
            "authority_effect":"NONE","execution_effect":"NONE","integration_effect":"NONE",
        }

    return {
        "decision":"ENGAGEMENT_VALID",
        "reason":"COUPLED_ENGAGEMENT_INVARIANT_SATISFIED",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
        "effect":"NONE",
    }


def clean_binding() -> dict[str, Any]:
    return {
        "schema":"LANE_ENGAGEMENT_BINDING_v0",
        "binding_id":"LANE_B_SUCCESSOR_BINDING_CANDIDATE_001",
        "lane_instance_id":SUCCESSOR_INSTANCE,
        "lane_id":"LANE_B",
        "branch":SUCCESSOR_BRANCH,
        "seat_id":"SYNTHETIC-SUCCESSOR-SEAT",
        "occupant_id":"LANE_B_SUCCESSOR_OCCUPANT_CANDIDATE_001",
        "invocation_id":"LANE_B_SUCCESSOR_INVOCATION_CANDIDATE_001",
        "engagement_id":"LANE_B_SUCCESSOR_ENGAGEMENT_CANDIDATE_001",
        "basis_head":SUCCESSOR_BASIS,
        "successor_ancestry_ref":f"coordination/succession/{SUCCESSOR_INSTANCE}.json@{SUCCESSOR_ANCESTRY_BLOB}",
        "predecessor_fence_ref":"coordination/predecessor_fences/LANE_B_LEGACY_INSTANCE_001.json@0b2ec2312dd9feaf81ffb7ac9b21e6256952d8fd",
        "predecessor_debt_ref":PREDECESSOR_DEBT,
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }


def clean_claim(binding: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema":"two_lane_work_claim_v0",
        "claim_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-SYNTHETIC-CLAIM",
        "lane_id":"LANE_B",
        "seat_id":binding["seat_id"],
        "occupant_id":binding["occupant_id"],
        "invocation_id":binding["invocation_id"],
        "branch":SUCCESSOR_BRANCH,
        "basis_head":SUCCESSOR_BASIS,
        "target_lineage":"SYNTHETIC_ENGAGEMENT_QUALIFICATION_SUBJECT",
        "campaign_id":None,
        "pressure_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001",
        "addressed_role":"WORKSHOP",
        "binding_ref":binding_ref(binding),
        "consequence_envelope_id":"SYNTHETIC_ENGAGEMENT_NO_EFFECT",
        "semantic_surfaces":["SYNTHETIC_ENGAGEMENT_MECHANICS"],
        "artifact_scopes":["docs/candidates/lane_b_successor_engagement_v0"],
        "mutation_paths":[],
        "status":"ACTIVE",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
        "priority_effect":"NONE",
    }


def quiet_peer_cursor() -> dict[str, Any]:
    return acknowledge(
        consumer_lane_id="LANE_B",
        peer_claims=[],
        current_peer_heads={
            "LANE_A":{"branch":LANE_A_BRANCH,"head":LANE_A_HEAD}
        },
    )


def engaged_manifest(initial_manifest: Mapping[str, Any], binding: Mapping[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(initial_manifest)
    out["status"] = "ACTIVE"
    out["occupant_binding"] = binding_ref(binding)
    return out


def clean_bundle() -> dict[str, Any]:
    initial = _load_json(ROOT / "coordination/lane_manifest.json")
    ancestry = _load_json(ROOT / f"coordination/succession/{SUCCESSOR_INSTANCE}.json")
    fence = load_live_fence()
    binding = clean_binding()
    claim = clean_claim(binding)
    cursor = quiet_peer_cursor()
    return {
        "initial_manifest":initial,
        "ancestry":ancestry,
        "fence_doc":fence,
        "binding":binding,
        "claim":claim,
        "cursor":cursor,
        "engaged_manifest":engaged_manifest(initial,binding),
    }


def eval_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    return evaluate_engagement(**bundle)


def pressure_k() -> dict[str, Any]:
    known_heads = {"LANE_A":{"branch":LANE_A_BRANCH,"head":LANE_A_HEAD}}
    cursor = acknowledge(
        consumer_lane_id="LANE_B",
        peer_claims=[],
        current_peer_heads=known_heads,
    )
    explicit_lane_a = any(
        row.get("lane_id") == "LANE_A"
        for row in cursor["peer_coordinates"]
    )

    explicit_null_digest_cursor = {
        "schema":"two_lane_coordination_cursor_v0",
        "consumer_lane_id":"LANE_B",
        "peer_coordinates":[{
            "lane_id":"LANE_A",
            "branch":LANE_A_BRANCH,
            "last_seen_head":LANE_A_HEAD,
            "last_seen_claim_digest":None,
        }],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    null_digest_valid = True
    null_digest_error = None
    try:
        validate_cursor(explicit_null_digest_cursor)
    except CoordinationError as exc:
        null_digest_valid = False
        null_digest_error = str(exc)

    explicit_missing_digest_cursor = copy.deepcopy(explicit_null_digest_cursor)
    del explicit_missing_digest_cursor["peer_coordinates"][0]["last_seen_claim_digest"]
    missing_digest_valid = True
    missing_digest_error = None
    try:
        validate_cursor(explicit_missing_digest_cursor)
    except CoordinationError as exc:
        missing_digest_valid = False
        missing_digest_error = str(exc)

    representable = explicit_lane_a or null_digest_valid or missing_digest_valid
    return {
        "cell_id":"K",
        "known_peer":{
            "lane_id":"LANE_A",
            "branch":LANE_A_BRANCH,
            "head":LANE_A_HEAD,
            "manifest_status":"READY_UNCLAIMED",
            "active_claim":"ABSENT",
        },
        "authoritative_acknowledge_output":cursor,
        "lane_a_explicitly_represented":explicit_lane_a,
        "explicit_null_digest_valid":null_digest_valid,
        "explicit_null_digest_error":null_digest_error,
        "explicit_missing_digest_valid":missing_digest_valid,
        "explicit_missing_digest_error":missing_digest_error,
        "fabricated_claim_digest_used":False,
        "result":(
            "VALID_EXPLICIT_NO_ACTIVE_CLAIM_REPRESENTATION"
            if representable
            else "BOUNDED_FRACTURE"
        ),
        "reason":(
            "KNOWN_READY_UNCLAIMED_PEER_EXPLICITLY_REPRESENTABLE"
            if representable
            else "KNOWN_READY_UNCLAIMED_PEER_NOT_EXPLICITLY_REPRESENTABLE"
        ),
    }


def synthetic_lane_a_active_claim() -> dict[str, Any]:
    return {
        "schema":"two_lane_work_claim_v0",
        "claim_id":"SYNTHETIC-LANE-A-ACTIVE-AFTER-CURSOR",
        "lane_id":"LANE_A",
        "seat_id":"SYNTHETIC-LANE-A-SEAT",
        "occupant_id":"SYNTHETIC-LANE-A-OCCUPANT",
        "invocation_id":"SYNTHETIC-LANE-A-INVOCATION",
        "branch":LANE_A_BRANCH,
        "basis_head":LANE_A_HEAD,
        "target_lineage":"SYNTHETIC-LANE-A-SUBJECT",
        "campaign_id":None,
        "pressure_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-L",
        "addressed_role":"SYNTHETIC",
        "binding_ref":"SYNTHETIC-LANE-A-BINDING",
        "consequence_envelope_id":"SYNTHETIC-LANE-A-NO-EFFECT",
        "semantic_surfaces":["SYNTHETIC-LANE-A-SURFACE"],
        "artifact_scopes":["synthetic/lane-a"],
        "mutation_paths":[],
        "status":"ACTIVE",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
        "priority_effect":"NONE",
    }


def pressure_l(local_claim: dict[str, Any], quiet_cursor: dict[str, Any]) -> dict[str, Any]:
    peer = synthetic_lane_a_active_claim()
    guard = pre_mutation_guard(
        local_claim=local_claim,
        peer_claims=[peer],
        cursor=quiet_cursor,
        current_peer_heads={
            "LANE_A":{"branch":LANE_A_BRANCH,"head":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
        },
    )
    return {
        "cell_id":"L",
        "quiet_cursor":quiet_cursor,
        "new_peer_claim_id":peer["claim_id"],
        "guard":guard,
        "result":(
            "REVALIDATION_REQUIRED"
            if guard.get("coordination_posture") == "REVALIDATION_REQUIRED"
            else "FAILED_TO_REVALIDATE"
        ),
    }


def run_pressure() -> dict[str, Any]:
    base = clean_bundle()
    live_fence = verify_live_fence(PREDECESSOR_HEAD)
    if (
        live_fence["direct_predecessor_effect_attempt"]["reason"] != "PREDECESSOR_FENCED"
        or live_fence["direct_predecessor_effect_attempt"]["predecessor_currently_operative"] is not False
    ):
        return {
            "object_type":"SUCCESSOR_ENGAGEMENT_PRESSURE_RESULT",
            "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-RESULT",
            "result":"ADMINISTRATION_INVALID",
            "reason":"PREDECESSOR_FENCE_NOT_OPERATIVE",
        }

    cells: dict[str, Any] = {}

    cells["A"] = eval_bundle(copy.deepcopy(base))

    b = copy.deepcopy(base)
    b["claim"]["claim_id"] = PREDECESSOR_CLAIM_ID
    cells["B"] = eval_bundle(b)

    c = copy.deepcopy(base)
    c["binding"]["invocation_id"] = PREDECESSOR_INVOCATION
    c["claim"]["invocation_id"] = PREDECESSOR_INVOCATION
    cells["C"] = eval_bundle(c)

    d = copy.deepcopy(base)
    d["binding"]["occupant_id"] = PREDECESSOR_OCCUPANT
    d["claim"]["occupant_id"] = PREDECESSOR_OCCUPANT
    cells["D"] = eval_bundle(d)

    e = copy.deepcopy(base)
    e["claim"]["invocation_id"] = "LANE_B_SUCCESSOR_OTHER_FRESH_INVOCATION"
    cells["E"] = eval_bundle(e)

    f = copy.deepcopy(base)
    f["engaged_manifest"]["occupant_binding"] = "binding://WRONG-BINDING"
    cells["F"] = eval_bundle(f)

    g = copy.deepcopy(base)
    g["binding"] = None
    cells["G"] = eval_bundle(g)

    h = copy.deepcopy(base)
    h["claim"] = None
    cells["H"] = eval_bundle(h)

    i = copy.deepcopy(base)
    i["binding"]["authority_effect"] = "SMUGGLED"
    cells["I"] = eval_bundle(i)

    j = copy.deepcopy(base)
    j["fence_doc"]["qualified_fence_payload"]["predecessor_head"] = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    cells["J"] = eval_bundle(j)

    cells["K"] = pressure_k()
    cells["L"] = pressure_l(base["claim"], base["cursor"])

    expectations = {
        "A":("ENGAGEMENT_VALID","COUPLED_ENGAGEMENT_INVARIANT_SATISFIED"),
        "B":("REJECT","OLD_CLAIM_REUSE"),
        "C":("REJECT","OLD_INVOCATION_REUSE"),
        "D":("REJECT","OLD_OCCUPANT_IDENTITY_REUSE"),
        "E":("REJECT","CLAIM_BINDING_MISMATCH:invocation_id"),
        "F":("REJECT","MANIFEST_BINDING_MISMATCH"),
        "G":("REJECT","CLAIM_WITHOUT_BINDING"),
        "H":("NOT_FULLY_ENGAGED","ACTIVE_CLAIM_ABSENT"),
        "I":("REJECT","BINDING_AUTHORITY_EFFECT_NOT_NONE"),
        "J":("STOP","PREDECESSOR_FENCE_INVALID"),
    }
    checks: dict[str, bool] = {}
    for cell_id, (decision, reason) in expectations.items():
        observed = cells[cell_id]
        checks[cell_id] = observed.get("decision") == decision and observed.get("reason") == reason

    checks["K"] = (
        cells["K"].get("result") == "BOUNDED_FRACTURE"
        and cells["K"].get("fabricated_claim_digest_used") is False
        and cells["K"].get("lane_a_explicitly_represented") is False
    )
    checks["L"] = (
        cells["L"].get("result") == "REVALIDATION_REQUIRED"
        and cells["L"]["guard"].get("coordination_clear") is False
        and any(
            row.get("reason") == "PEER_NOT_ACKNOWLEDGED"
            for row in cells["L"]["guard"].get("stale_peers", [])
        )
    )

    administration_valid = all(checks.values())
    overall = (
        "LANE_B_SUCCESSOR_ENGAGEMENT_FRACTURES"
        if administration_valid and cells["K"]["result"] == "BOUNDED_FRACTURE"
        else (
            "LANE_B_SUCCESSOR_ENGAGEMENT_SURVIVES"
            if administration_valid
            else "ADMINISTRATION_INVALID"
        )
    )

    return {
        "object_type":"SUCCESSOR_ENGAGEMENT_PRESSURE_RESULT",
        "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-RESULT",
        "successor_basis":SUCCESSOR_BASIS,
        "successor_initial_status":"READY_UNCLAIMED",
        "predecessor_fence":"VALID",
        "predecessor_operability":False,
        "binding_model":"QUALIFIED" if all(checks[x] for x in ["A","G","H","I"]) else "FRACTURE",
        "claim_binding_correspondence":"PASS" if all(checks[x] for x in ["A","B","C","D","E","G","H"]) else "FRACTURE",
        "manifest_binding_correspondence":"PASS" if all(checks[x] for x in ["A","F"]) else "FRACTURE",
        "fresh_invocation":"PASS" if checks["C"] else "FRACTURE",
        "fresh_occupant":"PASS" if checks["D"] else "FRACTURE",
        "peer_no_claim_representation":"FRACTURE" if cells["K"]["result"] == "BOUNDED_FRACTURE" else "PASS",
        "peer_change_revalidation":"PASS" if checks["L"] else "FRACTURE",
        "authority_separation":"PASS" if checks["I"] and cells["A"].get("authority_effect") == "NONE" else "FRACTURE",
        "cell_checks":checks,
        "cells":cells,
        "result":overall,
        "live_successor_mutation":"NONE",
        "live_engagement":"NONE",
        "authority":"NONE",
        "execution":"NONE",
        "merge":"NONE",
        "stop":True,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = run_pressure()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    print(
        f"SUCCESSOR_ENGAGEMENT_RESULT={result['result']} "
        f"K={result.get('peer_no_claim_representation')} "
        f"L={result.get('peer_change_revalidation')}"
    )
    return 0 if result["result"] != "ADMINISTRATION_INVALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
