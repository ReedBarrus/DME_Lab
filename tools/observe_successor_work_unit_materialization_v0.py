#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination import basis_workcycle_v1 as bw
from src.coordination.successor_work_unit_materialization_v0 import (
    SuccessorWorkUnitMaterializationError,
    build_successor_work_spec,
    materialize_successor_work_unit,
)
from tests.coordination.test_basis_workcycle_v1 import unit_fixture
from tests.coordination.test_successor_work_unit_materialization_v0 import work_spec

OUT = ROOT / "successor_work_unit_materialization_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def derive_successor() -> dict:
    unit = unit_fixture()
    admissibility = bw.pressure_admissibility(unit)
    reconciliation = bw.basis_reconciliation(
        unit,
        disposition="PARTIALLY_SATISFIED",
        remaining_gap="one source-supported obstruction remains",
        next_pressure_basis="resolve remaining source-supported obstruction",
    )
    return bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=reconciliation,
    )


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing successor_work_unit_materialization_observation.json first"
        )

    successor = derive_successor()
    spec = work_spec(successor)
    unit = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec,
    )
    unit_repeat = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec,
    )
    admissibility = bw.pressure_admissibility(unit)

    alternate_spec = build_successor_work_spec(
        successor_candidate=successor,
        evidence_refs=["fixture://reconciliation", "fixture://remaining-gap"],
        desired_consequence="The remaining source-supported obstruction is resolved.",
        relevance_question="Would an alternate bounded pressure resolve the exact remaining obstruction?",
        pressure_id="P-SUCCESSOR-WORK-ALT-001",
        target_distinction_lhs="REMAINING_OBSTRUCTION",
        target_distinction_rhs="RESOLVED_OBSTRUCTION",
        selection_basis="Fresh reconciliation leaves one exact load-bearing gap.",
        expected_information_gain="Whether an alternate bounded transformation resolves the same exact gap.",
        application_dependency="A qualified result must exist before any application.",
        priority_basis="BLOCKS_METABOLIC_CONTINUATION",
        load_bearing_effects=["BASIS", "OBSERVABILITY"],
        allowed_operations=["OBSERVE", "COMPARE"],
        prohibited_operations=["GRANT_AUTHORITY", "EXECUTE", "SELF_PROMOTE"],
        success_condition="One alternate bounded result addresses the exact remaining obstruction.",
        failure_condition="The alternate pressure widens scope.",
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
    alternate_unit = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=alternate_spec,
    )

    tampered_spec = copy.deepcopy(spec)
    tampered_spec["proposed_change"] = "silently widened transformation"
    tamper_error = None
    try:
        materialize_successor_work_unit(
            successor_candidate=successor,
            work_spec=tampered_spec,
        )
    except SuccessorWorkUnitMaterializationError as exc:
        tamper_error = {
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    assertions = {
        "successor_identity_becomes_work_item_identity": (
            unit["identity"]["work_item_id"] == successor["successor_id"]
        ),
        "next_pressure_basis_becomes_declared_basis": (
            unit["basis"]["statement"] == successor["next_pressure_basis"]
        ),
        "source_successor_identity_bound": (
            unit["materialization"]["source_successor_id"] == successor["successor_id"]
            and unit["materialization"]["source_successor_integrity_sha256"]
            == successor["integrity_sha256"]
        ),
        "reconciliation_identity_bound": (
            unit["materialization"]["source_reconciliation_identity"]
            == successor["reconciliation_identity"]
        ),
        "explicit_work_spec_bound": (
            unit["materialization"]["work_spec_id"] == spec["work_spec_id"]
            and unit["materialization"]["work_spec_integrity_sha256"]
            == spec["integrity_sha256"]
            and unit["materialization"]["spec_source"] == "EXTERNALLY_SUPPLIED"
        ),
        "materialized_unit_valid": (
            bw.validate_workflow_unit(unit) is None
        ),
        "fixed_inputs_deterministic": unit == unit_repeat,
        "materialized_pressure_admissible_but_not_admitted": (
            admissibility["admissible"] is True
            and admissibility["work_admission_effect"] == "NONE"
        ),
        "changed_work_spec_changes_unit_not_successor": (
            alternate_unit["identity"]["work_item_id"] == successor["successor_id"]
            and alternate_unit["materialization"]["source_successor_id"]
            == successor["successor_id"]
            and alternate_unit["integrity_sha256"] != unit["integrity_sha256"]
        ),
        "tampered_work_spec_rejected": tamper_error is not None,
        "no_qualification_authority_execution_or_standing_effect": (
            unit["qualification"]["scientific_standing"] == "NONE"
            and unit["materialization"]["work_admission_effect"] == "NONE"
            and unit["materialization"]["authority_effect"] == "NONE"
            and unit["materialization"]["execution_effect"] == "NONE"
            and unit["materialization"]["scientific_standing_effect"] == "NONE"
        ),
    }

    observation = {
        "object_type": "SUCCESSOR_WORK_UNIT_MATERIALIZATION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SUCCESSOR_PLUS_EXPLICIT_WORK_SPEC_FIXTURE",
        "source_successor": successor,
        "source_work_spec": spec,
        "materialized_unit": unit,
        "alternate_work_spec": alternate_spec,
        "alternate_materialized_unit_identity": alternate_unit["integrity_sha256"],
        "pressure_admissibility": admissibility,
        "tamper_case": tamper_error,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "One exact deterministic successor candidate plus one externally supplied "
            "bounded work spec can materialize one complete basis_workcycle_v1-compatible "
            "next workflow unit while conserving successor/reconciliation/next-pressure "
            "identity. Materialization does not invent the work spec and creates no "
            "qualification, work admission, authority, execution, or scientific standing."
        ),
        "work_admission_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(f"[OK] successor_id {successor['successor_id']}")
    print(f"[OK] materialized_work_item_id {unit['identity']['work_item_id']}")
    print(f"[OK] pressure_admissible {admissibility['admissible']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
