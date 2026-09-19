"""Bounded role-address availability surface for ADDRESSING_001."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

ROLE_REGISTRY_SCHEMA = "ROLE_REGISTRY_v0"
RECORD_FIELDS = {"record_id", "work_payload"}
WORK_FIELDS = {
    "source_role",
    "target_role",
    "created_against_basis",
    "task_type",
    "payload_refs",
    "authority_ceiling",
    "required_output_type",
    "depends_on",
    "supersedes",
}


class AddressingShapeError(ValueError):
    """Raised when role, record, or work artifacts do not match the bounded v0 shape."""


@dataclass(frozen=True, slots=True)
class RoleRegistry:
    roles: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RoleRegistry":
        if not isinstance(value, Mapping) or set(value) != {"schema", "roles"}:
            raise AddressingShapeError("unexpected role-registry fields")
        if value["schema"] != ROLE_REGISTRY_SCHEMA:
            raise AddressingShapeError("unexpected role-registry schema")
        roles = value["roles"]
        if not isinstance(roles, list) or not roles:
            raise AddressingShapeError("roles must be a non-empty list")
        if any(not isinstance(role, str) or not role for role in roles):
            raise AddressingShapeError("role ids must be non-empty strings")
        if len(set(roles)) != len(roles):
            raise AddressingShapeError("role ids must be unique")
        if roles != sorted(roles):
            raise AddressingShapeError("role ids must be lexicographically ordered")
        return cls(tuple(roles))

    def require(self, role_id: str) -> None:
        if role_id not in self.roles:
            raise AddressingShapeError(f"unregistered role: {role_id}")


@dataclass(frozen=True, slots=True)
class AddressedWork:
    source_role: str
    target_role: str
    created_against_basis: str
    task_type: str
    payload_refs: tuple[str, ...]
    authority_ceiling: str
    required_output_type: str
    depends_on: tuple[str, ...]
    supersedes: str | None

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
        *,
        role_registry: RoleRegistry,
    ) -> "AddressedWork":
        if not isinstance(value, Mapping) or set(value) != WORK_FIELDS:
            raise AddressingShapeError("unexpected addressed-work fields")

        for key in (
            "source_role",
            "target_role",
            "created_against_basis",
            "task_type",
            "authority_ceiling",
            "required_output_type",
        ):
            if not isinstance(value[key], str) or not value[key]:
                raise AddressingShapeError(f"{key} must be a non-empty string")

        role_registry.require(value["source_role"])
        role_registry.require(value["target_role"])

        payload_refs = _string_tuple(value["payload_refs"], "payload_refs")
        depends_on = _string_tuple(value["depends_on"], "depends_on")
        supersedes = value["supersedes"]
        if supersedes is not None and (not isinstance(supersedes, str) or not supersedes):
            raise AddressingShapeError("supersedes must be null or a non-empty string")

        return cls(
            source_role=value["source_role"],
            target_role=value["target_role"],
            created_against_basis=value["created_against_basis"],
            task_type=value["task_type"],
            payload_refs=payload_refs,
            authority_ceiling=value["authority_ceiling"],
            required_output_type=value["required_output_type"],
            depends_on=depends_on,
            supersedes=supersedes,
        )

    def as_mapping(self) -> dict[str, Any]:
        return {
            "source_role": self.source_role,
            "target_role": self.target_role,
            "created_against_basis": self.created_against_basis,
            "task_type": self.task_type,
            "payload_refs": list(self.payload_refs),
            "authority_ceiling": self.authority_ceiling,
            "required_output_type": self.required_output_type,
            "depends_on": list(self.depends_on),
            "supersedes": self.supersedes,
        }


@dataclass(frozen=True, slots=True)
class DurableWorkRecord:
    record_id: str
    work_payload: AddressedWork

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
        *,
        role_registry: RoleRegistry,
    ) -> "DurableWorkRecord":
        if not isinstance(value, Mapping) or set(value) != RECORD_FIELDS:
            raise AddressingShapeError("unexpected durable-work-record fields")
        record_id = value["record_id"]
        if not isinstance(record_id, str) or not record_id:
            raise AddressingShapeError("record_id must be a non-empty string")
        work_payload = value["work_payload"]
        if not isinstance(work_payload, Mapping):
            raise AddressingShapeError("work_payload must be an object")
        return cls(
            record_id=record_id,
            work_payload=AddressedWork.from_mapping(work_payload, role_registry=role_registry),
        )

    def as_mapping(self) -> dict[str, Any]:
        return {"record_id": self.record_id, "work_payload": self.work_payload.as_mapping()}


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise AddressingShapeError(f"{label} must be a list")
    if any(not isinstance(item, str) or not item for item in value):
        raise AddressingShapeError(f"{label} entries must be non-empty strings")
    if len(set(value)) != len(value):
        raise AddressingShapeError(f"{label} must not contain duplicates")
    return tuple(value)


def load_role_registry(path: Path) -> RoleRegistry:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    return RoleRegistry.from_mapping(value)


def load_global_work_registry(
    work_root: Path,
    *,
    role_registry: RoleRegistry,
) -> tuple[DurableWorkRecord, ...]:
    """Read every durable record; no target-role filtering occurs here."""
    root = Path(work_root)
    records: list[DurableWorkRecord] = []
    for path in sorted(root.glob("*.json"), key=lambda item: item.name):
        value = json.loads(path.read_text(encoding="utf-8"))
        records.append(DurableWorkRecord.from_mapping(value, role_registry=role_registry))

    record_ids = [record.record_id for record in records]
    if len(set(record_ids)) != len(record_ids):
        raise AddressingShapeError("record_id values must be globally unique")
    return tuple(records)


def project_available_to_role(
    records: Iterable[DurableWorkRecord],
    role_id: str,
    role_registry: RoleRegistry,
) -> tuple[DurableWorkRecord, ...]:
    """Pure role-local projection: exact work_payload.target_role equality only."""
    role_registry.require(role_id)
    materialized = tuple(records)
    return tuple(record for record in materialized if record.work_payload.target_role == role_id)


def global_record_ids(records: Iterable[DurableWorkRecord]) -> tuple[str, ...]:
    """Audit/global durable identity projection, independent of TARGET_ROLE."""
    return tuple(record.record_id for record in records)
