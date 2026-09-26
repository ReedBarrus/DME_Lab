#!/usr/bin/env python3
"""Observe deterministic basis reconciliation under bounded evidence fixtures.

No work is admitted, authorized, scheduled, executed, or invoked.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination import basis_workcycle_v1 as bw


OUT = ROOT / "basis_reconciliation_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unit_fixture() -> dict:
    return {
        "identity": {
            "work_item_id": "W-RECONCILE-001",
            "campaign_id": "WORKCYCLE_STABILIZATION_001",
            "parent_work_item_id": "W-PRIOR-001",
            "operative_frame_ref": "FRAME-H-OPERATE-RECONCILE-001",
            "created_from_event": "BASIS_RECONCILIATION_PRESSURE_001",
        },
        "basis": {
            "basis_id": "B-RECONCILE-001",
            "basis_type": "LOAD_BEARING_UNCERTAINTY",
            "statement": "Observed work consequence must reconcile against the original operative obstruction.",
            "evidence_refs": [],
            "desired_consequence": {
                "statement": "One source-supported reconciliation disposition is derived from application/consequence evidence."
            },
            "current_obstruction": {
                "statement": "The basis remains open until operational consequence is reconciled."
            },
            "relevance_test": {
                "question": "Did the observed consequence actually resolve the load-bearing basis?",
                "failure_if_unanswered": True,
            },
            "basis_status": "SUPPORTED",
        },
        "pressure_selection": {
            "pressure_id": "BASIS_RECONCILIATION_PRESSURE_001",
            "target_distinction": {
                "lhs": "QUALIFIED_RESULT",
                "rhs": "SATISFIED_BASIS",
            },
            "selection_basis": "A qualified result must not close its basis until application and observed consequence support closure.",
            "expected_information_gain": {
                "statement": "Which bounded reconciliation disposition is supported by the observed operational evidence."
            },
            "application_dependency": "A matched reconciliation can later constrain successor derivation.",
            "stop_if_resolved_by_existing_evidence": True,
            "priority_basis": "BLOCKS_METABOLIC_CONTINUATION",
            "load_bearing_effects": ["APPLICATION", "BASIS", "OBSERVABILITY"],
        },
        "pressure_contract": {
            "allowed_operations": ["OBSERVE", "COMPARE", "RECONCILE", "FALSIFY"],
            "prohibited_operations": ["ADMIT", "EXECUTE", "CREATE_AUTHORITY"],
            "success_condition": {
                "statement": "Reconciliation changes only when bounded application/consequence/obstruction evidence changes."
            },
            "failure_condition": {
                "statement": "Qualified-but-unapplied work closes the basis, missing consequence closes the basis, or contradiction is ignored."
            },
            "unresolved_condition": {
                "statement": "The bounded evidence cannot determine a reconciliation posture."
            },
            "pressure_budget": {
                "max_rounds": 1,
                "max_branch_count": 1,
                "max_unresolved_children": 0,
            },
        },
        "result": {
            "source_result_ref": None,
            "distinctions": [],
            "apparatus_failures": [],
            "semantic_failures": [],
        },
        "qualification": {
            "adjudication_ref": "QUALIFIED-RECONCILE-FIXTURE",
            "scientific_standing": "QUALIFIED",
            "authority_effect": "NONE",
            "qualification_basis": "fixture",
            "unresolved_load_bearing_questions": [],
        },
        "application": {
            "required": True,
            "target_surface": "WORKFLOW",
            "proposed_change": {"statement": "Apply the qualified bounded result."},
            "executable_change_ref": None,
            "application_status": "ELIGIBLE",
            "withholding_basis": None,
        },
        "consequence_observation": {
            "required_if_applied": True,
            "expected_effect": "The load-bearing obstruction is reduced or resolved.",
            "observed_effect": None,
            "effect_class": "NOT_YET_OBSERVABLE",
            "evidence_refs": [],
            "regression_detected": False,
        },
        "basis_reconciliation": {
            "original_basis_id": "B-RECONCILE-001",
            "disposition": None,
            "remaining_gap": None,
            "next_pressure_allowed": False,
            "next_pressure_basis": None,
            "termination_reason": None,
        },
        "sanity_check": {
            "if_this_work_succeeds": {
                "what_changes_in_the_operating_world": "Successor derivation can consume an evidence-bound basis disposition instead of a caller-selected one."
            },
            "if_nothing_would_change": {"posture": "DO_NOT_RUN"},
        },
    }


def consequence(unit: dict, disposition: str, suffix: str) -> dict:
    return bw.wc.seal_object(
        {
            "object_type": "CONSEQUENCE_EVALUATION_V0",
            "evaluation_id": f"EVAL-{suffix}",
            "work_item_id": unit["identity"]["work_item_id"],
            "consequence_id": f"CONSEQ-{suffix}",
            "disposition": disposition,
            "integrity_sha256": "",
        }
    )


def applied_unit() -> dict:
    unit = unit_fixture()
    unit["application"]["application_status"] = "APPLIED"
    unit["consequence_observation"]["effect_class"] = "OBSERVED"
    return unit


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "basis_reconciliation_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    not_applied_unit = unit_fixture()
    not_applied = bw.derive_basis_reconciliation_from_evidence(
        not_applied_unit,
        consequence_evaluation=None,
        current_obstruction_posture="REMAINS",
    )

    no_consequence_unit = unit_fixture()
    no_consequence_unit["application"]["application_status"] = "APPLIED"
    no_consequence = bw.derive_basis_reconciliation_from_evidence(
        no_consequence_unit,
        consequence_evaluation=None,
        current_obstruction_posture="REMAINS",
    )

    satisfied_unit = applied_unit()
    matched = consequence(satisfied_unit, "CONSEQUENCE_MATCHED", "MATCHED")
    satisfied = bw.derive_basis_reconciliation_from_evidence(
        satisfied_unit,
        consequence_evaluation=matched,
        current_obstruction_posture="RESOLVED",
    )

    partial_unit = applied_unit()
    partial_eval = consequence(partial_unit, "CONSEQUENCE_MATCHED", "PARTIAL")
    partial = bw.derive_basis_reconciliation_from_evidence(
        partial_unit,
        consequence_evaluation=partial_eval,
        current_obstruction_posture="REMAINS",
        remaining_gap="one source-supported obstruction remains",
    )

    contradicted_unit = applied_unit()
    contradicted_eval = consequence(
        contradicted_unit,
        "CONSEQUENCE_CONTRADICTED",
        "CONTRADICTED",
    )
    invalidated = bw.derive_basis_reconciliation_from_evidence(
        contradicted_unit,
        consequence_evaluation=contradicted_eval,
        current_obstruction_posture="REMAINS",
    )

    changed_unit = applied_unit()
    changed_eval = consequence(changed_unit, "CONSEQUENCE_MATCHED", "CHANGED")
    changed_without_reframe = bw.derive_basis_reconciliation_from_evidence(
        changed_unit,
        consequence_evaluation=changed_eval,
        current_obstruction_posture="CHANGED",
    )
    reframed = bw.derive_basis_reconciliation_from_evidence(
        changed_unit,
        consequence_evaluation=changed_eval,
        current_obstruction_posture="CHANGED",
        reframed_basis="source-supported replacement basis B2",
    )

    assertions = {
        "qualified_not_applied_not_satisfied": not_applied["disposition"] == "STILL_BLOCKED",
        "applied_without_consequence_not_satisfied": no_consequence["disposition"] == "STILL_BLOCKED",
        "matched_plus_resolved_satisfied": satisfied["disposition"] == "SATISFIED",
        "matched_plus_remaining_obstruction_partial": partial["disposition"] == "PARTIALLY_SATISFIED",
        "contradicted_invalidates": invalidated["disposition"] == "INVALIDATED",
        "changed_without_reframe_invalidates": changed_without_reframe["disposition"] == "INVALIDATED",
        "changed_with_explicit_reframe_reframes": reframed["disposition"] == "REFRAMED",
        "reframe_is_explicit": reframed["next_pressure_basis"] == "source-supported replacement basis B2",
        "satisfied_has_no_next_pressure": satisfied["next_pressure_allowed"] is False,
        "no_authority_effect": all(
            item["authority_effect"] == "NONE"
            for item in [
                not_applied,
                no_consequence,
                satisfied,
                partial,
                invalidated,
                changed_without_reframe,
                reframed,
            ]
        ),
        "no_execution_effect": all(
            item["execution_effect"] == "NONE"
            for item in [
                not_applied,
                no_consequence,
                satisfied,
                partial,
                invalidated,
                changed_without_reframe,
                reframed,
            ]
        ),
    }

    witness = {
        "object_type": "BASIS_RECONCILIATION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EVIDENCE_BOUND_RECONCILIATION_FIXTURE",
        "qualified_not_applied_case": not_applied,
        "applied_without_consequence_case": no_consequence,
        "matched_resolved_case": satisfied,
        "matched_obstruction_remains_case": partial,
        "contradicted_case": invalidated,
        "changed_without_reframe_case": changed_without_reframe,
        "changed_with_explicit_reframe_case": reframed,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Deterministic bounded reconciliation over supplied application, consequence, "
            "and source-supported obstruction posture only. The fixture does not independently "
            "discover world state, validate the obstruction classification, admit work, create "
            "authority, execute, schedule, or invoke a model."
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
    print(f"[OK] satisfied {satisfied['disposition']}")
    print(f"[OK] partial {partial['disposition']}")
    print(f"[OK] contradicted {invalidated['disposition']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
