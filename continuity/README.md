# Continuity Delta v0

Purpose: reduce cross-invocation reconstruction by preserving a small durable activity stream that consumers read as deltas from their own last-seen coordinate.

This is not project authority, semantic adjudication, a global memory object, or a replacement for repository evidence.

## Core contract

```text
activity occurs
-> append a continuity event
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

The initial consumers are `codex`, `chatgpt`, and `grep-kitty`.

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
  "last_seen_event_id": null
}
```

A cursor says only what continuity event the named consumer reports having consumed through. Consumers do not need identical internal state.

## Consumer startup protocol

1. Read your cursor.
2. Read continuity events strictly after `last_seen_event_id`.
3. State the delta: what happened, what reportedly changed, what remains unresolved, and what must not be assumed.
4. Follow only refs required by the current operation or standing claim.
5. Work from authoritative source material where needed.
6. Append new consequential activity to `events.jsonl`.
7. Advance your cursor only after the delta has been consumed.

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
