"""G11 conservation of unresolved residue from one qualified partial basis."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import workcycle_v0 as wc

OBJECT_TYPE = "PARTIAL_BASIS_RESIDUAL_CONSERVATION_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"


class PartialBasisResidualConservationError(ValueError):
    pass


def _blob(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise PartialBasisResidualConservationError(
            f"{field} must be a Git blob SHA"
        )
    return value


def _texts(values: Sequence[str], field: str) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise PartialBasisResidualConservationError(
            f"{field} must be a list"
        )
    out: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise PartialBasisResidualConservationError(
                f"{field} members must be non-empty strings"
            )
        out.append(value.strip())
    if len(out) != len(set(out)):
        raise PartialBasisResidualConservationError(
            f"{field} must not contain duplicates"
        )
    return sorted(out)


def build_partial_basis_residual_conservation(
    *,
    source_g10_result_blob_sha: str,
    source_g10_witness_blob_sha: str,
    basis_id: str,
    source_profile_id: str,
    source_extension_id: str,
    interior_unresolved_members: Sequence[str],
    nonresidual_members: Sequence[str],
    exterior_posture: str,
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    _blob(source_g10_result_blob_sha, "source_g10_result_blob_sha")
    _blob(source_g10_witness_blob_sha, "source_g10_witness_blob_sha")

    for value, field in (
        (basis_id, "basis_id"),
        (source_profile_id, "source_profile_id"),
        (source_extension_id, "source_extension_id"),
    ):
        if not isinstance(value, str) or not value.strip():
            raise PartialBasisResidualConservationError(
                f"{field} must be non-empty"
            )

    if exterior_posture != "UNRESOLVED":
        raise PartialBasisResidualConservationError(
            "v0 exterior_posture must remain UNRESOLVED"
        )
    if representation_source != "EXTERNALLY_SUPPLIED":
        raise PartialBasisResidualConservationError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )

    residual = _texts(
        interior_unresolved_members, "interior_unresolved_members"
    )
    classified = _texts(nonresidual_members, "nonresidual_members")

    if set(residual) & set(classified):
        raise PartialBasisResidualConservationError(
            "residual and nonresidual members must not overlap"
        )

    material = {
        "distinction_id": DISTINCTION_ID,
        "source_g10_result_blob_sha": source_g10_result_blob_sha,
        "source_g10_witness_blob_sha": source_g10_witness_blob_sha,
        "basis_id": basis_id.strip(),
        "source_profile_id": source_profile_id.strip(),
        "source_extension_id": source_extension_id.strip(),
        "interior_unresolved_members": residual,
        "nonresidual_members": classified,
        "exterior_posture": exterior_posture,
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "residual_id": (
            "partial-basis-residual:sha256:"
            + wc.canonical_sha256(material)
        ),
        "residual_conserved": "YES",
        "residual_gap_status": "NOT_ESTABLISHED",
        "residual_work_eligibility": "NOT_ESTABLISHED",
        "architecture_requirement": "NOT_ESTABLISHED",
        "gap_discovery_effect": "NONE",
        "gap_selection_effect": "NONE",
        "work_justification_effect": "NONE",
        "work_materialization_effect": "NONE",
        "retention_transition_effect": "NONE",
        "raw_source_deletion_effect": "NONE",
        "method_capitalization_effect": "NONE",
        "policy_mutation_effect": "NONE",
        "planning_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "The exact unresolved residue from one qualified G10 partial basis "
            "may be conserved as a typed carrier preserving interior unresolved "
            "members, unresolved exterior posture, and source identity. Residual "
            "gap standing, work eligibility, architecture requirement, global "
            "coverage, planning, authority, execution, and scientific standing "
            "remain unestablished."
        ),
        "integrity_sha256": "",
    })


def validate_partial_basis_residual_conservation(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise PartialBasisResidualConservationError(
            "value must be an object"
        )
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    expected = build_partial_basis_residual_conservation(
        source_g10_result_blob_sha=retained[
            "source_g10_result_blob_sha"
        ],
        source_g10_witness_blob_sha=retained[
            "source_g10_witness_blob_sha"
        ],
        basis_id=retained["basis_id"],
        source_profile_id=retained["source_profile_id"],
        source_extension_id=retained["source_extension_id"],
        interior_unresolved_members=retained[
            "interior_unresolved_members"
        ],
        nonresidual_members=retained["nonresidual_members"],
        exterior_posture=retained["exterior_posture"],
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise PartialBasisResidualConservationError(
            "representation mismatch"
        )
    return retained
