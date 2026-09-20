from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "labboib_temporal_seat", ROOT / "tools" / "labboib_seat.py"
)
assert SPEC and SPEC.loader
SEAT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SEAT)


MANIFEST = {
    "schema_version": "temporal_seat_manifest_v0",
    "seat_id": "LABBOIB",
    "consumer_id": "labboib",
    "seat_class": "TEMPORAL_REENTRY_SEAT_CANDIDATE",
    "role": "bounded test seat",
    "cursor_ref": "continuity/cursors/labboib.json",
    "working_state_ref": "continuity/current_state/labboib_working_state_v0.json",
    "inbox_ref": "continuity/queues/labboib/inbox.jsonl",
    "outbox_ref": "continuity/queues/labboib/outbox.jsonl",
    "trigger": {"state": "UNBOUND", "kind": None, "schedule_ref": None},
    "occupant": {"binding": "UNBOUND", "model_family": None, "invocation_ref": None},
    "allowed_wake_effects": ["read basis"],
    "forbidden_wake_effects": ["ambient authority"],
    "noncollapses": ["MODEL_INSTANCE != SEAT"],
    "authority_effect": "NONE_BY_MANIFEST",
    "execution_effect": "NONE_BY_MANIFEST",
}

CURSOR = {
    "consumer": "labboib",
    "cursor_state": "POSITIONED",
    "last_seen_event_id": "CE-000002",
    "bootstrap_mode": "FROM_HEAD",
    "bootstrap_basis": {
        "stream_head_at_materialization": "CE-000002",
        "purpose": "test",
        "historical_chat_imported": False,
    },
}

WORKING_STATE = {
    "schema_version": "temporal_seat_working_state_v0",
    "seat_id": "LABBOIB",
    "state_id": "STATE-TEST",
    "campaign": {
        "campaign_id": "C-TEST",
        "title": "Test campaign",
        "status": "ACTIVE",
        "objective": "Pressure temporal wake.",
        "branch": "test",
        "base_ref": "main",
        "base_commit": "a" * 40,
    },
    "continuity": {
        "consumer": "labboib",
        "synchronized_through": "CE-000002",
        "historical_chat_imported": False,
    },
    "injection_coordinate": {"last_consumed_injection_id": None},
    "current_frontier": "wake",
    "unresolved": [],
    "authority": {"standing": "NONE", "source": None},
    "last_wake_receipt_ref": None,
    "standing_effect": "NONE_BY_WORKING_STATE",
    "authority_effect": "NONE_BY_WORKING_STATE",
}

EVENTS = [
    {
        "event_id": "CE-000001",
        "observed_at": "2026-09-20T00:00:00Z",
        "actor": "test",
        "surface": "repo",
        "kind": "TEST",
        "summary": "one",
        "refs": [],
        "parent_refs": [],
        "reported_standing_delta": None,
        "reported_frontier_delta": None,
    },
    {
        "event_id": "CE-000002",
        "observed_at": "2026-09-20T00:01:00Z",
        "actor": "test",
        "surface": "repo",
        "kind": "TEST",
        "summary": "two",
        "refs": [],
        "parent_refs": [],
        "reported_standing_delta": None,
        "reported_frontier_delta": None,
    },
]


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
    ).strip()


