#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination.materialized_invocation_result_settlement_v0 import (
    CANDIDATE_ACCEPTED,
    CANDIDATE_HELD,
    CANDIDATE_REJECTED,
    MaterializedResultSettlementError,
    build_materialized_candidate_settlement,
)
from tests.coordination.test_materialized_invocation_result_settlement_v0 import (
    bases,
    dispositions,
    valid_materialized_witness,
)

OUT = ROOT / "materialized_invocation_result_settlement_observation.json"


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
            "remove existing materialized_invocation_result_settlement_observation.json first"
        )

    witness = valid_materialized_witness()
    witness_before = deepcopy(witness)

    settlement = build_materialized_candidate_settlement(
        result_witness=witness,
        field_dispositions=dispositions(),
        settlement_basis=bases(),
        settlement_actor_identity="independent-materialized-settler-fixture-v0",
    )
    settlement_repeat = build_materialized_candidate_settlement(
        result_witness=witness,
        field_dispositions=dispositions(),
        settlement_basis=bases(),
        settlement_actor_identity="independent-materialized-settler-fixture-v0",
    )

    changed_dispositions = dispositions()
    changed_dispositions["count"] = CANDIDATE_REJECTED
    changed_settlement = build_materialized_candidate_settlement(
        result_witness=witness,
        field_dispositions=changed_dispositions,
        settlement_basis=bases(),
        settlement_actor_identity="independent-materialized-settler-fixture-v0",
    )

    tampered = deepcopy(witness)
    tampered["materialized_unit_integrity_sha256"] = "f" * 64
    tamper_error = None
    try:
        build_materialized_candidate_settlement(
            result_witness=tampered,
            field_dispositions=dispositions(),
            settlement_basis=bases(),
            settlement_actor_identity="independent-materialized-settler-fixture-v0",
        )
    except MaterializedResultSettlementError as exc:
        tamper_error = {
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    assertions = {
        "fixed_inputs_deterministic": settlement == settlement_repeat,
        "source_witness_preserved": witness == witness_before,
        "source_witness_id_bound": (
            settlement["source_witness_id"] == witness["witness_id"]
        ),
        "source_output_identity_bound": (
            settlement["source_raw_output_sha256"]
            == witness["raw_output_sha256"]
        ),
        "successor_lineage_bound": (
            settlement["source_successor_id"] == witness["successor_id"]
            and settlement["source_successor_integrity_sha256"]
            == witness["successor_integrity_sha256"]
        ),
        "work_spec_lineage_bound": (
            settlement["source_work_spec_id"] == witness["work_spec_id"]
            and settlement["source_work_spec_integrity_sha256"]
            == witness["work_spec_integrity_sha256"]
        ),
        "materialized_unit_lineage_bound": (
            settlement["source_materialized_work_item_id"]
            == witness["materialized_work_item_id"]
            and settlement["source_materialized_unit_integrity_sha256"]
            == witness["materialized_unit_integrity_sha256"]
        ),
        "admission_consumption_attempt_lineage_bound": (
            settlement["source_atomic_admission_id"]
            == witness["atomic_admission_id"]
            and settlement["source_consumption_id"]
            == witness["consumption_id"]
            and settlement["source_work_attempt_id"]
            == witness["work_attempt_id"]
        ),
        "field_level_dispositions_recorded": (
            settlement["accepted_fields"]
            == ["fixture_result", "work_item_id"]
            and settlement["held_fields"] == ["count"]
        ),
        "classification_source_external": (
            settlement["classification_source"] == "EXTERNALLY_SUPPLIED"
        ),
        "accepted_creates_no_qualification": (
            settlement["scientific_admission_created"] is False
            and settlement["qualification_effect"] == "NONE"
        ),
        "disposition_change_changes_settlement": (
            settlement["settlement_id"]
            != changed_settlement["settlement_id"]
        ),
        "tampered_chain_rejected": tamper_error is not None,
        "no_consequence_authority_execution_atlas_or_standing_effect": (
            settlement["external_consequence_effect"] == "NONE"
            and settlement["authority_effect"] == "NONE"
            and settlement["execution_effect"] == "NONE"
            and settlement["atlas_mutation_effect"] == "NONE"
            and settlement["scientific_standing_effect"] == "NONE"
        ),
    }

    observation = {
        "object_type": "MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EXACT_MATERIALIZED_SETTLEMENT_FIXTURE",
        "source_witness_id": witness["witness_id"],
        "successor_id": witness["successor_id"],
        "work_spec_id": witness["work_spec_id"],
        "materialized_unit_integrity_sha256": witness[
            "materialized_unit_integrity_sha256"
        ],
        "consumption_id": witness["consumption_id"],
        "settlement": settlement,
        "changed_disposition_settlement_id": changed_settlement["settlement_id"],
        "tamper_case": tamper_error,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, one immutable exact materialized-work "
            "result witness can receive externally supplied field-level candidate "
            "dispositions and explicit bases in one deterministic settlement record "
            "while conserving exact successor, work-spec, materialized-unit, "
            "admission, consumption, attempt, and output lineage. Candidate "
            "acceptance creates no qualification and settlement creates no external "
            "consequence, authority, execution, Atlas mutation, or scientific "
            "standing."
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
    print(f"[OK] settlement_id {settlement['settlement_id']}")
    print(
        "[OK] accepted_creates_no_qualification "
        + str(assertions["accepted_creates_no_qualification"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
