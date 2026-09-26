#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.invariance_catalogue_carrier_reconstructor_v0 import (
    UNRESOLVED,
    reconstruct_catalogue_carrier,
)

OUT = ROOT / "docs" / "evidence" / "for_planner" / "invariance_catalogue_carrier_reconstruction_v0_observation.json"

CARRIER_PATH = ROOT / "docs" / "campaigns" / "invariance_catalogue_001" / "specimens" / "G20_OPERATIONAL_CATALOGUE_ENTRY_V0.json"

EXPECTED_BLOBS = {
    "control_carrier": (
        "docs/campaigns/invariance_catalogue_001/specimens/G20_OPERATIONAL_CATALOGUE_ENTRY_V0.json",
        "8e67e8aca3ff71d1512e008196f905fffd82bbd2",
    ),
    "g21_adjudication": (
        "docs/campaigns/invariance_catalogue_001/pressure_runs/OPERATIONAL_INVARIANCE_CATALOGUE_V0_ADJUDICATION_RESULT_001.md",
        "204988eac6d1161a06e1e26250565dc303c62c77",
    ),
    "reconstructor": (
        "src/control/invariance_catalogue_carrier_reconstructor_v0.py",
        "7d19a07ca1c8bc8d53ff175955f1128fb6e2a4de",
    ),
    "horizon": (
        "docs/campaigns/invariance_catalogue_carrier_reconstruction_001/HORIZON_SELECTION_G22_V0.md",
        "82fd28c98eea50892fca0388f95d1213759a3be2",
    ),
    "contract": (
        "docs/campaigns/invariance_catalogue_carrier_reconstruction_001/G22_CONTRACT_V0.md",
        "b6440a52ff4746fb9cb6199e517b9537a9f59216",
    ),
}

REQUESTED_SURFACES = [
    "REPOSITORY_PRODUCER_ROUTE",
    "PYTHON_CALLABLE_INVOCATION",
    "UNTESTED_SURFACE_SENTINEL",
]

SINGLE_ABLATIONS = {
    "A1_REMOVE_OBJECT_TYPE": ["object_type"],
    "A2_REMOVE_CATALOGUE_ENTRY_ID": ["catalogue_entry_id"],
    "A3_REMOVE_QUALIFIED_SCOPE": ["qualified_scope"],
    "A4_REMOVE_TESTED_SURFACES": ["tested_surfaces"],
    "A5_REMOVE_RECONSTRUCTION_USE": ["reconstruction_use"],
    "A6_REMOVE_CATALOGUE_AUTHORITY_EFFECT": ["catalogue_authority_effect"],
    "A7_REMOVE_STOPPED": ["stopped"],
    "B1_REMOVE_RELATIONS": ["relations"],
    "B2_REMOVE_STANDING": ["standing"],
    "B3_REMOVE_SURFACE_BINDINGS": ["surface_bindings"],
    "B4_REMOVE_LIVE_CURRENTNESS": ["live_applicability_currentness"],
    "B5_REMOVE_BASIS_HANDLES": ["basis_handles"],
    "B6_REMOVE_KNOWN_NONCLAIMS": ["known_nonclaims"],
    "C1_REMOVE_SCOPE_AND_TESTED_SURFACES": ["qualified_scope", "tested_surfaces"],
}


def git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def canonical_bytes(obj: object) -> int:
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def exact_required_target(control_carrier: dict) -> dict:
    return {
        "relations": deepcopy(control_carrier["relations"]),
        "standing": control_carrier["standing"],
        "live_applicability_currentness": control_carrier["live_applicability_currentness"],
        "basis_handles": deepcopy(control_carrier["basis_handles"]),
        "known_nonclaims": deepcopy(control_carrier["known_nonclaims"]),
        "queries": {
            "REPOSITORY_PRODUCER_ROUTE": {
                "lookup_posture": "CATALOGUED_TESTED_BINDING",
                "surface_binding": deepcopy(
                    control_carrier["surface_bindings"]["REPOSITORY_PRODUCER_ROUTE"]
                ),
                "tested_surface_match": True,
                "live_application_authorized": False,
            },
            "PYTHON_CALLABLE_INVOCATION": {
                "lookup_posture": "CATALOGUED_TESTED_BINDING",
                "surface_binding": deepcopy(
                    control_carrier["surface_bindings"]["PYTHON_CALLABLE_INVOCATION"]
                ),
                "tested_surface_match": True,
                "live_application_authorized": False,
            },
            "UNTESTED_SURFACE_SENTINEL": {
                "lookup_posture": "NO_QUALIFIED_BINDING",
                "surface_binding": None,
                "tested_surface_match": False,
                "live_application_authorized": False,
            },
        },
    }


