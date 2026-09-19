"""Bounded runtime-evidence producer for HANDLING_001 recovery qualification."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence

APPARATUS_COMMIT = "caec21938315b959582da2d4948fd0ab1c1bd545"
ADDRESSING_PATH = Path("lab/ops/candidates/addressing_001/addressing.py")
ADDRESSING_BLOB = "3c87f8e245075f1acabc3f1d68da8ac296a99dd7"
HANDLING_PATH = Path("lab/ops/candidates/handling_001/handling.py")
HANDLING_BLOB = "92ce4f978b84b38f1ac44ac66b2942ea9c565078"
ROLE_REGISTRY_PATH = Path("lab/ops/candidates/addressing_001/role_registry_v0.json")
ROLE_REGISTRY_BLOB = "3e9a0e8e97b78c1396aec6eace9c4dab43ee09c5"
CONTROLLED_WORK_PATH = Path(
    "lab/ops/candidates/addressing_001/held_out_realization/records/A.json"
)
CONTROLLED_WORK_BLOB = "734694e55ea7586b5f5a4c19e4d645ddd3c075fd"
CONTROLLED_WORK_SHA256 = "568f4e7c55eef95fe469ff68a34d411a495be5172398f956888773e5698af0c2"
CONTROLLED_RECORD_ID = "84495c8b-2e38-470d-8746-86e6b67097e9"
CONTROLLED_TARGET_ROLE = "WORKSHOP"
QUERY_ROLE = "WORKSHOP"

RECOVERY_A_CELL_ID = "93fe211c-a5a5-4d94-bf47-a8aa02ccfbb3"
RECOVERY_B_CELL_ID = "9bb69fe2-b55c-4ae2-84df-ed0f76a2f0ca"
RECOVERY_B_CLAIM_EVENT_ID = "a4c47042-51d6-46fa-82f7-70e041cc0e79"
RECOVERY_A_OUTPUT_PATH = Path(
    "lab/ops/candidates/handling_001/recovery_realization_v1/raw/A_observation.json"
)
RECOVERY_B_OUTPUT_PATH = Path(
    "lab/ops/candidates/handling_001/recovery_realization_v1/raw/B_observation.json"
)

OBSERVATION_FIELDS = (
    "WORK_EXISTS",
    "WORK_AVAILABLE_TO_ROLE",
    "WORK_CLAIMED_FOR_HANDLING",
    "AUTHORITY_STATE_CHANGED",
    "CONSEQUENCE_PATH_INVOKED",
)
PROVENANCE_FIELDS = (
    "cell_id",
    "apparatus_commit",
    "addressing_blob",
    "handling_blob",
    "role_registry_blob",
    "controlled_work_blob",
    "controlled_work_sha256",
    "claim_events_sha256",
    "invoked_functions",
    "invocation_trace_sha256",
)
INVOKED_FUNCTIONS = (
    "load_role_registry",
    "DurableWorkRecord.from_mapping",
    "global_record_ids",
    "project_available_to_role",
    "work_claimed_for_handling",
)


class RuntimeEvidenceHarnessError(RuntimeError):
    """Base failure for bounded runtime-evidence production."""


class FrozenIdentityMismatch(RuntimeEvidenceHarnessError):
    """Raised before invocation when a frozen input identity does not match."""


class FrozenCellInputMismatch(RuntimeEvidenceHarnessError):
    """Raised before invocation when A/B claim input differs from its frozen coordinate."""


class RawObservationInvalid(RuntimeEvidenceHarnessError):
    """Raised when a raw observation lacks the bounded invocation provenance."""


@dataclass(frozen=True, slots=True)
class _CellBinding:
    cell_id: str
    claim_events: tuple[dict[str, str], ...]
    output_path: Path


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def _read_verified_blob(repo_root: Path, path: Path, expected_blob: str) -> bytes:
    payload = (repo_root / path).read_bytes()
    actual = _git_blob_sha1(payload)
    if actual != expected_blob:
        raise FrozenIdentityMismatch(
            f"{path}: expected git blob {expected_blob}, observed {actual}"
        )
    return payload


def _verify_frozen_bytes(repo_root: Path) -> dict[str, bytes]:
    addressing = _read_verified_blob(repo_root, ADDRESSING_PATH, ADDRESSING_BLOB)
    handling = _read_verified_blob(repo_root, HANDLING_PATH, HANDLING_BLOB)
    registry = _read_verified_blob(repo_root, ROLE_REGISTRY_PATH, ROLE_REGISTRY_BLOB)
    specimen = _read_verified_blob(repo_root, CONTROLLED_WORK_PATH, CONTROLLED_WORK_BLOB)
    specimen_sha = _sha256(specimen)
    if specimen_sha != CONTROLLED_WORK_SHA256:
        raise FrozenIdentityMismatch(
            f"{CONTROLLED_WORK_PATH}: expected sha256 {CONTROLLED_WORK_SHA256}, observed {specimen_sha}"
        )
    return {
        "addressing": addressing,
        "handling": handling,
        "registry": registry,
        "specimen": specimen,
    }


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeEvidenceHarnessError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_frozen_apparatus(repo_root: Path):
    addressing = _load_module(
        "lab.ops.candidates.addressing_001.addressing",
        repo_root / ADDRESSING_PATH,
    )
    handling = _load_module(
        "lab.ops.candidates.handling_001.handling",
        repo_root / HANDLING_PATH,
    )
    return addressing, handling


def _normalize_claim_events(claim_events: Iterable[Mapping[str, Any]]) -> tuple[dict[str, str], ...]:
    normalized: list[dict[str, str]] = []
    for raw in claim_events:
        if not isinstance(raw, Mapping):
            raise FrozenCellInputMismatch("claim event must be a mapping")
        value = dict(raw)
        if set(value) != {"claim_event_id", "event_type", "work_record_id"}:
            raise FrozenCellInputMismatch("claim-event fields differ from frozen shape")
        if any(not isinstance(value[key], str) or not value[key] for key in value):
            raise FrozenCellInputMismatch("claim-event values must be non-empty strings")
        normalized.append(value)
    return tuple(normalized)


def _claim_events_sha256(claim_events: Sequence[Mapping[str, Any]]) -> str:
    return _sha256(_canonical_json_bytes(list(claim_events)))


def _recovery_binding(cell_label: str) -> _CellBinding:
    if cell_label == "A":
        return _CellBinding(
            cell_id=RECOVERY_A_CELL_ID,
            claim_events=(),
            output_path=RECOVERY_A_OUTPUT_PATH,
        )
    if cell_label == "B":
        return _CellBinding(
            cell_id=RECOVERY_B_CELL_ID,
            claim_events=(
                {
                    "claim_event_id": RECOVERY_B_CLAIM_EVENT_ID,
                    "event_type": "CLAIM_FOR_HANDLING",
                    "work_record_id": CONTROLLED_RECORD_ID,
                },
            ),
            output_path=RECOVERY_B_OUTPUT_PATH,
        )
    raise FrozenCellInputMismatch("cell_label must be exactly A or B")


def _invocation_trace_sha256(
    *,
    observation: Mapping[str, bool],
    cell_id: str,
    claim_events_sha256: str,
    invoked_functions: Sequence[str],
) -> str:
    return _sha256(
        _canonical_json_bytes(
            {
                "observation": dict(observation),
                "cell_id": cell_id,
                "claim_events_sha256": claim_events_sha256,
                "invoked_functions": list(invoked_functions),
                "apparatus_commit": APPARATUS_COMMIT,
                "addressing_blob": ADDRESSING_BLOB,
                "handling_blob": HANDLING_BLOB,
                "role_registry_blob": ROLE_REGISTRY_BLOB,
                "controlled_work_blob": CONTROLLED_WORK_BLOB,
                "controlled_work_sha256": CONTROLLED_WORK_SHA256,
            }
        )
    )


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())


def _produce_raw_observation(
    repo_root: Path,
    *,
    cell_id: str,
    claim_events: Sequence[Mapping[str, Any]],
    output_path: Path,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    frozen = _verify_frozen_bytes(root)
    addressing, handling = _load_frozen_apparatus(root)

    trace: list[str] = []
    registry = addressing.load_role_registry(root / ROLE_REGISTRY_PATH)
    trace.append("load_role_registry")
    if registry.roles != ("COMMANDER", "WORKSHOP"):
        raise FrozenIdentityMismatch("role registry contents differ from frozen roles")

    specimen_mapping = json.loads(frozen["specimen"].decode("utf-8"))
    work = addressing.DurableWorkRecord.from_mapping(
        specimen_mapping,
        role_registry=registry,
    )
    trace.append("DurableWorkRecord.from_mapping")
    if work.record_id != CONTROLLED_RECORD_ID:
        raise FrozenIdentityMismatch("controlled work record_id changed")
    if work.work_payload.target_role != CONTROLLED_TARGET_ROLE:
        raise FrozenIdentityMismatch("controlled work target_role changed")

    before_authority = work.work_payload.authority_ceiling
    before_work = _canonical_json_bytes(work.as_mapping())

    global_ids = addressing.global_record_ids((work,))
    trace.append("global_record_ids")
    available = addressing.project_available_to_role((work,), QUERY_ROLE, registry)
    trace.append("project_available_to_role")
    claimed = handling.work_claimed_for_handling(work, tuple(claim_events))
    trace.append("work_claimed_for_handling")

    after_authority = work.work_payload.authority_ceiling
    after_work = _canonical_json_bytes(work.as_mapping())
    if before_work != after_work:
        raise RuntimeEvidenceHarnessError("frozen apparatus mutated controlled work")

    observation = {
        "WORK_EXISTS": CONTROLLED_RECORD_ID in global_ids,
        "WORK_AVAILABLE_TO_ROLE": any(
            record.record_id == CONTROLLED_RECORD_ID for record in available
        ),
        "WORK_CLAIMED_FOR_HANDLING": bool(claimed),
        "AUTHORITY_STATE_CHANGED": before_authority != after_authority,
        "CONSEQUENCE_PATH_INVOKED": any(
            name.startswith("consequence:") for name in trace
        ),
    }
    claim_sha = _claim_events_sha256(claim_events)
    provenance = {
        "cell_id": cell_id,
        "apparatus_commit": APPARATUS_COMMIT,
        "addressing_blob": ADDRESSING_BLOB,
        "handling_blob": HANDLING_BLOB,
        "role_registry_blob": ROLE_REGISTRY_BLOB,
        "controlled_work_blob": CONTROLLED_WORK_BLOB,
        "controlled_work_sha256": CONTROLLED_WORK_SHA256,
        "claim_events_sha256": claim_sha,
        "invoked_functions": list(trace),
        "invocation_trace_sha256": _invocation_trace_sha256(
            observation=observation,
            cell_id=cell_id,
            claim_events_sha256=claim_sha,
            invoked_functions=trace,
        ),
    }
    artifact = {**observation, "_execution_provenance": provenance}
    validate_raw_observation(artifact)
    _write_exclusive(Path(output_path), _canonical_json_bytes(artifact))
    return artifact


def produce_recovery_raw_observation(
    repo_root: Path,
    *,
    cell_label: str,
    claim_events: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Produce exactly one frozen recovery A/B raw observation artifact.

    No expected observation vector is accepted. Frozen claim-event bytes are checked
    before any apparatus invocation. Qualification must not call this with valid
    recovery coordinates.
    """
    binding = _recovery_binding(cell_label)
    normalized = _normalize_claim_events(claim_events)
    if _canonical_json_bytes(list(normalized)) != _canonical_json_bytes(
        list(binding.claim_events)
    ):
        raise FrozenCellInputMismatch(
            f"{cell_label} claim-event input differs from frozen recovery coordinate"
        )
    return _produce_raw_observation(
        Path(repo_root),
        cell_id=binding.cell_id,
        claim_events=normalized,
        output_path=Path(repo_root) / binding.output_path,
    )


