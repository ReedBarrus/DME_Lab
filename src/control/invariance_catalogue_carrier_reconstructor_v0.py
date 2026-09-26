from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

UNRESOLVED = "UNRESOLVED_FROM_CARRIER"


def _copy_or_unresolved(carrier: Mapping[str, Any], key: str) -> Any:
    if key not in carrier:
        return UNRESOLVED
    return deepcopy(carrier[key])


def _binding_domain_complete(carrier: Mapping[str, Any]) -> bool | None:
    bindings = carrier.get("surface_bindings")
    if not isinstance(bindings, Mapping):
        return None

    binding_keys = set(bindings.keys())

    tested = carrier.get("tested_surfaces")
    if isinstance(tested, Sequence) and not isinstance(tested, (str, bytes)):
        return set(tested) == binding_keys

    scope = carrier.get("qualified_scope")
    if isinstance(scope, Mapping):
        count = scope.get("tested_surface_count")
        if isinstance(count, int):
            return count == len(binding_keys)

    return None


def reconstruct_catalogue_carrier(
    carrier: Mapping[str, Any],
    *,
    requested_surfaces: Sequence[str],
) -> dict[str, Any]:
    bindings = carrier.get("surface_bindings")
    bindings_mapping = bindings if isinstance(bindings, Mapping) else None
    domain_complete = _binding_domain_complete(carrier)

    queries: dict[str, Any] = {}
    for surface in requested_surfaces:
        if bindings_mapping is None:
            posture = UNRESOLVED
            binding = UNRESOLVED
            tested_match: bool | str = UNRESOLVED
        elif surface in bindings_mapping:
            posture = "CATALOGUED_TESTED_BINDING"
            binding = deepcopy(bindings_mapping[surface])
            tested_match = True
        elif domain_complete is True:
            posture = "NO_QUALIFIED_BINDING"
            binding = None
            tested_match = False
        else:
            posture = UNRESOLVED
            binding = UNRESOLVED
            tested_match = UNRESOLVED

        queries[surface] = {
            "lookup_posture": posture,
            "surface_binding": binding,
            "tested_surface_match": tested_match,
            "live_application_authorized": False,
        }

    return {
        "object_type": "INVARIANCE_CATALOGUE_CARRIER_RECONSTRUCTION_V0",
        "relations": _copy_or_unresolved(carrier, "relations"),
        "standing": _copy_or_unresolved(carrier, "standing"),
        "live_applicability_currentness": _copy_or_unresolved(
            carrier, "live_applicability_currentness"
        ),
        "basis_handles": _copy_or_unresolved(carrier, "basis_handles"),
        "known_nonclaims": _copy_or_unresolved(carrier, "known_nonclaims"),
        "binding_domain_complete": domain_complete
        if domain_complete is not None
        else UNRESOLVED,
        "queries": queries,
        "catalogue_authority_effect": "NONE",
        "planning_effect": "NONE",
        "execution_effect": "NONE",
    }
