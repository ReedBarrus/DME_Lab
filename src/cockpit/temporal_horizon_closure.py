"""Deterministic Atlas temporal/current/upcoming horizon closure.

This projection combines exact temporal evidence, current workcycle projection,
and already-declared next pressure into one bounded relational-horizon
candidate. It creates no standing, authority, admission, or execution.
"""

from __future__ import annotations

from typing import Any, Mapping


OBJECT_TYPE = "ATLAS_TEMPORAL_HORIZON_CLOSURE_V0"


def _recent_transition(temporal: Mapping[str, Any]) -> dict[str, Any] | None:
    transitions = temporal.get("transitions")
    if not isinstance(transitions, list) or not transitions:
        return None
    item = transitions[-1]
    return dict(item) if isinstance(item, dict) else None


def _history_posture(temporal: Mapping[str, Any]) -> dict[str, Any]:
    recent = _recent_transition(temporal)
    if recent is None:
        return {
            "posture": "UNRESOLVED",
            "reason": "no adjacent temporal transition available",
            "recent_transition": None,
        }
    events = recent.get("events") or []
    classifications = sorted({
        classification
        for event in events
        if isinstance(event, dict)
        for classification in (event.get("classifications") or [])
        if isinstance(classification, str)
    })
    return {
        "posture": "SUPPORTED",
        "recent_transition": {
            "transition_id": recent.get("transition_id"),
            "from_commit_sha": recent.get("from_commit_sha"),
            "to_commit_sha": recent.get("to_commit_sha"),
            "event_count": recent.get("event_count", len(events)),
            "classifications": classifications,
            "source_handles": list(recent.get("source_handles") or []),
        },
        "causation_claim": "NONE",
    }


def _horizon_rule(next_pressure: str | None) -> dict[str, str]:
    rules = {
        "T2_ADJUDICATION": {
            "family": "H_reconstruct",
            "subject": "campaign-to-work decomposition lineage",
            "support_predicate": "exact campaign/horizon/decomposition/work identities are challengeably recoverable",
            "boundary_condition": "decomposition remains exercised but independently unadjudicated",
            "pressure_direction": "adjudicate decomposition lineage without executing work",
        },
        "T6_PRESSURE": {
            "family": "H_correct",
            "subject": "typed repair-routing discrimination",
            "support_predicate": "distinct defect classes route to distinct repair destinations without retry authority",
            "boundary_condition": "repair law is implemented but not independently pressured",
            "pressure_direction": "pressure typed repair routing",
        },
        "T7_PRESSURE": {
            "family": "H_observe",
            "subject": "operator currentness and control truth",
            "support_predicate": "Cockpit labels currentness, control, budget, seat, and eligibility without overclaim",
            "boundary_condition": "operator projection is implemented but not independently pressured",
            "pressure_direction": "pressure witnessability and control truth",
        },
        "AUTO_CONTINUATION_PRESSURE": {
            "family": "H_operate",
            "subject": "one-successor bounded continuation",
            "support_predicate": "one successor can be admitted only after source-bound eligibility + lease + budget + authority",
            "boundary_condition": "workcycle is otherwise pressure-clean but production admission is not concurrency-safe",
            "pressure_direction": "pressure one bounded successor admission without model invocation",
        },
    }
    return rules.get(
        str(next_pressure),
        {
            "family": "H_observe",
            "subject": "current workcycle unresolved boundary",
            "support_predicate": "current state can be reconstructed from explicit evidence",
            "boundary_condition": f"next pressure is {next_pressure or 'UNRESOLVED'}",
            "pressure_direction": "resolve currentness before further motion",
        },
    )


def _surface(posture: str, basis: list[str], risk: str | None = None) -> dict[str, Any]:
    return {
        "posture": posture,
        "evidence_handles": basis,
        "risk": risk,
    }


