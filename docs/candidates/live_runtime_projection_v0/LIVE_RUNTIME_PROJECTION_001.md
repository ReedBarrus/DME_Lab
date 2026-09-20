# LIVE_RUNTIME_PROJECTION_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

SOURCE:
DURABLE RUNTIME STORES

PROJECTION:
DERIVED / READ-ONLY

TRANSPORT:
SERVER-SENT EVENTS + JSON SNAPSHOT

COCKPIT EFFECT:
DISPLAY ONLY

CONTROLLER EFFECT:
NONE

AUTHORITY EFFECT:
NONE
```

## Sole question

```text
CAN DURABLE STATE CHANGING
OUTSIDE THE COCKPIT

CAUSE THE COCKPIT RUNTIME PROJECTION
TO UPDATE AUTOMATICALLY

WITHOUT THE PROJECTION
BECOMING AUTHORITATIVE STATE?
```

## Source surfaces

v0 reads existing durable state only:

```text
GOBLIN CONTROLLER DB
→ seats
→ wakes
→ operator invocations
→ action requests
→ receipts
→ semantic requests/proposals

CAMPAIGN DB
→ campaigns
→ relation standing
→ envelope requests
→ execution receipts

SELECTION DB
→ append-only selection events

PREPARATION DB
→ prep receipts
→ prep artifacts

LOCAL SEMANTIC DB
→ model resources
→ model leases
→ semantic run status
```

No manual Cockpit state database is introduced.

## Projection boundary

```text
DURABLE SOURCE STATE
→ read-only observation
→ normalized runtime snapshot
→ SSE / JSON transport
→ Cockpit display

NOT:

Cockpit
→ durable runtime mutation
```

Standing scars:

```text
PROJECTION
!=
SOURCE OF TRUTH

COCKPIT
!=
CONTROLLER

DISPLAYED STATE
!=
AUTHORITY

UI ACTION
!=
CONSEQUENCE

LIVE PROJECTION
!=
ATOMIC GLOBAL WORLD STATE
```

## Cross-store observation

Runtime state is currently distributed across multiple SQLite stores.

The v0 projection reads each source independently using SQLite read-only mode.

Therefore:

```text
cross_store_atomicity:
NOT_ESTABLISHED
```

The projection must not imply all displayed rows were observed under one global
transaction.

Each snapshot carries per-source availability and an explicit cross-store
atomicity statement.

## Runtime snapshot coordinates

The v0 snapshot exposes:

```text
SEATS
CAMPAIGNS
FRONTIER / STANDING
REQUESTS
SELECTION HISTORY
CURRENT SELECTION
PREPARATION RECEIPTS
CURRENT READINESS
ACTIVE WAKES / OPERATIONS
MODEL RESOURCES
MODEL LEASES
AUTHORITY / ACTION REQUESTS
RECEIPTS
SEMANTIC REQUESTS
SOURCE DIAGNOSTICS
```

The projection may derive display-oriented groupings but may not infer
authorization, priority, scientific standing, or seat purpose not present in
the durable stores.

## Live transport

The sidecar exposes:

```text
GET /runtime/snapshot.json
GET /runtime/events
```

`/runtime/events` is an SSE stream.

It emits an initial snapshot and emits another runtime-projection event when
the normalized snapshot identity changes.

No POST/PUT/PATCH/DELETE runtime mutation route exists.

## Existing Cockpit composition

The repository Cockpit remains usable without the live sidecar.

When a runtime endpoint is supplied, the observer subscribes and renders a
separate live-runtime pane.

When no sidecar is available:

```text
RUNTIME TELEMETRY:
UNAVAILABLE / NOT CONFIGURED
```

The observer must not simulate liveness.

## Pressure cells

```text
L1 READ-ONLY BASELINE
   snapshot reads durable stores
   → source DB bytes/state unchanged
   → projection_effect = NONE

L2 EXTERNAL SEAT CHANGE
   writer changes controller state outside Cockpit
   → SSE emits changed snapshot automatically
   → browser refresh not required

L3 DEVELOPMENT STATE CHANGE
   external request / selection / preparation state changes
   → next snapshot reflects durable change
   → no projection-side mutation

L4 ACTIVE OPERATION CHANGE
   external wake / operation state changes
   → live projection reflects occupancy / active wake

L5 RESOURCE LEASE CHANGE
   external model lease state changes
   → live projection reflects lease
   → model selection / authority not inferred

L6 MISSING OPTIONAL SOURCE
   one configured runtime store is unavailable
   → snapshot remains explicit PARTIAL
   → missing source not represented as empty healthy state

L7 WRITE ATTEMPT
   POST / PUT / PATCH / DELETE against runtime sidecar
   → rejected
   → durable state unchanged

L8 NO CHANGE
   no durable projected state changes
   → no duplicate state-change event emitted merely because polling occurred

L9 CROSS-STORE NON-ATOMICITY
   snapshot explicitly reports NOT_ESTABLISHED
   → one rendered screen does not imply one atomic world transaction
```

## Claim ceiling

A passing candidate may support only that the tested sidecar can observe the
declared durable SQLite surfaces read-only, derive runtime snapshots, and push
changed snapshots over SSE to a read-only Cockpit pane when durable projected
state changes elsewhere.

It does not establish:

```text
atomic cross-store world snapshots
scheduler correctness
bounded reentry
general event-bus correctness
production networking
multi-host runtime observation
authorization through UI
Cockpit Controller functionality
human-use / visual-semantic qualification
```
