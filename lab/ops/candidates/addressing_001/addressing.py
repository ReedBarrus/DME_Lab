"""Bounded role-address availability surface for ADDRESSING_001."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

ROLE_REGISTRY_SCHEMA = "ROLE_REGISTRY_v0"
WORK_FIELDS = {
    "work_id",
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
    """Raised when role or work artifacts do not match the bounded v0 shape."""


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
    work_id: str
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
            "work_id",
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
            work_id=value["work_id"],
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
            "work_id": self.work_id,
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
) -> tuple[AddressedWork, ...]:
    """Read every durable work object; no target-role filtering occurs here."""
    root = Path(work_root)
    items: list[AddressedWork] = []
    for path in sorted(root.glob("*.json"), key=lambda item: item.name):
        value = json.loads(path.read_text(encoding="utf-8"))
        items.append(AddressedWork.from_mapping(value, role_registry=role_registry))

    ids = [item.work_id for item in items]
    if len(set(ids)) != len(ids):
        raise AddressingShapeError("work_id values must be globally unique")
    return tuple(items)


def project_available_to_role(
    work_items: Iterable[AddressedWork],
    role_id: str,
    role_registry: RoleRegistry,
) -> tuple[AddressedWork, ...]:
    """Pure role-local projection: exact TARGET_ROLE equality only."""
    role_registry.require(role_id)
    items = tuple(work_items)
    return tuple(item for item in items if item.target_role == role_id)


def global_work_ids(work_items: Iterable[AddressedWork]) -> tuple[str, ...]:
    """Audit/global existence projection, independent of TARGET_ROLE."""
    return tuple(item.work_id for item in work_items)
