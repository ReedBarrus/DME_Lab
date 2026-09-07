from __future__ import annotations

import unittest

from src.runtime.history_constraint_ablation_pressure import CONTROL_RULES, run
from src.runtime.provenance_recovery_pressure import UNRESOLVED


class HistoryConstraintAblationPressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.regimes = cls.report["single_constraint_variants"]

    def test_chart_8_reproduces_under_control(self) -> None:
        prior = self.report["prior_chart_8"]

        self.assertTrue(prior["reproduced_unchanged"])
        self.assertFalse(prior["evidence_modified"])
        self.assertTrue(prior["remains_valid"])
        self.assertFalse(
            self.report["C0_current_contract"][
                "chart_8_admissible_discriminator_found"
            ]
        )

    def test_each_variant_changes_exactly_one_declared_dimension(self) -> None:
        for name, result in self.regimes.items():
            if name == "C0_current_contract":
                continue
            changed = [
                key
                for key in CONTROL_RULES
                if result["rules"][key] != CONTROL_RULES[key]
            ]
            self.assertEqual(changed, [result["changed_rule"]], name)

    def test_carrier_recomputed_only_when_generating_boundary_changes(self) -> None:
        for name, result in self.regimes.items():
            if name == "C7_remove_commit_index_from_boundary_only":
                self.assertTrue(result["carrier"]["recomputed"])
                self.assertFalse(result["carrier"]["bytes_fixed"])
            else:
                self.assertFalse(result["carrier"]["recomputed"], name)
                self.assertTrue(result["carrier"]["bytes_fixed"], name)

    def test_source_h14_lineage_remains_fixed(self) -> None:
        source = self.report["fixed_source_lineage"]

        self.assertEqual(source["record_count"], 14)
        self.assertEqual(source["identity_before"], source["identity_after"])
        self.assertTrue(source["unchanged"])

    def test_integer_only_ablation_opens_discriminator(self) -> None:
        result = self.regimes["C1_relax_integer_only"]

        self.assertTrue(result["integrity"]["ok"])
        self.assertTrue(result["admissibility"])
        self.assertTrue(result["relations"]["H14_subsequence"])
        self.assertFalse(result["relations"]["H14_prefix"])
        self.assertTrue(result["discriminator_reachable"])

    def test_duplicate_index_ablation_remains_unresolved(self) -> None:
        result = self.regimes["C2_relax_duplicate_index_prohibition"]

        self.assertEqual(result["ordering"]["status"], UNRESOLVED)
        self.assertTrue(result["ordering"]["physical_input_order_dependent"])
        self.assertFalse(result["ordering"]["tie_break_invented"])
        self.assertEqual(result["admissibility"], UNRESOLVED)
        self.assertEqual(result["discriminator_reachable"], UNRESOLVED)

    def test_gap_free_ablation_maintains_collapse(self) -> None:
        result = self.regimes["C3_relax_gap_free_only"]

        self.assertTrue(result["admissibility"])
        self.assertTrue(result["relations"]["H14_subsequence"])
        self.assertTrue(result["relations"]["H14_prefix"])
        self.assertFalse(result["discriminator_reachable"])

    def test_start_at_one_ablation_opens_discriminator(self) -> None:
        result = self.regimes["C4_relax_start_at_one_only"]

        self.assertTrue(result["admissibility"])
        self.assertTrue(result["relations"]["H14_subsequence"])
        self.assertFalse(result["relations"]["H14_prefix"])
        self.assertTrue(result["discriminator_reachable"])

    def test_record_id_uniqueness_ablation_maintains_collapse(self) -> None:
        result = self.regimes["C5_relax_duplicate_record_id_only"]

        self.assertTrue(result["admissibility"])
        self.assertTrue(result["relations"]["H14_subsequence"])
        self.assertTrue(result["relations"]["H14_prefix"])
        self.assertFalse(result["discriminator_reachable"])

    def test_ordering_ablation_opens_discriminator(self) -> None:
        result = self.regimes["C6_vary_replay_ordering_only"]

        self.assertTrue(result["integrity"]["ok"])
        self.assertTrue(result["continuity"]["ok"])
        self.assertTrue(result["admissibility"])
        self.assertTrue(result["relations"]["H14_subsequence"])
        self.assertFalse(result["relations"]["H14_prefix"])

    def test_commitment_boundary_ablation_recomputes_and_opens_discriminator(self) -> None:
        result = self.regimes["C7_remove_commit_index_from_boundary_only"]

        self.assertTrue(result["carrier"]["source_lineage_fixed"])
        self.assertEqual(result["carrier"]["committed_fields"], ["record_id", "envelope"])
        self.assertTrue(result["integrity"]["ok"])
        self.assertTrue(result["admissibility"])
        self.assertTrue(result["relations"]["H14_subsequence"])
        self.assertFalse(result["relations"]["H14_prefix"])

    def test_relations_recorded_in_every_interpretable_regime(self) -> None:
        for name, result in self.regimes.items():
            if name == "C2_relax_duplicate_index_prohibition":
                continue
            self.assertIsInstance(result["relations"]["H14_prefix"], bool, name)
            self.assertIsInstance(result["relations"]["H14_subsequence"], bool, name)

    def test_ambiguous_ordering_does_not_inherit_physical_tie_break(self) -> None:
        result = self.regimes["C2_relax_duplicate_index_prohibition"]
        observations = result["ordering"]["runtime_observations"]

        self.assertNotEqual(
            observations["inserted_before_existing_tie"]["tied_record_ids"],
            observations["inserted_after_existing_tie"]["tied_record_ids"],
        )
        self.assertEqual(result["relations"]["H14_prefix"], UNRESOLVED)
        self.assertEqual(result["relations"]["H14_subsequence"], UNRESOLVED)

    def test_production_contract_and_history_remain_unchanged(self) -> None:
        changes = self.report["production_changes"]

        self.assertFalse(changes["ledger_validator"])
        self.assertFalse(changes["digest_boundary"])
        self.assertFalse(changes["replay_order"])
        self.assertFalse(changes["canonical_history"])

    def test_classification_and_commit_index_coupling_are_executable(self) -> None:
        classifications = self.report["constraint_classifications"]

        self.assertEqual(len(classifications["collapse-contributing"]), 4)
        self.assertEqual(len(classifications["collapse-maintaining"]), 2)
        self.assertEqual(classifications[UNRESOLVED], [
            "C2_relax_duplicate_index_prohibition"
        ])
        self.assertTrue(self.report["multiple_individual_constraints_contribute"])
        self.assertTrue(self.report["commit_index_role_coupling"]["supported"])

    def test_no_scheduler_basis_tensor_or_generalized_architecture_added(self) -> None:
        self.assertEqual(self.report["architecture_added"], [])
        self.assertFalse(
            self.report["duple_basis_interpretation"]["runtime_basis_object_added"]
        )
        self.assertFalse(self.report["navigation_relevance"]["regime_switching_added"])
        self.assertFalse(self.report["navigation_relevance"]["scheduler_added"])
        self.assertFalse(
            self.report["attention_cost_note"]["cost_or_attention_model_added"]
        )


if __name__ == "__main__":
    unittest.main()
