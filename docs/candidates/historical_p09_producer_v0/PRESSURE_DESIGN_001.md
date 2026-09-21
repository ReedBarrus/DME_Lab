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
```

## Sole question

Given an explicitly closed bounded-unit scope and raw lifecycle events for every unit in that scope, can a producer derive exactly one of:

```text
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP
```

without inferring favorable standing from absent records?

## Raw membrane

Allowed candidate input:

```text
closed_scope
unit_ids[]
events[]:
  unit_id
  event_type
```

Closed event vocabulary:

```text
EFFECT_BEARING_UNIT_START
TERMINAL_RECEIPT
OWNERSHIP_INDEPENDENT_CHECKPOINT
```

The producer derives per-unit posture. A started unit requires ACTIVE ownership unless it has either a TERMINAL_RECEIPT or an OWNERSHIP_INDEPENDENT_CHECKPOINT.

```text
NO EVENT SEEN
!=
TERMINAL

MISSING UNIT FROM CLOSED SCOPE
!=
NO UNFINISHED UNIT

CLOSED SCOPE
!=
SEARCHED WHAT WAS CONVENIENT
```

If `closed_scope != true`, administration is invalid and no standing is emitted.

## Frozen cells

```text
A all started units terminal
  -> NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP

B one started unit lacks terminal/checkpoint
  -> UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP

C one started unit lacks terminal but has ownership-independent checkpoint
  -> NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP

D scope not declared closed
  -> ADMINISTRATION_INVALID

E multi-unit scope with one unfinished unit
  -> UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP
```

## Claim ceiling

A positive qualification establishes only that this producer correctly derives P09 standing from the frozen raw event grammar. It does not establish favorable P09 standing for historical Lane B. Historical application requires a separately constructed closed raw basis for the exact specimen.

No live lane mutation. No RELEASE. No P11 standing. No P18 repair. No merge authorization.
