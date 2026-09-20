# LIVE_RUNTIME_PROJECTION_001 — Qualification 001

## Tested basis

```text
candidate branch:
live-runtime-projection-v0

tested head:
075f4b2ba394c37cf20f68691cd3e1f2ae23bab6

stack base:
preparation-v0
0eecbca16a2d5af706b7d110a656091ade89e500

workflow:
LIVE_RUNTIME_PROJECTION_001

run:
35505664468

job:
106064932764

conclusion:
SUCCESS
```

## Exact tested artifacts

```text
candidate design:
7aa92203a84aee7ea63d836b50fb3622ededa94e

runtime sidecar:
4ccb0297a43cefef6249043d5533fccf51434007

Cockpit runtime subscriber:
efc0f1774d21810db748c5c03fcd23ab0358a8a3

Cockpit app mount:
98f594ffcebd64cfbd3a494c8ea7fd54efffd999

Cockpit HTML mount:
19afa311f6d0552beace1d37be4c3e9768c71f92

Cockpit runtime styling:
1f5f82fbe5ea9d0fb575c322c1330dbd7278bdb8

pressure suite:
51604dfc35e6730467011354f512a49d622857c5

focused workflow:
a81d6335e4cfaf0f96cf14a7419a5c80ceb161ca
```

## Observed pressure

```text
L1 READ-ONLY BASELINE:
PASS

runtime snapshot read the configured durable stores
controller row counts before/after were identical

projection_effect = NONE
authority_effect = NONE
execution_effect = NONE
standing_effect = NONE

source_of_truth = DURABLE_RUNTIME_STORES


L2 EXTERNAL SEAT CHANGE / OPEN SSE STREAM:
PASS

Cockpit-side SSE connection opened
initial snapshot observed no occupied seat

external controller writer:
GOB_A → OCCUPIED
wake = W-LIVE-EXTERNAL

same already-open SSE connection:
received a second runtime_projection event

browser refresh:
not required

reconnect:
not required

state_sha256:
changed


L3 DEVELOPMENT STATE CHANGE:
PASS

external selection event + preparation receipt were appended
outside the projection sidecar

subsequent snapshot reflected:
selection history
current selection
MAYA preparation receipt
PREP_INCOMPLETE readiness

projection-side source mutation:
none


L4 ACTIVE OPERATION CHANGE:
PASS

external controller writer started GOB_B wake

snapshot reflected:
occupied seat GOB_B
active wake W-LIVE-B

projection_effect:
NONE


L5 RESOURCE LEASE CHANGE:
PASS

external writer added:
LEASE-LIVE
QWEN_LOCAL_PRIMARY
leased_to MAYA
status ACTIVE

snapshot reflected active lease

authority_effect:
NONE


L6 MISSING CONFIGURED SOURCE:
PASS

configured semantic DB path did not exist

projection_status:
PARTIAL

semantic source status:
UNAVAILABLE

model resources:
empty only with explicit source failure attached

therefore:
MISSING SOURCE
!=
HEALTHY EMPTY STATE


L7 WRITE ATTEMPT:
PASS

POST /runtime/snapshot.json
→ HTTP 405

controller durable row counts:
unchanged

sidecar exposes no POST / PUT / PATCH / DELETE mutation route


L8 NO DURABLE CHANGE:
PASS

two observations at different times produced:
different observed_at
same state_sha256

open change iterator:
did not emit another state event merely because polling occurred

after external GOB_C wake:
iterator emitted changed state

therefore:
OBSERVER POLLED
!=
WORLD CHANGED


L9 CROSS-STORE NON-ATOMICITY:
PASS

snapshot explicitly retained:

cross_store_atomicity = NOT_ESTABLISHED

current campaign store also exposed:
standing movement history unavailable in current source

therefore:
ONE RENDERED SCREEN
!=
ONE ATOMIC GLOBAL WORLD TRANSACTION
```

## Live transport result

The tested sidecar exposes only:

```text
GET /runtime/snapshot.json
GET /runtime/events
```

The second endpoint is an SSE stream.

A runtime event contains:

```text
state_sha256
observed_at
state
```

The state identity excludes the observation timestamp.

That prevents periodic polling from manufacturing apparent activity.

```text
OBSERVATION TIME CHANGED
!=
RUNTIME STATE CHANGED
```

## Cockpit composition

The existing repository Cockpit remains independently usable.

The new live pane subscribes only when a runtime SSE endpoint is supplied.

Without that endpoint it reports live runtime as unconfigured/unavailable rather
than simulating activity.

The existing Cockpit observer test suite passed on the same tested head.

```text
LIVE PANE UNAVAILABLE
!=
STATIC COCKPIT INVALID
```

## Durable surfaces projected

The tested normalized runtime model can expose:

```text
seats
occupied seats
active wakes
operator invocations
action requests
controller receipts
semantic requests/proposals

campaigns
current relation standing/frontier
envelope requests
execution receipts

selection history
derived current selection

preparation receipts/artifacts
derived preparation readiness

model resources
model leases
active model leases
semantic run status
```

The projection does not own any of those records.

## Standing-history limit

The current campaign store retains current relation standing and the latest
adjudication/basis fields, but not append-only standing-movement history.

The runtime projection therefore reports:

```text
standing_movement_history:
UNAVAILABLE_IN_CURRENT_CAMPAIGN_STORE
```

It does not fabricate a movement timeline from current state.

## Composition regression

The same workflow re-executed:

```text
existing Cockpit observer:
PASS

PREPARATION_001:
PASS

ENVELOPE_SELECTION_001:
PASS

DEVELOPMENT_CAMPAIGN_001:
PASS
```

## Bounded result

The executed fixture supports only:

```text
THE TESTED LIVE RUNTIME SIDECAR
CAN READ THE DECLARED DURABLE SQLITE SURFACES
WITHOUT MUTATING THEM,

DERIVE A NON-AUTHORITATIVE RUNTIME SNAPSHOT,

AND PUSH A CHANGED SNAPSHOT
OVER AN ALREADY-OPEN SSE CONNECTION

AFTER PROJECTED DURABLE STATE
CHANGES ELSEWHERE,

WITHOUT REQUIRING A BROWSER REFRESH
OR GIVING THE COCKPIT WRITE AUTHORITY.
```

## Nonclaims

This qualification does not establish:

```text
atomic cross-store world snapshots
bounded reentry
scheduler correctness
general event-bus correctness
production networking
multi-host observation
Controller UI authority
automatic action from UI
standing-history reconstruction
human-use / visual-semantic qualification
```

## Standing boundary

```text
LIVE_RUNTIME_PROJECTION_001:
9 / 9 PASS

OPEN-STREAM EXTERNAL-CHANGE UPDATE:
PASS

EXISTING COCKPIT OBSERVER REGRESSION:
PASS

PREPARATION_001 REGRESSION:
PASS

ENVELOPE_SELECTION_001 REGRESSION:
PASS

DEVELOPMENT_CAMPAIGN_001 REGRESSION:
PASS

COCKPIT WRITE AUTHORITY:
NONE

CONTROLLER EFFECT:
NONE

SCHEDULER:
UNTOUCHED

BOUNDED_REENTRY_001:
NOT MATERIALIZED

LANGUAGE_ROOM_001:
PARKED
```
