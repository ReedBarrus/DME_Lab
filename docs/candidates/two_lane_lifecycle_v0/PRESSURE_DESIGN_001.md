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

Every controller-consumed semantic predicate must be supplied through exactly
one of the two classes frozen in the governing contract:

```text
RAW_INPUT

or

QUALIFIED_UPSTREAM_STANDING
```

No third category exists.

```text
TYPED
!=
QUALIFIED

PREDICATE PRESENT
!=
PREDICATE ESTABLISHED

ABSENCE CLAIM
!=
ABSENCE OF INPUT

SOURCE BASIS
!=
QUALIFIED STANDING
```

The exhaustive input predicate registry is P01-P18 in
`LANE_LIFECYCLE_DISPOSITION_001.md`.

A future apparatus must reject administration when:

```text
a controller-consumed predicate is not in P01-P18

a RAW_INPUT predicate lacks its exact raw basis

a QUALIFIED_UPSTREAM_STANDING witness lacks:
  relation_type
  standing
  basis_ref
  producer
  version

basis_ref is unrecoverable

producer/version is not qualified to establish the named relation_type

a negative standing is inferred from missing input rather than explicitly
derived or witnessed
```

The qualified producer relation is apparatus configuration, not a cell verdict:
producer/version must resolve to a frozen qualification receipt establishing the
relation types it may produce.

The candidate derives:

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
P01 SOURCE_CLAIM_STATUS_IS_ACTIVE

P02 SOURCE_LANE_STATUS_IS_ACTIVE

P03 SOURCE_OCCUPANT_BINDING is non-null

P04 REQUESTED_TRANSITION = COMPLETE

P05 WORK_UNIT_CORRESPONDENCE_MATCHES

P06 COMPLETION_CRITERION_RAW_TERMS_SATISFIED

every required P07 REQUIRED_COMPLETION_UPSTREAM_STANDING witness
has its frozen required standing

P08 COMPLETION_BLOCKER_STATUS = NONE_ESTABLISHED
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
P01 SOURCE_CLAIM_STATUS_IS_ACTIVE

P02 SOURCE_LANE_STATUS_IS_ACTIVE

P03 SOURCE_OCCUPANT_BINDING is non-null

P04 REQUESTED_TRANSITION = RELEASE

P09 ACTIVE_OWNERSHIP_EFFECT_STATUS =
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP

P10 REQUIRED_CONSERVED_REFERENCE_SET
derived from raw source objects

P11 REQUIRED_REFERENCE_RETENTION_STATUS = RETAINABLE
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
P01 SOURCE_CLAIM_STATUS_IS_ACTIVE

P02 SOURCE_LANE_STATUS_IS_ACTIVE

P03 SOURCE_OCCUPANT_BINDING is non-null

P04 REQUESTED_TRANSITION = MARK_BLOCKED

P12 MARK_BLOCKED_BLOCKING_RELATION standing = ESTABLISHED

P12 basis_ref recoverable
and producer/version qualified
```

Expected postcondition when admissible:

```text
claim = BLOCKED
lane = HELD
occupant_binding = exact supplied non-null P03 identity PRESERVED
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

RAW_INPUT fixtures may contain exact objects such as:

```text
current claim object
current lane manifest
transition-request object
work-unit binding object
bounded-unit / envelope identity objects
completion-criterion object
raw terminal receipt / work-evidence objects
historical / unresolved reference objects
disposition evidence reference + exact retained object
terminal historical claim object
attempted current claim object
fresh work-unit binding object
```

They may not contain semantic summary fields such as:

```text
MATCHES
SATISFIED
NOT_SATISFIED
blocker_none
unfinished_unit_absent
retainable
release_safe
completion_admissible
expected lifecycle verdict
```

Those semantics must either be mechanically derived from the raw objects under
P01-P18 or supplied as QUALIFIED_UPSTREAM_STANDING.

QUALIFIED_UPSTREAM_STANDING fixtures must use the exact witness shape:

```text
relation_type
standing
basis_ref
producer
version
```

and must pass producer/version qualification for that relation_type.

## R1 — request does not determine admissibility

RAW_INPUT:

```text
P01:
claim object.status = ACTIVE

P02:
lane manifest.status = ACTIVE

P03:
lane manifest.occupant_binding = OCCUPANT-X

P04:
transition request.requested_transition = COMPLETE

P05 raw correspondence basis:
binding.envelope_id = ENV-01
binding.bounded_unit_id = UNIT-01
claim.envelope_id = ENV-01
claim.bounded_unit_id = UNIT-01

P06 raw completion basis:
criterion.required_receipt_id = RECEIPT-01
criterion.required_outcome = SUCCESS

receipt.receipt_id = RECEIPT-01
receipt.bounded_unit_id = UNIT-01
receipt.outcome = FAILURE
```

QUALIFIED_UPSTREAM_STANDING:

```text
P08:
relation_type = COMPLETION_BLOCKER_STATUS
standing = NONE_ESTABLISHED
basis_ref = <recoverable blocker-status basis>
producer = <qualified producer>
version = <qualified version>
```

Controller derivation:

```text
P05 = true by exact identity equality
P06 = false because raw receipt outcome != required outcome
P08 = NONE_ESTABLISHED by qualified standing
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

RAW_INPUT:

```text
P01:
claim object.status = ACTIVE

P02:
lane manifest.status = ACTIVE

P03:
lane manifest.occupant_binding = OCCUPANT-X

P04:
transition request.requested_transition = RELEASE

P10:
source claim / source object carries unresolved_ref_id = PROV-REF-01
```

QUALIFIED_UPSTREAM_STANDING:

```text
P09:
relation_type = ACTIVE_OWNERSHIP_EFFECT_STATUS
standing = NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
basis_ref = <recoverable effect-ownership basis>
producer = <qualified producer>
version = <qualified version>

P11:
relation_type = REFERENCE_RETENTION_STATUS
standing = RETAINABLE
basis_ref = <recoverable retention basis for PROV-REF-01>
producer = <qualified producer>
version = <qualified version>

P18:
relation_type = INVOCATION_EFFECT_ATTRIBUTION
standing = UNRESOLVED
basis_ref = <recoverable provenance basis>
producer = <qualified producer>
version = <qualified version>
```

Expected:

```text
candidate consumes UNRESOLVED only as qualified upstream standing
candidate independently derives RELEASE admissibility from P01 + P09 + P10 + P11
claim = RELEASED
lane = READY_UNCLAIMED
occupant = null
PROV-REF-01 retained
```

The fixture must not contain a RELEASE verdict.

## R3 — representable release is not live historical release adjudication

Use a synthetic fixture shaped like the historical Lane-B representation, but
supply the complete RELEASE basis through the closed membrane.

RAW_INPUT:

```text
P01:
synthetic claim object.status = ACTIVE

P02:
synthetic lane manifest.status = ACTIVE

P03:
synthetic lane manifest.occupant_binding = OCCUPANT-X

P04:
transition request.requested_transition = RELEASE

P10:
synthetic source object carries unresolved_ref_id = PROV-REF-01
```

QUALIFIED_UPSTREAM_STANDING:

```text
P09:
relation_type = ACTIVE_OWNERSHIP_EFFECT_STATUS
standing = NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
basis_ref = <recoverable synthetic effect-ownership basis>
producer = <qualified producer>
version = <qualified version>

P11:
relation_type = REFERENCE_RETENTION_STATUS
standing = RETAINABLE
basis_ref = <recoverable synthetic retention basis for PROV-REF-01>
producer = <qualified producer>
version = <qualified version>

P18:
relation_type = INVOCATION_EFFECT_ATTRIBUTION
standing = UNRESOLVED
basis_ref = <recoverable synthetic provenance basis>
producer = <qualified producer>
version = <qualified version>
```

The synthetic claim identity / source shape may mirror the historical specimen,
but no live historical object is consumed as a RELEASE verdict.

Expected synthetic result may be RELEASED only from P01 + P09 + P10 + P11.
P18 remains conserved provenance debt and does not itself authorize RELEASE.

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

P12 QUALIFIED_UPSTREAM_STANDING:
  relation_type = MARK_BLOCKED_BLOCKING_STATUS
  standing = ESTABLISHED
  basis_ref = <recoverable peer-ownership blocking basis>
  producer = <qualified producer>
  version = <qualified version>
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

P12 QUALIFIED_UPSTREAM_STANDING:
relation_type = MARK_BLOCKED_BLOCKING_STATUS
standing = ESTABLISHED
basis_ref = <recoverable blocking basis>
producer = <qualified producer>
version = <qualified version>
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
P06 derives false from exact raw criterion + receipt mismatch
→ inadmissible

RELEASE:
P09 qualified standing =
UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP
→ inadmissible

MARK_BLOCKED:
P12 qualified standing = NONE_ESTABLISHED
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

RAW_INPUT:

```text
P14:
current claim.status = ACTIVE
→ CLAIM_STATUS_IS_REUSABLE_TERMINAL_CLASS derives false

