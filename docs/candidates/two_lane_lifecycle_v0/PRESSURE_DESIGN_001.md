# LANE_LIFECYCLE_DISPOSITION_001 — Pressure Design 001

## Object

```text
OBJECT_TYPE:
PRESSURE_DESIGN

OBJECT_ID:
LANE_LIFECYCLE_DISPOSITION_001_PRESSURE_001

STATUS:
R1-R10 REPAIRED FOR FRESH REVIEW

EXECUTION:
NOT AUTHORIZED
```

## Governing contract

```text
docs/candidates/two_lane_lifecycle_v0/
LANE_LIFECYCLE_DISPOSITION_001.md
```

## Administration boundary

Synthetic fixtures only.

No fixture may mutate live Lane A or Lane B.

No pressure execution is authorized by this repair.

Candidate input may contain only:

```text
current operating state
raw source objects
requested transition
qualified upstream relations
with recoverable basis
```

The candidate must derive:

```text
admissibility
resulting claim state
resulting lane state
resulting occupant posture
required conserved debt / refs
```

The scorer alone owns:

```text
expected admissibility
expected resulting claim state
expected resulting lane state
expected occupant posture
expected debt preservation
```

Freeze:

```text
RAW LIFECYCLE BASIS
!=
EXPECTED DISPOSITION

UPSTREAM STANDING
!=
LIFECYCLE VERDICT

QUALIFIED UPSTREAM RELATION:
ALLOWED

LIFECYCLE-SHAPED ANSWER:
FORBIDDEN
```

## Closed requested transition vocabulary

Only:

```text
COMPLETE
RELEASE
MARK_BLOCKED
```

Every other requested transition is outside the v0 qualified surface.

## Frozen transition law

### COMPLETE

Admissible iff:

```text
source claim = ACTIVE

required work-unit relation matches

frozen completion criterion satisfied

every upstream relation required by that criterion
has required standing

no established blocker forbids completion
```

Expected postcondition when admissible:

```text
claim = COMPLETED
lane = READY_UNCLAIMED
occupant_binding = null
required refs conserved
```

### RELEASE

Admissible iff:

```text
source claim = ACTIVE

no currently effect-bearing unfinished unit
requires ACTIVE ownership to remain conserved

required historical / unresolved refs
can be retained
```

Expected postcondition when admissible:

```text
claim = RELEASED
lane = READY_UNCLAIMED
occupant_binding = null
required unresolved refs conserved
```

### MARK_BLOCKED

Admissible iff:

```text
source claim = ACTIVE

an established blocking relation exists

blocking relation has recoverable basis
```

Expected postcondition when admissible:

```text
claim = BLOCKED
lane = HELD
occupant_binding = PRESERVED
```

Freeze:

```text
BLOCKED
!=
TERMINAL

MARK_BLOCKED
!=
OCCUPANT RELEASE
```

## Raw fixture vocabulary

Raw fixtures may contain:

```text
claim status
lane status
occupant binding
requested transition

bounded-unit source object
completion criterion source object
unfinished effect-bearing unit source object
historical/unresolved reference objects
blocking relation object

qualified upstream relation:
  relation_type
  standing
  basis_ref
  producer
  version
```

Raw fixtures may not contain:

```text
completion_admissible
release_safe
release_not_admissible
completion_impossible
blocked_is_correct
operator-intent conclusion disguised as raw state
release/completion verdict prose
expected claim state
expected lane state
expected occupant posture
expected pass
expected lifecycle verdict
```

## R1 — request does not determine admissibility

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant bound

requested_transition = COMPLETE

completion criterion source:
NOT SATISFIED
```

Expected:

```text
requested_transition preserved = COMPLETE
admissible = false
prior claim = ACTIVE
prior lane = ACTIVE
prior occupant preserved
```

Freeze:

```text
REQUEST
!=
ADMISSIBILITY
!=
RESULTING STATE
```

## R2 — upstream standing does not encode lifecycle verdict

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant bound

requested_transition = RELEASE

qualified upstream relation:
  relation_type = INVOCATION_EFFECT_ATTRIBUTION
  standing = UNRESOLVED
  basis_ref = exact recoverable source
  producer/version = frozen upstream identity

no unfinished effect-bearing unit requiring ACTIVE ownership

unresolved provenance ref:
present and retainable
```