class LabboibTemporalSeatTest(unittest.TestCase):
    def make_repo(self) -> tuple[TemporaryDirectory, Path]:
        temporary = TemporaryDirectory()
        root = Path(temporary.name)
        git(root, "init")
        git(root, "config", "user.email", "test@example.invalid")
        git(root, "config", "user.name", "Temporal Seat Test")

        files = {
            SEAT.MANIFEST_PATH: json.dumps(MANIFEST, indent=2) + "\n",
            SEAT.CURSOR_PATH: json.dumps(CURSOR, indent=2) + "\n",
            SEAT.WORKING_STATE_PATH: json.dumps(WORKING_STATE, indent=2) + "\n",
            SEAT.EVENTS_PATH: "".join(json.dumps(row) + "\n" for row in EVENTS),
            SEAT.INBOX_PATH: "",
            SEAT.OUTBOX_PATH: "",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        git(root, "add", ".")
        git(root, "commit", "-m", "seat fixture")
        return temporary, root

    def commit_file(self, root: Path, relative: str, content: str, message: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        git(root, "add", relative)
        git(root, "commit", "-m", message)

    def test_wake_is_read_only_and_recovers_exact_current_coordinate(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)
        before = {
            relative: (root / relative).read_bytes()
            for relative in (
                SEAT.CURSOR_PATH,
                SEAT.WORKING_STATE_PATH,
                SEAT.EVENTS_PATH,
                SEAT.INBOX_PATH,
                SEAT.OUTBOX_PATH,
            )
        }

        wake = SEAT.build_wake(root, "HEAD")

        self.assertEqual(wake["status"], "READY")
        self.assertRegex(wake["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(wake["continuity_head"], "CE-000002")
        self.assertEqual(wake["unread_continuity_events"], [])
        self.assertEqual(wake["pending_injections"], [])
        self.assertEqual(wake["authority_effect"], "NONE_BY_WAKE")
        self.assertEqual(wake["execution_effect"], "NONE_BY_WAKE")
        self.assertEqual(wake["seat_manifest"]["trigger"]["state"], "UNBOUND")
        self.assertEqual(wake["seat_manifest"]["occupant"]["binding"], "UNBOUND")
        after = {
            relative: (root / relative).read_bytes()
            for relative in before
        }
        self.assertEqual(after, before)

    def test_event_after_cursor_is_unread_without_advancing_cursor(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        third = dict(EVENTS[-1])
        third["event_id"] = "CE-000003"
        third["summary"] = "new after seat coordinate"
        rows = EVENTS + [third]
        self.commit_file(
            root,
            SEAT.EVENTS_PATH,
            "".join(json.dumps(row) + "\n" for row in rows),
            "append event",
        )

        cursor_before = (root / SEAT.CURSOR_PATH).read_bytes()
        wake = SEAT.build_wake(root, "HEAD")

        self.assertEqual(
            [row["event_id"] for row in wake["unread_continuity_events"]],
            ["CE-000003"],
        )
        self.assertEqual((root / SEAT.CURSOR_PATH).read_bytes(), cursor_before)

    def test_injection_is_visible_but_does_not_create_authority(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        injection = {
            "schema_version": "temporal_seat_injection_v0",
            "injection_id": "LI-000001",
            "target_seat": "LABBOIB",
            "kind": "MESSAGE",
            "body": "go inspect the next bounded thing",
            "refs": [],
            "authority": {"claimed": False, "authority_ref": None},
            "created_by": "human",
        }
        self.commit_file(
            root,
            SEAT.INBOX_PATH,
            json.dumps(injection, sort_keys=True) + "\n",
            "inject message",
        )

        wake = SEAT.build_wake(root, "HEAD")

        self.assertEqual(len(wake["pending_injections"]), 1)
        self.assertFalse(wake["pending_injections"][0]["authority"]["claimed"])
        self.assertEqual(wake["authority_effect"], "NONE_BY_WAKE")

    def test_authority_claim_without_reference_is_rejected(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        injection = {
            "schema_version": "temporal_seat_injection_v0",
            "injection_id": "LI-000001",
            "target_seat": "LABBOIB",
            "kind": "AUTHORITY_OBJECT_REF",
            "body": "trust me bro",
            "refs": [],
            "authority": {"claimed": True, "authority_ref": None},
            "created_by": "synthetic",
        }
        self.commit_file(
            root,
            SEAT.INBOX_PATH,
            json.dumps(injection) + "\n",
            "bad authority injection",
        )

        with self.assertRaisesRegex(
            SEAT.TemporalSeatError,
            "authority-claiming injection requires an authority_ref",
        ):
            SEAT.build_wake(root, "HEAD")

    def test_cursor_and_working_state_disagreement_blocks_wake(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        changed = json.loads(json.dumps(WORKING_STATE))
        changed["continuity"]["synchronized_through"] = "CE-000001"
        self.commit_file(
            root,
            SEAT.WORKING_STATE_PATH,
            json.dumps(changed, indent=2) + "\n",
            "drift working state",
        )

        with self.assertRaisesRegex(
            SEAT.TemporalSeatError,
            "continuity coordinate disagrees",
        ):
            SEAT.build_wake(root, "HEAD")

    def test_local_injection_helper_appends_sequential_non_authorizing_object(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        first = SEAT.append_injection(
            root,
            kind="MESSAGE",
            body="hello suit",
            created_by="human",
            refs=[],
            authority_ref=None,
        )
        second = SEAT.append_injection(
            root,
            kind="PACKET_REF",
            body="inspect packet",
            created_by="human",
            refs=["packet:one"],
            authority_ref=None,
        )

        self.assertEqual(first["injection_id"], "LI-000001")
        self.assertEqual(second["injection_id"], "LI-000002")
        self.assertFalse(first["authority"]["claimed"])
        self.assertFalse(second["authority"]["claimed"])

    def test_output_queue_requires_sequential_identity_and_zero_effect(self) -> None:
        temporary, root = self.make_repo()
        self.addCleanup(temporary.cleanup)

        basis = git(root, "rev-parse", "HEAD")
        output = {
            "schema_version": "temporal_seat_output_v0",
            "output_id": "LO-000001",
            "seat_id": "LABBOIB",
            "output_kind": "STATUS",
            "basis_commit": basis,
            "consumed_continuity_through": "CE-000002",
            "consumed_injection_through": None,
            "summary": "seat is awake",
            "refs": [],
            "authority_effect": "NONE_BY_OUTPUT",
            "execution_effect": "NONE_BY_OUTPUT",
        }
        retained = SEAT.append_output(root, output)

        self.assertEqual(retained["output_id"], "LO-000001")

        bad = dict(output)
        bad["output_id"] = "LO-000003"
        with self.assertRaisesRegex(SEAT.TemporalSeatError, "next queue identity"):
            SEAT.append_output(root, bad)


if __name__ == "__main__":
    unittest.main()
