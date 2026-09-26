#!/usr/bin/env python3
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
from src.coordination.invocation_result_settlement_v0 import build_candidate_settlement
from src.coordination.settlement_consequence_reconciliation_v0 import (
    build_consequence_evaluation,
    build_observed_consequence,
    reconcile,
)
from tests.coordination.test_basis_workcycle_v1 import unit_fixture
from tests.coordination.test_invocation_result_settlement_v0 import (
    bases,
    dispositions,
    valid_witness,
)

OUT = ROOT / "second_successor_from_reconciliation_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def applied_unit() -> dict:
    unit = unit_fixture()
    unit["qualification"]["scientific_standing"] = "QUALIFIED"
    unit["application"]["application_status"] = "APPLIED"
    unit["consequence_observation"]["effect_class"] = "NOT_YET_OBSERVABLE"
    return unit


def source_settlement() -> dict:
    return build_candidate_settlement(
        result_witness=valid_witness(),
        field_dispositions=dispositions(),
        settlement_basis=bases(),
        settlement_actor_identity="independent-settler-fixture-v0",
    )


def matched_case(unit: dict, settled: dict, obstruction: str, remaining_gap: str | None = None):
    observed = build_observed_consequence(
        settlement=settled,
        work_item_id=unit["identity"]["work_item_id"],
        expected_effect="fixture obstruction resolves",
        observed_effect=(
            "fixture obstruction resolved"
            if obstruction == "RESOLVED"
            else "expected effect observed but one obstruction remains"
        ),
        effect_class="OBSERVED",
        evidence_refs=[f"fixture://matched-{obstruction.lower()}"],
    )
    evaluation = build_consequence_evaluation(
        observed_consequence=observed,
        disposition="CONSEQUENCE_MATCHED",
        evaluation_basis="independent fixture observation matches expected effect",
        evaluator_identity="independent-consequence-evaluator-v0",
    )
    composition = reconcile(
        unit=unit,
        settlement=settled,
        expected_work_attempt_id=settled["source_work_attempt_id"],
        observed_consequence=observed,
        consequence_evaluation=evaluation,
        current_obstruction_posture=obstruction,
        remaining_gap=remaining_gap,
    )
    return observed, evaluation, composition


def contradicted_case(unit: dict, settled: dict):
    observed = build_observed_consequence(
        settlement=settled,
        work_item_id=unit["identity"]["work_item_id"],
        expected_effect="fixture obstruction resolves",
        observed_effect="fixture obstruction worsened",
        effect_class="OBSERVED",
        evidence_refs=["fixture://contradicted"],
        regression_detected=True,
    )
    evaluation = build_consequence_evaluation(
        observed_consequence=observed,
        disposition="CONSEQUENCE_CONTRADICTED",
        evaluation_basis="independent fixture observation contradicts expected effect",
        evaluator_identity="independent-consequence-evaluator-v0",
    )
    composition = reconcile(
        unit=unit,
        settlement=settled,
        expected_work_attempt_id=settled["source_work_attempt_id"],
        observed_consequence=observed,
        consequence_evaluation=evaluation,
        current_obstruction_posture="REMAINS",
    )
    return observed, evaluation, composition


