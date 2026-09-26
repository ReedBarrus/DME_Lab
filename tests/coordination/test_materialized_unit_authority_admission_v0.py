from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.coordination import workcycle_v0 as wc
from src.coordination.materialized_unit_authority_admission_v0 import (
    materialized_unit_authority_coordinates,
    try_materialized_unit_verified_authority_atomic_admission,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    build_successor_work_spec,
    materialize_successor_work_unit,
)
from src.runtime.local_authority_consumption_v0 import (
    LocalAuthorityStateStore,
    consume_authority_once,
)
from tests.coordination.test_successor_work_unit_materialization_v0 import (
    partial_successor,
    work_spec,
)
from tests.coordination.test_verified_authority_admission_v0 import control_on


def alternate_spec(candidate: dict) -> dict:
    return build_successor_work_spec(
        successor_candidate=candidate,
        evidence_refs=["fixture://reconciliation", "fixture://remaining-gap"],
        desired_consequence="The remaining source-supported obstruction is resolved.",
        relevance_question="Would alternate bounded work resolve the exact remaining obstruction?",
        pressure_id="P-SUCCESSOR-WORK-AUTH-ALT-001",
        target_distinction_lhs="REMAINING_OBSTRUCTION",
        target_distinction_rhs="RESOLVED_OBSTRUCTION",
        selection_basis="Fresh reconciliation leaves one exact load-bearing gap.",
        expected_information_gain="Whether alternate bounded work resolves the same exact gap.",
        application_dependency="A qualified result must exist before any application.",
        priority_basis="BLOCKS_METABOLIC_CONTINUATION",
        load_bearing_effects=["BASIS", "OBSERVABILITY"],
        allowed_operations=["OBSERVE", "COMPARE"],
        prohibited_operations=["GRANT_AUTHORITY", "EXECUTE", "SELF_PROMOTE"],
        success_condition="One alternate bounded result addresses the exact remaining obstruction.",
        failure_condition="The alternate work widens scope.",
        unresolved_condition="Evidence remains insufficient.",
        max_rounds=1,
        max_branch_count=1,
        max_unresolved_children=0,
        application_required=True,
        target_surface="DISPOSABLE_FIXTURE",
        proposed_change="Apply one alternate bounded candidate transformation.",
        expected_effect="The remaining obstruction becomes independently observable.",
        operating_change="The exact remaining load-bearing obstruction changes posture.",
    )


def materialized_pair():
    successor = partial_successor()
    spec_a = work_spec(successor)
    spec_b = alternate_spec(successor)
    unit_a = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec_a,
    )
    unit_b = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec_b,
    )
    return successor, spec_a, unit_a, spec_b, unit_b


def envelope_for(
    successor: dict,
    spec: dict,
    unit: dict,
    capability: str = "CAP.MATERIALIZED.EXACT.001",
) -> dict:
    coordinates = materialized_unit_authority_coordinates(
        successor_candidate=successor,
        work_spec=spec,
        materialized_unit=unit,
    )
    return {
        "object_type": "LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0",
        "capability_id": capability,
        "approval_id": capability.replace("CAP", "APP", 1),
        "principal_id": "CODEX_PRINCIPAL_001",
        "request_sha256": coordinates["request_sha256"],
        "input_sha256": coordinates["input_sha256"],
        "model": "fixture/not-a-model",
        "endpoint_identity": "disposable-fixture-endpoint",
        "executor_sha256": "3" * 64,
        "policy_sha256": "4" * 64,
        "use_limit": 1,
        "remaining_uses": 1,
        "status": "ACTIVE",
        "issued_at": "2026-09-26T00:00:00Z",
        "expires_at": None,
    }


def attempt(
    *,
    root: Path,
    authority_store: LocalAuthorityStateStore,
    env: dict,
    successor: dict,
    spec: dict,
    unit: dict,
    attempt_id: str,
) -> dict:
    return try_materialized_unit_verified_authority_atomic_admission(
        store_dir=root / "atomic",
        authority_store=authority_store,
        authority_envelope=env,
        attempting_principal_id="CODEX_PRINCIPAL_001",
        successor_candidate=successor,
        work_spec=spec,
        materialized_unit=unit,
        work_attempt_id=attempt_id,
        seat_id="LABBOIB",
        occupant_id=f"occupant-{attempt_id}",
        wake_generation=1,
        dependency_satisfied=True,
        frame_current=True,
        no_hold=True,
        control=control_on(),
        initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
    )


