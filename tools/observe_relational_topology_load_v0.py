#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.relational_topology_load_v0 import (
    RelationalTopology,
    TopologyEdge,
    TopologyNode,
    evaluate_focal_incoming_load,
    normalized_topology_consequence_signature,
)

OUT = ROOT / "docs" / "evidence" / "for_planner" / "relational_topology_load_v0_observation.json"

EXPECTED_BLOBS = {
    "h1_adjudication": (
        "docs/campaigns/relational_invariance_load_001/pressure_runs/RELATIONAL_INVARIANCE_LOAD_V0_ADJUDICATION_RESULT_001.md",
        "d0fa23ee2301024e9a6b96dede95ec62b253156f",
    ),
    "projection": (
        "docs/projections/RELATIONAL_INVARIANCE_FOUNDATION_PRESSURE_TRAIN_V0.md",
        "c09a78d496a0df65ec9570ee05bfbd6d21f5f80a",
    ),
    "topology_evaluator": (
        "src/control/relational_topology_load_v0.py",
        "810d05ed8dfdfb72b7b6e2cc052d511ac8d8a865",
    ),
    "horizon": (
        "docs/campaigns/relational_topology_load_001/HORIZON_SELECTION_RTL1_V0.md",
        "a40c1c31e18b8a5a5b078ad380a8849c6345afb9",
    ),
    "contract": (
        "docs/campaigns/relational_topology_load_001/RTL1_CONTRACT_V0.md",
        "5100e36f23091d37c89b404c861a079f85f9ddbe",
    ),
}


def git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def base_nodes() -> tuple[TopologyNode, ...]:
    return (
        TopologyNode("A", 99),
        TopologyNode("B", 3),
        TopologyNode("C", 99),
        TopologyNode("D", 3),
    )


def edge_load_multiset(topology: RelationalTopology) -> list[int]:
    return sorted(edge.load for edge in topology.edges if edge.active)


def focal_edge_dict(topology: RelationalTopology, edge_id: str) -> dict:
    edge = next(edge for edge in topology.edges if edge.edge_id == edge_id)
    return {
        "edge_id": edge.edge_id,
        "source": edge.source,
        "target": edge.target,
        "load": edge.load,
        "active": edge.active,
    }


def local_endpoint_state(topology: RelationalTopology, focal_edge_id: str) -> dict:
    nodes = {node.node_id: node for node in topology.nodes}
    edge = next(edge for edge in topology.edges if edge.edge_id == focal_edge_id)
    return {
        "source_id": edge.source,
        "source_incoming_capacity": nodes[edge.source].incoming_capacity,
        "target_id": edge.target,
        "target_incoming_capacity": nodes[edge.target].incoming_capacity,
    }


