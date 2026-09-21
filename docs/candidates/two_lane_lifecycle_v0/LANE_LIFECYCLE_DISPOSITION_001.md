# LANE_LIFECYCLE_DISPOSITION_001 — Candidate Contract v0

## Object

```text
OBJECT_TYPE:
CANDIDATE_CONTRACT

OBJECT_ID:
LANE_LIFECYCLE_DISPOSITION_001

STATUS:
MATERIALIZED FOR REVIEW

PRESSURE:
NOT EXECUTED

LIVE_LANE_EFFECT:
NONE
```

## Standing

TWO_LANE_COORDINATION_001 qualified activation prerequisites and pre-mutation
peer coordination, but did not qualify the terminal transition by which an
active claim and occupant relation are disposed.

The existing schemas already contain terminal values. This candidate does not
add new terminal status vocabulary unless pressure requires it.

## Sole question

Can an ACTIVE two-lane work claim be durably transitioned to an existing
terminal claim state and can its lane become mechanically reusable or held,
without silently asserting completion, erasing unresolved debt, transferring
authority, or deleting the historical claim?

## Protected distinctions

```text
CLAIM TERMINAL != CLAIM DELETED
RELEASED != COMPLETED
COMPLETED != SUCCESSFUL BYTES EXIST
RELEASED != FAILURE
BLOCKED != ACTIVE
LANE READY_UNCLAIMED != AUTHORITY AVAILABLE
OCCUPANT RELEASED != WORK HISTORY ERASED
CLAIM DISPOSITION != EFFECT ATTRIBUTION
CLAIM DISPOSITION != AUTHORITY GRANT
TERMINAL RECEIPT != AUTOMATIC LANE RELEASE
```

## Existing vocabularies retained

```text
claim status:
ACTIVE
RELEASED
COMPLETED
BLOCKED

lane status:
READY_UNCLAIMED
ACTIVE
HELD
CLOSED
```

## Candidate transition semantics

### COMPLETED

Use only when the governing bounded work relation has sufficient evidence to
establish valid completion of the claim under its own claim ceiling.

```text
OUTPUT EXISTS != CLAIM COMPLETED
```

### RELEASED

The claim relinquishes future ownership / reservation of its declared operating
surface without asserting that its bounded objective was validly completed by
the named invocation.

This is the intended terminal semantics for the historical Lane-B specimen.

```text
RELEASED = NO LONGER ACTIVE
RELEASED != COMPLETED
RELEASED != RETROACTIVELY ATTRIBUTED
```

### BLOCKED

The claim cannot currently proceed and should not continue effect-bearing work.
The expected lane posture for an unresolved blocking condition is HELD.

### CLOSED

CLOSED remains a lane-retirement state, not the ordinary end of one work unit.

```text
WORK UNIT TERMINAL != LANE RETIRED
```

## Candidate disposition receipt

A terminal transition should retain a separate durable object rather than
encoding all semantics into the claim status scalar.

Candidate shape:

```text
LANE_CLAIM_DISPOSITION_v0

disposition_id
claim_id
lane_id
claim_status_before
claim_status_after
lane_status_before
lane_status_after
occupant_binding_before
occupant_binding_after
basis_head
disposition_kind
reason_code
terminal_work_ref
unresolved_refs[]
authority_effect = NONE
execution_effect = NONE
integration_effect = NONE
```

This shape is pressureable and not yet a frozen schema.

```text
DISPOSITION RECEIPT PRESENT
!=
DISPOSITION VALID
```

The transition must be mechanically checked against source claim / manifest
state.

## Reusable-lane invariant

A lane may report READY_UNCLAIMED only when:

```text
occupant_binding = null
current retained claim status != ACTIVE
terminal claim / disposition evidence remains reachable
no lifecycle rule requires HELD
```

The retained file may still be named coordination/active_work_claim.json for
v0 compatibility.

```text
PATH NAME SAYS ACTIVE
!=
CLAIM STATUS IS ACTIVE
```

## Historical Lane-B intended application

Current specimen:

```text
claim:
SEAT_ENGAGEMENT_HANDSHAKE_001-LANE_B-CLAIM-001

declared invocation:
SEAT_ENGAGEMENT_HANDSHAKE_001-WORKSHOP-INVOCATION-001

candidate result:
green

effect attribution:
historically unresolved
```

Therefore the candidate lifecycle relation must permit:

```text
ACTIVE → RELEASED
lane ACTIVE → READY_UNCLAIMED
occupant binding non-null → null
unresolved provenance reference retained
```

without claiming:

```text
claim COMPLETED
original invocation caused all candidate effects
historical authority restored
historical ambiguity resolved
```

## No automatic expiry

```text
INVOCATION APPEARS GONE
!=
CLAIM AUTO-RELEASED
```

A terminal disposition requires an explicit admissible transition.

## Claim ceiling

A passing pressure may establish only that the tested lane/claim representation
can move from ACTIVE operating state to tested existing terminal states while
preserving historical claim identity, unresolved references, and authority
non-effects.

It does not establish general lease safety, crash recovery, authenticated
occupants, effect provenance, scheduler safety, or automatic lifecycle
management.
