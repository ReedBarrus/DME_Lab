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

from src.coordination.materialized_reconciliation_successor_projection_v0 import (
    derive_materialized_successor_projection,
)
from src.coordination.materialized_settlement_consequence_reconciliation_v0 import (
    build_consequence_evaluation,
    build_observed_consequence,
    reconcile,
)
from tests.coordination.test_materialized_settlement_consequence_reconciliation_v0 import (
    fixture,
)

OUT = ROOT / "materialized_reconciliation_successor_projection_observation.json"


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
            "remove existing materialized_reconciliation_successor_projection_observation.json first"
        )

    successor, spec, unit, settlement = fixture()
    observed = build_observed_consequence(
        settlement=settlement,
        materialized_unit=unit,
        expected_effect="exact materialized obstruction resolves",
        observed_effect="exact materialized obstruction resolved",
        effect_class="OBSERVED",
        evidence_refs=["fixture://successor-projection"],
    )
    matched_eval = build_consequence_evaluation(
        observed_consequence=observed,
        disposition="CONSEQUENCE_MATCHED",
        evaluation_basis="independent exact-work evidence matches",
        evaluator_identity="independent-materialized-successor-evaluator-v0",
    )

    satisfied_composition = reconcile(
        unit=unit,
        settlement=settlement,
        expected_work_attempt_id=settlement["source_work_attempt_id"],
        observed_consequence=observed,
        consequence_evaluation=matched_eval,
        current_obstruction_posture="RESOLVED",
    )
    satisfied = derive_materialized_successor_projection(
        unit=unit,
        reconciliation_composition=satisfied_composition,
    )

    partial_composition = reconcile(
        unit=unit,
        settlement=settlement,
        expected_work_attempt_id=settlement["source_work_attempt_id"],
        observed_consequence=observed,
        consequence_evaluation=matched_eval,
        current_obstruction_posture="REMAINS",
        remaining_gap="one source-supported obstruction remains",
    )
    partial = derive_materialized_successor_projection(
        unit=unit,
        reconciliation_composition=partial_composition,
    )
    partial_repeat = derive_materialized_successor_projection(
        unit=unit,
        reconciliation_composition=partial_composition,
    )

    contradicted_eval = build_consequence_evaluation(
        observed_consequence=observed,
        disposition="CONSEQUENCE_CONTRADICTED",
        evaluation_basis="independent exact-work evidence contradicts",
        evaluator_identity="independent-materialized-successor-evaluator-v0",
    )
    invalidated_composition = reconcile(
        unit=unit,
        settlement=settlement,
        expected_work_attempt_id=settlement["source_work_attempt_id"],
        observed_consequence=observed,
        consequence_evaluation=contradicted_eval,
        current_obstruction_posture="REMAINS",
    )
    invalidated = derive_materialized_successor_projection(
        unit=unit,
        reconciliation_composition=invalidated_composition,
    )

    assertions = {
        "satisfied_closes_basis": satisfied["derived_successor_posture"] == "CLOSE_BASIS",
        "satisfied_no_successor": (
            satisfied["derived_candidate_posture"] == "NO_SUCCESSOR"
            and satisfied["derived_successor_id"] is None
            and satisfied["next_pressure_allowed"] is False
        ),
        "partial_allows_continuation": (
            partial["basis_disposition"] == "PARTIALLY_SATISFIED"
            and partial["next_pressure_allowed"] is True
            and partial["derived_successor_posture"] == "RESOLVE_LOAD_BEARING_GAP"
            and partial["derived_candidate_posture"] == "PROPOSED_NOT_ADMITTED"
            and partial["derived_successor_id"] is not None
        ),
        "partial_successor_deterministic": partial == partial_repeat,
        "partial_successor_binds_reconciliation": (
            partial["successor_candidate"]["reconciliation_identity"]
            == partial_composition["reconciliation_identity"]
            and partial["successor_candidate"]["next_pressure_basis"]
            == partial_composition["basis_reconciliation"]["next_pressure_basis"]
        ),
        "invalidated_holds": (
            invalidated["derived_successor_posture"] == "HOLD_NO_JUSTIFIED_WORK"
            and invalidated["derived_candidate_posture"] == "NO_SUCCESSOR"
            and invalidated["derived_successor_id"] is None
        ),
        "exact_materialized_lineage_preserved": (
            satisfied["source_successor_id"] == successor["successor_id"]
            and satisfied["source_work_spec_id"] == spec["work_spec_id"]
            and satisfied["source_materialized_unit_integrity_sha256"]
            == unit["integrity_sha256"]
            and partial["source_successor_id"] == successor["successor_id"]
            and partial["source_work_spec_id"] == spec["work_spec_id"]
            and partial["source_materialized_unit_integrity_sha256"]
            == unit["integrity_sha256"]
        ),
        "no_work_or_authority_created": all(
            projection["work_created"] is False
            and projection["work_admission_effect"] == "NONE"
            and projection["authority_effect"] == "NONE"
            and projection["execution_effect"] == "NONE"
            and projection["scientific_standing_effect"] == "NONE"
            for projection in (satisfied, partial, invalidated)
        ),
    }

    observation = {
        "object_type": "MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EXACT_MATERIALIZED_SUCCESSOR_PROJECTION_FIXTURE",
        "source_successor_id": successor["successor_id"],
        "source_work_spec_id": spec["work_spec_id"],
        "source_materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "satisfied": satisfied,
        "partial": partial,
        "invalidated": invalidated,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, successor existence is a deterministic "
            "projection of exact materialized reconciliation posture rather than a "
            "default loop continuation. SATISFIED closes the basis with no successor; "
            "INVALIDATED holds with no successor; PARTIALLY_SATISFIED permits one "
            "deterministic unadmitted successor candidate bound to the exact "
            "reconciliation identity and next-pressure basis. Exact successor, "
            "work-spec, and materialized-unit lineage is preserved. No work is "
            "materialized, admitted, authorized, scheduled, or executed."
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
    print(f"[OK] satisfied_no_successor {assertions['satisfied_no_successor']}")
    print(f"[OK] partial_allows_continuation {assertions['partial_allows_continuation']}")
    print(f"[OK] invalidated_holds {assertions['invalidated_holds']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
