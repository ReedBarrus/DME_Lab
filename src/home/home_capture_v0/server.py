#!/usr/bin/env python3
"""Bounded local server for Home Capture v0.

The server persists only raw user-authored CARE, COMMIT, and DEVELOP captures.
It deliberately performs no interpretation or standing promotion.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import shutil
import socket
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = ROOT / "data"
INDEX_PATH = ROOT / "index.html"
ALLOWED_LANES = {"care", "commit", "develop"}
MAX_CAPTURE_BYTES = 256_000
MAX_HISTORY_ROWS = 2_000


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_private_ipv4() -> str | None:
    """Return a private LAN address when one is visible, without contacting it."""
    candidates: list[str] = []
    try:
        for result in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidates.append(result[4][0])
    except OSError:
        return None
    for value in dict.fromkeys(candidates):
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        if address.is_private and not address.is_loopback and not address.is_link_local:
            return value
    return None


class HomeStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir.resolve()
        self.db_path = self.data_dir / "home_capture.sqlite3"
        self.exports_dir = self.data_dir / "exports"

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

        # Preserve existing v0 data while moving future state into data/.
        legacy_db = ROOT / "home_capture.sqlite3"
        using_default_data_dir = self.data_dir == DEFAULT_DATA_DIR.resolve()
        if using_default_data_dir and legacy_db.exists() and not self.db_path.exists():
            shutil.move(str(legacy_db), str(self.db_path))

        with self.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS captures (
                    id TEXT PRIMARY KEY,
                    mode TEXT NOT NULL CHECK (mode IN ('care','commit','develop')),
                    raw_text TEXT NOT NULL,
                    origin TEXT NOT NULL DEFAULT 'user_explicit',
                    client_time TEXT,
                    created_at_utc TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_captures_created "
                "ON captures(created_at_utc DESC)"
            )

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def connection(self):
        conn = self.connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def count(self) -> int:
        with self.connection() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0])

    def insert(self, lane: str, raw_text: str, client_time: object) -> dict[str, object]:
        record: dict[str, object] = {
            "id": f"home:capture:{uuid.uuid4()}",
            "mode": lane,
            "raw_text": raw_text,
            "origin": "user_explicit",
            "client_time": client_time if isinstance(client_time, str) else None,
            "created_at_utc": now_utc_iso(),
        }
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO captures"
                "(id, mode, raw_text, origin, client_time, created_at_utc) "
                "VALUES(:id,:mode,:raw_text,:origin,:client_time,:created_at_utc)",
                record,
            )
        return record

    def history(
        self, lane: str | None = None, query: str = "", order: str = "desc", limit: int = 500
    ) -> list[dict[str, object]]:
        clauses: list[str] = []
        parameters: list[object] = []
        if lane:
            clauses.append("mode = ?")
            parameters.append(lane)
        if query:
            clauses.append("raw_text LIKE ? ESCAPE '\\'")
            escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            parameters.append(f"%{escaped}%")
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        direction = "ASC" if order == "asc" else "DESC"
        parameters.append(max(1, min(limit, MAX_HISTORY_ROWS)))
        sql = (
            "SELECT id, mode, raw_text, origin, client_time, created_at_utc "
            f"FROM captures{where} ORDER BY created_at_utc {direction}, id {direction} LIMIT ?"
        )
        with self.connection() as conn:
            return [dict(row) for row in conn.execute(sql, parameters).fetchall()]

    def export_rows(self) -> list[dict[str, object]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id, mode, raw_text, origin, client_time, created_at_utc "
                "FROM captures ORDER BY created_at_utc ASC, id ASC"
            ).fetchall()
        return [dict(row) for row in rows]


class HomeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def server_bind(self) -> None:
        # Windows otherwise permits competing listeners in some configurations.
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

    def __init__(
        self,
        address: tuple[str, int],
        store: HomeStore,
        access_mode: str,
    ):
        self.store = store
        self.access_mode = access_mode
        super().__init__(address, HomeHandler)

    @property
    def advertised_url(self) -> str | None:
        if self.access_mode != "lan":
            return None
        address = discover_private_ipv4()
        return f"http://{address}:{self.server_port}" if address else None


class HomeHandler(BaseHTTPRequestHandler):
    server_version = "HomeCapture/0.2"
    server: HomeServer

    def _common_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")

    def _send_bytes(
        self,
        body: bytes,
        content_type: str,
        status: HTTPStatus = HTTPStatus.OK,
        disposition: str | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if disposition:
            self.send_header("Content-Disposition", disposition)
        self._common_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
            status,
        )

    def _send_text(
        self,
        body: str,
        content_type: str = "text/plain; charset=utf-8",
        status: HTTPStatus = HTTPStatus.OK,
        disposition: str | None = None,
    ) -> None:
        self._send_bytes(body.encode("utf-8"), content_type, status, disposition)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self._send_text(INDEX_PATH.read_text(encoding="utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/health":
            self._send_json(
                {
                    "service": "home_capture_v0",
                    "status": "operational",
                    "version": "0.2",
                    "capture_count": self.server.store.count(),
                    "access_mode": self.server.access_mode,
                    "phone_url": self.server.advertised_url,
                    "public_internet_supported": False,
                    "process_id": os.getpid(),
                }
            )
            return
        if path in {"/api/recent", "/api/captures"}:
            query = parse_qs(parsed.query)
            lane = query.get("lane", [""])[0].strip().lower()
            if lane in {"", "all"}:
                lane = ""
            elif lane not in ALLOWED_LANES:
                self._send_json({"error": "invalid_lane"}, HTTPStatus.BAD_REQUEST)
                return
            order = query.get("order", ["desc"])[0].strip().lower()
            if order not in {"asc", "desc"}:
                self._send_json({"error": "invalid_order"}, HTTPStatus.BAD_REQUEST)
                return
            try:
                limit = int(query.get("limit", ["500"])[0])
            except ValueError:
                self._send_json({"error": "invalid_limit"}, HTTPStatus.BAD_REQUEST)
                return
            rows = self.server.store.history(
                lane=lane or None,
                query=query.get("q", [""])[0],
                order=order,
                limit=limit,
            )
            self._send_json({"captures": rows, "count": self.server.store.count()})
            return
        if path == "/api/export.jsonl":
            body = "\n".join(
                json.dumps(row, ensure_ascii=False) for row in self.server.store.export_rows()
            )
            if body:
                body += "\n"
            self._send_text(
                body,
                "application/x-ndjson; charset=utf-8",
                disposition='attachment; filename="home-captures.jsonl"',
            )
            return
        if path == "/api/export.md":
            rows = self.server.store.history(order="asc", limit=30)
            lines = [
                "# Home Capture v0 — recent packet",
                "",
                "> Raw user-authored captures only. No derived interpretation is included.",
                "",
            ]
            for row in rows:
                when = row["client_time"] or row["created_at_utc"]
                lines += [
                    f"## {str(row['mode']).upper()} — {when}",
                    f"- ref: `{row['id']}`",
                    f"- origin: `{row['origin']}`",
                    "",
                    str(row["raw_text"]),
                    "",
                ]
            self._send_text("\n".join(lines), "text/markdown; charset=utf-8")
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        if urlparse(self.path).path != "/api/capture":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json({"error": "content_type_must_be_json"}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "invalid_content_length"}, HTTPStatus.BAD_REQUEST)
            return
        if length <= 0 or length > MAX_CAPTURE_BYTES:
            self._send_json({"error": "invalid_content_length"}, HTTPStatus.BAD_REQUEST)
            return
        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "invalid_json"}, HTTPStatus.BAD_REQUEST)
            return
        if not isinstance(data, dict):
            self._send_json({"error": "invalid_json_object"}, HTTPStatus.BAD_REQUEST)
            return

        lane = str(data.get("mode", "")).strip().lower()
        raw_text_value = data.get("raw_text")
        if lane not in ALLOWED_LANES:
            self._send_json({"error": "invalid_mode"}, HTTPStatus.BAD_REQUEST)
            return
        if not isinstance(raw_text_value, str) or not raw_text_value.strip():
            self._send_json({"error": "empty_capture"}, HTTPStatus.BAD_REQUEST)
            return

        record = self.server.store.insert(lane, raw_text_value, data.get("client_time"))
        self._send_json(record, HTTPStatus.CREATED)

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep hidden-launcher logs quiet except for client/server failures.
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)


def create_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    data_dir: Path = DEFAULT_DATA_DIR,
    access_mode: str = "desktop",
) -> HomeServer:
    store = HomeStore(data_dir)
    store.initialize()
    return HomeServer((host, port), store, access_mode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Home Capture v0")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--access-mode", choices=("desktop", "lan"), default="desktop")
    args = parser.parse_args()

    server = create_server(args.host, args.port, args.data_dir, args.access_mode)
    display_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    print(f"Home Capture v0 running at http://{display_host}:{server.server_port}")
    print(f"Database: {server.store.db_path}")
    if server.advertised_url:
        print(f"Trusted-LAN phone URL: {server.advertised_url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
