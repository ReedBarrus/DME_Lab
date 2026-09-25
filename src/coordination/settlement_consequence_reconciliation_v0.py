"""Compose candidate settlement with independently supplied consequence evidence."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import basis_workcycle_v1 as bw
from src.coordination.invocation_result_settlement_v0 import SETTLEMENT_TYPE
from src.runtime.local_authority_consumption_v0 import canonical_sha256


OBSERVED_CONSEQUENCE_TYPE = "SETTLED_RESULT_OBSERVED_CONSEQUENCE_V0"
CONSEQUENCE_EVALUATION_TYPE = "SETTLED_RESULT_CONSEQUENCE_EVALUATION_V0"
COMPOSITION_TYPE = "SETTLEMENT_CONSEQUENCE_RECONCILIATION_V0"

CONSEQUENCE_DISPOSITIONS = {
    "CONSEQUENCE_MATCHED",
    "CONSEQUENCE_PARTIAL",
    "CONSEQUENCE_CONTRADICTED",
    "CONSEQUENCE_UNRESOLVED",
}


class SettlementConsequenceError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise SettlementConsequenceError(f"{field} must be non-empty")
    return value


def validate_settlement(settlement: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(settlement, Mapping):
        raise SettlementConsequenceError("settlement must be an object")
    value = copy.deepcopy(dict(settlement))
    if value.get("object_type") != SETTLEMENT_TYPE:
        raise SettlementConsequenceError("settlement object_type mismatch")
    if value.get("classification_source") != "EXTERNALLY_SUPPLIED":
        raise SettlementConsequenceError("settlement classification source mismatch")
    for field in ("qualification_effect", "authority_effect", "execution_effect", "atlas_mutation_effect"):
        if value.get(field) != "NONE":
            raise SettlementConsequenceError(f"settlement {field} must be NONE")

    material = {
        "source_witness_id": _text(value.get("source_witness_id"), "source_witness_id"),
        "source_raw_output_sha256": _text(value.get("source_raw_output_sha256"), "source_raw_output_sha256"),
        "source_work_attempt_id": _text(value.get("source_work_attempt_id"), "source_work_attempt_id"),
        "settlement_actor_identity": _text(value.get("settlement_actor_identity"), "settlement_actor_identity"),
        "field_dispositions": dict(sorted(value.get("field_dispositions", {}).items())),
        "settlement_basis": dict(sorted(value.get("settlement_basis", {}).items())),
    }
    expected = "invocation-result-candidate-settlement:sha256:" + canonical_sha256(material)
    if value.get("settlement_id") != expected:
        raise SettlementConsequenceError("settlement identity mismatch")
    return value


def build_observed_consequence(
    *,
    settlement: Mapping[str, Any],
    work_item_id: str,
    expected_effect: str,
    observed_effect: str | None,
    effect_class: str,
    evidence_refs: Sequence[str],
    regression_detected: bool = False,
) -> dict[str, Any]:
    settled = validate_settlement(settlement)
    if effect_class not in {"OBSERVED", "NOT_YET_OBSERVABLE"}:
        raise SettlementConsequenceError("unsupported effect_class")
    if effect_class == "OBSERVED":
        observed = _text(observed_effect, "observed_effect")
    else:
        if observed_effect is not None:
            raise SettlementConsequenceError("unobservable consequence cannot carry observed effect")
        observed = None
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)):
        raise SettlementConsequenceError("evidence_refs must be a list")
    refs = [_text(x, "evidence_refs[]") for x in evidence_refs]
    material = {
        "source_settlement_id": settled["settlement_id"],
        "source_work_attempt_id": settled["source_work_attempt_id"],
        "work_item_id": _text(work_item_id, "work_item_id"),
        "expected_effect": _text(expected_effect, "expected_effect"),
        "observed_effect": observed,
        "effect_class": effect_class,
        "evidence_refs": refs,
        "regression_detected": bool(regression_detected),
        "observation_source": "EXTERNALLY_SUPPLIED",
    }
    return bw.wc.seal_object({
        "object_type": OBSERVED_CONSEQUENCE_TYPE,
        **material,
        "consequence_id": "settled-result-consequence:sha256:" + canonical_sha256(material),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "integrity_sha256": "",
    })


def build_consequence_evaluation(
    *,
    observed_consequence: Mapping[str, Any],
    disposition: str,
    evaluation_basis: str,
    evaluator_identity: str,
) -> dict[str, Any]:
    bw.wc.verify_seal(observed_consequence)
    if observed_consequence.get("object_type") != OBSERVED_CONSEQUENCE_TYPE:
        raise SettlementConsequenceError("observed consequence object_type mismatch")
    if disposition not in CONSEQUENCE_DISPOSITIONS:
        raise SettlementConsequenceError("unsupported consequence disposition")
    material = {
        "work_item_id": observed_consequence["work_item_id"],
        "consequence_id": observed_consequence["consequence_id"],
        "source_settlement_id": observed_consequence["source_settlement_id"],
        "disposition": disposition,
        "evaluation_basis": _text(evaluation_basis, "evaluation_basis"),
        "evaluator_identity": _text(evaluator_identity, "evaluator_identity"),
        "classification_source": "EXTERNALLY_SUPPLIED",
    }
    return bw.wc.seal_object({
        "object_type": CONSEQUENCE_EVALUATION_TYPE,
        **material,
        "evaluation_id": "settled-result-consequence-evaluation:sha256:" + canonical_sha256(material),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "integrity_sha256": "",
    })


def reconcile(
    *,
    unit: Mapping[str, Any],
    settlement: Mapping[str, Any],
    expected_work_attempt_id: str,
    observed_consequence: Mapping[str, Any] | None,
    consequence_evaluation: Mapping[str, Any] | None,
    current_obstruction_posture: str,
    remaining_gap: str | None = None,
    reframed_basis: str | None = None,
) -> dict[str, Any]:
    bw.validate_workflow_unit(unit)
    settled = validate_settlement(settlement)
    if settled["source_work_attempt_id"] != _text(expected_work_attempt_id, "expected_work_attempt_id"):
        raise SettlementConsequenceError("settlement/work-attempt identity mismatch")

    local_unit = copy.deepcopy(unit)
    consequence_id = None
    evaluation_id = None
    basis_eval = None

    if observed_consequence is None:
        if consequence_evaluation is not None:
            raise SettlementConsequenceError("evaluation requires consequence")
        local_unit["consequence_observation"].update({
            "observed_effect": None,
            "effect_class": "NOT_YET_OBSERVABLE",
            "evidence_refs": [],
            "regression_detected": False,
        })
    else:
        bw.wc.verify_seal(observed_consequence)
        if observed_consequence.get("object_type") != OBSERVED_CONSEQUENCE_TYPE:
            raise SettlementConsequenceError("consequence type mismatch")
        if observed_consequence.get("source_settlement_id") != settled["settlement_id"]:
            raise SettlementConsequenceError("consequence/settlement identity mismatch")
        if observed_consequence.get("work_item_id") != unit["identity"]["work_item_id"]:
            raise SettlementConsequenceError("consequence/work-item identity mismatch")
        consequence_id = observed_consequence["consequence_id"]
        local_unit["consequence_observation"].update({
            "expected_effect": observed_consequence["expected_effect"],
            "observed_effect": observed_consequence["observed_effect"],
            "effect_class": observed_consequence["effect_class"],
            "evidence_refs": list(observed_consequence["evidence_refs"]),
            "regression_detected": observed_consequence["regression_detected"],
        })
        if consequence_evaluation is not None:
            bw.wc.verify_seal(consequence_evaluation)
            if consequence_evaluation.get("object_type") != CONSEQUENCE_EVALUATION_TYPE:
                raise SettlementConsequenceError("evaluation type mismatch")
            if consequence_evaluation.get("consequence_id") != consequence_id:
                raise SettlementConsequenceError("evaluation/consequence identity mismatch")
            if consequence_evaluation.get("source_settlement_id") != settled["settlement_id"]:
                raise SettlementConsequenceError("evaluation/settlement identity mismatch")
            if consequence_evaluation.get("work_item_id") != unit["identity"]["work_item_id"]:
                raise SettlementConsequenceError("evaluation/work-item identity mismatch")
            evaluation_id = consequence_evaluation["evaluation_id"]
            basis_eval = bw.wc.seal_object({
                "object_type": "CONSEQUENCE_EVALUATION_V0",
                "evaluation_id": evaluation_id,
                "work_item_id": consequence_evaluation["work_item_id"],
                "consequence_id": consequence_id,
                "disposition": consequence_evaluation["disposition"],
                "integrity_sha256": "",
            })

    reconciliation = bw.derive_basis_reconciliation_from_evidence(
        local_unit,
        consequence_evaluation=basis_eval,
        current_obstruction_posture=current_obstruction_posture,
        remaining_gap=remaining_gap,
        reframed_basis=reframed_basis,
    )
    material = {
        "settlement_id": settled["settlement_id"],
        "source_work_attempt_id": settled["source_work_attempt_id"],
        "work_item_id": unit["identity"]["work_item_id"],
        "basis_id": unit["basis"]["basis_id"],
        "consequence_id": consequence_id,
        "evaluation_id": evaluation_id,
        "reconciliation_identity": reconciliation["integrity_sha256"],
    }
    return bw.wc.seal_object({
        "object_type": COMPOSITION_TYPE,
        **material,
        "composition_id": "settlement-consequence-reconciliation:sha256:" + canonical_sha256(material),
        "basis_reconciliation": reconciliation,
        "settlement_is_consequence": False,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "atlas_mutation_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "integrity_sha256": "",
    })
