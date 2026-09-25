"""Read-only qualification readiness for WORKCYCLE_STABILIZATION_001.

This module does not create scientific standing. It only determines whether
bounded evidence prerequisites are present for an independent qualifier.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.coordination.workcycle_v0 import derive_campaign_progress


OBJECT_TYPE = "WORKCYCLE_QUALIFICATION_READINESS_V0"

HORIZON_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "ATLAS_TEMPORAL_HORIZON_CLOSURE_001_ADJUDICATION_RESULT.md"
)
ONE_SUCCESSOR_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "ONE_SUCCESSOR_CONTINUATION_PRESSURE_RESULT_001.md"
)
ATOMIC_ADMISSION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "ATOMIC_ADMISSION_PRESSURE_RESULT_001.md"
)
AUTHORITY_BINDING_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "AUTHORITY_BINDING_PRESSURE_RESULT_001.md"
)
SUCCESSOR_IDENTITY_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "SUCCESSOR_IDENTITY_CONSERVATION_PRESSURE_RESULT_001.md"
)
BASIS_RECONCILIATION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "BASIS_RECONCILIATION_PRESSURE_RESULT_001.md"
)
VERIFIED_AUTHORITY_ADMISSION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_PRESSURE_RESULT_001.md"
)
ADMITTED_AUTHORITY_CONSUMPTION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE_RESULT_001.md"
)
INVOCATION_RESULT_WITNESS_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "INVOCATION_RESULT_WITNESS_PRESSURE_RESULT_001.md"
)
INVOCATION_RESULT_SETTLEMENT_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "INVOCATION_RESULT_SETTLEMENT_PRESSURE_RESULT_001.md"
)
SETTLEMENT_CONSEQUENCE_RECONCILIATION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "SETTLEMENT_CONSEQUENCE_RECONCILIATION_PRESSURE_RESULT_001.md"
)
SECOND_SUCCESSOR_FROM_RECONCILIATION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "SECOND_SUCCESSOR_FROM_RECONCILIATION_PRESSURE_RESULT_001.md"
)
SUCCESSOR_WORK_UNIT_MATERIALIZATION_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE_RESULT_001.md"
)
REPEATED_METABOLIC_LOOP_RESULT = Path(
    "docs/campaigns/workcycle_stabilization_001/pressure_runs/"
    "REPEATED_METABOLIC_LOOP_PRESSURE_RESULT_001.md"
)


def _markdown_field(path: Path, field: str) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    target = field.strip().rstrip(":")
    for index, line in enumerate(lines):
        if line.strip().rstrip(":") != target:
            continue
        for candidate in lines[index + 1:]:
            value = candidate.strip()
            if value:
                return value
    return None


def build_workcycle_qualification_readiness(repo_root: str | Path) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    progress = derive_campaign_progress(repo)
    cells = progress["cells"]

    cell_postures = {name: item["posture"] for name, item in cells.items()}
    bounded_cells_ready = all(
        cell_postures.get(f"T{index}") == "BOUNDED_PASS"
        for index in range(8)
    )

    horizon_path = repo / HORIZON_RESULT
    horizon_disposition = _markdown_field(horizon_path, "DISPOSITION")
    horizon_ready = horizon_disposition == "HORIZON_MATCHED"

    successor_path = repo / ONE_SUCCESSOR_RESULT
    successor_disposition = _markdown_field(successor_path, "DISPOSITION")
    successor_ready = successor_disposition == "ONE_SUCCESSOR_MATCHED"

    admission_path = repo / ATOMIC_ADMISSION_RESULT
    admission_disposition = _markdown_field(admission_path, "DISPOSITION")
    admission_ready = admission_disposition == "ATOMIC_ADMISSION_MATCHED"

    authority_binding_path = repo / AUTHORITY_BINDING_RESULT
    authority_binding_disposition = _markdown_field(
        authority_binding_path, "DISPOSITION"
    )
    authority_binding_ready = (
        authority_binding_disposition == "AUTHORITY_BINDING_MATCHED"
    )

    successor_identity_path = repo / SUCCESSOR_IDENTITY_RESULT
    successor_identity_disposition = _markdown_field(
        successor_identity_path, "DISPOSITION"
    )
    successor_identity_ready = (
        successor_identity_disposition == "SUCCESSOR_IDENTITY_MATCHED"
    )

    basis_reconciliation_path = repo / BASIS_RECONCILIATION_RESULT
    basis_reconciliation_disposition = _markdown_field(
        basis_reconciliation_path, "DISPOSITION"
    )
    basis_reconciliation_ready = (
        basis_reconciliation_disposition == "BASIS_RECONCILIATION_MATCHED"
    )

    verified_authority_admission_path = repo / VERIFIED_AUTHORITY_ADMISSION_RESULT
    verified_authority_admission_disposition = _markdown_field(
        verified_authority_admission_path, "DISPOSITION"
    )
    verified_authority_admission_ready = (
        verified_authority_admission_disposition
        == "VERIFIED_AUTHORITY_ATOMIC_ADMISSION_MATCHED"
    )

    admitted_authority_consumption_path = repo / ADMITTED_AUTHORITY_CONSUMPTION_RESULT
    admitted_authority_consumption_disposition = _markdown_field(
        admitted_authority_consumption_path, "DISPOSITION"
    )
    admitted_authority_consumption_ready = (
        admitted_authority_consumption_disposition
        == "ADMITTED_AUTHORITY_CONSUMPTION_MATCHED"
    )

    invocation_result_witness_path = repo / INVOCATION_RESULT_WITNESS_RESULT
    invocation_result_witness_disposition = _markdown_field(
        invocation_result_witness_path, "DISPOSITION"
    )
    invocation_result_witness_ready = (
        invocation_result_witness_disposition
        == "INVOCATION_RESULT_WITNESS_MATCHED"
    )

    invocation_result_settlement_path = repo / INVOCATION_RESULT_SETTLEMENT_RESULT
    invocation_result_settlement_disposition = _markdown_field(
        invocation_result_settlement_path, "DISPOSITION"
    )
    invocation_result_settlement_ready = (
        invocation_result_settlement_disposition
        == "INVOCATION_RESULT_SETTLEMENT_MATCHED"
    )

    settlement_consequence_reconciliation_path = (
        repo / SETTLEMENT_CONSEQUENCE_RECONCILIATION_RESULT
    )
    settlement_consequence_reconciliation_disposition = _markdown_field(
        settlement_consequence_reconciliation_path, "DISPOSITION"
    )
    settlement_consequence_reconciliation_ready = (
        settlement_consequence_reconciliation_disposition
        == "SETTLEMENT_CONSEQUENCE_RECONCILIATION_MATCHED"
    )

    second_successor_path = repo / SECOND_SUCCESSOR_FROM_RECONCILIATION_RESULT
    second_successor_disposition = _markdown_field(
        second_successor_path, "DISPOSITION"
    )
    second_successor_ready = (
        second_successor_disposition
        == "SECOND_SUCCESSOR_FROM_RECONCILIATION_MATCHED"
    )

    successor_work_unit_materialization_path = (
        repo / SUCCESSOR_WORK_UNIT_MATERIALIZATION_RESULT
    )
    successor_work_unit_materialization_disposition = _markdown_field(
        successor_work_unit_materialization_path, "DISPOSITION"
    )
    successor_work_unit_materialization_ready = (
        successor_work_unit_materialization_disposition
        == "SUCCESSOR_WORK_UNIT_MATERIALIZATION_MATCHED"
    )

    metabolic_loop_path = repo / REPEATED_METABOLIC_LOOP_RESULT
    metabolic_loop_disposition = _markdown_field(
        metabolic_loop_path, "DISPOSITION"
    )
    metabolic_loop_ready = (
        metabolic_loop_disposition == "REPEATED_METABOLIC_LOOP_MATCHED"
    )

    bounded_blockers: list[str] = []
    if not bounded_cells_ready:
        for name in [f"T{i}" for i in range(8)]:
            if cell_postures.get(name) != "BOUNDED_PASS":
                bounded_blockers.append(f"{name}:{cell_postures.get(name, 'MISSING')}")
    if not horizon_ready:
        bounded_blockers.append(
            f"TEMPORAL_HORIZON:{horizon_disposition or 'UNFROZEN'}"
        )

    self_moving_blockers = list(bounded_blockers)
    if not successor_ready:
        self_moving_blockers.append(
            f"ONE_SUCCESSOR:{successor_disposition or 'UNFROZEN'}"
        )
    if not admission_ready:
        self_moving_blockers.append(
            f"ATOMIC_ADMISSION:{admission_disposition or 'UNFROZEN'}"
        )
    if not authority_binding_ready:
        self_moving_blockers.append(
            f"AUTHORITY_BINDING:{authority_binding_disposition or 'UNFROZEN'}"
        )
    if not successor_identity_ready:
        self_moving_blockers.append(
            f"SUCCESSOR_IDENTITY:{successor_identity_disposition or 'UNFROZEN'}"
        )
    if not basis_reconciliation_ready:
        self_moving_blockers.append(
            f"BASIS_RECONCILIATION:{basis_reconciliation_disposition or 'UNFROZEN'}"
        )
    if not verified_authority_admission_ready:
        self_moving_blockers.append(
            "VERIFIED_AUTHORITY_ATOMIC_ADMISSION:"
            + (verified_authority_admission_disposition or "UNFROZEN")
        )
    if not admitted_authority_consumption_ready:
        self_moving_blockers.append(
            "ADMITTED_AUTHORITY_CONSUMPTION:"
            + (admitted_authority_consumption_disposition or "UNFROZEN")
        )
    if not invocation_result_witness_ready:
        self_moving_blockers.append(
            "INVOCATION_RESULT_WITNESS:"
            + (invocation_result_witness_disposition or "UNFROZEN")
        )
    if not invocation_result_settlement_ready:
        self_moving_blockers.append(
            "INVOCATION_RESULT_SETTLEMENT:"
            + (invocation_result_settlement_disposition or "UNFROZEN")
        )
    if not settlement_consequence_reconciliation_ready:
        self_moving_blockers.append(
            "SETTLEMENT_CONSEQUENCE_RECONCILIATION:"
            + (settlement_consequence_reconciliation_disposition or "UNFROZEN")
        )
    if not second_successor_ready:
        self_moving_blockers.append(
            "SECOND_SUCCESSOR_FROM_RECONCILIATION:"
            + (second_successor_disposition or "UNFROZEN")
        )
    if not successor_work_unit_materialization_ready:
        self_moving_blockers.append(
            "SUCCESSOR_WORK_UNIT_MATERIALIZATION:"
            + (successor_work_unit_materialization_disposition or "UNFROZEN")
        )
    if not metabolic_loop_ready:
        self_moving_blockers.append(
            f"REPEATED_METABOLIC_LOOP:{metabolic_loop_disposition or 'UNFROZEN'}"
        )

    return {
        "object_type": OBJECT_TYPE,
        "campaign_id": "WORKCYCLE_STABILIZATION_001",
        "cell_postures": cell_postures,
        "temporal_horizon": {
            "result_path": HORIZON_RESULT.as_posix(),
            "disposition": horizon_disposition,
            "ready": horizon_ready,
        },
        "one_successor": {
            "result_path": ONE_SUCCESSOR_RESULT.as_posix(),
            "disposition": successor_disposition,
            "ready": successor_ready,
        },
        "atomic_admission": {
            "result_path": ATOMIC_ADMISSION_RESULT.as_posix(),
            "disposition": admission_disposition,
            "ready": admission_ready,
        },
        "authority_binding": {
            "result_path": AUTHORITY_BINDING_RESULT.as_posix(),
            "disposition": authority_binding_disposition,
            "ready": authority_binding_ready,
        },
        "successor_identity": {
            "result_path": SUCCESSOR_IDENTITY_RESULT.as_posix(),
            "disposition": successor_identity_disposition,
            "ready": successor_identity_ready,
        },
        "basis_reconciliation": {
            "result_path": BASIS_RECONCILIATION_RESULT.as_posix(),
            "disposition": basis_reconciliation_disposition,
            "ready": basis_reconciliation_ready,
        },
        "verified_authority_atomic_admission": {
            "result_path": VERIFIED_AUTHORITY_ADMISSION_RESULT.as_posix(),
            "disposition": verified_authority_admission_disposition,
            "ready": verified_authority_admission_ready,
        },
        "admitted_authority_consumption": {
            "result_path": ADMITTED_AUTHORITY_CONSUMPTION_RESULT.as_posix(),
            "disposition": admitted_authority_consumption_disposition,
            "ready": admitted_authority_consumption_ready,
        },
        "invocation_result_witness": {
            "result_path": INVOCATION_RESULT_WITNESS_RESULT.as_posix(),
            "disposition": invocation_result_witness_disposition,
            "ready": invocation_result_witness_ready,
        },
        "invocation_result_settlement": {
            "result_path": INVOCATION_RESULT_SETTLEMENT_RESULT.as_posix(),
            "disposition": invocation_result_settlement_disposition,
            "ready": invocation_result_settlement_ready,
        },
        "settlement_consequence_reconciliation": {
            "result_path": SETTLEMENT_CONSEQUENCE_RECONCILIATION_RESULT.as_posix(),
            "disposition": settlement_consequence_reconciliation_disposition,
            "ready": settlement_consequence_reconciliation_ready,
        },
        "second_successor_from_reconciliation": {
            "result_path": SECOND_SUCCESSOR_FROM_RECONCILIATION_RESULT.as_posix(),
            "disposition": second_successor_disposition,
            "ready": second_successor_ready,
        },
        "successor_work_unit_materialization": {
            "result_path": SUCCESSOR_WORK_UNIT_MATERIALIZATION_RESULT.as_posix(),
            "disposition": successor_work_unit_materialization_disposition,
            "ready": successor_work_unit_materialization_ready,
        },
        "repeated_metabolic_loop": {
            "result_path": REPEATED_METABOLIC_LOOP_RESULT.as_posix(),
            "disposition": metabolic_loop_disposition,
            "ready": metabolic_loop_ready,
        },
        "bounded_workcycle": {
            "qualification_readiness": (
                "READY_FOR_INDEPENDENT_QUALIFICATION"
                if not bounded_blockers
                else "HELD"
            ),
            "blockers": bounded_blockers,
            "standing_effect": "NONE",
        },
        "self_moving_workcycle": {
            "qualification_readiness": (
                "READY_FOR_INDEPENDENT_QUALIFICATION"
                if not self_moving_blockers
                else "HELD"
            ),
            "blockers": self_moving_blockers,
            "standing_effect": "NONE",
        },
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "Read-only qualification readiness only. READY does not create "
            "scientific standing, execution authority, or campaign progress."
        ),
    }
