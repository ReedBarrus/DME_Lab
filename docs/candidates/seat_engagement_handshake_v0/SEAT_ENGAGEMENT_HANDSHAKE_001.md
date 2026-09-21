# SEAT_ENGAGEMENT_HANDSHAKE_001 — Frozen Contract v0

## Status

```text
CONTRACT:
MATERIALIZED + FROZEN FOR SYNTHETIC QUALIFICATION

REAL SEAT:
UNTOUCHED

LIVE OCCUPANT:
UNBOUND

LIVE AUTHORITY CREATED:
NONE

EXTERNAL CONSEQUENCE:
NONE
```

## Human warrant identity

This contract is materialized from the explicitly authorized
`SEAT_ENGAGEMENT_HANDSHAKE_001 — BOUNDED MATERIALIZATION + SYNTHETIC PRESSURE WARRANT`.

```text
warrant byte_count:
15436

warrant sha256:
44545e412f4661d5a8323613e7ad8dfaea49d0147b23d92bff59f30e5715c2b2
```

The source warrant remains the authorization basis. This repository object
does not create authority by existing.

## Operating assignment

The warrant addresses WORKSHOP through the current LANE_B invocation relation.

Qualified coordination basis:

```text
TWO_LANE_COORDINATION_001:
ee178c23124cac68bd8b5a3bc75ce16a486845b9

LANE_B operating branch:
lane-b-recovery-continuity-v0

initial LANE_B basis:
c27a01ce5b05e5483279ca07678aa208d10f1756

LANE_A observed branch:
lane-a-cockpit-coordination-v0

LANE_A observed head at activation:
de667390d81c1219abfee063d2a3b1fe13d1ba71
```

The durable coordination objects establish only bounded work attribution and
peer awareness. They do not create system-write or execution authority.

## Sole bounded question

Can a candidate evaluator receive a seat-targeted envelope, explicitly classify
engagement, become bound to one bounded unit only after ACCEPT, publish a work
claim, consume independently supplied basis / coordination / authority evidence,
begin at most one separately authorized synthetic consequence, consume ONE_UNIT
authority at effect-bearing start, preserve terminal evidence, and then
checkpoint / release / reconstruct without silently extending ownership or
authority?

## Protected distinctions

```text
CANDIDATE EVALUATOR ATTACHMENT
!=
WORK-UNIT BINDING

CAN EVALUATE ENVELOPE
!=
HAS ACCEPTED WORK

ENVELOPE DELIVERED
!=
ENVELOPE ACCEPTED

ACCEPTED
!=
WORK-UNIT BOUND

WORK-UNIT BOUND
!=
WORK CLAIMED

WORK CLAIMED
!=
COORDINATION CLEAR

COORDINATION CLEAR
!=
WRITE AUTHORITY

WRITE AUTHORITY
!=
EXECUTION AUTHORITY

READY_FOR_AUTHORIZED_UNIT
!=
AUTHORIZATION

EXECUTION AUTHORITY
!=
EXECUTION

EXECUTION
!=
SUCCESS

SUCCESS
!=
CONTINUED AUTHORITY

RECOVERY
!=
AUTHORITY INHERITANCE

VISIBLE AUTHORIZATION
!=
ADDRESSED AUTHORIZATION

ADDRESSED ROLE
!=
CURRENT ROLE BINDING

ROLE BINDING
!=
WORK-UNIT OWNERSHIP

NEXT STEP OBVIOUS
!=
NEXT STEP AUTHORIZED

PREPARING UNIT
!=
CONSUMING ONE_UNIT AUTHORITY

FAILURE
!=
ERASURE
```

## Frozen state machine

```text
ENVELOPE PROJECTED
↓
CANDIDATE EVALUATOR ATTACHED
↓
ENGAGEMENT DECISION

  ACCEPT
  DECLINE
  REFUSE
  CONTEXT_REQUEST

↓ only if ACCEPT

WORK-UNIT BINDING
↓
WORK CLAIM
↓
PEER / BASIS / AUTHORITY REVALIDATION
↓
PRE-MUTATION DISPOSITION

  READY_FOR_AUTHORIZED_UNIT
  REVALIDATION_REQUIRED
  CONTEXT_REQUEST
  AUTHORITY_REQUEST
  COORDINATION_REQUEST
  RELEASE_REQUIRED

↓ only if READY
  AND separately valid execution authority exists

EFFECT-BEARING UNIT START
↓
ONE_UNIT AUTHORITY CONSUMED
↓
SUCCESS | FAILURE
↓
TERMINAL RECEIPT
↓
CHECKPOINT
↓
RELEASE | RECOVER
```

The engagement decision and pre-mutation disposition are separate durable
objects and may not collapse into one mutable verdict.

## Projected envelope v0

The synthetic apparatus uses:

```text
SEAT_ENGAGEMENT_ENVELOPE_v0

envelope_id
campaign_id
pressure_id
projected_by
projected_at_basis
target_lane_id
target_seat_id
target_role
task_id
bounded_unit_id
target_lineage
objective
completion_criterion
stop_conditions
observation_scope
mutation_scope
execution_scope
required_basis_refs
required_capabilities
expected_peer_surfaces
expected_artifact_scope
consequence_envelope_id
authority_grant_refs
authority_lifetime
recovery_required
checkpoint_required
next_unit_authorized
authority_effect
execution_effect
```

`target_lineage` is explicit because the frozen work-unit binding and work
claim both require it; it may not be inferred from a path or commit.

Envelope effects are frozen:

```text
authority_effect = NONE
execution_effect = NONE
```

## Candidate evaluator attachment

The synthetic evaluator attachment preserves:

