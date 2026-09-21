#!/usr/bin/env python3
"""Bounded grammar pressure for PRIMARY_ECOLOGY_v0.

This apparatus qualifies only identity/observation separation. It creates no
live seats, occupants, invocations, work claims, authority, or execution.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "docs/candidates/primary_ecology_v0/fixtures"

ROLE_FIELDS = {
    "schema","role_id","purpose","may_observe","may_produce","may_request",
    "forbidden_effect_classes","authority_effect","execution_effect",
}
SEAT_FIELDS = {
    "schema","seat_id","role_id","seat_state","occupant_id","invocation_id",
    "work_claim_ref","cursor_ref","authority_effect","execution_effect",
}
BASIS_FIELDS = {
    "schema","basis_id","observer_seat_id","observer_occupant_id",
    "observer_invocation_id","basis_ref","observed_objects",
    "explicit_missing_objects","source_refs","authority_effect","execution_effect",
}
BINDING_FIELDS = {
    "schema","binding_id","role_id","seat_id","occupant_id","invocation_id",
    "observation_basis_ref","task_ref","work_claim_ref","standing_refs",
    "authority_refs","authority_effect","execution_effect",
}

PLACEHOLDERS = {"TBD", "UNKNOWN", "PLACEHOLDER", "NONE", "NULL"}


class EcologyError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def object_identity(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonempty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise EcologyError(f"{field} must be a non-empty string")


def _string_list(value: Any, field: str) -> None:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
        raise EcologyError(f"{field} must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise EcologyError(f"{field} must not contain duplicates")


def validate_role(role: Mapping[str, Any]) -> None:
    if not isinstance(role, Mapping) or set(role) != ROLE_FIELDS:
        raise EcologyError("role fields must be exact")
    if role["schema"] != "ecology_role_v0":
        raise EcologyError("wrong role schema")
    for field in ("role_id", "purpose"):
        _nonempty_string(role[field], field)
    for field in ("may_observe","may_produce","may_request","forbidden_effect_classes"):
        _string_list(role[field], field)
    if role["authority_effect"] != "NONE":
        raise EcologyError("ROLE_AUTHORITY_EFFECT_NOT_NONE")
    if role["execution_effect"] != "NONE":
        raise EcologyError("ROLE_EXECUTION_EFFECT_NOT_NONE")


def validate_seat(seat: Mapping[str, Any]) -> None:
    if not isinstance(seat, Mapping) or set(seat) != SEAT_FIELDS:
        raise EcologyError("seat fields must be exact")
    if seat["schema"] != "ecology_seat_v0":
        raise EcologyError("wrong seat schema")
    for field in ("seat_id","role_id"):
        _nonempty_string(seat[field], field)
    if seat["seat_state"] not in {"AVAILABLE_UNOCCUPIED","OCCUPIED_CANDIDATE"}:
        raise EcologyError("invalid seat_state")
    for field in ("occupant_id","invocation_id","work_claim_ref","cursor_ref"):
        value = seat[field]
        if value is not None:
            _nonempty_string(value, field)
            if value.upper() in PLACEHOLDERS:
                raise EcologyError(f"{field} placeholder identity forbidden")
    if seat["seat_state"] == "AVAILABLE_UNOCCUPIED":
        if seat["occupant_id"] is not None or seat["invocation_id"] is not None or seat["work_claim_ref"] is not None:
            raise EcologyError("EMPTY_SEAT_MUST_NOT_CARRY_OCCUPANT_INVOCATION_OR_CLAIM")
    if seat["seat_state"] == "OCCUPIED_CANDIDATE":
        if seat["occupant_id"] is None or seat["invocation_id"] is None:
            raise EcologyError("occupied candidate requires occupant and invocation")
    if seat["authority_effect"] != "NONE":
        raise EcologyError("SEAT_AUTHORITY_EFFECT_NOT_NONE")
    if seat["execution_effect"] != "NONE":
        raise EcologyError("SEAT_EXECUTION_EFFECT_NOT_NONE")


def validate_observation_basis(basis: Mapping[str, Any]) -> None:
    if not isinstance(basis, Mapping) or set(basis) != BASIS_FIELDS:
        raise EcologyError("observation basis fields must be exact")
    if basis["schema"] != "observation_basis_v0":
        raise EcologyError("wrong observation basis schema")
    for field in ("basis_id","observer_seat_id","observer_occupant_id","observer_invocation_id","basis_ref"):
        _nonempty_string(basis[field], field)
    if not isinstance(basis["observed_objects"], list) or not isinstance(basis["explicit_missing_objects"], list):
        raise EcologyError("observation lists must be lists")
    observed_ids: list[str] = []
    for row in basis["observed_objects"]:
        if not isinstance(row, dict) or set(row) != {"object_id","identity","source_ref"}:
            raise EcologyError("observed object fields must be exact")
        for field in ("object_id","identity","source_ref"):
            _nonempty_string(row[field], f"observed.{field}")
        observed_ids.append(row["object_id"])
    missing_ids: list[str] = []
    for row in basis["explicit_missing_objects"]:
        if not isinstance(row, dict) or set(row) != {"object_id","reason"}:
            raise EcologyError("missing object fields must be exact")
        for field in ("object_id","reason"):
            _nonempty_string(row[field], f"missing.{field}")
        missing_ids.append(row["object_id"])
    if len(observed_ids) != len(set(observed_ids)) or len(missing_ids) != len(set(missing_ids)):
        raise EcologyError("duplicate object identity in observation basis")
    if set(observed_ids) & set(missing_ids):
        raise EcologyError("object cannot be both observed and explicitly missing")
    _string_list(basis["source_refs"], "source_refs")
    if basis["authority_effect"] != "NONE" or basis["execution_effect"] != "NONE":
        raise EcologyError("observation basis effects must remain NONE")


def observation_basis_ref(basis: Mapping[str, Any]) -> str:
    validate_observation_basis(basis)
    return f"observation-basis://{basis['basis_id']}@{object_identity(dict(basis))}"


def validate_binding(binding: Mapping[str, Any]) -> None:
    if not isinstance(binding, Mapping) or set(binding) != BINDING_FIELDS:
        raise EcologyError("binding fields must be exact")
    if binding["schema"] != "ecology_engagement_binding_v0":
        raise EcologyError("wrong engagement binding schema")
    for field in ("binding_id","role_id","seat_id","occupant_id","invocation_id","observation_basis_ref","task_ref"):
        _nonempty_string(binding[field], field)
        if binding[field].upper() in PLACEHOLDERS:
            raise EcologyError(f"{field} placeholder identity forbidden")
    if binding["work_claim_ref"] is not None:
        _nonempty_string(binding["work_claim_ref"], "work_claim_ref")
    for field in ("standing_refs","authority_refs"):
        _string_list(binding[field], field)
    if binding["authority_effect"] != "NONE":
        raise EcologyError("BINDING_AUTHORITY_EFFECT_NOT_NONE")
    if binding["execution_effect"] != "NONE":
        raise EcologyError("BINDING_EXECUTION_EFFECT_NOT_NONE")


def validate_correspondence(
    *,
    role: Mapping[str, Any],
    seat: Mapping[str, Any],
    binding: Mapping[str, Any],
    basis: Mapping[str, Any],
) -> None:
    validate_role(role)
    validate_seat(seat)
    validate_binding(binding)
    validate_observation_basis(basis)

    if seat["seat_state"] != "OCCUPIED_CANDIDATE":
        raise EcologyError("CORRESPONDENCE_REQUIRES_OCCUPIED_CANDIDATE_SEAT")
    if binding["role_id"] != role["role_id"] or seat["role_id"] != role["role_id"]:
        raise EcologyError("ROLE_SEAT_BINDING_MISMATCH")
    if binding["seat_id"] != seat["seat_id"]:
        raise EcologyError("BINDING_SEAT_MISMATCH")
    if binding["occupant_id"] != seat["occupant_id"]:
        raise EcologyError("BINDING_SEAT_OCCUPANT_MISMATCH")
    if binding["invocation_id"] != seat["invocation_id"]:
        raise EcologyError("BINDING_SEAT_INVOCATION_MISMATCH")
    if binding["work_claim_ref"] != seat["work_claim_ref"]:
        raise EcologyError("SEAT_BINDING_WORK_CLAIM_MISMATCH")
    if basis["observer_seat_id"] != binding["seat_id"]:
        raise EcologyError("BINDING_BASIS_SEAT_MISMATCH")
    if basis["observer_occupant_id"] != binding["occupant_id"]:
        raise EcologyError("BINDING_BASIS_OCCUPANT_MISMATCH")
    if basis["observer_invocation_id"] != binding["invocation_id"]:
        raise EcologyError("BINDING_BASIS_INVOCATION_MISMATCH")
    expected_ref = observation_basis_ref(basis)
    if binding["observation_basis_ref"] != expected_ref:
        raise EcologyError("BINDING_OBSERVATION_BASIS_REF_MISMATCH")


def observation_status(basis: Mapping[str, Any], object_id: str) -> str:
    validate_observation_basis(basis)
    if any(row["object_id"] == object_id for row in basis["observed_objects"]):
        return "OBSERVED"
    if any(row["object_id"] == object_id for row in basis["explicit_missing_objects"]):
        return "MISSING"
    return "UNKNOWN"


def role_catalog() -> dict[str, Any]:
    value = _load(FIXTURE_DIR / "ROLE_CATALOG_v0.json")
    if not isinstance(value, dict):
        raise EcologyError("role catalog must be object")
    return value


def seat_catalog() -> dict[str, Any]:
    value = _load(FIXTURE_DIR / "SEAT_CATALOG_v0.json")
    if not isinstance(value, dict):
        raise EcologyError("seat catalog must be object")
    return value


def fixtures() -> dict[str, Any]:
    value = _load(FIXTURE_DIR / "RAW_FIXTURES_v0.json")
    if not isinstance(value, dict):
        raise EcologyError("fixtures must be object")
    return value


def clean_role(role_id: str = "SCIENTIST") -> dict[str, Any]:
    catalog = role_catalog()
    for role in catalog["roles"]:
        if role["role_id"] == role_id:
            validate_role(role)
            return copy.deepcopy(role)
    raise EcologyError(f"unknown role {role_id}")


def clean_empty_seat(seat_id: str = "SCIENCE_TEST_01") -> dict[str, Any]:
    catalog = seat_catalog()
    for seat in catalog["seats"]:
        if seat["seat_id"] == seat_id:
            validate_seat(seat)
            return copy.deepcopy(seat)
    raise EcologyError(f"unknown seat {seat_id}")


def occupied_seat(*, seat: Mapping[str, Any], occupant_id: str, invocation_id: str) -> dict[str, Any]:
    out = copy.deepcopy(dict(seat))
    out["seat_state"] = "OCCUPIED_CANDIDATE"
    out["occupant_id"] = occupant_id
    out["invocation_id"] = invocation_id
    out["work_claim_ref"] = None
    validate_seat(out)
    return out


def clean_basis() -> dict[str, Any]:
    value = fixtures()["observation_basis"]
    validate_observation_basis(value)
    return copy.deepcopy(value)


def clean_binding() -> dict[str, Any]:
    value = fixtures()["engagement_binding"]
    validate_binding(value)
    return copy.deepcopy(value)


def clean_bundle() -> dict[str, Any]:
    role = clean_role("SCIENTIST")
    basis = clean_basis()
    binding = clean_binding()
    seat = occupied_seat(
        seat=clean_empty_seat(binding["seat_id"]),
        occupant_id=binding["occupant_id"],
        invocation_id=binding["invocation_id"],
    )
    validate_correspondence(role=role, seat=seat, binding=binding, basis=basis)
    return {"role":role, "seat":seat, "binding":binding, "basis":basis}


def fresh_basis(
    basis: Mapping[str, Any],
    *,
    seat_id: str,
    occupant_id: str,
    invocation_id: str,
    basis_id: str,
    observed_objects: list[dict[str, Any]] | None = None,
    explicit_missing_objects: list[dict[str, Any]] | None = None,
    source_refs: list[str] | None = None,
) -> dict[str, Any]:
    """Construct a current basis for a fresh observer coordinate.

    The predecessor basis is validated as lineage input only. Its epistemic
    payload is never copied. Current observation content must be supplied
    explicitly for the new invocation.
    """
    validate_observation_basis(basis)
    out = {
        "schema":"observation_basis_v0",
        "basis_id":basis_id,
        "observer_seat_id":seat_id,
        "observer_occupant_id":occupant_id,
        "observer_invocation_id":invocation_id,
        "basis_ref":f"fixture://PRIMARY_ECOLOGY_GRAMMAR_001/{basis_id}",
        "observed_objects":copy.deepcopy(observed_objects or []),
        "explicit_missing_objects":copy.deepcopy(explicit_missing_objects or []),
        "source_refs":copy.deepcopy(source_refs or []),
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    validate_observation_basis(out)
    return out


def rotate_invocation(
    binding: Mapping[str, Any],
    basis: Mapping[str, Any],
    new_invocation_id: str,
    *,
    observed_objects: list[dict[str, Any]] | None = None,
    explicit_missing_objects: list[dict[str, Any]] | None = None,
    source_refs: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_binding(binding)
    new_basis = fresh_basis(
        basis,
        seat_id=binding["seat_id"],
        occupant_id=binding["occupant_id"],
        invocation_id=new_invocation_id,
        basis_id=f"{basis['basis_id']}:FOR:{new_invocation_id}",
        observed_objects=observed_objects,
        explicit_missing_objects=explicit_missing_objects,
        source_refs=source_refs,
    )
    out = copy.deepcopy(dict(binding))
    out["binding_id"] = f"BINDING:{binding['seat_id']}:{binding['occupant_id']}:{new_invocation_id}"
    out["invocation_id"] = new_invocation_id
    out["observation_basis_ref"] = observation_basis_ref(new_basis)
    out["work_claim_ref"] = None
    out["standing_refs"] = []
    out["authority_refs"] = []
    validate_binding(out)
    return out, new_basis


def rotate_occupant(
    binding: Mapping[str, Any],
    basis: Mapping[str, Any],
    new_occupant_id: str,
    new_invocation_id: str,
    *,
    observed_objects: list[dict[str, Any]] | None = None,
    explicit_missing_objects: list[dict[str, Any]] | None = None,
    source_refs: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_binding(binding)
    new_basis = fresh_basis(
        basis,
        seat_id=binding["seat_id"],
        occupant_id=new_occupant_id,
        invocation_id=new_invocation_id,
        basis_id=f"{basis['basis_id']}:FOR:{new_occupant_id}:{new_invocation_id}",
        observed_objects=observed_objects,
        explicit_missing_objects=explicit_missing_objects,
        source_refs=source_refs,
    )
    out = copy.deepcopy(dict(binding))
    out["binding_id"] = f"BINDING:{binding['seat_id']}:{new_occupant_id}:{new_invocation_id}"
    out["occupant_id"] = new_occupant_id
    out["invocation_id"] = new_invocation_id
    out["observation_basis_ref"] = observation_basis_ref(new_basis)
    out["work_claim_ref"] = None
    out["standing_refs"] = []
    out["authority_refs"] = []
    validate_binding(out)
    return out, new_basis

def authority_standing(binding: Mapping[str, Any]) -> str:
    validate_binding(binding)
    return "UNADJUDICATED" if binding["authority_refs"] else "ABSENT"


def _correspondence_cell(
    *,
    role: Mapping[str, Any],
    seat: Mapping[str, Any],
    binding: Mapping[str, Any],
    basis: Mapping[str, Any],
    expected_error: str,
) -> str:
    try:
        validate_correspondence(role=role, seat=seat, binding=binding, basis=basis)
    except EcologyError as exc:
        return "PASS" if str(exc) == expected_error else "FRACTURE"
    return "FRACTURE"


def run_pressure() -> dict[str, Any]:
    role = clean_role()
    empty = clean_empty_seat()
    bundle = clean_bundle()
    basis = bundle["basis"]
    binding = bundle["binding"]

    cells: dict[str, Any] = {}

    validate_seat(empty)
    cells["A"] = {"result":"PASS","relation":"SEAT_EXISTS_WITHOUT_OCCUPANT"}

    second = clean_empty_seat("SCIENCE_TEST_02")
    cells["B"] = {
        "result":"PASS" if empty["role_id"] == second["role_id"] and empty["seat_id"] != second["seat_id"] else "FRACTURE",
        "relation":"ROLE_IDENTITY_DISTINCT_FROM_SEAT_IDENTITY",
    }

    old = copy.deepcopy(binding)
    old["standing_refs"] = ["standing://OLD_INVOCATION"]
    old["authority_refs"] = ["authority://OLD_INVOCATION"]
    old["work_claim_ref"] = "claim://OLD_INVOCATION"
    validate_binding(old)
    rotated, rotated_basis = rotate_occupant(old, basis, "OCCUPANT_B", "INVOCATION_B")
    rotated_seat = occupied_seat(
        seat=clean_empty_seat(rotated["seat_id"]),
        occupant_id=rotated["occupant_id"],
        invocation_id=rotated["invocation_id"],
    )
    validate_correspondence(role=role, seat=rotated_seat, binding=rotated, basis=rotated_basis)
    cells["C"] = {
        "result":"PASS" if rotated["seat_id"] == old["seat_id"] and rotated["occupant_id"] != old["occupant_id"] and not rotated["standing_refs"] and not rotated["authority_refs"] and rotated["work_claim_ref"] is None else "FRACTURE",
        "relation":"OCCUPANT_ROTATION_WITHOUT_SEAT_OR_STANDING_INHERITANCE",
    }

    same_occ, same_occ_basis = rotate_invocation(old, basis, "INVOCATION_C")
    same_occ_seat = occupied_seat(
        seat=clean_empty_seat(same_occ["seat_id"]),
        occupant_id=same_occ["occupant_id"],
        invocation_id=same_occ["invocation_id"],
    )
    validate_correspondence(role=role, seat=same_occ_seat, binding=same_occ, basis=same_occ_basis)
    cells["D"] = {
        "result":"PASS" if same_occ["occupant_id"] == old["occupant_id"] and same_occ["invocation_id"] != old["invocation_id"] and not same_occ["standing_refs"] and not same_occ["authority_refs"] and same_occ["work_claim_ref"] is None else "FRACTURE",
        "relation":"OCCUPANT_IDENTITY_DISTINCT_FROM_INVOCATION_IDENTITY",
    }

    cells["E"] = {
        "result":"PASS" if binding["work_claim_ref"] is None else "FRACTURE",
        "relation":"INVOCATION_DISTINCT_FROM_WORK_CLAIM",
    }

    with_claim = copy.deepcopy(binding)
    with_claim["work_claim_ref"] = "claim://CANDIDATE"
    validate_binding(with_claim)
    cells["F"] = {
        "result":"PASS" if authority_standing(with_claim) == "ABSENT" else "FRACTURE",
        "relation":"WORK_CLAIM_DISTINCT_FROM_AUTHORITY",
    }

    bad_role = copy.deepcopy(role)
    bad_role["authority_effect"] = "GRANT"
    try:
        validate_role(bad_role)
        g = "FRACTURE"
    except EcologyError as exc:
        g = "PASS" if str(exc) == "ROLE_AUTHORITY_EFFECT_NOT_NONE" else "FRACTURE"
    cells["G"] = {"result":g,"relation":"ROLE_DOES_NOT_MANUFACTURE_AUTHORITY"}

    cells["H"] = {
        "result":"PASS" if observation_status(basis, "WORLD_OBJECT_NOT_IN_BASIS") == "UNKNOWN" else "FRACTURE",
        "relation":"CURRENT_WORLD_DISTINCT_FROM_OBSERVATION_BASIS",
    }

    cells["I"] = {
        "result":"PASS" if observation_status(basis, "MISSING_OBJECT") == "MISSING" else "FRACTURE",
        "relation":"MISSING_DISTINCT_FROM_ABSENT",
    }

    before = observation_status(basis, "LATER_WORLD_OBJECT")
    later_world = {"objects":["LATER_WORLD_OBJECT"]}
    after = observation_status(basis, "LATER_WORLD_OBJECT")
    cells["J"] = {
        "result":"PASS" if before == "UNKNOWN" and after == "UNKNOWN" and "LATER_WORLD_OBJECT" in later_world["objects"] else "FRACTURE",
        "relation":"DECISION_TIME_BASIS_DISTINCT_FROM_LATER_WORLD",
    }

    bad_seat = copy.deepcopy(empty)
    bad_seat["seat_state"] = "OCCUPIED_CANDIDATE"
    bad_seat["occupant_id"] = "TBD"
    bad_seat["invocation_id"] = "INVOCATION_PLACEHOLDER_TEST"
    try:
        validate_seat(bad_seat)
        k = "FRACTURE"
    except EcologyError as exc:
        k = "PASS" if "placeholder identity forbidden" in str(exc) else "FRACTURE"
    cells["K"] = {"result":k,"relation":"ABSENT_DISTINCT_FROM_PLACEHOLDER_IDENTITY"}

    auth_role = copy.deepcopy(role)
    auth_role["role_id"] = "AUTHORIZER_TEST_ROLE"
    validate_role(auth_role)
    auth_ref_binding = copy.deepcopy(binding)
    auth_ref_binding["authority_refs"] = ["authority://UNQUALIFIED-REFERENCE"]
    validate_binding(auth_ref_binding)
    cells["L"] = {
        "result":"PASS" if auth_role["authority_effect"] == "NONE" and authority_standing(auth_ref_binding) == "UNADJUDICATED" else "FRACTURE",
        "relation":"ROLE_LABEL_AND_AUTHORITY_REF_DISTINCT_FROM_AUTHORITY_STANDING",
    }

    # M1 -- invocation/basis mismatch. Seat and binding agree on new invocation;
    # basis remains the exact old invocation basis.
    m1_seat = copy.deepcopy(bundle["seat"])
    m1_binding = copy.deepcopy(binding)
    m1_seat["invocation_id"] = "INVOCATION_B"
    m1_binding["invocation_id"] = "INVOCATION_B"
    cells["M1"] = {
        "result":_correspondence_cell(
            role=role, seat=m1_seat, binding=m1_binding, basis=basis,
            expected_error="BINDING_BASIS_INVOCATION_MISMATCH",
        ),
        "relation":"CURRENT_INVOCATION_MUST_CORRESPOND_TO_CURRENT_OBSERVATION_BASIS",
    }

    # M2 -- occupant/basis mismatch. Seat and binding agree on new occupant;
    # basis remains owned by the old occupant.
    m2_seat = copy.deepcopy(bundle["seat"])
    m2_binding = copy.deepcopy(binding)
    m2_seat["occupant_id"] = "OCCUPANT_B"
    m2_binding["occupant_id"] = "OCCUPANT_B"
    cells["M2"] = {
        "result":_correspondence_cell(
            role=role, seat=m2_seat, binding=m2_binding, basis=basis,
            expected_error="BINDING_BASIS_OCCUPANT_MISMATCH",
        ),
        "relation":"CURRENT_OCCUPANT_MUST_CORRESPOND_TO_CURRENT_OBSERVATION_BASIS",
    }

    # M3 -- seat/basis mismatch with same role and current occupant/invocation.
    m3_seat = occupied_seat(
        seat=clean_empty_seat("SCIENCE_TEST_02"),
        occupant_id=binding["occupant_id"],
        invocation_id=binding["invocation_id"],
    )
    m3_binding = copy.deepcopy(binding)
    m3_binding["seat_id"] = "SCIENCE_TEST_02"
    cells["M3"] = {
        "result":_correspondence_cell(
            role=role, seat=m3_seat, binding=m3_binding, basis=basis,
            expected_error="BINDING_BASIS_SEAT_MISMATCH",
        ),
        "relation":"CURRENT_SEAT_MUST_CORRESPOND_TO_CURRENT_OBSERVATION_BASIS",
    }

    # M4 -- binding role must correspond to seat/role object.
    m4_binding = copy.deepcopy(binding)
    m4_binding["role_id"] = "PLANNER"
    cells["M4"] = {
        "result":_correspondence_cell(
            role=role, seat=bundle["seat"], binding=m4_binding, basis=basis,
            expected_error="ROLE_SEAT_BINDING_MISMATCH",
        ),
        "relation":"BINDING_ROLE_MUST_CORRESPOND_TO_SEAT_ROLE",
    }

    # N0 -- mutual absence and exact same claim ref are both coherent.
    n0_null = clean_bundle()
    n0_same = clean_bundle()
    n0_same["seat"]["work_claim_ref"] = "claim://SAME-CURRENT-CLAIM"
    n0_same["binding"]["work_claim_ref"] = "claim://SAME-CURRENT-CLAIM"
    try:
        validate_correspondence(
            role=n0_null["role"], seat=n0_null["seat"],
            binding=n0_null["binding"], basis=n0_null["basis"],
        )
        validate_correspondence(
            role=n0_same["role"], seat=n0_same["seat"],
            binding=n0_same["binding"], basis=n0_same["basis"],
        )
        n0 = "PASS"
    except EcologyError:
        n0 = "FRACTURE"
    cells["N0"] = {
        "result":n0,
        "relation":"CURRENT_WORK_CLAIM_MUTUAL_ABSENCE_OR_EXACT_IDENTITY_IS_COHERENT",
    }

    # N1 -- both surfaces claim work, but disagree on exact current claim identity.
    n1 = clean_bundle()
    n1["seat"]["work_claim_ref"] = "claim://A"
    n1["binding"]["work_claim_ref"] = "claim://B"
    cells["N1"] = {
        "result":_correspondence_cell(
            role=n1["role"], seat=n1["seat"], binding=n1["binding"], basis=n1["basis"],
            expected_error="SEAT_BINDING_WORK_CLAIM_MISMATCH",
        ),
        "relation":"SEAT_AND_BINDING_MUST_AGREE_ON_CURRENT_WORK_CLAIM_IDENTITY",
    }

    # N2 -- seat says a current claim exists while binding says no claim.
    n2 = clean_bundle()
    n2["seat"]["work_claim_ref"] = "claim://A"
    cells["N2"] = {
        "result":_correspondence_cell(
            role=n2["role"], seat=n2["seat"], binding=n2["binding"], basis=n2["basis"],
            expected_error="SEAT_BINDING_WORK_CLAIM_MISMATCH",
        ),
        "relation":"SEAT_CLAIM_PRESENT_BINDING_CLAIM_ABSENT_IS_INVALID",
    }

    # N3 -- binding says a current claim exists while seat says no claim.
    n3 = clean_bundle()
    n3["binding"]["work_claim_ref"] = "claim://A"
    cells["N3"] = {
        "result":_correspondence_cell(
            role=n3["role"], seat=n3["seat"], binding=n3["binding"], basis=n3["basis"],
            expected_error="SEAT_BINDING_WORK_CLAIM_MISMATCH",
        ),
        "relation":"SEAT_CLAIM_ABSENT_BINDING_CLAIM_PRESENT_IS_INVALID",
    }

    # P1 -- old observed content must not auto-propagate into a fresh invocation.
    p_old = clean_basis()
    p_old["observed_objects"] = [{
        "object_id":"POISON_SENTINEL",
        "identity":"sha256:" + ("b" * 64),
        "source_ref":"fixture://OLD_OBSERVATION/POISON_SENTINEL",
    }]
    p_old["explicit_missing_objects"] = []
    p_old["source_refs"] = ["fixture://OLD_OBSERVATION"]
    validate_observation_basis(p_old)
    p_binding = clean_binding()
    p_new_binding, p_new_basis = rotate_invocation(
        p_binding, p_old, "INVOCATION_P1"
    )
    cells["P1"] = {
        "result":"PASS" if observation_status(p_new_basis, "POISON_SENTINEL") == "UNKNOWN" and not p_new_basis["observed_objects"] else "FRACTURE",
        "relation":"OLD_OBSERVED_OBJECT_MUST_NOT_AUTO_PROPAGATE_TO_FRESH_INVOCATION",
    }

    # P2 -- prior missingness is also invocation-local and must not auto-propagate.
    p2_old = clean_basis()
    p2_old["observed_objects"] = []
    p2_old["explicit_missing_objects"] = [{
        "object_id":"MISSING_POISON_SENTINEL",
        "reason":"MISSING_FOR_PRIOR_INVOCATION",
    }]
    p2_old["source_refs"] = ["fixture://OLD_MISSINGNESS"]
    validate_observation_basis(p2_old)
    _, p2_new_basis = rotate_invocation(
        clean_binding(), p2_old, "INVOCATION_P2"
    )
    cells["P2"] = {
        "result":"PASS" if observation_status(p2_new_basis, "MISSING_POISON_SENTINEL") == "UNKNOWN" and not p2_new_basis["explicit_missing_objects"] else "FRACTURE",
        "relation":"OLD_MISSINGNESS_MUST_NOT_AUTO_PROPAGATE_TO_FRESH_INVOCATION",
    }

    # P3 -- the same fact may appear again only when supplied as fresh current
    # observation input for the new invocation.
    fresh_x = [{
        "object_id":"POISON_SENTINEL",
        "identity":"sha256:" + ("c" * 64),
        "source_ref":"fixture://FRESH_OBSERVATION/INVOCATION_P3/POISON_SENTINEL",
    }]
    p3_binding, p3_basis = rotate_invocation(
        clean_binding(),
        p_old,
        "INVOCATION_P3",
        observed_objects=fresh_x,
        explicit_missing_objects=[],
        source_refs=["fixture://FRESH_OBSERVATION/INVOCATION_P3"],
    )
    p3_seat = occupied_seat(
        seat=clean_empty_seat(p3_binding["seat_id"]),
        occupant_id=p3_binding["occupant_id"],
        invocation_id=p3_binding["invocation_id"],
    )
    validate_correspondence(
        role=role, seat=p3_seat, binding=p3_binding, basis=p3_basis
    )
    cells["P3"] = {
        "result":"PASS" if observation_status(p3_basis, "POISON_SENTINEL") == "OBSERVED" and p3_basis["source_refs"] == ["fixture://FRESH_OBSERVATION/INVOCATION_P3"] else "FRACTURE",
        "relation":"FRESH_OBSERVATION_MAY_REESTABLISH_SAME_FACT_EXPLICITLY",
    }

    # P4 -- prior basis remains recoverable as a separate exact historical
    # reference, but it is not the current invocation's observation basis.
    p4_current_binding, p4_current_basis = rotate_invocation(
        clean_binding(), p_old, "INVOCATION_P4"
    )
    historical_ref = observation_basis_ref(p_old)
    current_ref = observation_basis_ref(p4_current_basis)
    cells["P4"] = {
        "result":"PASS" if historical_ref != current_ref and p4_current_binding["observation_basis_ref"] == current_ref and observation_status(p4_current_basis, "POISON_SENTINEL") == "UNKNOWN" else "FRACTURE",
        "relation":"HISTORICAL_BASIS_REFERENCE_DISTINCT_FROM_CURRENT_OBSERVATION",
    }

    evaluation_key = _load(FIXTURE_DIR / "EVALUATION_KEY_v0.json")
    expected_cells = evaluation_key.get("cells", {}) if isinstance(evaluation_key, dict) else {}
    key_matches = all(expected_cells.get(cell_id) == cell["result"] for cell_id, cell in cells.items()) and set(expected_cells) == set(cells)
    passed = all(cell["result"] == "PASS" for cell in cells.values()) and key_matches
    terminal = "QUALIFIED_SYNTHETIC_GRAMMAR" if passed else "PRIMARY_ECOLOGY_GRAMMAR_FRACTURES"
    if isinstance(evaluation_key, dict) and evaluation_key.get("terminal_status") != terminal:
        terminal = "ADMINISTRATION_INVALID"

    return {
        "object_type":"PRIMARY_ECOLOGY_GRAMMAR_PRESSURE_RESULT",
        "object_id":"PRIMARY_ECOLOGY_GRAMMAR_001-RESULT",
        "status":terminal,
        "cells":cells,
        "core_relations":{
            "role_ne_seat":cells["B"]["result"],
            "seat_ne_occupant":cells["A"]["result"],
            "occupant_ne_invocation":cells["D"]["result"],
            "invocation_ne_work_claim":cells["E"]["result"],
            "work_claim_ne_authority":cells["F"]["result"],
            "current_world_ne_observation_basis":cells["H"]["result"],
            "cross_object_identity_correspondence":"PASS" if all(cells[x]["result"] == "PASS" for x in ("M1","M2","M3","M4","N0","N1","N2","N3")) else "FRACTURE",
            "seat_binding_work_claim_correspondence":"PASS" if all(cells[x]["result"] == "PASS" for x in ("N0","N1","N2","N3")) else "FRACTURE",
            "fresh_observation_payload_noninheritance":"PASS" if all(cells[x]["result"] == "PASS" for x in ("P1","P2","P3","P4")) else "FRACTURE",
        },
        "role_vocabulary_status":"PROVISIONAL_EXTENSIBLE",
        "durable_ecology_installed":False,
        "occupant_binding_effect":"NONE",
        "work_claim_effect":"NONE",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
        "integration_effect":"NONE",
        "representation_succession":"NOT_TESTED",
        "legacy_seat_migration":"NOT_TESTED",
        "historical_basis_reuse":"SEPARATE_TYPED_RELATION_REQUIRED_NOT_MODELED",
        "function_needs_seat":"NOT_TESTED",
        "stop":True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = run_pressure()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "QUALIFIED_SYNTHETIC_GRAMMAR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
