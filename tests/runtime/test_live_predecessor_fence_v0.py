from __future__ import annotations

import unittest

from tools.live_predecessor_fence_v0 import (
    evaluate_attempt,
    load_live_fence,
    overlapping_successor_candidate,
    predecessor_attempt_from_claim,
    validate_live_fence,
    verify_live_fence,
)
from tools.two_lane_coordination_v0 import acknowledge, pre_mutation_guard


HEAD = "41316921b211c1daf75c9b71b8147e0eb67d372d"


def successor_claim(doc: dict) -> dict:
    p = doc["predecessor_snapshot"]
    return {
        "schema":"two_lane_work_claim_v0",
        "claim_id":"SYNTHETIC-ZOMBIE-VERIFY-CLAIM",
        "lane_id":"LANE_B_SUCCESSOR_CANDIDATE",
        "seat_id":"SYNTHETIC-SEAT",
        "occupant_id":"SYNTHETIC-OCCUPANT",
        "invocation_id":"SYNTHETIC-INVOCATION",
        "branch":"synthetic-not-activated",
        "basis_head":"0"*40,
        "target_lineage":p["target_lineage"],
        "campaign_id":None,
        "pressure_id":"LIVE_LANE_B_PREDECESSOR_FENCE_001",
        "addressed_role":"WORKSHOP",
        "binding_ref":"SYNTHETIC-NON-ACTIVATED",
        "consequence_envelope_id":p["consequence_envelope_id"],
        "semantic_surfaces":[p["semantic_surfaces"][0]],
        "artifact_scopes":[p["artifact_scopes"][0]],
        "mutation_paths":[],
        "status":"ACTIVE",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
        "priority_effect":"NONE",
    }


class LiveLaneBPredecessorFenceTests(unittest.TestCase):
    def test_direct_old_coordinates_are_fenced_without_history_rewrite(self):
        result = verify_live_fence(HEAD)
        self.assertEqual(result["historical_claim_status"], "ACTIVE")
        self.assertIsNotNone(result["historical_occupant_binding"])
        direct = result["direct_predecessor_effect_attempt"]
        self.assertEqual(direct["decision"], "REJECT")
        self.assertEqual(direct["reason"], "PREDECESSOR_FENCED")
        self.assertFalse(direct["predecessor_currently_operative"])

    def test_zombie_pair_changes_only_operability_consequence(self):
        result = verify_live_fence(HEAD)
        with_fence = result["zombie_overlap_with_fence"]
        without = result["zombie_overlap_counterfactual_without_fence"]
        self.assertTrue(with_fence["semantic_overlap"])
        self.assertTrue(with_fence["provenance_overlap"])
        self.assertFalse(with_fence["predecessor_currently_operative"])
        self.assertEqual(with_fence["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(without["predecessor_currently_operative"])
        self.assertEqual(without["coordination_posture"], "COORDINATION_HOLD")
        self.assertEqual(without["reason"], "ACTIVE_PREDECESSOR_OVERLAP")

    def test_authoritative_two_lane_guard_consults_live_fence(self):
        doc = load_live_fence()
        validate_live_fence(doc)
        local = successor_claim(doc)
        peer = doc["historical_claim_object"]
        current = {"LANE_B":{"branch":peer["branch"],"head":HEAD}}
        cursor = acknowledge(
            consumer_lane_id=local["lane_id"],
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
        self.assertEqual(result["comparisons"][0]["relation"], "FENCED_PREDECESSOR_EXCLUDED")
        self.assertTrue(result["comparisons"][0]["semantic_overlap"])
        self.assertTrue(result["comparisons"][0]["provenance_overlap"])
        self.assertFalse(result["comparisons"][0]["peer_currently_operative"])
        self.assertEqual(len(result["fence_consultations"]), 1)
        self.assertEqual(result["fence_consultations"][0]["reason"], "PREDECESSOR_FENCED")

    def test_predecessor_advance_conflicts(self):
        doc=load_live_fence()
        result=evaluate_attempt(
            attempt=predecessor_attempt_from_claim(doc, doc["historical_claim_object"]),
            observed_predecessor_head="a"*40,
            include_fence=True,
            doc=doc,
        )
        self.assertEqual(result["decision"], "CONFLICT_STOP")
        self.assertEqual(result["reason"], "PREDECESSOR_ADVANCED_AFTER_FENCE")

    def test_debt_and_non_effects_preserved(self):
        doc=load_live_fence()
        ids=validate_live_fence(doc)
        self.assertEqual(doc["predecessor_debt"]["p09"]["standing"], "NOT_ESTABLISHED")
        self.assertEqual(doc["predecessor_debt"]["p10"]["standing"], "NOT_ESTABLISHED")
        self.assertEqual(doc["predecessor_debt"]["p11"]["standing"], "NOT_ESTABLISHED")
        self.assertEqual(doc["predecessor_debt"]["p18"]["standing"], "UNRESOLVED")
        self.assertEqual(doc["effect"], "FUTURE_EFFECT_EXCLUSION_ONLY")
        for k in ("historical_disposition_effect","authority_effect","completion_effect","release_effect","history_rewrite_effect"):
            self.assertEqual(doc[k], "NONE")
        self.assertEqual(ids["qualified_fence_payload_identity"], "sha256:2cced34cedccb4d763031fdfe3b271a8146473f9995b437fb9f0b894f0fabb86")


if __name__ == "__main__":
    unittest.main()