def summarize_successor(candidate: dict) -> dict:
    return {
        "successor_posture": candidate["successor_posture"],
        "candidate_posture": candidate["candidate_posture"],
        "successor_id": candidate["successor_id"],
        "next_pressure_basis": candidate.get("next_pressure_basis"),
        "selection_basis": candidate["selection_basis"],
        "authority_effect": candidate["authority_effect"],
        "execution_effect": candidate["execution_effect"],
        "scientific_standing_effect": candidate["scientific_standing_effect"],
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing second_successor_from_reconciliation_observation.json first"
        )

    unit = applied_unit()
    settled = source_settlement()
    admissibility = bw.pressure_admissibility(unit)

    blocked = reconcile(
        unit=unit,
        settlement=settled,
        expected_work_attempt_id=settled["source_work_attempt_id"],
        observed_consequence=None,
        consequence_evaluation=None,
        current_obstruction_posture="REMAINS",
    )
    blocked_successor = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=blocked["basis_reconciliation"],
    )

    partial_observed, partial_evaluation, partial = matched_case(
        unit,
        settled,
        "REMAINS",
        remaining_gap="one source-supported obstruction remains",
    )
    partial_successor = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=partial["basis_reconciliation"],
    )
    partial_successor_repeat = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=partial["basis_reconciliation"],
    )

    satisfied_observed, satisfied_evaluation, satisfied = matched_case(
        unit,
        settled,
        "RESOLVED",
    )
    satisfied_successor = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=satisfied["basis_reconciliation"],
    )

    invalidated_observed, invalidated_evaluation, invalidated = contradicted_case(
        unit,
        settled,
    )
    invalidated_successor = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=invalidated["basis_reconciliation"],
    )

    assertions = {
        "settlement_only_routes_to_observe_consequence": (
            blocked["basis_reconciliation"]["disposition"] == "STILL_BLOCKED"
            and blocked_successor["successor_posture"]
            == "OBSERVE_APPLICATION_CONSEQUENCE"
        ),
        "partial_reconciliation_routes_to_resolve_gap": (
            partial["basis_reconciliation"]["disposition"] == "PARTIALLY_SATISFIED"
            and partial_successor["successor_posture"] == "RESOLVE_LOAD_BEARING_GAP"
        ),
        "partial_reconciliation_derives_exact_successor": (
            partial_successor["candidate_posture"] == "PROPOSED_NOT_ADMITTED"
            and partial_successor["successor_id"] is not None
            and partial_successor["next_pressure_basis"]
            == partial["basis_reconciliation"]["next_pressure_basis"]
        ),
        "partial_successor_is_deterministic": (
            partial_successor["successor_id"]
            == partial_successor_repeat["successor_id"]
        ),
        "satisfied_reconciliation_closes_basis": (
            satisfied["basis_reconciliation"]["disposition"] == "SATISFIED"
            and satisfied_successor["successor_posture"] == "CLOSE_BASIS"
            and satisfied_successor["candidate_posture"] == "NO_SUCCESSOR"
            and satisfied_successor["successor_id"] is None
        ),
        "invalidated_reconciliation_holds_without_successor": (
            invalidated["basis_reconciliation"]["disposition"] == "INVALIDATED"
            and invalidated_successor["successor_posture"]
            == "HOLD_NO_JUSTIFIED_WORK"
            and invalidated_successor["candidate_posture"] == "NO_SUCCESSOR"
            and invalidated_successor["successor_id"] is None
        ),
        "reconciliation_changes_future_projection": len({
            blocked_successor["successor_posture"],
            partial_successor["successor_posture"],
            satisfied_successor["successor_posture"],
            invalidated_successor["successor_posture"],
        }) >= 3,
        "no_authority_execution_or_standing_effect": all(
            item[key] == "NONE"
            for item in (
                blocked_successor,
                partial_successor,
                satisfied_successor,
                invalidated_successor,
            )
            for key in (
                "authority_effect",
                "execution_effect",
                "scientific_standing_effect",
            )
        ),
    }

    observation = {
        "object_type": "SECOND_SUCCESSOR_FROM_RECONCILIATION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_RECONCILIATION_TO_SUCCESSOR_COMPOSITION_FIXTURE",
        "source_settlement_id": settled["settlement_id"],
        "admissibility": admissibility,
        "settlement_only_case": {
            "reconciliation": blocked["basis_reconciliation"],
            "successor": summarize_successor(blocked_successor),
        },
        "partial_case": {
            "consequence_id": partial_observed["consequence_id"],
            "evaluation_id": partial_evaluation["evaluation_id"],
            "reconciliation": partial["basis_reconciliation"],
            "successor": summarize_successor(partial_successor),
        },
        "satisfied_case": {
            "consequence_id": satisfied_observed["consequence_id"],
            "evaluation_id": satisfied_evaluation["evaluation_id"],
            "reconciliation": satisfied["basis_reconciliation"],
            "successor": summarize_successor(satisfied_successor),
        },
        "invalidated_case": {
            "consequence_id": invalidated_observed["consequence_id"],
            "evaluation_id": invalidated_evaluation["evaluation_id"],
            "reconciliation": invalidated["basis_reconciliation"],
            "successor": summarize_successor(invalidated_successor),
        },
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Disposable composition pressure only. It tests whether already-qualified "
            "basis reconciliation lawfully changes next-work posture and exact successor "
            "projection without manual successor selection. It does not admit, authorize, "
            "schedule, execute, or grant scientific standing to successor work."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OBSERVED] all_assertions_pass {observation['all_assertions_pass']}")
    print(
        "[OBSERVED] settlement_only "
        + blocked_successor["successor_posture"]
    )
    print(
        "[OBSERVED] partial "
        + partial["basis_reconciliation"]["disposition"]
        + " -> "
        + partial_successor["successor_posture"]
    )
    print(
        "[OBSERVED] satisfied "
        + satisfied["basis_reconciliation"]["disposition"]
        + " -> "
        + satisfied_successor["successor_posture"]
    )
    print(
        "[OBSERVED] invalidated "
        + invalidated["basis_reconciliation"]["disposition"]
        + " -> "
        + invalidated_successor["successor_posture"]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
