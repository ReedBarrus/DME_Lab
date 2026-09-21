#!/usr/bin/env python3
"""Execute the frozen LANE_LIFECYCLE_DISPOSITION_001 synthetic pressure exactly once."""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.lane_lifecycle_disposition_v0 import (  # noqa: E402
    AdministrationInvalid,
    LifecycleController,
    canonical_bytes,
    sha256_id,
)
from tools import lane_lifecycle_disposition_oracle_v0 as oracle  # noqa: E402

REQUIRED_CELL_ORDER = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I",
    "N1", "N2", "N3", "N4",
    "N6A", "N6B", "N6C", "N7A", "N7B",
    "N5A", "N5B", "N5C",
]

EXPECTED_TOP_LEVEL_COUNT = 21


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout.strip()


def verify_freeze(manifest: Mapping[str, Any]) -> None:
    for row in manifest["frozen_files"]:
        path = ROOT / row["path"]
        if not path.is_file():
            raise RuntimeError(f"freeze path missing: {row['path']}")
        observed = git_blob(path)
        if observed != row["git_blob"]:
            raise RuntimeError(
                f"freeze mismatch {row['path']}: expected {row['git_blob']} observed {observed}"
            )

    py = manifest["environment"]["python"]
    observed = f"{sys.version_info.major}.{sys.version_info.minor}"
    if observed != py:
        raise RuntimeError(f"python version mismatch: expected {py}, observed {observed}")

    if manifest["environment"].get("stdlib_only") is not True:
        raise RuntimeError("freeze must require stdlib_only=true")


def parse_path(path: str) -> Sequence[str]:
    return path.split(".")


def get_path(obj: Mapping[str, Any], path: str) -> Any:
    cur: Any = obj
    for key in parse_path(path):
        cur = cur[key]
    return cur


def set_path(obj: MutableMapping[str, Any], path: str, value: Any) -> None:
    parts = list(parse_path(path))
    cur: Any = obj
    for key in parts[:-1]:
        cur = cur[key]
    cur[parts[-1]] = value


def apply_input_mutation(base: Mapping[str, Any], mutation: Mapping[str, Any]) -> Dict[str, Any]:
    if mutation.get("op") != "replace":
        raise RuntimeError(f"unsupported input mutation: {mutation}")
    out = copy.deepcopy(base)
    path = mutation["path"]
    if "from" in mutation and get_path(out, path) != mutation["from"]:
        raise RuntimeError(
            f"mutation precondition mismatch at {path}: "
            f"expected {mutation['from']!r}, observed {get_path(out, path)!r}"
        )
    set_path(out, path, mutation.get("value"))
    return out


