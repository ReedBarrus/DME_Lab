from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
HOME_DIR = ROOT / "src" / "home" / "home_capture_v0"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONSUMER = load_module(
    "bounded_read_consumer_v0", ROOT / "src" / "home" / "bounded_read_consumer_v0.py"
)
SERVER = load_module("home_capture_server_for_consumer", HOME_DIR / "server.py")


class BoundedReadConsumerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name) / "data"
        self.server = SERVER.create_server(
            "127.0.0.1", 0, self.data_dir, desktop_notifications=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.temp_dir.cleanup()

    def post(self, path: str, payload: dict[str, object]):
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=3) as response:
            return json.loads(response.read())

    def consume(self):
        return CONSUMER.consume_bridge(
            CONSUMER.read_packet(self.data_dir / "agent_bridge" / "chat_now.json"),
            CONSUMER.read_packet(self.data_dir / "agent_bridge" / "due_events.json"),
        )

    def test_consumer_preserves_unknown_without_source_or_expected_lineage_input(self) -> None:
        result = self.consume()
        self.assertEqual(result["projection_authority"], "DERIVED_FROM_HOME")
        self.assertEqual(result["commitment_lineage"], CONSUMER.UNKNOWN)
        self.assertEqual(
            result["unknown_not_projected"], list(CONSUMER.LINEAGE_FACTS_NOT_PROJECTED)
        )
        self.assertFalse(result["execution_authority_inferred"])
        self.assertEqual(result["events"], [])
        self.assertEqual(result["incorrect_inferences"], [])

    def test_isolated_event_standing_sequence_survives_projection_consumption(self) -> None:
        created = self.post(
            "/api/capture",
            {"mode": "commit", "raw_text": "fixture specification A",
             "recurrence_type": "WEEKLY_PATTERN", "weekly_days": ["WED", "FRI"],
             "temporal_placement": "MORNING"},
        )
        commitment = created["commitment"]
        event = self.post(
            "/api/chat-home/future-note",
            {"due_at": "2035-01-01T00:00:00Z", "raw_instruction": "immutable fixture note",
             "context_refs": ["fixture:bounded"],
             "commitment_id": commitment["commitment_id"]},
        )
        event_id = event["event_id"]
        original_specification = event["specification_id"]
        original_instruction = event["raw_instruction"]

        current = self.consume()
        current_event = next(item for item in current["events"] if item["event_id"] == event_id)
        self.assertEqual(current_event["reference_standing"], "CURRENT")
        self.assertFalse(current_event["due_grants_execution_authority"])

        amended = self.post(
            f"/api/commitments/{quote(commitment['commitment_id'], safe='')}/amend",
            {"amendment_kind": "RECORDING_CORRECTION",
             "raw_text": "fixture specification B", "raw_amendment_reason": "fixture correction",
             "recurrence_type": "WEEKLY_PATTERN", "weekly_days": ["MON"],
             "temporal_placement": "EVENING"},
        )
        superseded = self.consume()
        superseded_event = next(
            item for item in superseded["events"] if item["event_id"] == event_id
        )
        self.assertEqual(superseded_event["reference_standing"], "SPECIFICATION_SUPERSEDED")
        self.assertEqual(superseded_event["specification_id"], original_specification)
        self.assertEqual(
            superseded_event["current_specification_id"],
            amended["specification"]["specification_id"],
        )
        self.assertEqual(superseded_event["raw_instruction"], original_instruction)
        self.assertTrue(superseded_event["current_applicability_requires_adjudication"])
        self.assertFalse(superseded_event["due_grants_execution_authority"])

        self.post(
            f"/api/commitments/{quote(commitment['commitment_id'], safe='')}/resolve",
            {"mode": "RELEASED", "raw_feedback": "fixture closure"},
        )
        closed = self.consume()
        closed_event = next(item for item in closed["events"] if item["event_id"] == event_id)
        self.assertEqual(closed_event["reference_standing"], "COMMITMENT_CLOSED")
        self.assertEqual(closed_event["specification_id"], original_specification)
        self.assertEqual(closed_event["raw_instruction"], original_instruction)
        self.assertEqual(closed_event["status"], "SCHEDULED")
        self.assertFalse(closed_event["due_grants_execution_authority"])
        self.assertEqual(
            [current["relevant_source_revision"], superseded["relevant_source_revision"],
             closed["relevant_source_revision"]],
            [1, 2, 3],
        )

    def test_consumer_rejects_cross_packet_source_disagreement(self) -> None:
        chat = CONSUMER.read_packet(self.data_dir / "agent_bridge" / "chat_now.json")
        due = CONSUMER.read_packet(self.data_dir / "agent_bridge" / "due_events.json")
        due["relevant_source_revision"] += 1
        with self.assertRaisesRegex(CONSUMER.ContractError, "bridge_envelope_disagreement"):
            CONSUMER.consume_bridge(chat, due)


if __name__ == "__main__":
    unittest.main()
