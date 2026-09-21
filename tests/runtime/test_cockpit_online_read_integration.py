from __future__ import annotations

import http.client
from pathlib import Path
import tempfile
import threading
import unittest

from src.cockpit.live_runtime_projection import (
    RuntimeProjectionServer,
    RuntimeSources,
    build_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]


class CockpitOnlineReadIntegrationPressure(unittest.TestCase):
    def test_unconfigured_sources_are_explicit_and_read_projection_has_no_effect(self) -> None:
        snapshot = build_snapshot(RuntimeSources(repo=ROOT))
        state = snapshot["state"]
        self.assertEqual(state["projection_status"], "AVAILABLE")
        self.assertEqual(state["projection_effect"], "NONE")
        self.assertEqual(state["authority_effect"], "NONE")
        self.assertEqual(state["execution_effect"], "NONE")
        self.assertEqual(state["standing_effect"], "NONE")
        self.assertEqual(state["cross_store_atomicity"], "NOT_ESTABLISHED")
        self.assertTrue(
            all(source["status"] == "NOT_CONFIGURED" for source in state["sources"])
        )

    def test_missing_configured_source_is_partial_not_healthy_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing-controller.sqlite3"
            snapshot = build_snapshot(
                RuntimeSources(repo=ROOT, controller_db=missing)
            )
            state = snapshot["state"]
            self.assertEqual(state["projection_status"], "PARTIAL")
            controller = next(
                source for source in state["sources"]
                if source["source"] == "controller"
            )
            self.assertEqual(controller["status"], "UNAVAILABLE")
            self.assertFalse(missing.exists())

    def test_snapshot_is_stable_over_same_durable_state(self) -> None:
        sources = RuntimeSources(repo=ROOT)
        first = build_snapshot(sources)
        second = build_snapshot(sources)
        self.assertEqual(first["state_sha256"], second["state_sha256"])
        self.assertEqual(first["state"], second["state"])

    def test_http_write_methods_are_rejected(self) -> None:
        server = RuntimeProjectionServer(
            ("127.0.0.1", 0),
            RuntimeSources(repo=ROOT),
            0.05,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = server.server_address
            for method in ("POST", "PUT", "PATCH", "DELETE"):
                conn = http.client.HTTPConnection(host, port, timeout=2)
                conn.request(method, "/runtime/snapshot.json", body=b"{}")
                response = conn.getresponse()
                response.read()
                self.assertEqual(response.status, 405)
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
