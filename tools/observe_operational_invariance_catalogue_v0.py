#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.control.invariance_catalogue_v0 import (
    resolve_surface_binding,
    validate_catalogue_entry,
)

OUT = ROOT / "docs" / "evidence" / "for_planner" / "operational_invariance_catalogue_v0_observation.json"

ENTRY_PATH = ROOT / "docs" / "campaigns" / "invariance_catalogue_001" / "specimens" / "G20_OPERATIONAL_CATALOGUE_ENTRY_V0.json"

EXPECTED_BLOBS = {
    "memory_compilation_method": (
        "docs/methods/MEMORY_COMPILATION_METHOD_v0.md",
        "cf3179d0cb2f25459c54112cf783b2479531452c",
    ),
    "g20_adjudication": (
        "docs/campaigns/typed_surface_stewardship_001/pressure_runs/TYPED_SURFACE_STEWARDSHIP_V0_ADJUDICATION_RESULT_001.md",
        "2445254a4b0738c269a627bde5c746c1e51227cc",
    ),
    "g20_pressure_result": (
        "docs/campaigns/typed_surface_stewardship_001/pressure_runs/TYPED_SURFACE_STEWARDSHIP_V0_PRESSURE_RESULT_001.md",
        "0f1fe776a9ed7ade963b4c5373071ddb304f6ee1",
    ),
    "g20_witness": (
        "docs/evidence/for_planner/typed_surface_stewardship_v0_observation.json",
        "a63e164636a34010105d307e5891cff62e26be73",
    ),
    "catalogue_entry": (
        "docs/campaigns/invariance_catalogue_001/specimens/G20_OPERATIONAL_CATALOGUE_ENTRY_V0.json",
        "8e67e8aca3ff71d1512e008196f905fffd82bbd2",
    ),
    "lookup_membrane": (
        "src/control/invariance_catalogue_v0.py",
        "ba74a02fbbcf3d9baa823310de09dd7082cd5aa3",
    ),
    "horizon": (
        "docs/campaigns/invariance_catalogue_001/HORIZON_SELECTION_G21_V0.md",
        "ee55fed8c8c243fdb2e87d39cb2893fd1a131ab4",
    ),
    "contract": (
        "docs/campaigns/invariance_catalogue_001/G21_CONTRACT_V0.md",
        "245e37841e8f67f5b9a0abca38973acc7b35026f",
    ),
}


def git_blob(path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


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

    # The candidate entry is the only rich semantic input read by this observer.
    # Frozen basis files above are identity-checked through Git but not opened.
    entry = json.loads(ENTRY_PATH.read_text(encoding="utf-8"))
    entry_summary = validate_catalogue_entry(entry)

    repository = resolve_surface_binding(
        entry,
        surface_type="REPOSITORY_PRODUCER_ROUTE",
    )
    callable_surface = resolve_surface_binding(
        entry,
        surface_type="PYTHON_CALLABLE_INVOCATION",
    )
    untested = resolve_surface_binding(
        entry,
        surface_type="UNTESTED_SURFACE_SENTINEL",
    )

    expected_nonclaims = set(entry["known_nonclaims"])

    checks = {
        "frozen_blobs_match": all(blob_checks.values()),
        "catalogue_entry_valid": entry_summary["tested_surface_count"] == 2,
        "repository_lookup_posture": repository["lookup_posture"] == "CATALOGUED_TESTED_BINDING",
        "repository_binding_present": repository["surface_binding"] is not None,
        "repository_closure_preserved": repository["surface_binding"]["observed_closure_posture"] == "HOLD",
        "repository_live_application_not_authorized": repository["live_application_authorized"] is False,
        "callable_lookup_posture": callable_surface["lookup_posture"] == "CATALOGUED_TESTED_BINDING",
        "callable_binding_present": callable_surface["surface_binding"] is not None,
        "callable_closure_preserved": callable_surface["surface_binding"]["observed_closure_posture"] == "COHERENT",
        "callable_live_application_not_authorized": callable_surface["live_application_authorized"] is False,
        "untested_lookup_posture": untested["lookup_posture"] == "NO_QUALIFIED_BINDING",
        "untested_binding_absent": untested["surface_binding"] is None,
        "untested_live_application_not_authorized": untested["live_application_authorized"] is False,
        "standing_preserved": all(
            item["standing"] == "MATCHED_BOUNDED_RELATION_NOT_LEDGER_PROMOTED"
            for item in (repository, callable_surface, untested)
        ),
        "live_currentness_preserved": all(
            item["live_applicability_currentness"]
            == "UNRESOLVED_BEYOND_FROZEN_G20_BASIS"
            for item in (repository, callable_surface, untested)
        ),
        "basis_handles_preserved": all(
            item["basis_handles"] == entry["basis_handles"]
            for item in (repository, callable_surface, untested)
        ),
        "nonclaims_preserved": all(
            set(item["known_nonclaims"]) == expected_nonclaims
            for item in (repository, callable_surface, untested)
        ),
        "neutral_effects": all(
            item["catalogue_authority_effect"] == "NONE"
            and item["planning_effect"] == "NONE"
            and item["execution_effect"] == "NONE"
            for item in (repository, callable_surface, untested)
        ),
    }

    observation = {
        "object_type": "OPERATIONAL_INVARIANCE_CATALOGUE_V0_OBSERVATION",
        "pressure_id": "OPERATIONAL_INVARIANCE_CATALOGUE_V0_PRESSURE_001",
        "frozen_basis": {
            "expected_blobs": {
                name: expected
                for name, (_, expected) in EXPECTED_BLOBS.items()
            },
            "actual_blobs": actual_blobs,
            "blob_checks": blob_checks,
        },
        "catalogue_entry_summary": entry_summary,
        "queries": {
            "repository_producer_route": repository,
            "python_callable_invocation": callable_surface,
            "untested_surface_sentinel": untested,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "rich_basis_content_reads": 0,
        "candidate_relations": {
            "catalogued_tested_binding_ne_live_applicability": "YES",
            "catalogue_index_ne_scientific_basis": "YES",
            "untested_surface_ne_inferred_binding": "YES",
            "compact_operational_entry_supports_tested_surface_routing_without_rich_basis_reopen": "YES",
        },
        "effects": {
            "catalogue_schema_finalization_effect": "NONE",
            "ledger_promotion_effect": "NONE",
            "live_applicability_effect": "NONE",
            "planning_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "claim_ceiling": (
            "One compact candidate catalogue entry indexing the exact matched G20 "
            "relation over two tested digital surfaces, plus one untested sentinel "
            "lookup. The observer reads the candidate entry and mechanically verifies "
            "frozen basis identities without opening rich G20 basis contents. "
            "No minimal-carrier claim, final catalogue schema, live applicability, "
            "safe deletion, automatic relation discovery, universal portability, "
            "planning activation, authority, execution, global invariance, or "
            "scientific standing is created."
        ),
        "stopped": "YES",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] wrote {OUT.relative_to(ROOT)}")
    print(f"[OK] repository lookup {repository['lookup_posture']}")
    print(f"[OK] callable lookup {callable_surface['lookup_posture']}")
    print(f"[OK] untested lookup {untested['lookup_posture']}")
    print(f"[OK] rich basis content reads {observation['rich_basis_content_reads']}")
    print(f"[OK] all_checks_pass {observation['all_checks_pass']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
