from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


OBJECT_TYPE = "TYPED_DISTINCTION_REGISTRY_PROJECTION_V0"
RECORD_TYPE = "TYPED_DISTINCTION_RECORD_V0"
CELL_ID = "DISTINCTION_PATH_IDENTITY_NE_CONTENT_IDENTITY_001"
CELL_PATH = "src/cockpit/observer/repository_fabric_app.mjs"
REGISTRY_RELATIVE_PATH = Path(
    "docs/campaigns/sca001/"
    "TYPED_DISTINCTION_REGISTRY_V0.jsonl"
)
DEFAULT_OUTPUT = Path("generated/typed_distinction_registry_v0.json")

REQUIRED_FIELDS = (
    "object_type",
    "distinction_id",
    "subject_addresses",
    "relation_type",
    "value",
    "scope",
    "source_handles",
    "constructed_by",
    "constructed_at",
    "observed_at",
    "evaluated_at",
    "standing",
    "currentness",
    "claim_ceiling",
    "dependencies",
    "unresolved",
    "authority_effect",
    "execution_effect",
    "control_effect",
)


class TypedDistinctionRegistryError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _identity(prefix: str, value: Any) -> str:
    return f"{prefix}:sha256:{_sha256_bytes(_canonical(value).encode('utf-8'))}"


