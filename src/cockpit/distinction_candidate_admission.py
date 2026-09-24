from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.cockpit.typed_distinction_registry import (
    TypedDistinctionRegistryError,
    build_reconstruction_packet as build_legacy_reconstruction_packet,
    evaluate_distinction_record,
    reconstruct_distinction as reconstruct_legacy_distinction,
)


OBJECT_TYPE = "ATLAS_CANDIDATE_ADMISSION_CELL_001_PROJECTION_V0"
ADMISSION_RECORD_TYPE = "DISTINCTION_ADMISSION_RECORD_V0"
CELL_ID = "DISTINCTION_PATH_IDENTITY_NE_CONTENT_IDENTITY_001"
CANDIDATE_STANDING = "CANDIDATE_FOR_BOUNDED_ADMISSION"
ADMITTED_STANDING = "ADMITTED_BOUNDED"
ADMISSION_REASON = "EXACT_MECHANICAL_SPECIMEN_RESOLVED"
SOURCE_HEAD = "9e6415c02794bf1d71952cdc7939663a3c56023f"
EVALUATOR_PATH = "src/cockpit/typed_distinction_registry.py"
EVALUATOR_FUNCTION = "evaluate_distinction_record"
EVALUATOR_SOURCE_BLOB_SHA = "a78d1c7317f83ed0a73161cd03902840c62795f6"
SOURCE_SEAT = {"seat": "LABBOIB", "model": "QWEN"}
ADMISSION_REGISTRY_RELATIVE_PATH = Path(
    "docs/campaigns/sca001/"
    "DISTINCTION_ADMISSION_REGISTRY_V0.jsonl"
)

HANDLE_BINDING_FIELDS = (
    "handle_kind",
    "from_commit_sha",
    "from_tree_sha",
    "to_commit_sha",
    "to_tree_sha",
    "path",
    "old_blob_sha",
    "new_blob_sha",
)