P15:
current lane manifest.occupant_binding = null

P13:
explicit disposition_evidence_refs[] raw object supplied for current state
```

Current lane manifest:

```text
lane.status = READY_UNCLAIMED
```

Expected:

```text
INVALID LIFECYCLE STATE
```

### D2 — BLOCKED claim cannot be READY_UNCLAIMED

RAW_INPUT:

```text
P14:
current claim.status = BLOCKED
→ CLAIM_STATUS_IS_REUSABLE_TERMINAL_CLASS derives false

P15:
current lane manifest.occupant_binding = OCCUPANT-X

current lane manifest.status = READY_UNCLAIMED
```

Expected:

```text
INVALID LIFECYCLE STATE
```

### D3 — BLOCKED / HELD cannot lose occupant

RAW_INPUT:

```text
P14:
current claim.status = BLOCKED
→ CLAIM_STATUS_IS_REUSABLE_TERMINAL_CLASS derives false

P15:
current lane manifest.occupant_binding = null

current lane manifest.status = HELD
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

RAW_INPUT:

```text
P01 claim.status = ACTIVE
P02 lane.status = ACTIVE
P03 occupant_binding = OCCUPANT-X
P04 requested_transition = COMPLETE

P05 exact work-unit correspondence:
binding / claim / envelope / bounded-unit identities all equal

P06 exact criterion + raw receipt:
criterion requires RECEIPT-01 / UNIT-01 / SUCCESS
raw receipt is RECEIPT-01 / UNIT-01 / SUCCESS
```

QUALIFIED_UPSTREAM_STANDING:

```text
P07:
each completion-required semantic relation supplies:
relation_type
required standing
recoverable basis_ref
qualified producer
qualified version

P08:
relation_type = COMPLETION_BLOCKER_STATUS
standing = NONE_ESTABLISHED
basis_ref = <recoverable blocker-status basis>
producer = <qualified producer>
version = <qualified version>
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

RAW_INPUT:

```text
P01 claim.status = ACTIVE
P02 lane.status = ACTIVE
P03 occupant_binding = OCCUPANT-X
P04 requested_transition = RELEASE

P10:
source object contains unresolved_ref_id = PROV-REF-01
```

QUALIFIED_UPSTREAM_STANDING:

```text
P09:
relation_type = ACTIVE_OWNERSHIP_EFFECT_STATUS
standing = NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
basis_ref = <recoverable effect-ownership basis>
producer = <qualified producer>
version = <qualified version>

P11:
relation_type = REFERENCE_RETENTION_STATUS
standing = RETAINABLE
basis_ref = <recoverable retention basis for PROV-REF-01>
producer = <qualified producer>
version = <qualified version>

P18:
relation_type = INVOCATION_EFFECT_ATTRIBUTION
standing = UNRESOLVED
basis_ref = <recoverable provenance basis>
producer = <qualified producer>
version = <qualified version>
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

RAW_INPUT:

```text
P01 claim.status = ACTIVE
P02 lane.status = ACTIVE
P03 occupant_binding = OCCUPANT-X
P04 requested_transition = MARK_BLOCKED
```

QUALIFIED_UPSTREAM_STANDING:

```text
P12:
relation_type = MARK_BLOCKED_BLOCKING_STATUS
standing = ESTABLISHED
basis_ref = <recoverable blocking basis>
producer = <qualified producer>
version = <qualified version>
```

Expected:

```text
admissible = true
claim = BLOCKED
lane = HELD
occupant = OCCUPANT-X
```

### E — silent deletion

Controller input:

```text
reuse any fully classified admissible fixture above
without adding a semantic predicate
```

Scorer-only adversarial mutation:

```text
candidate output omits the retained historical claim object
```

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

Controller input uses a fully classified RELEASE basis.

RAW_INPUT:

```text
P10:
source object contains unresolved_ref_id = PROV-REF-01
```

QUALIFIED_UPSTREAM_STANDING:

```text
P11:
relation_type = REFERENCE_RETENTION_STATUS
standing = RETAINABLE
basis_ref = <recoverable retention basis for PROV-REF-01>
producer = <qualified producer>
version = <qualified version>
```

