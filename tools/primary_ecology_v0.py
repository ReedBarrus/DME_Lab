#!/usr/bin/env python3
"""Bounded grammar pressure for PRIMARY_ECOLOGY_v0.

This apparatus qualifies only identity/observation separation. It creates no
live seats, occupants, invocations, work claims, authority, or execution.
"""
from __future__ import annotations

import argparse
import copy
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


def rotate_invocation(binding: Mapping[str, Any], new_invocation_id: str) -> dict[str, Any]:
    validate_binding(binding)
    out = copy.deepcopy(dict(binding))
    out["binding_id"] = f"BINDING:{binding['seat_id']}:{new_invocation_id}"
    out["invocation_id"] = new_invocation_id
    out["work_claim_ref"] = None
    out["standing_refs"] = []
    out["authority_refs"] = []
    validate_binding(out)
    return out


def rotate_occupant(binding: Mapping[str, Any], new_occupant_id: str, new_invocation_id: str) -> dict[str, Any]:
    out = rotate_invocation(binding, new_invocation_id)
    out["occupant_id"] = new_occupant_id
    out["binding_id"] = f"BINDING:{binding['seat_id']}:{new_occupant_id}:{new_invocation_id}"
    validate_binding(out)
    return out


def authority_standing(binding: Mapping[str, Any]) -> str:
    validate_binding(binding)
    # This grammar carries only references. It intentionally has no authority
    # adjudicator, so presence of a ref cannot become authority.
    return "UNADJUDICATED" if binding["authority_refs"] else "ABSENT"


def run_pressure() -> dict[str, Any]:
    role = clean_role()
    empty = clean_empty_seat()
    basis = clean_basis()
    binding = clean_binding()

    cells: dict[str, Any] = {}

    # A -- explicit empty seat.
    validate_seat(empty)
    cells["A"] = {"result":"PASS","relation":"SEAT_EXISTS_WITHOUT_OCCUPANT"}

    # B -- same role may have more than one seat; role identity does not collapse seat identity.
    second = clean_empty_seat("SCIENCE_TEST_02")
    cells["B"] = {
        "result":"PASS" if empty["role_id"] == second["role_id"] and empty["seat_id"] != second["seat_id"] else "FRACTURE",
        "relation":"ROLE_IDENTITY_DISTINCT_FROM_SEAT_IDENTITY",
    }

    # C -- occupant rotation retains seat identity and drops invocation-local refs.
    old = copy.deepcopy(binding)
    old["standing_refs"] = ["standing://OLD_INVOCATION"]
    old["authority_refs"] = ["authority://OLD_INVOCATION"]
    old["work_claim_ref"] = "claim://OLD_INVOCATION"
    validate_binding(old)
    rotated = rotate_occupant(old, "OCCUPANT_B", "INVOCATION_B")
    cells["C"] = {
        "result":"PASS" if rotated["seat_id"] == old["seat_id"] and rotated["occupant_id"] != old["occupant_id"] and not rotated["standing_refs"] and not rotated["authority_refs"] and rotated["work_claim_ref"] is None else "FRACTURE",
        "relation":"OCCUPANT_ROTATION_WITHOUT_SEAT_OR_STANDING_INHERITANCE",
    }

    # D -- invocation rotation can happen with the same occupant; standing/claim/authority do not inherit.
    same_occ = rotate_invocation(old, "INVOCATION_C")
    cells["D"] = {
        "result":"PASS" if same_occ["occupant_id"] == old["occupant_id"] and same_occ["invocation_id"] != old["invocation_id"] and not same_occ["standing_refs"] and not same_occ["authority_refs"] and same_occ["work_claim_ref"] is None else "FRACTURE",
        "relation":"OCCUPANT_IDENTITY_DISTINCT_FROM_INVOCATION_IDENTITY",
    }

    # E -- engagement may exist without a work claim.
    cells["E"] = {
        "result":"PASS" if binding["work_claim_ref"] is None else "FRACTURE",
        "relation":"INVOCATION_DISTINCT_FROM_WORK_CLAIM",
    }

    # F -- a work-claim ref never manufactures authority in this grammar.
    with_claim = copy.deepcopy(binding)
    with_claim["work_claim_ref"] = "claim://CANDIDATE"
    validate_binding(with_claim)
    cells["F"] = {
        "result":"PASS" if authority_standing(with_claim) == "ABSENT" else "FRACTURE",
        "relation":"WORK_CLAIM_DISTINCT_FROM_AUTHORITY",
    }

    # G -- role semantics cannot carry authority effect.
    bad_role = copy.deepcopy(role)
    bad_role["authority_effect"] = "GRANT"
    try:
        validate_role(bad_role)
        g = "FRACTURE"
    except EcologyError as exc:
        g = "PASS" if str(exc) == "ROLE_AUTHORITY_EFFECT_NOT_NONE" else "FRACTURE"
    cells["G"] = {"result":g,"relation":"ROLE_DOES_NOT_MANUFACTURE_AUTHORITY"}

    # H -- world existence not present in basis remains UNKNOWN, not OBSERVED or ABSENT.
    cells["H"] = {
        "result":"PASS" if observation_status(basis, "WORLD_OBJECT_NOT_IN_BASIS") == "UNKNOWN" else "FRACTURE",
        "relation":"CURRENT_WORLD_DISTINCT_FROM_OBSERVATION_BASIS",
    }

    # I -- explicit missingness is MISSING, not ABSENT.
    cells["I"] = {
        "result":"PASS" if observation_status(basis, "MISSING_OBJECT") == "MISSING" else "FRACTURE",
        "relation":"MISSING_DISTINCT_FROM_ABSENT",
    }

    # J -- basis remains basis-relative even if a later world snapshot includes the object.
    before = observation_status(basis, "LATER_WORLD_OBJECT")
    later_world = {"objects":["LATER_WORLD_OBJECT"]}
    after = observation_status(basis, "LATER_WORLD_OBJECT")
    cells["J"] = {
        "result":"PASS" if before == "UNKNOWN" and after == "UNKNOWN" and "LATER_WORLD_OBJECT" in later_world["objects"] else "FRACTURE",
        "relation":"DECISION_TIME_BASIS_DISTINCT_FROM_LATER_WORLD",
    }

    # K -- placeholder occupant is not a legitimate empty/occupied identity.
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

    # L -- authority-looking role label and authority refs remain non-authoritative.
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
