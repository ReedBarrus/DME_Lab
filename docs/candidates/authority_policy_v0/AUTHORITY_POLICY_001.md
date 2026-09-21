# AUTHORITY_POLICY_001 — Candidate Contract v0

## STATUS

```text
CANDIDATE HELD-OUT AUTHORITY POLICY CONTRACT

MATERIALIZED:
YES

ADOPTED:
NO

ACTIVE POLICY:
NO

AUTHORITY GRANTED BY THIS DOCUMENT:
NONE

IMPLEMENTATION:
NONE

REALIZATION:
NONE
```

This document is a candidate contract for pressure and review.

Its presence in Git does not make the policy active.

```text
POLICY OBJECT EXISTS
!=
POLICY ADOPTED

POLICY ADOPTED
!=
AUTHORITY GRANTED

AUTHORITY GRANTED
!=
AUTHORITY EXERCISED
```

This contract must not be used as evidence that an authority relation exists merely
because the contract describes how such a relation should be represented.

## Frozen repository basis

```text
repository:
ReedBarrus/DME_Lab

main:
8a5321c098b7f3a944e180612cd2e670b20f282e

contract branch origin:
8a5321c098b7f3a944e180612cd2e670b20f282e
```

The current repository lineage already preserves:

```text
interpretation
!=
authorization
!=
execution
!=
semantic promotion
```

and reports Reed as the current Executive authorization point in the existing
candidate authority-spine lineage.

AUTHORITY_POLICY_001 does not broaden, replace, or self-promote that standing.

## Sole policy question

```text
Can DME_Lab represent and negotiate authority as a
temporal, substrate-relative relation

while permitting useful low-risk observation

without silently allowing:

OBSERVE -> WRITE inheritance
VISIBLE GRANT -> ADDRESSEE inheritance
ROLE LABEL -> ROLE OCCUPANCY inheritance
OLD GRANT -> CURRENT GRANT inheritance
CONVENIENCE -> AUTHORITY expansion
POLICY DESCRIPTION -> AUTHORITY CREATION
```

## Foundational authority relation

The candidate authority relation is:

```text
AUTHORITY(t)
=
SUBSTRATE
x
OPERATION
x
SCOPE
x
BASIS
x
ADDRESSEE
x
BINDING
x
LIFETIME
```

This is a contract model for later pressure.

It is not a claim that all existing repository authority is already encoded this
way.

### SUBSTRATE

At minimum:

```text
CONVERSATION
DME_SYSTEM
EXTERNAL
```

A substrate identifies where the relevant consequence or observation lands.

### OPERATION

At minimum:

```text
OBSERVE
WRITE
EXECUTE
```

These operations are not ordered as a universal capability lattice.

For current DME work, however:

```text
OBSERVE
!=
WRITE
!=
EXECUTE
```

and no operation silently implies another.

### SCOPE

Authority is object-relative and purpose-relative.

A scope may bound:

```text
repository
branch
path
object identity
campaign
pressure
work claim
unit
operator
action family
external target
purpose
```

No broad scope may be inferred from a narrower one.

### BASIS

Every authority expansion must carry a traceable basis.

The basis may include:

```text
human grant
governing contract
active envelope
current branch / object coordinate
prior valid authority state
required policy relation
```

A basis is not authority merely because it is cited.

### ADDRESSEE

A grant must identify what relation it addresses, such as:

```text
role
seat
work claim
occupant
invocation
or an explicitly defined composition of these
```

### BINDING

A grant addressed to a role or seat does not automatically establish the current
occupant or invocation that may exercise it.

```text
CAN SEE GRANT
!=
IS ITS ADDRESSEE

ROLE-COMPATIBLE
!=
ROLE-BOUND

ROLE-BOUND
!=
UNIT-BOUND
```

### LIFETIME

Authority is temporal.

```text
AUTHORITY AT t0
!=
AUTHORITY AT t1
```

A lifetime may be bounded by:

```text
ONE_UNIT
ONE_ENVELOPE
UNTIL_RELEASED
EXPLICIT_EXPIRY
BASIS_INVALIDATION
WORK_CLAIM_COMPLETION
```

A completed or invalidated grant does not remain current merely because its
historical object still exists.

## Practical authority projections

The following are useful operating projections over the deeper relation:

```text
CHAT
=
CONVERSATION / WRITE

SYSTEM_READ
=
DME_SYSTEM / OBSERVE

SYSTEM_WRITE
=
DME_SYSTEM / WRITE

EXTERNAL_EFFECT
=
EXTERNAL / WRITE-or-EXECUTE
```

These projections are convenient labels, not the ontology itself.

## Consequence is substrate-relative

Freeze:

```text
CONVERSATIONAL CONSEQUENCE
!=
SYSTEM OBSERVATION
!=
SYSTEM MUTATION
!=
EXTERNAL CONSEQUENCE
```

