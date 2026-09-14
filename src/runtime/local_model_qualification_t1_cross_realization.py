"""One-call-per-specimen T1 cross-realization qualification apparatus.

This module reuses the frozen Q1-Q3 policy-visible inputs and strict response
parsers.  It adds only an explicitly frozen realization, exact context
admission records, and a live local-runtime identity/configuration guard.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from copy import deepcopy
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from src.runtime.lm_studio_policy_adapter import (
    LMStudioEndpointConfig,
    Transport,
    _local_http_transport,
)
from src.runtime import local_model_qualification_t1_q1 as q1
from src.runtime import local_model_qualification_t1_q2 as q2
from src.runtime import local_model_qualification_t1_q3 as q3


APPARATUS_VERSION = "local_model_qualification_t1_cross_realization_v0"
DEFAULT_FREEZE_PATH = Path(
    "traces/local_model_qualification_t1_turbo_freeze_v0.json"
)
DEADLINE_PRESSURE_FREEZE_PATH = Path(
    "traces/local_model_qualification_t1_turbo_q1_deadline_pressure_freeze_v0.json"
)
COMPLETION_BUDGET_PRESSURE_FREEZE_PATH = Path(
    "traces/local_model_qualification_t1_turbo_q1_completion_budget_pressure_freeze_v0.json"
)
SPECIMEN_MODULES = {"Q1": q1, "Q2": q2, "Q3": q3}
FREEZE_AUTHORIZATIONS = {
    "local_model_qualification_t1_turbo_freeze_v0": ("Q1", "Q2", "Q3"),
    "local_model_qualification_t1_turbo_q1_deadline_pressure_freeze_v0": ("Q1",),
    "local_model_qualification_t1_turbo_q1_completion_budget_pressure_freeze_v0": ("Q1",),
}
RuntimeInspector = Callable[[str, float], Mapping[str, Any]]


def _local_runtime_inspector(endpoint: str, timeout_seconds: float) -> Mapping[str, Any]:
    request = Request(endpoint, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _load_freeze(path: Path) -> dict[str, Any]:
    freeze = json.loads(path.read_text(encoding="utf-8"))
    artifact = freeze.get("artifact")
    if artifact not in FREEZE_AUTHORIZATIONS:
        raise RuntimeError("unexpected cross-realization freeze artifact")
    if freeze.get("maximum_model_calls_per_specimen") != 1:
        raise RuntimeError("cross-realization freeze must permit one call per specimen")
    authorized = FREEZE_AUTHORIZATIONS[artifact]
    if tuple(freeze.get("authorized_specimens", ())) != authorized:
        raise RuntimeError("authorized specimen set does not match the freeze type")
    if set(freeze.get("specimens", {})) != set(authorized):
        raise RuntimeError("freeze contains an unauthorized specimen definition")
    if freeze.get("q4_authorized") is not False:
        raise RuntimeError("Q4 must remain held out")
    for key in authorized:
        module = SPECIMEN_MODULES[key]
        specimen = freeze["specimens"][key]
        if specimen["specimen_id"] != module.SPECIMEN_ID:
            raise RuntimeError(f"{key} specimen identity drift")
        if specimen["prompt_template_sha256"] != module.prompt_template_hash():
            raise RuntimeError(f"{key} prompt template drift")
        if specimen["response_schema_sha256"] != module.response_schema_hash():
            raise RuntimeError(f"{key} response schema drift")
        admission = specimen["context_admission"]
        if admission["reserved_output_tokens"] != freeze["realization"][
            "provider_exposed_sampling_settings"
        ]["max_tokens"]:
            raise RuntimeError(f"{key} output-reserve drift")
        if admission["total_required_tokens"] != (
            admission["rendered_input_tokens"]
            + admission["reserved_output_tokens"]
        ):
            raise RuntimeError(f"{key} admission arithmetic drift")
        if admission["admitted"] is not True:
            raise RuntimeError(f"{key} is not frozen as admitted")
    return freeze


def _historical_freeze(repo_root: Path, specimen: Mapping[str, Any]) -> dict[str, Any]:
    path = repo_root / specimen["historical_freeze_path"]
    freeze = json.loads(path.read_text(encoding="utf-8"))
    source = specimen["source_specimen"]
    if freeze["source_specimen"] != source:
        raise RuntimeError("historical source freeze drift")
    return freeze


def build_exact_policy_visible_input(
    *, repo_root: Path, cross_freeze: Mapping[str, Any], specimen_key: str
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    module = SPECIMEN_MODULES[specimen_key]
    specimen = cross_freeze["specimens"][specimen_key]
    historical = _historical_freeze(repo_root, specimen)
    source = specimen["source_specimen"]
    source_bytes = q1._read_committed_bytes(repo_root, source["commit"], source["path"])
    observed_source_hash = q1._sha256_bytes(source_bytes)
    if observed_source_hash != source["sha256"]:
        raise RuntimeError("committed source specimen does not match frozen hash")
    if specimen_key == "Q1":
        selected_packet: Any = source_bytes.decode("utf-8")
        observed_packet_hash = None
    else:
        selected_packet = module.build_source_packet(source_bytes)
        observed_packet_hash = module.source_packet_hash(selected_packet)
        if observed_packet_hash != source["selected_packet_sha256"]:
            raise RuntimeError("selected source packet does not match frozen hash")
    policy_input = module.build_policy_visible_input(historical, selected_packet)
    serialized = q1._canonical_json(policy_input)
    admission = specimen["context_admission"]
    if q1._sha256_bytes(serialized.encode("utf-8")) != admission[
        "serialized_policy_visible_input_sha256"
    ]:
        raise RuntimeError("serialized policy-visible request drift")
    if len(serialized.encode("utf-8")) != admission[
        "serialized_policy_visible_input_bytes"
    ]:
        raise RuntimeError("serialized policy-visible request size drift")
    return policy_input, serialized, {
        **deepcopy(source),
        "observed_sha256": observed_source_hash,
        "observed_selected_packet_sha256": observed_packet_hash,
    }


def _select_live_realization(
    freeze: Mapping[str, Any], runtime_payload: Mapping[str, Any]
) -> dict[str, Any]:
    realization = freeze["realization"]
    requested = realization["requested_model_identifier"]
    models = runtime_payload.get("models")
    if not isinstance(models, list):
        raise RuntimeError("LM Studio model inventory has no model list")
    matches = [item for item in models if item.get("key") == requested]
    if len(matches) != 1:
        raise RuntimeError("requested model is not uniquely exposed by LM Studio")
    model = matches[0]
    instances = [
        item for item in model.get("loaded_instances", [])
        if item.get("id") == realization["loaded_model_instance_identifier"]
    ]
    if len(instances) != 1:
        raise RuntimeError("frozen loaded model instance is not uniquely active")
    live_config = instances[0].get("config", {})
    expected_config = realization["loaded_instance_config"]
    if live_config != expected_config:
        raise RuntimeError("loaded model configuration drifted from the freeze")
    checks = {
        "provider_model_key": model.get("key") == requested,
        "provider_display_name": model.get("display_name") == realization["display_name"],
        "architecture": model.get("architecture") == realization["architecture"],
        "quantization": model.get("quantization") == realization["quantization"],
        "size_bytes": model.get("size_bytes") == realization["size_bytes"],
        "params_string": model.get("params_string") == realization["params_string"],
        "format": model.get("format") == realization["format"],
        "maximum_supported_context": model.get("max_context_length")
        == realization["model_supported_maximum_context"],
    }
    if not all(checks.values()):
        failed = [key for key, value in checks.items() if not value]
        raise RuntimeError("live realization identity drift: " + ", ".join(failed))
    return deepcopy(model)


def _build_http_body(
    *, module: Any, realization: Mapping[str, Any], serialized_input: str
) -> dict[str, Any]:
    return {
        "messages": [{"role": "user", "content": serialized_input}],
        "model": realization["requested_model_identifier"],
        **deepcopy(realization["provider_exposed_sampling_settings"]),
        "response_format": module.response_format(),
        "stream": False,
    }


def capture_observation(
    *,
    repo_root: Path,
    freeze_path: Path,
    specimen_key: str,
    output_path: Path,
    execution_basis_commit: str,
    transport: Transport = _local_http_transport,
    runtime_inspector: RuntimeInspector = _local_runtime_inspector,
) -> dict[str, Any]:
    """Make exactly one fresh request after all local pre-call guards pass."""

    if specimen_key not in SPECIMEN_MODULES:
        raise RuntimeError("specimen must be Q1, Q2, or Q3")
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite one-shot observation: {output_path}")
    resolved_execution_basis = q1._resolve_commit(repo_root, execution_basis_commit)
    current_head = q1._resolve_commit(repo_root, "HEAD")
    if resolved_execution_basis != current_head:
        raise RuntimeError("execution-basis commit must resolve to committed HEAD")
    freeze = _load_freeze(freeze_path)
    specimen = freeze["specimens"][specimen_key]
    module = SPECIMEN_MODULES[specimen_key]
    policy_input, serialized_input, source_observation = build_exact_policy_visible_input(
        repo_root=repo_root, cross_freeze=freeze, specimen_key=specimen_key
    )

    realization = freeze["realization"]
    runtime_payload = runtime_inspector(
        realization["runtime_model_inventory_endpoint"],
        realization["timeout_seconds"],
    )
    live_model = _select_live_realization(freeze, runtime_payload)
    admission = specimen["context_admission"]
    context_length = live_model["loaded_instances"][0]["config"]["context_length"]
    if admission["total_required_tokens"] > context_length:
        raise RuntimeError("specimen is not admissible under the live context")

    body = _build_http_body(
        module=module, realization=realization, serialized_input=serialized_input
    )
    serialized_http = q1._canonical_json(body)
    endpoint_config = LMStudioEndpointConfig(
        endpoint=realization["endpoint"],
        model_identifier=realization["requested_model_identifier"],
        sampling_settings=realization["provider_exposed_sampling_settings"],
        timeout_seconds=realization["timeout_seconds"],
    )
    protected_surfaces = list(freeze["protected_surfaces"])
    status_before = q1._git_status(repo_root)
    protected_before = q1._protected_manifest(repo_root, protected_surfaces)
    started_at = q1._utc_now()

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
            {"Content-Type": "application/json"},
            endpoint_config.timeout_seconds,
        )
        if not 200 <= http_status < 300:
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

    finished_at = q1._utc_now()
    protected_after = q1._protected_manifest(repo_root, protected_surfaces)
    status_after = q1._git_status(repo_root)
    observation = {
        "artifact": specimen.get(
            "observation_artifact",
            f"local_model_qualification_t1_turbo_{specimen_key.lower()}_observation_v0",
        ),
        "artifact_class": "LOCAL_MODEL_QUALIFICATION_RUN_OBSERVATION",
        "apparatus_version": APPARATUS_VERSION,
        "specimen_key": specimen_key,
        "specimen_id": specimen["specimen_id"],
        "freeze_path": freeze_path.relative_to(repo_root).as_posix(),
        "execution_basis": {
            "argument": execution_basis_commit,
            "resolved_commit": resolved_execution_basis,
            "head_at_preflight": current_head,
            "valid": True,
        },
        "source_specimen": source_observation,
        "realization": {
            **deepcopy(realization),
            "provider_reported_model": provider_reported_model,
            "provider_system_fingerprint": provider_system_fingerprint,
            "provider_usage": provider_usage,
            "live_model_inventory_record": live_model,
        },
        "context_admission": deepcopy(admission),
        "declared_interface": {
            "prompt_template_identity": module.PROMPT_TEMPLATE["identity"],
            "prompt_template_sha256": module.prompt_template_hash(),
            "response_schema": module.response_format(),
            "response_schema_sha256": module.response_schema_hash(),
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
        "automatic_retries": 0,
        "repository_observation": {
            "status_before_inference": status_before,
            "status_after_inference": status_after,
            "protected_manifest_before": protected_before,
            "protected_manifest_after": protected_after,
        },
        "leakage_observation": deepcopy(specimen["leakage_boundary"]),
        "run_timing": {"started_at_utc": started_at, "finished_at_utc": finished_at},
        "semantic_evaluation": "NOT_PERFORMED_IN_OBSERVATION",
    }
    q1._write_new_json(output_path, observation)
    return observation


def mechanical_evaluation(
    *, observation_path: Path, freeze_path: Path, output_path: Path
) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite mechanical evaluation: {output_path}")
    freeze = _load_freeze(freeze_path)
    observation = json.loads(observation_path.read_text(encoding="utf-8"))
    specimen_key = observation["specimen_key"]
    specimen = freeze["specimens"][specimen_key]
    module = SPECIMEN_MODULES[specimen_key]
    raw = observation.get("raw_model_response")
    parsed = None
    parse_failure = None
    try:
        parsed = module.parse_response(raw)
    except Exception as exc:
        parse_failure = f"{type(exc).__name__}: {exc}"
    try:
        request = json.loads(observation["serialized_http_request"])
        request_reconstructs = (
            set(request) == q1.HTTP_BODY_FIELDS
            and request["messages"] == [{
                "role": "user",
                "content": observation["serialized_policy_visible_input"],
            }]
            and request["response_format"] == module.response_format()
            and "tools" not in request
            and "previous_response_id" not in request
        )
    except Exception:
        request_reconstructs = False
    try:
        provider = json.loads(observation["raw_response_body"])
        response_reconstructs = provider["choices"][0]["message"]["content"] == raw
    except Exception:
        response_reconstructs = False
    checks = {
        "inference_completed": (
            observation.get("adapter_failure") is None
            and isinstance(observation.get("http_status"), int)
            and 200 <= observation["http_status"] < 300
            and isinstance(raw, str)
        ),
        "exactly_one_call": observation.get("model_calls_made") == 1,
        "no_automatic_retry": observation.get("automatic_retries") == 0,
        "declared_response_shape_satisfied": parsed is not None,
        "raw_interaction_retained_and_reconstructable": (
            observation_path.exists() and request_reconstructs and response_reconstructs
        ),
        "source_basis_matched": observation["source_specimen"]["sha256"]
        == observation["source_specimen"]["observed_sha256"],
        "protected_surfaces_unchanged": (
            observation["repository_observation"]["protected_manifest_before"]
            == observation["repository_observation"]["protected_manifest_after"]
            and observation["repository_observation"]["status_before_inference"]
            == observation["repository_observation"]["status_after_inference"]
        ),
        "execution_basis_valid": (
            observation["execution_basis"]["valid"] is True
            and observation["execution_basis"]["resolved_commit"]
            == observation["execution_basis"]["head_at_preflight"]
        ),
        "context_admitted_before_call": (
            observation["context_admission"]["admitted"] is True
            and observation["context_admission"]["total_required_tokens"]
            <= observation["realization"]["loaded_instance_config"]["context_length"]
        ),
        "fresh_context_and_no_authority": (
            observation["declared_interface"]["message_count"] == 1
            and not observation["declared_interface"]["conversation_state_supplied"]
            and observation["declared_interface"]["model_tool_surface"] == []
            and observation["declared_interface"]["mcp_surface"] == []
            and not observation["declared_interface"]["repository_access_supplied_to_model"]
            and not observation["declared_interface"]["filesystem_access_supplied_to_model"]
        ),
        "provider_reported_termination": observation.get("finish_reason") == "stop",
        "terminal_action_valid": parsed is not None
        and parsed["terminal_action"] in module.TERMINAL_ACTIONS,
        "observation_and_evaluation_separate": (
            observation.get("semantic_evaluation") == "NOT_PERFORMED_IN_OBSERVATION"
            and "parsed_response" not in observation
        ),
    }
    if not checks["inference_completed"]:
        terminal_state = "APPARATUS_ERROR"
    elif all(checks.values()) and parsed is not None:
        terminal_state = "ESCALATED" if parsed["terminal_action"] == "ESCALATE" else "PASS"
    else:
        terminal_state = "FAIL"
    evaluation = {
        "artifact": specimen.get(
            "mechanical_evaluation_artifact",
            f"local_model_qualification_t1_turbo_{specimen_key.lower()}_mechanical_evaluation_v0",
        ),
        "artifact_class": "LOCAL_MODEL_QUALIFICATION_MECHANICAL_EVALUATION",
        "apparatus_version": APPARATUS_VERSION,
        "specimen_key": specimen_key,
        "specimen_id": specimen["specimen_id"],
        "freeze_path": observation["freeze_path"],
        "observation_path": specimen["output_paths"]["observation"],
        "observation_sha256": q1._sha256_bytes(observation_path.read_bytes()),
        "mechanical_checks": checks,
        "parsed_response": parsed,
        "parse_failure": parse_failure,
        "terminal_state": terminal_state,
        "semantic_success": "NOT_EVALUATED",
        "qualification_promotion": "NOT_EVALUATED",
    }
    q1._write_new_json(output_path, evaluation)
    return evaluation


def execute_once(
    *,
    repo_root: Path,
    freeze_path: Path,
    specimen_key: str,
    observation_path: Path,
    mechanical_path: Path,
    execution_basis_commit: str,
    transport: Transport = _local_http_transport,
    runtime_inspector: RuntimeInspector = _local_runtime_inspector,
) -> dict[str, Any]:
    capture_observation(
        repo_root=repo_root,
        freeze_path=freeze_path,
        specimen_key=specimen_key,
        output_path=observation_path,
        execution_basis_commit=execution_basis_commit,
        transport=transport,
        runtime_inspector=runtime_inspector,
    )
    return mechanical_evaluation(
        observation_path=observation_path,
        freeze_path=freeze_path,
        output_path=mechanical_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute one frozen Turbo T1 specimen.")
    parser.add_argument("specimen", choices=tuple(SPECIMEN_MODULES))
    parser.add_argument("--repo", default=".")
    parser.add_argument("--execution-basis-commit", required=True)
    parser.add_argument("--freeze", default=str(DEFAULT_FREEZE_PATH))
    args = parser.parse_args()
    repo_root = Path(args.repo).resolve()
    freeze_path = (repo_root / args.freeze).resolve()
    freeze = _load_freeze(freeze_path)
    outputs = freeze["specimens"][args.specimen]["output_paths"]
    result = execute_once(
        repo_root=repo_root,
        freeze_path=freeze_path,
        specimen_key=args.specimen,
        observation_path=repo_root / outputs["observation"],
        mechanical_path=repo_root / outputs["mechanical_evaluation"],
        execution_basis_commit=args.execution_basis_commit,
    )
    print(json.dumps({
        "specimen": args.specimen,
        "terminal_state": result["terminal_state"],
        "semantic_evaluation": "NOT_PERFORMED",
    }, indent=2, sort_keys=True))
    return 0 if result["terminal_state"] in {"PASS", "ESCALATED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
