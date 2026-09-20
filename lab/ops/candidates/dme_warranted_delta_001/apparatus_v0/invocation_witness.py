"""Invocation witness candidate for DME_WARRANTED_DELTA_001.

Bounded purpose:
- establish that one exact executor invocation crossed the harness boundary,
- bind that invocation to declared executor/transformation/input identities,
- bind an opaque result-state reference to the object returned by that call,
- avoid exposing post-state content through the provenance surface.

This module does not observe result-state coordinates and does not classify
delta conformance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping


class InvocationWitnessError(RuntimeError):
    pass


class IdentityMismatch(InvocationWitnessError):
    pass


class InvocationDidNotReturn(InvocationWitnessError):
    def __init__(self, entered_event: "ExecutionEntered", exception_type: str):
        super().__init__(f"invocation did not return: {exception_type}")
        self.entered_event = entered_event
        self.exception_type = exception_type


@dataclass(frozen=True)
class ExecutionEntered:
    realization_id: str
    invocation_id: str
    executor_identity: str
    transformation_identity: str
    input_state_identity: str
    event_type: str = "EXECUTION_ENTERED"


@dataclass(frozen=True)
class ExecutionReturned:
    realization_id: str
    invocation_id: str
    executor_identity: str
    transformation_identity: str
    input_state_identity: str
    result_state_ref: str
    event_type: str = "EXECUTION_RETURNED"


@dataclass(frozen=True)
class ExecutionProvenance:
    realization_id: str
    invocation_id: str
    executor_identity: str
    transformation_identity: str
    input_state_identity: str
    entered_event: ExecutionEntered
    returned_event: ExecutionReturned
    result_state_ref: str
    invocation_count: int


_CAPTURE_KEY = object()
_RESULT_BOUND = object()


class InvocationCapture:
    """Harness-sealed live capture.

    The public surface exposes provenance only. The returned object is retained
    privately so a later observer boundary can receive it without placing state
    content into execution provenance.
    """

    __slots__ = ("_provenance", "_result", "_seal", "_binding")

    def __init__(
        self,
        key: object,
        provenance: ExecutionProvenance,
        result: Any,
    ) -> None:
        if key is not _CAPTURE_KEY:
            raise TypeError("InvocationCapture is harness-created only")
        self._provenance = provenance
        self._result = result
        self._seal = _CAPTURE_KEY
        self._binding = _RESULT_BOUND

    @property
    def provenance(self) -> ExecutionProvenance:
        return self._provenance

    def _result_is_bound(self, expected_ref: str) -> bool:
        return (
            self._seal is _CAPTURE_KEY
            and self._binding is _RESULT_BOUND
            and self._provenance.result_state_ref == expected_ref
        )


class InvocationHarness:
    """Frozen-call-boundary candidate.

    The harness owns the executor callable and the transformation registry.
    Callers select a declared transformation identity; they do not supply an
    arbitrary executor callable to the invocation method.
    """

    def __init__(
        self,
        *,
        executor: Callable[[Callable[[Any], Any], Any], Any],
        executor_identity: str,
        transformations: Mapping[str, Callable[[Any], Any]],
    ) -> None:
        if not executor_identity:
            raise ValueError("executor_identity must be non-empty")
        if not transformations:
            raise ValueError("at least one transformation is required")
        self._executor = executor
        self._executor_identity = executor_identity
        self._transformations = dict(transformations)

    @property
    def executor_identity(self) -> str:
        return self._executor_identity

    def invoke_once(
        self,
        *,
        realization_id: str,
        invocation_id: str,
        transformation_identity: str,
        input_state: Any,
        input_state_identity: str,
    ) -> InvocationCapture:
        for label, value in (
            ("realization_id", realization_id),
            ("invocation_id", invocation_id),
            ("transformation_identity", transformation_identity),
            ("input_state_identity", input_state_identity),
        ):
            if not value:
                raise ValueError(f"{label} must be non-empty")

        try:
            transformation = self._transformations[transformation_identity]
        except KeyError as exc:
            raise IdentityMismatch("unknown transformation identity") from exc

        entered = ExecutionEntered(
            realization_id=realization_id,
            invocation_id=invocation_id,
            executor_identity=self._executor_identity,
            transformation_identity=transformation_identity,
            input_state_identity=input_state_identity,
        )

        try:
            result = self._executor(transformation, input_state)
        except BaseException as exc:
            raise InvocationDidNotReturn(entered, type(exc).__name__) from exc

        result_ref = f"{realization_id}:{invocation_id}:result:0"
        returned = ExecutionReturned(
            realization_id=realization_id,
            invocation_id=invocation_id,
            executor_identity=self._executor_identity,
            transformation_identity=transformation_identity,
            input_state_identity=input_state_identity,
            result_state_ref=result_ref,
        )
        provenance = ExecutionProvenance(
            realization_id=realization_id,
            invocation_id=invocation_id,
            executor_identity=self._executor_identity,
            transformation_identity=transformation_identity,
            input_state_identity=input_state_identity,
            entered_event=entered,
            returned_event=returned,
            result_state_ref=result_ref,
            invocation_count=1,
        )
        return InvocationCapture(_CAPTURE_KEY, provenance, result)


def validate_event_story(
    provenance: ExecutionProvenance,
    *,
    expected_executor_identity: str,
    expected_transformation_identity: str,
    expected_input_state_identity: str,
) -> bool:
    """Validate internal story consistency only.

    A structurally valid story is not proof that an invocation occurred.
    Invocation establishment additionally requires a live harness-sealed capture.
    """
    entered = provenance.entered_event
    returned = provenance.returned_event
    return all(
        (
            provenance.invocation_count == 1,
            entered.event_type == "EXECUTION_ENTERED",
            returned.event_type == "EXECUTION_RETURNED",
            provenance.realization_id == entered.realization_id == returned.realization_id,
            provenance.invocation_id == entered.invocation_id == returned.invocation_id,
            provenance.executor_identity
            == entered.executor_identity
            == returned.executor_identity
            == expected_executor_identity,
            provenance.transformation_identity
            == entered.transformation_identity
            == returned.transformation_identity
            == expected_transformation_identity,
            provenance.input_state_identity
            == entered.input_state_identity
            == returned.input_state_identity
            == expected_input_state_identity,
            provenance.result_state_ref == returned.result_state_ref,
        )
    )


def invocation_established(
    capture: InvocationCapture,
    *,
    expected_executor_identity: str,
    expected_transformation_identity: str,
    expected_input_state_identity: str,
) -> bool:
    if type(capture) is not InvocationCapture:
        return False
    provenance = capture.provenance
    if not validate_event_story(
        provenance,
        expected_executor_identity=expected_executor_identity,
        expected_transformation_identity=expected_transformation_identity,
        expected_input_state_identity=expected_input_state_identity,
    ):
        return False
    return capture._result_is_bound(provenance.result_state_ref)


def serialize_provenance(capture: InvocationCapture) -> dict[str, Any]:
    if type(capture) is not InvocationCapture:
        raise TypeError("live harness-sealed capture required")
    return asdict(capture.provenance)
