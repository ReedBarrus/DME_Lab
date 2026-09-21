#!/usr/bin/env python3
"""Composition repressure for LANE_B_SUCCESSOR_ENGAGEMENT_001-REPRESSURE-001.

This apparatus composes the exact original engagement evaluator with the exact
qualified quiet-peer coordination v1 surface. It does not mutate live state.
"""

from __future__ import annotations

import argparse
import copy
import json
from contextlib import contextmanager
from pathlib import Path
import subprocess
from typing import Any, Iterator, Mapping, Sequence

import tools.lane_b_successor_engagement_v0 as engagement
import tools.two_lane_coordination_v1 as coordination_v1

ROOT = Path(__file__).resolve().parents[1]

SUCCESSOR_BASIS = "5c2318b12317298345dbd71f0df735a7c4f376c5"
ENGAGEMENT_BASIS = "f6d033068c2df18c3261dae3e1769517a4762ae5"
QUIET_PEER_BASIS = "8a3c7ed546331097ac84231ec46c1c9439a3c906"

ENGAGEMENT_BLOBS = {
    ".github/workflows/lane-b-successor-engagement-001.yml":"fa5012f0782446f39e6de15dead97406a8389b3c",
    "docs/candidates/lane_b_successor_engagement_v0/PRESSURE_DESIGN_001.md":"1ba4a57ce21c2ee5b8759fd20d22359de01cb4c0",
    "schemas/lane_engagement_binding_v0.schema.json":"136b6fc7307c81d3e8c11be0bd8214498b816623",
    "tests/runtime/test_lane_b_successor_engagement_v0.py":"9126fa50c5a36193fff4ce798c8d9746ad13cb1e",
    "tools/lane_b_successor_engagement_v0.py":"a681c59948f3d7b7a0f4219693f9d4a0691c5162",
}

QUIET_PEER_BLOBS = {
    "schemas/peer_state_observation_v1.schema.json":"24e2cccff0fbcaa47fee1d9dd33f7569b4473259",
    "schemas/two_lane_coordination_cursor_v1.schema.json":"19d12deca3ed6df4aabc77987ef4b969d399dcd1",
    "tools/two_lane_coordination_v1.py":"cec40bbf31a7f36123ac0e8b3f7bc56fd6517f2b",
    "tests/runtime/test_quiet_peer_coordination_v1.py":"78e73d8d6d1ecbb30d8f2658c2d9e15ed81a23f3",
    "docs/candidates/quiet_peer_coordination_v1/PRESSURE_DESIGN_001.md":"9a2a07b7db36e96efd9ea2790c835169b6482777",
    "fixtures/quiet_peer_coordination_v1/lane_a_manifest.json":"ebd2379336f1cffa7acc1fa91bdc52308760a9fb",
    ".github/workflows/quiet-peer-coordination-representation-001.yml":"a50149cf0e93db225ed7072c1c9b2c6399d83767",
}

LIVE_FENCE_BLOB = "0b2ec2312dd9feaf81ffb7ac9b21e6256952d8fd"
QUALIFIED_FENCE_PAYLOAD = "sha256:2cced34cedccb4d763031fdfe3b271a8146473f9995b437fb9f0b894f0fabb86"


class RepressureAdministrationError(RuntimeError):
    pass


