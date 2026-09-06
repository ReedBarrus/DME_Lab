"""Shadow validation for the tested v0 ledger record schema."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re
from typing import Any


SCHEMA_PATH = Path("schemas") / "ledger_record_v0.schema.json"


@dataclass(frozen=True)
class SchemaError:
    path: str
    validator: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class SchemaValidationResult:
    valid: bool
    errors: tuple[SchemaError, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [error.to_dict() for error in self.errors],
        }


def load_schema(path: Path | str = SCHEMA_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_ledger_record(record: Any, schema: dict[str, Any] | None = None) -> SchemaValidationResult:
    active_schema = schema or load_schema()
    errors: list[SchemaError] = []
    _validate_json_domain(record, "$", errors)
    _validate_schema(record, active_schema, "$", errors)
    return SchemaValidationResult(not errors, tuple(errors))


def _validate_json_domain(value: Any, path: str, errors: list[SchemaError]) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(SchemaError(path, "json_domain", "non-finite number is not valid JSON"))
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                errors.append(SchemaError(path, "json_domain", "object keys must be strings"))
                continue
            _validate_json_domain(child, f"{path}.{key}", errors)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _validate_json_domain(child, f"{path}[{index}]", errors)
        return
    if value is None or isinstance(value, (str, int, bool, float)):
        return
    errors.append(SchemaError(path, "json_domain", f"{type(value).__name__} is not JSON serializable"))


def _validate_schema(value: Any, schema: dict[str, Any], path: str, errors: list[SchemaError]) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(SchemaError(path, "const", f"expected {schema['const']!r}"))

    expected_type = schema.get("type")
    if expected_type and not _matches_type(value, expected_type):
        errors.append(SchemaError(path, "type", f"expected {expected_type}"))
        return

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            errors.append(SchemaError(path, "minLength", f"length must be at least {min_length}"))
        pattern = schema.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            errors.append(SchemaError(path, "pattern", f"must match {pattern}"))

    if isinstance(value, int) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(SchemaError(path, "minimum", f"must be >= {minimum}"))

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(SchemaError(f"{path}.{key}", "required", "required property is missing"))

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, child in value.items():
            if key in properties:
                _validate_schema(child, properties[key], f"{path}.{key}", errors)
            elif additional is False:
                errors.append(SchemaError(f"{path}.{key}", "additionalProperties", "unexpected property"))


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return True

