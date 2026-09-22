#!/usr/bin/env python3
"""Execute the bounded A-K qualification for LIVE_COMPLETION_EVIDENCE_001."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from live_completion_raw_evaluator_v0 import (
    AdministrationInvalid,
    derive_p05,
    derive_p06,
)
import live_unit_completion_standing_producer_v0 as p07_producer
import live_completion_blocker_status_producer_v0 as p08_producer


ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "live_completion_evidence_v0"


def load(name: str) -> dict[str, Any]:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def recoverable(ref: str) -> bool:
    if ref.startswith("repo://"):
        return (ROOT / ref.removeprefix("repo://")).is_file()
    if ref.startswith("git:") and "@" in ref:
        body, expected_blob = ref.removeprefix("git:").rsplit("@", 1)
        commit, path = body.split(":", 1)
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", f"{commit}:{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return proc.returncode == 0 and proc.stdout.strip() == expected_blob
    return False


def relation_candidate_valid(
    relation: Mapping[str, Any],
    binding: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    synthetic_basis: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if synthetic_basis is not None:
        unit = synthetic_basis.get("unit_id")
        if unit != binding.get("work_unit_id"):
            return {
                "status": "REJECT",
                "reason": "LIVE_SUBJECT_IDENTITY_MISMATCH",
            }

    key = f"{relation.get('producer')}@{relation.get('version')}"
    row = registry.get("producer_candidates", {}).get(key)
    if not row or relation.get("relation_type") not in row.get("relation_types", []):
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "PRODUCER_VERSION_NOT_QUALIFIED",
        }
    if not recoverable(str(relation.get("basis_ref", ""))):
        return {
            "status": "NOT_ESTABLISHED",
            "reason": "BASIS_REF_UNRECOVERABLE",
        }
    return {"status": "ESTABLISHED", "reason": "CANDIDATE_RELATION_IDENTITY_VALID"}


def forbidden_raw_answer_fields() -> dict[str, list[str]]:
    forbidden = {"completion", "complete", "satisfied", "admissible", "lifecycle_answer"}
    files = [
        "FROZEN_LANE_A_SPECIMEN.json",
        "RAW_LIVE_WORK_BINDING.json",
        "RAW_COMPLETION_CRITERION.json",
        "RAW_WORK_EVIDENCE.json",
        "RAW_BLOCKER_SCOPE.json",
    ]
    findings: dict[str, list[str]] = {}

    def walk(value: Any, path: str, out: list[str]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in forbidden:
                    out.append(f"{path}.{key}" if path else key)
                walk(child, f"{path}.{key}" if path else key, out)
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                walk(child, f"{path}[{idx}]", out)

    for name in files:
        out: list[str] = []
        walk(load(name), "", out)
        findings[name] = out
    return findings


def _exception_observation(fn) -> dict[str, Any]:
    try:
        value = fn()
    except AdministrationInvalid as exc:
        return {"status": "ADMINISTRATION_INVALID", "reason": str(exc)}
    return {"status": "NO_EXCEPTION", "value": value}


def evaluate() -> dict[str, Any]:
    frozen = load("FROZEN_LANE_A_SPECIMEN.json")
    binding = load("RAW_LIVE_WORK_BINDING.json")
    criterion = load("RAW_COMPLETION_CRITERION.json")
    evidence = load("RAW_WORK_EVIDENCE.json")
    scope = load("RAW_BLOCKER_SCOPE.json")
    cells = load("PRESSURE_CELLS_A_K.json")["cells"]
    expected = load("EVALUATION_KEY.json")["expected"]
    registry = load("PRODUCER_CANDIDATES.json")

    p05 = derive_p05(ROOT, frozen, binding)
    p06 = derive_p06(ROOT, frozen, binding, criterion, evidence)

    # A
    observed: dict[str, dict[str, Any]] = {
        "A": {"P05": p05["status"]},
    }

    # B
    b_binding = copy.deepcopy(binding)
    b_binding["claim_id"] = cells["B"]["mutation"]["value"]
    observed["B"] = {"P05": derive_p05(ROOT, frozen, b_binding)["status"]}

    # C
    c_evidence = copy.deepcopy(evidence)
    c_evidence["lane_head"] = cells["C"]["mutation"]["value"]
    observed["C"] = _exception_observation(
        lambda: derive_p06(ROOT, frozen, binding, criterion, c_evidence)
    )

    # D
    d = derive_p06(ROOT, frozen, binding, None, evidence)
    observed["D"] = {"P06": d["status"], "reason": d["reason"]}

    # E
    e = relation_candidate_valid(cells["E"]["relation"], binding, registry)
    observed["E"] = {"P07": e["status"], "reason": e["reason"]}

    # F
    f = relation_candidate_valid(
        cells["F"]["relation"],
        binding,
        registry,
        synthetic_basis=cells["F"]["basis"],
    )
    observed["F"] = f

    # Producer identity/negative qualification checks.
    p07_positive = p07_producer.produce(
        ROOT, registry, binding, p05, p06
    )
    p07_tampered_registry = copy.deepcopy(registry)
    p07_tampered_registry["producer_candidates"][
        "LIVE_UNIT_COMPLETION_STANDING_PRODUCER@v0"
    ]["implementation_blob"] = "0" * 40
    p07_tampered = p07_producer.produce(
        ROOT, p07_tampered_registry, binding, p05, p06
    )

    # G
    g = p08_producer.produce(ROOT, registry, scope, None)
    observed["G"] = {"P08": g["status"], "reason": g["reason"]}

    # H / I
    h = p08_producer.produce(
        ROOT, registry, scope, cells["H"]["blocker_evaluations"]
    )
    i = p08_producer.produce(
        ROOT, registry, scope, cells["I"]["blocker_evaluations"]
    )
    observed["H"] = {"P08": h["relation"]["standing"]}
    observed["I"] = {"P08": i["relation"]["standing"]}

    p08_tampered_registry = copy.deepcopy(registry)
    p08_tampered_registry["producer_candidates"][
        "LIVE_COMPLETION_BLOCKER_STATUS_PRODUCER@v0"
    ]["implementation_blob"] = "0" * 40
    p08_tampered = p08_producer.produce(
        ROOT,
        p08_tampered_registry,
        scope,
        cells["I"]["blocker_evaluations"],
    )
    partial = dict(cells["I"]["blocker_evaluations"])
    partial.pop(next(iter(partial)))
    p08_partial = p08_producer.produce(ROOT, registry, scope, partial)

    p07_qualified = (
        p07_positive.get("status") == "ESTABLISHED"
        and p07_positive.get("relation", {}).get("standing") == "QUALIFIED"
        and p07_tampered.get("status") == "NOT_ESTABLISHED"
        and observed["E"]["P07"] == "NOT_ESTABLISHED"
        and observed["F"]["status"] == "REJECT"
    )
    p08_qualified = (
        observed["G"]["P08"] == "NOT_ESTABLISHED"
        and observed["H"]["P08"] == "FORBIDS_COMPLETION"
        and observed["I"]["P08"] == "NONE_ESTABLISHED"
        and p08_tampered.get("status") == "NOT_ESTABLISHED"
        and p08_partial.get("status") == "NOT_ESTABLISHED"
    )

    # J: composition only. No lifecycle controller call or state mutation.
    p01_p04 = cells["J"]["p01_p04"]
    composition_ok = (
        p01_p04 == {
            "P01": True,
            "P02": True,
            "P03": "WARRANT:FIRST_BOUNDED_REAL_WORK_TWO_LANE_TRIAL-LANE_A-001:LANE_A:WORKSHOP:INVOCATION-001",
            "P04": "COMPLETE",
        }
        and p05["status"] == "MATCHES"
        and p06["status"] == "SATISFIED"
        and p07_qualified
        and p08_qualified
        and p07_positive["relation"]["relation_type"] == "UNIT_COMPLETION_STANDING"
        and p07_positive["relation"]["standing"] == "QUALIFIED"
        and i["relation"]["relation_type"] == "COMPLETION_BLOCKER_STATUS"
        and i["relation"]["standing"] == "NONE_ESTABLISHED"
    )
    observed["J"] = {
        "composition": "COMPLETE_EVALUABLE" if composition_ok else "NOT_EVALUABLE",
        "transition_executed": False,
    }

    # K
    k_criterion = copy.deepcopy(criterion)
    k_criterion["criterion_basis_commit"] = cells["K"]["mutation"]["value"]
    observed["K"] = _exception_observation(
        lambda: derive_p06(ROOT, frozen, binding, k_criterion, evidence)
    )

    # Expected-vector subset comparison.
    cell_checks: dict[str, bool] = {}
    for cell_id, exp in expected.items():
        obs = observed[cell_id]
        cell_checks[cell_id] = all(obs.get(key) == value for key, value in exp.items())

    basis_refs = [
        binding["source_warrant_ref"],
        binding["completion_criterion_ref"],
        binding["work_evidence_bundle_ref"],
        criterion["criterion_basis_ref"],
        scope["criterion_ref"],
        *scope["required_source_refs"],
        p07_positive["relation"]["basis_ref"] if p07_positive.get("relation") else "",
        i["relation"]["basis_ref"] if i.get("relation") else "",
    ]
    basis_recovery = {ref: recoverable(ref) for ref in basis_refs}

    raw_forbidden = forbidden_raw_answer_fields()

    result = {
        "object_type": "BOUNDED_QUALIFICATION_EVIDENCE",
        "object_id": "LIVE_COMPLETION_EVIDENCE_001-QUALIFICATION-001",
        "base": "f36261e17790b853a91c81bc2f7d0e63e8ee8436",
        "frozen_specimen": {
            "lane_a": frozen["lane_a_head"],
            "lane_b": frozen["lane_b_head"],
        },
        "implementation_blobs": {
            "raw_evaluator": git_blob("tools/live_completion_raw_evaluator_v0.py"),
            "p07_producer": git_blob("tools/live_unit_completion_standing_producer_v0.py"),
            "p08_producer": git_blob("tools/live_completion_blocker_status_producer_v0.py"),
        },
        "fixture_sha256": {
            name: sha256_file(FIX / name)
            for name in [
                "FROZEN_LANE_A_SPECIMEN.json",
                "RAW_LIVE_WORK_BINDING.json",
                "RAW_COMPLETION_CRITERION.json",
                "RAW_WORK_EVIDENCE.json",
                "RAW_BLOCKER_SCOPE.json",
                "PRODUCER_CANDIDATES.json",
                "PRESSURE_CELLS_A_K.json",
                "EVALUATION_KEY.json",
            ]
        },
        "raw_derivation": {"P05": p05, "P06": p06},
        "producer_qualification": {
            "P07": {
                "pass": p07_qualified,
                "positive": p07_positive,
                "tampered_identity": p07_tampered,
            },
            "P08": {
                "pass": p08_qualified,
                "missing_evaluations": g,
                "blocker_positive": h,
                "blocker_clear": i,
                "tampered_identity": p08_tampered,
                "partial_scope": p08_partial,
            },
        },
        "basis_recovery": basis_recovery,
        "raw_fixture_forbidden_answer_fields": raw_forbidden,
        "cells": observed,
        "cell_checks": cell_checks,
        "pass": (
            all(cell_checks.values())
            and p07_qualified
            and p08_qualified
            and all(basis_recovery.values())
            and all(not hits for hits in raw_forbidden.values())
            and observed["J"]["composition"] == "COMPLETE_EVALUABLE"
            and observed["J"]["transition_executed"] is False
        ),
        "lifecycle_effect": "NONE",
        "lane_mutation": "NONE",
        "merge_effect": "NONE",
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    result = evaluate()
    data = pretty_bytes(result)
    if args.output:
        Path(args.output).write_bytes(data)
    else:
        print(data.decode("utf-8"), end="")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
