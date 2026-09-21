from __future__ import annotations

import unittest

from tools.lane_b_successor_engagement_repressure_v1 import run_repressure


class LaneBSuccessorEngagementRepressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_repressure()

    def test_exact_source_blobs_are_preserved(self):
        imports = self.result["import_check"]
        self.assertTrue(imports["engagement_exact"])
        self.assertTrue(imports["quiet_peer_exact"])
        self.assertTrue(imports["live_fence_exact"])
        self.assertTrue(all(x["match"] for x in imports["engagement"].values()))
        self.assertTrue(all(x["match"] for x in imports["quiet_peer"].values()))

    def test_A_J_original_engagement_relations_do_not_regress(self):
        expected = {
            "A":("ENGAGEMENT_VALID","COUPLED_ENGAGEMENT_INVARIANT_SATISFIED"),
            "B":("REJECT","OLD_CLAIM_REUSE"),
            "C":("REJECT","OLD_INVOCATION_REUSE"),
            "D":("REJECT","OLD_OCCUPANT_IDENTITY_REUSE"),
            "E":("REJECT","CLAIM_BINDING_MISMATCH:invocation_id"),
            "F":("REJECT","MANIFEST_BINDING_MISMATCH"),
            "G":("REJECT","CLAIM_WITHOUT_BINDING"),
            "H":("NOT_FULLY_ENGAGED","ACTIVE_CLAIM_ABSENT"),
            "I":("REJECT","BINDING_AUTHORITY_EFFECT_NOT_NONE"),
            "J":("STOP","PREDECESSOR_FENCE_INVALID"),
        }
        for cell_id, pair in expected.items():
            with self.subTest(cell=cell_id):
                cell = self.result["cells"][cell_id]
                self.assertEqual((cell["decision"], cell["reason"]), pair)
                self.assertTrue(self.result["cell_checks"][cell_id])
        self.assertEqual(self.result["original_a_j"], "PASS")

    def test_K_known_quiet_peer_is_explicit_and_engagement_valid(self):
        cell = self.result["cells"]["K"]
        self.assertTrue(cell["lane_a_coordinate_present"])
        self.assertEqual(cell["claim_observation"], {"state":"NO_ACTIVE_CLAIM"})
        self.assertFalse(cell["claim_digest_field_present"])
        self.assertFalse(cell["fabricated_digest"])
        self.assertEqual(cell["engagement"]["decision"], "ENGAGEMENT_VALID")
        self.assertTrue(self.result["cell_checks"]["K"])
        self.assertEqual(self.result["quiet_peer_representation"], "PASS")

    def test_L_quiet_to_active_is_causally_required_before_engagement(self):
        acceptance = self.result["cells"]["L"]["acceptance"]
        guard = acceptance["coordination_guard"]
        self.assertEqual(acceptance["decision"], "REVALIDATION_REQUIRED")
        self.assertEqual(acceptance["reason"], "PEER_CLAIM_APPEARED")
        self.assertFalse(acceptance["engagement_evaluated"])
        self.assertFalse(acceptance["engagement_acceptance_reached"])
        self.assertFalse(guard["coordination_clear"])
        self.assertTrue(any(
            x["reason"] == "PEER_CLAIM_APPEARED"
            for x in guard["stale_peers"]
        ))
        self.assertFalse(any(
            x["reason"] == "PEER_NOT_ACKNOWLEDGED"
            for x in guard["stale_peers"]
        ))
        self.assertTrue(self.result["cell_checks"]["L"])

    def test_M_omitted_quiet_coordinate_blocks_before_engagement(self):
        cell = self.result["cells"]["M"]
        acceptance = cell["acceptance"]
        guard = acceptance["coordination_guard"]
        self.assertEqual(acceptance["decision"], "REVALIDATION_REQUIRED")
        self.assertEqual(acceptance["reason"], "PEER_NOT_ACKNOWLEDGED")
        self.assertFalse(acceptance["engagement_evaluated"])
        self.assertFalse(acceptance["engagement_acceptance_reached"])
        self.assertFalse(guard["coordination_clear"])
        self.assertTrue(any(
            x["reason"] == "PEER_NOT_ACKNOWLEDGED"
            for x in guard["stale_peers"]
        ))
        self.assertTrue(self.result["cell_checks"]["M"])

    def test_N_active_overlap_blocks_before_engagement(self):
        acceptance = self.result["cells"]["N"]["acceptance"]
        guard = acceptance["coordination_guard"]
        self.assertEqual(acceptance["decision"], "COORDINATION_HOLD")
        self.assertFalse(acceptance["engagement_evaluated"])
        self.assertFalse(acceptance["engagement_acceptance_reached"])
        self.assertFalse(guard["coordination_clear"])
        self.assertTrue(any(x["coordination_block"] for x in guard["comparisons"]))
        self.assertTrue(self.result["cell_checks"]["N"])

    def test_O_stale_schema_valid_cursor_cannot_bypass_revalidation(self):
        cell = self.result["cells"]["O"]
        acceptance = cell["acceptance"]
        guard = acceptance["coordination_guard"]
        self.assertEqual(acceptance["decision"], "REVALIDATION_REQUIRED")
        self.assertEqual(acceptance["reason"], "PEER_CLAIM_APPEARED")
        self.assertFalse(acceptance["engagement_evaluated"])
        self.assertFalse(acceptance["engagement_acceptance_reached"])
        self.assertFalse(guard["coordination_clear"])
        self.assertTrue(self.result["cell_checks"]["O"])

    def test_O_CONTROL_stable_current_peer_clears_then_engages(self):
        cell = self.result["cells"]["O_CONTROL"]
        acceptance = cell["acceptance"]
        guard = acceptance["coordination_guard"]
        self.assertEqual(guard["coordination_posture"], "NO_COORDINATION_BLOCK")
        self.assertTrue(guard["coordination_clear"])
        self.assertTrue(acceptance["engagement_evaluated"])
        self.assertTrue(acceptance["engagement_acceptance_reached"])
        self.assertEqual(acceptance["decision"], "ENGAGEMENT_VALID")
        self.assertEqual(
            acceptance["reason"],
            "COUPLED_ENGAGEMENT_INVARIANT_SATISFIED",
        )
        self.assertTrue(self.result["cell_checks"]["O_CONTROL"])

    def test_predecessor_fence_remains_exact_and_excluding(self):
        obs = self.result["predecessor_fence_observation"]
        self.assertEqual(obs["historical_status"], "ACTIVE")
        self.assertFalse(obs["current_operability"])
        self.assertEqual(obs["reason"], "PREDECESSOR_FENCED")
        self.assertEqual(
            obs["qualified_payload"],
            "sha256:2cced34cedccb4d763031fdfe3b271a8146473f9995b437fb9f0b894f0fabb86",
        )
        self.assertEqual(self.result["predecessor_fence"], "PASS")

    def test_authority_and_effect_separation_survive(self):
        cell = self.result["cells"]["A"]
        self.assertEqual(cell["authority_effect"], "NONE")
        self.assertEqual(cell["execution_effect"], "NONE")
        self.assertEqual(cell["integration_effect"], "NONE")
        self.assertEqual(cell["effect"], "NONE")
        self.assertEqual(self.result["authority_separation"], "PASS")

    def test_required_summary_is_all_pass(self):
        for key in (
            "binding_model",
            "claim_binding_correspondence",
            "manifest_binding_correspondence",
            "fresh_invocation",
            "fresh_occupant",
            "quiet_peer_representation",
            "quiet_to_active_revalidation",
            "unrepresented_peer_intervention",
            "active_collision_regression",
            "predecessor_fence",
            "authority_separation",
            "current_coordination_coupling",
        ):
            with self.subTest(field=key):
                self.assertEqual(self.result[key], "PASS")

    def test_overall_survives_without_live_effects(self):
        self.assertEqual(
            self.result["result"],
            "LANE_B_SUCCESSOR_ENGAGEMENT_SURVIVES",
        )
        self.assertEqual(self.result["live_successor_mutation"], "NONE")
        self.assertEqual(self.result["live_engagement"], "NONE")
        self.assertEqual(self.result["authority"], "NONE")
        self.assertEqual(self.result["execution"], "NONE")
        self.assertEqual(self.result["merge"], "NONE")
        self.assertTrue(self.result["stop"])


if __name__ == "__main__":
    unittest.main()
