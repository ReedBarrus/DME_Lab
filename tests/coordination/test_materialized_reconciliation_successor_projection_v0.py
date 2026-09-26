from __future__ import annotations

import copy
import unittest

from src.coordination.materialized_reconciliation_successor_projection_v0 import (
    MaterializedReconciliationSuccessorError,
    derive_materialized_successor_projection,
)
from src.coordination.materialized_settlement_consequence_reconciliation_v0 import (
    build_consequence_evaluation,
    build_observed_consequence,
    reconcile,
)
from tests.coordination.test_materialized_settlement_consequence_reconciliation_v0 import (
    fixture,
)


def consequence_fixture():
    successor, spec, unit, settlement = fixture()
    observed = build_observed_consequence(
        settlement=settlement,
        materialized_unit=unit,
        expected_effect="exact materialized obstruction resolves",
        observed_effect="exact materialized obstruction resolved",
        effect_class="OBSERVED",
        evidence_refs=["fixture://successor-projection"],
    )
    matched_eval = build_consequence_evaluation(
        observed_consequence=observed,
        disposition="CONSEQUENCE_MATCHED",
        evaluation_basis="independent exact-work evidence matches",
        evaluator_identity="independent-materialized-successor-evaluator-v0",
    )
    return successor, spec, unit, settlement, observed, matched_eval


class MaterializedReconciliationSuccessorProjectionV0Tests(unittest.TestCase):
    def test_satisfied_reconciliation_lawfully_stops(self):
        _, _, unit, settlement, observed, evaluation = consequence_fixture()
        composition = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="RESOLVED",
        )
        projection = derive_materialized_successor_projection(
            unit=unit,
            reconciliation_composition=composition,
        )
        self.assertEqual(projection["basis_disposition"], "SATISFIED")
        self.assertEqual(projection["derived_successor_posture"], "CLOSE_BASIS")
        self.assertEqual(projection["derived_candidate_posture"], "NO_SUCCESSOR")
        self.assertIsNone(projection["derived_successor_id"])
        self.assertFalse(projection["next_pressure_allowed"])

    def test_partial_reconciliation_derives_one_deterministic_candidate(self):
        _, _, unit, settlement, observed, evaluation = consequence_fixture()
        composition = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="REMAINS",
            remaining_gap="one source-supported obstruction remains",
        )
        one = derive_materialized_successor_projection(
            unit=unit,
            reconciliation_composition=composition,
        )
        two = derive_materialized_successor_projection(
            unit=unit,
            reconciliation_composition=composition,
        )
        self.assertEqual(one, two)
        self.assertEqual(one["basis_disposition"], "PARTIALLY_SATISFIED")
        self.assertTrue(one["next_pressure_allowed"])
        self.assertEqual(
            one["next_pressure_basis"],
            "resolve remaining source-supported obstruction",
        )
        self.assertEqual(
            one["derived_successor_posture"],
            "RESOLVE_LOAD_BEARING_GAP",
        )
        self.assertEqual(
            one["derived_candidate_posture"],
            "PROPOSED_NOT_ADMITTED",
        )
        self.assertIsNotNone(one["derived_successor_id"])
        self.assertEqual(
            one["successor_candidate"]["reconciliation_identity"],
            composition["reconciliation_identity"],
        )
        self.assertEqual(
            one["successor_candidate"]["next_pressure_basis"],
            composition["basis_reconciliation"]["next_pressure_basis"],
        )

    def test_invalidated_reconciliation_lawfully_stops(self):
        _, _, unit, settlement, observed, _ = consequence_fixture()
        contradicted = build_consequence_evaluation(
            observed_consequence=observed,
            disposition="CONSEQUENCE_CONTRADICTED",
            evaluation_basis="independent exact-work evidence contradicts",
            evaluator_identity="independent-materialized-successor-evaluator-v0",
        )
        composition = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=contradicted,
            current_obstruction_posture="REMAINS",
        )
        projection = derive_materialized_successor_projection(
            unit=unit,
            reconciliation_composition=composition,
        )
        self.assertEqual(projection["basis_disposition"], "INVALIDATED")
        self.assertEqual(
            projection["derived_successor_posture"],
            "HOLD_NO_JUSTIFIED_WORK",
        )
        self.assertEqual(projection["derived_candidate_posture"], "NO_SUCCESSOR")
        self.assertIsNone(projection["derived_successor_id"])
        self.assertFalse(projection["next_pressure_allowed"])

    def test_projection_preserves_exact_materialized_lineage(self):
        successor, spec, unit, settlement, observed, evaluation = consequence_fixture()
        composition = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="REMAINS",
            remaining_gap="one source-supported obstruction remains",
        )
        projection = derive_materialized_successor_projection(
            unit=unit,
            reconciliation_composition=composition,
        )
        self.assertEqual(projection["source_successor_id"], successor["successor_id"])
        self.assertEqual(projection["source_work_spec_id"], spec["work_spec_id"])
        self.assertEqual(
            projection["source_materialized_unit_integrity_sha256"],
            unit["integrity_sha256"],
        )
        self.assertEqual(
            projection["source_composition_id"],
            composition["composition_id"],
        )
        self.assertEqual(
            projection["source_settlement_id"],
            settlement["settlement_id"],
        )

    def test_tampered_composition_is_rejected(self):
        _, _, unit, settlement, observed, evaluation = consequence_fixture()
        composition = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="RESOLVED",
        )
        tampered = copy.deepcopy(composition)
        tampered["work_spec_id"] = "successor-work-spec:sha256:" + "9" * 64
        with self.assertRaises(Exception):
            derive_materialized_successor_projection(
                unit=unit,
                reconciliation_composition=tampered,
            )

    def test_no_work_authority_execution_or_standing_created(self):
        _, _, unit, settlement, observed, evaluation = consequence_fixture()
        composition = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="RESOLVED",
        )
        projection = derive_materialized_successor_projection(
            unit=unit,
            reconciliation_composition=composition,
        )
        self.assertFalse(projection["work_created"])
        self.assertEqual(projection["work_admission_effect"], "NONE")
        self.assertEqual(projection["authority_effect"], "NONE")
        self.assertEqual(projection["execution_effect"], "NONE")
        self.assertEqual(projection["scientific_standing_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
