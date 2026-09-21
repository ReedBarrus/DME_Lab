# LANE_LIFECYCLE_DISPOSITION_001 — Candidate Contract v0

## Object

```text
OBJECT_TYPE:
CANDIDATE_CONTRACT

OBJECT_ID:
LANE_LIFECYCLE_DISPOSITION_001

STATUS:
R1-R10 REPAIRED FOR FRESH REVIEW

PRESSURE:
NOT EXECUTED

LIVE_LANE_EFFECT:
NONE
```

## Standing

TWO_LANE_COORDINATION_001 qualified activation prerequisites and pre-mutation
peer coordination, but did not qualify the lifecycle transition by which an
ACTIVE claim and occupant relation become completed, released, or held.

The existing schemas already contain:

```text
claim:
ACTIVE
RELEASED
COMPLETED
BLOCKED

lane:
READY_UNCLAIMED
ACTIVE
HELD
CLOSED
```

This candidate does not add new lifecycle status vocabulary.

Freeze:

```text
STATUS VOCABULARY EXISTS
!=
TRANSITION LAW QUALIFIED
```

## Sole question

Given:

```text
CURRENT OPERATING STATE
+
RAW SOURCE EVIDENCE
+
INDEPENDENTLY ESTABLISHED UPSTREAM RELATIONS
WITH RECOVERABLE BASIS
+
EXPLICIT REQUESTED TRANSITION
```

can a bounded lifecycle controller derive:

```text
TRANSITION ADMISSIBILITY
+
RESULTING CLAIM STATE
+
RESULTING LANE STATE
+
RESULTING OCCUPANT POSTURE
+
REQUIRED CONSERVED DEBT / REFERENCES
```

without:

```text
pre-adjudicating the requested transition,
manufacturing completion,
erasing unresolved debt,
transferring authority,
deleting historical claim identity,
or treating every non-ACTIVE claim as reusable?
```

## Protected distinctions

```text
REQUEST
!=
ADMISSIBILITY
!=
RESULTING STATE

UPSTREAM STANDING
!=
LIFECYCLE VERDICT

REPRESENTABLE RELEASE
!=
HISTORICAL RELEASE ADMISSIBILITY

BLOCKING CONDITION
!=
REQUESTED BLOCKING OUTCOME

CLAIM DISPOSITION
!=
EFFECT ATTRIBUTION

LIFECYCLE ADMISSIBLE
!=
LIVE EXECUTION AUTHORIZED

BLOCKED
!=
TERMINAL

MARK_BLOCKED
!=
OCCUPANT RELEASE

NON_ACTIVE
!=
TERMINAL
!=
REUSABLE

CLAIM STATE
!=
CLAIM DELETED

RELEASED
!=
COMPLETED

COMPLETED
!=
SUCCESSFUL BYTES EXIST

RELEASED
!=
RETROACTIVELY ATTRIBUTED

READY_UNCLAIMED
!=
AUTHORITY AVAILABLE

DISPOSITION RECEIPT EXISTS
!=
DISPOSITION VALID
```

## Three-arrow v0 controller

The only requested transition families qualified by this candidate are:

```text
COMPLETE
RELEASE
MARK_BLOCKED
```

Candidate postcondition geometry:

```text
ACTIVE
├─ COMPLETE ─────→ COMPLETED
│                  lane READY_UNCLAIMED
│                  occupant null
│
├─ RELEASE ──────→ RELEASED
│                  lane READY_UNCLAIMED
│                  occupant null
│
└─ MARK_BLOCKED ─→ BLOCKED
                   lane HELD
                   occupant preserved
```

Every other edge remains unqualified.

Claim-state classes for v0:

```text
EXECUTING:
ACTIVE

HELD / NONTERMINAL:
BLOCKED

TERMINAL + REUSABLE:
RELEASED
COMPLETED
```

Therefore:

```text
NON_ACTIVE
!=
TERMINAL
!=
REUSABLE
```

## Requested transition is operator input

The controller receives an explicit requested transition.

It does not choose operator intent.

