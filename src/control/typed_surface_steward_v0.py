from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from src.control.relational_change_steward_v0 import (
    FlowWitness,
    RelationObligations,
    RelationState,
    steward_relation_change,
)

SurfaceType = Literal[
    "REPOSITORY_PRODUCER_ROUTE",
    "PYTHON_CALLABLE_INVOCATION",
]

_REQUIRED_FIELDS = {
    "REPOSITORY_PRODUCER_ROUTE": {
        "endpoint": {"output_present", "output_path", "output_blob"},
        "counterpart": {"storage_path", "storage_blob"},
        "edge": {"relation_kind", "declared_output_path", "storage_path", "alignment"},
    },
    "PYTHON_CALLABLE_INVOCATION": {
        "endpoint": {"payload_kind", "endpoint_value", "payload_shape"},
        "counterpart": {"callable_path", "symbol", "code_blob"},
        "edge": {"relation_kind", "binding_mode", "argument_names", "return_coordinate"},
    },
}


@dataclass(frozen=True)
class TypedRelationState:
    surface_type: SurfaceType
    endpoint: Mapping[str, Any]
    counterpart: Mapping[str, Any]
    edge: Mapping[str, Any]


def _field_set(value: Mapping[str, Any]) -> list[str]:
    return sorted(value.keys())


def _validate_component(surface_type: SurfaceType, component: str, value: Mapping[str, Any]) -> None:
    required = _REQUIRED_FIELDS[surface_type][component]
    missing = sorted(required.difference(value.keys()))
    if missing:
        raise ValueError(
            f"{surface_type} {component} missing required fields: {', '.join(missing)}"
        )


def validate_typed_state(state: TypedRelationState) -> dict[str, Any]:
    for component in ("endpoint", "counterpart", "edge"):
        _validate_component(state.surface_type, component, getattr(state, component))
    return {
        "surface_type": state.surface_type,
        "endpoint_fields": _field_set(state.endpoint),
        "counterpart_fields": _field_set(state.counterpart),
        "edge_fields": _field_set(state.edge),
    }


def steward_typed_relation_change(
    *,
    relation_id: str,
    before: TypedRelationState,
    after: TypedRelationState,
    obligations: RelationObligations,
    flow_witness: FlowWitness,
) -> dict[str, Any]:
    if before.surface_type != after.surface_type:
        raise ValueError("surface type must remain stable inside one bounded stewardship check")

    before_geometry = validate_typed_state(before)
    after_geometry = validate_typed_state(after)

    stewardship = steward_relation_change(
        relation_id=relation_id,
        before=RelationState(
            endpoint=dict(before.endpoint),
            counterpart=dict(before.counterpart),
            edge=dict(before.edge),
        ),
        after=RelationState(
            endpoint=dict(after.endpoint),
            counterpart=dict(after.counterpart),
            edge=dict(after.edge),
        ),
        obligations=obligations,
        flow_witness=flow_witness,
    )

    return {
        "object_type": "TYPED_SURFACE_STEWARDSHIP_V0_RESULT",
        "relation_id": relation_id,
        "surface_type": before.surface_type,
        "before_geometry": before_geometry,
        "after_geometry": after_geometry,
        "abstract_roles": ["endpoint", "counterpart", "edge", "flow"],
        "stewardship": stewardship,
        "effects": {
            "surface_mutation_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
    }
