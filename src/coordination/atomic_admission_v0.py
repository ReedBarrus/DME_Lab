"""Concurrency-safe repo-local atomic admission candidate V0.

This module binds one bounded admission decision, one seat lease, one work-attempt
identity, one wake-budget reservation, and one pre-satisfied authority
coordinate in one fail-closed critical section.

It does not grant authority, invoke a model, execute work, mutate a trust root,
or establish self-moving-workcycle standing.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc


STATE_TYPE = "ATOMIC_ADMISSION_STATE_V0"
RECEIPT_TYPE = "ATOMIC_ADMISSION_RECEIPT_V0"


class AtomicAdmissionError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _write_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(_canonical_bytes(value))
    temporary.replace(path)


def _acquire_lock(lock_path: Path, *, attempts: int = 400, delay: float = 0.002) -> int:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(attempts):
        try:
            return os.open(
                str(lock_path),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
        except FileExistsError:
            time.sleep(delay)
    raise AtomicAdmissionError("atomic admission lock timeout")


def _release_lock(lock_path: Path, fd: int) -> None:
    try:
        os.close(fd)
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _load_or_initialize_state(
    state_path: Path,
    *,
    campaign_id: str,
    wake_generation: int,
    initial_budget: Mapping[str, Any],
) -> dict[str, Any]:
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AtomicAdmissionError(f"cannot read atomic admission state: {exc}") from exc
        if state.get("object_type") != STATE_TYPE:
            raise AtomicAdmissionError("atomic admission state schema mismatch")
        if state.get("campaign_id") != campaign_id:
            raise AtomicAdmissionError("campaign identity mismatch")
        budget = state.get("budget")
        if not isinstance(budget, dict):
            raise AtomicAdmissionError("atomic admission state budget missing")
        wc.verify_seal(budget)
        return state

    budget = dict(initial_budget)
    wc.verify_seal(budget)
    state = {
        "object_type": STATE_TYPE,
        "campaign_id": campaign_id,
        "wake_generation": wake_generation,
        "budget": budget,
        "active_admission": None,
        "seat_lease": None,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "model_invocation_effect": "NONE",
    }
    _write_atomic(state_path, state)
    return state


def try_atomic_admission(
    *,
    store_dir: str | Path,
    campaign_id: str,
    work_item_id: str,
    work_attempt_id: str,
    seat_id: str,
    occupant_id: str,
    wake_generation: int,
    authority_coordinate: str,
    authority_satisfied: bool,
    dependency_satisfied: bool,
    frame_current: bool,
    no_hold: bool,
    control: Mapping[str, Any],
    initial_budget: Mapping[str, Any],
) -> dict[str, Any]:
    """Attempt one bounded admission atomically.

    The supplied authority coordinate must already be satisfied. This function
    consumes no external authority and creates none.
    """
    required_strings = {
        "campaign_id": campaign_id,
        "work_item_id": work_item_id,
        "work_attempt_id": work_attempt_id,
        "seat_id": seat_id,
        "occupant_id": occupant_id,
        "authority_coordinate": authority_coordinate,
    }
    missing = [name for name, value in required_strings.items() if not str(value).strip()]
    if missing:
        raise AtomicAdmissionError(f"missing required identities: {', '.join(missing)}")
    if wake_generation < 0:
        raise AtomicAdmissionError("wake_generation must be nonnegative")
    wc.verify_seal(initial_budget)

    root = Path(store_dir)
    state_path = root / "atomic_admission_state.json"
    lock_path = root / "atomic_admission.lock"
    fd = _acquire_lock(lock_path)
    try:
        state = _load_or_initialize_state(
            state_path,
            campaign_id=campaign_id,
            wake_generation=wake_generation,
            initial_budget=initial_budget,
        )

        if int(state.get("wake_generation", -1)) != wake_generation:
            return {
                "object_type": "ATOMIC_ADMISSION_DECISION_V0",
                "admitted": False,
                "blockers": ["wake_generation_mismatch"],
                "receipt": None,
                "execution_performed": False,
                "model_invocation_effect": "NONE",
                "authority_effect": "NONE",
            }

        active = state.get("active_admission")
        seat_lease = state.get("seat_lease")
        seat_available = active is None and seat_lease is None

        continuation = wc.evaluate_one_successor_continuation(
            control=control,
            dependency_satisfied=dependency_satisfied,
            frame_current=frame_current,
            seat_available=seat_available,
            no_hold=no_hold,
            authority_satisfied=authority_satisfied,
            budget=state["budget"],
        )
        blockers = list(continuation["blockers"])
        if active is not None:
            blockers.append("active_admission")
        if not authority_coordinate:
            blockers.append("authority_coordinate_missing")

        if blockers:
            return {
                "object_type": "ATOMIC_ADMISSION_DECISION_V0",
                "admitted": False,
                "blockers": sorted(set(blockers)),
                "receipt": None,
                "state_sha256": _sha256(state),
                "execution_performed": False,
                "model_invocation_effect": "NONE",
                "authority_effect": "NONE",
            }

        pre_state_sha256 = _sha256(state)
        reserved_budget = wc.reserve_one_item(state["budget"])
        admission_material = {
            "campaign_id": campaign_id,
            "work_item_id": work_item_id,
            "work_attempt_id": work_attempt_id,
            "seat_id": seat_id,
            "occupant_id": occupant_id,
            "wake_generation": wake_generation,
            "authority_coordinate": authority_coordinate,
            "pre_state_sha256": pre_state_sha256,
            "reserved_budget_sha256": reserved_budget["integrity_sha256"],
        }
        admission_id = f"atomic-admission:sha256:{_sha256(admission_material)}"
        receipt = {
            "object_type": RECEIPT_TYPE,
            "admission_id": admission_id,
            **admission_material,
            "authority_input_posture": "CALLER_SUPPLIED_PRECONDITION",
            "authority_verification": "NOT_PERFORMED",
            "authority_effect": "NONE",
            "execution_performed": False,
            "model_invocation_effect": "NONE",
            "claim_ceiling": (
                "Atomic local admission receipt over caller-supplied preconditions only. "
                "Authority validity is not verified here; no authority is granted and no "
                "model invocation is performed."
            ),
        }

        next_state = dict(state)
        next_state["budget"] = reserved_budget
        next_state["seat_lease"] = {
            "seat_id": seat_id,
            "occupant_id": occupant_id,
            "work_attempt_id": work_attempt_id,
            "wake_generation": wake_generation,
        }
        next_state["active_admission"] = receipt
        _write_atomic(state_path, next_state)

        return {
            "object_type": "ATOMIC_ADMISSION_DECISION_V0",
            "admitted": True,
            "blockers": [],
            "receipt": receipt,
            "state_sha256": _sha256(next_state),
            "execution_performed": False,
            "model_invocation_effect": "NONE",
            "authority_effect": "NONE",
        }
    finally:
        _release_lock(lock_path, fd)
