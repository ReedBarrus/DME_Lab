# BOUNDED_REENTRY_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

WAKE SOURCE:
MANUAL / TEST-HARNESS ONLY

UNITS PER ACCEPTED WAKE:
AT MOST ONE

SEMANTIC MODEL:
NONE REQUIRED

SCHEDULER:
NOT MATERIALIZED

EXECUTION AUTHORITY:
UNCHANGED / EXTERNAL
```

## Sole question

```text
CAN A DURABLE SEAT

wake from no running occupant,
reconstruct its exact coordinate,
perform ONE bounded eligible unit,
emit a durable receipt,
release temporary occupancy,
and return dormant

WITHOUT THE WAKE ITSELF
BECOMING CONTINUOUS IDENTITY,
AUTHORITY,
OR OPEN-ENDED WORK?
```

## First specimen

The first specimen is a durable seat named:

```text
MAYA
```

The seat is retained in the existing GoblinPool controller.

Between wakes:

```text
seat identity:
retained durably

occupancy:
AVAILABLE

current wake:
NONE

model lease:
NONE REQUIRED

execution:
NONE
```

Therefore:

```text
SEAT PERSISTS
WHILE
OCCUPANT DOES NOT
```

## Wake-opportunity boundary

v0 uses a durable `WAKE_OPPORTUNITY_v0` object.

It binds:

```text
opportunity_id
seat_id
campaign_id
campaign_sha256
request_id | null
request_sha256 | null
selection_ref | null
selection_sha256 | null
preparation_kind | null
opportunity_basis
max_consumed_events
authority_effect = NONE
execution_effect = NONE
scheduler_effect = NONE
```

A wake opportunity is not a scheduler decision and is not execution authority.

```text
WAKE OPPORTUNITY
!=
WAKE ACCEPTED
!=
SEAT OCCUPIED
!=
WORK ELIGIBLE
!=
WORK PERFORMED
!=
STATE ADVANCED
```

## One-unit rule

One accepted wake may produce at most one of:

```text
ONE deterministic preparation receipt

OR

ONE NO_WORK / BLOCKED reentry outcome
```

After that bounded unit, the runner must stop.

If more eligible work remains:

```text
WORK REMAINS
!=
MAY CONTINUE RUNNING
```

A second unit requires a distinct wake opportunity.

## Deterministic preparation unit

The first moving specimen uses:

```text
preparation_kind = RESOLVE_REFS
```

No Qwen, Codex, or other semantic model is required.

For one exact selected + current + OPEN request, the unit derives a bounded
reference set from already-retained identities and appends one
`PREPARATION_RECEIPT_v0`.

The preparation layer remains responsible for validating that the request is
currently eligible.

## Reentry history

A companion append-only reentry store retains:

```text
wake opportunities
reentry lifecycle events
terminal reentry receipts
```

Lifecycle events are evidence of the runner's progression, not authority.

Candidate lifecycle event kinds:

```text
WAKE_ACCEPTED
RECONSTRUCTED
UNIT_STARTED
UNIT_RECEIPT_EMITTED
SUCCESSOR_COMMITTED
WAKE_BLOCKED
WAKE_ABORTED
DORMANT
```

## Successor boundary

Successful state advancement reuses the existing GoblinPool transactional
`commit_transition()` boundary.

The successor must atomically conserve:

```text
prior seat version
prior cursor
bounded consumed event prefix
one accepted reentry output
resulting working state
resulting cursor
version advance
occupancy release
state-transition receipt
```

No new seat-state commit mechanism is introduced.

## Crash boundary

Two distinct failure shapes are retained:

```text
CRASH BEFORE UNIT EFFECT
→ no preparation receipt
→ no successor
→ occupancy remains recoverable
→ no successful transition fabricated

