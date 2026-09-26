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

from src.coordination.materialized_settlement_consequence_reconciliation_v0 import (
    MaterializedSettlementConsequenceError,
    build_consequence_evaluation,
    build_observed_consequence,
    reconcile,
)
from src.coordination.successor_work_unit_materialization_v0 import (
    materialize_successor_work_unit,
)
from tests.coordination.test_materialized_settlement_consequence_reconciliation_v0 import (
    fixture,
)
from tests.coordination.test_materialized_unit_authority_admission_v0 import (
    alternate_spec,
)

OUT = ROOT / "materialized_settlement_consequence_reconciliation_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "remove existing materialized_settlement_consequence_reconciliation_observation.json first"
        )

    successor, spec, unit, settlement = fixture()

    settlement_only = reconcile(
        unit=unit,
        settlement=settlement,
        expected_work_attempt_id=settlement["source_work_attempt_id"],
        observed_consequence=None,
        consequence_evaluation=None,
        current_obstruction_posture="REMAINS",
    )

    matched_observed = build_observed_consequence(
        settlement=settlement,
        materialized_unit=unit,
        expected_effect="exact materialized obstruction resolves",
        observed_effect="exact materialized obstruction resolved",
        effect_class="OBSERVED",
        evidence_refs=["fixture://materialized-matched"],
    )
    matched_evaluation = build_consequence_evaluation(
        observed_consequence=matched_observed,
        disposition="CONSEQUENCE_MATCHED",
        evaluation_basis="independent exact-work fixture evidence matches",
        evaluator_identity="independent-materialized-consequence-evaluator-v0",
    )
    matched = reconcile(
        unit=unit,
        settlement=settlement,
        expected_work_attempt_id=settlement["source_work_attempt_id"],
        observed_consequence=matched_observed,
        consequence_evaluation=matched_evaluation,
        current_obstruction_posture="RESOLVED",
    )

    contradicted_observed = build_observed_consequence(
        settlement=settlement,
        materialized_unit=unit,
        expected_effect="exact materialized obstruction resolves",
        observed_effect="exact materialized obstruction worsened",
        effect_class="OBSERVED",
        evidence_refs=["fixture://materialized-contradicted"],
        regression_detected=True,
    )
    contradicted_evaluation = build_consequence_evaluation(
        observed_consequence=contradicted_observed,
        disposition="CONSEQUENCE_CONTRADICTED",
        evaluation_basis="independent exact-work fixture evidence contradicts",
        evaluator_identity="independent-materialized-consequence-evaluator-v0",
    )
    contradicted = reconcile(
        unit=unit,
        settlement=settlement,
        expected_work_attempt_id=settlement["source_work_attempt_id"],
        observed_consequence=contradicted_observed,
        consequence_evaluation=contradicted_evaluation,
        current_obstruction_posture="REMAINS",
    )

    spec_b = alternate_spec(successor)
    unit_b = materialize_successor_work_unit(
        successor_candidate=successor,
        work_spec=spec_b,
    )
    wrong_unit_error = None
    try:
        build_observed_consequence(
            settlement=settlement,
            materialized_unit=unit_b,
            expected_effect="fixture expected",
            observed_effect="fixture observed",
            effect_class="OBSERVED",
            evidence_refs=["fixture://wrong-materialization"],
        )
    except MaterializedSettlementConsequenceError as exc:
        wrong_unit_error = {
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    assertions = {
        "settlement_only_still_blocked": (
            settlement_only["basis_reconciliation"]["disposition"]
            == "STILL_BLOCKED"
            and settlement_only["consequence_id"] is None
            and settlement_only["settlement_is_consequence"] is False
        ),
        "matched_consequence_satisfies": (
            matched["basis_reconciliation"]["disposition"] == "SATISFIED"
        ),
        "contradicted_consequence_invalidates": (
            contradicted["basis_reconciliation"]["disposition"]
            == "INVALIDATED"
        ),
        "same_settlement_identity": (
            settlement_only["settlement_id"]
            == matched["settlement_id"]
            == contradicted["settlement_id"]
            == settlement["settlement_id"]
        ),
        "consequence_identities_differ": (
            matched["consequence_id"] != contradicted["consequence_id"]
        ),
        "evaluation_identities_differ": (
            matched["evaluation_id"] != contradicted["evaluation_id"]
        ),
        "reconciliation_identities_differ": (
            matched["reconciliation_identity"]
            != contradicted["reconciliation_identity"]
        ),
        "successor_lineage_bound": (
            matched["successor_id"] == successor["successor_id"]
            and matched_observed["successor_id"] == successor["successor_id"]
        ),
        "work_spec_lineage_bound": (
            matched["work_spec_id"] == spec["work_spec_id"]
            and matched_observed["work_spec_id"] == spec["work_spec_id"]
        ),
        "materialized_unit_lineage_bound": (
            matched["materialized_unit_integrity_sha256"]
            == unit["integrity_sha256"]
            and matched_observed["materialized_unit_integrity_sha256"]
            == unit["integrity_sha256"]
        ),
        "wrong_materialization_rejected": wrong_unit_error is not None,
        "no_effects_created": (
            matched["authority_effect"] == "NONE"
            and matched["execution_effect"] == "NONE"
            and matched["atlas_mutation_effect"] == "NONE"
            and matched["scientific_standing_effect"] == "NONE"
            and contradicted["authority_effect"] == "NONE"
            and contradicted["execution_effect"] == "NONE"
            and contradicted["atlas_mutation_effect"] == "NONE"
            and contradicted["scientific_standing_effect"] == "NONE"
        ),
    }

    observation = {
        "object_type": "MATERIALIZED_SETTLEMENT_CONSEQUENCE_RECONCILIATION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EXACT_MATERIALIZED_CONSEQUENCE_FIXTURE",
        "successor_id": successor["successor_id"],
        "work_spec_id": spec["work_spec_id"],
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "settlement_id": settlement["settlement_id"],
        "settlement_only": {
            "composition_id": settlement_only["composition_id"],
            "basis_disposition": settlement_only["basis_reconciliation"]["disposition"],
        },
        "matched": {
            "composition_id": matched["composition_id"],
            "consequence_id": matched["consequence_id"],
            "evaluation_id": matched["evaluation_id"],
            "reconciliation_identity": matched["reconciliation_identity"],
            "basis_disposition": matched["basis_reconciliation"]["disposition"],
        },
        "contradicted": {
            "composition_id": contradicted["composition_id"],
            "consequence_id": contradicted["consequence_id"],
            "evaluation_id": contradicted["evaluation_id"],
            "reconciliation_identity": contradicted["reconciliation_identity"],
            "basis_disposition": contradicted["basis_reconciliation"]["disposition"],
        },
        "wrong_materialization": wrong_unit_error,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, one exact materialized candidate "
            "settlement remains insufficient to reconcile the active basis without "
            "separately supplied consequence evidence. Independently supplied "
            "matched consequence evidence drives the existing bounded "
            "reconciliation law to SATISFIED when the obstruction is supplied as "
            "RESOLVED, while contradicted consequence evidence drives it to "
            "INVALIDATED. The same settlement identity yields distinct bounded "
            "basis postures only under distinct consequence/evaluation evidence, "
            "while exact successor, work-spec, and materialized-unit lineage is "
            "conserved. No authority, execution, Atlas mutation, or scientific "
            "standing is created."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (json.dumps(observation, indent=2) + "\n").encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {hashlib.sha256(encoded).hexdigest()}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(
        "[OK] settlement_only_still_blocked "
        + str(assertions["settlement_only_still_blocked"])
    )
    print(
        "[OK] matched_consequence_satisfies "
        + str(assertions["matched_consequence_satisfies"])
    )
    print(
        "[OK] contradicted_consequence_invalidates "
        + str(assertions["contradicted_consequence_invalidates"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
