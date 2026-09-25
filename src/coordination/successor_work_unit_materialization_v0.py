"""Materialize one deterministic next workflow unit from a successor + explicit work spec.

The successor selects the exact next-pressure basis. The work spec supplies the
bounded transformation semantics. This module binds those explicit inputs into
one basis_workcycle_v1-compatible unit.

It does not invent a work spec, admit work, grant authority, execute work, or
create scientific standing.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import basis_workcycle_v1 as bw
from src.coordination import workcycle_v0 as wc
from src.coordination.verified_authority_admission_v0 import (
    VerifiedAuthorityAtomicAdmissionError,
    validate_successor_candidate,
)


WORK_SPEC_TYPE = "SUCCESSOR_WORK_SPEC_V0"
MATERIALIZATION_TYPE = "SUCCESSOR_WORK_UNIT_MATERIALIZATION_V0"


class SuccessorWorkUnitMaterializationError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SuccessorWorkUnitMaterializationError(
            f"{field} must be a non-empty string"
        )
    return value.strip()


def _text_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise SuccessorWorkUnitMaterializationError(f"{field} must be a list")
    return [_text(item, f"{field}[]") for item in value]


def build_successor_work_spec(
    *,
    successor_candidate: Mapping[str, Any],
    evidence_refs: Sequence[str],
    desired_consequence: str,
    relevance_question: str,
    pressure_id: str,
    target_distinction_lhs: str,
    target_distinction_rhs: str,
    selection_basis: str,
    expected_information_gain: str,
    application_dependency: str,
    priority_basis: str,
    load_bearing_effects: Sequence[str],
    allowed_operations: Sequence[str],
    prohibited_operations: Sequence[str],
    success_condition: str,
    failure_condition: str,
    unresolved_condition: str,
    max_rounds: int,
    max_branch_count: int,
    max_unresolved_children: int,
    application_required: bool,
    target_surface: str,
    proposed_change: str,
    expected_effect: str,
    operating_change: str,
) -> dict[str, Any]:
    """Build one explicit externally supplied work spec for an exact successor."""
    try:
        successor = validate_successor_candidate(successor_candidate)
    except VerifiedAuthorityAtomicAdmissionError as exc:
        raise SuccessorWorkUnitMaterializationError(str(exc)) from exc

    if successor.get("successor_posture") != "RESOLVE_LOAD_BEARING_GAP":
        raise SuccessorWorkUnitMaterializationError(
            "v0 materialization requires RESOLVE_LOAD_BEARING_GAP successor"
        )
    next_basis = _text(successor.get("next_pressure_basis"), "next_pressure_basis")

    for field, value in {
        "max_rounds": max_rounds,
        "max_branch_count": max_branch_count,
        "max_unresolved_children": max_unresolved_children,
    }.items():
        if not isinstance(value, int) or value < 0:
            raise SuccessorWorkUnitMaterializationError(
                f"{field} must be a nonnegative integer"
            )
    if not isinstance(application_required, bool):
        raise SuccessorWorkUnitMaterializationError(
            "application_required must be boolean"
        )

    material = {
        "source_successor_id": successor["successor_id"],
        "source_successor_integrity_sha256": successor["integrity_sha256"],
        "source_reconciliation_identity": successor["reconciliation_identity"],
        "source_next_pressure_basis": next_basis,
        "evidence_refs": _text_list(evidence_refs, "evidence_refs"),
        "desired_consequence": _text(desired_consequence, "desired_consequence"),
        "relevance_question": _text(relevance_question, "relevance_question"),
        "pressure_id": _text(pressure_id, "pressure_id"),
        "target_distinction": {
            "lhs": _text(target_distinction_lhs, "target_distinction_lhs"),
            "rhs": _text(target_distinction_rhs, "target_distinction_rhs"),
        },
        "selection_basis": _text(selection_basis, "selection_basis"),
        "expected_information_gain": _text(
            expected_information_gain, "expected_information_gain"
        ),
        "application_dependency": _text(
            application_dependency, "application_dependency"
        ),
        "priority_basis": _text(priority_basis, "priority_basis"),
        "load_bearing_effects": _text_list(
            load_bearing_effects, "load_bearing_effects"
        ),
        "allowed_operations": _text_list(allowed_operations, "allowed_operations"),
        "prohibited_operations": _text_list(
            prohibited_operations, "prohibited_operations"
        ),
        "success_condition": _text(success_condition, "success_condition"),
        "failure_condition": _text(failure_condition, "failure_condition"),
        "unresolved_condition": _text(unresolved_condition, "unresolved_condition"),
        "pressure_budget": {
            "max_rounds": max_rounds,
            "max_branch_count": max_branch_count,
            "max_unresolved_children": max_unresolved_children,
        },
        "application_required": application_required,
        "target_surface": _text(target_surface, "target_surface"),
        "proposed_change": _text(proposed_change, "proposed_change"),
        "expected_effect": _text(expected_effect, "expected_effect"),
        "operating_change": _text(operating_change, "operating_change"),
        "spec_source": "EXTERNALLY_SUPPLIED",
    }

    return wc.seal_object(
        {
            "object_type": WORK_SPEC_TYPE,
            **material,
            "work_spec_id": (
                "successor-work-spec:sha256:" + wc.canonical_sha256(material)
            ),
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
            "integrity_sha256": "",
        }
    )


def _validate_work_spec(
    *,
    successor: Mapping[str, Any],
    work_spec: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(work_spec, Mapping):
        raise SuccessorWorkUnitMaterializationError("work_spec must be an object")
    spec = copy.deepcopy(dict(work_spec))
    try:
        wc.verify_seal(spec)
    except Exception as exc:
        raise SuccessorWorkUnitMaterializationError(
            f"work_spec seal invalid: {exc}"
        ) from exc
    if spec.get("object_type") != WORK_SPEC_TYPE:
        raise SuccessorWorkUnitMaterializationError("work_spec type mismatch")
    if spec.get("spec_source") != "EXTERNALLY_SUPPLIED":
        raise SuccessorWorkUnitMaterializationError(
            "work_spec source must be EXTERNALLY_SUPPLIED"
        )
    if spec.get("source_successor_id") != successor["successor_id"]:
        raise SuccessorWorkUnitMaterializationError(
            "work_spec/successor identity mismatch"
        )
    if (
        spec.get("source_successor_integrity_sha256")
        != successor["integrity_sha256"]
    ):
        raise SuccessorWorkUnitMaterializationError(
            "work_spec/successor integrity mismatch"
        )
    if (
        spec.get("source_reconciliation_identity")
        != successor["reconciliation_identity"]
    ):
        raise SuccessorWorkUnitMaterializationError(
            "work_spec/reconciliation identity mismatch"
        )
    if spec.get("source_next_pressure_basis") != successor["next_pressure_basis"]:
        raise SuccessorWorkUnitMaterializationError(
            "work_spec/next-pressure basis mismatch"
        )
    for field in ("authority_effect", "execution_effect", "scientific_standing_effect"):
        if spec.get(field) != "NONE":
            raise SuccessorWorkUnitMaterializationError(
                f"work_spec {field} must be NONE"
            )
    return spec


def materialize_successor_work_unit(
    *,
    successor_candidate: Mapping[str, Any],
    work_spec: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind exact successor identity + explicit work spec into one workflow unit."""
    try:
        successor = validate_successor_candidate(successor_candidate)
    except VerifiedAuthorityAtomicAdmissionError as exc:
        raise SuccessorWorkUnitMaterializationError(str(exc)) from exc

    if successor.get("candidate_posture") != "PROPOSED_NOT_ADMITTED":
        raise SuccessorWorkUnitMaterializationError(
            "successor is not PROPOSED_NOT_ADMITTED"
        )
    if successor.get("successor_posture") != "RESOLVE_LOAD_BEARING_GAP":
        raise SuccessorWorkUnitMaterializationError(
            "successor posture is not materializable in v0"
        )
    if successor.get("successor_id") is None:
        raise SuccessorWorkUnitMaterializationError(
            "no-successor projection cannot be materialized"
        )
    spec = _validate_work_spec(successor=successor, work_spec=work_spec)

    next_basis = successor["next_pressure_basis"]
    unit = {
        "identity": {
            "work_item_id": successor["successor_id"],
            "campaign_id": successor["campaign_id"],
            "parent_work_item_id": successor["parent_work_item_id"],
            "operative_frame_ref": successor["operative_frame_ref"],
            "created_from_event": spec["work_spec_id"],
        },
        "basis": {
            "basis_id": successor["basis_id"],
            "basis_type": "LOAD_BEARING_UNCERTAINTY",
            "statement": next_basis,
            "evidence_refs": list(spec["evidence_refs"]),
            "desired_consequence": {
                "statement": spec["desired_consequence"],
            },
            "current_obstruction": {
                "statement": next_basis,
            },
            "relevance_test": {
                "question": spec["relevance_question"],
                "failure_if_unanswered": True,
            },
            "basis_status": "DECLARED",
        },
        "pressure_selection": {
            "pressure_id": spec["pressure_id"],
            "target_distinction": copy.deepcopy(spec["target_distinction"]),
            "selection_basis": spec["selection_basis"],
            "expected_information_gain": {
                "statement": spec["expected_information_gain"],
            },
            "application_dependency": spec["application_dependency"],
            "stop_if_resolved_by_existing_evidence": True,
            "priority_basis": spec["priority_basis"],
            "load_bearing_effects": list(spec["load_bearing_effects"]),
        },
        "pressure_contract": {
            "allowed_operations": list(spec["allowed_operations"]),
            "prohibited_operations": list(spec["prohibited_operations"]),
            "success_condition": {
                "statement": spec["success_condition"],
            },
            "failure_condition": {
                "statement": spec["failure_condition"],
            },
            "unresolved_condition": {
                "statement": spec["unresolved_condition"],
            },
            "pressure_budget": copy.deepcopy(spec["pressure_budget"]),
        },
        "result": {
            "source_result_ref": None,
            "distinctions": [],
            "apparatus_failures": [],
            "semantic_failures": [],
        },
        "qualification": {
            "adjudication_ref": None,
            "scientific_standing": "NONE",
            "authority_effect": "NONE",
            "qualification_basis": "",
            "unresolved_load_bearing_questions": [],
        },
        "application": {
            "required": spec["application_required"],
            "target_surface": spec["target_surface"],
            "proposed_change": {
                "statement": spec["proposed_change"],
            },
            "executable_change_ref": None,
            "application_status": "NOT_YET_ELIGIBLE",
            "withholding_basis": "work unit is materialized but not qualified or admitted",
        },
        "consequence_observation": {
            "required_if_applied": True,
            "expected_effect": spec["expected_effect"],
            "observed_effect": None,
            "effect_class": "NOT_YET_OBSERVABLE",
            "evidence_refs": [],
            "regression_detected": False,
        },
        "basis_reconciliation": {
            "original_basis_id": successor["basis_id"],
            "disposition": None,
            "remaining_gap": None,
            "next_pressure_allowed": False,
            "next_pressure_basis": None,
            "termination_reason": None,
        },
        "sanity_check": {
            "if_this_work_succeeds": {
                "what_changes_in_the_operating_world": spec["operating_change"],
            },
            "if_nothing_would_change": {
                "posture": "DO_NOT_RUN",
            },
        },
        "materialization": {
            "object_type": MATERIALIZATION_TYPE,
            "source_successor_id": successor["successor_id"],
            "source_successor_integrity_sha256": successor["integrity_sha256"],
            "source_reconciliation_identity": successor["reconciliation_identity"],
            "source_next_pressure_basis": successor["next_pressure_basis"],
            "work_spec_id": spec["work_spec_id"],
            "work_spec_integrity_sha256": spec["integrity_sha256"],
            "spec_source": spec["spec_source"],
            "work_admission_effect": "NONE",
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "scientific_standing_effect": "NONE",
        },
        "integrity_sha256": "",
    }
    sealed = wc.seal_object(unit)
    bw.validate_workflow_unit(sealed)
    return sealed
