"""Specimen-local materialization of already-declared initial authority.

FIXTURE MATERIALIZATION != AUTHORITY GRANT.

The caller supplies an upstream authority declaration. This module performs only
structural validation and exact local state materialization; it does not decide
whether the declaration is warranted or authorized.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .stop_latch import ACTIVE, SCHEMA_VERSION

DECLARATION_SCHEMA_VERSION = "execution_stop_latch_initial_authority_v0"


class InitialAuthorityMaterializationError(RuntimeError):
    """Raised when the bounded fixture cannot materialize the supplied declaration."""


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def materialize_declared_initial_authority(
    store_root: Path, declaration: dict[str, Any]
) -> Path:
    """Materialize exact ACTIVE(E) bytes from an upstream declaration once."""
    required = {"schema_version", "execution_envelope_id", "declared_state"}
    if set(declaration) != required:
        raise InitialAuthorityMaterializationError(
            "unexpected initial-authority declaration fields"
        )
    if declaration.get("schema_version") != DECLARATION_SCHEMA_VERSION:
        raise InitialAuthorityMaterializationError(
            "unexpected initial-authority declaration schema"
        )
    execution_envelope_id = declaration.get("execution_envelope_id")
    if not isinstance(execution_envelope_id, str) or not execution_envelope_id.strip():
        raise InitialAuthorityMaterializationError(
            "execution_envelope_id must be a non-empty string"
        )
    if declaration.get("declared_state") != ACTIVE:
        raise InitialAuthorityMaterializationError(
            "bounded specimen requires an upstream declaration of ACTIVE"
        )

    identity_key = hashlib.sha256(execution_envelope_id.encode("utf-8")).hexdigest()
    state_path = Path(store_root) / "execution_envelopes" / f"{identity_key}.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "schema_version": SCHEMA_VERSION,
        "execution_envelope_id": execution_envelope_id,
        "state": ACTIVE,
    }
    try:
        fd = os.open(state_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise InitialAuthorityMaterializationError(
            "execution-envelope state already materialized"
        ) from exc

    with os.fdopen(fd, "wb") as fh:
        fh.write(_canonical_bytes(state))
        fh.flush()
        os.fsync(fh.fileno())
    return state_path