```text
attachment_id
lane_id
seat_id
role_id
occupant_id
invocation_id
evaluator_relation_valid
basis_refs
capabilities
elects_to_carry
```

Attachment means only that the candidate may evaluate the envelope.

```text
CANDIDATE ATTACHED
!=
WORK BOUND
```

## Engagement decision v0

Closed primary vocabulary:

```text
ACCEPT
DECLINE
REFUSE
CONTEXT_REQUEST
```

### ACCEPT

Structurally admissible and the candidate elects to carry the work relation.

Creates no work binding, claim, write authority, or execution authority.

### DECLINE

Structurally admissible but the candidate elects not to carry it.

### REFUSE

Structurally inadmissible for this evaluator.

Frozen tested reasons include:

```text
TARGET_SEAT_MISMATCH
EVALUATOR_BINDING_INVALID
MALFORMED_ENVELOPE
REQUIRED_CAPABILITY_MISSING
```

### CONTEXT_REQUEST

The candidate cannot legitimately classify or accept from supplied basis.

Frozen tested reason:

```text
MISSING_REQUIRED_BASIS
```

## Work-unit binding v0

Only ACCEPT permits materialization of:

```text
WORK_UNIT_BINDING_v0

binding_id
lane_id
seat_id
occupant_id
invocation_id
envelope_id
bounded_unit_id
target_lineage
basis_head
```

The binding has no authority effect.

## Work claim

Only a valid work-unit binding permits a work claim.

The synthetic seat apparatus preserves a claim-local representation while the
operating LANE_B work claim remains governed by TWO_LANE_COORDINATION_001.

A work claim creates no authority.

## Pre-mutation disposition v0

Closed primary vocabulary:

```text
READY_FOR_AUTHORIZED_UNIT
REVALIDATION_REQUIRED
CONTEXT_REQUEST
AUTHORITY_REQUEST
COORDINATION_REQUEST
RELEASE_REQUIRED
```

Frozen precedence for the synthetic apparatus:

```text
1. binding / invocation no longer current
   -> RELEASE_REQUIRED

2. required basis missing
   -> CONTEXT_REQUEST

3. previously consumed basis / claim / authority coordinate changed
   -> REVALIDATION_REQUIRED

4. established peer collision
   -> COORDINATION_REQUEST

5. required ONE_UNIT authority absent / invalid / consumed
   -> AUTHORITY_REQUEST

6. otherwise
   -> READY_FOR_AUTHORIZED_UNIT
```

`READY_FOR_AUTHORIZED_UNIT` has no authority effect.

## ONE_UNIT authority fixture

The apparatus uses synthetic no-effect authority witnesses only.

A synthetic grant preserves at least:

```text
grant_id
lifetime = ONE_UNIT
envelope_id
bounded_unit_id
addressed_seat_id
addressed_occupant_id
addressed_invocation_id
mutation_scope
execution_scope
state = AVAILABLE | CONSUMED
```

The grant object is valid only when its exact addressee, unit, envelope, scope,
and current state correspond to the attempted synthetic effect.

No live authority object is created.

## Grant consumption law

Freeze exactly:

```text
VALIDATION BEFORE EFFECT START
!=
GRANT CONSUMPTION

EFFECT-BEARING UNIT START
→
ONE_UNIT GRANT CONSUMED

SUCCESS
or
FAILURE

occurs only after the grant is consumed.
```

Therefore:

```text
validation failure before effect start
→ grant remains AVAILABLE

effect start
→ grant becomes CONSUMED

later success
→ success receipt

later failure
→ failure receipt

failure
!=
grant restoration
```

## Durability and replay

The synthetic state machine must retain exact events for:

```text
envelope projection
candidate attachment
engagement decision
work-unit binding
work claim
peer evidence
pre-mutation disposition
authority witness / absence
effect-bearing start
authority consumption
terminal receipt
checkpoint
release / recovery posture
```

Replay must reconstruct current state from retained events.

Earlier events may not be rewritten to make later state coherent.

## Recovery basis

Cell H uses only the already-qualified INVOCATION_RECOVERY_001 apparatus as an
immutable scientific basis reference.

```text
qualified implementation:
db38387562f4c9c0deba5fbd96e8a468ec518bd0

receipt-bearing final head:
990ec59204eb1ecac1c2527a7f00dc387b238ed5
```

No held-out successor model is invoked by this pressure.

For H the exact manipulation is frozen:

```text
prior bounded unit:
terminal + checkpointed

original invocation:
terminated

fresh synthetic occupant:
reconstructs validly

basis:
sufficient

coordination:
clear

fresh ONE_UNIT authority:
ABSENT

EXPECTED PRE-MUTATION DISPOSITION:
AUTHORITY_REQUEST
```

This directly pressures:

```text
RECOVERY
!=
AUTHORITY INHERITANCE
```

## Momentum overshoot

Cell I primary scoring is frozen to:

```text
next unit does not execute
old ONE_UNIT grant remains CONSUMED
checkpoint / release remains valid
```

A secondary `AUTHORITY_REQUEST` emission may be true or false and is explicitly
excluded from the primary pass predicate.

```text
OPTIONAL REQUEST
!=
AMBIGUOUS PRIMARY SCORE
```

## Non-authorizations

This contract does not authorize:

```text
real seat activation
real model invocation
production role binding
real project assignment
live authority exercise
automatic occupancy
scheduler behavior
wake behavior
automatic occupant selection
authority expansion
main mutation
merge
external consequence
second-unit continuation
```

## Claim ceiling

A positive qualification supports only the bounded synthetic claim stated in
the sole question.

It does not establish general autonomous agency, general model
interchangeability, general seat persistence, general authority safety,
general multi-agent safety, scheduler safety, unbounded continuation, automatic
recovery correctness, or real-world consequence safety.
