from __future__ import annotations

import unittest

from src.coordination.settlement_consequence_reconciliation_v0 import (
    SettlementConsequenceError,
    build_consequence_evaluation,
    build_observed_consequence,
    reconcile,
)
from tests.coordination.test_basis_workcycle_v1 import unit_fixture
from tests.coordination.test_invocation_result_settlement_v0 import (
    bases,
    dispositions,
    valid_witness,
)
from src.coordination.invocation_result_settlement_v0 import build_candidate_settlement


def fixture():
    unit = unit_fixture()
    unit["qualification"]["scientific_standing"] = "QUALIFIED"
    unit["application"]["application_status"] = "APPLIED"
    unit["consequence_observation"]["effect_class"] = "NOT_YET_OBSERVABLE"
    settled = build_candidate_settlement(
        result_witness=valid_witness(),
        field_dispositions=dispositions(),
        settlement_basis=bases(),
        settlement_actor_identity="independent-settler-fixture-v0",
    )
    return unit, settled


class SettlementConsequenceReconciliationV0Tests(unittest.TestCase):
    def test_settlement_alone_stays_blocked(self):
        unit, settled = fixture()
        result = reconcile(
            unit=unit,
            settlement=settled,
            expected_work_attempt_id=settled["source_work_attempt_id"],
            observed_consequence=None,
            consequence_evaluation=None,
            current_obstruction_posture="REMAINS",
        )
        self.assertEqual(result["basis_reconciliation"]["disposition"], "STILL_BLOCKED")
        self.assertIsNone(result["consequence_id"])
        self.assertFalse(result["settlement_is_consequence"])

    def test_matched_consequence_resolved_obstruction_satisfies(self):
        unit, settled = fixture()
        observed = build_observed_consequence(
            settlement=settled,
            work_item_id=unit["identity"]["work_item_id"],
            expected_effect="fixture obstruction resolves",
            observed_effect="fixture obstruction resolved",
            effect_class="OBSERVED",
            evidence_refs=["fixture://matched"],
        )
        evaluation = build_consequence_evaluation(
            observed_consequence=observed,
            disposition="CONSEQUENCE_MATCHED",
            evaluation_basis="independent fixture evidence matches",
            evaluator_identity="independent-consequence-evaluator-v0",
        )
        result = reconcile(
            unit=unit,
            settlement=settled,
            expected_work_attempt_id=settled["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="RESOLVED",
        )
        self.assertEqual(result["basis_reconciliation"]["disposition"], "SATISFIED")
        self.assertEqual(result["consequence_id"], observed["consequence_id"])
        self.assertEqual(result["evaluation_id"], evaluation["evaluation_id"])

    def test_contradicted_consequence_invalidates(self):
        unit, settled = fixture()
        observed = build_observed_consequence(
            settlement=settled,
            work_item_id=unit["identity"]["work_item_id"],
            expected_effect="fixture obstruction resolves",
            observed_effect="fixture obstruction worsened",
            effect_class="OBSERVED",
            evidence_refs=["fixture://contradicted"],
            regression_detected=True,
        )
        evaluation = build_consequence_evaluation(
            observed_consequence=observed,
            disposition="CONSEQUENCE_CONTRADICTED",
            evaluation_basis="independent fixture evidence contradicts expected effect",
            evaluator_identity="independent-consequence-evaluator-v0",
        )
        result = reconcile(
            unit=unit,
            settlement=settled,
            expected_work_attempt_id=settled["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="REMAINS",
        )
        self.assertEqual(result["basis_reconciliation"]["disposition"], "INVALIDATED")

    def test_wrong_settlement_binding_rejected(self):
        unit, settled = fixture()
        other = dict(settled)
        other["settlement_id"] = "invocation-result-candidate-settlement:sha256:" + "9" * 64
        with self.assertRaisesRegex(SettlementConsequenceError, "settlement identity mismatch"):
            build_observed_consequence(
                settlement=other,
                work_item_id=unit["identity"]["work_item_id"],
                expected_effect="fixture obstruction resolves",
                observed_effect="fixture obstruction resolved",
                effect_class="OBSERVED",
                evidence_refs=["fixture://wrong-settlement"],
            )

    def test_no_authority_execution_atlas_or_standing_effect(self):
        unit, settled = fixture()
        result = reconcile(
            unit=unit,
            settlement=settled,
            expected_work_attempt_id=settled["source_work_attempt_id"],
            observed_consequence=None,
            consequence_evaluation=None,
            current_obstruction_posture="REMAINS",
        )
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")
        self.assertEqual(result["atlas_mutation_effect"], "NONE")
        self.assertEqual(result["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