Scorer-only adversarial mutation:

```text
candidate RELEASE output omits PROV-REF-01
```

Expected:

```text
INVALID LIFECYCLE RESULT
```

### G — release manufactures completion

Controller input uses the same fully classified RELEASE basis as Cell B:

```text
P01 RAW_INPUT
P02 RAW_INPUT
P03 RAW_INPUT
P04 RAW_INPUT = RELEASE
P09 QUALIFIED_UPSTREAM_STANDING
P10 RAW_INPUT
P11 QUALIFIED_UPSTREAM_STANDING
P18 QUALIFIED_UPSTREAM_STANDING
```

No COMPLETE-specific completion predicate is supplied or consumed for this
RELEASE evaluation.

Adversarial candidate output:

```text
claim = COMPLETED
```

Expected scorer result:

```text
INVALID LIFECYCLE RESULT
```

The invalidity follows from the frozen RELEASE postcondition law, not from an
unqualified statement that completion was or was not established.

### H — lifecycle disposition manufactures authority

Controller input:

```text
reuse any fully classified fixture above
without adding a semantic predicate
```

Scorer-only adversarial mutation attempts:

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

RAW_INPUT:

```text
P14:
terminal historical claim.status = RELEASED or COMPLETED

P15:
lane manifest.occupant_binding = null

P13:
exact disposition evidence ref resolves to retained exact disposition object

P16:
terminal historical claim.claim_id
+
attempted current claim.claim_id

P17:
fresh work-unit binding object, if any,
+
attempted current claim identities
```

Controller derivation:

```text
if P16 says the old claim identity is reused
and P17 does not establish a distinct fresh binding/current-claim relation,
the attempted resurrection is invalid
```

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

## F12 source-state causal-effect pressure

These cells are held-out design cells only.

They are not executed by this repair.

Each cell starts from an otherwise valid branch baseline and changes exactly one
registered source-state predicate.

Freeze:

```text
PREDICATE REGISTERED
!=
PREDICATE CAUSALLY EFFECTIVE

HELD-OUT SOURCE-GUARD INTERVENTION
=
ONE SOURCE GUARD CHANGED
+
ALL UNRELATED BRANCH PREREQUISITES CONSERVED
```

### N1 — COMPLETE rejects non-ACTIVE source lane

Baseline:

```text
Cell A valid COMPLETE basis
```

Independent intervention:

```text
P01:
claim.status = ACTIVE
UNCHANGED

P02:
lane.status = HELD
CHANGED from ACTIVE

P03:
occupant_binding = OCCUPANT-X
UNCHANGED / non-null

P04:
requested_transition = COMPLETE

P05:
exact work-unit correspondence = true by raw derivation

P06:
raw completion criterion terms = satisfied by raw derivation

P07:
every criterion-required qualified upstream standing from Cell A
UNCHANGED and valid

P08:
COMPLETION_BLOCKER_STATUS = NONE_ESTABLISHED
UNCHANGED and qualified
```

Expected:

```text
admissible = false
blocking_source_predicate = P02 SOURCE_LANE_STATUS_IS_ACTIVE
no COMPLETE postcondition emitted
```

Required causal proof:

```text
same baseline with P02 = ACTIVE
→ COMPLETE admissible

same basis with only P02 != ACTIVE
→ COMPLETE inadmissible
```

### N2 — RELEASE rejects non-ACTIVE source lane

Baseline:

```text
Cell B valid RELEASE basis
```

Independent intervention:

```text
P01:
claim.status = ACTIVE
UNCHANGED

P02:
lane.status = HELD
CHANGED from ACTIVE

P03:
occupant_binding = OCCUPANT-X
UNCHANGED / non-null

P04:
requested_transition = RELEASE

P09:
ACTIVE_OWNERSHIP_EFFECT_STATUS =
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP
UNCHANGED and qualified

P10:
required conserved reference set
UNCHANGED from raw source

P11:
REFERENCE_RETENTION_STATUS = RETAINABLE
UNCHANGED and qualified

P18:
INVOCATION_EFFECT_ATTRIBUTION = UNRESOLVED
UNCHANGED when present in the baseline
```

Expected:

```text
admissible = false
blocking_source_predicate = P02 SOURCE_LANE_STATUS_IS_ACTIVE
no RELEASE postcondition emitted
```

