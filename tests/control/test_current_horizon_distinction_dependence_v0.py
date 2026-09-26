from __future__ import annotations

import copy
import unittest

from src.control.current_horizon_distinction_dependence_v0 import (
    APPLICABLE,
    NOT_APPLICABLE,
    UNDERDETERMINED,
    UNRESOLVED,
    CurrentHorizonDistinctionDependenceError,
    build_current_horizon_distinction_dependence,
    validate_current_horizon_distinction_dependence,
)

G4_BLOB = "a49d948432c9560310133557ce6c8102ce4931ac"
G5_RESULT_BLOB = "d738dd57ae7866bdf584509b553a6b061cd714d7"

G4_CASES = {
    "WORLD_ONLY": {
        "method_axis": {"cognitive_method_change": "UNCHANGED"}
    },
    "METHOD_ONLY": {
        "method_axis": {"cognitive_method_change": "CHANGED"}
    },
    "BOTH": {
        "method_axis": {"cognitive_method_change": "CHANGED"}
    },
    "NEITHER": {
        "method_axis": {"cognitive_method_change": "UNCHANGED"}
    },
    "WORLD_UNRESOLVED": {
        "method_axis": {"cognitive_method_change": "UNCHANGED"}
    },
    "METHOD_UNRESOLVED": {
        "method_axis": {"cognitive_method_change": "UNRESOLVED"}
    },
}

G5_GROUPS = {
    "CHANGED": ["BOTH", "METHOD_ONLY", "WORLD_ONLY"],
    "UNCHANGED": ["NEITHER"],
    "UNRESOLVED": ["METHOD_UNRESOLVED", "WORLD_UNRESOLVED"],
}


def build():
    return build_current_horizon_distinction_dependence(
        source_g4_observation_blob_sha=G4_BLOB,
        source_g5_result_blob_sha=G5_RESULT_BLOB,
        g4_cases=G4_CASES,
        g5_collision_groups=G5_GROUPS,
    )


class CurrentHorizonDistinctionDependenceV0Tests(unittest.TestCase):
    def test_pre_ablation_horizon_applicability_is_exact(self):
        obj = build()
        expected = {
            "WORLD_ONLY": NOT_APPLICABLE,
            "METHOD_ONLY": APPLICABLE,
            "BOTH": APPLICABLE,
            "NEITHER": NOT_APPLICABLE,
            "WORLD_UNRESOLVED": NOT_APPLICABLE,
            "METHOD_UNRESOLVED": UNRESOLVED,
        }
        self.assertEqual(obj["pre_ablation_applicability"], expected)

    def test_ablated_changed_bucket_is_underdetermined(self):
        obj = build()
        self.assertEqual(
            obj["post_ablation_generic_applicability"]["CHANGED"],
            UNDERDETERMINED,
        )

    def test_ablated_unchanged_bucket_remains_determinate(self):
        obj = build()
        self.assertEqual(
            obj["post_ablation_generic_applicability"]["UNCHANGED"],
            NOT_APPLICABLE,
        )

    def test_ablated_unresolved_bucket_is_underdetermined(self):
        obj = build()
        self.assertEqual(
            obj["post_ablation_generic_applicability"]["UNRESOLVED"],
            UNDERDETERMINED,
        )

    def test_declared_horizon_is_load_bearing_but_global_is_unresolved(self):
        obj = build()
        self.assertEqual(
            obj["declared_horizon_load_bearing_status"], "YES"
        )
        self.assertEqual(
            obj["global_current_load_bearing_status"], "UNRESOLVED"
        )

    def test_only_semantic_and_coordination_current_load_are_claimed(self):
        obj = build()
        self.assertEqual(obj["current_load_profile"]["semantic"], "YES")
        self.assertEqual(obj["current_load_profile"]["coordination"], "YES")
        for key in (
            "functional",
            "authority",
            "provenance",
            "temporal",
        ):
            self.assertEqual(
                obj["current_load_profile"][key], "UNRESOLVED"
            )

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
        tampered["global_current_load_bearing_status"] = "YES"
        with self.assertRaises(Exception):
            validate_current_horizon_distinction_dependence(tampered)

    def test_incomplete_collision_coverage_rejected(self):
        with self.assertRaisesRegex(
            CurrentHorizonDistinctionDependenceError,
            "cover exactly",
        ):
            build_current_horizon_distinction_dependence(
                source_g4_observation_blob_sha=G4_BLOB,
                source_g5_result_blob_sha=G5_RESULT_BLOB,
                g4_cases=G4_CASES,
                g5_collision_groups={"UNCHANGED": ["NEITHER"]},
            )


if __name__ == "__main__":
    unittest.main()
