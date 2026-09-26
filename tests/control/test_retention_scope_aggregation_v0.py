from __future__ import annotations

import copy
import unittest

from src.control.retention_scope_aggregation_v0 import (
    RetentionScopeAggregationError,
    build_retention_scope_aggregation,
    validate_retention_scope_aggregation,
)

G8_RESULT_BLOB = "e5f603fbea6ef05193f092245252cd26d6eae66a"
G8_WITNESS_BLOB = "949ff2b9333146ca16e68981123f338f6e4dfd15"


def build(requirements):
    return build_retention_scope_aggregation(
        source_g8_result_blob_sha=G8_RESULT_BLOB,
        source_g8_witness_blob_sha=G8_WITNESS_BLOB,
        horizon_requirements=requirements,
    )


class RetentionScopeAggregationV0Tests(unittest.TestCase):
    def test_required_dominates_not_required(self):
        obj = build({
            "H_CURRENT": "REQUIRED",
            "H_NONCURRENT": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
        })
        self.assertEqual(
            obj["declared_scope_hot_requirement"], "REQUIRED"
        )

    def test_all_not_required_yields_scope_not_required(self):
        obj = build({
            "H_A": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            "H_B": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
        })
        self.assertEqual(
            obj["declared_scope_hot_requirement"],
            "NOT_REQUIRED_FOR_DECLARED_SCOPE",
        )

    def test_unresolved_survives_without_required(self):
        obj = build({
            "H_A": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
            "H_B": "UNRESOLVED",
        })
        self.assertEqual(
            obj["declared_scope_hot_requirement"], "UNRESOLVED"
        )

    def test_required_dominates_unresolved(self):
        obj = build({
            "H_A": "REQUIRED",
            "H_B": "UNRESOLVED",
        })
        self.assertEqual(
            obj["declared_scope_hot_requirement"], "REQUIRED"
        )

    def test_scope_is_not_promoted_to_global(self):
        obj = build({"H_A": "REQUIRED"})
        self.assertEqual(
            obj["declared_scope_complete_for_supplied_horizons"], "YES"
        )
        self.assertEqual(
            obj["global_ecology_hot_requirement"], "UNRESOLVED"
        )

    def test_cold_source_retention_remains_required(self):
        obj = build({"H_A": "NOT_REQUIRED_FOR_DECLARED_HORIZON"})
        self.assertEqual(
            obj["exact_cold_source_retention_required"], "YES"
        )

    def test_no_transition_or_consequence_effects(self):
        obj = build({"H_A": "REQUIRED"})
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
        req = {"H_B": "UNRESOLVED", "H_A": "REQUIRED"}
        self.assertEqual(build(req), build(req))

    def test_validation_rejects_tampering(self):
        obj = build({"H_A": "REQUIRED"})
        tampered = copy.deepcopy(obj)
        tampered["global_ecology_hot_requirement"] = "REQUIRED"
        with self.assertRaises(Exception):
            validate_retention_scope_aggregation(tampered)

    def test_empty_scope_rejected(self):
        with self.assertRaisesRegex(
            RetentionScopeAggregationError, "non-empty"
        ):
            build({})


if __name__ == "__main__":
    unittest.main()
