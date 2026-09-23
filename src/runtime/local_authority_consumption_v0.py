"""Single-process, one-use authority consumption for one local invocation.

Current authority is retained in a local trust-root-owned JSON state file.
Repository artifacts may project historical receipts, but they are not the
source of remaining authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable, Mapping


ENVELOPE_TYPE = "LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0"
STATE_TYPE = "LOCAL_MODEL_INVOCATION_AUTHORITY_STATE_V0"
ISSUANCE_TYPE = "LOCAL_AUTHORITY_ISSUANCE_RECORD_V0"
RESERVATION_TYPE = "LOCAL_AUTHORITY_CONSUMPTION_RESERVATION_V0"
RECEIPT_TYPE = "LOCAL_AUTHORITY_CONSUMPTION_RECEIPT_V0"
DENIAL_TYPE = "LOCAL_AUTHORITY_REPLAY_DENIAL_V0"
FAILURE_TYPE = "LOCAL_AUTHORITY_INVOCATION_FAILURE_V0"

ACTIVE = "ACTIVE"
CONSUMING = "CONSUMING"
CONSUMED = "CONSUMED"
RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
NONE = "NONE"

_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,95}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_STATE_LOCK = threading.RLock()

AUTHORITY_ENVELOPE_KEYS = frozenset(
    {
        "object_type",
        "capability_id",
        "approval_id",
        "request_sha256",
        "input_sha256",
        "model",
        "endpoint_identity",
        "executor_sha256",
        "policy_sha256",
        "use_limit",
        "remaining_uses",
        "status",
        "issued_at",
        "expires_at",
    }
)


class AuthorityEnvelopeError(ValueError):
    """The supplied authority envelope cannot enter the V0 apparatus."""


class AuthorityStateError(RuntimeError):
    """The local authority state cannot be safely used."""


class AuthorityInvocationError(RuntimeError):
    """Invocation failed after authority was reserved and requires recovery."""


def default_authority_state_root() -> Path:
    return Path.home() / ".dme_lab_bridge" / "authority_state_v0"


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise AuthorityEnvelopeError(f"{field} must be a non-empty string")
    return value


def _required_id(value: Any, field: str) -> str:
    text = _required_text(value, field)
    if not _ID_RE.fullmatch(text):
        raise AuthorityEnvelopeError(f"{field} has invalid identity syntax")
    return text


def _required_sha256(value: Any, field: str) -> str:
    text = _required_text(value, field)
    if not _SHA256_RE.fullmatch(text):
        raise AuthorityEnvelopeError(f"{field} must be a lowercase SHA-256")
    return text


def canonical_sha256(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_authority_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != AUTHORITY_ENVELOPE_KEYS:
        raise AuthorityEnvelopeError("authority envelope has an exact-key mismatch")
    retained = copy.deepcopy(dict(envelope))
    if retained["object_type"] != ENVELOPE_TYPE:
        raise AuthorityEnvelopeError("unsupported authority envelope type")
    _required_id(retained["capability_id"], "capability_id")
    _required_id(retained["approval_id"], "approval_id")
    for field in (
        "request_sha256",
        "input_sha256",
        "executor_sha256",
        "policy_sha256",
    ):
        _required_sha256(retained[field], field)
    for field in ("model", "endpoint_identity", "issued_at"):
        _required_text(retained[field], field)
    if retained["expires_at"] is not None:
        raise AuthorityEnvelopeError("V0 supports only expires_at=null")
    if retained["use_limit"] != 1:
        raise AuthorityEnvelopeError("V0 requires use_limit=1")
    if retained["remaining_uses"] != 1:
        raise AuthorityEnvelopeError("a fresh V0 envelope requires remaining_uses=1")
    if retained["status"] != ACTIVE:
        raise AuthorityEnvelopeError("a fresh V0 envelope requires status=ACTIVE")
    return retained


def _record_id(prefix: str, record: Mapping[str, Any]) -> str:
    return f"{prefix}:sha256:{canonical_sha256(record)}"


class LocalAuthorityStateStore:
    """Atomic JSON state under one local root; qualified only in one process."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (default_authority_state_root() if root is None else root).resolve()

    def state_path(self, capability_id: str) -> Path:
        retained_id = _required_id(capability_id, "capability_id")
        return self.root / f"{retained_id}.json"

    def issue(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        retained = validate_authority_envelope(envelope)
        capability_id = retained["capability_id"]
        with _STATE_LOCK:
            path = self.state_path(capability_id)
            if path.exists():
                raise AuthorityStateError("capability state already exists")
            issued_record = {
                "object_type": ISSUANCE_TYPE,
                "capability_id": capability_id,
                "approval_id": retained["approval_id"],
                "issued_at": retained["issued_at"],
                "remaining_uses": 1,
                "status": ACTIVE,
            }
            state = {
                "object_type": STATE_TYPE,
                "issued_envelope_sha256": canonical_sha256(retained),
                "envelope": retained,
                "history": [issued_record],
            }
            self._write_unlocked(path, state)
            return copy.deepcopy(state)

    def read(self, capability_id: str) -> dict[str, Any]:
        with _STATE_LOCK:
            return copy.deepcopy(self._read_unlocked(self.state_path(capability_id)))

    def _read_unlocked(self, path: Path) -> dict[str, Any]:
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise AuthorityStateError("capability state is missing") from exc
        if not isinstance(state, dict) or state.get("object_type") != STATE_TYPE:
            raise AuthorityStateError("capability state has an unsupported type")
        if not isinstance(state.get("envelope"), dict) or not isinstance(
            state.get("history"), list
        ):
            raise AuthorityStateError("capability state is malformed")
        return state

    def _write_unlocked(self, path: Path, state: Mapping[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        encoded = (
            json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        ).encode("utf-8")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.stem}.",
            suffix=".tmp",
            dir=self.root,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_path, path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()


def consume_authority_once(
    envelope: Mapping[str, Any],
    *,
    store: LocalAuthorityStateStore,
    invoke: Callable[[], Any],
    clock: Callable[[], str],
) -> dict[str, Any]:
    """Consume one authority envelope and invoke at most once.

    The single-process lock is held across reservation, invocation, and final
    receipt persistence.  A durable CONSUMING reservation with zero remaining
    uses is written before the invocation boundary is entered.
    """

    retained = validate_authority_envelope(envelope)
    capability_id = retained["capability_id"]
    attempted_envelope_sha256 = canonical_sha256(retained)

    with _STATE_LOCK:
        state = store._read_unlocked(store.state_path(capability_id))
        if state.get("issued_envelope_sha256") != attempted_envelope_sha256:
            raise AuthorityStateError("attempted envelope differs from issued envelope")

        current = state["envelope"]
        status_before = current.get("status")
        remaining_before = current.get("remaining_uses")
        if status_before != ACTIVE or remaining_before != 1:
            prior_receipt = next(
                (
                    record
                    for record in reversed(state["history"])
                    if record.get("object_type") == RECEIPT_TYPE
                ),
                None,
            )
            denial_basis = {
                "object_type": DENIAL_TYPE,
                "capability_id": capability_id,
                "approval_id": retained["approval_id"],
                "attempted_envelope_sha256": attempted_envelope_sha256,
                "request_sha256": retained["request_sha256"],
                "input_sha256": retained["input_sha256"],
                "model": retained["model"],
                "endpoint_identity": retained["endpoint_identity"],
                "use_limit": retained["use_limit"],
                "pre_use_remaining_uses": remaining_before,
                "post_use_remaining_uses": remaining_before,
                "status": status_before,
                "current_authority": NONE,
                "decision": "DENY",
                "reason": "AUTHORITY_EXHAUSTED",
                "lmstudio_invoked": False,
                "invocation_count": 0,
                "historical_consumption_receipt_id": (
                    None if prior_receipt is None else prior_receipt["receipt_id"]
                ),
                "executor_sha256": retained["executor_sha256"],
                "policy_sha256": retained["policy_sha256"],
                "denied_at": _required_text(clock(), "denied_at"),
            }
            denial = dict(denial_basis)
            denial["denial_id"] = _record_id("denial", denial_basis)
            state["history"].append(denial)
            store._write_unlocked(store.state_path(capability_id), state)
            return {"decision": "DENY", "witness": copy.deepcopy(denial)}

        reserved_at = _required_text(clock(), "reserved_at")
        reservation_basis = {
            "object_type": RESERVATION_TYPE,
            "capability_id": capability_id,
            "approval_id": retained["approval_id"],
            "pre_use_remaining_uses": 1,
            "post_use_remaining_uses": 0,
            "status_before": ACTIVE,
            "status_after": CONSUMING,
            "authority_reserved_before_invocation": True,
            "reserved_at": reserved_at,
        }
        reservation = dict(reservation_basis)
        reservation["reservation_id"] = _record_id("reservation", reservation_basis)
        current["remaining_uses"] = 0
        current["status"] = CONSUMING
        state["history"].append(reservation)
        store._write_unlocked(store.state_path(capability_id), state)

        try:
            invocation_result = invoke()
        except Exception as exc:
            failed_at = _required_text(clock(), "failed_at")
            failure = {
                "object_type": FAILURE_TYPE,
                "capability_id": capability_id,
                "approval_id": retained["approval_id"],
                "reservation_id": reservation["reservation_id"],
                "remaining_uses": 0,
                "status": RECOVERY_REQUIRED,
                "current_authority": NONE,
                "invocation_error_type": type(exc).__name__,
                "failed_at": failed_at,
            }
            current["status"] = RECOVERY_REQUIRED
            state["history"].append(failure)
            store._write_unlocked(store.state_path(capability_id), state)
            raise AuthorityInvocationError(
                "invocation failed after authority reservation"
            ) from exc

        consumed_at = _required_text(clock(), "consumed_at")
        receipt_basis = {
            "object_type": RECEIPT_TYPE,
            "capability_id": capability_id,
            "approval_id": retained["approval_id"],
            "issued_envelope_sha256": attempted_envelope_sha256,
            "request_sha256": retained["request_sha256"],
            "input_sha256": retained["input_sha256"],
            "model": retained["model"],
            "endpoint_identity": retained["endpoint_identity"],
            "reservation_id": reservation["reservation_id"],
            "use_limit": 1,
            "pre_use_remaining_uses": 1,
            "post_use_remaining_uses": 0,
            "status": CONSUMED,
            "current_authority": NONE,
            "invocation_count": 1,
            "executor_sha256": retained["executor_sha256"],
            "policy_sha256": retained["policy_sha256"],
            "consumed_at": consumed_at,
        }
        receipt = dict(receipt_basis)
        receipt["receipt_id"] = _record_id("receipt", receipt_basis)
        current["status"] = CONSUMED
        state["history"].append(receipt)
        store._write_unlocked(store.state_path(capability_id), state)
        return {
            "decision": "INVOKED",
            "receipt": copy.deepcopy(receipt),
            "invocation_result": invocation_result,
        }
