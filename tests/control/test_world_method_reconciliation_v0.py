from __future__ import annotations

import copy
import unittest

from src.control.world_method_reconciliation_v0 import (
    WorldMethodReconciliationError,
    build_world_method_reconciliation,
    validate_world_method_reconciliation,
)

SOURCE_ID = (
    "materialized-settlement-consequence-reconciliation:sha256:"
    "04719abab92fef5f17a63ee36500748894d4e7e47054c72f105a8b28c4fe06a7"
)
SOURCE_INTEGRITY = (
    "091ad5b9dcdb6a40085d7f0318ab630bf0656d272d1046577500ae2e1ed66516"
)


def build(world: str, method: str):
    return build_world_method_reconciliation(
        source_reconciliation_id=SOURCE_ID,
        source_reconciliation_identity_sha256=SOURCE_INTEGRITY,
        world_posture_change=world,
        world_evidence_refs=[f"fixture://world/{world.lower()}"],
        cognitive_method_change=method,
        method_evidence_refs=[f"fixture://method/{method.lower()}"],
    )


class WorldMethodReconciliationV0Tests(unittest.TestCase):
    def test_world_only_is_representable(self):
        obj = build("CHANGED", "UNCHANGED")
        self.assertEqual(obj["world_axis"]["posture_change"], "CHANGED")
        self.assertEqual(
            obj["method_axis"]["cognitive_method_change"], "UNCHANGED"
        )

    def test_method_only_is_representable(self):
        obj = build("UNCHANGED", "CHANGED")
        self.assertEqual(obj["world_axis"]["posture_change"], "UNCHANGED")
        self.assertEqual(obj["method_axis"]["cognitive_method_change"], "CHANGED")

    def test_both_and_neither_are_distinct(self):
        both = build("CHANGED", "CHANGED")
        neither = build("UNCHANGED", "UNCHANGED")
        self.assertNotEqual(
            both["world_method_reconciliation_id"],
            neither["world_method_reconciliation_id"],
        )
        self.assertNotEqual(
            both["integrity_sha256"],
            neither["integrity_sha256"],
        )

    def test_unresolved_axis_remains_explicit(self):
        obj = build("UNRESOLVED", "UNCHANGED")
        self.assertEqual(obj["world_axis"]["posture_change"], "UNRESOLVED")
        self.assertTrue(obj["world_axis"]["evidence_refs"])

    def test_unresolved_requires_evidence(self):
        with self.assertRaisesRegex(
            WorldMethodReconciliationError,
            "UNRESOLVED world axis requires evidence refs",
        ):
            build_world_method_reconciliation(
                source_reconciliation_id=SOURCE_ID,
                source_reconciliation_identity_sha256=SOURCE_INTEGRITY,
                world_posture_change="UNRESOLVED",
                world_evidence_refs=[],
                cognitive_method_change="UNCHANGED",
                method_evidence_refs=["fixture://method/unchanged"],
            )

    def test_fixed_inputs_are_deterministic(self):
        self.assertEqual(build("CHANGED", "UNCHANGED"), build("CHANGED", "UNCHANGED"))

    def test_validation_rejects_tampering(self):
        obj = build("CHANGED", "UNCHANGED")
        tampered = copy.deepcopy(obj)
        tampered["method_axis"]["cognitive_method_change"] = "CHANGED"
        with self.assertRaises(Exception):
            validate_world_method_reconciliation(tampered)

    def test_no_causality_learning_or_consequence_effects(self):
        obj = build("CHANGED", "CHANGED")
        self.assertEqual(obj["causal_attribution_effect"], "NONE")
        self.assertEqual(obj["gap_selection_effect"], "NONE")
        self.assertEqual(obj["work_justification_effect"], "NONE")
        self.assertEqual(obj["planning_effect"], "NONE")
        self.assertEqual(obj["method_capitalization_effect"], "NONE")
        self.assertEqual(obj["policy_mutation_effect"], "NONE")
        self.assertEqual(obj["authority_effect"], "NONE")
        self.assertEqual(obj["execution_effect"], "NONE")
        self.assertEqual(obj["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