def topology_fixture(nodes, edges) -> RelationalTopology:
    return RelationalTopology(nodes=tuple(nodes), edges=tuple(edges))


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    actual_blobs = {
        name: git_blob(path)
        for name, (path, _) in EXPECTED_BLOBS.items()
    }
    blob_checks = {
        name: actual_blobs[name] == expected
        for name, (_, expected) in EXPECTED_BLOBS.items()
    }
    if not all(blob_checks.values()):
        raise SystemExit(f"frozen blob mismatch: {blob_checks}")

    focal = TopologyEdge("FOCAL", "A", "B", 2, True)

    t0_topology = topology_fixture(
        base_nodes(),
        (
            focal,
            TopologyEdge("CONTEXT", "C", "D", 2, True),
        ),
    )
    t1_topology = topology_fixture(
        base_nodes(),
        (
            focal,
            TopologyEdge("CONTEXT", "C", "B", 2, True),
        ),
    )

    t0 = evaluate_focal_incoming_load(t0_topology, focal_edge_id="FOCAL")
    t1 = evaluate_focal_incoming_load(t1_topology, focal_edge_id="FOCAL")

    # Bijective symbol renaming of T1 preserving incidence/capacity/load.
    t2_topology = topology_fixture(
        (
            TopologyNode("P", 99),
            TopologyNode("Q", 3),
            TopologyNode("R", 99),
            TopologyNode("S", 3),
        ),
        (
            TopologyEdge("EDGE_ALPHA", "P", "Q", 2, True),
            TopologyEdge("EDGE_BETA", "R", "Q", 2, True),
        ),
    )
    t2 = evaluate_focal_incoming_load(t2_topology, focal_edge_id="EDGE_ALPHA")

    # T3 operative topology remains T1; represented topology omits CONTEXT.
    t3_operative_topology = t1_topology
    t3_represented_topology = topology_fixture(
        base_nodes(),
        (focal,),
    )
    t3_operative = evaluate_focal_incoming_load(
        t3_operative_topology,
        focal_edge_id="FOCAL",
    )
    t3_represented = evaluate_focal_incoming_load(
        t3_represented_topology,
        focal_edge_id="FOCAL",
    )

    t1_signature = normalized_topology_consequence_signature(t1)
    t2_signature = normalized_topology_consequence_signature(t2)

    checks = {
        "frozen_blobs_match": all(blob_checks.values()),
        "t0_supported": t0["consequence_posture"] == "SUPPORTED",
        "t1_hold": t1["consequence_posture"] == "HOLD",
        "t0_t1_same_nodes_and_capacities": t0_topology.nodes == t1_topology.nodes,
        "t0_t1_same_focal_relation": (
            focal_edge_dict(t0_topology, "FOCAL")
            == focal_edge_dict(t1_topology, "FOCAL")
        ),
        "t0_t1_same_focal_endpoint_state": (
            local_endpoint_state(t0_topology, "FOCAL")
            == local_endpoint_state(t1_topology, "FOCAL")
        ),
        "t0_t1_same_edge_count": len(t0_topology.edges) == len(t1_topology.edges),
        "t0_t1_same_edge_load_multiset": (
            edge_load_multiset(t0_topology)
            == edge_load_multiset(t1_topology)
        ),
        "t0_t1_only_context_target_changes": (
            t0_topology.edges[1].edge_id == t1_topology.edges[1].edge_id == "CONTEXT"
            and t0_topology.edges[1].source == t1_topology.edges[1].source == "C"
            and t0_topology.edges[1].load == t1_topology.edges[1].load == 2
            and t0_topology.edges[1].active == t1_topology.edges[1].active is True
            and t0_topology.edges[1].target == "D"
            and t1_topology.edges[1].target == "B"
        ),
        "t0_t1_consequence_differs": (
            t0["consequence_posture"] != t1["consequence_posture"]
        ),
        "t2_raw_labels_differ_from_t1": (
            t2_topology.nodes != t1_topology.nodes
            and t2_topology.edges != t1_topology.edges
        ),
        "t2_hold": t2["consequence_posture"] == "HOLD",
        "t2_normalized_signature_matches_t1": t2_signature == t1_signature,
        "t3_local_focal_relation_identical": (
            focal_edge_dict(t3_operative_topology, "FOCAL")
            == focal_edge_dict(t3_represented_topology, "FOCAL")
        ),
        "t3_operative_hold": t3_operative["consequence_posture"] == "HOLD",
        "t3_represented_prediction_supported": (
            t3_represented["consequence_posture"] == "SUPPORTED"
        ),
        "t3_prediction_fracture": (
            t3_operative["consequence_posture"]
            != t3_represented["consequence_posture"]
        ),
        "t3_context_edge_operatively_present_but_unrepresented": (
            any(edge.edge_id == "CONTEXT" for edge in t3_operative_topology.edges)
            and not any(
                edge.edge_id == "CONTEXT"
                for edge in t3_represented_topology.edges
            )
        ),
    }

    observation = {
        "object_type": "RELATIONAL_TOPOLOGY_LOAD_V0_OBSERVATION",
        "pressure_id": "RELATIONAL_TOPOLOGY_LOAD_V0_PRESSURE_001",
        "frozen_basis": {
            "expected_blobs": {
                name: expected
                for name, (_, expected) in EXPECTED_BLOBS.items()
            },
            "actual_blobs": actual_blobs,
            "blob_checks": blob_checks,
        },
        "declared_transformation_class": (
            "BIJECTIVE_TOPOLOGY_SYMBOL_RENAMING_PRESERVING_INCIDENCE_CAPACITY_AND_LOAD"
        ),
        "cases": {
            "t0_context_distributed_away": {
                "topology": {
                    "nodes": [node.__dict__ for node in t0_topology.nodes],
                    "edges": [edge.__dict__ for edge in t0_topology.edges],
                },
                "result": t0,
            },
            "t1_context_rewired_to_focal_target": {
                "topology": {
                    "nodes": [node.__dict__ for node in t1_topology.nodes],
                    "edges": [edge.__dict__ for edge in t1_topology.edges],
                },
                "result": t1,
            },
            "t2_bijective_topology_renaming": {
                "topology": {
                    "nodes": [node.__dict__ for node in t2_topology.nodes],
                    "edges": [edge.__dict__ for edge in t2_topology.edges],
                },
                "result": t2,
            },
            "t3_unrepresented_context_edge": {
                "operative_topology": {
                    "nodes": [
                        node.__dict__ for node in t3_operative_topology.nodes
                    ],
                    "edges": [
                        edge.__dict__ for edge in t3_operative_topology.edges
                    ],
                },
                "represented_topology": {
                    "nodes": [
                        node.__dict__ for node in t3_represented_topology.nodes
                    ],
                    "edges": [
                        edge.__dict__ for edge in t3_represented_topology.edges
                    ],
                },
                "operative_result": t3_operative,
                "represented_prediction": t3_represented,
            },
        },
        "normalized_signatures": {
            "t1_context_rewired_to_focal_target": t1_signature,
            "t2_bijective_topology_renaming": t2_signature,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "candidate_relations": {
            "local_relation_state_equivalence_ne_topological_consequence_equivalence": "YES",
            "qualified_topological_consequence_invariant_under_bijective_renaming": "YES",
            "represented_relational_topology_ne_operative_relational_topology": "YES",
            "unrepresented_coupling_can_carry_consequence_within_declared_horizon": "YES",
            "relational_topology_carries_consequential_load_beyond_isolated_local_relation": "YES",
        },
        "effects": {
            "relation_discovery_effect": "NONE",
            "global_topology_law_effect": "NONE",
            "trajectory_law_effect": "NONE",
            "planning_effect": "NONE",
            "seat_identity_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One deterministic four-node/two-edge load-topology family with one "
            "focal relation, one surrounding relation, one bijective topology-symbol "
            "renaming control, and one observer-omission intervention. The pressure "
            "tests whether surrounding incidence/load configuration changes the focal "
            "consequence while the local focal relation is fixed, and whether omission "
            "of an operative coupling fractures the represented prediction. No "
            "universal topology law, causal ontology, global coupling, physical-world "
            "validation, trajectory/history law, planning activation, seat identity "
            "law, authority, execution, global invariance, or scientific standing is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] T0 focal consequence {t0['consequence_posture']}")
    print(f"[OK] T1 focal consequence {t1['consequence_posture']}")
    print(f"[OK] T0/T1 local relation identical {checks['t0_t1_same_focal_relation']}")
    print(f"[OK] T0/T1 endpoint state identical {checks['t0_t1_same_focal_endpoint_state']}")
    print(f"[OK] T0/T1 edge-load multiset identical {checks['t0_t1_same_edge_load_multiset']}")
    print(f"[OK] T2 normalized signature matches T1 {checks['t2_normalized_signature_matches_t1']}")
    print(f"[OK] T3 operative consequence {t3_operative['consequence_posture']}")
    print(f"[OK] T3 represented prediction {t3_represented['consequence_posture']}")
    print(f"[OK] T3 prediction fracture {checks['t3_prediction_fracture']}")
    print(f"[OK] all_checks_pass {observation['all_checks_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
