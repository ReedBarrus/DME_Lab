from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "continuity_registry_tool", ROOT / "tools" / "continuity.py"
)
assert SPEC and SPEC.loader
CONTINUITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTINUITY)


class ContinuityRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.invocation_temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.invocation_dir = Path(self.invocation_temp_dir.name)
        self.continuity_dir = self.root / "continuity"
        self.cursors_dir = self.continuity_dir / "cursors"
        self.cursors_dir.mkdir(parents=True)
        self.events_path = self.continuity_dir / "events.jsonl"
        self.registry_path = self.continuity_dir / "registry.json"
        self.events = [
            {"event_id": f"CE-{index:06d}", "summary": f"event {index}"}
            for index in range(1, 4)
        ]
        self.events_path.write_text(
            "".join(json.dumps(event) + "\n" for event in self.events),
            encoding="utf-8",
        )
        self.write_cursor("chatgpt", "POSITIONED", "CE-000001")
        self.write_cursor("codex", "POSITIONED", "CE-000003")
        self.registry = {
            "registry_version": "coordination-registry-v0",
            "consumers": [
                {
                    "consumer_id": "chatgpt-main",
                    "role": "semantic integrator and continuity consumer",
                    "cursor_ref": "continuity/cursors/chatgpt.json",
                    "tether_id": None,
                    "invocation_ref": None,
                    "invocation_kind": "NONE",
                    "association_basis": None,
                    "resolution_status": None,
                    "activity_state": "UNKNOWN",
                    "working_state_ref": None,
                },
                {
                    "consumer_id": "codex-main",
                    "role": "repository implementation and continuity consumer",
                    "cursor_ref": "continuity/cursors/codex.json",
                    "invocation_ref": None,
                    "invocation_kind": "NONE",
                    "activity_state": "UNKNOWN",
                    "working_state_ref": None,
                },
            ],
        }
        self.write_registry()
        self.original_paths = (
            CONTINUITY.ROOT,
            CONTINUITY.CONTINUITY_DIR,
            CONTINUITY.EVENTS_PATH,
            CONTINUITY.CURSORS_DIR,
            CONTINUITY.REGISTRY_PATH,
        )
        CONTINUITY.ROOT = self.root
        CONTINUITY.CONTINUITY_DIR = self.continuity_dir
        CONTINUITY.EVENTS_PATH = self.events_path
        CONTINUITY.CURSORS_DIR = self.cursors_dir
        CONTINUITY.REGISTRY_PATH = self.registry_path

    def tearDown(self) -> None:
        (
            CONTINUITY.ROOT,
            CONTINUITY.CONTINUITY_DIR,
            CONTINUITY.EVENTS_PATH,
            CONTINUITY.CURSORS_DIR,
            CONTINUITY.REGISTRY_PATH,
        ) = self.original_paths
        self.invocation_temp_dir.cleanup()
        self.temp_dir.cleanup()

    def write_cursor(
        self, consumer: str, state: str, coordinate: str | None
    ) -> None:
        cursor = {
            "consumer": consumer,
            "cursor_state": state,
            "last_seen_event_id": coordinate,
        }
        if state == "POSITIONED":
            cursor["bootstrap_mode"] = "AFTER_EVENT"
        (self.cursors_dir / f"{consumer}.json").write_text(
            json.dumps(cursor, indent=2) + "\n", encoding="utf-8"
        )

    def write_registry(self) -> None:
        self.registry_path.write_text(
            json.dumps(self.registry, indent=2) + "\n", encoding="utf-8"
        )

    def bind_manual_chatgpt(
        self,
        invocation_ref: str = "human-selected-chatgpt-invocation",
        tether_id: str = "local-chatgpt-tether-000001",
    ) -> None:
        entry = self.registry["consumers"][0]
        entry.update(
            {
                "tether_id": tether_id,
                "invocation_ref": invocation_ref,
                "invocation_kind": "chatgpt-thread",
                "association_basis": "MANUAL_ASSERTION",
                "resolution_status": "OPAQUE",
            }
        )
        self.write_registry()

    @staticmethod
    def by_id(snapshot: dict[str, object], consumer_id: str) -> dict[str, object]:
        consumers = snapshot["consumers"]
        assert isinstance(consumers, list)
        return next(
            consumer
            for consumer in consumers
            if isinstance(consumer, dict) and consumer["consumer_id"] == consumer_id
        )

    def test_snapshot_derives_two_cursor_coordinates_and_unread_counts(self) -> None:
        snapshot = CONTINUITY._registry_snapshot()
        self.assertEqual(snapshot["continuity_head"], "CE-000003")
        self.assertEqual(
            [consumer["consumer_id"] for consumer in snapshot["consumers"]],
            ["chatgpt-main", "codex-main"],
        )
        chatgpt = self.by_id(snapshot, "chatgpt-main")
        codex = self.by_id(snapshot, "codex-main")
        self.assertEqual(chatgpt["last_seen_event"], "CE-000001")
        self.assertEqual(chatgpt["unread_event_count"], 2)
        self.assertEqual(codex["last_seen_event"], "CE-000003")
        self.assertEqual(codex["unread_event_count"], 0)
        for consumer in (chatgpt, codex):
            self.assertEqual(consumer["invocation_ref_status"], "NOT_RETAINED")
            self.assertEqual(consumer["activity_state"], "UNKNOWN")
            self.assertEqual(consumer["working_state_ref_status"], "NOT_RETAINED")
        self.assertFalse(snapshot["authority_changed"])
        self.assertFalse(snapshot["standing_changed"])

    def test_legitimate_cursor_advance_changes_only_derived_consumer(self) -> None:
        before = CONTINUITY._registry_snapshot()
        CONTINUITY.command_ack(
            argparse.Namespace(consumer="chatgpt", event_id="CE-000002")
        )
        after = CONTINUITY._registry_snapshot()
        chatgpt = self.by_id(after, "chatgpt-main")
        self.assertEqual(chatgpt["last_seen_event"], "CE-000002")
        self.assertEqual(chatgpt["unread_event_count"], 1)
        self.assertEqual(
            self.by_id(before, "codex-main"), self.by_id(after, "codex-main")
        )
        retained_registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.assertEqual(retained_registry, self.registry)

    def test_missing_and_uninitialized_cursor_state_remain_explicit(self) -> None:
        (self.cursors_dir / "chatgpt.json").unlink()
        missing = self.by_id(CONTINUITY._registry_snapshot(), "chatgpt-main")
        self.assertEqual(missing["cursor_state"], "UNKNOWN")
        self.assertEqual(missing["cursor_observation"], "MISSING_CURSOR")
        self.assertIsNone(missing["unread_event_count"])

        self.write_cursor("chatgpt", "UNINITIALIZED", None)
        uninitialized = self.by_id(
            CONTINUITY._registry_snapshot(), "chatgpt-main"
        )
        self.assertEqual(uninitialized["cursor_state"], "UNINITIALIZED")
        self.assertEqual(uninitialized["cursor_observation"], "BOOTSTRAP_REQUIRED")
        self.assertIsNone(uninitialized["unread_event_count"])

    def test_stale_invocation_and_absent_working_state_are_not_invented(self) -> None:
        entry = self.registry["consumers"][0]
        entry["invocation_ref"] = "traces/missing-chatgpt-session.json"
        entry["invocation_kind"] = "chatgpt-thread"
        self.write_registry()

        chatgpt = self.by_id(CONTINUITY._registry_snapshot(), "chatgpt-main")
        self.assertEqual(chatgpt["invocation_ref_status"], "STALE_REF")
        self.assertEqual(chatgpt["activity_state"], "UNKNOWN")
        self.assertIsNone(chatgpt["working_state_ref"])
        self.assertEqual(chatgpt["working_state_ref_status"], "NOT_RETAINED")

    def test_retained_codex_invocation_is_observational_metadata_only(self) -> None:
        before = CONTINUITY._registry_snapshot()
        chatgpt_before = self.by_id(before, "chatgpt-main")
        codex_before = self.by_id(before, "codex-main")
        events_before = self.events_path.read_bytes()
        cursors_before = {
            path.name: path.read_bytes() for path in self.cursors_dir.iterdir()
        }
        invocation_path = self.invocation_dir / "rollout-codex-session.jsonl"
        invocation_path.write_text('{"type":"session_meta"}\n', encoding="utf-8")

        codex_entry = self.registry["consumers"][1]
        codex_entry["invocation_ref"] = str(invocation_path)
        codex_entry["invocation_kind"] = "codex-session"
        self.write_registry()

        after = CONTINUITY._registry_snapshot()
        codex_after = self.by_id(after, "codex-main")
        self.assertEqual(codex_after["invocation_ref"], str(invocation_path))
        self.assertEqual(codex_after["invocation_kind"], "codex-session")
        self.assertEqual(codex_after["invocation_ref_status"], "AVAILABLE")
        self.assertEqual(codex_after["last_seen_event"], codex_before["last_seen_event"])
        self.assertEqual(
            codex_after["unread_event_count"], codex_before["unread_event_count"]
        )
        self.assertEqual(codex_after["activity_state"], "UNKNOWN")
        self.assertEqual(
            codex_after["working_state_ref"], codex_before["working_state_ref"]
        )
        self.assertEqual(self.by_id(after, "chatgpt-main"), chatgpt_before)
        self.assertEqual(self.events_path.read_bytes(), events_before)
        self.assertEqual(
            {path.name: path.read_bytes() for path in self.cursors_dir.iterdir()},
            cursors_before,
        )
        self.assertFalse(after["authority_changed"])
        self.assertFalse(after["standing_changed"])

    def test_nonexistent_absolute_invocation_ref_remains_explicit(self) -> None:
        missing_path = self.invocation_dir / "missing-codex-session.jsonl"
        codex_entry = self.registry["consumers"][1]
        codex_entry["invocation_ref"] = str(missing_path)
        codex_entry["invocation_kind"] = "codex-session"
        self.write_registry()

        codex = self.by_id(CONTINUITY._registry_snapshot(), "codex-main")
        self.assertEqual(codex["invocation_ref_status"], "STALE_REF")
        self.assertEqual(codex["activity_state"], "UNKNOWN")
        self.assertIsNone(codex["working_state_ref"])

    def test_removed_invocation_association_is_not_retained(self) -> None:
        codex_entry = self.registry["consumers"][1]
        codex_entry["invocation_ref"] = None
        codex_entry["invocation_kind"] = "NONE"
        self.write_registry()

        codex = self.by_id(CONTINUITY._registry_snapshot(), "codex-main")
        self.assertIsNone(codex["invocation_ref"])
        self.assertEqual(codex["invocation_kind"], "NONE")
        self.assertEqual(codex["invocation_ref_status"], "NOT_RETAINED")
        self.assertEqual(codex["activity_state"], "UNKNOWN")

    def test_manual_opaque_tether_changes_only_invocation_metadata(self) -> None:
        before = CONTINUITY._registry_snapshot()
        chatgpt_before = self.by_id(before, "chatgpt-main")
        codex_before = self.by_id(before, "codex-main")
        events_before = self.events_path.read_bytes()
        cursors_before = {
            path.name: path.read_bytes() for path in self.cursors_dir.iterdir()
        }

        self.bind_manual_chatgpt()
        after = CONTINUITY._registry_snapshot()
        chatgpt_after = self.by_id(after, "chatgpt-main")

        self.assertEqual(chatgpt_after["tether_id"], "local-chatgpt-tether-000001")
        self.assertEqual(chatgpt_after["invocation_kind"], "chatgpt-thread")
        self.assertEqual(
            chatgpt_after["invocation_ref"], "human-selected-chatgpt-invocation"
        )
        self.assertEqual(chatgpt_after["association_basis"], "MANUAL_ASSERTION")
        self.assertEqual(chatgpt_after["resolution_status"], "OPAQUE")
        self.assertEqual(chatgpt_after["invocation_ref_status"], "OPAQUE")
        self.assertEqual(chatgpt_after["invocation_observation_failures"], [])
        for key in (
            "cursor_ref",
            "cursor_state",
            "last_seen_event",
            "unread_event_count",
            "cursor_observation",
            "activity_state",
            "working_state_ref",
            "working_state_ref_status",
        ):
            self.assertEqual(chatgpt_after[key], chatgpt_before[key])
        self.assertEqual(self.by_id(after, "codex-main"), codex_before)
        self.assertEqual(self.events_path.read_bytes(), events_before)
        self.assertEqual(
            {path.name: path.read_bytes() for path in self.cursors_dir.iterdir()},
            cursors_before,
        )
        self.assertFalse(after["authority_changed"])
        self.assertFalse(after["standing_changed"])

    def test_same_manual_tether_rebound_is_idempotent(self) -> None:
        self.bind_manual_chatgpt()
        first = CONTINUITY._registry_snapshot()
        self.bind_manual_chatgpt()
        self.assertEqual(CONTINUITY._registry_snapshot(), first)

    def test_replacing_opaque_ref_changes_only_tether_metadata(self) -> None:
        self.bind_manual_chatgpt(invocation_ref="first-human-label")
        before = CONTINUITY._registry_snapshot()
        chatgpt_before = self.by_id(before, "chatgpt-main")

        self.bind_manual_chatgpt(invocation_ref="replacement-human-label")
        after = CONTINUITY._registry_snapshot()
        chatgpt_after = self.by_id(after, "chatgpt-main")

        changed_keys = {
            key
            for key in chatgpt_before
            if chatgpt_before[key] != chatgpt_after[key]
        }
        self.assertEqual(changed_keys, {"invocation_ref"})
        self.assertEqual(
            self.by_id(after, "codex-main"), self.by_id(before, "codex-main")
        )

    def test_null_manual_association_is_not_retained(self) -> None:
        entry = self.registry["consumers"][0]
        entry.update(
            {
                "tether_id": None,
                "invocation_ref": None,
                "invocation_kind": "NONE",
                "association_basis": None,
                "resolution_status": None,
            }
        )
        self.write_registry()

        chatgpt = self.by_id(CONTINUITY._registry_snapshot(), "chatgpt-main")
        self.assertIsNone(chatgpt["tether_id"])
        self.assertEqual(chatgpt["invocation_ref_status"], "NOT_RETAINED")
        self.assertEqual(chatgpt["activity_state"], "UNKNOWN")

    def test_duplicate_tether_id_is_rejected_explicitly(self) -> None:
        self.bind_manual_chatgpt()
        self.registry["consumers"][1]["tether_id"] = "local-chatgpt-tether-000001"
        self.write_registry()

        with self.assertRaisesRegex(SystemExit, "duplicate tether_id"):
            CONTINUITY._registry_snapshot()

    def test_duplicate_opaque_ref_is_rejected_explicitly(self) -> None:
        self.bind_manual_chatgpt()
        self.registry["consumers"][1].update(
            {
                "tether_id": "local-chatgpt-tether-000002",
                "invocation_ref": "human-selected-chatgpt-invocation",
                "invocation_kind": "chatgpt-thread",
                "association_basis": "MANUAL_ASSERTION",
                "resolution_status": "OPAQUE",
            }
        )
        self.write_registry()

        with self.assertRaisesRegex(SystemExit, "duplicate manually asserted"):
            CONTINUITY._registry_snapshot()

    def test_malformed_association_basis_remains_explicit(self) -> None:
        self.bind_manual_chatgpt()
        self.registry["consumers"][0]["association_basis"] = "AUTOMATIC_DISCOVERY"
        self.write_registry()

        chatgpt = self.by_id(CONTINUITY._registry_snapshot(), "chatgpt-main")
        self.assertEqual(
            chatgpt["invocation_ref_status"], "INVALID_ASSOCIATION_BASIS"
        )
        self.assertTrue(chatgpt["invocation_observation_failures"])

    def test_manual_ref_that_looks_resolvable_remains_opaque(self) -> None:
        apparent_path = self.invocation_dir / "apparent-chatgpt-thread.json"
        apparent_path.write_text("{}\n", encoding="utf-8")
        self.bind_manual_chatgpt(invocation_ref=str(apparent_path))

        chatgpt = self.by_id(CONTINUITY._registry_snapshot(), "chatgpt-main")
        self.assertEqual(chatgpt["resolution_status"], "OPAQUE")
        self.assertEqual(chatgpt["invocation_ref_status"], "OPAQUE")

    def test_local_tether_id_cannot_masquerade_as_invocation_ref(self) -> None:
        self.bind_manual_chatgpt(
            invocation_ref="same-token", tether_id="same-token"
        )

        chatgpt = self.by_id(CONTINUITY._registry_snapshot(), "chatgpt-main")
        self.assertEqual(
            chatgpt["invocation_ref_status"], "INVALID_MANUAL_ASSOCIATION"
        )
        self.assertIn(
            "tether_id must not equal invocation_ref",
            chatgpt["invocation_observation_failures"],
        )


if __name__ == "__main__":
    unittest.main()
