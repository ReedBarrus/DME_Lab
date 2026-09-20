from __future__ import annotations

from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from tools.bounded_reentry_v0 import BoundedReentryRunner, ReentryStore
from tools.development_campaign_v0 import CampaignStore, build_campaign, object_sha256
from tools.envelope_selection_v0 import SELECT, SelectionStore, build_selection_event
from tools.goblin_pool import GoblinPool
from tools.preparation_assignment_v0 import (
    ASSIGN,
    RELEASE,
    AssignmentStore,
    build_assignment_event,
    build_satisfaction,
)
from tools.preparation_v0 import PreparationStore, build_receipt
from tools.wake_source_v0 import WakeSourceError, WakeSourceStore, build_manual_bell


class WakeSourcePressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.email", "lab@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.name", "DME Lab"],
            check=True,
        )
        (self.repo / "fixture.txt").write_text("H1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "fixture.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "H1"], check=True)
        self.h1 = self.head()
        self.basis = [f"git:{self.h1}"]

        self.controller_db = root / "controller.sqlite3"
        self.campaign_db = root / "campaign.sqlite3"
        self.selection_db = root / "selection.sqlite3"
        self.prep_db = root / "prep.sqlite3"
        self.assignment_db = root / "assignment.sqlite3"
        self.reentry_db = root / "reentry.sqlite3"
        self.wake_source_db = root / "wake-source.sqlite3"

        self.pool = GoblinPool(self.controller_db, self.repo)
        self.pool.initialize_fixture()
        for seat in ("MAYA", "COMMANDER", "WORKSHOP", "LABBOIB"):
            self.pool.bind_external_seat(
                seat_id=seat,
                cursor_event_id=f"EV-{seat}-GENESIS",
                working_state={"seat_id": seat, "mode": "DORMANT"},
                source_events=[
                    {
                        "event_id": f"EV-{seat}-GENESIS",
                        "kind": "SEAT_GENESIS",
                        "source": "WAKE_SOURCE_001",
                    }
                ],
                policy_ref=f"policy:{seat}:wake-source-v0",
                operator_profile_ref=f"operators:{seat}:prep-only-v0",
                authority_profile_ref=f"authority:{seat}:none-v0",
            )

        self.campaign_store = CampaignStore(self.campaign_db)
        self.selection_store = SelectionStore(self.campaign_store, self.selection_db)
        self.prep_store = PreparationStore(
            self.campaign_store,
            self.selection_store,
            self.prep_db,
        )
        self.assignment_store = AssignmentStore(
            self.campaign_store,
            self.selection_store,
            self.prep_store,
            self.assignment_db,
        )
        self.reentry_store = ReentryStore(self.reentry_db)
        self.wake_store = WakeSourceStore(
            assignment_store=self.assignment_store,
            reentry_store=self.reentry_store,
            db_path=self.wake_source_db,
        )
        self.runner = BoundedReentryRunner(
            repo=self.repo,
            pool=self.pool,
            campaign_store=self.campaign_store,
            selection_store=self.selection_store,
            preparation_store=self.prep_store,
            reentry_store=self.reentry_store,
            assignment_store=self.assignment_store,
        )

        self.campaign = build_campaign({
            "campaign_id": "WAKE_SOURCE_FIXTURE_001",
            "title": "Manual bell fixture",
            "basis_refs": self.basis,
            "objective": "Pressure one exact bell without scheduler authority.",
            "claim_ceiling": "Manual bell to one assignment-bound wake opportunity only.",
            "target_objects": ["OBJ1", "OBJ2", "OBJ3", "OBJ4"],
            "unresolved_relations": [
                {"relation_id": "R1", "statement": "BELL != WORK_SELECTION"},
                {"relation_id": "R2", "statement": "BELL != PRIORITY"},
                {"relation_id": "R3", "statement": "BELL_EMITTED != WAKE_ADMISSIBLE"},
                {"relation_id": "R4", "statement": "WAKE_SOURCE != SCHEDULER"},
            ],
            "pressure_points": [
                "Ring exact A17.",
                "Preserve no priority.",
                "Invalidate after emission.",
                "Keep time outside source.",
            ],
            "dependency_edges": [],
            "proposal_allowance": {
                "max_candidates": 4,
                "max_model_calls": 0,
                "allowed_resource_classes": ["DETERMINISTIC"],
            },
            "completion_criteria": ["All bell relations remain bounded."],
            "stop_conditions": ["Wake source chooses work.", "Scheduler semantics appear."],
            "explicit_non_authorizations": [
                "NO_SCHEDULER",
                "NO_PRIORITY",
                "NO_EXECUTION_AUTHORITY",
                "NO_STANDING_CHANGE",
            ],
        })
        self.campaign_store.post_campaign(self.campaign)

        self.requests: dict[str, dict] = {}
        self.selections: dict[str, dict] = {}
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
                "smallest_proposed_intervention": "Ring one exact manual bell.",
                "expected_observable": "One assignment-bound wake opportunity.",
                "allowed_effect_surface": [],
                "forbidden_effects": list(self.campaign["explicit_non_authorizations"]),
                "required_authority": "NONE_FOR_MANUAL_BELL",
                "resource_cost": {
                    "resource_class": "DETERMINISTIC",
                    "model_calls": 0,
                    "notes": "No scheduler or model.",
                },
                "expected_information_gain": "Discriminate bell from work selection.",
                "stop_conditions": list(self.campaign["stop_conditions"]),
                "packet_status": "CANDIDATE_REQUEST",
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
            self.campaign_store.lodge_request(request)
            selection = build_selection_event(
                campaign=self.campaign,
                request=request,
                selection_id=f"SEL-E{idx}",
                basis_refs=self.basis,
                kind=SELECT,
                reason="wake source fixture",
            )
            self.selection_store.append(selection)
            self.requests[request["request_id"]] = request
            self.selections[request["request_id"]] = selection

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def head(self) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()

    def move_world(self) -> str:
        with (self.repo / "fixture.txt").open("a", encoding="utf-8") as handle:
            handle.write("H2\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "fixture.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "H2"], check=True)
        return self.head()

    def assignment(
        self,
        assignment_id: str,
        *,
        request_id: str = "E1",
        seat_id: str = "MAYA",
    ) -> dict:
        event = build_assignment_event(
            campaign=self.campaign,
            request=self.requests[request_id],
            selection=self.selections[request_id],
            assignment_id=assignment_id,
            seat_id=seat_id,
            preparation_kind="RESOLVE_REFS",
            assigned_at_basis_refs=self.basis,
            kind=ASSIGN,
            reason="wake source sticky note",
        )
        self.assignment_store.append(event, current_basis_refs=self.basis)
        return event

    def release(self, assignment: dict, release_id: str) -> dict:
        event = build_assignment_event(
            campaign=self.campaign,
            request=self.requests[assignment["request_id"]],
            selection=self.selections[assignment["request_id"]],
            assignment_id=release_id,
            seat_id=assignment["seat_id"],
            preparation_kind=assignment["preparation_kind"],
            assigned_at_basis_refs=self.basis,
            kind=RELEASE,
            reason="release sticky note",
        )
        self.assignment_store.append(event, current_basis_refs=self.basis)
        return event

    def bell(self, assignment: dict, bell_id: str, basis: list[str] | None = None) -> dict:
        return build_manual_bell(
            assignment=assignment,
            bell_id=bell_id,
            bell_basis_refs=basis or self.basis,
        )

    def emit(
        self,
        assignment: dict,
        bell_id: str,
        opportunity_id: str,
        *,
        basis: list[str] | None = None,
        opportunity_basis: str | None = None,
    ) -> dict:
        bell = self.bell(assignment, bell_id, basis)
        return self.wake_store.emit(
            bell,
            current_basis_refs=basis or self.basis,
            opportunity_id=opportunity_id,
            opportunity_basis=opportunity_basis or self.h1,
            campaign=self.campaign,
            request=self.requests[assignment["request_id"]],
            selection=self.selections[assignment["request_id"]],
        )

    def prep_receipt(self, assignment: dict, prep_id: str) -> dict:
        receipt = build_receipt(
            campaign=self.campaign,
            request=self.requests[assignment["request_id"]],
            selection=self.selections[assignment["request_id"]],
            preparation_id=prep_id,
            prepared_by=assignment["seat_id"],
            preparation_kind=assignment["preparation_kind"],
            preparation_basis_refs=self.basis,
            input_refs=[f"request://{assignment['request_id']}"],
            output_refs=[],
            mechanical_status="PASS",
        )
        self.prep_store.append(receipt, current_basis_refs=self.basis)
        return receipt

    def satisfy(self, assignment: dict, satisfaction_id: str, prep_id: str) -> dict:
        prep = self.prep_receipt(assignment, prep_id)
        sat = build_satisfaction(
            assignment=assignment,
            preparation_receipt=prep,
            satisfaction_id=satisfaction_id,
        )
        self.assignment_store.append_satisfaction(sat)
        return sat

    def count_controller_wakes(self) -> int:
        conn = sqlite3.connect(self.controller_db)
        try:
            return conn.execute("SELECT COUNT(*) FROM wakes").fetchone()[0]
        finally:
            conn.close()

    def count_opportunities(self) -> int:
        conn = sqlite3.connect(self.reentry_db)
        try:
            return conn.execute("SELECT COUNT(*) FROM wake_opportunities").fetchone()[0]
        finally:
            conn.close()

    def count_bells(self) -> int:
        conn = sqlite3.connect(self.wake_source_db)
        try:
            return conn.execute("SELECT COUNT(*) FROM manual_bells").fetchone()[0]
        finally:
            conn.close()

    def test_w1_eligible_assignment_emits_one_exact_opportunity_no_wake(self) -> None:
        assignment = self.assignment("A17")
        result = self.emit(assignment, "B1", "W44")

        self.assertEqual(result["assignment_id"], "A17")
        self.assertEqual(result["opportunity_id"], "W44")
        self.assertNotEqual(result["bell_id"], result["opportunity_id"])
        self.assertEqual(self.count_bells(), 1)
        self.assertEqual(self.count_opportunities(), 1)
        self.assertEqual(self.count_controller_wakes(), 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")

        opportunity = self.reentry_store.opportunity("W44")
        self.assertEqual(opportunity["assignment_id"], "A17")
        self.assertEqual(opportunity["manual_bell_id"], "B1")
        self.assertEqual(opportunity["wake_source_kind"], "MANUAL_BELL")
        self.assertEqual(opportunity["authority_effect"], "NONE")
        self.assertEqual(opportunity["execution_effect"], "NONE")
        self.assertEqual(opportunity["scheduler_effect"], "NONE")

    def test_w2_satisfied_assignment_cannot_emit_bell(self) -> None:
        assignment = self.assignment("A2")
        self.satisfy(assignment, "SAT-A2", "P-A2")
        with self.assertRaises(WakeSourceError):
            self.emit(assignment, "B2", "W2")
        self.assertEqual(self.count_opportunities(), 0)

    def test_w3_released_assignment_cannot_emit_bell(self) -> None:
        assignment = self.assignment("A3")
        self.release(assignment, "A3-RELEASE")
        with self.assertRaises(WakeSourceError):
            self.emit(assignment, "B3", "W3")
        self.assertEqual(self.count_opportunities(), 0)

    def test_w4_stale_assignment_cannot_emit_bell(self) -> None:
        assignment = self.assignment("A4")
        h2 = self.move_world()
        basis2 = [f"git:{h2}"]
        with self.assertRaises(WakeSourceError):
            self.emit(
                assignment,
                "B4",
                "W4",
                basis=basis2,
                opportunity_basis=h2,
            )
        self.assertEqual(self.count_opportunities(), 0)

    def test_w5_obsolete_assignment_cannot_emit_bell(self) -> None:
        assignment = self.assignment("A5", request_id="E3")
        self.campaign_store.record_standing_update({
            "schema": "campaign_standing_update_v0",
            "campaign_id": self.campaign["campaign_id"],
            "relation_id": "R3",
            "standing": "FRACTURED",
            "adjudication_ref": "decision://R3/fractured",
            "basis_ref": f"git:{self.h1}",
        })
        with self.assertRaises(WakeSourceError):
            self.emit(assignment, "B5", "W5")
        self.assertEqual(self.count_opportunities(), 0)

    def test_w6_exact_bell_replay_returns_same_opportunity_relation(self) -> None:
        assignment = self.assignment("A6")
        bell = self.bell(assignment, "B6")
        first = self.wake_store.emit(
            bell,
            current_basis_refs=self.basis,
            opportunity_id="W6-FIRST",
            opportunity_basis=self.h1,
            campaign=self.campaign,
            request=self.requests["E1"],
            selection=self.selections["E1"],
        )
        second = self.wake_store.emit(
            bell,
            current_basis_refs=self.basis,
            opportunity_id="W6-DIFFERENT-REQUESTED-ID",
            opportunity_basis=self.h1,
            campaign=self.campaign,
            request=self.requests["E1"],
            selection=self.selections["E1"],
        )

        self.assertEqual(first["opportunity_id"], "W6-FIRST")
        self.assertEqual(second["opportunity_id"], "W6-FIRST")
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(self.count_bells(), 1)
        self.assertEqual(self.count_opportunities(), 1)

    def test_w7_two_eligible_assignments_input_names_only_one(self) -> None:
        a17 = self.assignment("A7-17", request_id="E1", seat_id="MAYA")
        self.assignment("A7-18", request_id="E2", seat_id="COMMANDER")
        projection = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )
        self.assertEqual(projection["wake_eligible_count"], 2)

        self.emit(a17, "B7", "W7")

        self.assertEqual(self.count_bells(), 1)
        self.assertEqual(self.count_opportunities(), 1)
        self.assertEqual(self.reentry_store.opportunity("W7")["assignment_id"], "A7-17")

    def test_w8_two_maya_assignments_do_not_create_queue_or_second_bell(self) -> None:
        a17 = self.assignment("A8-17", request_id="E1", seat_id="MAYA")
        self.assignment("A8-19", request_id="E2", seat_id="MAYA")
        projection = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )
        self.assertEqual(projection["wake_eligible_count"], 2)
        self.assertEqual(projection["priority_effect"], "NONE")

        self.emit(a17, "B8", "W8")
        self.assertEqual(self.count_bells(), 1)
        self.assertEqual(self.count_opportunities(), 1)
        self.assertEqual(self.reentry_store.opportunity("W8")["assignment_id"], "A8-17")

    def test_w9_bell_history_survives_invalidation_reentry_blocks_before_occupancy(self) -> None:
        a_sat = self.assignment("A9-SAT", request_id="E1", seat_id="MAYA")
        a_rel = self.assignment("A9-REL", request_id="E2", seat_id="COMMANDER")
        a_obs = self.assignment("A9-OBS", request_id="E3", seat_id="WORKSHOP")
        a_stale = self.assignment("A9-STALE", request_id="E4", seat_id="LABBOIB")

        self.emit(a_sat, "B9-SAT", "W9-SAT")
        self.emit(a_rel, "B9-REL", "W9-REL")
        self.emit(a_obs, "B9-OBS", "W9-OBS")
        self.emit(a_stale, "B9-STALE", "W9-STALE")

        self.satisfy(a_sat, "SAT-A9", "P-A9")
        self.release(a_rel, "A9-REL-RELEASE")
        self.campaign_store.record_standing_update({
            "schema": "campaign_standing_update_v0",
            "campaign_id": self.campaign["campaign_id"],
            "relation_id": "R3",
            "standing": "FRACTURED",
            "adjudication_ref": "decision://R3/fractured",
            "basis_ref": f"git:{self.h1}",
        })

        before_wakes = self.count_controller_wakes()
        sat_result = self.runner.run_once("W9-SAT")
        rel_result = self.runner.run_once("W9-REL")
        obs_result = self.runner.run_once("W9-OBS")

        self.assertEqual(sat_result["outcome"], "BLOCKED_ASSIGNMENT_SATISFIED")
        self.assertEqual(rel_result["outcome"], "BLOCKED_ASSIGNMENT_RELEASED")
        self.assertEqual(obs_result["outcome"], "BLOCKED_ASSIGNMENT_BLOCKED_OBSOLETE")
        self.assertEqual(self.count_controller_wakes(), before_wakes)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")
        self.assertEqual(self.pool.seat_snapshot("COMMANDER")["occupancy_state"], "AVAILABLE")
        self.assertEqual(self.pool.seat_snapshot("WORKSHOP")["occupancy_state"], "AVAILABLE")

        h2 = self.move_world()
        stale_result = self.runner.run_once("W9-STALE")
        self.assertEqual(
            stale_result["outcome"],
            "BLOCKED_ASSIGNMENT_BLOCKED_STALE",
        )
        self.assertEqual(self.count_controller_wakes(), before_wakes)
        self.assertEqual(self.pool.seat_snapshot("LABBOIB")["occupancy_state"], "AVAILABLE")

        for oid in ("W9-SAT", "W9-REL", "W9-OBS", "W9-STALE"):
            events = self.reentry_store.events(oid)
            self.assertEqual(events[-1]["event_kind"], "WAKE_BLOCKED")
            self.assertTrue(events[-1]["payload"]["revalidated_before_occupancy"])

        self.assertEqual(self.count_opportunities(), 4)
        self.assertEqual(self.count_bells(), 4)

    def test_w10_answered_bell_runs_one_unit_then_later_satisfaction_blocks_new_bell(self) -> None:
        assignment = self.assignment("A10")
        self.emit(assignment, "B10", "W10")

        result = self.runner.run_once("W10")
        self.assertEqual(result["outcome"], "UNIT_COMPLETED")
        self.assertEqual(result["work_units_performed"], 1)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")

        prep_id = result["preparation_receipt_id"]
        conn = sqlite3.connect(self.prep_db)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT receipt_json FROM preparation_receipts WHERE preparation_id=?",
                (prep_id,),
            ).fetchone()
        finally:
            conn.close()
        self.assertIsNotNone(row)
        prep = __import__("json").loads(row["receipt_json"])

        satisfaction = build_satisfaction(
            assignment=assignment,
            preparation_receipt=prep,
            satisfaction_id="SAT-A10",
        )
        self.assignment_store.append_satisfaction(satisfaction)

        projection = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )
        a10 = next(
            row for row in projection["assignment_projection"]
            if row["assignment_id"] == "A10"
        )
        self.assertEqual(a10["assignment_state"], "SATISFIED")
        self.assertFalse(a10["wake_eligible"])

        with self.assertRaises(WakeSourceError):
            self.emit(assignment, "B10-AGAIN", "W10-AGAIN")

        self.assertEqual(self.count_opportunities(), 1)
        self.assertEqual(self.count_bells(), 1)


if __name__ == "__main__":
    unittest.main()
