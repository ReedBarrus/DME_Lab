"""Prospective realization harness for EDGE_SOURCE_STANDING_HELD_OUT_001.

This file materializes the held-out realization procedure only.

It does NOT freeze the contract, authorize execution, apply the expected
scientific vector, or promote a scientific result.

The harness intentionally contains no expected-result vector.  A future,
separately authorized invocation must first pass administration preflight,
then collects all six raw evaluator observations in memory, and only emits
the completed observation vector after every cell returns.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
from importlib import metadata
import json
from pathlib import Path
import sys
from typing import Any


QUESTION_ID = "EDGE_SOURCE_STANDING_HELD_OUT_001"

EDGE_ENTITLEMENT_PATH = Path("src/cockpit/edge_entitlement_v0.py")
EDGE_ENTITLEMENT_GIT_BLOB = "ac3abb625c2a4a005bb5e9a324e77afc9b88ddb6"

SOURCE_STANDING_PATH = Path("src/cockpit/source_standing_v0.py")
SOURCE_STANDING_GIT_BLOB = "a0f26f7190971dbf4bdfa1046de4cb189bf79827"

FIXTURE_PATH = Path(
    "docs/candidates/concordance_cockpit_v0/held_out/"
    "EDGE_SOURCE_STANDING_HELD_OUT_FIXTURES_001.json"
)
FIXTURE_GIT_BLOB = "4f1d49b2ad1e39f122a0e23ba3ddaf27eb745047"
FIXTURE_CONTENT_SHA256 = (
    "16a0bae80c33c7ebd04a52cdc8370dfe427a50be1ca43a87d12c7e8b1422b6c2"
)

CRYPTOGRAPHY_VERSION = "46.0.4"

CLAIM_ARTIFACT_ID = "CLAIM_HO"
CLAIM_SHA256 = "29e6c8a409b59c405ac7190a9532c713be491237c96241315d66b3a1db9b1dd4"
SOURCE_REF = "S_HO"
FROM_REF = "FROM_HO"
RELATION_TYPE = "CONSTRAINS"
TO_REF = "TO_HO"
GROUNDING_KEY_FINGERPRINT = (
    "31a6404b748800f07cf1a5c0899fcbd83a2700829230ed315ef4f6683f2c43ad"
)

CELL_ORDER = ("P1", "H1", "H2", "H3", "H4", "H5")

FORBIDDEN_EVALUATOR_INPUT_KEYS = {
    "cell_id",
    "expected_result",
    "independent",
    "grounding_accepted",
    "claimant_controls_issuer",
    "standing_valid",
    "authorized",
}


class AdministrationInvalid(RuntimeError):
    """The realization procedure was not mechanically admissible."""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise AdministrationInvalid(reason)


def _read_exact(repo_root: Path, relative_path: Path) -> bytes:
    path = (repo_root / relative_path).resolve()
    try:
        path.relative_to(repo_root)
    except ValueError as exc:
        raise AdministrationInvalid("PATH_ESCAPES_REPO_ROOT") from exc
    try:
        return path.read_bytes()
    except OSError as exc:
        raise AdministrationInvalid(
            f"REQUIRED_FILE_UNREADABLE:{relative_path.as_posix()}"
        ) from exc


def _collect_dict_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                keys.add(key)
            keys.update(_collect_dict_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_collect_dict_keys(child))
    return keys


def administration_preflight(repo_root: Path) -> dict[str, Any]:
    """Verify the prospective administration without invoking the evaluator."""

    repo_root = repo_root.resolve()

    try:
        cryptography_version = metadata.version("cryptography")
    except metadata.PackageNotFoundError as exc:
        raise AdministrationInvalid("CRYPTOGRAPHY_NOT_INSTALLED") from exc

    _require(
        cryptography_version == CRYPTOGRAPHY_VERSION,
        "CRYPTOGRAPHY_VERSION_MISMATCH",
    )

    edge_bytes = _read_exact(repo_root, EDGE_ENTITLEMENT_PATH)
    standing_bytes = _read_exact(repo_root, SOURCE_STANDING_PATH)
    fixture_bytes = _read_exact(repo_root, FIXTURE_PATH)

    _require(
        _git_blob_sha1(edge_bytes) == EDGE_ENTITLEMENT_GIT_BLOB,
        "EDGE_ENTITLEMENT_IDENTITY_MISMATCH",
    )
    _require(
        _git_blob_sha1(standing_bytes) == SOURCE_STANDING_GIT_BLOB,
        "SOURCE_STANDING_IDENTITY_MISMATCH",
    )
    _require(
        _git_blob_sha1(fixture_bytes) == FIXTURE_GIT_BLOB,
        "FIXTURE_GIT_BLOB_MISMATCH",
    )
    _require(
        _sha256_hex(fixture_bytes) == FIXTURE_CONTENT_SHA256,
        "FIXTURE_CONTENT_SHA256_MISMATCH",
    )

    try:
        fixture = json.loads(fixture_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AdministrationInvalid("FIXTURE_JSON_INVALID") from exc

    _require(isinstance(fixture, dict), "FIXTURE_ROOT_NOT_OBJECT")
    _require(
        fixture.get("scientific_question_id") == QUESTION_ID,
        "QUESTION_ID_MISMATCH",
    )

    forbidden_present = _collect_dict_keys(fixture) & FORBIDDEN_EVALUATOR_INPUT_KEYS
    _require(
        not forbidden_present,
        "FIXTURE_CONTAINS_FORBIDDEN_SEMANTIC_INPUT",
    )

    grounding_root = fixture.get("grounding_root")
    _require(isinstance(grounding_root, dict), "GROUNDING_ROOT_INVALID")
    _require(
        grounding_root.get("private_key_retained") is False,
        "GROUNDING_ROOT_PRIVATE_KEY_RETENTION_NOT_FALSE",
    )
    _require(
        "private_key_hex" not in grounding_root,
        "GROUNDING_ROOT_PRIVATE_KEY_PRESENT",
    )

    try:
        root_public_raw = bytes.fromhex(grounding_root["public_key_hex"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AdministrationInvalid("GROUNDING_PUBLIC_KEY_INVALID") from exc

    _require(
        _sha256_hex(root_public_raw) == GROUNDING_KEY_FINGERPRINT,
        "GROUNDING_PUBLIC_KEY_FINGERPRINT_MISMATCH",
    )
    _require(
        grounding_root.get("fingerprint") == GROUNDING_KEY_FINGERPRINT,
        "GROUNDING_ROOT_DECLARED_FINGERPRINT_MISMATCH",
    )

    claim = fixture.get("claim")
    _require(isinstance(claim, dict), "CLAIM_FIXTURE_INVALID")

    try:
        claim_bytes = bytes.fromhex(claim["bytes_hex"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AdministrationInvalid("CLAIM_BYTES_INVALID") from exc

    _require(_sha256_hex(claim_bytes) == CLAIM_SHA256, "CLAIM_SHA256_MISMATCH")
    _require(claim.get("sha256") == CLAIM_SHA256, "CLAIM_DECLARED_SHA256_MISMATCH")
    _require(
        claim.get("artifact_id") == CLAIM_ARTIFACT_ID,
        "CLAIM_ARTIFACT_ID_MISMATCH",
    )
    _require(claim.get("source_ref") == SOURCE_REF, "SOURCE_REF_MISMATCH")
    _require(claim.get("from_ref") == FROM_REF, "FROM_REF_MISMATCH")
    _require(claim.get("relation_type") == RELATION_TYPE, "RELATION_TYPE_MISMATCH")
    _require(claim.get("to_ref") == TO_REF, "TO_REF_MISMATCH")

    cells = fixture.get("cells")
    _require(isinstance(cells, dict), "CELLS_INVALID")
    _require(set(cells) == set(CELL_ORDER), "SCIENTIFIC_CELL_SET_MISMATCH")

    for label in CELL_ORDER:
        cell = cells[label]
        _require(isinstance(cell, dict), f"CELL_INVALID:{label}")
        _require(
            set(cell) == {"standing_basis_hex", "grounding_signature_hex"},
            f"CELL_SHAPE_INVALID:{label}",
        )
        standing_hex = cell["standing_basis_hex"]
        signature_hex = cell["grounding_signature_hex"]
        _require(
            (standing_hex is None) == (signature_hex is None),
            f"CELL_PARTIAL_STANDING_INPUT:{label}",
        )
        if standing_hex is not None:
            try:
                bytes.fromhex(standing_hex)
                bytes.fromhex(signature_hex)
            except (TypeError, ValueError) as exc:
                raise AdministrationInvalid(
                    f"CELL_HEX_INVALID:{label}"
                ) from exc

    return fixture


def _derive_kwargs(
    fixture: dict[str, Any],
    cell: dict[str, Any],
) -> dict[str, Any]:
    """Construct only the evaluator's raw bounded input surface."""

    claim = fixture["claim"]
    standing_hex = cell["standing_basis_hex"]
    signature_hex = cell["grounding_signature_hex"]

    kwargs = {
        "claim_artifact_bytes": bytes.fromhex(claim["bytes_hex"]),
        "expected_claim_sha256": CLAIM_SHA256,
        "expected_claim_artifact_id": CLAIM_ARTIFACT_ID,
        "source_ref": SOURCE_REF,
        "from_ref": FROM_REF,
        "relation_type": RELATION_TYPE,
        "to_ref": TO_REF,
        "standing_basis_bytes": (
            None if standing_hex is None else bytes.fromhex(standing_hex)
        ),
        "grounding_signature": (
            None if signature_hex is None else bytes.fromhex(signature_hex)
        ),
    }

    _require(
        set(kwargs).isdisjoint(FORBIDDEN_EVALUATOR_INPUT_KEYS),
        "FORBIDDEN_EVALUATOR_INPUT_CONSTRUCTED",
    )
    return kwargs


