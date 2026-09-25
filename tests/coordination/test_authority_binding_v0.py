from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.coordination.authority_binding_v0 import (
    AuthorityBindingError,
    VERIFIED,
    verify_current_authority,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    consume_authority_once,
)


def envelope() -> dict:
    return {
        "object_type": "LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0",
        "capability_id": "CAP.TEST.001",
        "approval_id": "APP.TEST.001",
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


class AuthorityBindingV0Tests(unittest.TestCase):
    def test_fresh_exact_authority_is_verified_read_only(self):
        with TemporaryDirectory() as tmp:
            store = LocalAuthorityStateStore(Path(tmp))
            env = envelope()
            before = store.issue(env)
            binding = verify_current_authority(
                envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                store=store,
            )
            after = store.read(env["capability_id"])

        self.assertEqual(binding["verification_posture"], VERIFIED)
        self.assertEqual(binding["remaining_uses"], 1)
        self.assertEqual(binding["status"], "ACTIVE")
        self.assertEqual(binding["authority_effect"], "NONE")
        self.assertEqual(binding["consumption_effect"], "NONE")
        self.assertEqual(binding["model_invocation_effect"], "NONE")
        self.assertEqual(before, after)

    def test_wrong_principal_is_rejected(self):
        with TemporaryDirectory() as tmp:
            store = LocalAuthorityStateStore(Path(tmp))
            env = envelope()
            store.issue(env)
            with self.assertRaises(AuthorityBindingError):
                verify_current_authority(
                    envelope=env,
                    attempting_principal_id="OTHER_PRINCIPAL_001",
                    store=store,
                )

    def test_different_envelope_is_rejected(self):
        with TemporaryDirectory() as tmp:
            store = LocalAuthorityStateStore(Path(tmp))
            env = envelope()
            store.issue(env)
            altered = dict(env)
            altered["request_sha256"] = "9" * 64
            with self.assertRaises(AuthorityBindingError):
                verify_current_authority(
                    envelope=altered,
                    attempting_principal_id="CODEX_PRINCIPAL_001",
                    store=store,
                )

    def test_consumed_authority_is_not_current(self):
        with TemporaryDirectory() as tmp:
            store = LocalAuthorityStateStore(Path(tmp))
            env = envelope()
            store.issue(env)
            ticks = iter([
                "2026-09-25T00:00:01Z",
                "2026-09-25T00:00:02Z",
            ])
            consume_authority_once(
                env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                store=store,
                invoke=lambda: {"ok": True},
                clock=lambda: next(ticks),
            )
            with self.assertRaises(AuthorityBindingError):
                verify_current_authority(
                    envelope=env,
                    attempting_principal_id="CODEX_PRINCIPAL_001",
                    store=store,
                )


if __name__ == "__main__":
    unittest.main()
