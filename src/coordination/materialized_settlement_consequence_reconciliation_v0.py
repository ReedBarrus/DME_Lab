"""Exact materialized settlement -> consequence -> basis reconciliation."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import basis_workcycle_v1 as bw
from src.coordination.materialized_invocation_result_settlement_v0 import SETTLEMENT_TYPE
from src.runtime.local_authority_consumption_v0 import canonical_sha256

OBSERVED_CONSEQUENCE_TYPE = "MATERIALIZED_SETTLED_RESULT_OBSERVED_CONSEQUENCE_V0"
CONSEQUENCE_EVALUATION_TYPE = "MATERIALIZED_SETTLED_RESULT_CONSEQUENCE_EVALUATION_V0"
COMPOSITION_TYPE = "MATERIALIZED_SETTLEMENT_CONSEQUENCE_RECONCILIATION_V0"

_ALLOWED = {
    "CONSEQUENCE_MATCHED",
    "CONSEQUENCE_PARTIAL",
    "CONSEQUENCE_CONTRADICTED",
    "CONSEQUENCE_UNRESOLVED",
}


class MaterializedSettlementConsequenceError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise MaterializedSettlementConsequenceError(f"{field} must be non-empty")
    return value


def _settlement_core(value: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "source_witness_id",
        "source_raw_output_sha256",
        "source_work_attempt_id",
        "source_successor_id",
        "source_successor_integrity_sha256",
        "source_work_spec_id",
        "source_work_spec_integrity_sha256",
        "source_materialized_work_item_id",
        "source_materialized_unit_integrity_sha256",
        "source_consumption_id",
        "source_atomic_admission_id",
        "settlement_actor_identity",
    )
    core = {key: _text(value.get(key), key) for key in keys}
    core["field_dispositions"] = dict(sorted(value.get("field_dispositions", {}).items()))
    core["settlement_basis"] = dict(sorted(value.get("settlement_basis", {}).items()))
    return core


def validate_settlement(settlement: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(settlement, Mapping):
        raise MaterializedSettlementConsequenceError("settlement must be an object")
    value = copy.deepcopy(dict(settlement))
    if value.get("object_type") != SETTLEMENT_TYPE:
        raise MaterializedSettlementConsequenceError("settlement object_type mismatch")
    if value.get("classification_source") != "EXTERNALLY_SUPPLIED":
        raise MaterializedSettlementConsequenceError("settlement classification source mismatch")
    for field in (
        "qualification_effect",
        "authority_effect",
        "execution_effect",
        "external_consequence_effect",
        "atlas_mutation_effect",
        "scientific_standing_effect",
    ):
        if value.get(field) != "NONE":
            raise MaterializedSettlementConsequenceError(f"settlement {field} must be NONE")
    expected = (
        "materialized-invocation-result-candidate-settlement:sha256:"
        + canonical_sha256(_settlement_core(value))
    )
    if value.get("settlement_id") != expected:
        raise MaterializedSettlementConsequenceError("settlement identity mismatch")
    return value


def validate_unit_binding(unit: Mapping[str, Any], settlement: Mapping[str, Any]) -> None:
    bw.validate_workflow_unit(unit)
    m = unit.get("materialization")
    pairs = (
        (unit["identity"]["work_item_id"], settlement["source_materialized_work_item_id"], "work-item"),
        (unit["identity"]["work_item_id"], settlement["source_successor_id"], "successor"),
        (unit["integrity_sha256"], settlement["source_materialized_unit_integrity_sha256"], "unit"),
        (m.get("source_successor_integrity_sha256") if isinstance(m, Mapping) else None,
         settlement["source_successor_integrity_sha256"], "successor integrity"),
        (m.get("work_spec_id") if isinstance(m, Mapping) else None,
         settlement["source_work_spec_id"], "work-spec"),
        (m.get("work_spec_integrity_sha256") if isinstance(m, Mapping) else None,
         settlement["source_work_spec_integrity_sha256"], "work-spec integrity"),
    )
    for actual, expected, label in pairs:
        if actual != expected:
            raise MaterializedSettlementConsequenceError(
                f"settlement/materialized {label} mismatch"
            )


def build_observed_consequence(
    *,
    settlement: Mapping[str, Any],
    materialized_unit: Mapping[str, Any],
    expected_effect: str,
    observed_effect: str | None,
    effect_class: str,
    evidence_refs: Sequence[str],
    regression_detected: bool = False,
) -> dict[str, Any]:
    settled = validate_settlement(settlement)
    validate_unit_binding(materialized_unit, settled)
    if effect_class not in {"OBSERVED", "NOT_YET_OBSERVABLE"}:
        raise MaterializedSettlementConsequenceError("unsupported effect_class")
    observed = _text(observed_effect, "observed_effect") if effect_class == "OBSERVED" else None
    if effect_class != "OBSERVED" and observed_effect is not None:
        raise MaterializedSettlementConsequenceError(
            "unobservable consequence cannot carry observed effect"
        )
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, (str, bytes)):
        raise MaterializedSettlementConsequenceError("evidence_refs must be a list")
    refs = [_text(x, "evidence_refs[]") for x in evidence_refs]
    material = {
        "source_settlement_id": settled["settlement_id"],
        "source_witness_id": settled["source_witness_id"],
        "source_work_attempt_id": settled["source_work_attempt_id"],
        "successor_id": settled["source_successor_id"],
        "work_spec_id": settled["source_work_spec_id"],
        "materialized_unit_integrity_sha256": settled[
            "source_materialized_unit_integrity_sha256"
        ],
        "work_item_id": materialized_unit["identity"]["work_item_id"],
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
        "consequence_id": "materialized-settled-result-consequence:sha256:" + canonical_sha256(material),
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
        raise MaterializedSettlementConsequenceError("consequence object_type mismatch")
    if disposition not in _ALLOWED:
        raise MaterializedSettlementConsequenceError("unsupported consequence disposition")
    material = {
        key: observed_consequence[key]
        for key in (
            "work_item_id",
            "successor_id",
            "work_spec_id",
            "materialized_unit_integrity_sha256",
            "consequence_id",
            "source_settlement_id",
        )
    }
    material.update({
        "disposition": disposition,
        "evaluation_basis": _text(evaluation_basis, "evaluation_basis"),
        "evaluator_identity": _text(evaluator_identity, "evaluator_identity"),
        "classification_source": "EXTERNALLY_SUPPLIED",
    })
    return bw.wc.seal_object({
        "object_type": CONSEQUENCE_EVALUATION_TYPE,
        **material,
        "evaluation_id": (
            "materialized-settled-result-consequence-evaluation:sha256:"
            + canonical_sha256(material)
        ),
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
    settled = validate_settlement(settlement)
    validate_unit_binding(unit, settled)
    if settled["source_work_attempt_id"] != _text(
        expected_work_attempt_id, "expected_work_attempt_id"
    ):
        raise MaterializedSettlementConsequenceError(
            "settlement/work-attempt identity mismatch"
        )
    local_unit = copy.deepcopy(unit)
    consequence_id = evaluation_id = None
    basis_eval = None
    if observed_consequence is None:
        if consequence_evaluation is not None:
            raise MaterializedSettlementConsequenceError("evaluation requires consequence")
        local_unit["consequence_observation"].update({
            "observed_effect": None,
            "effect_class": "NOT_YET_OBSERVABLE",
            "evidence_refs": [],
            "regression_detected": False,
        })
    else:
        bw.wc.verify_seal(observed_consequence)
        expected = {
            "source_settlement_id": settled["settlement_id"],
            "source_witness_id": settled["source_witness_id"],
            "successor_id": settled["source_successor_id"],
            "work_spec_id": settled["source_work_spec_id"],
            "materialized_unit_integrity_sha256": settled[
                "source_materialized_unit_integrity_sha256"
            ],
            "work_item_id": unit["identity"]["work_item_id"],
        }
        for field, value in expected.items():
            if observed_consequence.get(field) != value:
                raise MaterializedSettlementConsequenceError(
                    f"consequence/{field} mismatch"
                )
        consequence_id = observed_consequence["consequence_id"]
        local_unit["consequence_observation"].update({
            key: copy.deepcopy(observed_consequence[key])
            for key in (
                "expected_effect",
                "observed_effect",
                "effect_class",
                "evidence_refs",
                "regression_detected",
            )
        })
        if consequence_evaluation is not None:
            bw.wc.verify_seal(consequence_evaluation)
            for field, value in {
                "consequence_id": consequence_id,
                "source_settlement_id": settled["settlement_id"],
                "successor_id": settled["source_successor_id"],
                "work_spec_id": settled["source_work_spec_id"],
                "materialized_unit_integrity_sha256": settled[
                    "source_materialized_unit_integrity_sha256"
                ],
                "work_item_id": unit["identity"]["work_item_id"],
            }.items():
                if consequence_evaluation.get(field) != value:
                    raise MaterializedSettlementConsequenceError(
                        f"evaluation/{field} mismatch"
                    )
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
        "source_witness_id": settled["source_witness_id"],
        "source_work_attempt_id": settled["source_work_attempt_id"],
        "successor_id": settled["source_successor_id"],
        "work_spec_id": settled["source_work_spec_id"],
        "materialized_unit_integrity_sha256": settled[
            "source_materialized_unit_integrity_sha256"
        ],
        "work_item_id": unit["identity"]["work_item_id"],
        "basis_id": unit["basis"]["basis_id"],
        "consequence_id": consequence_id,
        "evaluation_id": evaluation_id,
        "reconciliation_identity": reconciliation["integrity_sha256"],
    }
    return bw.wc.seal_object({
        "object_type": COMPOSITION_TYPE,
        **material,
        "composition_id": (
            "materialized-settlement-consequence-reconciliation:sha256:"
            + canonical_sha256(material)
        ),
        "basis_reconciliation": reconciliation,
        "settlement_is_consequence": False,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "atlas_mutation_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "integrity_sha256": "",
    })
