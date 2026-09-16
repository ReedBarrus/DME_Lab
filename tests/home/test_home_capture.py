from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
import threading
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "src" / "home" / "home_capture_v0"
SPEC = importlib.util.spec_from_file_location("home_capture_server", APP_DIR / "server.py")
assert SPEC and SPEC.loader
SERVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SERVER)


class HomeCaptureServerTest(unittest.TestCase):
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

    def get(self, path: str):
        with urlopen(f"{self.base_url}{path}", timeout=3) as response:
            return response.status, response.headers, response.read()

    def post_capture(self, mode: str, raw_text: str, client_time: str = "2026-09-15T12:00:00Z"):
        body = json.dumps(
            {"mode": mode, "raw_text": raw_text, "client_time": client_time}
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/capture",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read())

    def post_json(self, path: str, payload: dict[str, object]):
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read())

    def create_recurring(
        self, raw_text: str, weekly_days: list[str], placement: str | None = None
    ):
        return self.post_json(
            "/api/capture",
            {"mode": "commit", "raw_text": raw_text,
             "recurrence_type": "WEEKLY_PATTERN", "weekly_days": weekly_days,
             "temporal_placement": placement},
        )

    def backdate_commitment(self, commitment_id: str, timestamp: str) -> None:
        with self.server.store.connection() as connection:
            connection.execute(
                "UPDATE commitments SET created_at_utc=? WHERE commitment_id=?",
                (timestamp, commitment_id),
            )
            connection.execute(
                "UPDATE commitment_specifications SET created_at_utc=?,effective_at=? "
                "WHERE commitment_id=? AND amendment_kind='INITIAL'",
                (timestamp, timestamp, commitment_id),
            )

    def test_health_reports_operational_service_and_data_location(self) -> None:
        status, _, body = self.get("/api/health")
        health = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(health["service"], "home_capture_v0")
        self.assertEqual(health["status"], "operational")
        self.assertEqual(health["capture_count"], 0)
        self.assertEqual(health["access_mode"], "desktop")
        self.assertIsNone(health["phone_url"])
        self.assertFalse(health["public_internet_supported"])
        self.assertEqual(self.server.store.db_path, self.data_dir / "home_capture.sqlite3")
        self.assertTrue((self.data_dir / "exports").is_dir())

    def test_three_lanes_remain_distinct_and_raw_text_is_not_rewritten(self) -> None:
        texts = {
            "care": "  Need rest exactly as written.  ",
            "commit": "I explicitly adopt this bounded action.",
            "develop": "Running one DME build experiment.",
        }
        records = {}
        for lane, text in texts.items():
            status, record = self.post_capture(lane, text)
            self.assertEqual(status, 201)
            records[lane] = record
            self.assertEqual(record["mode"], lane)
            self.assertEqual(record["raw_text"], text)
            self.assertTrue(record["id"].startswith("home:capture:"))

        _, _, body = self.get("/api/captures?lane=all&order=asc")
        payload = json.loads(body)
        self.assertEqual(payload["count"], 3)
        self.assertEqual([row["mode"] for row in payload["captures"]], list(texts))
        self.assertEqual(
            {row["id"] for row in payload["captures"]},
            {record["id"] for record in records.values()},
        )

    def test_history_filter_search_and_chronological_order(self) -> None:
        self.post_capture("care", "alpha care", "2026-09-15T10:00:00Z")
        self.post_capture("develop", "beta develop", "2026-09-15T11:00:00Z")
        self.post_capture("care", "gamma care", "2026-09-15T12:00:00Z")

        query = urlencode({"lane": "care", "q": "gamma", "order": "asc"})
        _, _, body = self.get(f"/api/captures?{query}")
        captures = json.loads(body)["captures"]
        self.assertEqual(len(captures), 1)
        self.assertEqual(captures[0]["raw_text"], "gamma care")

        _, _, body = self.get("/api/captures?lane=all&order=asc")
        captures = json.loads(body)["captures"]
        created = [row["created_at_utc"] for row in captures]
        self.assertEqual(created, sorted(created))

    def test_restart_retains_history(self) -> None:
        _, record = self.post_capture("care", "retained through restart")
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

        self.server = SERVER.create_server(
            "127.0.0.1", 0, self.data_dir, desktop_notifications=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

        _, _, body = self.get("/api/captures")
        captures = json.loads(body)["captures"]
        self.assertEqual([row["id"] for row in captures], [record["id"]])

    def test_jsonl_export_contains_all_raw_captures(self) -> None:
        _, care = self.post_capture("care", "care export")
        _, commit = self.post_capture("commit", "commit export")
        status, headers, body = self.get("/api/export.jsonl")
        rows = [json.loads(line) for line in body.decode("utf-8").splitlines()]
        self.assertEqual(status, 200)
        self.assertIn("home-captures.jsonl", headers["Content-Disposition"])
        self.assertEqual([row["id"] for row in rows], [care["id"], commit["id"]])

    def test_explore_and_non_json_posts_are_rejected(self) -> None:
        with self.assertRaises(HTTPError) as caught:
            self.post_capture("explore", "must remain absent")
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()

        request = Request(
            f"{self.base_url}/api/capture",
            data=b"mode=care",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 415)
        caught.exception.close()

    def test_second_server_cannot_bind_same_address(self) -> None:
        with self.assertRaises(OSError):
            duplicate = SERVER.create_server(
                "127.0.0.1", self.server.server_port, Path(self.temp_dir.name) / "other",
                desktop_notifications=False,
            )
            duplicate.server_close()

    def test_lan_health_advertises_private_url_only_in_lan_mode(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        with mock.patch.object(SERVER, "discover_private_ipv4", return_value="192.168.1.44"):
            self.server = SERVER.create_server(
                "127.0.0.1", 0, self.data_dir, "lan", desktop_notifications=False
            )
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.base_url = f"http://127.0.0.1:{self.server.server_port}"
            _, _, body = self.get("/api/health")
            health = json.loads(body)
        self.assertEqual(health["phone_url"], f"http://192.168.1.44:{self.server.server_port}")
        self.assertFalse(health["public_internet_supported"])

    def test_direct_file_access_has_explicit_inert_state(self) -> None:
        html = (APP_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn("window.location.protocol === 'file:'", html)
        self.assertIn("Home is not running", html)
        self.assertIn("SAVE, history, and export are disabled", html)
        self.assertIn("setControlsEnabled(false)", html)

    def test_launcher_has_health_wait_duplicate_guard_and_graphical_error(self) -> None:
        launcher = (APP_DIR / "launch_home.ps1").read_text(encoding="utf-8")
        self.assertIn("/api/health", launcher)
        self.assertIn("if ($existing)", launcher)
        self.assertIn("Start-Sleep -Milliseconds 250", launcher)
        self.assertIn("System.Windows.Forms.MessageBox", launcher)
        self.assertIn("-WindowStyle Hidden", launcher)

    def test_native_exe_launcher_preserves_local_desktop_boundary(self) -> None:
        source = (APP_DIR / "HomeCaptureLauncher.cs").read_text(encoding="utf-8")
        self.assertIn('const string ServiceName = "home_capture_v0"', source)
        self.assertIn('" --host 127.0.0.1"', source)
        self.assertIn("CreateNoWindow = true", source)
        self.assertIn("MessageBox.Show", source)
        self.assertIn('Path.Combine(appDirectory, "data")', source)
        self.assertNotIn("powershell", source.lower())
        self.assertNotIn("0.0.0.0", source)

    def test_native_build_targets_gui_exe_and_embeds_icon(self) -> None:
        build = (APP_DIR / "build_home_capture.ps1").read_text(encoding="utf-8")
        self.assertIn('"/target:winexe"', build)
        self.assertIn('"/win32icon:$iconPath"', build)
        self.assertIn('Join-Path $appDir "Home Capture.exe"', build)
        self.assertNotIn("data\\", build.lower())

    def test_legacy_migration_preserves_raw_rows_backs_up_and_is_idempotent(self) -> None:
        isolated = Path(self.temp_dir.name) / "legacy"
        isolated.mkdir()
        db_path = isolated / "home_capture.sqlite3"
        source_rows = [
            ("c1", "care", "  raw care  ", "user_explicit", None, "2026-01-01T00:00:00+00:00"),
            ("c2", "commit", "raw commitment", "user_explicit", "client", "2026-01-02T00:00:00+00:00"),
            ("c3", "develop", "raw develop", "user_explicit", None, "2026-01-03T00:00:00+00:00"),
        ]
        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TABLE captures(id TEXT PRIMARY KEY,mode TEXT,raw_text TEXT,origin TEXT,"
            "client_time TEXT,created_at_utc TEXT)"
        )
        connection.executemany("INSERT INTO captures VALUES(?,?,?,?,?,?)", source_rows)
        connection.commit()
        connection.close()

        store = SERVER.HomeStore(isolated)
        store.initialize()
        self.assertIsNotNone(store.last_migration_backup)
        backup = store.last_migration_backup
        assert backup is not None
        migrated, saved = sqlite3.connect(db_path), sqlite3.connect(backup)
        try:
            self.assertEqual(migrated.execute("SELECT * FROM captures ORDER BY id").fetchall(), source_rows)
            self.assertEqual(saved.execute("SELECT * FROM captures ORDER BY id").fetchall(), source_rows)
            commitment = migrated.execute(
                "SELECT source_capture_id,current_status,start_at,end_at,report_at,"
                "recurrence_type,weekly_days_json,temporal_placement FROM commitments"
            ).fetchone()
            fabricated_reports = migrated.execute(
                "SELECT COUNT(*) FROM commitment_occurrence_reports"
            ).fetchone()[0]
            specifications = migrated.execute(
                "SELECT commitment_id,amendment_kind,statement,source_capture_id "
                "FROM commitment_specifications"
            ).fetchall()
        finally:
            migrated.close()
            saved.close()
        self.assertEqual(
            commitment, ("c2", "ACTIVE", None, None, None, "NONE", None, None)
        )
        self.assertEqual(fabricated_reports, 0)
        self.assertEqual(len(specifications), 1)
        self.assertEqual(specifications[0][1:], ("INITIAL", "raw commitment", "c2"))
        backup_count = len(list((isolated / "backups").glob("*.sqlite3")))
        SERVER.HomeStore(isolated).initialize()
        self.assertEqual(len(list((isolated / "backups").glob("*.sqlite3"))), backup_count)

    def test_schema_reinitialization_preserves_event_and_chat_coordinates(self) -> None:
        _, created = self.post_capture("commit", "migration sentinel")
        event = self.server.store.create_event(
            "Chat", "Chat", "2035-01-01T00:00:00Z", "FUTURE_CHAT_NOTE",
            "exact event", [created["commitment"]["commitment_id"]],
        )
        chat = self.server.store.update_chat_state({
            "current_pressure": "exact pressure", "active_recommendations": ["retain"],
            "unresolved_questions": ["still open"], "continuation_refs": ["ref:exact"],
            "explicit_executable_agent_commitments": [],
        })
        with self.server.store.connection() as connection:
            connection.execute("PRAGMA user_version=4")
        self.server.store.initialize()
        self.assertEqual(self.server.store.events("all")[0], event)
        retained = self.server.store.chat_state()
        for field in ("current_pressure", "active_recommendations", "unresolved_questions",
                      "continuation_refs", "updated_at"):
            self.assertEqual(retained[field], chat[field])
        self.assertEqual(len(self.server.store.specifications(
            created["commitment"]["commitment_id"]
        )), 1)

    def test_specification_amendments_preserve_identity_lineage_and_current_projection(self) -> None:
        _, created = self.create_recurring("stored wrong", ["THU", "SAT"], "EVENING")
        identity = created["commitment"]["commitment_id"]
        initial_id = created["commitment"]["specification_id"]
        status, corrected = self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/amend",
            {"amendment_kind": "RECORDING_CORRECTION", "raw_text": "stored wrong",
             "raw_amendment_reason": "  weekday boxes were misread  ",
             "recurrence_type": "WEEKLY_PATTERN", "weekly_days": ["WED", "FRI"],
             "temporal_placement": "EVENING"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(corrected["commitment"]["commitment_id"], identity)
        self.assertEqual(corrected["commitment"]["current_status"], "ACTIVE")
        self.assertEqual(corrected["commitment"]["weekly_days"], ["WED", "FRI"])
        correction_id = corrected["specification"]["specification_id"]
        self.assertEqual(corrected["specification"]["prior_specification_id"], initial_id)
        self.assertEqual(corrected["specification"]["raw_amendment_reason"],
                         "  weekday boxes were misread  ")

        _, changed = self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/amend",
            {"amendment_kind": "INTENTION_CHANGE", "raw_text": "changed deliberately",
             "raw_amendment_reason": None, "recurrence_type": "WEEKLY_PATTERN",
             "weekly_days": ["MON", "WED", "FRI"], "temporal_placement": "MORNING"},
        )
        self.assertEqual(changed["commitment"]["commitment_id"], identity)
        self.assertEqual(changed["specification"]["prior_specification_id"], correction_id)
        _, _, history_body = self.get(
            f"/api/commitments/{quote(identity, safe='')}/specifications"
        )
        history = json.loads(history_body)["specifications"]
        self.assertEqual([item["amendment_kind"] for item in history],
                         ["INITIAL", "RECORDING_CORRECTION", "INTENTION_CHANGE"])
        self.assertEqual([item["statement"] for item in history],
                         ["stored wrong", "stored wrong", "changed deliberately"])
        self.assertEqual(len({item["commitment_id"] for item in history}), 1)

    def test_report_keeps_applicable_specification_identity_after_later_amendment(self) -> None:
        today = date.today()
        weekday = SERVER.WEEKDAYS[today.weekday()]
        _, created = self.create_recurring("first specification", [weekday], "MORNING")
        identity = created["commitment"]["commitment_id"]
        initial_id = created["commitment"]["specification_id"]
        _, retained = self.post_json(
            "/api/recurring-reports",
            {"reports": [{"commitment_id": identity,
                           "intended_local_date": today.isoformat(),
                           "outcome": "MET", "raw_feedback": "under initial"}]},
        )
        self.assertEqual(retained["reports"][0]["specification_id"], initial_id)
        _, amended = self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/amend",
            {"amendment_kind": "INTENTION_CHANGE", "raw_text": "second specification",
             "recurrence_type": "WEEKLY_PATTERN", "weekly_days": [weekday],
             "temporal_placement": "EVENING"},
        )
        self.assertNotEqual(amended["specification"]["specification_id"], initial_id)
        reports = self.server.store.occurrence_reports(identity)
        self.assertEqual(reports[0]["specification_id"], initial_id)
        history = self.server.store.recurrence_history(identity, today.isoformat())
        self.assertEqual(history["occurrences"][0]["specification_id"], initial_id)

    def test_resolution_and_revised_replacement_remain_distinct_from_amendment(self) -> None:
        _, created = self.post_capture("commit", "stable identity")
        identity = created["commitment"]["commitment_id"]
        self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/amend",
            {"amendment_kind": "RECORDING_CORRECTION", "raw_text": "corrected statement",
             "recurrence_type": "NONE", "weekly_days": [], "temporal_placement": None},
        )
        _, revised = self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/resolve",
            {"mode": "REVISED", "raw_feedback": "identity superseded",
             "replacement": {"raw_text": "replacement identity", "recurrence_type": "NONE"}},
        )
        replacement = revised["replacement_commitment"]
        self.assertNotEqual(replacement["commitment_id"], identity)
        self.assertEqual(replacement["amendment_kind"], "INITIAL")
        self.assertEqual(len(self.server.store.specifications(identity)), 2)
        self.assertEqual(self.server.store.commitment(identity)["current_status"], "CLOSED")

    def test_specification_history_survives_restart(self) -> None:
        _, created = self.post_capture("commit", "before")
        identity = created["commitment"]["commitment_id"]
        self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/amend",
            {"amendment_kind": "INTENTION_CHANGE", "raw_text": "after",
             "recurrence_type": "NONE", "weekly_days": [], "temporal_placement": None},
        )
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)
        self.server = SERVER.create_server(
            "127.0.0.1", 0, self.data_dir, desktop_notifications=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start(); self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        self.assertEqual(self.server.store.commitment(identity)["raw_text"], "after")
        self.assertEqual([item["statement"] for item in self.server.store.specifications(identity)],
                         ["before", "after"])

    def test_weekday_controls_are_bounded_and_visible_selection_is_submitted_exactly(self) -> None:
        html = (APP_DIR / "index.html").read_text(encoding="utf-8")
        self.assertIn(".weekday-picks input[type=checkbox]{min-width:0;width:1.1rem", html)
        self.assertIn(".schedule input:not([type=checkbox])", html)
        self.assertIn("SELECTED DAYS: NONE", html)
        self.assertIn("weekly_days:selectedDays('weeklyDays')", html)
        status, created = self.post_json(
            "/api/capture",
            {"mode": "commit", "raw_text": "visible WED FRI",
             "recurrence_type": "WEEKLY_PATTERN", "weekly_days": ["WED", "FRI"],
             "temporal_placement": "EVENING"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(created["commitment"]["weekly_days"], ["WED", "FRI"])

    def test_unscheduled_and_scheduled_commitments_have_stable_active_projection(self) -> None:
        _, unscheduled = self.post_capture("commit", "unscheduled")
        status, scheduled = self.post_json(
            "/api/capture",
            {"mode": "commit", "raw_text": "scheduled", "start_at": "2030-01-01T10:00:00Z",
             "end_at": "2030-01-01T11:00:00Z", "report_at": "2030-01-01T12:00:00Z"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(unscheduled["commitment"]["current_status"], "ACTIVE")
        self.assertIsNone(unscheduled["commitment"]["start_at"])
        _, _, body = self.get("/api/commitments?view=active&observed_at=2029-01-01T00:00:00Z")
        rows = json.loads(body)["commitments"]
        self.assertEqual(len(rows), 2)
        scheduled_row = next(row for row in rows if row["raw_text"] == "scheduled")
        self.assertFalse(scheduled_row["report_due"])
        self.assertEqual(scheduled_row["source_capture_id"], scheduled["id"])

    def test_report_due_is_derived_and_does_not_close_or_infer_failure(self) -> None:
        _, record = self.post_json(
            "/api/capture",
            {"mode": "commit", "raw_text": "await report", "report_at": "2026-01-01T00:00:00Z"},
        )
        _, _, body = self.get("/api/commitments?view=report_due&observed_at=2026-01-02T00:00:00Z")
        due = json.loads(body)["commitments"]
        self.assertEqual(len(due), 1)
        self.assertTrue(due[0]["report_due"])
        self.assertEqual(due[0]["current_status"], "ACTIVE")
        self.assertIsNone(due[0]["resolution_mode"])
        self.assertNotIn("failure", json.dumps(due).lower())
        self.assertEqual(due[0]["commitment_id"], record["commitment"]["commitment_id"])

    def test_terminal_resolution_modes_and_feedback_remain_distinct(self) -> None:
        for mode in ("COMPLETED", "RELEASED", "BYPASSED", "FORGOTTEN"):
            _, created = self.post_capture("commit", f"commit {mode}")
            feedback = f"  exact {mode} feedback  "
            status, result = self.post_json(
                f"/api/commitments/{quote(created['commitment']['commitment_id'], safe='')}/resolve",
                {"mode": mode, "raw_feedback": feedback},
            )
            self.assertEqual(status, 201)
            self.assertEqual(result["resolution"]["mode"], mode)
            self.assertEqual(result["resolution"]["raw_feedback"], feedback)
        _, _, body = self.get("/api/commitments?view=history")
        rows = json.loads(body)["commitments"]
        self.assertEqual({row["resolution_mode"] for row in rows},
                         {"COMPLETED", "RELEASED", "BYPASSED", "FORGOTTEN"})
        self.assertTrue(all(row["current_status"] == "CLOSED" for row in rows))

    def test_revision_closes_original_and_creates_only_minimal_lineage(self) -> None:
        _, original = self.post_capture("commit", "original text remains")
        original_id = original["commitment"]["commitment_id"]
        _, result = self.post_json(
            f"/api/commitments/{original_id}/resolve",
            {"mode": "REVISED", "raw_feedback": "changed deliberately",
             "replacement": {"raw_text": "replacement commitment", "report_at": "2030-03-01T00:00:00Z"}},
        )
        replacement_id = result["replacement_commitment"]["commitment_id"]
        self.assertEqual(result["resolution"]["replacement_commitment_id"], replacement_id)
        _, _, history_body = self.get("/api/commitments?view=history&resolution=REVISED")
        original = json.loads(history_body)["commitments"][0]
        self.assertEqual(original["raw_text"], "original text remains")
        self.assertEqual(original["replacement_commitment_id"], replacement_id)
        _, _, active_body = self.get("/api/commitments?view=active")
        replacement = json.loads(active_body)["commitments"][0]
        self.assertEqual(replacement["raw_text"], "replacement commitment")
        self.assertEqual(replacement["current_status"], "ACTIVE")

    def test_lifecycle_state_survives_restart_and_care_develop_stay_independent(self) -> None:
        self.post_capture("care", "care stays care")
        self.post_capture("develop", "develop stays develop")
        _, commitment = self.post_capture("commit", "close me")
        self.post_json(
            f"/api/commitments/{commitment['commitment']['commitment_id']}/resolve",
            {"mode": "COMPLETED", "raw_feedback": None},
        )
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)
        self.server = SERVER.create_server(
            "127.0.0.1", 0, self.data_dir, desktop_notifications=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        _, _, history = self.get("/api/commitments?view=history")
        self.assertEqual(json.loads(history)["commitments"][0]["resolution_mode"], "COMPLETED")
        for lane, text in (("care", "care stays care"), ("develop", "develop stays develop")):
            _, _, body = self.get(f"/api/captures?lane={lane}")
            self.assertEqual(json.loads(body)["captures"][0]["raw_text"], text)

    def test_calendar_files_are_projections_and_do_not_mutate_commitment(self) -> None:
        _, created = self.post_json(
            "/api/capture",
            {"mode": "commit", "raw_text": "calendar action", "start_at": "2030-01-01T10:00:00Z",
             "end_at": "2030-01-01T11:00:00Z", "report_at": "2030-01-01T12:00:00Z"},
        )
        identity = created["commitment"]["commitment_id"]
        status, headers, body = self.get(
            f"/api/commitments/{quote(identity, safe='')}/calendar.ics"
        )
        text = body.decode()
        self.assertEqual(status, 200)
        self.assertIn("text/calendar", headers["Content-Type"])
        self.assertIn("BEGIN:VCALENDAR", text)
        self.assertIn("DTSTART:20300101T100000Z", text)
        self.assertIn(identity, text)
        status, _, review = self.get(
            "/api/calendar/review.ics?start_at=2030-01-01T09%3A00%3A00Z&duration_minutes=20"
        )
        self.assertEqual(status, 200)
        self.assertIn("RRULE:FREQ=DAILY", review.decode())
        self.assertIn("HOME COMMITMENT REPORT", review.decode())
        _, _, active = self.get("/api/commitments?view=active")
        self.assertEqual(json.loads(active)["commitments"][0]["current_status"], "ACTIVE")

    def test_ui_exposes_separate_projections_feedback_and_no_explore(self) -> None:
        html = (APP_DIR / "index.html").read_text(encoding="utf-8")
        for label in ("ACTIVE ONE-SHOT COMMITMENTS", "REPORT DUE", "CARE HISTORY", "COMMITMENT HISTORY",
                      "DEVELOP HISTORY", "DUE NOW", "FUTURE CHAT NOTE", "CHAT HOME",
                      "REGULAR WEEK", "TODAY / DAILY REPORT", "RECURRENCE HISTORY",
                      "COMPLETED", "REVISED", "RELEASED", "BYPASSED", "FORGOTTEN"):
            self.assertIn(label, html)
        self.assertIn("Export failed:", html)
        self.assertIn("@media(max-width:720px)", html)
        self.assertNotIn("EXPLORE", html.upper())
        self.assertNotIn("psycholog", html.lower())

    def test_hundreds_of_scheduled_events_can_coexist(self) -> None:
        due = "2035-01-01T00:00:00Z"
        for index in range(200):
            self.server.store.create_event(
                "Chat", "Chat", due, "FUTURE_CHAT_NOTE", f"instruction {index}",
                [f"context:{index}"],
            )
        events = self.server.store.events("scheduled")
        self.assertEqual(len(events), 200)
        self.assertEqual(len({item["event_id"] for item in events}), 200)

    def test_backend_scheduler_marks_due_without_ui_and_does_not_execute(self) -> None:
        event = self.server.store.create_event(
            "Chat", "Chat", "2020-01-01T00:00:00Z", "FUTURE_CHAT_NOTE",
            "inspect explicit evidence", ["home:commitment:example"],
        )
        deadline = time.monotonic() + 4
        due = []
        while time.monotonic() < deadline:
            due = self.server.store.events("due")
            if due:
                break
            time.sleep(0.05)
        self.assertEqual(due[0]["event_id"], event["event_id"])
        self.assertEqual(due[0]["status"], "DUE")
        self.assertIsNotNone(due[0]["triggered_at"])
        self.assertNotIn("executed", due[0])
        self.assertNotIn("completed", due[0])

    def test_future_chat_note_is_durable_and_distinct_from_reed_commitments(self) -> None:
        _, reed = self.post_capture("commit", "Reed commitment")
        status, note = self.post_json(
            "/api/chat-home/future-note",
            {"due_at": "2035-01-01T00:00:00Z", "raw_instruction": "future Chat instruction",
             "context_refs": [reed["commitment"]["commitment_id"]]},
        )
        self.assertEqual(status, 201)
        self.assertEqual((note["author"], note["target_actor"]), ("Chat", "Chat"))
        self.assertEqual(note["context_refs"], [reed["commitment"]["commitment_id"]])
        self.assertEqual(len(self.server.store.commitments("active")), 1)
        self.assertEqual(self.server.store.chat_state()["explicit_executable_agent_commitments"], [])

        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)
        self.server = SERVER.create_server(
            "127.0.0.1", 0, self.data_dir, desktop_notifications=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        retained = self.server.store.events("scheduled", "Chat")
        self.assertEqual(retained[0]["raw_instruction"], "future Chat instruction")

    def test_chat_state_is_attributed_and_agent_commitments_require_execution_path(self) -> None:
        payload = {"current_pressure": "bounded pressure", "active_recommendations": ["inspect"],
                   "unresolved_questions": ["what survives?"], "continuation_refs": ["ref:1"],
                   "explicit_executable_agent_commitments": [
                       {"instruction": "run bounded check", "execution_path": "api:/bounded/check"}
                   ]}
        status, state = self.post_json("/api/chat-home", payload)
        self.assertEqual(status, 201)
        self.assertEqual(state["attribution"], "Chat")
        self.assertEqual(state["current_pressure"], "bounded pressure")
        self.assertEqual(state["continuation_refs"], ["ref:1"])
        self.assertEqual(state["explicit_executable_agent_commitments"][0]["execution_path"],
                         "api:/bounded/check")
        with self.assertRaises(HTTPError) as caught:
            self.post_json("/api/chat-home", {
                **payload, "explicit_executable_agent_commitments": [{"instruction": "no path"}]
            })
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()

    def test_bridge_projections_are_derived_bounded_and_preserve_context_refs(self) -> None:
        self.post_capture("care", "unrelated personal history must not enter bridge")
        _, event = self.post_json(
            "/api/chat-home/future-note",
            {"due_at": "2020-01-01T00:00:00Z", "raw_instruction": "bounded due instruction",
             "context_refs": ["decision:one", "commitment:two"]},
        )
        _, _, due_body = self.get("/agent_bridge/due_events.json")
        due = json.loads(due_body)
        self.assertEqual(due["authority"], "DERIVED_FROM_HOME")
        self.assertEqual(due["projection_kind"], "DUE_AGENT_EVENTS_DERIVED_PROJECTION")
        self.assertTrue(due["generated_at"])
        projected = next(item for item in due["events"] if item["event_id"] == event["event_id"])
        self.assertEqual(projected["context_refs"], ["decision:one", "commitment:two"])
        self.assertNotIn("unrelated personal history", due_body.decode())
        _, _, chat_body = self.get("/agent_bridge/chat_now.json")
        chat = json.loads(chat_body)
        self.assertEqual(chat["attribution"], "Chat")
        self.assertEqual(chat["authority"], "DERIVED_FROM_HOME")

    def test_cancel_and_acknowledge_do_not_change_referenced_state_or_imply_consequence(self) -> None:
        _, care = self.post_capture("care", "reference remains exact")
        _, scheduled = self.post_json(
            "/api/chat-home/future-note",
            {"due_at": "2035-01-01T00:00:00Z", "raw_instruction": "later",
             "context_refs": [care["id"]]},
        )
        _, cancelled = self.post_json(
            f"/api/events/{quote(scheduled['event_id'], safe='')}/cancel", {}
        )
        self.assertEqual(cancelled["status"], "CANCELLED")
        _, _, care_body = self.get("/api/captures?lane=care")
        self.assertEqual(json.loads(care_body)["captures"][0]["raw_text"], "reference remains exact")

        _, due = self.post_json(
            "/api/chat-home/future-note",
            {"due_at": "2020-01-01T00:00:00Z", "raw_instruction": "ack only",
             "context_refs": [care["id"]]},
        )
        _, acknowledged = self.post_json(
            f"/api/events/{quote(due['event_id'], safe='')}/acknowledge", {}
        )
        self.assertEqual(acknowledged["status"], "ACKNOWLEDGED")
        self.assertIsNotNone(acknowledged["acknowledged_at"])
        self.assertNotIn("successful", acknowledged)
        self.assertNotIn("consequence", acknowledged)

    def test_existing_one_shot_commitment_lifecycle_remains_unchanged(self) -> None:
        _, created = self.post_capture("commit", "one shot remains one shot")
        commitment = created["commitment"]
        self.assertEqual(commitment["recurrence_type"], "NONE")
        self.assertEqual(commitment["weekly_days"], [])
        self.assertIsNone(commitment["temporal_placement"])
        _, result = self.post_json(
            f"/api/commitments/{quote(commitment['commitment_id'], safe='')}/resolve",
            {"mode": "COMPLETED", "raw_feedback": "exact terminal feedback"},
        )
        self.assertEqual(result["resolution"]["mode"], "COMPLETED")
        self.assertEqual(len(self.server.store.occurrence_reports(commitment["commitment_id"])), 0)

    def test_daily_commitment_is_one_identity_across_multiple_reports(self) -> None:
        _, created = self.create_recurring(
            "one stable daily commitment", list(SERVER.WEEKDAYS), "MORNING"
        )
        identity = created["commitment"]["commitment_id"]
        today = date.today()
        self.backdate_commitment(
            identity, (today - timedelta(days=7)).isoformat() + "T00:00:00+00:00"
        )
        reports = [
            {"commitment_id": identity, "intended_local_date": (today - timedelta(days=1)).isoformat(),
             "outcome": "MET", "raw_feedback": "first"},
            {"commitment_id": identity, "intended_local_date": today.isoformat(),
             "outcome": "PARTIAL", "raw_feedback": "second"},
        ]
        status, retained = self.post_json("/api/recurring-reports", {"reports": reports})
        self.assertEqual(status, 201)
        self.assertEqual({item["commitment_id"] for item in retained["reports"]}, {identity})
        self.assertEqual(len(self.server.store.occurrence_reports(identity)), 2)
        parent = self.server.store.commitment(identity)
        self.assertEqual(parent["current_status"], "ACTIVE")
        self.assertEqual(parent["commitment_id"], identity)

    def test_subset_week_projection_and_today_include_only_expected_commitments(self) -> None:
        today = date.today()
        today_name = SERVER.WEEKDAYS[today.weekday()]
        other_name = SERVER.WEEKDAYS[(today.weekday() + 1) % 7]
        _, expected = self.create_recurring("expected today", [today_name, other_name], "EVENING")
        _, not_today = self.create_recurring("not expected today", [other_name], "ANYTIME")
        _, _, week_body = self.get("/api/regular-week")
        week = json.loads(week_body)["days"]
        self.assertEqual(
            {item["commitment_id"] for item in week[today_name]},
            {expected["commitment"]["commitment_id"]},
        )
        self.assertEqual(
            {item["commitment_id"] for item in week[other_name]},
            {expected["commitment"]["commitment_id"], not_today["commitment"]["commitment_id"]},
        )
        _, _, today_body = self.get(f"/api/today-recurring?local_date={today.isoformat()}")
        projected = json.loads(today_body)["commitments"]
        self.assertEqual([item["raw_text"] for item in projected], ["expected today"])

    def test_no_report_and_report_without_outcome_remain_distinct(self) -> None:
        _, created = self.create_recurring(
            "gap preserving commitment", list(SERVER.WEEKDAYS), None
        )
        identity = created["commitment"]["commitment_id"]
        today = date.today()
        self.backdate_commitment(
            identity, (today - timedelta(days=2)).isoformat() + "T00:00:00+00:00"
        )
        exact_feedback = "  raw feedback without category  "
        _, result = self.post_json(
            "/api/recurring-reports",
            {"reports": [{"commitment_id": identity,
                           "intended_local_date": today.isoformat(),
                           "outcome": None, "raw_feedback": exact_feedback}]},
        )
        self.assertIsNone(result["reports"][0]["outcome"])
        self.assertEqual(result["reports"][0]["raw_feedback"], exact_feedback)
        history = self.server.store.recurrence_history(identity, today.isoformat())
        states = [item["state"] for item in history["occurrences"]]
        self.assertIn("NO_REPORT", states)
        self.assertEqual(states[-1], "REPORTED_WITHOUT_OUTCOME")
        self.assertNotIn("BYPASSED", states)
        self.assertNotIn("FORGOTTEN", states)

    def test_closed_recurring_commitment_stops_future_projection_but_keeps_history(self) -> None:
        _, created = self.create_recurring(
            "close recurring parent", list(SERVER.WEEKDAYS), "AFTERNOON"
        )
        identity = created["commitment"]["commitment_id"]
        today = date.today()
        self.backdate_commitment(
            identity, (today - timedelta(days=2)).isoformat() + "T00:00:00+00:00"
        )
        self.post_json(
            f"/api/commitments/{quote(identity, safe='')}/resolve",
            {"mode": "RELEASED", "raw_feedback": "parent explicitly closed"},
        )
        _, _, today_body = self.get(f"/api/today-recurring?local_date={today.isoformat()}")
        self.assertNotIn(identity, {
            item["commitment_id"] for item in json.loads(today_body)["commitments"]
        })
        history = self.server.store.recurrence_history(
            identity, (today + timedelta(days=14)).isoformat()
        )
        self.assertTrue(history["occurrences"])
        self.assertLessEqual(
            max(date.fromisoformat(item["intended_local_date"]) for item in history["occurrences"]),
            today,
        )
        self.assertTrue(all(item["state"] == "NO_REPORT" for item in history["occurrences"]))

    def test_restart_preserves_recurrence_and_occurrence_report(self) -> None:
        today = date.today()
        weekday = SERVER.WEEKDAYS[today.weekday()]
        _, created = self.create_recurring("restart regular", [weekday], "ANYTIME")
        identity = created["commitment"]["commitment_id"]
        self.post_json(
            "/api/recurring-reports",
            {"reports": [{"commitment_id": identity,
                           "intended_local_date": today.isoformat(),
                           "outcome": "NOT_APPLICABLE", "raw_feedback": "  exact restart text  "}]},
        )
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=5)
        self.server = SERVER.create_server(
            "127.0.0.1", 0, self.data_dir, desktop_notifications=False
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"
        parent = self.server.store.commitment(identity)
        self.assertEqual(parent["weekly_days"], [weekday])
        self.assertEqual(parent["temporal_placement"], "ANYTIME")
        reports = self.server.store.occurrence_reports(identity)
        self.assertEqual(reports[0]["outcome"], "NOT_APPLICABLE")
        self.assertEqual(reports[0]["raw_feedback"], "  exact restart text  ")


if __name__ == "__main__":
    unittest.main()
