from __future__ import annotations

import unittest

from src.cockpit.pressure_justification import (
    build_basis_record,
    build_pressure_justification,
)


def workcycle_fixture(next_pressure: str = "T7_PRESSURE") -> dict:
    return {
        "campaign_id": "WORKCYCLE_STABILIZATION_001",
        "active_horizon": "FIRST_PERMANENT_WORKLOAD_COMPRESSION_HISTORY_CONSERVATION",
        "next_pressure": next_pressure,
        "current_unresolved": [],
        "campaign_progress": {
            "T2": {"posture": "BOUNDED_PASS"},
            "T6": {"posture": "BOUNDED_PASS"},
            "T7": {"posture": "IMPLEMENTED_UNPRESSURED"},
        },
    }


def horizon_fixture(disposition: str = "HORIZON_MATCHED") -> dict:
    return {
        "disposition": disposition,
        "history_posture": "SUPPORTED",
        "currentness_posture": "SUPPORTED",
        "upcoming_work_posture": "SUPPORTED",
        "primary_horizon": {
            "family": "H_observe",
            "subject": "operator currentness and control truth",
            "boundary_condition": "operator projection is implemented but not independently pressured",
        },
        "distinctions_applied": [
            "LATEST_COMPLETED != ACTIVE",
            "PARTIAL_ELIGIBILITY != REAL_ELIGIBILITY",
        ],
        "seven_surfaces": {
            "identity_address": {"posture": "SUPPORTED"},
            "mechanical": {"posture": "SUPPORTED"},
        },
        "six_load_dimensions": {
            "functional": {
                "bearing_object": "T7_PRESSURE",
                "direction": "INCREASING",
            },
            "coordination": {
                "bearing_object": "PARTIAL_COORDINATES_ONLY",
                "direction": "INCREASING",
            },
            "authority": {
                "bearing_object": "LOCAL_OPERATOR_CONTROL_ACTIVE",
                "direction": "STABLE",
            },
        },
    }


def qualification_fixture(
    bounded: list[str] | None = None,
    self_moving: list[str] | None = None,
) -> dict:
    return {
        "bounded_workcycle": {"blockers": list(bounded or [])},
        "self_moving_workcycle": {"blockers": list(self_moving or [])},
    }


class PressureJustificationTests(unittest.TestCase):
    def test_t7_blocker_justifies_t7_pressure(self):
        workcycle = workcycle_fixture()
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                bounded=["T7:IMPLEMENTED_UNPRESSURED", "TEMPORAL_HORIZON:UNFROZEN"],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(result["proposed_pressure"], "T7_PRESSURE")
        self.assertEqual(result["next_work_posture"], "RESOLVE_LOAD_BEARING_GAP")
        self.assertEqual(result["if_nothing_changes"], "DO_NOT_RUN")
        self.assertEqual(result["work_admission_effect"], "NONE")

    def test_unresolved_horizon_holds_without_manufacturing_work(self):
        result = build_pressure_justification(
            workcycle=workcycle_fixture(),
            horizon_closure=horizon_fixture("HORIZON_UNRESOLVED"),
            qualification=qualification_fixture(bounded=["T7:IMPLEMENTED_UNPRESSURED"]),
        )
        self.assertEqual(result["pressure_posture"], "UNRESOLVED")
        self.assertEqual(result["next_work_posture"], "HOLD_NO_JUSTIFIED_WORK")

    def test_temporal_horizon_debt_preempts_auto_continuation(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                bounded=["TEMPORAL_HORIZON:UNFROZEN"],
                self_moving=[
                    "TEMPORAL_HORIZON:UNFROZEN",
                    "ONE_SUCCESSOR:UNFROZEN",
                    "ATOMIC_ADMISSION:UNFROZEN",
                ],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(result["proposed_pressure"], "TEMPORAL_HORIZON_ADJUDICATION")
        self.assertNotEqual(result["proposed_pressure"], "AUTO_CONTINUATION_PRESSURE")

    def test_no_blockers_returns_no_justified_work(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(),
        )
        self.assertEqual(result["pressure_posture"], "ALREADY_RESOLVED")
        self.assertIsNone(result["proposed_pressure"])
        self.assertEqual(result["next_work_posture"], "HOLD_NO_JUSTIFIED_WORK")

    def test_authority_binding_blocker_selects_authority_pressure(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                self_moving=[
                    "AUTHORITY_BINDING:UNFROZEN",
                    "REPEATED_METABOLIC_LOOP:UNFROZEN",
                ],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(result["proposed_pressure"], "AUTHORITY_BINDING_PRESSURE")

    def test_successor_identity_is_selected_after_authority_binding(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                self_moving=[
                    "SUCCESSOR_IDENTITY:UNFROZEN",
                    "BASIS_RECONCILIATION:UNFROZEN",
                    "VERIFIED_AUTHORITY_ATOMIC_ADMISSION:UNFROZEN",
                    "REPEATED_METABOLIC_LOOP:UNFROZEN",
                ],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(result["proposed_pressure"], "SUCCESSOR_IDENTITY_PRESSURE")

    def test_basis_reconciliation_is_selected_after_successor_identity(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                self_moving=[
                    "BASIS_RECONCILIATION:UNFROZEN",
                    "VERIFIED_AUTHORITY_ATOMIC_ADMISSION:UNFROZEN",
                    "REPEATED_METABOLIC_LOOP:UNFROZEN",
                ],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(result["proposed_pressure"], "BASIS_RECONCILIATION_PRESSURE")

    def test_verified_authority_atomic_admission_is_selected_before_loop(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                self_moving=[
                    "VERIFIED_AUTHORITY_ATOMIC_ADMISSION:UNFROZEN",
                    "REPEATED_METABOLIC_LOOP:UNFROZEN",
                ],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(
            result["proposed_pressure"],
            "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_PRESSURE",
        )


    def test_admitted_authority_consumption_is_selected_before_loop(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                self_moving=[
                    "ADMITTED_AUTHORITY_CONSUMPTION:UNFROZEN",
                    "REPEATED_METABOLIC_LOOP:UNFROZEN",
                ],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(
            result["proposed_pressure"],
            "ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE",
        )


    def test_repeated_metabolic_loop_is_selected_after_authority_binding(self):
        workcycle = workcycle_fixture("AUTO_CONTINUATION_PRESSURE")
        workcycle["campaign_progress"]["T7"] = {"posture": "BOUNDED_PASS"}
        result = build_pressure_justification(
            workcycle=workcycle,
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(
                self_moving=["REPEATED_METABOLIC_LOOP:UNFROZEN"],
            ),
        )
        self.assertEqual(result["pressure_posture"], "JUSTIFIED")
        self.assertEqual(
            result["proposed_pressure"],
            "REPEATED_METABOLIC_LOOP_PRESSURE",
        )

    def test_basis_identity_is_deterministic(self):
        one = build_basis_record(
            workcycle=workcycle_fixture(),
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(bounded=["T7:IMPLEMENTED_UNPRESSURED"]),
        )
        two = build_basis_record(
            workcycle=workcycle_fixture(),
            horizon_closure=horizon_fixture(),
            qualification=qualification_fixture(bounded=["T7:IMPLEMENTED_UNPRESSURED"]),
        )
        self.assertEqual(one["basis_id"], two["basis_id"])
        self.assertEqual(one["authority_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
