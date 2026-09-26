from __future__ import annotations

import copy
import unittest

from src.control.partial_basis_residual_conservation_v0 import (
    PartialBasisResidualConservationError,
    build_partial_basis_residual_conservation,
    validate_partial_basis_residual_conservation,
)

G10_RESULT_BLOB = "e0c27dd06b68ac7e3dc08d20093e60eee35509eb"
G10_WITNESS_BLOB = "4f4c7efef184c1f60ab362420d7ef09a1c43dab1"
PROFILE_ID = (
    "partial-basis-retention-profile:sha256:"
    "1727532fd69214120cddfbb46b2a9f7dc1f2a3c5078f62f33aec28abd277d5b3"
)
EXTENSION_ID = (
    "partial-basis-retention-profile-extension:sha256:"
    "00abe68d1546d608becb9289ba21070876e02cfe0ba016acefd2107bc6d242d2"
)


def build():
    return build_partial_basis_residual_conservation(
        source_g10_result_blob_sha=G10_RESULT_BLOB,
        source_g10_witness_blob_sha=G10_WITNESS_BLOB,
        basis_id="B1",
        source_profile_id=PROFILE_ID,
        source_extension_id=EXTENSION_ID,
        interior_unresolved_members=["H_C"],
        nonresidual_members=["H_A", "H_B"],
        exterior_posture="UNRESOLVED",
    )


class PartialBasisResidualConservationV0Tests(unittest.TestCase):
    def test_exact_residual_is_conserved(self):
        obj = build()
        self.assertEqual(
            obj["interior_unresolved_members"], ["H_C"]
        )
        self.assertEqual(obj["exterior_posture"], "UNRESOLVED")
        self.assertEqual(obj["nonresidual_members"], ["H_A", "H_B"])
        self.assertEqual(obj["residual_conserved"], "YES")

    def test_residual_is_not_promoted_to_gap_or_work(self):
        obj = build()
        self.assertEqual(
            obj["residual_gap_status"], "NOT_ESTABLISHED"
        )
        self.assertEqual(
            obj["residual_work_eligibility"], "NOT_ESTABLISHED"
        )
        self.assertEqual(
            obj["architecture_requirement"], "NOT_ESTABLISHED"
        )

    def test_no_gap_discovery_selection_or_work_effects(self):
        obj = build()
        for key in (
            "gap_discovery_effect",
            "gap_selection_effect",
            "work_justification_effect",
            "work_materialization_effect",
        ):
            self.assertEqual(obj[key], "NONE")

    def test_no_downstream_consequence_effects(self):
        obj = build()
        for key in (
            "retention_transition_effect",
            "raw_source_deletion_effect",
            "method_capitalization_effect",
            "policy_mutation_effect",
            "planning_effect",
            "authority_effect",
            "execution_effect",
            "scientific_standing_effect",
        ):
            self.assertEqual(obj[key], "NONE")

    def test_source_identity_is_exact(self):
        obj = build()
        self.assertEqual(obj["source_profile_id"], PROFILE_ID)
        self.assertEqual(obj["source_extension_id"], EXTENSION_ID)
        self.assertEqual(
            obj["source_g10_result_blob_sha"], G10_RESULT_BLOB
        )
        self.assertEqual(
            obj["source_g10_witness_blob_sha"], G10_WITNESS_BLOB
        )

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(build(), build())

    def test_validation_rejects_tampering(self):
        obj = build()
        tampered = copy.deepcopy(obj)
        tampered["residual_work_eligibility"] = "YES"
        with self.assertRaises(Exception):
            validate_partial_basis_residual_conservation(tampered)

    def test_residual_and_nonresidual_must_not_overlap(self):
        with self.assertRaisesRegex(
            PartialBasisResidualConservationError, "must not overlap"
        ):
            build_partial_basis_residual_conservation(
                source_g10_result_blob_sha=G10_RESULT_BLOB,
                source_g10_witness_blob_sha=G10_WITNESS_BLOB,
                basis_id="B1",
                source_profile_id=PROFILE_ID,
                source_extension_id=EXTENSION_ID,
                interior_unresolved_members=["H_C"],
                nonresidual_members=["H_A", "H_C"],
                exterior_posture="UNRESOLVED",
            )

    def test_exterior_cannot_be_silently_closed(self):
        with self.assertRaisesRegex(
            PartialBasisResidualConservationError,
            "must remain UNRESOLVED",
        ):
            build_partial_basis_residual_conservation(
                source_g10_result_blob_sha=G10_RESULT_BLOB,
                source_g10_witness_blob_sha=G10_WITNESS_BLOB,
                basis_id="B1",
                source_profile_id=PROFILE_ID,
                source_extension_id=EXTENSION_ID,
                interior_unresolved_members=["H_C"],
                nonresidual_members=["H_A", "H_B"],
                exterior_posture="EMPTY",
            )


if __name__ == "__main__":
    unittest.main()
