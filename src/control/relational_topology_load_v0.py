from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence


ConsequencePosture = Literal["SUPPORTED", "HOLD"]


@dataclass(frozen=True)
class TopologyNode:
    node_id: str
    incoming_capacity: int


@dataclass(frozen=True)
class TopologyEdge:
    edge_id: str
    source: str
    target: str
    load: int
    active: bool = True


@dataclass(frozen=True)
class RelationalTopology:
    nodes: tuple[TopologyNode, ...]
    edges: tuple[TopologyEdge, ...]


def evaluate_focal_incoming_load(
    topology: RelationalTopology,
    *,
    focal_edge_id: str,
) -> dict:
    nodes = {node.node_id: node for node in topology.nodes}
    edges = {edge.edge_id: edge for edge in topology.edges}

    if len(nodes) != len(topology.nodes):
        raise ValueError("duplicate node id")
    if len(edges) != len(topology.edges):
        raise ValueError("duplicate edge id")
    if focal_edge_id not in edges:
        raise ValueError("focal edge missing")

    for node in topology.nodes:
        if node.incoming_capacity < 0:
            raise ValueError("negative incoming capacity")

    for edge in topology.edges:
        if edge.source not in nodes or edge.target not in nodes:
            raise ValueError("edge endpoint missing")
        if edge.load < 0:
            raise ValueError("negative edge load")

    focal = edges[focal_edge_id]
    if not focal.active:
        raise ValueError("focal edge must be active")

    target = nodes[focal.target]
    incoming = tuple(
        edge
        for edge in topology.edges
        if edge.active and edge.target == focal.target
    )
    total_incoming_load = sum(edge.load for edge in incoming)
    consequence: ConsequencePosture = (
        "SUPPORTED"
        if total_incoming_load <= target.incoming_capacity
        else "HOLD"
    )

    return {
        "object_type": "RELATIONAL_TOPOLOGY_LOAD_V0_RESULT",
        "focal_edge": {
            "edge_id": focal.edge_id,
            "source": focal.source,
            "target": focal.target,
            "load": focal.load,
        },
        "focal_endpoint_state": {
            "source_node": focal.source,
            "target_node": focal.target,
            "target_incoming_capacity": target.incoming_capacity,
        },
        "incoming_incident_edges": [
            {
                "edge_id": edge.edge_id,
                "source": edge.source,
                "target": edge.target,
                "load": edge.load,
            }
            for edge in incoming
        ],
        "incoming_incident_edge_count": len(incoming),
        "total_incoming_load": total_incoming_load,
        "consequence_posture": consequence,
        "effects": {
            "mutation_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
    }


def normalized_topology_consequence_signature(result: dict) -> dict:
    incoming_loads = sorted(
        edge["load"] for edge in result["incoming_incident_edges"]
    )
    focal = result["focal_edge"]
    return {
        "focal_load": focal["load"],
        "target_incoming_capacity": result["focal_endpoint_state"][
            "target_incoming_capacity"
        ],
        "incoming_incident_edge_count": result["incoming_incident_edge_count"],
        "incoming_incident_loads": incoming_loads,
        "total_incoming_load": result["total_incoming_load"],
        "consequence_posture": result["consequence_posture"],
        "effects": result["effects"],
    }
