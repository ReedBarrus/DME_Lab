#!/usr/bin/env python3
"""Observe read-only current-authority binding in disposable local state.

No real trust-root state is touched. No authority is granted. One temporary
authority is consumed only inside the disposable fixture to prove that consumed
authority no longer verifies as current.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination.authority_binding_v0 import (
    AuthorityBindingError,
    verify_current_authority,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    consume_authority_once,
)


OUT = ROOT / "authority_binding_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def envelope() -> dict:
    return {
        "object_type": "LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0",
        "capability_id": "CAP.OBS.001",
        "approval_id": "APP.OBS.001",
        "principal_id": "CODEX_PRINCIPAL_001",
        "request_sha256": "1" * 64,
        "input_sha256": "2" * 64,
        "model": "test/model",
        "endpoint_identity": "local-test-endpoint",
        "executor_sha256": "3" * 64,
        "policy_sha256": "4" * 64,
        "use_limit": 1,
        "remaining_uses": 1,
        "status": "ACTIVE",
        "issued_at": "2026-09-25T00:00:00Z",
        "expires_at": None,
    }


def blocked(label: str, fn) -> dict:
    try:
        fn()
    except AuthorityBindingError as exc:
        return {
            "label": label,
            "blocked": True,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    return {
        "label": label,
        "blocked": False,
        "error_type": None,
        "error": None,
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "authority_binding_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    with TemporaryDirectory() as tmp:
        store = LocalAuthorityStateStore(Path(tmp) / "fresh")
        env = envelope()
        issued = store.issue(env)
        before = store.read(env["capability_id"])
        binding = verify_current_authority(
            envelope=env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            store=store,
        )
        after = store.read(env["capability_id"])

        wrong_principal = blocked(
            "wrong_principal",
            lambda: verify_current_authority(
                envelope=env,
                attempting_principal_id="OTHER_PRINCIPAL_001",
                store=store,
            ),
        )

        altered = dict(env)
        altered["request_sha256"] = "9" * 64
        altered_envelope = blocked(
            "altered_envelope",
            lambda: verify_current_authority(
                envelope=altered,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                store=store,
            ),
        )

        consumed_store = LocalAuthorityStateStore(Path(tmp) / "consumed")
        consumed_env = envelope()
        consumed_env["capability_id"] = "CAP.OBS.002"
        consumed_env["approval_id"] = "APP.OBS.002"
        consumed_store.issue(consumed_env)
        ticks = iter([
            "2026-09-25T00:00:01Z",
            "2026-09-25T00:00:02Z",
        ])
        consume_authority_once(
            consumed_env,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            store=consumed_store,
            invoke=lambda: {"ok": True},
            clock=lambda: next(ticks),
        )
        consumed = blocked(
            "consumed_authority",
            lambda: verify_current_authority(
                envelope=consumed_env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                store=consumed_store,
            ),
        )

    assertions = {
        "fresh_exact_verified": binding["verification_posture"] == "VERIFIED_CURRENT_ACTIVE_ONE_USE",
        "fresh_remaining_uses_one": binding["remaining_uses"] == 1,
        "fresh_status_active": binding["status"] == "ACTIVE",
        "fresh_store_read_only": before == after == issued,
        "wrong_principal_blocked": wrong_principal["blocked"] is True,
        "altered_envelope_blocked": altered_envelope["blocked"] is True,
        "consumed_authority_blocked": consumed["blocked"] is True,
        "no_authority_effect": binding["authority_effect"] == "NONE",
        "no_consumption_effect": binding["consumption_effect"] == "NONE",
        "no_execution_effect": binding["execution_effect"] == "NONE",
        "no_model_invocation_effect": binding["model_invocation_effect"] == "NONE",
    }

    witness = {
        "object_type": "AUTHORITY_BINDING_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_LOCAL_AUTHORITY_STATE_FIXTURE",
        "verified_binding": binding,
        "wrong_principal_case": wrong_principal,
        "altered_envelope_case": altered_envelope,
        "consumed_authority_case": consumed,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Read-only verification of one exact authority envelope against the "
            "current single-process local authority state. This fixture does not "
            "grant, consume, transfer, extend, or invoke authority and does not "
            "establish cross-process authority-state atomicity."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(witness, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    print(f"[OK] all_assertions_pass {witness['all_assertions_pass']}")
    print(f"[OK] verification_posture {binding['verification_posture']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
