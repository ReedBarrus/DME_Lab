# ENVELOPE_SELECTION_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

DURABLE SELECTION:
APPEND-ONLY HUMAN ATTENTION EVENT

CURRENT SELECTION:
DERIVED PROJECTION

PREPARATION ELIGIBILITY:
DERIVED PROJECTION ONLY

EXECUTION AUTHORITY:
NONE

STANDING EFFECT:
NONE
```

## Sole question

```text
CAN HUMAN ATTENTION TO AN EXACT
EXECUTION-ENVELOPE REQUEST

BE RETAINED AS APPEND-ONLY HISTORY

WHILE CURRENT SELECTION AND
PREPARATION ELIGIBILITY CHANGE

WITHOUT SELECTION BECOMING
CONSEQUENCE AUTHORITY?
```

## Core geometry

```text
SELECTION HISTORY
=
immutable attention events

CURRENT_SELECTION_SET
=
projection over selection history

REQUEST APPLICABILITY v0
=
current campaign basis refs
exactly equal campaign basis refs

CURRENT DEVELOPMENTAL RELEVANCE
=
campaign relation standing

PREPARATION ELIGIBILITY
=
current selection
× request applicability
× campaign standing
× preparation policy
```

The v0 preparation policy is deliberately non-consequential:

```text
selected
+
request applicability CURRENT
+
relation standing OPEN

→ ELIGIBLE_FOR_PACKET_PREPARATION

otherwise
→ BLOCKED
```

No packet preparation operation is executed by this candidate.

## Current selector boundary

Current Workflow names Reed as Executive.

Therefore v0 accepts durable selection events only when:

```text
selected_by = REED
```

Seats may lodge candidate requests.

Seats may not self-create human-selection history.

```text
REQUEST AUTHOR
!=
ATTENTION SELECTOR
```

This does not grant Reed execution authority through the selection object.
Execution authorization remains a separate downstream relation.

## Durable event

`ENVELOPE_SELECTION_v0` binds:

```text
selection_id

campaign_id
campaign_sha256

request_id
request_sha256

selected_by

selected_at_basis_refs[]
selected_at_basis_sha256

selection_kind:
  SELECTED_FOR_PACKET_FORMATION
  SELECTION_RELEASED

selection_reason:
  optional narrative

authorization_effect = NONE
execution_effect = NONE
standing_effect = NONE
```

The event never stores:

```text
STALE
OBSOLETE
PREPARATION_ELIGIBLE
PREPARATION_BLOCKED
AUTHORIZED
```

Those are current projections over history and present state.

## Governing non-collapses

```text
SELECTED REQUEST LABEL
!=
SELECTED REQUEST IDENTITY

HISTORICAL HUMAN ATTENTION
!=
CURRENT ATTENTION ALLOCATION

SELECTED
!=
PREPARATION ELIGIBLE

PREPARATION ELIGIBLE
!=
EXECUTION AUTHORITY

SELECTION BASIS
!=
CURRENT REQUEST BASIS

SELECTION WAS VALIDLY RECORDED
!=
REQUEST IS CURRENTLY USABLE

SELECTION RELEASED
!=
REQUEST OBSOLETE

HUMAN STOPPED FOCUSING ON IT
!=
WORLD MADE IT IRRELEVANT

SET MEMBERSHIP
!=
ORDER

ORDER
!=
PRIORITY

PRIORITY
!=
AUTHORITY

EXECUTED
!=
WAS SELECTED

HISTORY OBSERVED
!=
GOVERNANCE HISTORY WE WISH HAD OCCURRED
```

## Projection vocabulary

For each currently selected exact request identity, the projection may derive:

```text
attention:
SELECTED

request_applicability:
CURRENT | STALE

developmental_relevance:
OPEN | RESOLVED_EARNED | OBSOLETE_FRACTURED

preparation:
ELIGIBLE_FOR_PACKET_PREPARATION
| BLOCKED_PENDING_REVALIDATION
| BLOCKED_RESOLVED
| BLOCKED_OBSOLETE

authorization_effect:
NONE

execution_effect:
NONE

priority_effect:
NONE
```

A request may therefore remain historically and currently selected while being
blocked from preparation.

## Pressure cells

```text
S1 BASIC SELECTION
   E1 E2 E3 exist
   Reed selects exact E2
   → E2 joins CURRENT_SELECTION_SET
   → E1/E3 unchanged
   → no authority / execution / standing effect

S2 BASIS DRIFT
   E2 selected @ B1
   campaign/current basis → B2
   → selection event unchanged
   → current attention still SELECTED
   → request applicability STALE
   → preparation BLOCKED_PENDING_REVALIDATION

S3 REPLAY
   exact same selection event replay
   → one durable event

S4 ATTENTION MOVES
   select E2
   release E2
   select E3
   → historical E2 select/release retained
   → current projection contains E3 only

S5 SELECTED WITHOUT AUTHORITY
   E2 selected and preparation-eligible
   → authorization_effect NONE
   → execution_effect NONE

S6 FRACTURED RELATION
   E2 selected
   underlying campaign relation → FRACTURED
   → selection history unchanged
   → developmental relevance OBSOLETE_FRACTURED
   → preparation BLOCKED_OBSOLETE

S7 UNSELECTED EXECUTION
   E1 has no selection event
   execution receipt appears
   → execution receipt remains visible
   → no selection event synthesized

S8 PARALLEL ATTENTION
   select E14 E22 E31
   → all coexist in CURRENT_SELECTION_SET
   → output representation canonicalized
   → no priority relation inferred

S9 REQUEST IDENTITY REUSE
   selection binds E22@shaA
   alternate bytes are presented under E22 label
   → selection event rejected against mismatched request identity
   → old selection cannot attach to changed bytes

S10 NON-EXECUTIVE SELF-SELECTION
   a seat attempts selected_by != REED
   → event rejected
   → candidate request remains unchanged
```

## Claim ceiling

A passing candidate may support only that the tested selection store can retain
append-only Executive attention events bound to exact request identity, derive a
nonexclusive current-selection set, and derive preparation eligibility from
current basis and campaign standing without granting execution or standing
authority.

It does not establish:

```text
actual packet preparation
priority ordering
automatic packet formation
execution authorization
scheduler behavior
automatic seat assignment
general human-intent interpretation
```