def compare_required(reconstruction: dict, target: dict) -> dict:
    checks = {
        "relations": reconstruction["relations"] == target["relations"],
        "standing": reconstruction["standing"] == target["standing"],
        "live_applicability_currentness": (
            reconstruction["live_applicability_currentness"]
            == target["live_applicability_currentness"]
        ),
        "basis_handles": reconstruction["basis_handles"] == target["basis_handles"],
        "known_nonclaims": reconstruction["known_nonclaims"] == target["known_nonclaims"],
    }

    for surface, expected in target["queries"].items():
        actual = reconstruction["queries"][surface]
        checks[f"{surface}.lookup_posture"] = (
            actual["lookup_posture"] == expected["lookup_posture"]
        )
        checks[f"{surface}.surface_binding"] = (
            actual["surface_binding"] == expected["surface_binding"]
        )
        checks[f"{surface}.tested_surface_match"] = (
            actual["tested_surface_match"] == expected["tested_surface_match"]
        )
        checks[f"{surface}.live_application_authorized"] = (
            actual["live_application_authorized"]
            == expected["live_application_authorized"]
        )

    return checks


def run_variant(control: dict, target: dict, variant_id: str, removed: list[str]) -> dict:
    carrier = deepcopy(control)
    for key in removed:
        carrier.pop(key, None)

    reconstruction = reconstruct_catalogue_carrier(
        carrier,
        requested_surfaces=REQUESTED_SURFACES,
    )
    checks = compare_required(reconstruction, target)
    equivalent = all(checks.values())

    losses = sorted(name for name, passed in checks.items() if not passed)

    return {
        "variant_id": variant_id,
        "removed_coordinates": removed,
        "carrier_size_bytes": canonical_bytes(carrier),
        "size_delta_bytes_from_control": canonical_bytes(carrier) - canonical_bytes(control),
        "reconstruction": reconstruction,
        "required_checks": checks,
        "classification": (
            "RECONSTRUCTION_EQUIVALENT"
            if equivalent
            else "RECONSTRUCTION_LOSS"
        ),
        "loss_coordinates": losses,
    }


