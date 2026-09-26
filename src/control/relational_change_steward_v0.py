from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Obligation = Literal["CHANGE", "PRESERVE", "UNRESOLVED"]
FlowExpectation = Literal["PASS", "NOT_REQUIRED", "UNRESOLVED"]
FlowWitness = Literal["PASS", "FAIL", "ABSENT", "NOT_REQUIRED"]
ClosurePosture = Literal["COHERENT", "HOLD", "UNRESOLVED"]


@dataclass(frozen=True)
class RelationState:
    endpoint: Any
    counterpart: Any
    edge: Any


@dataclass(frozen=True)
class RelationObligations:
    endpoint: Obligation
    counterpart: Obligation
    edge: Obligation
    flow: FlowExpectation


def _check_obligation(before: Any, after: Any, obligation: Obligation) -> bool | None:
    if obligation == "UNRESOLVED":
        return None
    changed = before != after
    if obligation == "CHANGE":
        return changed
    if obligation == "PRESERVE":
        return not changed
    raise ValueError(f"unsupported obligation: {obligation}")


def steward_relation_change(
    *,
    relation_id: str,
    before: RelationState,
    after: RelationState,
    obligations: RelationObligations,
    flow_witness: FlowWitness,
) -> dict[str, Any]:
    if not relation_id:
        raise ValueError("relation_id is required")

    checks = {
        "endpoint": _check_obligation(before.endpoint, after.endpoint, obligations.endpoint),
        "counterpart": _check_obligation(
            before.counterpart, after.counterpart, obligations.counterpart
        ),
        "edge": _check_obligation(before.edge, after.edge, obligations.edge),
    }

    unresolved_obligation = any(v is None for v in checks.values()) or obligations.flow == "UNRESOLVED"

    if obligations.flow == "PASS":
        flow_check: bool | None = flow_witness == "PASS"
        flow_witness_required = True
    elif obligations.flow == "NOT_REQUIRED":
        flow_check = flow_witness in ("NOT_REQUIRED", "ABSENT")
        flow_witness_required = False
    else:
        flow_check = None
        flow_witness_required = None

    failed_state_obligation = any(v is False for v in checks.values())
    failed_flow = flow_check is False

    if unresolved_obligation:
        closure: ClosurePosture = "UNRESOLVED"
    elif failed_state_obligation or failed_flow:
        closure = "HOLD"
    else:
        closure = "COHERENT"

    return {
        "object_type": "RELATIONAL_CHANGE_STEWARDSHIP_V0_RESULT",
        "relation_id": relation_id,
        "before": {
            "endpoint": before.endpoint,
            "counterpart": before.counterpart,
            "edge": before.edge,
        },
        "after": {
            "endpoint": after.endpoint,
            "counterpart": after.counterpart,
            "edge": after.edge,
        },
        "obligations": {
            "endpoint": obligations.endpoint,
            "counterpart": obligations.counterpart,
            "edge": obligations.edge,
            "flow": obligations.flow,
        },
        "checks": {
            "endpoint_obligation_satisfied": checks["endpoint"],
            "counterpart_obligation_satisfied": checks["counterpart"],
            "edge_obligation_satisfied": checks["edge"],
            "flow_witness_required": flow_witness_required,
            "flow_witness": flow_witness,
            "flow_obligation_satisfied": flow_check,
        },
        "closure_posture": closure,
        "effects": {
            "mutation_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
    }
