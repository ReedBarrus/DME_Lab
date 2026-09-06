"""Synthetic envelopes used to pressure the provisional ledger contract."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def envelope(
    envelope_id: str,
    signal_id: str,
    event_time: str | None,
    source_sequence: int | None,
    payload: Any,
    *,
    missingness: dict[str, Any] | None = None,
    amendment: dict[str, Any] | None = None,
    extra_signal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    signal = {
        "identity": signal_id,
        "time": event_time,
        "type": "synthetic.os_event",
        "payload": payload,
    }
    if extra_signal:
        signal.update(extra_signal)

    result: dict[str, Any] = {
        "envelope_identity": envelope_id,
        "source": "synthetic",
        "source_sequence": source_sequence,
        "event_time": event_time,
        "arrival_time": "2026-09-05T00:00:00Z",
        "capture_version": "synthetic-v0",
        "signal": signal,
    }
    if missingness is not None:
        result["missingness"] = missingness
    if amendment is not None:
        result["amendment"] = amendment
    return result


def ordering_conflict_envelopes() -> list[dict[str, Any]]:
    return [
        envelope("env-order-b", "sig-order-b", "2026-09-05T00:00:02Z", 2, {"opaque": "B"}),
        envelope("env-order-a", "sig-order-a", "2026-09-05T00:00:01Z", 1, {"opaque": "A"}),
    ]


def identity_collision_envelopes() -> list[dict[str, Any]]:
    return [
        envelope("env-dup", "sig-dup-a", "2026-09-05T00:01:00Z", 1, {"attempt": 1}),
        envelope("env-dup", "sig-dup-b", "2026-09-05T00:01:01Z", 2, {"attempt": 2}),
    ]


def preservation_envelope() -> dict[str, Any]:
    return envelope(
        "env-preserve",
        "sig-preserve",
        "2026-09-05T00:02:00Z",
        7,
        {
            "opaque": {"z": [3, 2, 1], "a": "kept"},
            "explicit_null": None,
            "unusual": ["", 0, False, "unicode-check"],
        },
        missingness={"payload.absent_field": "absent"},
    )


def missingness_envelopes() -> list[dict[str, Any]]:
    return [
        envelope("env-missing-absent", "sig-missing-absent", None, 1, {}, missingness={"time": "absent"}),
        envelope(
            "env-missing-null",
            "sig-missing-null",
            None,
            2,
            {"value": None},
            missingness={"payload.value": "explicit_null"},
        ),
        envelope(
            "env-missing-unavailable",
            "sig-missing-unavailable",
            None,
            3,
            {"value": {"state": "unavailable"}},
            missingness={"payload.value": "unavailable"},
        ),
        envelope(
            "env-missing-malformed",
            "sig-missing-malformed",
            None,
            4,
            {"value": "not-a-timestamp"},
            missingness={"payload.value": "malformed"},
        ),
    ]


def amendment_pair() -> list[dict[str, Any]]:
    original = envelope("env-amend-original", "sig-amend", "2026-09-05T00:03:00Z", 1, {"value": "original"})
    amendment = envelope(
        "env-amend-later",
        "sig-amend-note",
        "2026-09-05T00:03:01Z",
        2,
        {"value": "later note"},
        amendment={"relation": "corrects", "target_record_id": "rec-000001"},
    )
    return [original, deepcopy(amendment)]

