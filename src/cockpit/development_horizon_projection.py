#!/usr/bin/env python3
"""Read-only developmental-horizon projection over existing durable evidence."""

from __future__ import annotations

from typing import Any


HORIZON_STATES = {
    "READY_FOR_PRESSURE",
    "ACTIVE",
    "EVIDENCE_ACCUMULATING",
    "BLOCKED",
    "EARNED",
    "FRACTURED",
}


class DevelopmentHorizonProjectionError(RuntimeError):
    pass


def _json_rows(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    return [
        row[field]
        for row in rows
        if isinstance(row.get(field), dict)
    ]


def _current_assignment_events(
    assignment_rows: list[dict[str, Any]],
    satisfaction_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    active: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for row in assignment_rows:
        event = row.get("event_json")
        if not isinstance(event, dict):
            continue
        key = (
            str(event.get("request_id")),
            str(event.get("request_sha256")),
            str(event.get("seat_id")),
            str(event.get("preparation_kind")),
        )
        kind = event.get("assignment_kind")
        if kind == "ASSIGNED":
            active[key] = event
        elif kind == "ASSIGNMENT_RELEASED":
            active.pop(key, None)

    satisfied_ids = {
        item.get("assignment_id")
        for item in _json_rows(satisfaction_rows, "satisfaction_json")
        if item.get("assignment_id")
    }
    return [
        event
        for key, event in sorted(active.items())
        if event.get("assignment_id") not in satisfied_ids
    ]


def derive_development_horizons(runtime_state: dict[str, Any]) -> dict[str, Any]:
    campaigns = _json_rows(runtime_state.get("campaigns", []), "campaign_json")
    campaign_ids = {c.get("campaign_id") for c in campaigns if c.get("campaign_id")}
    campaign_by_id = {c["campaign_id"]: c for c in campaigns if c.get("campaign_id")}

    standing_rows = runtime_state.get("frontier", [])
    standing_by_campaign: dict[str, dict[str, str]] = {}
    for row in standing_rows:
        cid = row.get("campaign_id")
        rid = row.get("relation_id")
        standing = row.get("standing")
        if cid in campaign_ids and rid and standing:
            standing_by_campaign.setdefault(cid, {})[rid] = standing

    requests = _json_rows(runtime_state.get("requests", []), "request_json")
    current_selection = [
        item
        for item in runtime_state.get("current_selection", [])
        if isinstance(item, dict)
    ]
    prep_receipts = _json_rows(
        runtime_state.get("preparation_receipts", []),
        "receipt_json",
    )
    assignment_rows = runtime_state.get("assignment_history", [])
    satisfaction_rows = runtime_state.get("assignment_satisfactions", [])
    current_assignments = _current_assignment_events(
        assignment_rows,
        satisfaction_rows,
    )
    bells = _json_rows(runtime_state.get("manual_bells", []), "bell_json")
    opportunities = _json_rows(
        runtime_state.get("reentry_opportunities", []),
        "opportunity_json",
    )
    reentry_receipts = _json_rows(
        runtime_state.get("reentry_receipts", []),
        "receipt_json",
    )

    cross_edges: set[tuple[str, str]] = set()
    local_edges: dict[str, list[dict[str, str]]] = {}
    for campaign in campaigns:
        cid = campaign["campaign_id"]
        for edge in campaign.get("dependency_edges", []):
            source = edge.get("from")
            target = edge.get("to")
            if source in campaign_ids and target in campaign_ids:
                cross_edges.add((source, target))
            else:
                local_edges.setdefault(cid, []).append(
                    {"from": str(source), "to": str(target)}
                )

    provisional: dict[str, dict[str, Any]] = {}
    for cid in sorted(campaign_ids):
        campaign = campaign_by_id[cid]
        declared = [
            relation["relation_id"]
            for relation in campaign.get("unresolved_relations", [])
        ]
        current_standing = standing_by_campaign.get(cid, {})
        open_relations = [
            rid for rid in declared
            if current_standing.get(rid, "OPEN") == "OPEN"
        ]
        earned_relations = [
            rid for rid in declared
            if current_standing.get(rid) == "EARNED"
        ]
        fractured_relations = [
            rid for rid in declared
            if current_standing.get(rid) == "FRACTURED"
        ]

        candidate_request_count = sum(
            1 for item in requests if item.get("campaign_id") == cid
        )
        current_selection_count = sum(
            1 for item in current_selection if item.get("campaign_id") == cid
        )
        preparation_receipt_count = sum(
            1 for item in prep_receipts if item.get("campaign_id") == cid
        )
        assignment_count = sum(
            1 for item in current_assignments if item.get("campaign_id") == cid
        )
        satisfaction_count = sum(
            1
            for item in _json_rows(satisfaction_rows, "satisfaction_json")
            if item.get("assignment_id")
            and any(
                a.get("assignment_id") == item.get("assignment_id")
                and a.get("campaign_id") == cid
                for a in _json_rows(assignment_rows, "event_json")
            )
        )
        manual_bell_count = sum(
            1 for item in bells if item.get("campaign_id") == cid
        )
        wake_opportunity_count = sum(
            1 for item in opportunities if item.get("campaign_id") == cid
        )

        opportunity_ids = {
            item.get("opportunity_id")
            for item in opportunities
            if item.get("campaign_id") == cid
        }
        reentry_receipt_count = sum(
            1
            for item in reentry_receipts
            if item.get("opportunity_id") in opportunity_ids
        )

        provisional[cid] = {
            "campaign_id": cid,
            "campaign_sha256": next(
                (
                    row.get("campaign_sha256")
                    for row in runtime_state.get("campaigns", [])
                    if row.get("campaign_id") == cid
                ),
                None,
            ),
            "objective": campaign.get("objective"),
            "claim_ceiling": campaign.get("claim_ceiling"),
            "campaign_packet_status": campaign.get("status"),
            "open_relations": open_relations,
            "earned_relations": earned_relations,
            "fractured_relations": fractured_relations,
            "relation_counts": {
                "open": len(open_relations),
                "earned": len(earned_relations),
                "fractured": len(fractured_relations),
            },
            "activity": {
                "candidate_requests": candidate_request_count,
                "current_selections": current_selection_count,
                "current_assignments": assignment_count,
                "assignment_satisfactions": satisfaction_count,
                "preparation_receipts": preparation_receipt_count,
                "manual_bells": manual_bell_count,
                "wake_opportunities": wake_opportunity_count,
                "reentry_receipts": reentry_receipt_count,
            },
            "local_dependency_edges": local_edges.get(cid, []),
        }

    # First derive intrinsic state without cross-campaign blockers.
    intrinsic: dict[str, str] = {}
    for cid, item in provisional.items():
        counts = item["relation_counts"]
        if counts["open"] == 0 and counts["fractured"] == 0 and counts["earned"] > 0:
            intrinsic[cid] = "EARNED"
            continue
        if counts["open"] == 0 and counts["fractured"] > 0:
            intrinsic[cid] = "FRACTURED"
            continue

        activity = item["activity"]
        evidence_count = (
            counts["earned"]
            + counts["fractured"]
            + activity["preparation_receipts"]
            + activity["reentry_receipts"]
            + activity["assignment_satisfactions"]
        )
        work_count = (
            activity["candidate_requests"]
            + activity["current_selections"]
            + activity["current_assignments"]
            + activity["manual_bells"]
            + activity["wake_opportunities"]
        )
        if evidence_count > 0:
            intrinsic[cid] = "EVIDENCE_ACCUMULATING"
        elif work_count > 0:
            intrinsic[cid] = "ACTIVE"
        else:
            intrinsic[cid] = "READY_FOR_PRESSURE"

    blockers_by_target: dict[str, list[str]] = {cid: [] for cid in campaign_ids}
    unlocks_by_source: dict[str, list[str]] = {cid: [] for cid in campaign_ids}
    for source, target in sorted(cross_edges):
        unlocks_by_source[source].append(target)
        if intrinsic.get(source) != "EARNED":
            blockers_by_target[target].append(source)

    horizons: list[dict[str, Any]] = []
    for cid in sorted(campaign_ids):
        item = provisional[cid]
        blockers = [
            {
                "campaign_id": blocker,
                "current_state": intrinsic.get(blocker, "UNKNOWN"),
                "required_state": "EARNED",
            }
            for blocker in blockers_by_target[cid]
        ]
        state = intrinsic[cid]
        if state not in {"EARNED", "FRACTURED"} and blockers:
            state = "BLOCKED"

        item["horizon_state"] = state
        item["intrinsic_state_without_external_blockers"] = intrinsic[cid]
        item["blocked_by"] = blockers
        item["unlocks"] = sorted(set(unlocks_by_source[cid]))
        item["priority_effect"] = "NONE"
        item["authority_effect"] = "NONE"
        item["execution_effect"] = "NONE"
        item["standing_effect"] = "NONE"
        horizons.append(item)

    state_counts = {
        state: sum(1 for item in horizons if item["horizon_state"] == state)
        for state in sorted(HORIZON_STATES)
    }

    return {
        "schema": "development_horizon_projection_v0",
        "horizons": horizons,
        "cross_campaign_dependencies": [
            {"from": source, "to": target}
            for source, target in sorted(cross_edges)
        ],
        "state_counts": state_counts,
        "priority_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "standing_effect": "NONE",
        "source_of_truth": "EXISTING_DURABLE_CAMPAIGN_AND_RUNTIME_EVIDENCE",
    }
