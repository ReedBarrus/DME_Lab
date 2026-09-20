# WAKE_SOURCE_001 — Qualification 001

## Tested basis

```text
candidate branch:
wake-source-v0

tested head:
41eabf6fcf42181b024be6b18c762dcb39881bc5

stack base:
preparation-assignment-v0
504be5126b08cd89769bd93f66e24432469bbc0a

workflow:
WAKE_SOURCE_001

run:
35507519237

job:
106069733854

conclusion:
SUCCESS
```

The same tested head also re-ran the modified bounded-reentry surface:

```text
BOUNDED_REENTRY_001

run:
35507519200

conclusion:
SUCCESS
```

## Exact tested artifacts

```text
candidate design:
44f03d596f486f78b9b0d57574d52e4a6faeafad

wake-source implementation:
ce495c6f6ab241c452ef8928a1c528151014edbd

assignment-aware bounded reentry:
712e3b166e1d32a2614c650f99f63fedcf54e2dc

manual-bell schema:
42a2064395bfa17edcdf5be0aa0bced1555ed48f

pressure suite:
6d3bc7ebc4308115993721f76bdabe3bc66a0b98

focused workflow:
391f8bc3017b2b89fcd04004b70d0f13bbb28951
```

## Observed focused pressure

GitHub Actions executed:

```text
python -m unittest tests.runtime.test_wake_source -v
```

and completed successfully.

Observed cells:

```text
W1  eligible exact assignment → one exact opportunity / no wake       PASS
W2  satisfied assignment cannot emit bell                             PASS
W3  released assignment cannot emit bell                              PASS
W4  stale assignment cannot emit bell                                 PASS
W5  obsolete assignment cannot emit bell                              PASS
W6  exact bell replay returns same opportunity relation               PASS
W7  two eligible assignments → only named assignment receives bell    PASS
W8  two MAYA assignments → no queue / second bell inferred            PASS
W9  bell survives later invalidation; reentry blocks before occupancy PASS
W10 answered bell runs <=1 unit; later satisfaction blocks new bell   PASS
```

## W1 — exact manual bell

One exact assignment:

```text
A17
seat = MAYA
request = exact E1 identity
preparation_kind = RESOLVE_REFS
assignment_state = OUTSTANDING
wake_eligible = true
```

received:

```text
MANUAL_BELL:
B1

WAKE_OPPORTUNITY:
W44
```

The retained opportunity bound:

```text
assignment_id = A17
assignment_sha256 = exact assignment identity

manual_bell_id = B1
manual_bell_sha256 = exact bell identity

wake_source_kind = MANUAL_BELL
```

while:

```text
controller wake rows:
0

MAYA occupancy:
AVAILABLE

authority_effect:
NONE

execution_effect:
NONE

scheduler_effect:
NONE
```

Therefore:

```text
MANUAL BELL IDENTITY
!=
WAKE OPPORTUNITY IDENTITY

BELL EMITTED
!=
WAKE ACCEPTED
```

## W2–W5 — emission eligibility

A newly requested bell was rejected when the exact assignment projection was:

```text
SATISFIED
RELEASED
BLOCKED_STALE
BLOCKED_OBSOLETE
```

No wake opportunity was retained in those cells.

Therefore:

```text
HISTORICAL ASSIGNMENT
!=
CURRENT BELL ELIGIBILITY
```

and:

```text
ASSIGNED
!=
OUTSTANDING
```

## W6 — bell identity replay

The same exact manual bell bytes were replayed with a different newly requested
opportunity label.

The store returned the already-retained original opportunity relation.

```text
same exact B1
→ same retained W relation
→ no second independently legitimate opportunity
```

Durable counts remained:

```text
manual bells:
1

wake opportunities:
1
```

Therefore:

```text
MANUAL BELL IDENTITY
!=
WAKE OPPORTUNITY IDENTITY
```

while one bell still names at most one exact opportunity relation.

## W7 / W8 — no hidden work selection or queue

Two independently outstanding assignments coexisted.

When the caller named one exact assignment, only that assignment received a
bell.

No second bell was synthesized.

Two separate MAYA assignments also coexisted without the wake source inferring:

```text
first
next
queue order
priority
```

Therefore:

```text
WAKE SOURCE
!=
WORK-SELECTION POLICY

MULTIPLE OUTSTANDING ASSIGNMENTS
!=
QUEUE ORDER

BELL
!=
ROUTER
```

## W9 — constitutional temporal rake

Four exact bells/opportunities were first retained while their assignments were
valid and wake-eligible.

After emission, the assignments independently became:

```text
SATISFIED
RELEASED
BLOCKED_OBSOLETE
BLOCKED_STALE
```

The historical bells and opportunities remained retained.

When each old opportunity was later answered, assignment-aware
`BOUNDED_REENTRY_001`:

```text
loaded exact assignment identity
rederived current assignment projection
observed assignment not OUTSTANDING / wake-eligible
retained WAKE_BLOCKED
returned bounded blocked terminal result
```

