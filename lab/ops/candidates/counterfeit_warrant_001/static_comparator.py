"""Static causal-cut comparator for COUNTERFEIT_WARRANT_001.

This module performs structural comparison only. It must not call the experimental
evaluator or derive warrant validity/admissibility.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

ALLOWED_WARRANT_DIFFERENCE = "binding_sha256"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compare_warrant_objects(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    if set(a) != {"schema_version", "binding_sha256"}:
        raise ValueError("unexpected Condition A warrant shape")
    if set(b) != {"schema_version", "binding_sha256"}:
        raise ValueError("unexpected Condition B warrant shape")
    differing = sorted(k for k in a if a[k] != b[k])
    return {
        "same_schema": a["schema_version"] == b["schema_version"],
        "differing_fields": differing,
        "only_permitted_difference": differing == [ALLOWED_WARRANT_DIFFERENCE],
    }


def initialize_isolated_root(
    source_dir: Path,
    target_root: Path,
    warrant_path: Path,
    conductor: Any,
) -> dict[str, Any]:
    if target_root.exists():
        raise ValueError("target root must be fresh")
    (target_root / "lab/processes").mkdir(parents=True)
    (target_root / "lab/events").mkdir(parents=True)
    (target_root / "lab/state").mkdir(parents=True)
    (target_root / "specimen").mkdir(parents=True)

    shutil.copyfile(
        source_dir / "fixtures/process_fixture.json",
        target_root / "lab/processes/counterfeit_warrant_001.json",
    )
    for name in (
        "role_output_packet.json",
        "binding_tuple.json",
        "property_dependency_map.json",
    ):
        shutil.copyfile(source_dir / "fixtures" / name, target_root / "specimen" / name)
    shutil.copyfile(warrant_path, target_root / "specimen/routing_warrant.json")
    shutil.copyfile(source_dir / "evaluator.py", target_root / "specimen/evaluator.py")

    process = read_json(source_dir / "fixtures/process_fixture.json")
    event = {
        "event_type": "PROCESS_REGISTERED",
        "process_id": process["process_id"],
        "initial_phase": process["initial_phase"],
    }
    events = target_root / "lab/events/events.jsonl"
    conductor.append_event(events, event)
    paths = conductor.Paths(
        events,
        target_root / "lab/state/LAB_STATE_v0.json",
        target_root / "lab/processes",
    )
    projection = conductor.replay(paths)
    return {"paths": paths, "projection": projection}


def compare_initialized_roots(root_a: Path, root_b: Path) -> dict[str, Any]:
    identical = {}
    for rel in (
        "lab/processes/counterfeit_warrant_001.json",
        "lab/events/events.jsonl",
        "lab/state/LAB_STATE_v0.json",
        "specimen/role_output_packet.json",
        "specimen/binding_tuple.json",
        "specimen/property_dependency_map.json",
        "specimen/evaluator.py",
    ):
        identical[rel] = (root_a / rel).read_bytes() == (root_b / rel).read_bytes()

    wa = read_json(root_a / "specimen/routing_warrant.json")
    wb = read_json(root_b / "specimen/routing_warrant.json")
    warrant_diff = compare_warrant_objects(wa, wb)
    return {
        "identical_surfaces": identical,
        "all_required_surfaces_identical": all(identical.values()),
        "warrant_difference": warrant_diff,
    }
