"""Read-only current-authority binding for bounded workcycle coordination.

This module verifies one exact authority envelope against the current
trust-root-owned LocalAuthorityStateStore without consuming authority.

It creates no authority, performs no invocation, and does not mutate the
authority store.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.runtime.local_authority_consumption_v0 import (
    ACTIVE,
    AUTHORITY_ENVELOPE_KEYS,
    ENVELOPE_TYPE,
    LocalAuthorityStateStore,
    AuthorityEnvelopeError,
    AuthorityStateError,
    canonical_sha256,
    validate_authority_envelope,
)


BINDING_TYPE = "CURRENT_AUTHORITY_BINDING_V0"
VERIFIED = "VERIFIED_CURRENT_ACTIVE_ONE_USE"


class AuthorityBindingError(RuntimeError):
    pass


_IMMUTABLE_FIELDS = (
    "capability_id",
    "approval_id",
    "principal_id",
    "request_sha256",
    "input_sha256",
    "model",
    "endpoint_identity",
    "executor_sha256",
    "policy_sha256",
    "use_limit",
    "issued_at",
    "expires_at",
)


def verify_current_authority(
    *,
    envelope: Mapping[str, Any],
    attempting_principal_id: str,
    store: LocalAuthorityStateStore,
) -> dict[str, Any]:
    """Verify that one exact issued authority envelope is current and usable.

    This function is read-only with respect to the authority store.
    """

    try:
        retained = validate_authority_envelope(envelope)
    except AuthorityEnvelopeError as exc:
        raise AuthorityBindingError(f"authority envelope invalid: {exc}") from exc

    capability_id = retained["capability_id"]
    if attempting_principal_id != retained["principal_id"]:
        raise AuthorityBindingError("attempting principal does not match envelope principal")

    try:
        state = store.read(capability_id)
    except AuthorityStateError as exc:
        raise AuthorityBindingError(f"authority state unavailable: {exc}") from exc

    current = state.get("envelope")
    if not isinstance(current, dict):
        raise AuthorityBindingError("current authority envelope missing")
    if set(current) != AUTHORITY_ENVELOPE_KEYS:
        raise AuthorityBindingError("current authority envelope has exact-key mismatch")
    if current.get("object_type") != ENVELOPE_TYPE:
        raise AuthorityBindingError("current authority envelope type mismatch")

    issued_sha = canonical_sha256(retained)
    if state.get("issued_envelope_sha256") != issued_sha:
        raise AuthorityBindingError("supplied envelope differs from issued authority")

    for field in _IMMUTABLE_FIELDS:
        if current.get(field) != retained.get(field):
            raise AuthorityBindingError(f"current authority field mismatch: {field}")

    if current.get("status") != ACTIVE:
        raise AuthorityBindingError(
            f"current authority is not ACTIVE: {current.get('status')}"
        )
    if current.get("remaining_uses") != 1:
        raise AuthorityBindingError(
            f"current authority remaining_uses is {current.get('remaining_uses')}"
        )

    state_identity = canonical_sha256(state)
    binding_basis = {
        "object_type": BINDING_TYPE,
        "verification_posture": VERIFIED,
        "capability_id": current["capability_id"],
        "approval_id": current["approval_id"],
        "principal_id": current["principal_id"],
        "request_sha256": current["request_sha256"],
        "input_sha256": current["input_sha256"],
        "model": current["model"],
        "endpoint_identity": current["endpoint_identity"],
        "executor_sha256": current["executor_sha256"],
        "policy_sha256": current["policy_sha256"],
        "issued_envelope_sha256": issued_sha,
        "authority_state_sha256": state_identity,
        "remaining_uses": 1,
        "status": ACTIVE,
        "authority_source": "LOCAL_TRUST_ROOT_AUTHORITY_STATE",
        "authority_effect": "NONE",
        "consumption_effect": "NONE",
        "execution_effect": "NONE",
        "model_invocation_effect": "NONE",
    }
    binding = copy.deepcopy(binding_basis)
    binding["binding_id"] = (
        "current-authority-binding:sha256:"
        + canonical_sha256(binding_basis)
    )
    binding["claim_ceiling"] = (
        "Read-only verification that one exact locally issued authority envelope "
        "is currently ACTIVE with one remaining use for the bound principal and "
        "request/input/model/executor/policy coordinates. This does not consume, "
        "grant, transfer, or extend authority and performs no invocation."
    )
    return binding
