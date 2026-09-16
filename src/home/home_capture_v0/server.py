#!/usr/bin/env python3
"""Home Capture v0: immutable raw captures plus explicit commitment lifecycle."""
from __future__ import annotations

import argparse
import ctypes
import ipaddress
import json
import os
import shutil
import socket
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = ROOT / "data"
INDEX_PATH = ROOT / "index.html"
ALLOWED_LANES = {"care", "commit", "develop"}
RESOLUTION_MODES = {"COMPLETED", "REVISED", "RELEASED", "BYPASSED", "FORGOTTEN"}
MAX_CAPTURE_BYTES = 256_000
MAX_HISTORY_ROWS = 2_000
SCHEMA_VERSION = 5
LEGACY_NAMESPACE = uuid.UUID("597b99c4-48ef-4f48-8ad0-ce69b86dc26e")
EVENT_STATUSES = {"SCHEDULED", "DUE", "ACKNOWLEDGED", "CANCELLED"}
RECURRENCE_TYPES = {"NONE", "WEEKLY_PATTERN"}
WEEKDAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
TEMPORAL_PLACEMENTS = {"ANYTIME", "MORNING", "AFTERNOON", "EVENING"}
OCCURRENCE_OUTCOMES = {"MET", "PARTIAL", "NOT_MET", "NOT_APPLICABLE"}
AMENDMENT_KINDS = {"INITIAL", "RECORDING_CORRECTION", "INTENTION_CHANGE"}


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: object, field: str) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError(f"invalid_{field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid_{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field}_requires_timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def validate_schedule(start: object, end: object, report: object) -> dict[str, str | None]:
    result = {
        "start_at": parse_time(start, "start_at"),
        "end_at": parse_time(end, "end_at"),
        "report_at": parse_time(report, "report_at"),
    }
    if result["end_at"] and not result["start_at"]:
        raise ValueError("end_at_requires_start_at")
    if result["start_at"] and result["end_at"]:
        if datetime.fromisoformat(result["end_at"]) < datetime.fromisoformat(result["start_at"]):
            raise ValueError("end_at_before_start_at")
    return result


def validate_recurrence(
    recurrence_type: object, weekly_days: object, temporal_placement: object
) -> dict[str, object]:
    recurrence = "NONE" if recurrence_type is None or recurrence_type == "" else str(recurrence_type).upper()
    if recurrence not in RECURRENCE_TYPES:
        raise ValueError("invalid_recurrence_type")
    placement = None if temporal_placement is None or temporal_placement == "" else str(temporal_placement).upper()
    if placement is not None and placement not in TEMPORAL_PLACEMENTS:
        raise ValueError("invalid_temporal_placement")
    days = [] if weekly_days is None else weekly_days
    if not isinstance(days, list) or any(str(day).upper() not in WEEKDAYS for day in days):
        raise ValueError("invalid_weekly_days")
    ordered_days = [day for day in WEEKDAYS if day in {str(value).upper() for value in days}]
    if recurrence == "NONE":
        if ordered_days or placement is not None:
            raise ValueError("nonrecurring_commitment_cannot_have_recurrence_coordinates")
        return {"recurrence_type": "NONE", "weekly_days_json": None,
                "temporal_placement": None}
    if not ordered_days:
        raise ValueError("weekly_pattern_requires_days")
    return {
        "recurrence_type": "WEEKLY_PATTERN",
        "weekly_days_json": json.dumps(ordered_days, separators=(",", ":")),
        "temporal_placement": placement,
    }


def parse_local_date(value: object, field: str = "intended_local_date") -> date:
    if not isinstance(value, str):
        raise ValueError(f"invalid_{field}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid_{field}") from exc


def discover_private_ipv4() -> str | None:
    try:
        values = [item[4][0] for item in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)]
    except OSError:
        return None
    for value in dict.fromkeys(values):
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
        self.backups_dir = self.data_dir / "backups"
        self.agent_bridge_dir = self.data_dir / "agent_bridge"
        self.last_migration_backup: Path | None = None

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10, cached_statements=0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    @contextmanager
    def connection(self):
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _backup(self, prior_version: int) -> Path:
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.backups_dir / f"home_capture_pre_schema_v{prior_version}_{stamp}.sqlite3"
        source, target = sqlite3.connect(self.db_path), sqlite3.connect(path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        return path

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.agent_bridge_dir.mkdir(parents=True, exist_ok=True)
        legacy = ROOT / "home_capture.sqlite3"
        if self.data_dir == DEFAULT_DATA_DIR.resolve() and legacy.exists() and not self.db_path.exists():
            shutil.move(str(legacy), str(self.db_path))
        if self.db_path.exists() and self.db_path.stat().st_size:
            probe = sqlite3.connect(self.db_path)
            try:
                version = int(probe.execute("PRAGMA user_version").fetchone()[0])
                has_captures = probe.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name='captures'"
                ).fetchone()
            finally:
                probe.close()
            if has_captures and version < SCHEMA_VERSION:
                self.last_migration_backup = self._backup(version)
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS captures(
                  id TEXT PRIMARY KEY,
                  mode TEXT NOT NULL CHECK(mode IN ('care','commit','develop')),
                  raw_text TEXT NOT NULL,
                  origin TEXT NOT NULL DEFAULT 'user_explicit',
                  client_time TEXT,
                  created_at_utc TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_captures_created
                  ON captures(created_at_utc DESC);
                CREATE TABLE IF NOT EXISTS commitments(
                  commitment_id TEXT PRIMARY KEY,
                  source_capture_id TEXT NOT NULL UNIQUE REFERENCES captures(id),
                  created_at_utc TEXT NOT NULL,
                  current_status TEXT NOT NULL CHECK(current_status IN ('ACTIVE','CLOSED')),
                  current_specification_id TEXT,
                  start_at TEXT,
                  end_at TEXT,
                  report_at TEXT,
                  recurrence_type TEXT NOT NULL DEFAULT 'NONE' CHECK(
                    recurrence_type IN ('NONE','WEEKLY_PATTERN')),
                  weekly_days_json TEXT,
                  temporal_placement TEXT CHECK(temporal_placement IS NULL OR
                    temporal_placement IN ('ANYTIME','MORNING','AFTERNOON','EVENING'))
                );
                CREATE TABLE IF NOT EXISTS commitment_specifications(
                  specification_id TEXT PRIMARY KEY,
                  commitment_id TEXT NOT NULL REFERENCES commitments(commitment_id),
                  created_at_utc TEXT NOT NULL,
                  effective_at TEXT NOT NULL,
                  statement TEXT NOT NULL,
                  start_at TEXT,
                  end_at TEXT,
                  report_at TEXT,
                  recurrence_type TEXT NOT NULL CHECK(
                    recurrence_type IN ('NONE','WEEKLY_PATTERN')),
                  weekly_days_json TEXT,
                  temporal_placement TEXT CHECK(temporal_placement IS NULL OR
                    temporal_placement IN ('ANYTIME','MORNING','AFTERNOON','EVENING')),
                  prior_specification_id TEXT REFERENCES commitment_specifications(specification_id),
                  amendment_kind TEXT NOT NULL CHECK(amendment_kind IN
                    ('INITIAL','RECORDING_CORRECTION','INTENTION_CHANGE')),
                  raw_amendment_reason TEXT,
                  source_capture_id TEXT REFERENCES captures(id)
                );
                CREATE INDEX IF NOT EXISTS idx_commitment_specifications_parent
                  ON commitment_specifications(commitment_id,effective_at,created_at_utc);
                CREATE TABLE IF NOT EXISTS commitment_resolutions(
                  resolution_id TEXT PRIMARY KEY,
                  commitment_id TEXT NOT NULL UNIQUE REFERENCES commitments(commitment_id),
                  mode TEXT NOT NULL CHECK(mode IN
                    ('COMPLETED','REVISED','RELEASED','BYPASSED','FORGOTTEN')),
                  resolved_at_utc TEXT NOT NULL,
                  raw_feedback TEXT,
                  replacement_commitment_id TEXT REFERENCES commitments(commitment_id)
                );
                CREATE INDEX IF NOT EXISTS idx_commitments_status
                  ON commitments(current_status, created_at_utc DESC);
                CREATE TABLE IF NOT EXISTS scheduled_events(
                  event_id TEXT PRIMARY KEY,
                  author TEXT NOT NULL,
                  target_actor TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  due_at TEXT NOT NULL,
                  kind TEXT NOT NULL,
                  raw_instruction TEXT NOT NULL,
                  context_refs_json TEXT NOT NULL,
                  status TEXT NOT NULL CHECK(status IN
                    ('SCHEDULED','DUE','ACKNOWLEDGED','CANCELLED')),
                  triggered_at TEXT,
                  acknowledged_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_scheduled_events_due
                  ON scheduled_events(status,due_at);
                CREATE TABLE IF NOT EXISTS commitment_occurrence_reports(
                  report_id TEXT PRIMARY KEY,
                  commitment_id TEXT NOT NULL REFERENCES commitments(commitment_id),
                  specification_id TEXT REFERENCES commitment_specifications(specification_id),
                  intended_local_date TEXT NOT NULL,
                  reported_at TEXT NOT NULL,
                  outcome TEXT CHECK(outcome IS NULL OR outcome IN
                    ('MET','PARTIAL','NOT_MET','NOT_APPLICABLE')),
                  raw_feedback TEXT,
                  UNIQUE(commitment_id,intended_local_date)
                );
                CREATE INDEX IF NOT EXISTS idx_occurrence_reports_commitment
                  ON commitment_occurrence_reports(commitment_id,intended_local_date);
                CREATE TABLE IF NOT EXISTS chat_home_state(
                  state_id TEXT PRIMARY KEY CHECK(state_id='chat'),
                  current_pressure_json TEXT,
                  active_recommendations_json TEXT NOT NULL,
                  unresolved_questions_json TEXT NOT NULL,
                  continuation_refs_json TEXT NOT NULL,
                  executable_agent_commitments_json TEXT NOT NULL,
                  generated_at_utc TEXT NOT NULL,
                  updated_at_utc TEXT NOT NULL
                );
                """
            )
            commitment_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(commitments)")
            }
            if "recurrence_type" not in commitment_columns:
                connection.execute(
                    "ALTER TABLE commitments ADD COLUMN recurrence_type TEXT NOT NULL "
                    "DEFAULT 'NONE' CHECK(recurrence_type IN ('NONE','WEEKLY_PATTERN'))"
                )
            if "weekly_days_json" not in commitment_columns:
                connection.execute("ALTER TABLE commitments ADD COLUMN weekly_days_json TEXT")
            if "temporal_placement" not in commitment_columns:
                connection.execute(
                    "ALTER TABLE commitments ADD COLUMN temporal_placement TEXT CHECK("
                    "temporal_placement IS NULL OR temporal_placement IN "
                    "('ANYTIME','MORNING','AFTERNOON','EVENING'))"
                )
            if "current_specification_id" not in commitment_columns:
                connection.execute(
                    "ALTER TABLE commitments ADD COLUMN current_specification_id TEXT"
                )
            for capture in connection.execute(
                "SELECT id,created_at_utc FROM captures WHERE mode='commit'"
            ):
                commitment_id = f"home:commitment:{uuid.uuid5(LEGACY_NAMESPACE, capture['id'])}"
                connection.execute(
                    "INSERT OR IGNORE INTO commitments("
                    "commitment_id,source_capture_id,created_at_utc,current_status,start_at,end_at,"
                    "report_at,recurrence_type,weekly_days_json,temporal_placement) "
                    "VALUES(?,?,?,'ACTIVE',NULL,NULL,NULL,'NONE',NULL,NULL)",
                    (commitment_id, capture["id"], capture["created_at_utc"]),
                )
            for row in connection.execute(
                "SELECT c.*,x.raw_text FROM commitments c "
                "JOIN captures x ON x.id=c.source_capture_id"
            ).fetchall():
                existing_specification = connection.execute(
                    "SELECT specification_id FROM commitment_specifications "
                    "WHERE commitment_id=? ORDER BY created_at_utc DESC,specification_id DESC LIMIT 1",
                    (row["commitment_id"],),
                ).fetchone()
                if existing_specification is None:
                    specification_id = str(uuid.uuid5(
                        LEGACY_NAMESPACE, f"{row['commitment_id']}:initial-specification"
                    ))
                    specification_id = f"home:commitment-specification:{specification_id}"
                    connection.execute(
                        "INSERT INTO commitment_specifications("
                        "specification_id,commitment_id,created_at_utc,effective_at,statement,"
                        "start_at,end_at,report_at,recurrence_type,weekly_days_json,temporal_placement,"
                        "prior_specification_id,amendment_kind,raw_amendment_reason,source_capture_id) "
                        "VALUES(?,?,?,?,?,?,?,?,?,?,?,NULL,'INITIAL',NULL,?)",
                        (specification_id, row["commitment_id"], row["created_at_utc"],
                         row["created_at_utc"], row["raw_text"], row["start_at"], row["end_at"],
                         row["report_at"], row["recurrence_type"], row["weekly_days_json"],
                         row["temporal_placement"], row["source_capture_id"]),
                    )
                else:
                    specification_id = existing_specification["specification_id"]
                if row["current_specification_id"] is None:
                    connection.execute(
                        "UPDATE commitments SET current_specification_id=? WHERE commitment_id=?",
                        (specification_id, row["commitment_id"]),
                    )
            report_columns = {
                row["name"] for row in connection.execute(
                    "PRAGMA table_info(commitment_occurrence_reports)"
                )
            }
            if "specification_id" not in report_columns:
                connection.execute(
                    "ALTER TABLE commitment_occurrence_reports ADD COLUMN specification_id TEXT"
                )
            connection.execute(
                "UPDATE commitment_occurrence_reports SET specification_id=("
                "SELECT current_specification_id FROM commitments c "
                "WHERE c.commitment_id=commitment_occurrence_reports.commitment_id) "
                "WHERE specification_id IS NULL"
            )
            connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            timestamp = now_utc_iso()
            connection.execute(
                "INSERT OR IGNORE INTO chat_home_state VALUES"
                "('chat',NULL,'[]','[]','[]','[]',?,?)", (timestamp, timestamp)
            )
        self.generate_bridge()

    def count(self) -> int:
        with self.connection() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM captures").fetchone()[0])

    @staticmethod
    def _capture(lane: str, text: str, client_time: object) -> dict[str, object]:
        return {
            "id": f"home:capture:{uuid.uuid4()}", "mode": lane, "raw_text": text,
            "origin": "user_explicit",
            "client_time": client_time if isinstance(client_time, str) else None,
            "created_at_utc": now_utc_iso(),
        }

    @staticmethod
    def _insert_capture(connection: sqlite3.Connection, record: dict[str, object]) -> None:
        connection.execute(
            "INSERT INTO captures VALUES(:id,:mode,:raw_text,:origin,:client_time,:created_at_utc)",
            record,
        )

    @staticmethod
    def _insert_commitment(connection, capture, schedule, recurrence=None) -> dict[str, object]:
        recurrence = recurrence or {
            "recurrence_type": "NONE", "weekly_days_json": None,
            "temporal_placement": None,
        }
        record = {
            "commitment_id": f"home:commitment:{uuid.uuid4()}",
            "source_capture_id": capture["id"], "created_at_utc": capture["created_at_utc"],
            "current_status": "ACTIVE", **schedule, **recurrence,
        }
        connection.execute(
            "INSERT INTO commitments("
            "commitment_id,source_capture_id,created_at_utc,current_status,start_at,end_at,report_at,"
            "recurrence_type,weekly_days_json,temporal_placement) VALUES("
            ":commitment_id,:source_capture_id,:created_at_utc,:current_status,:start_at,:end_at,"
            ":report_at,:recurrence_type,:weekly_days_json,:temporal_placement)", record,
        )
        specification_id = f"home:commitment-specification:{uuid.uuid4()}"
        connection.execute(
            "INSERT INTO commitment_specifications("
            "specification_id,commitment_id,created_at_utc,effective_at,statement,start_at,end_at,"
            "report_at,recurrence_type,weekly_days_json,temporal_placement,prior_specification_id,"
            "amendment_kind,raw_amendment_reason,source_capture_id) VALUES("
            "?,?,?,?,?,?,?,?,?,?,?,NULL,'INITIAL',NULL,?)",
            (specification_id, record["commitment_id"], record["created_at_utc"],
             record["created_at_utc"], capture["raw_text"], record["start_at"], record["end_at"],
             record["report_at"], record["recurrence_type"], record["weekly_days_json"],
             record["temporal_placement"], capture["id"]),
        )
        connection.execute(
            "UPDATE commitments SET current_specification_id=? WHERE commitment_id=?",
            (specification_id, record["commitment_id"]),
        )
        record["weekly_days"] = (
            json.loads(record["weekly_days_json"]) if record["weekly_days_json"] else []
        )
        record.pop("weekly_days_json")
        record.update({
            "specification_id": specification_id,
            "current_specification_id": specification_id,
            "specification_created_at": record["created_at_utc"],
            "effective_at": record["created_at_utc"],
            "amendment_kind": "INITIAL",
            "prior_specification_id": None,
            "raw_amendment_reason": None,
        })
        return record

    def insert(self, lane, text, client_time, schedule=None, recurrence=None) -> dict[str, object]:
        record = self._capture(lane, text, client_time)
        with self.connection() as connection:
            self._insert_capture(connection, record)
            if lane == "commit":
                empty = {"start_at": None, "end_at": None, "report_at": None}
                record["commitment"] = self._insert_commitment(
                    connection, record, schedule or empty, recurrence
                )
        return record

    def history(self, lane=None, query="", order="desc", limit=500) -> list[dict[str, object]]:
        clauses, parameters = [], []
        if lane:
            clauses.append("mode=?")
            parameters.append(lane)
        if query:
            clauses.append("raw_text LIKE ? ESCAPE '\\'")
            escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            parameters.append(f"%{escaped}%")
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        direction = "ASC" if order == "asc" else "DESC"
        parameters.append(max(1, min(limit, MAX_HISTORY_ROWS)))
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT id,mode,raw_text,origin,client_time,created_at_utc FROM captures"
                f"{where} ORDER BY created_at_utc {direction},id {direction} LIMIT ?", parameters,
            ).fetchall()
        return [dict(row) for row in rows]

    def export_rows(self) -> list[dict[str, object]]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT id,mode,raw_text,origin,client_time,created_at_utc FROM captures "
                "ORDER BY created_at_utc,id"
            ).fetchall()
        return [dict(row) for row in rows]

    def commitments(self, view="active", resolution=None, observed_at=None):
        observed = parse_time(observed_at or now_utc_iso(), "observed_at")
        if view in {"active", "report_due"}:
            clauses = ["c.current_status='ACTIVE'"]
        elif view == "history":
            clauses = ["c.current_status='CLOSED'"]
        else:
            raise ValueError("invalid_commitment_view")
        parameters: list[object] = []
        if resolution:
            mode = resolution.upper()
            if mode not in RESOLUTION_MODES:
                raise ValueError("invalid_resolution_mode")
            clauses.append("r.mode=?")
            parameters.append(mode)
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT c.commitment_id,c.source_capture_id,c.created_at_utc,c.current_status,"
                "c.current_specification_id,s.specification_id,s.created_at_utc specification_created_at,"
                "s.effective_at,s.statement raw_text,s.start_at,s.end_at,s.report_at,"
                "s.recurrence_type,s.weekly_days_json,s.temporal_placement,s.prior_specification_id,"
                "s.amendment_kind,s.raw_amendment_reason,x.origin,x.client_time,r.resolution_id,"
                "r.mode resolution_mode,r.resolved_at_utc,r.raw_feedback,"
                "r.replacement_commitment_id FROM commitments c "
                "JOIN captures x ON x.id=c.source_capture_id "
                "JOIN commitment_specifications s ON s.specification_id=c.current_specification_id "
                "LEFT JOIN commitment_resolutions r ON r.commitment_id=c.commitment_id "
                f"WHERE {' AND '.join(clauses)} ORDER BY c.created_at_utc DESC,c.commitment_id DESC",
                parameters,
            ).fetchall()
        result = [dict(row) for row in rows]
        for item in result:
            item["weekly_days"] = (
                json.loads(item.pop("weekly_days_json")) if item.get("weekly_days_json") else []
            )
            item["report_due"] = bool(
                item["current_status"] == "ACTIVE" and item["report_at"] and
                datetime.fromisoformat(item["report_at"]) <= datetime.fromisoformat(observed)
            )
        return [item for item in result if item["report_due"]] if view == "report_due" else result

    @staticmethod
    def _specification_row(row: sqlite3.Row) -> dict[str, object]:
        item = dict(row)
        item["weekly_days"] = (
            json.loads(item.pop("weekly_days_json")) if item.get("weekly_days_json") else []
        )
        return item

    def specifications(self, commitment_id: str) -> list[dict[str, object]]:
        with self.connection() as connection:
            exists = connection.execute(
                "SELECT 1 FROM commitments WHERE commitment_id=?", (commitment_id,)
            ).fetchone()
            if exists is None:
                raise LookupError("commitment_not_found")
            rows = connection.execute(
                "SELECT specification_id,commitment_id,created_at_utc,effective_at,statement,"
                "start_at,end_at,report_at,recurrence_type,weekly_days_json,temporal_placement,"
                "prior_specification_id,amendment_kind,raw_amendment_reason,source_capture_id "
                "FROM commitment_specifications WHERE commitment_id=? "
                "ORDER BY created_at_utc,specification_id", (commitment_id,)
            ).fetchall()
        return [self._specification_row(row) for row in rows]

    def amend(self, commitment_id, amendment_kind, statement, schedule, recurrence, reason=None):
        kind = str(amendment_kind or "").upper()
        if kind not in AMENDMENT_KINDS - {"INITIAL"}:
            raise ValueError("invalid_amendment_kind")
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError("empty_commitment_statement")
        if reason is not None and not isinstance(reason, str):
            raise ValueError("invalid_raw_amendment_reason")
        created = now_utc_iso()
        specification_id = f"home:commitment-specification:{uuid.uuid4()}"
        with self.connection() as connection:
            current = connection.execute(
                "SELECT current_status,current_specification_id FROM commitments "
                "WHERE commitment_id=?", (commitment_id,)
            ).fetchone()
            if current is None:
                raise LookupError("commitment_not_found")
            if current["current_status"] != "ACTIVE":
                raise RuntimeError("commitment_already_closed")
            prior = current["current_specification_id"]
            connection.execute(
                "INSERT INTO commitment_specifications("
                "specification_id,commitment_id,created_at_utc,effective_at,statement,start_at,end_at,"
                "report_at,recurrence_type,weekly_days_json,temporal_placement,prior_specification_id,"
                "amendment_kind,raw_amendment_reason,source_capture_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)",
                (specification_id, commitment_id, created, created, statement,
                 schedule["start_at"], schedule["end_at"], schedule["report_at"],
                 recurrence["recurrence_type"], recurrence["weekly_days_json"],
                 recurrence["temporal_placement"], prior, kind, reason),
            )
            connection.execute(
                "UPDATE commitments SET current_specification_id=? WHERE commitment_id=?",
                (specification_id, commitment_id),
            )
        return {"commitment": self.commitment(commitment_id),
                "specification": self.specifications(commitment_id)[-1]}

    def commitment(self, commitment_id):
        for view in ("active", "history"):
            for item in self.commitments(view):
                if item["commitment_id"] == commitment_id:
                    return item
        return None

    @staticmethod
    def _local_day(iso_timestamp: str) -> date:
        return datetime.fromisoformat(iso_timestamp).astimezone().date()

    def regular_week(self) -> dict[str, list[dict[str, object]]]:
        week = {day: [] for day in WEEKDAYS}
        for item in self.commitments("active"):
            if item["recurrence_type"] != "WEEKLY_PATTERN":
                continue
            for day in item["weekly_days"]:
                week[day].append(item)
        placement_order = {"MORNING": 0, "AFTERNOON": 1, "EVENING": 2,
                           "ANYTIME": 3, None: 4}
        for day in WEEKDAYS:
            week[day].sort(key=lambda item: (
                placement_order.get(item["temporal_placement"], 9), item["created_at_utc"],
                item["commitment_id"],
            ))
        return week

    def occurrence_reports(self, commitment_id: str) -> list[dict[str, object]]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT report_id,commitment_id,specification_id,intended_local_date,reported_at,"
                "outcome,raw_feedback "
                "FROM commitment_occurrence_reports WHERE commitment_id=? "
                "ORDER BY intended_local_date,reported_at", (commitment_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def specification_for_date(self, commitment_id: str, intended: date):
        candidates = [
            item for item in self.specifications(commitment_id)
            if self._local_day(item["effective_at"]) <= intended
        ]
        if not candidates:
            return None
        return candidates[-1]

    def _recurring_commitment_for_report(self, connection, commitment_id, intended: date):
        row = connection.execute(
            "SELECT c.commitment_id,c.created_at_utc,c.current_status,r.resolved_at_utc "
            "FROM commitments c LEFT JOIN commitment_resolutions r "
            "ON r.commitment_id=c.commitment_id WHERE c.commitment_id=?", (commitment_id,)
        ).fetchone()
        if row is None: raise LookupError("commitment_not_found")
        specification = self.specification_for_date(commitment_id, intended)
        if specification is None or specification["recurrence_type"] != "WEEKLY_PATTERN":
            raise ValueError("occurrence_report_requires_recurring_commitment")
        days = specification["weekly_days"]
        if WEEKDAYS[intended.weekday()] not in days:
            raise ValueError("date_is_not_expected_occurrence")
        if intended < self._local_day(row["created_at_utc"]):
            raise ValueError("occurrence_precedes_commitment")
        if row["resolved_at_utc"] and intended > self._local_day(row["resolved_at_utc"]):
            raise ValueError("occurrence_follows_commitment_closure")
        return row, specification

    def add_occurrence_reports(self, reports: object) -> list[dict[str, object]]:
        if not isinstance(reports, list) or not reports:
            raise ValueError("reports_must_be_nonempty_list")
        prepared = []
        with self.connection() as connection:
            for value in reports:
                if not isinstance(value, dict): raise ValueError("invalid_occurrence_report")
                commitment_id = value.get("commitment_id")
                if not isinstance(commitment_id, str) or not commitment_id:
                    raise ValueError("invalid_commitment_id")
                intended = parse_local_date(value.get("intended_local_date"))
                if intended > datetime.now().astimezone().date():
                    raise ValueError("cannot_report_future_occurrence")
                _, specification = self._recurring_commitment_for_report(
                    connection, commitment_id, intended
                )
                outcome_value = value.get("outcome")
                outcome = None if outcome_value is None or outcome_value == "" else str(outcome_value).upper()
                if outcome is not None and outcome not in OCCURRENCE_OUTCOMES:
                    raise ValueError("invalid_occurrence_outcome")
                feedback = value.get("raw_feedback")
                if feedback is not None and not isinstance(feedback, str):
                    raise ValueError("invalid_raw_feedback")
                prepared.append({
                    "report_id": f"home:occurrence-report:{uuid.uuid4()}",
                    "commitment_id": commitment_id,
                    "specification_id": specification["specification_id"],
                    "intended_local_date": intended.isoformat(),
                    "reported_at": now_utc_iso(), "outcome": outcome,
                    "raw_feedback": feedback,
                })
            try:
                connection.executemany(
                    "INSERT INTO commitment_occurrence_reports("
                    "report_id,commitment_id,specification_id,intended_local_date,reported_at,"
                    "outcome,raw_feedback) VALUES("
                    ":report_id,:commitment_id,:specification_id,:intended_local_date,:reported_at,"
                    ":outcome,:raw_feedback)",
                    prepared,
                )
            except sqlite3.IntegrityError as exc:
                raise RuntimeError("occurrence_report_already_exists") from exc
        return prepared

    def today_recurring(self, local_date: object = None) -> dict[str, object]:
        intended = (
            datetime.now().astimezone().date() if local_date is None
            else parse_local_date(local_date, "local_date")
        )
        day = WEEKDAYS[intended.weekday()]
        expected = []
        for item in self.commitments("active"):
            if intended < self._local_day(item["created_at_utc"]):
                continue
            specification = self.specification_for_date(item["commitment_id"], intended)
            if (specification is None or specification["recurrence_type"] != "WEEKLY_PATTERN"
                    or day not in specification["weekly_days"]):
                continue
            item = dict(item)
            item.update({
                "specification_id": specification["specification_id"],
                "current_specification_id": item["current_specification_id"],
                "specification_created_at": specification["created_at_utc"],
                "effective_at": specification["effective_at"],
                "raw_text": specification["statement"],
                "start_at": specification["start_at"], "end_at": specification["end_at"],
                "report_at": specification["report_at"],
                "recurrence_type": specification["recurrence_type"],
                "weekly_days": specification["weekly_days"],
                "temporal_placement": specification["temporal_placement"],
                "prior_specification_id": specification["prior_specification_id"],
                "amendment_kind": specification["amendment_kind"],
                "raw_amendment_reason": specification["raw_amendment_reason"],
            })
            reports = self.occurrence_reports(item["commitment_id"])
            item["occurrence_report"] = next(
                (report for report in reports if report["intended_local_date"] == intended.isoformat()),
                None,
            )
            expected.append(item)
        return {"local_date": intended.isoformat(), "weekday": day, "commitments": expected}

    def recurrence_history(self, commitment_id: str, through_date: object = None) -> dict[str, object]:
        item = self.commitment(commitment_id)
        if item is None: raise LookupError("commitment_not_found")
        if item["recurrence_type"] != "WEEKLY_PATTERN":
            raise ValueError("recurrence_history_requires_recurring_commitment")
        through = (
            datetime.now().astimezone().date() if through_date is None
            else parse_local_date(through_date, "through_date")
        )
        start = self._local_day(item["created_at_utc"])
        if item["current_status"] == "CLOSED" and item["resolved_at_utc"]:
            through = min(through, self._local_day(item["resolved_at_utc"]))
        reports = {value["intended_local_date"]: value for value in self.occurrence_reports(commitment_id)}
        occurrences = []
        cursor = start
        while cursor <= through:
            specification = self.specification_for_date(commitment_id, cursor)
            if (specification is not None
                    and specification["recurrence_type"] == "WEEKLY_PATTERN"
                    and WEEKDAYS[cursor.weekday()] in specification["weekly_days"]):
                report = reports.get(cursor.isoformat())
                occurrences.append({
                    "intended_local_date": cursor.isoformat(),
                    "specification_id": (
                        report["specification_id"] if report else specification["specification_id"]
                    ),
                    "state": (
                        "NO_REPORT" if report is None else
                        report["outcome"] or "REPORTED_WITHOUT_OUTCOME"
                    ),
                    "report": report,
                })
            cursor += timedelta(days=1)
        return {"commitment": item, "through_date": through.isoformat(),
                "occurrences": occurrences}

    def resolve(self, commitment_id, mode, feedback, replacement=None):
        mode = mode.upper()
        if mode not in RESOLUTION_MODES:
            raise ValueError("invalid_resolution_mode")
        if feedback is not None and not isinstance(feedback, str):
            raise ValueError("invalid_raw_feedback")
        if mode != "REVISED" and replacement is not None:
            raise ValueError("replacement_only_valid_for_revised")
        if mode == "REVISED" and not isinstance(replacement, dict):
            raise ValueError("revised_requires_replacement")
        replacement_capture = replacement_commitment = None
        with self.connection() as connection:
            current = connection.execute(
                "SELECT current_status FROM commitments WHERE commitment_id=?", (commitment_id,)
            ).fetchone()
            if current is None:
                raise LookupError("commitment_not_found")
            if current["current_status"] != "ACTIVE":
                raise RuntimeError("commitment_already_closed")
            if mode == "REVISED":
                text = replacement.get("raw_text")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("empty_replacement_commitment")
                schedule = validate_schedule(
                    replacement.get("start_at"), replacement.get("end_at"), replacement.get("report_at")
                )
                recurrence = validate_recurrence(
                    replacement.get("recurrence_type"), replacement.get("weekly_days"),
                    replacement.get("temporal_placement"),
                )
                replacement_capture = self._capture("commit", text, replacement.get("client_time"))
                self._insert_capture(connection, replacement_capture)
                replacement_commitment = self._insert_commitment(
                    connection, replacement_capture, schedule, recurrence
                )
            resolution = {
                "resolution_id": f"home:resolution:{uuid.uuid4()}",
                "commitment_id": commitment_id, "mode": mode,
                "resolved_at_utc": now_utc_iso(), "raw_feedback": feedback,
                "replacement_commitment_id": (
                    replacement_commitment["commitment_id"] if replacement_commitment else None
                ),
            }
            connection.execute(
                "INSERT INTO commitment_resolutions VALUES(:resolution_id,:commitment_id,:mode,"
                ":resolved_at_utc,:raw_feedback,:replacement_commitment_id)", resolution,
            )
            connection.execute(
                "UPDATE commitments SET current_status='CLOSED' WHERE commitment_id=?", (commitment_id,)
            )
        return {"resolution": resolution, "replacement_capture": replacement_capture,
                "replacement_commitment": replacement_commitment}

    @staticmethod
    def _event_row(row: sqlite3.Row) -> dict[str, object]:
        item = dict(row)
        item["context_refs"] = json.loads(item.pop("context_refs_json"))
        return item

    def events(self, view="all", target_actor=None) -> list[dict[str, object]]:
        clauses, parameters = [], []
        if view == "due": clauses.append("status='DUE'")
        elif view == "scheduled": clauses.append("status='SCHEDULED'")
        elif view == "open": clauses.append("status IN ('SCHEDULED','DUE')")
        elif view == "history": clauses.append("status IN ('ACKNOWLEDGED','CANCELLED')")
        elif view != "all": raise ValueError("invalid_event_view")
        if target_actor:
            clauses.append("target_actor=?"); parameters.append(target_actor)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connection() as connection:
            rows = connection.execute(
                f"SELECT * FROM scheduled_events {where} ORDER BY due_at,event_id", parameters
            ).fetchall()
        return [self._event_row(row) for row in rows]

    def create_event(self, author, target_actor, due_at, kind, instruction, context_refs):
        fields = {"author": author, "target_actor": target_actor, "kind": kind,
                  "raw_instruction": instruction}
        for name, value in fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"invalid_{name}")
        if not isinstance(context_refs, list) or any(
            not isinstance(value, str) or not value.strip() for value in context_refs
        ):
            raise ValueError("invalid_context_refs")
        canonical_due = parse_time(due_at, "due_at")
        if not canonical_due: raise ValueError("due_at_required")
        record = {
            "event_id": f"home:event:{uuid.uuid4()}", "author": author,
            "target_actor": target_actor, "created_at": now_utc_iso(),
            "due_at": canonical_due, "kind": kind, "raw_instruction": instruction,
            "context_refs_json": json.dumps(context_refs, ensure_ascii=False, separators=(",", ":")),
            "status": "SCHEDULED", "triggered_at": None, "acknowledged_at": None,
        }
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO scheduled_events VALUES(:event_id,:author,:target_actor,:created_at,"
                ":due_at,:kind,:raw_instruction,:context_refs_json,:status,:triggered_at,"
                ":acknowledged_at)", record
            )
        self.generate_bridge()
        return {
            **{key: value for key, value in record.items() if key != "context_refs_json"},
            "context_refs": list(context_refs),
        }

    def mark_due(self, observed_at=None) -> list[dict[str, object]]:
        observed = parse_time(observed_at or now_utc_iso(), "observed_at")
        assert observed
        with self.connection() as connection:
            identities = [row[0] for row in connection.execute(
                "SELECT event_id FROM scheduled_events WHERE status='SCHEDULED' AND due_at<=? "
                "ORDER BY due_at,event_id", (observed,)
            ).fetchall()]
            if identities:
                connection.executemany(
                    "UPDATE scheduled_events SET status='DUE',triggered_at=? "
                    "WHERE event_id=? AND status='SCHEDULED'", [(observed, item) for item in identities]
                )
            rows = [connection.execute(
                "SELECT * FROM scheduled_events WHERE event_id=?", (item,)
            ).fetchone() for item in identities]
        if identities: self.generate_bridge()
        return [self._event_row(row) for row in rows if row is not None]

    def transition_event(self, event_id, action):
        target = {"acknowledge": "ACKNOWLEDGED", "cancel": "CANCELLED"}.get(action)
        if not target: raise ValueError("invalid_event_action")
        with self.connection() as connection:
            row = connection.execute(
                "SELECT status FROM scheduled_events WHERE event_id=?", (event_id,)
            ).fetchone()
            if row is None: raise LookupError("event_not_found")
            if action == "acknowledge" and row["status"] != "DUE":
                raise RuntimeError("only_due_events_can_be_acknowledged")
            if action == "cancel" and row["status"] not in {"SCHEDULED", "DUE"}:
                raise RuntimeError("event_is_terminal")
            acknowledged = now_utc_iso() if action == "acknowledge" else None
            connection.execute(
                "UPDATE scheduled_events SET status=?,acknowledged_at=? WHERE event_id=?",
                (target, acknowledged, event_id),
            )
            result = connection.execute(
                "SELECT * FROM scheduled_events WHERE event_id=?", (event_id,)
            ).fetchone()
        self.generate_bridge()
        return self._event_row(result)

    @staticmethod
    def _json_array(value, field):
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"invalid_{field}")
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    def chat_state(self) -> dict[str, object]:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM chat_home_state WHERE state_id='chat'").fetchone()
        return {
            "attribution": "Chat", "current_pressure": (
                json.loads(row["current_pressure_json"]) if row["current_pressure_json"] else None
            ),
            "active_recommendations": json.loads(row["active_recommendations_json"]),
            "unresolved_questions": json.loads(row["unresolved_questions_json"]),
            "continuation_refs": json.loads(row["continuation_refs_json"]),
            "explicit_executable_agent_commitments": json.loads(row["executable_agent_commitments_json"]),
            "generated_at": row["generated_at_utc"], "updated_at": row["updated_at_utc"],
        }

    def update_chat_state(self, data):
        current = data.get("current_pressure")
        recommendations = self._json_array(data.get("active_recommendations", []), "active_recommendations")
        questions = self._json_array(data.get("unresolved_questions", []), "unresolved_questions")
        refs = self._json_array(data.get("continuation_refs", []), "continuation_refs")
        commitments = data.get("explicit_executable_agent_commitments", [])
        if not isinstance(commitments, list) or any(
            not isinstance(item, dict) or not isinstance(item.get("execution_path"), str)
            or not item["execution_path"].strip() for item in commitments
        ):
            raise ValueError("agent_commitment_requires_execution_path")
        commitment_json = json.dumps(commitments, ensure_ascii=False, separators=(",", ":"))
        updated = now_utc_iso()
        with self.connection() as connection:
            connection.execute(
                "UPDATE chat_home_state SET current_pressure_json=?,active_recommendations_json=?,"
                "unresolved_questions_json=?,continuation_refs_json=?,"
                "executable_agent_commitments_json=?,updated_at_utc=? WHERE state_id='chat'",
                (json.dumps(current, ensure_ascii=False, separators=(",", ":")), recommendations,
                 questions, refs, commitment_json, updated),
            )
        self.generate_bridge()
        return self.chat_state()

    def generate_bridge(self) -> None:
        generated = now_utc_iso()
        chat = self.chat_state()
        chat["future_notes"] = [item for item in self.events("open", "Chat") if item["author"] == "Chat"]
        chat["state_generated_at"] = chat.pop("generated_at")
        chat_packet = {"projection_kind": "CHAT_HOME_DERIVED_PROJECTION",
                       "authority": "DERIVED_FROM_HOME", "generated_at": generated, **chat}
        due_packet = {"projection_kind": "DUE_AGENT_EVENTS_DERIVED_PROJECTION",
                      "authority": "DERIVED_FROM_HOME", "generated_at": generated,
                      "events": self.events("due", "Chat")}
        for name, packet in (("chat_now.json", chat_packet), ("due_events.json", due_packet)):
            destination = self.agent_bridge_dir / name
            temporary = destination.with_name(f".{name}.{uuid.uuid4().hex}.tmp")
            temporary.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(temporary, destination)


def ics_escape(value: object) -> str:
    return (str(value).replace("\\", "\\\\").replace("\r\n", "\\n")
            .replace("\n", "\\n").replace("\r", "\\n")
            .replace(";", "\\;").replace(",", "\\,"))


def ics_time(value: str) -> str:
    return datetime.fromisoformat(value).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ics_document(lines: list[str]) -> str:
    """Serialize RFC 5545 content lines with conservative UTF-8 folding."""
    folded: list[str] = []
    for line in lines:
        remaining = line
        first = True
        while remaining:
            limit = 74 if first else 73
            used = 0
            split = 0
            for split, character in enumerate(remaining, start=1):
                width = len(character.encode("utf-8"))
                if used + width > limit:
                    split -= 1
                    break
                used += width
            else:
                split = len(remaining)
            if split == 0:
                split = 1
            folded.append(("" if first else " ") + remaining[:split])
            remaining = remaining[split:]
            first = False
    return "\r\n".join(folded) + "\r\n"


def commitment_calendar(item) -> str:
    if not item.get("start_at"):
        raise ValueError("commitment_has_no_start_at")
    title = str(item["raw_text"]).splitlines()[0].strip() or "Home commitment"
    description = f"Home commitment ref: {item['commitment_id']}"
    if item.get("report_at"):
        description += f"\nReport expected after: {item['report_at']}"
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//DME Lab//Home Capture v0//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "BEGIN:VEVENT",
             f"UID:{ics_escape(item['commitment_id'])}@dme-home.local",
             f"DTSTAMP:{ics_time(now_utc_iso())}", f"DTSTART:{ics_time(item['start_at'])}"]
    if item.get("end_at"):
        lines.append(f"DTEND:{ics_time(item['end_at'])}")
    lines += [f"SUMMARY:{ics_escape(title)}", f"DESCRIPTION:{ics_escape(description)}",
              "END:VEVENT", "END:VCALENDAR"]
    return ics_document(lines)


def review_calendar(start_at: str, minutes: int) -> str:
    start = datetime.fromisoformat(start_at)
    end = start + timedelta(minutes=minutes)
    uid = uuid.uuid5(LEGACY_NAMESPACE, f"review:{start_at}:{minutes}")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//DME Lab//Home Capture v0//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "BEGIN:VEVENT",
             f"UID:home-review:{uid}@dme-home.local", f"DTSTAMP:{ics_time(now_utc_iso())}",
             f"DTSTART:{ics_time(start.isoformat())}", f"DTEND:{ics_time(end.isoformat())}",
             "RRULE:FREQ=DAILY", "SUMMARY:HOME COMMITMENT REPORT",
             "DESCRIPTION:Inspect REPORT DUE commitments in Home; explicitly resolve or revise them; stop.",
             "END:VEVENT", "END:VCALENDAR"]
    return ics_document(lines)


class DesktopNotifier:
    """Best-effort local notification; it never changes event standing."""
    def notify(self, events: list[dict[str, object]]) -> None:
        if os.name != "nt" or not events: return
        count = len(events)
        first = str(events[0]["raw_instruction"])
        message = f"{count} Home event{'s are' if count != 1 else ' is'} DUE NOW.\n\n{first[:500]}"
        threading.Thread(
            target=lambda: ctypes.windll.user32.MessageBoxW(0, message, "Home — DUE NOW", 0x40),
            daemon=True,
        ).start()


class HomeScheduler:
    def __init__(self, store: HomeStore, notifier=None, interval_seconds=2.0):
        self.store, self.notifier, self.interval_seconds = store, notifier, interval_seconds
        self._stop = threading.Event()
        self.last_error = None
        self.last_sweep_at = None
        self._thread = threading.Thread(target=self._run, name="home-local-scheduler", daemon=True)
    def start(self): self._thread.start()
    def stop(self):
        self._stop.set()
        if self._thread.is_alive(): self._thread.join(timeout=max(2.0, self.interval_seconds + 1.0))
    def sweep_once(self):
        try:
            due = self.store.mark_due()
            if due and self.notifier: self.notifier.notify(due)
            self.last_error = None
            self.last_sweep_at = now_utc_iso()
            return due
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            raise
    def _run(self):
        while not self._stop.is_set():
            try: self.sweep_once()
            except Exception: pass  # API/health remains available; next sweep retries observation.
            self._stop.wait(self.interval_seconds)


class HomeServer(ThreadingHTTPServer):
    # Join request threads at close so their short-lived SQLite connections are
    # gone before a restart/rebuild test removes its data directory.
    daemon_threads, allow_reuse_address = False, False
    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()
    def __init__(self, address, store, access_mode, desktop_notifications=True):
        self.store, self.access_mode = store, access_mode
        super().__init__(address, HomeHandler)
        self.scheduler = HomeScheduler(store, DesktopNotifier() if desktop_notifications else None)
        self.scheduler.start()
    def server_close(self):
        if hasattr(self, "scheduler"):
            self.scheduler.stop()
        super().server_close()
    @property
    def advertised_url(self):
        address = discover_private_ipv4() if self.access_mode == "lan" else None
        return f"http://{address}:{self.server_port}" if address else None


class HomeHandler(BaseHTTPRequestHandler):
    server_version = "HomeCapture/0.5"
    server: HomeServer
    def _send(self, body, content_type, status=HTTPStatus.OK, disposition=None):
        self.send_response(status); self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if disposition: self.send_header("Content-Disposition", disposition)
        self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer"); self.end_headers(); self.wfile.write(body)
    def _json(self, payload, status=HTTPStatus.OK):
        self._send(json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8", status)
    def _text(self, body, content_type="text/plain; charset=utf-8", status=HTTPStatus.OK, disposition=None):
        self._send(body.encode(), content_type, status, disposition)
    def _read_json(self):
        if self.headers.get_content_type() != "application/json":
            self._json({"error":"content_type_must_be_json"}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE); return None
        try: length = int(self.headers.get("Content-Length", "0"))
        except ValueError: length = 0
        if length <= 0 or length > MAX_CAPTURE_BYTES:
            self._json({"error":"invalid_content_length"}, HTTPStatus.BAD_REQUEST); return None
        try: data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json({"error":"invalid_json"}, HTTPStatus.BAD_REQUEST); return None
        if not isinstance(data, dict):
            self._json({"error":"invalid_json_object"}, HTTPStatus.BAD_REQUEST); return None
        return data

    def do_GET(self):  # noqa: N802
        parsed, path = urlparse(self.path), urlparse(self.path).path
        if path == "/": self._text(INDEX_PATH.read_text(encoding="utf-8"), "text/html; charset=utf-8"); return
        if path == "/api/health":
            active = self.server.store.commitments("active")
            due_events = self.server.store.events("due")
            recurring_count = sum(
                item["recurrence_type"] == "WEEKLY_PATTERN" for item in active
            )
            self._json({"service":"home_capture_v0", "status":"operational", "version":"0.5",
                        "capture_count":self.server.store.count(), "active_commitment_count":len(active),
                        "report_due_count":sum(bool(x["report_due"]) for x in active),
                        "due_event_count":len(due_events),
                        "active_recurring_commitment_count":recurring_count,
                        "scheduler_last_sweep_at":self.server.scheduler.last_sweep_at,
                        "scheduler_error":self.server.scheduler.last_error,
                        "access_mode":self.server.access_mode, "phone_url":self.server.advertised_url,
                        "public_internet_supported":False, "process_id":os.getpid()}); return
        if path in {"/api/recent", "/api/captures"}:
            query = parse_qs(parsed.query); lane = query.get("lane", [""])[0].strip().lower()
            if lane in {"", "all"}: lane = ""
            elif lane not in ALLOWED_LANES: self._json({"error":"invalid_lane"}, HTTPStatus.BAD_REQUEST); return
            order = query.get("order", ["desc"])[0].lower()
            if order not in {"asc", "desc"}: self._json({"error":"invalid_order"}, HTTPStatus.BAD_REQUEST); return
            try: limit = int(query.get("limit", ["500"])[0])
            except ValueError: self._json({"error":"invalid_limit"}, HTTPStatus.BAD_REQUEST); return
            rows = self.server.store.history(lane or None, query.get("q", [""])[0], order, limit)
            self._json({"captures":rows, "count":self.server.store.count()}); return
        if path == "/api/commitments":
            query = parse_qs(parsed.query)
            try: rows = self.server.store.commitments(query.get("view", ["active"])[0],
                                                       query.get("resolution", [None])[0],
                                                       query.get("observed_at", [None])[0])
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json({"commitments":rows, "observed_at":now_utc_iso()}); return
        if path == "/api/regular-week":
            self._json({"days":self.server.store.regular_week(),
                        "projection_kind":"REGULAR_WEEK"}); return
        if path == "/api/today-recurring":
            query = parse_qs(parsed.query)
            try: result = self.server.store.today_recurring(query.get("local_date", [None])[0])
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(result); return
        if path == "/api/recurrence-history":
            query = parse_qs(parsed.query)
            identity = query.get("commitment_id", [""])[0]
            try: result = self.server.store.recurrence_history(
                identity, query.get("through_date", [None])[0]
            )
            except LookupError as exc: self._json({"error":str(exc)}, HTTPStatus.NOT_FOUND); return
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(result); return
        if path.startswith("/api/commitments/") and path.endswith("/specifications"):
            identity = unquote(
                path[len("/api/commitments/"):-len("/specifications")].strip("/")
            )
            try: specifications = self.server.store.specifications(identity)
            except LookupError as exc:
                self._json({"error":str(exc)}, HTTPStatus.NOT_FOUND); return
            self._json({"commitment_id":identity, "specifications":specifications}); return
        if path == "/api/events":
            self.server.scheduler.sweep_once()
            query = parse_qs(parsed.query)
            try: rows = self.server.store.events(query.get("view", ["all"])[0],
                                                  query.get("target_actor", [None])[0])
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json({"events":rows, "observed_at":now_utc_iso(),
                        "due_does_not_imply_executed":True}); return
        if path == "/api/chat-home":
            self._json(self.server.store.chat_state()); return
        if path in {"/agent_bridge/chat_now.json", "/agent_bridge/due_events.json"}:
            name = path.rsplit("/", 1)[1]
            self.server.store.generate_bridge()
            self._text((self.server.store.agent_bridge_dir / name).read_text(encoding="utf-8"),
                       "application/json; charset=utf-8"); return
        if path.startswith("/api/commitments/") and path.endswith("/calendar.ics"):
            identity = unquote(path[len("/api/commitments/"):-len("/calendar.ics")].strip("/"))
            item = self.server.store.commitment(identity)
            if not item: self._json({"error":"commitment_not_found"}, HTTPStatus.NOT_FOUND); return
            try: body = commitment_calendar(item)
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._text(body, "text/calendar; charset=utf-8", disposition='attachment; filename="home-commitment.ics"'); return
        if path == "/api/calendar/review.ics":
            query = parse_qs(parsed.query)
            try:
                start = parse_time(query.get("start_at", [None])[0], "start_at")
                if not start: raise ValueError("start_at_required")
                minutes = int(query.get("duration_minutes", ["15"])[0])
                if not 1 <= minutes <= 1440: raise ValueError("invalid_duration_minutes")
                body = review_calendar(start, minutes)
            except (ValueError, TypeError) as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._text(body, "text/calendar; charset=utf-8", disposition='attachment; filename="home-commitment-report.ics"'); return
        if path == "/api/export.jsonl":
            body = "\n".join(json.dumps(x, ensure_ascii=False) for x in self.server.store.export_rows())
            self._text(body + ("\n" if body else ""), "application/x-ndjson; charset=utf-8",
                       disposition='attachment; filename="home-captures.jsonl"'); return
        if path == "/api/export.md":
            lines = ["# Home Capture v0 — recent packet", "", "> Raw user-authored captures only.", ""]
            for row in self.server.store.history(order="asc", limit=30):
                lines += [f"## {row['mode'].upper()} — {row['client_time'] or row['created_at_utc']}",
                          f"- ref: `{row['id']}`", f"- origin: `{row['origin']}`", "", row["raw_text"], ""]
            self._text("\n".join(lines), "text/markdown; charset=utf-8"); return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/api/events", "/api/chat-home/future-note"}:
            data = self._read_json()
            if data is None: return
            if path == "/api/chat-home/future-note":
                author, target, kind = "Chat", "Chat", "FUTURE_CHAT_NOTE"
            else:
                author, target, kind = data.get("author"), data.get("target_actor"), data.get("kind")
            try:
                event = self.server.store.create_event(
                    author, target, data.get("due_at"), kind,
                    data.get("raw_instruction"), data.get("context_refs", []),
                )
                self.server.scheduler.sweep_once()
                event = next(item for item in self.server.store.events("all")
                             if item["event_id"] == event["event_id"])
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(event, HTTPStatus.CREATED); return
        if path == "/api/recurring-reports":
            data = self._read_json()
            if data is None: return
            try: reports = self.server.store.add_occurrence_reports(data.get("reports"))
            except LookupError as exc: self._json({"error":str(exc)}, HTTPStatus.NOT_FOUND); return
            except RuntimeError as exc: self._json({"error":str(exc)}, HTTPStatus.CONFLICT); return
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json({"reports":reports}, HTTPStatus.CREATED); return
        if path == "/api/chat-home":
            data = self._read_json()
            if data is None: return
            try: state = self.server.store.update_chat_state(data)
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(state, HTTPStatus.CREATED); return
        if path.startswith("/api/events/") and path.endswith(("/acknowledge", "/cancel")):
            action = "acknowledge" if path.endswith("/acknowledge") else "cancel"
            suffix = f"/{action}"
            identity = unquote(path[len("/api/events/"):-len(suffix)].strip("/"))
            data = self._read_json()
            if data is None: return
            if data:
                self._json({"error":"event_transition_accepts_empty_object_only"}, HTTPStatus.BAD_REQUEST); return
            try: event = self.server.store.transition_event(identity, action)
            except LookupError as exc: self._json({"error":str(exc)}, HTTPStatus.NOT_FOUND); return
            except RuntimeError as exc: self._json({"error":str(exc)}, HTTPStatus.CONFLICT); return
            self._json(event, HTTPStatus.CREATED); return
        if path == "/api/capture":
            data = self._read_json()
            if data is None: return
            lane, text = str(data.get("mode", "")).strip().lower(), data.get("raw_text")
            if lane not in ALLOWED_LANES: self._json({"error":"invalid_mode"}, HTTPStatus.BAD_REQUEST); return
            if not isinstance(text, str) or not text.strip(): self._json({"error":"empty_capture"}, HTTPStatus.BAD_REQUEST); return
            try:
                schedule = validate_schedule(data.get("start_at"), data.get("end_at"), data.get("report_at"))
                recurrence = validate_recurrence(
                    data.get("recurrence_type"), data.get("weekly_days"),
                    data.get("temporal_placement"),
                )
                if lane != "commit" and any(schedule.values()): raise ValueError("schedule_only_valid_for_commit")
                if lane != "commit" and recurrence["recurrence_type"] != "NONE":
                    raise ValueError("recurrence_only_valid_for_commit")
                record = self.server.store.insert(
                    lane, text, data.get("client_time"), schedule, recurrence
                )
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(record, HTTPStatus.CREATED); return
        if path.startswith("/api/commitments/") and path.endswith("/resolve"):
            identity = unquote(path[len("/api/commitments/"):-len("/resolve")].strip("/"))
            data = self._read_json()
            if data is None: return
            try: result = self.server.store.resolve(identity, str(data.get("mode", "")),
                                                     data.get("raw_feedback"), data.get("replacement"))
            except LookupError as exc: self._json({"error":str(exc)}, HTTPStatus.NOT_FOUND); return
            except RuntimeError as exc: self._json({"error":str(exc)}, HTTPStatus.CONFLICT); return
            except ValueError as exc: self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(result, HTTPStatus.CREATED); return
        if path.startswith("/api/commitments/") and path.endswith("/amend"):
            identity = unquote(path[len("/api/commitments/"):-len("/amend")].strip("/"))
            data = self._read_json()
            if data is None: return
            try:
                schedule = validate_schedule(
                    data.get("start_at"), data.get("end_at"), data.get("report_at")
                )
                recurrence = validate_recurrence(
                    data.get("recurrence_type"), data.get("weekly_days"),
                    data.get("temporal_placement"),
                )
                result = self.server.store.amend(
                    identity, data.get("amendment_kind"), data.get("raw_text"),
                    schedule, recurrence, data.get("raw_amendment_reason"),
                )
            except LookupError as exc:
                self._json({"error":str(exc)}, HTTPStatus.NOT_FOUND); return
            except RuntimeError as exc:
                self._json({"error":str(exc)}, HTTPStatus.CONFLICT); return
            except ValueError as exc:
                self._json({"error":str(exc)}, HTTPStatus.BAD_REQUEST); return
            self._json(result, HTTPStatus.CREATED); return
        self.send_error(HTTPStatus.NOT_FOUND)
    def log_message(self, fmt, *args):
        if args and str(args[1]).startswith(("4", "5")): super().log_message(fmt, *args)


def create_server(host="127.0.0.1", port=8765, data_dir=DEFAULT_DATA_DIR, access_mode="desktop",
                  desktop_notifications=True):
    store = HomeStore(data_dir); store.initialize()
    return HomeServer((host, port), store, access_mode, desktop_notifications)


def main():
    parser = argparse.ArgumentParser(description="Home Capture v0")
    parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--access-mode", choices=("desktop", "lan"), default="desktop")
    args = parser.parse_args(); server = create_server(args.host, args.port, args.data_dir, args.access_mode)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == "__main__": main()
