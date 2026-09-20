from __future__ import annotations

from pathlib import Path
import sqlite3
import subprocess
import tempfile
import threading
import unittest

from tools.bounded_reentry_v0 import (
    BoundedReentryRunner,
    InjectedReentryCrash,
    ReentryStore,
    build_wake_opportunity,
)
from tools.development_campaign_v0 import CampaignStore, build_campaign, object_sha256
from tools.envelope_selection_v0 import SELECT, SelectionStore, build_selection_event
from tools.goblin_pool import GoblinPool
from tools.preparation_v0 import PreparationStore


class BoundedReentryPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "lab@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "DME Lab"], check=True)
        (self.repo / "fixture.txt").write_text("H1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "fixture.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "H1"], check=True)
        self.h1 = self.head()

        self.controller_db = root / "controller.sqlite3"
        self.campaign_db = root / "campaign.sqlite3"
        self.selection_db = root / "selection.sqlite3"
        self.prep_db = root / "prep.sqlite3"
        self.reentry_db = root / "reentry.sqlite3"

        self.pool = GoblinPool(self.controller_db, self.repo)
        self.pool.initialize_fixture()
        self.pool.bind_external_seat(
            seat_id="MAYA",
            cursor_event_id="EV-MAYA-GENESIS",
            working_state={"seat_id": "MAYA", "mode": "DORMANT", "reentry_count": 0},
            source_events=[
                {
                    "event_id": "EV-MAYA-GENESIS",
                    "kind": "SEAT_GENESIS",
                    "source": "BOUNDED_REENTRY_001",
                }
            ],
            policy_ref="policy:MAYA:bounded-reentry-v0",
            operator_profile_ref="operators:MAYA:prep-only-v0",
            authority_profile_ref="authority:MAYA:none-v0",
        )
        self.pool.append_event(
            "EV-GLOBAL-1",
            seat_id=None,
            event_kind="CAMPAIGN_CHANGED",
            payload={"campaign_id": "REENTRY_FIXTURE_001"},
        )

        self.campaign_store = CampaignStore(self.campaign_db)
        self.selection_store = SelectionStore(self.campaign_store, self.selection_db)
        self.prep_store = PreparationStore(
            self.campaign_store, self.selection_store, self.prep_db
        )
        self.reentry_store = ReentryStore(self.reentry_db)

        self.campaign = build_campaign({
            "campaign_id": "REENTRY_FIXTURE_001",
            "title": "Bounded reentry fixture",
            "basis_refs": [f"git:{self.h1}"],
            "objective": "Pressure one deterministic reentry unit.",
            "claim_ceiling": "One wake, one unit, no scheduler.",
            "target_objects": ["R1", "R2"],
            "unresolved_relations": [
                {"relation_id": "R1", "statement": "WAKE != OPEN_ENDED_WORK"},
                {"relation_id": "R2", "statement": "SEAT_IDENTITY != OCCUPANCY"},
            ],
            "pressure_points": ["Pressure one reentry.", "Pressure occupancy separation."],
            "dependency_edges": [],
            "proposal_allowance": {
                "max_candidates": 2,
                "max_model_calls": 0,
                "allowed_resource_classes": ["DETERMINISTIC"],
            },
            "completion_criteria": ["One-unit lifecycle is discriminated."],
            "stop_conditions": ["World basis changes.", "Occupancy unavailable."],
            "explicit_non_authorizations": [
                "NO_SCHEDULER",
                "NO_EXECUTION_AUTHORITY",
                "NO_OPEN_ENDED_WORK",
            ],
        })
        self.campaign_store.post_campaign(self.campaign)

        self.requests = {}
        self.selections = {}
        for idx, relation in enumerate(self.campaign["unresolved_relations"], 1):
            request = {
                "schema": "execution_envelope_request_v0",
                "request_id": f"E{idx}",
                "campaign_id": self.campaign["campaign_id"],
                "campaign_sha256": object_sha256(self.campaign),
                "seat_id": "MAYA",
                "object_under_pressure": self.campaign["target_objects"][idx - 1],
                "unresolved_relation_id": relation["relation_id"],
                "unresolved_relation": relation["statement"],
                "smallest_proposed_intervention": "Perform one deterministic reference resolution.",
                "expected_observable": "One preparation receipt.",
                "allowed_effect_surface": [],
                "forbidden_effects": list(self.campaign["explicit_non_authorizations"]),
                "required_authority": "NONE_FOR_PREPARATION",
                "resource_cost": {
                    "resource_class": "DETERMINISTIC",
                    "model_calls": 0,
                    "notes": "No semantic model.",
                },
                "expected_information_gain": "Discriminate bounded reentry.",
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
                basis_refs=self.campaign["basis_refs"],
                kind=SELECT,
                reason="reentry fixture",
            )
            if idx == 1:
                self.selection_store.append(selection)
            self.requests[request["request_id"]] = request
            self.selections[request["request_id"]] = selection

        self.runner = BoundedReentryRunner(
            repo=self.repo,
            pool=self.pool,
            campaign_store=self.campaign_store,
            selection_store=self.selection_store,
            preparation_store=self.prep_store,
            reentry_store=self.reentry_store,
        )

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

    def opportunity(
        self,
        oid: str,
        *,
        request_id: str | None = "E1",
    ) -> dict:
        if request_id is None:
            opportunity = build_wake_opportunity(
                campaign=self.campaign,
                seat_id="MAYA",
                opportunity_id=oid,
                opportunity_basis=self.h1,
                request=None,
                selection=None,
                preparation_kind=None,
            )
        else:
            opportunity = build_wake_opportunity(
                campaign=self.campaign,
                seat_id="MAYA",
                opportunity_id=oid,
                opportunity_basis=self.h1,
                request=self.requests[request_id],
                selection=self.selections[request_id],
                preparation_kind="RESOLVE_REFS",
            )
        self.reentry_store.post_opportunity(opportunity)
        return opportunity

    def controller_counts(self) -> dict[str, int]:
        conn = sqlite3.connect(self.controller_db)
        try:
            return {
                "transitions": conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0],
                "outputs": conn.execute("SELECT COUNT(*) FROM outputs").fetchone()[0],
                "receipts": conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0],
            }
        finally:
            conn.close()

    def prep_count(self, request_id: str = "E1") -> int:
        return len(self.prep_store.history(self.campaign["campaign_id"], request_id))

    def test_r1_normal_reentry_one_prep_one_successor_then_dormant(self) -> None:
        self.opportunity("R1")
        before = self.pool.seat_snapshot("MAYA")
        self.assertEqual(before["occupancy_state"], "AVAILABLE")

        receipt = self.runner.run_once("R1")
        after = self.pool.seat_snapshot("MAYA")

        self.assertEqual(receipt["outcome"], "UNIT_COMPLETED")
        self.assertEqual(receipt["work_units_performed"], 1)
        self.assertEqual(self.prep_count(), 1)
        self.assertEqual(after["occupancy_state"], "AVAILABLE")
        self.assertIsNone(after["current_wake_id"])
        self.assertEqual(after["state_version"], before["state_version"] + 1)
        self.assertEqual(
            [e["event_kind"] for e in self.reentry_store.events("R1")],
            [
                "WAKE_ACCEPTED",
                "RECONSTRUCTED",
                "UNIT_STARTED",
                "UNIT_RECEIPT_EMITTED",
                "SUCCESSOR_COMMITTED",
                "DORMANT",
            ],
        )

    def test_r2_no_target_means_no_work_not_invented_task(self) -> None:
        self.opportunity("R2", request_id=None)
        receipt = self.runner.run_once("R2")
        self.assertEqual(receipt["outcome"], "NO_WORK")
        self.assertEqual(receipt["work_units_performed"], 0)
        self.assertEqual(self.prep_count(), 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")

    def test_r3_stale_selected_request_blocks_preparation_and_sleeps(self) -> None:
        self.opportunity("R3")
        self.move_world()
        receipt = self.runner.run_once("R3")
        self.assertEqual(receipt["outcome"], "BLOCKED_STALE")
        self.assertEqual(receipt["work_units_performed"], 0)
        self.assertEqual(self.prep_count(), 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")

    def test_r4_two_opportunities_one_occupant_maximum(self) -> None:
        self.opportunity("R4-A")
        self.opportunity("R4-B", request_id=None)
        entered = threading.Event()
        release = threading.Event()
        result: dict[str, object] = {}

        def hook(phase: str, payload: dict) -> None:
            if phase == "WAKE_ACCEPTED":
                entered.set()
                release.wait(timeout=4)

        def first() -> None:
            result["first"] = self.runner.run_once("R4-A", phase_hook=hook)

        thread = threading.Thread(target=first)
        thread.start()
        self.assertTrue(entered.wait(timeout=3))
        second = self.runner.run_once("R4-B")
        self.assertEqual(second["outcome"], "OCCUPANCY_CONFLICT")
        self.assertEqual(self.pool.seat_snapshot("MAYA")["current_wake_id"], "W-R4-A")
        release.set()
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result["first"]["outcome"], "UNIT_COMPLETED")
        self.assertEqual(self.prep_count(), 1)

    def test_r5_crash_before_unit_has_no_prep_or_successor_and_is_recoverable(self) -> None:
        self.opportunity("R5")
        with self.assertRaises(InjectedReentryCrash):
            self.runner.run_once("R5", inject_crash_at="BEFORE_UNIT")
        self.assertEqual(self.prep_count(), 0)
        self.assertEqual(self.controller_counts()["transitions"], 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "OCCUPIED")

        recovery = self.pool.recover_lease("MAYA", "W-R5", reason="TEST_RECOVERY")
        self.assertEqual(recovery["status"], "RECOVERED")
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")
        self.assertIsNone(self.reentry_store.receipt("R5"))

    def test_r6_crash_after_prep_keeps_artifact_without_seat_successor(self) -> None:
        self.opportunity("R6")
        with self.assertRaises(InjectedReentryCrash):
            self.runner.run_once("R6", inject_crash_at="AFTER_UNIT_BEFORE_COMMIT")
        self.assertEqual(self.prep_count(), 1)
        self.assertEqual(self.controller_counts()["transitions"], 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["state_version"], 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "OCCUPIED")

        self.pool.recover_lease("MAYA", "W-R6", reason="TEST_RECOVERY")
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")

    def test_r7_world_moves_after_unit_receipt_no_successor_admission(self) -> None:
        self.opportunity("R7")

        def hook(phase: str, payload: dict) -> None:
            if phase == "UNIT_RECEIPT_EMITTED":
                self.move_world()

        receipt = self.runner.run_once("R7", phase_hook=hook)
        self.assertEqual(receipt["outcome"], "STALE_AFTER_EFFECT")
        self.assertEqual(receipt["work_units_performed"], 1)
        self.assertEqual(self.prep_count(), 1)
        self.assertEqual(self.controller_counts()["transitions"], 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["state_version"], 0)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")

    def test_r8_same_opportunity_replay_does_not_perform_second_unit(self) -> None:
        self.opportunity("R8")
        first = self.runner.run_once("R8")
        second = self.runner.run_once("R8")

        self.assertEqual(first["outcome"], "UNIT_COMPLETED")
        self.assertTrue(second["idempotent_replay"])
        self.assertEqual(self.prep_count(), 1)
        self.assertEqual(self.controller_counts()["transitions"], 1)

    def test_r9_occupancy_is_temporary_not_seat_identity(self) -> None:
        self.opportunity("R9")
        seen = {}

        def hook(phase: str, payload: dict) -> None:
            if phase == "WAKE_ACCEPTED":
                seen["during"] = self.pool.seat_snapshot("MAYA")

        receipt = self.runner.run_once("R9", phase_hook=hook)
        after = self.pool.seat_snapshot("MAYA")
        self.assertEqual(seen["during"]["occupancy_state"], "OCCUPIED")
        self.assertEqual(after["occupancy_state"], "AVAILABLE")
        self.assertEqual(after["seat_id"], "MAYA")
        self.assertTrue(receipt["occupancy_released"])

    def test_r10_one_wake_does_not_self_extend_to_second_eligible_request(self) -> None:
        self.selection_store.append(self.selections["E2"])
        self.opportunity("R10", request_id="E1")

        projection_before = self.selection_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )
        self.assertEqual(projection_before["selection_count"], 2)

        receipt = self.runner.run_once("R10")
        self.assertEqual(receipt["work_units_performed"], 1)
        self.assertEqual(self.prep_count("E1"), 1)
        self.assertEqual(self.prep_count("E2"), 0)
        projection_after = self.selection_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.campaign["basis_refs"],
        )
        self.assertEqual(projection_after["selection_count"], 2)
        self.assertEqual(self.pool.seat_snapshot("MAYA")["occupancy_state"], "AVAILABLE")


if __name__ == "__main__":
    unittest.main()
