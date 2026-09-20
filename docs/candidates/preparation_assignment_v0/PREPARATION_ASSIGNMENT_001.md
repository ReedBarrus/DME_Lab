# PREPARATION_ASSIGNMENT_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

PURPOSE:
durable seat ↔ exact preparation-unit allocation

WAKE SOURCE:
NONE

SCHEDULER:
NONE

OCCUPANCY EFFECT:
NONE

EXECUTION AUTHORITY:
NONE

STANDING EFFECT:
NONE

PRIORITY EFFECT:
NONE
```

## Sole question

```text
CAN ONE EXACT PREPARATION UNIT
BE DURABLY ASSIGNED
TO ONE EXACT SEAT

WITHOUT ASSIGNMENT BECOMING:

priority
wake
occupancy
execution authority
request ownership
or permission for additional work?
```

## Core chain

```text
REQUEST
↓
SELECTION
↓
PREPARATION ELIGIBILITY
↓
ASSIGNMENT
↓
CURRENT WAKE ELIGIBILITY
↓
future WAKE OPPORTUNITY
↓
future BOUNDED REENTRY
```

This candidate stops at assignment and derived wake eligibility.

It does not create wake opportunities.

## Durable assignment event

```text
PREPARATION_ASSIGNMENT_v0

assignment_id

campaign_id
campaign_sha256

request_id
request_sha256

selection_ref
selection_sha256

seat_id
preparation_kind

assigned_by = REED

assigned_at_basis_refs[]
assigned_at_basis_sha256

assignment_kind:
  ASSIGNED
  ASSIGNMENT_RELEASED

assignment_reason

authority_effect = NONE
execution_effect = NONE
standing_effect = NONE
priority_effect = NONE
wake_effect = NONE
```

The event is historical evidence of allocation.

It does not contain current projection state such as:

```text
OUTSTANDING
SATISFIED
RELEASED
BLOCKED_STALE
BLOCKED_OBSOLETE
BLOCKED_RESOLVED
```

Those are derived.

## Assignment satisfaction

Generic PREPARATION_RECEIPT_v0 remains unchanged.

A separate exact linkage records that one qualifying preparation result discharged
one exact sticky note:

```text
ASSIGNMENT_SATISFACTION_v0

satisfaction_id

assignment_id
assignment_sha256

preparation_receipt_id
preparation_receipt_sha256

request_id
request_sha256

seat_id
preparation_kind

satisfaction_effect = SATISFIES_EXACT_ASSIGNMENT

authority_effect = NONE
execution_effect = NONE
standing_effect = NONE
priority_effect = NONE
wake_effect = NONE
```

Therefore:

```text
PREPARATION RECEIPT EXISTS
!=
ARBITRARY ASSIGNMENT SATISFIED

ASSIGNMENT LABEL
!=
ASSIGNMENT IDENTITY
```

A qualifying receipt must mechanically match the exact assignment across:

```text
request identity
selection identity
seat identity
preparation kind
mechanical_status = PASS
```

## Current projection

The current assignment projection is derived from:

```text
ASSIGNMENT HISTORY
+
RELEASE HISTORY
+
EXACT SATISFACTION LINKS
+
CURRENT REQUEST / CAMPAIGN / SELECTION STATE
```

Current states include:

```text
OUTSTANDING
SATISFIED
RELEASED
BLOCKED_STALE
BLOCKED_OBSOLETE
BLOCKED_RESOLVED
```

Additional defensive projection states may describe a lost current selection or
other preparation block without mutating historical assignment events.

Only:

```text
OUTSTANDING
```

is wake-eligible under this v0 projection.

No wake is emitted by this candidate.

## Governing non-collapses

```text
SELECTED
!=
ASSIGNED

ASSIGNED
!=
OUTSTANDING

OUTSTANDING
!=
AWAKE

AWAKE
!=
CONSEQUENCE AUTHORIZED

ASSIGNMENT RELEASED
!=
ASSIGNMENT SATISFIED

ASSIGNED ONE UNIT
!=
OWNS REQUEST

MULTIPLE ASSIGNMENTS
!=
QUEUE ORDER

FIRST ASSIGNED
!=
FIRST WOKEN

ASSIGNED
!=
PRIORITIZED

STICKY NOTE EXISTS
!=
BELL RANG
```

## Time boundary

The assignment object deliberately contains no scheduling semantics.

```text
due_at:
ABSENT

wake_at:
ABSENT

interval:
ABSENT

recurrence:
ABSENT
```

The assignment answers only:

> Who holds which exact clipboard unit?

A later wake-source candidate may answer:

> When may an outstanding sticky note receive a bell?

## Pressure cells

```text
A1  exact basic assignment
A2  unselected/ineligible request rejected
A3  stale after assignment
A4  fracture after assignment
A5  explicit release != satisfaction
A6  parallel seats / assignments
A7  multiple assignments to one seat != queue
A8  exact replay / identity conflict
A9  unrelated prep receipt cannot satisfy assignment
A10 exact qualifying receipt satisfies once
A11 satisfied assignment is no longer wake-eligible
A12 same request may receive a distinct assignment
    for another seat / preparation kind
```

## Claim ceiling

A passing candidate may support only that the tested assignment store can retain
exact human-authored seat/request/preparation allocations, derive current
wake-eligibility from existing campaign/selection state, preserve stale and
fractured assignment history, distinguish release from satisfaction, and bind
one exact qualifying preparation receipt to one exact assignment without
creating wake, priority, authority, execution, or standing effects.

It does not establish:

```text
scheduler correctness
wake-source correctness
automatic assignment policy
priority policy
queue order
automatic seat selection
automatic work selection
semantic-model routing
execution authority
standing authority
production liveness
```