def _load_pinned_evaluator(repo_root: Path):
    """Load the already-verified evaluator from this exact checkout."""

    repo_root = repo_root.resolve()
    repo_root_text = str(repo_root)
    if not sys.path or sys.path[0] != repo_root_text:
        sys.path.insert(0, repo_root_text)

    standing_module = importlib.import_module("src.cockpit.source_standing_v0")
    edge_module = importlib.import_module("src.cockpit.edge_entitlement_v0")

    _require(
        Path(standing_module.__file__).resolve()
        == (repo_root / SOURCE_STANDING_PATH).resolve(),
        "SOURCE_STANDING_IMPORT_PATH_MISMATCH",
    )
    _require(
        Path(edge_module.__file__).resolve()
        == (repo_root / EDGE_ENTITLEMENT_PATH).resolve(),
        "EDGE_ENTITLEMENT_IMPORT_PATH_MISMATCH",
    )

    return standing_module.SourceStandingEvaluatorV0


def collect_observations(repo_root: Path) -> dict[str, dict[str, str | None]]:
    """Collect the complete six-cell vector without applying an answer key."""

    fixture = administration_preflight(repo_root)
    Evaluator = _load_pinned_evaluator(repo_root)

    root_public_raw = bytes.fromhex(fixture["grounding_root"]["public_key_hex"])
    evaluator = Evaluator(grounding_public_key_raw=root_public_raw)

    observed: dict[str, dict[str, str | None]] = {}

    try:
        for label in CELL_ORDER:
            result = evaluator.derive(
                **_derive_kwargs(fixture, fixture["cells"][label])
            )
            observed[label] = {
                "status": result.status,
                "reason": result.reason,
                "standing_sha256": result.standing_sha256,
            }
    except Exception as exc:
        # Never emit a partial scientific vector.
        raise AdministrationInvalid("EVALUATION_DID_NOT_COMPLETE") from exc

    _require(set(observed) == set(CELL_ORDER), "OBSERVATION_VECTOR_INCOMPLETE")
    return observed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing the exact pinned apparatus and fixture.",
    )
    args = parser.parse_args(argv)

    try:
        observed = collect_observations(Path(args.repo_root))
    except AdministrationInvalid as exc:
        print(
            _canonical_json(
                {
                    "administration": "INVALID",
                    "reason": str(exc),
                    "scientific_vector": None,
                }
            ),
            file=sys.stderr,
        )
        return 2

    # Successful stdout is deliberately only the bounded raw observation vector.
    print(_canonical_json(observed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
