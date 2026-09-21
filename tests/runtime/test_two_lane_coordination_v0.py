from __future__ import annotations

import copy
import unittest

from tools.two_lane_coordination_v0 import (
    CoordinationError,
    acknowledge,
    claim_digest,
    compare_claims,
    pre_mutation_guard,
)


H0 = "0" * 40
H1 = "1" * 40
H2 = "2" * 40


def claim(
    *,
    lane: str,
    branch: str,
    basis: str = H0,
    target: str,
    envelope: str,
    semantic: list[str],
    artifacts: list[str],
    paths: list[str],
    claim_id: str,
) -> dict:
    return {
        "schema": "two_lane_work_claim_v0",
        "claim_id": claim_id,
        "lane_id": lane,
        "seat_id": f"{lane}-SEAT",
        "occupant_id": f"{lane}-OCCUPANT",
        "invocation_id": f"{lane}-INVOCATION",
        "branch": branch,
        "basis_head": basis,
        "target_lineage": target,
        "campaign_id": "TWO-LANE-CAMPAIGN",
        "pressure_id": "TWO_LANE_COORDINATION_001",
        "addressed_role": "WORKSHOP" if lane == "LANE_A" else "LAB",
        "binding_ref": f"BINDING:{lane}",
        "consequence_envelope_id": envelope,
        "semantic_surfaces": semantic,
        "artifact_scopes": artifacts,
        "mutation_paths": paths,
        "status": "ACTIVE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "integration_effect": "NONE",
        "priority_effect": "NONE",
    }


def heads(peer: dict, head: str) -> dict:
    return {
        peer["lane_id"]: {
            "branch": peer["branch"],
            "head": head,
        }
    }


