#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination import workcycle_v0 as wc
from src.coordination.successor_work_unit_materialization_v0 import (
    build_successor_work_spec,
    materialize_successor_work_unit,
)
from src.coordination.verified_authority_admission_v0 import (
    successor_authority_coordinates,
    try_verified_authority_atomic_admission,
)
from src.runtime.local_authority_consumption_v0 import LocalAuthorityStateStore
from tests.coordination.test_successor_work_unit_materialization_v0 import (
    partial_successor,
    work_spec,
)
from tests.coordination.test_verified_authority_admission_v0 import control_on

OUT = ROOT / "materialized_unit_authority_binding_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def envelope_for(successor: dict, capability: str) -> dict:
    coordinates = successor_authority_coordinates(successor)
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


def alternate_spec(successor: dict) -> dict:
    return build_successor_work_spec(
        successor_candidate=successor,
        evidence_refs=["fixture://reconciliation", "fixture://remaining-gap"],
        desired_consequence="The remaining source-supported obstruction is resolved.",
        relevance_question="Would alternate work resolve the exact remaining obstruction?",
        pressure_id="P-SUCCESSOR-WORK-ALT-AUTH-001",
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


def admit(successor: dict, env: dict, root: Path, attempt_id: str) -> dict:
    store = LocalAuthorityStateStore(root / "authority")
    store.issue(env)
    return try_verified_authority_atomic_admission(
        store_dir=root / "atomic",
        authority_store=store,
        authority_envelope=env,
        attempting_principal_id="CODEX_PRINCIPAL_001",
        successor_candidate=successor,
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


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing materialized_unit_authority_binding_observation.json first"
        )

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

    coords = successor_authority_coordinates(successor)
    env = envelope_for(successor, "CAP.MATERIALIZED.AUTH.001")

    with TemporaryDirectory() as tmp_a, TemporaryDirectory() as tmp_b:
        admission_a = admit(
            successor,
            env,
            Path(tmp_a),
            "ATTEMPT-MATERIALIZED-A",
        )
        admission_b = admit(
            successor,
            env,
            Path(tmp_b),
            "ATTEMPT-MATERIALIZED-B",
        )

    receipt_a = admission_a.get("receipt") or {}
    receipt_b = admission_b.get("receipt") or {}

    observations = {
        "same_successor_id": (
            unit_a["identity"]["work_item_id"] == successor["successor_id"]
            and unit_b["identity"]["work_item_id"] == successor["successor_id"]
        ),
        "work_specs_differ": spec_a["work_spec_id"] != spec_b["work_spec_id"],
        "materialized_units_differ": (
            unit_a["integrity_sha256"] != unit_b["integrity_sha256"]
        ),
        "authority_coordinates_bind_successor_only": (
            coords["input_sha256"] == successor["integrity_sha256"]
        ),
        "authority_coordinates_do_not_bind_unit_a": (
            coords["input_sha256"] != unit_a["integrity_sha256"]
        ),
        "authority_coordinates_do_not_bind_unit_b": (
            coords["input_sha256"] != unit_b["integrity_sha256"]
        ),
        "authority_request_is_identical_for_both_materializations": True,
        "unit_a_admits_under_successor_bound_authority": admission_a.get("admitted") is True,
        "unit_b_admits_under_same_successor_bound_authority": admission_b.get("admitted") is True,
        "receipt_a_lacks_materialized_unit_identity": (
            "materialized_unit_integrity_sha256" not in receipt_a
            and "work_spec_id" not in receipt_a
        ),
        "receipt_b_lacks_materialized_unit_identity": (
            "materialized_unit_integrity_sha256" not in receipt_b
            and "work_spec_id" not in receipt_b
        ),
    }

    fracture_observed = all(observations.values())

    witness = {
        "object_type": "MATERIALIZED_UNIT_AUTHORITY_BINDING_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SAME_SUCCESSOR_TWO_MATERIALIZED_UNITS",
        "successor_id": successor["successor_id"],
        "successor_integrity_sha256": successor["integrity_sha256"],
        "work_spec_a_id": spec_a["work_spec_id"],
        "work_spec_b_id": spec_b["work_spec_id"],
        "materialized_unit_a_integrity_sha256": unit_a["integrity_sha256"],
        "materialized_unit_b_integrity_sha256": unit_b["integrity_sha256"],
        "authority_coordinates": coords,
        "authority_input_equals_successor_integrity": (
            coords["input_sha256"] == successor["integrity_sha256"]
        ),
        "authority_input_equals_unit_a_integrity": (
            coords["input_sha256"] == unit_a["integrity_sha256"]
        ),
        "authority_input_equals_unit_b_integrity": (
            coords["input_sha256"] == unit_b["integrity_sha256"]
        ),
        "admission_a": {
            "admitted": admission_a.get("admitted"),
            "blockers": admission_a.get("blockers"),
            "receipt_fields": sorted(receipt_a.keys()),
        },
        "admission_b": {
            "admitted": admission_b.get("admitted"),
            "blockers": admission_b.get("blockers"),
            "receipt_fields": sorted(receipt_b.keys()),
        },
        "observations": observations,
        "apparatus_assertions_pass": fracture_observed,
        "fracture_observed": fracture_observed,
        "target_law_matched": False if fracture_observed else None,
        "claim_ceiling": (
            "At the exact supplied source, successor-bound authority/admission does "
            "not bind exact materialized work-unit identity or work-spec identity. "
            "Two distinct materialized units derived from the same successor share "
            "the same successor authority coordinates and can each be admitted in "
            "separate disposable fixtures without presenting materialized-unit "
            "identity to the admission layer. This does not invalidate successor-"
            "authority standing in isolation and does not establish a production exploit."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    OUT.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OBSERVED] apparatus_assertions_pass {witness['apparatus_assertions_pass']}")
    print(f"[OBSERVED] fracture_observed {witness['fracture_observed']}")
    print(
        "[OBSERVED] unit_integrities_differ "
        + str(observations["materialized_units_differ"])
    )
    print(
        "[OBSERVED] same_successor_authority_accepts_both "
        + str(
            observations["unit_a_admits_under_successor_bound_authority"]
            and observations["unit_b_admits_under_same_successor_bound_authority"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