def git_blob(path: str) -> str:
    proc = subprocess.run(
        ["git", "hash-object", path],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout.strip()


def verify_exact_imports() -> dict[str, Any]:
    engagement_rows = {}
    quiet_rows = {}
    for path, expected in ENGAGEMENT_BLOBS.items():
        observed = git_blob(path)
        engagement_rows[path] = {
            "expected": expected,
            "observed": observed,
            "match": observed == expected,
        }
    for path, expected in QUIET_PEER_BLOBS.items():
        observed = git_blob(path)
        quiet_rows[path] = {
            "expected": expected,
            "observed": observed,
            "match": observed == expected,
        }
    fence_observed = git_blob("coordination/predecessor_fences/LANE_B_LEGACY_INSTANCE_001.json")
    return {
        "engagement": engagement_rows,
        "quiet_peer": quiet_rows,
        "engagement_exact": all(row["match"] for row in engagement_rows.values()),
        "quiet_peer_exact": all(row["match"] for row in quiet_rows.values()),
        "live_fence_blob": fence_observed,
        "live_fence_exact": fence_observed == LIVE_FENCE_BLOB,
    }


def lane_a_manifest() -> dict[str, Any]:
    value = json.loads(
        (ROOT / "fixtures/quiet_peer_coordination_v1/lane_a_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if not isinstance(value, dict):
        raise RepressureAdministrationError("Lane-A manifest fixture is not object")
    return value


def lane_a_quiet_observation() -> dict[str, Any]:
    return coordination_v1.quiet_observation(
        lane_id="LANE_A",
        branch="lane-a-cockpit-coordination-v0",
        head=engagement.LANE_A_HEAD,
        manifest=lane_a_manifest(),
    )


def v1_quiet_cursor() -> dict[str, Any]:
    return coordination_v1.acknowledge_peer_states(
        consumer_lane_id="LANE_B",
        peer_state_observations=[lane_a_quiet_observation()],
    )


@contextmanager
def exact_v1_cursor_validator() -> Iterator[None]:
    """Change only the original evaluator's cursor-validation dependency."""
    old = engagement.validate_cursor
    engagement.validate_cursor = coordination_v1.validate_cursor
    try:
        yield
    finally:
        engagement.validate_cursor = old


def compose_clean_bundle() -> dict[str, Any]:
    # Deliberately do not call engagement.clean_bundle(), because that invokes
    # the original v0 quiet_peer_cursor() producer. All other original helpers
    # are reused unchanged.
    initial = engagement._load_json(ROOT / "coordination/lane_manifest.json")
    ancestry = engagement._load_json(
        ROOT / f"coordination/succession/{engagement.SUCCESSOR_INSTANCE}.json"
    )
    fence = engagement.load_live_fence()
    binding = engagement.clean_binding()
    claim = engagement.clean_claim(binding)
    return {
        "initial_manifest": initial,
        "ancestry": ancestry,
        "fence_doc": fence,
        "binding": binding,
        "claim": claim,
        "cursor": v1_quiet_cursor(),
        "engaged_manifest": engagement.engaged_manifest(initial, binding),
    }


def evaluate_original_engagement(bundle: dict[str, Any]) -> dict[str, Any]:
    with exact_v1_cursor_validator():
        return engagement.evaluate_engagement(**bundle)


def evaluate_engagement_with_current_coordination(
    bundle: dict[str, Any],
    *,
    current_peer_states: list[dict[str, Any]],
) -> dict[str, Any]:
    """Causal composition membrane for engagement acceptance.

    A complete candidate with claim + cursor cannot reach the unchanged
    engagement evaluator until the exact qualified v1 pre-mutation guard
    returns coordination_clear=True. Incomplete candidates that cannot
    possibly yield ENGAGEMENT_VALID retain the original engagement result.
    """
    claim = bundle.get("claim")
    cursor = bundle.get("cursor")

    if claim is None or cursor is None:
        result = copy.deepcopy(evaluate_original_engagement(bundle))
        result["coordination_guard"] = None
        result["engagement_evaluated"] = True
        result["engagement_acceptance_reached"] = (
            result.get("decision") == "ENGAGEMENT_VALID"
        )
        return result

    guard = coordination_v1.pre_mutation_guard(
        local_claim=claim,
        current_peer_states=current_peer_states,
        cursor=cursor,
    )

    if guard.get("coordination_clear") is not True:
        if guard.get("coordination_posture") == "REVALIDATION_REQUIRED":
            stale = guard.get("stale_peers", [])
            reason = stale[0].get("reason") if stale else "REVALIDATION_REQUIRED"
        elif guard.get("coordination_posture") == "COORDINATION_HOLD":
            reason = "COORDINATION_HOLD"
        elif guard.get("coordination_posture") == "CONFLICT_STOP":
            reason = "CONFLICT_STOP"
        else:
            reason = "COORDINATION_NOT_CLEAR"

        return {
            "decision": guard.get("coordination_posture"),
            "reason": reason,
            "coordination_guard": guard,
            "engagement_evaluated": False,
            "engagement_acceptance_reached": False,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "integration_effect": "NONE",
            "effect": "NONE",
        }

    result = copy.deepcopy(evaluate_original_engagement(bundle))
    result["coordination_guard"] = guard
    result["engagement_evaluated"] = True
    result["engagement_acceptance_reached"] = (
        result.get("decision") == "ENGAGEMENT_VALID"
    )
    return result


def lane_a_active_observation_overlapping(local_claim: Mapping[str, Any]) -> dict[str, Any]:
    peer_claim = coordination_v1.synthetic_claim(
        "LANE_A",
        "lane-a-cockpit-coordination-v0",
        claim_id="SYNTHETIC-LANE-A-REPRESSURE-ACTIVE",
        basis_head=engagement.LANE_A_HEAD,
        semantic=local_claim["semantic_surfaces"][0],
        artifact=local_claim["artifact_scopes"][0],
        target=local_claim["target_lineage"],
        envelope=local_claim["consequence_envelope_id"],
    )
    manifest = coordination_v1.active_manifest_from(
        lane_a_manifest(),
        occupant="SYNTHETIC-LANE-A-REPRESSURE-BINDING",
    )
    return coordination_v1.active_observation(
        lane_id="LANE_A",
        branch="lane-a-cockpit-coordination-v0",
        head=engagement.LANE_A_HEAD,
        manifest=manifest,
        claim=peer_claim,
    )


def run_repressure() -> dict[str, Any]:
    import_check = verify_exact_imports()
    if not import_check["engagement_exact"]:
        return {
            "object_type":"SUCCESSOR_ENGAGEMENT_REPRESSURE_RESULT",
            "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-REPRESSURE-001-RESULT",
            "result":"ADMINISTRATION_INVALID",
            "reason":"ENGAGEMENT_BLOB_MISMATCH",
            "import_check":import_check,
            "live_successor_mutation":"NONE","live_engagement":"NONE",
            "authority":"NONE","execution":"NONE","merge":"NONE","stop":True,
        }
    if not import_check["quiet_peer_exact"]:
        return {
            "object_type":"SUCCESSOR_ENGAGEMENT_REPRESSURE_RESULT",
            "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-REPRESSURE-001-RESULT",
            "result":"ADMINISTRATION_INVALID",
            "reason":"QUIET_PEER_BLOB_MISMATCH_REQUALIFY_REQUIRED",
            "import_check":import_check,
            "live_successor_mutation":"NONE","live_engagement":"NONE",
            "authority":"NONE","execution":"NONE","merge":"NONE","stop":True,
        }
    if not import_check["live_fence_exact"]:
        return {
            "object_type":"SUCCESSOR_ENGAGEMENT_REPRESSURE_RESULT",
            "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-REPRESSURE-001-RESULT",
            "result":"ADMINISTRATION_INVALID",
            "reason":"LIVE_FENCE_BLOB_MISMATCH",
            "import_check":import_check,
            "live_successor_mutation":"NONE","live_engagement":"NONE",
            "authority":"NONE","execution":"NONE","merge":"NONE","stop":True,
        }

    live_fence = engagement.verify_live_fence(engagement.PREDECESSOR_HEAD)
    fence_doc = engagement.load_live_fence()
    if (
        live_fence["direct_predecessor_effect_attempt"]["reason"] != "PREDECESSOR_FENCED"
        or live_fence["direct_predecessor_effect_attempt"]["predecessor_currently_operative"] is not False
        or fence_doc["qualified_fence_law_ref"]["qualified_fence_payload_identity"] != QUALIFIED_FENCE_PAYLOAD
        or fence_doc["historical_claim_object"]["status"] != "ACTIVE"
    ):
        return {
            "object_type":"SUCCESSOR_ENGAGEMENT_REPRESSURE_RESULT",
            "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-REPRESSURE-001-RESULT",
            "result":"ADMINISTRATION_INVALID",
            "reason":"PREDECESSOR_FENCE_NOT_OPERATIVE",
            "import_check":import_check,
            "live_successor_mutation":"NONE","live_engagement":"NONE",
            "authority":"NONE","execution":"NONE","merge":"NONE","stop":True,
        }

    base = compose_clean_bundle()
    quiet_current = [lane_a_quiet_observation()]
    cells: dict[str, Any] = {}

    # Original A-J, exact mutations, evaluated by the unchanged original
    # engagement function with only the cursor validator dependency replaced.
    cells["A"] = evaluate_engagement_with_current_coordination(copy.deepcopy(base), current_peer_states=quiet_current)

    b = copy.deepcopy(base)
    b["claim"]["claim_id"] = engagement.PREDECESSOR_CLAIM_ID
    cells["B"] = evaluate_engagement_with_current_coordination(b, current_peer_states=quiet_current)

    c = copy.deepcopy(base)
    c["binding"]["invocation_id"] = engagement.PREDECESSOR_INVOCATION
    c["claim"]["invocation_id"] = engagement.PREDECESSOR_INVOCATION
    cells["C"] = evaluate_engagement_with_current_coordination(c, current_peer_states=quiet_current)

    d = copy.deepcopy(base)
    d["binding"]["occupant_id"] = engagement.PREDECESSOR_OCCUPANT
    d["claim"]["occupant_id"] = engagement.PREDECESSOR_OCCUPANT
    cells["D"] = evaluate_engagement_with_current_coordination(d, current_peer_states=quiet_current)

    e = copy.deepcopy(base)
    e["claim"]["invocation_id"] = "LANE_B_SUCCESSOR_OTHER_FRESH_INVOCATION"
    cells["E"] = evaluate_engagement_with_current_coordination(e, current_peer_states=quiet_current)

    f = copy.deepcopy(base)
    f["engaged_manifest"]["occupant_binding"] = "binding://WRONG-BINDING"
    cells["F"] = evaluate_engagement_with_current_coordination(f, current_peer_states=quiet_current)

    g = copy.deepcopy(base)
    g["binding"] = None
    cells["G"] = evaluate_engagement_with_current_coordination(g, current_peer_states=quiet_current)

    h = copy.deepcopy(base)
    h["claim"] = None
    cells["H"] = evaluate_engagement_with_current_coordination(h, current_peer_states=quiet_current)

    i = copy.deepcopy(base)
    i["binding"]["authority_effect"] = "SMUGGLED"
    cells["I"] = evaluate_engagement_with_current_coordination(i, current_peer_states=quiet_current)

    j = copy.deepcopy(base)
    j["fence_doc"]["qualified_fence_payload"]["predecessor_head"] = "b" * 40
    cells["J"] = evaluate_engagement_with_current_coordination(j, current_peer_states=quiet_current)

    original_expectations = {
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
    for cell_id, expected in original_expectations.items():
        observed = cells[cell_id]
        checks[cell_id] = (
            observed.get("decision") == expected[0]
            and observed.get("reason") == expected[1]
        )

    # K — explicit known quiet peer is represented and the same cursor is
    # actually accepted by the original engagement evaluator.
    quiet_cursor = base["cursor"]
    quiet_rows = quiet_cursor["peer_coordinates"]
    k_engagement = evaluate_engagement_with_current_coordination(copy.deepcopy(base), current_peer_states=quiet_current)
    cells["K"] = {
        "cursor":quiet_cursor,
        "lane_a_coordinate_present":(
            len(quiet_rows) == 1 and quiet_rows[0]["lane_id"] == "LANE_A"
        ),
        "claim_observation":quiet_rows[0]["claim_observation"] if quiet_rows else None,
        "claim_digest_field_present":(
            bool(quiet_rows)
            and "claim_digest" in quiet_rows[0]["claim_observation"]
        ),
        "fabricated_digest":False,
        "engagement":k_engagement,
    }
    checks["K"] = (
        cells["K"]["lane_a_coordinate_present"] is True
        and cells["K"]["claim_observation"] == {"state":"NO_ACTIVE_CLAIM"}
        and cells["K"]["claim_digest_field_present"] is False
        and cells["K"]["fabricated_digest"] is False
        and k_engagement.get("decision") == "ENGAGEMENT_VALID"
    )

    # L — retained explicit quiet coordinate, current peer becomes ACTIVE.
    # This now exercises the composed acceptance membrane itself.
    active_obs = lane_a_active_observation_overlapping(base["claim"])
    l_acceptance = evaluate_engagement_with_current_coordination(
        copy.deepcopy(base),
        current_peer_states=[active_obs],
    )
    cells["L"] = {"acceptance": l_acceptance}
    l_guard = l_acceptance.get("coordination_guard") or {}
    checks["L"] = (
        l_acceptance.get("decision") == "REVALIDATION_REQUIRED"
        and l_acceptance.get("reason") == "PEER_CLAIM_APPEARED"
        and l_acceptance.get("engagement_evaluated") is False
        and l_acceptance.get("engagement_acceptance_reached") is False
        and l_guard.get("coordination_clear") is False
    )

    # M — same current quiet observation, only retained coordinate omitted.
    omitted_cursor = coordination_v1.acknowledge_peer_states(
        consumer_lane_id="LANE_B",
        peer_state_observations=[],
    )
    m_bundle = copy.deepcopy(base)
    m_bundle["cursor"] = omitted_cursor
    m_acceptance = evaluate_engagement_with_current_coordination(
        m_bundle,
        current_peer_states=quiet_current,
    )
    cells["M"] = {
        "explicit_cursor": quiet_cursor,
        "omitted_cursor": omitted_cursor,
        "acceptance": m_acceptance,
    }
    m_guard = m_acceptance.get("coordination_guard") or {}
    checks["M"] = (
        m_acceptance.get("decision") == "REVALIDATION_REQUIRED"
        and m_acceptance.get("reason") == "PEER_NOT_ACKNOWLEDGED"
        and m_acceptance.get("engagement_evaluated") is False
        and m_guard.get("coordination_clear") is False
    )

    # N — correctly retained ACTIVE peer with overlapping claim still blocks
    # before the original engagement evaluator is reachable.
    active_cursor = coordination_v1.acknowledge_peer_states(
        consumer_lane_id="LANE_B",
        peer_state_observations=[active_obs],
    )
    n_bundle = copy.deepcopy(base)
    n_bundle["cursor"] = active_cursor
    n_acceptance = evaluate_engagement_with_current_coordination(
        n_bundle,
        current_peer_states=[active_obs],
    )
    cells["N"] = {"cursor": active_cursor, "acceptance": n_acceptance}
    n_guard = n_acceptance.get("coordination_guard") or {}
    checks["N"] = (
        n_acceptance.get("decision") == "COORDINATION_HOLD"
        and n_acceptance.get("engagement_evaluated") is False
        and n_guard.get("coordination_clear") is False
        and any(
            row.get("coordination_block")
            for row in n_guard.get("comparisons", [])
        )
    )

    # O — exact adversarial stale-cursor bypass attempt.
    # Retain the H0 quiet cursor, then current Lane A becomes ACTIVE at H1.
    active_o = copy.deepcopy(active_obs)
    active_o["head"] = "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    o_acceptance = evaluate_engagement_with_current_coordination(
        copy.deepcopy(base),
        current_peer_states=[active_o],
    )
    cells["O"] = {
        "retained_cursor": quiet_cursor,
        "current_peer_state": active_o,
        "acceptance": o_acceptance,
    }
    o_guard = o_acceptance.get("coordination_guard") or {}
    checks["O"] = (
        o_acceptance.get("decision") == "REVALIDATION_REQUIRED"
        and o_acceptance.get("reason") == "PEER_CLAIM_APPEARED"
        and o_acceptance.get("engagement_evaluated") is False
        and o_acceptance.get("engagement_acceptance_reached") is False
        and o_guard.get("coordination_clear") is False
    )

    # O_CONTROL — retained quiet coordinate and current quiet state are
    # unchanged; guard clears, then and only then can engagement evaluate.
    o_control_acceptance = evaluate_engagement_with_current_coordination(
        copy.deepcopy(base),
        current_peer_states=quiet_current,
    )
    cells["O_CONTROL"] = {
        "retained_cursor": quiet_cursor,
        "current_peer_state": quiet_current[0],
        "acceptance": o_control_acceptance,
    }
    o_control_guard = o_control_acceptance.get("coordination_guard") or {}
    checks["O_CONTROL"] = (
        o_control_guard.get("coordination_posture") == "NO_COORDINATION_BLOCK"
        and o_control_guard.get("coordination_clear") is True
        and o_control_acceptance.get("engagement_evaluated") is True
        and o_control_acceptance.get("decision") == "ENGAGEMENT_VALID"
        and o_control_acceptance.get("engagement_acceptance_reached") is True
    )

    predecessor_fence_pass = (
        live_fence["direct_predecessor_effect_attempt"]["reason"] == "PREDECESSOR_FENCED"
        and live_fence["direct_predecessor_effect_attempt"]["predecessor_currently_operative"] is False
        and fence_doc["historical_claim_object"]["status"] == "ACTIVE"
        and fence_doc["qualified_fence_law_ref"]["qualified_fence_payload_identity"] == QUALIFIED_FENCE_PAYLOAD
    )
    authority_separation_pass = (
        cells["A"].get("authority_effect") == "NONE"
        and cells["A"].get("execution_effect") == "NONE"
        and cells["A"].get("integration_effect") == "NONE"
        and cells["A"].get("effect") == "NONE"
    )

    original_a_j_pass = all(checks[x] for x in "ABCDEFGHIJ")
    all_pass = (
        original_a_j_pass
        and all(checks[x] for x in ["K","L","M","N","O","O_CONTROL"])
        and predecessor_fence_pass
        and authority_separation_pass
    )

    return {
        "object_type":"SUCCESSOR_ENGAGEMENT_REPRESSURE_RESULT",
        "object_id":"LANE_B_SUCCESSOR_ENGAGEMENT_001-REPRESSURE-001-RESULT",
        "successor_basis":SUCCESSOR_BASIS,
        "engagement_basis":ENGAGEMENT_BASIS,
        "quiet_peer_basis":QUIET_PEER_BASIS,
        "import_check":import_check,
        "binding_model":"PASS" if all(checks[x] for x in ["A","G","H","I"]) else "FRACTURE",
        "claim_binding_correspondence":"PASS" if all(checks[x] for x in ["A","B","C","D","E","G","H"]) else "FRACTURE",
        "manifest_binding_correspondence":"PASS" if all(checks[x] for x in ["A","F"]) else "FRACTURE",
        "fresh_invocation":"PASS" if checks["C"] else "FRACTURE",
        "fresh_occupant":"PASS" if checks["D"] else "FRACTURE",
        "quiet_peer_representation":"PASS" if checks["K"] else "FRACTURE",
        "quiet_to_active_revalidation":"PASS" if checks["L"] else "FRACTURE",
        "unrepresented_peer_intervention":"PASS" if checks["M"] else "FRACTURE",
        "active_collision_regression":"PASS" if checks["N"] else "FRACTURE",
        "predecessor_fence":"PASS" if predecessor_fence_pass else "FRACTURE",
        "authority_separation":"PASS" if authority_separation_pass else "FRACTURE",
        "current_coordination_coupling":"PASS" if checks["O"] and checks["O_CONTROL"] else "FRACTURE",
        "original_a_j":"PASS" if original_a_j_pass else "FRACTURE",
        "cell_checks":checks,
        "cells":cells,
        "predecessor_fence_observation":{
            "historical_status":fence_doc["historical_claim_object"]["status"],
            "current_operability":live_fence["direct_predecessor_effect_attempt"]["predecessor_currently_operative"],
            "reason":live_fence["direct_predecessor_effect_attempt"]["reason"],
            "qualified_payload":fence_doc["qualified_fence_law_ref"]["qualified_fence_payload_identity"],
        },
        "result":(
            "LANE_B_SUCCESSOR_ENGAGEMENT_SURVIVES"
            if all_pass
            else "LANE_B_SUCCESSOR_ENGAGEMENT_FRACTURES"
        ),
        "live_successor_mutation":"NONE",
        "live_engagement":"NONE",
        "authority":"NONE",
        "execution":"NONE",
        "merge":"NONE",
        "stop":True,
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    result = run_repressure()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    print(
        f"ENGAGEMENT_REPRESSURE_RESULT={result['result']} "
        f"K={result.get('quiet_peer_representation')} "
        f"L={result.get('quiet_to_active_revalidation')} "
        f"M={result.get('unrepresented_peer_intervention')} "
        f"N={result.get('active_collision_regression')} "
        f"O={result.get('current_coordination_coupling')}"
    )
    return 0 if result["result"] == "LANE_B_SUCCESSOR_ENGAGEMENT_SURVIVES" else 1


if __name__ == "__main__":
    raise SystemExit(main())
