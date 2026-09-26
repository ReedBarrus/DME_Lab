from __future__ import annotations

import copy
import unittest

from src.control.distinction_retention_currentness_v0 import (
    DistinctionRetentionCurrentnessError,
    build_distinction_retention_currentness,
    validate_distinction_retention_currentness,
)

G7_RESULT_BLOB = "7d037362dd0e438ae7c1fb2553d452a9ae2fd233"
G7_WITNESS_BLOB = "1ff52354096371710ccdcdd77dfb9a6b2c1ada3b"


def build(currentness: str):
    return build_distinction_retention_currentness(
        source_g7_result_blob_sha=G7_RESULT_BLOB,
        source_g7_witness_blob_sha=G7_WITNESS_BLOB,
        horizon_currentness=currentness,
    )


class DistinctionRetentionCurrentnessV0Tests(unittest.TestCase):
    def test_current_preserves_declared_horizon_hot_requirement(self):
        obj = build("CURRENT")
        self.assertEqual(
            obj["declared_horizon_hot_requirement"], "REQUIRED"
        )

    def test_noncurrent_removes_requirement_for_declared_horizon_only(self):
        obj = build("NONCURRENT")
        self.assertEqual(
            obj["declared_horizon_hot_requirement"],
            "NOT_REQUIRED_FOR_DECLARED_HORIZON",
        )
        self.assertEqual(obj["global_hot_requirement"], "UNRESOLVED")

    def test_unresolved_currentness_preserves_unresolvedness(self):
        obj = build("UNRESOLVED")
        self.assertEqual(
            obj["declared_horizon_hot_requirement"], "UNRESOLVED"
        )
        self.assertEqual(obj["global_hot_requirement"], "UNRESOLVED")

    def test_cold_source_retention_stays_required_in_all_cases(self):
        for posture in ("CURRENT", "NONCURRENT", "UNRESOLVED"):
            self.assertEqual(
                build(posture)["exact_cold_source_retention_required"], "YES"
            )

    def test_no_transition_deletion_or_consequence_effect(self):
        for posture in ("CURRENT", "NONCURRENT", "UNRESOLVED"):
            obj = build(posture)
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
        self.assertEqual(build("CURRENT"), build("CURRENT"))

    def test_validation_rejects_tampering(self):
        obj = build("CURRENT")
        tampered = copy.deepcopy(obj)
        tampered["global_hot_requirement"] = "REQUIRED"
        with self.assertRaises(Exception):
            validate_distinction_retention_currentness(tampered)

    def test_invalid_currentness_rejected(self):
        with self.assertRaisesRegex(
            DistinctionRetentionCurrentnessError,
            "unsupported horizon_currentness",
        ):
            build("STALEISH")


if __name__ == "__main__":
    unittest.main()
