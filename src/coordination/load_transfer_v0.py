"""LOAD_TRANSFER_001 minimal coordination substrate.

This module carries one bounded repository-local coordination handoff.
It does not invoke models, grant authority, retry work, schedule workers,
promote standing, or mutate a trust root.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


FRAME_TYPE = "CURRENT_OPERATIVE_FRAME_V0"
WORK_ITEM_TYPE = "SEAT_WORK_ITEM_V0"
HANDOFF_TYPE = "HANDOFF_RECEIPT_V0"

FRAME_OPERATIVE = "OPERATIVE"
FRAME_SUPERSEDED = "SUPERSEDED"

WORK_STATUSES = frozenset(
    {"QUEUED", "CLAIMED", "COMPLETED", "HELD", "REJECTED", "SUPERSEDED"}
)
TERMINAL_WORK_STATUSES = frozenset({"COMPLETED", "HELD", "REJECTED"})
RESULT_POSTURES = TERMINAL_WORK_STATUSES

AUTHORITY_NONE = "NONE"
SCIENTIFIC_EFFECT_NONE = "NONE"
ATLAS_EFFECT_NONE = "NONE"
UNRESOLVED_DESTINATION = "UNRESOLVED"

FRAME_REQUIRED = frozenset(
    {
        "object_type",
        "frame_id",
        "created_at",
        "repo_ref",
        "repo_head",
        "target",
        "qualified_standing",
        "active_horizon",
        "unresolved_load",
        "authority_posture",
        "available_surfaces",
        "current_work_item_ids",
        "explicitly_noncurrent",
        "source_handles",
        "claim_ceiling",
        "status",
        "superseded_by",
        "integrity_sha256",
    }
)

WORK_REQUIRED = frozenset(
    {
        "object_type",
        "work_item_id",
        "created_at",
        "created_from_frame_id",
        "status",
        "role",
        "source_objects",
        "required_handoff_ids",
        "requested_transformation",
        "allowed_consequences",
        "forbidden_consequences",
        "required_evidence",
        "required_output",
        "claim_ceiling",
        "stop_condition",
        "authority_requirement",
        "budget_requirement",
        "next_destination_if_complete",
        "next_destination_if_unresolved",
        "claimed_by",
        "claimed_at",
        "completed_at",
        "result_posture",
        "output_object_identities",
        "integrity_sha256",
    }
)

HANDOFF_REQUIRED = frozenset(
    {
        "object_type",
        "handoff_id",
        "created_at",
        "seat_id",
        "work_item_id",
        "input_frame_id",
        "input_work_item_identity",
        "terminal_work_item_identity",
        "input_object_identities",
        "output_object_identities",
        "result_posture",
        "unresolved",
        "authority_effect",
        "scientific_standing_effect",
        "atlas_effect",
        "next_eligible_destination",
        "challenge_handles",
        "stop_reason",
        "integrity_sha256",
    }
)


class CoordinationError(ValueError):
    """A coordination object cannot lawfully enter the bounded substrate."""


class FrameUnresolved(CoordinationError):
    """The operative frame is missing, malformed, stale, or superseded."""


class WorkItemRejected(CoordinationError):
    """A work item transition is not permitted by the declared frame/role."""


class HandoffUnresolved(CoordinationError):
    """A handoff cannot be reconstructed from the serialized objects."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _payload_without_integrity(obj: Mapping[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(dict(obj))
    payload.pop("integrity_sha256", None)
    return payload


def seal_object(obj: Mapping[str, Any]) -> dict[str, Any]:
    retained = copy.deepcopy(dict(obj))
    retained["integrity_sha256"] = canonical_sha256(_payload_without_integrity(retained))
    return retained


def verify_seal(obj: Mapping[str, Any]) -> str:
    observed = obj.get("integrity_sha256")
    if not isinstance(observed, str) or len(observed) != 64:
        raise CoordinationError("missing or invalid integrity_sha256")
    expected = canonical_sha256(_payload_without_integrity(obj))
    if observed != expected:
        raise CoordinationError(
            f"object integrity mismatch (expected {expected}, got {observed})"
        )
    return observed


def object_identity(obj: Mapping[str, Any]) -> str:
    """Return the stable identity of one sealed coordination/output object."""
    return verify_seal(obj)


def artifact_descriptor(repo_path: str, content: bytes) -> dict[str, Any]:
    """Bind one repository-local artifact without granting any write authority."""
    _require_text(repo_path, "repo_path")
    if repo_path.startswith("/") or "\\" in repo_path or ".." in Path(repo_path).parts:
        raise CoordinationError("repo_path must be safe repository-relative syntax")
    if not isinstance(content, bytes):
        raise CoordinationError("artifact content must be bytes")
    return seal_object(
        {
            "object_type": "REPO_ARTIFACT_IDENTITY_V0",
            "repo_path": repo_path,
            "content_sha256": hashlib.sha256(content).hexdigest(),
            "size_bytes": len(content),
            "integrity_sha256": "",
        }
    )


