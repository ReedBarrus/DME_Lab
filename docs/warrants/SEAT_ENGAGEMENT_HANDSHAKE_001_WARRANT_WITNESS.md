# SEAT_ENGAGEMENT_HANDSHAKE_001 — Human Warrant Witness

## Status

```text
WARRANT OCCURRENCE:
PRE-EXISTING CONVERSATIONAL HUMAN AUTHORIZATION

THIS FILE:
DURABLE WITNESS / RECONSTRUCTION AID

AUTHORITY EFFECT OF RECORDING:
NONE

RETROACTIVE GRANT:
NONE

WARRANT EXPANSION:
NONE
```

This artifact records the bounded warrant that was issued conversationally
before WORKSHOP activated LANE_B.

```text
WARRANT RECORD
!=
WARRANT GRANT

RECORD CREATED LATER
!=
AUTHORITY CREATED LATER
```

The authoritative historical fact is that the human authorization preceded
WORKSHOP's current Lane-B claim. This file exists so future repo-only
reconstruction need not rely on commit author identity or conversational memory
to recover the warrant's declared limits.

## Addressee

```text
WORKSHOP acting through an explicitly established
LANE_B occupant / invocation relation.
```

Protected distinction:

```text
VISIBLE WARRANT
!=
ADDRESSED WARRANT
```

Before mutation, the acting invocation must establish that it is the current
bounded actor for LANE_B under this warrant.

## Purpose

Materialize, mechanically pressure, repair if earned, and qualify the smallest
seat-engagement state machine required to connect:

- projected work envelopes
- candidate evaluators
- engagement decisions
- work-unit binding
- work claims
- two-lane coordination
- authority revalidation
- one bounded consequence
- receipts
- checkpoint / release / recovery

without activating a real seat or exercising live project authority.

## Frozen transition target

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
RECEIPT
↓
CHECKPOINT
↓
RELEASE | RECOVER
```

## Core non-collapse laws

```text
CANDIDATE EVALUATOR ATTACHMENT != WORK-UNIT BINDING
CAN EVALUATE ENVELOPE != HAS ACCEPTED WORK
ENVELOPE DELIVERED != ENVELOPE ACCEPTED
ACCEPTED != WORK-UNIT BOUND
WORK-UNIT BOUND != WORK CLAIMED
WORK CLAIMED != COORDINATION CLEAR
COORDINATION CLEAR != WRITE AUTHORITY
WRITE AUTHORITY != EXECUTION AUTHORITY
READY_FOR_AUTHORIZED_UNIT != AUTHORIZATION
EXECUTION AUTHORITY != EXECUTION
EXECUTION != SUCCESS
SUCCESS != CONTINUED AUTHORITY
RECOVERY != AUTHORITY INHERITANCE
VISIBLE AUTHORIZATION != ADDRESSED AUTHORIZATION
ADDRESSED ROLE != CURRENT ROLE BINDING
ROLE BINDING != WORK-UNIT OWNERSHIP
NEXT STEP OBVIOUS != NEXT STEP AUTHORIZED
```

## Grant-consumption law

```text
PREPARING UNIT
!=
CONSUMING ONE_UNIT AUTHORITY

EFFECT-BEARING UNIT START
→
ONE_UNIT AUTHORITY CONSUMED
```

A later success or failure receipt does not determine whether the one-unit grant
was consumed.

## Required Lane-B activation sequence

Before repository mutation under the warrant:

```text
reconstruct current LANE_B
→ verify bounded lane availability
→ establish current invocation relation
→ publish exact ACTIVE work claim
→ consume current relevant LANE_A claim state
→ retain peer coordination cursor
→ run qualified pre-mutation guard
→ separately establish warrant-bounded SYSTEM_WRITE
→ mutate only inside the allowed surface
```

If peer claim, binding, branch basis, or coordination is unresolved:

```text
STOP AND REPORT
```

## Authorized repository mutation surface

```text
docs/candidates/seat_engagement_handshake_v0/**
schemas/seat_engagement_*
tools/seat_engagement_handshake_v0.py
tests/runtime/test_seat_engagement_handshake_v0.py
.github/workflows/seat-engagement-handshake-001.yml
minimum LANE_B coordination objects required to establish / retain
the bounded work claim and peer cursor
```

Read-only reconstruction may inspect relevant Lane A/B coordinates, governing
coordination qualification, Invocation Recovery, Authority Policy, seat/cursor
contracts, and receipts.

## Authorized execution

```text
deterministic synthetic state-machine apparatus
+
qualification tests
```

## Not authorized

```text
real model successor invocation
real seat engagement
real production role transfer
live project work assignment
live authority exercise
live Cockpit consequence
external effect
main mutation
merge
LANE_A mutation
scheduler behavior
wake behavior
automatic occupant selection
automatic authority expansion
second interesting unit merely because first succeeded
```

## Pressure target

The warrant requires synthetic pressure covering at least:

```text
A   clean engagement
B   valid decline
C1  target-seat mismatch → REFUSE
C2  invalid evaluator binding → REFUSE
D   established peer collision → COORDINATION_REQUEST
E   absent authority → AUTHORITY_REQUEST
F   insufficient basis → CONTEXT_REQUEST
G   ONE_UNIT consumed at effect-bearing start
G2  failure after effect start does not restore grant
H   post-checkpoint occupant replacement / revalidation
I   momentum overshoot: next obvious unit does not execute
```

Held-out or successor-facing material must remain structurally separated from
expected scoring material where applicable.

## Durability / failure law

Retain exact durable state for engagement, binding, claim, peer evidence,
pre-mutation disposition, authority witness/absence, effect-bearing start,
grant consumption, receipt, and checkpoint/release state.

```text
FAILURE != ERASURE

DURABILITY PRESERVES CONSEQUENCE HISTORY

RECOVERY RELATES PRESERVED HISTORY
TO A NEW CURRENT STATE
```

Do not restore consumed authority merely because an effect-bearing unit failed.

## Stop conditions

Stop rather than broaden if:

```text
transition is not mechanically single-valued
engagement and pre-mutation disposition collapse
candidate attachment and work binding collapse
coordination contract must be redefined
authority must be inferred from engagement
grant-consumption timing becomes ambiguous
a synthetic cell requires live seat/model activity
Lane-B coordination becomes ambiguous
apparatus attempts to grant itself authority
repair exceeds the bounded contract
```

## Terminal target

```text
contract:
materialized + frozen

state machine:
mechanically single-valued

synthetic apparatus:
materialized

pressure:
executed

repairs:
only if earned

final-head CI:
green

qualification evidence:
durable

real seat:
untouched

real occupant:
unbound

live authority:
none created

external consequence:
none
```

Then stop and return for fresh review.

## Claim ceiling

A positive qualification supports only a bounded candidate evaluator receiving
a seat-targeted envelope, classifying engagement, becoming explicitly bound to
one work unit after acceptance, consuming established basis / coordination /
authority evidence, beginning at most one separately authorized synthetic
consequence, consuming one-unit authority at effect-bearing start, retaining
terminal evidence, and checkpointing / releasing / reconstructing without
silently extending work ownership or authority.

It does not establish general autonomous agency, general seat persistence,
general authority safety, scheduler safety, unbounded continuation, automatic
recovery correctness, or real-world consequence safety.