and:

```text
NON-MUTATING
!=
CONSEQUENCE-FREE
```

System observation may change the observer's epistemic state, consume resources,
produce logs, or change later reasoning without mutating the observed repository
object.

## Proposed DME_Lab default policy v0

THIS SECTION IS A CANDIDATE POLICY TO PRESSURE.

IT IS NOT ACTIVE MERELY BECAUSE THIS FILE EXISTS.

### Conversation

```text
CONVERSATION / WRITE

proposed default:
AVAILABLE
```

Ordinary conversational reasoning and drafting require no DME system mutation.

### DME system observation

```text
DME_SYSTEM / OBSERVE

proposed default:
PRESUMPTIVELY AVAILABLE
when materially useful to ground requested DME work
and no contrary domain contract exists
```

This proposed default exists to avoid turning the human into a repeated
permission bus for ordinary grounding.

Explicit contraction dominates convenience:

```text
CHAT_ONLY
->
DME_SYSTEM / OBSERVE unavailable
DME_SYSTEM / WRITE unavailable
EXTERNAL observation/effect unavailable
```

### DME system write

```text
DME_SYSTEM / WRITE

proposed default:
NOT AMBIENT
```

A system write requires:

```text
explicit bounded grant

OR

previously active,
unexpired,
currently applicable envelope

AND

valid addressee / binding for the attempted unit
```

Freeze:

```text
SYSTEM_READ GRANTED
!=
SYSTEM_WRITE IMPLIED
```

### External observation

```text
EXTERNAL / OBSERVE

proposed default:
POLICY-RELATIVE
```

No universal default is earned by this contract.

### External write / execution

```text
EXTERNAL / WRITE-or-EXECUTE

proposed default:
NOT AMBIENT

requires:
explicit bounded grant
```

## Three scope planes

A future execution envelope should distinguish at least:

### OBSERVATION_SCOPE

What may be read to ground the task?

Example coordinates:

```text
repo
branch
PR
CI receipt
governing contract
runtime projection
specific external observation source
```

### MUTATION_SCOPE

What durable substrate may be changed?

Example coordinates:

```text
branch
paths
objects
allowed mutation kinds
forbidden targets
```

### EXECUTION_SCOPE

What already-materialized capability or authority may actually be exercised?

Example coordinates:

```text
deterministic tests
model invocation
workflow execution
operator call
deployment
external action
```

Freeze:

```text
OBSERVATION SCOPE
DOES NOT CREATE
MUTATION SCOPE

MUTATION SCOPE
DOES NOT CREATE
EXECUTION SCOPE
```

## Authority expansion and contraction

### Expansion

Any expansion beyond current authority requires a traceable relation:

```text
BASIS
ADDRESSEE
SCOPE
GRANT
LIFETIME
```

Freeze:

```text
CONVENIENCE
MAY MOTIVATE
AN AUTHORITY REQUEST

BUT CANNOT
SATISFY IT
```

### Contraction

Authority contraction may occur voluntarily without a fresh grant.

Examples:

```text
SYSTEM_WRITE
->
SYSTEM_READ

SYSTEM_READ
->
CHAT_ONLY
```

A bounded grant may also contract automatically at its frozen completion
boundary.

```text
ONE_UNIT COMPLETE
->
ONE_UNIT WRITE GRANT CONSUMED
```

This contract does not establish a scheduler or automatic expiry mechanism.

## Request operations

The candidate workflow distinguishes three requests.

### CONTEXT_REQUEST

Meaning:

```text
I cannot establish the required proposition or basis
from my currently available information.
```

A context request may be satisfied by:

```text
human-provided context
authorized system observation
qualified durable receipt
other explicitly admissible evidence
```

Freeze:

```text
MISSING INFORMATION
!=
MISSING AUTHORITY
```

### AUTHORITY_REQUEST

Meaning:

```text
I can identify the desired next effect,
but causing it exceeds my current authority.
```

A request must seek the smallest sufficient expansion.

A request is never its own grant.

```text
AUTHORITY REQUESTED
!=
AUTHORITY GRANTED
```

### COORDINATION_REQUEST

Meaning:

```text
I may possess authority in isolation,
but peer ownership, overlapping work,
or unresolved binding makes exercise unsafe or ambiguous.
```

Freeze:

```text
MISSING CONTEXT
!=
MISSING AUTHORITY
!=
MISSING COORDINATION
```

## Candidate AUTHORITY_REQUEST_v0 semantic coordinates

A future materialization may encode at least:

```text
request_id

requesting_role
requesting_seat
requesting_occupant
requesting_invocation

current_authority_refs

requested_expansion:
  substrate
  operation
  observation_scope
  mutation_scope
  execution_scope

reason
minimum_required_scope
requested_lifetime

basis_refs

fallback_if_denied

does_not_request
```

