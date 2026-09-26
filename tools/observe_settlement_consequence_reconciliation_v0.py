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

OUT = ROOT / "settlement_consequence_reconciliation_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def applied_unit() -> dict:
    unit = unit_fixture()
    unit["qualification"]["scientific_standing"] = "QUALIFIED"
    unit["application"]["application_status"] = "APPLIED"
    unit["consequence_observation"]["effect_class"] = "NOT_YET_OBSERVABLE"
    return unit


def main() -> int:
    if OUT.exists():
        raise SystemExit("remove existing settlement_consequence_reconciliation_observation.json first")

    unit = applied_unit()
    settled = build_candidate_settlement(
        result_witness=valid_witness(),
        field_dispositions=dispositions(),
        settlement_basis=bases(),
        settlement_actor_identity="independent-settler-fixture-v0",
    )

    blocked = reconcile(
        unit=unit,
        settlement=settled,
        expected_work_attempt_id=settled["source_work_attempt_id"],
        observed_consequence=None,
        consequence_evaluation=None,
        current_obstruction_posture="REMAINS",
    )

    matched_observation = build_observed_consequence(
        settlement=settled,
        work_item_id=unit["identity"]["work_item_id"],
        expected_effect="fixture obstruction resolves",
        observed_effect="fixture obstruction resolved",
        effect_class="OBSERVED",
        evidence_refs=["fixture://matched-world-state"],
    )
    matched_evaluation = build_consequence_evaluation(
        observed_consequence=matched_observation,
        disposition="CONSEQUENCE_MATCHED",
        evaluation_basis="independent fixture observation matches expected effect",
        evaluator_identity="independent-consequence-evaluator-v0",
    )
    satisfied = reconcile(
        unit=unit,
        settlement=settled,
        expected_work_attempt_id=settled["source_work_attempt_id"],
        observed_consequence=matched_observation,
        consequence_evaluation=matched_evaluation,
        current_obstruction_posture="RESOLVED",
    )

    contradicted_observation = build_observed_consequence(
        settlement=settled,
        work_item_id=unit["identity"]["work_item_id"],
        expected_effect="fixture obstruction resolves",
        observed_effect="fixture obstruction worsened",
        effect_class="OBSERVED",
        evidence_refs=["fixture://contradicted-world-state"],
        regression_detected=True,
    )
    contradicted_evaluation = build_consequence_evaluation(
        observed_consequence=contradicted_observation,
        disposition="CONSEQUENCE_CONTRADICTED",
        evaluation_basis="independent fixture observation contradicts expected effect",
        evaluator_identity="independent-consequence-evaluator-v0",
    )
    invalidated = reconcile(
        unit=unit,
        settlement=settled,
        expected_work_attempt_id=settled["source_work_attempt_id"],
        observed_consequence=contradicted_observation,
        consequence_evaluation=contradicted_evaluation,
        current_obstruction_posture="REMAINS",
    )

    assertions = {
        "settlement_alone_stays_blocked": (
            blocked["basis_reconciliation"]["disposition"] == "STILL_BLOCKED"
            and blocked["consequence_id"] is None
        ),
        "settlement_not_collapsed_into_consequence": (
            blocked["settlement_is_consequence"] is False
            and satisfied["settlement_is_consequence"] is False
            and invalidated["settlement_is_consequence"] is False
        ),
        "matched_consequence_satisfies_resolved_basis": (
            satisfied["basis_reconciliation"]["disposition"] == "SATISFIED"
        ),
        "contradicted_consequence_invalidates_basis": (
            invalidated["basis_reconciliation"]["disposition"] == "INVALIDATED"
        ),
        "same_settlement_different_consequence_changes_reconciliation": (
            satisfied["settlement_id"] == invalidated["settlement_id"]
            and satisfied["basis_reconciliation"]["integrity_sha256"]
            != invalidated["basis_reconciliation"]["integrity_sha256"]
        ),
        "consequence_identity_bound": (
            satisfied["consequence_id"] == matched_observation["consequence_id"]
            and invalidated["consequence_id"] == contradicted_observation["consequence_id"]
        ),
        "evaluation_identity_bound": (
            satisfied["evaluation_id"] == matched_evaluation["evaluation_id"]
            and invalidated["evaluation_id"] == contradicted_evaluation["evaluation_id"]
        ),
        "no_authority_execution_atlas_or_standing_effect": all(
            result[key] == "NONE"
            for result in (blocked, satisfied, invalidated)
            for key in (
                "authority_effect",
                "execution_effect",
                "atlas_mutation_effect",
                "scientific_standing_effect",
            )
        ),
    }

    observation = {
        "object_type": "SETTLEMENT_CONSEQUENCE_RECONCILIATION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SAME_PROCESS_CONSEQUENCE_RECONCILIATION_FIXTURE",
        "source_settlement": settled,
        "settlement_only_case": blocked,
        "matched_consequence": matched_observation,
        "matched_evaluation": matched_evaluation,
        "satisfied_case": satisfied,
        "contradicted_consequence": contradicted_observation,
        "contradicted_evaluation": contradicted_evaluation,
        "invalidated_case": invalidated,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "One deterministic candidate settlement can remain basis-blocking without "
            "independent consequence evidence, while separately supplied matched or "
            "contradicted consequence evidence can drive the existing bounded basis "
            "reconciliation law to SATISFIED or INVALIDATED respectively. This does not "
            "derive or admit a successor, grant authority, execute work, or mutate Atlas."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "atlas_mutation_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(f"[OK] settlement_only {blocked['basis_reconciliation']['disposition']}")
    print(f"[OK] matched_case {satisfied['basis_reconciliation']['disposition']}")
    print(f"[OK] contradicted_case {invalidated['basis_reconciliation']['disposition']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