class MaterializedUnitAuthorityAdmissionV0Tests(unittest.TestCase):
    def test_exact_materialized_work_authority_admits_and_binds_receipt(self):
        successor, spec_a, unit_a, _, _ = materialized_pair()
        env = envelope_for(successor, spec_a, unit_a)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalAuthorityStateStore(root / "authority")
            before = store.issue(env)
            result = attempt(
                root=root,
                authority_store=store,
                env=env,
                successor=successor,
                spec=spec_a,
                unit=unit_a,
                attempt_id="EXACT-A",
            )
            after = store.read(env["capability_id"])

        self.assertTrue(result["admitted"])
        receipt = result["receipt"]
        self.assertEqual(receipt["successor_id"], successor["successor_id"])
        self.assertEqual(
            receipt["materialized_unit_integrity_sha256"],
            unit_a["integrity_sha256"],
        )
        self.assertEqual(receipt["work_spec_id"], spec_a["work_spec_id"])
        self.assertEqual(
            receipt["work_spec_integrity_sha256"],
            spec_a["integrity_sha256"],
        )
        self.assertEqual(
            receipt["authority_input_sha256"],
            unit_a["integrity_sha256"],
        )
        self.assertFalse(receipt["authority_consumed"])
        self.assertEqual(before, after)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["execution_effect"], "NONE")

    def test_same_successor_different_materialized_unit_fails_closed(self):
        successor, spec_a, unit_a, spec_b, unit_b = materialized_pair()
        coords_a = materialized_unit_authority_coordinates(
            successor_candidate=successor,
            work_spec=spec_a,
            materialized_unit=unit_a,
        )
        coords_b = materialized_unit_authority_coordinates(
            successor_candidate=successor,
            work_spec=spec_b,
            materialized_unit=unit_b,
        )
        self.assertNotEqual(coords_a, coords_b)

        env = envelope_for(successor, spec_a, unit_a)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            result = attempt(
                root=root,
                authority_store=store,
                env=env,
                successor=successor,
                spec=spec_b,
                unit=unit_b,
                attempt_id="WRONG-MATERIALIZATION",
            )

        self.assertFalse(result["admitted"])
        self.assertIn(
            "authority_request_materialized_work_mismatch",
            result["blockers"],
        )

    def test_same_unit_with_wrong_work_spec_fails_before_admission(self):
        successor, spec_a, unit_a, spec_b, _ = materialized_pair()
        env = envelope_for(successor, spec_a, unit_a)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            result = attempt(
                root=root,
                authority_store=store,
                env=env,
                successor=successor,
                spec=spec_b,
                unit=unit_a,
                attempt_id="WRONG-SPEC",
            )

        self.assertFalse(result["admitted"])
        self.assertEqual(result["blockers"], ["materialized_work_binding_invalid"])
        self.assertFalse((root / "atomic" / "atomic_admission_state.json").exists())

    def test_tampered_materialized_unit_fails_before_admission(self):
        successor, spec_a, unit_a, _, _ = materialized_pair()
        env = envelope_for(successor, spec_a, unit_a)
        tampered = copy.deepcopy(unit_a)
        tampered["application"]["target_surface"] = "TAMPERED"
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            result = attempt(
                root=root,
                authority_store=store,
                env=env,
                successor=successor,
                spec=spec_a,
                unit=tampered,
                attempt_id="TAMPERED-UNIT",
            )

        self.assertFalse(result["admitted"])
        self.assertEqual(result["blockers"], ["materialized_work_binding_invalid"])
        self.assertFalse((root / "atomic" / "atomic_admission_state.json").exists())

    def test_consumed_exact_authority_fails_before_admission(self):
        successor, spec_a, unit_a, _, _ = materialized_pair()
        env = envelope_for(successor, spec_a, unit_a)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            ticks = iter([
                "2026-09-26T00:00:01Z",
                "2026-09-26T00:00:02Z",
            ])
            consume_authority_once(
                env,
                attempting_principal_id="CODEX_PRINCIPAL_001",
                store=store,
                invoke=lambda: {"ok": True},
                clock=lambda: next(ticks),
            )
            result = attempt(
                root=root,
                authority_store=store,
                env=env,
                successor=successor,
                spec=spec_a,
                unit=unit_a,
                attempt_id="CONSUMED-EXACT",
            )

        self.assertFalse(result["admitted"])
        self.assertEqual(result["blockers"], ["authority_verification_failed"])

    def test_two_same_process_callers_still_produce_one_exact_admission(self):
        successor, spec_a, unit_a, _, _ = materialized_pair()
        env = envelope_for(successor, spec_a, unit_a)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = LocalAuthorityStateStore(root / "authority")
            store.issue(env)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(
                    pool.map(
                        lambda attempt_id: attempt(
                            root=root,
                            authority_store=store,
                            env=env,
                            successor=successor,
                            spec=spec_a,
                            unit=unit_a,
                            attempt_id=attempt_id,
                        ),
                        ["EXACT-RACE-A", "EXACT-RACE-B"],
                    )
                )

        admitted = [item for item in results if item["admitted"]]
        blocked = [item for item in results if not item["admitted"]]
        self.assertEqual(len(admitted), 1)
        self.assertEqual(len(blocked), 1)
        self.assertIn("active_admission", blocked[0]["blockers"])
        self.assertEqual(
            admitted[0]["receipt"]["materialized_unit_integrity_sha256"],
            unit_a["integrity_sha256"],
        )
        self.assertEqual(
            admitted[0]["receipt"]["work_spec_id"],
            spec_a["work_spec_id"],
        )


if __name__ == "__main__":
    unittest.main()
