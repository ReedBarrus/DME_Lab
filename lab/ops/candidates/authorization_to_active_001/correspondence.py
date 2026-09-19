"""Exact bounded correspondence for AUTHORIZATION_TO_ACTIVE_001."""
from __future__ import annotations

from typing import Any

LIVE = "LIVE"


class AuthorizationShapeError(ValueError):
    """Raised when raw experimental inputs do not match the frozen specimen shape."""


def _require_exact_fields(value: dict[str, Any], required: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != required:
        raise AuthorizationShapeError(f"unexpected {label} fields")


def validate_execution_envelope(envelope: dict[str, Any]) -> None:
    _require_exact_fields(
        envelope,
        {"execution_envelope_id", "implementation_basis", "requested_consequence"},
        "execution-envelope",
    )
    for key in ("execution_envelope_id", "implementation_basis", "requested_consequence"):
        if not isinstance(envelope[key], str) or not envelope[key]:
            raise AuthorizationShapeError(f"{key} must be a non-empty string")


def validate_authorization(authorization: dict[str, Any]) -> None:
    _require_exact_fields(
        authorization,
        {"execution_envelope_id", "implementation_basis", "allowed_consequences", "status"},
        "authorization",
    )
    for key in ("execution_envelope_id", "implementation_basis", "status"):
        if not isinstance(authorization[key], str) or not authorization[key]:
            raise AuthorizationShapeError(f"authorization {key} must be a non-empty string")
    allowed = authorization["allowed_consequences"]
    if not isinstance(allowed, list) or not allowed:
        raise AuthorizationShapeError("allowed_consequences must be a non-empty list")
    if any(not isinstance(item, str) or not item for item in allowed):
        raise AuthorizationShapeError("allowed_consequences entries must be non-empty strings")
    if len(set(allowed)) != len(allowed):
        raise AuthorizationShapeError("allowed_consequences must not contain duplicates")


def corresponds(
    authorization: dict[str, Any] | None,
    envelope: dict[str, Any],
) -> bool:
    """Derive exact AO↔E correspondence from raw inputs; never consume a validity flag."""
    validate_execution_envelope(envelope)
    if authorization is None:
        return False
    validate_authorization(authorization)
    return (
        authorization["execution_envelope_id"] == envelope["execution_envelope_id"]
        and authorization["implementation_basis"] == envelope["implementation_basis"]
        and envelope["requested_consequence"] in authorization["allowed_consequences"]
        and authorization["status"] == LIVE
    )
