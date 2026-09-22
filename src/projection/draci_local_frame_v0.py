"""Bounded, derived DRACI projections for two exact Lab specimens.

This module does not evaluate lifecycle or authorization semantics.  It
projects exact source inputs and supplied mechanism observations.  Each
returned mapping is an append-free view, not a frame/event schema or a source
of authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping, Sequence


CONTROLLER_CENTERED = "controller-centered"
CLAIM_LANE_CENTERED = "claim/lane-centered"
SUPPORTED_PROJECTIONS = (CONTROLLER_CENTERED, CLAIM_LANE_CENTERED)

AUTHORIZATION_OBJECT_CENTERED = "authorization-object-centered"
LATCH_STATE_CARRIER_CENTERED = "latch/state-carrier-centered"
SUPPORTED_AUTHORIZATION_PROJECTIONS = (
    AUTHORIZATION_OBJECT_CENTERED,
    LATCH_STATE_CARRIER_CENTERED,
)

REPOSITORY_CENTERED = "repository-centered"
OBSERVER_CENTERED = "observer-centered"
SUPPORTED_SPARSE_OBSERVATION_PROJECTIONS = (
    REPOSITORY_CENTERED,
    OBSERVER_CENTERED,
)

EXACT_GUARD_SEQUENCE = tuple(f"P{number:02d}" for number in range(1, 9))

EXACT_SOURCE_REFS = {
    "controller": (
        "git-blob:89ff5ffc6c3555bc31716735af6e93498d675ced:"
        "tools/lane_lifecycle_disposition_v0.py"
    ),
    "specimen_input": (
        "git-blob:6768f0609d7bfb015acf57fe3baad49ecf807279:"
        "fixtures/lane_lifecycle_disposition_v0/pressure_cells_v0.json"
        "#/bases/complete_valid"
    ),
    "evaluation_key": (
        "git-blob:ddfc4bfd9acedd8824374dd88dc097ef1e156423:"
        "fixtures/lane_lifecycle_disposition_v0/evaluation_key_v0.json#/cells/A"
    ),
}

EXACT_BASIS_REFS = {
    "execution_freeze": (
        "git-blob:17fdc143f61336d1bd9e42e578c9ef481f84692c:"
        "fixtures/lane_lifecycle_disposition_v0/EXECUTION_FREEZE_001.json"
    ),
    "producer_registry": (
        "git-blob:6b469f82a4e9c12e9c6bb143a646ccaba393bedb:"
        "fixtures/lane_lifecycle_disposition_v0/producer_registry_v0.json"
    ),
    "basis_catalog": (
        "git-blob:170795fc3638cca1fdf008b3a7e2b5746520f8c2:"
        "fixtures/lane_lifecycle_disposition_v0/basis_catalog_v0.json"
    ),
}

EXACT_SPECIMEN_CONTENT_IDENTITY = (
    "sha256:0070296a2edf3e8f801c0e81b14fa924f1343323dc847d78dcc36aafd287e06c"
)
EXACT_ADJUDICATION_CONTENT_IDENTITY = (
    "sha256:82d802f9696b54c2d414c9f6c11043b2ce32a7c991de7fb5ced1cbbaa860745a"
)

AUTHORIZATION_CELL_IDS = ("A", "B0", "B1", "B2", "B3", "B4")

EXACT_AUTHORIZATION_CONTENT_IDENTITIES = {
    "A": "sha256:f0899813acf450979b8ca0f19926374cb94c79908b66461472e85742705f294d",
    "B0": "ABSENT_BY_SPECIMEN_DESIGN",
    "B1": "sha256:354a23ff8908ffbf6ff7dc95f6328947821e3a0b68f6bd709fc8592038b24192",
    "B2": "sha256:c58601690adaeae8639da24aa4a60c4369a4e16177abbfcd5439e4e5d5e2463c",
    "B3": "sha256:8113b189faa13d3a616c0f5b626acbc55895054d6ae89c152850df88f17f1dfd",
    "B4": "sha256:3c33e85466f7124b7c929ef2bdbf8ab01f182951771bc063394ab5ac2c4861f9",
}
EXACT_EXECUTION_ENVELOPE_CONTENT_IDENTITY = (
    "sha256:48e78654c42c5ef838c78ab915e1d8deb09ae52fe0a4e52ed1368192ed4b1d21"
)

_AUTHORIZATION_FIXTURE_BLOBS = {
    "A": "a3dff6392e30f89f016f05a2fa0e048fdfb460f4",
    "B1": "8de3c222edae0bf26b4545fc226bd4d23655ecd8",
    "B2": "db2ba2f6a97efc8e4bae01562e859ef80f348196",
    "B3": "d3615d808f5961ae2b8ea568ee781af8dfee6875",
    "B4": "dd2007ed929c07d88f672ef45fd020e2a96a18d2",
}

EXACT_AUTHORIZATION_BASIS_REFS = {
    "apparatus_contract": (
        "git-blob:8d20932c9fc63923c5981ffcb139f73b000cef4d:"
        "lab/ops/candidates/authorization_to_active_001/README.md"
    ),
    "bounded_checkpoint": (
        "git-blob:c16c60f28e063a5465c07f9122e718425a6c994c:"
        "lab/ops/checkpoints/AUTHORIZATION_TO_ACTIVE_001_COMPLETE.md"
    ),
    "apparatus_qualification": (
        "git-blob:761597e7d72e89b567b7f665759d378303997f43:"
        "tests/lab/test_authorization_to_active_001_apparatus.py"
    ),
}

EXACT_SPARSE_OBSERVATION_EVIDENCE_IDENTITY = (
    "sha256:5efafda949329d1e7fe55af16d733355b377cf0fa4b79c7e24f980dbc9aa2740"
)

EXACT_SPARSE_OBSERVATION_SOURCE_REFS = {
    "frame_0_capture": (
        "git-blob:7b332ec693e9ee07bde4999d549d9940e6f8d778:"
        "traces/absent_interval_round_trip_pressure_v0.json"
        "#/specimens/S1/first_capture"
    ),
    "frame_1_capture": (
        "git-blob:7b332ec693e9ee07bde4999d549d9940e6f8d778:"
        "traces/absent_interval_round_trip_pressure_v0.json"
        "#/specimens/S1/second_capture"
    ),
    "endpoint_relation": (
        "git-blob:7b332ec693e9ee07bde4999d549d9940e6f8d778:"
        "traces/absent_interval_round_trip_pressure_v0.json"
        "#/specimens/S1/endpoint_relation"
    ),
    "occurrence_relation": (
        "git-blob:7b332ec693e9ee07bde4999d549d9940e6f8d778:"
        "traces/absent_interval_round_trip_pressure_v0.json"
        "#/specimens/S1/occurrence_relation"
    ),
    "admission_health": (
        "git-blob:7b332ec693e9ee07bde4999d549d9940e6f8d778:"
        "traces/absent_interval_round_trip_pressure_v0.json"
        "#/specimens/S1/health"
    ),
    "recovery": (
        "git-blob:7b332ec693e9ee07bde4999d549d9940e6f8d778:"
        "traces/absent_interval_round_trip_pressure_v0.json"
        "#/specimens/S1/recovery"
    ),
}

EXACT_SPARSE_OBSERVATION_BASIS_REFS = {
    "pressure_decision": (
        "git-blob:30258b1dede09dbcaec0162f03ab070486b3d0f8:"
        "docs/decisions/reconstruction/absent_interval_round_trip_pressure_v0.md"
    ),
    "pressure_harness": (
        "git-blob:33777be545695a6be6ea5f89aab129bd75312285:"
        "src/runtime/absent_interval_round_trip_pressure.py"
    ),
    "pressure_tests": (
        "git-blob:703fa773ba4290229a0c1ab506f8fdbef573d04a:"
        "tests/runtime/test_absent_interval_round_trip_pressure.py"
    ),
    "capture_coordinator": (
        "git-blob:794312d1b92fe98a789bffc67bafb012f1579963:"
        "src/runtime/foreground_repository_observation.py"
    ),
    "ledger": (
        "git-blob:bb4360687a3f19a36ea03bca306caa98a78aaaeb:"
        "src/ledger/jsonl.py"
    ),
    "admission": (
        "git-blob:44c3248a7a80776b486c92dcabed0a64ca7168f1:"
        "src/ingest/admission.py"
    ),
    "reconstruction": (
        "git-blob:49f31438b380a36afbc5b04f1506d68bebf0d3cc:"
        "src/reconstruction/admission.py"
    ),
}


class ProjectionInputError(ValueError):
    """The supplied objects do not match the exact bounded specimen."""


def _canonical_bytes(value: Any) -> bytes:
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


def _content_identity(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def exact_authorization_source_refs(cell_id: str) -> dict[str, str]:
    """Return the retained source coordinates for one frozen A/B0-B4 cell."""

    if cell_id not in AUTHORIZATION_CELL_IDS:
        raise ProjectionInputError(f"unsupported authorization cell: {cell_id!r}")
    if cell_id == "B0":
        authorization_ref = (
            "git-blob:8d20932c9fc63923c5981ffcb139f73b000cef4d:"
            "lab/ops/candidates/authorization_to_active_001/README.md#B0-AO-absence"
        )
    else:
        fixture_name = "authorization_A.json" if cell_id == "A" else f"authorization_{cell_id}.json"
        authorization_ref = (
            f"git-blob:{_AUTHORIZATION_FIXTURE_BLOBS[cell_id]}:"
            "lab/ops/candidates/authorization_to_active_001/fixtures/"
            f"{fixture_name}"
        )
    return {
        "authorization": authorization_ref,
        "execution_envelope": (
            "git-blob:963d467d383f4e6346833dc3a2987ce1fb01a704:"
            "lab/ops/candidates/authorization_to_active_001/fixtures/"
            "execution_envelope.json"
        ),
        "correspondence": (
            "git-blob:191f6dfa6aab14293f94b6bca3365b8b14e0aab7:"
            "lab/ops/candidates/authorization_to_active_001/correspondence.py"
        ),
        "materializer": (
            "git-blob:e0590ad965f66e193218c40eaa767d7e62189a76:"
            "lab/ops/candidates/authorization_to_active_001/materializer.py"
        ),
        "exclusive_latch": (
            "git-blob:694e824e9c4b6db742b1c51e2539027562c10f00:"
            "lab/ops/candidates/execution_stop_latch_001/stop_latch.py"
        ),
    }


def _require_exact_mapping(
    supplied: Mapping[str, str],
    expected: Mapping[str, str],
    label: str,
) -> None:
    if dict(supplied) != dict(expected):
        raise ProjectionInputError(f"{label} does not match the exact Cell-A basis")


def _validate_exact_specimen(
    lifecycle_input: Mapping[str, Any],
    adjudication: Mapping[str, Any],
) -> None:
    if _content_identity(lifecycle_input) != EXACT_SPECIMEN_CONTENT_IDENTITY:
        raise ProjectionInputError("lifecycle_input is not exact lifecycle COMPLETE Cell A")

    consulted = adjudication.get("predicates_consulted", {}).get("admissibility")
    if tuple(consulted or ()) != EXACT_GUARD_SEQUENCE:
        raise ProjectionInputError("exact P01-P08 joint guard is required")
    if _content_identity(adjudication) != EXACT_ADJUDICATION_CONTENT_IDENTITY:
        raise ProjectionInputError("adjudication is not the exact Cell-A controller result")


def _roles(
    projection_question: str,
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> dict[str, Any]:
    frozen_basis = [basis_refs[key] for key in sorted(basis_refs)]
    if projection_question == CONTROLLER_CENTERED:
        return {
            "S": {
                "configuration": "LIFECYCLE_CONTROLLER",
                "source_ref": source_refs["controller"],
            },
            "O": {
                "configuration": "CLAIM_LANE_REQUEST_TUPLE",
                "source_ref": source_refs["specimen_input"],
            },
            "F": {
                "configuration": "FROZEN_QUALIFICATION_BASIS",
                "basis_refs": frozen_basis,
            },
        }
    return {
        "S": {
            "configuration": "CLAIM_LANE_REQUEST_TUPLE",
            "source_ref": source_refs["specimen_input"],
        },
        "O": {
            "configuration": "CONTROLLER_ADJUDICATION",
            "source_ref": source_refs["evaluation_key"],
        },
        "F": {
            "configuration": "CONTROLLER_AND_FROZEN_QUALIFICATION_BASIS",
            "source_refs": [source_refs["controller"], *frozen_basis],
        },
    }


def _derived_projection_identity(
    projection_question: str,
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> str:
    identity_basis = {
        "projection_version": "draci_local_frame_v0_lifecycle_complete_cell_a",
        "projection_question": projection_question,
        "source_refs": dict(source_refs),
        "basis_refs": dict(basis_refs),
    }
    return "derived-view:" + _content_identity(identity_basis)


def project_lifecycle_complete_cell_a(
    *,
    projection_question: str,
    lifecycle_input: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> dict[str, Any]:
    """Project the exact qualified lifecycle COMPLETE Cell-A specimen.

    Every input is caller-supplied.  The function performs no I/O, lookup,
    append, mutation, lifecycle evaluation, or currentness/authority inference.
    """

    if projection_question not in SUPPORTED_PROJECTIONS:
        raise ProjectionInputError(
            f"unsupported projection_question: {projection_question!r}"
        )
    _require_exact_mapping(source_refs, EXACT_SOURCE_REFS, "source_refs")
    _require_exact_mapping(basis_refs, EXACT_BASIS_REFS, "basis_refs")
    _validate_exact_specimen(lifecycle_input, adjudication)

    supplied_input = copy.deepcopy(dict(lifecycle_input))
    supplied_adjudication = copy.deepcopy(dict(adjudication))
    retained_source_refs = copy.deepcopy(dict(source_refs))
    retained_basis_refs = copy.deepcopy(dict(basis_refs))

    claim = supplied_input["claim"]
    lane = supplied_input["lane"]
    request = supplied_input["request"]
    resulting = supplied_adjudication["resulting_state"]

    occupant_binding = lane["occupant_binding"]
    pre_relations = {
        "claim_status": claim["status"],
        "lane_status": lane["status"],
        "occupant_binding": occupant_binding,
        "occupant_presence": "PRESENT" if occupant_binding is not None else "ABSENT",
    }
    operative_relations = {
        "requested_transition": request["requested_transition"],
        "selected_branch": supplied_adjudication["selected_branch"],
        "joint_guard": list(EXACT_GUARD_SEQUENCE),
        "admissible": supplied_adjudication["admissible"],
    }
    post_relations = {
        "projected": copy.deepcopy(resulting),
        "realized": "UNRESOLVED",
    }

    pairwise = {
        "R_SO": {
            "relation": "controller_to_claim_lane_request",
            "standing": "COORDINATE_ONLY",
        },
        "R_SF": {
            "relation": "controller_to_frozen_basis",
            "standing": "COORDINATE_ONLY",
        },
        "R_OF": {
            "relation": "claim_lane_request_to_frozen_basis",
            "standing": "COORDINATE_ONLY",
        },
        "joint_admissibility_established": False,
    }
    higher_order_couplings = [
        {
            "coupling": "EXACT_P01_P08_JOINT_GUARD",
            "predicates": list(EXACT_GUARD_SEQUENCE),
            "source": "adjudication.predicates_consulted.admissibility",
            "standing": "JOINT_CONTROLLER_ADJUDICATION_BASIS",
            "pairwise_substitution": "FORBIDDEN",
        }
    ]

    event = {
        "local_label": "EVENT_1",
        "label_standing": "DERIVED_VIEW_ONLY_NOT_SOURCE_EVENT_ID",
        "kind": "BOUNDED_DISPOSITION_ADJUDICATION_OCCURRENCE",
        "origin": {
            "location": "controller evaluation",
            "source_ref": retained_source_refs["controller"],
        },
        "footprint": [
            "request",
            "selection",
            "P01-P08 joint guard",
            "returned adjudication",
        ],
        "full_consequence_footprint": {
            "controller_execution_effect": supplied_adjudication["execution_effect"],
            "live_execution": "EXPLICITLY_ABSENT",
            "downstream_consequences": "UNRESOLVED",
        },
        "occurrence": {
            "scope": "bounded disposition adjudication",
            "status": "OCCURRED",
        },
        "consequence_closure": {
            "adjudication_return": "CLOSED",
            "live_execution": "NOT_PERFORMED",
            "downstream_consequences": "UNRESOLVED",
        },
    }

    projection = {
        "projection_question": projection_question,
        "projection_identity": _derived_projection_identity(
            projection_question, retained_source_refs, retained_basis_refs
        ),
        "projection_identity_standing": "DERIVED_VIEW_ONLY",
        "source_refs": retained_source_refs,
        "source_content_identities": {
            "specimen_input": EXACT_SPECIMEN_CONTENT_IDENTITY,
            "adjudication": EXACT_ADJUDICATION_CONTENT_IDENTITY,
        },
        "basis_refs": retained_basis_refs,
        "roles": _roles(
            projection_question, retained_source_refs, retained_basis_refs
        ),
        "pairwise_relations": pairwise,
        "temporal_relations": {
            "temporal_anchor": "bounded disposition adjudication",
            "PRE": pre_relations,
            "OPERATIVE": operative_relations,
            "POST": post_relations,
        },
        "post_mode": "ADJUDICATED",
        "higher_order_couplings": higher_order_couplings,
        "observation_depth": {
            "adjudication": {
                "realized": "CONTROLLER_RESULT_RETURNED",
                "observed": "SOURCE_RESULT_SUPPLIED",
                "evidenced": "EXACT_SOURCE_REFS_RETAINED",
                "qualified": "LANE_LIFECYCLE_DISPOSITION_001_BOUNDED_SCOPE",
            },
            "live_post_state": {
                "realized": "UNRESOLVED",
                "observed": "UNRESOLVED",
                "evidenced": "UNRESOLVED",
                "qualified": "UNRESOLVED",
            },
        },
        "currentness": "UNRESOLVED",
        "authority": {
            "view": "DERIVED_SOURCE_BOUND_VIEW_ONLY",
            "source_authority_effect": supplied_adjudication["authority_effect"],
            "general_authority_standing": "NONE",
        },
        "execution_effect": supplied_adjudication["execution_effect"],
        "event": event,
        "trajectory": ["FRAME_0", "EVENT_1", "FRAME_1"],
        "trajectory_standing": "DERIVED_VIEW_ONLY",
        "frame_labels_are_authoritative_ids": False,
        "unresolved_coordinates": [
            "live post-execution state",
            "downstream consequence closure",
            "currentness",
            "general authority standing",
        ],
    }
    return projection


def _validate_authorization_specimen(
    *,
    cell_id: str,
    authorization: Mapping[str, Any] | None,
    execution_envelope: Mapping[str, Any],
    materialization_observation: Mapping[str, Any],
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> None:
    expected_sources = exact_authorization_source_refs(cell_id)
    _require_exact_mapping(source_refs, expected_sources, "authorization source_refs")
    _require_exact_mapping(
        basis_refs, EXACT_AUTHORIZATION_BASIS_REFS, "authorization basis_refs"
    )

    if _content_identity(execution_envelope) != EXACT_EXECUTION_ENVELOPE_CONTENT_IDENTITY:
        raise ProjectionInputError("execution_envelope is not the exact frozen specimen")

    expected_authorization_identity = EXACT_AUTHORIZATION_CONTENT_IDENTITIES[cell_id]
    if cell_id == "B0":
        if authorization is not None:
            raise ProjectionInputError("B0 requires authorization-object absence")
    elif authorization is None or _content_identity(authorization) != expected_authorization_identity:
        raise ProjectionInputError(f"authorization is not the exact frozen {cell_id} specimen")

    positive = cell_id == "A"
    expected_observation = {
        "prior_state_exists": False,
        "corresponds": positive,
        "materializer_returned_path": positive,
        "carrier_exists": positive,
        "carrier_state": "ACTIVE" if positive else None,
    }
    if dict(materialization_observation) != expected_observation:
        raise ProjectionInputError(
            f"materialization observation does not match retained {cell_id} evidence"
        )


def _authorization_roles(
    projection_question: str,
    source_refs: Mapping[str, str],
) -> dict[str, Any]:
    if projection_question == AUTHORIZATION_OBJECT_CENTERED:
        return {
            "S": {
                "configuration": "EXACT_AUTHORIZATION_OBJECT_UNDER_BOUNDED_MATERIALIZER",
                "source_ref": source_refs["authorization"],
            },
            "O": {
                "configuration": "EXECUTION_ENVELOPE_AND_STATE_CARRIER",
                "source_refs": [
                    source_refs["execution_envelope"],
                    source_refs["exclusive_latch"],
                ],
            },
            "F": {
                "configuration": "CORRESPONDENCE_RULE_CLEAN_ROOT_EXCLUSIVE_LATCH",
                "source_refs": [
                    source_refs["correspondence"],
                    source_refs["materializer"],
                    source_refs["exclusive_latch"],
                ],
            },
        }
    return {
        "S": {
            "configuration": "EXECUTION_STATE_CARRIER_UNDER_EXCLUSIVE_LATCH",
            "source_refs": [
                source_refs["execution_envelope"],
                source_refs["exclusive_latch"],
            ],
        },
        "O": {
            "configuration": "AUTHORIZATION_OBJECT_AND_EXECUTION_ENVELOPE",
            "source_refs": [
                source_refs["authorization"],
                source_refs["execution_envelope"],
            ],
        },
        "F": {
            "configuration": "CORRESPONDENCE_AND_MATERIALIZATION_APPARATUS",
            "source_refs": [
                source_refs["correspondence"],
                source_refs["materializer"],
            ],
        },
    }


def _authorization_term_results(
    authorization: Mapping[str, Any] | None,
    execution_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    if authorization is None:
        return {
            "authorization_object_present": False,
            "execution_envelope_id_equal": "NOT_EVALUATED",
            "implementation_basis_equal": "NOT_EVALUATED",
            "requested_consequence_allowed": "NOT_EVALUATED",
            "authorization_status_live": "NOT_EVALUATED",
            "prior_state_absent": True,
        }
    return {
        "authorization_object_present": True,
        "execution_envelope_id_equal": (
            authorization["execution_envelope_id"]
            == execution_envelope["execution_envelope_id"]
        ),
        "implementation_basis_equal": (
            authorization["implementation_basis"]
            == execution_envelope["implementation_basis"]
        ),
        "requested_consequence_allowed": (
            execution_envelope["requested_consequence"]
            in authorization["allowed_consequences"]
        ),
        "authorization_status_live": authorization["status"] == "LIVE",
        "prior_state_absent": True,
    }


def _derived_authorization_projection_identity(
    *,
    projection_question: str,
    cell_id: str,
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
    materialization_observation: Mapping[str, Any],
) -> str:
    identity_basis = {
        "projection_version": "draci_local_frame_v0_authorization_to_active_001",
        "projection_question": projection_question,
        "cell_id": cell_id,
        "source_refs": dict(source_refs),
        "basis_refs": dict(basis_refs),
        "materialization_observation": dict(materialization_observation),
    }
    return "derived-view:" + _content_identity(identity_basis)


def project_authorization_to_active_001(
    *,
    projection_question: str,
    cell_id: str,
    authorization: Mapping[str, Any] | None,
    execution_envelope: Mapping[str, Any],
    materialization_observation: Mapping[str, Any],
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> dict[str, Any]:
    """Project one exact retained AUTHORIZATION_TO_ACTIVE_001 A/B0-B4 cell.

    The materializer and correspondence mechanism are not invoked here.  Their
    exact, externally observed bounded result is supplied by the caller.
    """

    if projection_question not in SUPPORTED_AUTHORIZATION_PROJECTIONS:
        raise ProjectionInputError(
            f"unsupported authorization projection_question: {projection_question!r}"
        )
    if cell_id not in AUTHORIZATION_CELL_IDS:
        raise ProjectionInputError(f"unsupported authorization cell: {cell_id!r}")

    _validate_authorization_specimen(
        cell_id=cell_id,
        authorization=authorization,
        execution_envelope=execution_envelope,
        materialization_observation=materialization_observation,
        source_refs=source_refs,
        basis_refs=basis_refs,
    )

    retained_authorization = (
        None if authorization is None else copy.deepcopy(dict(authorization))
    )
    retained_envelope = copy.deepcopy(dict(execution_envelope))
    retained_observation = copy.deepcopy(dict(materialization_observation))
    retained_source_refs = copy.deepcopy(dict(source_refs))
    retained_basis_refs = copy.deepcopy(dict(basis_refs))
    positive = cell_id == "A"

    correspondence_standing = "CORRESPONDS" if positive else "NONCORRESPONDING"
    carrier_standing = "ACTIVE" if positive else "ABSENT"
    local_closure = "CLOSED_ACTIVE" if positive else "CLOSED_ABSENT"
    term_results = _authorization_term_results(
        retained_authorization, retained_envelope
    )

    pairwise_relations = {
        "R_SO": {
            "relation": "authorization_object_to_execution_envelope",
            "standing": "COORDINATE_ONLY",
        },
        "R_SF": {
            "relation": "authorization_object_to_materialization_field",
            "standing": "COORDINATE_ONLY",
        },
        "R_OF": {
            "relation": "execution_envelope_carrier_to_materialization_field",
            "standing": "COORDINATE_ONLY",
        },
        "active_materialization_established": False,
    }
    higher_order_couplings = [
        {
            "coupling": "EXACT_AO_ENVELOPE_CLEAN_ROOT_CONJUNCTION",
            "authorization_object_presence": term_results[
                "authorization_object_present"
            ],
            "required_terms": [
                "execution_envelope_id_equal",
                "implementation_basis_equal",
                "requested_consequence_allowed",
                "authorization_status_live",
                "prior_state_absent",
            ],
            "term_results": term_results,
            "conjunction_result": correspondence_standing,
            "pairwise_substitution": "FORBIDDEN",
        }
    ]

    pre_relations = {
        "state_root": "CLEAN",
        "execution_state_carrier": "ABSENT",
        "authorization_object": "PRESENT" if authorization is not None else "ABSENT",
    }
    operative_relations = {
        "correspondence_derivation": correspondence_standing,
        "materialization_attempt": "OCCURRED",
        "clean_root_exclusion_check": "PRIOR_STATE_ABSENT",
        "exclusive_carrier_creation": "CREATED" if positive else "NOT_CREATED",
    }
    post_relations = {
        "execution_envelope_id": retained_envelope["execution_envelope_id"],
        "active_carrier": carrier_standing,
        "workshop_execution": "UNRESOLVED",
    }

    observation_depth = {
        "active_carrier": {
            "realized": carrier_standing,
            "observed": carrier_standing,
            "evidenced": "MATERIALIZER_REPORT_AND_EXTERNAL_CARRIER_OBSERVATION",
            "qualified": (
                "AUTHORIZATION_TO_ACTIVE_001_BOUNDED_POSITIVE_PROPERTY"
                if positive
                else f"AUTHORIZATION_TO_ACTIVE_001_{cell_id}_BOUNDED_ABSENCE"
            ),
        },
        "workshop_execution": {
            "realized": "UNRESOLVED",
            "observed": "UNRESOLVED",
            "evidenced": "UNRESOLVED",
            "qualified": "UNRESOLVED",
        },
    }

    event = {
        "local_label": "EVENT_1",
        "label_standing": "DERIVED_VIEW_ONLY_NOT_SOURCE_EVENT_ID",
        "kind": "BOUNDED_ACTIVE_MATERIALIZATION_ATTEMPT",
        "origin": {
            "location": "bounded materializer invocation",
            "source_ref": retained_source_refs["materializer"],
        },
        "footprint": [
            "correspondence derivation",
            "state-root exclusion check",
            "exclusive carrier creation",
        ],
        "full_consequence_footprint": {
            "active_carrier": carrier_standing,
            "workshop_consequence": "UNRESOLVED",
        },
        "occurrence": {
            "scope": "bounded materialization attempt",
            "status": "OCCURRED",
        },
        "consequence_closure": {
            "active_materialization": local_closure,
            "workshop_consequence": "UNRESOLVED",
        },
    }

    return {
        "specimen": "AUTHORIZATION_TO_ACTIVE_001",
        "cell_id": cell_id,
        "projection_question": projection_question,
        "projection_identity": _derived_authorization_projection_identity(
            projection_question=projection_question,
            cell_id=cell_id,
            source_refs=retained_source_refs,
            basis_refs=retained_basis_refs,
            materialization_observation=retained_observation,
        ),
        "projection_identity_standing": "DERIVED_VIEW_ONLY",
        "source_refs": retained_source_refs,
        "source_content_identities": {
            "authorization": EXACT_AUTHORIZATION_CONTENT_IDENTITIES[cell_id],
            "execution_envelope": EXACT_EXECUTION_ENVELOPE_CONTENT_IDENTITY,
        },
        "basis_refs": retained_basis_refs,
        "roles": _authorization_roles(
            projection_question, retained_source_refs
        ),
        "pairwise_relations": pairwise_relations,
        "temporal_relations": {
            "temporal_anchor": "bounded initial ACTIVE materialization attempt",
            "PRE": pre_relations,
            "OPERATIVE": operative_relations,
            "POST": post_relations,
        },
        "post_mode": "REALIZED" if positive else "OBSERVED",
        "higher_order_couplings": higher_order_couplings,
        "observation_depth": observation_depth,
        "currentness": "UNRESOLVED",
        "authority": {
            "view": "DERIVED_SOURCE_BOUND_VIEW_ONLY",
            "authorization_correspondence": correspondence_standing,
            "issuer_authority": "UNRESOLVED",
            "general_authority": "NOT_ESTABLISHED",
            "delegation": "NOT_ESTABLISHED",
            "retry_authority": "NOT_ESTABLISHED",
        },
        "event": event,
        "trajectory": ["FRAME_0", "EVENT_1", "FRAME_1"],
        "trajectory_standing": "DERIVED_VIEW_ONLY",
        "frame_labels_are_authoritative_ids": False,
        "unresolved_coordinates": [
            "issuer authority",
            "general authority",
            "currentness",
            "Workshop execution",
            "downstream consequence closure",
            "delegation",
            "retry authority",
            "STOP integration",
        ],
    }


def _validate_sparse_observation_evidence(
    sparse_evidence: Mapping[str, Any],
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> None:
    _require_exact_mapping(
        source_refs,
        EXACT_SPARSE_OBSERVATION_SOURCE_REFS,
        "sparse-observation source_refs",
    )
    _require_exact_mapping(
        basis_refs,
        EXACT_SPARSE_OBSERVATION_BASIS_REFS,
        "sparse-observation basis_refs",
    )
    if _content_identity(sparse_evidence) != EXACT_SPARSE_OBSERVATION_EVIDENCE_IDENTITY:
        raise ProjectionInputError(
            "sparse_evidence is not the exact admitted S1 endpoint basis"
        )

    first = sparse_evidence["first_capture"]
    second = sparse_evidence["second_capture"]
    endpoint = sparse_evidence["endpoint_relation"]
    occurrence = sparse_evidence["occurrence_relation"]
    health = sparse_evidence["health"]
    recovery = sparse_evidence["recovery"]

    if first["filesystem_configuration"] != second["filesystem_configuration"]:
        raise ProjectionInputError("S1 filesystem endpoints are not equivalent")
    if first["git_configuration"] != second["git_configuration"]:
        raise ProjectionInputError("S1 Git endpoints are not equivalent")
    if endpoint != {
        "filesystem_configuration_equivalent": True,
        "git_configuration_equivalent": True,
        "both_sources_equivalent": True,
    }:
        raise ProjectionInputError("S1 endpoint relation is not exact equivalence")
    if occurrence.get("distinct_observation_occurrences") is not True:
        raise ProjectionInputError("S1 observation occurrences are not distinct")

    occurrence_ids = [
        first["filesystem_occurrence"]["record_id"],
        first["git_occurrence"]["record_id"],
        second["filesystem_occurrence"]["record_id"],
        second["git_occurrence"]["record_id"],
    ]
    if len(set(occurrence_ids)) != 4:
        raise ProjectionInputError("S1 source observation identities collapsed")
    if health.get("projection_subject_ids") != occurrence_ids:
        raise ProjectionInputError("S1 admitted projection subjects do not match endpoints")
    if health.get("structurally_healthy") is not True:
        raise ProjectionInputError("S1 retained observation basis is not healthy")
    if recovery.get("driver_path_available") is not False:
        raise ProjectionInputError("external driver path entered recovered evidence")


def _sparse_observation_roles(
    projection_question: str,
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> dict[str, Any]:
    observation_refs = [
        source_refs["frame_0_capture"],
        source_refs["frame_1_capture"],
    ]
    field_refs = [basis_refs[key] for key in sorted(basis_refs)]
    if projection_question == REPOSITORY_CENTERED:
        return {
            "S": {
                "configuration": "BOUNDED_REPOSITORY_FIXTURE_OBSERVED_SUBJECT",
                "source_refs": observation_refs,
            },
            "O": {
                "configuration": "CAPTURED_FILESYSTEM_AND_GIT_ENDPOINTS",
                "source_refs": observation_refs,
            },
            "F": {
                "configuration": "FOREGROUND_CAPTURE_LEDGER_ADMISSION_RECONSTRUCTION",
                "basis_refs": field_refs,
            },
        }
    return {
        "S": {
            "configuration": "FOREGROUND_OBSERVATION_AND_RECONSTRUCTION_APPARATUS",
            "basis_refs": field_refs,
        },
        "O": {
            "configuration": "DISTINCT_ADMITTED_ENDPOINT_OCCURRENCES",
            "source_refs": observation_refs,
        },
        "F": {
            "configuration": "BOUNDED_REPOSITORY_AND_RETAINED_EVIDENCE_BASIS",
            "source_refs": [*observation_refs, source_refs["admission_health"]],
        },
    }


def _endpoint_occurrence(capture: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "filesystem": copy.deepcopy(capture["filesystem_occurrence"]),
        "git": copy.deepcopy(capture["git_occurrence"]),
        "admission_standing": "ADMITTED_AND_PROJECTED_IN_BOUNDED_TRACE",
    }


def _derived_sparse_projection_identity(
    *,
    projection_question: str,
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> str:
    identity_basis = {
        "projection_version": "draci_local_frame_v0_sparse_observation_s1",
        "projection_question": projection_question,
        "source_refs": dict(source_refs),
        "basis_refs": dict(basis_refs),
        "evidence_identity": EXACT_SPARSE_OBSERVATION_EVIDENCE_IDENTITY,
    }
    return "derived-view:" + _content_identity(identity_basis)


def project_sparse_observation_s1(
    *,
    projection_question: str,
    sparse_evidence: Mapping[str, Any],
    source_refs: Mapping[str, str],
    basis_refs: Mapping[str, str],
) -> dict[str, Any]:
    """Project exact admitted S1 endpoints without importing driver knowledge."""

    if projection_question not in SUPPORTED_SPARSE_OBSERVATION_PROJECTIONS:
        raise ProjectionInputError(
            f"unsupported sparse-observation projection_question: {projection_question!r}"
        )
    _validate_sparse_observation_evidence(sparse_evidence, source_refs, basis_refs)

    evidence = copy.deepcopy(dict(sparse_evidence))
    retained_source_refs = copy.deepcopy(dict(source_refs))
    retained_basis_refs = copy.deepcopy(dict(basis_refs))
    first = evidence["first_capture"]
    second = evidence["second_capture"]

    frame_0_occurrence = _endpoint_occurrence(first)
    frame_1_occurrence = _endpoint_occurrence(second)
    frame_0_configuration = {
        "filesystem": copy.deepcopy(first["filesystem_configuration"]),
        "git": copy.deepcopy(first["git_configuration"]),
    }
    frame_1_configuration = {
        "filesystem": copy.deepcopy(second["filesystem_configuration"]),
        "git": copy.deepcopy(second["git_configuration"]),
    }

    transition_gap = {
        "kind": "TRANSITION_GAP",
        "standing": "BOUNDED_UNOBSERVED_INTERVAL",
        "event": "NOT_DERIVED",
        "event_hypothesis": "UNRESOLVED",
        "intermediate_frame": "NOT_DERIVED",
        "intermediate_trajectory": "UNRESOLVED",
    }

    return {
        "specimen": "ABSENT_INTERVAL_ROUND_TRIP_PRESSURE_V0_S1",
        "projection_question": projection_question,
        "projection_identity": _derived_sparse_projection_identity(
            projection_question=projection_question,
            source_refs=retained_source_refs,
            basis_refs=retained_basis_refs,
        ),
        "projection_identity_standing": "DERIVED_VIEW_ONLY",
        "source_refs": retained_source_refs,
        "source_content_identity": EXACT_SPARSE_OBSERVATION_EVIDENCE_IDENTITY,
        "basis_refs": retained_basis_refs,
        "roles": _sparse_observation_roles(
            projection_question, retained_source_refs, retained_basis_refs
        ),
        "endpoint_occurrences": {
            "FRAME_0": frame_0_occurrence,
            "FRAME_1": frame_1_occurrence,
        },
        "endpoint_configurations": {
            "FRAME_0": frame_0_configuration,
            "FRAME_1": frame_1_configuration,
        },
        "endpoint_relation": {
            "configuration": "EQUIVALENT",
            "observation_occurrences": "DISTINCT",
            "configuration_equality_collapses_occurrence_identity": False,
        },
        "temporal_relations": {
            "temporal_anchor": "two admitted endpoint observation occurrences",
            "PRE": {
                "frame": "FRAME_0",
                "observation_occurrence": frame_0_occurrence,
            },
            "OPERATIVE": transition_gap,
            "POST": {
                "frame": "FRAME_1",
                "observation_occurrence": frame_1_occurrence,
            },
        },
        "post_mode": "OBSERVED",
        "transition_gap": transition_gap,
        "event": None,
        "event_hypothesis": "UNRESOLVED",
        "consequence_closure": "UNAVAILABLE_NO_ADMITTED_EVENT",
        "known_invariants": [
            "observation occurrence identities are distinct",
            "source provenance is retained",
            "endpoint filesystem configurations are equivalent",
            "endpoint Git configurations are equivalent",
            "all four endpoint source observations are admitted and projected",
            "FRAME_0 precedes FRAME_1 in retained commit order",
        ],
        "observation_depth": {
            "endpoints": {
                "observed": True,
                "evidenced": "EXACT_RETAINED_TRACE_COORDINATES",
                "qualified": "ABSENT_INTERVAL_ROUND_TRIP_BOUNDED_SCOPE",
            },
            "intermediate_path": {
                "observed": "UNRESOLVED",
                "evidenced": "UNRESOLVED",
                "qualified": "UNRESOLVED",
            },
        },
        "external_driver_ceiling": {
            "driver_path_in_projection_input": False,
            "driver_path_available_after_recovery": False,
            "driver_knowledge_imported": False,
            "reconstructed_interval_claim": "UNRESOLVED",
        },
        "currentness": "UNRESOLVED",
        "authority": {
            "view": "DERIVED_SOURCE_BOUND_VIEW_ONLY",
            "general_authority": "NOT_ESTABLISHED",
        },
        "trajectory": ["FRAME_0", "TRANSITION_GAP", "FRAME_1"],
        "trajectory_standing": "ENDPOINT_SEQUENCE_WITH_UNRESOLVED_INTERVAL",
        "frame_labels_are_authoritative_ids": False,
        "unresolved_coordinates": [
            "intermediate event sequence",
            "intermediate configurations",
            "whether any transformation occurred",
            "event hypothesis",
            "consequence closure",
            "generic currentness",
        ],
    }


__all__: Sequence[str] = (
    "AUTHORIZATION_OBJECT_CENTERED",
    "AUTHORIZATION_CELL_IDS",
    "CLAIM_LANE_CENTERED",
    "CONTROLLER_CENTERED",
    "EXACT_AUTHORIZATION_BASIS_REFS",
    "EXACT_BASIS_REFS",
    "EXACT_GUARD_SEQUENCE",
    "EXACT_SPARSE_OBSERVATION_BASIS_REFS",
    "EXACT_SPARSE_OBSERVATION_SOURCE_REFS",
    "EXACT_SOURCE_REFS",
    "LATCH_STATE_CARRIER_CENTERED",
    "OBSERVER_CENTERED",
    "ProjectionInputError",
    "REPOSITORY_CENTERED",
    "exact_authorization_source_refs",
    "project_authorization_to_active_001",
    "project_lifecycle_complete_cell_a",
    "project_sparse_observation_s1",
)
