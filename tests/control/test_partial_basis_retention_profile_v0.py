from __future__ import annotations

import copy
import unittest

from src.control.partial_basis_retention_profile_v0 import (
    PartialBasisRetentionProfileError,
    build_partial_basis_retention_profile,
    evaluate_basis_extension,
    validate_partial_basis_retention_profile,
)

G9_RESULT_BLOB = "94152a26078c527cabfef7cd2cf1e7e3b4990df1"
G9_WITNESS_BLOB = "212d7a9d4fb7bc982cb83b418ee6d5982008c574"


def build(basis_id, requirements):
    return build_partial_basis_retention_profile(
        source_g9_result_blob_sha=G9_RESULT_BLOB,
        source_g9_witness_blob_sha=G9_WITNESS_BLOB,
        basis_id=basis_id,
        horizon_requirements=requirements,
    )


class PartialBasisRetentionProfileV0Tests(unittest.TestCase):
    def test_b0_profile_is_exact(self):
        obj = build(
            "B0",
            {
                "H_A": "REQUIRED",
                "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            },
        )
        self.assertEqual(
            obj["retention_profile"],
            {
                "required_members": ["H_A"],
                "unresolved_members": [],
                "not_required_members": ["H_B"],
                "n_required": 1,
                "n_unresolved": 0,
                "n_not_required": 1,
                "basis_size": 2,
            },
        )
        self.assertEqual(
            obj["declared_scope_hot_requirement"], "REQUIRED"
        )

    def test_b1_extension_adds_unresolved_without_mutating_b0(self):
        b0 = build(
            "B0",
            {
                "H_A": "REQUIRED",
                "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            },
        )
        b1 = build(
            "B1",
            {
                "H_A": "REQUIRED",
                "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
                "H_C": "UNRESOLVED",
            },
        )
        ext = evaluate_basis_extension(b0, b1)
        self.assertEqual(
            ext["prior_local_coordinates_preserved"], "YES"
        )
        self.assertEqual(ext["new_horizons"], ["H_C"])
        self.assertEqual(
            b1["retention_profile"],
            {
                "required_members": ["H_A"],
                "unresolved_members": ["H_C"],
                "not_required_members": ["H_B"],
                "n_required": 1,
                "n_unresolved": 1,
                "n_not_required": 1,
                "basis_size": 3,
            },
        )

    def test_exterior_remains_unresolved(self):
        obj = build("B0", {"H_A": "REQUIRED"})
        self.assertEqual(obj["exterior_posture"], "UNRESOLVED")
        self.assertEqual(
            obj["global_ecology_hot_requirement"], "UNRESOLVED"
        )

    def test_profile_counts_do_not_create_scalar_load(self):
        obj = build("B0", {"H_A": "REQUIRED"})
        for forbidden in (
            "scalar_hotness",
            "load_weight",
            "utility",
            "economic_value",
        ):
            self.assertNotIn(forbidden, obj)

    def test_extension_detects_changed_prior_coordinate(self):
        b0 = build("B0", {"H_A": "REQUIRED"})
        b1 = build(
            "B1",
            {
                "H_A": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
                "H_B": "UNRESOLVED",
            },
        )
        ext = evaluate_basis_extension(b0, b1)
        self.assertEqual(
            ext["prior_local_coordinates_preserved"], "NO"
        )

    def test_no_transition_or_downstream_effects(self):
        obj = build("B0", {"H_A": "REQUIRED"})
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

    def test_fixed_inputs_are_deterministic(self):
        req = {
            "H_B": "UNRESOLVED",
            "H_A": "REQUIRED",
        }
        self.assertEqual(build("B0", req), build("B0", req))

    def test_validation_rejects_tampering(self):
        obj = build("B0", {"H_A": "REQUIRED"})
        tampered = copy.deepcopy(obj)
        tampered["exterior_posture"] = "EMPTY"
        with self.assertRaises(Exception):
            validate_partial_basis_retention_profile(tampered)

    def test_empty_basis_rejected(self):
        with self.assertRaisesRegex(
            PartialBasisRetentionProfileError, "non-empty"
        ):
            build("B0", {})


if __name__ == "__main__":
    unittest.main()
