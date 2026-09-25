#!/usr/bin/env python3
"""Observe deterministic successor identity conservation.

This is a disposable projection-only pressure. It does not admit, authorize,
schedule, execute, or invoke successor work.
"""

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


OUT = ROOT / "successor_identity_observation.json"


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
            "work_item_id": "W-METABOLIC-001",
            "campaign_id": "WORKCYCLE_STABILIZATION_001",
            "parent_work_item_id": None,
            "operative_frame_ref": "FRAME-H-OPERATE-001",
            "created_from_event": "SUCCESSOR_IDENTITY_PRESSURE_001",
        },
        "basis": {
            "basis_id": "B-H-OPERATE-001",
            "basis_type": "LOAD_BEARING_UNCERTAINTY",
            "statement": "A qualified bounded workcycle cannot yet continue through a source-bound derived successor.",
            "evidence_refs": [],
            "desired_consequence": {
                "statement": "Derive at most one reconstructable successor candidate identity from exact prior basis and reconciliation."
            },
            "current_obstruction": {
                "statement": "Successor identity is implemented but not yet independently pressured."
            },
            "relevance_test": {
                "question": "Does deterministic successor identity reduce coordination ambiguity?",
                "failure_if_unanswered": True,
            },
            "basis_status": "SUPPORTED",
        },
        "pressure_selection": {
            "pressure_id": "SUCCESSOR_IDENTITY_CONSERVATION_PRESSURE_001",
            "target_distinction": {
                "lhs": "SUCCESSOR_POSTURE",
                "rhs": "SUCCESSOR_IDENTITY",
            },
            "selection_basis": "Atomic admission needs a source-bound successor candidate rather than a planner-invented work identity.",
            "expected_information_gain": {
                "statement": "Whether exact prior coordinates reconstruct one stable successor candidate identity."
            },
            "application_dependency": "A matched successor identity can later be bound into atomic admission.",
            "stop_if_resolved_by_existing_evidence": True,
            "priority_basis": "BLOCKS_COORDINATION",
            "load_bearing_effects": ["BASIS", "RECONSTRUCTION", "AUTHORITY"],
        },
        "pressure_contract": {
            "allowed_operations": ["OBSERVE", "RECONSTRUCT", "COMPARE", "FALSIFY"],
            "prohibited_operations": ["ADMIT", "EXECUTE", "CREATE_AUTHORITY"],
            "success_condition": {"statement": "Same exact reconciliation reconstructs same successor identity; HOLD/CLOSE yield none."},
            "failure_condition": {"statement": "Identical source coordinates diverge or terminal postures manufacture a successor."},
            "unresolved_condition": {"statement": "Identity conservation cannot be determined."},
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
            "adjudication_ref": None,
            "scientific_standing": "NONE",
            "authority_effect": "NONE",
            "qualification_basis": "",
            "unresolved_load_bearing_questions": [],
        },
        "application": {
            "required": True,
            "target_surface": "ATLAS",
            "proposed_change": {"statement": "Bind a matched successor identity into later admission."},
            "executable_change_ref": None,
            "application_status": "NOT_YET_ELIGIBLE",
            "withholding_basis": None,
        },
        "consequence_observation": {
            "required_if_applied": True,
            "expected_effect": "Successor identity becomes reconstructable from prior coordinates.",
            "observed_effect": None,
            "effect_class": "NOT_YET_OBSERVABLE",
            "evidence_refs": [],
            "regression_detected": False,
        },
        "basis_reconciliation": {
            "original_basis_id": "B-H-OPERATE-001",
            "disposition": None,
            "remaining_gap": None,
            "next_pressure_allowed": False,
            "next_pressure_basis": None,
            "termination_reason": None,
        },
        "sanity_check": {
            "if_this_work_succeeds": {
                "what_changes_in_the_operating_world": "A later admission can consume one source-bound successor candidate identity."
            },
            "if_nothing_would_change": {"posture": "DO_NOT_RUN"},
        },
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "successor_identity_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    unit = unit_fixture()
    admissibility = bw.pressure_admissibility(unit)

    reconciliation = bw.basis_reconciliation(
        unit,
        disposition="STILL_BLOCKED",
        remaining_gap="one load-bearing successor remains",
        next_pressure_basis="bind verified authority and derived successor into atomic admission",
    )
    first = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=reconciliation,
    )
    second = bw.derive_successor_candidate(
        copy.deepcopy(unit),
        admissibility=copy.deepcopy(admissibility),
        reconciliation=copy.deepcopy(reconciliation),
    )

    changed_reconciliation = bw.basis_reconciliation(
        unit,
        disposition="STILL_BLOCKED",
        remaining_gap="a different load-bearing successor remains",
        next_pressure_basis="pressure a distinct successor basis",
    )
    changed = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=changed_reconciliation,
    )

    satisfied = bw.basis_reconciliation(
        unit,
        disposition="SATISFIED",
        remaining_gap=None,
    )
    closed = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=satisfied,
    )

    hold_unit = unit_fixture()
    hold_unit["pressure_selection"]["load_bearing_effects"] = ["CURIOSITY"]
    hold_admissibility = bw.pressure_admissibility(hold_unit)
    held = bw.derive_successor_candidate(
        hold_unit,
        admissibility=hold_admissibility,
    )

    assertions = {
        "pressure_admissible": admissibility["admissible"] is True,
        "same_source_same_successor_id": first["successor_id"] == second["successor_id"],
        "same_source_same_basis": first["basis_id"] == second["basis_id"],
        "same_source_same_posture": first["successor_posture"] == second["successor_posture"],
        "same_source_same_claim_ceiling": first["claim_ceiling"] == second["claim_ceiling"],
        "changed_reconciliation_changes_identity": first["successor_id"] != changed["successor_id"],
        "candidate_not_admitted": first["candidate_posture"] == "PROPOSED_NOT_ADMITTED",
        "close_basis_has_no_successor": closed["successor_id"] is None and closed["candidate_posture"] == "NO_SUCCESSOR",
        "hold_has_no_successor": held["successor_id"] is None and held["candidate_posture"] == "NO_SUCCESSOR",
        "no_authority_effect": all(x["authority_effect"] == "NONE" for x in [first, second, changed, closed, held]),
        "no_execution_effect": all(x["execution_effect"] == "NONE" for x in [first, second, changed, closed, held]),
    }

    witness = {
        "object_type": "SUCCESSOR_IDENTITY_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_DETERMINISTIC_PROJECTION_FIXTURE",
        "reconciliation": reconciliation,
        "first_reconstruction": first,
        "second_reconstruction": second,
        "changed_reconciliation": changed_reconciliation,
        "changed_successor": changed,
        "closed_basis_case": closed,
        "hold_case": held,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Deterministic successor candidate identity projection only. "
            "This does not establish basis correctness, frame currentness, work admission, "
            "authority, execution, scheduling, or model invocation."
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
    print(f"[OK] successor_id {first['successor_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
