# GOBLIN_POOL_001

## Status

```text
EXPERIMENTAL CONTROLLER CANDIDATE

ARCHITECT FOR:
MANY DURABLE TEMPORAL SEATS

PRESSURE WITH:
3 SEATS

BASE:
LABBOIB_TEMPORAL_SEAT_v0 candidate

GENERAL MULTI-AGENT ARCHITECTURE:
NOT CLAIMED

SCHEDULER:
NOT BOUND

MODEL:
OPTIONAL / NOT REQUIRED BY FIXTURE

EXTERNAL AUTHORITY EXPANSION:
NONE
```

## Sole question

```text
CAN ONE DURABLE CONTROLLER
MEDIATE MULTIPLE INDEPENDENT TEMPORAL SEATS

WHILE PRESERVING:

seat identity
seat-local continuity
single-successor semantics
transactional state transition
operator boundaries
authority boundaries

UNDER OVERLAPPING WAKE PRESSURE?
```

## Controller boundary

The controller owns only mechanical coordination:

```text
SQLite serialization
seat leases
event delivery
basis-version checks
operator registry
operator admission
transactional commit
receipt retention
```

It does not own:

```text
goblin policy
goblin identity
goblin authority
semantic purpose
campaign selection
scientific adjudication
model reasoning
```

Therefore:

```text
CONTROLLER
!=
GOBLIN POLICY

CONTROLLER
!=
GOBLIN IDENTITY

CONTROLLER
!=
GOBLIN AUTHORITY

CONTROLLER
!=
SEMANTIC DECISION-MAKER
```

## Minimum fixture

```text
SEATS:
GOB_A
GOB_B
GOB_C

CONTROLLER:
1

DURABLE STORE:
1 SQLite database

EVENT STORE:
shared physical table
seat-addressable events

OPERATOR REGISTRY:
shared

MODEL SURFACE:
optional semantic request/proposal carrier
```

The SQLite file is generated at runtime and is not repository authority.

## Required retained seat coordinates

Each seat row retains:

```text
seat_id
cursor_event_id
working_state_json
state_version
status
occupancy_state
current_wake_id
policy_ref
operator_profile_ref
authority_profile_ref
```

The controller does not interpret `policy_ref` as semantic policy. It only
retains the seat-local reference.

## Operator surface

The first canonical operators are intentionally austere:

```text
READ_REPO_STATE
RUN_DECLARED_TEST
WRITE_PACKET
```

The controller exposes four independent gates:

```text
REGISTERED
AVAILABLE
ELIGIBLE
AUTHORIZED
```

Execution is downstream of all four.

```text
REGISTERED
!=
AVAILABLE

AVAILABLE
!=
ELIGIBLE

ELIGIBLE
!=
AUTHORIZED

AUTHORIZED
!=
EXECUTED
```

No controller method selects which operator a seat should want.

The caller / seat policy must name a candidate operator. The controller only
checks whether that exact operator is mechanically admissible.

## Transaction law

An accepted seat successor is one SQLite transaction:

```text
EXACT PRIOR SEAT BASIS
+
EXACT CONSUMED EVENT PREFIX
+
EXACT ACCEPTED OUTPUT
+
EXACT ACCEPTED OPERATOR INVOCATIONS
+
EXACT RESULTING WORKING STATE
+
EXACT RESULTING CURSOR
+
STATE VERSION ADVANCE
+
LEASE RELEASE
+
TRANSITION RECEIPT
```

Either all become durable or none do.

```text
OUTPUT ACCEPTED
!=
STATE TRANSITION COMMITTED
```

until the transaction commits.

## Minimum durable identities

```text
seat_id
wake_id
event_id
output_id
transition_id
operator_invocation_id
receipt_id
semantic_request_id
semantic_proposal_id
```

These identities are intentionally distinct.

## Core non-collapses

```text
SEAT REGISTERED
!=
SEAT AWAKE

WAKE ELIGIBLE
!=
WAKE STARTED

WAKE STARTED
!=
SEAT OCCUPIED

SEAT OCCUPIED
!=
MODEL BOUND

OPERATOR AVAILABLE
!=
OPERATOR ELIGIBLE

OPERATOR ELIGIBLE
!=
OPERATOR AUTHORIZED

OPERATOR AUTHORIZED
!=
OPERATOR EXECUTED

OUTPUT PRODUCED
!=
OUTPUT ACCEPTED

OUTPUT ACCEPTED
!=
STATE TRANSITION COMMITTED

EVENT PRESENT
!=
EVENT CONSUMED

CURSOR POSITION
!=
WORKING STATE

TIME ADVANCED
!=
AGENT DID WORK

DETERMINISTICALLY SELECTABLE
!=
AUTHORIZED TO EXECUTE

MODEL PROPOSED
!=
CONTROLLER SELECTED
!=
AUTHORITY GRANTED
!=
OPERATOR EXECUTED
```