This contract does not freeze serialization or schema yet.

## Candidate AUTHORITY_DECISION_v0 semantic coordinates

A future grant/deny relation may encode at least:

```text
request_id

decision:
  GRANTED
  DENIED
  MODIFIED

grantor_relation
basis_refs

granted_substrate
granted_operation
granted_scope
addressed_to
binding_requirements
lifetime
completion_boundary

explicit_non_grants
```

The existence of an AUTHORITY_DECISION object is not enough.

A later mechanism must establish that the grantor relation itself had standing to
grant the requested authority.

```text
GRANT OBJECT EXISTS
!=
GRANTOR HAD GRANT AUTHORITY
```

## Materialization / activation / execution

Freeze the verbs:

```text
DRAFT
=
construct a representation

FREEZE SEMANTICS
=
declare content stable for bounded review

MATERIALIZE
=
write the object into a durable substrate

ACTIVATE
=
make a durable object operationally current / applicable

EXECUTE
=
exercise the authority or consequence it permits
```

and:

```text
DRAFT
!=
MATERIALIZE
!=
ACTIVATE
!=
EXECUTE
```

A materialized authority object may remain inactive.

```text
AUTHORITY TO WRITE AN AUTHORITY OBJECT
!=
AUTHORITY GRANTED BY THAT OBJECT
```

## Default behavior at an authority membrane

When a next required action exceeds current authority:

```text
DO NOT:
silently expand authority
silently exercise nearby authority
abandon safe work unnecessarily

DO:

1. preserve current safe state
2. classify the deficit:
   CONTEXT
   AUTHORITY
   COORDINATION
3. emit the smallest relevant request
4. state the minimum requested expansion / information
5. state what remains possible without it
6. wait, yield, or continue only permissible work
```

## Provenance and receipts

Any future authority expansion should preserve enough information to reconstruct:

```text
what changed
from what prior authority state
on what basis
for whom
for what scope
for how long
who / what granted it
what did NOT become authorized
```

A receipt records a claimed transition.

```text
RECEIPT EXISTS
!=
TRANSITION VALID
```

Validation remains separately pressureable.

## Protected non-inheritance laws

AUTHORITY_POLICY_001 must preserve:

```text
SYSTEM OBSERVATION
!=
SYSTEM MUTATION

READ GRANT
!=
WRITE GRANT

WRITE GRANT
!=
EXECUTION GRANT

VISIBLE GRANT
!=
ADDRESSED GRANT

ADDRESSED ROLE
!=
CURRENT ROLE BINDING

ROLE BINDING
!=
WORK-UNIT OWNERSHIP

OLD GRANT
!=
CURRENT GRANT

POLICY DEFAULT
!=
SPECIFIC GRANT

REQUEST
!=
GRANT

MATERIALIZED AUTHORITY OBJECT
!=
ACTIVE AUTHORITY

ACTIVE AUTHORITY
!=
AUTHORITY EXERCISED

CONVENIENCE
!=
AUTHORITY
```

## Anti-manufacture boundary

This contract must not manufacture the authority it is designed to govern.

Therefore:

```text
AUTHORITY POLICY DESCRIBES
HOW AUTHORITY MAY BE REPRESENTED / REQUESTED / CHECKED

IT DOES NOT CREATE
A GRANTOR OF LAST RESORT

IT DOES NOT PROVE
WHO MAY GRANT WHAT

IT DOES NOT TURN
POLICY DEFAULTS INTO HISTORICAL FACTS

IT DOES NOT RETROACTIVELY
VALIDATE PRIOR ACTIONS

IT DOES NOT SELF-ACTIVATE
```

Any later adoption or activation requires separate authority and review.

## Claim ceiling

If the future pressure succeeds, the maximum claim is:

```text
Under the frozen tested conditions, the candidate policy can
distinguish bounded observation, mutation, execution, addressee,
binding, lifetime, and request semantics without silently
strengthening the tested authority relation.
```

It does not establish:

```text
general authorization safety
general identity authentication
general role binding
general scheduler safety
general external-action safety
that Reed must remain the permanent Executive
that every existing authority object is valid
that DME_SYSTEM observation is universally low-risk
that policy objects can grant authority merely by existing
```

## Contract boundary

This candidate contract authorizes no implementation and no policy activation.

```text
CONTRACT:
MATERIALIZED FOR REVIEW

POLICY:
NOT ADOPTED

POLICY ACTIVE:
NO

IMPLEMENTATION:
NONE

REALIZATION:
NONE

AUTHORITY EFFECT:
NONE
```

Next legitimate step:

```text
FRESH REVIEW
+
ADVERSARIAL PRESSURE DESIGN REVIEW

NOT:
activation
NOT:
runtime enforcement
NOT:
retroactive authority adjudication
```
