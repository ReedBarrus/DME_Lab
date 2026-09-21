from __future__ import annotations

import copy
import unittest

from tools.primary_ecology_v0 import (
    EcologyError,
    authority_standing,
    clean_basis,
    clean_binding,
    clean_bundle,
    clean_empty_seat,
    clean_role,
    observation_basis_ref,
    observation_status,
    occupied_seat,
    rotate_invocation,
    rotate_occupant,
    run_pressure,
    validate_correspondence,
    validate_role,
    validate_seat,
)


class PrimaryEcologyGrammarTests(unittest.TestCase):
    def test_A_empty_seat_is_explicit(self):
        seat = clean_empty_seat()
        self.assertEqual(seat["seat_state"], "AVAILABLE_UNOCCUPIED")
        self.assertIsNone(seat["occupant_id"])
        self.assertIsNone(seat["invocation_id"])
        self.assertIsNone(seat["work_claim_ref"])

    def test_B_same_role_can_have_distinct_seats(self):
        a = clean_empty_seat("SCIENCE_TEST_01")
        b = clean_empty_seat("SCIENCE_TEST_02")
        self.assertEqual(a["role_id"], b["role_id"])
        self.assertNotEqual(a["seat_id"], b["seat_id"])

    def test_C_occupant_rotation_preserves_seat_and_drops_local_state(self):
        bundle = clean_bundle()
        old = copy.deepcopy(bundle["binding"])
        old["standing_refs"] = ["standing://OLD"]
        old["authority_refs"] = ["authority://OLD"]
        old["work_claim_ref"] = "claim://OLD"
        new, new_basis = rotate_occupant(
            old,
            bundle["basis"],
            "OCCUPANT_B",
            "INVOCATION_B",
        )
        new_seat = occupied_seat(
            seat=clean_empty_seat(new["seat_id"]),
            occupant_id=new["occupant_id"],
            invocation_id=new["invocation_id"],
        )
        validate_correspondence(
            role=bundle["role"],
            seat=new_seat,
            binding=new,
            basis=new_basis,
        )
        self.assertEqual(new["seat_id"], old["seat_id"])
        self.assertNotEqual(new["occupant_id"], old["occupant_id"])
        self.assertEqual(new["standing_refs"], [])
        self.assertEqual(new["authority_refs"], [])
        self.assertIsNone(new["work_claim_ref"])

    def test_D_invocation_rotation_does_not_inherit_prior_standing(self):
        bundle = clean_bundle()
        old = copy.deepcopy(bundle["binding"])
        old["standing_refs"] = ["standing://OLD"]
        old["authority_refs"] = ["authority://OLD"]
        old["work_claim_ref"] = "claim://OLD"
        new, new_basis = rotate_invocation(old, bundle["basis"], "INVOCATION_C")
        new_seat = occupied_seat(
            seat=clean_empty_seat(new["seat_id"]),
            occupant_id=new["occupant_id"],
            invocation_id=new["invocation_id"],
        )
        validate_correspondence(
            role=bundle["role"],
            seat=new_seat,
            binding=new,
            basis=new_basis,
        )
        self.assertEqual(new["occupant_id"], old["occupant_id"])
        self.assertNotEqual(new["invocation_id"], old["invocation_id"])
        self.assertEqual(new["standing_refs"], [])
        self.assertEqual(new["authority_refs"], [])
        self.assertIsNone(new["work_claim_ref"])

    def test_E_engagement_can_exist_without_work_claim(self):
        binding = clean_binding()
        self.assertIsNone(binding["work_claim_ref"])

    def test_F_work_claim_reference_does_not_manufacture_authority(self):
        binding = clean_binding()
        binding["work_claim_ref"] = "claim://CANDIDATE"
        self.assertEqual(authority_standing(binding), "ABSENT")

    def test_G_role_authority_leak_rejected(self):
        role = clean_role()
        role["authority_effect"] = "GRANT"
        with self.assertRaisesRegex(EcologyError, "ROLE_AUTHORITY_EFFECT_NOT_NONE"):
            validate_role(role)

    def test_H_unobserved_world_object_is_unknown(self):
        basis = clean_basis()
        self.assertEqual(observation_status(basis, "WORLD_OBJECT_NOT_IN_BASIS"), "UNKNOWN")

    def test_I_explicit_missing_is_not_absent(self):
        basis = clean_basis()
        self.assertEqual(observation_status(basis, "MISSING_OBJECT"), "MISSING")

    def test_J_later_world_change_does_not_rewrite_prior_basis(self):
        basis = clean_basis()
        before = observation_status(basis, "LATER_WORLD_OBJECT")
        later_world = {"objects":["LATER_WORLD_OBJECT"]}
        after = observation_status(basis, "LATER_WORLD_OBJECT")
        self.assertIn("LATER_WORLD_OBJECT", later_world["objects"])
        self.assertEqual((before, after), ("UNKNOWN", "UNKNOWN"))

    def test_K_placeholder_occupant_is_rejected(self):
        seat = clean_empty_seat()
        seat["seat_state"] = "OCCUPIED_CANDIDATE"
        seat["occupant_id"] = "TBD"
        seat["invocation_id"] = "INVOCATION_TEST"
        with self.assertRaisesRegex(EcologyError, "placeholder identity forbidden"):
            validate_seat(seat)

    def test_L_role_label_or_authority_ref_is_not_authority(self):
        role = clean_role()
        role["role_id"] = "AUTHORIZER_TEST_ROLE"
        validate_role(role)
        binding = clean_binding()
        binding["authority_refs"] = ["authority://UNQUALIFIED"]
        self.assertEqual(role["authority_effect"], "NONE")
        self.assertEqual(authority_standing(binding), "UNADJUDICATED")

    def test_M1_invocation_basis_mismatch_rejected(self):
        b = clean_bundle()
        b["seat"]["invocation_id"] = "INVOCATION_B"
        b["binding"]["invocation_id"] = "INVOCATION_B"
        with self.assertRaisesRegex(EcologyError, "BINDING_BASIS_INVOCATION_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_M2_occupant_basis_mismatch_rejected(self):
        b = clean_bundle()
        b["seat"]["occupant_id"] = "OCCUPANT_B"
        b["binding"]["occupant_id"] = "OCCUPANT_B"
        with self.assertRaisesRegex(EcologyError, "BINDING_BASIS_OCCUPANT_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_M3_seat_basis_mismatch_rejected(self):
        b = clean_bundle()
        b["seat"] = occupied_seat(
            seat=clean_empty_seat("SCIENCE_TEST_02"),
            occupant_id=b["binding"]["occupant_id"],
            invocation_id=b["binding"]["invocation_id"],
        )
        b["binding"]["seat_id"] = "SCIENCE_TEST_02"
        with self.assertRaisesRegex(EcologyError, "BINDING_BASIS_SEAT_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_M4_role_seat_binding_mismatch_rejected(self):
        b = clean_bundle()
        b["binding"]["role_id"] = "PLANNER"
        with self.assertRaisesRegex(EcologyError, "ROLE_SEAT_BINDING_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_observation_basis_ref_pins_exact_basis_bytes(self):
        b = clean_bundle()
        original_ref = observation_basis_ref(b["basis"])
        self.assertEqual(b["binding"]["observation_basis_ref"], original_ref)
        b["basis"]["source_refs"].append("fixture://LATER-MUTATION")
        with self.assertRaisesRegex(EcologyError, "BINDING_OBSERVATION_BASIS_REF_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_occupied_seat_requires_explicit_occupant_and_invocation(self):
        seat = occupied_seat(
            seat=clean_empty_seat(),
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_TEST_001",
        )
        self.assertEqual(seat["seat_state"], "OCCUPIED_CANDIDATE")
        self.assertEqual(seat["seat_id"], "SCIENCE_TEST_01")

    def test_overall_pressure_is_bounded_and_nonconsequential(self):
        result = run_pressure()
        self.assertEqual(result["status"], "QUALIFIED_SYNTHETIC_GRAMMAR")
        self.assertTrue(all(cell["result"] == "PASS" for cell in result["cells"].values()))
        self.assertEqual(
            result["core_relations"]["cross_object_identity_correspondence"], "PASS"
        )
        self.assertFalse(result["durable_ecology_installed"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["integration_effect"], "NONE")
        self.assertEqual(result["representation_succession"], "NOT_TESTED")
        self.assertEqual(result["legacy_seat_migration"], "NOT_TESTED")
        self.assertEqual(
            result["historical_basis_reuse"], "EXPLICIT_RELATION_NOT_YET_MODELED"
        )


if __name__ == "__main__":
    unittest.main()
