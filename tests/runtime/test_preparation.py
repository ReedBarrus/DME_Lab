from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from tools.development_campaign_v0 import CampaignStore, build_campaign, object_sha256
from tools.envelope_selection_v0 import SelectionStore, build_selection_event, SELECT
from tools.preparation_v0 import (
    PreparationError,
    PreparationStore,
    build_receipt,
)


class PreparationPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.campaign_store = CampaignStore(root / "campaign.sqlite3")
        self.selection_store = SelectionStore(
            self.campaign_store,
            root / "selection.sqlite3",
        )
        self.prep_store = PreparationStore(
            self.campaign_store,
            self.selection_store,
            root / "preparation.sqlite3",
        )

        self.basis = ["git:H1", "standing:S1"]
        self.campaign = build_campaign({
            "campaign_id": "PREP_FIXTURE_001",
            "title": "Preparation fixture",
            "basis_refs": self.basis,
            "objective": "Pressure preparation without consequence authority.",
            "claim_ceiling": "Preparation only.",
            "target_objects": ["OBJ_A", "OBJ_B"],
            "unresolved_relations": [
                {"relation_id": "R1", "statement": "A != B"},
                {"relation_id": "R2", "statement": "B != C"},
            ],
            "pressure_points": ["Pressure R1.", "Pressure R2."],
            "dependency_edges": [],
            "proposal_allowance": {
                "max_candidates": 2,
                "max_model_calls": 0,
                "allowed_resource_classes": ["DETERMINISTIC"],
            },
            "completion_criteria": ["Relations get explicit standing."],
            "stop_conditions": ["Basis unreconstructable."],
            "explicit_non_authorizations": [
                "NO_EXECUTION",
                "NO_STANDING_CHANGE",
                "NO_CANONICAL_MUTATION",
            ],
        })
        self.campaign_store.post_campaign(self.campaign)

        self.requests = {}
        for idx, relation in enumerate(self.campaign["unresolved_relations"], 1):
            request = {
                "schema": "execution_envelope_request_v0",
                "request_id": f"E{idx}",
                "campaign_id": self.campaign["campaign_id"],
                "campaign_sha256": object_sha256(self.campaign),
                "seat_id": "LABBOIB",
                "object_under_pressure": self.campaign["target_objects"][idx - 1],
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
                    "notes": "Preparation fixture.",
                },
                "expected_information_gain": "Discriminate one relation.",
                "stop_conditions": list(self.campaign["stop_conditions"]),
                "packet_status": "CANDIDATE_REQUEST",
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
            self.campaign_store.lodge_request(request)
            self.requests[request["request_id"]] = request

        self.selection_e1 = build_selection_event(
            campaign=self.campaign,
            request=self.requests["E1"],
            selection_id="SEL-E1",
            basis_refs=self.basis,
            kind=SELECT,
            reason="prepare E1",
        )
        self.selection_store.append(self.selection_e1)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def receipt(
        self,
        prep_id: str,
        *,
        prepared_by: str = "LABBOIB",
        kind: str = "RESOLVE_REFS",
        basis: list[str] | None = None,
        inputs: list[str] | None = None,
        outputs: list[str] | None = None,
        status: str = "PASS",
        review: str | None = None,
    ) -> dict:
        return build_receipt(
            campaign=self.campaign,
            request=self.requests["E1"],
            selection=self.selection_e1,
            preparation_id=prep_id,
            prepared_by=prepared_by,
            preparation_kind=kind,
            preparation_basis_refs=basis or self.basis,
            input_refs=inputs or ["request://E1"],
            output_refs=outputs or [],
            mechanical_status=status,
            review_disposition=review,
        )

    def packet(self) -> dict:
        return {
            "PACKET_ID": "PKT-E1-DRAFT",
            "BASIS": "git:H1",
            "CURRENT_PRESSURE": "Pressure R1 without broadening.",
            "ADMITTED_EVIDENCE": ["request://E1"],
            "UNRESOLVED": ["R1"],
            "AUTHORIZED_OPERATIONS": ["fixture-read-only"],
            "UNAUTHORIZED_EXTRAPOLATIONS": ["NO_CANONICAL_MUTATION"],
            "REQUIRED_EVIDENCE_RETURN": ["exact observations"],
            "STOP_OR_ESCALATE_IF": ["basis changes"],
            "EXECUTION_QUESTIONS": ["Does the bounded pressure discriminate R1?"],
            "AUTHORIZATION": "NOT_AUTHORIZED",
        }

    def test_p1_eligible_selected_request_retains_bounded_prep_only(self) -> None:
        receipt = self.receipt("P1")
        result = self.prep_store.append(receipt, current_basis_refs=self.basis)
        projection = self.prep_store.projection(
            self.campaign["campaign_id"], "E1", current_basis_refs=self.basis
        )

        self.assertFalse(result["idempotent_replay"])
        self.assertEqual(projection["receipt_count"], 1)
        self.assertEqual(receipt["preparation_effect"], "PREPARATION_ONLY")
        self.assertEqual(receipt["canonical_mutation_effect"], "NONE")
        self.assertEqual(receipt["authorization_effect"], "NONE")
        self.assertEqual(receipt["execution_effect"], "NONE")
        self.assertEqual(receipt["standing_effect"], "NONE")

    def test_p2_unselected_request_is_not_preparation_eligible(self) -> None:
        fake_selection = build_selection_event(
            campaign=self.campaign,
            request=self.requests["E2"],
            selection_id="SEL-E2-NOT-APPENDED",
            basis_refs=self.basis,
            kind=SELECT,
        )
        receipt = build_receipt(
            campaign=self.campaign,
            request=self.requests["E2"],
            selection=fake_selection,
            preparation_id="P2",
            prepared_by="LABBOIB",
            preparation_kind="RESOLVE_REFS",
            preparation_basis_refs=self.basis,
            input_refs=["request://E2"],
            output_refs=[],
            mechanical_status="PASS",
        )
        with self.assertRaises(PreparationError):
            self.prep_store.append(receipt, current_basis_refs=self.basis)

    def test_p3_selected_but_stale_blocks_preparation(self) -> None:
        h2 = ["git:H2", "standing:S1"]
        receipt = self.receipt("P3", basis=h2)
        with self.assertRaises(PreparationError):
            self.prep_store.append(receipt, current_basis_refs=h2)

        projection = self.prep_store.projection(
            self.campaign["campaign_id"], "E1", current_basis_refs=h2
        )
        self.assertEqual(projection["readiness"], "PREP_BLOCKED_STALE")
        self.assertEqual(projection["receipt_count"], 0)

    def test_p4_prep_history_survives_world_move_but_readiness_stales(self) -> None:
        receipt = self.receipt("P4")
        before = copy.deepcopy(receipt)
        self.prep_store.append(receipt, current_basis_refs=self.basis)

        projection = self.prep_store.projection(
            self.campaign["campaign_id"],
            "E1",
            current_basis_refs=["git:H2", "standing:S1"],
        )

        self.assertEqual(receipt, before)
        self.assertEqual(projection["readiness"], "PREP_BLOCKED_STALE")
        self.assertEqual(projection["receipt_count"], 1)
        self.assertEqual(projection["stale_receipt_count"], 1)

    def test_p5_fracture_preserves_prep_history_and_blocks_as_obsolete(self) -> None:
        self.prep_store.append(self.receipt("P5"), current_basis_refs=self.basis)
        self.campaign_store.record_standing_update({
            "schema": "campaign_standing_update_v0",
            "campaign_id": self.campaign["campaign_id"],
            "relation_id": "R1",
            "standing": "FRACTURED",
            "adjudication_ref": "decision://R1/fractured",
            "basis_ref": "git:H1",
        })

        projection = self.prep_store.projection(
            self.campaign["campaign_id"], "E1", current_basis_refs=self.basis
        )
        self.assertEqual(projection["readiness"], "PREP_BLOCKED_OBSOLETE")
        self.assertEqual(projection["receipt_count"], 1)

    def test_p6_multi_seat_prep_coexists_without_priority(self) -> None:
        for idx, seat in enumerate(("LABBOIB", "COMMANDER", "WORKSHOP", "MAYA"), 1):
            self.prep_store.append(
                self.receipt(f"P6-{idx}", prepared_by=seat),
                current_basis_refs=self.basis,
            )

        history = self.prep_store.history(self.campaign["campaign_id"], "E1")
        self.assertEqual(
            {r["prepared_by"] for r in history},
            {"LABBOIB", "COMMANDER", "WORKSHOP", "MAYA"},
        )
        self.assertTrue(all(r["priority_effect"] == "NONE" for r in history))

    def test_p7_conflicting_reviews_are_both_retained_without_adjudication(self) -> None:
        self.prep_store.append(
            self.receipt(
                "P7-A",
                prepared_by="COMMANDER",
                kind="REVIEW_RESULT",
                review="PASS",
            ),
            current_basis_refs=self.basis,
        )
        self.prep_store.append(
            self.receipt(
                "P7-B",
                prepared_by="LABBOIB",
                kind="REVIEW_RESULT",
                review="OBJECTION",
            ),
            current_basis_refs=self.basis,
        )

        projection = self.prep_store.projection(
            self.campaign["campaign_id"], "E1", current_basis_refs=self.basis
        )
        history = self.prep_store.history(self.campaign["campaign_id"], "E1")
        self.assertEqual({r["review_disposition"] for r in history}, {"PASS", "OBJECTION"})
        self.assertEqual(
            projection["readiness"],
            "PREP_INCOMPLETE_REVIEW_CONFLICT",
        )

    def test_p8_packet_draft_can_be_ready_for_authority_review_but_not_authorized(self) -> None:
        packet = self.packet()
        self.prep_store.register_artifact(
            "packet://PKT-E1-DRAFT",
            "EXECUTION_PACKET_v0",
            packet,
        )
        self.prep_store.append(
            self.receipt(
                "P8",
                prepared_by="WORKSHOP",
                kind="DRAFT_PACKET",
                outputs=["packet://PKT-E1-DRAFT"],
            ),
            current_basis_refs=self.basis,
        )

        projection = self.prep_store.projection(
            self.campaign["campaign_id"], "E1", current_basis_refs=self.basis
        )
        self.assertEqual(packet["AUTHORIZATION"], "NOT_AUTHORIZED")
        self.assertEqual(
            projection["readiness"],
            "PREP_READY_FOR_AUTHORITY_REVIEW",
        )
        self.assertEqual(projection["authorization_effect"], "NONE")
        self.assertEqual(projection["execution_effect"], "NONE")

    def test_p9_exact_receipt_replay_is_idempotent_conflicting_bytes_rejected(self) -> None:
        receipt = self.receipt("P9")
        first = self.prep_store.append(receipt, current_basis_refs=self.basis)
        second = self.prep_store.append(receipt, current_basis_refs=self.basis)

        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(len(self.prep_store.history(self.campaign["campaign_id"], "E1")), 1)

        changed = copy.deepcopy(receipt)
        changed["prepared_by"] = "COMMANDER"
        with self.assertRaises(PreparationError):
            self.prep_store.append(changed, current_basis_refs=self.basis)

    def test_p10_later_authority_does_not_make_stale_preparation_current(self) -> None:
        packet = self.packet()
        self.prep_store.register_artifact(
            "packet://P10",
            "EXECUTION_PACKET_v0",
            packet,
        )
        self.prep_store.append(
            self.receipt(
                "P10",
                kind="DRAFT_PACKET",
                outputs=["packet://P10"],
            ),
            current_basis_refs=self.basis,
        )

        projection = self.prep_store.projection(
            self.campaign["campaign_id"],
            "E1",
            current_basis_refs=["git:H2", "standing:S1"],
            external_authority_status="PRESENT",
        )
        self.assertEqual(projection["external_authority_status"], "PRESENT")
        self.assertEqual(projection["readiness"], "PREP_BLOCKED_STALE")
        self.assertEqual(projection["authorization_effect"], "NONE")
        self.assertEqual(projection["execution_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
