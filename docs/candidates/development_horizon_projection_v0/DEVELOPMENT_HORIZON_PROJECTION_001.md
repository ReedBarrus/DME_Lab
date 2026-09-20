# DEVELOPMENT_HORIZON_PROJECTION_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

DURABLE ROADMAP DATABASE:
NONE

SOURCE:
EXISTING DEVELOPMENT CAMPAIGNS
+
CURRENT STANDING
+
CURRENT RUNTIME EVIDENCE

OUTPUT:
READ-ONLY HORIZON PROJECTION

AUTHORITY EFFECT:
NONE

PRIORITY EFFECT:
NONE
```

## Sole question

```text
CAN THE LAB DERIVE
A CURRENT DEVELOPMENTAL-HORIZON VIEW

FROM ALREADY-DURABLE
CAMPAIGNS / STANDING / ACTIVITY

WITHOUT INVENTING
A SECOND ROADMAP DATABASE,
PRIORITY ORDER,
OR DEVELOPMENTAL AUTHORITY?
```

## Governing cut

```text
HORIZON
!=
PLAN

PROJECT FUTURE
!=
SECOND TASK DATABASE

CAN READ HORIZON
!=
CAN ALTER HORIZON
```

A campaign states the developmental boundary it is trying to earn.

The horizon projection only answers what those already-durable campaigns
currently imply.

## Inputs

The projection may read:

```text
campaign packets
relation standing
campaign dependency edges
envelope requests
selection history / current selection
preparation receipts
assignment history / satisfaction
manual bells / bell emissions
bounded-reentry receipts
```

No input is mutated by projection.

## Cross-campaign dependency convention

The existing `dependency_edges` field is reused.

When an edge endpoint exactly names another campaign currently visible to the
projection:

```text
FROM_CAMPAIGN
→
TO_CAMPAIGN
```

the edge is treated as a developmental horizon dependency:

```text
FROM_CAMPAIGN must be EARNED
before TO_CAMPAIGN is unblocked.
```

Edges whose endpoints are not both known campaign IDs remain campaign-local
information and do not become cross-campaign blockers.

No new dependency store is introduced.

## Derived horizon states

The projection may derive:

```text
READY_FOR_PRESSURE
ACTIVE
EVIDENCE_ACCUMULATING
BLOCKED
EARNED
FRACTURED
```

These are current projection vocabulary only.

They are not written into campaign packets.

### EARNED

```text
all declared campaign relations = EARNED
```

### FRACTURED

```text
no OPEN relations remain
and at least one relation = FRACTURED
```

### BLOCKED

```text
at least one cross-campaign dependency
is not currently EARNED
```

### EVIDENCE_ACCUMULATING

Unblocked + OPEN frontier + at least one evidence-bearing activity:

```text
non-OPEN relation standing
OR preparation receipt
OR bounded-reentry receipt
```

### ACTIVE

Unblocked + OPEN frontier + current work activity:

```text
candidate request
OR current selection
OR assignment
OR manual bell
```

when no evidence-bearing activity above is yet present.

### READY_FOR_PRESSURE

Unblocked + OPEN frontier + no current work/evidence activity.

## No roadmap ranking

Multiple horizons may simultaneously be:

```text
READY_FOR_PRESSURE
ACTIVE
EVIDENCE_ACCUMULATING
```

without a ranking.

```text
UNBLOCKED
!=
PRIORITIZED

SCREEN POSITION
!=
PRIORITY

DEPENDENCY
!=
RECOMMENDATION
```

The UI may group states, but must not claim a best next horizon.

## Exact blockers and unlocks

Each horizon projection exposes:

```text
blocked_by[]
unlocks[]
```

`blocked_by` contains exact campaign IDs and their current horizon states.

`unlocks` contains dependent campaign IDs for which the current campaign is a
declared blocker.

A counterfactual may state:

```text
IF H1 BECAME EARNED,
H2 WOULD LOSE THIS DECLARED BLOCKER
```

It may not state:

```text
YOU SHOULD DO H1 NEXT
```

## Evidence orientation

Each horizon exposes:

```text
objective
claim_ceiling

open_relations[]
earned_relations[]
fractured_relations[]

candidate_request_count
current_selection_count
preparation_receipt_count
assignment_count
satisfaction_count
manual_bell_count
wake_opportunity_count
reentry_receipt_count
```

This is orientation, not standing promotion.

## Cockpit

God Gobbo may render a DEVELOPMENT HORIZONS pane grouped by current projected
state.

Each card shows:

```text
campaign / horizon ID
objective
current state
open / earned / fractured relations
exact blockers
declared unlocks
current work/evidence counts
```

No horizon-control button is introduced by this experiment.

```text
COCKPIT SHOWS HORIZON
!=
COCKPIT CHANGES HORIZON
```

## Pressure cells

```text
H1 READY
   OPEN campaign
   no blockers
   no work/evidence
   → READY_FOR_PRESSURE

H2 ACTIVE
   OPEN campaign
   current request/selection/assignment
   → ACTIVE
   → priority NONE

H3 EVIDENCE ACCUMULATING
   OPEN campaign
   preparation/reentry evidence exists
   → EVIDENCE_ACCUMULATING

H4 EARNED
   all relations EARNED
   → EARNED

H5 FRACTURED
   no OPEN relations
   at least one FRACTURED
   → FRACTURED

H6 BLOCKED
   WAKE_POLICY depends on RUNTIME_SANITY
   RUNTIME_SANITY not EARNED
   → WAKE_POLICY BLOCKED
   → exact blocker exposed

H7 UNLOCK
   same graph
   RUNTIME_SANITY becomes EARNED
   → WAKE_POLICY loses blocker
   → READY / ACTIVE according to its own activity
   → no priority inferred

H8 UNKNOWN EDGE
   dependency endpoint does not name a visible campaign
   → retained as local edge
   → does not fabricate cross-campaign blocker

H9 PROJECTION ONLY
   derive horizons
   → campaign / standing / assignment / bell stores unchanged

H10 COEXISTING HORIZONS
   multiple horizons READY / ACTIVE
   → all coexist
   → priority_effect = NONE
```

## Claim ceiling

A passing candidate may support only that the tested projection can derive
current horizon orientation and exact cross-campaign blockers from existing
durable campaign/runtime evidence without introducing roadmap state, priority,
authorization, execution, or standing effects.

It does not establish:

```text
roadmap authority
automatic prioritization
automatic campaign adoption
automatic assignment
automatic wake
scheduler policy
horizon-editing UI
general dependency semantics outside the tested convention
```
