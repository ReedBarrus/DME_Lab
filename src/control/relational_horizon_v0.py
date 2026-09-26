"""Minimal relational horizon representation for CONTROL_KERNEL_001.

This module represents one externally supplied operative horizon and its declared
load-bearing gaps. It does not select gaps, rank gaps, justify work, materialize
work, grant authority, execute, or create scientific standing.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from src.coordination import workcycle_v0 as wc


HORIZON_TYPE = "RELATIONAL_HORIZON_V0"
ALLOWED_POSTURES = {"PARTIAL", "CLOSED", "DEGRADED", "UNKNOWN"}


class RelationalHorizonError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RelationalHorizonError(f"{field} must be non-empty")
    return value.strip()


def _gap(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise RelationalHorizonError("gap must be an object")
    blocks = value.get("blocks")
    if not isinstance(blocks, Sequence) or isinstance(blocks, (str, bytes)):
        raise RelationalHorizonError("gap.blocks must be a list")
    normalized_blocks = [_text(x, "gap.blocks[]") for x in blocks]
    if not normalized_blocks:
        raise RelationalHorizonError("gap.blocks must not be empty")
    if not isinstance(value.get("work_eligible"), bool):
        raise RelationalHorizonError("gap.work_eligible must be boolean")
    return {
        "gap_id": _text(value.get("gap_id"), "gap.gap_id"),
        "statement": _text(value.get("statement"), "gap.statement"),
        "blocks": normalized_blocks,
        "work_eligible": value["work_eligible"],
    }


def build_relational_horizon(
    *,
    horizon_id: str,
    subject: str,
    counterparty_or_surface: str,
    declared_purpose: str,
    posture: str,
    evidence_refs: Sequence[str],
    load_bearing_gaps: Sequence[Mapping[str, Any]],
    anomaly_count: int = 0,
    stale_basis: bool = False,
    external_novelty_present: bool = False,
    representation_source: str = "EXTERNALLY_SUPPLIED",
) -> dict[str, Any]:
    if posture not in ALLOWED_POSTURES:
        raise RelationalHorizonError("unsupported posture")
    if representation_source != "EXTERNALLY_SUPPLIED":
        raise RelationalHorizonError(
            "v0 representation source must be EXTERNALLY_SUPPLIED"
        )
    if not isinstance(evidence_refs, Sequence) or isinstance(
        evidence_refs, (str, bytes)
    ):
        raise RelationalHorizonError("evidence_refs must be a list")
    refs = [_text(x, "evidence_refs[]") for x in evidence_refs]
    if not isinstance(load_bearing_gaps, Sequence) or isinstance(
        load_bearing_gaps, (str, bytes)
    ):
        raise RelationalHorizonError("load_bearing_gaps must be a list")
    gaps = [_gap(g) for g in load_bearing_gaps]
    ids = [g["gap_id"] for g in gaps]
    if len(ids) != len(set(ids)):
        raise RelationalHorizonError("duplicate gap_id")
    if posture == "CLOSED" and gaps:
        raise RelationalHorizonError("CLOSED horizon cannot retain live gaps")
    if not isinstance(anomaly_count, int) or anomaly_count < 0:
        raise RelationalHorizonError("anomaly_count must be nonnegative")
    if not isinstance(stale_basis, bool) or not isinstance(
        external_novelty_present, bool
    ):
        raise RelationalHorizonError("challenge posture fields must be boolean")

    logical_horizon_id = _text(horizon_id, "horizon_id")
    material = {
        "horizon_id": logical_horizon_id,
        "relation": {
            "subject": _text(subject, "subject"),
            "counterparty_or_surface": _text(
                counterparty_or_surface, "counterparty_or_surface"
            ),
            "declared_purpose": _text(declared_purpose, "declared_purpose"),
        },
        "current_posture": {
            "state": posture,
            "evidence_refs": refs,
        },
        "load_bearing_gaps": gaps,
        "challenge_posture": {
            "anomaly_count": anomaly_count,
            "stale_basis": stale_basis,
            "external_novelty_present": external_novelty_present,
        },
        "representation_source": representation_source,
    }

    return wc.seal_object({
        "object_type": HORIZON_TYPE,
        **material,
        "horizon_state_id": (
            "relational-horizon-state:sha256:" + wc.canonical_sha256(material)
        ),
        "gap_selection_effect": "NONE",
        "work_justification_effect": "NONE",
        "work_materialization_effect": "NONE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "scientific_standing_effect": "NONE",
        "claim_ceiling": (
            "One externally supplied relational horizon state representation only. "
            "Stable logical horizon identity may persist while posture/gap state "
            "changes. No gap selection, ranking, work justification, planning, "
            "authority, execution, or scientific standing is established."
        ),
        "integrity_sha256": "",
    })


def validate_relational_horizon(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise RelationalHorizonError("horizon must be an object")
    retained = copy.deepcopy(dict(value))
    wc.verify_seal(retained)
    if retained.get("object_type") != HORIZON_TYPE:
        raise RelationalHorizonError("horizon type mismatch")
    expected = build_relational_horizon(
        horizon_id=retained["horizon_id"],
        subject=retained["relation"]["subject"],
        counterparty_or_surface=retained["relation"]["counterparty_or_surface"],
        declared_purpose=retained["relation"]["declared_purpose"],
        posture=retained["current_posture"]["state"],
        evidence_refs=retained["current_posture"]["evidence_refs"],
        load_bearing_gaps=retained["load_bearing_gaps"],
        anomaly_count=retained["challenge_posture"]["anomaly_count"],
        stale_basis=retained["challenge_posture"]["stale_basis"],
        external_novelty_present=retained["challenge_posture"][
            "external_novelty_present"
        ],
        representation_source=retained["representation_source"],
    )
    if retained != expected:
        raise RelationalHorizonError("horizon representation mismatch")
    return retained
