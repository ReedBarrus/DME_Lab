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
SOURCE_FIELDS = {
    "schema","source_id","object_id","identity","authority_effect","execution_effect",
}
MISSINGNESS_WITNESS_FIELDS = {
    "schema","witness_id","object_id","standing","reason",
    "authority_effect","execution_effect",
}
SOURCE_ENCOUNTER_FIELDS = {
    "schema","encounter_id","seat_id","occupant_id","invocation_id",
    "source_ref","encounter_kind","basis_ref","authority_effect","execution_effect",
}
MISSINGNESS_WITNESS_ENCOUNTER_FIELDS = {
    "schema","encounter_id","seat_id","occupant_id","invocation_id",
    "witness_ref","encounter_kind","basis_ref","authority_effect","execution_effect",
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
        if not isinstance(row, dict) or set(row) != {"object_id","reason","witness_ref"}:
            raise EcologyError("missing object fields must be exact")
        for field in ("object_id","reason","witness_ref"):
            _nonempty_string(row[field], f"missing.{field}")
        missing_ids.append(row["object_id"])
    if len(observed_ids) != len(set(observed_ids)) or len(missing_ids) != len(set(missing_ids)):
        raise EcologyError("duplicate object identity in observation basis")
    if set(observed_ids) & set(missing_ids):
        raise EcologyError("object cannot be both observed and explicitly missing")
    _string_list(basis["source_refs"], "source_refs")
    represented_sources = set(basis["source_refs"])
    for row in basis["observed_objects"]:
        if row["source_ref"] not in represented_sources:
            raise EcologyError("OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED")
    if basis["authority_effect"] != "NONE" or basis["execution_effect"] != "NONE":
        raise EcologyError("observation basis effects must remain NONE")


def observation_basis_ref(basis: Mapping[str, Any]) -> str:
    validate_observation_basis(basis)
    return f"observation-basis://{basis['basis_id']}@{object_identity(dict(basis))}"


def validate_observation_source(source: Mapping[str, Any]) -> None:
    if not isinstance(source, Mapping) or set(source) != SOURCE_FIELDS:
        raise EcologyError("observation source fields must be exact")
    if source["schema"] != "observation_source_v0":
        raise EcologyError("wrong observation source schema")
    for field in ("source_id","object_id","identity"):
        _nonempty_string(source[field], field)
    if source["authority_effect"] != "NONE" or source["execution_effect"] != "NONE":
        raise EcologyError("observation source effects must remain NONE")


def observation_source_ref(source: Mapping[str, Any]) -> str:
    validate_observation_source(source)
    return f"observation-source://{source['source_id']}@{object_identity(dict(source))}"


def validate_observation_grounding(
    basis: Mapping[str, Any],
    source_carriers: list[Mapping[str, Any]],
) -> None:
    validate_observation_basis(basis)
    if not isinstance(source_carriers, list):
        raise EcologyError("source_carriers must be a list")

    by_ref: dict[str, Mapping[str, Any]] = {}
    for source in source_carriers:
        validate_observation_source(source)
        ref = observation_source_ref(source)
        if ref in by_ref:
            raise EcologyError("duplicate exact observation source carrier")
        by_ref[ref] = source

    for row in basis["observed_objects"]:
        source = by_ref.get(row["source_ref"])
        if source is None:
            raise EcologyError("OBSERVED_OBJECT_SOURCE_CARRIER_NOT_SUPPLIED")
        if source["object_id"] != row["object_id"]:
            raise EcologyError("OBSERVED_OBJECT_SOURCE_OBJECT_MISMATCH")
        if source["identity"] != row["identity"]:
            raise EcologyError("OBSERVED_OBJECT_SOURCE_IDENTITY_MISMATCH")


def validate_missingness_witness(witness: Mapping[str, Any]) -> None:
    if not isinstance(witness, Mapping) or set(witness) != MISSINGNESS_WITNESS_FIELDS:
        raise EcologyError("missingness witness fields must be exact")
    if witness["schema"] != "missingness_witness_v0":
        raise EcologyError("wrong missingness witness schema")
    for field in ("witness_id","object_id","reason"):
        _nonempty_string(witness[field], field)
    if witness["standing"] != "UNAVAILABLE_AT_BASIS":
        raise EcologyError("MISSINGNESS_WITNESS_STANDING_INVALID")
    if witness["authority_effect"] != "NONE" or witness["execution_effect"] != "NONE":
        raise EcologyError("missingness witness effects must remain NONE")


def missingness_witness_ref(witness: Mapping[str, Any]) -> str:
    validate_missingness_witness(witness)
    return f"missingness-witness://{witness['witness_id']}@{object_identity(dict(witness))}"


def validate_missingness_grounding(
    basis: Mapping[str, Any],
    missingness_witnesses: list[Mapping[str, Any]],
) -> None:
    validate_observation_basis(basis)
    if not isinstance(missingness_witnesses, list):
        raise EcologyError("missingness_witnesses must be a list")

    by_ref: dict[str, Mapping[str, Any]] = {}
    for witness in missingness_witnesses:
        validate_missingness_witness(witness)
        ref = missingness_witness_ref(witness)
        if ref in by_ref:
            raise EcologyError("duplicate exact missingness witness")
        by_ref[ref] = witness

    for row in basis["explicit_missing_objects"]:
        witness = by_ref.get(row["witness_ref"])
        if witness is None:
            raise EcologyError("MISSINGNESS_WITNESS_NOT_SUPPLIED")
        if witness["object_id"] != row["object_id"]:
            raise EcologyError("MISSINGNESS_WITNESS_OBJECT_MISMATCH")
        if witness["reason"] != row["reason"]:
            raise EcologyError("MISSINGNESS_WITNESS_REASON_MISMATCH")


def validate_source_encounter(encounter: Mapping[str, Any]) -> None:
    if not isinstance(encounter, Mapping) or set(encounter) != SOURCE_ENCOUNTER_FIELDS:
        raise EcologyError("source encounter fields must be exact")
    if encounter["schema"] != "source_encounter_v0":
        raise EcologyError("wrong source encounter schema")
    for field in (
        "encounter_id","seat_id","occupant_id","invocation_id",
        "source_ref","basis_ref",
    ):
        _nonempty_string(encounter[field], field)
    if encounter["encounter_kind"] != "PRESENTED_TO_INVOCATION":
        raise EcologyError("SOURCE_ENCOUNTER_KIND_INVALID")
    if encounter["authority_effect"] != "NONE" or encounter["execution_effect"] != "NONE":
        raise EcologyError("source encounter effects must remain NONE")


def source_encounter_ref(encounter: Mapping[str, Any]) -> str:
    validate_source_encounter(encounter)
    return f"source-encounter://{encounter['encounter_id']}@{object_identity(dict(encounter))}"


def validate_source_encounter_grounding(
    *,
    basis: Mapping[str, Any],
    binding: Mapping[str, Any],
    source_encounters: list[Mapping[str, Any]],
) -> None:
    validate_observation_basis(basis)
    validate_binding(binding)
    if not isinstance(source_encounters, list):
        raise EcologyError("source_encounters must be a list")

    by_source: dict[str, Mapping[str, Any]] = {}
    exact_refs: set[str] = set()
    for encounter in source_encounters:
        validate_source_encounter(encounter)
        exact_ref = source_encounter_ref(encounter)
        if exact_ref in exact_refs:
            raise EcologyError("duplicate exact source encounter")
        exact_refs.add(exact_ref)
        source_ref = encounter["source_ref"]
        if source_ref in by_source:
            raise EcologyError("duplicate source encounter for source_ref")
        by_source[source_ref] = encounter

    for row in basis["observed_objects"]:
        if not source_encounters:
            raise EcologyError("CURRENT_SOURCE_ENCOUNTER_NOT_SUPPLIED")
        encounter = by_source.get(row["source_ref"])
        if encounter is None:
            raise EcologyError("SOURCE_ENCOUNTER_SOURCE_MISMATCH")
        if encounter["seat_id"] != binding["seat_id"]:
            raise EcologyError("SOURCE_ENCOUNTER_SEAT_MISMATCH")
        if encounter["occupant_id"] != binding["occupant_id"]:
            raise EcologyError("SOURCE_ENCOUNTER_OCCUPANT_MISMATCH")
        if encounter["invocation_id"] != binding["invocation_id"]:
            raise EcologyError("SOURCE_ENCOUNTER_INVOCATION_MISMATCH")
        if encounter["basis_ref"] != basis["basis_ref"]:
            raise EcologyError("SOURCE_ENCOUNTER_BASIS_MISMATCH")


def validate_missingness_witness_encounter(encounter: Mapping[str, Any]) -> None:
    if (
        not isinstance(encounter, Mapping)
        or set(encounter) != MISSINGNESS_WITNESS_ENCOUNTER_FIELDS
    ):
        raise EcologyError("missingness witness encounter fields must be exact")
    if encounter["schema"] != "missingness_witness_encounter_v0":
        raise EcologyError("wrong missingness witness encounter schema")
    for field in (
        "encounter_id","seat_id","occupant_id","invocation_id",
        "witness_ref","basis_ref",
    ):
        _nonempty_string(encounter[field], field)
    if encounter["encounter_kind"] != "PRESENTED_TO_INVOCATION":
        raise EcologyError("MISSINGNESS_WITNESS_ENCOUNTER_KIND_INVALID")
    if encounter["authority_effect"] != "NONE" or encounter["execution_effect"] != "NONE":
        raise EcologyError("missingness witness encounter effects must remain NONE")


def missingness_witness_encounter_ref(encounter: Mapping[str, Any]) -> str:
    validate_missingness_witness_encounter(encounter)
    return (
        f"missingness-witness-encounter://{encounter['encounter_id']}"
        f"@{object_identity(dict(encounter))}"
    )


def validate_missingness_witness_encounter_grounding(
    *,
    basis: Mapping[str, Any],
    binding: Mapping[str, Any],
    missingness_witness_encounters: list[Mapping[str, Any]],
) -> None:
    validate_observation_basis(basis)
    validate_binding(binding)
    if not isinstance(missingness_witness_encounters, list):
        raise EcologyError("missingness_witness_encounters must be a list")

    by_witness: dict[str, Mapping[str, Any]] = {}
    exact_refs: set[str] = set()
    for encounter in missingness_witness_encounters:
        validate_missingness_witness_encounter(encounter)
        exact_ref = missingness_witness_encounter_ref(encounter)
        if exact_ref in exact_refs:
            raise EcologyError("duplicate exact missingness witness encounter")
        exact_refs.add(exact_ref)
        witness_ref = encounter["witness_ref"]
        if witness_ref in by_witness:
            raise EcologyError("duplicate missingness witness encounter for witness_ref")
        by_witness[witness_ref] = encounter

    for row in basis["explicit_missing_objects"]:
        if not missingness_witness_encounters:
            raise EcologyError("CURRENT_MISSINGNESS_WITNESS_ENCOUNTER_NOT_SUPPLIED")
        encounter = by_witness.get(row["witness_ref"])
        if encounter is None:
            raise EcologyError("MISSINGNESS_WITNESS_ENCOUNTER_WITNESS_MISMATCH")
        if encounter["seat_id"] != binding["seat_id"]:
            raise EcologyError("MISSINGNESS_WITNESS_ENCOUNTER_SEAT_MISMATCH")
        if encounter["occupant_id"] != binding["occupant_id"]:
            raise EcologyError("MISSINGNESS_WITNESS_ENCOUNTER_OCCUPANT_MISMATCH")
        if encounter["invocation_id"] != binding["invocation_id"]:
            raise EcologyError("MISSINGNESS_WITNESS_ENCOUNTER_INVOCATION_MISMATCH")
        if encounter["basis_ref"] != basis["basis_ref"]:
            raise EcologyError("MISSINGNESS_WITNESS_ENCOUNTER_BASIS_MISMATCH")


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
    source_carriers: list[Mapping[str, Any]] | None = None,
    missingness_witnesses: list[Mapping[str, Any]] | None = None,
    source_encounters: list[Mapping[str, Any]] | None = None,
    missingness_witness_encounters: list[Mapping[str, Any]] | None = None,
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
    validate_observation_grounding(basis, source_carriers or [])
    validate_missingness_grounding(basis, missingness_witnesses or [])
    validate_source_encounter_grounding(
        basis=basis,
        binding=binding,
        source_encounters=source_encounters or [],
    )
    validate_missingness_witness_encounter_grounding(
        basis=basis,
        binding=binding,
        missingness_witness_encounters=missingness_witness_encounters or [],
    )


def basis_claim_status(basis: Mapping[str, Any], object_id: str) -> str:
    """Return only what the basis bytes themselves represent.

    A row in observed_objects does not by itself establish observation or even
    current presentation to the invocation; those standings require the wider
    current correspondence/encounter membrane.
    """
    validate_observation_basis(basis)
    if any(row["object_id"] == object_id for row in basis["observed_objects"]):
        return "SOURCE_CLAIM_REPRESENTED"
    if any(row["object_id"] == object_id for row in basis["explicit_missing_objects"]):
        return "MISSINGNESS_CLAIM_REPRESENTED"
    return "UNKNOWN"


def current_epistemic_status(
    *,
    role: Mapping[str, Any],
    seat: Mapping[str, Any],
    binding: Mapping[str, Any],
    basis: Mapping[str, Any],
    object_id: str,
    source_carriers: list[Mapping[str, Any]] | None = None,
    missingness_witnesses: list[Mapping[str, Any]] | None = None,
    source_encounters: list[Mapping[str, Any]] | None = None,
    missingness_witness_encounters: list[Mapping[str, Any]] | None = None,
) -> str:
    """Return only the standing earned by the fully validated current bundle."""
    validate_correspondence(
        role=role,
        seat=seat,
        binding=binding,
        basis=basis,
        source_carriers=source_carriers,
        missingness_witnesses=missingness_witnesses,
        source_encounters=source_encounters,
        missingness_witness_encounters=missingness_witness_encounters,
    )
    raw = basis_claim_status(basis, object_id)
    if raw == "SOURCE_CLAIM_REPRESENTED":
        return "SOURCE_PRESENTED"
    if raw == "MISSINGNESS_CLAIM_REPRESENTED":
        return "MISSINGNESS_WITNESS_PRESENTED"
    return raw


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


def clean_sources() -> list[dict[str, Any]]:
    value = fixtures()["source_carriers"]
    if not isinstance(value, list):
        raise EcologyError("source_carriers fixture must be a list")
    out = copy.deepcopy(value)
    for source in out:
        validate_observation_source(source)
    return out


def clean_missingness_witnesses() -> list[dict[str, Any]]:
    value = fixtures()["missingness_witnesses"]
    if not isinstance(value, list):
        raise EcologyError("missingness_witnesses fixture must be a list")
    out = copy.deepcopy(value)
    for witness in out:
        validate_missingness_witness(witness)
    return out


def clean_source_encounters() -> list[dict[str, Any]]:
    value = fixtures()["source_encounters"]
    if not isinstance(value, list):
        raise EcologyError("source_encounters fixture must be a list")
    out = copy.deepcopy(value)
    for encounter in out:
        validate_source_encounter(encounter)
    return out


def clean_missingness_witness_encounters() -> list[dict[str, Any]]:
    value = fixtures()["missingness_witness_encounters"]
    if not isinstance(value, list):
        raise EcologyError("missingness_witness_encounters fixture must be a list")
    out = copy.deepcopy(value)
    for encounter in out:
        validate_missingness_witness_encounter(encounter)
    return out


def clean_bundle() -> dict[str, Any]:
    role = clean_role("SCIENTIST")
    basis = clean_basis()
    binding = clean_binding()
    sources = clean_sources()
    missingness_witnesses = clean_missingness_witnesses()
    source_encounters = clean_source_encounters()
    missingness_witness_encounters = clean_missingness_witness_encounters()
    seat = occupied_seat(
        seat=clean_empty_seat(binding["seat_id"]),
        occupant_id=binding["occupant_id"],
        invocation_id=binding["invocation_id"],
    )
    validate_correspondence(
        role=role, seat=seat, binding=binding, basis=basis,
        source_carriers=sources,
        missingness_witnesses=missingness_witnesses,
        source_encounters=source_encounters,
        missingness_witness_encounters=missingness_witness_encounters,
    )
    return {
        "role":role, "seat":seat, "binding":binding, "basis":basis,
        "sources":sources, "missingness_witnesses":missingness_witnesses,
        "source_encounters":source_encounters,
        "missingness_witness_encounters":missingness_witness_encounters,
    }


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
    source_carriers: list[Mapping[str, Any]] | None = None,
    missingness_witnesses: list[Mapping[str, Any]] | None = None,
    source_encounters: list[Mapping[str, Any]] | None = None,
    missingness_witness_encounters: list[Mapping[str, Any]] | None = None,
) -> str:
    try:
        validate_correspondence(
            role=role, seat=seat, binding=binding, basis=basis,
            source_carriers=source_carriers,
            missingness_witnesses=missingness_witnesses,
            source_encounters=source_encounters,
            missingness_witness_encounters=missingness_witness_encounters,
        )
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
        "result":"PASS" if basis_claim_status(basis, "WORLD_OBJECT_NOT_IN_BASIS") == "UNKNOWN" else "FRACTURE",
        "relation":"CURRENT_WORLD_DISTINCT_FROM_OBSERVATION_BASIS",
    }

    cells["I"] = {
        "result":"PASS" if basis_claim_status(basis, "MISSING_OBJECT") == "MISSINGNESS_CLAIM_REPRESENTED" else "FRACTURE",
        "relation":"MISSINGNESS_CLAIM_REPRESENTED_DISTINCT_FROM_ABSENT",
    }

    before = basis_claim_status(basis, "LATER_WORLD_OBJECT")
    later_world = {"objects":["LATER_WORLD_OBJECT"]}
    after = basis_claim_status(basis, "LATER_WORLD_OBJECT")
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
            source_carriers=n0_null["sources"],
            missingness_witnesses=n0_null["missingness_witnesses"],
            source_encounters=n0_null["source_encounters"],
            missingness_witness_encounters=n0_null["missingness_witness_encounters"],
        )
        validate_correspondence(
            role=n0_same["role"], seat=n0_same["seat"],
            binding=n0_same["binding"], basis=n0_same["basis"],
            source_carriers=n0_same["sources"],
            missingness_witnesses=n0_same["missingness_witnesses"],
            source_encounters=n0_same["source_encounters"],
            missingness_witness_encounters=n0_same["missingness_witness_encounters"],
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
    p_old["source_refs"] = [
        "fixture://OLD_OBSERVATION/POISON_SENTINEL"
    ]
    validate_observation_basis(p_old)
    p_binding = clean_binding()
    p_new_binding, p_new_basis = rotate_invocation(
        p_binding, p_old, "INVOCATION_P1"
    )
    cells["P1"] = {
        "result":"PASS" if basis_claim_status(p_new_basis, "POISON_SENTINEL") == "UNKNOWN" and not p_new_basis["observed_objects"] else "FRACTURE",
        "relation":"OLD_OBSERVED_OBJECT_MUST_NOT_AUTO_PROPAGATE_TO_FRESH_INVOCATION",
    }

    # P2 -- prior missingness is also invocation-local and must not auto-propagate.
    p2_old = clean_basis()
    p2_old["observed_objects"] = []
    p2_old["explicit_missing_objects"] = [{
        "object_id":"MISSING_POISON_SENTINEL",
        "reason":"MISSING_FOR_PRIOR_INVOCATION",
        "witness_ref":"missingness-witness://PRIOR-P2@opaque:prior",
    }]
    p2_old["source_refs"] = ["fixture://OLD_MISSINGNESS"]
    validate_observation_basis(p2_old)
    _, p2_new_basis = rotate_invocation(
        clean_binding(), p2_old, "INVOCATION_P2"
    )
    cells["P2"] = {
        "result":"PASS" if basis_claim_status(p2_new_basis, "MISSING_POISON_SENTINEL") == "UNKNOWN" and not p2_new_basis["explicit_missing_objects"] else "FRACTURE",
        "relation":"OLD_MISSINGNESS_MUST_NOT_AUTO_PROPAGATE_TO_FRESH_INVOCATION",
    }

    # P3 -- the same fact may appear again only when supplied as fresh current
    # observation input for the new invocation.
    p3_source = {
        "schema":"observation_source_v0",
        "source_id":"SOURCE_INVOCATION_P3_POISON_SENTINEL",
        "object_id":"POISON_SENTINEL",
        "identity":"sha256:" + ("c" * 64),
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    p3_source_ref = observation_source_ref(p3_source)
    fresh_x = [{
        "object_id":"POISON_SENTINEL",
        "identity":"sha256:" + ("c" * 64),
        "source_ref":p3_source_ref,
    }]
    p3_binding, p3_basis = rotate_invocation(
        clean_binding(),
        p_old,
        "INVOCATION_P3",
        observed_objects=fresh_x,
        explicit_missing_objects=[],
        source_refs=[p3_source_ref],
    )
    p3_seat = occupied_seat(
        seat=clean_empty_seat(p3_binding["seat_id"]),
        occupant_id=p3_binding["occupant_id"],
        invocation_id=p3_binding["invocation_id"],
    )
    p3_encounter = {
        "schema":"source_encounter_v0",
        "encounter_id":"ENCOUNTER_INVOCATION_P3_POISON_SENTINEL",
        "seat_id":p3_binding["seat_id"],
        "occupant_id":p3_binding["occupant_id"],
        "invocation_id":p3_binding["invocation_id"],
        "source_ref":p3_source_ref,
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":p3_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    validate_correspondence(
        role=role, seat=p3_seat, binding=p3_binding, basis=p3_basis,
        source_carriers=[p3_source],
        source_encounters=[p3_encounter],
    )
    cells["P3"] = {
        "result":"PASS" if basis_claim_status(p3_basis, "POISON_SENTINEL") == "SOURCE_CLAIM_REPRESENTED" and p3_basis["source_refs"] == [p3_source_ref] else "FRACTURE",
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
        "result":"PASS" if historical_ref != current_ref and p4_current_binding["observation_basis_ref"] == current_ref and basis_claim_status(p4_current_basis, "POISON_SENTINEL") == "UNKNOWN" else "FRACTURE",
        "relation":"HISTORICAL_BASIS_REFERENCE_DISTINCT_FROM_CURRENT_OBSERVATION",
    }

    # Q1 -- an observed-object claim with no represented source relation is invalid.
    q1 = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q1",
        basis_id="OBSERVATION_BASIS_Q1",
    )
    q1["observed_objects"] = [{
        "object_id":"MAGIC_OBJECT",
        "identity":"sha256:" + ("d" * 64),
        "source_ref":"source://TOTALLY-REAL-BRO",
    }]
    try:
        validate_observation_basis(q1)
        q1_result = "FRACTURE"
    except EcologyError as exc:
        q1_result = "PASS" if str(exc) == "OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED" else "FRACTURE"
    cells["Q1"] = {
        "result":q1_result,
        "relation":"OBSERVED_OBJECT_REQUIRES_REPRESENTED_SOURCE_RELATION",
    }

    # Q2 -- naming a different source in the basis does not ground the claim.
    q2 = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q2",
        basis_id="OBSERVATION_BASIS_Q2",
        source_refs=["source://B"],
    )
    q2["observed_objects"] = [{
        "object_id":"MAGIC_OBJECT",
        "identity":"sha256:" + ("e" * 64),
        "source_ref":"source://A",
    }]
    try:
        validate_observation_basis(q2)
        q2_result = "FRACTURE"
    except EcologyError as exc:
        q2_result = "PASS" if str(exc) == "OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED" else "FRACTURE"
    cells["Q2"] = {
        "result":q2_result,
        "relation":"OBSERVED_OBJECT_SOURCE_MUST_MATCH_EXPLICIT_BASIS_SOURCE_REF",
    }

    # Q3A -- exact represented source carrier says one object, observation says another.
    q3a_source = {
        "schema":"observation_source_v0",
        "source_id":"SOURCE_GARY_BATHMAT",
        "object_id":"GARY_FROM_ACCOUNTING",
        "identity":"opaque:GARY-BATHMAT-v1",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    q3a_ref = observation_source_ref(q3a_source)
    q3a_basis = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q3A",
        basis_id="OBSERVATION_BASIS_Q3A",
        observed_objects=[{
            "object_id":"BIGFOOT",
            "identity":"opaque:GARY-BATHMAT-v1",
            "source_ref":q3a_ref,
        }],
        source_refs=[q3a_ref],
    )
    try:
        validate_observation_grounding(q3a_basis, [q3a_source])
        q3a_result = "FRACTURE"
    except EcologyError as exc:
        q3a_result = "PASS" if str(exc) == "OBSERVED_OBJECT_SOURCE_OBJECT_MISMATCH" else "FRACTURE"
    cells["Q3A"] = {
        "result":q3a_result,
        "relation":"SOURCE_OBJECT_ID_MUST_CORRESPOND_TO_OBSERVATION_OBJECT_ID",
    }

    # Q3B -- object agrees, but exact represented source identity differs.
    q3b_source = {
        "schema":"observation_source_v0",
        "source_id":"SOURCE_BIGFOOT_B",
        "object_id":"BIGFOOT",
        "identity":"opaque:IDENTITY-B",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    q3b_ref = observation_source_ref(q3b_source)
    q3b_basis = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q3B",
        basis_id="OBSERVATION_BASIS_Q3B",
        observed_objects=[{
            "object_id":"BIGFOOT",
            "identity":"opaque:IDENTITY-A",
            "source_ref":q3b_ref,
        }],
        source_refs=[q3b_ref],
    )
    try:
        validate_observation_grounding(q3b_basis, [q3b_source])
        q3b_result = "FRACTURE"
    except EcologyError as exc:
        q3b_result = "PASS" if str(exc) == "OBSERVED_OBJECT_SOURCE_IDENTITY_MISMATCH" else "FRACTURE"
    cells["Q3B"] = {
        "result":q3b_result,
        "relation":"SOURCE_IDENTITY_MUST_CORRESPOND_TO_OBSERVATION_IDENTITY",
    }

    # Q3C -- exact represented carrier agrees on source, object, and identity.
    q3c_source = {
        "schema":"observation_source_v0",
        "source_id":"SOURCE_BIGFOOT_C",
        "object_id":"BIGFOOT",
        "identity":"opaque:IDENTITY-A",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    q3c_ref = observation_source_ref(q3c_source)
    q3c_basis = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q3C",
        basis_id="OBSERVATION_BASIS_Q3C",
        observed_objects=[{
            "object_id":"BIGFOOT",
            "identity":"opaque:IDENTITY-A",
            "source_ref":q3c_ref,
        }],
        source_refs=[q3c_ref],
    )
    try:
        validate_observation_grounding(q3c_basis, [q3c_source])
        q3c_result = "PASS"
    except EcologyError:
        q3c_result = "FRACTURE"
    cells["Q3C"] = {
        "result":q3c_result,
        "relation":"EXACT_REPRESENTED_SOURCE_OBJECT_IDENTITY_CORRESPONDENCE_IS_ADMISSIBLE",
    }

    # Q4A -- missingness with a witness ref but no represented witness carrier.
    q4a = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q4A",
        basis_id="OBSERVATION_BASIS_Q4A",
        explicit_missing_objects=[{
            "object_id":"SECRET_DRAGON_LEDGER",
            "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
            "witness_ref":"missingness-witness://UNSUPPLIED@opaque:missing",
        }],
    )
    try:
        validate_missingness_grounding(q4a, [])
        q4a_result = "FRACTURE"
    except EcologyError as exc:
        q4a_result = "PASS" if str(exc) == "MISSINGNESS_WITNESS_NOT_SUPPLIED" else "FRACTURE"
    cells["Q4A"] = {
        "result":q4a_result,
        "relation":"MISSINGNESS_REQUIRES_REPRESENTED_WITNESS",
    }

    # Q4B -- represented witness refers to a different object.
    q4b_witness = {
        "schema":"missingness_witness_v0",
        "witness_id":"WITNESS_Q4B",
        "object_id":"OTHER_OBJECT",
        "standing":"UNAVAILABLE_AT_BASIS",
        "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    q4b_ref = missingness_witness_ref(q4b_witness)
    q4b = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q4B",
        basis_id="OBSERVATION_BASIS_Q4B",
        explicit_missing_objects=[{
            "object_id":"SECRET_DRAGON_LEDGER",
            "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
            "witness_ref":q4b_ref,
        }],
    )
    try:
        validate_missingness_grounding(q4b, [q4b_witness])
        q4b_result = "FRACTURE"
    except EcologyError as exc:
        q4b_result = "PASS" if str(exc) == "MISSINGNESS_WITNESS_OBJECT_MISMATCH" else "FRACTURE"
    cells["Q4B"] = {
        "result":q4b_result,
        "relation":"MISSINGNESS_WITNESS_OBJECT_MUST_CORRESPOND",
    }

    # Q4C -- exact represented witness corresponds to object and reason.
    q4c_witness = {
        "schema":"missingness_witness_v0",
        "witness_id":"WITNESS_Q4C",
        "object_id":"SECRET_DRAGON_LEDGER",
        "standing":"UNAVAILABLE_AT_BASIS",
        "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    q4c_ref = missingness_witness_ref(q4c_witness)
    q4c = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q4C",
        basis_id="OBSERVATION_BASIS_Q4C",
        explicit_missing_objects=[{
            "object_id":"SECRET_DRAGON_LEDGER",
            "reason":"SOURCE_NOT_AVAILABLE_AT_BASIS",
            "witness_ref":q4c_ref,
        }],
    )
    try:
        validate_missingness_grounding(q4c, [q4c_witness])
        q4c_result = "PASS"
    except EcologyError:
        q4c_result = "FRACTURE"
    cells["Q4C"] = {
        "result":q4c_result,
        "relation":"EXACT_REPRESENTED_MISSINGNESS_CORRESPONDENCE_IS_ADMISSIBLE",
    }

    # Q4D -- witness and basis must not tell different missingness reasons.
    q4d_witness = {
        "schema":"missingness_witness_v0",
        "witness_id":"WITNESS_Q4D",
        "object_id":"SECRET_DRAGON_LEDGER",
        "standing":"UNAVAILABLE_AT_BASIS",
        "reason":"NETWORK_TIMEOUT",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    q4d_ref = missingness_witness_ref(q4d_witness)
    q4d = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_Q4D",
        basis_id="OBSERVATION_BASIS_Q4D",
        explicit_missing_objects=[{
            "object_id":"SECRET_DRAGON_LEDGER",
            "reason":"PERMISSION_DENIED",
            "witness_ref":q4d_ref,
        }],
    )
    try:
        validate_missingness_grounding(q4d, [q4d_witness])
        q4d_result = "FRACTURE"
    except EcologyError as exc:
        q4d_result = "PASS" if str(exc) == "MISSINGNESS_WITNESS_REASON_MISMATCH" else "FRACTURE"
    cells["Q4D"] = {
        "result":q4d_result,
        "relation":"MISSINGNESS_WITNESS_REASON_MUST_CORRESPOND",
    }

    # Q5 / R1 -- exact source exists and corresponds, but current invocation has
    # no represented encounter with it.
    r_source = {
        "schema":"observation_source_v0",
        "source_id":"SOURCE_BIGFOOT_R",
        "object_id":"BIGFOOT",
        "identity":"opaque:IDENTITY-R",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    r_source_ref = observation_source_ref(r_source)
    r_basis = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_R",
        basis_id="OBSERVATION_BASIS_R",
        observed_objects=[{
            "object_id":"BIGFOOT",
            "identity":"opaque:IDENTITY-R",
            "source_ref":r_source_ref,
        }],
        source_refs=[r_source_ref],
    )
    r_binding = clean_binding()
    r_binding["binding_id"] = "BINDING:SCIENCE_TEST_01:LABOIB_CANDIDATE:INVOCATION_R"
    r_binding["invocation_id"] = "INVOCATION_R"
    r_binding["observation_basis_ref"] = observation_basis_ref(r_basis)
    r_seat = occupied_seat(
        seat=clean_empty_seat("SCIENCE_TEST_01"),
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_R",
    )
    try:
        validate_correspondence(
            role=role, seat=r_seat, binding=r_binding, basis=r_basis,
            source_carriers=[r_source],
            source_encounters=[],
        )
        r1_result = "FRACTURE"
    except EcologyError as exc:
        r1_result = "PASS" if str(exc) == "CURRENT_SOURCE_ENCOUNTER_NOT_SUPPLIED" else "FRACTURE"
    cells["R1"] = {
        "result":r1_result,
        "relation":"CURRENT_OBSERVED_CLAIM_REQUIRES_REPRESENTED_SOURCE_ENCOUNTER",
    }

    # R2 -- encounter names the exact source but belongs to a different invocation.
    r2_encounter = {
        "schema":"source_encounter_v0",
        "encounter_id":"ENCOUNTER_R2",
        "seat_id":r_binding["seat_id"],
        "occupant_id":r_binding["occupant_id"],
        "invocation_id":"INVOCATION_OTHER",
        "source_ref":r_source_ref,
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":r_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    try:
        validate_source_encounter_grounding(
            basis=r_basis, binding=r_binding, source_encounters=[r2_encounter]
        )
        r2_result = "FRACTURE"
    except EcologyError as exc:
        r2_result = "PASS" if str(exc) == "SOURCE_ENCOUNTER_INVOCATION_MISMATCH" else "FRACTURE"
    cells["R2"] = {
        "result":r2_result,
        "relation":"SOURCE_ENCOUNTER_MUST_BELONG_TO_CURRENT_INVOCATION",
    }

    # R3 -- current invocation encounter points at a different exact source.
    r3_encounter = {
        "schema":"source_encounter_v0",
        "encounter_id":"ENCOUNTER_R3",
        "seat_id":r_binding["seat_id"],
        "occupant_id":r_binding["occupant_id"],
        "invocation_id":r_binding["invocation_id"],
        "source_ref":"observation-source://OTHER@opaque:other",
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":r_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    try:
        validate_source_encounter_grounding(
            basis=r_basis, binding=r_binding, source_encounters=[r3_encounter]
        )
        r3_result = "FRACTURE"
    except EcologyError as exc:
        r3_result = "PASS" if str(exc) == "SOURCE_ENCOUNTER_SOURCE_MISMATCH" else "FRACTURE"
    cells["R3"] = {
        "result":r3_result,
        "relation":"SOURCE_ENCOUNTER_MUST_POINT_TO_EXACT_OBSERVED_SOURCE",
    }

    # R4 -- exact current seat / occupant / invocation / source / basis encounter.
    r4_encounter = {
        "schema":"source_encounter_v0",
        "encounter_id":"ENCOUNTER_R4",
        "seat_id":r_binding["seat_id"],
        "occupant_id":r_binding["occupant_id"],
        "invocation_id":r_binding["invocation_id"],
        "source_ref":r_source_ref,
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":r_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    try:
        validate_correspondence(
            role=role, seat=r_seat, binding=r_binding, basis=r_basis,
            source_carriers=[r_source],
            source_encounters=[r4_encounter],
        )
        r4_result = "PASS"
    except EcologyError:
        r4_result = "FRACTURE"
    cells["R4"] = {
        "result":r4_result,
        "relation":"EXACT_CURRENT_SOURCE_ENCOUNTER_IS_ADMISSIBLE",
    }

    # R5-R7 pressure the remaining declared encounter coordinates.
    r5 = copy.deepcopy(r4_encounter)
    r5["seat_id"] = "SCIENCE_TEST_02"
    try:
        validate_source_encounter_grounding(
            basis=r_basis, binding=r_binding, source_encounters=[r5]
        )
        r5_result = "FRACTURE"
    except EcologyError as exc:
        r5_result = "PASS" if str(exc) == "SOURCE_ENCOUNTER_SEAT_MISMATCH" else "FRACTURE"
    cells["R5"] = {
        "result":r5_result,
        "relation":"SOURCE_ENCOUNTER_MUST_BELONG_TO_CURRENT_SEAT",
    }

    r6 = copy.deepcopy(r4_encounter)
    r6["occupant_id"] = "OCCUPANT_OTHER"
    try:
        validate_source_encounter_grounding(
            basis=r_basis, binding=r_binding, source_encounters=[r6]
        )
        r6_result = "FRACTURE"
    except EcologyError as exc:
        r6_result = "PASS" if str(exc) == "SOURCE_ENCOUNTER_OCCUPANT_MISMATCH" else "FRACTURE"
    cells["R6"] = {
        "result":r6_result,
        "relation":"SOURCE_ENCOUNTER_MUST_BELONG_TO_CURRENT_OCCUPANT",
    }

    r7 = copy.deepcopy(r4_encounter)
    r7["basis_ref"] = "fixture://OTHER_BASIS"
    try:
        validate_source_encounter_grounding(
            basis=r_basis, binding=r_binding, source_encounters=[r7]
        )
        r7_result = "FRACTURE"
    except EcologyError as exc:
        r7_result = "PASS" if str(exc) == "SOURCE_ENCOUNTER_BASIS_MISMATCH" else "FRACTURE"
    cells["R7"] = {
        "result":r7_result,
        "relation":"SOURCE_ENCOUNTER_MUST_BELONG_TO_CURRENT_BASIS_COORDINATE",
    }

    # Q6A -- exact missingness witness exists and corresponds, but no current
    # invocation encounter with that witness is represented.
    s_witness = {
        "schema":"missingness_witness_v0",
        "witness_id":"WITNESS_MOTHMAN_S",
        "object_id":"MOTHMAN_FILES",
        "standing":"UNAVAILABLE_AT_BASIS",
        "reason":"PERMISSION_DENIED",
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    s_witness_ref = missingness_witness_ref(s_witness)
    s_basis = fresh_basis(
        clean_basis(),
        seat_id="SCIENCE_TEST_01",
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_S",
        basis_id="OBSERVATION_BASIS_S",
        explicit_missing_objects=[{
            "object_id":"MOTHMAN_FILES",
            "reason":"PERMISSION_DENIED",
            "witness_ref":s_witness_ref,
        }],
    )
    s_binding = clean_binding()
    s_binding["binding_id"] = "BINDING:SCIENCE_TEST_01:LABOIB_CANDIDATE:INVOCATION_S"
    s_binding["invocation_id"] = "INVOCATION_S"
    s_binding["observation_basis_ref"] = observation_basis_ref(s_basis)
    s_seat = occupied_seat(
        seat=clean_empty_seat("SCIENCE_TEST_01"),
        occupant_id="LABOIB_CANDIDATE",
        invocation_id="INVOCATION_S",
    )
    try:
        validate_correspondence(
            role=role, seat=s_seat, binding=s_binding, basis=s_basis,
            missingness_witnesses=[s_witness],
            missingness_witness_encounters=[],
        )
        s1_result = "FRACTURE"
    except EcologyError as exc:
        s1_result = (
            "PASS"
            if str(exc) == "CURRENT_MISSINGNESS_WITNESS_ENCOUNTER_NOT_SUPPLIED"
            else "FRACTURE"
        )
    cells["S1"] = {
        "result":s1_result,
        "relation":"CURRENT_MISSING_CLAIM_REQUIRES_REPRESENTED_WITNESS_ENCOUNTER",
    }

    # S2 -- encounter belongs to a different invocation.
    s2_encounter = {
        "schema":"missingness_witness_encounter_v0",
        "encounter_id":"MISSINGNESS_ENCOUNTER_S2",
        "seat_id":s_binding["seat_id"],
        "occupant_id":s_binding["occupant_id"],
        "invocation_id":"INVOCATION_OTHER",
        "witness_ref":s_witness_ref,
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":s_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    try:
        validate_missingness_witness_encounter_grounding(
            basis=s_basis,
            binding=s_binding,
            missingness_witness_encounters=[s2_encounter],
        )
        s2_result = "FRACTURE"
    except EcologyError as exc:
        s2_result = (
            "PASS"
            if str(exc) == "MISSINGNESS_WITNESS_ENCOUNTER_INVOCATION_MISMATCH"
            else "FRACTURE"
        )
    cells["S2"] = {
        "result":s2_result,
        "relation":"MISSINGNESS_WITNESS_ENCOUNTER_MUST_BELONG_TO_CURRENT_INVOCATION",
    }

    # S3 -- encounter points to a different witness.
    s3_encounter = {
        "schema":"missingness_witness_encounter_v0",
        "encounter_id":"MISSINGNESS_ENCOUNTER_S3",
        "seat_id":s_binding["seat_id"],
        "occupant_id":s_binding["occupant_id"],
        "invocation_id":s_binding["invocation_id"],
        "witness_ref":"missingness-witness://OTHER@opaque:other",
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":s_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    try:
        validate_missingness_witness_encounter_grounding(
            basis=s_basis,
            binding=s_binding,
            missingness_witness_encounters=[s3_encounter],
        )
        s3_result = "FRACTURE"
    except EcologyError as exc:
        s3_result = (
            "PASS"
            if str(exc) == "MISSINGNESS_WITNESS_ENCOUNTER_WITNESS_MISMATCH"
            else "FRACTURE"
        )
    cells["S3"] = {
        "result":s3_result,
        "relation":"MISSINGNESS_WITNESS_ENCOUNTER_MUST_POINT_TO_EXACT_WITNESS",
    }

    # S4 -- exact current seat / occupant / invocation / witness / basis encounter.
    s4_encounter = {
        "schema":"missingness_witness_encounter_v0",
        "encounter_id":"MISSINGNESS_ENCOUNTER_S4",
        "seat_id":s_binding["seat_id"],
        "occupant_id":s_binding["occupant_id"],
        "invocation_id":s_binding["invocation_id"],
        "witness_ref":s_witness_ref,
        "encounter_kind":"PRESENTED_TO_INVOCATION",
        "basis_ref":s_basis["basis_ref"],
        "authority_effect":"NONE",
        "execution_effect":"NONE",
    }
    try:
        validate_correspondence(
            role=role, seat=s_seat, binding=s_binding, basis=s_basis,
            missingness_witnesses=[s_witness],
            missingness_witness_encounters=[s4_encounter],
        )
        s4_result = "PASS"
    except EcologyError:
        s4_result = "FRACTURE"
    cells["S4"] = {
        "result":s4_result,
        "relation":"EXACT_CURRENT_MISSINGNESS_WITNESS_ENCOUNTER_IS_ADMISSIBLE",
    }

    # S5-S7 pressure the remaining declared encounter coordinates.
    s5 = copy.deepcopy(s4_encounter)
    s5["seat_id"] = "SCIENCE_TEST_02"
    try:
        validate_missingness_witness_encounter_grounding(
            basis=s_basis, binding=s_binding, missingness_witness_encounters=[s5]
        )
        s5_result = "FRACTURE"
    except EcologyError as exc:
        s5_result = (
            "PASS"
            if str(exc) == "MISSINGNESS_WITNESS_ENCOUNTER_SEAT_MISMATCH"
            else "FRACTURE"
        )
    cells["S5"] = {
        "result":s5_result,
        "relation":"MISSINGNESS_WITNESS_ENCOUNTER_MUST_BELONG_TO_CURRENT_SEAT",
    }

    s6 = copy.deepcopy(s4_encounter)
    s6["occupant_id"] = "OCCUPANT_OTHER"
    try:
        validate_missingness_witness_encounter_grounding(
            basis=s_basis, binding=s_binding, missingness_witness_encounters=[s6]
        )
        s6_result = "FRACTURE"
    except EcologyError as exc:
        s6_result = (
            "PASS"
            if str(exc) == "MISSINGNESS_WITNESS_ENCOUNTER_OCCUPANT_MISMATCH"
            else "FRACTURE"
        )
    cells["S6"] = {
        "result":s6_result,
        "relation":"MISSINGNESS_WITNESS_ENCOUNTER_MUST_BELONG_TO_CURRENT_OCCUPANT",
    }

    s7 = copy.deepcopy(s4_encounter)
    s7["basis_ref"] = "fixture://OTHER_BASIS"
    try:
        validate_missingness_witness_encounter_grounding(
            basis=s_basis, binding=s_binding, missingness_witness_encounters=[s7]
        )
        s7_result = "FRACTURE"
    except EcologyError as exc:
        s7_result = (
            "PASS"
            if str(exc) == "MISSINGNESS_WITNESS_ENCOUNTER_BASIS_MISMATCH"
            else "FRACTURE"
        )
    cells["S7"] = {
        "result":s7_result,
        "relation":"MISSINGNESS_WITNESS_ENCOUNTER_MUST_BELONG_TO_CURRENT_BASIS_COORDINATE",
    }

    # Q7 / T1 -- a basis row alone earns only represented-source-claim standing.
    t_bundle = clean_bundle()
    t1_status = basis_claim_status(t_bundle["basis"], "OBSERVED_OBJECT")
    cells["T1"] = {
        "result":"PASS" if t1_status == "SOURCE_CLAIM_REPRESENTED" else "FRACTURE",
        "relation":"BASIS_ROW_DOES_NOT_MANUFACTURE_OBSERVED_STANDING",
    }

    # T2 -- after the exact current encounter membrane survives, the strongest
    # standing earned is SOURCE_PRESENTED, not OBSERVED.
    t2_status = "INVALID"
    try:
        t2_status = current_epistemic_status(
            role=t_bundle["role"],
            seat=t_bundle["seat"],
            binding=t_bundle["binding"],
            basis=t_bundle["basis"],
            object_id="OBSERVED_OBJECT",
            source_carriers=t_bundle["sources"],
            missingness_witnesses=t_bundle["missingness_witnesses"],
            source_encounters=t_bundle["source_encounters"],
            missingness_witness_encounters=t_bundle["missingness_witness_encounters"],
        )
        t2_result = "PASS" if t2_status == "SOURCE_PRESENTED" else "FRACTURE"
    except EcologyError:
        t2_result = "FRACTURE"
    cells["T2"] = {
        "result":t2_result,
        "relation":"PRESENTED_TO_INVOCATION_EARNS_SOURCE_PRESENTED_NOT_OBSERVED",
    }

    # T3 -- the current apparatus must not emit OBSERVED standing for either a
    # basis-only row or the fully validated presented-source chain.
    cells["T3"] = {
        "result":"PASS" if t1_status != "OBSERVED" and t2_status != "OBSERVED" else "FRACTURE",
        "relation":"OBSERVED_STANDING_REQUIRES_STRONGER_FUTURE_MACHINERY",
    }

    # Q8 / U1 -- a missingness row alone earns only represented-claim standing.
    u_bundle = clean_bundle()
    u1_status = basis_claim_status(u_bundle["basis"], "MISSING_OBJECT")
    cells["U1"] = {
        "result":"PASS" if u1_status == "MISSINGNESS_CLAIM_REPRESENTED" else "FRACTURE",
        "relation":"BASIS_MISSINGNESS_ROW_DOES_NOT_MANUFACTURE_MISSING_STANDING",
    }

    # U2 -- after exact witness correspondence and current witness encounter,
    # the strongest standing earned is MISSINGNESS_WITNESS_PRESENTED.
    u2_status = "INVALID"
    try:
        u2_status = current_epistemic_status(
            role=u_bundle["role"],
            seat=u_bundle["seat"],
            binding=u_bundle["binding"],
            basis=u_bundle["basis"],
            object_id="MISSING_OBJECT",
            source_carriers=u_bundle["sources"],
            missingness_witnesses=u_bundle["missingness_witnesses"],
            source_encounters=u_bundle["source_encounters"],
            missingness_witness_encounters=u_bundle["missingness_witness_encounters"],
        )
        u2_result = (
            "PASS"
            if u2_status == "MISSINGNESS_WITNESS_PRESENTED"
            else "FRACTURE"
        )
    except EcologyError:
        u2_result = "FRACTURE"
    cells["U2"] = {
        "result":u2_result,
        "relation":"PRESENTED_WITNESS_EARNS_MISSINGNESS_WITNESS_PRESENTED_NOT_MISSING",
    }

    # U3 -- current machinery must not emit bare MISSING standing.
    cells["U3"] = {
        "result":"PASS" if u1_status != "MISSING" and u2_status != "MISSING" else "FRACTURE",
        "relation":"MISSING_STANDING_REQUIRES_STRONGER_FUTURE_MACHINERY",
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
            "fresh_observation_source_relation":"PASS" if all(cells[x]["result"] == "PASS" for x in ("Q1","Q2")) else "FRACTURE",
            "observation_source_object_identity_correspondence":"PASS" if all(cells[x]["result"] == "PASS" for x in ("Q3A","Q3B","Q3C")) else "FRACTURE",
            "explicit_missingness_grounding":"PASS" if all(cells[x]["result"] == "PASS" for x in ("Q4A","Q4B","Q4C","Q4D")) else "FRACTURE",
            "current_invocation_source_encounter":"PASS" if all(cells[x]["result"] == "PASS" for x in ("R1","R2","R3","R4","R5","R6","R7")) else "FRACTURE",
            "current_invocation_missingness_witness_encounter":"PASS" if all(cells[x]["result"] == "PASS" for x in ("S1","S2","S3","S4","S5","S6","S7")) else "FRACTURE",
            "observed_status_semantic_ceiling":"PASS" if all(cells[x]["result"] == "PASS" for x in ("T1","T2","T3")) else "FRACTURE",
            "missing_status_semantic_ceiling":"PASS" if all(cells[x]["result"] == "PASS" for x in ("U1","U2","U3")) else "FRACTURE",
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
        "observation_source_identity_correspondence":"TESTED_EXACT_OPAQUE_CORRESPONDENCE",
        "observation_identity_scheme_semantics":"NOT_TESTED",
        "observation_source_truth":"NOT_TESTED",
        "missingness_witness_correspondence":"TESTED_EXACT_OBJECT_REASON",
        "missingness_witness_truth":"NOT_TESTED",
        "universal_unavailability":"NOT_CLAIMED",
        "source_encounter_correspondence":"TESTED_CURRENT_SEAT_OCCUPANT_INVOCATION_SOURCE_BASIS",
        "source_encounter_truth":"NOT_TESTED",
        "direct_object_perception":"NOT_CLAIMED",
        "source_understanding":"NOT_CLAIMED",
        "missingness_witness_encounter_correspondence":"TESTED_CURRENT_SEAT_OCCUPANT_INVOCATION_WITNESS_BASIS",
        "missingness_witness_encounter_truth":"NOT_TESTED",
        "missingness_reason_understanding":"NOT_CLAIMED",
        "presented_source_standing":"SOURCE_PRESENTED",
        "direct_observation_standing":"NOT_ESTABLISHED",
        "source_inspection_or_consumption":"NOT_ESTABLISHED",
        "presented_missingness_standing":"MISSINGNESS_WITNESS_PRESENTED",
        "missing_standing":"NOT_ESTABLISHED",
        "retrieval_attempt_or_failure":"NOT_ESTABLISHED",
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
