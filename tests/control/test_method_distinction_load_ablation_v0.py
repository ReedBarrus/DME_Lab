from __future__ import annotations

import copy
import unittest

from src.control.method_distinction_load_ablation_v0 import (
    MethodDistinctionLoadError,
    build_method_distinction_load_ablation,
    validate_method_distinction_load_ablation,
)

G4_WITNESS_BLOB = "a49d948432c9560310133557ce6c8102ce4931ac"

CASES = {
    "WORLD_ONLY": {
        "world_axis": {"posture_change": "CHANGED"},
        "method_axis": {"cognitive_method_change": "UNCHANGED"},
    },
    "METHOD_ONLY": {
        "world_axis": {"posture_change": "UNCHANGED"},
        "method_axis": {"cognitive_method_change": "CHANGED"},
    },
    "BOTH": {
        "world_axis": {"posture_change": "CHANGED"},
        "method_axis": {"cognitive_method_change": "CHANGED"},
    },
    "NEITHER": {
        "world_axis": {"posture_change": "UNCHANGED"},
        "method_axis": {"cognitive_method_change": "UNCHANGED"},
    },
    "WORLD_UNRESOLVED": {
        "world_axis": {"posture_change": "UNRESOLVED"},
        "method_axis": {"cognitive_method_change": "UNCHANGED"},
    },
    "METHOD_UNRESOLVED": {
        "world_axis": {"posture_change": "UNCHANGED"},
        "method_axis": {"cognitive_method_change": "UNRESOLVED"},
    },
}


def build():
    return build_method_distinction_load_ablation(
        source_g4_observation_blob_sha=G4_WITNESS_BLOB,
        cases=CASES,
    )


class MethodDistinctionLoadAblationV0Tests(unittest.TestCase):
    def test_expected_collision_groups(self):
        obj = build()
        self.assertEqual(
            obj["collision_groups"]["CHANGED"],
            ["BOTH", "METHOD_ONLY", "WORLD_ONLY"],
        )
        self.assertEqual(obj["collision_groups"]["UNCHANGED"], ["NEITHER"])
        self.assertEqual(
            obj["collision_groups"]["UNRESOLVED"],
            ["METHOD_UNRESOLVED", "WORLD_UNRESOLVED"],
        )

    def test_discrimination_count_reduces(self):
        obj = build()
        self.assertEqual(obj["pre_ablation_distinct_signature_count"], 6)
        self.assertEqual(obj["post_ablation_distinct_signature_count"], 3)
        self.assertTrue(obj["semantic_discrimination_loss"])

    def test_only_semantic_load_is_claimed(self):
        obj = build()
        self.assertEqual(obj["load_profile"]["semantic"], "YES")
        for key in (
            "functional",
            "authority",
            "provenance",
            "temporal",
            "coordination",
        ):
            self.assertEqual(obj["load_profile"][key], "UNRESOLVED")

    def test_ablation_effect_does_not_create_live_load_status(self):
        obj = build()
        self.assertEqual(obj["current_load_bearing_status"], "UNRESOLVED")

    def test_no_retention_capitalization_or_consequence_effects(self):
        obj = build()
        for key in (
            "retention_effect",
            "method_capitalization_effect",
            "policy_mutation_effect",
            "gap_selection_effect",
            "work_justification_effect",
            "planning_effect",
            "authority_effect",
            "execution_effect",
            "scientific_standing_effect",
        ):
            self.assertEqual(obj[key], "NONE")

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(build(), build())

    def test_validation_rejects_tampering(self):
        obj = build()
        tampered = copy.deepcopy(obj)
        tampered["load_profile"]["authority"] = "YES"
        with self.assertRaises(Exception):
            validate_method_distinction_load_ablation(tampered)

    def test_invalid_blob_binding_rejected(self):
        with self.assertRaisesRegex(
            MethodDistinctionLoadError, "Git blob SHA"
        ):
            build_method_distinction_load_ablation(
                source_g4_observation_blob_sha="not-a-blob",
                cases=CASES,
            )


if __name__ == "__main__":
    unittest.main()