def _produce_qualification_raw_observation(
    repo_root: Path,
    *,
    qualification_cell_id: str,
    claim_events: Iterable[Mapping[str, Any]],
    output_path: Path,
) -> dict[str, Any]:
    """Qualification-only path using non-held-out cell/claim identities."""
    normalized = _normalize_claim_events(claim_events)
    if qualification_cell_id in {RECOVERY_A_CELL_ID, RECOVERY_B_CELL_ID}:
        raise FrozenCellInputMismatch("held-out recovery cell ids are forbidden in qualification")
    if any(
        event["claim_event_id"] == RECOVERY_B_CLAIM_EVENT_ID for event in normalized
    ):
        raise FrozenCellInputMismatch("held-out recovery B claim id is forbidden in qualification")
    return _produce_raw_observation(
        Path(repo_root),
        cell_id=qualification_cell_id,
        claim_events=normalized,
        output_path=Path(output_path),
    )


def validate_raw_observation(value: Mapping[str, Any]) -> None:
    expected_top = set(OBSERVATION_FIELDS) | {"_execution_provenance"}
    if not isinstance(value, Mapping) or set(value) != expected_top:
        raise RawObservationInvalid("raw observation schema mismatch")
    if any(not isinstance(value[field], bool) for field in OBSERVATION_FIELDS):
        raise RawObservationInvalid("observation values must be booleans")
    provenance = value["_execution_provenance"]
    if not isinstance(provenance, Mapping) or set(provenance) != set(PROVENANCE_FIELDS):
        raise RawObservationInvalid("execution provenance schema mismatch")
    if tuple(provenance["invoked_functions"]) != INVOKED_FUNCTIONS:
        raise RawObservationInvalid("required frozen apparatus invocation trace absent")
    for field, expected in (
        ("apparatus_commit", APPARATUS_COMMIT),
        ("addressing_blob", ADDRESSING_BLOB),
        ("handling_blob", HANDLING_BLOB),
        ("role_registry_blob", ROLE_REGISTRY_BLOB),
        ("controlled_work_blob", CONTROLLED_WORK_BLOB),
        ("controlled_work_sha256", CONTROLLED_WORK_SHA256),
    ):
        if provenance[field] != expected:
            raise RawObservationInvalid(f"provenance {field} mismatch")
    observation = {field: value[field] for field in OBSERVATION_FIELDS}
    expected_trace = _invocation_trace_sha256(
        observation=observation,
        cell_id=provenance["cell_id"],
        claim_events_sha256=provenance["claim_events_sha256"],
        invoked_functions=provenance["invoked_functions"],
    )
    if provenance["invocation_trace_sha256"] != expected_trace:
        raise RawObservationInvalid("invocation trace digest mismatch")
