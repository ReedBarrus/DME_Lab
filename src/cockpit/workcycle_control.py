"""Operator-local workcycle control membrane.

Real control state is intentionally stored outside the repository. Repository
objects may describe requested posture, but cannot enable execution by commit.

This module provides preview -> confirm -> commit for bounded operator gestures.
It does not invoke a model or mutate repository source.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from typing import Any, Mapping
from urllib.parse import urlparse

from src.cockpit.workcycle_projection import build_workcycle_projection


class WorkcycleControlError(RuntimeError):
    pass


CONTROL_SCHEMA = "WORKCYCLE_LOCAL_CONTROL_V0"
CONTROL_VERBS = frozenset({"ENABLE", "PAUSE", "STOP", "WAKE", "CLEAR_WAKE", "ADMIT_ONE"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def default_control_state(campaign_id: str = "WORKCYCLE_STABILIZATION_001") -> dict[str, Any]:
    return {
        "object_type": CONTROL_SCHEMA,
        "campaign_id": campaign_id,
        "lifecycle_state": "PAUSED",
        "workflow_enabled": False,
        "seat_work_enabled": False,
        "wake_requested": False,
        "wake_generation": 0,
        "auto_continuation_limit": 0,
        "current_admission": None,
        "last_operator_gesture": None,
        "updated_at": None,
        "execution_effect": "LOCAL_WORKCYCLE_CONTROL_ONLY",
        "authority_effect": "OPERATOR_LOCAL_CONTROL",
    }


def _write_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


@dataclass
class LocalWorkcycleControlStore:
    path: Path
    repo: Path
    lock: threading.RLock = field(default_factory=threading.RLock)

    def read(self) -> dict[str, Any]:
        with self.lock:
            try:
                value = json.loads(self.path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                value = default_control_state()
                _write_atomic(self.path, value)
            except (OSError, json.JSONDecodeError) as exc:
                raise WorkcycleControlError(f"cannot read local control state: {exc}") from exc
            if value.get("object_type") != CONTROL_SCHEMA:
                raise WorkcycleControlError("local control state schema mismatch")
            return value

    def state_sha256(self) -> str:
        return _sha256(self.read())

    def _next_state(self, state: Mapping[str, Any], verb: str) -> dict[str, Any]:
        if verb not in CONTROL_VERBS:
            raise WorkcycleControlError(f"unsupported workcycle control verb: {verb}")
        next_state = copy.deepcopy(dict(state))

        if verb == "ENABLE":
            next_state["lifecycle_state"] = "ACTIVE"
            next_state["workflow_enabled"] = True
            next_state["seat_work_enabled"] = True
        elif verb == "PAUSE":
            next_state["lifecycle_state"] = "PAUSED"
            next_state["workflow_enabled"] = False
            next_state["seat_work_enabled"] = False
            next_state["wake_requested"] = False
        elif verb == "STOP":
            next_state["lifecycle_state"] = "STOPPED"
            next_state["workflow_enabled"] = False
            next_state["seat_work_enabled"] = False
            next_state["wake_requested"] = False
            next_state["auto_continuation_limit"] = 0
            next_state["current_admission"] = None
        elif verb == "WAKE":
            if not state.get("workflow_enabled") or not state.get("seat_work_enabled"):
                raise WorkcycleControlError("WAKE requires ENABLED workflow + seat work")
            next_state["wake_requested"] = True
            next_state["wake_generation"] = int(state.get("wake_generation", 0)) + 1
        elif verb == "CLEAR_WAKE":
            next_state["wake_requested"] = False
        elif verb == "ADMIT_ONE":
            if not state.get("workflow_enabled") or not state.get("seat_work_enabled"):
                raise WorkcycleControlError("ADMIT_ONE requires ENABLED workflow + seat work")
            if not state.get("wake_requested"):
                raise WorkcycleControlError("ADMIT_ONE requires an outstanding WAKE")
            if state.get("current_admission") is not None:
                raise WorkcycleControlError("an admission is already active")
            projection = build_workcycle_projection(self.repo)
            item = projection.get("next_eligible_work_item")
            eligibility = projection.get("eligibility") or {}
            if not item:
                raise WorkcycleControlError("no source-bound next eligible work item exists")
            if eligibility.get("eligible") is not True:
                raise WorkcycleControlError(
                    "real eligibility is not established; unresolved coordinates remain"
                )
            next_state["current_admission"] = {
                "work_item_id": item,
                "admitted_at": _utc_now(),
                "wake_generation": next_state["wake_generation"],
                "status": "ADMITTED_NOT_INVOKED",
            }
            next_state["wake_requested"] = False

        return next_state

    def preview(self, intent: Mapping[str, Any]) -> dict[str, Any]:
        verb = str(intent.get("verb", "")).upper()
        gesture_id = str(intent.get("gesture_id", "")).strip()
        if not gesture_id:
            raise WorkcycleControlError("gesture_id is required")
        with self.lock:
            current = self.read()
            next_state = self._next_state(current, verb)
            preview = {
                "object_type": "WORKCYCLE_CONTROL_PREVIEW_V0",
                "gesture_id": gesture_id,
                "verb": verb,
                "reason": intent.get("reason"),
                "current_state_sha256": _sha256(current),
                "current_state": current,
                "next_state": next_state,
                "execution_effect": "LOCAL_CONTROL_STATE_TRANSITION",
                "model_invocation_effect": "NONE",
                "repository_mutation_effect": "NONE",
            }
            return {
                "preview": preview,
                "preview_sha256": _sha256(preview),
            }

    def commit(
        self,
        *,
        preview: Mapping[str, Any],
        preview_sha256: str,
        confirmed_by: str,
    ) -> dict[str, Any]:
        if confirmed_by != "REED":
            raise WorkcycleControlError("explicit local operator confirmation required")
        if _sha256(preview) != preview_sha256:
            raise WorkcycleControlError("preview identity mismatch")
        with self.lock:
            current = self.read()
            if _sha256(current) != preview.get("current_state_sha256"):
                raise WorkcycleControlError("control state changed after preview")
            next_state = copy.deepcopy(dict(preview.get("next_state") or {}))
            next_state["last_operator_gesture"] = {
                "gesture_id": preview.get("gesture_id"),
                "verb": preview.get("verb"),
                "confirmed_by": confirmed_by,
                "committed_at": _utc_now(),
            }
            next_state["updated_at"] = _utc_now()
            _write_atomic(self.path, next_state)
            return {
                "status": "COMMITTED",
                "state_sha256": _sha256(next_state),
                "state": next_state,
                "model_invocation_effect": "NONE",
                "repository_mutation_effect": "NONE",
            }


class WorkcycleControlServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], store: LocalWorkcycleControlStore):
        super().__init__(address, WorkcycleControlHandler)
        self.store = store


class WorkcycleControlHandler(BaseHTTPRequestHandler):
    server: WorkcycleControlServer

    def _headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Cache-Control", "no-store")

    def _json(self, status: int, value: Mapping[str, Any]) -> None:
        payload = _canonical_bytes(value)
        self.send_response(status)
        self._headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 1_000_000:
            raise WorkcycleControlError("invalid request body length")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._headers()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/workcycle/control/state":
            state = self.server.store.read()
            self._json(200, {"state": state, "state_sha256": _sha256(state)})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_json()
            if path == "/workcycle/control/preview":
                self._json(200, self.server.store.preview(body))
                return
            if path == "/workcycle/control/commit":
                result = self.server.store.commit(
                    preview=body.get("preview") or {},
                    preview_sha256=str(body.get("preview_sha256", "")),
                    confirmed_by=str(body.get("confirmed_by", "")),
                )
                self._json(200, result)
                return
            self._json(404, {"error": "not found"})
        except Exception as exc:
            self._json(409, {"error": f"{type(exc).__name__}: {exc}"})

    def do_PUT(self) -> None:
        self._json(405, {"error": "method not allowed"})

    do_PATCH = do_PUT
    do_DELETE = do_PUT

    def log_message(self, format: str, *args: Any) -> None:
        return