def verify_artifact_descriptor(
    descriptor: Mapping[str, Any], content: bytes
) -> str:
    verify_seal(descriptor)
    if descriptor.get("object_type") != "REPO_ARTIFACT_IDENTITY_V0":
        raise CoordinationError("unsupported artifact descriptor")
    if not isinstance(content, bytes):
        raise CoordinationError("artifact content must be bytes")
    if descriptor.get("size_bytes") != len(content):
        raise CoordinationError("artifact size mismatch")
    observed = hashlib.sha256(content).hexdigest()
    if descriptor.get("content_sha256") != observed:
        raise CoordinationError("artifact byte identity mismatch")
    return descriptor["integrity_sha256"]


def _require_exact_keys(obj: Mapping[str, Any], required: frozenset[str], label: str) -> None:
    if not isinstance(obj, Mapping) or set(obj) != required:
        missing = sorted(required - set(obj))
        extra = sorted(set(obj) - required)
        raise CoordinationError(
            f"{label} exact-key mismatch; missing={missing}, extra={extra}"
        )


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoordinationError(f"{field} must be non-empty text")
    return value


def _require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise CoordinationError(f"{field} must be a list")
    return value


def validate_frame(
    frame: Mapping[str, Any], *, require_current: bool = True
) -> dict[str, Any]:
    _require_exact_keys(frame, FRAME_REQUIRED, FRAME_TYPE)
    verify_seal(frame)
    if frame["object_type"] != FRAME_TYPE:
        raise FrameUnresolved("unsupported frame object_type")
    for field in (
        "frame_id",
        "created_at",
        "repo_ref",
        "repo_head",
        "target",
        "qualified_standing",
        "active_horizon",
        "authority_posture",
        "claim_ceiling",
    ):
        _require_text(frame[field], field)
    if len(frame["repo_head"]) != 40:
        raise FrameUnresolved("repo_head must be an exact 40-character commit id")
    for field in (
        "unresolved_load",
        "available_surfaces",
        "current_work_item_ids",
        "explicitly_noncurrent",
        "source_handles",
    ):
        _require_list(frame[field], field)
    if frame["status"] not in {FRAME_OPERATIVE, FRAME_SUPERSEDED}:
        raise FrameUnresolved("invalid frame status")
    if frame["status"] == FRAME_SUPERSEDED:
        _require_text(frame["superseded_by"], "superseded_by")
        if require_current:
            raise FrameUnresolved(
                f"frame {frame['frame_id']} is superseded by {frame['superseded_by']}"
            )
    elif frame["superseded_by"] is not None:
        raise FrameUnresolved("operative frame cannot declare superseded_by")
    return copy.deepcopy(dict(frame))


def read_current_frame(frame: Mapping[str, Any]) -> dict[str, Any]:
    return validate_frame(frame, require_current=True)


def supersede_frame(
    frame: Mapping[str, Any], *, successor_frame_id: str
) -> dict[str, Any]:
    retained = validate_frame(frame, require_current=True)
    _require_text(successor_frame_id, "successor_frame_id")
    if successor_frame_id == retained["frame_id"]:
        raise FrameUnresolved("frame cannot supersede itself")
    retained["status"] = FRAME_SUPERSEDED
    retained["superseded_by"] = successor_frame_id
    return seal_object(retained)


def validate_work_item(item: Mapping[str, Any]) -> dict[str, Any]:
    _require_exact_keys(item, WORK_REQUIRED, WORK_ITEM_TYPE)
    verify_seal(item)
    if item["object_type"] != WORK_ITEM_TYPE:
        raise WorkItemRejected("unsupported work item object_type")
    for field in (
        "work_item_id",
        "created_at",
        "created_from_frame_id",
        "role",
        "requested_transformation",
        "required_output",
        "claim_ceiling",
        "stop_condition",
        "authority_requirement",
        "budget_requirement",
        "next_destination_if_complete",
        "next_destination_if_unresolved",
    ):
        _require_text(item[field], field)
    for field in (
        "source_objects",
        "required_handoff_ids",
        "allowed_consequences",
        "forbidden_consequences",
        "required_evidence",
        "output_object_identities",
    ):
        _require_list(item[field], field)
    if item["status"] not in WORK_STATUSES:
        raise WorkItemRejected("invalid work item status")
    if item["status"] == "QUEUED":
        if any(
            item[field] is not None
            for field in ("claimed_by", "claimed_at", "completed_at", "result_posture")
        ):
            raise WorkItemRejected("queued work item carries later-lifecycle fields")
    if item["status"] == "CLAIMED":
        _require_text(item["claimed_by"], "claimed_by")
        _require_text(item["claimed_at"], "claimed_at")
        if item["completed_at"] is not None or item["result_posture"] is not None:
            raise WorkItemRejected("claimed work item carries completion fields")
    if item["status"] in TERMINAL_WORK_STATUSES:
        _require_text(item["claimed_by"], "claimed_by")
        _require_text(item["claimed_at"], "claimed_at")
        _require_text(item["completed_at"], "completed_at")
        if item["result_posture"] != item["status"]:
            raise WorkItemRejected("terminal status/result_posture mismatch")
    return copy.deepcopy(dict(item))