class TwoLaneCoordinationPressure(unittest.TestCase):
    def test_a_nonoverlapping_work_has_no_coordination_block(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET-A",
            envelope="ENV-A",
            semantic=["COCKPIT_ADDRESSING"],
            artifacts=["cockpit/ui"],
            paths=["src/cockpit/app.py"],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="TARGET-B",
            envelope="ENV-B",
            semantic=["SEAT_RECOVERY"],
            artifacts=["continuity/recovery"],
            paths=["src/recovery/seat.py"],
            claim_id="CLAIM-B",
        )
        current = heads(peer, H1)
        cursor = acknowledge(
            consumer_lane_id="LANE_A",
            peer_claims=[peer],
            current_peer_heads=current,
        )
        result = pre_mutation_guard(
            local_claim=local,
            peer_claims=[peer],
            cursor=cursor,
            current_peer_heads=current,
        )
        self.assertEqual(result["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(result["coordination_clear"])
        self.assertEqual(result["comparisons"][0]["relation"], "CLEAR")
        self.assertEqual(result["authorization_effect"], "NONE")

    def test_b_same_path_different_semantics_is_representation_overlap_only(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET-A",
            envelope="ENV-A",
            semantic=["UI_NAVIGATION"],
            artifacts=["ui/navigation"],
            paths=["src/shared.py"],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="TARGET-B",
            envelope="ENV-B",
            semantic=["RECOVERY_PARSER"],
            artifacts=["recovery/parser"],
            paths=["src/shared.py"],
            claim_id="CLAIM-B",
        )
        comparison = compare_claims(local, peer)
        self.assertEqual(comparison["relation"], "REPRESENTATION_OVERLAP_ONLY")
        self.assertFalse(comparison["semantic_collision"])
        self.assertFalse(comparison["provenance_collision"])
        self.assertFalse(comparison["coordination_block"])
        self.assertEqual(comparison["path_overlap"], ["src/shared.py"])

    def test_c_different_files_same_semantic_surface_blocks(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET-A",
            envelope="ENV-A",
            semantic=["IDENTITY_CORRESPONDENCE"],
            artifacts=["producer"],
            paths=["src/producer.py"],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="TARGET-B",
            envelope="ENV-B",
            semantic=["IDENTITY_CORRESPONDENCE"],
            artifacts=["consumer"],
            paths=["src/consumer.py"],
            claim_id="CLAIM-B",
        )
        current = heads(peer, H1)
        cursor = acknowledge(
            consumer_lane_id="LANE_A",
            peer_claims=[peer],
            current_peer_heads=current,
        )
        result = pre_mutation_guard(
            local_claim=local,
            peer_claims=[peer],
            cursor=cursor,
            current_peer_heads=current,
        )
        self.assertEqual(result["coordination_posture"], "COORDINATION_HOLD")
        self.assertEqual(result["comparisons"][0]["relation"], "SEMANTIC_COLLISION")

    def test_d_same_consequence_trajectory_blocks_across_isolated_branches(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="INVOCATION_RECOVERY_APPARATUS",
            envelope="IR001-APPARATUS-MATERIALIZATION",
            semantic=["COMMON_COMPONENT_MATERIALIZATION_A"],
            artifacts=["invocation_recovery/common_components"],
            paths=["docs/canonical/common/role.txt"],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="INVOCATION_RECOVERY_APPARATUS",
            envelope="IR001-APPARATUS-MATERIALIZATION",
            semantic=["COMMON_COMPONENT_MATERIALIZATION_B"],
            artifacts=["invocation_recovery/common_components"],
            paths=["fixtures/common/role.txt"],
            claim_id="CLAIM-B",
        )
        comparison = compare_claims(local, peer)
        self.assertFalse(comparison["semantic_collision"])
        self.assertTrue(comparison["provenance_collision"])
        self.assertEqual(comparison["relation"], "PROVENANCE_COLLISION")
        self.assertTrue(comparison["coordination_block"])

    def test_e_stale_peer_head_requires_revalidation_before_overlap_adjudication(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET",
            envelope="ENV-A",
            semantic=["X"],
            artifacts=["a"],
            paths=["a.py"],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="TARGET-B",
            envelope="ENV-B",
            semantic=["Y"],
            artifacts=["b"],
            paths=["b.py"],
            claim_id="CLAIM-B",
        )
        old = heads(peer, H1)
        cursor = acknowledge(
            consumer_lane_id="LANE_A",
            peer_claims=[peer],
            current_peer_heads=old,
        )
        moved = heads(peer, H2)
        result = pre_mutation_guard(
            local_claim=local,
            peer_claims=[peer],
            cursor=cursor,
            current_peer_heads=moved,
        )
        self.assertEqual(result["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertFalse(result["coordination_clear"])
        self.assertEqual(result["comparisons"], [])
        self.assertEqual(result["stale_peers"][0]["reason"], "PEER_HEAD_ADVANCED")

    def test_e_after_revalidation_current_overlap_can_hold(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET",
            envelope="ENV-A",
            semantic=["SHARED-R"],
            artifacts=["a"],
            paths=["a.py"],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="TARGET-B",
            envelope="ENV-B",
            semantic=["SHARED-R"],
            artifacts=["b"],
            paths=["b.py"],
            claim_id="CLAIM-B2",
        )
        current = heads(peer, H2)
        cursor = acknowledge(
            consumer_lane_id="LANE_A",
            peer_claims=[peer],
            current_peer_heads=current,
        )
        result = pre_mutation_guard(
            local_claim=local,
            peer_claims=[peer],
            cursor=cursor,
            current_peer_heads=current,
        )
        self.assertEqual(result["coordination_posture"], "COORDINATION_HOLD")
        self.assertEqual(result["comparisons"][0]["relation"], "SEMANTIC_COLLISION")

    def test_f_claim_digest_change_requires_revalidation_even_if_head_matches(self) -> None:
        local = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET-A",
            envelope="ENV-A",
            semantic=["X"],
            artifacts=["a"],
            paths=[],
            claim_id="CLAIM-A",
        )
        peer = claim(
            lane="LANE_B",
            branch="lane-b",
            target="TARGET-B",
            envelope="ENV-B",
            semantic=["Y"],
            artifacts=["b"],
            paths=[],
            claim_id="CLAIM-B",
        )
        current = heads(peer, H1)
        cursor = acknowledge(
            consumer_lane_id="LANE_A",
            peer_claims=[peer],
            current_peer_heads=current,
        )

        changed = copy.deepcopy(peer)
        changed["semantic_surfaces"] = ["Z"]
        self.assertNotEqual(claim_digest(peer), claim_digest(changed))

        result = pre_mutation_guard(
            local_claim=local,
            peer_claims=[changed],
            cursor=cursor,
            current_peer_heads=current,
        )
        self.assertEqual(result["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertEqual(result["stale_peers"][0]["reason"], "PEER_CLAIM_CHANGED")

    def test_malformed_or_effect_bearing_claim_is_rejected(self) -> None:
        bad = claim(
            lane="LANE_A",
            branch="lane-a",
            target="TARGET",
            envelope="ENV",
            semantic=["X"],
            artifacts=["a"],
            paths=[],
            claim_id="BAD",
        )
        bad["authority_effect"] = "GRANT"
        with self.assertRaisesRegex(CoordinationError, "authority_effect"):
            claim_digest(bad)


if __name__ == "__main__":
    unittest.main()
