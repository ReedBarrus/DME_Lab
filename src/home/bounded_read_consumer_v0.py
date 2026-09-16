#!/usr/bin/env python3
"""Boring read-only consumer for the bounded Home agent bridge v0."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


UNKNOWN = "UNKNOWN_NOT_PROJECTED"
ENVELOPE_FIELDS = (
    "projection_kind",
    "authority",
    "generated_at",
    "relevant_source_revision",
    "semantic_freshness",
    "source_identity",
)
EVENT_FIELDS = (
    "event_id",
    "author",
    "origin",
    "target_actor",
    "created_at",
    "due_at",
    "kind",
    "raw_instruction",
    "context_refs",
    "commitment_id",
    "specification_id",
    "status",
    "triggered_at",
    "acknowledged_at",
    "due_grants_execution_authority",
    "reference_standing",
    "current_specification_id",
    "current_commitment_status",
    "current_applicability_requires_adjudication",
)
LINEAGE_FACTS_NOT_PROJECTED = (
    "commitment_specification_history",
    "amendment_kinds",
    "prior_specification_links",
    "historical_weekday_coordinates",
)


class ContractError(ValueError):
    """Projection did not satisfy the declared bounded consumer contract."""


def _envelope(packet: dict[str, Any], expected_kind: str) -> dict[str, Any]:
    missing = [name for name in ENVELOPE_FIELDS if name not in packet]
    if missing:
        raise ContractError(f"missing_envelope_fields:{','.join(missing)}")
    if packet["projection_kind"] != expected_kind:
        raise ContractError("unexpected_projection_kind")
    if packet["authority"] != "DERIVED_FROM_HOME":
        raise ContractError("unexpected_projection_authority")
    if not isinstance(packet["relevant_source_revision"], int):
        raise ContractError("invalid_relevant_source_revision")
    source = packet["source_identity"]
    if not isinstance(source, dict) or not all(
        name in source for name in ("system", "surface", "schema_version", "source_instance_id")
    ):
        raise ContractError("incomplete_source_identity")
    return {name: packet[name] for name in ENVELOPE_FIELDS}


def _projected_event(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("invalid_event_object")
    missing = [name for name in EVENT_FIELDS if name not in value]
    if missing:
        raise ContractError(f"missing_event_fields:{','.join(missing)}")
    return {name: value[name] for name in EVENT_FIELDS}


def consume_bridge(chat_now: dict[str, Any], due_events: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct only facts actually serialized by two bounded bridge packets."""
    chat_envelope = _envelope(chat_now, "CHAT_HOME_DERIVED_PROJECTION")
    due_envelope = _envelope(due_events, "DUE_AGENT_EVENTS_DERIVED_PROJECTION")
    for field in ("authority", "relevant_source_revision", "semantic_freshness", "source_identity"):
        if chat_envelope[field] != due_envelope[field]:
            raise ContractError(f"bridge_envelope_disagreement:{field}")

    candidates = []
    for value in chat_now.get("future_notes", []):
        candidates.append(_projected_event(value))
    for value in due_events.get("events", []):
        candidates.append(_projected_event(value))
    by_id: dict[str, dict[str, Any]] = {}
    for event in candidates:
        prior = by_id.get(event["event_id"])
        if prior is not None and prior != event:
            raise ContractError("conflicting_duplicate_event_projection")
        by_id[event["event_id"]] = event

    source = chat_envelope["source_identity"]
    events = [by_id[event_id] for event_id in sorted(by_id)]
    return {
        "consumer": "bounded_read_consumer_v0",
        "source_instance_id": source["source_instance_id"],
        "source_surface": source["surface"],
        "source_schema_version": source["schema_version"],
        "relevant_source_revision": chat_envelope["relevant_source_revision"],
        "projection_authority": chat_envelope["authority"],
        "semantic_freshness": chat_envelope["semantic_freshness"],
        "execution_authority_inferred": False,
        "execution_authority_projected": [
            {
                "event_id": event["event_id"],
                "due_grants_execution_authority": event["due_grants_execution_authority"],
            }
            for event in events
        ],
        "events": events,
        "commitment_lineage": UNKNOWN,
        "unknown_not_projected": list(LINEAGE_FACTS_NOT_PROJECTED),
        "incorrect_inferences": [],
    }


def read_packet(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError("projection_root_must_be_object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chat-now", type=Path, required=True)
    parser.add_argument("--due-events", type=Path, required=True)
    args = parser.parse_args()
    result = consume_bridge(read_packet(args.chat_now), read_packet(args.due_events))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
