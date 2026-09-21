#!/usr/bin/env python3
"""TWO_LANE_COORDINATION_001 bounded coordination guard."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

CLAIM_SCHEMA = "two_lane_work_claim_v0"
CURSOR_SCHEMA = "two_lane_coordination_cursor_v0"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
STATUSES = {"ACTIVE", "RELEASED", "COMPLETED", "BLOCKED"}


class CoordinationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def claim_digest(claim: dict[str, Any]) -> str:
    validate_claim(claim)
    return "sha256:" + hashlib.sha256(canonical_bytes(claim)).hexdigest()


def _string(value: Any, field: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value:
        raise CoordinationError(f"{field} must be a non-empty string")


def _strings(value: Any, field: str, *, nonempty: bool = False) -> None:
    if not isinstance(value, list):
        raise CoordinationError(f"{field} must be a list")
    if any(not isinstance(item, str) or not item for item in value):
        raise CoordinationError(f"{field} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise CoordinationError(f"{field} must not contain duplicates")
    if nonempty and not value:
        raise CoordinationError(f"{field} must not be empty")


def validate_claim(claim: dict[str, Any]) -> None:
    required = {
        "schema","claim_id","lane_id","seat_id","occupant_id","invocation_id",
        "branch","basis_head","target_lineage","campaign_id","pressure_id",
        "addressed_role","binding_ref","consequence_envelope_id",
        "semantic_surfaces","artifact_scopes","mutation_paths","status",
        "authority_effect","execution_effect","integration_effect","priority_effect",
    }
    if set(claim) != required:
        raise CoordinationError(
            f"claim fields must be exact; missing={sorted(required-set(claim))} "
            f"extra={sorted(set(claim)-required)}"
        )
    if claim["schema"] != CLAIM_SCHEMA:
        raise CoordinationError("wrong claim schema")
    for field in (
        "claim_id","lane_id","seat_id","occupant_id","invocation_id","branch",
        "target_lineage","consequence_envelope_id"
    ):
        _string(claim[field], field)
    for field in ("campaign_id","pressure_id","addressed_role","binding_ref"):
        _string(claim[field], field, nullable=True)
    if claim["campaign_id"] is None and claim["pressure_id"] is None:
        raise CoordinationError("campaign_id or pressure_id is required")
    if not HEX40.fullmatch(str(claim["basis_head"])):
        raise CoordinationError("basis_head must be exact lowercase 40-hex")
    _strings(claim["semantic_surfaces"], "semantic_surfaces", nonempty=True)
    _strings(claim["artifact_scopes"], "artifact_scopes", nonempty=True)
    _strings(claim["mutation_paths"], "mutation_paths")
    if claim["status"] not in STATUSES:
        raise CoordinationError("invalid claim status")
    for field in (
        "authority_effect","execution_effect","integration_effect","priority_effect"
    ):
        if claim[field] != "NONE":
            raise CoordinationError(f"{field} must remain NONE")


def validate_cursor(cursor: dict[str, Any]) -> None:
    required = {
        "schema","consumer_lane_id","peer_coordinates",
        "authority_effect","execution_effect"
    }
    if set(cursor) != required:
        raise CoordinationError("cursor fields must be exact")
    if cursor["schema"] != CURSOR_SCHEMA:
        raise CoordinationError("wrong cursor schema")
    _string(cursor["consumer_lane_id"], "consumer_lane_id")
    if cursor["authority_effect"] != "NONE" or cursor["execution_effect"] != "NONE":
        raise CoordinationError("cursor effects must remain NONE")
    peers = cursor["peer_coordinates"]
    if not isinstance(peers, list):
        raise CoordinationError("peer_coordinates must be a list")
    seen: set[str] = set()
    for peer in peers:
        if not isinstance(peer, dict) or set(peer) != {
            "lane_id","branch","last_seen_head","last_seen_claim_digest"
        }:
            raise CoordinationError("peer coordinate fields must be exact")
        _string(peer["lane_id"], "peer lane_id")
        _string(peer["branch"], "peer branch")
        if peer["lane_id"] in seen:
            raise CoordinationError("duplicate peer lane_id")
        seen.add(peer["lane_id"])
        if not HEX40.fullmatch(str(peer["last_seen_head"])):
            raise CoordinationError("last_seen_head must be exact lowercase 40-hex")
        if not SHA256.fullmatch(str(peer["last_seen_claim_digest"])):
            raise CoordinationError("last_seen_claim_digest must be sha256:<64 hex>")


def compare_claims(local: dict[str, Any], peer: dict[str, Any]) -> dict[str, Any]:
    validate_claim(local)
    validate_claim(peer)
    active = local["status"] == "ACTIVE" and peer["status"] == "ACTIVE"
    semantic = sorted(set(local["semantic_surfaces"]) & set(peer["semantic_surfaces"]))
    artifacts = sorted(set(local["artifact_scopes"]) & set(peer["artifact_scopes"]))
    paths = sorted(set(local["mutation_paths"]) & set(peer["mutation_paths"]))
    same_trajectory = (
        local["target_lineage"] == peer["target_lineage"]
        and local["consequence_envelope_id"] == peer["consequence_envelope_id"]
    )

    semantic_collision = active and bool(semantic)
    provenance_collision = active and same_trajectory and bool(artifacts)

    if semantic_collision:
        relation = "SEMANTIC_COLLISION"
    elif provenance_collision:
        relation = "PROVENANCE_COLLISION"
    elif active and paths:
        relation = "REPRESENTATION_OVERLAP_ONLY"
    else:
        relation = "CLEAR"

    return {
        "schema": "two_lane_claim_comparison_v0",
        "local_claim_id": local["claim_id"],
        "peer_claim_id": peer["claim_id"],
        "active_pair": active,
        "semantic_overlap": semantic,
        "artifact_overlap": artifacts,
        "path_overlap": paths,
        "same_consequence_trajectory": same_trajectory,
        "semantic_collision": semantic_collision,
        "provenance_collision": provenance_collision,
        "relation": relation,
        "coordination_block": semantic_collision or provenance_collision,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def acknowledge(
    *,
    consumer_lane_id: str,
    peer_claims: list[dict[str, Any]],
    current_peer_heads: dict[str, dict[str, str]],
) -> dict[str, Any]:
    peers = []
    seen: set[str] = set()
    for claim in sorted(peer_claims, key=lambda c: str(c.get("lane_id"))):
        validate_claim(claim)
        lane_id = claim["lane_id"]
        if lane_id == consumer_lane_id:
            raise CoordinationError("cannot acknowledge local lane as peer")
        if lane_id in seen:
            raise CoordinationError("multiple claims for one peer lane")
        seen.add(lane_id)
        current = current_peer_heads.get(lane_id)
        if not isinstance(current, dict) or set(current) != {"branch","head"}:
            raise CoordinationError(f"current peer coordinate missing for {lane_id}")
        if current["branch"] != claim["branch"]:
            raise CoordinationError(f"peer branch mismatch for {lane_id}")
        if not HEX40.fullmatch(str(current["head"])):
            raise CoordinationError(f"peer head malformed for {lane_id}")
        peers.append({
            "lane_id": lane_id,
            "branch": current["branch"],
            "last_seen_head": current["head"],
            "last_seen_claim_digest": claim_digest(claim),
        })
    return {
        "schema": CURSOR_SCHEMA,
        "consumer_lane_id": consumer_lane_id,
        "peer_coordinates": peers,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def pre_mutation_guard(
    *,
    local_claim: dict[str, Any],
    peer_claims: list[dict[str, Any]],
    cursor: dict[str, Any],
    current_peer_heads: dict[str, dict[str, str]],
) -> dict[str, Any]:
    validate_claim(local_claim)
    validate_cursor(cursor)
    if local_claim["status"] != "ACTIVE":
        raise CoordinationError("local claim must be ACTIVE")
    if cursor["consumer_lane_id"] != local_claim["lane_id"]:
        raise CoordinationError("cursor consumer does not match local lane")

    observed = {p["lane_id"]: p for p in cursor["peer_coordinates"]}
    stale = []
    activity_advances = []
    peers: dict[str, dict[str, Any]] = {}
    for peer in peer_claims:
        validate_claim(peer)
        lane_id = peer["lane_id"]
        if lane_id == local_claim["lane_id"]:
            raise CoordinationError("peer claim uses local lane_id")
        if lane_id in peers:
            raise CoordinationError("multiple peer claims for one lane")
        peers[lane_id] = peer

        current = current_peer_heads.get(lane_id)
        if not isinstance(current, dict) or set(current) != {"branch","head"}:
            stale.append({"lane_id": lane_id, "reason": "CURRENT_PEER_HEAD_MISSING"})
            continue
        if current["branch"] != peer["branch"]:
            stale.append({"lane_id": lane_id, "reason": "PEER_BRANCH_MISMATCH"})
            continue
        if not HEX40.fullmatch(str(current["head"])):
            raise CoordinationError("current peer head malformed")
        retained = observed.get(lane_id)
        if retained is None:
            stale.append({"lane_id": lane_id, "reason": "PEER_NOT_ACKNOWLEDGED"})
            continue
        if retained["branch"] != current["branch"]:
            stale.append({"lane_id": lane_id, "reason": "CURSOR_BRANCH_MISMATCH"})
            continue
        digest = claim_digest(peer)
        if retained["last_seen_claim_digest"] != digest:
            stale.append({
                "lane_id": lane_id,
                "reason": "PEER_CLAIM_CHANGED",
                "last_seen_claim_digest": retained["last_seen_claim_digest"],
                "current_claim_digest": digest,
                "last_seen_head": retained["last_seen_head"],
                "current_head": current["head"],
            })
            continue
        if retained["last_seen_head"] != current["head"]:
            activity_advances.append({
                "lane_id": lane_id,
                "reason": "PEER_ACTIVITY_ADVANCED_CLAIM_UNCHANGED",
                "last_seen_head": retained["last_seen_head"],
                "current_head": current["head"],
                "claim_digest": digest,
            })

    if stale:
        return {
            "schema": "two_lane_pre_mutation_guard_v0",
            "local_claim_id": local_claim["claim_id"],
            "coordination_posture": "REVALIDATION_REQUIRED",
            "stale_peers": stale,
            "comparisons": [],
            "peer_activity_advances": activity_advances,
            "coordination_clear": False,
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
            "integration_effect": "NONE",
        }

    comparisons = [compare_claims(local_claim, peers[k]) for k in sorted(peers)]
    blocked = [c for c in comparisons if c["coordination_block"]]
    return {
        "schema": "two_lane_pre_mutation_guard_v0",
        "local_claim_id": local_claim["claim_id"],
        "coordination_posture": (
            "COORDINATION_HOLD" if blocked else "NO_COORDINATION_BLOCK"
        ),
        "stale_peers": [],
        "peer_activity_advances": activity_advances,
        "comparisons": comparisons,
        "coordination_clear": not blocked,
        "authorization_effect": "NONE",
        "execution_effect": "NONE",
        "integration_effect": "NONE",
    }


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CoordinationError(f"{path} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_compare = sub.add_parser("compare")
    p_compare.add_argument("local", type=Path)
    p_compare.add_argument("peer", type=Path)

    p_ack = sub.add_parser("ack")
    p_ack.add_argument("--lane", required=True)
    p_ack.add_argument("--heads", required=True, type=Path)
    p_ack.add_argument("peers", nargs="+", type=Path)

    p_guard = sub.add_parser("guard")
    p_guard.add_argument("local", type=Path)
    p_guard.add_argument("cursor", type=Path)
    p_guard.add_argument("heads", type=Path)
    p_guard.add_argument("peers", nargs="+", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "compare":
            result = compare_claims(_load(args.local), _load(args.peer))
        elif args.command == "ack":
            result = acknowledge(
                consumer_lane_id=args.lane,
                peer_claims=[_load(p) for p in args.peers],
                current_peer_heads=_load(args.heads),
            )
        elif args.command == "guard":
            result = pre_mutation_guard(
                local_claim=_load(args.local),
                peer_claims=[_load(p) for p in args.peers],
                cursor=_load(args.cursor),
                current_peer_heads=_load(args.heads),
            )
        else:
            raise AssertionError(args.command)
    except (CoordinationError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status":"BLOCKED",
            "error":str(exc),
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
