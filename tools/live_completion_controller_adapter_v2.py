#!/usr/bin/env python3
"""Qualified semantic adapter candidate for the frozen Lane-A completion specimen.

Public operation:
    evaluate(repo_root)

The operation accepts no adjudicated predicates or controller-shaped carriers.
It reconstructs raw source state, derives P05/P06/P07/P08, projects the exact
controller input, records its identity, immediately invokes the exact
authoritative controller, and wraps the result without executing a transition.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

import lane_lifecycle_disposition_v0 as lifecycle
import live_completion_raw_evaluator_v1 as raw
import live_unit_completion_standing_producer_v1 as p07
import live_completion_blocker_status_producer_v1 as p08


class AdapterInvalid(RuntimeError):
    pass


CONTROLLER_PATH = "tools/lane_lifecycle_disposition_v0.py"
CONTROLLER_BLOB = "89ff5ffc6c3555bc31716735af6e93498d675ced"
LIFECYCLE_REGISTRY_PATH = "fixtures/lane_lifecycle_disposition_v0/producer_registry_v0.json"
LIFECYCLE_REGISTRY_BLOB = "6b469f82a4e9c12e9c6bb143a646ccaba393bedb"
LIFECYCLE_BASIS_PATH = "fixtures/lane_lifecycle_disposition_v0/basis_catalog_v0.json"
LIFECYCLE_BASIS_BLOB = "170795fc3638cca1fdf008b3a7e2b5746520f8c2"

FIX = Path("fixtures/live_completion_evidence_v1")
ADAPTER_FIX = Path("fixtures/live_completion_adapter_v0")
CONTRACT_PATH = ADAPTER_FIX / "PROJECTION_CONTRACT_001.json"


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AdapterInvalid(
            f"GIT_FAILURE:{' '.join(args)}:{proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def _blob(repo: Path, path: str) -> str:
    return _git(repo, "hash-object", path)


def _git_blob(repo: Path, ref: str, path: str) -> str:
    return _git(repo, "rev-parse", f"{ref}:{path}")


def _git_json(repo: Path, ref: str, path: str) -> dict[str, Any]:
    return json.loads(_git(repo, "show", f"{ref}:{path}"))


def _load(repo: Path, path: str | Path) -> dict[str, Any]:
    return json.loads((repo / path).read_text(encoding="utf-8"))


def _verify_ref(repo: Path, ref: str) -> dict[str, Any]:
    if ref.startswith("repo://"):
        path = ref.removeprefix("repo://")
        if not (repo / path).is_file():
            raise AdapterInvalid(f"UNRECOVERABLE_REF:{ref}")
        return {"ref": ref, "blob": _blob(repo, path)}
    if ref.startswith("git:") and "@" in ref:
        body, expected = ref.removeprefix("git:").rsplit("@", 1)
        commit, path = body.split(":", 1)
        actual = _git_blob(repo, commit, path)
        if actual != expected:
            raise AdapterInvalid(f"UNRECOVERABLE_REF:{ref}")
        return {"ref": ref, "blob": actual}
    raise AdapterInvalid(f"UNSUPPORTED_REF:{ref}")


def _verify_contract(repo: Path) -> dict[str, Any]:
    contract = _load(repo, CONTRACT_PATH)
    if contract.get("schema") != "LIVE_COMPLETION_ADAPTER_PROJECTION_CONTRACT_v0":
        raise AdapterInvalid("PROJECTION_CONTRACT_SCHEMA_INVALID")

    self_row = contract["adapter_implementation"]
    if self_row.get("path") != "tools/live_completion_controller_adapter_v2.py":
        raise AdapterInvalid("ADAPTER_PATH_NOT_PINNED")
    if _blob(repo, self_row["path"]) != self_row.get("blob"):
        raise AdapterInvalid("ADAPTER_IMPLEMENTATION_DRIFT")

    controller = contract["authoritative_controller"]
    if controller.get("path") != CONTROLLER_PATH or controller.get("blob") != CONTROLLER_BLOB:
        raise AdapterInvalid("CONTROLLER_CONTRACT_MISMATCH")
    if _blob(repo, CONTROLLER_PATH) != CONTROLLER_BLOB:
        raise AdapterInvalid("AUTHORITATIVE_CONTROLLER_DRIFT")

    if _blob(repo, LIFECYCLE_REGISTRY_PATH) != LIFECYCLE_REGISTRY_BLOB:
        raise AdapterInvalid("AUTHORITATIVE_CONTROLLER_REGISTRY_DRIFT")
    if _blob(repo, LIFECYCLE_BASIS_PATH) != LIFECYCLE_BASIS_BLOB:
        raise AdapterInvalid("AUTHORITATIVE_CONTROLLER_BASIS_DRIFT")

    for label, row in contract.get("pinned_repo_inputs", {}).items():
        if _blob(repo, row["path"]) != row["blob"]:
            raise AdapterInvalid(f"PIN_MISMATCH:{label}")

    for label, row in contract.get("pinned_git_inputs", {}).items():
        if _git_blob(repo, row["ref"], row["path"]) != row["blob"]:
            raise AdapterInvalid(f"GIT_PIN_MISMATCH:{label}")
    return contract


def _verify_relation_basis(
    repo: Path,
    basis_path: str,
    expected_basis_ref: str,
) -> dict[str, Any]:
    basis = _load(repo, basis_path)
    if basis.get("basis_ref") != expected_basis_ref:
        raise AdapterInvalid("RELATION_BASIS_REF_MISMATCH")
    _verify_ref(repo, str(basis.get("historical_claim_ref", "")))
    pinned = basis.get("pinned_inputs")
    if not isinstance(pinned, dict) or not pinned:
        raise AdapterInvalid("RELATION_BASIS_PINS_MISSING")
    for label, row in pinned.items():
        if _blob(repo, str(row.get("path"))) != row.get("blob"):
            raise AdapterInvalid(f"RELATION_BASIS_PIN_MISMATCH:{label}")
    return basis


def _controller_registry(
    repo: Path,
    qualification_registry: Mapping[str, Any],
) -> dict[str, Any]:
    base = _load(repo, LIFECYCLE_REGISTRY_PATH)
    result = copy.deepcopy(base)
    out = result.setdefault("qualified_producers", {})
    for key, row in qualification_registry.get("qualified_producers", {}).items():
        if row.get("status") != "QUALIFIED":
            raise AdapterInvalid(f"RUNTIME_PRODUCER_NOT_QUALIFIED:{key}")
        out[key] = {
            "relation_types": list(row.get("relation_types", [])),
            "qualification_ref": row.get("qualification_receipt_path"),
        }
    return result


def _controller_basis(repo: Path) -> dict[str, Any]:
    base = _load(repo, LIFECYCLE_BASIS_PATH)
    result = copy.deepcopy(base)
    objects = result.setdefault("basis_objects", {})
    objects[p07.BASIS_REF] = _verify_relation_basis(
        repo, str(FIX / "P07_RELATION_BASIS_001.json"), p07.BASIS_REF
    )
    objects[p08.BASIS_REF] = _verify_relation_basis(
        repo, str(FIX / "P08_RELATION_BASIS_001.json"), p08.BASIS_REF
    )
    return result


def _standing(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "relation_type": row["relation_type"],
        "standing": row["standing"],
        "basis_ref": row["basis_ref"],
        "producer": row["producer"],
        "version": row["version"],
    }


def _derive(repo: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    frozen = _load(repo, FIX / "FROZEN_LANE_A_SPECIMEN.json")
    binding = _load(repo, FIX / "RAW_LIVE_WORK_BINDING.json")
    criterion = _load(repo, FIX / "RAW_COMPLETION_CRITERION.json")
    evidence = _load(repo, FIX / "RAW_WORK_EVIDENCE.json")
    scope = _load(repo, FIX / "RAW_BLOCKER_SCOPE.json")
    registry = _load(repo, FIX / "PRODUCER_QUALIFICATION_REGISTRY_002.json")

    _verify_relation_basis(
        repo, str(FIX / "P07_RELATION_BASIS_001.json"), p07.BASIS_REF
    )
    _verify_relation_basis(
        repo, str(FIX / "P08_RELATION_BASIS_001.json"), p08.BASIS_REF
    )

    historical_claim = _git_json(
        repo, str(frozen["lane_a_head"]), str(frozen["lane_a_claim_path"])
    )
    historical_manifest = _git_json(
        repo, str(frozen["lane_a_head"]), str(frozen["lane_a_manifest_path"])
    )

    p05_result = raw.derive_p05(repo, frozen, binding)
    p06_result = raw.derive_p06(repo, frozen, binding, criterion, evidence)
    p07_result = p07.produce(repo, registry, binding, p05_result, p06_result)
    p08_result = p08.produce(
        repo, registry, frozen, binding, criterion, evidence, scope
    )

    if p05_result.get("status") != "MATCHES":
        raise AdapterInvalid("P05_NOT_MATCHED")
    if p06_result.get("status") != "SATISFIED":
        raise AdapterInvalid("P06_NOT_SATISFIED")
    if p07_result.get("status") != "ESTABLISHED":
        raise AdapterInvalid("P07_NOT_ESTABLISHED")
    if p08_result.get("status") != "ESTABLISHED":
        raise AdapterInvalid("P08_NOT_ESTABLISHED")

    p07_relation = p07_result["relation"]
    p08_relation = p08_result["relation"]
    if p07_relation.get("standing") != "QUALIFIED":
        raise AdapterInvalid("P07_STANDING_NOT_QUALIFIED")
    if p08_relation.get("standing") not in {
        "NONE_ESTABLISHED",
        "FORBIDS_COMPLETION",
    }:
        raise AdapterInvalid("P08_STANDING_INVALID")

    canonical_unit = p05_result["bounded_unit_id"]
    envelope_id = historical_claim["consequence_envelope_id"]
    outcome_map = contract["projection_rules"]["p06_outcome_mapping"]
    outcome = outcome_map.get(p06_result["status"])
    if outcome is None:
        raise AdapterInvalid("P06_OUTCOME_MAPPING_UNDEFINED")

    receipt_id = (
        contract["projection_rules"]["receipt_id_prefix"] + canonical_unit
    )
    controller_input = {
        "claim": {
            "claim_id": historical_claim["claim_id"],
            "status": historical_claim["status"],
            "envelope_id": envelope_id,
            "bounded_unit_id": canonical_unit,
        },
        "lane": {
            "status": historical_manifest["status"],
            "occupant_binding": historical_manifest["occupant_binding"],
        },
        "request": {"requested_transition": "COMPLETE"},
        "binding": {
            "envelope_id": envelope_id,
            "bounded_unit_id": canonical_unit,
        },
        "envelope": {
            "envelope_id": envelope_id,
            "bounded_unit_id": canonical_unit,
        },
        "criterion": {
            "required_receipt_id": receipt_id,
            "required_bounded_unit_id": canonical_unit,
            "required_outcome": outcome,
            "required_upstream_relations": [
                {
                    "relation_type": "UNIT_COMPLETION_STANDING",
                    "standing": "QUALIFIED",
                }
            ],
        },
        "receipt": {
            "receipt_id": receipt_id,
            "bounded_unit_id": canonical_unit,
            "outcome": outcome,
        },
        "standings": [
            _standing(p07_relation),
            _standing(p08_relation),
        ],
    }

    # Frozen projection invariants.
    if controller_input["claim"]["envelope_id"] != historical_claim["consequence_envelope_id"]:
        raise AdapterInvalid("ENVELOPE_PROJECTION_INVALID")
    if any(
        controller_input[path]["bounded_unit_id"] != canonical_unit
        for path in ("claim", "binding", "envelope", "receipt")
    ):
        raise AdapterInvalid("UNIT_PROJECTION_INVALID")
    if controller_input["criterion"]["required_bounded_unit_id"] != canonical_unit:
        raise AdapterInvalid("UNIT_PROJECTION_INVALID")
    if controller_input["criterion"]["required_outcome"] != outcome:
        raise AdapterInvalid("OUTCOME_PROJECTION_INVALID")
    if controller_input["receipt"]["outcome"] != outcome:
        raise AdapterInvalid("OUTCOME_PROJECTION_INVALID")

    historical_ref = (
        f"git:{frozen['lane_a_head']}:{frozen['lane_a_claim_path']}"
        f"@{frozen['lane_a_claim_blob']}"
    )
    _verify_ref(repo, historical_ref)

    return {
        "frozen": frozen,
        "historical_claim_ref": historical_ref,
        "historical_claim_object": historical_claim,
        "controller_claim_projection": copy.deepcopy(controller_input["claim"]),
        "controller_input": controller_input,
        "controller_input_digest": _digest(controller_input),
        "relations": {
            "P05": p05_result,
            "P06": p06_result,
            "P07": p07_result,
            "P08": p08_result,
        },
        "qualification_registry": registry,
    }


def _invoke_atomic(
    repo: Path,
    derived: Mapping[str, Any],
) -> dict[str, Any]:
    """Immediately invoke exact controller with the exact locally projected object.

    No projection object, callback, hook, or mutation function is accepted from
    the caller. The pre-invocation digest and post-return digest must match.
    """
    controller_input = derived["controller_input"]
    recorded_digest = derived["controller_input_digest"]
    if _digest(controller_input) != recorded_digest:
        raise AdapterInvalid("PROJECTED_INPUT_DIGEST_MISMATCH_PRE_INVOKE")

    controller = lifecycle.LifecycleController(
        _controller_registry(repo, derived["qualification_registry"]),
        _controller_basis(repo),
    )

    # The next consequential call consumes the same local object whose digest was
    # just verified. There is no caller callback or return between these lines.
    result = controller.evaluate_branch(controller_input)

    if _digest(controller_input) != recorded_digest:
        raise AdapterInvalid("PROJECTED_INPUT_MUTATED_DURING_INVOKE")
    return result


def evaluate(repo_root: str | Path) -> dict[str, Any]:
    """Run the bounded adapter operation.

    This is intentionally the only public adapter operation. It accepts only a
    repository root; all semantic inputs are reconstructed from pinned basis.
    """
    repo = Path(repo_root).resolve()
    contract = _verify_contract(repo)
    derived = _derive(repo, contract)
    raw_controller_result = _invoke_atomic(repo, derived)

    controller_claim_projection_returned = raw_controller_result.get(
        "historical_claim"
    )
    controller_result = copy.deepcopy(raw_controller_result)
    controller_result.pop("historical_claim", None)

    if controller_claim_projection_returned != derived["controller_claim_projection"]:
        raise AdapterInvalid("CONTROLLER_CLAIM_PROJECTION_RETURN_MISMATCH")

    return {
        "adapter_contract_id": contract["contract_id"],
        "adapter_implementation_blob": contract["adapter_implementation"]["blob"],
        "authoritative_controller": {
            "path": CONTROLLER_PATH,
            "blob": CONTROLLER_BLOB,
        },
        "historical_claim_ref": derived["historical_claim_ref"],
        "historical_claim_object": derived["historical_claim_object"],
        "controller_claim_projection": derived["controller_claim_projection"],
        "controller_input_digest": derived["controller_input_digest"],
        "controller_input_projection": copy.deepcopy(derived["controller_input"]),
        "derived_relations": copy.deepcopy(derived["relations"]),
        "controller_result": controller_result,
        "controller_returned_claim_projection": controller_claim_projection_returned,
        "transition_executed": False,
        "lane_mutation": "NONE",
        "claim_mutation": "NONE",
        "occupant_mutation": "NONE",
        "merge_effect": "NONE",
    }


def public_signature() -> str:
    return str(inspect.signature(evaluate))
