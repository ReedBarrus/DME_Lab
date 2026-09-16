from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.parse import urlencode
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
        self.server = SERVER.create_server("127.0.0.1", 0, self.data_dir)
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

        self.server = SERVER.create_server("127.0.0.1", 0, self.data_dir)
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
                "127.0.0.1", self.server.server_port, Path(self.temp_dir.name) / "other"
            )
            duplicate.server_close()

    def test_lan_health_advertises_private_url_only_in_lan_mode(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        with mock.patch.object(SERVER, "discover_private_ipv4", return_value="192.168.1.44"):
            self.server = SERVER.create_server("127.0.0.1", 0, self.data_dir, "lan")
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


if __name__ == "__main__":
    unittest.main()