Required causal proof:

```text
same baseline with P02 = ACTIVE
→ RELEASE admissible

same basis with only P02 != ACTIVE
→ RELEASE inadmissible
```

### N3 — MARK_BLOCKED rejects non-ACTIVE source lane

Baseline:

```text
Cell C valid MARK_BLOCKED basis
```

Independent intervention:

```text
P01:
claim.status = ACTIVE
UNCHANGED

P02:
lane.status = HELD
CHANGED from ACTIVE

P03:
occupant_binding = OCCUPANT-X
UNCHANGED / non-null

P04:
requested_transition = MARK_BLOCKED

P12:
relation_type = MARK_BLOCKED_BLOCKING_STATUS
standing = ESTABLISHED
basis_ref = <same recoverable blocking basis as baseline>
producer = <same qualified producer>
version = <same qualified version>
```

Expected:

```text
admissible = false
blocking_source_predicate = P02 SOURCE_LANE_STATUS_IS_ACTIVE
no BLOCKED / HELD postcondition emitted
```

Required causal proof:

```text
same baseline with P02 = ACTIVE
→ MARK_BLOCKED admissible

same basis with only P02 != ACTIVE
→ MARK_BLOCKED inadmissible
```

### N4 — MARK_BLOCKED rejects null source occupant

Baseline:

```text
Cell C valid MARK_BLOCKED basis
```

Independent intervention:

```text
P01:
claim.status = ACTIVE
UNCHANGED

P02:
lane.status = ACTIVE
UNCHANGED

P03:
occupant_binding = null
CHANGED from OCCUPANT-X

P04:
requested_transition = MARK_BLOCKED

P12:
relation_type = MARK_BLOCKED_BLOCKING_STATUS
standing = ESTABLISHED
basis_ref = <same recoverable blocking basis as baseline>
producer = <same qualified producer>
version = <same qualified version>
```

Expected:

```text
admissible = false
blocking_source_predicate = P03 SOURCE_OCCUPANT_BINDING
no BLOCKED / HELD postcondition emitted
```

Required causal proof:

```text
same baseline with non-null P03
→ MARK_BLOCKED admissible
→ exact P03 identity preserved after transition

same basis with only P03 = null
→ MARK_BLOCKED inadmissible
```

D3 remains unchanged:

```text
claim BLOCKED
lane HELD
occupant null
→ INVALID
```

N4 rejects the invalid source before transition, while D3 independently rejects
the prohibited resulting posture.

### F12 branch audit

```text
COMPLETE

required predicates:
P01 P02 P03 P04 P05 P06
every criterion-required P07
P08

source guards:
P01 = true
P02 = true
P03 != null

result:
COMPLETED
READY_UNCLAIMED
occupant null

mechanical source blockers:
P01 / P02 / P03

D1-D3:
result compatible


RELEASE

required predicates:
P01 P02 P03 P04 P09 P10 P11
P18 where supplied for conserved provenance standing

source guards:
P01 = true
P02 = true
P03 != null

result:
RELEASED
READY_UNCLAIMED
occupant null
required refs conserved

mechanical source blockers:
P01 / P02 / P03

D1-D3:
result compatible


MARK_BLOCKED

required predicates:
P01 P02 P03 P04 P12

source guards:
P01 = true
P02 = true
P03 != null

result:
BLOCKED
HELD
occupant = exact P03 source identity

mechanical source blockers:
P01 / P02 / P03

D1-D3:
exact occupant preservation prevents D3
HELD posture prevents D2
BLOCKED is never treated as reusable terminal state
```

All registered source-state predicates required by each branch are therefore
explicit members of its admissibility conjunction and have held-out causal
interventions.

## F13 exclusive request-dispatch pressure

These are held-out pressure-design cells only.

They are not executed by this repair.

The pressure target is branch-selection causality, not merely whether the final
administration is accepted or rejected.

Freeze:

```text
REQUEST TOKEN VALID
!=
REQUEST SELECTS BRANCH

BRANCH PREREQUISITES SATISFIED
!=
BRANCH REQUESTED

SCORER REJECTS WRONG OUTPUT
!=
CONTROLLER DISPATCH QUALIFIED

CAUSALLY EFFECTIVE
!=
BOOLEAN-CONJUNCTION MEMBER
```

### Dispatch observation surface

Every future N5 administration must expose a mechanical dispatch trace before
branch admissibility is scored:

