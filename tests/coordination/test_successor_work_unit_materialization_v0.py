from __future__ import annotations

import copy
import unittest

from src.coordination import basis_workcycle_v1 as bw
from src.coordination.successor_work_unit_materialization_v0 import (
    SuccessorWorkUnitMaterializationError,
    build_successor_work_spec,
    materialize_successor_work_unit,
)
from tests.coordination.test_basis_workcycle_v1 import unit_fixture


def partial_successor() -> dict:
    unit = unit_fixture()
    admissibility = bw.pressure_admissibility(unit)
    reconciliation = bw.basis_reconciliation(
        unit,
        disposition="PARTIALLY_SATISFIED",
        remaining_gap="one source-supported obstruction remains",
        next_pressure_basis="resolve remaining source-supported obstruction",
    )
    return bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=reconciliation,
    )


def work_spec(candidate: dict) -> dict:
    return build_successor_work_spec(
        successor_candidate=candidate,
        evidence_refs=["fixture://reconciliation", "fixture://remaining-gap"],
        desired_consequence="The remaining source-supported obstruction is resolved.",
        relevance_question="Would this bounded pressure resolve the exact remaining obstruction?",
        pressure_id="P-SUCCESSOR-WORK-001",
        target_distinction_lhs="REMAINING_OBSTRUCTION",
        target_distinction_rhs="RESOLVED_OBSTRUCTION",
        selection_basis="Fresh reconciliation leaves one exact load-bearing gap.",
        expected_information_gain="Whether the remaining obstruction can be resolved without widening scope.",
        application_dependency="A qualified result must exist before any application.",
        priority_basis="BLOCKS_METABOLIC_CONTINUATION",
        load_bearing_effects=["BASIS", "OBSERVABILITY", "COORDINATION"],
        allowed_operations=["OBSERVE", "COMPARE", "PROPOSE"],
        prohibited_operations=["GRANT_AUTHORITY", "EXECUTE", "SELF_PROMOTE"],
        success_condition="One bounded result addresses the exact remaining obstruction.",
        failure_condition="The pressure widens beyond the exact remaining obstruction.",
        unresolved_condition="Evidence remains insufficient to resolve the obstruction.",
        max_rounds=1,
        max_branch_count=1,
        max_unresolved_children=0,
        application_required=True,
        target_surface="DISPOSABLE_FIXTURE",
        proposed_change="Apply one bounded candidate transformation to the remaining obstruction.",
        expected_effect="The remaining obstruction becomes independently observable as resolved or still present.",
        operating_change="The exact remaining load-bearing obstruction changes posture.",
    )


