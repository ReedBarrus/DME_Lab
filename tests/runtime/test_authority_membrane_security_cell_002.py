from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.runtime.local_authority_consumption_v0 import (
    ACTIVE,
    CONSUMED,
    DENIAL_TYPE,
    ENVELOPE_TYPE,
    NONE,
    PRINCIPAL_DENIAL_TYPE,
    RECEIPT_TYPE,
    RESERVATION_TYPE,
    AuthorityEnvelopeError,
    LocalAuthorityStateStore,
    consume_authority_once,
    default_authority_state_root,
    validate_authority_envelope,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class AuthorityMembraneSecurityCell002Test(unittest.TestCase):
    def setUp(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.state_root = Path(temporary.name) / "authority_state_v0"
        self.store = LocalAuthorityStateStore(self.state_root)
        self.approve = mock.Mock(return_value=True)
        self.envelope = {
            "object_type": ENVELOPE_TYPE,
            "capability_id": "AUTHORITY_MEMBRANE_CELL_002_CAPABILITY_001",
            "approval_id": "AUTHORITY_MEMBRANE_CELL_002_APPROVAL_001",
            "principal_id": "CODEX_PRINCIPAL_001",
            "request_sha256": sha256(b"exact request identity"),
            "input_sha256": sha256(b"exact prompt bytes"),
            "model": "qwen/qwen3-coder-30b",
            "endpoint_identity": "http://127.0.0.1:1234/v1/chat/completions",
            "executor_sha256": sha256(
                (
                    repository_root
                    / "src"
                    / "runtime"
                    / "local_authority_consumption_v0.py"
                ).read_bytes()
            ),
            "policy_sha256": sha256(
                (repository_root / "bridge" / "policy_v0.json").read_bytes()
            ),
            "use_limit": 1,
            "remaining_uses": 1,
            "status": ACTIVE,
            "issued_at": "2026-09-22T18:00:00+00:00",
            "expires_at": None,
        }
        exact_consequence = {
            key: self.envelope[key]
            for key in (
                "request_sha256",
                "input_sha256",
                "principal_id",
                "model",
                "endpoint_identity",
                "executor_sha256",
                "policy_sha256",
            )
        }
        self.assertTrue(self.approve(exact_consequence))
        self.store.issue(self.envelope)

    @staticmethod
    def clock(*values: str):
        retained = iter(values)
        return lambda: next(retained)

    def test_default_state_root_is_outside_the_repository_trust_surface(self) -> None:
        expected = Path.home() / ".dme_lab_bridge" / "authority_state_v0"
        self.assertEqual(default_authority_state_root(), expected)

    def test_issued_and_attempting_principal_use_bounded_identity_syntax(self) -> None:
        malformed_envelope = dict(self.envelope)
        malformed_envelope["principal_id"] = "invalid principal"
        with self.assertRaises(AuthorityEnvelopeError):
            validate_authority_envelope(malformed_envelope)

        invoke_lmstudio = mock.Mock()
        with self.assertRaises(AuthorityEnvelopeError):
            consume_authority_once(
                self.envelope,
                attempting_principal_id="invalid principal",
                store=self.store,
                invoke=invoke_lmstudio,
                clock=self.clock(),
            )
        invoke_lmstudio.assert_not_called()

    def test_control_consumes_before_one_invocation_and_persists_receipt(self) -> None:
        invoke_lmstudio = mock.Mock(return_value={"assistant_text": "CONTROL_OK"})
        result = consume_authority_once(
            self.envelope,
            attempting_principal_id=self.envelope["principal_id"],
            store=self.store,
            invoke=invoke_lmstudio,
            clock=self.clock(
                "2026-09-22T18:00:01+00:00",
                "2026-09-22T18:00:02+00:00",
            ),
        )

        invoke_lmstudio.assert_called_once_with()
        self.assertEqual(result["decision"], "INVOKED")
        receipt = result["receipt"]
        self.assertEqual(receipt["object_type"], RECEIPT_TYPE)
        self.assertEqual(receipt["principal_id"], self.envelope["principal_id"])
        self.assertEqual(receipt["pre_use_remaining_uses"], 1)
        self.assertEqual(receipt["post_use_remaining_uses"], 0)
        self.assertEqual(receipt["invocation_count"], 1)
        self.assertEqual(receipt["status"], CONSUMED)
        self.assertEqual(receipt["current_authority"], NONE)

        retained = self.store.read(self.envelope["capability_id"])
        self.assertEqual(
            retained["history"][0]["principal_id"], self.envelope["principal_id"]
        )
        self.assertEqual(
            retained["history"][1]["principal_id"], self.envelope["principal_id"]
        )
        self.assertEqual(retained["envelope"]["remaining_uses"], 0)
        self.assertEqual(retained["envelope"]["status"], CONSUMED)
        self.assertEqual(retained["history"][-1], receipt)
        self.assertTrue(self.store.state_path(self.envelope["capability_id"]).exists())

    def test_replay_is_denied_and_historical_receipt_remains_readable(self) -> None:
        first_invoke = mock.Mock(return_value={"assistant_text": "CONTROL_OK"})
        first = consume_authority_once(
            self.envelope,
            attempting_principal_id=self.envelope["principal_id"],
            store=self.store,
            invoke=first_invoke,
            clock=self.clock(
                "2026-09-22T18:00:01+00:00",
                "2026-09-22T18:00:02+00:00",
            ),
        )
        first_invoke.assert_called_once_with()

        replay_invoke = mock.Mock(side_effect=AssertionError("replay crossed boundary"))
        replay = consume_authority_once(
            self.envelope,
            attempting_principal_id=self.envelope["principal_id"],
            store=self.store,
            invoke=replay_invoke,
            clock=self.clock("2026-09-22T18:00:03+00:00"),
        )

        replay_invoke.assert_not_called()
        self.assertEqual(replay["decision"], "DENY")
        denial = replay["witness"]
        self.assertEqual(denial["object_type"], DENIAL_TYPE)
        self.assertEqual(denial["principal_id"], self.envelope["principal_id"])
        self.assertEqual(
            denial["attempting_principal_id"], self.envelope["principal_id"]
        )
        self.assertEqual(denial["reason"], "AUTHORITY_EXHAUSTED")
        self.assertEqual(denial["pre_use_remaining_uses"], 0)
        self.assertEqual(denial["post_use_remaining_uses"], 0)
        self.assertEqual(denial["invocation_count"], 0)
        self.assertFalse(denial["lmstudio_invoked"])
        self.assertEqual(denial["current_authority"], NONE)
        self.assertEqual(
            denial["historical_consumption_receipt_id"],
            first["receipt"]["receipt_id"],
        )

        retained = self.store.read(self.envelope["capability_id"])
        receipts = [
            record
            for record in retained["history"]
            if record.get("object_type") == RECEIPT_TYPE
        ]
        denials = [
            record
            for record in retained["history"]
            if record.get("object_type") == DENIAL_TYPE
        ]
        self.assertEqual(receipts, [first["receipt"]])
        self.assertEqual(denials, [denial])
        self.assertEqual(retained["envelope"]["remaining_uses"], 0)
        self.assertEqual(retained["envelope"]["status"], CONSUMED)

    def test_wrong_principal_is_denied_before_reservation_without_consumption(self) -> None:
        invoke_lmstudio = mock.Mock(
            side_effect=AssertionError("wrong principal crossed boundary")
        )
        result = consume_authority_once(
            self.envelope,
            attempting_principal_id="CODEX_PRINCIPAL_002",
            store=self.store,
            invoke=invoke_lmstudio,
            clock=self.clock("2026-09-22T18:00:01+00:00"),
        )

        self.approve.assert_called_once()
        invoke_lmstudio.assert_not_called()
        self.assertEqual(result["decision"], "DENY")
        denial = result["witness"]
        self.assertEqual(denial["object_type"], PRINCIPAL_DENIAL_TYPE)
        self.assertEqual(
            denial["capability_id"], self.envelope["capability_id"]
        )
        self.assertEqual(denial["approval_id"], self.envelope["approval_id"])
        self.assertEqual(
            denial["issued_principal_id"], self.envelope["principal_id"]
        )
        self.assertEqual(denial["attempting_principal_id"], "CODEX_PRINCIPAL_002")
        self.assertEqual(denial["remaining_uses_before"], 1)
        self.assertEqual(denial["remaining_uses_after"], 1)
        self.assertEqual(denial["status_before"], ACTIVE)
        self.assertEqual(denial["status_after"], ACTIVE)
        self.assertEqual(denial["decision"], "DENY")
        self.assertEqual(denial["reason"], "PRINCIPAL_MISMATCH")
        self.assertFalse(denial["lmstudio_invoked"])
        self.assertEqual(denial["invocation_count"], 0)
        self.assertEqual(
            denial["executor_sha256"], self.envelope["executor_sha256"]
        )
        self.assertEqual(denial["policy_sha256"], self.envelope["policy_sha256"])

        retained = self.store.read(self.envelope["capability_id"])
        self.assertEqual(retained["envelope"]["remaining_uses"], 1)
        self.assertEqual(retained["envelope"]["status"], ACTIVE)
        reservations = [
            record
            for record in retained["history"]
            if record.get("object_type") == RESERVATION_TYPE
        ]
        self.assertEqual(reservations, [])


if __name__ == "__main__":
    unittest.main()
