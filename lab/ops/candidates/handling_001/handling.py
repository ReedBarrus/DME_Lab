"""Bounded explicit handling-claim surface for HANDLING_001."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from lab.ops.candidates.addressing_001.addressing import DurableWorkRecord

CLAIM_FOR_HANDLING = "CLAIM_FOR_HANDLING"
CLAIM_EVENT_FIELDS = {"claim_event_id", "event_type", "work_record_id"}


class HandlingClaimShapeError(ValueError):
    """Raised when a HANDLING_CLAIM_EVENT_v0 does not match the bounded shape."""


@dataclass(frozen=True, slots=True)
class HandlingClaimEvent:
    claim_event_id: str
    event_type: str
    work_record_id: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "HandlingClaimEvent":
        if not isinstance(value, Mapping) or set(value) != CLAIM_EVENT_FIELDS:
            raise HandlingClaimShapeError("unexpected handling-claim-event fields")
        for key in ("claim_event_id", "event_type", "work_record_id"):
            if not isinstance(value[key], str) or not value[key]:
                raise HandlingClaimShapeError(f"{key} must be a non-empty string")
        return cls(
            claim_event_id=value["claim_event_id"],
            event_type=value["event_type"],
            work_record_id=value["work_record_id"],
        )

    def as_mapping(self) -> dict[str, str]:
        return {
            "claim_event_id": self.claim_event_id,
            "event_type": self.event_type,
            "work_record_id": self.work_record_id,
        }


def corresponds(claim: HandlingClaimEvent, work: DurableWorkRecord) -> bool:
    """Exact bounded claim-event -> work-record correspondence."""
    return (
        claim.event_type == CLAIM_FOR_HANDLING
        and claim.work_record_id == work.record_id
    )


def work_claimed_for_handling(
    work: DurableWorkRecord,
    claim_events: Iterable[Mapping[str, Any]],
) -> bool:
    """True iff at least one valid corresponding explicit handling claim exists."""
    for raw_claim in claim_events:
        try:
            claim = HandlingClaimEvent.from_mapping(raw_claim)
        except HandlingClaimShapeError:
            continue
        if corresponds(claim, work):
            return True
    return False
