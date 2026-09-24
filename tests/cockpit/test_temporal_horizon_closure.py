from __future__ import annotations

import unittest

from src.cockpit.temporal_horizon_closure import derive_temporal_horizon_closure


def temporal_fixture() -> dict:
    return {
        "source_commit": "a" * 40,
        "transitions": [
            {
                "transition_id": "T1",
                "from_commit_sha": "0" * 40,
                "to_commit_sha": "a" * 40,
                "event_count": 1,
                "source_handles": [{"handle_kind": "GIT_COMMIT", "commit_sha": "a" * 40}],
                "events": [
                    {
                        "classifications": ["PERSISTED", "CONTENT_CHANGED"],
                    }
                ],
            }
        ],
    }


def workcycle_fixture() -> dict:
    return {
        "campaign_id": "WORKCYCLE_STABILIZATION_001",
        "active_horizon": "FIRST_PERMANENT_WORKLOAD_COMPRESSION_HISTORY_CONSERVATION",
        "next_pressure": "T2_ADJUDICATION",
        "active_work_item": None,
        "latest_completed_work_item": "W1",
        "next_eligible_work_item": None,
        "current_unresolved": [],
        "projection_errors": [],
        "campaign_progress": {"T2": {"posture": "EXERCISED_UNADJUDICATED"}},
        "eligibility": {
            "posture": "PARTIAL_COORDINATES_ONLY",
            "eligible": None,
        },
        "operative_control": {
            "status": "LOCAL_OPERATOR_CONTROL_ACTIVE",
            "workflow_enabled": False,
        },
        "seat_ecology": {
            "durable_seat_count": 1,
            "occupied_seat_count": 0,
        },
        "latest_consequence": {
            "evidence_handles": ["candidate.md", "report.md"],
        },
        "latest_consequence_evaluation": {
            "disposition": "CONSEQUENCE_MATCHED",
        },
    }


class TemporalHorizonClosureTests(unittest.TestCase):
    def test_history_current_and_upcoming_match_one_bounded_horizon(self):
        result = derive_temporal_horizon_closure(
            temporal_lineage=temporal_fixture(),
            workcycle=workcycle_fixture(),
            development_horizons={"state_counts": {"READY_FOR_PRESSURE": 1}},
        )
        self.assertEqual(result["disposition"], "HORIZON_MATCHED")
        self.assertEqual(result["primary_horizon"]["family"], "H_reconstruct")
        self.assertEqual(
            result["primary_horizon"]["subject"],
            "campaign-to-work decomposition lineage",
        )
        self.assertEqual(result["history"]["causation_claim"], "NONE")
        self.assertEqual(
            result["seven_surfaces"]["identity_address"]["posture"],
            "SUPPORTED",
        )
        self.assertEqual(
            result["next_work_candidate"]["candidate_posture"],
            "PROPOSED_NOT_ADMITTED",
        )
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")

    def test_missing_history_holds_horizon(self):
        result = derive_temporal_horizon_closure(
            temporal_lineage={},
            workcycle=workcycle_fixture(),
        )
        self.assertEqual(result["disposition"], "HORIZON_UNRESOLVED")
        self.assertEqual(result["history_posture"], "UNRESOLVED")
        self.assertEqual(
            result["seven_surfaces"]["mechanical"]["posture"],
            "UNRESOLVED",
        )
        self.assertEqual(
            result["next_work_candidate"]["candidate_posture"],
            "HELD_UNRESOLVED_HORIZON",
        )

    def test_projection_error_holds_currentness(self):
        workcycle = workcycle_fixture()
        workcycle["projection_errors"] = ["bad seal"]
        result = derive_temporal_horizon_closure(
            temporal_lineage=temporal_fixture(),
            workcycle=workcycle,
        )
        self.assertEqual(result["disposition"], "HORIZON_UNRESOLVED")
        self.assertEqual(result["currentness_posture"], "UNRESOLVED")

    def test_missing_declared_upcoming_pressure_holds_horizon(self):
        workcycle = workcycle_fixture()
        workcycle["next_pressure"] = None
        result = derive_temporal_horizon_closure(
            temporal_lineage=temporal_fixture(),
            workcycle=workcycle,
        )
        self.assertEqual(result["disposition"], "HORIZON_UNRESOLVED")
        self.assertEqual(result["upcoming_work_posture"], "UNRESOLVED")

    def test_history_never_becomes_semantic_causation(self):
        result = derive_temporal_horizon_closure(
            temporal_lineage=temporal_fixture(),
            workcycle=workcycle_fixture(),
        )
        self.assertIn("TEMPORAL_SUCCESSION != CAUSATION", result["distinctions_applied"])
        self.assertEqual(result["history"]["causation_claim"], "NONE")


if __name__ == "__main__":
    unittest.main()
