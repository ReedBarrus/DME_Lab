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
    fresh_basis,
    observation_basis_ref,
    observation_source_ref,
    missingness_witness_ref,
    source_encounter_ref,
    missingness_witness_encounter_ref,
    basis_claim_status,
    current_epistemic_status,
    occupied_seat,
    rotate_invocation,
    rotate_occupant,
    run_pressure,
    validate_correspondence,
    validate_observation_basis,
    validate_observation_grounding,
    validate_missingness_grounding,
    validate_source_encounter_grounding,
    validate_missingness_witness_encounter_grounding,
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
        self.assertEqual(
            authority_standing(binding),
            "NO_AUTHORITY_REF_REPRESENTED",
        )

    def test_G_role_authority_leak_rejected(self):
        role = clean_role()
        role["authority_effect"] = "GRANT"
        with self.assertRaisesRegex(EcologyError, "ROLE_AUTHORITY_EFFECT_NOT_NONE"):
            validate_role(role)

    def test_H_unobserved_world_object_is_unknown(self):
        basis = clean_basis()
        self.assertEqual(basis_claim_status(basis, "WORLD_OBJECT_NOT_IN_BASIS"), "UNREPRESENTED_AT_BASIS")

    def test_I_explicit_missing_is_not_absent(self):
        basis = clean_basis()
        self.assertEqual(basis_claim_status(basis, "MISSING_OBJECT"), "MISSINGNESS_CLAIM_REPRESENTED")

    def test_J_later_world_change_does_not_rewrite_prior_basis(self):
        basis = clean_basis()
        before = basis_claim_status(basis, "LATER_WORLD_OBJECT")
        later_world = {"objects":["LATER_WORLD_OBJECT"]}
        after = basis_claim_status(basis, "LATER_WORLD_OBJECT")
        self.assertIn("LATER_WORLD_OBJECT", later_world["objects"])
        self.assertEqual((before, after), ("UNREPRESENTED_AT_BASIS", "UNREPRESENTED_AT_BASIS"))

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

    def test_N0_mutual_null_or_exact_same_work_claim_is_valid(self):
        null_bundle = clean_bundle()
        validate_correspondence(
            role=null_bundle["role"],
            seat=null_bundle["seat"],
            binding=null_bundle["binding"],
            basis=null_bundle["basis"],
            source_carriers=null_bundle["sources"],
            missingness_witnesses=null_bundle["missingness_witnesses"],
            source_encounters=null_bundle["source_encounters"],
            missingness_witness_encounters=null_bundle["missingness_witness_encounters"],
        )

        same_bundle = clean_bundle()
        same_bundle["seat"]["work_claim_ref"] = "claim://SAME-CURRENT-CLAIM"
        same_bundle["binding"]["work_claim_ref"] = "claim://SAME-CURRENT-CLAIM"
        validate_correspondence(
            role=same_bundle["role"],
            seat=same_bundle["seat"],
            binding=same_bundle["binding"],
            basis=same_bundle["basis"],
            source_carriers=same_bundle["sources"],
            missingness_witnesses=same_bundle["missingness_witnesses"],
            source_encounters=same_bundle["source_encounters"],
            missingness_witness_encounters=same_bundle["missingness_witness_encounters"],
        )

    def test_N1_work_claim_identity_mismatch_rejected(self):
        b = clean_bundle()
        b["seat"]["work_claim_ref"] = "claim://A"
        b["binding"]["work_claim_ref"] = "claim://B"
        with self.assertRaisesRegex(EcologyError, "SEAT_BINDING_WORK_CLAIM_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_N2_seat_claim_binding_absent_rejected(self):
        b = clean_bundle()
        b["seat"]["work_claim_ref"] = "claim://A"
        with self.assertRaisesRegex(EcologyError, "SEAT_BINDING_WORK_CLAIM_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_N3_seat_absent_binding_claim_rejected(self):
        b = clean_bundle()
        b["binding"]["work_claim_ref"] = "claim://A"
        with self.assertRaisesRegex(EcologyError, "SEAT_BINDING_WORK_CLAIM_MISMATCH"):
            validate_correspondence(
                role=b["role"], seat=b["seat"], binding=b["binding"], basis=b["basis"]
            )

    def test_P1_old_observed_payload_does_not_auto_propagate(self):
        old = clean_basis()
        old["observed_objects"] = [{
            "object_id":"POISON_SENTINEL",
            "identity":"sha256:" + ("b" * 64),
            "source_ref":"fixture://OLD_OBSERVATION/POISON_SENTINEL",
        }]
        old["explicit_missing_objects"] = []
        old["source_refs"] = [
            "fixture://OLD_OBSERVATION/POISON_SENTINEL"
        ]

        new_binding, new_basis = rotate_invocation(
            clean_binding(), old, "INVOCATION_P1"
        )

        self.assertEqual(basis_claim_status(new_basis, "POISON_SENTINEL"), "UNREPRESENTED_AT_BASIS")
        self.assertEqual(new_basis["observed_objects"], [])
        self.assertEqual(new_basis["explicit_missing_objects"], [])
        self.assertEqual(new_basis["source_refs"], [])
        self.assertNotEqual(new_binding["observation_basis_ref"], observation_basis_ref(old))

    def test_P2_old_missingness_does_not_auto_propagate(self):
        old = clean_basis()
        old["observed_objects"] = []
        old["explicit_missing_objects"] = [{
            "object_id":"MISSING_POISON_SENTINEL",
            "reason":"MISSING_FOR_PRIOR_INVOCATION",
            "witness_ref":"missingness-witness://PRIOR-P2@opaque:prior",
        }]
        old["source_refs"] = ["fixture://OLD_MISSINGNESS"]

        _, new_basis = rotate_invocation(
            clean_binding(), old, "INVOCATION_P2"
        )

        self.assertEqual(
            basis_claim_status(new_basis, "MISSING_POISON_SENTINEL"), "UNREPRESENTED_AT_BASIS"
        )
        self.assertEqual(new_basis["explicit_missing_objects"], [])
        self.assertEqual(new_basis["source_refs"], [])

    def test_P3_fresh_observation_can_reestablish_same_fact(self):
        old = clean_basis()
        old["observed_objects"] = [{
            "object_id":"POISON_SENTINEL",
            "identity":"sha256:" + ("b" * 64),
            "source_ref":"fixture://OLD_OBSERVATION/POISON_SENTINEL",
        }]
        old["explicit_missing_objects"] = []
        old["source_refs"] = [
            "fixture://OLD_OBSERVATION/POISON_SENTINEL"
        ]

        fresh_source = {
            "schema":"observation_source_v0",
            "source_id":"SOURCE_INVOCATION_P3_POISON_SENTINEL",
            "object_id":"POISON_SENTINEL",
            "identity":"sha256:" + ("c" * 64),
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        fresh_source_ref = observation_source_ref(fresh_source)
        fresh_observation = [{
            "object_id":"POISON_SENTINEL",
            "identity":"sha256:" + ("c" * 64),
            "source_ref":fresh_source_ref,
        }]
        new_binding, new_basis = rotate_invocation(
            clean_binding(),
            old,
            "INVOCATION_P3",
            observed_objects=fresh_observation,
            explicit_missing_objects=[],
            source_refs=[fresh_source_ref],
        )
        new_seat = occupied_seat(
            seat=clean_empty_seat(new_binding["seat_id"]),
            occupant_id=new_binding["occupant_id"],
            invocation_id=new_binding["invocation_id"],
        )
        encounter = {
            "schema":"source_encounter_v0",
            "encounter_id":"ENCOUNTER_INVOCATION_P3_POISON_SENTINEL",
            "seat_id":new_binding["seat_id"],
            "occupant_id":new_binding["occupant_id"],
            "invocation_id":new_binding["invocation_id"],
            "source_ref":fresh_source_ref,
            "encounter_kind":"PRESENTED_TO_INVOCATION",
            "basis_ref":new_basis["basis_ref"],
            "observation_basis_ref":observation_basis_ref(new_basis),
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        validate_correspondence(
            role=clean_role(),
            seat=new_seat,
            binding=new_binding,
            basis=new_basis,
            source_carriers=[fresh_source],
            source_encounters=[encounter],
        )
        self.assertEqual(
            basis_claim_status(new_basis, "POISON_SENTINEL"),
            "SOURCE_CLAIM_REPRESENTED",
        )
        self.assertEqual(
            current_epistemic_status(
                role=clean_role(),
                seat=new_seat,
                binding=new_binding,
                basis=new_basis,
                object_id="POISON_SENTINEL",
                source_carriers=[fresh_source],
                source_encounters=[encounter],
            ),
            "SOURCE_PRESENTED",
        )
        self.assertEqual(
            new_basis["source_refs"],
            [fresh_source_ref],
        )

    def test_P4_historical_basis_is_separate_from_current_observation(self):
        old = clean_basis()
        old["observed_objects"] = [{
            "object_id":"POISON_SENTINEL",
            "identity":"sha256:" + ("b" * 64),
            "source_ref":"fixture://OLD_OBSERVATION/POISON_SENTINEL",
        }]
        old["explicit_missing_objects"] = []
        old["source_refs"] = [
            "fixture://OLD_OBSERVATION/POISON_SENTINEL"
        ]

        historical_ref = observation_basis_ref(old)
        current_binding, current_basis = rotate_invocation(
            clean_binding(), old, "INVOCATION_P4"
        )
        current_ref = observation_basis_ref(current_basis)

        self.assertNotEqual(historical_ref, current_ref)
        self.assertEqual(current_binding["observation_basis_ref"], current_ref)
        self.assertEqual(
            basis_claim_status(current_basis, "POISON_SENTINEL"), "UNREPRESENTED_AT_BASIS"
        )

    def test_fresh_basis_requires_explicit_current_payload(self):
        old = clean_basis()
        new = fresh_basis(
            old,
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_EXPLICIT",
            basis_id="OBSERVATION_BASIS_TEST_001:FOR:INVOCATION_EXPLICIT",
        )
        self.assertEqual(new["observed_objects"], [])
        self.assertEqual(new["explicit_missing_objects"], [])
        self.assertEqual(new["source_refs"], [])

    def test_Q1_observed_object_without_basis_source_rejected(self):
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q1",
            basis_id="OBSERVATION_BASIS_Q1",
        )
        basis["observed_objects"] = [{
            "object_id":"MAGIC_OBJECT",
            "identity":"sha256:" + ("d" * 64),
            "source_ref":"source://TOTALLY-REAL-BRO",
        }]
        with self.assertRaisesRegex(
            EcologyError, "OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED"
        ):
            validate_observation_basis(basis)

    def test_Q2_observed_object_with_different_basis_source_rejected(self):
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q2",
            basis_id="OBSERVATION_BASIS_Q2",
            source_refs=["source://B"],
        )
        basis["observed_objects"] = [{
            "object_id":"MAGIC_OBJECT",
            "identity":"sha256:" + ("e" * 64),
            "source_ref":"source://A",
        }]
        with self.assertRaisesRegex(
            EcologyError, "OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED"
        ):
            validate_observation_basis(basis)

    def test_Q3A_source_object_mismatch_rejected(self):
        source = {
            "schema":"observation_source_v0",
            "source_id":"SOURCE_GARY_BATHMAT",
            "object_id":"GARY_FROM_ACCOUNTING",
            "identity":"opaque:GARY-BATHMAT-v1",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        ref = observation_source_ref(source)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q3A",
            basis_id="OBSERVATION_BASIS_Q3A",
            observed_objects=[{
                "object_id":"BIGFOOT",
                "identity":"opaque:GARY-BATHMAT-v1",
                "source_ref":ref,
            }],
            source_refs=[ref],
        )
        with self.assertRaisesRegex(
            EcologyError, "OBSERVED_OBJECT_SOURCE_OBJECT_MISMATCH"
        ):
            validate_observation_grounding(basis, [source])

    def test_Q3B_source_identity_mismatch_rejected(self):
        source = {
            "schema":"observation_source_v0",
            "source_id":"SOURCE_BIGFOOT_B",
            "object_id":"BIGFOOT",
            "identity":"opaque:IDENTITY-B",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        ref = observation_source_ref(source)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q3B",
            basis_id="OBSERVATION_BASIS_Q3B",
            observed_objects=[{
                "object_id":"BIGFOOT",
                "identity":"opaque:IDENTITY-A",
                "source_ref":ref,
            }],
            source_refs=[ref],
        )
        with self.assertRaisesRegex(
            EcologyError, "OBSERVED_OBJECT_SOURCE_IDENTITY_MISMATCH"
        ):
            validate_observation_grounding(basis, [source])

    def test_Q3C_exact_source_object_identity_correspondence_valid(self):
        source = {
            "schema":"observation_source_v0",
            "source_id":"SOURCE_BIGFOOT_C",
            "object_id":"BIGFOOT",
            "identity":"opaque:IDENTITY-A",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        ref = observation_source_ref(source)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q3C",
            basis_id="OBSERVATION_BASIS_Q3C",
            observed_objects=[{
                "object_id":"BIGFOOT",
                "identity":"opaque:IDENTITY-A",
                "source_ref":ref,
            }],
            source_refs=[ref],
        )
        validate_observation_grounding(basis, [source])

    def test_Q4A_missingness_without_supplied_witness_rejected(self):
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q4A",
            basis_id="OBSERVATION_BASIS_Q4A",
            explicit_missing_objects=[{
                "object_id":"SECRET_DRAGON_LEDGER",
                "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
                "witness_ref":"missingness-witness://UNSUPPLIED@opaque:missing",
            }],
        )
        with self.assertRaisesRegex(EcologyError, "MISSINGNESS_WITNESS_NOT_SUPPLIED"):
            validate_missingness_grounding(basis, [])

    def test_Q4B_missingness_witness_wrong_object_rejected(self):
        witness = {
            "schema":"missingness_witness_v0",
            "witness_id":"WITNESS_Q4B",
            "object_id":"OTHER_OBJECT",
            "standing":"UNAVAILABLE_AT_BASIS",
            "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        ref = missingness_witness_ref(witness)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q4B",
            basis_id="OBSERVATION_BASIS_Q4B",
            explicit_missing_objects=[{
                "object_id":"SECRET_DRAGON_LEDGER",
                "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
                "witness_ref":ref,
            }],
        )
        with self.assertRaisesRegex(EcologyError, "MISSINGNESS_WITNESS_OBJECT_MISMATCH"):
            validate_missingness_grounding(basis, [witness])

    def test_Q4C_exact_missingness_correspondence_valid(self):
        witness = {
            "schema":"missingness_witness_v0",
            "witness_id":"WITNESS_Q4C",
            "object_id":"SECRET_DRAGON_LEDGER",
            "standing":"UNAVAILABLE_AT_BASIS",
            "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        ref = missingness_witness_ref(witness)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q4C",
            basis_id="OBSERVATION_BASIS_Q4C",
            explicit_missing_objects=[{
                "object_id":"SECRET_DRAGON_LEDGER",
                "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
                "witness_ref":ref,
            }],
        )
        validate_missingness_grounding(basis, [witness])
        self.assertEqual(basis_claim_status(basis, "SECRET_DRAGON_LEDGER"), "MISSINGNESS_CLAIM_REPRESENTED")

    def test_Q4D_missingness_reason_mismatch_rejected(self):
        witness = {
            "schema":"missingness_witness_v0",
            "witness_id":"WITNESS_Q4D",
            "object_id":"SECRET_DRAGON_LEDGER",
            "standing":"UNAVAILABLE_AT_BASIS",
            "reason":"NETWORK_TIMEOUT",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        ref = missingness_witness_ref(witness)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_Q4D",
            basis_id="OBSERVATION_BASIS_Q4D",
            explicit_missing_objects=[{
                "object_id":"SECRET_DRAGON_LEDGER",
                "reason":"PERMISSION_DENIED",
                "witness_ref":ref,
            }],
        )
        with self.assertRaisesRegex(EcologyError, "MISSINGNESS_WITNESS_REASON_MISMATCH"):
            validate_missingness_grounding(basis, [witness])

    def _q5_bundle(self):
        source = {
            "schema":"observation_source_v0",
            "source_id":"SOURCE_BIGFOOT_R",
            "object_id":"BIGFOOT",
            "identity":"opaque:IDENTITY-R",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        source_ref = observation_source_ref(source)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_R",
            basis_id="OBSERVATION_BASIS_R",
            observed_objects=[{
                "object_id":"BIGFOOT",
                "identity":"opaque:IDENTITY-R",
                "source_ref":source_ref,
            }],
            source_refs=[source_ref],
        )
        binding = clean_binding()
        binding["binding_id"] = "BINDING:SCIENCE_TEST_01:LABOIB_CANDIDATE:INVOCATION_R"
        binding["invocation_id"] = "INVOCATION_R"
        binding["observation_basis_ref"] = observation_basis_ref(basis)
        seat = occupied_seat(
            seat=clean_empty_seat("SCIENCE_TEST_01"),
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_R",
        )
        encounter = {
            "schema":"source_encounter_v0",
            "encounter_id":"ENCOUNTER_R4",
            "seat_id":binding["seat_id"],
            "occupant_id":binding["occupant_id"],
            "invocation_id":binding["invocation_id"],
            "source_ref":source_ref,
            "encounter_kind":"PRESENTED_TO_INVOCATION",
            "basis_ref":basis["basis_ref"],
            "observation_basis_ref":observation_basis_ref(basis),
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        return source, basis, binding, seat, encounter

    def test_R1_source_without_current_encounter_rejected(self):
        source, basis, binding, seat, _ = self._q5_bundle()
        with self.assertRaisesRegex(EcologyError, "CURRENT_SOURCE_ENCOUNTER_NOT_SUPPLIED"):
            validate_correspondence(
                role=clean_role(),
                seat=seat,
                binding=binding,
                basis=basis,
                source_carriers=[source],
                source_encounters=[],
            )

    def test_R2_encounter_wrong_invocation_rejected(self):
        _, basis, binding, _, encounter = self._q5_bundle()
        encounter["invocation_id"] = "INVOCATION_OTHER"
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_INVOCATION_MISMATCH"):
            validate_source_encounter_grounding(
                basis=basis, binding=binding, source_encounters=[encounter]
            )

    def test_R3_encounter_wrong_source_rejected(self):
        _, basis, binding, _, encounter = self._q5_bundle()
        encounter["source_ref"] = "observation-source://OTHER@opaque:other"
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_SOURCE_MISMATCH"):
            validate_source_encounter_grounding(
                basis=basis, binding=binding, source_encounters=[encounter]
            )

    def test_R4_exact_current_source_encounter_valid(self):
        source, basis, binding, seat, encounter = self._q5_bundle()
        validate_correspondence(
            role=clean_role(),
            seat=seat,
            binding=binding,
            basis=basis,
            source_carriers=[source],
            source_encounters=[encounter],
        )
        self.assertTrue(source_encounter_ref(encounter).startswith("source-encounter://"))

    def test_R5_encounter_wrong_seat_rejected(self):
        _, basis, binding, _, encounter = self._q5_bundle()
        encounter["seat_id"] = "SCIENCE_TEST_02"
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_SEAT_MISMATCH"):
            validate_source_encounter_grounding(
                basis=basis, binding=binding, source_encounters=[encounter]
            )

    def test_R6_encounter_wrong_occupant_rejected(self):
        _, basis, binding, _, encounter = self._q5_bundle()
        encounter["occupant_id"] = "OCCUPANT_OTHER"
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_OCCUPANT_MISMATCH"):
            validate_source_encounter_grounding(
                basis=basis, binding=binding, source_encounters=[encounter]
            )

    def test_R7_encounter_wrong_basis_rejected(self):
        _, basis, binding, _, encounter = self._q5_bundle()
        encounter["basis_ref"] = "fixture://OTHER_BASIS"
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_BASIS_MISMATCH"):
            validate_source_encounter_grounding(
                basis=basis, binding=binding, source_encounters=[encounter]
            )

    def _q6_bundle(self):
        witness = {
            "schema":"missingness_witness_v0",
            "witness_id":"WITNESS_MOTHMAN_S",
            "object_id":"MOTHMAN_FILES",
            "standing":"UNAVAILABLE_AT_BASIS",
            "reason":"PERMISSION_DENIED",
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        witness_ref = missingness_witness_ref(witness)
        basis = fresh_basis(
            clean_basis(),
            seat_id="SCIENCE_TEST_01",
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_S",
            basis_id="OBSERVATION_BASIS_S",
            explicit_missing_objects=[{
                "object_id":"MOTHMAN_FILES",
                "reason":"PERMISSION_DENIED",
                "witness_ref":witness_ref,
            }],
        )
        binding = clean_binding()
        binding["binding_id"] = "BINDING:SCIENCE_TEST_01:LABOIB_CANDIDATE:INVOCATION_S"
        binding["invocation_id"] = "INVOCATION_S"
        binding["observation_basis_ref"] = observation_basis_ref(basis)
        seat = occupied_seat(
            seat=clean_empty_seat("SCIENCE_TEST_01"),
            occupant_id="LABOIB_CANDIDATE",
            invocation_id="INVOCATION_S",
        )
        encounter = {
            "schema":"missingness_witness_encounter_v0",
            "encounter_id":"MISSINGNESS_ENCOUNTER_S4",
            "seat_id":binding["seat_id"],
            "occupant_id":binding["occupant_id"],
            "invocation_id":binding["invocation_id"],
            "witness_ref":witness_ref,
            "encounter_kind":"PRESENTED_TO_INVOCATION",
            "basis_ref":basis["basis_ref"],
            "observation_basis_ref":observation_basis_ref(basis),
            "authority_effect":"NONE",
            "execution_effect":"NONE",
        }
        return witness, basis, binding, seat, encounter

    def test_S1_witness_without_current_encounter_rejected(self):
        witness, basis, binding, seat, _ = self._q6_bundle()
        with self.assertRaisesRegex(
            EcologyError, "CURRENT_MISSINGNESS_WITNESS_ENCOUNTER_NOT_SUPPLIED"
        ):
            validate_correspondence(
                role=clean_role(),
                seat=seat,
                binding=binding,
                basis=basis,
                missingness_witnesses=[witness],
                missingness_witness_encounters=[],
            )

    def test_S2_missingness_encounter_wrong_invocation_rejected(self):
        _, basis, binding, _, encounter = self._q6_bundle()
        encounter["invocation_id"] = "INVOCATION_OTHER"
        with self.assertRaisesRegex(
            EcologyError, "MISSINGNESS_WITNESS_ENCOUNTER_INVOCATION_MISMATCH"
        ):
            validate_missingness_witness_encounter_grounding(
                basis=basis,
                binding=binding,
                missingness_witness_encounters=[encounter],
            )

    def test_S3_missingness_encounter_wrong_witness_rejected(self):
        _, basis, binding, _, encounter = self._q6_bundle()
        encounter["witness_ref"] = "missingness-witness://OTHER@opaque:other"
        with self.assertRaisesRegex(
            EcologyError, "MISSINGNESS_WITNESS_ENCOUNTER_WITNESS_MISMATCH"
        ):
            validate_missingness_witness_encounter_grounding(
                basis=basis,
                binding=binding,
                missingness_witness_encounters=[encounter],
            )

    def test_S4_exact_current_missingness_witness_encounter_valid(self):
        witness, basis, binding, seat, encounter = self._q6_bundle()
        validate_correspondence(
            role=clean_role(),
            seat=seat,
            binding=binding,
            basis=basis,
            missingness_witnesses=[witness],
            missingness_witness_encounters=[encounter],
        )
        self.assertTrue(
            missingness_witness_encounter_ref(encounter).startswith(
                "missingness-witness-encounter://"
            )
        )

    def test_S5_missingness_encounter_wrong_seat_rejected(self):
        _, basis, binding, _, encounter = self._q6_bundle()
        encounter["seat_id"] = "SCIENCE_TEST_02"
        with self.assertRaisesRegex(
            EcologyError, "MISSINGNESS_WITNESS_ENCOUNTER_SEAT_MISMATCH"
        ):
            validate_missingness_witness_encounter_grounding(
                basis=basis,
                binding=binding,
                missingness_witness_encounters=[encounter],
            )

    def test_S6_missingness_encounter_wrong_occupant_rejected(self):
        _, basis, binding, _, encounter = self._q6_bundle()
        encounter["occupant_id"] = "OCCUPANT_OTHER"
        with self.assertRaisesRegex(
            EcologyError, "MISSINGNESS_WITNESS_ENCOUNTER_OCCUPANT_MISMATCH"
        ):
            validate_missingness_witness_encounter_grounding(
                basis=basis,
                binding=binding,
                missingness_witness_encounters=[encounter],
            )

    def test_S7_missingness_encounter_wrong_basis_rejected(self):
        _, basis, binding, _, encounter = self._q6_bundle()
        encounter["basis_ref"] = "fixture://OTHER_BASIS"
        with self.assertRaisesRegex(
            EcologyError, "MISSINGNESS_WITNESS_ENCOUNTER_BASIS_MISMATCH"
        ):
            validate_missingness_witness_encounter_grounding(
                basis=basis,
                binding=binding,
                missingness_witness_encounters=[encounter],
            )

    def test_T1_basis_row_is_only_source_claim_represented(self):
        bundle = clean_bundle()
        self.assertEqual(
            basis_claim_status(bundle["basis"], "OBSERVED_OBJECT"),
            "SOURCE_CLAIM_REPRESENTED",
        )

    def test_T2_full_current_chain_earns_source_presented(self):
        bundle = clean_bundle()
        self.assertEqual(
            current_epistemic_status(
                role=bundle["role"],
                seat=bundle["seat"],
                binding=bundle["binding"],
                basis=bundle["basis"],
                object_id="OBSERVED_OBJECT",
                source_carriers=bundle["sources"],
                missingness_witnesses=bundle["missingness_witnesses"],
                source_encounters=bundle["source_encounters"],
                missingness_witness_encounters=bundle[
                    "missingness_witness_encounters"
                ],
            ),
            "SOURCE_PRESENTED",
        )

    def test_T3_current_apparatus_does_not_emit_observed_standing(self):
        bundle = clean_bundle()
        basis_status = basis_claim_status(bundle["basis"], "OBSERVED_OBJECT")
        current_status = current_epistemic_status(
            role=bundle["role"],
            seat=bundle["seat"],
            binding=bundle["binding"],
            basis=bundle["basis"],
            object_id="OBSERVED_OBJECT",
            source_carriers=bundle["sources"],
            missingness_witnesses=bundle["missingness_witnesses"],
            source_encounters=bundle["source_encounters"],
            missingness_witness_encounters=bundle[
                "missingness_witness_encounters"
            ],
        )
        self.assertNotEqual(basis_status, "OBSERVED")
        self.assertNotEqual(current_status, "OBSERVED")

    def test_U1_basis_missingness_row_is_only_claim_represented(self):
        bundle = clean_bundle()
        self.assertEqual(
            basis_claim_status(bundle["basis"], "MISSING_OBJECT"),
            "MISSINGNESS_CLAIM_REPRESENTED",
        )

    def test_U2_full_current_missingness_chain_earns_witness_presented(self):
        bundle = clean_bundle()
        self.assertEqual(
            current_epistemic_status(
                role=bundle["role"],
                seat=bundle["seat"],
                binding=bundle["binding"],
                basis=bundle["basis"],
                object_id="MISSING_OBJECT",
                source_carriers=bundle["sources"],
                missingness_witnesses=bundle["missingness_witnesses"],
                source_encounters=bundle["source_encounters"],
                missingness_witness_encounters=bundle[
                    "missingness_witness_encounters"
                ],
            ),
            "MISSINGNESS_WITNESS_PRESENTED",
        )

    def test_U3_current_apparatus_does_not_emit_missing_standing(self):
        bundle = clean_bundle()
        basis_status = basis_claim_status(bundle["basis"], "MISSING_OBJECT")
        current_status = current_epistemic_status(
            role=bundle["role"],
            seat=bundle["seat"],
            binding=bundle["binding"],
            basis=bundle["basis"],
            object_id="MISSING_OBJECT",
            source_carriers=bundle["sources"],
            missingness_witnesses=bundle["missingness_witnesses"],
            source_encounters=bundle["source_encounters"],
            missingness_witness_encounters=bundle[
                "missingness_witness_encounters"
            ],
        )
        self.assertNotEqual(basis_status, "MISSING")
        self.assertNotEqual(current_status, "MISSING")

    def test_V1_basis_silence_is_unrepresented_not_unknown(self):
        bundle = clean_bundle()
        self.assertEqual(
            basis_claim_status(bundle["basis"], "PROJECT_X"),
            "UNREPRESENTED_AT_BASIS",
        )

    def test_V2_validated_bundle_silence_is_no_current_represented_claim(self):
        bundle = clean_bundle()
        self.assertEqual(
            current_epistemic_status(
                role=bundle["role"],
                seat=bundle["seat"],
                binding=bundle["binding"],
                basis=bundle["basis"],
                object_id="PROJECT_X",
                source_carriers=bundle["sources"],
                missingness_witnesses=bundle["missingness_witnesses"],
                source_encounters=bundle["source_encounters"],
                missingness_witness_encounters=bundle[
                    "missingness_witness_encounters"
                ],
            ),
            "NO_CURRENT_REPRESENTED_CLAIM",
        )

    def test_V3_basis_silence_does_not_emit_negative_epistemic_fact(self):
        bundle = clean_bundle()
        basis_status = basis_claim_status(bundle["basis"], "PROJECT_X")
        current_status = current_epistemic_status(
            role=bundle["role"],
            seat=bundle["seat"],
            binding=bundle["binding"],
            basis=bundle["basis"],
            object_id="PROJECT_X",
            source_carriers=bundle["sources"],
            missingness_witnesses=bundle["missingness_witnesses"],
            source_encounters=bundle["source_encounters"],
            missingness_witness_encounters=bundle[
                "missingness_witness_encounters"
            ],
        )
        forbidden = {"UNKNOWN", "ABSENT", "MISSING", "FALSE", "UNAVAILABLE"}
        self.assertNotIn(basis_status, forbidden)
        self.assertNotIn(current_status, forbidden)

    def test_W1_source_encounter_same_label_different_basis_bytes_rejected(self):
        source, basis_a, binding_a, seat, encounter = self._q5_bundle()
        basis_b = copy.deepcopy(basis_a)
        basis_b["basis_id"] = "OBSERVATION_BASIS_R_MUTATED"
        self.assertEqual(basis_a["basis_ref"], basis_b["basis_ref"])
        self.assertNotEqual(
            observation_basis_ref(basis_a),
            observation_basis_ref(basis_b),
        )
        binding_b = copy.deepcopy(binding_a)
        binding_b["observation_basis_ref"] = observation_basis_ref(basis_b)
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_EXACT_BASIS_MISMATCH"):
            validate_correspondence(
                role=clean_role(),
                seat=seat,
                binding=binding_b,
                basis=basis_b,
                source_carriers=[source],
                source_encounters=[encounter],
            )

    def test_W2_missingness_encounter_same_label_different_basis_bytes_rejected(self):
        witness, basis_a, binding_a, seat, encounter = self._q6_bundle()
        basis_b = copy.deepcopy(basis_a)
        basis_b["basis_id"] = "OBSERVATION_BASIS_S_MUTATED"
        self.assertEqual(basis_a["basis_ref"], basis_b["basis_ref"])
        self.assertNotEqual(
            observation_basis_ref(basis_a),
            observation_basis_ref(basis_b),
        )
        binding_b = copy.deepcopy(binding_a)
        binding_b["observation_basis_ref"] = observation_basis_ref(basis_b)
        with self.assertRaisesRegex(
            EcologyError, "MISSINGNESS_WITNESS_ENCOUNTER_EXACT_BASIS_MISMATCH"
        ):
            validate_correspondence(
                role=clean_role(),
                seat=seat,
                binding=binding_b,
                basis=basis_b,
                missingness_witnesses=[witness],
                missingness_witness_encounters=[encounter],
            )

    def test_W3_encounter_exact_current_basis_identity_valid(self):
        source, basis_a, binding_a, seat, encounter = self._q5_bundle()
        basis_b = copy.deepcopy(basis_a)
        basis_b["basis_id"] = "OBSERVATION_BASIS_R_CURRENT"
        binding_b = copy.deepcopy(binding_a)
        binding_b["observation_basis_ref"] = observation_basis_ref(basis_b)
        encounter["observation_basis_ref"] = observation_basis_ref(basis_b)
        validate_correspondence(
            role=clean_role(),
            seat=seat,
            binding=binding_b,
            basis=basis_b,
            source_carriers=[source],
            source_encounters=[encounter],
        )

    def test_W4_basis_byte_mutation_invalidates_prior_encounter(self):
        source, basis, binding, seat, encounter = self._q5_bundle()
        exact_before = observation_basis_ref(basis)
        basis["source_refs"] = list(basis["source_refs"]) + ["fixture://Q10/EXTRA"]
        binding["observation_basis_ref"] = observation_basis_ref(basis)
        self.assertNotEqual(exact_before, binding["observation_basis_ref"])
        with self.assertRaisesRegex(EcologyError, "SOURCE_ENCOUNTER_EXACT_BASIS_MISMATCH"):
            validate_correspondence(
                role=clean_role(),
                seat=seat,
                binding=binding,
                basis=basis,
                source_carriers=[source],
                source_encounters=[encounter],
            )

    def test_X1_empty_authority_refs_are_not_absent(self):
        binding = clean_binding()
        binding["authority_refs"] = []
        self.assertEqual(
            authority_standing(binding),
            "NO_AUTHORITY_REF_REPRESENTED",
        )
        self.assertNotEqual(authority_standing(binding), "ABSENT")

    def test_X2_unqualified_authority_ref_remains_unadjudicated(self):
        binding = clean_binding()
        binding["authority_refs"] = ["authority://Q11-UNQUALIFIED"]
        self.assertEqual(authority_standing(binding), "UNADJUDICATED")
        self.assertNotEqual(authority_standing(binding), "AUTHORIZED")

    def test_X3_authority_ref_silence_does_not_emit_negative_authority_fact(self):
        binding = clean_binding()
        binding["authority_refs"] = []
        status = authority_standing(binding)
        self.assertNotIn(
            status,
            {"ABSENT", "DENIED", "UNAUTHORIZED", "REVOKED", "INVALID"},
        )

    def test_X4_work_claim_without_authority_ref_preserves_distinction(self):
        binding = clean_binding()
        binding["work_claim_ref"] = "claim://Q11-CANDIDATE"
        binding["authority_refs"] = []
        validate_binding(binding)
        self.assertEqual(binding["work_claim_ref"], "claim://Q11-CANDIDATE")
        self.assertEqual(
            authority_standing(binding),
            "NO_AUTHORITY_REF_REPRESENTED",
        )
        self.assertEqual(binding["authority_effect"], "NONE")

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
        self.assertEqual(
            result["core_relations"]["seat_binding_work_claim_correspondence"], "PASS"
        )
        self.assertEqual(
            result["core_relations"]["fresh_observation_payload_noninheritance"], "PASS"
        )
        self.assertEqual(
            result["core_relations"]["fresh_observation_source_relation"], "PASS"
        )
        self.assertEqual(
            result["core_relations"]["observation_source_object_identity_correspondence"],
            "PASS",
        )
        self.assertEqual(
            result["core_relations"]["explicit_missingness_grounding"], "PASS"
        )
        self.assertEqual(
            result["core_relations"]["current_invocation_source_encounter"], "PASS"
        )
        self.assertEqual(
            result["core_relations"]["current_invocation_missingness_witness_encounter"],
            "PASS",
        )
        self.assertEqual(
            result["core_relations"]["observed_status_semantic_ceiling"],
            "PASS",
        )
        self.assertEqual(
            result["core_relations"]["missing_status_semantic_ceiling"],
            "PASS",
        )
        self.assertEqual(
            result["core_relations"]["unknown_status_semantic_ceiling"],
            "PASS",
        )
        self.assertEqual(
            result["core_relations"]["encounter_exact_current_basis_identity"],
            "PASS",
        )
        self.assertEqual(
            result["core_relations"]["authority_absence_semantic_ceiling"],
            "PASS",
        )
        self.assertFalse(result["durable_ecology_installed"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["integration_effect"], "NONE")
        self.assertEqual(result["representation_succession"], "NOT_TESTED")
        self.assertEqual(result["legacy_seat_migration"], "NOT_TESTED")
        self.assertEqual(
            result["historical_basis_reuse"], "SEPARATE_TYPED_RELATION_REQUIRED_NOT_MODELED"
        )
        self.assertEqual(
            result["observation_source_identity_correspondence"],
            "TESTED_EXACT_OPAQUE_CORRESPONDENCE",
        )
        self.assertEqual(
            result["observation_identity_scheme_semantics"], "NOT_TESTED"
        )
        self.assertEqual(result["observation_source_truth"], "NOT_TESTED")
        self.assertEqual(
            result["missingness_witness_correspondence"],
            "TESTED_EXACT_OBJECT_REASON",
        )
        self.assertEqual(result["missingness_witness_truth"], "NOT_TESTED")
        self.assertEqual(result["universal_unavailability"], "NOT_CLAIMED")
        self.assertEqual(
            result["source_encounter_correspondence"],
            "TESTED_CURRENT_SEAT_OCCUPANT_INVOCATION_SOURCE_BASIS",
        )
        self.assertEqual(result["source_encounter_truth"], "NOT_TESTED")
        self.assertEqual(result["direct_object_perception"], "NOT_CLAIMED")
        self.assertEqual(result["source_understanding"], "NOT_CLAIMED")
        self.assertEqual(
            result["missingness_witness_encounter_correspondence"],
            "TESTED_CURRENT_SEAT_OCCUPANT_INVOCATION_WITNESS_BASIS",
        )
        self.assertEqual(
            result["missingness_witness_encounter_truth"], "NOT_TESTED"
        )
        self.assertEqual(
            result["missingness_reason_understanding"], "NOT_CLAIMED"
        )
        self.assertEqual(result["presented_source_standing"], "SOURCE_PRESENTED")
        self.assertEqual(
            result["direct_observation_standing"], "NOT_ESTABLISHED"
        )
        self.assertEqual(
            result["source_inspection_or_consumption"], "NOT_ESTABLISHED"
        )
        self.assertEqual(
            result["presented_missingness_standing"],
            "MISSINGNESS_WITNESS_PRESENTED",
        )
        self.assertEqual(result["missing_standing"], "NOT_ESTABLISHED")
        self.assertEqual(
            result["retrieval_attempt_or_failure"], "NOT_ESTABLISHED"
        )
        self.assertEqual(
            result["silent_basis_standing"], "UNREPRESENTED_AT_BASIS"
        )
        self.assertEqual(
            result["silent_current_standing"], "NO_CURRENT_REPRESENTED_CLAIM"
        )
        self.assertEqual(result["unknown_standing"], "NOT_ESTABLISHED")
        self.assertEqual(result["basis_exhaustiveness"], "NOT_ESTABLISHED")
        self.assertEqual(
            result["encounter_basis_identity"],
            "EXACT_OBSERVATION_BASIS_CONTENT_IDENTITY",
        )
        self.assertEqual(
            result["friendly_basis_ref_identity_sufficient"], "NO"
        )
        self.assertEqual(
            result["empty_authority_ref_standing"],
            "NO_AUTHORITY_REF_REPRESENTED",
        )
        self.assertEqual(
            result["represented_authority_ref_standing"], "UNADJUDICATED"
        )
        self.assertEqual(
            result["authority_absence_standing"], "NOT_ESTABLISHED"
        )
        self.assertEqual(
            result["authority_denial_standing"], "NOT_ESTABLISHED"
        )


if __name__ == "__main__":
    unittest.main()
