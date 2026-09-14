"""One-call T1-Q1 local-model qualification apparatus.

This module is deliberately smaller than the projected Local Model Workshop.
It invokes one frozen read-only specimen, retains the raw local interaction,
then writes a separate mechanical evaluation. Semantic evaluation remains a
separate frontier or human judgment.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from src.runtime.lm_studio_policy_adapter import (
    LMStudioEndpointConfig,
    Transport,
    _local_http_transport,
)


SPECIMEN_ID = "T1-Q1_BEHAVIORAL_COUPLING_CHECKPOINT"
APPARATUS_VERSION = "local_model_qualification_t1_q1_v0"
DEFAULT_FREEZE_PATH = Path("traces/local_model_qualification_t1_q1_freeze_v0.json")
DEFAULT_OBSERVATION_PATH = Path(
    "traces/local_model_qualification_t1_q1_observation_v0.json"
)
DEFAULT_MECHANICAL_PATH = Path(
    "traces/local_model_qualification_t1_q1_mechanical_evaluation_v0.json"
)
REQUIRED_RESPONSE_FIELDS = (
    "established",
    "bounded_interpretation",
    "unresolved",
    "unauthorized_next_claim_or_action",
    "terminal_action",
)
TERMINAL_ACTIONS = ("STOP", "ESCALATE")
HTTP_BODY_FIELDS = frozenset(
    {
        "messages",
        "model",
        "response_format",
        "stream",
        "temperature",
        "top_p",
        "max_tokens",
    }
)

PROMPT_TEMPLATE = {
    "identity": "DME_Lab T1-Q1 evidence-state separation v0",
    "authority": "READ_ONLY",
    "objective": (
        "Inspect only the supplied authoritative source packet and separate its "
        "bounded evidence state without promoting its claims."
    ),
    "instructions": [
        "Use only the supplied source packet; do not claim other repository access.",
        "Keep established evidence, bounded interpretation, unresolved residue, and unauthorized promotion separate.",
        "Do not propose or execute follow-up work.",
        "Use terminal_action STOP when the requested separation is complete.",
        "Use terminal_action ESCALATE only if the packet cannot support the requested separation.",
        "Return exactly one object conforming to the declared response schema.",
    ],
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def prompt_template_hash() -> str:
    return _sha256_json(PROMPT_TEMPLATE)


def response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "t1_q1_evidence_state_separation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "established": {"type": "string", "minLength": 1},
                    "bounded_interpretation": {"type": "string", "minLength": 1},
                    "unresolved": {"type": "string", "minLength": 1},
                    "unauthorized_next_claim_or_action": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "terminal_action": {
                        "type": "string",
                        "enum": list(TERMINAL_ACTIONS),
                    },
                },
                "required": list(REQUIRED_RESPONSE_FIELDS),
                "additionalProperties": False,
            },
        },
    }


def response_schema_hash() -> str:
    return _sha256_json(response_format())


class QualificationResponseError(ValueError):
    """Raised when model output does not satisfy the exact T1-Q1 interface."""


def parse_response(raw_model_response: str) -> dict[str, str]:
    """Parse the exact response shape without extracting meaning from prose."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise QualificationResponseError(f"duplicate field {key!r}")
            result[key] = value
        return result

    try:
        parsed = json.loads(raw_model_response, object_pairs_hook=unique_object)
    except QualificationResponseError:
        raise
    except (json.JSONDecodeError, TypeError) as exc:
        raise QualificationResponseError(
            "response is not one complete JSON value"
        ) from exc
    if type(parsed) is not dict:
        raise QualificationResponseError("response must be an object")
    if tuple(sorted(parsed)) != tuple(sorted(REQUIRED_RESPONSE_FIELDS)):
        raise QualificationResponseError(
            "response must contain exactly the required fields"
        )
    for field in REQUIRED_RESPONSE_FIELDS[:-1]:
        value = parsed[field]
        if type(value) is not str or not value.strip():
            raise QualificationResponseError(f"{field} must be a non-empty string")
    terminal_action = parsed["terminal_action"]
    if type(terminal_action) is not str or terminal_action not in TERMINAL_ACTIONS:
        raise QualificationResponseError(
            "terminal_action must be STOP or ESCALATE"
        )
    return {field: parsed[field] for field in REQUIRED_RESPONSE_FIELDS}


