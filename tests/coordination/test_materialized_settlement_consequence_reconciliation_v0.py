from __future__ import annotations

import unittest

from src.coordination.materialized_invocation_result_settlement_v0 import (
    build_materialized_candidate_settlement,
)
from src.coordination.materialized_settlement_consequence_reconciliation_v0 import (
    MaterializedSettlementConsequenceError,
    build_consequence_evaluation,
    build_observed_consequence,
    reconcile,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    materialize_successor_work_unit,
)
from tests.coordination.test_materialized_invocation_result_settlement_v0 import (
    bases,
    dispositions,
    valid_materialized_witness,
)
from tests.coordination.test_materialized_unit_authority_admission_v0 import (
    alternate_spec,
)
from tests.coordination.test_successor_work_unit_materialization_v0 import (
    partial_successor,
    work_spec,
)


def fixture():
    successor = partial_successor()
    spec = work_spec(successor)
    unit = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec,
    )
    settlement = build_materialized_candidate_settlement(
        result_witness=valid_materialized_witness(),
        field_dispositions=dispositions(),
        settlement_basis=bases(),
        settlement_actor_identity="independent-materialized-settler-fixture-v0",
    )
    return successor, spec, unit, settlement


class MaterializedSettlementConsequenceReconciliationV0Tests(unittest.TestCase):
    def test_settlement_alone_stays_blocked(self):
        _, _, unit, settlement = fixture()
        result = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=None,
            consequence_evaluation=None,
            current_obstruction_posture="REMAINS",
        )
        self.assertEqual(
            result["basis_reconciliation"]["disposition"],
            "STILL_BLOCKED",
        )
        self.assertIsNone(result["consequence_id"])
        self.assertFalse(result["settlement_is_consequence"])

    def test_matched_consequence_resolved_obstruction_satisfies(self):
        _, _, unit, settlement = fixture()
        observed = build_observed_consequence(
            settlement=settlement,
            materialized_unit=unit,
            expected_effect="exact materialized obstruction resolves",
            observed_effect="exact materialized obstruction resolved",
            effect_class="OBSERVED",
            evidence_refs=["fixture://materialized-matched"],
        )
        evaluation = build_consequence_evaluation(
            observed_consequence=observed,
            disposition="CONSEQUENCE_MATCHED",
            evaluation_basis="independent exact-work evidence matches",
            evaluator_identity="independent-materialized-consequence-evaluator-v0",
        )
        result = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="RESOLVED",
        )
        self.assertEqual(
            result["basis_reconciliation"]["disposition"],
            "SATISFIED",
        )
        self.assertEqual(result["consequence_id"], observed["consequence_id"])
        self.assertEqual(result["evaluation_id"], evaluation["evaluation_id"])

    def test_contradicted_consequence_invalidates(self):
        _, _, unit, settlement = fixture()
        observed = build_observed_consequence(
            settlement=settlement,
            materialized_unit=unit,
            expected_effect="exact materialized obstruction resolves",
            observed_effect="exact materialized obstruction worsened",
            effect_class="OBSERVED",
            evidence_refs=["fixture://materialized-contradicted"],
            regression_detected=True,
        )
        evaluation = build_consequence_evaluation(
            observed_consequence=observed,
            disposition="CONSEQUENCE_CONTRADICTED",
            evaluation_basis="independent exact-work evidence contradicts expected effect",
            evaluator_identity="independent-materialized-consequence-evaluator-v0",
        )
        result = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
            observed_consequence=observed,
            consequence_evaluation=evaluation,
            current_obstruction_posture="REMAINS",
        )
        self.assertEqual(
            result["basis_reconciliation"]["disposition"],
            "INVALIDATED",
        )

    def test_consequence_binds_exact_work_lineage(self):
        successor, spec, unit, settlement = fixture()
        observed = build_observed_consequence(
            settlement=settlement,
            materialized_unit=unit,
            expected_effect="fixture expected",
            observed_effect="fixture observed",
            effect_class="OBSERVED",
            evidence_refs=["fixture://lineage"],
        )
        self.assertEqual(observed["successor_id"], successor["successor_id"])
        self.assertEqual(observed["work_spec_id"], spec["work_spec_id"])
        self.assertEqual(
            observed["materialized_unit_integrity_sha256"],
            unit["integrity_sha256"],
        )
        self.assertEqual(
            observed["source_settlement_id"],
            settlement["settlement_id"],
        )

    def test_wrong_materialization_under_same_successor_is_rejected(self):
        successor, _, _, settlement = fixture()
        spec_b = alternate_spec(successor)
        unit_b = materialize_successor_work_unit(
            successor_candidate=successor,
            work_spec=spec_b,
        )
        with self.assertRaisesRegex(
            MaterializedSettlementConsequenceError,
            "settlement/materialized unit mismatch|settlement/materialized work-spec",
        ):
            build_observed_consequence(
                settlement=settlement,
                materialized_unit=unit_b,
                expected_effect="fixture expected",
                observed_effect="fixture observed",
                effect_class="OBSERVED",
                evidence_refs=["fixture://wrong-unit"],
            )

    def test_tampered_settlement_is_rejected(self):
        _, _, unit, settlement = fixture()
        tampered = dict(settlement)
        tampered["settlement_id"] = (
            "materialized-invocation-result-candidate-settlement:sha256:"
            + "9" * 64
        )
        with self.assertRaisesRegex(
            MaterializedSettlementConsequenceError,
            "settlement identity mismatch",
        ):
            build_observed_consequence(
                settlement=tampered,
                materialized_unit=unit,
                expected_effect="fixture expected",
                observed_effect="fixture observed",
                effect_class="OBSERVED",
                evidence_refs=["fixture://tampered"],
            )

    def test_no_authority_execution_atlas_or_standing_effect(self):
        _, _, unit, settlement = fixture()
        result = reconcile(
            unit=unit,
            settlement=settlement,
            expected_work_attempt_id=settlement["source_work_attempt_id"],
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
