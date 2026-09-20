# Continuity Delta v0

Purpose: reduce cross-invocation reconstruction by preserving a small durable activity stream that consumers read as deltas from their own last-seen coordinate.

This is not project authority, semantic adjudication, a global memory object, or a replacement for repository evidence.

## Core contract

```text
activity occurs
-> append a continuity event
-> fresh consumer explicitly bootstraps a stream coordinate
-> consumer reads events after its cursor
-> consumer follows authoritative refs only when the current task depends on them
-> consumer performs work
-> consumer appends consequential activity
-> consumer advances its cursor after consumption
```

Continuity transports recorded claims about activity. It does not adjudicate them.

```text
ACTIVITY_RECORDED
!=
ARTIFACT_EXISTS
!=
RESULT_VERIFIED
!=
STANDING_CHANGED
!=
FRONTIER_CHANGED
```

`reported_standing_delta` and `reported_frontier_delta` are reports by the event producer. They are not authoritative mutations merely because they appear here.

## Durable files

- `events.jsonl` — append-only continuity events.
- `cursors/<consumer>.json` — consumer-relative last-seen event coordinate.
- `registry.json` — identity and reference records for exactly `chatgpt-main` and
  `codex-main`; it is not a second cursor store.
- `tools/continuity.py` — minimal local CLI for reading deltas, appending activity, and advancing a cursor.

The initial consumers are `codex`, `chatgpt`, and `grep-kitty`.

## Local CLI

From the repository root:

```text
python tools/continuity.py delta --consumer codex
python tools/continuity.py delta --consumer grep-kitty
python tools/continuity.py registry
```

An uninitialized consumer receives `BOOTSTRAP_REQUIRED`, the current stream
head, and the legal modes instead of ordinary unread events. Establish exactly
one initial coordinate explicitly:

```text
python tools/continuity.py bootstrap --consumer codex --mode FROM_ORIGIN
python tools/continuity.py bootstrap --consumer codex --mode FROM_HEAD
python tools/continuity.py bootstrap --consumer codex --mode AFTER_EVENT --event-id CE-000001
```

`FROM_ORIGIN` grants navigation from the beginning of the retained stream.
`FROM_HEAD` positions at the current head, so only later appended events qualify
as delta. `AFTER_EVENT` positions after one named retained event. An unknown
event ID is rejected without changing the cursor.

Append one recorded activity event:

```text
python tools/continuity.py append \
  --actor codex \
  --surface vscode-cli \
  --kind EXECUTION_RESULT \
  --summary "bounded task completed" \
  --ref commit:abc123
```

After a consumer has actually consumed through an event:

```text
python tools/continuity.py ack --consumer codex --event-id CE-000001
```

`--event-id latest` is the default, but consumers should not advance past events they have not actually consumed.

The CLI is intentionally file-backed and single-writer-naive. It is a probe surface, not a synchronization service.

## Event record v0

Required fields:

```text
event_id
observed_at
actor
surface
kind
summary
refs
parent_refs
reported_standing_delta
reported_frontier_delta
```

Semantics:

- `event_id`: continuity-local identity, monotonically assigned in v0.
- `observed_at`: producer-reported timestamp.
- `actor`: participant that recorded the activity.
- `surface`: where the activity occurred, e.g. `chatgpt`, `vscode-cli`, `repo`.
- `kind`: descriptive activity kind; not yet a formal ontology.
- `summary`: compact report of what occurred.
- `refs`: repository paths, commit SHAs, traces, evidence packets, or other durable references needed to inspect the claim.
- `parent_refs`: prior continuity events this event explicitly responds to or consumes. This is lineage, not universal causal attribution.
- `reported_standing_delta`: producer-reported scientific/semantic standing change, or null.
- `reported_frontier_delta`: producer-reported navigation/frontier change, or null.

## Cursor record v0

```json
{
  "consumer": "codex",
  "cursor_state": "UNINITIALIZED",
  "last_seen_event_id": null
}
```

A fresh cursor is `UNINITIALIZED`; its null `last_seen_event_id` is missing
position, not an origin coordinate. It cannot produce ordinary delta.

Explicit bootstrap changes it to `POSITIONED` and retains `bootstrap_mode`.
For `FROM_HEAD` and `AFTER_EVENT`, `last_seen_event_id` records the established
event boundary. For `FROM_ORIGIN`, the explicit mode—not null by itself—records
the origin boundary. A cursor otherwise says only what continuity coordinate
the named consumer reports having established or consumed through. Consumers
do not need identical internal state.

```text
UNINITIALIZED != POSITIONED
null != stream coordinate
BOOTSTRAP_REQUIRED != unread delta
```

## Experimental cursor consumers

Two additional cursor-bearing consumers are currently under bounded pressure:

- `sol` → `continuity/cursors/sol.json`
- `pulse` → `continuity/cursors/pulse.json`

They are **not** registry-listed semantic seats in v0.

```text
cursor-bearing consumer
!=
registry-listed seat
!=
invocation identity
!=
scheduled automation
```

Their existence does not widen authority or standing. Each may advance only its
own cursor and only after actual consumption.

## Two-consumer registry v0

`registry.json` stores only the two intended semantic consumer identities,
human-readable roles, cursor references, and optional invocation/working-state
references. The `registry` command derives `cursor_state`, `last_seen_event`,
and `unread_event_count` from the referenced cursor and `events.jsonl` at read
time. Missing cursors, uninitialized cursors, and stale optional references
remain explicit.

```text
registry identity/reference
!= cursor authority
!= invocation liveness
!= working semantic state
!= authority
!= standing
```

The registry is a read-only projection. Inspecting it never advances a cursor,
acknowledges an event, establishes activity, or reconstructs semantic state.

A manual ChatGPT tether uses a locally unique `tether_id`, the explicitly
supplied opaque `invocation_ref`, `invocation_kind: chatgpt-thread`,
`association_basis: MANUAL_ASSERTION`, and `resolution_status: OPAQUE` or
`UNRESOLVED`. The projection does not resolve the opaque value as a path.

```text
local tether identity != ChatGPT-native invocation identity
manual assertion != independent verification
opaque association != liveness or semantic synchronization
```

## Consumer startup protocol

1. Read your cursor.
2. If it is `UNINITIALIZED`, stop ordinary synchronization and choose an
   explicit bootstrap mode.
3. If it is `POSITIONED`, read continuity events strictly after its established
   coordinate.
4. State the delta: what happened, what reportedly changed, what remains unresolved, and what must not be assumed.
5. Follow only refs required by the current operation or standing claim.
6. Work from authoritative source material where needed.
7. Append new consequential activity to `events.jsonl`.
8. Advance your cursor only after the delta has been consumed.

Do not treat a continuity summary as a substitute for a referenced test, trace, commit, decision, or other authoritative source when the current operation depends on that evidence.

## CONTINUITY-001 pressure

Compare ordinary repository reconstruction against delta consumption for the same bounded continuation task.

Measure at minimum:

```text
files/refs read
context consumed
elapsed continuation effort
incorrect claims
missing changes
human corrections required
standing errors
frontier errors
false continuity assumptions
```

Pass criterion is directional, not yet a numeric threshold:

```text
less reconstruction work
+
fewer human corrections
+
equal or better standing fidelity
```

If the delta carrier does not buy this, it has not earned expansion.

## Explicit non-claims

v0 does not establish:

- concurrency safety;
- multi-writer conflict resolution;
- automatic event capture;
- background synchronization;
- authority transfer;
- semantic truth from event presence;
- automatic standing/frontier mutation;
- generalized agent memory;
- a durable transport beyond Git/file persistence.

Those remain pressure territory.
