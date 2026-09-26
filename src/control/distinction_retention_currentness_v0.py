"""G8 currentness-conditioned retention requirement."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc

OBJECT_TYPE = "DISTINCTION_RETENTION_CURRENTNESS_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"
HORIZON_ID = "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0"

CURRENTNESS = {"CURRENT", "NONCURRENT", "UNRESOLVED"}

LAW = {
    "CURRENT": "REQUIRED",
    "NONCURRENT": "NOT_REQUIRED_FOR_DECLARED_HORIZON",
    "UNRESOLVED": "UNRESOLVED",
}


class DistinctionRetentionCurrentnessError(ValueError):
    pass


def _blob(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise DistinctionRetentionCurrentnessError(
            f"{field} must be a Git blob SHA"
        )
    return value


def build_distinction_retention_currentness(
    *,
    source_g7_result_blob_sha: str,
    source_g7_witness_blob_sha: str,
    horizon_currentness: str,
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    _blob(source_g7_result_blob_sha, "source_g7_result_blob_sha")
    _blob(source_g7_witness_blob_sha, "source_g7_witness_blob_sha")

    if horizon_currentness not in CURRENTNESS:
        raise DistinctionRetentionCurrentnessError(
            "unsupported horizon_currentness"
        )
    if representation_source != "EXTERNALLY_SUPPLIED":
        raise DistinctionRetentionCurrentnessError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )

    material = {
        "distinction_id": DISTINCTION_ID,
        "horizon_id": HORIZON_ID,
        "source_g7_result_blob_sha": source_g7_result_blob_sha,
        "source_g7_witness_blob_sha": source_g7_witness_blob_sha,
        "horizon_currentness": horizon_currentness,
        "declared_horizon_hot_requirement": LAW[horizon_currentness],
        "global_hot_requirement": "UNRESOLVED",
        "exact_cold_source_retention_required": "YES",
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "currentness_gate_id": (
            "distinction-retention-currentness:sha256:"
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
            "The G7 horizon-scoped hot-retention requirement may be conditioned "
            "only by externally supplied currentness of the exact declared "
            "horizon. No transition, deletion, global cooling, capitalization, "
            "planning authority, execution authority, or scientific standing "
            "is established."
        ),
        "integrity_sha256": "",
    })


def validate_distinction_retention_currentness(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise DistinctionRetentionCurrentnessError("value must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    expected = build_distinction_retention_currentness(
        source_g7_result_blob_sha=retained["source_g7_result_blob_sha"],
        source_g7_witness_blob_sha=retained["source_g7_witness_blob_sha"],
        horizon_currentness=retained["horizon_currentness"],
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise DistinctionRetentionCurrentnessError("representation mismatch")
    return retained