def main() -> int:
    if OUT.exists():
        raise SystemExit(f"remove existing {OUT.relative_to(ROOT)} first")

    actual_blobs = {
        name: git_blob(path)
        for name, (path, _) in EXPECTED_BLOBS.items()
    }
    blob_checks = {
        name: actual_blobs[name] == expected
        for name, (_, expected) in EXPECTED_BLOBS.items()
    }
    if not all(blob_checks.values()):
        raise SystemExit(f"frozen blob mismatch: {blob_checks}")

    control_carrier = json.loads(CARRIER_PATH.read_text(encoding="utf-8"))
    target = exact_required_target(control_carrier)

    control = run_variant(
        control_carrier,
        target,
        "A0_CONTROL",
        [],
    )

    variants = [
        run_variant(control_carrier, target, variant_id, removed)
        for variant_id, removed in SINGLE_ABLATIONS.items()
    ]

    by_id = {v["variant_id"]: v for v in variants}

    expected_equivalent = {
        "A1_REMOVE_OBJECT_TYPE",
        "A2_REMOVE_CATALOGUE_ENTRY_ID",
        "A3_REMOVE_QUALIFIED_SCOPE",
        "A4_REMOVE_TESTED_SURFACES",
        "A5_REMOVE_RECONSTRUCTION_USE",
        "A6_REMOVE_CATALOGUE_AUTHORITY_EFFECT",
        "A7_REMOVE_STOPPED",
    }
    expected_loss = {
        "B1_REMOVE_RELATIONS",
        "B2_REMOVE_STANDING",
        "B3_REMOVE_SURFACE_BINDINGS",
        "B4_REMOVE_LIVE_CURRENTNESS",
        "B5_REMOVE_BASIS_HANDLES",
        "B6_REMOVE_KNOWN_NONCLAIMS",
        "C1_REMOVE_SCOPE_AND_TESTED_SURFACES",
    }

    expectation_checks = {
        "control_equivalent": control["classification"] == "RECONSTRUCTION_EQUIVALENT",
        "expected_equivalent_set": all(
            by_id[v]["classification"] == "RECONSTRUCTION_EQUIVALENT"
            for v in expected_equivalent
        ),
        "expected_loss_set": all(
            by_id[v]["classification"] == "RECONSTRUCTION_LOSS"
            for v in expected_loss
        ),
        "paired_scope_loss_is_untested_refusal": (
            "UNTESTED_SURFACE_SENTINEL.lookup_posture"
            in by_id["C1_REMOVE_SCOPE_AND_TESTED_SURFACES"]["loss_coordinates"]
        ),
        "single_scope_ablation_preserves_refusal": (
            by_id["A3_REMOVE_QUALIFIED_SCOPE"]["reconstruction"]["queries"]
            ["UNTESTED_SURFACE_SENTINEL"]["lookup_posture"]
            == "NO_QUALIFIED_BINDING"
        ),
        "single_tested_surfaces_ablation_preserves_refusal": (
            by_id["A4_REMOVE_TESTED_SURFACES"]["reconstruction"]["queries"]
            ["UNTESTED_SURFACE_SENTINEL"]["lookup_posture"]
            == "NO_QUALIFIED_BINDING"
        ),
    }

    observation = {
        "object_type": "INVARIANCE_CATALOGUE_CARRIER_RECONSTRUCTION_LOAD_V0_OBSERVATION",
        "pressure_id": "INVARIANCE_CATALOGUE_CARRIER_RECONSTRUCTION_LOAD_V0_PRESSURE_001",
        "frozen_basis": {
            "expected_blobs": {
                name: expected
                for name, (_, expected) in EXPECTED_BLOBS.items()
            },
            "actual_blobs": actual_blobs,
            "blob_checks": blob_checks,
        },
        "control_carrier_size_bytes": canonical_bytes(control_carrier),
        "required_reconstruction_target": target,
        "control": control,
        "ablations": variants,
        "expectation_checks": expectation_checks,
        "all_expectations_match": all(expectation_checks.values()),
        "candidate_findings": {
            "task_relative_removable_single_coordinates": sorted(
                variant_id
                for variant_id in expected_equivalent
                if by_id[variant_id]["classification"] == "RECONSTRUCTION_EQUIVALENT"
            ),
            "task_relative_load_bearing_ablations": sorted(
                variant_id
                for variant_id in expected_loss
                if by_id[variant_id]["classification"] == "RECONSTRUCTION_LOSS"
            ),
            "single_coordinate_redundancy_ne_absence_of_distributed_reconstruction_load": "YES",
            "operational_carrier_load_is_task_relative": "YES",
        },
        "effects": {
            "catalogue_mutation_effect": "NONE",
            "source_mutation_effect": "NONE",
            "safe_deletion_effect": "NONE",
            "final_schema_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One ablation study over the exact G21 candidate operational entry and "
            "one declared bounded reconstruction target. Passing an ablation means "
            "only that the removed coordinate was not individually required for this "
            "target under this reconstructor and preserved alternate coordinates. "
            "Failing an ablation means only that the removed coordinate or coordinate "
            "set carried load for this target. No global uselessness, global necessity, "
            "final schema, safe deletion, quantitative performance benefit, live "
            "applicability, planning activation, authority, execution, global "
            "invariance, or scientific standing is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] control {control['classification']}")
    for variant in variants:
        print(f"[OK] {variant['variant_id']} -> {variant['classification']}")
    print(
        "[OK] paired scope/tested-surfaces loss coordinates "
        f"{by_id['C1_REMOVE_SCOPE_AND_TESTED_SURFACES']['loss_coordinates']}"
    )
    print(f"[OK] all_expectations_match {observation['all_expectations_match']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
