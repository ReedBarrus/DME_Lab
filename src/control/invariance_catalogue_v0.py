from __future__ import annotations

from typing import Any, Mapping


REQUIRED_TOP_LEVEL = {
    "object_type",
    "catalogue_entry_id",
    "standing",
    "relations",
    "qualified_scope",
    "tested_surfaces",
    "surface_bindings",
    "live_applicability_currentness",
    "reconstruction_use",
    "basis_handles",
    "known_nonclaims",
    "catalogue_authority_effect",
}


def validate_catalogue_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_TOP_LEVEL.difference(entry.keys()))
    if missing:
        raise ValueError(f"catalogue entry missing required fields: {', '.join(missing)}")

    tested = list(entry["tested_surfaces"])
    bindings = dict(entry["surface_bindings"])

    if set(tested) != set(bindings):
        raise ValueError("tested_surfaces must exactly match surface_bindings keys")

    if entry["catalogue_authority_effect"] != "NONE":
        raise ValueError("catalogue entry must not create authority")

    return {
        "catalogue_entry_id": entry["catalogue_entry_id"],
        "tested_surface_count": len(tested),
        "tested_surfaces": tested,
        "standing": entry["standing"],
        "live_applicability_currentness": entry["live_applicability_currentness"],
    }


def resolve_surface_binding(
    entry: Mapping[str, Any],
    *,
    surface_type: str,
) -> dict[str, Any]:
    summary = validate_catalogue_entry(entry)
    tested = set(entry["tested_surfaces"])

    common = {
        "object_type": "OPERATIONAL_INVARIANCE_CATALOGUE_LOOKUP_V0",
        "catalogue_entry_id": entry["catalogue_entry_id"],
        "requested_surface": surface_type,
        "relations": list(entry["relations"]),
        "standing": entry["standing"],
        "live_applicability_currentness": entry["live_applicability_currentness"],
        "basis_handles": list(entry["basis_handles"]),
        "known_nonclaims": list(entry["known_nonclaims"]),
        "catalogue_authority_effect": "NONE",
        "planning_effect": "NONE",
        "execution_effect": "NONE",
    }

    if surface_type not in tested:
        return {
            **common,
            "lookup_posture": "NO_QUALIFIED_BINDING",
            "surface_binding": None,
            "tested_surface_match": False,
            "live_application_authorized": False,
        }

    return {
        **common,
        "lookup_posture": "CATALOGUED_TESTED_BINDING",
        "surface_binding": dict(entry["surface_bindings"][surface_type]),
        "tested_surface_match": True,
        "live_application_authorized": False,
    }
