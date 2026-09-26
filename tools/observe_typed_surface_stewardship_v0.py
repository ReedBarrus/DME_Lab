#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.relational_change_steward_v0 import RelationObligations
from src.control.typed_surface_steward_v0 import (
    TypedRelationState,
    steward_typed_relation_change,
)

OUT = ROOT / "docs" / "evidence" / "for_planner" / "typed_surface_stewardship_v0_observation.json"

G18_PATH = ROOT / "docs" / "evidence" / "for_planner" / "evidence_producer_route_alignment_v0_observation.json"
G19_PATH = ROOT / "docs" / "evidence" / "for_planner" / "relational_change_stewardship_v0_observation.json"

EXPECTED = {
    "g18_witness": "9d6e627401c3c51b9cc30449d80f6c94a99711d7",
    "g19_witness": "5a9798384a1dcd7fe38bfdcd3406eed98306c98d",
    "g19_adjudication": "b22483a5ecf9551bfdf9c22834367db4082640a5",
    "g19_steward": "8dddd57779d2432dd87c92ce95056dee2be398b5",
    "typed_adapter": "0beec144cb64aaccb4b022ff707248b69d96c9da",
}

PATHS = {
    "g18_witness": "docs/evidence/for_planner/evidence_producer_route_alignment_v0_observation.json",
    "g19_witness": "docs/evidence/for_planner/relational_change_stewardship_v0_observation.json",
    "g19_adjudication": "docs/campaigns/relational_change_stewardship_001/pressure_runs/RELATIONAL_CHANGE_STEWARDSHIP_V0_ADJUDICATION_RESULT_001.md",
    "g19_steward": "src/control/relational_change_steward_v0.py",
    "typed_adapter": "src/control/typed_surface_steward_v0.py",
}


