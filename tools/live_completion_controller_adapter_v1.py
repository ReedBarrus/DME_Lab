#!/usr/bin/env python3
"""Adapter from repaired live completion evidence into the exact qualified lifecycle controller.

This module evaluates only. It never mutates lane state or executes a repository transition.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

import lane_lifecycle_disposition_v0 as lifecycle
import live_completion_raw_evaluator_v1 as raw
import live_unit_completion_standing_producer_v1 as p07
import live_completion_blocker_status_producer_v1 as p08

AUTHORITATIVE_CONTROLLER_BLOB = "89ff5ffc6c3555bc31716735af6e93498d675ced"
AUTHORITATIVE_PRODUCER_REGISTRY_BLOB = "6b469f82a4e9c12e9c6bb143a646ccaba393bedb"
AUTHORITATIVE_BASIS_CATALOG_BLOB = "170795fc3638cca1fdf008b3a7e2b5746520f8c2"

FIX = Path("fixtures/live_completion_evidence_v1")
LIFECYCLE_FIX = Path("fixtures/lane_lifecycle_disposition_v0")


class BridgeInvalid(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise BridgeInvalid(proc.stderr.strip() or "GIT_FAILURE")
    return proc.stdout.strip()


def _blob(repo: Path, path: str) -> str:
    return _git(repo, "hash-object", path)


def _git_blob(repo: Path, ref: str, path: str) -> str:
    return _git(repo, "rev-parse", f"{ref}:{path}")


def _git_json(repo: Path, ref: str, path: str) -> dict[str, Any]:
    return json.loads(_git(repo, "show", f"{ref}:{path}"))


def _load(repo: Path, path: str | Path) -> dict[str, Any]:
    return json.loads((repo / path).read_text(encoding="utf-8"))


def verify_authoritative_controller_surface(repo_root: str | Path) -> None:
    repo = Path(repo_root).resolve()
    checks = {
        "tools/lane_lifecycle_disposition_v0.py": AUTHORITATIVE_CONTROLLER_BLOB,
        str(LIFECYCLE_FIX / "producer_registry_v0.json"): AUTHORITATIVE_PRODUCER_REGISTRY_BLOB,
        str(LIFECYCLE_FIX / "basis_catalog_v0.json"): AUTHORITATIVE_BASIS_CATALOG_BLOB,
    }
    for path, expected in checks.items():
        if _blob(repo, path) != expected:
            raise BridgeInvalid(f"AUTHORITATIVE_SURFACE_DRIFT:{path}")


def verify_relation_basis(repo_root: str | Path, basis_path: str, expected_basis_ref: str) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    basis = _load(repo, basis_path)
    if basis.get("basis_ref") != expected_basis_ref:
        raise BridgeInvalid("BASIS_REF_MISMATCH")

    hist = str(basis.get("historical_claim_ref", ""))
    if not hist.startswith("git:") or "@" not in hist:
        raise BridgeInvalid("HISTORICAL_CLAIM_REF_INVALID")
    body, expected_blob = hist.removeprefix("git:").rsplit("@", 1)
    ref, path = body.split(":", 1)
    if _git_blob(repo, ref, path) != expected_blob:
        raise BridgeInvalid("HISTORICAL_CLAIM_REF_UNRECOVERABLE")

    pinned = basis.get("pinned_inputs", {})
    if not isinstance(pinned, dict) or not pinned:
        raise BridgeInvalid("PINNED_INPUTS_MISSING")
    for label, row in pinned.items():
        path = row.get("path")
        expected = row.get("blob")
        if not path or not expected:
            raise BridgeInvalid(f"PIN_INVALID:{label}")
        if _blob(repo, str(path)) != expected:
            raise BridgeInvalid(f"PIN_MISMATCH:{label}")
    return basis


def reproduce_relations(repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    frozen = _load(repo, FIX / "FROZEN_LANE_A_SPECIMEN.json")
    binding = _load(repo, FIX / "RAW_LIVE_WORK_BINDING.json")
    criterion = _load(repo, FIX / "RAW_COMPLETION_CRITERION.json")
    evidence = _load(repo, FIX / "RAW_WORK_EVIDENCE.json")
    scope = _load(repo, FIX / "RAW_BLOCKER_SCOPE.json")
    registry = _load(repo, FIX / "PRODUCER_QUALIFICATION_REGISTRY_002.json")

    verify_relation_basis(repo, str(FIX / "P07_RELATION_BASIS_001.json"), p07.BASIS_REF)
    verify_relation_basis(repo, str(FIX / "P08_RELATION_BASIS_001.json"), p08.BASIS_REF)

    p05_result = raw.derive_p05(repo, frozen, binding)
    p06_result = raw.derive_p06(repo, frozen, binding, criterion, evidence)
    p07_result = p07.produce(repo, registry, binding, p05_result, p06_result)
    p08_result = p08.produce(repo, registry, frozen, binding, criterion, evidence, scope)

    if p07_result.get("status") != "ESTABLISHED":
        raise BridgeInvalid("P07_NOT_REPRODUCED")
    if p08_result.get("status") != "ESTABLISHED":
        raise BridgeInvalid("P08_NOT_REPRODUCED")
    return {
        "P05": p05_result,
        "P06": p06_result,
        "P07": p07_result,
        "P08": p08_result,
    }


def _composed_controller_registry(repo: Path, qualification_registry: Mapping[str, Any]) -> dict[str, Any]:
    base = _load(repo, LIFECYCLE_FIX / "producer_registry_v0.json")
    result = copy.deepcopy(base)
    out = result.setdefault("qualified_producers", {})
    for key, row in qualification_registry.get("qualified_producers", {}).items():
        if row.get("status") != "QUALIFIED":
            raise BridgeInvalid(f"UNQUALIFIED_REGISTRY_ROW:{key}")
        out[key] = {
            "relation_types": list(row.get("relation_types", [])),
            "qualification_ref": row.get("qualification_receipt_path"),
        }
    return result


def _composed_basis_catalog(repo: Path) -> dict[str, Any]:
    base = _load(repo, LIFECYCLE_FIX / "basis_catalog_v0.json")
    result = copy.deepcopy(base)
    objects = result.setdefault("basis_objects", {})
    p07_basis = verify_relation_basis(repo, str(FIX / "P07_RELATION_BASIS_001.json"), p07.BASIS_REF)
    p08_basis = verify_relation_basis(repo, str(FIX / "P08_RELATION_BASIS_001.json"), p08.BASIS_REF)
    objects[p07.BASIS_REF] = p07_basis
    objects[p08.BASIS_REF] = p08_basis
    return result


def _controller_standing(row: Mapping[str, Any]) -> dict[str, Any]:
    """Project a qualified live relation onto the exact lifecycle standing membrane."""
    return {
        "relation_type": row.get("relation_type"),
        "standing": row.get("standing"),
        "basis_ref": row.get("basis_ref"),
        "producer": row.get("producer"),
        "version": row.get("version"),
    }


def build_controller_input(repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    verify_authoritative_controller_surface(repo)
    frozen = _load(repo, FIX / "FROZEN_LANE_A_SPECIMEN.json")
    binding = _load(repo, FIX / "RAW_LIVE_WORK_BINDING.json")
    relations = reproduce_relations(repo)

    claim = _git_json(repo, str(frozen["lane_a_head"]), str(frozen["lane_a_claim_path"]))
    manifest = _git_json(repo, str(frozen["lane_a_head"]), str(frozen["lane_a_manifest_path"]))

    unit = relations["P05"]["bounded_unit_id"]
    envelope_id = claim.get("consequence_envelope_id")
    receipt_id = f"live-completion-receipt:{unit}"
    p06_ok = relations["P06"].get("status") == "SATISFIED"

    return {
        "claim": {
            "claim_id": claim.get("claim_id"),
            "status": claim.get("status"),
            "envelope_id": envelope_id,
            "bounded_unit_id": unit,
        },
        "lane": {
            "status": manifest.get("status"),
            "occupant_binding": manifest.get("occupant_binding"),
        },
        "request": {"requested_transition": "COMPLETE"},
        "binding": {"envelope_id": envelope_id, "bounded_unit_id": unit},
        "envelope": {"envelope_id": envelope_id, "bounded_unit_id": unit},
        "criterion": {
            "required_receipt_id": receipt_id,
            "required_bounded_unit_id": unit,
            "required_outcome": "RAW_COMPLETION_TERMS_SATISFIED",
            "required_upstream_relations": [
                {"relation_type": "UNIT_COMPLETION_STANDING", "standing": "QUALIFIED"}
            ],
        },
        "receipt": {
            "receipt_id": receipt_id,
            "bounded_unit_id": unit,
            "outcome": "RAW_COMPLETION_TERMS_SATISFIED" if p06_ok else "RAW_COMPLETION_TERMS_NOT_SATISFIED",
        },
        "standings": [
            _controller_standing(relations["P07"]["relation"]),
            _controller_standing(relations["P08"]["relation"]),
        ],
    }


def evaluate_authoritative_controller(repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    verify_authoritative_controller_surface(repo)
    qualification_registry = _load(repo, FIX / "PRODUCER_QUALIFICATION_REGISTRY_002.json")
    controller = lifecycle.LifecycleController(
        _composed_controller_registry(repo, qualification_registry),
        _composed_basis_catalog(repo),
    )
    controller_input = build_controller_input(repo)
    result = controller.evaluate_branch(controller_input)
    return {
        "controller_blob": AUTHORITATIVE_CONTROLLER_BLOB,
        "controller_result": result,
        "controller_input": controller_input,
        "transition_executed": False,
        "live_lane_mutation": "NONE",
    }
