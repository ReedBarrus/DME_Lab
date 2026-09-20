from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from tools.development_campaign_v0 import (
    CampaignStore,
    DevelopmentCampaignError,
    build_campaign,
    object_sha256,
)


class DevelopmentCampaignPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "campaign.sqlite3"
        self.store = CampaignStore(self.db)
        self.spec = {
            "campaign_id": "LOCAL_COGNITION_001",
            "title": "Local cognition developmental horizon",
            "basis_refs": [
                "git:0b35fa02e475ba3729d2b8e39ab0e63cce5cdd91",
                "qualification:LOCAL_SEMANTIC_OPERATOR_001",
            ],
            "objective": (
                "Qualify local semantic cognition without granting model "
                "state-transition or execution authority."
            ),
            "claim_ceiling": (
                "Only bounded proposal-generation, resource-legibility, "
                "lease, and selection relations may advance."
            ),
            "target_objects": [
                "LOCAL_SEMANTIC_OPERATOR_001",
                "MODEL_RESOURCE_REGISTRY_001",
                "MODEL_LEASE_001",
            ],
            "unresolved_relations": [
                {
                    "relation_id": "R1",
                    "statement": "MODEL_AVAILABLE != MODEL_ELIGIBLE",
                },
                {
                    "relation_id": "R2",
                    "statement": "MODEL_SELECTED != MODEL_LEASED",
                },
                {
                    "relation_id": "R3",
                    "statement": "VALID_PROPOSAL != STATE_TRANSITION",
                },
            ],
            "pressure_points": [
                "Pressure resource availability versus request eligibility.",
                "Pressure selection versus exclusive lease acquisition.",
                "Pressure valid semantic proposal versus state mutation.",
            ],
            "dependency_edges": [
                {"from": "MODEL_RESOURCE_REGISTRY_001", "to": "MODEL_LEASE_001"},
            ],
            "proposal_allowance": {
                "max_candidates": 2,
                "max_model_calls": 1,
                "allowed_resource_classes": ["DETERMINISTIC", "LOCAL_CHEAP"],
            },
            "completion_criteria": [
                "All retained unresolved relations receive explicit external standing.",
            ],
            "stop_conditions": [
                "Required basis cannot be reconstructed.",
                "Proposed work requires execution authority not represented by the request.",
            ],
            "explicit_non_authorizations": [
                "NO_AUTOMATIC_EXECUTION",
                "NO_AUTOMATIC_AUTHORIZATION",
                "NO_AUTOMATIC_SCHEDULING",
                "NO_SCIENTIFIC_PROMOTION",
            ],
        }
        self.campaign = build_campaign(self.spec)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def request(
        self,
        *,
        request_id: str,
        seat_id: str,
        relation_id: str = "R1",
        target: str = "MODEL_RESOURCE_REGISTRY_001",
    ) -> dict:
        relation = {
            item["relation_id"]: item["statement"]
            for item in self.campaign["unresolved_relations"]
        }[relation_id]
        return {
            "schema": "execution_envelope_request_v0",
            "request_id": request_id,
            "campaign_id": self.campaign["campaign_id"],
            "campaign_sha256": object_sha256(self.campaign),
            "seat_id": seat_id,
            "object_under_pressure": target,
            "unresolved_relation_id": relation_id,
            "unresolved_relation": relation,
            "smallest_proposed_intervention": (
                "Run one isolated pressure that independently varies the relation."
            ),
            "expected_observable": "A bounded observable discriminating the relation.",
            "allowed_effect_surface": [],
            "forbidden_effects": list(self.campaign["explicit_non_authorizations"]),
            "required_authority": "EXECUTIVE_AUTHORIZATION_REQUIRED",
            "resource_cost": {
                "resource_class": "DETERMINISTIC",
                "model_calls": 0,
                "notes": "Envelope proposal only.",
            },
            "expected_information_gain": "Discriminate one unresolved relation.",
            "stop_conditions": list(self.campaign["stop_conditions"]),
            "packet_status": "CANDIDATE_REQUEST",
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
        }

    def standing_update(self, relation_id: str, standing: str) -> dict:
        return {
            "schema": "campaign_standing_update_v0",
            "campaign_id": self.campaign["campaign_id"],
            "relation_id": relation_id,
            "standing": standing,
            "adjudication_ref": f"decision://{relation_id}/{standing}",
            "basis_ref": "git:adjudicated-basis",
        }

    def post(self) -> None:
        self.store.post_campaign(self.campaign)

    def test_c1_build_and_post_have_no_authority_effect(self) -> None:
        self.assertEqual(self.campaign["status"], "CANDIDATE")
        self.assertEqual(self.campaign["authority_effect"], "NONE")
        self.assertEqual(self.campaign["execution_effect"], "NONE")
        self.assertEqual(self.campaign["adoption_effect"], "NONE")

        first = self.store.post_campaign(self.campaign)
        second = self.store.post_campaign(self.campaign)
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(first["authority_effect"], "NONE")
        self.assertEqual(first["execution_effect"], "NONE")

    def test_c2_multiple_seats_can_lodge_different_requests_same_relation(self) -> None:
        self.post()
        a = self.request(request_id="E-LABBOIB-1", seat_id="LABBOIB")
        b = self.request(request_id="E-COMMANDER-1", seat_id="COMMANDER")

        self.store.lodge_request(a)
        self.store.lodge_request(b)

        snap = self.store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )
        seats = {item["seat_id"] for item in snap["candidate_requests"]}
        relations = {item["relation_id"] for item in snap["candidate_requests"]}
        self.assertEqual(seats, {"LABBOIB", "COMMANDER"})
        self.assertEqual(relations, {"R1"})
        self.assertEqual(snap["authority_effect"], "NONE")

    def test_c3_draft_allowance_caps_candidate_generation(self) -> None:
        self.post()
        drafted = self.store.draft_requests(
            self.campaign["campaign_id"],
            "LABBOIB",
        )
        self.assertEqual(len(drafted), 2)
        self.assertTrue(all(r["packet_status"] == "CANDIDATE_REQUEST" for r in drafted))
        self.assertTrue(all(r["authorization_effect"] == "NONE" for r in drafted))
        self.assertTrue(all(r["execution_effect"] == "NONE" for r in drafted))
        self.assertTrue(all(r["resource_cost"]["model_calls"] == 0 for r in drafted))

        replay = self.store.draft_requests(
            self.campaign["campaign_id"],
            "LABBOIB",
        )
        self.assertEqual(
            [r["request_id"] for r in replay],
            [r["request_id"] for r in drafted],
        )

    def test_c4_request_is_not_execution_packet(self) -> None:
        self.post()
        request = self.request(request_id="E-C4", seat_id="LABBOIB")
        result = self.store.lodge_request(request)

        self.assertEqual(request["schema"], "execution_envelope_request_v0")
        self.assertEqual(request["packet_status"], "CANDIDATE_REQUEST")
        self.assertEqual(request["authorization_effect"], "NONE")
        self.assertEqual(request["execution_effect"], "NONE")
        self.assertNotIn("AUTHORIZATION", request)
        self.assertNotIn("AUTHORIZED_OPERATIONS", request)
        self.assertEqual(result["authorization_effect"], "NONE")

    def test_c5_execution_receipts_do_not_close_campaign_relations(self) -> None:
        self.post()
        drafted = self.store.draft_requests(
            self.campaign["campaign_id"],
            "WORKSHOP",
        )
        for index, request in enumerate(drafted):
            self.store.record_execution_receipt(
                receipt_id=f"RCPT-{index}",
                request_id=request["request_id"],
                execution_status="COMPLETED",
            )

        snap = self.store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )
        self.assertEqual(snap["execution_receipt_count"], len(drafted))
        self.assertEqual(snap["frontier_status"], "OPEN")
        self.assertEqual(set(snap["open_relations"]), {"R1", "R2", "R3"})

    def test_c6_fracture_can_make_planned_request_historical_without_execution(self) -> None:
        self.post()
        request = self.request(
            request_id="E-C6",
            seat_id="COMMANDER",
            relation_id="R1",
        )
        self.store.lodge_request(request)
        self.store.record_standing_update(self.standing_update("R1", "FRACTURED"))

        snap = self.store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )
        self.assertNotIn("R1", snap["open_relations"])
        self.assertEqual(snap["standing"]["R1"]["standing"], "FRACTURED")
        self.assertEqual(snap["execution_receipt_count"], 0)
        self.assertEqual(
            [item["request_id"] for item in snap["candidate_requests"]],
            ["E-C6"],
        )

    def test_c7_campaign_frontier_resolves_from_standing_not_task_completion(self) -> None:
        self.post()
        self.store.lodge_request(
            self.request(request_id="E-C7", seat_id="LABBOIB", relation_id="R1")
        )

        self.store.record_standing_update(self.standing_update("R1", "EARNED"))
        self.store.record_standing_update(self.standing_update("R2", "FRACTURED"))
        self.store.record_standing_update(self.standing_update("R3", "EARNED"))

        snap = self.store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )
        self.assertEqual(snap["frontier_status"], "RESOLVED")
        self.assertEqual(snap["open_relations"], [])
        self.assertEqual(snap["execution_receipt_count"], 0)
        self.assertEqual(len(snap["candidate_requests"]), 1)

    def test_c8_basis_drift_marks_projection_stale_without_rewriting_campaign(self) -> None:
        self.post()
        original_sha = object_sha256(self.campaign)
        before = copy.deepcopy(self.campaign)

        snap = self.store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=["git:different-world"],
        )

        self.assertEqual(snap["basis_status"], "STALE")
        self.assertEqual(snap["campaign_sha256"], original_sha)
        self.assertEqual(self.store.get_campaign(self.campaign["campaign_id"]), before)

    def test_c9_request_identity_is_idempotent_and_conflict_legible(self) -> None:
        self.post()
        request = self.request(request_id="E-C9", seat_id="LABBOIB")

        first = self.store.lodge_request(request)
        second = self.store.lodge_request(request)
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])

        changed = copy.deepcopy(request)
        changed["expected_information_gain"] = "Different bytes under same ID."
        with self.assertRaises(DevelopmentCampaignError):
            self.store.lodge_request(changed)


if __name__ == "__main__":
    unittest.main()
