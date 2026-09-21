# HISTORICAL_P09_PRODUCER_QUALIFICATION_001

## Object

```text
OBJECT_TYPE:
UPSTREAM_STANDING_PRODUCER_QUALIFICATION

OBJECT_ID:
HISTORICAL_P09_PRODUCER_QUALIFICATION_001

RELATION_TYPE:
ACTIVE_OWNERSHIP_EFFECT_STATUS

TARGET_CONSUMER:
LANE_LIFECYCLE_DISPOSITION_001 / P09

REPAIR:
P09_SCOPE_AND_TEMPORAL_BOUNDARY_001
```

## Sole question

Given a mechanically bound closed scope of effect-bearing units and an ordered,
content-addressed raw event log for that scope, can a producer derive exactly one of:

```text
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP
```

without inferring favorable standing from omitted units, missing events, or
terminal/checkpoint events that precede the relevant effect start?

## Repaired raw membrane

The producer no longer accepts:

```text
closed_scope = true
```

as evidence that accounting is closed.

Allowed candidate input is:

```text
scope:
  scope_id
  unit_ids[]
  event_count
  event_log_sha256
  scope_identity

events[]:
  scope_id
  unit_id
  event_index
  event_type
```

Closed event vocabulary:

```text
EFFECT_BEARING_UNIT_START
TERMINAL_RECEIPT
OWNERSHIP_INDEPENDENT_CHECKPOINT
```

The producer must mechanically establish:

```text
scope_identity
=
digest(scope_id + exact unit inventory + event_count + event_log_sha256)

event_log_sha256
=
digest(exact ordered events[])

event_count
=
len(events[])

every event.scope_id
=
scope.scope_id

every event.unit_id
∈
scope.unit_ids[]

event_index
=
contiguous ordered sequence
```

Therefore:

```text
DECLARED CLOSED_SCOPE
!=
CLOSED ACCOUNTING MECHANICALLY ESTABLISHED

UNIT INVENTORY PRESENT
!=
EVENT LOG BOUND TO THAT INVENTORY

EVENT PRESENT
!=
EVENT ORDER IRRELEVANT
```

The scope identity is the producer's bounded evidentiary subject. Historical
administration must therefore provide an exact retained scope/event-log basis;
it may not manufacture a fresh favorable scope record from a convenient subset.

## Temporal derivation law

For each unit, the producer retains:

```text
latest EFFECT_BEARING_UNIT_START
latest TERMINAL_RECEIPT
latest OWNERSHIP_INDEPENDENT_CHECKPOINT
```

A started unit is finished for P09 only when at least one closing event occurs
strictly after the latest relevant effect start:

```text
max(latest terminal, latest independent checkpoint)
>
latest effect start
```

Otherwise the unit remains unfinished.

Freeze:

```text
TERMINAL EXISTS
!=
TERMINAL AFTER RELEVANT EFFECT START

CHECKPOINT EXISTS
!=
CHECKPOINT COVERS CURRENT EFFECT

EARLIER CLOSURE
!=
LATER EFFECT DISPOSITION
```

## Frozen cells

```text
A
one unit:
START -> TERMINAL
=> NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP

B
one unit:
START
=> UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP

C
one unit:
START -> OWNERSHIP_INDEPENDENT_CHECKPOINT
=> NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP

D
scope identity does not match supplied scope basis
=> ADMINISTRATION_INVALID

E
two-unit closed scope:
U1 START -> TERMINAL
U2 START
=> UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP

F
frozen scope identity/event-log identity names U1 + unfinished U2,
but supplied event list omits U2
=> ADMINISTRATION_INVALID

G
TERMINAL -> START
=> UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP

H
OWNERSHIP_INDEPENDENT_CHECKPOINT -> START
=> UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP
```

Cell F is the explicit omission attack:

```text
FAVORABLE SUBSET
+
UNCHANGED CLOSED-SCOPE IDENTITY
→
ADMINISTRATION_INVALID
```

Cells G/H are the explicit temporal-coverage attack.

## Claim ceiling

A positive qualification establishes only that this producer correctly derives
P09 standing from the frozen bounded scope/event grammar.

It does not establish:

```text
favorable P09 for historical Lane B
that an arbitrary caller's scope record is complete
universal event-log completeness
historical RELEASE admissibility
```

Historical Lane-B application requires a separately reconstructed exact source
basis whose scope identity and event-log identity are recoverable from the
preserved specimen.

No live lane mutation. No RELEASE. No P11 standing. No P18 repair. No merge authorization.