Expected:

```text
candidate consumes UNRESOLVED as upstream standing
candidate independently derives RELEASE admissibility
claim = RELEASED
lane = READY_UNCLAIMED
occupant = null
unresolved provenance ref retained
```

The fixture must not contain:

```text
release_safe = true
release_admissible = true
```

## R3 — representable release is not live historical release adjudication

Use a synthetic fixture shaped like the historical Lane-B representation:

```text
claim shape:
SEAT_ENGAGEMENT_HANDSHAKE_001-LANE_B-CLAIM-001-like

requested_transition:
RELEASE

attribution relation:
UNRESOLVED

unresolved provenance ref:
present
```

Expected synthetic result may be RELEASED only from the frozen synthetic raw
facts.

The cell must not assert:

```text
historical Lane B release is admissible
historical Lane B should be mutated
historical effect attribution is resolved
```

Freeze:

```text
REPRESENTABLE RELEASE
!=
HISTORICAL RELEASE ADMISSIBILITY
```

## R4 — blocking evidence does not precompute MARK_BLOCKED

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant bound

requested_transition = MARK_BLOCKED

qualified blocking relation:
  relation_type = PEER_OWNERSHIP_UNRESOLVED
  standing = ESTABLISHED
  basis_ref = exact recoverable source
  producer/version = frozen upstream identity
```

Expected:

```text
admissible = true
claim = BLOCKED
lane = HELD
occupant preserved
```

The raw fixture must not contain:

```text
blocked_is_correct = true
mark_blocked_admissible = true
```

## R5 — BLOCKED is nonterminal

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant = OCCUPANT-X

requested_transition = MARK_BLOCKED

valid established blocker
```

Expected:

```text
claim = BLOCKED
lane = HELD
occupant = OCCUPANT-X
terminal = false
reusable = false
```

## R6 — MARK_BLOCKED preserves occupant

Same raw blocking basis as R5.

Adversarial candidate output:

```text
claim = BLOCKED
lane = HELD
occupant = null
```

Expected:

```text
INVALID LIFECYCLE RESULT
```

Freeze:

```text
MARK_BLOCKED
!=
OCCUPANT RELEASE
```

## R7 — transition law is derived, not copied from expected output

The apparatus must derive admissibility from the frozen law using raw source
objects and qualified upstream relations.

Required anti-cheat:

```text
evaluation key is not passed to candidate

raw fixture contains no lifecycle-shaped verdict fields

changing the scorer's expected verdict
does not change candidate derivation
```

At minimum pressure:

```text
COMPLETE:
one completion prerequisite absent
→ inadmissible

RELEASE:
unfinished effect-bearing unit requires ACTIVE ownership
→ inadmissible

MARK_BLOCKED:
no established blocking relation
→ inadmissible
```

## R8 — lifecycle vs terminal terminology

Pressure result vocabulary must distinguish:

```text
LIFECYCLE DISPOSITION:
COMPLETE | RELEASE | MARK_BLOCKED evaluation

TERMINAL RESULT:
COMPLETED | RELEASED

NONTERMINAL HOLD RESULT:
BLOCKED
```

Any scorer or report that classifies BLOCKED as terminal is invalid.

## R9 — branch-specific occupant posture

For valid requested transitions:

```text
COMPLETE:
claim COMPLETED
lane READY_UNCLAIMED
occupant null

RELEASE:
claim RELEASED
lane READY_UNCLAIMED
occupant null

MARK_BLOCKED:
claim BLOCKED
lane HELD
occupant preserved
```

Generic logic:

```text
ANY lifecycle disposition
→ occupant null
```

must fail pressure.

## R10 — reusable lane invariant

A lane may be READY_UNCLAIMED only if:

```text
claim status ∈ {RELEASED, COMPLETED}

AND

occupant_binding = null

AND

required lifecycle disposition evidence is reachable
```

Required negative cells:

### D1 — ACTIVE claim cannot be reusable

```text
claim = ACTIVE
lane = READY_UNCLAIMED
occupant = null
```

Expected:

```text
INVALID LIFECYCLE STATE
```

### D2 — BLOCKED claim cannot be READY_UNCLAIMED

```text
claim = BLOCKED
lane = READY_UNCLAIMED
occupant = OCCUPANT-X
```

Expected:

```text
INVALID LIFECYCLE STATE
```