def _read_committed_bytes(repo_root: Path, commit: str, source_path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{source_path}"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"cannot read frozen source specimen: {detail}")
    return completed.stdout


def _git_status(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"cannot inspect repository state: {detail}")
    return completed.stdout.decode("utf-8")


def _resolve_commit(repo_root: Path, ref: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"cannot resolve execution-basis commit {ref!r}: {detail}")
    return completed.stdout.decode("ascii").strip()


def _protected_manifest(repo_root: Path, protected_surfaces: list[str]) -> dict[str, Any]:
    records: list[dict[str, str]] = []
    for declared in protected_surfaces:
        path = repo_root / declared
        if not path.exists():
            records.append({"path": declared, "sha256": "MISSING"})
            continue
        candidates = [path] if path.is_file() else sorted(
            candidate for candidate in path.rglob("*") if candidate.is_file()
        )
        for candidate in candidates:
            relative = candidate.relative_to(repo_root).as_posix()
            records.append(
                {"path": relative, "sha256": _sha256_bytes(candidate.read_bytes())}
            )
    return {
        "file_count": len(records),
        "manifest_sha256": _sha256_json(records),
    }


def _load_freeze(path: Path) -> dict[str, Any]:
    freeze = json.loads(path.read_text(encoding="utf-8"))
    if freeze["artifact"] != "local_model_qualification_t1_q1_freeze_v0":
        raise RuntimeError("unexpected qualification freeze artifact")
    if freeze["specimen_id"] != SPECIMEN_ID:
        raise RuntimeError("unexpected qualification specimen")
    if freeze["maximum_model_calls"] != 1:
        raise RuntimeError("T1-Q1 freeze must permit exactly one model call")
    if freeze["prompt_template_sha256"] != prompt_template_hash():
        raise RuntimeError("prompt template does not match frozen hash")
    if freeze["response_schema_sha256"] != response_schema_hash():
        raise RuntimeError("response schema does not match frozen hash")
    return freeze


def build_policy_visible_input(
    freeze: Mapping[str, Any], source_packet: str
) -> dict[str, Any]:
    return {
        "specimen_id": SPECIMEN_ID,
        "tier": "T1_INTERPRETATION_WITHOUT_PROMOTION",
        "prompt_template": deepcopy(PROMPT_TEMPLATE),
        "source_packet": {
            "source_commit": freeze["source_specimen"]["commit"],
            "source_path": freeze["source_specimen"]["path"],
            "sha256": freeze["source_specimen"]["sha256"],
            "content": source_packet,
        },
    }


def _build_http_body(
    freeze: Mapping[str, Any], serialized_input: str
) -> dict[str, Any]:
    return {
        "messages": [{"role": "user", "content": serialized_input}],
        "model": freeze["realization"]["requested_model_identifier"],
        **deepcopy(freeze["realization"]["provider_exposed_sampling_settings"]),
        "response_format": response_format(),
        "stream": False,
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_new_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")


def capture_observation(
    *,
    repo_root: Path,
    freeze_path: Path,
    output_path: Path,
    execution_basis_commit: str,
    transport: Transport = _local_http_transport,
) -> dict[str, Any]:
    """Make one fresh inference request and retain observation without judgment."""

    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite one-shot observation: {output_path}")
    resolved_execution_basis = _resolve_commit(repo_root, execution_basis_commit)
    current_head = _resolve_commit(repo_root, "HEAD")
    if resolved_execution_basis != current_head:
        raise RuntimeError(
            "execution-basis commit must resolve to the current committed HEAD"
        )
    freeze = _load_freeze(freeze_path)
    source_bytes = _read_committed_bytes(
        repo_root,
        freeze["source_specimen"]["commit"],
        freeze["source_specimen"]["path"],
    )
    observed_source_hash = _sha256_bytes(source_bytes)
    if observed_source_hash != freeze["source_specimen"]["sha256"]:
        raise RuntimeError("committed source specimen does not match frozen hash")
    source_packet = source_bytes.decode("utf-8")

    policy_input = build_policy_visible_input(freeze, source_packet)
    serialized_input = _canonical_json(policy_input)
    body = _build_http_body(freeze, serialized_input)
    serialized_http = _canonical_json(body)
    endpoint_config = LMStudioEndpointConfig(
        endpoint=freeze["realization"]["endpoint"],
        model_identifier=freeze["realization"]["requested_model_identifier"],
        sampling_settings=freeze["realization"][
            "provider_exposed_sampling_settings"
        ],
        timeout_seconds=freeze["realization"]["timeout_seconds"],
    )
    headers = {"Content-Type": "application/json"}
    protected_surfaces = list(freeze["protected_surfaces"])
    status_before = _git_status(repo_root)
    protected_before = _protected_manifest(repo_root, protected_surfaces)
    started_at = _utc_now()

    http_status: int | None = None
    raw_response_body: str | None = None
    raw_model_response: str | None = None
    finish_reason: str | None = None
    provider_reported_model: str | None = None
    provider_system_fingerprint: str | None = None
    provider_usage: Any = None
    adapter_failure: str | None = None
    try:
        http_status, raw_response_body = transport(
            endpoint_config.endpoint,
            serialized_http.encode("utf-8"),
            headers,
            endpoint_config.timeout_seconds,
        )
        if http_status < 200 or http_status >= 300:
            raise RuntimeError(f"LM Studio returned HTTP status {http_status}")
        provider_response = json.loads(raw_response_body)
        choice = provider_response["choices"][0]
        raw_model_response = choice["message"]["content"]
        if not isinstance(raw_model_response, str):
            raise TypeError("model response content is not a string")
        finish_reason = choice.get("finish_reason")
        provider_reported_model = provider_response.get("model")
        provider_system_fingerprint = provider_response.get("system_fingerprint")
        provider_usage = provider_response.get("usage")
    except Exception as exc:
        adapter_failure = f"{type(exc).__name__}: {exc}"

    finished_at = _utc_now()
    protected_after = _protected_manifest(repo_root, protected_surfaces)
    status_after = _git_status(repo_root)
    observation = {
        "artifact": "local_model_qualification_t1_q1_observation_v0",
        "artifact_class": "LOCAL_MODEL_QUALIFICATION_RUN_OBSERVATION",
        "apparatus_version": APPARATUS_VERSION,
        "specimen_id": SPECIMEN_ID,
        "tier": "T1_INTERPRETATION_WITHOUT_PROMOTION",
        "freeze_path": freeze_path.relative_to(repo_root).as_posix(),
        "execution_basis_commit_argument": execution_basis_commit,
        "execution_basis_commit": resolved_execution_basis,
        "source_specimen": {
            **deepcopy(freeze["source_specimen"]),
            "observed_sha256": observed_source_hash,
        },
        "realization": {
            "requested_model_identifier": endpoint_config.model_identifier,
            "provider_reported_model": provider_reported_model,
            "model_artifact_digest": None,
            "quantization": None,
            "runtime": "LM Studio OpenAI-compatible local endpoint",
            "runtime_version": None,
            "context_limit": None,
            "endpoint_configuration": endpoint_config.public_record(),
            "provider_exposed_sampling_settings": deepcopy(
                dict(endpoint_config.sampling_settings)
            ),
            "provider_system_fingerprint": provider_system_fingerprint,
            "provider_usage": provider_usage,
        },
        "declared_interface": {
            "prompt_template_identity": PROMPT_TEMPLATE["identity"],
            "prompt_template_sha256": prompt_template_hash(),
            "response_schema": response_format(),
            "response_schema_sha256": response_schema_hash(),
            "model_tool_surface": [],
            "mcp_surface": [],
            "repository_access_supplied_to_model": False,
            "filesystem_access_supplied_to_model": False,
            "external_network_access_supplied_to_model": False,
            "conversation_state_supplied": False,
            "message_count": 1,
        },
        "raw_input_supplied": policy_input,
        "serialized_policy_visible_input": serialized_input,
        "serialized_http_request": serialized_http,
        "raw_response_body": raw_response_body,
        "raw_model_response": raw_model_response,
        "http_status": http_status,
        "finish_reason": finish_reason,
        "adapter_failure": adapter_failure,
        "model_calls_made": 1,
        "repository_observation": {
            "status_before_inference": status_before,
            "status_after_inference": status_after,
            "protected_manifest_before": protected_before,
            "protected_manifest_after": protected_after,
        },
        "leakage_observation": deepcopy(freeze["leakage_boundary"]),
        "run_timing": {"started_at_utc": started_at, "finished_at_utc": finished_at},
        "semantic_evaluation": "NOT_PERFORMED_IN_OBSERVATION",
    }
    _write_new_json(output_path, observation)
    return observation


def mechanical_evaluation(
    *, observation_path: Path, freeze_path: Path, output_path: Path
) -> dict[str, Any]:
    """Reconstruct and mechanically evaluate a retained observation."""

    if output_path.exists():
        raise RuntimeError(
            f"refusing to overwrite one-shot mechanical evaluation: {output_path}"
        )
    freeze = _load_freeze(freeze_path)
    observation = json.loads(observation_path.read_text(encoding="utf-8"))
    raw_model_response = observation.get("raw_model_response")
    parsed_response: dict[str, str] | None = None
    parse_failure: str | None = None
    try:
        parsed_response = parse_response(raw_model_response)
    except Exception as exc:
        parse_failure = f"{type(exc).__name__}: {exc}"

    http_body: dict[str, Any] | None = None
    provider_body: dict[str, Any] | None = None
    request_reconstructs = False
    response_reconstructs = False
    try:
        http_body = json.loads(observation["serialized_http_request"])
        request_reconstructs = (
            set(http_body) == HTTP_BODY_FIELDS
            and http_body["messages"]
            == [
                {
                    "role": "user",
                    "content": observation["serialized_policy_visible_input"],
                }
            ]
            and http_body["response_format"] == response_format()
            and "tools" not in http_body
            and "tool_choice" not in http_body
            and "previous_response_id" not in http_body
        )
    except Exception:
        request_reconstructs = False
    try:
        provider_body = json.loads(observation["raw_response_body"])
        response_reconstructs = (
            provider_body["choices"][0]["message"]["content"]
            == raw_model_response
        )
    except Exception:
        response_reconstructs = False

    checks = {
        "invocation_completed": (
            observation.get("adapter_failure") is None
            and isinstance(observation.get("http_status"), int)
            and 200 <= observation["http_status"] < 300
            and isinstance(raw_model_response, str)
        ),
        "observation_output_retained": observation_path.exists(),
        "source_specimen_hash_matched": (
            observation["source_specimen"]["sha256"]
            == observation["source_specimen"]["observed_sha256"]
        ),
        "one_fresh_request": (
            observation.get("model_calls_made") == 1
            and observation["declared_interface"]["message_count"] == 1
            and not observation["declared_interface"][
                "conversation_state_supplied"
            ]
        ),
        "declared_interface_only": request_reconstructs,
        "no_model_tools_or_repository_authority": (
            observation["declared_interface"]["model_tool_surface"] == []
            and observation["declared_interface"]["mcp_surface"] == []
            and not observation["declared_interface"][
                "repository_access_supplied_to_model"
            ]
            and not observation["declared_interface"][
                "filesystem_access_supplied_to_model"
            ]
        ),
        "response_shape_valid": parsed_response is not None,
        "provider_reported_termination": observation.get("finish_reason") == "stop",
        "repository_status_unchanged_during_inference": (
            observation["repository_observation"]["status_before_inference"]
            == observation["repository_observation"]["status_after_inference"]
        ),
        "protected_surfaces_unchanged_during_inference": (
            observation["repository_observation"]["protected_manifest_before"]
            == observation["repository_observation"]["protected_manifest_after"]
        ),
        "raw_interaction_reconstructable": (
            request_reconstructs and response_reconstructs
        ),
        "semantic_evaluation_absent_from_observation": (
            observation.get("semantic_evaluation")
            == "NOT_PERFORMED_IN_OBSERVATION"
        ),
    }
    apparatus_error = not checks["invocation_completed"]
    if apparatus_error:
        terminal_state = "APPARATUS_ERROR"
    elif (
        all(checks.values())
        and parsed_response is not None
        and parsed_response["terminal_action"] == "ESCALATE"
    ):
        terminal_state = "ESCALATED"
    elif all(checks.values()) and parsed_response is not None:
        terminal_state = "PASS"
    else:
        terminal_state = "FAIL"

    evaluation = {
        "artifact": "local_model_qualification_t1_q1_mechanical_evaluation_v0",
        "artifact_class": "LOCAL_MODEL_QUALIFICATION_MECHANICAL_EVALUATION",
        "apparatus_version": APPARATUS_VERSION,
        "specimen_id": SPECIMEN_ID,
        "freeze_path": observation["freeze_path"],
        "observation_path": freeze["output_paths"]["observation"],
        "observation_sha256": _sha256_bytes(observation_path.read_bytes()),
        "mechanical_checks": checks,
        "parsed_response": parsed_response,
        "parse_failure": parse_failure,
        "terminal_state": terminal_state,
        "semantic_success": "NOT_EVALUATED",
        "qualification_promotion": "NOT_EVALUATED",
        "campaign_scope": freeze["campaign_scope"],
    }
    _write_new_json(output_path, evaluation)
    return evaluation


def execute_once(
    *,
    repo_root: Path,
    freeze_path: Path,
    observation_path: Path,
    mechanical_path: Path,
    execution_basis_commit: str,
    transport: Transport = _local_http_transport,
) -> dict[str, Any]:
    capture_observation(
        repo_root=repo_root,
        freeze_path=freeze_path,
        output_path=observation_path,
        execution_basis_commit=execution_basis_commit,
        transport=transport,
    )
    return mechanical_evaluation(
        observation_path=observation_path,
        freeze_path=freeze_path,
        output_path=mechanical_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute the frozen read-only T1-Q1 qualification once."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--execution-basis-commit", required=True)
    parser.add_argument("--freeze", default=str(DEFAULT_FREEZE_PATH))
    parser.add_argument("--observation-output", default=str(DEFAULT_OBSERVATION_PATH))
    parser.add_argument("--mechanical-output", default=str(DEFAULT_MECHANICAL_PATH))
    args = parser.parse_args()
    repo_root = Path(args.repo).resolve()
    result = execute_once(
        repo_root=repo_root,
        freeze_path=(repo_root / args.freeze).resolve(),
        observation_path=(repo_root / args.observation_output).resolve(),
        mechanical_path=(repo_root / args.mechanical_output).resolve(),
        execution_basis_commit=args.execution_basis_commit,
    )
    print(
        json.dumps(
            {
                "specimen_id": result["specimen_id"],
                "terminal_state": result["terminal_state"],
                "observation_path": args.observation_output,
                "mechanical_evaluation_path": args.mechanical_output,
                "semantic_evaluation": "NOT_PERFORMED",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["terminal_state"] in {"PASS", "ESCALATED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
