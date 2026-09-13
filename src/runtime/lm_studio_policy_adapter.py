"""Stateless local LM Studio policy adapter for the frozen feedback experiment.

The adapter sends only the fixed task, current episode's policy-visible
protocol history, and terminal action vocabulary.  It retains call evidence in
memory for a caller to persist separately from the frozen world trace.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
import ipaddress
import json
from types import MappingProxyType
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from src.runtime.bounded_consequential_feedback_experiment import TERMINAL_ACTIONS


DEFAULT_ENDPOINT = "http://127.0.0.1:1234/v1/chat/completions"
ALLOWED_SAMPLING_SETTINGS = frozenset(
    {
        "frequency_penalty",
        "max_tokens",
        "min_p",
        "presence_penalty",
        "repeat_penalty",
        "seed",
        "stop",
        "temperature",
        "top_k",
        "top_p",
    }
)
FORBIDDEN_REQUEST_FIELDS = frozenset(
    {
        "conversation",
        "input",
        "integrations",
        "messages",
        "model",
        "previous_response_id",
        "stream",
        "tool_choice",
        "tools",
    }
)

Transport = Callable[[str, bytes, Mapping[str, str], float], tuple[int, str]]


class LMStudioAdapterError(RuntimeError):
    """Raised when the local adapter boundary or response is invalid."""


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        raise LMStudioAdapterError(
            f"LM Studio endpoint redirect rejected ({code})"
        )


def _validate_local_endpoint(endpoint: str) -> None:
    parsed = urlsplit(endpoint)
    if parsed.scheme != "http":
        raise ValueError("LM Studio endpoint must use http on an IP loopback address")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("LM Studio endpoint must not embed credentials")
    if parsed.query or parsed.fragment:
        raise ValueError("LM Studio endpoint must not contain query or fragment data")
    if parsed.path.rstrip("/") != "/v1/chat/completions":
        raise ValueError("LM Studio endpoint must target /v1/chat/completions")
    try:
        address = ipaddress.ip_address(parsed.hostname or "")
    except ValueError as exc:
        raise ValueError("LM Studio endpoint host must be an IP loopback address") from exc
    if not address.is_loopback:
        raise ValueError("LM Studio endpoint must remain on the loopback interface")


def _validate_sampling_settings(settings: Mapping[str, Any]) -> dict[str, Any]:
    copied = deepcopy(dict(settings))
    unknown = set(copied) - ALLOWED_SAMPLING_SETTINGS
    if unknown:
        raise ValueError(f"unsupported sampling settings: {sorted(unknown)}")
    forbidden = set(copied) & FORBIDDEN_REQUEST_FIELDS
    if forbidden:
        raise ValueError(f"forbidden request fields: {sorted(forbidden)}")
    try:
        json.dumps(copied, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("sampling settings must be finite JSON values") from exc
    return copied


@dataclass(frozen=True)
class LMStudioEndpointConfig:
    endpoint: str
    model_identifier: str
    sampling_settings: Mapping[str, Any]
    timeout_seconds: float = 120.0
    api_token: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        _validate_local_endpoint(self.endpoint)
        if not self.model_identifier.strip():
            raise ValueError("model identifier must be non-empty")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        object.__setattr__(
            self,
            "sampling_settings",
            MappingProxyType(_validate_sampling_settings(self.sampling_settings)),
        )

    def public_record(self) -> dict[str, Any]:
        parsed = urlsplit(self.endpoint)
        return {
            "endpoint": self.endpoint,
            "scheme": parsed.scheme,
            "host": parsed.hostname,
            "port": parsed.port,
            "path": parsed.path,
            "loopback_only": True,
            "redirects_allowed": False,
            "environment_proxies_allowed": False,
            "authentication_configured": self.api_token is not None,
            "timeout_seconds": self.timeout_seconds,
        }


class LMStudioPolicyAdapter:
    """Callable policy implementation with one stateless HTTP request per call."""

    def __init__(
        self,
        config: LMStudioEndpointConfig,
        *,
        transport: Transport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or _local_http_transport
        self._call_records: list[dict[str, Any]] = []

    @property
    def call_records(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._call_records))

    def serialize_policy_visible_request(
        self,
        fixed_task: str,
        policy_visible_protocol_history: tuple[dict[str, Any], ...],
    ) -> str:
        visible = {
            "fixed_task": fixed_task,
            "policy_visible_protocol_history": deepcopy(
                list(policy_visible_protocol_history)
            ),
            "legal_action_vocabulary": list(TERMINAL_ACTIONS),
        }
        try:
            return json.dumps(
                visible,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise LMStudioAdapterError(
                "policy-visible input must be finite JSON data"
            ) from exc

    def __call__(
        self,
        fixed_task: str,
        policy_visible_protocol_history: tuple[dict[str, Any], ...],
    ) -> str:
        serialized_visible = self.serialize_policy_visible_request(
            fixed_task,
            policy_visible_protocol_history,
        )
        body = {
            "messages": [{"role": "user", "content": serialized_visible}],
            "model": self._config.model_identifier,
            **deepcopy(dict(self._config.sampling_settings)),
            "stream": False,
        }
        serialized_http = json.dumps(
            body,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
        headers = {"Content-Type": "application/json"}
        if self._config.api_token is not None:
            headers["Authorization"] = f"Bearer {self._config.api_token}"

        base_record = {
            "endpoint_configuration": self._config.public_record(),
            "model_identifier": self._config.model_identifier,
            "provider_exposed_sampling_settings": deepcopy(
                dict(self._config.sampling_settings)
            ),
            "serialized_policy_visible_request": serialized_visible,
            "serialized_http_request": serialized_http,
            "conversation_state_supplied": False,
            "tools_supplied": False,
        }
        try:
            status, raw_response_body = self._transport(
                self._config.endpoint,
                serialized_http.encode("utf-8"),
                headers,
                self._config.timeout_seconds,
            )
            if status < 200 or status >= 300:
                raise LMStudioAdapterError(
                    f"LM Studio returned HTTP status {status}"
                )
            response = json.loads(raw_response_body)
            raw_model_response = response["choices"][0]["message"]["content"]
            if not isinstance(raw_model_response, str):
                raise TypeError("model response content is not a string")
        except Exception as exc:
            failed_record = {
                **base_record,
                "http_status": locals().get("status"),
                "raw_response_body": locals().get("raw_response_body"),
                "raw_model_response": None,
                "parsed_requested_action": None,
                "adapter_failure": f"{type(exc).__name__}: {exc}",
            }
            self._call_records.append(failed_record)
            if isinstance(exc, LMStudioAdapterError):
                raise
            raise LMStudioAdapterError("invalid LM Studio inference response") from exc

        parsed_requested_action = (
            raw_model_response if raw_model_response in TERMINAL_ACTIONS else None
        )
        self._call_records.append(
            {
                **base_record,
                "http_status": status,
                "raw_response_body": raw_response_body,
                "raw_model_response": raw_model_response,
                "parsed_requested_action": parsed_requested_action,
                "adapter_failure": None,
            }
        )
        # Return the raw content. The existing world remains the sole strict
        # action acceptance boundary and will not repair prose or whitespace.
        return raw_model_response


def _local_http_transport(
    endpoint: str,
    body: bytes,
    headers: Mapping[str, str],
    timeout_seconds: float,
) -> tuple[int, str]:
    _validate_local_endpoint(endpoint)
    opener = build_opener(ProxyHandler({}), _RejectRedirects())
    request = Request(
        endpoint,
        data=body,
        headers=dict(headers),
        method="POST",
    )
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        raise LMStudioAdapterError(
            f"LM Studio HTTP error {exc.code}: {response_body}"
        ) from exc
    except URLError as exc:
        raise LMStudioAdapterError(f"LM Studio connection failed: {exc.reason}") from exc
