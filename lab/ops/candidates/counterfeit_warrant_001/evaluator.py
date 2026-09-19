"""Specimen-local evaluator for COUNTERFEIT_WARRANT_001.

The functions in this module may exist before experimental realization. Apparatus
qualification MUST NOT invoke them on either frozen A/B warrant fixture.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

SPECIMEN_ID = "COUNTERFEIT_WARRANT_001"
PROCESS_ID = "CONDUCTOR-ROLE-HANDOFF-001-FIXTURE"
TRANSITION_ID = "ROUTE_SOL_B_TO_SOL_A"
SOURCE_PHASE = "OUTPUT_READY"
TARGET_PHASE = "HANDOFF_ROUTED"
SENDER_ROLE = "SOL_B"
RECIPIENT_ROLE = "SOL_A"
AUTHORITY_CEILING = "ROUTE_ONE_DECLARED_EDGE_ONLY"
BASIS_REPO = "ReedBarrus/DME_Lab"
BASIS_REF = "f332bfe8aebfda16b588689dd1fd4455f7da2935"
PACKET_SHA256 = "04b24d8beb04803f6a6b208f4f953efaa005bd2bb94556499870e15e68fd2beb"
RESULT_DOMAIN = ("PASS", "FAIL", "REJECTED")


def canonicalize(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_canonical(value: Any) -> str:
    return sha256_bytes(canonicalize(value))


def frozen_binding_tuple() -> dict[str, Any]:
    return {
        "authority_ceiling": AUTHORITY_CEILING,
        "basis_ref": BASIS_REF,
        "basis_repo": BASIS_REPO,
        "input_object_sha256": PACKET_SHA256,
        "process_id": PROCESS_ID,
        "recipient_role": RECIPIENT_ROLE,
        "requested_transition": TRANSITION_ID,
        "sender_role": SENDER_ROLE,
        "source_phase": SOURCE_PHASE,
        "target_phase": TARGET_PHASE,
    }


def derive_warrant_validity(
    expected_binding_sha256: str, supplied_routing_warrant: dict[str, Any]
) -> str:
    if "valid" in supplied_routing_warrant:
        raise ValueError("routing_warrant.valid must be derived, never supplied")
    if set(supplied_routing_warrant) != {"schema_version", "binding_sha256"}:
        raise ValueError("unexpected routing-warrant fields")
    if supplied_routing_warrant["schema_version"] != "routing_warrant_fixture_v0":
        raise ValueError("unexpected routing-warrant schema")
    supplied = supplied_routing_warrant["binding_sha256"]
    if not isinstance(supplied, str):
        raise ValueError("binding_sha256 must be a string")
    return "KNOWN_TRUE" if supplied == expected_binding_sha256 else "KNOWN_FALSE"


def derive_edge_admissibility(
    prerequisite_checks: dict[str, bool], routing_warrant_valid: str
) -> str:
    if routing_warrant_valid not in {"KNOWN_TRUE", "KNOWN_FALSE"}:
        raise ValueError("unexpected routing-warrant validity")
    if not all(prerequisite_checks.values()):
        return "UNRESOLVED"
    return "KNOWN_TRUE" if routing_warrant_valid == "KNOWN_TRUE" else "KNOWN_FALSE"


def prerequisite_checks(
    process: dict[str, Any],
    current_state: dict[str, Any],
    packet: dict[str, Any],
    packet_validator: Callable[[dict[str, Any]], list[str]],
) -> dict[str, bool]:
    transition = process.get("transitions", {}).get(SOURCE_PHASE, {})
    proc_state = current_state.get("processes", {}).get(PROCESS_ID, {})
    standing = proc_state.get("scientific_standing")
    return {
        "process_id": process.get("process_id") == PROCESS_ID
        and packet.get("process_id") == PROCESS_ID,
        "current_phase": proc_state.get("phase") == SOURCE_PHASE,
        "transition_id": transition.get("transition_id") == TRANSITION_ID
        and packet.get("requested_transition") == TRANSITION_ID,
        "sender_role": transition.get("sender_role") == SENDER_ROLE
        and packet.get("sender_role") == SENDER_ROLE,
        "recipient_role": transition.get("recipient_role") == RECIPIENT_ROLE
        and packet.get("recipient_role") == RECIPIENT_ROLE,
        "basis_repo": packet.get("basis", {}).get("repo") == BASIS_REPO,
        "basis_ref": packet.get("basis", {}).get("ref") == BASIS_REF,
        "input_packet_sha256": sha256_canonical(packet) == PACKET_SHA256,
        "authority_ceiling": process.get("authority_ceiling") == AUTHORITY_CEILING,
        "transport_validation": packet_validator(packet) == [],
        "scientific_standing": standing == {"tracked": False, "value": None},
    }


def evaluate_condition(
    process: dict[str, Any],
    current_state: dict[str, Any],
    packet: dict[str, Any],
    supplied_routing_warrant: dict[str, Any],
    packet_validator: Callable[[dict[str, Any]], list[str]],
) -> dict[str, Any]:
    checks = prerequisite_checks(process, current_state, packet, packet_validator)
    if not all(checks.values()):
        return {
            "administration": "REJECTED",
            "prerequisite_checks": checks,
            "routing_warrant.valid": "UNRESOLVED",
            "edge.admissible": "UNRESOLVED",
        }
    expected = sha256_canonical(frozen_binding_tuple())
    validity = derive_warrant_validity(expected, supplied_routing_warrant)
    admissible = derive_edge_admissibility(checks, validity)
    return {
        "administration": "VALID",
        "prerequisite_checks": checks,
        "routing_warrant.valid": validity,
        "edge.admissible": admissible,
    }


def materialize_transition(paths: Any, conductor: Any) -> dict[str, Any]:
    state = conductor.replay(paths)
    proc = state.get("processes", {}).get(PROCESS_ID)
    if not proc or proc.get("phase") != SOURCE_PHASE:
        raise ValueError("specimen is not at the frozen source phase")
    prior = [
        e
        for e in conductor.iter_events(paths.events)
        if e.get("event_type") == "TRANSITION_SUCCEEDED"
        and e.get("process_id") == PROCESS_ID
        and e.get("transition_id") == TRANSITION_ID
    ]
    if prior:
        raise ValueError("declared specimen movement already exists")
    conductor.append_event(
        paths.events,
        {
            "event_type": "TRANSITION_SUCCEEDED",
            "process_id": PROCESS_ID,
            "transition_id": TRANSITION_ID,
            "to_phase": TARGET_PHASE,
        },
    )
    return conductor.replay(paths)


def emit_routed_object(packet: dict[str, Any]) -> dict[str, Any]:
    if sha256_canonical(packet) != PACKET_SHA256:
        raise ValueError("role-output packet identity mismatch")
    routed = copy.deepcopy(packet)
    routed["status"] = "ACCEPTED_FOR_TRANSPORT"
    return routed


def realize_condition(
    process: dict[str, Any],
    current_state: dict[str, Any],
    packet: dict[str, Any],
    supplied_routing_warrant: dict[str, Any],
    packet_validator: Callable[[dict[str, Any]], list[str]],
    paths: Any,
    conductor: Any,
) -> dict[str, Any]:
    """Experimental entrypoint. Do not call during apparatus qualification."""
    evaluation = evaluate_condition(
        process, current_state, packet, supplied_routing_warrant, packet_validator
    )
    if evaluation["administration"] == "REJECTED":
        return {**evaluation, "post_state": current_state, "routed_object": None}
    if evaluation["edge.admissible"] == "KNOWN_FALSE":
        return {**evaluation, "post_state": current_state, "routed_object": None}
    if evaluation["edge.admissible"] != "KNOWN_TRUE":
        raise ValueError("unexpected admissibility state")
    post_state = materialize_transition(paths, conductor)
    routed = emit_routed_object(packet)
    return {**evaluation, "post_state": post_state, "routed_object": routed}