```text
REQUESTED_TRANSITION
!=
TRANSITION_ADMISSIBILITY
!=
RESULTING_STATE
```

A request may be:

```text
COMPLETE
RELEASE
MARK_BLOCKED
```

and may still be rejected by the lifecycle law.

## Experimental membrane

Candidate input may contain only:

```text
current operating state
raw source objects
requested transition
qualified upstream relations
with recoverable basis
```

A qualified upstream relation may preserve:

```text
relation_type
standing
basis_ref
producer
version
```

Example:

```text
relation_type:
INVOCATION_EFFECT_ATTRIBUTION

standing:
UNRESOLVED

basis_ref:
<recoverable exact source>

producer/version:
<qualified upstream identity>
```

This is admissible because it is an upstream relation, not a lifecycle verdict.

Forbidden candidate input includes lifecycle-shaped answer fields such as:

```text
completion_admissible = true
release_safe = true
completion_impossible = true
release_not_admissible = true
blocked_is_correct = true
resulting_lane_state = READY_UNCLAIMED
expected_disposition = RELEASED
```

Freeze:

```text
QUALIFIED UPSTREAM RELATION:
ALLOWED

LIFECYCLE-SHAPED ANSWER:
FORBIDDEN
```

The candidate derives:

```text
admissibility
resulting claim state
resulting lane state
resulting occupant posture
required conserved debt / refs
```

The scorer owns:

```text
expected admissibility
expected resulting claim state
expected resulting lane state
expected occupant posture
expected debt preservation
```

## Lifecycle admissibility laws

### COMPLETE

```text
COMPLETE admissible iff:

source claim = ACTIVE

AND

required work-unit relation matches

AND

the frozen completion criterion is satisfied

AND

every upstream relation required by that criterion
has the required standing

AND

no established blocker forbids completion
```

If admissible:

```text
claim:
ACTIVE → COMPLETED

lane:
ACTIVE → READY_UNCLAIMED

occupant:
non-null → null

required unresolved refs:
retained according to the completion criterion
```

COMPLETE is a lifecycle verdict only.

```text
COMPLETION ADMISSIBLE
!=
LIVE COMPLETION EXECUTION AUTHORIZED
```

### RELEASE

```text
RELEASE admissible iff:

source claim = ACTIVE

AND

no currently effect-bearing unfinished unit
requires ACTIVE ownership to remain conserved

AND

required historical / unresolved refs
can be retained in disposition evidence
```

If admissible:

```text
claim:
ACTIVE → RELEASED

lane:
ACTIVE → READY_UNCLAIMED

occupant:
non-null → null

required historical / unresolved refs:
retained
```

RELEASE relinquishes future ownership or reservation without asserting valid
completion of the bounded objective by the named invocation.

```text
RELEASED
!=
COMPLETED

RELEASED
!=
RETROACTIVELY ATTRIBUTED

RELEASE
!=
ERASURE
```

### MARK_BLOCKED

```text
MARK_BLOCKED admissible iff:

source claim = ACTIVE

AND

an established blocking relation exists

AND

that blocking relation has recoverable basis
```

If admissible:

```text
claim:
ACTIVE → BLOCKED

lane:
ACTIVE → HELD

occupant:
PRESERVED
```

Freeze:

```text
BLOCKED
!=
TERMINATED

BLOCKED
!=
REUSABLE

BLOCKED
!=
AUTOMATICALLY RESUMABLE

MARK_BLOCKED
!=
OCCUPANT RELEASE
```

Resume semantics remain undefined and out of scope.

## Lifecycle disposition terminology

Use:

```text
LIFECYCLE DISPOSITION:
evaluation of COMPLETE | RELEASE | MARK_BLOCKED

TERMINAL DISPOSITION:
COMPLETED | RELEASED

NONTERMINAL HOLD DISPOSITION:
BLOCKED
```

Do not use generic "terminal disposition" language for BLOCKED.

## Candidate disposition receipt

A lifecycle transition should retain a separate durable object rather than
encoding all semantics into a scalar status.

