"""Orthogonal world/method reconciliation representation for G4."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import workcycle_v0 as wc


OBJECT_TYPE = "WORLD_METHOD_RECONCILIATION_V0"
ALLOWED_CHANGE = {"CHANGED", "UNCHANGED", "UNRESOLVED"}


class WorldMethodReconciliationError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorldMethodReconciliationError(f"{field} must be non-empty")
    return value.strip()


def _refs(value: Sequence[str], field: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise WorldMethodReconciliationError(f"{field} must be a list")
    return [_text(x, f"{field}[]") for x in value]


def build_world_method_reconciliation(
    *,
    source_reconciliation_id: str,
    source_reconciliation_integrity_sha256: str,
    world_posture_change: str,
    world_evidence_refs: Sequence[str],
    cognitive_method_change: str,
    method_evidence_refs: Sequence[str],
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    if world_posture_change not in ALLOWED_CHANGE:
        raise WorldMethodReconciliationError("unsupported world_posture_change")
    if cognitive_method_change not in ALLOWED_CHANGE:
        raise WorldMethodReconciliationError("unsupported cognitive_method_change")
    if representation_source != "EXTERNALLY_SUPPLIED":
        raise WorldMethodReconciliationError(
            "v0 representation_source must be EXTERNALLY_SUPPLIED"
        )

    source_integrity = _text(
        source_reconciliation_integrity_sha256,
        "source_reconciliation_integrity_sha256",
    )
    if len(source_integrity) != 64:
        raise WorldMethodReconciliationError(
            "source_reconciliation_integrity_sha256 must be sha256"
        )

    world_refs = _refs(world_evidence_refs, "world_evidence_refs")
    method_refs = _refs(method_evidence_refs, "method_evidence_refs")

    if world_posture_change == "UNRESOLVED" and not world_refs:
        raise WorldMethodReconciliationError(
            "UNRESOLVED world axis requires evidence refs"
        )
    if cognitive_method_change == "UNRESOLVED" and not method_refs:
        raise WorldMethodReconciliationError(
            "UNRESOLVED method axis requires evidence refs"
        )

    material = {
        "source_reconciliation_id": _text(
            source_reconciliation_id, "source_reconciliation_id"
        ),
        "source_reconciliation_integrity_sha256": source_integrity,
        "world_axis": {
            "posture_change": world_posture_change,
            "evidence_refs": world_refs,
        },
        "method_axis": {
            "cognitive_method_change": cognitive_method_change,
            "evidence_refs": method_refs,
        },
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": OBJECT_TYPE,
        **material,
        "world_method_reconciliation_id": (
            "world-method-reconciliation:sha256:" + wc.canonical_sha256(material)
        ),
        "causal_attribution_effect": "NONE",
        "gap_selection_effect": "NONE",
        "work_justification_effect": "NONE",
        "planning_effect": "NONE",
        "method_capitalization_effect": "NONE",
        "policy_mutation_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One exact source reconciliation may carry separately evidenced world "
            "posture-change and cognitive-method-change axes. No causality, method "
            "improvement, capitalization, policy mutation, gap discovery, work "
            "selection, authority, execution, or scientific standing is established."
        ),
        "integrity_sha256": "",
    })


def validate_world_method_reconciliation(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise WorldMethodReconciliationError("value must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    if retained.get("object_type") != OBJECT_TYPE:
        raise WorldMethodReconciliationError("object_type mismatch")
    expected = build_world_method_reconciliation(
        source_reconciliation_id=retained["source_reconciliation_id"],
        source_reconciliation_integrity_sha256=retained[
            "source_reconciliation_integrity_sha256"
        ],
        world_posture_change=retained["world_axis"]["posture_change"],
        world_evidence_refs=retained["world_axis"]["evidence_refs"],
        cognitive_method_change=retained["method_axis"][
            "cognitive_method_change"
        ],
        method_evidence_refs=retained["method_axis"]["evidence_refs"],
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise WorldMethodReconciliationError("representation mismatch")
    return retained
