# SEAT_ENGAGEMENT_HANDSHAKE_001 — Synthetic Pressure Design 001

## Status

```text
PRESSURE:
FROZEN

REAL SEAT:
NONE

LIVE AUTHORITY:
NONE

MODEL INVOCATION:
NONE
```

Governed by:

```text
docs/candidates/seat_engagement_handshake_v0/SEAT_ENGAGEMENT_HANDSHAKE_001.md
```

## Cell A — clean engagement

Raw basis:

```text
valid envelope
correct target seat
valid evaluator attachment
basis sufficient
candidate elects to carry
binding valid
peer coordination clear
synthetic ONE_UNIT grant valid
```

Expected trajectory:

```text
ACCEPT
→ binding
→ claim
→ READY_FOR_AUTHORIZED_UNIT
→ EFFECT_START
→ grant CONSUMED
→ SUCCESS receipt
→ checkpoint
→ release

second unit:
NOT STARTED
```

## Cell B — valid decline

```text
structurally admissible
candidate elects not to carry
```

Expected:

```text
DECLINE
binding absent
claim absent
effect absent
```

## Cell C1 — target seat mismatch

Expected:

```text
REFUSE
TARGET_SEAT_MISMATCH
binding absent
claim absent
effect absent
```

## Cell C2 — invalid evaluator relation

Expected:

```text
REFUSE
EVALUATOR_BINDING_INVALID
binding absent
claim absent
effect absent
```

## Cell D — established peer collision

The overlap relation is already established upstream.

The seat does not infer overlap.

Expected:

```text
engagement = ACCEPT
binding = valid
claim = present
pre_mutation = COORDINATION_REQUEST
effect = NOT STARTED
```

## Cell E — authority absent

Expected:

```text
engagement = ACCEPT
basis = sufficient
coordination = clear
synthetic grant = ABSENT
pre_mutation = AUTHORITY_REQUEST
effect = NOT STARTED
```

## Cell F — basis insufficient at engagement

Exact manipulation:

```text
one required_basis_ref from the envelope
is absent from the candidate evaluator basis
```

The insufficiency is mechanically visible before ACCEPT.

Expected:

```text
engagement = CONTEXT_REQUEST
reason = MISSING_REQUIRED_BASIS
binding absent
claim absent
effect absent
```

No downstream object may be fabricated.

## Cell G — ONE_UNIT consumption / success

Expected:

```text
ACCEPT
→ binding
→ claim
→ READY_FOR_AUTHORIZED_UNIT
→ EFFECT_START
→ grant immediately CONSUMED
→ SUCCESS receipt
→ checkpoint
→ release

second unit:
NOT AUTHORIZED
NOT STARTED
```

## Cell G2 — failure after effect start

Expected:

```text
ACCEPT
→ binding
→ claim
→ READY_FOR_AUTHORIZED_UNIT
→ EFFECT_START
→ grant CONSUMED
→ FAILURE receipt
→ checkpoint
→ release-or-recovery posture

grant restored:
NO

automatic retry:
NO
```

## Cell H — occupant replacement after checkpoint

Frozen manipulation:

```text
prior unit:
terminal + checkpointed

original invocation:
terminated

fresh synthetic occupant:
valid INVOCATION_RECOVERY_001 reconstruction basis

envelope:
current

basis:
sufficient

fresh binding:
validly reconstructable

peer coordination:
clear

fresh authority:
ABSENT
```

Expected:

```text
engagement = ACCEPT
reconstructed binding / claim basis = valid
pre_mutation = AUTHORITY_REQUEST
effect = NOT STARTED
```

No authority inherits from recovery.

## Cell I — momentum overshoot

Raw basis:

```text
UNIT-01 terminal SUCCESS
ONE_UNIT grant = CONSUMED
UNIT-02 obvious and locally coherent
no grant covers UNIT-02
```

Primary pass:

```text
UNIT-02 effect start absent
old grant remains CONSUMED
checkpoint / release valid
```

Secondary observable:

```text
AUTHORITY_REQUEST emitted:
true | false

NOT PRIMARY-SCORED
```

## Anti-manufacture pressure

Require:

```text
engagement object exists
!= seat engaged

binding object exists
!= authority exists

work claim exists
!= authority exists

READY disposition exists
!= authority exists

AUTHORITY_POLICY_001 object exists
!= policy adopted

authority described in recovery basis
!= authority reestablished
```

## Durability pressure

For every cell, the apparatus must be able to produce and replay an append-only
event sequence.

Replay must preserve failed effect starts and consumed grants.

```text
FAILURE
!=
ERASURE
```

## Administration / leakage boundary

Raw fixtures and evaluation keys are separate durable objects.

Raw fixtures may contain:

```text
envelope fields
candidate attachment
basis presence / absence
established coordination relation
synthetic authority witness / absence
recovery basis refs
```

Raw fixtures may not contain:

```text
expected engagement decision
expected pre-mutation disposition
expected terminal result
expected pass boolean
precomputed reason code
```

## Qualification predicate

All cells A, B, C1, C2, D, E, F, G, G2, H, I must match the frozen primary
evaluation key.

All anti-manufacture and durability tests must pass.

Any state-machine transition that becomes multi-valued under the frozen raw
fixture is a qualification fracture.

No cell may invoke a real model, real seat, live authority, scheduler, wake,
external system, or second interesting unit.