```text
requested_transition
selected_branch
excluded_branches[]
branch_predicates_consulted[]
branch_admissibility
resulting_state_if_admitted
```

The scorer must verify:

```text
selected_branch
=
requested_transition

excluded_branches
=
the other two lifecycle branches
```

A scorer rejection after the wrong branch ran does not qualify dispatch.

### N5A — COMPLETE baseline, P04 changed to RELEASE

Construct one synthetic input set with:

```text
shared source guards:
P01 = true
P02 = true
P03 = non-null

COMPLETE-supporting predicates:
P05 = true by raw derivation
P06 = true by raw derivation
required P07 qualified
P08 = NONE_ESTABLISHED qualified

RELEASE-supporting predicates:
P09 =
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP qualified
P10 exact conserved reference set derived
P11 = RETAINABLE qualified
P18 = UNRESOLVED qualified where conserved provenance standing is included
```

Baseline:

```text
P04 = COMPLETE

selected_branch:
COMPLETE

result:
derived only from COMPLETE law
```

Independent intervention:

```text
CHANGE ONLY:
P04 COMPLETE → RELEASE

ALL OTHER INPUTS:
BYTE / SEMANTICALLY IDENTICAL
```

Required observation:

```text
requested_transition = RELEASE

selected_branch = RELEASE

excluded_branches =
COMPLETE
MARK_BLOCKED

COMPLETE branch predicates may remain present in the input set
but COMPLETE MUST NOT be operative

RELEASE admissibility/result:
derived only from RELEASE law
```

Because the synthetic input set deliberately contains a valid RELEASE basis,
the expected admitted result is:

```text
claim RELEASED
lane READY_UNCLAIMED
occupant null
```

This demonstrates dispatch directly rather than depending on missing-input
rejection.

### N5B — RELEASE baseline, P04 changed to MARK_BLOCKED

Construct one synthetic input set with:

```text
shared source guards:
P01 = true
P02 = true
P03 = OCCUPANT-X

RELEASE-supporting predicates:
P09 =
NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP qualified
P10 exact conserved reference set derived
P11 = RETAINABLE qualified

MARK_BLOCKED-supporting predicate:
P12 MARK_BLOCKED_BLOCKING_STATUS = ESTABLISHED qualified
```

Baseline:

```text
P04 = RELEASE

selected_branch:
RELEASE

result:
derived only from RELEASE law
```

Independent intervention:

```text
CHANGE ONLY:
P04 RELEASE → MARK_BLOCKED

ALL OTHER INPUTS:
BYTE / SEMANTICALLY IDENTICAL
```

Required observation:

```text
requested_transition = MARK_BLOCKED

selected_branch = MARK_BLOCKED

excluded_branches =
COMPLETE
RELEASE

RELEASE branch predicates remain present
but RELEASE MUST NOT be operative

MARK_BLOCKED admissibility/result:
derived only from MARK_BLOCKED law
```

Because the unchanged input set deliberately contains a valid P12 witness, the
expected admitted result is:

```text
claim BLOCKED
lane HELD
occupant = exact OCCUPANT-X source identity
```

### N5C — MARK_BLOCKED baseline, P04 changed to COMPLETE

Construct one synthetic input set with:

```text
shared source guards:
P01 = true
P02 = true
P03 = OCCUPANT-X

MARK_BLOCKED-supporting predicate:
P12 MARK_BLOCKED_BLOCKING_STATUS = ESTABLISHED qualified

COMPLETE-supporting predicates:
P05 = true by raw derivation
P06 = true by raw derivation
required P07 qualified

P08 COMPLETION_BLOCKER_STATUS =
FORBIDS_COMPLETION
qualified
```

Baseline:

```text
P04 = MARK_BLOCKED

selected_branch:
MARK_BLOCKED

MARK_BLOCKED admitted from P12
```

Independent intervention:

```text
CHANGE ONLY:
P04 MARK_BLOCKED → COMPLETE

ALL OTHER INPUTS:
BYTE / SEMANTICALLY IDENTICAL
```

Required observation:

```text
requested_transition = COMPLETE

selected_branch = COMPLETE

excluded_branches =
RELEASE
MARK_BLOCKED

MARK_BLOCKED's valid P12 witness remains present
but MARK_BLOCKED MUST NOT be operative
```

The newly selected COMPLETE branch must evaluate its own unchanged predicates.
Because P08 = FORBIDS_COMPLETION, the expected COMPLETE result is:

