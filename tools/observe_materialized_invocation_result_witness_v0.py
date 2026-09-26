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

from src.observation.materialized_invocation_result_witness_v0 import (
    MaterializedInvocationResultWitnessError,
    build_materialized_invocation_result_witness,
)
from tests.observation.test_materialized_invocation_result_witness_v0 import (
    valid_materialized_consumption,
)

OUT = ROOT / "materialized_invocation_result_witness_observation.json"


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
            "remove existing materialized_invocation_result_witness_observation.json first"
        )

    successor, spec, unit, receipt, raw = valid_materialized_consumption()

    limitations = [
        "callback return does not prove external consequence",
        "raw callback output is not semantically interpreted",
        "no settlement is performed",
        "model identity is unresolved unless explicitly supplied",
    ]
    witness = build_materialized_invocation_result_witness(
        consumption_receipt=receipt,
        raw_output=raw,
        adapter_identity="materialized-disposable-callback-adapter-v0",
        observer_limitations=limitations,
        model_identity=None,
    )
    witness_repeat = build_materialized_invocation_result_witness(
        consumption_receipt=receipt,
        raw_output=raw,
        adapter_identity="materialized-disposable-callback-adapter-v0",
        observer_limitations=limitations,
        model_identity=None,
    )
    changed_output_witness = build_materialized_invocation_result_witness(
        consumption_receipt=receipt,
        raw_output={**raw, "count": 2},
        adapter_identity="materialized-disposable-callback-adapter-v0",
        observer_limitations=limitations,
        model_identity=None,
    )

    tampered = deepcopy(receipt)
    tampered["materialized_unit_integrity_sha256"] = "f" * 64
    tamper_error = None
    try:
        build_materialized_invocation_result_witness(
            consumption_receipt=tampered,
            raw_output=raw,
            adapter_identity="materialized-disposable-callback-adapter-v0",
            observer_limitations=limitations,
            model_identity=None,
        )
    except MaterializedInvocationResultWitnessError as exc:
        tamper_error = {
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    assertions = {
        "fixed_inputs_deterministic": witness == witness_repeat,
        "successor_lineage_bound": (
            witness["successor_id"] == successor["successor_id"]
            and witness["successor_integrity_sha256"]
            == successor["integrity_sha256"]
        ),
        "work_spec_lineage_bound": (
            witness["work_spec_id"] == spec["work_spec_id"]
            and witness["work_spec_integrity_sha256"]
            == spec["integrity_sha256"]
        ),
        "materialized_unit_lineage_bound": (
            witness["materialized_work_item_id"]
            == unit["identity"]["work_item_id"]
            and witness["materialized_unit_integrity_sha256"]
            == unit["integrity_sha256"]
        ),
        "consumption_lineage_bound": (
            witness["consumption_id"] == receipt["consumption_id"]
            and witness["composition_id"] == receipt["composition_id"]
            and witness["atomic_admission_id"] == receipt["atomic_admission_id"]
            and witness["work_attempt_id"] == receipt["work_attempt_id"]
        ),
        "raw_output_preserved": witness["raw_output"] == raw,
        "raw_output_identity_bound": len(witness["raw_output_sha256"]) == 64,
        "output_change_changes_witness": (
            witness["raw_output_sha256"]
            != changed_output_witness["raw_output_sha256"]
            and witness["witness_id"] != changed_output_witness["witness_id"]
        ),
        "tampered_chain_rejected": tamper_error is not None,
        "missing_model_identity_preserved_unresolved": (
            witness["model_identity"] is None
            and "model_identity" in witness["unresolved_fields"]
        ),
        "no_interpretation_settlement_external_effect_or_standing": (
            witness["semantic_interpretation"] == "NONE"
            and witness["settlement_effect"] == "NONE"
            and witness["authority_effect"] == "NONE"
            and witness["execution_effect"] == "NONE"
            and witness["scientific_standing_effect"] == "NONE"
            and witness["external_effect_inferred"] is False
        ),
    }

    observation = {
        "object_type": "MATERIALIZED_INVOCATION_RESULT_WITNESS_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_EXACT_MATERIALIZED_RESULT_WITNESS_FIXTURE",
        "successor_id": successor["successor_id"],
        "work_spec_id": spec["work_spec_id"],
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "consumption_id": receipt["consumption_id"],
        "witness": witness,
        "changed_output_witness_id": changed_output_witness["witness_id"],
        "tamper_case": tamper_error,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "At the exact supplied source, one already-consumed exact "
            "materialized-work attempt can bind its exact raw callback return into "
            "one deterministic immutable result witness while conserving exact "
            "successor, work-spec, materialized-unit, admission, consumption, and "
            "attempt identities. Output mutation changes witness identity and "
            "chain tampering is rejected. Missing model identity remains explicitly "
            "unresolved. No semantic interpretation, settlement, external effect, "
            "execution standing, authority, or scientific standing is created."
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
    print(f"[OK] witness_id {witness['witness_id']}")
    print(f"[OK] raw_output_sha256 {witness['raw_output_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