def apply_output_mutation(base: Mapping[str, Any], mutation: Mapping[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    op = mutation["op"]
    path = mutation["path"]
    parts = list(parse_path(path))
    cur: Any = out
    for key in parts[:-1]:
        cur = cur[key]
    if op == "delete_field":
        del cur[parts[-1]]
    elif op == "replace":
        cur[parts[-1]] = mutation.get("value")
    else:
        raise RuntimeError(f"unsupported output mutation: {mutation}")
    return out


def differing_leaf_paths(a: Any, b: Any, prefix: str = "") -> Sequence[str]:
    paths = []
    if type(a) is not type(b):
        return [prefix or "$"]
    if isinstance(a, dict):
        keys = sorted(set(a) | set(b))
        for key in keys:
            child = f"{prefix}.{key}" if prefix else key
            if key not in a or key not in b:
                paths.append(child)
            else:
                paths.extend(differing_leaf_paths(a[key], b[key], child))
        return paths
    if isinstance(a, list):
        if a != b:
            paths.append(prefix or "$")
        return paths
    if a != b:
        paths.append(prefix or "$")
    return paths


def input_identities(data: Mapping[str, Any]) -> Dict[str, Any]:
    identities: Dict[str, Any] = {}
    for key in sorted(data):
        value = data[key]
        if key == "standings":
            identities[key] = [
                {
                    "relation_type": row.get("relation_type"),
                    "identity": sha256_id(row),
                }
                for row in value
            ]
        else:
            identities[key] = sha256_id(value)
    identities["whole_input"] = sha256_id(data)
    return identities


def output_summary(output: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "requested_transition": output.get("requested_transition"),
        "selected_branch": output.get("selected_branch"),
        "predicates_consulted": output.get("predicates_consulted"),
        "admissible": output.get("admissible"),
        "blocking_predicate": output.get("blocking_predicate"),
        "resulting_state": output.get("resulting_state"),
    }


def receipt_ref(cell_id: str) -> str:
    return f"lane-lifecycle-synthetic-pressure-001/pressure_result.json#cell={cell_id}"


def run_branch_cell(
    cell: Mapping[str, Any],
    base: Mapping[str, Any],
    controller: LifecycleController,
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    observed = controller.evaluate_branch(copy.deepcopy(base))
    score = oracle.score_branch(cell["cell_id"], observed, expected)
    return {
        "CELL_ID": cell["cell_id"],
        "INPUT_OBJECT_IDENTITIES": input_identities(base),
        "REQUESTED_TRANSITION": observed.get("requested_transition"),
        "SELECTED_BRANCH": observed.get("selected_branch"),
        "PREDICATES_CONSULTED": observed.get("predicates_consulted"),
        "ADMISSIBILITY_RESULT": observed.get("admissible"),
        "BLOCKING_PREDICATE": observed.get("blocking_predicate"),
        "RESULTING_STATE": observed.get("resulting_state"),
        "D1_D3_RESULT": score["D1_D3"],
        "EXPECTED_RESULT": expected,
        "OBSERVED_RESULT": {"controller": output_summary(observed), "score": score},
        "PASS_FAIL": "PASS" if score["pass"] else "FAIL",
        "EXECUTION_RECEIPT_ARTIFACT_REF": receipt_ref(cell["cell_id"]),
    }


def run_invariant_group(
    cell: Mapping[str, Any],
    fixtures: Mapping[str, Any],
    controller: LifecycleController,
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    observed_sub = {}
    identities = {}
    for subcell in cell["subcells"]:
        data = copy.deepcopy(fixtures["invariant_cases"][subcell])
        identities[subcell] = input_identities(data)
        observed_sub[subcell] = controller.validate_resulting_state(data)
    observed = {"subcells": observed_sub}
    score = oracle.score_invariant_group(observed, expected)
    return {
        "CELL_ID": cell["cell_id"],
        "SUBCELLS": list(cell["subcells"]),
        "INPUT_OBJECT_IDENTITIES": identities,
        "REQUESTED_TRANSITION": None,
        "SELECTED_BRANCH": None,
        "PREDICATES_CONSULTED": {
            sub: row.get("predicates_consulted") for sub, row in observed_sub.items()
        },
        "ADMISSIBILITY_RESULT": None,
        "BLOCKING_PREDICATE": None,
        "RESULTING_STATE": None,
        "D1_D3_RESULT": score["D1_D3"],
        "EXPECTED_RESULT": expected,
        "OBSERVED_RESULT": {"controller": observed, "score": score},
        "PASS_FAIL": "PASS" if score["pass"] else "FAIL",
        "EXECUTION_RECEIPT_ARTIFACT_REF": receipt_ref(cell["cell_id"]),
    }


def run_adversarial(
    cell: Mapping[str, Any],
    base: Mapping[str, Any],
    controller: LifecycleController,
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    baseline = controller.evaluate_branch(copy.deepcopy(base))
    if not baseline.get("admissible"):
        raise RuntimeError(f"{cell['cell_id']} adversarial baseline not admissible")
    mutated = apply_output_mutation(baseline, cell["mutation"])
    score = oracle.detect_adversarial_violation(cell["cell_id"], mutated, baseline)
    expected_match = (
        score["status"] == expected.get("status")
        and score.get("violation") == expected.get("violation")
    )
    score = dict(score)
    score["expected_match"] = expected_match
    score["pass"] = bool(score["pass"] and expected_match)
    return {
        "CELL_ID": cell["cell_id"],
        "INPUT_OBJECT_IDENTITIES": input_identities(base),
        "REQUESTED_TRANSITION": baseline.get("requested_transition"),
        "SELECTED_BRANCH": baseline.get("selected_branch"),
        "PREDICATES_CONSULTED": baseline.get("predicates_consulted"),
        "ADMISSIBILITY_RESULT": baseline.get("admissible"),
        "BLOCKING_PREDICATE": baseline.get("blocking_predicate"),
        "RESULTING_STATE": mutated.get("resulting_state"),
        "D1_D3_RESULT": score["D1_D3"],
        "EXPECTED_RESULT": expected,
        "OBSERVED_RESULT": {
            "baseline_controller": output_summary(baseline),
            "adversarial_mutation": cell["mutation"],
            "mutated_output_identity": sha256_id(mutated),
            "score": score,
        },
        "PASS_FAIL": "PASS" if score["pass"] else "FAIL",
        "EXECUTION_RECEIPT_ARTIFACT_REF": receipt_ref(cell["cell_id"]),
    }


def run_reactivation(
    cell: Mapping[str, Any],
    fixtures: Mapping[str, Any],
    controller: LifecycleController,
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    data = copy.deepcopy(fixtures[cell["input_ref"]])
    observed = controller.evaluate_reactivation(data)
    score = oracle.score_reactivation(observed, expected)
    return {
        "CELL_ID": cell["cell_id"],
        "INPUT_OBJECT_IDENTITIES": input_identities(data),
        "REQUESTED_TRANSITION": None,
        "SELECTED_BRANCH": None,
        "PREDICATES_CONSULTED": observed.get("predicates_consulted"),
        "ADMISSIBILITY_RESULT": observed.get("admissible"),
        "BLOCKING_PREDICATE": observed.get("blocking_predicate"),
        "RESULTING_STATE": observed.get("resulting_state"),
        "D1_D3_RESULT": score["D1_D3"],
        "EXPECTED_RESULT": expected,
        "OBSERVED_RESULT": {"controller": observed, "score": score},
        "PASS_FAIL": "PASS" if score["pass"] else "FAIL",
        "EXECUTION_RECEIPT_ARTIFACT_REF": receipt_ref(cell["cell_id"]),
    }


def run_paired(
    cell: Mapping[str, Any],
    base: Mapping[str, Any],
    controller: LifecycleController,
    expected: Mapping[str, Any],
) -> Dict[str, Any]:
    baseline_input = copy.deepcopy(base)
    intervention_input = apply_input_mutation(base, cell["mutation"])
    diffs = list(differing_leaf_paths(baseline_input, intervention_input))
    expected_path = cell["mutation"]["path"]
    single_variable = diffs == [expected_path]
    if not single_variable:
        raise RuntimeError(
            f"{cell['cell_id']} not a single-variable intervention: {diffs}, expected {[expected_path]}"
        )

    baseline = controller.evaluate_branch(baseline_input)
    intervention = controller.evaluate_branch(intervention_input)

    if cell["target_predicate"] == "P04":
        score = oracle.score_dispatch_intervention(baseline, intervention, expected)
    else:
        score = oracle.score_guard_intervention(baseline, intervention, expected)

    score = dict(score)
    score["single_variable_intervention"] = single_variable
    score["diff_paths"] = diffs
    score["pass"] = bool(score["pass"] and single_variable)

    return {
        "CELL_ID": cell["cell_id"],
        "INPUT_OBJECT_IDENTITIES": {
            "baseline": input_identities(baseline_input),
            "intervention": input_identities(intervention_input),
            "changed_leaf_paths": diffs,
        },
        "REQUESTED_TRANSITION": {
            "baseline": baseline.get("requested_transition"),
            "intervention": intervention.get("requested_transition"),
        },
        "SELECTED_BRANCH": {
            "baseline": baseline.get("selected_branch"),
            "intervention": intervention.get("selected_branch"),
        },
        "PREDICATES_CONSULTED": {
            "baseline": baseline.get("predicates_consulted"),
            "intervention": intervention.get("predicates_consulted"),
        },
        "ADMISSIBILITY_RESULT": {
            "baseline": baseline.get("admissible"),
            "intervention": intervention.get("admissible"),
        },
        "BLOCKING_PREDICATE": intervention.get("blocking_predicate"),
        "RESULTING_STATE": {
            "baseline": baseline.get("resulting_state"),
            "intervention": intervention.get("resulting_state"),
        },
        "D1_D3_RESULT": score["D1_D3"],
        "EXPECTED_RESULT": expected,
        "OBSERVED_RESULT": {
            "baseline": output_summary(baseline),
            "intervention": output_summary(intervention),
            "score": score,
        },
        "PASS_FAIL": "PASS" if score["pass"] else "FAIL",
        "EXECUTION_RECEIPT_ARTIFACT_REF": receipt_ref(cell["cell_id"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--freeze",
        default="fixtures/lane_lifecycle_disposition_v0/EXECUTION_FREEZE_001.json",
    )
    parser.add_argument("--output", default="pressure_result.json")
    args = parser.parse_args()

    freeze_path = ROOT / args.freeze
    freeze = load_json(freeze_path)
    verify_freeze(freeze)

    fixtures = load_json(ROOT / freeze["fixture_set"]["path"])
    evaluation = load_json(ROOT / freeze["evaluation_key"]["path"])
    producer_registry = load_json(ROOT / freeze["producer_registry"]["path"])
    basis_catalog = load_json(ROOT / freeze["basis_catalog"]["path"])

    cells = fixtures["cells"]
    ids = [row["cell_id"] for row in cells]
    if ids != REQUIRED_CELL_ORDER:
        raise RuntimeError(f"cell order mismatch: {ids}")
    if len(cells) != EXPECTED_TOP_LEVEL_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TOP_LEVEL_COUNT} cells, found {len(cells)}")
    if set(evaluation["cells"]) != set(REQUIRED_CELL_ORDER):
        raise RuntimeError("evaluation key cell set does not exactly match required cell set")

    controller = LifecycleController(producer_registry, basis_catalog)
    receipts = []
    disposition = "QUALIFIED"
    failing_cell = None

    for cell in cells:
        cell_id = cell["cell_id"]
        expected = evaluation["cells"][cell_id]
        kind = cell["kind"]
        try:
            if kind == "branch":
                receipt = run_branch_cell(
                    cell, fixtures["bases"][cell["base"]], controller, expected
                )
            elif kind == "invariant_group":
                receipt = run_invariant_group(cell, fixtures, controller, expected)
            elif kind == "adversarial_output":
                receipt = run_adversarial(
                    cell, fixtures["bases"][cell["base"]], controller, expected
                )
            elif kind == "reactivation":
                receipt = run_reactivation(cell, fixtures, controller, expected)
            elif kind == "paired_intervention":
                receipt = run_paired(
                    cell, fixtures["bases"][cell["base"]], controller, expected
                )
            else:
                raise RuntimeError(f"unsupported cell kind: {kind}")
        except Exception as exc:
            receipt = {
                "CELL_ID": cell_id,
                "PASS_FAIL": "FAIL",
                "OBSERVED_RESULT": {
                    "exception_type": type(exc).__name__,
                    "exception": str(exc),
                },
                "EXPECTED_RESULT": expected,
                "EXECUTION_RECEIPT_ARTIFACT_REF": receipt_ref(cell_id),
            }

        receipts.append(receipt)
        if receipt.get("PASS_FAIL") != "PASS":
            disposition = "FRACTURE"
            failing_cell = cell_id
            break

    matrix = {
        "P01": {"COMPLETE": "N6A", "RELEASE": "N6B", "MARK_BLOCKED": "N6C"},
        "P02": {"COMPLETE": "N1", "RELEASE": "N2", "MARK_BLOCKED": "N3"},
        "P03": {"COMPLETE": "N7A", "RELEASE": "N7B", "MARK_BLOCKED": "N4"},
        "P04": {"COMPLETE": "N5A", "RELEASE": "N5B", "MARK_BLOCKED": "N5C"},
    }
    executed_ids = {row["CELL_ID"] for row in receipts if row.get("PASS_FAIL") == "PASS"}
    matrix_execution = {
        predicate: {
            branch: {
                "cell_id": cell_id,
                "executed_pass": cell_id in executed_ids,
            }
            for branch, cell_id in branches.items()
        }
        for predicate, branches in matrix.items()
    }

    result = {
        "object_type": "PRESSURE_RESULT",
        "object_id": "LANE_LIFECYCLE_DISPOSITION_001-SYNTHETIC_PRESSURE-001",
        "disposition": disposition,
        "failing_cell": failing_cell,
        "qualified_design_head": freeze["qualified_design_head"],
        "frozen_execution_head": freeze["apparatus_basis_head"],
        "execution_command": freeze["executable_command"],
        "environment": freeze["environment"],
        "frozen_identities": freeze["frozen_files"],
        "cell_order": REQUIRED_CELL_ORDER,
        "cell_receipts": receipts,
        "F11": {
            "no_third_input_category": True,
            "undeclared_semantic_input_influence": "NOT_OBSERVED" if disposition == "QUALIFIED" else "UNRESOLVED_AFTER_FAILURE",
        },
        "F12": {
            "source_guard_cells": ["N1", "N2", "N3", "N4", "N6A", "N6B", "N6C", "N7A", "N7B"],
        },
        "F13": {
            "dispatch_cells": ["N5A", "N5B", "N5C"],
        },
        "F14": {
            "matrix": matrix_execution,
            "covered_pass_count": sum(
                1
                for branches in matrix_execution.values()
                for row in branches.values()
                if row["executed_pass"]
            ),
            "required_count": 12,
        },
        "live_lane_effect": "NONE",
        "historical_lane_b_disposition": "NONE",
        "clean_extraction": "NONE",
        "merge": "NONE",
    }

    out_path = Path(args.output)
    out_path.write_bytes(canonical_bytes(result))
    print(json.dumps(result, sort_keys=True, indent=2))
    print(
        f"PRESSURE_DISPOSITION={disposition} "
        f"EXECUTED_RECEIPTS={len(receipts)} "
        f"F14={result['F14']['covered_pass_count']}/12"
    )
    return 0 if disposition == "QUALIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
