from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.coordination import workcycle_v0 as wc
from src.coordination.materialized_admitted_authority_consumption_v0 import (
    consume_materialized_admitted_authority_once,
)
from src.coordination.materialized_unit_authority_admission_v0 import (
    try_materialized_unit_verified_authority_atomic_admission,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    materialize_successor_work_unit,
)
from src.runtime.local_authority_consumption_v0 import (
    AuthorityInvocationError,
    LocalAuthorityStateStore,
)
from tests.coordination.test_materialized_unit_authority_admission_v0 import (
    alternate_spec,
    envelope_for,
)
from tests.coordination.test_successor_work_unit_materialization_v0 import (
    partial_successor,
    work_spec,
)
from tests.coordination.test_verified_authority_admission_v0 import control_on


def exact_fixture(root: Path):
    successor = partial_successor()
    spec = work_spec(successor)
    unit = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec,
    )
    env = envelope_for(
        successor,
        spec,
        unit,
        capability="CAP.MATERIALIZED.CONSUME.001",
    )
    store = LocalAuthorityStateStore(root / "authority")
    store.issue(env)
    decision = try_materialized_unit_verified_authority_atomic_admission(
        store_dir=root / "atomic",
        authority_store=store,
        authority_envelope=env,
        attempting_principal_id="CODEX_PRINCIPAL_001",
        successor_candidate=successor,
        work_spec=spec,
        materialized_unit=unit,
        work_attempt_id="ATTEMPT-MATERIALIZED-CONSUME-001",
        seat_id="LABBOIB",
        occupant_id="occupant-materialized-consume",
        wake_generation=1,
        dependency_satisfied=True,
        frame_current=True,
        no_hold=True,
        control=control_on(),
        initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
    )
    if decision["admitted"] is not True:
        raise AssertionError(f"exact admission fixture failed: {decision}")
    return successor, spec, unit, env, store, decision["receipt"]


