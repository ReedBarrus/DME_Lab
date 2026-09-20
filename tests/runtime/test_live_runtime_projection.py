from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
import http.client
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest

from tools.development_campaign_v0 import CampaignStore, build_campaign, object_sha256
from tools.envelope_selection_v0 import SELECT, SelectionStore, build_selection_event
from tools.goblin_pool import GoblinPool
from tools.local_semantic_operator_v0 import LocalSemanticHarness
from tools.preparation_v0 import PreparationStore, build_receipt
from src.cockpit.live_runtime_projection import (
    RuntimeProjectionServer,
    RuntimeSources,
    build_snapshot,
    iter_changed_snapshots,
)


ROOT = Path(__file__).resolve().parents[2]


def repo_head() -> str:
    import subprocess
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


class LiveRuntimeProjectionPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.controller_db = root / "controller.sqlite3"
        self.campaign_db = root / "campaign.sqlite3"
        self.selection_db = root / "selection.sqlite3"
        self.preparation_db = root / "preparation.sqlite3"
        self.semantic_db = root / "semantic.sqlite3"

        self.pool = GoblinPool(self.controller_db, ROOT)
        self.pool.initialize_fixture()

        self.campaign_store = CampaignStore(self.campaign_db)
        self.selection_store = SelectionStore(self.campaign_store, self.selection_db)
        self.preparation_store = PreparationStore(
            self.campaign_store,
            self.selection_store,
            self.preparation_db,
        )

        self.head = repo_head()
        self.basis = [f"git:{self.head}"]
        self.campaign = build_campaign({
            "campaign_id": "LIVE_FIXTURE_001",
            "title": "Live runtime projection fixture",
            "basis_refs": self.basis,
            "objective": "Pressure live read-only runtime projection.",
            "claim_ceiling": "Projection only.",
            "target_objects": ["LIVE_RUNTIME_PROJECTION_001"],
            "unresolved_relations": [
                {"relation_id": "R1", "statement": "DISPLAYED_STATE != AUTHORITY"},
            ],
            "pressure_points": ["Change durable state outside Cockpit."],
            "dependency_edges": [],
            "proposal_allowance": {
                "max_candidates": 1,
                "max_model_calls": 0,
                "allowed_resource_classes": ["DETERMINISTIC"],
            },
            "completion_criteria": ["Live projection change is observed."],
            "stop_conditions": ["Projection attempts a source write."],
            "explicit_non_authorizations": [
                "NO_EXECUTION",
                "NO_AUTHORITY",
                "NO_STANDING_CHANGE",
            ],
        })
        self.campaign_store.post_campaign(self.campaign)
        relation = self.campaign["unresolved_relations"][0]
        self.request = {
            "schema": "execution_envelope_request_v0",
            "request_id": "E-LIVE-1",
            "campaign_id": self.campaign["campaign_id"],
            "campaign_sha256": object_sha256(self.campaign),
            "seat_id": "LABBOIB",
            "object_under_pressure": "LIVE_RUNTIME_PROJECTION_001",
            "unresolved_relation_id": relation["relation_id"],
            "unresolved_relation": relation["statement"],
            "smallest_proposed_intervention": "Observe one external durable write.",
            "expected_observable": "Cockpit stream advances without refresh.",
            "allowed_effect_surface": [],
            "forbidden_effects": list(self.campaign["explicit_non_authorizations"]),
            "required_authority": "NONE_FOR_OBSERVATION",
            "resource_cost": {
                "resource_class": "DETERMINISTIC",
                "model_calls": 0,
                "notes": "Read-only projection pressure.",
            },
            "expected_information_gain": "Discriminate live projection from static display.",
            "stop_conditions": list(self.campaign["stop_conditions"]),
            "packet_status": "CANDIDATE_REQUEST",
            "authorization_effect": "NONE",
            "execution_effect": "NONE",
        }
        self.campaign_store.lodge_request(self.request)

        self.semantic = LocalSemanticHarness(self.pool, self.semantic_db)
        self.semantic.register_resource(
            resource_id="QWEN_LOCAL_PRIMARY",
            model_id="qwen-fixture",
            base_url="http://127.0.0.1:1234/v1",
            status="AVAILABLE",
        )

        self.sources = RuntimeSources(
            repo=ROOT,
            controller_db=self.controller_db,
            campaign_db=self.campaign_db,
            selection_db=self.selection_db,
            preparation_db=self.preparation_db,
            semantic_db=self.semantic_db,
            comparison_basis_refs=("git:HEAD",),
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def controller_counts(self) -> tuple[int, int, int]:
        conn = sqlite3.connect(self.controller_db)
        try:
            return (
                conn.execute("SELECT COUNT(*) FROM seats").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM wakes").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0],
            )
        finally:
            conn.close()

    def add_selection_and_prep(self) -> None:
        selection = build_selection_event(
            campaign=self.campaign,
            request=self.request,
            selection_id="SEL-LIVE-1",
            basis_refs=self.basis,
            kind=SELECT,
            reason="live projection fixture",
        )
        self.selection_store.append(selection)
        receipt = build_receipt(
            campaign=self.campaign,
            request=self.request,
            selection=selection,
            preparation_id="PREP-LIVE-1",
            prepared_by="MAYA",
            preparation_kind="RESOLVE_REFS",
            preparation_basis_refs=self.basis,
            input_refs=["request://E-LIVE-1"],
            output_refs=["refs://resolved"],
            mechanical_status="PASS",
        )
        self.preparation_store.append(receipt, current_basis_refs=self.basis)

    def start_server(self) -> tuple[RuntimeProjectionServer, threading.Thread]:
        server = RuntimeProjectionServer(("127.0.0.1", 0), self.sources, 0.03)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread

    def read_sse_event(self, response: http.client.HTTPResponse) -> dict:
        data = None
        while True:
            line = response.fp.readline().decode("utf-8")
            if not line:
                raise AssertionError("SSE stream closed")
            if line.startswith("data: "):
                data = json.loads(line[6:])
            if line == "\n":
                if data is not None:
                    return data

    def test_l1_baseline_is_read_only_and_non_authoritative(self) -> None:
        before = self.controller_counts()
        snapshot = build_snapshot(self.sources)
        after = self.controller_counts()

        self.assertEqual(before, after)
        state = snapshot["state"]
        self.assertEqual(state["source_of_truth"], "DURABLE_RUNTIME_STORES")
        self.assertEqual(state["projection_effect"], "NONE")
        self.assertEqual(state["authority_effect"], "NONE")
        self.assertEqual(state["execution_effect"], "NONE")
        self.assertEqual(state["standing_effect"], "NONE")
        self.assertEqual(state["projection_status"], "AVAILABLE")

    def test_l2_open_stream_advances_after_external_seat_write_without_refresh(self) -> None:
        server, thread = self.start_server()
        conn = http.client.HTTPConnection(
            "127.0.0.1",
            server.server_address[1],
            timeout=4,
        )
        try:
            conn.request("GET", "/runtime/events")
            response = conn.getresponse()
            self.assertEqual(response.status, 200)
            initial = self.read_sse_event(response)
            self.assertEqual(
                initial["state"]["active_operations"]["occupied_seats"],
                [],
            )

            self.pool.start_wake("GOB_A", "W-LIVE-EXTERNAL")

            changed = self.read_sse_event(response)
            self.assertNotEqual(initial["state_sha256"], changed["state_sha256"])
            occupied = changed["state"]["active_operations"]["occupied_seats"]
            self.assertEqual([seat["seat_id"] for seat in occupied], ["GOB_A"])
            self.assertEqual(
                changed["state"]["active_operations"]["active_wakes"][0]["wake_id"],
                "W-LIVE-EXTERNAL",
            )
        finally:
            conn.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_l3_external_selection_and_prep_appear_in_projection(self) -> None:
        before = build_snapshot(self.sources)
        self.assertEqual(before["state"]["current_selection"], [])
        self.assertEqual(before["state"]["preparation_receipts"], [])

        self.add_selection_and_prep()
        after = build_snapshot(self.sources)

        self.assertNotEqual(before["state_sha256"], after["state_sha256"])
        self.assertEqual(
            [e["event_json"]["request_id"] for e in after["state"]["selection_history"]],
            ["E-LIVE-1"],
        )
        self.assertEqual(
            [r["receipt_json"]["prepared_by"] for r in after["state"]["preparation_receipts"]],
            ["MAYA"],
        )
        readiness = after["state"]["preparation_readiness"][0]
        self.assertEqual(readiness["request_id"], "E-LIVE-1")
        self.assertEqual(readiness["request_applicability"], "CURRENT")
        self.assertEqual(readiness["readiness"], "PREP_INCOMPLETE")

    def test_l4_external_active_operation_is_projected_not_created(self) -> None:
        self.pool.start_wake("GOB_B", "W-LIVE-B")
        snapshot = build_snapshot(self.sources)
        active = snapshot["state"]["active_operations"]

        self.assertEqual([s["seat_id"] for s in active["occupied_seats"]], ["GOB_B"])
        self.assertEqual([w["wake_id"] for w in active["active_wakes"]], ["W-LIVE-B"])
        self.assertEqual(snapshot["state"]["projection_effect"], "NONE")

    def test_l5_external_resource_lease_change_is_visible_without_authority_inference(self) -> None:
        conn = sqlite3.connect(self.semantic_db)
        try:
            conn.execute(
                """
                INSERT INTO model_leases(
                    lease_id,resource_id,seat_id,request_id,status
                ) VALUES(?,?,?,?,?)
                """,
                ("LEASE-LIVE", "QWEN_LOCAL_PRIMARY", "MAYA", "SR-LIVE", "ACTIVE"),
            )
            conn.commit()
        finally:
            conn.close()

        state = build_snapshot(self.sources)["state"]
        self.assertEqual(len(state["active_model_leases"]), 1)
        lease = state["active_model_leases"][0]
        self.assertEqual(lease["seat_id"], "MAYA")
        self.assertEqual(state["authority_effect"], "NONE")

    def test_l6_missing_configured_source_is_partial_not_healthy_empty(self) -> None:
        sources = RuntimeSources(
            repo=ROOT,
            controller_db=self.controller_db,
            campaign_db=self.campaign_db,
            selection_db=self.selection_db,
            preparation_db=self.preparation_db,
            semantic_db=Path(self.tmp.name) / "missing-semantic.sqlite3",
            comparison_basis_refs=("git:HEAD",),
        )
        state = build_snapshot(sources)["state"]
        self.assertEqual(state["projection_status"], "PARTIAL")
        semantic_status = next(s for s in state["sources"] if s["source"] == "semantic")
        self.assertEqual(semantic_status["status"], "UNAVAILABLE")
        self.assertEqual(state["model_resources"], [])

    def test_l7_runtime_http_write_methods_are_rejected_and_state_unchanged(self) -> None:
        before = self.controller_counts()
        server, thread = self.start_server()
        conn = http.client.HTTPConnection(
            "127.0.0.1",
            server.server_address[1],
            timeout=3,
        )
        try:
            conn.request("POST", "/runtime/snapshot.json", body=b"{}")
            response = conn.getresponse()
            self.assertEqual(response.status, 405)
            response.read()
        finally:
            conn.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

        self.assertEqual(before, self.controller_counts())

    def test_l8_polling_does_not_create_state_changes(self) -> None:
        first = build_snapshot(self.sources)
        time.sleep(0.02)
        second = build_snapshot(self.sources)
        self.assertNotEqual(first["observed_at"], second["observed_at"])
        self.assertEqual(first["state_sha256"], second["state_sha256"])

        stop = threading.Event()
        stream = iter_changed_snapshots(
            self.sources,
            poll_interval=0.02,
            stop_event=stop,
        )
        initial = next(stream)
        self.assertEqual(initial["state_sha256"], first["state_sha256"])

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(next, stream)
            with self.assertRaises(TimeoutError):
                future.result(timeout=0.12)
            self.pool.start_wake("GOB_C", "W-LIVE-C")
            changed = future.result(timeout=2)
            self.assertNotEqual(initial["state_sha256"], changed["state_sha256"])
        stop.set()

    def test_l9_projection_declares_cross_store_atomicity_unestablished(self) -> None:
        state = build_snapshot(self.sources)["state"]
        self.assertEqual(state["cross_store_atomicity"], "NOT_ESTABLISHED")
        self.assertEqual(
            state["standing_movement_history"]["status"],
            "UNAVAILABLE_IN_CURRENT_CAMPAIGN_STORE",
        )


if __name__ == "__main__":
    unittest.main()
