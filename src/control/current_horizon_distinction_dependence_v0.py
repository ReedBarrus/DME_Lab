"""G6 current-horizon dependence probe for one exact distinction."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import workcycle_v0 as wc


OBJECT_TYPE = "CURRENT_HORIZON_DISTINCTION_DEPENDENCE_V0"
HORIZON_ID = "COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"

APPLICABLE = "APPLICABLE"
NOT_APPLICABLE = "NOT_APPLICABLE"
UNRESOLVED = "UNRESOLVED"
UNDERDETERMINED = "UNDERDETERMINED"


class CurrentHorizonDistinctionDependenceError(ValueError):
    pass


def _method_applicability(case: Mapping[str, Any]) -> str:
    try:
        method = case["method_axis"]["cognitive_method_change"]
    except (KeyError, TypeError) as exc:
        raise CurrentHorizonDistinctionDependenceError(
            "invalid G4 case shape"
        ) from exc

    if method == "CHANGED":
        return APPLICABLE
    if method == "UNCHANGED":
        return NOT_APPLICABLE
    if method == "UNRESOLVED":
        return UNRESOLVED
    raise CurrentHorizonDistinctionDependenceError(
        "unsupported cognitive_method_change"
    )


def _generic_bucket_posture(
    members: list[str],
    pre_applicability: Mapping[str, str],
) -> str:
    observed = {pre_applicability[name] for name in members}
    if len(observed) == 1:
        return next(iter(observed))
    return UNDERDETERMINED


def build_current_horizon_distinction_dependence(
    *,
    source_g4_observation_blob_sha: str,
    source_g5_result_blob_sha: str,
    g4_cases: Mapping[str, Mapping[str, Any]],
    g5_collision_groups: Mapping[str, list[str]],
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    for value, field in (
        (source_g4_observation_blob_sha, "source_g4_observation_blob_sha"),
        (source_g5_result_blob_sha, "source_g5_result_blob_sha"),
    ):
        if not isinstance(value, str) or len(value) != 40:
            raise CurrentHorizonDistinctionDependenceError(
                f"{field} must be a Git blob SHA"
            )

    if representation_source != "EXTERNALLY_SUPPLIED":
        raise CurrentHorizonDistinctionDependenceError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )
    if not isinstance(g4_cases, Mapping) or not g4_cases:
        raise CurrentHorizonDistinctionDependenceError(
            "g4_cases must be a non-empty mapping"
        )
    if not isinstance(g5_collision_groups, Mapping):
        raise CurrentHorizonDistinctionDependenceError(
            "g5_collision_groups must be a mapping"
        )

    pre_applicability = {
        name: _method_applicability(case)
        for name, case in g4_cases.items()
    }

    expected_names = set(pre_applicability)
    grouped_names: set[str] = set()
    generic_postures: dict[str, str] = {}

    for bucket, members in g5_collision_groups.items():
        if not isinstance(members, list) or not all(
            isinstance(x, str) for x in members
        ):
            raise CurrentHorizonDistinctionDependenceError(
                "collision group members must be a list of names"
            )
        grouped_names.update(members)
        generic_postures[bucket] = _generic_bucket_posture(
            members, pre_applicability
        )

    if grouped_names != expected_names:
        raise CurrentHorizonDistinctionDependenceError(
            "collision groups must cover exactly the G4 cases"
        )

    underdetermined_buckets = sorted(
        bucket
        for bucket, posture in generic_postures.items()
        if posture == UNDERDETERMINED
    )

    declared_horizon_load_bearing = bool(underdetermined_buckets)

    current_load_profile = {
        "functional": "UNRESOLVED",
        "semantic": "YES" if declared_horizon_load_bearing else "NO",
        "authority": "UNRESOLVED",
        "provenance": "UNRESOLVED",
        "temporal": "UNRESOLVED",
        "coordination": "YES" if declared_horizon_load_bearing else "NO",
    }

    material = {
        "horizon_id": HORIZON_ID,
        "distinction_id": DISTINCTION_ID,
        "source_g4_observation_blob_sha": source_g4_observation_blob_sha,
        "source_g5_result_blob_sha": source_g5_result_blob_sha,
        "pre_ablation_applicability": pre_applicability,
        "post_ablation_generic_applicability": generic_postures,
        "underdetermined_generic_buckets": underdetermined_buckets,
        "declared_horizon_load_bearing_status": (
            "YES" if declared_horizon_load_bearing else "NO"
        ),
        "global_current_load_bearing_status": "UNRESOLVED",
        "current_load_profile": current_load_profile,
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "dependence_id": (
            "current-horizon-distinction-dependence:sha256:"
            + wc.canonical_sha256(material)
        ),
        "retention_effect": "NONE",
        "method_capitalization_effect": "NONE",
        "policy_mutation_effect": "NONE",
        "gap_selection_effect": "NONE",
        "work_justification_effect": "NONE",
        "planning_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "WORLD_CHANGE != METHOD_CHANGE may be established as load-bearing "
            "for the exact declared COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0 "
            "when ablation makes generic change buckets unable to preserve "
            "deterministic method-specific applicability. Global ecology "
            "dependence, retention, capitalization, policy mutation, authority, "
            "execution, and scientific standing remain unestablished."
        ),
        "integrity_sha256": "",
    })


def validate_current_horizon_distinction_dependence(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CurrentHorizonDistinctionDependenceError(
            "value must be an object"
        )
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    if retained.get("object_type") != OBJECT_TYPE:
        raise CurrentHorizonDistinctionDependenceError(
            "object_type mismatch"
        )

    reconstructed_cases = {
        name: {
            "method_axis": {
                "cognitive_method_change": posture
            }
        }
        for name, posture in (
            (
                name,
                "CHANGED"
                if applicability == APPLICABLE
                else "UNCHANGED"
                if applicability == NOT_APPLICABLE
                else "UNRESOLVED",
            )
            for name, applicability in retained[
                "pre_ablation_applicability"
            ].items()
        )
    }

    reconstructed_groups: dict[str, list[str]] = {}
    for bucket in retained["post_ablation_generic_applicability"]:
        reconstructed_groups[bucket] = sorted(
            name
            for name in retained["pre_ablation_applicability"]
            if (
                bucket == "CHANGED"
                and name in {"WORLD_ONLY", "METHOD_ONLY", "BOTH"}
            )
            or (
                bucket == "UNCHANGED"
                and name == "NEITHER"
            )
            or (
                bucket == "UNRESOLVED"
                and name in {"WORLD_UNRESOLVED", "METHOD_UNRESOLVED"}
            )
        )

    expected = build_current_horizon_distinction_dependence(
        source_g4_observation_blob_sha=retained[
            "source_g4_observation_blob_sha"
        ],
        source_g5_result_blob_sha=retained[
            "source_g5_result_blob_sha"
        ],
        g4_cases=reconstructed_cases,
        g5_collision_groups=reconstructed_groups,
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise CurrentHorizonDistinctionDependenceError(
            "representation mismatch"
        )
    return retained
