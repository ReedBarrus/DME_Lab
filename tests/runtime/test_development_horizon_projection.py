from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from src.cockpit.development_horizon_projection import derive_development_horizons
from tools.development_campaign_v0 import build_campaign, object_sha256, validate_campaign


ROOT = Path(__file__).resolve().parents[2]


class DevelopmentHorizonProjectionPressure(unittest.TestCase):
    def campaign(
        self,
        campaign_id: str,
        *,
        relations: list[str] | None = None,
        dependency_edges: list[dict[str, str]] | None = None,
    ) -> dict:
        relations = relations or ["R1"]
        return build_campaign({
            "campaign_id": campaign_id,
            "title": campaign_id,
            "basis_refs": ["git:H1"],
            "objective": f"Earn {campaign_id}.",
            "claim_ceiling": "Projection fixture only.",
            "target_objects": [f"OBJ-{campaign_id}"],
            "unresolved_relations": [
                {"relation_id": rid, "statement": f"{rid} remains unwarranted"}
                for rid in relations
            ],
            "pressure_points": [f"Pressure {campaign_id}."],
            "dependency_edges": dependency_edges or [],
            "proposal_allowance": {
                "max_candidates": 2,
                "max_model_calls": 0,
                "allowed_resource_classes": ["DETERMINISTIC"],
            },
            "completion_criteria": ["Explicit standing exists."],
            "stop_conditions": ["Basis unreconstructable."],
            "explicit_non_authorizations": ["NO_PRIORITY"],
        })

    def runtime(
        self,
        campaigns: list[dict],
        *,
        standings: dict[tuple[str, str], str] | None = None,
        requests: list[dict] | None = None,
        current_selection: list[dict] | None = None,
        prep_receipts: list[dict] | None = None,
        assignment_events: list[dict] | None = None,
        satisfactions: list[dict] | None = None,
        bells: list[dict] | None = None,
        opportunities: list[dict] | None = None,
        reentry_receipts: list[dict] | None = None,
    ) -> dict:
        standings = standings or {}
        frontier = []
        for campaign in campaigns:
            for relation in campaign["unresolved_relations"]:
                key = (campaign["campaign_id"], relation["relation_id"])
                frontier.append({
                    "campaign_id": campaign["campaign_id"],
                    "relation_id": relation["relation_id"],
                    "standing": standings.get(key, "OPEN"),
                    "adjudication_ref": None,
                    "basis_ref": None,
                })
        return {
            "campaigns": [
                {
                    "campaign_id": campaign["campaign_id"],
                    "campaign_sha256": object_sha256(campaign),
                    "campaign_json": campaign,
                }
                for campaign in campaigns
            ],
            "frontier": frontier,
            "requests": [{"request_json": item} for item in (requests or [])],
            "current_selection": current_selection or [],
            "preparation_receipts": [
                {"receipt_json": item} for item in (prep_receipts or [])
            ],
            "assignment_history": [
                {"event_json": item} for item in (assignment_events or [])
            ],
            "assignment_satisfactions": [
                {"satisfaction_json": item} for item in (satisfactions or [])
            ],
            "manual_bells": [{"bell_json": item} for item in (bells or [])],
            "reentry_opportunities": [
                {"opportunity_json": item} for item in (opportunities or [])
            ],
            "reentry_receipts": [
                {"receipt_json": item} for item in (reentry_receipts or [])
            ],
        }

    def one(self, projection: dict, campaign_id: str) -> dict:
        return next(
            item for item in projection["horizons"]
            if item["campaign_id"] == campaign_id
        )

    def test_h1_open_idle_campaign_is_ready_for_pressure(self) -> None:
        c = self.campaign("H1")
        projection = derive_development_horizons(self.runtime([c]))
        item = self.one(projection, "H1")
        self.assertEqual(item["horizon_state"], "READY_FOR_PRESSURE")
        self.assertEqual(item["blocked_by"], [])
        self.assertEqual(item["priority_effect"], "NONE")

    def test_h2_current_work_activity_is_active_without_priority(self) -> None:
        c = self.campaign("H2")
        request = {
            "campaign_id": "H2",
            "request_id": "E-H2",
        }
        selection = {
            "campaign_id": "H2",
            "request_id": "E-H2",
            "request_sha256": "a" * 64,
        }
        assignment = {
            "campaign_id": "H2",
            "assignment_id": "A-H2",
            "assignment_kind": "ASSIGNED",
            "request_id": "E-H2",
            "request_sha256": "a" * 64,
            "seat_id": "MAYA",
            "preparation_kind": "RESOLVE_REFS",
        }
        projection = derive_development_horizons(
            self.runtime(
                [c],
                requests=[request],
                current_selection=[selection],
                assignment_events=[assignment],
            )
        )
        item = self.one(projection, "H2")
        self.assertEqual(item["horizon_state"], "ACTIVE")
        self.assertEqual(item["activity"]["candidate_requests"], 1)
        self.assertEqual(item["activity"]["current_selections"], 1)
        self.assertEqual(item["activity"]["current_assignments"], 1)
        self.assertEqual(projection["priority_effect"], "NONE")

    def test_h3_prep_or_reentry_evidence_is_evidence_accumulating(self) -> None:
        c = self.campaign("H3")
        prep = {
            "campaign_id": "H3",
            "request_id": "E-H3",
            "preparation_id": "P-H3",
        }
        opportunity = {
            "campaign_id": "H3",
            "opportunity_id": "W-H3",
        }
        receipt = {
            "opportunity_id": "W-H3",
            "receipt_id": "BRR-H3",
        }
        projection = derive_development_horizons(
            self.runtime(
                [c],
                prep_receipts=[prep],
                opportunities=[opportunity],
                reentry_receipts=[receipt],
            )
        )
        item = self.one(projection, "H3")
        self.assertEqual(item["horizon_state"], "EVIDENCE_ACCUMULATING")
        self.assertEqual(item["activity"]["preparation_receipts"], 1)
        self.assertEqual(item["activity"]["reentry_receipts"], 1)

    def test_h4_all_relations_earned_means_earned(self) -> None:
        c = self.campaign("H4", relations=["R1", "R2"])
        projection = derive_development_horizons(
            self.runtime(
                [c],
                standings={
                    ("H4", "R1"): "EARNED",
                    ("H4", "R2"): "EARNED",
                },
            )
        )
        item = self.one(projection, "H4")
        self.assertEqual(item["horizon_state"], "EARNED")
        self.assertEqual(item["open_relations"], [])
        self.assertEqual(item["earned_relations"], ["R1", "R2"])

    def test_h5_resolved_with_fracture_means_fractured(self) -> None:
        c = self.campaign("H5", relations=["R1", "R2"])
        projection = derive_development_horizons(
            self.runtime(
                [c],
                standings={
                    ("H5", "R1"): "EARNED",
                    ("H5", "R2"): "FRACTURED",
                },
            )
        )
        item = self.one(projection, "H5")
        self.assertEqual(item["horizon_state"], "FRACTURED")
        self.assertEqual(item["fractured_relations"], ["R2"])

    def test_h6_known_cross_campaign_dependency_blocks_target(self) -> None:
        sanity = self.campaign("RUNTIME_SANITY_GATE_001")
        wake = self.campaign(
            "WAKE_POLICY_001",
            dependency_edges=[
                {
                    "from": "RUNTIME_SANITY_GATE_001",
                    "to": "WAKE_POLICY_001",
                }
            ],
        )
        projection = derive_development_horizons(self.runtime([sanity, wake]))
        item = self.one(projection, "WAKE_POLICY_001")
        self.assertEqual(item["horizon_state"], "BLOCKED")
        self.assertEqual(
            [b["campaign_id"] for b in item["blocked_by"]],
            ["RUNTIME_SANITY_GATE_001"],
        )
        sanity_item = self.one(projection, "RUNTIME_SANITY_GATE_001")
        self.assertEqual(sanity_item["unlocks"], ["WAKE_POLICY_001"])

    def test_h7_earned_blocker_unlocks_target_without_priority(self) -> None:
        sanity = self.campaign("RUNTIME_SANITY_GATE_001")
        wake = self.campaign(
            "WAKE_POLICY_001",
            dependency_edges=[
                {
                    "from": "RUNTIME_SANITY_GATE_001",
                    "to": "WAKE_POLICY_001",
                }
            ],
        )
        projection = derive_development_horizons(
            self.runtime(
                [sanity, wake],
                standings={
                    ("RUNTIME_SANITY_GATE_001", "R1"): "EARNED",
                },
            )
        )
        wake_item = self.one(projection, "WAKE_POLICY_001")
        self.assertEqual(wake_item["horizon_state"], "READY_FOR_PRESSURE")
        self.assertEqual(wake_item["blocked_by"], [])
        self.assertEqual(wake_item["priority_effect"], "NONE")

    def test_h8_unknown_dependency_endpoint_remains_local_not_blocker(self) -> None:
        c = self.campaign(
            "H8",
            dependency_edges=[
                {"from": "INTERNAL_A", "to": "INTERNAL_B"}
            ],
        )
        projection = derive_development_horizons(self.runtime([c]))
        item = self.one(projection, "H8")
        self.assertEqual(item["horizon_state"], "READY_FOR_PRESSURE")
        self.assertEqual(item["blocked_by"], [])
        self.assertEqual(
            item["local_dependency_edges"],
            [{"from": "INTERNAL_A", "to": "INTERNAL_B"}],
        )
        self.assertEqual(projection["cross_campaign_dependencies"], [])

    def test_h9_projection_does_not_mutate_inputs(self) -> None:
        c = self.campaign("H9")
        state = self.runtime([c])
        before = copy.deepcopy(state)
        projection = derive_development_horizons(state)
        self.assertEqual(state, before)
        self.assertEqual(projection["authority_effect"], "NONE")
        self.assertEqual(projection["execution_effect"], "NONE")
        self.assertEqual(projection["standing_effect"], "NONE")

    def test_h10_multiple_unblocked_horizons_coexist_without_order(self) -> None:
        ready = self.campaign("H10-READY")
        active = self.campaign("H10-ACTIVE")
        projection = derive_development_horizons(
            self.runtime(
                [ready, active],
                requests=[
                    {"campaign_id": "H10-ACTIVE", "request_id": "E10"}
                ],
            )
        )
        states = {
            item["campaign_id"]: item["horizon_state"]
            for item in projection["horizons"]
        }
        self.assertEqual(states["H10-READY"], "READY_FOR_PRESSURE")
        self.assertEqual(states["H10-ACTIVE"], "ACTIVE")
        self.assertEqual(projection["priority_effect"], "NONE")

    def test_current_operating_horizon_candidate_files_validate(self) -> None:
        for name in (
            "COCKPIT_OPERATING_SPACE_001.json",
            "RUNTIME_SANITY_GATE_001.json",
            "WAKE_POLICY_001.json",
        ):
            campaign = json.loads(
                (
                    ROOT
                    / "docs"
                    / "campaigns"
                    / "candidates"
                    / name
                ).read_text(encoding="utf-8")
            )
            validate_campaign(campaign)


if __name__ == "__main__":
    unittest.main()
