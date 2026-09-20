# LABBOIB Temporal Seat v0

## Status

```text
CANDIDATE TEMPORAL RE-ENTRY SEAT
NOT DURABLE MAIN STATE
NOT SCHEDULED
NO OCCUPANT BOUND
NO EXECUTION AUTHORITY
```

## Purpose

Materialize the smallest reconstructable LABBOIB seat that can be invoked
repeatedly across time without requiring a continuous model process and without
turning persistence into ambient execution authority.

The seat is a durable operational package, not a claim about consciousness or
persistent subjective identity.

```text
SEAT CONTINUITY
!=
MODEL CONTINUITY

MODEL INSTANCE
!=
SEAT

SCHEDULED RE-ENTRY
!=
CONTINUOUS PROCESS IDENTITY

PERSISTENT ATTENTION
!=
PERSISTENT EXECUTION AUTHORITY
```

## Four retained coordinates

LABBOIB v0 retains four independent surfaces:

```text
SEAT MANIFEST
→ role / allowed wake effects / forbidden effects

CONTINUITY CURSOR
→ events consumed through

WORKING STATE
→ campaign / frontier / unresolved task-local state

INBOX + OUTBOX
→ human / seat injections and emitted operational objects
```

None may substitute for another.

```text
CURSOR POSITION
!=
WORKING SEMANTIC STATE

MESSAGE DELIVERED
!=
MESSAGE ACCEPTED

OUTPUT EMITTED
!=
AUTHORITY CREATED
```

## Initial continuity coordinate

The candidate LABBOIB cursor is positioned:

```text
FROM_HEAD
through CE-000033
```

This coordinate is prospective from the seat installation boundary.

It deliberately does not claim that historical ChatGPT conversations were
imported into the continuity stream.

```text
HISTORICAL CHAT AVAILABLE
!=
HISTORICAL CHAT DURABLY INGESTED
```

Conversation-history farming remains a separate future ingestion pressure.

## Wake contract

The deterministic wake runtime is:

```text
tools/labboib_seat.py
```

One read-only wake performs:

```text
resolve requested Git ref to exact commit
→ load exact seat manifest
→ load exact LABBOIB cursor
→ load exact working state
→ load exact continuity stream
→ load exact LABBOIB inbox / outbox
→ verify coordinate consistency
→ derive unread continuity after cursor
→ derive pending injections after injection coordinate
→ emit temporal_seat_wake_v0
→ stop
```

The wake itself performs no acknowledgement or consequence.

```text
WAKE
!=
ACK

WAKE
!=
MODEL RESPONSE

WAKE
!=
GIT COMMIT

WAKE
!=
AUTHORITY

WAKE
!=
EXECUTION
```

A wake with `status = READY` means only that the durable seat basis is
mechanically reconstructable enough to present to an occupant. It does not
mean a scheduler is bound, an occupant exists, authority exists, or a
consequential operation is legal.

## Occupant boundary

The v0 manifest begins with:

```text
trigger.state:
UNBOUND

occupant.binding:
UNBOUND
```

A future cloud GPT-5.6 Sol invocation, local LM Studio model, Codex process, or
other compatible transformer may occupy the seat only through a separately
declared invocation binding.

Changing occupants does not itself change the seat's durable coordinates.

Model capability remains independent:

```text
SAME SEAT BASIS
!=
SAME REASONING CAPABILITY
```

## Allowed wake outputs

The wake contract exposes only these output classes:

```text
STATUS
HANDOFF
REVIEW_REQUEST
ACTION_REQUEST
WAKE_RECEIPT
```

Every `temporal_seat_output_v0` carries:

```text
authority_effect = NONE_BY_OUTPUT
execution_effect = NONE_BY_OUTPUT
```

An ACTION_REQUEST requests authority or consequence. It does not create it.

## Human injection boundary

The local helper can append typed LABBOIB injections:

```text
MESSAGE
PRIORITY
PACKET_REF
ACTION_REQUEST
AUTHORITY_OBJECT_REF
```

A normal message carries no authority.

An injection claiming authority must provide a separate `authority_ref`.
The presence of that reference still does not establish that the authority
object is valid; the future occupant must inspect the referenced durable basis
before relying on it.

```text
AUTHORITY REF PRESENT
!=
AUTHORITY VALID
```

## Stop conditions

A LABBOIB occupant must stop rather than improvise when:

```text
explicit human authority is required for consequence
required durable basis is missing / stale / malformed / contradictory
independent role judgment or review is required
requested effect exceeds manifest scope
continuity cannot be reconstructed from LABBOIB's own coordinate
```

## Scheduler boundary

The suit is scheduler-compatible but not scheduled by this candidate.

A future scheduler may trigger repeated wake invocations.

```text
SCHEDULE TRIGGER
→ WAKE

NOT:

SCHEDULE TRIGGER
→ EXECUTION AUTHORITY
```

The scheduler must not silently advance LABBOIB's continuity cursor merely
because a wake occurred.

## Local bus boundary

The inbox and outbox are intentionally file-backed JSONL probe surfaces.

They are not yet:

```text
concurrency-safe
multi-writer safe
real-time WebSocket transport
shared-room semantics
delivery acknowledgement
message-order consensus
authority transport
```

Those belong to the later chat-bus pressure.

## Current self-hosting campaign

The retained candidate working state carries:

```text
LABBOIB_SELF_HOSTING_001
```

with the bounded objective of materializing and pressuring this temporal seat.

The working state is task-local continuity, not universal Lab truth.

## Exact current artifacts

```text
continuity/seats/labboib.json
continuity/cursors/labboib.json
continuity/current_state/labboib_working_state_v0.json
continuity/queues/labboib/inbox.jsonl
continuity/queues/labboib/outbox.jsonl

tools/labboib_seat.py

schemas/temporal_seat_manifest_v0.schema.json
schemas/temporal_seat_working_state_v0.schema.json
schemas/temporal_seat_injection_v0.schema.json
schemas/temporal_seat_wake_v0.schema.json
schemas/temporal_seat_output_v0.schema.json

tests/runtime/test_labboib_temporal_seat.py
```

## Qualification ceiling

At initial candidate materialization:

```text
IMPLEMENTATION:
MATERIALIZED

TESTS:
MATERIALIZED

TEST EXECUTION:
NOT YET OBSERVED

SCHEMA / JSON STATIC SWEEP:
AVAILABLE

SCHEDULER:
UNBOUND

CLOUD OCCUPANT:
UNBOUND

MAIN INTEGRATION:
NONE

AUTHORITY:
NONE

EXTERNAL EXECUTION:
NONE
```

No later standing is inferred from this contract.
