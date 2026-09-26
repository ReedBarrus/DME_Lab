"""Minimal retained carrier for G7."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc

OBJECT_TYPE = "DISTINCTION_RETENTION_MODE_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"
HORIZON_ID = "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0"
LAW = {
    "CHANGED": "APPLICABLE",
    "UNCHANGED": "NOT_APPLICABLE",
    "UNRESOLVED": "UNRESOLVED",
}
SOURCE_KEYS = (
    "g4_result",
    "g4_witness",
    "g5_result",
    "g5_witness",
    "g6_result",
    "g6_witness",
)


class DistinctionRetentionModeError(ValueError):
    pass


def _validate_blob(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise DistinctionRetentionModeError(f"{field} must be a Git blob SHA")
    return value


def build_distinction_retention_mode(
    *,
    exact_source_handles: Mapping[str, str],
) -> dict[str, Any]:
    if set(exact_source_handles) != set(SOURCE_KEYS):
        raise DistinctionRetentionModeError("source handle set mismatch")

    handles = {
        key: _validate_blob(exact_source_handles[key], key)
        for key in SOURCE_KEYS
    }

    material = {
        "distinction_id": DISTINCTION_ID,
        "horizon_id": HORIZON_ID,
        "method_axis_applicability_law": dict(LAW),
        "exact_source_handles": handles,
        "unresolved_boundaries": [
            "global ecology retention",
            "quantitative carrying-cost optimum",
            "method improvement",
            "method capitalization",
            "raw source deletion",
        ],
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "retention_mode_id": (
            "distinction-retention-mode:sha256:"
            + wc.canonical_sha256(material)
        ),
        "distinction_retention_required_for_declared_horizon": "YES",
        "full_g4_g5_g6_inline_hot_required": "NO",
        "minimal_hot_carrier_candidate": "YES",
        "exact_cold_source_retention_required": "YES",
        "raw_source_deletion_effect": "NONE",
        "method_capitalization_effect": "NONE",
        "policy_mutation_effect": "NONE",
        "planning_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "integrity_sha256": "",
    })


def validate_distinction_retention_mode(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise DistinctionRetentionModeError("value must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    expected = build_distinction_retention_mode(
        exact_source_handles=retained["exact_source_handles"],
    )
    if retained != expected:
        raise DistinctionRetentionModeError("representation mismatch")
    return retained


def reconstruct_horizon_applicability(
    carrier: Mapping[str, Any],
    cognitive_method_change: str,
) -> str:
    retained = validate_distinction_retention_mode(carrier)
    try:
        return retained["method_axis_applicability_law"][
            cognitive_method_change
        ]
    except KeyError as exc:
        raise DistinctionRetentionModeError(
            "unsupported cognitive_method_change"
        ) from exc