class MaterializedAdmittedAuthorityConsumptionV0Tests(unittest.TestCase):
    def test_exact_materialized_work_consumes_once_and_invokes_once(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            successor, spec, unit, env, store, admission = exact_fixture(root)
            calls: list[str] = []
            ticks = iter([
                "2026-09-26T00:30:01Z",
                "2026-09-26T00:30:02Z",
            ])
            result = consume_materialized_admitted_authority_once(
                admission_receipt=admission,
                successor_candidate=successor,
                work_spec=spec,
                materialized_unit=unit,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("invoked") or {"fixture": "ok"},
                clock=lambda: next(ticks),
            )
            after = store.read(env["capability_id"])

        self.assertTrue(result["consumed"])
        self.assertTrue(result["invocation_performed"])
        self.assertEqual(calls, ["invoked"])
        self.assertEqual(result["invocation_result"], {"fixture": "ok"})
        receipt = result["receipt"]
        self.assertEqual(receipt["successor_id"], successor["successor_id"])
        self.assertEqual(receipt["work_spec_id"], spec["work_spec_id"])
        self.assertEqual(
            receipt["materialized_unit_integrity_sha256"],
            unit["integrity_sha256"],
        )
        self.assertEqual(receipt["authority_status_after"], "CONSUMED")
        self.assertEqual(receipt["authority_remaining_uses_after"], 0)
        self.assertEqual(receipt["execution_effect"], "NONE")
        self.assertEqual(after["envelope"]["status"], "CONSUMED")
        self.assertEqual(after["envelope"]["remaining_uses"], 0)

    def test_replay_is_denied_without_second_callback(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            successor, spec, unit, env, store, admission = exact_fixture(root)
            calls: list[str] = []
            ticks = iter([
                "2026-09-26T00:30:01Z",
                "2026-09-26T00:30:02Z",
            ])
            first = consume_materialized_admitted_authority_once(
                admission_receipt=admission,
                successor_candidate=successor,
                work_spec=spec,
                materialized_unit=unit,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("first") or {"ok": True},
                clock=lambda: next(ticks),
            )
            second = consume_materialized_admitted_authority_once(
                admission_receipt=admission,
                successor_candidate=successor,
                work_spec=spec,
                materialized_unit=unit,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("second") or {"bad": True},
                clock=lambda: "2026-09-26T00:30:03Z",
            )

        self.assertTrue(first["consumed"])
        self.assertFalse(second["consumed"])
        self.assertEqual(second["blockers"], ["authority_verification_failed"])
        self.assertEqual(calls, ["first"])

    def test_wrong_materialized_unit_is_blocked_before_consumption(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            successor, spec_a, unit_a, env, store, admission = exact_fixture(root)
            spec_b = alternate_spec(successor)
            unit_b = materialize_successor_work_unit(
                successor_candidate=successor,
                work_spec=spec_b,
            )
            calls: list[str] = []
            result = consume_materialized_admitted_authority_once(
                admission_receipt=admission,
                successor_candidate=successor,
                work_spec=spec_b,
                materialized_unit=unit_b,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("wrong"),
                clock=lambda: "2026-09-26T00:30:01Z",
            )
            after = store.read(env["capability_id"])

        self.assertFalse(result["consumed"])
        self.assertIn(
            result["blockers"][0],
            {
                "admission_materialized_unit_integrity_sha256_mismatch",
                "admission_work_spec_id_mismatch",
                "admission_work_spec_integrity_sha256_mismatch",
            },
        )
        self.assertEqual(calls, [])
        self.assertEqual(after["envelope"]["status"], "ACTIVE")
        self.assertEqual(after["envelope"]["remaining_uses"], 1)

    def test_tampered_exact_admission_receipt_is_blocked(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            successor, spec, unit, env, store, admission = exact_fixture(root)
            tampered = dict(admission)
            tampered["work_spec_id"] = "successor-work-spec:sha256:" + "9" * 64
            calls: list[str] = []
            result = consume_materialized_admitted_authority_once(
                admission_receipt=tampered,
                successor_candidate=successor,
                work_spec=spec,
                materialized_unit=unit,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("tampered"),
                clock=lambda: "2026-09-26T00:30:01Z",
            )
            after = store.read(env["capability_id"])

        self.assertFalse(result["consumed"])
        self.assertEqual(result["blockers"], ["admission_or_materialized_work_invalid"])
        self.assertEqual(calls, [])
        self.assertEqual(after["envelope"]["status"], "ACTIVE")

    def test_post_reservation_failure_enters_recovery_required(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            successor, spec, unit, env, store, admission = exact_fixture(root)
            calls: list[str] = []
            ticks = iter([
                "2026-09-26T00:30:01Z",
                "2026-09-26T00:30:02Z",
            ])

            def fail():
                calls.append("failed-once")
                raise RuntimeError("fixture failure")

            with self.assertRaises(AuthorityInvocationError):
                consume_materialized_admitted_authority_once(
                    admission_receipt=admission,
                    successor_candidate=successor,
                    work_spec=spec,
                    materialized_unit=unit,
                    authority_envelope=env,
                    attempting_principal_id="CODEX_PRINCIPAL_001",
                    authority_store=store,
                    invoke=fail,
                    clock=lambda: next(ticks),
                )

            after_failure = store.read(env["capability_id"])
            retry = consume_materialized_admitted_authority_once(
                admission_receipt=admission,
                successor_candidate=successor,
                work_spec=spec,
                materialized_unit=unit,
                authority_envelope=env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                authority_store=store,
                invoke=lambda: calls.append("illegal-retry"),
                clock=lambda: "2026-09-26T00:30:03Z",
            )

        self.assertEqual(after_failure["envelope"]["status"], "RECOVERY_REQUIRED")
        self.assertEqual(after_failure["envelope"]["remaining_uses"], 0)
        self.assertFalse(retry["consumed"])
        self.assertEqual(retry["blockers"], ["authority_verification_failed"])
        self.assertEqual(calls, ["failed-once"])


if __name__ == "__main__":
    unittest.main()
