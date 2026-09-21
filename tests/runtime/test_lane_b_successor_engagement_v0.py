from __future__ import annotations

from pathlib import Path
import unittest

from tools.lane_b_successor_engagement_v0 import (
    ROOT,
    PREDECESSOR_CLAIM_ID,
    PREDECESSOR_INVOCATION,
    PREDECESSOR_OCCUPANT,
    clean_bundle,
    eval_bundle,
    pressure_k,
    pressure_l,
    run_pressure,
)


class LaneBSuccessorEngagementQualification(unittest.TestCase):
    def test_A_clean_engagement(self):
        r = eval_bundle(clean_bundle())
        self.assertEqual(r["decision"], "ENGAGEMENT_VALID")
        self.assertEqual(r["reason"], "COUPLED_ENGAGEMENT_INVARIANT_SATISFIED")
        self.assertEqual(r["authority_effect"], "NONE")
        self.assertEqual(r["execution_effect"], "NONE")
        self.assertEqual(r["effect"], "NONE")

    def test_B_old_claim_reuse(self):
        b = clean_bundle()
        b["claim"]["claim_id"] = PREDECESSOR_CLAIM_ID
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("REJECT", "OLD_CLAIM_REUSE"))

    def test_C_old_invocation_reuse(self):
        b = clean_bundle()
        b["binding"]["invocation_id"] = PREDECESSOR_INVOCATION
        b["claim"]["invocation_id"] = PREDECESSOR_INVOCATION
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("REJECT", "OLD_INVOCATION_REUSE"))

    def test_D_old_occupant_reuse(self):
        b = clean_bundle()
        b["binding"]["occupant_id"] = PREDECESSOR_OCCUPANT
        b["claim"]["occupant_id"] = PREDECESSOR_OCCUPANT
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("REJECT", "OLD_OCCUPANT_IDENTITY_REUSE"))

    def test_E_binding_claim_mismatch(self):
        b = clean_bundle()
        b["claim"]["invocation_id"] = "LANE_B_SUCCESSOR_OTHER_FRESH_INVOCATION"
        r = eval_bundle(b)
        self.assertEqual(
            (r["decision"], r["reason"]),
            ("REJECT", "CLAIM_BINDING_MISMATCH:invocation_id"),
        )

    def test_F_manifest_binding_mismatch(self):
        b = clean_bundle()
        b["engaged_manifest"]["occupant_binding"] = "binding://WRONG-BINDING"
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("REJECT", "MANIFEST_BINDING_MISMATCH"))

    def test_G_claim_without_binding(self):
        b = clean_bundle()
        b["binding"] = None
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("REJECT", "CLAIM_WITHOUT_BINDING"))

    def test_H_binding_without_claim(self):
        b = clean_bundle()
        b["claim"] = None
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("NOT_FULLY_ENGAGED", "ACTIVE_CLAIM_ABSENT"))

    def test_I_authority_smuggling(self):
        b = clean_bundle()
        b["binding"]["authority_effect"] = "SMUGGLED"
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("REJECT", "BINDING_AUTHORITY_EFFECT_NOT_NONE"))

    def test_J_invalid_predecessor_fence(self):
        b = clean_bundle()
        b["fence_doc"]["qualified_fence_payload"]["predecessor_head"] = "b" * 40
        r = eval_bundle(b)
        self.assertEqual((r["decision"], r["reason"]), ("STOP", "PREDECESSOR_FENCE_INVALID"))

    def test_K_known_ready_peer_without_claim_is_bounded_fracture(self):
        r = pressure_k()
        self.assertEqual(r["result"], "BOUNDED_FRACTURE")
        self.assertEqual(r["reason"], "KNOWN_READY_UNCLAIMED_PEER_NOT_EXPLICITLY_REPRESENTABLE")
        self.assertFalse(r["lane_a_explicitly_represented"])
        self.assertFalse(r["explicit_null_digest_valid"])
        self.assertFalse(r["explicit_missing_digest_valid"])
        self.assertFalse(r["fabricated_claim_digest_used"])
        self.assertEqual(r["authoritative_acknowledge_output"]["peer_coordinates"], [])

    def test_L_peer_activation_after_quiet_cursor_requires_revalidation(self):
        b = clean_bundle()
        r = pressure_l(b["claim"], b["cursor"])
        self.assertEqual(r["result"], "REVALIDATION_REQUIRED")
        self.assertEqual(r["guard"]["coordination_posture"], "REVALIDATION_REQUIRED")
        self.assertFalse(r["guard"]["coordination_clear"])
        self.assertTrue(
            any(x["reason"] == "PEER_NOT_ACKNOWLEDGED" for x in r["guard"]["stale_peers"])
        )

    def test_overall_disposition_is_scientific_fracture_not_admin_failure(self):
        r = run_pressure()
        self.assertEqual(r["result"], "LANE_B_SUCCESSOR_ENGAGEMENT_FRACTURES")
        self.assertEqual(r["binding_model"], "QUALIFIED")
        self.assertEqual(r["claim_binding_correspondence"], "PASS")
        self.assertEqual(r["manifest_binding_correspondence"], "PASS")
        self.assertEqual(r["fresh_invocation"], "PASS")
        self.assertEqual(r["fresh_occupant"], "PASS")
        self.assertEqual(r["peer_no_claim_representation"], "FRACTURE")
        self.assertEqual(r["peer_change_revalidation"], "PASS")
        self.assertEqual(r["authority_separation"], "PASS")

    def test_live_successor_state_is_not_materialized_by_qualification(self):
        self.assertFalse((ROOT / "coordination/active_work_claim.json").exists())
        self.assertFalse((ROOT / "coordination/peer_cursor.json").exists())
        result = run_pressure()
        self.assertEqual(result["live_successor_mutation"], "NONE")
        self.assertEqual(result["live_engagement"], "NONE")
        self.assertEqual(result["authority"], "NONE")
        self.assertEqual(result["execution"], "NONE")
        self.assertEqual(result["merge"], "NONE")


if __name__ == "__main__":
    unittest.main()
