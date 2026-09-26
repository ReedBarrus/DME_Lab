"""G9 declared retention-scope aggregation for one distinction."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc

OBJECT_TYPE = "RETENTION_SCOPE_AGGREGATION_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"

LOCAL_POSTURES = {
    "REQUIRED",
    "NOT_REQUIRED_FOR_DECLARED_HORIZON",
    "UNRESOLVED",
}


class RetentionScopeAggregationError(ValueError):
    pass


def _aggregate(postures: list[str]) -> str:
    if "REQUIRED" in postures:
        return "REQUIRED"
    if "UNRESOLVED" in postures:
        return "UNRESOLVED"
    return "NOT_REQUIRED_FOR_DECLARED_SCOPE"


def build_retention_scope_aggregation(
    *,
    source_g8_result_blob_sha: str,
    source_g8_witness_blob_sha: str,
    horizon_requirements: Mapping[str, str],
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    for value, field in (
        (source_g8_result_blob_sha, "source_g8_result_blob_sha"),
        (source_g8_witness_blob_sha, "source_g8_witness_blob_sha"),
    ):
        if not isinstance(value, str) or len(value) != 40:
            raise RetentionScopeAggregationError(
                f"{field} must be a Git blob SHA"
            )

    if representation_source != "EXTERNALLY_SUPPLIED":
        raise RetentionScopeAggregationError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )

    if not isinstance(horizon_requirements, Mapping) or not horizon_requirements:
        raise RetentionScopeAggregationError(
            "horizon_requirements must be a non-empty mapping"
        )

    normalized: dict[str, str] = {}
    for horizon_id, posture in horizon_requirements.items():
        if not isinstance(horizon_id, str) or not horizon_id.strip():
            raise RetentionScopeAggregationError(
                "horizon id must be non-empty"
            )
        if posture not in LOCAL_POSTURES:
            raise RetentionScopeAggregationError(
                "unsupported local hot requirement"
            )
        normalized[horizon_id.strip()] = posture

    scope_posture = _aggregate(list(normalized.values()))

    material = {
        "distinction_id": DISTINCTION_ID,
        "source_g8_result_blob_sha": source_g8_result_blob_sha,
        "source_g8_witness_blob_sha": source_g8_witness_blob_sha,
        "declared_horizon_requirements": dict(sorted(normalized.items())),
        "declared_scope_hot_requirement": scope_posture,
        "declared_scope_complete_for_supplied_horizons": "YES",
        "global_ecology_hot_requirement": "UNRESOLVED",
        "exact_cold_source_retention_required": "YES",
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "scope_aggregation_id": (
            "retention-scope-aggregation:sha256:"
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
            "An exact non-empty declared set of horizon-local hot-retention "
            "requirements for one distinction may be aggregated into one "
            "declared-scope posture. Global ecology completeness and global "
            "hot requirement remain unresolved. No retention transition, "
            "deletion, capitalization, authority, execution, or scientific "
            "standing is established."
        ),
        "integrity_sha256": "",
    })


def validate_retention_scope_aggregation(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise RetentionScopeAggregationError("value must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    expected = build_retention_scope_aggregation(
        source_g8_result_blob_sha=retained["source_g8_result_blob_sha"],
        source_g8_witness_blob_sha=retained["source_g8_witness_blob_sha"],
        horizon_requirements=retained["declared_horizon_requirements"],
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise RetentionScopeAggregationError("representation mismatch")
    return retained
