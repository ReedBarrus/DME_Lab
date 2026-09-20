# WAKE_SOURCE_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

WAKE SOURCE:
MANUAL_BELL ONLY

INPUT:
ONE EXACT ASSIGNMENT IDENTITY

OUTPUT:
ONE EXACT WAKE OPPORTUNITY

WORK SELECTION:
NONE

SEAT SELECTION:
NONE

PRIORITY:
NONE

SCHEDULER:
NONE

EXECUTION AUTHORITY:
NONE
```

## Sole question

```text
CAN ONE MANUAL BELL

BOUND TO ONE EXACT CURRENTLY
OUTSTANDING + WAKE-ELIGIBLE ASSIGNMENT

RETAIN ONE EXACT WAKE OPPORTUNITY

WITHOUT THE WAKE SOURCE
CHOOSING WORK, CHOOSING A SEAT,
RANKING ASSIGNMENTS, OCCUPYING A SEAT,
RUNNING PREPARATION, SATISFYING THE ASSIGNMENT,
GRANTING AUTHORITY, OR CHANGING STANDING?
```

## Identity chain

```text
MANUAL_BELL B1
assignment = A17@shaA
bell_basis_refs = B

        ↓ exactly once

WAKE_OPPORTUNITY W44
bell = B1@shaB
assignment = A17@shaA

        ↓ later

BOUNDED REENTRY
revalidates A17 before occupancy
```

Therefore:

```text
MANUAL BELL IDENTITY
!=
WAKE OPPORTUNITY IDENTITY

ASSIGNMENT LABEL
!=
ASSIGNMENT IDENTITY

BELL EMISSION VALIDITY
!=
WAKE ACCEPTANCE VALIDITY
```

## MANUAL_BELL_v0

The durable bell binds:

```text
bell_id

assignment_id
assignment_sha256

campaign_id
campaign_sha256

request_id
request_sha256

selection_ref
selection_sha256

seat_id
preparation_kind

bell_basis_refs[]
bell_basis_sha256

wake_source_kind = MANUAL_BELL

authority_effect = NONE
execution_effect = NONE
standing_effect = NONE
priority_effect = NONE
scheduler_effect = NONE
```

No due time, recurrence, interval, priority, or scheduler field exists.

## Wake-source responsibility

`WAKE_SOURCE_001` may:

```text
read one exact assignment identity
derive current assignment projection
require:
  assignment_state = OUTSTANDING
  wake_eligible = true
retain exact manual bell
retain exactly one wake opportunity bound to that bell + assignment
stop
```

It may not:

```text
choose another assignment
choose a seat
choose a preparation kind
rank outstanding assignments
infer queue order
occupy a seat
run preparation
satisfy an assignment
grant authority
change standing
schedule a future wake
```

## Reentry entrance condition

Wake-source-created opportunities carry:

```text
assignment_id
assignment_sha256

manual_bell_id
manual_bell_sha256
```

For those opportunities, `BOUNDED_REENTRY_001` must:

```text
load exact opportunity
verify exact bell / assignment binding
rederive CURRENT ASSIGNMENT PROJECTION
require:
  exact assignment_state = OUTSTANDING
  exact wake_eligible = true

ONLY THEN:
  start_wake()
```

Therefore:

```text
REVALIDATE
BEFORE
OCCUPY
```

If the assignment became:

```text
SATISFIED
RELEASED
BLOCKED_NOT_SELECTED
BLOCKED_STALE
BLOCKED_OBSOLETE
BLOCKED_RESOLVED
BLOCKED_PREPARATION
```

after bell emission but before answer, the wake opportunity remains historical
but reentry is blocked before controller occupancy.

## Cross-store limit

Assignment projection and controller occupancy currently live in separate
durable stores.

v0 establishes the tested ordering:

```text
assignment revalidation
→ controller occupancy attempt
```

It does not establish a single atomic transaction spanning all assignment,
campaign, selection, preparation, and controller stores.

```text
REVALIDATED IMMEDIATELY BEFORE OCCUPANCY
!=
GLOBALLY ATOMIC WITH OCCUPANCY
```

That stronger race remains outside this claim.

## Bell replay

One exact bell identity may emit only one exact opportunity relation.

```text
same B1 replay
→ same W44 relation
→ no second independently legitimate opportunity
```

Changing the bytes behind the same `bell_id` is rejected.

## Pressure cells

```text
W1 ELIGIBLE ASSIGNMENT
   exact A17 OUTSTANDING + wake_eligible
   → retain B1
   → retain exact W44
   → no wake / occupancy / authority

W2 SATISFIED ASSIGNMENT
   → bell emission rejected
   → no wake opportunity

W3 RELEASED ASSIGNMENT
   → bell emission rejected
   → no wake opportunity

W4 BLOCKED_STALE ASSIGNMENT
   → bell emission rejected
   → no wake opportunity

W5 BLOCKED_OBSOLETE ASSIGNMENT
   → bell emission rejected
   → no wake opportunity

W6 EXACT BELL REPLAY
   same B1 replay
   → idempotent
   → same W44
   → no second opportunity

W7 TWO ELIGIBLE ASSIGNMENTS
   input names A17 only
   → only A17 gets a bell
   → no hidden selection / priority

W8 TWO ASSIGNMENTS ON MAYA
   bell names one exact assignment
   → no queue-order inference
   → no second bell synthesized

W9 BELL VALID THEN ASSIGNMENT INVALID BEFORE ANSWER
   B1/W44 retained while A17 OUTSTANDING
   then A17 becomes SATISFIED / RELEASED / STALE / OBSOLETE
   → W44 remains historical
   → bounded reentry revalidation fails
   → controller occupancy remains AVAILABLE
   → no unit / successor

W10 BELL ANSWERED
   eligible A17
   → B1 / W44
   → bounded reentry performs <=1 bound unit
   → wake source performs nothing further
   → exact later satisfaction makes A17 non-wake-eligible
   → new bell attempt rejected
```

## Claim ceiling

A passing candidate may support only that one manually named, exact,
currently wake-eligible assignment can produce one durable manual-bell record
and one exact assignment-bound wake opportunity, and that the tested reentry
entrance revalidates that assignment before controller occupancy.

It does not establish:

```text
clock behavior
wake policy
scheduling
due-time semantics
automatic bell creation
automatic assignment selection
priority policy
queue ordering
multi-host race closure
global cross-store atomicity
execution authority
standing authority
```
