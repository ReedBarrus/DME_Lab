"""G10 partial declared-basis retention profile."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc

OBJECT_TYPE = "PARTIAL_BASIS_RETENTION_PROFILE_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"

LOCAL_POSTURES = {
    "REQUIRED",
    "UNRESOLVED",
    "NOT_REQUIRED_FOR_DECLARED_HORIZON",
}


class PartialBasisRetentionProfileError(ValueError):
    pass


def _blob(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise PartialBasisRetentionProfileError(
            f"{field} must be a Git blob SHA"
        )
    return value


def _aggregate(postures: list[str]) -> str:
    if "REQUIRED" in postures:
        return "REQUIRED"
    if "UNRESOLVED" in postures:
        return "UNRESOLVED"
    return "NOT_REQUIRED_FOR_DECLARED_SCOPE"


def build_partial_basis_retention_profile(
    *,
    source_g9_result_blob_sha: str,
    source_g9_witness_blob_sha: str,
    basis_id: str,
    horizon_requirements: Mapping[str, str],
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    _blob(source_g9_result_blob_sha, "source_g9_result_blob_sha")
    _blob(source_g9_witness_blob_sha, "source_g9_witness_blob_sha")

    if not isinstance(basis_id, str) or not basis_id.strip():
        raise PartialBasisRetentionProfileError("basis_id must be non-empty")
    if representation_source != "EXTERNALLY_SUPPLIED":
        raise PartialBasisRetentionProfileError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )
    if not isinstance(horizon_requirements, Mapping) or not horizon_requirements:
        raise PartialBasisRetentionProfileError(
            "horizon_requirements must be a non-empty mapping"
        )

    normalized: dict[str, str] = {}
    for horizon_id, posture in horizon_requirements.items():
        if not isinstance(horizon_id, str) or not horizon_id.strip():
            raise PartialBasisRetentionProfileError(
                "horizon id must be non-empty"
            )
        if posture not in LOCAL_POSTURES:
            raise PartialBasisRetentionProfileError(
                "unsupported local hot requirement"
            )
        normalized[horizon_id.strip()] = posture

    required = sorted(
        h for h, p in normalized.items() if p == "REQUIRED"
    )
    unresolved = sorted(
        h for h, p in normalized.items() if p == "UNRESOLVED"
    )
    not_required = sorted(
        h
        for h, p in normalized.items()
        if p == "NOT_REQUIRED_FOR_DECLARED_HORIZON"
    )

    profile = {
        "required_members": required,
        "unresolved_members": unresolved,
        "not_required_members": not_required,
        "n_required": len(required),
        "n_unresolved": len(unresolved),
        "n_not_required": len(not_required),
        "basis_size": len(normalized),
    }

    material = {
        "distinction_id": DISTINCTION_ID,
        "source_g9_result_blob_sha": source_g9_result_blob_sha,
        "source_g9_witness_blob_sha": source_g9_witness_blob_sha,
        "basis_id": basis_id.strip(),
        "declared_horizon_requirements": dict(sorted(normalized.items())),
        "retention_profile": profile,
        "declared_scope_hot_requirement": _aggregate(
            list(normalized.values())
        ),
        "exterior_posture": "UNRESOLVED",
        "global_ecology_hot_requirement": "UNRESOLVED",
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "profile_id": (
            "partial-basis-retention-profile:sha256:"
            + wc.canonical_sha256(material)
        ),
        "retention_transition_effect": "NONE",
        "raw_source_deletion_effect": "NONE",
        "method_capitalization_effect": "NONE",
        "policy_mutation_effect": "NONE",
        "planning_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One exact partial declared basis may carry a non-scalar retention "
            "profile over REQUIRED, UNRESOLVED, and NOT_REQUIRED member sets "
            "while the exterior remains explicitly unresolved. No global "
            "coverage, load weighting, scalar hotness, economic optimum, "
            "retention transition, authority, execution, or scientific standing "
            "is established."
        ),
        "integrity_sha256": "",
    })


def evaluate_basis_extension(
    base: Mapping[str, Any],
    extended: Mapping[str, Any],
) -> dict[str, Any]:
    base_v = validate_partial_basis_retention_profile(base)
    ext_v = validate_partial_basis_retention_profile(extended)

    if base_v["distinction_id"] != ext_v["distinction_id"]:
        raise PartialBasisRetentionProfileError(
            "extension distinction mismatch"
        )

    base_req = base_v["declared_horizon_requirements"]
    ext_req = ext_v["declared_horizon_requirements"]

    if not set(base_req).issubset(ext_req):
        raise PartialBasisRetentionProfileError(
            "extended basis must contain every base horizon"
        )

    preserved = all(ext_req[h] == p for h, p in base_req.items())
    new_horizons = sorted(set(ext_req) - set(base_req))

    material = {
        "base_profile_id": base_v["profile_id"],
        "extended_profile_id": ext_v["profile_id"],
        "base_basis_id": base_v["basis_id"],
        "extended_basis_id": ext_v["basis_id"],
        "prior_local_coordinates_preserved": (
            "YES" if preserved else "NO"
        ),
        "new_horizons": new_horizons,
        "exterior_posture": "UNRESOLVED",
    }

    return wc.seal_object({
        "object_type": "PARTIAL_BASIS_RETENTION_PROFILE_EXTENSION_V0",
        **material,
        "extension_id": (
            "partial-basis-retention-profile-extension:sha256:"
            + wc.canonical_sha256(material)
        ),
        "global_invariance_effect": "NONE",
        "planning_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "integrity_sha256": "",
    })


def validate_partial_basis_retention_profile(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PartialBasisRetentionProfileError("value must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    expected = build_partial_basis_retention_profile(
        source_g9_result_blob_sha=retained["source_g9_result_blob_sha"],
        source_g9_witness_blob_sha=retained["source_g9_witness_blob_sha"],
        basis_id=retained["basis_id"],
        horizon_requirements=retained["declared_horizon_requirements"],
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise PartialBasisRetentionProfileError(
            "representation mismatch"
        )
    return retained
