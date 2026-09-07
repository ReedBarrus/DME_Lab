"""Reconstruct bounded admission relationships from authoritative replay."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


RECONSTRUCTION_TYPE = "admission_relationships_v0"


def reconstruct_admission_relationships(replayed_records: list[dict[str, Any]]) -> dict[str, Any]:
    observations: dict[str, dict[str, Any]] = {}
    ordered_observation_ids: list[str] = []
    admissions_by_subject: dict[str, list[dict[str, Any]]] = {}
    orphan_admissions: list[dict[str, Any]] = []

    for record in replayed_records:
        envelope = record.get("envelope", {})
        if envelope.get("record_type") == "observation":
            record_id = record["record_id"]
            ordered_observation_ids.append(record_id)
            observations[record_id] = {
                "observation_record_id": record_id,
                "observation_commit_index": record["commit_index"],
                "source": envelope["source"],
                "provenance": deepcopy(envelope["provenance"]),
                "observation": deepcopy(envelope["observation"]),
            }

    for record in replayed_records:
        envelope = record.get("envelope", {})
        if envelope.get("record_type") != "admission":
            continue
        admission = {
            "admission_record_id": record["record_id"],
            "admission_commit_index": record["commit_index"],
            "subject_record_id": envelope["subject_record_id"],
            "comparator_identity": envelope["comparator_identity"],
            "comparator_version": envelope["comparator_version"],
            "comparison_result": deepcopy(envelope["comparison_result"]),
            "decision": envelope["decision"],
            "decision_basis": envelope["decision_basis"],
        }
        if admission["subject_record_id"] in observations:
            admissions_by_subject.setdefault(admission["subject_record_id"], []).append(admission)
        else:
            orphan_admissions.append(admission)

    admitted_subject_ids = {
        admission["subject_record_id"]
        for admissions in admissions_by_subject.values()
        for admission in admissions
        if admission["decision"] == "admitted"
    }

    reconstructed_observations = []
    for record_id in ordered_observation_ids:
        admission_records = admissions_by_subject.get(record_id, [])
        reconstructed_observations.append(
            {
                **observations[record_id],
                "admission_record_ids": [admission["admission_record_id"] for admission in admission_records],
                "admissions": admission_records,
                "participates_in_admitted_projection": record_id in admitted_subject_ids,
            }
        )

    return {
        "reconstruction_type": RECONSTRUCTION_TYPE,
        "authoritative_record_ids": [record["record_id"] for record in replayed_records],
        "observations": reconstructed_observations,
        "orphan_admissions": orphan_admissions,
    }


def derive_admitted_projection(reconstruction: dict[str, Any]) -> list[dict[str, Any]]:
    projection = []
    for observation in reconstruction["observations"]:
        admitted_ids = [
            admission["admission_record_id"]
            for admission in observation["admissions"]
            if admission["decision"] == "admitted"
        ]
        if not admitted_ids:
            continue
        projection.append(
            {
                "subject_record_id": observation["observation_record_id"],
                "observation_record_id": observation["observation_record_id"],
                "admission_record_ids": admitted_ids,
                "source": observation["source"],
                "reconstruction_type": reconstruction["reconstruction_type"],
            }
        )
    return projection
