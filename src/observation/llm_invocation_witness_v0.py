"""Pure construction of one bounded raw LLM invocation witness.

The witness retains caller-supplied observation references.  It does not read
their targets, derive an Atlas frame, interpret model output, infer an external
effect, or persist anything.
"""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence


WITNESS_TYPE = "RAW_LLM_INVOCATION_WITNESS_V0"
UNRESOLVED = "UNRESOLVED"

TOOL_REQUEST = "TOOL_REQUEST"
TOOL_RESULT = "TOOL_RESULT"
MODEL_CLAIM_ABOUT_TOOL_RESULT = "MODEL_CLAIM_ABOUT_TOOL_RESULT"
TOOL_TRACE_KINDS = (
    TOOL_REQUEST,
    TOOL_RESULT,
    MODEL_CLAIM_ABOUT_TOOL_RESULT,
)

_TOOL_TRACE_KEYS = frozenset({"ordinal", "kind", "raw_ref"})


class InvocationWitnessInputError(ValueError):
    """A supplied value cannot form the bounded raw witness."""


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvocationWitnessInputError(f"{field} must be a non-empty string")
    return value


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, field)


def _text_list(values: Sequence[str], field: str, *, nonempty: bool = False) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise InvocationWitnessInputError(f"{field} must be a sequence of strings")
    retained = [
        _required_text(value, f"{field}[{index}]")
        for index, value in enumerate(values)
    ]
    if nonempty and not retained:
        raise InvocationWitnessInputError(f"{field} must not be empty")
    return retained


def _tool_trace_list(
    entries: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(entries, (str, bytes)) or not isinstance(entries, Sequence):
        raise InvocationWitnessInputError("tool_trace_refs must be a sequence")

    retained: list[dict[str, Any]] = []
    for expected_ordinal, entry in enumerate(entries, start=1):
        if not isinstance(entry, Mapping) or set(entry) != _TOOL_TRACE_KEYS:
            raise InvocationWitnessInputError(
                "each tool_trace_refs entry must contain exactly "
                "ordinal, kind, and raw_ref"
            )
        ordinal = entry["ordinal"]
        if isinstance(ordinal, bool) or ordinal != expected_ordinal:
            raise InvocationWitnessInputError(
                "tool_trace_refs ordinals must be contiguous and one-based"
            )
        kind = _required_text(entry["kind"], f"tool_trace_refs[{expected_ordinal}].kind")
        if kind not in TOOL_TRACE_KINDS:
            raise InvocationWitnessInputError(f"unsupported tool trace kind: {kind!r}")
        raw_ref = _required_text(
            entry["raw_ref"], f"tool_trace_refs[{expected_ordinal}].raw_ref"
        )
        retained.append({"ordinal": ordinal, "kind": kind, "raw_ref": raw_ref})
    return retained


def build_raw_invocation_witness(
    *,
    invocation_id: str,
    input_identity: str,
    raw_input_ref: str,
    adapter_identity: str,
    declared_basis_refs: Sequence[str],
    tool_trace_refs: Sequence[Mapping[str, Any]],
    raw_output_identity: str,
    raw_output_ref: str,
    external_crossing_refs: Sequence[str],
    observer_limitations: Sequence[str],
    model_identity: str | None = None,
    start_frame_ref: str | None = None,
    end_frame_ref: str | None = None,
) -> dict[str, Any]:
    """Return a deterministic, append-free witness from supplied observations.

    ``tool_trace_refs`` preserves three distinct raw boundary kinds.  An
    external effect is deliberately not an accepted assertion: references to
    observed crossings can be retained, while effect establishment remains
    unresolved in this witness.
    """

    retained_model_identity = _optional_text(model_identity, "model_identity")
    retained_start_frame_ref = _optional_text(start_frame_ref, "start_frame_ref")
    retained_end_frame_ref = _optional_text(end_frame_ref, "end_frame_ref")

    measured_fields = [
        "invocation_id",
        "input_identity",
        "raw_input_ref",
        "adapter_identity",
        "declared_basis_refs",
        "tool_trace_refs",
        "raw_output_identity",
        "raw_output_ref",
        "external_crossing_refs",
        "observer_limitations",
    ]
    unresolved_fields = ["tool_trace_completeness", "external_effect"]

    optional_fields = (
        ("model_identity", retained_model_identity),
        ("start_frame_ref", retained_start_frame_ref),
        ("end_frame_ref", retained_end_frame_ref),
    )
    for field, value in optional_fields:
        if value is None:
            unresolved_fields.append(field)
        else:
            measured_fields.append(field)

    witness = {
        "witness_type": WITNESS_TYPE,
        "invocation_id": _required_text(invocation_id, "invocation_id"),
        "input_identity": _required_text(input_identity, "input_identity"),
        "raw_input_ref": _required_text(raw_input_ref, "raw_input_ref"),
        "adapter_identity": _required_text(adapter_identity, "adapter_identity"),
        "model_identity": retained_model_identity or UNRESOLVED,
        "declared_basis_refs": _text_list(declared_basis_refs, "declared_basis_refs"),
        "tool_trace_refs": _tool_trace_list(tool_trace_refs),
        "raw_output_identity": _required_text(
            raw_output_identity, "raw_output_identity"
        ),
        "raw_output_ref": _required_text(raw_output_ref, "raw_output_ref"),
        "start_frame_ref": retained_start_frame_ref or UNRESOLVED,
        "end_frame_ref": retained_end_frame_ref or UNRESOLVED,
        "external_crossing_refs": _text_list(
            external_crossing_refs, "external_crossing_refs"
        ),
        "observer_limitations": _text_list(
            observer_limitations, "observer_limitations", nonempty=True
        ),
        "measured_fields": measured_fields,
        "derived_fields": [],
        "interpreted_fields": [],
        "unresolved_fields": unresolved_fields,
    }
    return copy.deepcopy(witness)