def claim_work_item(
    frame: Mapping[str, Any],
    item: Mapping[str, Any],
    *,
    seat_id: str,
    seat_role: str,
    claimed_at: str,
    available_handoffs: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    current = read_current_frame(frame)
    retained = validate_work_item(item)
    _require_text(seat_id, "seat_id")
    _require_text(seat_role, "seat_role")
    _require_text(claimed_at, "claimed_at")

    if retained["status"] != "QUEUED":
        raise WorkItemRejected(
            f"work item {retained['work_item_id']} is not QUEUED"
        )
    if retained["created_from_frame_id"] != current["frame_id"]:
        raise WorkItemRejected("STALE_FRAME_ID")
    if retained["work_item_id"] not in current["current_work_item_ids"]:
        raise WorkItemRejected("work item is not current in operative frame")
    if retained["role"] != seat_role:
        raise WorkItemRejected(
            f"ROLE_MISMATCH required={retained['role']} observed={seat_role}"
        )

    required_handoff_ids = set(retained["required_handoff_ids"])
    observed_handoff_ids: set[str] = set()
    for handoff in available_handoffs:
        validated = validate_handoff(handoff)
        observed_handoff_ids.add(validated["handoff_id"])
    missing_handoffs = sorted(required_handoff_ids - observed_handoff_ids)
    if missing_handoffs:
        raise WorkItemRejected(
            f"REQUIRED_HANDOFF_UNAVAILABLE {missing_handoffs}"
        )

    retained["status"] = "CLAIMED"
    retained["claimed_by"] = seat_id
    retained["claimed_at"] = claimed_at
    return seal_object(retained)


def _normalize_output_objects(
    output_objects: Sequence[Mapping[str, Any]],
) -> list[str]:
    identities: list[str] = []
    for index, obj in enumerate(output_objects):
        if not isinstance(obj, Mapping):
            raise WorkItemRejected(f"output_objects[{index}] must be an object")
        identities.append(object_identity(obj))
    return identities


def complete_work_item(
    frame: Mapping[str, Any],
    item: Mapping[str, Any],
    *,
    seat_id: str,
    completed_at: str,
    result_posture: str,
    output_objects: Sequence[Mapping[str, Any]],
    unresolved: Sequence[str],
    next_eligible_destination: str | None = None,
    challenge_handles: Sequence[str] = (),
    stop_reason: str,
    handoff_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    current = read_current_frame(frame)
    retained = validate_work_item(item)
    _require_text(seat_id, "seat_id")
    _require_text(completed_at, "completed_at")
    _require_text(stop_reason, "stop_reason")
    _require_text(handoff_id, "handoff_id")

    if retained["status"] != "CLAIMED":
        raise WorkItemRejected("only CLAIMED work can complete")
    if retained["claimed_by"] != seat_id:
        raise WorkItemRejected("seat cannot complete work claimed by another seat")
    if retained["created_from_frame_id"] != current["frame_id"]:
        raise WorkItemRejected("STALE_FRAME_ID")
    if result_posture not in RESULT_POSTURES:
        raise WorkItemRejected("invalid result_posture")
    if not isinstance(unresolved, Sequence) or isinstance(unresolved, (str, bytes)):
        raise WorkItemRejected("unresolved must be a sequence of strings")
    unresolved_values = [str(value) for value in unresolved]
    output_ids = _normalize_output_objects(output_objects)

    retained["status"] = result_posture
    retained["completed_at"] = completed_at
    retained["result_posture"] = result_posture
    retained["output_object_identities"] = output_ids
    completed = seal_object(retained)

    if next_eligible_destination is None:
        next_eligible_destination = (
            retained["next_destination_if_complete"]
            if result_posture == "COMPLETED"
            else retained["next_destination_if_unresolved"]
        )
    _require_text(next_eligible_destination, "next_eligible_destination")

    receipt = seal_object(
        {
            "object_type": HANDOFF_TYPE,
            "handoff_id": handoff_id,
            "created_at": completed_at,
            "seat_id": seat_id,
            "work_item_id": completed["work_item_id"],
            "input_frame_id": current["frame_id"],
            "input_work_item_identity": item["integrity_sha256"],
            "terminal_work_item_identity": completed["integrity_sha256"],
            "input_object_identities": [
                current["integrity_sha256"],
                *[str(value) for value in completed["source_objects"]],
            ],
            "output_object_identities": output_ids,
            "result_posture": result_posture,
            "unresolved": unresolved_values,
            "authority_effect": AUTHORITY_NONE,
            "scientific_standing_effect": SCIENTIFIC_EFFECT_NONE,
            "atlas_effect": ATLAS_EFFECT_NONE,
            "next_eligible_destination": next_eligible_destination,
            "challenge_handles": [str(value) for value in challenge_handles],
            "stop_reason": stop_reason,
            "integrity_sha256": "",
        }
    )
    return completed, receipt


def validate_handoff(receipt: Mapping[str, Any]) -> dict[str, Any]:
    _require_exact_keys(receipt, HANDOFF_REQUIRED, HANDOFF_TYPE)
    verify_seal(receipt)
    if receipt["object_type"] != HANDOFF_TYPE:
        raise HandoffUnresolved("unsupported handoff object_type")
    for field in (
        "handoff_id",
        "created_at",
        "seat_id",
        "work_item_id",
        "input_frame_id",
        "input_work_item_identity",
        "terminal_work_item_identity",
        "result_posture",
        "next_eligible_destination",
        "stop_reason",
    ):
        _require_text(receipt[field], field)
    for field in (
        "input_object_identities",
        "output_object_identities",
        "unresolved",
        "challenge_handles",
    ):
        _require_list(receipt[field], field)
    if receipt["result_posture"] not in RESULT_POSTURES:
        raise HandoffUnresolved("invalid result posture")
    if receipt["authority_effect"] != AUTHORITY_NONE:
        raise HandoffUnresolved("handoff receipt cannot grant authority")
    if receipt["scientific_standing_effect"] != SCIENTIFIC_EFFECT_NONE:
        raise HandoffUnresolved("handoff receipt cannot promote scientific standing")
    if receipt["atlas_effect"] != ATLAS_EFFECT_NONE:
        raise HandoffUnresolved("handoff receipt cannot mutate Atlas")
    return copy.deepcopy(dict(receipt))


def resolve_next_destination(
    item: Mapping[str, Any], receipt: Mapping[str, Any]
) -> str:
    work = validate_work_item(item)
    handoff = validate_handoff(receipt)
    if work["work_item_id"] != handoff["work_item_id"]:
        raise HandoffUnresolved("work item / handoff identity mismatch")
    if work["status"] not in TERMINAL_WORK_STATUSES:
        raise HandoffUnresolved("next destination requires terminal work")
    destination = handoff["next_eligible_destination"]
    if not destination:
        return UNRESOLVED_DESTINATION
    return destination


def reconstruct_handoff(
    frame: Mapping[str, Any],
    item: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    output_objects: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    current = read_current_frame(frame)
    work = validate_work_item(item)
    handoff = validate_handoff(receipt)

    if handoff["input_frame_id"] != current["frame_id"]:
        raise HandoffUnresolved("handoff references a different frame")
    if handoff["work_item_id"] != work["work_item_id"]:
        raise HandoffUnresolved("handoff references a different work item")
    if work["status"] not in TERMINAL_WORK_STATUSES:
        raise HandoffUnresolved("handoff source work is not terminal")
    if work["result_posture"] != handoff["result_posture"]:
        raise HandoffUnresolved("work/handoff result posture mismatch")
    if handoff["terminal_work_item_identity"] != work["integrity_sha256"]:
        raise HandoffUnresolved("terminal work-item identity mismatch")

    observed_output_ids = _normalize_output_objects(output_objects)
    if observed_output_ids != handoff["output_object_identities"]:
        raise HandoffUnresolved("HANDOFF_OUTPUT_IDENTITY_MISMATCH")
    if observed_output_ids != work["output_object_identities"]:
        raise HandoffUnresolved("WORK_OUTPUT_IDENTITY_MISMATCH")

    expected_inputs = {
        current["integrity_sha256"],
        *[str(value) for value in work["source_objects"]],
    }
    if not expected_inputs.issubset(set(handoff["input_object_identities"])):
        raise HandoffUnresolved("handoff input identity closure incomplete")

    return {
        "frame_id": current["frame_id"],
        "work_item_id": work["work_item_id"],
        "result_posture": handoff["result_posture"],
        "output_object_identities": observed_output_ids,
        "unresolved": copy.deepcopy(handoff["unresolved"]),
        "next_eligible_destination": handoff["next_eligible_destination"],
        "authority_required": work["authority_requirement"] != AUTHORITY_NONE,
        "allowed_transformation": work["requested_transformation"],
        "forbidden_consequences": copy.deepcopy(work["forbidden_consequences"]),
        "live_chat_context_required": False,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    retained: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            retained.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise CoordinationError(f"invalid JSONL at {path}:{line_no}") from exc
    return retained


def append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
