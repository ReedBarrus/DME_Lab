#!/usr/bin/env python3
"""GOBLIN_POOL_001 — bounded three-seat SQLite controller pressure rig.

The controller owns serialization, leases, event delivery, operator mediation,
transactional seat-state commits, and receipts.

It does NOT own seat purpose, semantic planning, campaign selection,
scientific adjudication, or authority synthesis.

REGISTERED != AVAILABLE != ELIGIBLE != AUTHORIZED != EXECUTED
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "goblin_pool_v0.sql"
SEAT_IDS = ("GOB_A", "GOB_B", "GOB_C")
OPERATOR_IDS = ("READ_REPO_STATE", "RUN_DECLARED_TEST", "WRITE_PACKET")


class GoblinPoolError(RuntimeError):
    pass


class InjectedCrash(RuntimeError):
    pass


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _unjson(value: str) -> Any:
    return json.loads(value)


class GoblinPool:
    def __init__(self, db_path: str | Path, workspace: str | Path) -> None:
        self.db_path = Path(db_path).resolve()
        self.workspace = Path(workspace).resolve()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            isolation_level=None,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    @staticmethod
    def _begin(conn: sqlite3.Connection) -> None:
        conn.execute("BEGIN IMMEDIATE")

    def initialize_fixture(self) -> None:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        conn = self._connect()
        try:
            conn.executescript(schema)
            self._begin(conn)

            if conn.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
                conn.execute(
                    """
                    INSERT INTO events(event_id, seat_id, event_kind, payload_json)
                    VALUES(?,?,?,?)
                    """,
                    ("EV-000001", None, "POOL_GENESIS", _json({"scope": "GOBLIN_POOL_001"})),
                )

            for seat_id in SEAT_IDS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO seats(
                        seat_id, cursor_event_id, working_state_json, state_version,
                        status, occupancy_state, current_wake_id, policy_ref,
                        operator_profile_ref, authority_profile_ref
                    ) VALUES(?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        seat_id,
                        "EV-000001",
                        _json({"seat_id": seat_id, "counter": 0, "mode": "IDLE"}),
                        0,
                        "REGISTERED",
                        "AVAILABLE",
                        None,
                        f"policy:{seat_id}:v0",
                        f"operators:{seat_id}:v0",
                        f"authority:{seat_id}:v0",
                    ),
                )

            operator_rows = (
                ("READ_REPO_STATE", 1, 1, 1, "READ_REPO_STATE"),
                ("RUN_DECLARED_TEST", 1, 1, 1, "RUN_DECLARED_TEST"),
                ("WRITE_PACKET", 1, 1, 1, "WRITE_PACKET"),
            )
            conn.executemany(
                """
                INSERT OR IGNORE INTO operators(
                    operator_id, registered, available, authority_required, adapter_kind
                ) VALUES(?,?,?,?,?)
                """,
                operator_rows,
            )

            eligibility = {
                "GOB_A": {
                    "READ_REPO_STATE": 1,
                    "RUN_DECLARED_TEST": 0,
                    "WRITE_PACKET": 0,
                },
                "GOB_B": {
                    "READ_REPO_STATE": 1,
                    "RUN_DECLARED_TEST": 1,
                    "WRITE_PACKET": 0,
                },
                "GOB_C": {
                    "READ_REPO_STATE": 1,
                    "RUN_DECLARED_TEST": 0,
                    "WRITE_PACKET": 1,
                },
            }
            authority = {
                "GOB_A": {
                    "READ_REPO_STATE": (1, "AUTH:GOB_A:READ"),
                    "RUN_DECLARED_TEST": (0, None),
                    "WRITE_PACKET": (0, None),
                },
                "GOB_B": {
                    "READ_REPO_STATE": (1, "AUTH:GOB_B:READ"),
                    "RUN_DECLARED_TEST": (1, "AUTH:GOB_B:TEST"),
                    "WRITE_PACKET": (0, None),
                },
                "GOB_C": {
                    "READ_REPO_STATE": (1, "AUTH:GOB_C:READ"),
                    "RUN_DECLARED_TEST": (0, None),
                    "WRITE_PACKET": (0, None),
                },
            }
            for seat_id in SEAT_IDS:
                for operator_id in OPERATOR_IDS:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO seat_operator_eligibility(
                            seat_id, operator_id, eligible
                        ) VALUES(?,?,?)
                        """,
                        (seat_id, operator_id, eligibility[seat_id][operator_id]),
                    )
                    authorized, authority_ref = authority[seat_id][operator_id]
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO seat_operator_authority(
                            seat_id, operator_id, authorized, authority_ref
                        ) VALUES(?,?,?,?)
                        """,
                        (seat_id, operator_id, authorized, authority_ref),
                    )

            conn.execute(
                """
                INSERT OR REPLACE INTO declared_tests(test_id, argv_json)
                VALUES(?,?)
                """,
                (
                    "SMOKE_TRUE",
                    _json(
                        [
                            sys.executable,
                            "-c",
                            "print('GOBLIN_DECLARED_TEST_PASS')",
                        ]
                    ),
                ),
            )
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def bind_external_seat(
        self,
        *,
        seat_id: str,
        cursor_event_id: str,
        working_state: dict[str, Any],
        source_events: list[dict[str, Any]],
        policy_ref: str,
        operator_profile_ref: str,
        authority_profile_ref: str,
    ) -> dict[str, Any]:
        """Bind one externally reconstructed seat without claiming identity collapse."""
        conn = self._connect()
        try:
            self._begin(conn)

            for event in source_events:
                event_id = event.get("event_id")
                if not isinstance(event_id, str) or not event_id:
                    raise GoblinPoolError("external seat event missing event_id")
                retained = conn.execute(
                    "SELECT seat_id, event_kind, payload_json FROM events WHERE event_id = ?",
                    (event_id,),
                ).fetchone()
                payload_json = _json(event)
                if retained is None:
                    conn.execute(
                        """
                        INSERT INTO events(event_id, seat_id, event_kind, payload_json)
                        VALUES(?,?,?,?)
                        """,
                        (
                            event_id,
                            seat_id,
                            str(event.get("kind") or "EXTERNAL_EVENT"),
                            payload_json,
                        ),
                    )
                elif (
                    retained["seat_id"] != seat_id
                    or retained["payload_json"] != payload_json
                ):
                    raise GoblinPoolError(
                        f"event identity {event_id!r} already names different bytes/binding"
                    )

            if conn.execute(
                "SELECT 1 FROM events WHERE event_id = ?",
                (cursor_event_id,),
            ).fetchone() is None:
                raise GoblinPoolError(
                    f"external seat cursor {cursor_event_id!r} is not present in imported events"
                )

            existing = conn.execute(
                "SELECT * FROM seats WHERE seat_id = ?",
                (seat_id,),
            ).fetchone()
            desired = {
                "cursor_event_id": cursor_event_id,
                "working_state_json": _json(working_state),
                "state_version": 0,
                "status": "BOUND",
                "occupancy_state": "AVAILABLE",
                "current_wake_id": None,
                "policy_ref": policy_ref,
                "operator_profile_ref": operator_profile_ref,
                "authority_profile_ref": authority_profile_ref,
            }
            if existing is not None:
                for key, value in desired.items():
                    if existing[key] != value:
                        raise GoblinPoolError(
                            f"existing seat {seat_id!r} disagrees on {key}"
                        )
                conn.commit()
                return {
                    "status": "ALREADY_BOUND",
                    "seat_id": seat_id,
                    "cursor_event_id": cursor_event_id,
                    "state_version": 0,
                }

            conn.execute(
                """
                INSERT INTO seats(
                    seat_id, cursor_event_id, working_state_json, state_version,
                    status, occupancy_state, current_wake_id, policy_ref,
                    operator_profile_ref, authority_profile_ref
                ) VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    seat_id,
                    cursor_event_id,
                    desired["working_state_json"],
                    0,
                    "BOUND",
                    "AVAILABLE",
                    None,
                    policy_ref,
                    operator_profile_ref,
                    authority_profile_ref,
                ),
            )
            conn.commit()
            return {
                "status": "BOUND",
                "seat_id": seat_id,
                "cursor_event_id": cursor_event_id,
                "state_version": 0,
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def configure_seat_operator(
        self,
        seat_id: str,
        operator_id: str,
        *,
        eligible: bool,
        authorized: bool,
        authority_ref: str | None,
    ) -> None:
        conn = self._connect()
        try:
            self._begin(conn)
            if conn.execute(
                "SELECT 1 FROM seats WHERE seat_id = ?",
                (seat_id,),
            ).fetchone() is None:
                raise GoblinPoolError(f"unknown seat {seat_id!r}")
            if conn.execute(
                "SELECT 1 FROM operators WHERE operator_id = ?",
                (operator_id,),
            ).fetchone() is None:
                raise GoblinPoolError(f"unknown operator {operator_id!r}")
            if authorized and not eligible:
                raise GoblinPoolError(
                    "operator cannot be authorized for a seat while ineligible"
                )
            if authorized and not authority_ref:
                raise GoblinPoolError(
                    "authorized seat operator requires explicit authority_ref"
                )
            conn.execute(
                """
                INSERT OR REPLACE INTO seat_operator_eligibility(
                    seat_id, operator_id, eligible
                ) VALUES(?,?,?)
                """,
                (seat_id, operator_id, 1 if eligible else 0),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO seat_operator_authority(
                    seat_id, operator_id, authorized, authority_ref
                ) VALUES(?,?,?,?)
                """,
                (
                    seat_id,
                    operator_id,
                    1 if authorized else 0,
                    authority_ref,
                ),
            )
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def register_declared_test(self, test_id: str, argv: list[str]) -> None:
        if not test_id or not argv or not all(isinstance(item, str) and item for item in argv):
            raise GoblinPoolError("declared test requires non-empty test_id and argv")
        conn = self._connect()
        try:
            self._begin(conn)
            retained = conn.execute(
                "SELECT argv_json FROM declared_tests WHERE test_id = ?",
                (test_id,),
            ).fetchone()
            argv_json = _json(argv)
            if retained is not None and retained["argv_json"] != argv_json:
                raise GoblinPoolError(
                    f"declared test {test_id!r} already names different argv"
                )
            conn.execute(
                """
                INSERT OR IGNORE INTO declared_tests(test_id, argv_json)
                VALUES(?,?)
                """,
                (test_id, argv_json),
            )
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def append_event(
        self,
        event_id: str,
        *,
        seat_id: str | None,
        event_kind: str,
        payload: Any,
    ) -> None:
        if seat_id is not None and seat_id not in SEAT_IDS:
            raise GoblinPoolError(f"unknown seat_id {seat_id!r}")
        conn = self._connect()
        try:
            self._begin(conn)
            conn.execute(
                """
                INSERT INTO events(event_id, seat_id, event_kind, payload_json)
                VALUES(?,?,?,?)
                """,
                (event_id, seat_id, event_kind, _json(payload)),
            )
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def seat_snapshot(self, seat_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM seats WHERE seat_id = ?",
                (seat_id,),
            ).fetchone()
            if row is None:
                raise GoblinPoolError(f"unknown seat {seat_id!r}")
            return {
                "seat_id": row["seat_id"],
                "cursor_event_id": row["cursor_event_id"],
                "working_state": _unjson(row["working_state_json"]),
                "state_version": row["state_version"],
                "status": row["status"],
                "occupancy_state": row["occupancy_state"],
                "current_wake_id": row["current_wake_id"],
                "policy_ref": row["policy_ref"],
                "operator_profile_ref": row["operator_profile_ref"],
                "authority_profile_ref": row["authority_profile_ref"],
            }
        finally:
            conn.close()

    def _event_seq(self, conn: sqlite3.Connection, event_id: str) -> int:
        row = conn.execute(
            "SELECT seq FROM events WHERE event_id = ?",
            (event_id,),
        ).fetchone()
        if row is None:
            raise GoblinPoolError(f"unknown cursor event {event_id!r}")
        return int(row["seq"])

    def _eligible_events_conn(
        self,
        conn: sqlite3.Connection,
        seat_id: str,
        cursor_event_id: str,
    ) -> list[sqlite3.Row]:
        cursor_seq = self._event_seq(conn, cursor_event_id)
        return conn.execute(
            """
            SELECT * FROM events
            WHERE seq > ?
              AND (seat_id IS NULL OR seat_id = ?)
            ORDER BY seq ASC
            """,
            (cursor_seq, seat_id),
        ).fetchall()

    def eligible_events(self, seat_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            seat = conn.execute(
                "SELECT cursor_event_id FROM seats WHERE seat_id = ?",
                (seat_id,),
            ).fetchone()
            if seat is None:
                raise GoblinPoolError(f"unknown seat {seat_id!r}")
            rows = self._eligible_events_conn(
                conn, seat_id, seat["cursor_event_id"]
            )
            return [
                {
                    "event_id": row["event_id"],
                    "seat_id": row["seat_id"],
                    "event_kind": row["event_kind"],
                    "payload": _unjson(row["payload_json"]),
                    "seq": row["seq"],
                }
                for row in rows
            ]
        finally:
            conn.close()

    def start_wake(self, seat_id: str, wake_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            self._begin(conn)

            existing = conn.execute(
                "SELECT * FROM wakes WHERE wake_id = ?",
                (wake_id,),
            ).fetchone()
            if existing is not None:
                conn.commit()
                return {
                    "wake_id": wake_id,
                    "seat_id": existing["seat_id"],
                    "status": existing["status"],
                    "basis_version": existing["basis_version"],
                    "basis_cursor_event_id": existing["basis_cursor_event_id"],
                    "outcome": existing["outcome"],
                    "idempotent_replay": True,
                }

            seat = conn.execute(
                "SELECT * FROM seats WHERE seat_id = ?",
                (seat_id,),
            ).fetchone()
            if seat is None:
                raise GoblinPoolError(f"unknown seat {seat_id!r}")

            created_order = (
                conn.execute(
                    "SELECT COALESCE(MAX(created_order), 0) + 1 FROM wakes"
                ).fetchone()[0]
            )

            if seat["occupancy_state"] == "OCCUPIED":
                outcome = _json(
                    {
                        "classification": "OCCUPANCY_CONFLICT",
                        "occupying_wake_id": seat["current_wake_id"],
                    }
                )
                conn.execute(
                    """
                    INSERT INTO wakes(
                        wake_id, seat_id, basis_version, basis_cursor_event_id,
                        status, outcome, created_order
                    ) VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        wake_id,
                        seat_id,
                        seat["state_version"],
                        seat["cursor_event_id"],
                        "OCCUPANCY_CONFLICT",
                        outcome,
                        created_order,
                    ),
                )
                conn.commit()
                return {
                    "wake_id": wake_id,
                    "seat_id": seat_id,
                    "status": "OCCUPANCY_CONFLICT",
                    "occupying_wake_id": seat["current_wake_id"],
                    "basis_version": seat["state_version"],
                    "basis_cursor_event_id": seat["cursor_event_id"],
                }

            conn.execute(
                """
                INSERT INTO wakes(
                    wake_id, seat_id, basis_version, basis_cursor_event_id,
                    status, outcome, created_order
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    wake_id,
                    seat_id,
                    seat["state_version"],
                    seat["cursor_event_id"],
                    "STARTED",
                    None,
                    created_order,
                ),
            )
            updated = conn.execute(
                """
                UPDATE seats
                SET occupancy_state = 'OCCUPIED', current_wake_id = ?
                WHERE seat_id = ? AND occupancy_state = 'AVAILABLE'
                """,
                (wake_id, seat_id),
            )
            if updated.rowcount != 1:
                raise GoblinPoolError("seat occupancy changed during wake acquisition")

            conn.commit()
            return {
                "wake_id": wake_id,
                "seat_id": seat_id,
                "status": "STARTED",
                "basis_version": seat["state_version"],
                "basis_cursor_event_id": seat["cursor_event_id"],
                "working_state": _unjson(seat["working_state_json"]),
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def recover_lease(
        self,
        seat_id: str,
        wake_id: str,
        *,
        reason: str = "LEASE_RECOVERY",
    ) -> dict[str, Any]:
        conn = self._connect()
        try:
            self._begin(conn)
            seat = conn.execute(
                "SELECT * FROM seats WHERE seat_id = ?",
                (seat_id,),
            ).fetchone()
            wake = conn.execute(
                "SELECT * FROM wakes WHERE wake_id = ? AND seat_id = ?",
                (wake_id, seat_id),
            ).fetchone()
            if seat is None or wake is None:
                raise GoblinPoolError("seat or wake missing during lease recovery")

            if (
                seat["occupancy_state"] == "OCCUPIED"
                and seat["current_wake_id"] == wake_id
                and wake["status"] == "STARTED"
            ):
                conn.execute(
                    "UPDATE wakes SET status = 'ABORTED', outcome = ? WHERE wake_id = ?",
                    (_json({"classification": reason}), wake_id),
                )
                conn.execute(
                    """
                    UPDATE seats
                    SET occupancy_state = 'AVAILABLE', current_wake_id = NULL
                    WHERE seat_id = ?
                    """,
                    (seat_id,),
                )
                conn.commit()
                return {
                    "status": "RECOVERED",
                    "seat_id": seat_id,
                    "wake_id": wake_id,
                }

            conn.commit()
            return {
                "status": "NO_RECOVERY_NEEDED",
                "seat_id": seat_id,
                "wake_id": wake_id,
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _operator_posture_conn(
        conn: sqlite3.Connection,
        seat_id: str,
        operator_id: str,
    ) -> dict[str, Any]:
        operator = conn.execute(
            "SELECT * FROM operators WHERE operator_id = ?",
            (operator_id,),
        ).fetchone()
        if operator is None:
            return {
                "operator_id": operator_id,
                "registered": False,
                "available": False,
                "eligible": False,
                "authorized": False,
                "authority_ref": None,
            }

        eligibility = conn.execute(
            """
            SELECT eligible FROM seat_operator_eligibility
            WHERE seat_id = ? AND operator_id = ?
            """,
            (seat_id, operator_id),
        ).fetchone()
        authority = conn.execute(
            """
            SELECT authorized, authority_ref FROM seat_operator_authority
            WHERE seat_id = ? AND operator_id = ?
            """,
            (seat_id, operator_id),
        ).fetchone()

        registered = bool(operator["registered"])
        available = registered and bool(operator["available"])
        eligible = available and eligibility is not None and bool(eligibility["eligible"])
        authorized = (
            eligible
            and authority is not None
            and bool(authority["authorized"])
        )

        return {
            "operator_id": operator_id,
            "registered": registered,
            "available": available,
            "eligible": eligible,
            "authorized": authorized,
            "authority_ref": authority["authority_ref"] if authority is not None else None,
            "adapter_kind": operator["adapter_kind"],
            "authority_required": bool(operator["authority_required"]),
        }

    def operator_posture(self, seat_id: str, operator_id: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            return self._operator_posture_conn(conn, seat_id, operator_id)
        finally:
            conn.close()

    def set_operator_availability(self, operator_id: str, available: bool) -> None:
        conn = self._connect()
        try:
            self._begin(conn)
            updated = conn.execute(
                "UPDATE operators SET available = ? WHERE operator_id = ?",
                (1 if available else 0, operator_id),
            )
            if updated.rowcount != 1:
                raise GoblinPoolError(f"unknown operator {operator_id!r}")
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def _assert_active_wake(
        self,
        conn: sqlite3.Connection,
        wake_id: str,
    ) -> tuple[sqlite3.Row, sqlite3.Row]:
        wake = conn.execute(
            "SELECT * FROM wakes WHERE wake_id = ?",
            (wake_id,),
        ).fetchone()
        if wake is None:
            raise GoblinPoolError(f"unknown wake {wake_id!r}")
        seat = conn.execute(
            "SELECT * FROM seats WHERE seat_id = ?",
            (wake["seat_id"],),
        ).fetchone()
        if seat is None:
            raise GoblinPoolError("wake refers to missing seat")
        if (
            wake["status"] != "STARTED"
            or seat["occupancy_state"] != "OCCUPIED"
            or seat["current_wake_id"] != wake_id
        ):
            raise GoblinPoolError("wake is not the active occupant of its seat")
        return wake, seat

    def _run_adapter(
        self,
        adapter_kind: str,
        invocation_id: str,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        if adapter_kind == "READ_REPO_STATE":
            result = subprocess.run(
                ["git", "-C", str(self.workspace), "rev-parse", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=10,
            )
            if result.returncode != 0:
                raise GoblinPoolError(
                    "READ_REPO_STATE failed: " + result.stderr.strip()
                )
            return {
                "head": result.stdout.strip(),
                "adapter_kind": adapter_kind,
            }

        if adapter_kind == "RUN_DECLARED_TEST":
            test_id = args.get("test_id")
            if not isinstance(test_id, str):
                raise GoblinPoolError("RUN_DECLARED_TEST requires string test_id")
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT argv_json FROM declared_tests WHERE test_id = ?",
                    (test_id,),
                ).fetchone()
            finally:
                conn.close()
            if row is None:
                raise GoblinPoolError(f"undeclared test {test_id!r}")
            argv = _unjson(row["argv_json"])
            result = subprocess.run(
                argv,
                cwd=self.workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=30,
            )
            return {
                "adapter_kind": adapter_kind,
                "test_id": test_id,
                "argv": argv,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": result.returncode == 0,
            }

        if adapter_kind == "WRITE_PACKET":
            packet = args.get("packet")
            if not isinstance(packet, dict):
                raise GoblinPoolError("WRITE_PACKET requires object packet")
            packet_dir = self.workspace / ".goblin_pool_packets"
            packet_dir.mkdir(parents=True, exist_ok=True)
            packet_path = packet_dir / f"{invocation_id}.json"
            rendered = json.dumps(packet, indent=2, sort_keys=True) + "\n"
            if packet_path.exists():
                retained = packet_path.read_text(encoding="utf-8")
                if retained != rendered:
                    raise GoblinPoolError(
                        "WRITE_PACKET invocation identity already names different bytes"
                    )
            else:
                with packet_path.open("x", encoding="utf-8", newline="\n") as handle:
                    handle.write(rendered)
            return {
                "adapter_kind": adapter_kind,
                "packet_path": str(packet_path),
                "bytes": len(rendered.encode("utf-8")),
            }

        raise GoblinPoolError(f"unsupported adapter_kind {adapter_kind!r}")

    def execute_operator(
        self,
        wake_id: str,
        operator_invocation_id: str,
        operator_id: str,
        args: dict[str, Any],
    ) -> dict[str, Any]:
        conn = self._connect()
        try:
            self._begin(conn)
            wake, seat = self._assert_active_wake(conn, wake_id)

            existing = conn.execute(
                """
                SELECT * FROM operator_invocations
                WHERE operator_invocation_id = ?
                """,
                (operator_invocation_id,),
            ).fetchone()
            if existing is not None:
                conn.commit()
                return {
                    "operator_invocation_id": operator_invocation_id,
                    "status": existing["status"],
                    "result": (
                        _unjson(existing["result_json"])
                        if existing["result_json"] is not None
                        else None
                    ),
                    "idempotent_replay": True,
                }

            posture = self._operator_posture_conn(
                conn, seat["seat_id"], operator_id
            )

            if not posture["registered"]:
                status = "NOT_REGISTERED"
            elif not posture["available"]:
                status = "NOT_AVAILABLE"
            elif not posture["eligible"]:
                status = "NOT_ELIGIBLE"
            elif not posture["authorized"]:
                status = "AUTHORITY_REQUIRED"
            else:
                status = "ADMITTED"

            conn.execute(
                """
                INSERT INTO operator_invocations(
                    operator_invocation_id, wake_id, seat_id, operator_id,
                    status, args_json, result_json
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    operator_invocation_id,
                    wake_id,
                    seat["seat_id"],
                    operator_id,
                    status,
                    _json(args),
                    None,
                ),
            )

            if status == "AUTHORITY_REQUIRED":
                request_id = f"AR-{operator_invocation_id}"
                conn.execute(
                    """
                    INSERT INTO action_requests(
                        request_id, wake_id, seat_id, operator_id, reason, authority_ref
                    ) VALUES(?,?,?,?,?,?)
                    """,
                    (
                        request_id,
                        wake_id,
                        seat["seat_id"],
                        operator_id,
                        "eligible operator lacks explicit authority",
                        posture["authority_ref"],
                    ),
                )
                conn.commit()
                return {
                    "operator_invocation_id": operator_invocation_id,
                    "status": status,
                    "posture": posture,
                    "action_request_id": request_id,
                    "executed": False,
                }

            if status != "ADMITTED":
                conn.commit()
                return {
                    "operator_invocation_id": operator_invocation_id,
                    "status": status,
                    "posture": posture,
                    "executed": False,
                }

            adapter_kind = posture["adapter_kind"]
            conn.commit()
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            conn.close()
            raise
        finally:
            if conn:
                conn.close()

        try:
            result = self._run_adapter(
                adapter_kind,
                operator_invocation_id,
                args,
            )
            final_status = "EXECUTED"
        except Exception as exc:
            result = {
                "error": f"{type(exc).__name__}: {exc}",
                "adapter_kind": adapter_kind,
            }
            final_status = "FAILED"

        conn = self._connect()
        try:
            self._begin(conn)
            row = conn.execute(
                """
                SELECT * FROM operator_invocations
                WHERE operator_invocation_id = ?
                """,
                (operator_invocation_id,),
            ).fetchone()
            if row is None:
                raise GoblinPoolError("operator invocation disappeared")
            if row["status"] != "ADMITTED":
                raise GoblinPoolError(
                    "operator invocation changed after admission"
                )
            conn.execute(
                """
                UPDATE operator_invocations
                SET status = ?, result_json = ?
                WHERE operator_invocation_id = ?
                """,
                (final_status, _json(result), operator_invocation_id),
            )
            receipt_id = f"R-{operator_invocation_id}"
            conn.execute(
                """
                INSERT INTO receipts(
                    receipt_id, receipt_kind, wake_id, seat_id, subject_id, payload_json
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    receipt_id,
                    "OPERATOR_EXECUTION",
                    wake_id,
                    row["seat_id"],
                    operator_invocation_id,
                    _json(
                        {
                            "operator_id": operator_id,
                            "status": final_status,
                            "result": result,
                        }
                    ),
                ),
            )
            conn.commit()
            return {
                "operator_invocation_id": operator_invocation_id,
                "receipt_id": receipt_id,
                "status": final_status,
                "result": result,
                "executed": final_status == "EXECUTED",
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def emit_semantic_request(
        self,
        wake_id: str,
        request_id: str,
        prompt: str,
    ) -> dict[str, Any]:
        conn = self._connect()
        try:
            self._begin(conn)
            wake, seat = self._assert_active_wake(conn, wake_id)
            conn.execute(
                """
                INSERT INTO semantic_requests(
                    request_id, wake_id, seat_id, basis_version, prompt, status
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    request_id,
                    wake_id,
                    seat["seat_id"],
                    wake["basis_version"],
                    prompt,
                    "PENDING",
                ),
            )
            conn.commit()
            return {
                "request_id": request_id,
                "wake_id": wake_id,
                "seat_id": seat["seat_id"],
                "basis_version": wake["basis_version"],
                "status": "PENDING",
                "seat_state_changed": False,
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def submit_semantic_proposal(
        self,
        request_id: str,
        proposal_id: str,
        payload: Any,
    ) -> dict[str, Any]:
        conn = self._connect()
        try:
            self._begin(conn)
            request = conn.execute(
                "SELECT * FROM semantic_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            if request is None:
                raise GoblinPoolError(f"unknown semantic request {request_id!r}")
            conn.execute(
                """
                INSERT INTO semantic_proposals(proposal_id, request_id, payload_json)
                VALUES(?,?,?)
                """,
                (proposal_id, request_id, _json(payload)),
            )
            conn.execute(
                """
                UPDATE semantic_requests SET status = 'PROPOSAL_RECEIVED'
                WHERE request_id = ?
                """,
                (request_id,),
            )
            conn.commit()
            return {
                "proposal_id": proposal_id,
                "request_id": request_id,
                "status": "PROPOSAL_RECEIVED",
                "seat_state_changed": False,
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def _validate_consumption(
        self,
        conn: sqlite3.Connection,
        seat: sqlite3.Row,
        consumed_event_ids: list[str],
    ) -> str:
        eligible = self._eligible_events_conn(
            conn,
            seat["seat_id"],
            seat["cursor_event_id"],
        )
        eligible_ids = [row["event_id"] for row in eligible]
        if consumed_event_ids != eligible_ids[: len(consumed_event_ids)]:
            raise GoblinPoolError(
                "consumed events must be a contiguous prefix of seat-eligible events"
            )
        if not consumed_event_ids:
            return seat["cursor_event_id"]
        return consumed_event_ids[-1]

    def _accepted_invocations(
        self,
        conn: sqlite3.Connection,
        wake_id: str,
        seat_id: str,
        invocation_ids: list[str],
    ) -> None:
        for invocation_id in invocation_ids:
            row = conn.execute(
                """
                SELECT * FROM operator_invocations
                WHERE operator_invocation_id = ?
                """,
                (invocation_id,),
            ).fetchone()
            if (
                row is None
                or row["wake_id"] != wake_id
                or row["seat_id"] != seat_id
                or row["status"] != "EXECUTED"
            ):
                raise GoblinPoolError(
                    f"operator invocation {invocation_id!r} is not an executed "
                    "invocation of this wake"
                )

    def commit_transition(
        self,
        wake_id: str,
        *,
        transition_id: str,
        output_id: str,
        output_kind: str,
        output_payload: Any,
        consumed_event_ids: list[str],
        resulting_working_state: dict[str, Any],
        accepted_operator_invocation_ids: list[str] | None = None,
        inject_failure_before_commit: bool = False,
    ) -> dict[str, Any]:
        accepted_operator_invocation_ids = list(
            accepted_operator_invocation_ids or []
        )
        conn = self._connect()
        try:
            self._begin(conn)
            wake = conn.execute(
                "SELECT * FROM wakes WHERE wake_id = ?",
                (wake_id,),
            ).fetchone()
            if wake is None:
                raise GoblinPoolError(f"unknown wake {wake_id!r}")

            if wake["status"] == "COMMITTED":
                transition = conn.execute(
                    "SELECT * FROM transitions WHERE wake_id = ?",
                    (wake_id,),
                ).fetchone()
                output = conn.execute(
                    "SELECT * FROM outputs WHERE wake_id = ?",
                    (wake_id,),
                ).fetchone()
                receipt = conn.execute(
                    """
                    SELECT * FROM receipts
                    WHERE wake_id = ? AND receipt_kind = 'STATE_TRANSITION'
                    """,
                    (wake_id,),
                ).fetchone()
                if (
                    transition is None
                    or output is None
                    or receipt is None
                    or transition["transition_id"] != transition_id
                    or output["output_id"] != output_id
                ):
                    raise GoblinPoolError(
                        "committed wake replay does not match retained identities"
                    )
                conn.commit()
                return {
                    "status": "ALREADY_COMMITTED",
                    "idempotent_replay": True,
                    "receipt_id": receipt["receipt_id"],
                    "transition_id": transition_id,
                    "output_id": output_id,
                    "resulting_version": transition["resulting_version"],
                }

            seat = conn.execute(
                "SELECT * FROM seats WHERE seat_id = ?",
                (wake["seat_id"],),
            ).fetchone()
            if seat is None:
                raise GoblinPoolError("wake refers to missing seat")

            if seat["state_version"] != wake["basis_version"]:
                conn.execute(
                    """
                    UPDATE wakes
                    SET status = 'STALE_REJECTED', outcome = ?
                    WHERE wake_id = ?
                    """,
                    (
                        _json(
                            {
                                "classification": "STALE_BASIS",
                                "wake_basis_version": wake["basis_version"],
                                "current_seat_version": seat["state_version"],
                            }
                        ),
                        wake_id,
                    ),
                )
                conn.commit()
                return {
                    "status": "STALE_BASIS",
                    "wake_id": wake_id,
                    "seat_id": seat["seat_id"],
                    "wake_basis_version": wake["basis_version"],
                    "current_seat_version": seat["state_version"],
                    "accepted": False,
                }

            if (
                wake["status"] != "STARTED"
                or seat["occupancy_state"] != "OCCUPIED"
                or seat["current_wake_id"] != wake_id
            ):
                raise GoblinPoolError(
                    "wake is not the current seat occupant and basis is not stale"
                )

            existing_output = conn.execute(
                "SELECT wake_id FROM outputs WHERE output_id = ?",
                (output_id,),
            ).fetchone()
            if existing_output is not None:
                raise GoblinPoolError(
                    f"duplicate output_id {output_id!r} belongs to "
                    f"wake {existing_output['wake_id']!r}"
                )

            existing_transition = conn.execute(
                "SELECT wake_id FROM transitions WHERE transition_id = ?",
                (transition_id,),
            ).fetchone()
            if existing_transition is not None:
                raise GoblinPoolError(
                    f"duplicate transition_id {transition_id!r}"
                )

            resulting_cursor = self._validate_consumption(
                conn, seat, consumed_event_ids
            )
            self._accepted_invocations(
                conn,
                wake_id,
                seat["seat_id"],
                accepted_operator_invocation_ids,
            )

            prior_version = seat["state_version"]
            resulting_version = prior_version + 1
            prior_state_json = seat["working_state_json"]
            resulting_state_json = _json(resulting_working_state)

            conn.execute(
                """
                INSERT INTO outputs(
                    output_id, wake_id, seat_id, output_kind, payload_json
                ) VALUES(?,?,?,?,?)
                """,
                (
                    output_id,
                    wake_id,
                    seat["seat_id"],
                    output_kind,
                    _json(output_payload),
                ),
            )

            conn.execute(
                """
                INSERT INTO transitions(
                    transition_id, wake_id, seat_id,
                    prior_version, resulting_version,
                    prior_cursor_event_id, resulting_cursor_event_id,
                    prior_working_state_json, resulting_working_state_json,
                    consumed_events_json, accepted_outputs_json,
                    accepted_operator_invocations_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    transition_id,
                    wake_id,
                    seat["seat_id"],
                    prior_version,
                    resulting_version,
                    seat["cursor_event_id"],
                    resulting_cursor,
                    prior_state_json,
                    resulting_state_json,
                    _json(consumed_event_ids),
                    _json([output_id]),
                    _json(accepted_operator_invocation_ids),
                ),
            )

            conn.execute(
                """
                UPDATE seats
                SET cursor_event_id = ?,
                    working_state_json = ?,
                    state_version = ?,
                    status = 'ACTIVE',
                    occupancy_state = 'AVAILABLE',
                    current_wake_id = NULL
                WHERE seat_id = ?
                """,
                (
                    resulting_cursor,
                    resulting_state_json,
                    resulting_version,
                    seat["seat_id"],
                ),
            )

            conn.execute(
                """
                UPDATE wakes
                SET status = 'COMMITTED', outcome = ?
                WHERE wake_id = ?
                """,
                (
                    _json(
                        {
                            "classification": "STATE_TRANSITION_COMMITTED",
                            "transition_id": transition_id,
                            "output_id": output_id,
                        }
                    ),
                    wake_id,
                ),
            )

            receipt_id = f"R-{transition_id}"
            receipt_payload = {
                "seat_id": seat["seat_id"],
                "wake_id": wake_id,
                "transition_id": transition_id,
                "prior_version": prior_version,
                "resulting_version": resulting_version,
                "prior_cursor_event_id": seat["cursor_event_id"],
                "resulting_cursor_event_id": resulting_cursor,
                "consumed_event_ids": consumed_event_ids,
                "accepted_output_ids": [output_id],
                "accepted_operator_invocation_ids": accepted_operator_invocation_ids,
                "prior_working_state": _unjson(prior_state_json),
                "resulting_working_state": resulting_working_state,
            }
            conn.execute(
                """
                INSERT INTO receipts(
                    receipt_id, receipt_kind, wake_id, seat_id, subject_id, payload_json
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    receipt_id,
                    "STATE_TRANSITION",
                    wake_id,
                    seat["seat_id"],
                    transition_id,
                    _json(receipt_payload),
                ),
            )

            if inject_failure_before_commit:
                raise InjectedCrash(
                    "synthetic controller crash immediately before transaction commit"
                )

            conn.commit()
            return {
                "status": "COMMITTED",
                "receipt_id": receipt_id,
                **receipt_payload,
            }
        except Exception:
            if conn.in_transaction:
                conn.rollback()
            raise
        finally:
            conn.close()

    def counts(self) -> dict[str, int]:
        conn = self._connect()
        try:
            tables = (
                "seats",
                "events",
                "wakes",
                "operator_invocations",
                "action_requests",
                "semantic_requests",
                "semantic_proposals",
                "outputs",
                "transitions",
                "receipts",
            )
            return {
                table: int(
                    conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                )
                for table in tables
            }
        finally:
            conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--workspace", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")

    p_snapshot = sub.add_parser("seat")
    p_snapshot.add_argument("seat_id", choices=SEAT_IDS)

    p_wake = sub.add_parser("wake")
    p_wake.add_argument("seat_id", choices=SEAT_IDS)
    p_wake.add_argument("wake_id")

    p_posture = sub.add_parser("posture")
    p_posture.add_argument("seat_id", choices=SEAT_IDS)
    p_posture.add_argument("operator_id")

    args = parser.parse_args(argv)
    pool = GoblinPool(args.db, args.workspace)

    if args.command == "init":
        pool.initialize_fixture()
        result = {
            "status": "INITIALIZED",
            "seats": [pool.seat_snapshot(seat) for seat in SEAT_IDS],
        }
    elif args.command == "seat":
        result = pool.seat_snapshot(args.seat_id)
    elif args.command == "wake":
        result = pool.start_wake(args.seat_id, args.wake_id)
    elif args.command == "posture":
        result = pool.operator_posture(args.seat_id, args.operator_id)
    else:
        raise AssertionError(args.command)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
