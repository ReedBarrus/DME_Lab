#!/usr/bin/env python3
"""Qualified-candidate v1 peer-state coordination for explicit quiet peers.

This is an isolated pressure apparatus. It preserves v0 ACTIVE-claim semantics
by reusing v0 claim validation, claim digests, and claim comparison, while
adding explicit peer-state observations and cursor coordinates.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.live_predecessor_fence_v0 import (
    LiveFenceError,
    evaluate_peer_current_operability,
    load_live_fence,
)
from tools.two_lane_coordination_v0 import (
    CoordinationError,
    acknowledge as acknowledge_v0,
    claim_digest,
    compare_claims,
    validate_claim,
)

ROOT = Path(__file__).resolve().parents[1]

OBS_SCHEMA = "PEER_STATE_OBSERVATION_v1"
CURSOR_SCHEMA = "two_lane_coordination_cursor_v1"
COORD_SCHEMA = "PEER_STATE_COORDINATE_v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
PREDECESSOR_HEAD = "41316921b211c1daf75c9b71b8147e0eb67d372d"

MANIFEST_FIELDS = {
    "schema","lane_id","branch","intended_horizon","coordination_contract_ref",
    "status","occupant_binding","active_work_claim_path","peer_cursor_path",
    "authority_effect","execution_effect","integration_effect",
}
OBS_COMMON_FIELDS = {
    "schema","lane_id","branch","head","lane_manifest","claim_presence",
    "claim_path_observation","authority_effect","execution_effect",
}
CURSOR_FIELDS = {
    "schema","consumer_lane_id","peer_coordinates","authority_effect","execution_effect"
}
COORD_FIELDS = {"schema","lane_id","branch","last_seen_head","claim_observation"}


class PeerStateCoordinationError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PeerStateCoordinationError(f"{path} must contain an object")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise PeerStateCoordinationError(f"{field} must be non-empty string")
    return value


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    if not isinstance(manifest, Mapping) or set(manifest) != MANIFEST_FIELDS:
        raise PeerStateCoordinationError("lane manifest fields must be exact")
    if manifest.get("schema") != "two_lane_lane_manifest_v0":
        raise PeerStateCoordinationError("wrong lane manifest schema")
    if manifest.get("lane_id") not in {"LANE_A","LANE_B"}:
        raise PeerStateCoordinationError("invalid lane_id")
    _string(manifest.get("branch"), "manifest branch")
    if manifest.get("status") not in {"READY_UNCLAIMED","ACTIVE","HELD","CLOSED"}:
        raise PeerStateCoordinationError("invalid manifest status")
    if manifest.get("active_work_claim_path") != "coordination/active_work_claim.json":
        raise PeerStateCoordinationError("active work claim path mismatch")
    if manifest.get("peer_cursor_path") != "coordination/peer_cursor.json":
        raise PeerStateCoordinationError("peer cursor path mismatch")
    if (
        manifest.get("authority_effect") != "NONE"
        or manifest.get("execution_effect") != "NONE"
        or manifest.get("integration_effect") != "NONE"
    ):
        raise PeerStateCoordinationError("manifest effects must remain NONE")


def validate_peer_state_observation(obs: Mapping[str, Any]) -> None:
    if not isinstance(obs, Mapping):
        raise PeerStateCoordinationError("peer state observation must be object")
    state = obs.get("claim_presence")
    expected = OBS_COMMON_FIELDS | ({"active_claim"} if state == "ACTIVE_CLAIM" else set())
    if set(obs) != expected:
        raise PeerStateCoordinationError("peer state observation fields must be exact")
    if obs.get("schema") != OBS_SCHEMA:
        raise PeerStateCoordinationError("wrong peer state observation schema")
    _string(obs.get("lane_id"), "lane_id")
    _string(obs.get("branch"), "branch")
    if not HEX40.fullmatch(str(obs.get("head"))):
        raise PeerStateCoordinationError("head must be exact lowercase 40-hex")
    if obs.get("authority_effect") != "NONE" or obs.get("execution_effect") != "NONE":
        raise PeerStateCoordinationError("peer observation effects must remain NONE")

    manifest = obs.get("lane_manifest")
    validate_manifest(manifest)
    if manifest["lane_id"] != obs["lane_id"] or manifest["branch"] != obs["branch"]:
        raise PeerStateCoordinationError("manifest does not correspond to peer coordinate")

    path_obs = obs.get("claim_path_observation")
    if not isinstance(path_obs, Mapping) or set(path_obs) != {"path","state"}:
        raise PeerStateCoordinationError("claim path observation fields must be exact")
    if path_obs.get("path") != "coordination/active_work_claim.json":
        raise PeerStateCoordinationError("claim path observation path mismatch")

    if state == "ACTIVE_CLAIM":
        if path_obs.get("state") != "PRESENT_AT_OBSERVED_HEAD":
            raise PeerStateCoordinationError("ACTIVE_CLAIM requires present claim-path basis")
        claim = obs.get("active_claim")
        try:
            validate_claim(claim)
        except CoordinationError as exc:
            raise PeerStateCoordinationError(f"active claim invalid: {exc}") from exc
        if claim["status"] != "ACTIVE":
            raise PeerStateCoordinationError("active claim observation requires ACTIVE claim")
        if claim["lane_id"] != obs["lane_id"] or claim["branch"] != obs["branch"]:
            raise PeerStateCoordinationError("active claim does not correspond to observed peer")
        if manifest["status"] != "ACTIVE":
            raise PeerStateCoordinationError("ACTIVE_CLAIM requires ACTIVE lane manifest")
    elif state == "NO_ACTIVE_CLAIM":
        if path_obs.get("state") != "ABSENT_AT_OBSERVED_HEAD":
            raise PeerStateCoordinationError("NO_ACTIVE_CLAIM requires explicit absent claim-path basis")
        if "active_claim" in obs:
            raise PeerStateCoordinationError("NO_ACTIVE_CLAIM cannot carry active_claim")
    else:
        raise PeerStateCoordinationError("claim_presence must be ACTIVE_CLAIM or NO_ACTIVE_CLAIM")


def validate_claim_observation(value: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping):
        raise PeerStateCoordinationError("claim_observation must be object")
    state = value.get("state")
    if state == "ACTIVE_CLAIM":
        if set(value) != {"state","claim_digest"}:
            raise PeerStateCoordinationError("ACTIVE_CLAIM coordinate requires exact digest field")
        if not SHA256.fullmatch(str(value.get("claim_digest"))):
            raise PeerStateCoordinationError("ACTIVE_CLAIM claim_digest must be sha256:<64 hex>")
    elif state == "NO_ACTIVE_CLAIM":
        if set(value) != {"state"}:
            raise PeerStateCoordinationError("NO_ACTIVE_CLAIM coordinate forbids claim_digest field")
    else:
        raise PeerStateCoordinationError("claim observation state invalid")


def validate_cursor(cursor: Mapping[str, Any]) -> None:
    if not isinstance(cursor, Mapping) or set(cursor) != CURSOR_FIELDS:
        raise PeerStateCoordinationError("cursor fields must be exact")
    if cursor.get("schema") != CURSOR_SCHEMA:
        raise PeerStateCoordinationError("wrong cursor schema")
    _string(cursor.get("consumer_lane_id"), "consumer_lane_id")
    if cursor.get("authority_effect") != "NONE" or cursor.get("execution_effect") != "NONE":
        raise PeerStateCoordinationError("cursor effects must remain NONE")
    peers = cursor.get("peer_coordinates")
    if not isinstance(peers, list):
        raise PeerStateCoordinationError("peer_coordinates must be list")
    seen: set[str] = set()
    for peer in peers:
        if not isinstance(peer, Mapping) or set(peer) != COORD_FIELDS:
            raise PeerStateCoordinationError("peer coordinate fields must be exact")
        if peer.get("schema") != COORD_SCHEMA:
            raise PeerStateCoordinationError("wrong peer coordinate schema")
        lane_id = _string(peer.get("lane_id"), "peer lane_id")
        if lane_id in seen:
            raise PeerStateCoordinationError("duplicate peer lane_id")
        seen.add(lane_id)
        _string(peer.get("branch"), "peer branch")
        if not HEX40.fullmatch(str(peer.get("last_seen_head"))):
            raise PeerStateCoordinationError("last_seen_head must be exact lowercase 40-hex")
        validate_claim_observation(peer.get("claim_observation"))


def coordinate_from_observation(obs: Mapping[str, Any]) -> dict[str, Any]:
    validate_peer_state_observation(obs)
    if obs["claim_presence"] == "ACTIVE_CLAIM":
        claim_observation = {
            "state":"ACTIVE_CLAIM",
            "claim_digest":claim_digest(obs["active_claim"]),
        }
    else:
        claim_observation = {"state":"NO_ACTIVE_CLAIM"}
    return {
        "schema":COORD_SCHEMA,
        "lane_id":obs["lane_id"],
        "branch":obs["branch"],
        "last_seen_head":obs["head"],
        "claim_observation":claim_observation,
    }


def acknowledge_peer_states(
    *,
    consumer_lane_id: str,
    peer_state_observations: list[dict[str, Any]],
) -> dict[str, Any]:
    _string(consumer_lane_id, "consumer_lane_id")
    peers = []
    seen: set[str] = set()
    for obs in sorted(peer_state_observations, key=lambda x: str(x.get("lane_id"))):
        validate_peer_state_observation(obs)
        lane_id = obs["lane_id"]
        if lane_id == consumer_lane_id:
            raise PeerStateCoordinationError("cannot acknowledge local lane as peer")
        if lane_id in seen:
            raise PeerStateCoordinationError("multiple state observations for one peer lane")
        seen.add(lane_id)
        peers.append(coordinate_from_observation(obs))
    cursor = {
        "schema":CURSOR_SCHEMA,
        "consumer_lane_id":consumer_lane_id,
        "peer_coordinates":peers,
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    validate_cursor(cursor)
    return cursor


def _coord_map(cursor: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {row["lane_id"]: row for row in cursor["peer_coordinates"]}


def _obs_map(current: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    peers: dict[str, dict[str, Any]] = {}
    for obs in current:
        validate_peer_state_observation(obs)
        lane_id = obs["lane_id"]
        if lane_id in peers:
            raise PeerStateCoordinationError("multiple current observations for one peer lane")
        peers[lane_id] = obs
    return peers


def _active_claim(obs: Mapping[str, Any]) -> dict[str, Any] | None:
    return obs["active_claim"] if obs["claim_presence"] == "ACTIVE_CLAIM" else None


def pre_mutation_guard(
    *,
    local_claim: dict[str, Any],
    current_peer_states: list[dict[str, Any]],
    cursor: dict[str, Any],
) -> dict[str, Any]:
    try:
        validate_claim(local_claim)
    except CoordinationError as exc:
        raise PeerStateCoordinationError(f"local claim invalid: {exc}") from exc
    validate_cursor(cursor)
    if local_claim["status"] != "ACTIVE":
        raise PeerStateCoordinationError("local claim must be ACTIVE")
    if cursor["consumer_lane_id"] != local_claim["lane_id"]:
        raise PeerStateCoordinationError("cursor consumer does not match local lane")

    retained = _coord_map(cursor)
    current = _obs_map(current_peer_states)
    stale = []
    activity_advances = []

    # A retained relevant peer must still have a fresh current observation.
    for lane_id in sorted(retained):
        if lane_id not in current:
            stale.append({"lane_id":lane_id,"reason":"CURRENT_PEER_STATE_MISSING"})

    # Every freshly observed relevant peer must have a retained coordinate.
    for lane_id in sorted(current):
        obs = current[lane_id]
        old = retained.get(lane_id)
        if old is None:
            stale.append({"lane_id":lane_id,"reason":"PEER_NOT_ACKNOWLEDGED"})
            continue
        if old["branch"] != obs["branch"]:
            stale.append({"lane_id":lane_id,"reason":"PEER_BRANCH_MISMATCH"})
            continue

        old_claim = old["claim_observation"]
        new_state = obs["claim_presence"]
        old_state = old_claim["state"]

        if old_state == "NO_ACTIVE_CLAIM" and new_state == "ACTIVE_CLAIM":
            stale.append({
                "lane_id":lane_id,
                "reason":"PEER_CLAIM_APPEARED",
                "last_seen_head":old["last_seen_head"],
                "current_head":obs["head"],
                "current_claim_digest":claim_digest(obs["active_claim"]),
            })
            continue

        if old_state == "ACTIVE_CLAIM" and new_state == "NO_ACTIVE_CLAIM":
            stale.append({
                "lane_id":lane_id,
                "reason":"PEER_CLAIM_DISAPPEARED",
                "last_seen_claim_digest":old_claim["claim_digest"],
                "last_seen_head":old["last_seen_head"],
                "current_head":obs["head"],
            })
            continue

        if old_state == "ACTIVE_CLAIM" and new_state == "ACTIVE_CLAIM":
            digest = claim_digest(obs["active_claim"])
            if old_claim["claim_digest"] != digest:
                stale.append({
                    "lane_id":lane_id,
                    "reason":"PEER_CLAIM_CHANGED",
                    "last_seen_claim_digest":old_claim["claim_digest"],
                    "current_claim_digest":digest,
                    "last_seen_head":old["last_seen_head"],
                    "current_head":obs["head"],
                })
                continue
            if old["last_seen_head"] != obs["head"]:
                activity_advances.append({
                    "lane_id":lane_id,
                    "reason":"PEER_ACTIVITY_ADVANCED_CLAIM_UNCHANGED",
                    "last_seen_head":old["last_seen_head"],
                    "current_head":obs["head"],
                    "claim_digest":digest,
                })
            continue

        if old_state == "NO_ACTIVE_CLAIM" and new_state == "NO_ACTIVE_CLAIM":
            if old["last_seen_head"] != obs["head"]:
                activity_advances.append({
                    "lane_id":lane_id,
                    "reason":"PEER_ACTIVITY_ADVANCED_NO_ACTIVE_CLAIM",
                    "last_seen_head":old["last_seen_head"],
                    "current_head":obs["head"],
                })
            continue

        raise PeerStateCoordinationError("unreachable claim state transition")

    if stale:
        return {
            "schema":"two_lane_pre_mutation_guard_v1",
            "local_claim_id":local_claim["claim_id"],
            "coordination_posture":"REVALIDATION_REQUIRED",
            "stale_peers":stale,
            "peer_activity_advances":activity_advances,
            "comparisons":[],
            "fence_consultations":[],
            "coordination_clear":False,
            "authorization_effect":"NONE",
            "execution_effect":"NONE",
            "integration_effect":"NONE",
        }

    comparisons = []
    fence_consultations = []
    for lane_id in sorted(current):
        obs = current[lane_id]
        peer = _active_claim(obs)
        if peer is None:
            continue

        try:
            fence_result = evaluate_peer_current_operability(
                peer,
                obs["head"],
                include_fence=True,
            )
        except LiveFenceError as exc:
            raise PeerStateCoordinationError(f"predecessor fence invalid: {exc}") from exc

        if fence_result.get("applicable"):
            consultation = {
                "peer_claim_id":peer["claim_id"],
                "peer_branch":peer["branch"],
                "observed_peer_head":obs["head"],
                "decision":fence_result.get("decision"),
                "reason":fence_result.get("reason"),
                "predecessor_currently_operative":fence_result.get("predecessor_currently_operative"),
                "consulted_fence_identity":fence_result.get("consulted_fence_identity"),
                "live_fence_object_identity":fence_result.get("live_fence_object_identity"),
            }
            fence_consultations.append(consultation)
            if fence_result.get("decision") == "CONFLICT_STOP":
                return {
                    "schema":"two_lane_pre_mutation_guard_v1",
                    "local_claim_id":local_claim["claim_id"],
                    "coordination_posture":"CONFLICT_STOP",
                    "stale_peers":[],
                    "peer_activity_advances":activity_advances,
                    "comparisons":[],
                    "fence_consultations":fence_consultations,
                    "coordination_clear":False,
                    "authorization_effect":"NONE",
                    "execution_effect":"NONE",
                    "integration_effect":"NONE",
                }
            if fence_result.get("predecessor_currently_operative") is False:
                comparison = compare_claims(local_claim, peer)
                comparison["historical_active_pair"] = comparison["active_pair"]
                comparison["provenance_overlap"] = bool(
                    comparison["same_consequence_trajectory"] and comparison["artifact_overlap"]
                )
                comparison["peer_currently_operative"] = False
                comparison["semantic_collision"] = False
                comparison["provenance_collision"] = False
                comparison["coordination_block"] = False
                comparison["relation"] = "FENCED_PREDECESSOR_EXCLUDED"
                comparison["consulted_fence_identity"] = fence_result.get("consulted_fence_identity")
                comparisons.append(comparison)
                continue

        comparisons.append(compare_claims(local_claim, peer))

    blocked = [row for row in comparisons if row["coordination_block"]]
    return {
        "schema":"two_lane_pre_mutation_guard_v1",
        "local_claim_id":local_claim["claim_id"],
        "coordination_posture":"COORDINATION_HOLD" if blocked else "NO_COORDINATION_BLOCK",
        "stale_peers":[],
        "peer_activity_advances":activity_advances,
        "comparisons":comparisons,
        "fence_consultations":fence_consultations,
        "coordination_clear":not blocked,
        "authorization_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
    }


def quiet_observation(
    *,
    lane_id: str,
    branch: str,
    head: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema":OBS_SCHEMA,
        "lane_id":lane_id,
        "branch":branch,
        "head":head,
        "lane_manifest":copy.deepcopy(manifest),
        "claim_presence":"NO_ACTIVE_CLAIM",
        "claim_path_observation":{
            "path":"coordination/active_work_claim.json",
            "state":"ABSENT_AT_OBSERVED_HEAD",
        },
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }


def active_observation(
    *,
    lane_id: str,
    branch: str,
    head: str,
    manifest: dict[str, Any],
    claim: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema":OBS_SCHEMA,
        "lane_id":lane_id,
        "branch":branch,
        "head":head,
        "lane_manifest":copy.deepcopy(manifest),
        "claim_presence":"ACTIVE_CLAIM",
        "active_claim":copy.deepcopy(claim),
        "claim_path_observation":{
            "path":"coordination/active_work_claim.json",
            "state":"PRESENT_AT_OBSERVED_HEAD",
        },
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }


def synthetic_claim(
    lane_id: str,
    branch: str,
    *,
    claim_id: str,
    basis_head: str,
    semantic: str = "SYNTHETIC_SHARED_SURFACE",
    artifact: str = "synthetic/shared",
    target: str = "SYNTHETIC_TARGET",
    envelope: str = "SYNTHETIC_ENVELOPE",
) -> dict[str, Any]:
    return {
        "schema":"two_lane_work_claim_v0",
        "claim_id":claim_id,
        "lane_id":lane_id,
        "seat_id":f"{lane_id}-SEAT",
        "occupant_id":f"{lane_id}-OCCUPANT-{claim_id}",
        "invocation_id":f"{lane_id}-INVOCATION-{claim_id}",
        "branch":branch,
        "basis_head":basis_head,
        "target_lineage":target,
        "campaign_id":None,
        "pressure_id":"QUIET_PEER_COORDINATION_REPRESENTATION_001",
        "addressed_role":"SYNTHETIC",
        "binding_ref":f"BINDING:{claim_id}",
        "consequence_envelope_id":envelope,
        "semantic_surfaces":[semantic],
        "artifact_scopes":[artifact],
        "mutation_paths":[],
        "status":"ACTIVE",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
        "priority_effect":"NONE",
    }


def active_manifest_from(base: dict[str, Any], occupant: str = "SYNTHETIC-BINDING") -> dict[str, Any]:
    value = copy.deepcopy(base)
    value["status"] = "ACTIVE"
    value["occupant_binding"] = occupant
    return value


def run_pressure() -> dict[str, Any]:
    lane_a_manifest = _load_json(ROOT / "fixtures/quiet_peer_coordination_v1/lane_a_manifest.json")
    fence = load_live_fence()
    historical_claim = fence["historical_claim_object"]
    historical_manifest = fence["historical_lane_manifest_object"]

    local_claim = synthetic_claim(
        "LANE_B",
        "lane-b-successor-v1",
        claim_id="SYNTHETIC-LANE-B-LOCAL",
        basis_head="5c2318b12317298345dbd71f0df735a7c4f376c5",
    )

    quiet = quiet_observation(
        lane_id="LANE_A",
        branch="lane-a-cockpit-coordination-v0",
        head="de667390d81c1219abfee063d2a3b1fe13d1ba71",
        manifest=lane_a_manifest,
    )

    active_claim_a = synthetic_claim(
        "LANE_A",
        "lane-a-cockpit-coordination-v0",
        claim_id="SYNTHETIC-LANE-A-ACTIVE-A",
        basis_head="de667390d81c1219abfee063d2a3b1fe13d1ba71",
    )
    active_manifest_a = active_manifest_from(lane_a_manifest)
    active_a = active_observation(
        lane_id="LANE_A",
        branch="lane-a-cockpit-coordination-v0",
        head="de667390d81c1219abfee063d2a3b1fe13d1ba71",
        manifest=active_manifest_a,
        claim=active_claim_a,
    )

    cells: dict[str, Any] = {}

    # A — quiet peer representation.
    cursor_quiet = acknowledge_peer_states(
        consumer_lane_id="LANE_B",
        peer_state_observations=[quiet],
    )
    cells["A"] = {
        "cursor":cursor_quiet,
        "pass":(
            len(cursor_quiet["peer_coordinates"]) == 1
            and cursor_quiet["peer_coordinates"][0]["lane_id"] == "LANE_A"
            and cursor_quiet["peer_coordinates"][0]["claim_observation"] == {"state":"NO_ACTIVE_CLAIM"}
        ),
    }

    # B — active peer representation + v0 active-claim compatibility.
    cursor_active = acknowledge_peer_states(
        consumer_lane_id="LANE_B",
        peer_state_observations=[active_a],
    )
    v0_cursor = acknowledge_v0(
        consumer_lane_id="LANE_B",
        peer_claims=[active_claim_a],
        current_peer_heads={"LANE_A":{"branch":active_a["branch"],"head":active_a["head"]}},
    )
    active_digest = claim_digest(active_claim_a)
    cells["B"] = {
        "cursor_v1":cursor_active,
        "cursor_v0":v0_cursor,
        "pass":(
            cursor_active["peer_coordinates"][0]["claim_observation"]
            == {"state":"ACTIVE_CLAIM","claim_digest":active_digest}
            and v0_cursor["peer_coordinates"][0]["last_seen_claim_digest"] == active_digest
        ),
    }

    # C/D/E — structurally invalid claim-observation unions.
    bad_null = copy.deepcopy(cursor_quiet)
    bad_null["peer_coordinates"][0]["claim_observation"]["claim_digest"] = None
    bad_fake = copy.deepcopy(cursor_quiet)
    bad_fake["peer_coordinates"][0]["claim_observation"]["claim_digest"] = "sha256:" + "1"*64
    bad_missing = copy.deepcopy(cursor_active)
    del bad_missing["peer_coordinates"][0]["claim_observation"]["claim_digest"]
    for cell_id, candidate in [("C",bad_null),("D",bad_fake),("E",bad_missing)]:
        try:
            validate_cursor(candidate)
            cells[cell_id] = {"valid":True,"error":None,"pass":False}
        except PeerStateCoordinationError as exc:
            cells[cell_id] = {"valid":False,"error":str(exc),"pass":True}

    # F — quiet -> active.
    f = pre_mutation_guard(
        local_claim=local_claim,
        current_peer_states=[active_a],
        cursor=cursor_quiet,
    )
    cells["F"] = {
        "guard":f,
        "pass":(
            f["coordination_posture"] == "REVALIDATION_REQUIRED"
            and any(x["reason"] == "PEER_CLAIM_APPEARED" for x in f["stale_peers"])
        ),
    }

    # G — active digest A -> digest B.
    active_claim_b = copy.deepcopy(active_claim_a)
    active_claim_b["claim_id"] = "SYNTHETIC-LANE-A-ACTIVE-B"
    active_claim_b["invocation_id"] = "LANE_A-INVOCATION-SYNTHETIC-LANE-A-ACTIVE-B"
    active_b = active_observation(
        lane_id="LANE_A",
        branch="lane-a-cockpit-coordination-v0",
        head="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        manifest=active_manifest_a,
        claim=active_claim_b,
    )
    g = pre_mutation_guard(local_claim=local_claim,current_peer_states=[active_b],cursor=cursor_active)
    cells["G"] = {
        "guard":g,
        "pass":(
            g["coordination_posture"] == "REVALIDATION_REQUIRED"
            and any(x["reason"] == "PEER_CLAIM_CHANGED" for x in g["stale_peers"])
        ),
    }

    # H — active -> quiet.
    quiet_h1 = quiet_observation(
        lane_id="LANE_A", branch="lane-a-cockpit-coordination-v0",
        head="cccccccccccccccccccccccccccccccccccccccc",
        manifest=lane_a_manifest,
    )
    h = pre_mutation_guard(local_claim=local_claim,current_peer_states=[quiet_h1],cursor=cursor_active)
    cells["H"] = {
        "guard":h,
        "pass":(
            h["coordination_posture"] == "REVALIDATION_REQUIRED"
            and any(x["reason"] == "PEER_CLAIM_DISAPPEARED" for x in h["stale_peers"])
        ),
    }

    # I — quiet stable.
    i = pre_mutation_guard(local_claim=local_claim,current_peer_states=[quiet],cursor=cursor_quiet)
    cells["I"] = {
        "guard":i,
        "pass":(
            i["coordination_posture"] == "NO_COORDINATION_BLOCK"
            and i["coordination_clear"] is True
            and i["peer_activity_advances"] == []
            and i["comparisons"] == []
        ),
    }

    # J — quiet head advance with fresh explicit quiet observation.
    quiet_h1b = quiet_observation(
        lane_id="LANE_A", branch="lane-a-cockpit-coordination-v0",
        head="dddddddddddddddddddddddddddddddddddddddd",
        manifest=lane_a_manifest,
    )
    j = pre_mutation_guard(local_claim=local_claim,current_peer_states=[quiet_h1b],cursor=cursor_quiet)
    cells["J"] = {
        "guard":j,
        "pass":(
            j["coordination_posture"] == "NO_COORDINATION_BLOCK"
            and j["coordination_clear"] is True
            and any(
                x["reason"] == "PEER_ACTIVITY_ADVANCED_NO_ACTIVE_CLAIM"
                for x in j["peer_activity_advances"]
            )
        ),
    }

    # K — same current quiet peer, coordinate omitted.
    omitted_cursor = acknowledge_peer_states(consumer_lane_id="LANE_B",peer_state_observations=[])
    k = pre_mutation_guard(local_claim=local_claim,current_peer_states=[quiet],cursor=omitted_cursor)
    cells["K"] = {
        "explicit_cursor_guard":i,
        "omitted_cursor_guard":k,
        "pass":(
            i["coordination_posture"] == "NO_COORDINATION_BLOCK"
            and k["coordination_posture"] == "REVALIDATION_REQUIRED"
            and any(x["reason"] == "PEER_NOT_ACKNOWLEDGED" for x in k["stale_peers"])
        ),
    }

    # L — current active pair collision regression.
    l = pre_mutation_guard(local_claim=local_claim,current_peer_states=[active_a],cursor=cursor_active)
    cells["L"] = {
        "guard":l,
        "pass":(
            l["coordination_posture"] == "COORDINATION_HOLD"
            and l["coordination_clear"] is False
            and any(x["coordination_block"] for x in l["comparisons"])
        ),
    }

    # M — fenced historical predecessor remains excluded.
    historical_obs = active_observation(
        lane_id="LANE_B",
        branch=historical_claim["branch"],
        head=PREDECESSOR_HEAD,
        manifest=historical_manifest,
        claim=historical_claim,
    )
    local_other = synthetic_claim(
        "LANE_A",
        "synthetic-local-for-fence-regression",
        claim_id="SYNTHETIC-LOCAL-FENCE-REGRESSION",
        basis_head="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        semantic=historical_claim["semantic_surfaces"][0],
        artifact=historical_claim["artifact_scopes"][0],
        target=historical_claim["target_lineage"],
        envelope=historical_claim["consequence_envelope_id"],
    )
    cursor_hist = acknowledge_peer_states(
        consumer_lane_id="LANE_A",
        peer_state_observations=[historical_obs],
    )
    m = pre_mutation_guard(local_claim=local_other,current_peer_states=[historical_obs],cursor=cursor_hist)
    cells["M"] = {
        "guard":m,
        "pass":(
            m["coordination_posture"] == "NO_COORDINATION_BLOCK"
            and m["coordination_clear"] is True
            and len(m["fence_consultations"]) == 1
            and m["fence_consultations"][0]["predecessor_currently_operative"] is False
            and m["comparisons"][0]["relation"] == "FENCED_PREDECESSOR_EXCLUDED"
        ),
    }

    checks = {cell_id:value["pass"] for cell_id,value in cells.items()}
    all_pass = all(checks.values())
    result = (
        "QUIET_PEER_COORDINATION_REPRESENTATION_SURVIVES"
        if all_pass
        else "QUIET_PEER_COORDINATION_REPRESENTATION_FRACTURES"
    )
    return {
        "object_type":"QUIET_PEER_COORDINATION_PRESSURE_RESULT",
        "object_id":"QUIET_PEER_COORDINATION_REPRESENTATION_001-RESULT",
        "quiet_peer_explicitly_representable":"PASS" if checks["A"] else "FRACTURE",
        "active_peer_representation":"PASS" if checks["B"] else "FRACTURE",
        "absence_typed_explicitly":"PASS" if checks["A"] and checks["C"] and checks["D"] else "FRACTURE",
        "null_digest_overload":"REJECTED" if checks["C"] else "FRACTURE",
        "quiet_to_active_revalidation":"PASS" if checks["F"] else "FRACTURE",
        "active_to_active_change":"PASS" if checks["G"] else "FRACTURE",
        "active_to_quiet_revalidation":"PASS" if checks["H"] else "FRACTURE",
        "quiet_head_advance":"PASS" if checks["J"] else "FRACTURE",
        "unrepresented_peer_detection":"PASS" if checks["K"] else "FRACTURE",
        "active_collision_regression":"PASS" if checks["L"] else "FRACTURE",
        "fenced_predecessor_regression":"PASS" if checks["M"] else "FRACTURE",
        "v0_active_claim_compatibility":"PASS" if checks["B"] else "FRACTURE",
        "cells":cells,
        "cell_checks":checks,
        "result":result,
        "live_mutation":"NONE",
        "authority":"NONE",
        "execution":"NONE",
        "merge":"NONE",
        "stop":True,
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    result = run_pressure()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    print(
        f"QUIET_PEER_RESULT={result['result']} "
        f"A={result['quiet_peer_explicitly_representable']} "
        f"K={result['unrepresented_peer_detection']} "
        f"M={result['fenced_predecessor_regression']}"
    )
    return 0 if result["result"] == "QUIET_PEER_COORDINATION_REPRESENTATION_SURVIVES" else 1


if __name__ == "__main__":
    raise SystemExit(main())