```text
admissible = false
blocking predicate = P08
no COMPLETE postcondition emitted
```

The required dispatch result is still a pass because the previously supported
MARK_BLOCKED branch was excluded and COMPLETE alone became operative.

### Generalized P04 intervention property

For every administration:

```text
INPUT_SET = I
P04 = X
→ selected_branch = X
```

For the same non-P04 input set:

```text
INPUT_SET = I
P04 = Y
X != Y
→ selected_branch = Y
```

Therefore:

```text
CHANGE ONLY P04
→
CHANGE OPERATIVE BRANCH
```

No unrelated predicate mutation is required.

### F13 branch-dispatch audit

```text
P04 = COMPLETE

selected:
COMPLETE law

excluded:
RELEASE
MARK_BLOCKED

admissibility source:
P01 P02 P03 P04 P05 P06
required P07
P08

result if admitted:
COMPLETED
READY_UNCLAIMED
occupant null


P04 = RELEASE

selected:
RELEASE law

excluded:
COMPLETE
MARK_BLOCKED

admissibility source:
P01 P02 P03 P04 P09 P10 P11
P18 conserved where supplied but not sufficient by itself

result if admitted:
RELEASED
READY_UNCLAIMED
occupant null


P04 = MARK_BLOCKED

selected:
MARK_BLOCKED law

excluded:
COMPLETE
RELEASE

admissibility source:
P01 P02 P03 P04 P12

result if admitted:
BLOCKED
HELD
exact source occupant identity preserved
```

Any controller path where:

```text
P04 = X
operative branch = Y
X != Y
```

is an automatic pressure failure.

### F11 regression

```text
ALL CONTROLLER INPUT:
RAW_INPUT
XOR
QUALIFIED_UPSTREAM_STANDING

NO THIRD CATEGORY:
PRESERVED
```

P04 remains RAW_INPUT. The derived `selected_branch` is internal controller
state, not a new input category or nineteenth semantic predicate.

### F12 regression

```text
P01:
still causally effective

P02:
still causally effective

P03:
still causally effective

N1-N4:
unchanged

source-state geometry:
unchanged
```

F13 adds dispatch causality; it does not weaken any source-state guard.

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

## F11 consumed-predicate audit

This pressure design consumes exactly the P01-P18 registry from the governing
contract.

```text
P01  SOURCE_CLAIM_STATUS_IS_ACTIVE                    RAW_INPUT
P02  SOURCE_LANE_STATUS_IS_ACTIVE                     RAW_INPUT
P03  SOURCE_OCCUPANT_BINDING                          RAW_INPUT
P04  REQUESTED_TRANSITION                             RAW_INPUT
P05  WORK_UNIT_CORRESPONDENCE_MATCHES                 RAW_INPUT
P06  COMPLETION_CRITERION_RAW_TERMS_SATISFIED         RAW_INPUT
P07  REQUIRED_COMPLETION_UPSTREAM_STANDING             QUALIFIED_UPSTREAM_STANDING
P08  COMPLETION_BLOCKER_STATUS                         QUALIFIED_UPSTREAM_STANDING
P09  ACTIVE_OWNERSHIP_EFFECT_STATUS                    QUALIFIED_UPSTREAM_STANDING
P10  REQUIRED_CONSERVED_REFERENCE_SET                  RAW_INPUT
P11  REQUIRED_REFERENCE_RETENTION_STATUS               QUALIFIED_UPSTREAM_STANDING
P12  MARK_BLOCKED_BLOCKING_RELATION                    QUALIFIED_UPSTREAM_STANDING
P13  LIFECYCLE_DISPOSITION_EVIDENCE_REACHABLE          RAW_INPUT
P14  CLAIM_STATUS_IS_REUSABLE_TERMINAL_CLASS           RAW_INPUT
P15  REUSABLE_OCCUPANT_BINDING_IS_NULL                 RAW_INPUT
P16  OLD_CLAIM_IDENTITY_REUSED_FOR_NEW_UNIT            RAW_INPUT
P17  FRESH_BINDING_CLAIM_RELATION_PRESENT              RAW_INPUT
P18  INVOCATION_EFFECT_ATTRIBUTION_STANDING             QUALIFIED_UPSTREAM_STANDING
```

No cell may add a bare semantic summary outside this list.

Scorer-only output predicates remain outside the candidate membrane.

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
