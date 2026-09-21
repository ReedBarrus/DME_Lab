#!/usr/bin/env python3
"""Bounded synthetic apparatus for INVOCATION_EFFECT_PROVENANCE_001.

Experimental surfaces are explicit:
- SyntheticEffectHarness owns ground truth and the controlled durable effect path.
- candidate_emit receives only candidate-visible raw context.
- score_observation independently compares candidate provenance with ground truth.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping, MutableMapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

ATTRIBUTION = {"ESTABLISHED", "UNATTRIBUTED", "INVALID"}
CLAIM_EXERCISE = {"VALID", "INVALID", "UNESTABLISHED"}
AUTHORITY = {"VALID", "ABSENT", "CONSUMED", "INVALID"}
EFFECT_RESULT = {"SUCCESS", "FAILURE", "NOT_STARTED"}
PRESSURE_RESULT = {
    "INVOCATION_EFFECT_PROVENANCE_SURVIVES",
    "INVOCATION_EFFECT_PROVENANCE_FRACTURES",
    "ADMINISTRATION_INVALID",
}

CANDIDATE_INPUT_KEYS = {"schema", "invocation_binding", "effect_observation"}
INVOCATION_BINDING_KEYS = {
    "seat_id", "occupant_id", "invocation_id", "claim_id", "work_unit_id", "authority_ref"
}
EFFECT_OBSERVATION_KEYS = {
    "effect_id", "effect_kind", "mutation_event_id", "pre_coordinate",
    "post_coordinate", "object_refs", "entry_witness"
}
RECEIPT_KEYS = {
    "schema", "effect_id", "seat_id", "occupant_id", "invocation_id", "claim_id",
    "work_unit_id", "authority_ref", "pre_coordinate", "post_coordinate",
    "mutation_event_id", "effect_kind", "object_refs", "witness_commitment",
    "receipt_digest"
}
FORBIDDEN_CANDIDATE_KEYS = {
    "actual_actor_invocation_id",
    "tested_invocation_id",
    "expected_attribution",
    "expected_claim_exercise",
    "expected_authority",
    "evaluation_key",
    "attribution_verdict",
    "claim_exercise_verdict",
}


class AdministrationInvalid(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def object_identity(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise AdministrationInvalid(
            f"{label} keys mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )


def _coord(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise AdministrationInvalid(f"{field} must be sha256:<64 hex>")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise AdministrationInvalid(f"{field} malformed") from exc
    return value


def witness_commitment(entry_witness: str) -> str:
    if not isinstance(entry_witness, str) or not entry_witness:
        raise AdministrationInvalid("entry_witness must be non-empty")
    return sha256_bytes(entry_witness.encode("utf-8"))


def _receipt_digest_material(receipt_without_digest: Mapping[str, Any], entry_witness: str) -> dict[str, Any]:
    material = {
        "entry_witness": entry_witness,
        "effect_id": receipt_without_digest["effect_id"],
        "seat_id": receipt_without_digest["seat_id"],
        "occupant_id": receipt_without_digest["occupant_id"],
        "invocation_id": receipt_without_digest["invocation_id"],
        "claim_id": receipt_without_digest["claim_id"],
        "work_unit_id": receipt_without_digest["work_unit_id"],
        "authority_ref": receipt_without_digest["authority_ref"],
        "pre_coordinate": receipt_without_digest["pre_coordinate"],
        "post_coordinate": receipt_without_digest["post_coordinate"],
        "mutation_event_id": receipt_without_digest["mutation_event_id"],
        "effect_kind": receipt_without_digest["effect_kind"],
        "object_refs": receipt_without_digest["object_refs"],
        "witness_commitment": receipt_without_digest["witness_commitment"],
    }
    return material


def candidate_emit(candidate_input: Mapping[str, Any]) -> dict[str, Any]:
    """Pure candidate surface. It does not read fixtures, evaluation keys, Git, or files."""
    _exact_keys(candidate_input, CANDIDATE_INPUT_KEYS, "candidate_input")
    if candidate_input["schema"] != "invocation_effect_candidate_input_v0":
        raise AdministrationInvalid("wrong candidate input schema")

    binding = candidate_input["invocation_binding"]
    observation = candidate_input["effect_observation"]
    if not isinstance(binding, Mapping) or not isinstance(observation, Mapping):
        raise AdministrationInvalid("candidate nested inputs must be objects")
    _exact_keys(binding, INVOCATION_BINDING_KEYS, "invocation_binding")
    _exact_keys(observation, EFFECT_OBSERVATION_KEYS, "effect_observation")

    leaked = FORBIDDEN_CANDIDATE_KEYS & set(candidate_input)
    leaked |= FORBIDDEN_CANDIDATE_KEYS & set(binding)
    leaked |= FORBIDDEN_CANDIDATE_KEYS & set(observation)
    if leaked:
        raise AdministrationInvalid(f"candidate answer leakage: {sorted(leaked)}")

    pre = _coord(observation["pre_coordinate"], "pre_coordinate")
    post = _coord(observation["post_coordinate"], "post_coordinate")
    object_refs = observation["object_refs"]
    if not isinstance(object_refs, list) or any(not isinstance(x, str) or not x for x in object_refs):
        raise AdministrationInvalid("object_refs must be non-empty strings")
    if len(object_refs) != len(set(object_refs)):
        raise AdministrationInvalid("object_refs must be unique")

    receipt: dict[str, Any] = {
        "schema": "invocation_effect_provenance_receipt_v0",
        "effect_id": observation["effect_id"],
        "seat_id": binding["seat_id"],
        "occupant_id": binding["occupant_id"],
        "invocation_id": binding["invocation_id"],
        "claim_id": binding["claim_id"],
        "work_unit_id": binding["work_unit_id"],
        "authority_ref": binding["authority_ref"],
        "pre_coordinate": pre,
        "post_coordinate": post,
        "mutation_event_id": observation["mutation_event_id"],
        "effect_kind": observation["effect_kind"],
        "object_refs": list(object_refs),
        "witness_commitment": witness_commitment(observation["entry_witness"]),
        "receipt_digest": "",
    }
    receipt["receipt_digest"] = sha256_bytes(
        canonical_bytes(_receipt_digest_material(receipt, observation["entry_witness"]))
    )
    _exact_keys(receipt, RECEIPT_KEYS, "candidate_receipt")
    return receipt


def _write_fsync(path: Path, payload: bytes, *, exclusive: bool) -> None:
    flags = os.O_WRONLY | os.O_CREAT
    if exclusive:
        flags |= os.O_EXCL
    else:
        flags |= os.O_TRUNC
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())


def _payload_bytes(text: str) -> bytes:
    if not isinstance(text, str):
        raise AdministrationInvalid("fixture payloads must be strings")
    return text.encode("utf-8")


def validate_fixture(fixture: Mapping[str, Any]) -> None:
    expected = {
        "cell_id", "tested_invocation_id", "effect_id", "effect_kind",
        "mutation_event_id", "actual_actor_invocation_id", "seat_id", "occupant_id",
        "candidate_claim_id", "candidate_work_unit_id", "authority_ref",
        "authority_state", "authority_scope", "branch_id", "git_author",
        "claim_at_effect_start", "tested_work_unit_id",
        "initial_payload", "mutation_payload", "entry_witness", "candidate_mode",
        "candidate_observation_override", "expected_output_payload", "object_refs",
    }
    _exact_keys(fixture, expected, "held_out_fixture")
    if fixture["authority_state"] not in AUTHORITY:
        raise AdministrationInvalid("invalid authority_state")
    if fixture["candidate_mode"] not in {"EMIT", "NO_PROVENANCE"}:
        raise AdministrationInvalid("invalid candidate_mode")
    claim = fixture["claim_at_effect_start"]
    _exact_keys(claim, {"claim_id", "status", "invocation_id", "work_unit_id"}, "claim_at_effect_start")
    authority_scope = fixture["authority_scope"]
    _exact_keys(authority_scope, {"invocation_id", "claim_id", "work_unit_id"}, "authority_scope")
    override = fixture["candidate_observation_override"]
    if not isinstance(override, Mapping) or not set(override) <= {"pre_coordinate", "post_coordinate"}:
        raise AdministrationInvalid("candidate_observation_override malformed")
    for key, value in override.items():
        _coord(value, f"override.{key}")


class SyntheticEffectHarness:
    def __init__(self, root: Path):
        self.root = Path(root)

    def execute(self, fixture: Mapping[str, Any]) -> dict[str, Any]:
        validate_fixture(fixture)
        cell_id = str(fixture["cell_id"])
        cell_root = self.root / cell_id
        cell_root.mkdir(parents=True, exist_ok=False)
        target = cell_root / "durable_effect_target.bin"

        initial = _payload_bytes(fixture["initial_payload"])
        mutation = _payload_bytes(fixture["mutation_payload"])
        _write_fsync(target, initial, exclusive=True)
        pre_read = target.read_bytes()
        pre_coordinate = sha256_bytes(pre_read)

        entry_event = {
            "event_type": "EFFECT_ENTRY",
            "effect_id": fixture["effect_id"],
            "actor_invocation_id": fixture["actual_actor_invocation_id"],
            "entry_witness_commitment": witness_commitment(fixture["entry_witness"]),
            "pre_coordinate": pre_coordinate,
        }

        _write_fsync(target, mutation, exclusive=False)
        post_read = target.read_bytes()
        post_coordinate = sha256_bytes(post_read)
        mutation_event = {
            "event_type": "CONTROLLED_MUTATION",
            "mutation_event_id": fixture["mutation_event_id"],
            "effect_id": fixture["effect_id"],
            "actor_invocation_id": fixture["actual_actor_invocation_id"],
            "pre_coordinate": pre_coordinate,
            "post_coordinate": post_coordinate,
            "target_name": target.name,
        }
        effect_exists = (
            pre_coordinate != post_coordinate
            and sha256_bytes(target.read_bytes()) == post_coordinate
            and mutation_event["pre_coordinate"] == pre_coordinate
            and mutation_event["post_coordinate"] == post_coordinate
        )

        candidate_input = None
        candidate_output = None
        if fixture["candidate_mode"] == "EMIT":
            observed_pre = fixture["candidate_observation_override"].get(
                "pre_coordinate", pre_coordinate
            )
            observed_post = fixture["candidate_observation_override"].get(
                "post_coordinate", post_coordinate
            )
            candidate_input = {
                "schema": "invocation_effect_candidate_input_v0",
                "invocation_binding": {
                    "seat_id": fixture["seat_id"],
                    "occupant_id": fixture["occupant_id"],
                    "invocation_id": fixture["actual_actor_invocation_id"],
                    "claim_id": fixture["candidate_claim_id"],
                    "work_unit_id": fixture["candidate_work_unit_id"],
                    "authority_ref": fixture["authority_ref"],
                },
                "effect_observation": {
                    "effect_id": fixture["effect_id"],
                    "effect_kind": fixture["effect_kind"],
                    "mutation_event_id": fixture["mutation_event_id"],
                    "pre_coordinate": observed_pre,
                    "post_coordinate": observed_post,
                    "object_refs": list(fixture["object_refs"]),
                    "entry_witness": fixture["entry_witness"],
                },
            }
            candidate_output = candidate_emit(candidate_input)

        expected_output = fixture["expected_output_payload"]
        output_match = None
        if expected_output is not None:
            output_match = post_coordinate == sha256_bytes(_payload_bytes(expected_output))

        ground_truth = {
            "cell_id": cell_id,
            "tested_invocation_id": fixture["tested_invocation_id"],
            "actual_actor_invocation_id": fixture["actual_actor_invocation_id"],
            "effect_id": fixture["effect_id"],
            "effect_kind": fixture["effect_kind"],
            "mutation_event_id": fixture["mutation_event_id"],
            "entry_witness": fixture["entry_witness"],
            "pre_coordinate": pre_coordinate,
            "post_coordinate": post_coordinate,
            "effect_exists": effect_exists,
            "effect_result": "SUCCESS" if effect_exists else "FAILURE",
            "claim_at_effect_start": copy.deepcopy(fixture["claim_at_effect_start"]),
            "tested_work_unit_id": fixture["tested_work_unit_id"],
            "authority_state": fixture["authority_state"],
            "authority_ref": fixture["authority_ref"],
            "authority_scope": copy.deepcopy(fixture["authority_scope"]),
            "branch_id": fixture["branch_id"],
            "git_author": fixture["git_author"],
            "object_refs": list(fixture["object_refs"]),
            "output_match": output_match,
            "entry_event": entry_event,
            "mutation_event": mutation_event,
            "raw_initial_sha256": sha256_bytes(pre_read),
            "raw_post_sha256": sha256_bytes(post_read),
        }
        return {
            "fixture_identity": object_identity(fixture),
            "candidate_input": candidate_input,
            "candidate_input_identity": object_identity(candidate_input) if candidate_input is not None else None,
            "candidate_output": candidate_output,
            "candidate_output_identity": object_identity(candidate_output) if candidate_output is not None else None,
            "ground_truth": ground_truth,
        }


def _receipt_matches_harness(receipt: Mapping[str, Any], ground: Mapping[str, Any]) -> bool:
    try:
        _exact_keys(receipt, RECEIPT_KEYS, "candidate_receipt")
    except AdministrationInvalid:
        return False
    if receipt.get("schema") != "invocation_effect_provenance_receipt_v0":
        return False

    trace_match = (
        receipt.get("effect_id") == ground["effect_id"]
        and receipt.get("effect_kind") == ground["effect_kind"]
        and receipt.get("mutation_event_id") == ground["mutation_event_id"]
        and receipt.get("pre_coordinate") == ground["pre_coordinate"]
        and receipt.get("post_coordinate") == ground["post_coordinate"]
        and receipt.get("object_refs") == ground["object_refs"]
        and receipt.get("witness_commitment") == witness_commitment(ground["entry_witness"])
    )
    recomputed = sha256_bytes(
        canonical_bytes(_receipt_digest_material(receipt, ground["entry_witness"]))
    )
    return trace_match and receipt.get("receipt_digest") == recomputed


def score_observation(
    ground: Mapping[str, Any],
    candidate_output: Mapping[str, Any] | None,
) -> dict[str, Any]:
    effect_exists = bool(ground["effect_exists"])
    tested = ground["tested_invocation_id"]
    actual = ground["actual_actor_invocation_id"]

    if not effect_exists:
        attribution = "UNATTRIBUTED"
    elif candidate_output is None:
        attribution = "UNATTRIBUTED"
    else:
        receipt_invocation = candidate_output.get("invocation_id")
        matches_harness = _receipt_matches_harness(candidate_output, ground)

        if receipt_invocation == tested:
            if actual != tested or not matches_harness:
                attribution = "INVALID"
            else:
                attribution = "ESTABLISHED"
        else:
            if not matches_harness:
                attribution = "INVALID"
            else:
                attribution = "UNATTRIBUTED"

    if attribution != "ESTABLISHED":
        exercise = "UNESTABLISHED"
    else:
        claim = ground["claim_at_effect_start"]
        matching = (
            claim["status"] == "ACTIVE"
            and claim["invocation_id"] == tested
            and claim["work_unit_id"] == ground["tested_work_unit_id"]
        )
        exercise = "VALID" if matching else "INVALID"

    result = {
        "EFFECT_EXISTS": effect_exists,
        "INVOCATION_EFFECT_ATTRIBUTION": attribution,
        "CLAIM_EXERCISE": exercise,
        "AUTHORIZATION_AT_EFFECT_START": ground["authority_state"],
        "EFFECT_RESULT": ground["effect_result"],
        "OUTPUT_MATCH": ground["output_match"],
    }
    if attribution not in ATTRIBUTION:
        raise AssertionError(attribution)
    if exercise not in CLAIM_EXERCISE:
        raise AssertionError(exercise)
    if result["AUTHORIZATION_AT_EFFECT_START"] not in AUTHORITY:
        raise AssertionError(result["AUTHORIZATION_AT_EFFECT_START"])
    if result["EFFECT_RESULT"] not in EFFECT_RESULT:
        raise AssertionError(result["EFFECT_RESULT"])
    return result


def git_blob(path: Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout.strip()


def verify_freeze(freeze: Mapping[str, Any]) -> None:
    for row in freeze["frozen_files"]:
        path = ROOT / row["path"]
        if not path.is_file():
            raise AdministrationInvalid(f"frozen path missing: {row['path']}")
        observed = git_blob(path)
        if observed != row["git_blob"]:
            raise AdministrationInvalid(
                f"freeze mismatch {row['path']}: expected {row['git_blob']} observed {observed}"
            )
    expected_python = freeze["environment"]["python"]
    observed_python = f"{sys.version_info.major}.{sys.version_info.minor}"
    if observed_python != expected_python:
        raise AdministrationInvalid(
            f"python version mismatch expected {expected_python} observed {observed_python}"
        )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def execute_held_out(
    *,
    fixtures_path: Path,
    key_path: Path,
    freeze_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    freeze = load_json(freeze_path)
    verify_freeze(freeze)
    fixture_set = load_json(fixtures_path)
    evaluation_key = load_json(key_path)

    fixtures = fixture_set["fixtures"]
    order = fixture_set["cell_order"]
    if [row["cell_id"] for row in fixtures] != order:
        raise AdministrationInvalid("held-out fixture order mismatch")
    if set(evaluation_key["cells"]) != set(order):
        raise AdministrationInvalid("evaluation-key cell set mismatch")
    if order != freeze["held_out_cell_order"]:
        raise AdministrationInvalid("freeze cell order mismatch")

    receipts: list[dict[str, Any]] = []
    disposition = "INVOCATION_EFFECT_PROVENANCE_SURVIVES"
    failing_cell = None

    with tempfile.TemporaryDirectory(prefix="iep001-held-out-") as tmp:
        harness = SyntheticEffectHarness(Path(tmp))
        for fixture in fixtures:
            cell_id = fixture["cell_id"]
            expected = evaluation_key["cells"][cell_id]
            observation = harness.execute(fixture)
            derived = score_observation(
                observation["ground_truth"],
                observation["candidate_output"],
            )
            passed = derived == expected
            receipt = {
                "cell_id": cell_id,
                "fixture_identity": observation["fixture_identity"],
                "candidate_input_identity": observation["candidate_input_identity"],
                "candidate_output_identity": observation["candidate_output_identity"],
                "candidate_input": observation["candidate_input"],
                "candidate_output": observation["candidate_output"],
                "harness_ground_truth": observation["ground_truth"],
                "derived_relation_vector": derived,
                "expected_relation_vector": expected,
                "pass": passed,
            }
            receipts.append(receipt)
            if not passed:
                disposition = "INVOCATION_EFFECT_PROVENANCE_FRACTURES"
                failing_cell = cell_id
                break

    result = {
        "object_type": "INVOCATION_EFFECT_PROVENANCE_001_PRESSURE_RESULT",
        "object_id": "INVOCATION_EFFECT_PROVENANCE_001-HELD_OUT-001",
        "disposition": disposition,
        "failing_cell": failing_cell,
        "qualified_apparatus_basis_head": freeze["apparatus_basis_head"],
        "qualified_warrant_blob": freeze["warrant_blob"],
        "cell_order": order,
        "cell_receipts": receipts,
        "historical_lane_b_mutation": "NONE",
        "retroactive_lane_b_attribution": "NONE",
        "live_lane_a_mutation": "NONE",
        "live_lane_b_mutation": "NONE",
        "merge": "NONE",
        "deployment": "NONE",
        "external_consequence": "NONE",
    }
    output_path.write_bytes(canonical_bytes(result))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    held = sub.add_parser("held-out")
    held.add_argument("--fixtures", type=Path, required=True)
    held.add_argument("--key", type=Path, required=True)
    held.add_argument("--freeze", type=Path, required=True)
    held.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "held-out":
            result = execute_held_out(
                fixtures_path=args.fixtures,
                key_path=args.key,
                freeze_path=args.freeze,
                output_path=args.output,
            )
        else:
            raise AssertionError(args.command)
    except (AdministrationInvalid, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        result = {
            "object_type": "INVOCATION_EFFECT_PROVENANCE_001_PRESSURE_RESULT",
            "object_id": "INVOCATION_EFFECT_PROVENANCE_001-HELD_OUT-001",
            "disposition": "ADMINISTRATION_INVALID",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "historical_lane_b_mutation": "NONE",
            "retroactive_lane_b_attribution": "NONE",
            "live_lane_a_mutation": "NONE",
            "live_lane_b_mutation": "NONE",
            "merge": "NONE",
            "deployment": "NONE",
            "external_consequence": "NONE",
        }
        args.output.write_bytes(canonical_bytes(result))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    if result["disposition"] == "INVOCATION_EFFECT_PROVENANCE_SURVIVES":
        print(
            f"IEP001_DISPOSITION={result['disposition']} "
            f"CELLS={len(result['cell_receipts'])}/{len(result['cell_order'])}"
        )
        return 0
    print(
        f"IEP001_DISPOSITION={result['disposition']} "
        f"FAILING_CELL={result.get('failing_cell')}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