class SuccessorWorkUnitMaterializationV0Tests(unittest.TestCase):
    def test_exact_successor_and_spec_materialize_valid_unit(self):
        candidate = partial_successor()
        spec = work_spec(candidate)
        unit = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=spec,
        )
        bw.validate_workflow_unit(unit)
        self.assertEqual(
            unit["identity"]["work_item_id"],
            candidate["successor_id"],
        )
        self.assertEqual(
            unit["basis"]["statement"],
            candidate["next_pressure_basis"],
        )
        self.assertEqual(
            unit["materialization"]["work_spec_id"],
            spec["work_spec_id"],
        )

    def test_fixed_inputs_are_deterministic(self):
        candidate = partial_successor()
        spec = work_spec(candidate)
        one = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=spec,
        )
        two = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=spec,
        )
        self.assertEqual(one, two)
        self.assertEqual(one["integrity_sha256"], two["integrity_sha256"])

    def test_materialized_unit_is_not_qualified_admitted_authorized_or_executed(self):
        candidate = partial_successor()
        spec = work_spec(candidate)
        unit = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=spec,
        )
        self.assertEqual(unit["qualification"]["scientific_standing"], "NONE")
        self.assertEqual(unit["application"]["application_status"], "NOT_YET_ELIGIBLE")
        self.assertEqual(unit["materialization"]["work_admission_effect"], "NONE")
        self.assertEqual(unit["materialization"]["authority_effect"], "NONE")
        self.assertEqual(unit["materialization"]["execution_effect"], "NONE")
        self.assertEqual(
            unit["materialization"]["scientific_standing_effect"],
            "NONE",
        )

    def test_materialized_unit_preserves_pressure_admissibility_separation(self):
        candidate = partial_successor()
        spec = work_spec(candidate)
        unit = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=spec,
        )
        admissibility = bw.pressure_admissibility(unit)
        self.assertTrue(admissibility["admissible"])
        self.assertEqual(admissibility["work_admission_effect"], "NONE")
        self.assertEqual(admissibility["authority_effect"], "NONE")
        self.assertEqual(admissibility["execution_effect"], "NONE")

    def test_work_spec_bound_to_different_successor_is_rejected(self):
        candidate = partial_successor()
        spec = work_spec(candidate)

        altered = copy.deepcopy(candidate)
        altered["next_pressure_basis"] = "different remaining obstruction"
        altered["integrity_sha256"] = ""
        from src.coordination import workcycle_v0 as wc
        altered = wc.seal_object(altered)

        with self.assertRaisesRegex(
            SuccessorWorkUnitMaterializationError,
            "work_spec/successor integrity mismatch|work_spec/next-pressure basis mismatch",
        ):
            materialize_successor_work_unit(
                successor_candidate=altered,
                work_spec=spec,
            )

    def test_tampered_work_spec_is_rejected(self):
        candidate = partial_successor()
        spec = work_spec(candidate)
        tampered = copy.deepcopy(spec)
        tampered["proposed_change"] = "silently widened transformation"
        with self.assertRaisesRegex(
            SuccessorWorkUnitMaterializationError,
            "work_spec seal invalid",
        ):
            materialize_successor_work_unit(
                successor_candidate=candidate,
                work_spec=tampered,
            )

    def test_no_successor_projection_cannot_be_materialized(self):
        unit = unit_fixture()
        admissibility = bw.pressure_admissibility(unit)
        reconciliation = bw.basis_reconciliation(
            unit,
            disposition="SATISFIED",
            remaining_gap=None,
        )
        no_successor = bw.derive_successor_candidate(
            unit,
            admissibility=admissibility,
            reconciliation=reconciliation,
        )
        with self.assertRaises(SuccessorWorkUnitMaterializationError):
            build_successor_work_spec(
                successor_candidate=no_successor,
                evidence_refs=["fixture://none"],
                desired_consequence="none",
                relevance_question="none",
                pressure_id="P-NONE",
                target_distinction_lhs="A",
                target_distinction_rhs="B",
                selection_basis="none",
                expected_information_gain="none",
                application_dependency="none",
                priority_basis="none",
                load_bearing_effects=["BASIS"],
                allowed_operations=["OBSERVE"],
                prohibited_operations=["EXECUTE"],
                success_condition="none",
                failure_condition="none",
                unresolved_condition="none",
                max_rounds=1,
                max_branch_count=1,
                max_unresolved_children=0,
                application_required=True,
                target_surface="NONE",
                proposed_change="none",
                expected_effect="none",
                operating_change="none",
            )

    def test_changed_work_spec_changes_materialized_unit_not_successor(self):
        candidate = partial_successor()
        one_spec = work_spec(candidate)
        two_spec = build_successor_work_spec(
            successor_candidate=candidate,
            evidence_refs=["fixture://reconciliation", "fixture://remaining-gap"],
            desired_consequence="The remaining source-supported obstruction is resolved.",
            relevance_question="Would this bounded pressure resolve the exact remaining obstruction?",
            pressure_id="P-SUCCESSOR-WORK-002",
            target_distinction_lhs="REMAINING_OBSTRUCTION",
            target_distinction_rhs="RESOLVED_OBSTRUCTION",
            selection_basis="Fresh reconciliation leaves one exact load-bearing gap.",
            expected_information_gain="Whether the remaining obstruction can be resolved under an alternate bounded pressure.",
            application_dependency="A qualified result must exist before any application.",
            priority_basis="BLOCKS_METABOLIC_CONTINUATION",
            load_bearing_effects=["BASIS", "OBSERVABILITY"],
            allowed_operations=["OBSERVE", "COMPARE"],
            prohibited_operations=["GRANT_AUTHORITY", "EXECUTE"],
            success_condition="One alternate bounded result addresses the exact remaining obstruction.",
            failure_condition="The alternate pressure widens scope.",
            unresolved_condition="Evidence remains insufficient.",
            max_rounds=1,
            max_branch_count=1,
            max_unresolved_children=0,
            application_required=True,
            target_surface="DISPOSABLE_FIXTURE",
            proposed_change="Apply one alternate bounded candidate transformation.",
            expected_effect="The remaining obstruction changes posture.",
            operating_change="The exact remaining obstruction changes posture.",
        )
        one = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=one_spec,
        )
        two = materialize_successor_work_unit(
            successor_candidate=candidate,
            work_spec=two_spec,
        )
        self.assertEqual(
            one["materialization"]["source_successor_id"],
            two["materialization"]["source_successor_id"],
        )
        self.assertNotEqual(one_spec["work_spec_id"], two_spec["work_spec_id"])
        self.assertNotEqual(one["integrity_sha256"], two["integrity_sha256"])


if __name__ == "__main__":
    unittest.main()
