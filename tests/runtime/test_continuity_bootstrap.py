from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "continuity_bootstrap_tool", ROOT / "tools" / "continuity.py"
)
assert SPEC and SPEC.loader
CONTINUITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTINUITY)


class ContinuityBootstrapTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.continuity_dir = Path(self.temp_dir.name) / "continuity"
        self.cursors_dir = self.continuity_dir / "cursors"
        self.cursors_dir.mkdir(parents=True)
        self.events_path = self.continuity_dir / "events.jsonl"
        self.events = [
            {"event_id": f"CE-{index:06d}", "summary": f"event {index}"}
            for index in range(1, 4)
        ]
        self.events_path.write_text(
            "".join(json.dumps(event) + "\n" for event in self.events), encoding="utf-8"
        )
        self.original_paths = (
            CONTINUITY.CONTINUITY_DIR, CONTINUITY.EVENTS_PATH, CONTINUITY.CURSORS_DIR
        )
        CONTINUITY.CONTINUITY_DIR = self.continuity_dir
        CONTINUITY.EVENTS_PATH = self.events_path
        CONTINUITY.CURSORS_DIR = self.cursors_dir
        self.write_fresh_cursor()

    def tearDown(self) -> None:
        (CONTINUITY.CONTINUITY_DIR, CONTINUITY.EVENTS_PATH,
         CONTINUITY.CURSORS_DIR) = self.original_paths
        self.temp_dir.cleanup()

    @property
    def cursor_path(self) -> Path:
        return self.cursors_dir / "test-consumer.json"

    def write_fresh_cursor(self) -> None:
        self.cursor_path.write_text(
            json.dumps({"consumer": "test-consumer", "cursor_state": "UNINITIALIZED",
                        "last_seen_event_id": None}, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def capture(function, args) -> list[dict[str, object]]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            function(args)
        return [json.loads(line) for line in output.getvalue().splitlines() if line]

    def bootstrap(self, mode: str, event_id: str | None = None) -> dict[str, object]:
        output = self.capture(
            CONTINUITY.command_bootstrap,
            argparse.Namespace(consumer="test-consumer", mode=mode, event_id=event_id),
        )
        return output[0]

    def delta(self) -> list[dict[str, object]]:
        return self.capture(
            CONTINUITY.command_delta, argparse.Namespace(consumer="test-consumer")
        )

    def acknowledge(self, event_id: str) -> dict[str, object]:
        output = self.capture(
            CONTINUITY.command_ack,
            argparse.Namespace(consumer="test-consumer", event_id=event_id),
        )
        return output[0]

    def test_fresh_null_cursor_reports_bootstrap_required_not_ordinary_delta(self) -> None:
        output = self.delta()
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["status"], "BOOTSTRAP_REQUIRED")
        self.assertEqual(output[0]["cursor_state"], "UNINITIALIZED")
        self.assertEqual(output[0]["current_stream_head"], "CE-000003")
        self.assertEqual(output[0]["legal_bootstrap_modes"], [
            "FROM_ORIGIN", "FROM_HEAD", "AFTER_EVENT <event_id>"
        ])
        self.assertNotIn("summary", output[0])

    def test_from_origin_entitles_consumer_to_existing_stream(self) -> None:
        cursor = self.bootstrap("FROM_ORIGIN")
        self.assertEqual(cursor["cursor_state"], "POSITIONED")
        self.assertIsNone(cursor["last_seen_event_id"])
        self.assertEqual(cursor["bootstrap_mode"], "FROM_ORIGIN")
        self.assertEqual([event["event_id"] for event in self.delta()], [
            "CE-000001", "CE-000002", "CE-000003"
        ])

    def test_from_head_excludes_existing_stream_and_admits_only_new_events(self) -> None:
        cursor = self.bootstrap("FROM_HEAD")
        self.assertEqual(cursor["cursor_state"], "POSITIONED")
        self.assertEqual(cursor["last_seen_event_id"], "CE-000003")
        self.assertEqual(self.delta(), [])
        new_event = {"event_id": "CE-000004", "summary": "new after bootstrap"}
        with self.events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(new_event) + "\n")
        self.assertEqual([event["event_id"] for event in self.delta()], ["CE-000004"])

    def test_after_event_returns_only_events_after_explicit_coordinate(self) -> None:
        cursor = self.bootstrap("AFTER_EVENT", "CE-000001")
        self.assertEqual(cursor["last_seen_event_id"], "CE-000001")
        self.assertEqual([event["event_id"] for event in self.delta()], [
            "CE-000002", "CE-000003"
        ])

    def test_invalid_after_event_fails_without_mutating_cursor(self) -> None:
        before = self.cursor_path.read_bytes()
        with self.assertRaisesRegex(SystemExit, "unknown event"):
            self.bootstrap("AFTER_EVENT", "CE-999999")
        self.assertEqual(self.cursor_path.read_bytes(), before)
        retained = json.loads(before)
        self.assertEqual(retained["cursor_state"], "UNINITIALIZED")
        self.assertIsNone(retained["last_seen_event_id"])

    def test_backward_acknowledgement_is_rejected_without_mutation(self) -> None:
        self.bootstrap("AFTER_EVENT", "CE-000002")
        cursor_before = self.cursor_path.read_bytes()
        events_before = self.events_path.read_bytes()

        with self.assertRaisesRegex(SystemExit, "cannot acknowledge backward"):
            CONTINUITY.command_ack(
                argparse.Namespace(consumer="test-consumer", event_id="CE-000001")
            )

        self.assertEqual(self.cursor_path.read_bytes(), cursor_before)
        self.assertEqual(self.events_path.read_bytes(), events_before)

    def test_acknowledgement_is_contiguous_and_single_event(self) -> None:
        with self.events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps({"event_id": "CE-000004", "summary": "event 4"}) + "\n")
        self.bootstrap("AFTER_EVENT", "CE-000002")
        cursor_before_skip = self.cursor_path.read_bytes()
        events_before_skip = self.events_path.read_bytes()

        with self.assertRaisesRegex(SystemExit, "immediate next unread event is 'CE-000003'"):
            self.acknowledge("CE-000004")

        self.assertEqual(self.cursor_path.read_bytes(), cursor_before_skip)
        self.assertEqual(self.events_path.read_bytes(), events_before_skip)
        self.assertEqual(
            [event["event_id"] for event in self.delta()],
            ["CE-000003", "CE-000004"],
        )

        first = self.acknowledge("CE-000003")
        self.assertEqual(first["last_seen_event_id"], "CE-000003")
        self.assertEqual(
            [event["event_id"] for event in self.delta()], ["CE-000004"]
        )

        second = self.acknowledge("CE-000004")
        self.assertEqual(second["last_seen_event_id"], "CE-000004")
        self.assertEqual(self.delta(), [])

    def test_from_origin_first_acknowledgement_must_be_first_event(self) -> None:
        origin = self.bootstrap("FROM_ORIGIN")
        self.assertEqual(origin["cursor_state"], "POSITIONED")
        self.assertIsNone(origin["last_seen_event_id"])
        self.assertEqual(
            [event["event_id"] for event in self.delta()],
            ["CE-000001", "CE-000002", "CE-000003"],
        )
        cursor_after_bootstrap = self.cursor_path.read_bytes()
        events_before = self.events_path.read_bytes()

        with self.assertRaisesRegex(SystemExit, "immediate next unread event is 'CE-000001'"):
            self.acknowledge("CE-000003")
        self.assertEqual(self.cursor_path.read_bytes(), cursor_after_bootstrap)
        self.assertEqual(self.events_path.read_bytes(), events_before)

        with self.assertRaisesRegex(SystemExit, "immediate next unread event is 'CE-000001'"):
            self.acknowledge("CE-000002")
        self.assertEqual(self.cursor_path.read_bytes(), cursor_after_bootstrap)
        self.assertEqual(self.events_path.read_bytes(), events_before)
        self.assertEqual(
            [event["event_id"] for event in self.delta()],
            ["CE-000001", "CE-000002", "CE-000003"],
        )

        first = self.acknowledge("CE-000001")
        self.assertEqual(first["last_seen_event_id"], "CE-000001")
        self.assertEqual(
            [event["event_id"] for event in self.delta()],
            ["CE-000002", "CE-000003"],
        )
        self.assertEqual(self.events_path.read_bytes(), events_before)

    def test_empty_from_head_acknowledgement_starts_with_first_appended_event(self) -> None:
        self.events_path.write_bytes(b"")
        head = self.bootstrap("FROM_HEAD")
        self.assertEqual(head["cursor_state"], "POSITIONED")
        self.assertIsNone(head["last_seen_event_id"])
        self.assertEqual(head["bootstrap_mode"], "FROM_HEAD")
        self.assertEqual(self.delta(), [])

        appended = [
            {"event_id": "CE-000001", "summary": "first after empty head"},
            {"event_id": "CE-000002", "summary": "second after empty head"},
        ]
        self.events_path.write_text(
            "".join(json.dumps(event) + "\n" for event in appended), encoding="utf-8"
        )
        self.assertEqual(
            [event["event_id"] for event in self.delta()],
            ["CE-000001", "CE-000002"],
        )
        cursor_before_skip = self.cursor_path.read_bytes()
        events_before_skip = self.events_path.read_bytes()

        with self.assertRaisesRegex(SystemExit, "immediate next unread event is 'CE-000001'"):
            self.acknowledge("CE-000002")

        self.assertEqual(self.cursor_path.read_bytes(), cursor_before_skip)
        self.assertEqual(self.events_path.read_bytes(), events_before_skip)
        self.assertEqual(
            [event["event_id"] for event in self.delta()],
            ["CE-000001", "CE-000002"],
        )

        first = self.acknowledge("CE-000001")
        self.assertEqual(first["last_seen_event_id"], "CE-000001")
        self.assertEqual(
            [event["event_id"] for event in self.delta()], ["CE-000002"]
        )

    def test_acknowledgement_at_stream_head_rejects_without_mutation(self) -> None:
        retained = self.events[:2]
        self.events_path.write_text(
            "".join(json.dumps(event) + "\n" for event in retained), encoding="utf-8"
        )
        head = self.bootstrap("FROM_HEAD")
        self.assertEqual(head["last_seen_event_id"], "CE-000002")
        self.assertEqual(self.delta(), [])
        cursor_before = self.cursor_path.read_bytes()
        events_before = self.events_path.read_bytes()

        with self.assertRaisesRegex(SystemExit, "no unread event exists"):
            self.acknowledge("latest")

        self.assertEqual(self.cursor_path.read_bytes(), cursor_before)
        self.assertEqual(self.events_path.read_bytes(), events_before)
        self.assertEqual(self.delta(), [])

    def test_materialized_reported_state_survives_fresh_context_without_replay(self) -> None:
        basis_path = self.continuity_dir / "base_state_artifact.json"
        basis_path.write_text(
            json.dumps({
                "ACTIVE_OPERATOR": "O0",
                "TARGET": "P0",
                "STATUS": "UNRESOLVED",
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        event = {
            "event_id": "CE-000003",
            "kind": "STATE_UPDATE",
            "payload": {
                "target_coordinate": "P0",
                "prior_status": "UNRESOLVED",
                "new_value": True,
            },
            "standing": "REPORTED",
            "refs": ["base_state_artifact.json"],
        }
        retained_events = self.events[:2] + [event]
        self.events_path.write_text(
            "".join(json.dumps(item) + "\n" for item in retained_events),
            encoding="utf-8",
        )
        self.bootstrap("AFTER_EVENT", "CE-000002")
        basis_before = basis_path.read_bytes()
        events_before = self.events_path.read_bytes()

        basis = json.loads(basis_before)
        self.assertEqual(event["payload"]["target_coordinate"], basis["TARGET"])
        self.assertEqual(event["payload"]["prior_status"], basis["STATUS"])

        state_dir = self.continuity_dir / "current_state"
        state_dir.mkdir()
        state_path = state_dir / "semantic_tunnel_materialization_001.json"
        state_path.write_text(
            json.dumps({
                "CURRENT_STATE_ID": "CS-SEMANTIC-TUNNEL-001",
                "ACTIVE_OPERATOR": basis["ACTIVE_OPERATOR"],
                "TARGET": basis["TARGET"],
                "STATUS": "RESOLVED",
                "VALUE": event["payload"]["new_value"],
                "STANDING": event["standing"],
                "VERIFICATION_STANDING": "NOT_VERIFIED",
                "SOURCE_EVENT": event["event_id"],
                "SOURCE_BASIS_REF": event["refs"][0],
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        self.assertEqual([path.name for path in state_dir.iterdir()], [state_path.name])

        acknowledged = self.acknowledge("CE-000003")
        self.assertEqual(acknowledged["last_seen_event_id"], "CE-000003")
        self.assertEqual(self.delta(), [])
        self.assertEqual(basis_path.read_bytes(), basis_before)
        self.assertEqual(self.events_path.read_bytes(), events_before)

        recovered = json.loads(state_path.read_bytes())
        self.assertEqual(recovered["ACTIVE_OPERATOR"], "O0")
        self.assertEqual(recovered["TARGET"], "P0")
        self.assertEqual(recovered["STATUS"], "RESOLVED")
        self.assertIs(recovered["VALUE"], True)
        self.assertEqual(recovered["STANDING"], "REPORTED")
        self.assertEqual(recovered["VERIFICATION_STANDING"], "NOT_VERIFIED")
        self.assertEqual(recovered["SOURCE_EVENT"], "CE-000003")
        self.assertEqual(recovered["SOURCE_BASIS_REF"], "base_state_artifact.json")


if __name__ == "__main__":
    unittest.main()
