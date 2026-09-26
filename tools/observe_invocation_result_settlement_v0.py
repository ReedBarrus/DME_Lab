#!/usr/bin/env python3
"""Observe immutable result witness -> field-level candidate settlement."""

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

from src.coordination.invocation_result_settlement_v0 import (
    CANDIDATE_ACCEPTED,
    CANDIDATE_HELD,
    CANDIDATE_REJECTED,
    UNRESOLVED,
    ResultSettlementError,
    build_candidate_settlement,
)
from src.observation.invocation_result_witness_v0 import (
    build_invocation_result_witness,
)
from src.runtime.local_authority_consumption_v0 import canonical_sha256


OUT = ROOT / "invocation_result_settlement_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def consumption_receipt() -> dict:
    chain = {
        "composition_id": "verified-authority-atomic-admission:sha256:" + "1" * 64,
        "atomic_admission_id": "atomic-admission:sha256:" + "2" * 64,
        "successor_id": "successor:sha256:" + "3" * 64,
        "successor_integrity_sha256": "4" * 64,
        "authority_binding_id": "current-authority-binding:sha256:" + "5" * 64,
        "authority_consumption_receipt_id": "receipt:sha256:" + "6" * 64,
        "authority_reservation_id": "reservation:sha256:" + "7" * 64,
        "capability_id": "CAP.SETTLEMENT.OBS.001",
        "work_attempt_id": "ATTEMPT-SETTLEMENT-OBS-001",
    }
    return {
        "object_type": "ADMITTED_AUTHORITY_CONSUMPTION_RECEIPT_V0",
        **chain,
        "consumption_id": (
            "admitted-authority-consumption:sha256:" + canonical_sha256(chain)
        ),
        "authority_status_after": "CONSUMED",
        "authority_remaining_uses_after": 0,
        "authority_consumed": True,
        "invocation_performed": True,
        "invocation_count": 1,
        "authority_effect": "NONE",
        "consumption_effect": "CONSUMED_ONE_USE",
        "scientific_standing_effect": "NONE",
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "invocation_result_settlement_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    raw_output = {
        "supported_value": 17,
        "useful_but_unverified": "candidate",
        "overclaim": "external effect definitely happened",
        "unknown": None,
    }
    witness = build_invocation_result_witness(
        consumption_receipt=consumption_receipt(),
        raw_output=raw_output,
        adapter_identity="disposable-callback-adapter-v0",
        observer_limitations=[
            "callback return does not prove external consequence",
            "source witness performs no semantic interpretation",
            "source witness performs no settlement",
        ],
        model_identity=None,
    )
    witness_before = deepcopy(witness)

    field_dispositions = {
        "supported_value": CANDIDATE_ACCEPTED,
        "useful_but_unverified": CANDIDATE_HELD,
        "overclaim": CANDIDATE_REJECTED,
        "unknown": UNRESOLVED,
    }
    settlement_basis = {
        "supported_value": "field is explicitly retained in immutable witness",
        "useful_but_unverified": "candidate value lacks qualification",
        "overclaim": "source witness explicitly infers no external effect",
        "unknown": "supplied field remains unresolved",
    }

    settlement = build_candidate_settlement(
        result_witness=witness,
        field_dispositions=field_dispositions,
        settlement_basis=settlement_basis,
        settlement_actor_identity="independent-settler-fixture-v0",
    )
    settlement_repeat = build_candidate_settlement(
        result_witness=witness,
        field_dispositions=field_dispositions,
        settlement_basis=settlement_basis,
        settlement_actor_identity="independent-settler-fixture-v0",
    )

    changed_dispositions = dict(field_dispositions)
    changed_dispositions["useful_but_unverified"] = CANDIDATE_ACCEPTED
    changed_settlement = build_candidate_settlement(
        result_witness=witness,
        field_dispositions=changed_dispositions,
        settlement_basis=settlement_basis,
        settlement_actor_identity="independent-settler-fixture-v0",
    )

    tampered = deepcopy(witness)
    tampered["raw_output"]["supported_value"] = 999
    tamper_error = None
    try:
        build_candidate_settlement(
            result_witness=tampered,
            field_dispositions=field_dispositions,
            settlement_basis=settlement_basis,
            settlement_actor_identity="independent-settler-fixture-v0",
        )
    except ResultSettlementError as exc:
        tamper_error = {
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    assertions = {
        "source_witness_preserved": witness == witness_before,
        "settlement_binds_witness_id": (
            settlement["source_witness_id"] == witness["witness_id"]
        ),
        "settlement_binds_output_identity": (
            settlement["source_raw_output_sha256"]
            == witness["raw_output_sha256"]
        ),
        "field_dispositions_distinct": (
            settlement["accepted_fields"] == ["supported_value"]
            and settlement["held_fields"] == ["useful_but_unverified"]
            and settlement["rejected_fields"] == ["overclaim"]
            and settlement["unresolved_fields"] == ["unknown"]
        ),
        "fixed_inputs_deterministic": settlement == settlement_repeat,
        "disposition_change_changes_settlement_id": (
            settlement["settlement_id"]
            != changed_settlement["settlement_id"]
        ),
        "tampered_raw_output_rejected": tamper_error is not None,
        "classification_externally_supplied": (
            settlement["classification_source"] == "EXTERNALLY_SUPPLIED"
        ),
        "accepted_does_not_qualify": (
            "supported_value" in settlement["accepted_fields"]
            and settlement["qualification_effect"] == "NONE"
            and settlement["scientific_admission_created"] is False
        ),
        "no_authority_effect": settlement["authority_effect"] == "NONE",
        "no_execution_effect": settlement["execution_effect"] == "NONE",
        "no_atlas_mutation": settlement["atlas_mutation_effect"] == "NONE",
    }

    observation = {
        "object_type": "INVOCATION_RESULT_SETTLEMENT_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_FIELD_LEVEL_CANDIDATE_SETTLEMENT_FIXTURE",
        "source_result_witness": witness,
        "settlement": settlement,
        "changed_disposition_settlement": changed_settlement,
        "tamper_case": tamper_error,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Same-process disposable evidence that externally supplied field-level "
            "candidate dispositions and explicit bases can be bound deterministically "
            "to one immutable invocation result witness while preserving accepted, "
            "held, rejected, and unresolved as distinct classes. Candidate acceptance "
            "does not create qualification, authority, execution, external consequence, "
            "or Atlas mutation."
        ),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "atlas_mutation_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "stopped": "YES",
    }

    encoded = (
        json.dumps(observation, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    OUT.write_bytes(encoded)
    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] sha256 {sha256_bytes(encoded)}")
    print(f"[OK] all_assertions_pass {observation['all_assertions_pass']}")
    print(f"[OK] settlement_id {settlement['settlement_id']}")
    print(f"[OK] accepted_fields {len(settlement['accepted_fields'])}")
    print(f"[OK] held_fields {len(settlement['held_fields'])}")
    print(f"[OK] rejected_fields {len(settlement['rejected_fields'])}")
    print(f"[OK] unresolved_fields {len(settlement['unresolved_fields'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
