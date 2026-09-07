from __future__ import annotations

import unittest

from src.runtime.provenance_recovery_pressure import UNRESOLVED
from src.runtime.tie_order_invariance_pressure import (
    RESOLVED_BY_ORDER_INVARIANCE,
    _resolve_relation,
    run,
)


class TieOrderInvariancePressureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = run()
        cls.linearizations = cls.report["bounded_linearizations"]

    def test_chart_9_c2_reproduces_unchanged(self) -> None:
        prior = self.report["prior_chart_9"]

        self.assertTrue(prior["C2_reproduced_unchanged"])
        self.assertFalse(prior["evidence_modified"])
        self.assertTrue(prior["remains_valid"])

    def test_all_bounded_equal_index_linearizations_are_enumerated(self) -> None:
        self.assertEqual(self.report["tied_records"]["count"], 2)
        self.assertEqual(len(self.linearizations), 2)
        self.assertEqual(
            self.report["ordering_constraints"][
                "complete_bounded_linearization_count"
            ],
            2,
        )
        self.assertTrue(
            self.report["relation_resolution"][
                "all_permitted_linearizations_evaluated"
            ]
        )

    def test_physical_runtime_order_is_not_privileged(self) -> None:
        runtime = self.report["runtime_stable_sort_observations"]

        self.assertEqual(
            runtime["classification"], "non-authoritative implementation behavior"
        )
        self.assertFalse(runtime["used_to_select_linearization"])
        self.assertFalse(
            self.report["ordering_constraints"]["physical_input_order_authoritative"]
        )

    def test_no_tie_break_is_introduced(self) -> None:
        self.assertIsNone(self.report["ordering_constraints"]["secondary_key"])
        self.assertFalse(self.report["tie_break"]["introduced"])
        self.assertFalse(self.report["tie_break"]["used"])

    def test_prefix_is_evaluated_for_each_linearization(self) -> None:
        self.assertEqual(
            [result["prefix"] for result in self.linearizations.values()],
            [False, False],
        )

    def test_ordered_subsequence_is_evaluated_for_each_linearization(self) -> None:
        self.assertEqual(
            [result["ordered_subsequence"] for result in self.linearizations.values()],
            [True, True],
        )

    def test_complete_relation_signatures_are_recorded(self) -> None:
        self.assertEqual(
            self.report["relation_resolution"]["complete_relation_signatures"],
            [
                {"prefix": False, "ordered_subsequence": True},
                {"prefix": False, "ordered_subsequence": True},
            ],
        )

    def test_relations_resolve_only_by_complete_invariance(self) -> None:
        prefix = self.report["relation_resolution"]["prefix"]
        subsequence = self.report["relation_resolution"]["ordered_subsequence"]

        self.assertTrue(prefix["invariant"])
        self.assertTrue(subsequence["invariant"])
        self.assertEqual(prefix["status"], RESOLVED_BY_ORDER_INVARIANCE)
        self.assertEqual(subsequence["status"], RESOLVED_BY_ORDER_INVARIANCE)
        self.assertFalse(
            self.report["relation_resolution"]["existential_result_sufficient"]
        )

    def test_non_invariant_relation_would_remain_unresolved(self) -> None:
        result = _resolve_relation([False, True])

        self.assertFalse(result["invariant"])
        self.assertEqual(result["status"], UNRESOLVED)
        self.assertIsNone(result["value"])

    def test_ordering_and_admissibility_remain_unresolved(self) -> None:
        self.assertEqual(self.report["ordering_status"], UNRESOLVED)
        self.assertEqual(self.report["admissibility_status"], UNRESOLVED)
        self.assertEqual(
            self.report["relation_resolution"]["overall_status"],
            RESOLVED_BY_ORDER_INVARIANCE,
        )

    def test_prior_chart_9_evidence_remains_untouched(self) -> None:
        back_pressure = self.report["chart_9_back_pressure"]

        self.assertTrue(back_pressure["refined"])
        self.assertFalse(back_pressure["prior_result_invalidated"])
        self.assertFalse(back_pressure["prior_trace_modified"])

    def test_production_replay_semantics_remain_unchanged(self) -> None:
        changes = self.report["production_changes"]

        self.assertFalse(changes["replay_semantics"])
        self.assertFalse(changes["secondary_order_key"])
        self.assertFalse(changes["canonical_history"])

    def test_no_generalized_architecture_is_added(self) -> None:
        self.assertEqual(self.report["architecture_added"], [])
        self.assertFalse(
            self.report["duple_interpretation"]["runtime_abstraction_added"]
        )
        self.assertFalse(self.report["navigation_relevance"]["navigator_added"])
        self.assertFalse(self.report["navigation_relevance"]["scheduler_added"])
        self.assertFalse(
            self.report["navigation_relevance"]["attention_or_cost_added"]
        )


if __name__ == "__main__":
    unittest.main()