class DistinctionAdmissionBindingError(TypedDistinctionRegistryError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def candidate_digest(candidate: Mapping[str, Any]) -> str:
    return _sha256(dict(candidate))


def _admission_identity(payload: Mapping[str, Any]) -> str:
    return "distinction-admission:" + _sha256(dict(payload))


def load_admission_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise DistinctionAdmissionBindingError(
            f"admission registry unavailable: {source}"
        ) from exc

    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(raw.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DistinctionAdmissionBindingError(
                f"admission registry line {line_number} is not valid UTF-8 JSON"
            ) from exc
        if not isinstance(record, dict):
            raise DistinctionAdmissionBindingError(
                f"admission registry line {line_number} is not an object"
            )
        admission_id = record.get("admission_record_id")
        if not isinstance(admission_id, str) or not admission_id:
            raise DistinctionAdmissionBindingError(
                f"admission registry line {line_number} lacks admission_record_id"
            )
        if admission_id in seen:
            raise DistinctionAdmissionBindingError(
                f"duplicate admission_record_id: {admission_id}"
            )
        seen.add(admission_id)
        records.append(record)
    return records


def build_admission_record(
    candidate: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> dict[str, Any]:
    if candidate.get("distinction_id") != CELL_ID:
        raise DistinctionAdmissionBindingError("unsupported candidate distinction")
    if candidate.get("standing") != CANDIDATE_STANDING:
        raise DistinctionAdmissionBindingError("candidate standing changed before admission")
    if evaluation.get("distinction_id") != candidate.get("distinction_id"):
        raise DistinctionAdmissionBindingError("evaluation targets a different candidate")
    if evaluation.get("standing") != ADMITTED_STANDING:
        raise DistinctionAdmissionBindingError("evaluation did not admit the candidate")
    if evaluation.get("admission_reason") != ADMISSION_REASON:
        raise DistinctionAdmissionBindingError("unexpected admission reason")
    if any(evaluation.get(field) != "NONE" for field in (
        "authority_effect", "execution_effect", "control_effect"
    )):
        raise DistinctionAdmissionBindingError("admission attempted to create an effect")

    payload = {
        "object_type": ADMISSION_RECORD_TYPE,
        "distinction_id": candidate["distinction_id"],
        "candidate_digest": candidate_digest(candidate),
        "candidate_standing": CANDIDATE_STANDING,
        "decision": ADMITTED_STANDING,
        "admission_reason": ADMISSION_REASON,
        "evaluator": {
            "path": EVALUATOR_PATH,
            "function": EVALUATOR_FUNCTION,
            "source_head": SOURCE_HEAD,
            "source_blob_sha": EVALUATOR_SOURCE_BLOB_SHA,
        },
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
        "materialized_by": dict(SOURCE_SEAT),
    }
    return {
        "admission_record_id": _admission_identity(payload),
        **payload,
    }


def validate_admission_record(
    candidate: Mapping[str, Any],
    admission_record: Mapping[str, Any],
) -> None:
    if candidate.get("distinction_id") != CELL_ID:
        raise DistinctionAdmissionBindingError("unsupported candidate distinction")
    if candidate.get("standing") != CANDIDATE_STANDING:
        raise DistinctionAdmissionBindingError("candidate no longer has candidate standing")
    if admission_record.get("object_type") != ADMISSION_RECORD_TYPE:
        raise DistinctionAdmissionBindingError("unsupported admission record type")
    if admission_record.get("distinction_id") != candidate.get("distinction_id"):
        raise DistinctionAdmissionBindingError("admission record targets wrong candidate")
    if admission_record.get("candidate_digest") != candidate_digest(candidate):
        raise DistinctionAdmissionBindingError("candidate digest binding mismatch")
    if admission_record.get("candidate_standing") != CANDIDATE_STANDING:
        raise DistinctionAdmissionBindingError("admission record candidate standing mismatch")
    if admission_record.get("decision") != ADMITTED_STANDING:
        raise DistinctionAdmissionBindingError("admission decision is not ADMITTED_BOUNDED")
    if admission_record.get("admission_reason") != ADMISSION_REASON:
        raise DistinctionAdmissionBindingError("admission reason mismatch")
    expected_evaluator = {
        "path": EVALUATOR_PATH,
        "function": EVALUATOR_FUNCTION,
        "source_head": SOURCE_HEAD,
        "source_blob_sha": EVALUATOR_SOURCE_BLOB_SHA,
    }
    if admission_record.get("evaluator") != expected_evaluator:
        raise DistinctionAdmissionBindingError("evaluator identity mismatch")
    if any(admission_record.get(field) != "NONE" for field in (
        "authority_effect", "execution_effect", "control_effect"
    )):
        raise DistinctionAdmissionBindingError("admission record contains a forbidden effect")
    if admission_record.get("materialized_by") != SOURCE_SEAT:
        raise DistinctionAdmissionBindingError("admission record source seat mismatch")

    payload = {
        key: value
        for key, value in admission_record.items()
        if key != "admission_record_id"
    }
    if admission_record.get("admission_record_id") != _admission_identity(payload):
        raise DistinctionAdmissionBindingError("admission record identity mismatch")


def derive_admitted_distinction(
    candidate: Mapping[str, Any],
    admission_record: Mapping[str, Any],
) -> dict[str, Any]:
    validate_admission_record(candidate, admission_record)
    return {
        **dict(candidate),
        "candidate_standing": CANDIDATE_STANDING,
        "standing": ADMITTED_STANDING,
        "admission_reason": admission_record["admission_reason"],
        "candidate_digest": admission_record["candidate_digest"],
        "admission_record_id": admission_record["admission_record_id"],
        "admission_source": dict(admission_record["evaluator"]),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
    }


def build_derived_reconstruction_packet(
    admitted_record: Mapping[str, Any],
) -> dict[str, Any]:
    if admitted_record.get("standing") != ADMITTED_STANDING:
        raise DistinctionAdmissionBindingError(
            "only a derived admitted distinction can be reconstructed"
        )
    return {
        "packet_type": "DISTINCTION_RECONSTRUCTION_PACKET_V0",
        "distinction_address": admitted_record["distinction_id"],
        "subject_address": admitted_record["subject_addresses"][0],
        "source_handles": [dict(item) for item in admitted_record["source_handles"]],
        "current_standing": admitted_record["standing"],
        "claim_ceiling": admitted_record["claim_ceiling"],
        "dependencies": list(admitted_record["dependencies"]),
        "unresolved": list(admitted_record["unresolved"]),
        "admission_record_id": admitted_record["admission_record_id"],
        "candidate_digest": admitted_record["candidate_digest"],
    }


def reconstruct_derived_distinction(
    packet: Mapping[str, Any],
    admitted_record: Mapping[str, Any],
) -> dict[str, Any]:
    expected = build_derived_reconstruction_packet(admitted_record)
    if dict(packet) != expected:
        raise DistinctionAdmissionBindingError(
            "reconstruction packet differs from derived admitted posture"
        )
    return {
        "result_type": "DISTINCTION_RECONSTRUCTION_RESULT_V0",
        "distinction_address": admitted_record["distinction_id"],
        "exact_distinction": "PATH_IDENTITY != CONTENT_IDENTITY",
        "mechanical_support": [
            {
                "same_path": handle["path"],
                "adjacent_commits": [
                    handle["from_commit_sha"],
                    handle["to_commit_sha"],
                ],
                "distinct_blobs": [
                    handle["old_blob_sha"],
                    handle["new_blob_sha"],
                ],
                "source_handle": dict(handle),
            }
            for handle in admitted_record["source_handles"]
        ],
        "applies_to": admitted_record["scope"],
        "does_not_establish": admitted_record["claim_ceiling"],
        "current_standing": admitted_record["standing"],
        "dependencies": admitted_record["dependencies"],
        "unresolved": admitted_record["unresolved"],
        "authority_effect": "NONE",
        "admission_record_id": admitted_record["admission_record_id"],
    }


def _raw_handle_projection(handle: Mapping[str, Any]) -> dict[str, Any]:
    return {field: handle.get(field) for field in HANDLE_BINDING_FIELDS}


def compare_reconstructed_posture(
    *,
    candidate: Mapping[str, Any],
    legacy_admitted: Mapping[str, Any],
    legacy_result: Mapping[str, Any],
    derived_admitted: Mapping[str, Any],
    derived_result: Mapping[str, Any],
) -> dict[str, Any]:
    mismatches: list[str] = []

    comparisons = {
        "distinction": (
            legacy_result.get("exact_distinction"),
            derived_result.get("exact_distinction"),
        ),
        "scope": (
            legacy_result.get("applies_to"),
            derived_result.get("applies_to"),
        ),
        "claim_ceiling": (
            legacy_result.get("does_not_establish"),
            derived_result.get("does_not_establish"),
        ),
        "standing": (
            legacy_result.get("current_standing"),
            derived_result.get("current_standing"),
        ),
        "dependencies": (
            legacy_result.get("dependencies"),
            derived_result.get("dependencies"),
        ),
        "unresolved": (
            legacy_result.get("unresolved"),
            derived_result.get("unresolved"),
        ),
        "authority_effect": (
            legacy_result.get("authority_effect"),
            derived_result.get("authority_effect"),
        ),
    }
    for field, (old, new) in comparisons.items():
        if old != new:
            mismatches.append(field)

    candidate_handles = [
        _raw_handle_projection(item)
        for item in candidate.get("source_handles", [])
    ]
    legacy_handles = [
        _raw_handle_projection(item)
        for item in legacy_admitted.get("resolved_source_handles", [])
    ]
    derived_handles = [
        _raw_handle_projection(item)
        for item in derived_admitted.get("source_handles", [])
    ]
    if legacy_handles != candidate_handles:
        mismatches.append("legacy_source_handle_binding")
    if derived_handles != candidate_handles:
        mismatches.append("derived_source_handle_binding")

    return {
        "object_type": "DISTINCTION_RECONSTRUCTION_CONSERVATION_RESULT_V0",
        "source_seat": dict(SOURCE_SEAT),
        "result": (
            "SAME_BOUNDED_POSTURE"
            if not mismatches
            else "DIFFERENT_BOUNDED_POSTURE"
        ),
        "mismatches": mismatches,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
    }


def build_candidate_admission_cell(
    *,
    candidate: Mapping[str, Any],
    admission_record: Mapping[str, Any],
    temporal_lineage: Mapping[str, Any],
) -> dict[str, Any]:
    legacy_admitted = evaluate_distinction_record(candidate, temporal_lineage)
    if legacy_admitted.get("standing") != ADMITTED_STANDING:
        raise DistinctionAdmissionBindingError(
            "unchanged evaluator no longer admits the source candidate"
        )
    expected_record = build_admission_record(candidate, legacy_admitted)
    if dict(admission_record) != expected_record:
        raise DistinctionAdmissionBindingError(
            "durable admission record does not match unchanged evaluator result"
        )

    legacy_packet = build_legacy_reconstruction_packet(legacy_admitted)
    legacy_result = reconstruct_legacy_distinction(
        legacy_packet,
        [legacy_admitted],
    )

    derived_admitted = derive_admitted_distinction(candidate, admission_record)
    derived_packet = build_derived_reconstruction_packet(derived_admitted)
    derived_result = reconstruct_derived_distinction(
        derived_packet,
        derived_admitted,
    )

    conservation = compare_reconstructed_posture(
        candidate=candidate,
        legacy_admitted=legacy_admitted,
        legacy_result=legacy_result,
        derived_admitted=derived_admitted,
        derived_result=derived_result,
    )
    return {
        "object_type": OBJECT_TYPE,
        "source_seat": dict(SOURCE_SEAT),
        "candidate": dict(candidate),
        "admission_record": dict(admission_record),
        "derived_admitted_distinction": derived_admitted,
        "reconstruction_packet": derived_packet,
        "reconstruction_result": derived_result,
        "legacy_reconstruction_result": legacy_result,
        "conservation": conservation,
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
        "claim_ceiling": (
            "This cell establishes only candidate-to-admission-record binding "
            "for the existing D001 bounded specimen. It creates no authority, "
            "topology mutation, generic admission framework, or extractor standing."
        ),
    }
