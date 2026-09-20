"""Durable causal invocation witness candidate for DME_WARRANTED_DELTA_001.

Bounded purpose:
- make invocation completion durably verifiable after the live root is gone,
- require witness-root participation on the actual call/return path,
- keep post-state content out of the durable witness surface.

Threat-model assumption for this candidate:
- caller may supply requests, construct arbitrary receipt bytes, replay old bytes,
  and read the public key + journal;
- caller may not read witness-root private key material, mutate witness-root code,
  or invoke non-public witness-root internals.

This module does not establish that those isolation assumptions hold in a final
runtime. It only qualifies behavior within that declared boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


SCHEMA_VERSION = "dme_durable_invocation_witness_v0"
ESTABLISHED = "ESTABLISHED"
NOT_ESTABLISHED = "NOT_ESTABLISHED"


class DurableWitnessError(RuntimeError):
    pass


class IdentityMismatch(DurableWitnessError):
    pass


class InvocationDidNotReturn(DurableWitnessError):
    pass


@dataclass(frozen=True)
class DurableInvocationCapture:
    realization_id: str
    invocation_id: str
    result_state_ref: str
    _result: Any


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str
    result_state_ref: str | None = None


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def public_key_id(public_key_bytes: bytes) -> str:
    return hashlib.sha256(public_key_bytes).hexdigest()


def _result_ref(
    *,
    realization_id: str,
    invocation_id: str,
    executor_identity: str,
    transformation_identity: str,
    input_state_identity: str,
) -> str:
    # This handle is derived only from invocation metadata, never result content.
    material = canonical_json(
        {
            "realization_id": realization_id,
            "invocation_id": invocation_id,
            "executor_identity": executor_identity,
            "transformation_identity": transformation_identity,
            "input_state_identity": input_state_identity,
            "slot": "result:0",
        }
    )
    return f"urn:dme:result:{hashlib.sha256(material).hexdigest()}"


class DurableWitnessRoot:
    """Witness-root candidate that mediates the only accepted completion path.

    The caller does not supply an executor callable or transformation callable to
    `mediate_once`. Those are root-owned registrations fixed at construction.

    A signed ENTERED event is durably appended before the executor call.
    A signed RETURNED event is durably appended only after that same call returns.
    """

    __slots__ = (
        "__private_key",
        "__journal_path",
        "__executor",
        "__executor_identity",
        "__transformations",
        "__public_key_bytes",
        "__public_key_id",
    )

    def __init__(
        self,
        *,
        private_key: Ed25519PrivateKey,
        journal_path: Path,
        executor: Callable[[Callable[[Any], Any], Any], Any],
        executor_identity: str,
        transformations: Mapping[str, Callable[[Any], Any]],
    ) -> None:
        if not executor_identity:
            raise ValueError("executor_identity must be non-empty")
        if not transformations:
            raise ValueError("at least one transformation is required")
        self.__private_key = private_key
        self.__journal_path = Path(journal_path)
        self.__executor = executor
        self.__executor_identity = executor_identity
        self.__transformations = dict(transformations)
        self.__public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.__public_key_id = public_key_id(self.__public_key_bytes)

    @classmethod
    def fresh(
        cls,
        *,
        journal_path: Path,
        executor: Callable[[Callable[[Any], Any], Any], Any],
        executor_identity: str,
        transformations: Mapping[str, Callable[[Any], Any]],
    ) -> "DurableWitnessRoot":
        return cls(
            private_key=Ed25519PrivateKey.generate(),
            journal_path=journal_path,
            executor=executor,
            executor_identity=executor_identity,
            transformations=transformations,
        )

    @property
    def public_key_bytes(self) -> bytes:
        return self.__public_key_bytes

    @property
    def witness_key_id(self) -> str:
        return self.__public_key_id

    def __append_signed_event(self, payload: dict[str, Any]) -> None:
        envelope = {
            "payload": payload,
            "signature_hex": self.__private_key.sign(canonical_json(payload)).hex(),
        }
        self.__journal_path.parent.mkdir(parents=True, exist_ok=True)
        with self.__journal_path.open("ab") as fh:
            fh.write(canonical_json(envelope) + b"\n")
            fh.flush()
            os.fsync(fh.fileno())

    def mediate_once(
        self,
        *,
        realization_id: str,
        invocation_id: str,
        transformation_identity: str,
        input_state: Any,
        input_state_identity: str,
    ) -> DurableInvocationCapture:
        for label, value in (
            ("realization_id", realization_id),
            ("invocation_id", invocation_id),
            ("transformation_identity", transformation_identity),
            ("input_state_identity", input_state_identity),
        ):
            if not value:
                raise ValueError(f"{label} must be non-empty")

        try:
            transformation = self.__transformations[transformation_identity]
        except KeyError as exc:
            raise IdentityMismatch("unknown transformation identity") from exc

        base = {
            "schema_version": SCHEMA_VERSION,
            "witness_key_id": self.__public_key_id,
            "realization_id": realization_id,
            "invocation_id": invocation_id,
            "executor_identity": self.__executor_identity,
            "transformation_identity": transformation_identity,
            "input_state_identity": input_state_identity,
        }
        entered = {
            **base,
            "event_type": "EXECUTION_ENTERED",
            "sequence": 1,
        }
        self.__append_signed_event(entered)

        try:
            result = self.__executor(transformation, input_state)
        except BaseException as exc:
            raise InvocationDidNotReturn(type(exc).__name__) from exc

        result_state_ref = _result_ref(
            realization_id=realization_id,
            invocation_id=invocation_id,
            executor_identity=self.__executor_identity,
            transformation_identity=transformation_identity,
            input_state_identity=input_state_identity,
        )
        returned = {
            **base,
            "event_type": "EXECUTION_RETURNED",
            "sequence": 2,
            "result_state_ref": result_state_ref,
        }
        self.__append_signed_event(returned)

        return DurableInvocationCapture(
            realization_id=realization_id,
            invocation_id=invocation_id,
            result_state_ref=result_state_ref,
            _result=result,
        )


def _load_envelopes(journal_bytes: bytes) -> list[dict[str, Any]]:
    lines = [line for line in journal_bytes.splitlines() if line.strip()]
    out: list[dict[str, Any]] = []
    for raw in lines:
        value = json.loads(raw)
        if set(value) != {"payload", "signature_hex"}:
            raise ValueError("unexpected witness envelope shape")
        if not isinstance(value["payload"], dict):
            raise ValueError("payload must be an object")
        if not isinstance(value["signature_hex"], str):
            raise ValueError("signature_hex must be a string")
        out.append(value)
    return out


def verify_durable_invocation(
    journal_bytes: bytes,
    *,
    public_key_bytes: bytes,
    expected_realization_id: str,
    expected_invocation_id: str,
    expected_executor_identity: str,
    expected_transformation_identity: str,
    expected_input_state_identity: str,
) -> VerificationResult:
    """Verify durable completion without inspecting any result-state content."""
    try:
        envelopes = _load_envelopes(journal_bytes)
    except (ValueError, json.JSONDecodeError):
        return VerificationResult(NOT_ESTABLISHED, "MALFORMED_JOURNAL")

    if len(envelopes) != 2:
        return VerificationResult(NOT_ESTABLISHED, "REQUIRES_EXACT_ENTER_RETURN_PAIR")

    try:
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
    except ValueError:
        return VerificationResult(NOT_ESTABLISHED, "INVALID_PUBLIC_KEY")

    key_id = public_key_id(public_key_bytes)
    payloads: list[dict[str, Any]] = []
    for envelope in envelopes:
        payload = envelope["payload"]
        try:
            signature = bytes.fromhex(envelope["signature_hex"])
            public_key.verify(signature, canonical_json(payload))
        except (ValueError, InvalidSignature):
            return VerificationResult(NOT_ESTABLISHED, "INVALID_SIGNATURE")
        payloads.append(payload)

    entered, returned = payloads
    shared_expected = {
        "schema_version": SCHEMA_VERSION,
        "witness_key_id": key_id,
        "realization_id": expected_realization_id,
        "invocation_id": expected_invocation_id,
        "executor_identity": expected_executor_identity,
        "transformation_identity": expected_transformation_identity,
        "input_state_identity": expected_input_state_identity,
    }

    for key, value in shared_expected.items():
        if entered.get(key) != value or returned.get(key) != value:
            return VerificationResult(NOT_ESTABLISHED, f"IDENTITY_MISMATCH:{key}")

    if entered.get("event_type") != "EXECUTION_ENTERED" or entered.get("sequence") != 1:
        return VerificationResult(NOT_ESTABLISHED, "INVALID_ENTERED_EVENT")
    if returned.get("event_type") != "EXECUTION_RETURNED" or returned.get("sequence") != 2:
        return VerificationResult(NOT_ESTABLISHED, "INVALID_RETURNED_EVENT")

    expected_ref = _result_ref(
        realization_id=expected_realization_id,
        invocation_id=expected_invocation_id,
        executor_identity=expected_executor_identity,
        transformation_identity=expected_transformation_identity,
        input_state_identity=expected_input_state_identity,
    )
    if returned.get("result_state_ref") != expected_ref:
        return VerificationResult(NOT_ESTABLISHED, "RESULT_REF_MISMATCH")

    allowed_enter = set(shared_expected) | {"event_type", "sequence"}
    allowed_return = allowed_enter | {"result_state_ref"}
    if set(entered) != allowed_enter or set(returned) != allowed_return:
        return VerificationResult(NOT_ESTABLISHED, "UNEXPECTED_EVENT_FIELDS")

    return VerificationResult(ESTABLISHED, "SIGNED_CAUSAL_PAIR", expected_ref)
