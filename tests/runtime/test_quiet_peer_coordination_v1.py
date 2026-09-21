from __future__ import annotations

import copy
import unittest

from tools.two_lane_coordination_v1 import (
    PeerStateCoordinationError,
    acknowledge_peer_states,
    pre_mutation_guard,
    quiet_observation,
    run_pressure,
    validate_cursor,
    validate_peer_state_observation,
)


class QuietPeerCoordinationV1Qualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_pressure()

    def test_A_quiet_peer_explicitly_represented(self):
        cell = self.result["cells"]["A"]
        self.assertTrue(cell["pass"])
        row = cell["cursor"]["peer_coordinates"][0]
        self.assertEqual(row["lane_id"], "LANE_A")
        self.assertEqual(row["claim_observation"], {"state":"NO_ACTIVE_CLAIM"})
        self.assertNotIn("claim_digest", row["claim_observation"])

    def test_B_active_peer_representation_preserves_v0_digest(self):
        cell = self.result["cells"]["B"]
        self.assertTrue(cell["pass"])
        v1 = cell["cursor_v1"]["peer_coordinates"][0]["claim_observation"]["claim_digest"]
        v0 = cell["cursor_v0"]["peer_coordinates"][0]["last_seen_claim_digest"]
        self.assertEqual(v1, v0)

    def test_C_null_digest_counterfeit_rejected(self):
        cell = self.result["cells"]["C"]
        self.assertTrue(cell["pass"])
        self.assertFalse(cell["valid"])
        self.assertIn("NO_ACTIVE_CLAIM coordinate forbids claim_digest", cell["error"])

    def test_D_fake_digest_for_absence_rejected(self):
        cell = self.result["cells"]["D"]
        self.assertTrue(cell["pass"])
        self.assertFalse(cell["valid"])
        self.assertIn("NO_ACTIVE_CLAIM coordinate forbids claim_digest", cell["error"])

    def test_E_active_without_digest_rejected(self):
        cell = self.result["cells"]["E"]
        self.assertTrue(cell["pass"])
        self.assertFalse(cell["valid"])
        self.assertIn("ACTIVE_CLAIM coordinate requires exact digest field", cell["error"])

    def test_F_quiet_to_active_revalidates(self):
        guard = self.result["cells"]["F"]["guard"]
        self.assertEqual(guard["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertTrue(any(x["reason"] == "PEER_CLAIM_APPEARED" for x in guard["stale_peers"]))

    def test_G_active_digest_change_revalidates(self):
        guard = self.result["cells"]["G"]["guard"]
        self.assertEqual(guard["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertTrue(any(x["reason"] == "PEER_CLAIM_CHANGED" for x in guard["stale_peers"]))

    def test_H_active_to_quiet_revalidates(self):
        guard = self.result["cells"]["H"]["guard"]
        self.assertEqual(guard["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertTrue(any(x["reason"] == "PEER_CLAIM_DISAPPEARED" for x in guard["stale_peers"]))

    def test_I_quiet_stable_needs_no_revalidation(self):
        guard = self.result["cells"]["I"]["guard"]
        self.assertEqual(guard["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(guard["coordination_clear"])
        self.assertEqual(guard["comparisons"], [])
        self.assertEqual(guard["peer_activity_advances"], [])

    def test_J_quiet_head_advance_is_visible_and_nonblocking(self):
        guard = self.result["cells"]["J"]["guard"]
        self.assertEqual(guard["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(guard["coordination_clear"])
        self.assertTrue(any(
            x["reason"] == "PEER_ACTIVITY_ADVANCED_NO_ACTIVE_CLAIM"
            for x in guard["peer_activity_advances"]
        ))

    def test_K_omitted_quiet_coordinate_is_not_acknowledged(self):
        cell = self.result["cells"]["K"]
        self.assertTrue(cell["pass"])
        self.assertEqual(cell["explicit_cursor_guard"]["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertEqual(cell["omitted_cursor_guard"]["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertTrue(any(
            x["reason"] == "PEER_NOT_ACKNOWLEDGED"
            for x in cell["omitted_cursor_guard"]["stale_peers"]
        ))

    def test_L_active_collision_regression(self):
        guard = self.result["cells"]["L"]["guard"]
        self.assertEqual(guard["coordination_posture"], "COORDINATION_HOLD")
        self.assertFalse(guard["coordination_clear"])
        self.assertTrue(any(x["coordination_block"] for x in guard["comparisons"]))

    def test_M_fenced_predecessor_regression(self):
        guard = self.result["cells"]["M"]["guard"]
        self.assertEqual(guard["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(guard["coordination_clear"])
        self.assertEqual(guard["comparisons"][0]["relation"], "FENCED_PREDECESSOR_EXCLUDED")
        self.assertFalse(guard["fence_consultations"][0]["predecessor_currently_operative"])

    def test_absence_requires_explicit_claim_path_basis(self):
        quiet = copy.deepcopy(self.result["cells"]["A"]["cursor"])
        self.assertEqual(quiet["peer_coordinates"][0]["claim_observation"], {"state":"NO_ACTIVE_CLAIM"})

        # Producer input cannot manufacture NO_ACTIVE_CLAIM from omitted basis.
        raw = {
            "schema":"PEER_STATE_OBSERVATION_v1",
            "lane_id":"LANE_A",
            "branch":"lane-a-cockpit-coordination-v0",
            "head":"de667390d81c1219abfee063d2a3b1fe13d1ba71",
            "lane_manifest":{
                "schema":"two_lane_lane_manifest_v0",
                "lane_id":"LANE_A",
                "branch":"lane-a-cockpit-coordination-v0",
                "intended_horizon":"Cockpit / coordination / operator interaction",
                "coordination_contract_ref":"git:ee178c23124cac68bd8b5a3bc75ce16a486845b9",
                "status":"READY_UNCLAIMED",
                "occupant_binding":None,
                "active_work_claim_path":"coordination/active_work_claim.json",
                "peer_cursor_path":"coordination/peer_cursor.json",
                "authority_effect":"NONE",
                "execution_effect":"NONE",
                "integration_effect":"NONE",
            },
            "claim_presence":"NO_ACTIVE_CLAIM",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        with self.assertRaises(PeerStateCoordinationError):
            validate_peer_state_observation(raw)

    def test_overall_survives_with_no_effects(self):
        self.assertEqual(
            self.result["result"],
            "QUIET_PEER_COORDINATION_REPRESENTATION_SURVIVES",
        )
        self.assertTrue(all(self.result["cell_checks"].values()))
        self.assertEqual(self.result["live_mutation"], "NONE")
        self.assertEqual(self.result["authority"], "NONE")
        self.assertEqual(self.result["execution"], "NONE")
        self.assertEqual(self.result["merge"], "NONE")
        self.assertTrue(self.result["stop"])


if __name__ == "__main__":
    unittest.main()