### D3 — BLOCKED / HELD cannot lose occupant

```text
claim = BLOCKED
lane = HELD
occupant = null
```

Expected:

```text
INVALID LIFECYCLE STATE
```

Freeze:

```text
NON_ACTIVE
!=
TERMINAL
!=
REUSABLE
```

## Additional bounded cells

These preserve useful earlier pressure while conforming to the repaired membrane.

### A — valid completion

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant bound

requested_transition = COMPLETE

work-unit relation:
MATCHES

completion criterion source:
SATISFIED

required upstream completion relations:
all required standing present

established blockers:
none
```

Expected:

```text
admissible = true
claim = COMPLETED
lane = READY_UNCLAIMED
occupant = null
history retained
authority effect = NONE
```

### B — release without completion attribution

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant bound

requested_transition = RELEASE

effect attribution upstream relation:
UNRESOLVED
with recoverable basis

unfinished effect-bearing unit requiring ACTIVE ownership:
absent

unresolved provenance ref:
present and retainable
```

Expected:

```text
admissible = true
claim = RELEASED
lane = READY_UNCLAIMED
occupant = null
unresolved provenance preserved
claim COMPLETED = false
```

This remains synthetic and does not adjudicate live Lane B.

### C — unresolved blocker

Raw basis:

```text
claim = ACTIVE
lane = ACTIVE
occupant = OCCUPANT-X

requested_transition = MARK_BLOCKED

qualified blocking relation:
ESTABLISHED
with recoverable basis
```

Expected:

```text
admissible = true
claim = BLOCKED
lane = HELD
occupant = OCCUPANT-X
```

### E — silent deletion

Candidate omits historical claim object after a valid lifecycle evaluation.

Expected:

```text
INVALID LIFECYCLE RESULT
```

Freeze:

```text
RELEASE
!=
DELETE HISTORY
```

### F — release erases unresolved debt

Raw basis contains a required unresolved provenance reference.

Candidate RELEASE result omits it.

Expected:

```text
INVALID LIFECYCLE RESULT
```

### G — release manufactures completion

Raw basis:

```text
requested_transition = RELEASE
effect attribution = UNRESOLVED
completion criterion not established
release prerequisites otherwise satisfied
```

Candidate emits:

```text
claim = COMPLETED
```

Expected:

```text
INVALID LIFECYCLE RESULT
```

### H — lifecycle disposition manufactures authority

Any lifecycle result attempts:

```text
authority_effect != NONE
or
execution_effect != NONE
or
integration_effect != NONE
```

Expected:

```text
INVALID
```

Freeze:

```text
ANY LIFECYCLE DISPOSITION
MANUFACTURES AUTHORITY
→ INVALID
```

### I — old claim resurrection

After:

```text
claim = RELEASED | COMPLETED
lane = READY_UNCLAIMED
occupant = null
```

a new work unit attempts to change the old claim back to ACTIVE without a fresh
binding / claim identity.

Expected:

```text
INVALID
```

Freeze:

```text
REACTIVATION
!=
RESURRECT OLD CLAIM

NEW WORK UNIT
→
NEW CURRENT BINDING / CLAIM RELATION
```

## Resulting disposition evidence

A candidate result may retain neutral fields such as:

```text
work_basis_ref
qualified_upstream_relation_refs[]
unresolved_refs[]
```

Do not use a generic field named `terminal_work_ref` for MARK_BLOCKED.

Required neutral rule:

```text
work_basis_ref
!=
proof of terminality
```

## Qualification target

A future positive pressure requires:

```text
R1-R10:
all mechanically pass

additional cells A-I:
all mechanically pass

raw fixtures:
no lifecycle answer leakage

qualified upstream relations:
recoverable basis preserved

resulting claim artifact:
retained

lifecycle disposition evidence:
retained

unresolved refs:
preserved when required

BLOCKED:
never terminalized
never made reusable
never loses occupant

authority effect:
NONE

execution effect:
NONE

integration effect:
NONE
```

No live-lane mutation is part of this pressure.

## Current posture

```text
PRESSURE DESIGN:
REPAIRED

PRESSURE EXECUTION:
NOT AUTHORIZED

FIXTURE FREEZE:
NOT EXECUTED

LIVE LANE EFFECT:
NONE

NEXT:
FRESH REVIEW
```