CRASH AFTER PREP RECEIPT, BEFORE SEAT COMMIT
→ preparation receipt remains real
→ successor remains absent
→ occupancy remains recoverable
→ artifact existence != seat advancement
```

## World-movement boundary

A wake records exact Git HEAD at acceptance.

The runner reobserves exact Git HEAD before successor admission.

If:

```text
wake basis = H1
preparation receipt = realized @ H1
current world = H2
```

then:

```text
preparation receipt:
retained

seat successor:
NOT ADMITTED

wake:
aborted / released

reentry outcome:
STALE_AFTER_EFFECT
```

Therefore:

```text
UNIT EFFECT EXISTS
!=
UNIT EFFECT CURRENTLY APPLICABLE

WORLD MOVED
!=
HISTORY REWRITTEN
```

## Occupancy / temporary-resource boundary

The existing GoblinPool occupancy relation is the temporary v0 execution lease.

```text
SEAT IDENTITY
!=
CURRENT OCCUPANCY

WAKE HELD OCCUPANCY
!=
SEAT IDENTITY

OCCUPANCY ACQUIRED
!=
OPEN-ENDED PROCESS RIGHT
```

Normal completion releases occupancy transactionally.

Crash recovery uses the existing explicit `recover_lease()` path.

No model-resource lease is required by this first specimen.

## Live observation

`LIVE_RUNTIME_PROJECTION_001` may project:

```text
seat occupancy
current wake
reentry opportunities
reentry lifecycle events
terminal reentry receipts
preparation receipt
resulting dormancy
```

The live projection is an observer only.

```text
CONTROLLER RECORDED WAKE
!=
COCKPIT SAW WAKE

COCKPIT SAW WAKE
!=
WAKE SUCCEEDED
```

## Pressure cells

```text
R1 NORMAL REENTRY
   MAYA dormant
   → wake accepted
   → exact coordinate reconstructed
   → one deterministic preparation receipt
   → one successor commit
   → occupancy released
   → MAYA dormant

R2 NOTHING ELIGIBLE
   wake accepted with no target work
   → NO_WORK receipt/outcome
   → no invented task
   → sleep

R3 STALE SELECTED REQUEST
   selected request exists
   current Git basis differs
   → no preparation receipt
   → BLOCKED_STALE outcome
   → sleep

R4 OCCUPANCY COLLISION
   two wake opportunities target MAYA
   → one occupant maximum
   → second OCCUPANCY_CONFLICT
   → no duplicate work

R5 CRASH BEFORE UNIT EFFECT
   wake accepted
   injected crash before preparation
   → no prep receipt
   → no successor
   → recovery releases occupancy
   → no fabricated success

R6 CRASH AFTER EFFECT, BEFORE SEAT COMMIT
   one prep receipt appended
   injected crash before successor commit
   → prep receipt retained
   → seat successor absent
   → recovery releases occupancy

R7 WORLD MOVES DURING WAKE
   accepted @ H1
   prep receipt @ H1
   external Git actor → H2
   → receipt retained
   → no successor admission
   → STALE_AFTER_EFFECT
   → sleep

R8 REPLAY SAME WAKE
   exact same opportunity / wake replay
   → no second independently legitimate work unit

R9 OCCUPANCY RELEASE
   completion and explicit crash recovery
   → occupancy AVAILABLE
   → current_wake_id null
   → occupancy != seat identity

R10 WAKE CANNOT SELF-EXTEND
   two eligible selected requests exist
   opportunity binds one exact request
   → exactly one prep receipt
   → other work remains
   → seat sleeps
   → second unit requires another opportunity
```

## Claim ceiling

A passing candidate may support only that the tested durable seat can be
manually re-entered for at most one deterministic preparation-or-blocked unit,
retain a durable terminal receipt, use the existing transactional successor
boundary, and return to unoccupied durable state under the tested normal,
collision, crash, stale-world, and replay cells.

It does not establish:

```text
scheduler correctness
periodic wake policy
automatic wake selection
semantic cognition during wake
multi-unit wake excursions
general liveness
production daemon behavior
autonomous scientific authority
automatic execution authority
```