and critically did so before calling controller `start_wake()`.

Observed:

```text
controller wake rows created by all four rejected answers:
0
```

All affected seats remained:

```text
occupancy = AVAILABLE
```

No preparation unit or seat successor was produced by those rejected answers.

Therefore:

```text
BELL EMISSION VALIDITY
!=
WAKE ACCEPTANCE VALIDITY

WAKE OPPORTUNITY EXISTS
!=
SEAT MAY ACCEPT IT

REVALIDATE
BEFORE
OCCUPY
```

The old bell history was not rewritten.

## Cross-store limit retained

Assignment projection and controller occupancy remain separate durable stores.

The tested mechanism establishes the ordering:

```text
rederive assignment projection
→ require OUTSTANDING + wake_eligible
→ only then call start_wake()
```

It does not establish a single globally atomic transaction spanning campaign,
selection, preparation, assignment, bell, and controller stores.

Therefore:

```text
REVALIDATED IMMEDIATELY BEFORE OCCUPANCY
!=
GLOBALLY ATOMIC WITH OCCUPANCY
```

That stronger race remains unearned.

## W10 — source stops at the bell

An eligible exact assignment received one manual bell and one exact
wake opportunity.

Assignment-aware bounded reentry then:

```text
revalidated exact assignment
accepted wake
performed exactly one RESOLVE_REFS unit
retained preparation receipt
committed one seat successor
released occupancy
returned dormant
```

The wake source performed no additional action.

An exact assignment satisfaction was then retained separately using the
qualified preparation result.

Projection became:

```text
assignment_state = SATISFIED
wake_eligible = false
```

A new bell attempt against the same exact assignment was rejected.

Therefore:

```text
WAKE SOURCE CREATED OPPORTUNITY
!=
WAKE SOURCE RAN MAYA

PREPARATION RECEIPT
!=
WAKE SOURCE SATISFIED ASSIGNMENT

SATISFIED
→
NEW BELL ELIGIBILITY = NO
```

## Exact basis relation

Bell creation required:

```text
bell_basis_refs
==
basis used to derive current assignment projection
```

and the opportunity Git basis had to be present in that exact bell basis.

Therefore:

```text
CURRENT ELIGIBILITY DECISION
!=
STALE BELL METADATA
```

## Responsibility boundary

The tested wake source may:

```text
read one exact assignment identity
derive its current assignment projection
require OUTSTANDING + wake_eligible
retain one exact manual bell
retain one exact assignment-bound wake opportunity
stop
```

It does not:

```text
choose another assignment
choose seat
choose preparation kind
rank work
infer queue order
occupy seat
run preparation
satisfy assignment
grant authority
change standing
schedule future work
```

## Composition regression

The same successful focused workflow re-executed:

```text
PREPARATION_ASSIGNMENT_001:
PASS

BOUNDED_REENTRY_001:
PASS

LIVE_RUNTIME_PROJECTION_001:
PASS

PREPARATION_001:
PASS

ENVELOPE_SELECTION_001:
PASS

DEVELOPMENT_CAMPAIGN_001:
PASS

GOBLIN_POOL_001:
PASS
```

The separate BOUNDED_REENTRY_001 workflow also passed on the same tested head.

## Bounded result

The executed fixture supports only that:

```text
ONE MANUALLY NAMED
EXACT OUTSTANDING + WAKE-ELIGIBLE ASSIGNMENT

CAN RETAIN:

ONE EXACT MANUAL BELL
+
ONE EXACT ASSIGNMENT-BOUND WAKE OPPORTUNITY

WITHOUT THE WAKE SOURCE
CHOOSING WORK,
CHOOSING A SEAT,
CREATING PRIORITY,
OCCUPYING A SEAT,
RUNNING PREPARATION,
SATISFYING THE ASSIGNMENT,
GRANTING AUTHORITY,
OR CHANGING STANDING,

AND THE TESTED REENTRY ENTRANCE
REVALIDATES THAT ASSIGNMENT
BEFORE CONTROLLER OCCUPANCY.
```

## Nonclaims

This qualification does not establish:

```text
clock behavior
wake policy
due-time semantics
recurrence
scheduler correctness
automatic bell creation
automatic assignment selection
priority policy
queue ordering
global cross-store atomicity
multi-host race closure
execution authority
standing authority
```

## Standing boundary

```text
WAKE_SOURCE_001:
10 / 10 PASS

MANUAL BELL:
YES

EXACT BELL IDENTITY:
YES

EXACT ASSIGNMENT-BOUND OPPORTUNITY:
YES

REVALIDATE BEFORE OCCUPY:
PASS IN TESTED INVALIDATION CELLS

CLOCK:
ABSENT

WAKE POLICY:
ABSENT

SCHEDULER:
UNTOUCHED

AUTOMATIC BELL SOURCE:
NONE

EXECUTION AUTHORITY CREATED:
NONE

STANDING EFFECT:
NONE
```