## Pressure cells

### P1 — simultaneous different-seat wake

```text
GOB_A eligible
GOB_B eligible

wake A
wake B

→ both may become occupied
→ no state cross-contamination
```

### P2 — same-seat overlap

```text
GOB_A wake W1 occupies seat

before W1 commits:
wake W2 arrives

→ exactly one STARTED
→ exactly one OCCUPANCY_CONFLICT
→ no second legitimate successor
```

### P3 — stale state submission

```text
W1 reads basis B0
W1 lease is recovered
W2 commits B1
W1 submits output produced against B0

→ STALE_BASIS
→ output rejected
```

Scar:

```text
VALIDLY PRODUCED OUTPUT
!=
VALID AGAINST CURRENT SEAT BASIS
```

### P4 — duplicate output

```text
output_id O1 already belongs to one committed transition

later wake submits O1

→ reject duplicate identity
→ exactly one durable output / successor
```

### P5 — deterministic-only wake

```text
GOB_B
→ RUN_DECLARED_TEST
→ exact declared test adapter
→ execution receipt
→ state commit

semantic request count:
0
```

This pressures:

```text
AGENTIC BEHAVIOR
!=
TRANSFORMER INVOCATION
```

### P6 — semantic escalation

```text
active wake
→ semantic request
→ typed semantic proposal

seat cursor:
UNCHANGED

seat working state:
UNCHANGED

seat state_version:
UNCHANGED
```

The semantic proposal cannot directly mutate durable seat state.

### P7 — authority stop

Fixture:

```text
GOB_C / WRITE_PACKET

REGISTERED:
true

AVAILABLE:
true

ELIGIBLE:
true

AUTHORIZED:
false
```

Expected:

```text
AUTHORITY_REQUIRED
→ ACTION_REQUEST retained
→ packet adapter not invoked
```

### P8 — crash before commit

A synthetic failure is injected after all successor SQL statements have been
issued but immediately before transaction commit.

Expected:

```text
ROLLBACK

no accepted output
no transition
no cursor advance
no working-state change
no version advance

lease remains visibly occupied
→ explicit lease recovery
→ AVAILABLE
```

### P9 — crash after commit / retry

After a transition commits, the caller discards the response and submits the
same wake / transition / output identities again.

Expected:

```text
ALREADY_COMMITTED
idempotent_replay = true

outputs:
1

transitions:
1

seat state_version:
1
```

## Event addressing

The event store is physically shared but events may be addressed to one seat or
to all seats.

Each seat consumes only events eligible after its own cursor.

```text
SHARED EVENT STORE
!=
SHARED CONSUMPTION COORDINATE
```

A seat transition may advance its cursor only over a contiguous prefix of
events eligible for that seat. It may not silently skip an eligible event.

## Semantic operator boundary

The controller can retain:

```text
semantic request
semantic proposal
```

but a proposal does not mutate:

```text
cursor
working state
state version
authority
```

A later experiment may bind GPT, LM Studio, Codex, a human, or another solver
to this request surface.

That binding is outside GOBLIN_POOL_001.

## Crash / lease boundary

Wake acquisition is a durable reservation.

A process crash can therefore leave a seat visibly OCCUPIED.

The first experiment uses explicit lease recovery rather than prematurely
inventing generalized lease timeout semantics.

```text
CRASHED OCCUPANT
!=
SECOND SUCCESSOR AUTHORIZED
```

## Claim ceiling

A passing candidate may support only:

```text
ONE SQLITE CONTROLLER CAN MEDIATE
THREE DURABLE TEMPORAL SEATS

UNDER THE TESTED:
OVERLAP
STALE-BASIS
DUPLICATE
DETERMINISTIC
SEMANTIC-ESCALATION
AUTHORITY-STOP
AND CRASH CONDITIONS

WITHOUT OBSERVED
SEAT-IDENTITY OR SUCCESSOR COLLAPSE.
```

It does not establish:

```text
30-seat scalability
distributed-controller safety
network partition tolerance
general autonomous agency
safe arbitrary operators
general scheduler correctness
general economic autonomy
VS Code / CLI tunnel safety
model-router correctness
production reliability
```

## Current implementation surface

```text
schemas/goblin_pool_v0.sql
tools/goblin_pool.py
tests/runtime/test_goblin_pool.py
```

Qualification must come from executed pressure, not this document.
