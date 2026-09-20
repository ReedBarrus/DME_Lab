"""Thin Concordance cockpit primitives.

This module is a read-only projection helper. It does not create authority,
scientific standing, or developmental causality.

Core discipline:
    SEAT != OPERATION != ARTIFACT != HANDOFF != FRACTURE
    EDGE != VISUAL CONNECTOR
    COCKPIT VIEW != SOURCE OF TRUTH
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Literal


OperationStatus = Literal[
    "ADMITTED",
    "RUNNING",
    "FRACTURED",
    "STOPPED",
    "LOST",
    "COMPLETE",
]
HandoffRelation = Literal["PROPOSES", "REQUESTS", "REFERENCES"]
DevelopmentRelation = Literal[
    "RECORDED",
    "REFERENCED_BY",
    "MOTIVATED",
    "CONSTRAINS",
    "INCORPORATED",
    "TEMPORALLY_PRECEDES",
]


@dataclass(frozen=True)
class ArtifactRefV0:
    artifact_id: str
    kind: str
    locator: str


@dataclass(frozen=True)
class SeatV0:
    seat_id: str
    role: str
    continuity_ref: str | None = None
    archetype: str | None = None
    callsign: str | None = None


@dataclass(frozen=True)
class OperationV0:
    operation_id: str
    seat_id: str
    parent_operation_id: str | None
    role: str
    purpose: str
    authority_ref: str | None
    status: OperationStatus
    started_at: str | None = None
    last_progress_at: str | None = None
    last_checkpoint_ref: str | None = None
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    fracture_ref: str | None = None
    stop_reason: str | None = None
    next_proposed_operation: str | None = None


@dataclass(frozen=True)
class HandoffV0:
    handoff_id: str
    from_operation_id: str
    to_seat_id: str
    relation_type: HandoffRelation
    basis_refs: tuple[str, ...]


@dataclass(frozen=True)
class FractureV0:
    fracture_id: str
    operation_id: str
    expected: str
    observed: str
    cause_surface: str | None
    surviving_distinction: str | None
    basis_refs: tuple[str, ...]
    authority_status: str = "NOT_GRANTED"


@dataclass(frozen=True)
class DevelopmentEdgeV0:
    edge_id: str
    from_ref: str
    to_ref: str
    relation_type: DevelopmentRelation
    basis_refs: tuple[str, ...]
    status: Literal["SUPPORTED", "PROVISIONAL"] = "SUPPORTED"


class ConcordanceProjectionError(ValueError):
    pass


def _require_nonempty(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConcordanceProjectionError(f"{label} must be a non-empty string")


def _validate_unique(items: Iterable[object], field: str) -> None:
    seen: set[str] = set()
    for item in items:
        value = getattr(item, field)
        if value in seen:
            raise ConcordanceProjectionError(f"duplicate {field}: {value}")
        seen.add(value)


def _artifact_index(artifacts: tuple[ArtifactRefV0, ...]) -> dict[str, ArtifactRefV0]:
    return {item.artifact_id: item for item in artifacts}


def build_concordance_projection(
    *,
    seats: Iterable[SeatV0],
    operations: Iterable[OperationV0],
    artifacts: Iterable[ArtifactRefV0],
    handoffs: Iterable[HandoffV0],
    fractures: Iterable[FractureV0],
    development_edges: Iterable[DevelopmentEdgeV0] = (),
) -> dict[str, object]:
    """Build a conservative read-only cockpit projection.

    Supported developmental edges require durable basis refs that exist in the
    supplied artifact set. Unsupported/provisional relations are surfaced as
    unresolved relations, never promoted into supported edges.

    Authority is never inferred from handoff, adjacency, operation status, or
    completion. v0 exposes operation.authority_ref only as a reference and marks
    whether that referenced artifact is present.
    """
    seats_t = tuple(seats)
    operations_t = tuple(operations)
    artifacts_t = tuple(artifacts)
    handoffs_t = tuple(handoffs)
    fractures_t = tuple(fractures)
    edges_t = tuple(development_edges)

    _validate_unique(seats_t, "seat_id")
    _validate_unique(operations_t, "operation_id")
    _validate_unique(artifacts_t, "artifact_id")
    _validate_unique(handoffs_t, "handoff_id")
    _validate_unique(fractures_t, "fracture_id")
    _validate_unique(edges_t, "edge_id")

    seat_ids = {x.seat_id for x in seats_t}
    operation_ids = {x.operation_id for x in operations_t}
    fracture_ids = {x.fracture_id for x in fractures_t}
    artifact_by_id = _artifact_index(artifacts_t)
    known_refs = seat_ids | operation_ids | fracture_ids | set(artifact_by_id)

    for seat in seats_t:
        _require_nonempty(seat.seat_id, "seat_id")
        _require_nonempty(seat.role, "seat.role")

    diagnostics: list[dict[str, object]] = []

    operation_rows: list[dict[str, object]] = []
    for op in operations_t:
        _require_nonempty(op.operation_id, "operation_id")
        _require_nonempty(op.seat_id, "operation.seat_id")
        _require_nonempty(op.role, "operation.role")
        _require_nonempty(op.purpose, "operation.purpose")
        if op.seat_id not in seat_ids:
            diagnostics.append(
                {
                    "kind": "MISSING_SEAT_REF",
                    "operation_id": op.operation_id,
                    "seat_id": op.seat_id,
                }
            )
        if op.parent_operation_id and op.parent_operation_id not in operation_ids:
            diagnostics.append(
                {
                    "kind": "MISSING_PARENT_OPERATION_REF",
                    "operation_id": op.operation_id,
                    "parent_operation_id": op.parent_operation_id,
                }
            )
        authority_projection = {
            "authority_ref": op.authority_ref,
            "basis_present": bool(op.authority_ref and op.authority_ref in artifact_by_id),
            "authority_state": "UNRESOLVED_BY_V0",
        }
        if op.authority_ref and op.authority_ref not in artifact_by_id:
            diagnostics.append(
                {
                    "kind": "MISSING_AUTHORITY_REF",
                    "operation_id": op.operation_id,
                    "authority_ref": op.authority_ref,
                }
            )
        if op.fracture_ref and op.fracture_ref not in fracture_ids:
            diagnostics.append(
                {
                    "kind": "MISSING_FRACTURE_REF",
                    "operation_id": op.operation_id,
                    "fracture_ref": op.fracture_ref,
                }
            )
        row = asdict(op)
        row["authority_projection"] = authority_projection
        row["scientific_standing"] = "NOT_INFERRED_BY_V0"
        operation_rows.append(row)

    handoff_rows: list[dict[str, object]] = []
    for handoff in handoffs_t:
        if handoff.relation_type not in {"PROPOSES", "REQUESTS", "REFERENCES"}:
            raise ConcordanceProjectionError(
                f"unsupported handoff relation_type: {handoff.relation_type}"
            )
        missing_basis = [ref for ref in handoff.basis_refs if ref not in artifact_by_id]
        row = asdict(handoff)
        row["authority_effect"] = "NONE"
        row["supported"] = bool(handoff.basis_refs) and not missing_basis
        if not handoff.basis_refs:
            diagnostics.append(
                {
                    "kind": "NO_BASIS_FOR_HANDOFF",
                    "handoff_id": handoff.handoff_id,
                }
            )
        if missing_basis:
            diagnostics.append(
                {
                    "kind": "MISSING_HANDOFF_BASIS",
                    "handoff_id": handoff.handoff_id,
                    "basis_refs": missing_basis,
                }
            )
        handoff_rows.append(row)

    fracture_rows: list[dict[str, object]] = []
    for fracture in fractures_t:
        missing_basis = [ref for ref in fracture.basis_refs if ref not in artifact_by_id]
        row = asdict(fracture)
        row["supported"] = bool(fracture.basis_refs) and not missing_basis
        row["standing_effect"] = "NONE"
        if not fracture.basis_refs:
            diagnostics.append(
                {
                    "kind": "NO_BASIS_FOR_FRACTURE",
                    "fracture_id": fracture.fracture_id,
                }
            )
        if missing_basis:
            diagnostics.append(
                {
                    "kind": "MISSING_FRACTURE_BASIS",
                    "fracture_id": fracture.fracture_id,
                    "basis_refs": missing_basis,
                }
            )
        fracture_rows.append(row)

    supported_edges: list[dict[str, object]] = []
    unresolved_relations: list[dict[str, object]] = []
    for edge in edges_t:
        missing_basis = [ref for ref in edge.basis_refs if ref not in artifact_by_id]
        missing_endpoint = [
            ref for ref in (edge.from_ref, edge.to_ref) if ref not in known_refs
        ]
        reasons: list[str] = []
        if edge.status != "SUPPORTED":
            reasons.append("EDGE_NOT_ADJUDICATED_SUPPORTED")
        if not edge.basis_refs:
            reasons.append("NO_BASIS_FOR_EDGE")
        if missing_basis:
            reasons.append("MISSING_EDGE_BASIS")
        if missing_endpoint:
            reasons.append("MISSING_EDGE_ENDPOINT")

        row = asdict(edge)
        if reasons:
            row["render_status"] = "UNRESOLVED"
            row["reasons"] = reasons
            if missing_basis:
                row["missing_basis_refs"] = missing_basis
            if missing_endpoint:
                row["missing_endpoint_refs"] = missing_endpoint
            unresolved_relations.append(row)
        else:
            row["render_status"] = "SUPPORTED"
            supported_edges.append(row)

    return {
        "schema_version": "concordance_cockpit_projection_v0",
        "projection_claims": {
            "cockpit_view_is_source_of_truth": False,
            "visible_relation_is_semantic_promotion": False,
            "handoff_implies_authority": False,
            "operation_complete_implies_standing": False,
            "fracture_implies_downstream_change": False,
        },
        "seats": [asdict(x) for x in seats_t],
        "operations": operation_rows,
        "artifacts": [asdict(x) for x in artifacts_t],
        "handoffs": handoff_rows,
        "fractures": fracture_rows,
        "development_edges": supported_edges,
        "unresolved_relations": unresolved_relations,
        "diagnostics": diagnostics,
    }