Candidate shape:

```text
LANE_CLAIM_DISPOSITION_v0

disposition_id
claim_id
lane_id

requested_transition
admissible

claim_status_before
claim_status_after

lane_status_before
lane_status_after

occupant_binding_before
occupant_binding_after

basis_head
reason_code

work_basis_ref
qualified_upstream_relation_refs[]
unresolved_refs[]

authority_effect = NONE
execution_effect = NONE
integration_effect = NONE
```

This remains a pressureable candidate shape, not a frozen schema.

```text
DISPOSITION RECEIPT PRESENT
!=
DISPOSITION VALID
```

The receipt may cite exact qualified upstream relation identities, but may not
replace the controller's lifecycle derivation with a precomputed answer.

## Reusable-lane invariant

A lane may report READY_UNCLAIMED only when:

```text
claim status ∈ {RELEASED, COMPLETED}

AND

occupant_binding = null

AND

required lifecycle disposition evidence is reachable
```

Therefore these states are invalid:

```text
claim ACTIVE
+
lane READY_UNCLAIMED
+
occupant null
```

```text
claim BLOCKED
+
lane READY_UNCLAIMED
```

```text
claim BLOCKED
+
lane HELD
+
occupant null
```

The retained file may still be named:

```text
coordination/active_work_claim.json
```

for v0 compatibility.

```text
PATH NAME SAYS ACTIVE
!=
CLAIM STATUS IS ACTIVE
```

## Historical Lane-B specimen

Current historical specimen:

```text
branch:
lane-b-recovery-continuity-v0

head:
41316921b211c1daf75c9b71b8147e0eb67d372d

claim:
SEAT_ENGAGEMENT_HANDSHAKE_001-LANE_B-CLAIM-001

declared invocation:
SEAT_ENGAGEMENT_HANDSHAKE_001-WORKSHOP-INVOCATION-001

candidate result:
green

effect attribution:
UNRESOLVED
```

This specimen establishes that a RELEASE-shaped outcome is representable.

It does not establish that live historical RELEASE is admissible.

```text
REPRESENTABLE RELEASE PATH
!=
HISTORICAL LANE-B RELEASE ADMISSIBILITY
```

A synthetic RELEASE pressure may model:

```text
ACTIVE → RELEASED
lane ACTIVE → READY_UNCLAIMED
occupant non-null → null
unresolved provenance ref retained
```

without claiming:

```text
claim COMPLETED
original invocation caused all candidate effects
historical authority restored
historical ambiguity resolved
live Lane B may now be mutated
```

## No automatic expiry

```text
INVOCATION APPEARS GONE
!=
CLAIM AUTO-RELEASED
```

A lifecycle disposition requires an explicit requested transition and a valid
admissibility derivation.

## Authority and effect non-inheritance

Every lifecycle disposition object preserves:

```text
authority_effect = NONE
execution_effect = NONE
integration_effect = NONE
```

Any candidate lifecycle disposition that manufactures authority, execution, or
integration effect is invalid.

```text
LIFECYCLE DISPOSITION
!=
AUTHORITY GRANT
```

## Claim ceiling

A passing future pressure may establish only:

```text
Under the frozen tested synthetic conditions,
the three-arrow lifecycle controller can derive
admissibility and branch-specific postconditions for
COMPLETE, RELEASE, and MARK_BLOCKED
from raw operating state plus qualified upstream relations,
while preserving claim identity, unresolved debt,
occupant posture, reusable-lane invariants,
and authority non-effects.
```

It does not establish:

```text
historical Lane-B release admissibility
live Lane-B release
effect provenance
general lease safety
crash recovery
authenticated occupants
scheduler safety
automatic lifecycle management
resume semantics for BLOCKED
general authority policy
```

## Current terminal posture

```text
CONTRACT REPAIR:
MATERIALIZED

PRESSURE:
UNEXECUTED

LIVE LANE EFFECT:
NONE

HISTORICAL LANE-B RELEASE:
NOT AUTHORIZED

NEXT:
FRESH REVIEW
```
