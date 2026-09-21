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
from tools.envelope_selection_v0 import (
    EnvelopeSelectionError,
    RELEASE,
    SELECT,
    SelectionStore,
    build_selection_event,
)


class EnvelopeSelectionPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.campaign_store = CampaignStore(root / "campaign.sqlite3")
        self.selection_store = SelectionStore(
            self.campaign_store,
            root / "selection.sqlite3",
        )

        self.spec = {
            "campaign_id": "SELECTION_FIXTURE_001",
            "title": "Envelope selection fixture",
            "basis_refs": ["git:B1", "standing:S1"],
            "objective": "Pressure human attention without consequence authority.",
            "claim_ceiling": "Selection may route attention only.",
            "target_objects": ["OBJ_A", "OBJ_B", "OBJ_C"],
            "unresolved_relations": [
                {"relation_id": "R1", "statement": "A != B"},
                {"relation_id": "R2", "statement": "B != C"},
                {"relation_id": "R3", "statement": "C != D"},
            ],
            "pressure_points": [
                "Pressure R1.",
                "Pressure R2.",
                "Pressure R3.",
            ],
            "dependency_edges": [],
            "proposal_allowance": {
                "max_candidates": 3,
                "max_model_calls": 0,
                "allowed_resource_classes": ["DETERMINISTIC"],
            },
            "completion_criteria": ["All relations receive explicit standing."],
            "stop_conditions": ["Basis becomes unreconstructable."],
            "explicit_non_authorizations": [
                "NO_EXECUTION",
                "NO_STANDING_CHANGE",
            ],
        }
        self.campaign = build_campaign(self.spec)
        self.campaign_store.post_campaign(self.campaign)

        self.requests = {}
        for index, relation in enumerate(self.campaign["unresolved_relations"], start=1):
            request = {
                "schema": "execution_envelope_request_v0",
                "request_id": f"E{index}",
                "campaign_id": self.campaign["campaign_id"],
                "campaign_sha256": object_sha256(self.campaign),
                "seat_id": "LABBOIB",
                "object_under_pressure": self.campaign["target_objects"][index - 1],
                "unresolved_relation_id": relation["relation_id"],
                "unresolved_relation": relation["statement"],
                "smallest_proposed_intervention": f"Pressure {relation['relation_id']}.",
                "expected_observable": "A bounded discriminating observation.",
                "allowed_effect_surface": [],
                "forbidden_effects": list(self.campaign["explicit_non_authorizations"]),
                "required_authority": "EXECUTIVE_AUTHORIZATION_REQUIRED",
                "resource_cost": {
                    "resource_class": "DETERMINISTIC",
                    "model_calls": 0,
                    "notes": "Selection fixture request.",
                },
                "expected_information_gain": "Distinguish one relation.",
                "stop_conditions": list(self.campaign["stop_conditions"]),
                "packet_status": "CANDIDATE_REQUEST",
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
            self.campaign_store.lodge_request(request)
            self.requests[request["request_id"]] = request

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def event(
        self,
        request_id: str,
        selection_id: str,
        kind: str = SELECT,
        basis_refs: list[str] | None = None,
    ) -> dict:
        return build_selection_event(
            campaign=self.campaign,
            request=self.requests[request_id],
            selection_id=selection_id,
            basis_refs=basis_refs or self.campaign["basis_refs"],
            kind=kind,
            reason="fixture selection",
        )

    def project(self, basis_refs: list[str] | None = None) -> dict:
        return self.selection_store.projection(
            self.campaign["campaign_id"],
            basis_refs or self.campaign["basis_refs"],
        )

    def test_s1_basic_selection_changes_only_current_attention_projection(self) -> None:
        self.selection_store.append(self.event("E2", "S1"))
        projection = self.project()

        self.assertEqual(projection["selection_count"], 1)
        self.assertEqual(
            [item["request_id"] for item in projection["current_selection_set"]],
            ["E2"],
        )
        selected = projection["current_selection_set"][0]
        self.assertEqual(selected["attention"], "SELECTED")
        self.assertEqual(selected["authorization_effect"], "NONE")
        self.assertEqual(selected["execution_effect"], "NONE")
        self.assertEqual(selected["standing_effect"], "NONE")
        self.assertEqual(len(self.selection_store.history(self.campaign["campaign_id"])), 1)

    def test_s2_basis_drift_preserves_selection_and_blocks_preparation(self) -> None:
        event = self.event("E2", "S2", basis_refs=self.campaign["basis_refs"])
        before = copy.deepcopy(event)
        self.selection_store.append(event)

        projection = self.project(["git:B2", "standing:S1"])
        selected = projection["current_selection_set"][0]

        self.assertEqual(event, before)
        self.assertEqual(selected["request_id"], "E2")
        self.assertEqual(selected["request_applicability"], "STALE")
        self.assertEqual(
            selected["preparation"],
            "BLOCKED_PENDING_REVALIDATION",
        )
        self.assertEqual(self.selection_store.history(self.campaign["campaign_id"])[0]["request_id"], "E2")

    def test_s3_exact_selection_replay_is_idempotent(self) -> None:
        event = self.event("E2", "S3")
        first = self.selection_store.append(event)
        second = self.selection_store.append(event)

        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(len(self.selection_store.history(self.campaign["campaign_id"])), 1)

    def test_s4_attention_moves_without_rewriting_history(self) -> None:
        self.selection_store.append(self.event("E2", "S4-A"))
        self.selection_store.append(self.event("E2", "S4-B", kind=RELEASE))
        self.selection_store.append(self.event("E3", "S4-C"))

        history = self.selection_store.history(self.campaign["campaign_id"])
        self.assertEqual(
            [event["selection_kind"] for event in history],
            [SELECT, RELEASE, SELECT],
        )
        self.assertEqual(
            [item["request_id"] for item in self.project()["current_selection_set"]],
            ["E3"],
        )

    def test_s5_selected_preparation_eligibility_does_not_grant_authority(self) -> None:
        self.selection_store.append(self.event("E2", "S5"))
        selected = self.project()["current_selection_set"][0]

        self.assertEqual(
            selected["preparation"],
            "ELIGIBLE_FOR_PACKET_PREPARATION",
        )
        self.assertEqual(selected["authorization_effect"], "NONE")
        self.assertEqual(selected["execution_effect"], "NONE")
        self.assertEqual(selected["standing_effect"], "NONE")

    def test_s6_fractured_relation_makes_selected_request_obsolete_not_erased(self) -> None:
        self.selection_store.append(self.event("E2", "S6"))
        self.campaign_store.record_standing_update({
            "schema": "campaign_standing_update_v0",
            "campaign_id": self.campaign["campaign_id"],
            "relation_id": "R2",
            "standing": "FRACTURED",
            "adjudication_ref": "decision://R2/fractured",
            "basis_ref": "git:B1",
        })

        selected = self.project()["current_selection_set"][0]
        self.assertEqual(selected["attention"], "SELECTED")
        self.assertEqual(
            selected["developmental_relevance"],
            "OBSOLETE_FRACTURED",
        )
        self.assertEqual(selected["preparation"], "BLOCKED_OBSOLETE")
        self.assertEqual(len(self.selection_store.history(self.campaign["campaign_id"])), 1)

    def test_s7_unselected_execution_does_not_fabricate_selection(self) -> None:
        self.campaign_store.record_execution_receipt(
            receipt_id="RCPT-E1",
            request_id="E1",
            execution_status="COMPLETED",
        )
        projection = self.project()
        campaign_snapshot = self.campaign_store.snapshot(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )

        self.assertEqual(campaign_snapshot["execution_receipt_count"], 1)
        self.assertEqual(projection["selection_count"], 0)
        self.assertEqual(self.selection_store.history(self.campaign["campaign_id"]), [])

    def test_s8_parallel_attention_is_a_set_not_priority(self) -> None:
        self.selection_store.append(self.event("E3", "S8-C"))
        self.selection_store.append(self.event("E1", "S8-A"))
        self.selection_store.append(self.event("E2", "S8-B"))

        projection = self.project()
        self.assertEqual(
            [item["request_id"] for item in projection["current_selection_set"]],
            ["E1", "E2", "E3"],
        )
        self.assertEqual(projection["priority_effect"], "NONE")
        self.assertTrue(
            all(
                item["priority_effect"] == "NONE"
                for item in projection["current_selection_set"]
            )
        )

    def test_s9_selection_rejects_changed_bytes_under_same_request_label(self) -> None:
        event = self.event("E2", "S9")
        event["request_sha256"] = "0" * 64

        with self.assertRaises(EnvelopeSelectionError):
            self.selection_store.append(event)

        self.assertEqual(self.selection_store.history(self.campaign["campaign_id"]), [])

    def test_s10_non_executive_cannot_mint_selection_event(self) -> None:
        with self.assertRaises(EnvelopeSelectionError):
            build_selection_event(
                campaign=self.campaign,
                request=self.requests["E2"],
                selection_id="S10",
                basis_refs=self.campaign["basis_refs"],
                kind=SELECT,
                selected_by="LABBOIB",
            )
        self.assertEqual(self.selection_store.history(self.campaign["campaign_id"]), [])


    def test_s11_reed_label_policy_does_not_authenticate_event_origin(self) -> None:
        # A: ordinary helper path.
        event_a = self.event("E2", "S11-A")
        first = self.selection_store.append(event_a)
        self.assertFalse(first["idempotent_replay"])

        # Release the exact request so the same request identity can be selected
        # again through an independent event-formation path.
        self.selection_store.append(
            self.event("E2", "S11-REL", kind=RELEASE)
        )

        # B: bypass build_selection_event and form otherwise-valid bytes
        # directly. No signer, session principal, capability, or authenticated
        # origin is consumed by SelectionStore._validate().
        event_b = copy.deepcopy(event_a)
        event_b["selection_id"] = "S11-B"
        event_b["selection_reason"] = "independent caller asserts REED"
        second = self.selection_store.append(event_b)
        self.assertFalse(second["idempotent_replay"])

        stored = self.selection_store.history(
            self.campaign["campaign_id"]
        )
        stored_b = next(
            event for event in stored
            if event["selection_id"] == "S11-B"
        )
        self.assertEqual(stored_b["selected_by"], "REED")
        self.assertEqual(
            set(stored_b),
            {
                "schema",
                "selection_id",
                "campaign_id",
                "campaign_sha256",
                "request_id",
                "request_sha256",
                "selected_by",
                "selected_at_basis_refs",
                "selected_at_basis_sha256",
                "selection_kind",
                "selection_reason",
                "authorization_effect",
                "execution_effect",
                "standing_effect",
                "_seq",
            },
        )

        # C: the store does enforce the selector attribute policy.
        event_c = copy.deepcopy(event_b)
        event_c["selection_id"] = "S11-C"
        event_c["selected_by"] = "LABBOIB"
        with self.assertRaisesRegex(
            EnvelopeSelectionError,
            "v0 selector must be REED",
        ):
            self.selection_store.append(event_c)


if __name__ == "__main__":
    unittest.main()
