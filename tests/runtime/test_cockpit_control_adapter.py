from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from src.cockpit.control_adapter import (
    CockpitControlAdapter,
    CockpitControlError,
    ControlSources,
)
from tools.bounded_reentry_v0 import BoundedReentryRunner, ReentryStore
from tools.development_campaign_v0 import (
    CampaignStore,
    build_campaign,
    object_sha256,
)
from tools.envelope_selection_v0 import (
    RELEASE as SELECTION_RELEASE,
    SelectionStore,
    build_selection_event,
)
from tools.goblin_pool import GoblinPool
from tools.preparation_assignment_v0 import (
    AssignmentStore,
    build_satisfaction,
)
from tools.preparation_v0 import PreparationStore
from tools.wake_source_v0 import WakeSourceStore


ROOT = Path(__file__).resolve().parents[2]


class CockpitControlAdapterPressure(unittest.TestCase):
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
        self.prep_db = root / "preparation.sqlite3"
        self.assignment_db = root / "assignment.sqlite3"
        self.reentry_db = root / "reentry.sqlite3"
        self.wake_db = root / "wake-source.sqlite3"

        self.pool = GoblinPool(self.controller_db, self.repo)
        self.pool.initialize_fixture()
        self.pool.bind_external_seat(
            seat_id="MAYA",
            cursor_event_id="EV-MAYA-GENESIS",
            working_state={"seat_id": "MAYA", "mode": "DORMANT"},
            source_events=[
                {
                    "event_id": "EV-MAYA-GENESIS",
                    "kind": "SEAT_GENESIS",
                    "source": "COCKPIT_CONTROL_ADAPTER_001",
                }
            ],
            policy_ref="policy:MAYA:cockpit-control-v0",
            operator_profile_ref="operators:MAYA:prep-only-v0",
            authority_profile_ref="authority:MAYA:none-v0",
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
            db_path=self.wake_db,
        )

        raw = json.loads(
            (
                ROOT
                / "docs"
                / "campaigns"
                / "candidates"
                / "COCKPIT_OPERATING_SPACE_001.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(raw["campaign_id"], "COCKPIT_OPERATING_SPACE_001")
        spec = {
            "campaign_id": raw["campaign_id"],
            "title": raw["title"],
            "basis_refs": self.basis,
            "objective": raw["objective"],
            "claim_ceiling": raw["claim_ceiling"],
            "target_objects": raw["target_objects"],
            "unresolved_relations": raw["unresolved_relations"],
            "pressure_points": raw["pressure_points"],
            "dependency_edges": raw["dependency_edges"],
            "proposal_allowance": {
                "max_candidates": raw["proposal_allowance"]["max_candidates"],
                "max_model_calls": raw["proposal_allowance"]["max_model_calls"],
                "allowed_resource_classes": raw["proposal_allowance"][
                    "allowed_resource_classes"
                ],
            },
            "completion_criteria": raw["completion_criteria"],
            "stop_conditions": raw["stop_conditions"],
            "explicit_non_authorizations": raw["explicit_non_authorizations"],
        }
        self.campaign = build_campaign(spec)
        self.campaign_store.post_campaign(self.campaign)

        self.requests: dict[str, dict] = {}
        for idx, relation in enumerate(self.campaign["unresolved_relations"][:2], 1):
            request = {
                "schema": "execution_envelope_request_v0",
                "request_id": f"COS-E{idx}",
                "campaign_id": self.campaign["campaign_id"],
                "campaign_sha256": object_sha256(self.campaign),
                "seat_id": "LABBOIB",
                "object_under_pressure": self.campaign["target_objects"][idx - 1],
                "unresolved_relation_id": relation["relation_id"],
                "unresolved_relation": relation["statement"],
                "smallest_proposed_intervention": (
                    "Exercise the smallest typed Cockpit control gesture."
                ),
                "expected_observable": (
                    "Whether one exact already-qualified object is retained "
                    "without direct controller mutation."
                ),
                "allowed_effect_surface": [],
                "forbidden_effects": list(
                    self.campaign["explicit_non_authorizations"]
                ),
                "required_authority": "EXECUTIVE_AUTHORIZATION_REQUIRED",
                "resource_cost": {
                    "resource_class": "DETERMINISTIC",
                    "model_calls": 0,
                    "notes": "Cockpit control dogfood request.",
                },
                "expected_information_gain": (
                    "Measure whether Cockpit control preserves the causal membrane."
                ),
                "stop_conditions": list(self.campaign["stop_conditions"]),
                "packet_status": "CANDIDATE_REQUEST",
                "authorization_effect": "NONE",
                "execution_effect": "NONE",
            }
            self.campaign_store.lodge_request(request)
            self.requests[request["request_id"]] = request

        self.adapter = CockpitControlAdapter(
            ControlSources(
                repo=self.repo,
                campaign_db=self.campaign_db,
                selection_db=self.selection_db,
                preparation_db=self.prep_db,
                assignment_db=self.assignment_db,
                reentry_db=self.reentry_db,
                wake_source_db=self.wake_db,
                comparison_basis_refs=("git:HEAD",),
            )
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

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def head(self) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout.strip()

    def file_sha(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def commit_intent(self, intent: dict) -> tuple[dict, dict]:
        preview = self.adapter.build_preview(intent)
        result = self.adapter.commit(
            preview=preview["preview"],
            preview_sha256=preview["preview_sha256"],
            confirmed_by="REED",
        )
        return preview, result

    def focus(self, request_id: str, gesture: str) -> dict:
        _, result = self.commit_intent(
            {
                "verb": "FOCUS",
                "gesture_id": gesture,
                "campaign_id": self.campaign["campaign_id"],
                "request_id": request_id,
                "reason": "dogfood focus",
            }
        )
        return result

    def assign(
        self,
        request_id: str,
        gesture: str,
        *,
        seat_id: str = "MAYA",
        preparation_kind: str = "RESOLVE_REFS",
    ) -> dict:
        _, result = self.commit_intent(
            {
                "verb": "ASSIGN",
                "gesture_id": gesture,
                "campaign_id": self.campaign["campaign_id"],
                "request_id": request_id,
                "seat_id": seat_id,
                "preparation_kind": preparation_kind,
                "reason": "dogfood assignment",
            }
        )
        return result

    def ring(self, assignment_id: str, gesture: str) -> dict:
        _, result = self.commit_intent(
            {
                "verb": "RING",
                "gesture_id": gesture,
                "campaign_id": self.campaign["campaign_id"],
                "assignment_id": assignment_id,
                "reason": "dogfood bell",
            }
        )
        return result

    def current_assignment(self, assignment_id: str) -> dict:
        return self.assignment_store._load_assignment(assignment_id)

    def prep_receipt(self, preparation_id: str) -> dict:
        conn = sqlite3.connect(self.prep_db)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT receipt_json FROM preparation_receipts WHERE preparation_id=?",
                (preparation_id,),
            ).fetchone()
        finally:
            conn.close()
        self.assertIsNotNone(row)
        return json.loads(row["receipt_json"])

    def test_c1_focus_preview_then_exact_commit(self) -> None:
        intent = {
            "verb": "FOCUS",
            "gesture_id": "C1",
            "campaign_id": self.campaign["campaign_id"],
            "request_id": "COS-E1",
            "reason": "focus COS-R1",
        }
        preview = self.adapter.build_preview(intent)

        self.assertEqual(
            self.selection_store.history(self.campaign["campaign_id"]),
            [],
        )
        event = preview["preview"]["durable_objects"][0]
        self.assertEqual(event["schema"], "envelope_selection_v0")
        self.assertEqual(event["selected_by"], "REED")
        self.assertEqual(event["authorization_effect"], "NONE")
        self.assertEqual(event["execution_effect"], "NONE")

        result = self.adapter.commit(
            preview=preview["preview"],
            preview_sha256=preview["preview_sha256"],
            confirmed_by="REED",
        )
        self.assertEqual(result["verb"], "FOCUS")
        self.assertEqual(
            len(self.selection_store.history(self.campaign["campaign_id"])),
            1,
        )

    def test_c2_assign_preview_then_exact_commit(self) -> None:
        self.focus("COS-E1", "C2-FOCUS")
        intent = {
            "verb": "ASSIGN",
            "gesture_id": "C2",
            "campaign_id": self.campaign["campaign_id"],
            "request_id": "COS-E1",
            "seat_id": "MAYA",
            "preparation_kind": "RESOLVE_REFS",
            "reason": "Maya gets one clipboard",
        }
        preview = self.adapter.build_preview(intent)
        event = preview["preview"]["durable_objects"][0]

        self.assertEqual(
            self.assignment_store.history(self.campaign["campaign_id"]),
            [],
        )
        self.assertEqual(event["seat_id"], "MAYA")
        self.assertEqual(event["wake_effect"], "NONE")
        self.assertEqual(event["priority_effect"], "NONE")

        result = self.adapter.commit(
            preview=preview["preview"],
            preview_sha256=preview["preview_sha256"],
            confirmed_by="REED",
        )
        self.assertEqual(result["verb"], "ASSIGN")
        row = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )["assignment_projection"][0]
        self.assertEqual(row["assignment_state"], "OUTSTANDING")

    def test_c3_release_is_exact_assignment_release_only(self) -> None:
        self.focus("COS-E1", "C3-FOCUS")
        assignment_result = self.assign("COS-E1", "C3-ASSIGN")
        assignment_id = assignment_result["retained_objects"][0]["id"]

        preview = self.adapter.build_preview(
            {
                "verb": "RELEASE",
                "gesture_id": "C3-RELEASE",
                "campaign_id": self.campaign["campaign_id"],
                "assignment_id": assignment_id,
                "reason": "withdraw exact allocation",
            }
        )
        event = preview["preview"]["durable_objects"][0]
        self.assertEqual(event["assignment_kind"], "ASSIGNMENT_RELEASED")
        self.assertEqual(event["wake_effect"], "NONE")

        self.adapter.commit(
            preview=preview["preview"],
            preview_sha256=preview["preview_sha256"],
            confirmed_by="REED",
        )
        projection = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )
        row = next(
            r
            for r in projection["assignment_projection"]
            if r["assignment_id"] == assignment_id
        )
        self.assertEqual(row["assignment_state"], "RELEASED")
        self.assertIsNone(row["satisfaction_id"])

    def test_c4_ring_retains_exact_bell_and_opportunity_but_does_not_wake(self) -> None:
        self.focus("COS-E1", "C4-FOCUS")
        assignment = self.assign("COS-E1", "C4-ASSIGN")
        assignment_id = assignment["retained_objects"][0]["id"]

        controller_before = self.file_sha(self.controller_db)
        preview = self.adapter.build_preview(
            {
                "verb": "RING",
                "gesture_id": "C4-RING",
                "campaign_id": self.campaign["campaign_id"],
                "assignment_id": assignment_id,
                "reason": "ring exact sticky note",
            }
        )
        self.assertEqual(
            [obj["schema"] for obj in preview["preview"]["durable_objects"]],
            ["manual_bell_v0", "wake_opportunity_v0"],
        )
        result = self.adapter.commit(
            preview=preview["preview"],
            preview_sha256=preview["preview_sha256"],
            confirmed_by="REED",
        )

        self.assertEqual(result["verb"], "RING")
        self.assertEqual(self.file_sha(self.controller_db), controller_before)
        self.assertEqual(
            self.pool.seat_snapshot("MAYA")["occupancy_state"],
            "AVAILABLE",
        )
        self.assertEqual(len(self.reentry_store.events("CCA-W-C4-RING")), 0)
        self.assertIsNotNone(self.wake_store.bell("CCA-B-C4-RING"))

    def test_c5_confirmation_and_exact_preview_identity_are_required(self) -> None:
        preview = self.adapter.build_preview(
            {
                "verb": "FOCUS",
                "gesture_id": "C5",
                "campaign_id": self.campaign["campaign_id"],
                "request_id": "COS-E1",
                "reason": None,
            }
        )
        with self.assertRaises(CockpitControlError):
            self.adapter.commit(
                preview=preview["preview"],
                preview_sha256=preview["preview_sha256"],
                confirmed_by="MAYA",
            )
        with self.assertRaises(CockpitControlError):
            self.adapter.commit(
                preview=preview["preview"],
                preview_sha256="0" * 64,
                confirmed_by="REED",
            )
        self.assertEqual(
            self.selection_store.history(self.campaign["campaign_id"]),
            [],
        )

    def test_c6_world_move_makes_preview_stale_before_commit(self) -> None:
        preview = self.adapter.build_preview(
            {
                "verb": "FOCUS",
                "gesture_id": "C6",
                "campaign_id": self.campaign["campaign_id"],
                "request_id": "COS-E1",
                "reason": "will stale",
            }
        )
        (self.repo / "fixture.txt").write_text("H2\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "fixture.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "H2"], check=True)

        with self.assertRaises(CockpitControlError):
            self.adapter.commit(
                preview=preview["preview"],
                preview_sha256=preview["preview_sha256"],
                confirmed_by="REED",
            )
        self.assertEqual(
            self.selection_store.history(self.campaign["campaign_id"]),
            [],
        )

    def test_c7_two_eligible_assignments_ring_only_named_assignment(self) -> None:
        self.focus("COS-E1", "C7-F1")
        self.focus("COS-E2", "C7-F2")
        a1 = self.assign("COS-E1", "C7-A1", seat_id="MAYA")
        a2 = self.assign("COS-E2", "C7-A2", seat_id="COMMANDER")
        a1_id = a1["retained_objects"][0]["id"]
        a2_id = a2["retained_objects"][0]["id"]

        self.ring(a1_id, "C7-BELL")

        self.assertIsNotNone(self.wake_store.bell("CCA-B-C7-BELL"))
        self.assertIsNone(self.wake_store.bell("CCA-B-C7-OTHER"))
        conn = sqlite3.connect(self.wake_db)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT assignment_id FROM manual_bells ORDER BY seq"
            ).fetchall()
        finally:
            conn.close()
        self.assertEqual([row["assignment_id"] for row in rows], [a1_id])
        projection = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )
        self.assertTrue(
            next(
                r for r in projection["assignment_projection"]
                if r["assignment_id"] == a2_id
            )["wake_eligible"]
        )

    def test_c8_two_maya_assignments_do_not_create_queue_or_second_bell(self) -> None:
        self.focus("COS-E1", "C8-F1")
        self.focus("COS-E2", "C8-F2")
        a1 = self.assign("COS-E1", "C8-A1", seat_id="MAYA")
        a2 = self.assign("COS-E2", "C8-A2", seat_id="MAYA")
        a1_id = a1["retained_objects"][0]["id"]
        a2_id = a2["retained_objects"][0]["id"]

        self.ring(a1_id, "C8-RING")

        conn = sqlite3.connect(self.wake_db)
        conn.row_factory = sqlite3.Row
        try:
            bells = conn.execute(
                "SELECT assignment_id FROM manual_bells ORDER BY seq"
            ).fetchall()
        finally:
            conn.close()
        self.assertEqual([row["assignment_id"] for row in bells], [a1_id])
        self.assertNotEqual(a1_id, a2_id)

    def test_c9_adapter_rejects_unqualified_verbs_and_extra_intent_fields(self) -> None:
        with self.assertRaises(CockpitControlError):
            self.adapter.build_preview(
                {
                    "verb": "AUTHORIZE",
                    "gesture_id": "C9-AUTH",
                    "campaign_id": self.campaign["campaign_id"],
                    "request_id": "COS-E1",
                }
            )
        with self.assertRaises(CockpitControlError):
            self.adapter.build_preview(
                {
                    "verb": "FOCUS",
                    "gesture_id": "C9-EXTRA",
                    "campaign_id": self.campaign["campaign_id"],
                    "request_id": "COS-E1",
                    "authority_effect": "GRANT",
                }
            )

    def test_c10_all_four_control_verbs_leave_controller_store_untouched(self) -> None:
        before = self.file_sha(self.controller_db)
        self.focus("COS-E1", "C10-F")
        assignment = self.assign("COS-E1", "C10-A")
        assignment_id = assignment["retained_objects"][0]["id"]
        self.ring(assignment_id, "C10-B")

        self.assertEqual(self.file_sha(self.controller_db), before)

        # Release another independent assignment to exercise the fourth verb
        # without invalidating the bell specimen above.
        self.focus("COS-E2", "C10-F2")
        second = self.assign("COS-E2", "C10-A2")
        second_id = second["retained_objects"][0]["id"]
        self.commit_intent(
            {
                "verb": "RELEASE",
                "gesture_id": "C10-R",
                "campaign_id": self.campaign["campaign_id"],
                "assignment_id": second_id,
                "reason": "release second clipboard",
            }
        )
        self.assertEqual(self.file_sha(self.controller_db), before)

    def test_c11_ring_then_external_reentry_proves_adapter_did_not_run_maya(self) -> None:
        self.focus("COS-E1", "C11-F")
        assignment_result = self.assign("COS-E1", "C11-A")
        assignment_id = assignment_result["retained_objects"][0]["id"]
        ring_result = self.ring(assignment_id, "C11-B")
        opportunity_id = next(
            item["id"]
            for item in ring_result["retained_objects"]
            if item["kind"] == "wake_opportunity_v0"
        )

        self.assertEqual(
            self.pool.seat_snapshot("MAYA")["occupancy_state"],
            "AVAILABLE",
        )
        self.assertEqual(
            len(self.prep_store.history(self.campaign["campaign_id"], "COS-E1")),
            0,
        )

        reentry = self.runner.run_once(opportunity_id)
        self.assertEqual(reentry["work_units_performed"], 1)
        self.assertEqual(
            self.pool.seat_snapshot("MAYA")["occupancy_state"],
            "AVAILABLE",
        )
        receipt = self.prep_receipt(reentry["preparation_receipt_id"])

        assignment = self.current_assignment(assignment_id)
        satisfaction = build_satisfaction(
            assignment=assignment,
            preparation_receipt=receipt,
            satisfaction_id="SAT-C11",
        )
        self.assignment_store.append_satisfaction(satisfaction)
        projected = self.assignment_store.projection(
            self.campaign["campaign_id"],
            current_basis_refs=self.basis,
        )
        row = next(
            r
            for r in projected["assignment_projection"]
            if r["assignment_id"] == assignment_id
        )
        self.assertEqual(row["assignment_state"], "SATISFIED")
        self.assertFalse(row["wake_eligible"])

    def test_c12_selection_change_after_assign_preview_forces_repreview(self) -> None:
        self.focus("COS-E1", "C12-F")
        preview = self.adapter.build_preview(
            {
                "verb": "ASSIGN",
                "gesture_id": "C12-A",
                "campaign_id": self.campaign["campaign_id"],
                "request_id": "COS-E1",
                "seat_id": "MAYA",
                "preparation_kind": "RESOLVE_REFS",
                "reason": "stale after focus release",
            }
        )
        selection = self.selection_store.current_set(
            self.campaign["campaign_id"]
        )[0]
        release = build_selection_event(
            campaign=self.campaign,
            request=self.requests["COS-E1"],
            selection_id="SEL-C12-RELEASE",
            basis_refs=self.basis,
            kind=SELECTION_RELEASE,
            reason="invalidate adapter preview",
        )
        self.selection_store.append(release)

        with self.assertRaises(CockpitControlError):
            self.adapter.commit(
                preview=preview["preview"],
                preview_sha256=preview["preview_sha256"],
                confirmed_by="REED",
            )
        self.assertEqual(
            self.assignment_store.history(self.campaign["campaign_id"]),
            [],
        )


    def test_c13_ring_preview_rejects_non_resolve_refs_assignment(self) -> None:
        self.focus("COS-E1", "C13-F")
        assignment = self.assign(
            "COS-E1",
            "C13-A",
            preparation_kind="DRAFT_PACKET",
        )
        assignment_id = assignment["retained_objects"][0]["id"]

        with self.assertRaises(CockpitControlError):
            self.adapter.build_preview(
                {
                    "verb": "RING",
                    "gesture_id": "C13-R",
                    "campaign_id": self.campaign["campaign_id"],
                    "assignment_id": assignment_id,
                    "reason": "pressure perceptual affordance against exact preview",
                }
            )


if __name__ == "__main__":
    unittest.main()
