#!/usr/bin/env python3
"""SEAT_ENGAGEMENT_HANDSHAKE_001 deterministic synthetic apparatus."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


HEX40 = re.compile(r"^[0-9a-f]{40}$")

ENGAGEMENT_DECISIONS = (
    "ACCEPT",
    "DECLINE",
    "REFUSE",
    "CONTEXT_REQUEST",
)

PRE_MUTATION_DISPOSITIONS = (
    "READY_FOR_AUTHORIZED_UNIT",
    "REVALIDATION_REQUIRED",
    "CONTEXT_REQUEST",
    "AUTHORITY_REQUEST",
    "COORDINATION_REQUEST",
    "RELEASE_REQUIRED",
)

PRIMARY_OBSERVABLE_FIELDS = (
    "engagement_decision",
    "engagement_reason",
    "binding_present",
    "work_claim_present",
    "pre_mutation_disposition",
    "effect_started",
    "grant_state",
    "terminal_receipt",
    "checkpointed",
    "released",
    "second_unit_started",
)

INVOCATION_RECOVERY_QUALIFIED_HEAD = (
    "db38387562f4c9c0deba5fbd96e8a468ec518bd0"
)
INVOCATION_RECOVERY_RECEIPT_HEAD = (
    "990ec59204eb1ecac1c2527a7f00dc387b238ed5"
)


class HandshakeError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise HandshakeError(f"{path} must contain a JSON object")
    return value


def _exact_fields(value: Mapping[str, Any], required: set[str], label: str) -> None:
    if set(value) != required:
        raise HandshakeError(
            f"{label} fields must be exact; "
            f"missing={sorted(required-set(value))} extra={sorted(set(value)-required)}"
        )


def _string(value: Any, label: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value:
        raise HandshakeError(f"{label} must be a non-empty string")


def _strings(value: Any, label: str) -> None:
    if not isinstance(value, list):
        raise HandshakeError(f"{label} must be a list")
    if any(not isinstance(item, str) or not item for item in value):
        raise HandshakeError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise HandshakeError(f"{label} must not contain duplicates")


def validate_envelope(envelope: Mapping[str, Any]) -> None:
    required = {
        "schema",
        "envelope_id",
        "campaign_id",
        "pressure_id",
        "projected_by",
        "projected_at_basis",
        "target_lane_id",
        "target_seat_id",
        "target_role",
        "task_id",
        "bounded_unit_id",
        "target_lineage",
        "objective",
        "completion_criterion",
        "stop_conditions",
        "observation_scope",
        "mutation_scope",
        "execution_scope",
        "required_basis_refs",
        "required_capabilities",
        "expected_peer_surfaces",
        "expected_artifact_scope",
        "consequence_envelope_id",
        "authority_grant_refs",
        "authority_lifetime",
        "recovery_required",
        "checkpoint_required",
        "next_unit_authorized",
        "authority_effect",
        "execution_effect",
    }
    _exact_fields(envelope, required, "envelope")
    if envelope["schema"] != "seat_engagement_envelope_v0":
        raise HandshakeError("wrong envelope schema")
    for field in (
        "envelope_id",
        "pressure_id",
        "projected_by",
        "target_lane_id",
        "target_seat_id",
        "target_role",
        "task_id",
        "bounded_unit_id",
        "target_lineage",
        "objective",
        "completion_criterion",
        "consequence_envelope_id",
    ):
        _string(envelope[field], field)
    _string(envelope["campaign_id"], "campaign_id", nullable=True)
    if not HEX40.fullmatch(str(envelope["projected_at_basis"])):
        raise HandshakeError("projected_at_basis must be exact lowercase 40-hex")
    for field in (
        "stop_conditions",
        "observation_scope",
        "mutation_scope",
        "execution_scope",
        "required_basis_refs",
        "required_capabilities",
        "expected_peer_surfaces",
        "expected_artifact_scope",
        "authority_grant_refs",
    ):
        _strings(envelope[field], field)
    if envelope["authority_lifetime"] != "ONE_UNIT":
        raise HandshakeError("authority_lifetime must be ONE_UNIT")
    if not isinstance(envelope["recovery_required"], bool):
        raise HandshakeError("recovery_required must be boolean")
    if envelope["checkpoint_required"] is not True:
        raise HandshakeError("checkpoint_required must be true")
    if envelope["next_unit_authorized"] is not False:
        raise HandshakeError("next_unit_authorized must be false")
    if envelope["authority_effect"] != "NONE":
        raise HandshakeError("envelope authority_effect must remain NONE")
    if envelope["execution_effect"] != "NONE":
        raise HandshakeError("envelope execution_effect must remain NONE")


def validate_candidate(candidate: Mapping[str, Any]) -> None:
    required = {
        "schema",
        "attachment_id",
        "lane_id",
        "seat_id",
        "role_id",
        "occupant_id",
        "invocation_id",
        "evaluator_relation_valid",
        "basis_refs",
        "capabilities",
        "elects_to_carry",
    }
    _exact_fields(candidate, required, "candidate")
    if candidate["schema"] != "seat_engagement_candidate_attachment_v0":
        raise HandshakeError("wrong candidate schema")
    for field in (
        "attachment_id",
        "lane_id",
        "seat_id",
        "role_id",
        "occupant_id",
        "invocation_id",
    ):
        _string(candidate[field], field)
    if not isinstance(candidate["evaluator_relation_valid"], bool):
        raise HandshakeError("evaluator_relation_valid must be boolean")
    if not isinstance(candidate["elects_to_carry"], bool):
        raise HandshakeError("elects_to_carry must be boolean")
    _strings(candidate["basis_refs"], "basis_refs")
    _strings(candidate["capabilities"], "capabilities")


def validate_grant(grant: Mapping[str, Any]) -> None:
    required = {
        "schema",
        "grant_id",
        "lifetime",
        "envelope_id",
        "bounded_unit_id",
        "addressed_seat_id",
        "addressed_occupant_id",
        "addressed_invocation_id",
        "mutation_scope",
        "execution_scope",
        "state",
    }
    _exact_fields(grant, required, "grant")
    if grant["schema"] != "seat_engagement_one_unit_grant_v0":
        raise HandshakeError("wrong grant schema")
    for field in (
        "grant_id",
        "envelope_id",
        "bounded_unit_id",
        "addressed_seat_id",
        "addressed_occupant_id",
        "addressed_invocation_id",
    ):
        _string(grant[field], field)
    if grant["lifetime"] != "ONE_UNIT":
        raise HandshakeError("grant lifetime must be ONE_UNIT")
    if grant["state"] not in {"AVAILABLE", "CONSUMED"}:
        raise HandshakeError("invalid grant state")
    _strings(grant["mutation_scope"], "grant mutation_scope")
    _strings(grant["execution_scope"], "grant execution_scope")


def validate_fixture_manifest(fixture: Mapping[str, Any]) -> None:
    required = {
        "schema",
        "contract_ref",
        "projected_at_basis",
        "invocation_recovery_basis",
        "base_envelope",
        "base_candidate",
        "valid_grant",
        "cells",
    }
    _exact_fields(fixture, required, "fixture manifest")
    if fixture["schema"] != "seat_engagement_handshake_fixture_manifest_v0":
        raise HandshakeError("wrong fixture manifest schema")
    if not HEX40.fullmatch(str(fixture["projected_at_basis"])):
        raise HandshakeError("fixture projected_at_basis malformed")
    validate_envelope(fixture["base_envelope"])
    validate_candidate(fixture["base_candidate"])
    validate_grant(fixture["valid_grant"])
    recovery = fixture["invocation_recovery_basis"]
    if set(recovery) != {"qualified_implementation_head", "receipt_head"}:
        raise HandshakeError("recovery basis fields must be exact")
    if recovery["qualified_implementation_head"] != INVOCATION_RECOVERY_QUALIFIED_HEAD:
        raise HandshakeError("wrong qualified recovery head")
    if recovery["receipt_head"] != INVOCATION_RECOVERY_RECEIPT_HEAD:
        raise HandshakeError("wrong recovery receipt head")
    expected_cells = ("A", "B", "C1", "C2", "D", "E", "F", "G", "G2", "H", "I")
    if tuple(fixture["cells"]) != expected_cells:
        raise HandshakeError("fixture cells must be exact and ordered")
    for cell_id, cell in fixture["cells"].items():
        if not isinstance(cell, dict):
            raise HandshakeError(f"cell {cell_id} must be object")
        allowed = {
            "candidate_overrides",
            "envelope_overrides",
            "peer_state",
            "authority",
            "unit_outcome",
            "attempt_second_unit",
            "recovery",
            "momentum_overshoot",
        }
        if not set(cell).issubset(allowed):
            raise HandshakeError(f"cell {cell_id} has unknown fields")
        if not isinstance(cell.get("candidate_overrides", {}), dict):
            raise HandshakeError("candidate_overrides must be object")
        if not isinstance(cell.get("envelope_overrides", {}), dict):
            raise HandshakeError("envelope_overrides must be object")
        if cell["peer_state"] not in {"CLEAR", "ESTABLISHED_COLLISION"}:
            raise HandshakeError("invalid peer_state")
        if cell["authority"] not in {"VALID", "ABSENT"}:
            raise HandshakeError("invalid authority fixture")
        if cell["unit_outcome"] not in {None, "SUCCESS", "FAILURE"}:
            raise HandshakeError("invalid unit_outcome")
        if not isinstance(cell["attempt_second_unit"], bool):
            raise HandshakeError("attempt_second_unit must be boolean")


def validate_evaluation_key(key: Mapping[str, Any]) -> None:
    _exact_fields(key, {"schema", "cells", "secondary_observables"}, "evaluation key")
    if key["schema"] != "seat_engagement_handshake_evaluation_key_v0":
        raise HandshakeError("wrong evaluation key schema")
    expected_cells = ("A", "B", "C1", "C2", "D", "E", "F", "G", "G2", "H", "I")
    if tuple(key["cells"]) != expected_cells:
        raise HandshakeError("evaluation cells must be exact and ordered")
    for cell_id, row in key["cells"].items():
        if tuple(row) != PRIMARY_OBSERVABLE_FIELDS:
            raise HandshakeError(f"evaluation key fields drift in {cell_id}")
        if row["engagement_decision"] not in ENGAGEMENT_DECISIONS:
            raise HandshakeError("invalid engagement decision in key")
        disp = row["pre_mutation_disposition"]
        if disp is not None and disp not in PRE_MUTATION_DISPOSITIONS:
            raise HandshakeError("invalid disposition in key")
        if row["grant_state"] not in {"ABSENT", "AVAILABLE", "CONSUMED"}:
            raise HandshakeError("invalid grant state in key")
        if row["terminal_receipt"] not in {None, "SUCCESS", "FAILURE"}:
            raise HandshakeError("invalid terminal receipt in key")
        for field in (
            "binding_present",
            "work_claim_present",
            "effect_started",
            "checkpointed",
            "released",
            "second_unit_started",
        ):
            if not isinstance(row[field], bool):
                raise HandshakeError(f"{field} must be boolean")
    if key["secondary_observables"] != {
        "I": {"authority_request_emitted": "UNSCORED"}
    }:
        raise HandshakeError("secondary observable boundary drift")


def _decision(
    *,
    candidate: Mapping[str, Any],
    envelope: Mapping[str, Any],
    decision: str,
    basis_status: str,
    binding_status: str,
    missing: list[str],
    reason: str,
) -> dict[str, Any]:
    if decision not in ENGAGEMENT_DECISIONS:
        raise HandshakeError("invalid engagement decision")
    return {
        "schema": "seat_engagement_decision_v0",
        "decision": decision,
        "seat_id": str(candidate.get("seat_id") or "UNRESOLVED-SEAT"),
        "occupant_id": str(candidate.get("occupant_id") or "UNRESOLVED-OCCUPANT"),
        "invocation_id": str(candidate.get("invocation_id") or "UNRESOLVED-INVOCATION"),
        "envelope_id": str(envelope.get("envelope_id") or "UNRESOLVED-ENVELOPE"),
        "evaluated_basis": str(
            envelope.get("projected_at_basis") or ("0" * 40)
        ),
        "basis_status": basis_status,
        "binding_status": binding_status,
        "coordination_status": "NOT_YET_EVALUATED",
        "authority_status": "NOT_YET_EVALUATED",
        "missing_requirements": sorted(missing),
        "reason_code": reason,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def evaluate_engagement(
    envelope: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        validate_envelope(envelope)
        validate_candidate(candidate)
    except HandshakeError:
        return _decision(
            candidate=candidate,
            envelope=envelope,
            decision="REFUSE",
            basis_status="UNRESOLVED",
            binding_status="NOT_APPLICABLE",
            missing=[],
            reason="MALFORMED_ENVELOPE",
        )

    if candidate["seat_id"] != envelope["target_seat_id"]:
        return _decision(
            candidate=candidate,
            envelope=envelope,
            decision="REFUSE",
            basis_status="SUFFICIENT",
            binding_status="NOT_APPLICABLE",
            missing=[],
            reason="TARGET_SEAT_MISMATCH",
        )

    relation_valid = (
        candidate["evaluator_relation_valid"]
        and candidate["lane_id"] == envelope["target_lane_id"]
        and candidate["role_id"] == envelope["target_role"]
    )
    if not relation_valid:
        return _decision(
            candidate=candidate,
            envelope=envelope,
            decision="REFUSE",
            basis_status="SUFFICIENT",
            binding_status="CANDIDATE_INVALID",
            missing=[],
            reason="EVALUATOR_BINDING_INVALID",
        )

    missing_basis = sorted(
        set(envelope["required_basis_refs"]) - set(candidate["basis_refs"])
    )
    if missing_basis:
        return _decision(
            candidate=candidate,
            envelope=envelope,
            decision="CONTEXT_REQUEST",
            basis_status="INSUFFICIENT",
            binding_status="CANDIDATE_VALID",
            missing=missing_basis,
            reason="MISSING_REQUIRED_BASIS",
        )

    missing_caps = sorted(
        set(envelope["required_capabilities"]) - set(candidate["capabilities"])
    )
    if missing_caps:
        return _decision(
            candidate=candidate,
            envelope=envelope,
            decision="REFUSE",
            basis_status="SUFFICIENT",
            binding_status="CANDIDATE_INVALID",
            missing=missing_caps,
            reason="REQUIRED_CAPABILITY_MISSING",
        )

    if not candidate["elects_to_carry"]:
        return _decision(
            candidate=candidate,
            envelope=envelope,
            decision="DECLINE",
            basis_status="SUFFICIENT",
            binding_status="CANDIDATE_VALID",
            missing=[],
            reason="EVALUATOR_DECLINED",
        )

    return _decision(
        candidate=candidate,
        envelope=envelope,
        decision="ACCEPT",
        basis_status="SUFFICIENT",
        binding_status="CANDIDATE_VALID",
        missing=[],
        reason="ENGAGEMENT_ADMISSIBLE",
    )


def materialize_binding(
    envelope: Mapping[str, Any],
    candidate: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    if decision["decision"] != "ACCEPT":
        raise HandshakeError("work-unit binding requires ACCEPT")
    return {
        "schema": "seat_engagement_work_unit_binding_v0",
        "binding_id": (
            f"BIND:{envelope['envelope_id']}:{candidate['occupant_id']}:"
            f"{candidate['invocation_id']}:{envelope['bounded_unit_id']}"
        ),
        "lane_id": candidate["lane_id"],
        "seat_id": candidate["seat_id"],
        "occupant_id": candidate["occupant_id"],
        "invocation_id": candidate["invocation_id"],
        "envelope_id": envelope["envelope_id"],
        "bounded_unit_id": envelope["bounded_unit_id"],
        "target_lineage": envelope["target_lineage"],
        "basis_head": envelope["projected_at_basis"],
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def materialize_work_claim(
    envelope: Mapping[str, Any],
    binding: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "seat_engagement_work_claim_v0",
        "claim_id": f"CLAIM:{binding['binding_id']}",
        "lane_id": binding["lane_id"],
        "seat_id": binding["seat_id"],
        "occupant_id": binding["occupant_id"],
        "invocation_id": binding["invocation_id"],
        "envelope_id": binding["envelope_id"],
        "bounded_unit_id": binding["bounded_unit_id"],
        "target_lineage": binding["target_lineage"],
        "basis_head": binding["basis_head"],
        "semantic_surfaces": list(envelope["expected_peer_surfaces"]),
        "artifact_scopes": list(envelope["expected_artifact_scope"]),
        "consequence_envelope_id": envelope["consequence_envelope_id"],
        "status": "ACTIVE",
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def _grant_corresponds(
    grant: Mapping[str, Any] | None,
    envelope: Mapping[str, Any],
    binding: Mapping[str, Any],
) -> bool:
    if grant is None:
        return False
    try:
        validate_grant(grant)
    except HandshakeError:
        return False
    return (
        grant["state"] == "AVAILABLE"
        and grant["envelope_id"] == envelope["envelope_id"]
        and grant["bounded_unit_id"] == envelope["bounded_unit_id"]
        and grant["addressed_seat_id"] == binding["seat_id"]
        and grant["addressed_occupant_id"] == binding["occupant_id"]
        and grant["addressed_invocation_id"] == binding["invocation_id"]
        and set(envelope["mutation_scope"]).issubset(set(grant["mutation_scope"]))
        and set(envelope["execution_scope"]).issubset(set(grant["execution_scope"]))
    )


def pre_mutation_disposition(
    *,
    envelope: Mapping[str, Any],
    candidate: Mapping[str, Any],
    binding: Mapping[str, Any],
    work_claim: Mapping[str, Any],
    peer_state: str,
    grant: Mapping[str, Any] | None,
    basis_state: str = "SUFFICIENT",
    coordinate_changed: bool = False,
) -> dict[str, Any]:
    if (
        binding["occupant_id"] != candidate["occupant_id"]
        or binding["invocation_id"] != candidate["invocation_id"]
        or binding["seat_id"] != candidate["seat_id"]
    ):
        disposition = "RELEASE_REQUIRED"
        reason = "BINDING_NOT_CURRENT"
    elif basis_state != "SUFFICIENT":
        disposition = "CONTEXT_REQUEST"
        reason = "REQUIRED_BASIS_UNRESOLVED"
    elif coordinate_changed:
        disposition = "REVALIDATION_REQUIRED"
        reason = "CONSUMED_COORDINATE_CHANGED"
    elif peer_state == "ESTABLISHED_COLLISION":
        disposition = "COORDINATION_REQUEST"
        reason = "ESTABLISHED_PEER_COLLISION"
    elif not _grant_corresponds(grant, envelope, binding):
        disposition = "AUTHORITY_REQUEST"
        if grant is None:
            reason = "CURRENT_ONE_UNIT_AUTHORITY_ABSENT"
        elif grant.get("state") == "CONSUMED":
            reason = "CURRENT_ONE_UNIT_AUTHORITY_CONSUMED"
        else:
            reason = "CURRENT_ONE_UNIT_AUTHORITY_INVALID"
    else:
        disposition = "READY_FOR_AUTHORIZED_UNIT"
        reason = "MEMBRANE_CLEAR_AUTHORITY_SEPARATELY_VALID"

    if grant is None:
        authority_status = "ABSENT"
    elif _grant_corresponds(grant, envelope, binding):
        authority_status = "AVAILABLE"
    elif grant.get("state") == "CONSUMED":
        authority_status = "CONSUMED"
    else:
        authority_status = "INVALID"

    return {
        "schema": "seat_engagement_pre_mutation_disposition_v0",
        "disposition": disposition,
        "binding_id": binding["binding_id"],
        "work_claim_id": work_claim["claim_id"],
        "basis_status": (
            "CHANGED"
            if coordinate_changed
            else ("SUFFICIENT" if basis_state == "SUFFICIENT" else "INSUFFICIENT")
        ),
        "coordination_status": (
            "COLLISION" if peer_state == "ESTABLISHED_COLLISION" else "CLEAR"
        ),
        "authority_status": authority_status,
        "reason_code": reason,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
    }


def begin_effect(
    *,
    envelope: Mapping[str, Any],
    binding: Mapping[str, Any],
    disposition: Mapping[str, Any],
    grant: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if disposition["disposition"] != "READY_FOR_AUTHORIZED_UNIT":
        raise HandshakeError("effect start requires READY_FOR_AUTHORIZED_UNIT")
    if not _grant_corresponds(grant, envelope, binding):
        raise HandshakeError("effect start requires current corresponding ONE_UNIT grant")
    consumed = copy.deepcopy(dict(grant))
    events = [
        {
            "event_type": "EFFECT_BEARING_UNIT_START",
            "bounded_unit_id": envelope["bounded_unit_id"],
            "grant_id": grant["grant_id"],
        }
    ]
    consumed["state"] = "CONSUMED"
    events.append(
        {
            "event_type": "ONE_UNIT_AUTHORITY_CONSUMED",
            "bounded_unit_id": envelope["bounded_unit_id"],
            "grant_id": grant["grant_id"],
        }
    )
    return consumed, events


def finish_effect(
    *,
    envelope: Mapping[str, Any],
    consumed_grant: Mapping[str, Any],
    outcome: str,
) -> list[dict[str, Any]]:
    if consumed_grant["state"] != "CONSUMED":
        raise HandshakeError("terminal outcome requires consumed grant")
    if outcome not in {"SUCCESS", "FAILURE"}:
        raise HandshakeError("outcome must be SUCCESS or FAILURE")
    return [
        {
            "event_type": "TERMINAL_RECEIPT",
            "bounded_unit_id": envelope["bounded_unit_id"],
            "outcome": outcome,
        },
        {
            "event_type": "CHECKPOINT",
            "bounded_unit_id": envelope["bounded_unit_id"],
            "terminal_outcome": outcome,
        },
        {
            "event_type": "RELEASE",
            "bounded_unit_id": envelope["bounded_unit_id"],
            "reason": "BOUNDED_UNIT_TERMINAL",
        },
    ]


def _event(event_type: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {"event_type": event_type, "payload": copy.deepcopy(dict(payload))}


def _apply_overrides(base: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(base))
    for key, value in overrides.items():
        result[key] = copy.deepcopy(value)
    return result


def _raw_authority_state(authority: str) -> str:
    return "AVAILABLE" if authority == "VALID" else "ABSENT"


def run_cell(
    fixture: Mapping[str, Any],
    cell_id: str,
) -> dict[str, Any]:
    validate_fixture_manifest(fixture)
    if cell_id not in fixture["cells"]:
        raise HandshakeError("unknown cell")
    cell = fixture["cells"][cell_id]
    envelope = _apply_overrides(fixture["base_envelope"], cell["envelope_overrides"])
    candidate = _apply_overrides(fixture["base_candidate"], cell["candidate_overrides"])
    validate_envelope(envelope)
    validate_candidate(candidate)

    events: list[dict[str, Any]] = []
    recovery = cell.get("recovery")
    prior_checkpoint = bool(recovery and recovery.get("prior_checkpoint_present"))
    if recovery:
        if set(recovery) != {
            "qualified",
            "prior_checkpoint_present",
            "prior_receipt",
            "prior_invocation_id",
            "historical_authority_ref",
        }:
            raise HandshakeError("recovery fixture fields drift")
        if recovery["qualified"] is not True:
            raise HandshakeError("H requires qualified recovery basis")
        if fixture["invocation_recovery_basis"]["qualified_implementation_head"] != INVOCATION_RECOVERY_QUALIFIED_HEAD:
            raise HandshakeError("recovery implementation basis drift")
        events.append(
            _event(
                "RECOVERY_BASIS_RETAINED",
                {
                    "qualified_implementation_head": INVOCATION_RECOVERY_QUALIFIED_HEAD,
                    "receipt_head": INVOCATION_RECOVERY_RECEIPT_HEAD,
                    "prior_invocation_id": recovery["prior_invocation_id"],
                    "prior_receipt": recovery["prior_receipt"],
                    "historical_authority_ref": recovery["historical_authority_ref"],
                    "authority_effect": "NONE",
                },
            )
        )
        if prior_checkpoint:
            events.append(
                _event(
                    "PRIOR_CHECKPOINT_RETAINED",
                    {"prior_invocation_id": recovery["prior_invocation_id"]},
                )
            )

    events.append(_event("ENVELOPE_PROJECTED", envelope))
    events.append(_event("CANDIDATE_EVALUATOR_ATTACHED", candidate))

    decision = evaluate_engagement(envelope, candidate)
    events.append(_event("ENGAGEMENT_DECISION", decision))

    grant: dict[str, Any] | None
    if cell["authority"] == "VALID":
        grant = copy.deepcopy(fixture["valid_grant"])
        if (
            candidate["occupant_id"] != grant["addressed_occupant_id"]
            or candidate["invocation_id"] != grant["addressed_invocation_id"]
        ):
            # Do not retarget historical authority to a fresh occupant.
            grant = None
    else:
        grant = None

    observables = {
        "engagement_decision": decision["decision"],
        "engagement_reason": decision["reason_code"],
        "binding_present": False,
        "work_claim_present": False,
        "pre_mutation_disposition": None,
        "effect_started": False,
        "grant_state": _raw_authority_state(cell["authority"]) if grant is not None else "ABSENT",
        "terminal_receipt": None,
        "checkpointed": prior_checkpoint,
        "released": False,
        "second_unit_started": False,
    }
    secondary = {"authority_request_emitted": False}

    if decision["decision"] != "ACCEPT":
        return {
            "cell_id": cell_id,
            "observables": observables,
            "secondary_observables": secondary,
            "events": events,
        }

    binding = materialize_binding(envelope, candidate, decision)
    events.append(_event("WORK_UNIT_BINDING", binding))
    observables["binding_present"] = True

    work_claim = materialize_work_claim(envelope, binding)
    events.append(_event("WORK_CLAIM", work_claim))
    observables["work_claim_present"] = True

    peer_evidence = {
        "schema": "seat_engagement_peer_evidence_v0",
        "state": cell["peer_state"],
        "established_relation": (
            "SEMANTIC_OR_PROVENANCE_COLLISION"
            if cell["peer_state"] == "ESTABLISHED_COLLISION"
            else None
        ),
        "inference_performed_by_seat": False,
    }
    events.append(_event("PEER_EVIDENCE", peer_evidence))

    authority_evidence: dict[str, Any]
    if grant is None:
        authority_evidence = {
            "schema": "seat_engagement_authority_absence_v0",
            "state": "ABSENT",
            "authority_effect": "NONE",
        }
    else:
        authority_evidence = copy.deepcopy(grant)
    events.append(_event("AUTHORITY_EVIDENCE", authority_evidence))

    disposition = pre_mutation_disposition(
        envelope=envelope,
        candidate=candidate,
        binding=binding,
        work_claim=work_claim,
        peer_state=cell["peer_state"],
        grant=grant,
    )
    events.append(_event("PRE_MUTATION_DISPOSITION", disposition))
    observables["pre_mutation_disposition"] = disposition["disposition"]

    if disposition["disposition"] != "READY_FOR_AUTHORIZED_UNIT":
        observables["grant_state"] = (
            "ABSENT"
            if grant is None
            else str(grant["state"])
        )
        return {
            "cell_id": cell_id,
            "observables": observables,
            "secondary_observables": secondary,
            "events": events,
        }

    if grant is None:
        raise HandshakeError("READY without grant is forbidden")

    consumed, start_events = begin_effect(
        envelope=envelope,
        binding=binding,
        disposition=disposition,
        grant=grant,
    )
    for item in start_events:
        events.append(_event(item["event_type"], item))
    observables["effect_started"] = True
    observables["grant_state"] = consumed["state"]

    outcome = cell["unit_outcome"]
    if outcome not in {"SUCCESS", "FAILURE"}:
        raise HandshakeError("READY cell requires terminal synthetic outcome")
    terminal = finish_effect(
        envelope=envelope,
        consumed_grant=consumed,
        outcome=outcome,
    )
    for item in terminal:
        events.append(_event(item["event_type"], item))
    observables["terminal_receipt"] = outcome
    observables["checkpointed"] = True
    observables["released"] = True

    if cell["attempt_second_unit"]:
        if consumed["state"] != "CONSUMED":
            raise HandshakeError("second-unit pressure requires consumed grant")
        blocked = (
            envelope["next_unit_authorized"] is False
            or consumed["state"] == "CONSUMED"
        )
        if not blocked:
            raise HandshakeError("second unit unexpectedly admissible")
        events.append(
            _event(
                "SECOND_UNIT_BLOCKED",
                {
                    "reason": "NEXT_UNIT_NOT_AUTHORIZED",
                    "prior_grant_state": consumed["state"],
                    "authority_effect": "NONE",
                    "execution_effect": "NONE",
                },
            )
        )
        observables["second_unit_started"] = False
        # Cell I permits an authority request but does not require one.
        if cell.get("momentum_overshoot"):
            secondary["authority_request_emitted"] = False

    return {
        "cell_id": cell_id,
        "observables": observables,
        "secondary_observables": secondary,
        "events": events,
    }


def replay_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    state = {
        "engagement_decision": None,
        "binding_present": False,
        "work_claim_present": False,
        "pre_mutation_disposition": None,
        "effect_started": False,
        "grant_state": "ABSENT",
        "terminal_receipt": None,
        "checkpointed": False,
        "released": False,
        "second_unit_started": False,
    }
    for event in events:
        event_type = event["event_type"]
        payload = event["payload"]
        if event_type == "PRIOR_CHECKPOINT_RETAINED":
            state["checkpointed"] = True
        elif event_type == "ENGAGEMENT_DECISION":
            state["engagement_decision"] = payload["decision"]
        elif event_type == "WORK_UNIT_BINDING":
            state["binding_present"] = True
        elif event_type == "WORK_CLAIM":
            state["work_claim_present"] = True
        elif event_type == "AUTHORITY_EVIDENCE":
            state["grant_state"] = payload.get("state", "ABSENT")
        elif event_type == "PRE_MUTATION_DISPOSITION":
            state["pre_mutation_disposition"] = payload["disposition"]
        elif event_type == "EFFECT_BEARING_UNIT_START":
            state["effect_started"] = True
        elif event_type == "ONE_UNIT_AUTHORITY_CONSUMED":
            state["grant_state"] = "CONSUMED"
        elif event_type == "TERMINAL_RECEIPT":
            state["terminal_receipt"] = payload["outcome"]
        elif event_type == "CHECKPOINT":
            state["checkpointed"] = True
        elif event_type == "RELEASE":
            state["released"] = True
        elif event_type == "SECOND_UNIT_STARTED":
            state["second_unit_started"] = True
        elif event_type == "SECOND_UNIT_BLOCKED":
            state["second_unit_started"] = False
    return state


def primary_projection(result: Mapping[str, Any]) -> dict[str, Any]:
    observed = result["observables"]
    return {field: observed[field] for field in PRIMARY_OBSERVABLE_FIELDS}


def score_cell(
    result: Mapping[str, Any],
    evaluation_key: Mapping[str, Any],
) -> bool:
    validate_evaluation_key(evaluation_key)
    cell_id = result["cell_id"]
    return primary_projection(result) == evaluation_key["cells"][cell_id]


def qualify(
    fixture: Mapping[str, Any],
    evaluation_key: Mapping[str, Any],
) -> dict[str, Any]:
    validate_fixture_manifest(fixture)
    validate_evaluation_key(evaluation_key)
    cells: dict[str, Any] = {}
    all_pass = True
    for cell_id in fixture["cells"]:
        result = run_cell(fixture, cell_id)
        passed = score_cell(result, evaluation_key)
        all_pass = all_pass and passed
        replayed = replay_events(result["events"])
        cells[cell_id] = {
            "pass": passed,
            "primary_observables": primary_projection(result),
            "secondary_observables": result["secondary_observables"],
            "event_count": len(result["events"]),
            "events_sha256": sha256_bytes(canonical_bytes(result["events"])),
            "events": result["events"],
            "replay": replayed,
        }
    return {
        "schema": "seat_engagement_handshake_qualification_evidence_v0",
        "contract_ref": fixture["contract_ref"],
        "fixture_sha256": sha256_bytes(canonical_bytes(fixture)),
        "evaluation_key_sha256": sha256_bytes(canonical_bytes(evaluation_key)),
        "invocation_recovery_basis": fixture["invocation_recovery_basis"],
        "cells": cells,
        "all_primary_cells_pass": all_pass,
        "real_seat_effect": "NONE",
        "real_occupant_effect": "NONE",
        "live_authority_effect": "NONE",
        "external_effect": "NONE",
        "model_invocations": 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_qualify = sub.add_parser("qualify")
    p_qualify.add_argument("--fixtures", type=Path, required=True)
    p_qualify.add_argument("--key", type=Path, required=True)
    p_qualify.add_argument("--expected", type=Path)

    args = parser.parse_args(argv)
    if args.command == "qualify":
        fixture = load_json(args.fixtures)
        key = load_json(args.key)
        evidence = qualify(fixture, key)
        raw = canonical_bytes(evidence)
        if args.expected is not None:
            expected = args.expected.read_bytes()
            if expected != raw:
                print(json.dumps({
                    "status": "FRACTURE",
                    "reason": "QUALIFICATION_EVIDENCE_DRIFT",
                    "expected_sha256": sha256_bytes(expected),
                    "observed_sha256": sha256_bytes(raw),
                }, sort_keys=True))
                return 2
        print(raw.decode("utf-8"), end="")
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
