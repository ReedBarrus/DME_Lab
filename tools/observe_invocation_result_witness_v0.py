#!/usr/bin/env python3
"""Observe exact consumed invocation return -> immutable result witness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.coordination import workcycle_v0 as wc
from src.coordination.admitted_authority_consumption_v0 import (
    consume_admitted_authority_once,
)
from src.coordination.verified_authority_admission_v0 import (
    successor_authority_coordinates,
    try_verified_authority_atomic_admission,
)
from src.observation.invocation_result_witness_v0 import (
    InvocationResultWitnessError,
    build_invocation_result_witness,
)
from src.runtime.local_authority_consumption_v0 import LocalAuthorityStateStore


OUT = ROOT / "invocation_result_witness_observation.json"


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def control_on() -> dict:
    return {
        "workflow_enabled": True,
        "campaign_enabled": True,
        "seat_work_enabled": True,
        "wake_requested": True,
        "auto_continuation_limit": 1,
    }


def successor() -> dict:
    return wc.seal_object(
        {
            "object_type": "SUCCESSOR_CANDIDATE_V1",
            "campaign_id": "WORKCYCLE_STABILIZATION_001",
            "parent_work_item_id": "W-PARENT",
            "basis_id": "B-H-OPERATE-001",
            "operative_frame_ref": "FRAME-H-OPERATE-001",
            "successor_posture": "RESOLVE_LOAD_BEARING_GAP",
            "reconciliation_identity": "a" * 64,
            "next_pressure_basis": "pressure-result-witness",
            "successor_id": "successor:sha256:" + "a" * 64,
            "candidate_posture": "PROPOSED_NOT_ADMITTED",
            "selection_basis": "active basis has one admissible load-bearing pressure",
            "claim_ceiling": "disposable fixture",
            "work_admission_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def envelope_for(candidate: dict) -> dict:
    coordinates = successor_authority_coordinates(candidate)
    return {
        "object_type": "LOCAL_MODEL_INVOCATION_AUTHORITY_ENVELOPE_V0",
        "capability_id": "CAP.RESULT.WITNESS.A",
        "approval_id": "APP.RESULT.WITNESS.A",
        "principal_id": "CODEX_PRINCIPAL_001",
        "request_sha256": coordinates["request_sha256"],
        "input_sha256": coordinates["input_sha256"],
        "model": "fixture/not-a-model",
        "endpoint_identity": "disposable-fixture-endpoint",
        "executor_sha256": "3" * 64,
        "policy_sha256": "4" * 64,
        "use_limit": 1,
        "remaining_uses": 1,
        "status": "ACTIVE",
        "issued_at": "2026-09-25T00:00:00Z",
        "expires_at": None,
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(
            "invocation_result_witness_observation.json already exists; "
            "move/remove it before a fresh observation"
        )

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        candidate = successor()
        envelope = envelope_for(candidate)
        store = LocalAuthorityStateStore(root / "authority")
        store.issue(envelope)

        admission = try_verified_authority_atomic_admission(
            store_dir=root / "atomic",
            authority_store=store,
            authority_envelope=envelope,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            successor_candidate=candidate,
            work_attempt_id="ATTEMPT-RESULT-WITNESS",
            seat_id="LABBOIB",
            occupant_id="occupant-ATTEMPT-RESULT-WITNESS",
            wake_generation=1,
            dependency_satisfied=True,
            frame_current=True,
            no_hold=True,
            control=control_on(),
            initial_budget=wc.new_budget(campaign_id="WORKCYCLE_STABILIZATION_001"),
        )
        if admission["admitted"] is not True:
            raise RuntimeError(f"admission fixture failed: {admission}")

        ticks = iter([
            "2026-09-25T00:00:01Z",
            "2026-09-25T00:00:02Z",
        ])
        raw_output = {
            "fixture_result": "SUCCESS",
            "observed_value": 17,
            "nested": {"stable": True},
        }
        consumed = consume_admitted_authority_once(
            composition_receipt=admission["receipt"],
            successor_candidate=candidate,
            authority_envelope=envelope,
            attempting_principal_id="CODEX_PRINCIPAL_001",
            authority_store=store,
            invoke=lambda: raw_output,
            clock=lambda: next(ticks),
        )
        if consumed["consumed"] is not True:
            raise RuntimeError(f"consumption fixture failed: {consumed}")

        limitations = [
            "callback return does not prove an external-world consequence",
            "no semantic interpretation is performed",
            "no settlement is performed",
        ]
        witness = build_invocation_result_witness(
            consumption_receipt=consumed["receipt"],
            raw_output=consumed["invocation_result"],
            adapter_identity="disposable-callback-adapter-v0",
            observer_limitations=limitations,
            model_identity=None,
        )
        witness_repeat = build_invocation_result_witness(
            consumption_receipt=consumed["receipt"],
            raw_output=consumed["invocation_result"],
            adapter_identity="disposable-callback-adapter-v0",
            observer_limitations=limitations,
            model_identity=None,
        )
        changed_output_witness = build_invocation_result_witness(
            consumption_receipt=consumed["receipt"],
            raw_output={
                "fixture_result": "SUCCESS",
                "observed_value": 18,
                "nested": {"stable": True},
            },
            adapter_identity="disposable-callback-adapter-v0",
            observer_limitations=limitations,
            model_identity=None,
        )

        tampered_receipt = dict(consumed["receipt"])
        tampered_receipt["work_attempt_id"] = "ATTEMPT-TAMPERED"
        tamper_error = None
        try:
            build_invocation_result_witness(
                consumption_receipt=tampered_receipt,
                raw_output=consumed["invocation_result"],
                adapter_identity="disposable-callback-adapter-v0",
                observer_limitations=limitations,
                model_identity=None,
            )
        except InvocationResultWitnessError as exc:
            tamper_error = {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

    assertions = {
        "full_chain_reaches_result_witness": (
            admission["admitted"] is True
            and consumed["consumed"] is True
            and witness["object_type"] == "INVOCATION_RESULT_WITNESS_V0"
        ),
        "attempt_identity_bound": (
            witness["work_attempt_id"]
            == consumed["receipt"]["work_attempt_id"]
        ),
        "admission_identity_bound": (
            witness["atomic_admission_id"]
            == consumed["receipt"]["atomic_admission_id"]
        ),
        "consumption_identity_bound": (
            witness["consumption_id"]
            == consumed["receipt"]["consumption_id"]
        ),
        "raw_output_identity_bound": (
            witness["raw_output"] == raw_output
            and isinstance(witness["raw_output_sha256"], str)
            and len(witness["raw_output_sha256"]) == 64
        ),
        "fixed_inputs_deterministic": witness == witness_repeat,
        "output_change_changes_witness": (
            witness["raw_output_sha256"]
            != changed_output_witness["raw_output_sha256"]
            and witness["witness_id"]
            != changed_output_witness["witness_id"]
        ),
        "tampered_consumption_receipt_rejected": tamper_error is not None,
        "missing_model_identity_unresolved": (
            witness["model_identity"] is None
            and "model_identity" in witness["unresolved_fields"]
        ),
        "no_external_effect_inferred": witness["external_effect_inferred"] is False,
        "no_semantic_interpretation": witness["semantic_interpretation"] == "NONE",
        "no_settlement": witness["settlement_effect"] == "NONE",
        "no_authority_effect": witness["authority_effect"] == "NONE",
        "no_scientific_standing": (
            witness["scientific_standing_effect"] == "NONE"
        ),
    }

    observation = {
        "object_type": "INVOCATION_RESULT_WITNESS_OBSERVATION_V0",
        "repo_head": git_head(),
        "fixture_posture": "DISPOSABLE_SAME_PROCESS_FULL_CHAIN_RESULT_FIXTURE",
        "admission_receipt": admission["receipt"],
        "consumption_receipt": consumed["receipt"],
        "result_witness": witness,
        "changed_output_witness": changed_output_witness,
        "tamper_case": tamper_error,
        "assertions": assertions,
        "all_assertions_pass": all(assertions.values()),
        "claim_ceiling": (
            "Same-process disposable evidence that one exact admitted and "
            "one-shot-consumed work attempt can bind its raw callback return into "
            "one deterministic immutable result witness. The witness binds exact "
            "attempt/admission/consumption/output identities and infers no external "
            "consequence, semantic correctness, settlement, authority, or standing."
        ),
        "authority_effect": "NONE",
        "settlement_effect": "NONE",
        "production_execution_effect": "NONE",
        "model_invocation_effect": "NONE",
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
    print(f"[OK] result_witness_id {witness['witness_id']}")
    print(f"[OK] output_sha256 {witness['raw_output_sha256']}")
    print(f"[OK] external_effect_inferred {witness['external_effect_inferred']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