def load_registry_records(path: str | Path) -> list[dict[str, Any]]:
    registry_path = Path(path)
    try:
        raw = registry_path.read_bytes()
    except OSError as exc:
        raise TypedDistinctionRegistryError(f"registry unavailable: {registry_path}") from exc
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(raw.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise TypedDistinctionRegistryError(
                f"registry line {line_number} is not valid UTF-8 JSON"
            ) from exc
        if not isinstance(record, dict):
            raise TypedDistinctionRegistryError(f"registry line {line_number} is not an object")
        distinction_id = record.get("distinction_id")
        if not isinstance(distinction_id, str) or not distinction_id:
            raise TypedDistinctionRegistryError(
                f"registry line {line_number} lacks distinction_id"
            )
        if distinction_id in seen:
            raise TypedDistinctionRegistryError(f"duplicate distinction_id: {distinction_id}")
        seen.add(distinction_id)
        records.append(record)
    return records


def _decision(
    record: Mapping[str, Any],
    standing: str,
    reason: str,
    *,
    resolved_source_handles: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    return {
        **dict(record),
        "standing": standing,
        "admission_reason": reason,
        "resolved_source_handles": [dict(item) for item in resolved_source_handles],
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
    }


def _transition_index(temporal_lineage: Mapping[str, Any]) -> dict[tuple[str, str], Mapping[str, Any]]:
    transitions = temporal_lineage.get("transitions")
    if not isinstance(transitions, list):
        raise TypedDistinctionRegistryError("temporal lineage transitions are unavailable")
    return {
        (item.get("from_commit_sha"), item.get("to_commit_sha")): item
        for item in transitions
        if isinstance(item, dict)
    }


def _frame_index(temporal_lineage: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    frames = temporal_lineage.get("frames")
    if not isinstance(frames, list):
        raise TypedDistinctionRegistryError("temporal lineage frames are unavailable")
    return {
        item.get("commit_sha"): item
        for item in frames
        if isinstance(item, dict) and isinstance(item.get("commit_sha"), str)
    }


def evaluate_distinction_record(
    record: Mapping[str, Any],
    temporal_lineage: Mapping[str, Any],
) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        standing = "NOT_ADMITTED" if "claim_ceiling" in missing else "UNRESOLVED"
        return _decision(record, standing, f"MISSING_REQUIRED_FIELDS:{','.join(missing)}")

    if record.get("object_type") != RECORD_TYPE or record.get("distinction_id") != CELL_ID:
        return _decision(record, "NOT_ADMITTED", "UNSUPPORTED_CELL_OR_RECORD_TYPE")
    if record.get("relation_type") != "NOT_EQUAL" or record.get("value") != {
        "left": "PATH_IDENTITY",
        "right": "CONTENT_IDENTITY",
    }:
        return _decision(record, "NOT_ADMITTED", "UNSUPPORTED_RELATION_TYPE_OR_VALUE")
    if any(record.get(field) != "NONE" for field in (
        "authority_effect", "execution_effect", "control_effect"
    )):
        return _decision(record, "NOT_ADMITTED", "NON_NONE_EFFECT_FORBIDDEN")
    if not isinstance(record.get("claim_ceiling"), str) or not record["claim_ceiling"].strip():
        return _decision(record, "NOT_ADMITTED", "CLAIM_CEILING_REQUIRED")
    if record.get("currentness") != "HISTORICAL_SPECIMEN":
        return _decision(record, "NOT_ADMITTED", "HISTORICAL_SPECIMEN_CANNOT_BE_CURRENT")
    if not isinstance(record.get("dependencies"), list) or not isinstance(record.get("unresolved"), list):
        return _decision(record, "NOT_ADMITTED", "DEPENDENCIES_AND_UNRESOLVED_MUST_BE_LISTS")

    subjects = record.get("subject_addresses")
    if not isinstance(subjects, list) or len(subjects) != 1:
        return _decision(record, "NOT_ADMITTED", "EXACTLY_ONE_SUBJECT_REQUIRED")
    subject = subjects[0]
    expected_subject = {
        "substrate": "repo_path",
        "repository": temporal_lineage.get("repository_identity"),
        "path": CELL_PATH,
        "object_kind": "file",
    }
    if subject != expected_subject:
        return _decision(record, "NOT_ADMITTED", "SUBJECT_ADDRESS_MISMATCH")
    scope = record.get("scope")
    if not isinstance(scope, dict) or scope != {
        "scope_type": "EXACT_ADJACENT_GIT_TRANSITIONS",
        "repository": temporal_lineage.get("repository_identity"),
        "path": CELL_PATH,
    }:
        return _decision(record, "NOT_ADMITTED", "SCOPE_MISMATCH_OR_EXPANSION")

    handles = record.get("source_handles")
    if not isinstance(handles, list) or not handles:
        return _decision(record, "UNRESOLVED", "SOURCE_HANDLE_REQUIRED")
    transitions = _transition_index(temporal_lineage)
    frames = _frame_index(temporal_lineage)
    resolved: list[dict[str, Any]] = []
    observed_blobs: set[str] = set()
    for handle in handles:
        if not isinstance(handle, dict):
            return _decision(record, "UNRESOLVED", "SOURCE_HANDLE_MALFORMED", resolved_source_handles=resolved)
        required_handle = {
            "handle_kind", "from_commit_sha", "from_tree_sha", "to_commit_sha",
            "to_tree_sha", "path", "old_blob_sha", "new_blob_sha",
        }
        if not required_handle.issubset(handle):
            return _decision(record, "UNRESOLVED", "CONTENT_COMPARISON_OR_FRAME_HANDLE_ABSENT", resolved_source_handles=resolved)
        if handle.get("handle_kind") != "GIT_ADJACENT_PATH_CONTENT_CHANGE" or handle.get("path") != CELL_PATH:
            return _decision(record, "NOT_ADMITTED", "SOURCE_HANDLE_KIND_OR_PATH_MISMATCH", resolved_source_handles=resolved)
        transition = transitions.get((handle["from_commit_sha"], handle["to_commit_sha"]))
        before = frames.get(handle["from_commit_sha"])
        after = frames.get(handle["to_commit_sha"])
        if not transition or not before or not after:
            return _decision(record, "UNRESOLVED", "SOURCE_FRAME_OR_TRANSITION_UNAVAILABLE", resolved_source_handles=resolved)
        if before.get("tree_sha") != handle["from_tree_sha"] or after.get("tree_sha") != handle["to_tree_sha"]:
            return _decision(record, "UNRESOLVED", "SOURCE_TREE_IDENTITY_MISMATCH", resolved_source_handles=resolved)
        events = transition.get("events")
        event = next((item for item in events or [] if (
            item.get("old_path") == CELL_PATH
            and item.get("new_path") == CELL_PATH
            and item.get("old_object_sha") == handle["old_blob_sha"]
            and item.get("new_object_sha") == handle["new_blob_sha"]
        )), None)
        if not event:
            return _decision(record, "UNRESOLVED", "PROVENANCE_EVENT_NOT_RESOLVED", resolved_source_handles=resolved)
        if handle["old_blob_sha"] == handle["new_blob_sha"]:
            return _decision(record, "NOT_ADMITTED", "DISTINCT_CONTENT_IDENTITIES_REQUIRED", resolved_source_handles=resolved)
        classes = set(event.get("classifications") or [])
        if not {"PERSISTED", "CONTENT_CHANGED"}.issubset(classes):
            return _decision(record, "NOT_ADMITTED", "MECHANICAL_PATH_AND_CONTENT_SUPPORT_REQUIRED", resolved_source_handles=resolved)
        if event.get("identity_basis") != "SAME_PATH_ADJACENT_FIRST_PARENT_FRAMES":
            return _decision(record, "NOT_ADMITTED", "SAME_PATH_CONTINUITY_NOT_ESTABLISHED", resolved_source_handles=resolved)
        observed_blobs.update((handle["old_blob_sha"], handle["new_blob_sha"]))
        resolved.append({
            **handle,
            "from_frame_id": before["frame_id"],
            "to_frame_id": after["frame_id"],
            "transition_id": transition["transition_id"],
            "event_id": event["event_id"],
            "identity_basis": event["identity_basis"],
            "classifications": list(event["classifications"]),
        })
    if len(observed_blobs) < 2:
        return _decision(record, "NOT_ADMITTED", "AT_LEAST_TWO_CONTENT_IDENTITIES_REQUIRED", resolved_source_handles=resolved)

    return _decision(record, "ADMITTED_BOUNDED", "EXACT_MECHANICAL_SPECIMEN_RESOLVED", resolved_source_handles=resolved)


def build_reconstruction_packet(admitted_record: Mapping[str, Any]) -> dict[str, Any]:
    if admitted_record.get("standing") != "ADMITTED_BOUNDED":
        raise TypedDistinctionRegistryError("only an admitted bounded distinction can be reconstructed")
    return {
        "packet_type": "DISTINCTION_RECONSTRUCTION_PACKET_V0",
        "distinction_address": admitted_record["distinction_id"],
        "subject_address": admitted_record["subject_addresses"][0],
        "source_handles": admitted_record["resolved_source_handles"],
        "current_standing": admitted_record["standing"],
        "claim_ceiling": admitted_record["claim_ceiling"],
        "dependencies": admitted_record["dependencies"],
        "unresolved": admitted_record["unresolved"],
    }


def reconstruct_distinction(
    packet: Mapping[str, Any],
    admitted_records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    record = next(
        (item for item in admitted_records if item.get("distinction_id") == packet.get("distinction_address")),
        None,
    )
    if not record or record.get("standing") != "ADMITTED_BOUNDED":
        raise TypedDistinctionRegistryError("distinction address does not resolve to admitted standing")
    expected = build_reconstruction_packet(record)
    if dict(packet) != expected:
        raise TypedDistinctionRegistryError("reconstruction packet differs from admitted bounded posture")
    return {
        "result_type": "DISTINCTION_RECONSTRUCTION_RESULT_V0",
        "distinction_address": record["distinction_id"],
        "exact_distinction": "PATH_IDENTITY != CONTENT_IDENTITY",
        "mechanical_support": [
            {
                "same_path": handle["path"],
                "adjacent_frames": [handle["from_frame_id"], handle["to_frame_id"]],
                "distinct_blobs": [handle["old_blob_sha"], handle["new_blob_sha"]],
            }
            for handle in record["resolved_source_handles"]
        ],
        "applies_to": record["scope"],
        "does_not_establish": record["claim_ceiling"],
        "current_standing": record["standing"],
        "dependencies": record["dependencies"],
        "unresolved": record["unresolved"],
        "authority_effect": "NONE",
    }


def build_typed_distinction_registry_projection(
    registry_path: str | Path,
    temporal_lineage: Mapping[str, Any],
) -> dict[str, Any]:
    records = load_registry_records(registry_path)
    evaluated = [evaluate_distinction_record(record, temporal_lineage) for record in records]
    admitted = [record for record in evaluated if record["standing"] == "ADMITTED_BOUNDED"]
    packets = [build_reconstruction_packet(record) for record in admitted]
    reconstructions = [reconstruct_distinction(packet, admitted) for packet in packets]
    registry_file = Path(registry_path)
    raw = registry_file.read_bytes()
    registry_coordinate = registry_file.as_posix()
    canonical_suffix = REGISTRY_RELATIVE_PATH.as_posix()
    if registry_coordinate.endswith(canonical_suffix):
        registry_coordinate = canonical_suffix
    return {
        "object_type": OBJECT_TYPE,
        "projection_standing": "DERIVED_READ_ONLY",
        "source_registry": {
            "path": registry_coordinate,
            "sha256": _sha256_bytes(raw),
        },
        "temporal_source_commit": temporal_lineage.get("source_commit"),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
        "records": evaluated,
        "reconstruction_packets": packets,
        "reconstruction_results": reconstructions,
        "counts": {
            "records": len(evaluated),
            "admitted_bounded": len(admitted),
            "not_admitted": sum(item["standing"] == "NOT_ADMITTED" for item in evaluated),
            "unresolved": sum(item["standing"] == "UNRESOLVED" for item in evaluated),
        },
        "projection_id": _identity("typed-distinction-projection", {
            "registry_sha256": _sha256_bytes(raw),
            "temporal_source_commit": temporal_lineage.get("source_commit"),
            "records": evaluated,
        }),
        "claim_ceiling": (
            "This derived projection admits only the exact Cell 001 historical Git specimen. "
            "Registration creates no authority, execution standing, dependence relation, or "
            "semantic causation."
        ),
    }


def build_unavailable_typed_distinction_registry_projection(
    *,
    registry_path: str | Path,
    temporal_lineage: Mapping[str, Any],
    reason: str,
) -> dict[str, Any]:
    registry_file = Path(registry_path)
    registry_coordinate = registry_file.as_posix()
    canonical_suffix = REGISTRY_RELATIVE_PATH.as_posix()
    if registry_coordinate.endswith(canonical_suffix):
        registry_coordinate = canonical_suffix
    return {
        "object_type": OBJECT_TYPE,
        "projection_standing": "UNAVAILABLE",
        "source_registry": {
            "path": registry_coordinate,
            "sha256": "UNAVAILABLE",
        },
        "temporal_source_commit": temporal_lineage.get("source_commit"),
        "authority_effect": "NONE",
        "execution_effect": "NONE",
        "control_effect": "NONE",
        "records": [],
        "reconstruction_packets": [],
        "reconstruction_results": [],
        "counts": {
            "records": 0,
            "admitted_bounded": 0,
            "not_admitted": 0,
            "unresolved": 0,
        },
        "unavailable_reason": reason,
        "claim_ceiling": (
            "The typed distinction overlay is unavailable. No distinction standing, "
            "authority, execution, control, or semantic causation is inferred."
        ),
    }


def generate_typed_distinction_registry_projection(
    *,
    registry_path: str | Path,
    temporal_lineage: Mapping[str, Any],
    output: str | Path,
) -> dict[str, Any]:
    output_path = Path(output)
    temporary = output_path.with_name(output_path.name + ".tmp")
    output_path.unlink(missing_ok=True)
    temporary.unlink(missing_ok=True)
    projection = build_typed_distinction_registry_projection(registry_path, temporal_lineage)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        temporary.write_text(
            json.dumps(projection, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output_path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        raise
    return projection


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the derived typed-distinction registry projection V0."
    )
    parser.add_argument("--registry", default=str(REGISTRY_RELATIVE_PATH))
    parser.add_argument("--temporal-lineage", required=True)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    temporal = json.loads(Path(args.temporal_lineage).read_text(encoding="utf-8"))
    projection = generate_typed_distinction_registry_projection(
        registry_path=args.registry,
        temporal_lineage=temporal,
        output=args.output,
    )
    print(json.dumps({"output": args.output, "counts": projection["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
