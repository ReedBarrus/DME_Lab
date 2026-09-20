from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from tools.development_campaign_v0 import CampaignStore, build_campaign, object_sha256
from tools.envelope_selection_v0 import (
    RELEASE as SELECTION_RELEASE,
    SELECT,
    SelectionStore,
    build_selection_event,
)
from tools.preparation_v0 import PreparationStore, build_receipt
from tools.preparation_assignment_v0 import (
    ASSIGN,
    RELEASE,
    AssignmentStore,
    PreparationAssignmentError,
    build_assignment_event,
    build_satisfaction,
)


class PreparationAssignmentPressure(unittest.TestCase):
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
        self.assignment_store = AssignmentStore(
            self.campaign_store,
            self.selection_store,
            self.prep_store,
            root / "assignment.sqlite3",
        )

        self.basis = ["git:H1", "standing:S1"]
        self.campaign = build_campaign({
            "campaign_id": "ASSIGNMENT_FIXTURE_001",
            "title": "Preparation assignment fixture",
            "basis_refs": self.basis,
            "objective": "Pressure sticky-note allocation without wake or authority.",
            "claim_ceiling": "Assignment and exact satisfaction linkage only.",
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
                "NO_WAKE",
                "NO_PRIORITY",
            ],
        })
        self.campaign_store.post_campaign(self.campaign)

        self.requests: dict[str, dict] = {}
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
                    "notes": "Assignment fixture.",
                },
                "expected_information_gain": "Distinguish one relation.",
                "stop_conditions": list(self.campaign["stop_conditions"]),
                "packet_status": "CANDIDATE_REQUEST",
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
            self.campaign_store.lodge_request(request)
            self.requests[request["request_id"]] = request

        self.selections: dict[str, dict] = {}
        self.select("E1", "SEL-E1")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def select(self, request_id: str, selection_id: str) -> dict:
        event = build_selection_event(
            campaign=self.campaign,
            request=self.requests[request_id],
            selection_id=selection_id,
            basis_refs=self.basis,
            kind=SELECT,
            reason=f"select {request_id}",
        )
        self.selection_store.append(event)
        self.selections[request_id] = event
        return event

    def release_selection(self, request_id: str, selection_id: str) -> dict:
        event = build_selection_event(
            campaign=self.campaign,
            request=self.requests[request_id],
            selection_id=selection_id,
            basis_refs=self.basis,
            kind=SELECTION_RELEASE,
            reason=f"release {request_id}",
        )
        self.selection_store.append(event)
        return event

    def assignment(
        self,
        assignment_id: str,
        *,
        request_id: str = "E1",
        seat_id: str = "MAYA",
        preparation_kind: str = "RESOLVE_REFS",
        kind: str = ASSIGN,
        basis: list[str] | None = None,
    ) -> dict:
        return build_assignment_event(
            campaign=self.campaign,
            request=self.requests[request_id],
            selection=self.selections[request_id],
            assignment_id=assignment_id,
            seat_id=seat_id,
            preparation_kind=preparation_kind,
            assigned_at_basis_refs=basis or self.basis,
            kind=kind,
            reason="fixture sticky note",
        )

    def prep_receipt(
        self,
        prep_id: str,
        *,
        request_id: str = "E1",
        seat_id: str = "MAYA",
        preparation_kind: str = "RESOLVE_REFS",
        status: str = "PASS",
    ) -> dict:
        return build_receipt(
            campaign=self.campaign,
            request=self.requests[request_id],
            selection=self.selections[request_id],
            preparation_id=prep_id,
            prepared_by=seat_id,
            preparation_kind=preparation_kind,
            preparation_basis_refs=self.basis,
            input_refs=[f"request://{request_id}"],
            output_refs=[],
            mechanical_status=status,
        )

    def project(self, basis: list[str] | None = None) -> dict:
        return self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=basis or self.basis,
        )

    def row(self, assignment_id: str, basis: list[str] | None = None) -> dict:
        rows = self.project(basis)["assignment_projection"]
        return next(r for r in rows if r["assignment_id"] == assignment_id)

    def test_a1_exact_basic_assignment_creates_no_wake_or_authority(self) -> None:
        event = self.assignment("A1")
        result = self.assignment_store.append(
            event,
            current_basis_refs=self.basis,
        )
        row = self.row("A1")

        self.assertFalse(result["idempotent_replay"])
        self.assertEqual(row["assignment_state"], "OUTSTANDING")
        self.assertTrue(row["wake_eligible"])
        self.assertEqual(event["authority_effect"], "NONE")
        self.assertEqual(event["execution_effect"], "NONE")
        self.assertEqual(event["priority_effect"], "NONE")
        self.assertEqual(event["wake_effect"], "NONE")

    def test_a2_unselected_request_rejected(self) -> None:
        self.select("E2", "SEL-E2-A2")
        original = self.selections["E2"]
        self.release_selection("E2", "SEL-E2-A2-RELEASE")
        event = build_assignment_event(
            campaign=self.campaign,
            request=self.requests["E2"],
            selection=original,
            assignment_id="A2",
            seat_id="MAYA",
            preparation_kind="RESOLVE_REFS",
            assigned_at_basis_refs=self.basis,
            kind=ASSIGN,
        )
        with self.assertRaises(PreparationAssignmentError):
            self.assignment_store.append(event, current_basis_refs=self.basis)
        self.assertEqual(self.assignment_store.history(self.campaign["campaign_id"]), [])

    def test_a3_stale_after_assignment_preserves_history_blocks_wake(self) -> None:
        event = self.assignment("A3")
        self.assignment_store.append(event, current_basis_refs=self.basis)
        row = self.row("A3", ["git:H2", "standing:S1"])

        self.assertEqual(row["assignment_state"], "BLOCKED_STALE")
        self.assertFalse(row["wake_eligible"])
        self.assertEqual(
            self.assignment_store.history(self.campaign["campaign_id"])[0]["assignment_id"],
            "A3",
        )

    def test_a4_fracture_after_assignment_marks_obsolete(self) -> None:
        self.assignment_store.append(
            self.assignment("A4"),
            current_basis_refs=self.basis,
        )
        self.campaign_store.record_standing_update({
            "schema": "campaign_standing_update_v0",
            "campaign_id": self.campaign["campaign_id"],
            "relation_id": "R1",
            "standing": "FRACTURED",
            "adjudication_ref": "decision://R1/fractured",
            "basis_ref": "git:H1",
        })
        row = self.row("A4")
        self.assertEqual(row["assignment_state"], "BLOCKED_OBSOLETE")
        self.assertFalse(row["wake_eligible"])

    def test_a5_release_is_not_satisfaction(self) -> None:
        self.assignment_store.append(
            self.assignment("A5-ASSIGN"),
            current_basis_refs=self.basis,
        )
        self.assignment_store.append(
            self.assignment("A5-RELEASE", kind=RELEASE),
            current_basis_refs=self.basis,
        )
        row = self.row("A5-ASSIGN")

        self.assertEqual(row["assignment_state"], "RELEASED")
        self.assertIsNone(row["satisfaction_id"])
        self.assertFalse(row["wake_eligible"])
        self.assertEqual(self.assignment_store.satisfaction_history(), [])

    def test_a6_parallel_homies_coexist_without_priority(self) -> None:
        self.select("E2", "SEL-E2-A6")
        events = [
            self.assignment("A6-MAYA", request_id="E1", seat_id="MAYA"),
            self.assignment("A6-COMMANDER", request_id="E2", seat_id="COMMANDER"),
            self.assignment(
                "A6-WORKSHOP",
                request_id="E1",
                seat_id="WORKSHOP",
                preparation_kind="ASSEMBLE_EVIDENCE",
            ),
        ]
        for event in events:
            self.assignment_store.append(event, current_basis_refs=self.basis)

        projection = self.project()
        self.assertEqual(projection["wake_eligible_count"], 3)
        self.assertEqual(projection["priority_effect"], "NONE")
        self.assertEqual(
            {r["seat_id"] for r in projection["assignment_projection"]},
            {"MAYA", "COMMANDER", "WORKSHOP"},
        )

    def test_a7_multiple_assignments_to_one_seat_do_not_create_queue_order(self) -> None:
        self.select("E2", "SEL-E2-A7")
        self.assignment_store.append(
            self.assignment("A7-E1", request_id="E1", seat_id="MAYA"),
            current_basis_refs=self.basis,
        )
        self.assignment_store.append(
            self.assignment("A7-E2", request_id="E2", seat_id="MAYA"),
            current_basis_refs=self.basis,
        )

        projection = self.project()
        self.assertEqual(projection["wake_eligible_count"], 2)
        self.assertEqual(
            {item["assignment_id"] for item in projection["wake_eligible_assignments"]},
            {"A7-E1", "A7-E2"},
        )
        self.assertEqual(projection["priority_effect"], "NONE")

    def test_a8_exact_replay_idempotent_identity_conflict_rejected(self) -> None:
        event = self.assignment("A8")
        first = self.assignment_store.append(event, current_basis_refs=self.basis)
        second = self.assignment_store.append(event, current_basis_refs=self.basis)
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])

        changed = copy.deepcopy(event)
        changed["seat_id"] = "COMMANDER"
        with self.assertRaises(PreparationAssignmentError):
            self.assignment_store.append(changed, current_basis_refs=self.basis)

    def test_a9_unrelated_preparation_receipt_cannot_satisfy_assignment(self) -> None:
        assignment = self.assignment("A9")
        self.assignment_store.append(assignment, current_basis_refs=self.basis)

        unrelated = self.prep_receipt("P-A9", seat_id="COMMANDER")
        self.prep_store.append(unrelated, current_basis_refs=self.basis)
        satisfaction = build_satisfaction(
            assignment=assignment,
            preparation_receipt=unrelated,
            satisfaction_id="SAT-A9",
        )
        with self.assertRaises(PreparationAssignmentError):
            self.assignment_store.append_satisfaction(satisfaction)
        self.assertEqual(self.assignment_store.satisfaction_history(), [])

    def test_a10_exact_qualifying_receipt_satisfies_once(self) -> None:
        assignment = self.assignment("A10")
        self.assignment_store.append(assignment, current_basis_refs=self.basis)

        receipt = self.prep_receipt("P-A10")
        self.prep_store.append(receipt, current_basis_refs=self.basis)
        satisfaction = build_satisfaction(
            assignment=assignment,
            preparation_receipt=receipt,
            satisfaction_id="SAT-A10",
        )
        first = self.assignment_store.append_satisfaction(satisfaction)
        second = self.assignment_store.append_satisfaction(satisfaction)

        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(self.row("A10")["assignment_state"], "SATISFIED")
        self.assertEqual(len(self.assignment_store.satisfaction_history()), 1)

    def test_a11_satisfied_assignment_is_not_wake_eligible(self) -> None:
        assignment = self.assignment("A11")
        self.assignment_store.append(assignment, current_basis_refs=self.basis)
        receipt = self.prep_receipt("P-A11")
        self.prep_store.append(receipt, current_basis_refs=self.basis)
        self.assignment_store.append_satisfaction(
            build_satisfaction(
                assignment=assignment,
                preparation_receipt=receipt,
                satisfaction_id="SAT-A11",
            )
        )

        projection = self.project()
        row = self.row("A11")
        self.assertEqual(row["assignment_state"], "SATISFIED")
        self.assertFalse(row["wake_eligible"])
        self.assertEqual(projection["wake_eligible_count"], 0)

    def test_a12_same_request_can_have_distinct_seat_kind_assignments(self) -> None:
        self.assignment_store.append(
            self.assignment(
                "A12-MAYA",
                seat_id="MAYA",
                preparation_kind="RESOLVE_REFS",
            ),
            current_basis_refs=self.basis,
        )
        self.assignment_store.append(
            self.assignment(
                "A12-COMMANDER",
                seat_id="COMMANDER",
                preparation_kind="REVIEW_RESULT",
            ),
            current_basis_refs=self.basis,
        )

        rows = self.project()["assignment_projection"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            {(r["seat_id"], r["preparation_kind"]) for r in rows},
            {("MAYA", "RESOLVE_REFS"), ("COMMANDER", "REVIEW_RESULT")},
        )
        self.assertTrue(all(r["assignment_state"] == "OUTSTANDING" for r in rows))


if __name__ == "__main__":
    unittest.main()
