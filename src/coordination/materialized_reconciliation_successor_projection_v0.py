"""Project lawful successor posture from one exact materialized reconciliation."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from src.coordination import basis_workcycle_v1 as bw
from src.coordination.materialized_settlement_consequence_reconciliation_v0 import (
    COMPOSITION_TYPE,
)
from src.runtime.local_authority_consumption_v0 import canonical_sha256


PROJECTION_TYPE = "MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_V0"


class MaterializedReconciliationSuccessorError(ValueError):
    pass


def derive_materialized_successor_projection(
    *,
    unit: Mapping[str, Any],
    reconciliation_composition: Mapping[str, Any],
) -> dict[str, Any]:
    bw.validate_workflow_unit(unit)
    if not isinstance(reconciliation_composition, Mapping):
        raise MaterializedReconciliationSuccessorError(
            "reconciliation_composition must be an object"
        )
    composition = copy.deepcopy(dict(reconciliation_composition))
    bw.wc.verify_seal(composition)
    if composition.get("object_type") != COMPOSITION_TYPE:
        raise MaterializedReconciliationSuccessorError(
            "reconciliation composition type mismatch"
        )

    materialization = unit.get("materialization")
    if not isinstance(materialization, Mapping):
        raise MaterializedReconciliationSuccessorError(
            "materialized unit metadata missing"
        )

    expected = {
        "work_item_id": unit["identity"]["work_item_id"],
        "successor_id": unit["identity"]["work_item_id"],
        "work_spec_id": materialization.get("work_spec_id"),
        "materialized_unit_integrity_sha256": unit["integrity_sha256"],
        "basis_id": unit["basis"]["basis_id"],
    }
    for field, value in expected.items():
        if composition.get(field) != value:
            raise MaterializedReconciliationSuccessorError(
                f"reconciliation/{field} identity mismatch"
            )

    reconciliation = composition.get("basis_reconciliation")
    if not isinstance(reconciliation, Mapping):
        raise MaterializedReconciliationSuccessorError(
            "basis_reconciliation missing"
        )
    bw.wc.verify_seal(reconciliation)
    if reconciliation.get("integrity_sha256") != composition.get(
        "reconciliation_identity"
    ):
        raise MaterializedReconciliationSuccessorError(
            "reconciliation identity mismatch"
        )

    admissibility = bw.pressure_admissibility(unit)
    successor = bw.derive_successor_candidate(
        unit,
        admissibility=admissibility,
        reconciliation=reconciliation,
    )

    material = {
        "source_composition_id": composition["composition_id"],
        "source_settlement_id": composition["settlement_id"],
        "source_consequence_id": composition["consequence_id"],
        "source_evaluation_id": composition["evaluation_id"],
        "source_reconciliation_identity": composition[
            "reconciliation_identity"
        ],
        "source_successor_id": composition["successor_id"],
        "source_work_spec_id": composition["work_spec_id"],
        "source_materialized_unit_integrity_sha256": composition[
            "materialized_unit_integrity_sha256"
        ],
        "basis_disposition": reconciliation["disposition"],
        "next_pressure_allowed": reconciliation["next_pressure_allowed"],
        "next_pressure_basis": reconciliation["next_pressure_basis"],
        "derived_successor_posture": successor["successor_posture"],
        "derived_candidate_posture": successor["candidate_posture"],
        "derived_successor_id": successor["successor_id"],
        "derived_successor_integrity_sha256": successor["integrity_sha256"],
    }

    return bw.wc.seal_object({
        "object_type": PROJECTION_TYPE,
        **material,
        "projection_id": (
            "materialized-reconciliation-successor-projection:sha256:"
            + canonical_sha256(material)
        ),
        "successor_candidate": successor,
        "work_created": False,
        "work_admission_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One deterministic successor-or-no-successor projection from one "
            "exact materialized reconciliation composition. SATISFIED and "
            "INVALIDATED reconciliation may lawfully produce no successor; a "
            "PARTIALLY_SATISFIED reconciliation may produce one deterministic "
            "unadmitted successor candidate. No work is materialized, admitted, "
            "authorized, scheduled, or executed."
        ),
        "integrity_sha256": "",
    })
