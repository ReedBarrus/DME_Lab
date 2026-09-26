"""G5 method/distinction load ablation over the matched G4 frame."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import workcycle_v0 as wc


OBJECT_TYPE = "METHOD_DISTINCTION_LOAD_ABLATION_V0"
DISTINCTION_ID = "WORLD_CHANGE_NE_METHOD_CHANGE"
ALLOWED_AXIS = {"CHANGED", "UNCHANGED", "UNRESOLVED"}
LOAD_DIMENSIONS = (
    "functional",
    "semantic",
    "authority",
    "provenance",
    "temporal",
    "coordination",
)


class MethodDistinctionLoadError(ValueError):
    pass


def _axis(value: Any, field: str) -> str:
    if value not in ALLOWED_AXIS:
        raise MethodDistinctionLoadError(f"unsupported {field}")
    return value


def _collapse(world: str, method: str) -> str:
    if "UNRESOLVED" in (world, method):
        return "UNRESOLVED"
    if "CHANGED" in (world, method):
        return "CHANGED"
    return "UNCHANGED"


def build_method_distinction_load_ablation(
    *,
    source_g4_observation_integrity_sha256: str,
    cases: Mapping[str, Mapping[str, Any]],
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    if representation_source != "EXTERNALLY_SUPPLIED":
        raise MethodDistinctionLoadError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )
    if (
        not isinstance(source_g4_observation_integrity_sha256, str)
        or len(source_g4_observation_integrity_sha256) != 64
    ):
        raise MethodDistinctionLoadError(
            "source_g4_observation_integrity_sha256 must be sha256"
        )
    if not isinstance(cases, Mapping) or not cases:
        raise MethodDistinctionLoadError("cases must be a non-empty mapping")

    pre: dict[str, dict[str, str]] = {}
    ablated: dict[str, str] = {}
    for name, case in cases.items():
        if not isinstance(name, str) or not name:
            raise MethodDistinctionLoadError("case name must be non-empty")
        try:
            world = _axis(case["world_axis"]["posture_change"], "world axis")
            method = _axis(
                case["method_axis"]["cognitive_method_change"],
                "method axis",
            )
        except (KeyError, TypeError) as exc:
            raise MethodDistinctionLoadError(
                f"invalid G4 case shape for {name}"
            ) from exc
        pre[name] = {"world": world, "method": method}
        ablated[name] = _collapse(world, method)

    groups: dict[str, list[str]] = {}
    for name, posture in ablated.items():
        groups.setdefault(posture, []).append(name)
    for names in groups.values():
        names.sort()

    pre_signatures = {
        name: f"{coords['world']}|{coords['method']}"
        for name, coords in pre.items()
    }
    distinct_pre = len(set(pre_signatures.values()))
    distinct_post = len(set(ablated.values()))
    semantic_loss = distinct_post < distinct_pre

    load_profile = {
        "functional": "UNRESOLVED",
        "semantic": "YES" if semantic_loss else "NO",
        "authority": "UNRESOLVED",
        "provenance": "UNRESOLVED",
        "temporal": "UNRESOLVED",
        "coordination": "UNRESOLVED",
    }

    material = {
        "distinction_id": DISTINCTION_ID,
        "source_g4_observation_integrity_sha256": (
            source_g4_observation_integrity_sha256
        ),
        "pre_ablation_cases": pre,
        "ablated_generic_change": ablated,
        "collision_groups": groups,
        "pre_ablation_distinct_signature_count": distinct_pre,
        "post_ablation_distinct_signature_count": distinct_post,
        "semantic_discrimination_loss": semantic_loss,
        "load_profile": load_profile,
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "ablation_id": (
            "method-distinction-load-ablation:sha256:"
            + wc.canonical_sha256(material)
        ),
        "current_load_bearing_status": "UNRESOLVED",
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
            "Ablating WORLD_CHANGE != METHOD_CHANGE from the exact supplied G4 "
            "case frame may establish deterministic loss of representational "
            "discrimination and therefore semantic load within that frame only. "
            "No live-horizon dependence, method improvement, retention, "
            "capitalization, policy mutation, work justification, authority, "
            "execution, or scientific standing is established."
        ),
        "integrity_sha256": "",
    })


def validate_method_distinction_load_ablation(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise MethodDistinctionLoadError("value must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    if retained.get("object_type") != OBJECT_TYPE:
        raise MethodDistinctionLoadError("object_type mismatch")

    reconstructed_cases = {
        name: {
            "world_axis": {"posture_change": coords["world"]},
            "method_axis": {
                "cognitive_method_change": coords["method"]
            },
        }
        for name, coords in retained["pre_ablation_cases"].items()
    }
    expected = build_method_distinction_load_ablation(
        source_g4_observation_integrity_sha256=retained[
            "source_g4_observation_integrity_sha256"
        ],
        cases=reconstructed_cases,
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise MethodDistinctionLoadError("representation mismatch")
    return retained