def derive_temporal_horizon_closure(
    *,
    temporal_lineage: Mapping[str, Any],
    workcycle: Mapping[str, Any],
    development_horizons: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    history = _history_posture(temporal_lineage)
    next_pressure = workcycle.get("next_pressure")
    rule = _horizon_rule(str(next_pressure) if next_pressure is not None else None)

    campaign_id = workcycle.get("campaign_id")
    active_horizon = workcycle.get("active_horizon")
    current_unresolved = list(workcycle.get("current_unresolved") or [])
    evaluation = workcycle.get("latest_consequence_evaluation") or {}
    disposition = evaluation.get("disposition")
    cells = workcycle.get("campaign_progress") or {}
    eligibility = workcycle.get("eligibility") or {}
    operative_control = workcycle.get("operative_control") or {}
    seat_ecology = workcycle.get("seat_ecology") or {}

    temporal_handle = str(
        (history.get("recent_transition") or {}).get("transition_id") or "TEMPORAL_UNRESOLVED"
    )
    workcycle_handle = f"campaign:{campaign_id or 'UNRESOLVED'}"
    horizon_handle = f"horizon:{active_horizon or 'UNRESOLVED'}"
    evidence = [temporal_handle, workcycle_handle, horizon_handle]

    seven_surfaces = {
        "identity_address": _surface(
            "SUPPORTED" if campaign_id and temporal_lineage.get("source_commit") else "UNRESOLVED",
            evidence,
            None if campaign_id else "campaign identity absent",
        ),
        "mechanical": _surface(
            "SUPPORTED" if history["posture"] == "SUPPORTED" else "UNRESOLVED",
            [temporal_handle],
            None if history["posture"] == "SUPPORTED" else "temporal transition unavailable",
        ),
        "symbolic_semantic": _surface(
            "SUPPORTED" if active_horizon and next_pressure else "UNRESOLVED",
            [workcycle_handle, horizon_handle],
            None if active_horizon and next_pressure else "horizon/current pressure not explicit",
        ),
        "relational_topological": _surface(
            "SUPPORTED" if isinstance(cells, dict) and bool(cells) else "UNRESOLVED",
            [workcycle_handle],
            None if cells else "campaign cell topology unavailable",
        ),
        "consequence_environmental": _surface(
            "SUPPORTED" if disposition == "CONSEQUENCE_MATCHED" else "AT_RISK",
            list((workcycle.get("latest_consequence") or {}).get("evidence_handles") or []),
            None if disposition == "CONSEQUENCE_MATCHED" else "latest consequence not independently matched",
        ),
        "provenance": _surface(
            "SUPPORTED" if history["posture"] == "SUPPORTED" else "UNRESOLVED",
            [temporal_handle] + list((workcycle.get("latest_consequence") or {}).get("evidence_handles") or []),
            None if history["posture"] == "SUPPORTED" else "temporal provenance incomplete",
        ),
        "invariance_meta": _surface(
            "SUPPORTED"
            if disposition == "CONSEQUENCE_MATCHED" and not workcycle.get("projection_errors")
            else "AT_RISK",
            [workcycle_handle],
            None
            if disposition == "CONSEQUENCE_MATCHED" and not workcycle.get("projection_errors")
            else "reconstruction/projection debt remains",
        ),
    }

    six_loads = {
        "functional": {
            "bearing_object": str(next_pressure or "UNRESOLVED"),
            "direction": "INCREASING" if next_pressure else "UNRESOLVED",
            "reason": "declared next pressure carries the next required transformation",
        },
        "semantic": {
            "bearing_object": str(active_horizon or "UNRESOLVED"),
            "direction": "REDISTRIBUTED" if active_horizon else "UNRESOLVED",
            "reason": "campaign intent is condensed into an explicit horizon/current-pressure relation",
        },
        "authority": {
            "bearing_object": str(operative_control.get("status") or "UNRESOLVED"),
            "direction": "INCREASING" if operative_control.get("workflow_enabled") else "STABLE",
            "reason": "operator-local control may permit workflow motion but does not itself admit work",
        },
        "provenance": {
            "bearing_object": temporal_handle,
            "direction": "STABLE" if history["posture"] == "SUPPORTED" else "UNRESOLVED",
            "reason": "horizon must remain challengeable to exact temporal and workcycle evidence",
        },
        "temporal": {
            "bearing_object": temporal_handle,
            "direction": "INCREASING",
            "reason": "history/current/upcoming must remain distinct while composing one horizon candidate",
        },
        "coordination": {
            "bearing_object": str(eligibility.get("posture") or "UNRESOLVED"),
            "direction": "INCREASING" if eligibility.get("eligible") is not True else "DECREASING",
            "reason": "seat/dependency/frame/authority coordinates constrain whether projected work can become admissible",
        },
    }

    distinctions = [
        "HISTORY != CURRENTNESS",
        "TEMPORAL_SUCCESSION != CAUSATION",
        "LATEST_COMPLETED != ACTIVE",
        "PARTIAL_ELIGIBILITY != REAL_ELIGIBILITY",
        "REPO_REQUESTED_CONTROL != OPERATIVE_LOCAL_CONTROL",
        "REGISTERED_SEAT != LIVE_OCCUPANT != EXECUTION_AUTHORITY",
        "WAKE_REQUEST != WORK_ADMISSION != MODEL_INVOCATION",
        "WORK_COMPLETION != CAMPAIGN_ADVANCE",
    ]

    next_work = {
        "candidate_id": f"{campaign_id or 'UNRESOLVED'}::{next_pressure or 'UNRESOLVED'}",
        "campaign_id": campaign_id,
        "horizon_handle": active_horizon,
        "addressed_region": rule["subject"],
        "applicable_distinctions": distinctions,
        "bounded_operator": rule["pressure_direction"],
        "expected_consequence": (
            "reduce the declared horizon boundary without changing authority or "
            "scientific standing merely by producing an artifact"
        ),
        "seven_surface_conservation_envelope": {
            name: value["posture"] for name, value in seven_surfaces.items()
        },
        "six_load_review_debt": list(six_loads),
        "authority_requirement": "EXPLICITLY_UNRESOLVED_UNTIL_ADMISSION",
        "wake_budget_requirement": "ONE_RESERVED_UNIT_REQUIRED_IF_EXECUTION_IS_LATER_ADMITTED",
        "evidence_debt": current_unresolved,
        "stop_condition": "stop after one bounded pressure result; do not auto-admit successor work",
        "repair_destination": "TYPED_REPAIR_ROUTING",
        "admission_effect": "NONE",
        "execution_effect": "NONE",
    }

    development_summary = {
        "available": bool(development_horizons),
        "state_counts": dict((development_horizons or {}).get("state_counts") or {}),
    }

    return {
        "object_type": OBJECT_TYPE,
        "history": history,
        "current": {
            "campaign_id": campaign_id,
            "active_horizon": active_horizon,
            "active_work_item": workcycle.get("active_work_item"),
            "latest_completed_work_item": workcycle.get("latest_completed_work_item"),
            "next_eligible_work_item": workcycle.get("next_eligible_work_item"),
            "current_unresolved": current_unresolved,
            "eligibility": eligibility,
            "operative_control": operative_control,
            "seat_ecology": seat_ecology,
        },
        "upcoming": {
            "declared_next_pressure": next_pressure,
            "source": "WORKCYCLE_DERIVED_CURRENTNESS",
            "execution_effect": "NONE",
        },
        "primary_horizon": {
            "family": rule["family"],
            "subject": rule["subject"],
            "support_predicate": rule["support_predicate"],
            "boundary_condition": rule["boundary_condition"],
            "pressure_direction": rule["pressure_direction"],
            "claim_ceiling": (
                "one bounded horizon candidate derived from exact temporal/current/"
                "declared-upcoming evidence; no causal, standing, authority, or execution claim"
            ),
        },
        "seven_surfaces": seven_surfaces,
        "six_load_dimensions": six_loads,
        "distinctions_applied": distinctions,
        "next_work_candidate": next_work,
        "development_horizon_summary": development_summary,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "campaign_progress_effect": "NONE",
    }