def git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    actual_blobs = {name: git_blob(path) for name, path in PATHS.items()}
    blob_checks = {name: actual_blobs[name] == EXPECTED[name] for name in EXPECTED}
    if not all(blob_checks.values()):
        raise SystemExit(f"frozen blob mismatch: {blob_checks}")

    g18 = load_json(G18_PATH)
    g19 = load_json(G19_PATH)

    generated_blob = g18["producer_run"]["generated_root_git_blob"]
    root_path = g18["producer"]["declared_output_path"]
    storage_path = g18["historical_evidence"]["relocated_path"]
    storage_blob = g18["historical_evidence"]["blob_after"]

    repository_before = TypedRelationState(
        surface_type="REPOSITORY_PRODUCER_ROUTE",
        endpoint={
            "output_present": False,
            "output_path": root_path,
            "output_blob": None,
        },
        counterpart={
            "storage_path": storage_path,
            "storage_blob": storage_blob,
        },
        edge={
            "relation_kind": "PRODUCES_TO",
            "declared_output_path": root_path,
            "storage_path": storage_path,
            "alignment": "MISALIGNED",
        },
    )
    repository_after = TypedRelationState(
        surface_type="REPOSITORY_PRODUCER_ROUTE",
        endpoint={
            "output_present": g18["producer_run"]["old_root_output_created"],
            "output_path": root_path,
            "output_blob": generated_blob,
        },
        counterpart={
            "storage_path": storage_path,
            "storage_blob": storage_blob,
        },
        edge={
            "relation_kind": "PRODUCES_TO",
            "declared_output_path": root_path,
            "storage_path": storage_path,
            "alignment": "MISALIGNED",
        },
    )

    repository = steward_typed_relation_change(
        relation_id="G20_REPOSITORY_PRODUCER_ROUTE",
        before=repository_before,
        after=repository_after,
        obligations=RelationObligations(
            endpoint="CHANGE",
            counterpart="PRESERVE",
            edge="PRESERVE",
            flow="PASS",
        ),
        flow_witness=(
            "FAIL"
            if g18["assembly"]["producer_output_route_migrated"] is False
            and g18["producer_run"]["old_root_output_created"] is True
            else "PASS"
        ),
    )

    c1 = next(case for case in g19["cases"] if case["case_id"] == "C1_COHERENT")
    c1_result = c1["result"]

    callable_before = TypedRelationState(
        surface_type="PYTHON_CALLABLE_INVOCATION",
        endpoint={
            "payload_kind": "RELATION_STATE_ENDPOINT",
            "endpoint_value": c1_result["before"]["endpoint"],
            "payload_shape": ["endpoint", "counterpart", "edge"],
        },
        counterpart={
            "callable_path": "src/control/relational_change_steward_v0.py",
            "symbol": "steward_relation_change",
            "code_blob": EXPECTED["g19_steward"],
        },
        edge={
            "relation_kind": "INVOKES",
            "binding_mode": "KEYWORD_CALL",
            "argument_names": [
                "relation_id",
                "before",
                "after",
                "obligations",
                "flow_witness",
            ],
            "return_coordinate": "closure_posture",
        },
    )
    callable_after = TypedRelationState(
        surface_type="PYTHON_CALLABLE_INVOCATION",
        endpoint={
            "payload_kind": "RELATION_STATE_ENDPOINT",
            "endpoint_value": c1_result["after"]["endpoint"],
            "payload_shape": ["endpoint", "counterpart", "edge"],
        },
        counterpart={
            "callable_path": "src/control/relational_change_steward_v0.py",
            "symbol": "steward_relation_change",
            "code_blob": EXPECTED["g19_steward"],
        },
        edge={
            "relation_kind": "INVOKES",
            "binding_mode": "KEYWORD_CALL",
            "argument_names": [
                "relation_id",
                "before",
                "after",
                "obligations",
                "flow_witness",
            ],
            "return_coordinate": "closure_posture",
        },
    )

    callable_case = steward_typed_relation_change(
        relation_id="G20_PYTHON_CALLABLE_INVOCATION",
        before=callable_before,
        after=callable_after,
        obligations=RelationObligations(
            endpoint="CHANGE",
            counterpart="PRESERVE",
            edge="PRESERVE",
            flow="PASS",
        ),
        flow_witness=c1_result["checks"]["flow_witness"],
    )

    repo_geometry = repository["before_geometry"]
    callable_geometry = callable_case["before_geometry"]

    abstract_roles_match = (
        repository["abstract_roles"]
        == callable_case["abstract_roles"]
        == ["endpoint", "counterpart", "edge", "flow"]
    )
    endpoint_fields_distinct = set(repo_geometry["endpoint_fields"]) != set(callable_geometry["endpoint_fields"])
    counterpart_fields_distinct = set(repo_geometry["counterpart_fields"]) != set(callable_geometry["counterpart_fields"])
    edge_fields_distinct = set(repo_geometry["edge_fields"]) != set(callable_geometry["edge_fields"])
    field_vocabularies_distinct = (
        endpoint_fields_distinct
        and counterpart_fields_distinct
        and edge_fields_distinct
    )

    checks = {
        "frozen_blobs_match": all(blob_checks.values()),
        "repository_surface_hold": repository["stewardship"]["closure_posture"] == "HOLD",
        "callable_surface_coherent": callable_case["stewardship"]["closure_posture"] == "COHERENT",
        "abstract_roles_match": abstract_roles_match,
        "field_vocabularies_distinct": field_vocabularies_distinct,
        "repository_surface_type_preserved": repository["surface_type"] == "REPOSITORY_PRODUCER_ROUTE",
        "callable_surface_type_preserved": callable_case["surface_type"] == "PYTHON_CALLABLE_INVOCATION",
        "source_effects_neutral": (
            repository["effects"]["surface_mutation_effect"] == "NONE"
            and callable_case["effects"]["surface_mutation_effect"] == "NONE"
        ),
    }

    observation = {
        "object_type": "TYPED_SURFACE_STEWARDSHIP_V0_OBSERVATION",
        "pressure_id": "TYPED_SURFACE_STEWARDSHIP_V0_PRESSURE_001",
        "frozen_basis": {
            "expected_blobs": EXPECTED,
            "actual_blobs": actual_blobs,
            "blob_checks": blob_checks,
        },
        "repository_surface": repository,
        "callable_surface": callable_case,
        "cross_surface": {
            "abstract_roles_match": abstract_roles_match,
            "endpoint_fields_distinct": endpoint_fields_distinct,
            "counterpart_fields_distinct": counterpart_fields_distinct,
            "edge_fields_distinct": edge_fields_distinct,
            "field_vocabularies_distinct": field_vocabularies_distinct,
            "same_abstract_stewardship_role_ne_same_operative_configuration_geometry": "YES",
            "typed_surface_binding_preserves_surface_specific_observation": "YES",
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "effects": {
            "relation_discovery_effect": "NONE",
            "source_mutation_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "Two exact digital specimens only: one repository producer-route "
            "surface reconstructed from the frozen G18 witness and one Python "
            "callable-invocation surface reconstructed from the frozen G19 witness. "
            "The pressure tests typed binding into the same abstract stewardship "
            "roles while preserving distinct surface geometry. No physical surface, "
            "universal schema, automatic relation discovery, planning activation, "
            "authority, execution, global invariance, or scientific standing is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] repository closure {repository['stewardship']['closure_posture']}")
    print(f"[OK] callable closure {callable_case['stewardship']['closure_posture']}")
    print(f"[OK] abstract roles match {abstract_roles_match}")
    print(f"[OK] field vocabularies distinct {field_vocabularies_distinct}")
    print(f"[OK] all_checks_pass {observation['all_checks_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
