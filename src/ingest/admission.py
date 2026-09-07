"""Bounded v0 ingest admission records over the existing append ledger."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.ledger import JsonlLedger, SchemaValidationResult, validate_ledger_record


COMPARATOR_IDENTITY = "ingest_candidate_envelope_minimum"
COMPARATOR_V0 = "ingest_candidate_envelope_minimum_v0"
COMPARATOR_V0_EVENT_TIME_REQUIRED = "ingest_candidate_envelope_event_time_required_v0_pressure"
DECISIONS = ("admitted", "rejected", "unresolved")


def make_observation_envelope(
    observation: Any,
    *,
    source: str,
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "record_type": "observation",
        "source": source,
        "observation": observation,
        "provenance": deepcopy(provenance or {}),
    }


def append_observation(
    ledger: JsonlLedger,
    observation: Any,
    *,
    source: str,
    provenance: dict[str, Any] | None = None,
    record_id: str | None = None,
) -> dict[str, Any]:
    return ledger.append(make_observation_envelope(observation, source=source, provenance=provenance), record_id=record_id)


def compare_observation_record(
    subject_record: dict[str, Any],
    *,
    comparator_version: str = COMPARATOR_V0,
) -> dict[str, Any]:
    schema = comparator_schema(comparator_version)
    if schema is None:
        return {
            "status": "unavailable",
            "valid": None,
            "errors": [
                {
                    "path": "$.comparator_version",
                    "validator": "available_comparator",
                    "message": f"unsupported comparator version: {comparator_version}",
                }
            ],
        }

    validation = validate_ledger_record(subject_record, schema)
    return comparison_result(validation)


def make_admission_envelope(
    subject_record: dict[str, Any],
    *,
    comparator_identity: str = COMPARATOR_IDENTITY,
    comparator_version: str = COMPARATOR_V0,
) -> dict[str, Any]:
    comparison = compare_observation_record(subject_record, comparator_version=comparator_version)
    decision, basis = decide_admission(comparison)
    return {
        "record_type": "admission",
        "subject_record_id": subject_record["record_id"],
        "comparator_identity": comparator_identity,
        "comparator_version": comparator_version,
        "comparison_result": comparison,
        "decision": decision,
        "decision_basis": basis,
    }


def append_admission(
    ledger: JsonlLedger,
    subject_record: dict[str, Any],
    *,
    comparator_identity: str = COMPARATOR_IDENTITY,
    comparator_version: str = COMPARATOR_V0,
    record_id: str | None = None,
) -> dict[str, Any]:
    return ledger.append(
        make_admission_envelope(
            subject_record,
            comparator_identity=comparator_identity,
            comparator_version=comparator_version,
        ),
        record_id=record_id,
    )


def derive_admitted_projection(replayed_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations = {
        record["record_id"]: record
        for record in replayed_records
        if record.get("envelope", {}).get("record_type") == "observation"
    }
    admission_records = [
        record
        for record in replayed_records
        if record.get("envelope", {}).get("record_type") == "admission"
        and record["envelope"].get("decision") == "admitted"
    ]
    projected: list[dict[str, Any]] = []
    included: set[str] = set()
    for admission in admission_records:
        subject_id = admission["envelope"]["subject_record_id"]
        if subject_id in observations and subject_id not in included:
            projected.append(
                {
                    "subject_record_id": subject_id,
                    "observation_record_id": subject_id,
                    "admission_record_ids": [
                        record["record_id"]
                        for record in admission_records
                        if record["envelope"]["subject_record_id"] == subject_id
                    ],
                    "source": observations[subject_id]["envelope"].get("source"),
                }
            )
            included.add(subject_id)
    return projected


def reconstruct_admission_lineage(replayed_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projection_ids = {item["subject_record_id"] for item in derive_admitted_projection(replayed_records)}
    admissions_by_subject: dict[str, list[dict[str, Any]]] = {}
    for record in replayed_records:
        envelope = record.get("envelope", {})
        if envelope.get("record_type") == "admission":
            admissions_by_subject.setdefault(envelope["subject_record_id"], []).append(
                {
                    "admission_record_id": record["record_id"],
                    "comparator_identity": envelope["comparator_identity"],
                    "comparator_version": envelope["comparator_version"],
                    "comparison_result": envelope["comparison_result"],
                    "decision": envelope["decision"],
                    "decision_basis": envelope["decision_basis"],
                }
            )

    lineage = []
    for record in replayed_records:
        envelope = record.get("envelope", {})
        if envelope.get("record_type") != "observation":
            continue
        subject_id = record["record_id"]
        lineage.append(
            {
                "subject_record_id": subject_id,
                "observation": envelope["observation"],
                "observation_source": envelope["source"],
                "observation_provenance": envelope["provenance"],
                "admission_records": admissions_by_subject.get(subject_id, []),
                "participates_in_admitted_projection": subject_id in projection_ids,
            }
        )
    return lineage


def decide_admission(comparison: dict[str, Any]) -> tuple[str, str]:
    if comparison["status"] != "compared":
        return "unresolved", "comparison unavailable"
    if comparison["valid"] is True:
        return "admitted", "comparison valid under comparator"
    return "rejected", "comparison invalid under comparator"


def comparison_result(validation: SchemaValidationResult) -> dict[str, Any]:
    return {
        "status": "compared",
        "valid": validation.valid,
        "errors": [error.to_dict() for error in validation.errors],
    }


def comparator_schema(comparator_version: str) -> dict[str, Any] | None:
    if comparator_version == COMPARATOR_V0:
        return _record_schema(_observation_schema(required_observation_fields=["envelope_identity", "source", "signal"]))
    if comparator_version == COMPARATOR_V0_EVENT_TIME_REQUIRED:
        return _record_schema(
            _observation_schema(
                required_observation_fields=["envelope_identity", "source", "event_time", "signal"],
                observation_properties={"event_time": {"type": "string", "minLength": 1}},
            )
        )
    return None


def _record_schema(observation_schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "required": ["record_id", "commit_index", "envelope", "integrity"],
        "additionalProperties": True,
        "properties": {
            "envelope": {
                "type": "object",
                "required": ["record_type", "source", "observation", "provenance"],
                "additionalProperties": True,
                "properties": {
                    "record_type": {"const": "observation"},
                    "source": {"type": "string", "minLength": 1},
                    "observation": observation_schema,
                    "provenance": {"type": "object"},
                },
            }
        },
    }


def _observation_schema(
    *,
    required_observation_fields: list[str],
    observation_properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    properties = {
        "envelope_identity": {"type": "string", "minLength": 1},
        "source": {"type": "string", "minLength": 1},
        "signal": {
            "type": "object",
            "required": ["identity", "type", "payload"],
            "additionalProperties": True,
            "properties": {
                "identity": {"type": "string", "minLength": 1},
                "type": {"type": "string", "minLength": 1},
            },
        },
    }
    properties.update(observation_properties or {})
    return {
        "type": "object",
        "required": required_observation_fields,
        "additionalProperties": True,
        "properties": properties,
    }
