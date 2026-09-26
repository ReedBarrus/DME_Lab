from __future__ import annotations

import copy
import unittest

from src.control.distinction_retention_mode_v0 import (
    DistinctionRetentionModeError,
    build_distinction_retention_mode,
    reconstruct_horizon_applicability,
    validate_distinction_retention_mode,
)

HANDLES = {
    "g4_result": "7a876e3e23b5a7f7d73f8ec86b393137da8f5ede",
    "g4_witness": "a49d948432c9560310133557ce6c8102ce4931ac",
    "g5_result": "d738dd57ae7866bdf584509b553a6b061cd714d7",
    "g5_witness": "a334412ac95fd66a228dba49fb888ffc225a6e7f",
    "g6_result": "bacc6f48a2c7c9a4658758cf663822b3b934557c",
    "g6_witness": "3e9c7b24cacbf608d87d2f14175e265267cc0ef1",
}

CASES = {
    "WORLD_ONLY": ("UNCHANGED", "NOT_APPLICABLE"),
    "METHOD_ONLY": ("CHANGED", "APPLICABLE"),
    "BOTH": ("CHANGED", "APPLICABLE"),
    "NEITHER": ("UNCHANGED", "NOT_APPLICABLE"),
    "WORLD_UNRESOLVED": ("UNCHANGED", "NOT_APPLICABLE"),
    "METHOD_UNRESOLVED": ("UNRESOLVED", "UNRESOLVED"),
}


def build():
    return build_distinction_retention_mode(exact_source_handles=HANDLES)


class DistinctionRetentionModeV0Tests(unittest.TestCase):
    def test_minimal_carrier_reconstructs_exact_horizon_outcomes(self):
        carrier = build()
        for _, (method_posture, expected) in CASES.items():
            self.assertEqual(
                reconstruct_horizon_applicability(carrier, method_posture),
                expected,
            )

    def test_richer_case_tables_are_not_inline(self):
        carrier = build()
        for forbidden in (
            "pre_ablation_cases",
            "collision_groups",
            "pre_ablation_applicability",
            "post_ablation_generic_applicability",
        ):
            self.assertNotIn(forbidden, carrier)

    def test_retention_split_is_explicit(self):
        carrier = build()
        self.assertEqual(
            carrier["distinction_retention_required_for_declared_horizon"],
            "YES",
        )
        self.assertEqual(
            carrier["full_g4_g5_g6_inline_hot_required"], "NO"
        )
        self.assertEqual(carrier["minimal_hot_carrier_candidate"], "YES")
        self.assertEqual(
            carrier["exact_cold_source_retention_required"], "YES"
        )

    def test_no_deletion_capitalization_or_execution_effect(self):
        carrier = build()
        for key in (
            "raw_source_deletion_effect",
            "method_capitalization_effect",
            "policy_mutation_effect",
            "planning_effect",
            "authority_effect",
            "execution_effect",
            "scientific_standing_effect",
        ):
            self.assertEqual(carrier[key], "NONE")

    def test_exact_source_handles_are_retained(self):
        self.assertEqual(build()["exact_source_handles"], HANDLES)

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(build(), build())

    def test_validation_rejects_tampering(self):
        carrier = build()
        tampered = copy.deepcopy(carrier)
        tampered["full_g4_g5_g6_inline_hot_required"] = "YES"
        with self.assertRaises(Exception):
            validate_distinction_retention_mode(tampered)

    def test_source_handle_set_must_be_exact(self):
        bad = dict(HANDLES)
        bad.pop("g6_witness")
        with self.assertRaisesRegex(
            DistinctionRetentionModeError, "source handle set mismatch"
        ):
            build_distinction_retention_mode(exact_source_handles=bad)


if __name__ == "__main__":
    unittest.main()
