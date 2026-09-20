# DME_Lab — Capability Withdrawal Pressure v0

## Status

**Candidate reusable method.**

This document defines a small experimental pressure pattern for exposing hidden
dependency structure by withdrawing one supporting capability.

Its authority is methodological only.

It does not:

- establish a universal decomposition rule;
- prove that any resulting factorization is complete;
- authorize removal of a capability merely because the method exists;
- authorize repair, redesign, standing promotion, or authority expansion;
- convert a functional dependency into semantic equivalence;
- convert a functional dependency into authority entitlement.

The method earns only the bounded relation exposed by the executed withdrawal.

---

## Purpose

Use Capability Withdrawal Pressure when an operation appears atomic or a
distinction appears unnecessary because two behaviors, states, or transitions
always co-occur under a permissive operating condition.

The method asks:

> **What capability is currently making this distinction look unnecessary?**

Core intervention:

    apparently atomic behavior
    +
    supporting capability
    →
    smooth operation

    withdraw exactly one supporting capability
    →
    observe independent survival / failure

If a seam appears, the bounded result is:

    the prior coupling was contingent on the withdrawn capability

It is not automatically:

    the resulting decomposition is complete

---

## Core discriminator

Preserve these relations separately:

    functional dependency
    !=
    semantic equivalence
    !=
    authority entitlement

A component may depend on a capability operationally without:

- meaning the same thing as that capability;
- owning the evidence supplied by that capability;
- inheriting the authority exercised by that capability;
- being entitled to recreate or reacquire that capability when it is absent.

---

## Off-book subsidy classes

Capability withdrawal may expose one or more hidden subsidies.

### Operational subsidy

One component or capability is silently carrying another function.

    X available
    → Y works

    X removed
    → Y fails or partially survives

This establishes an operational dependency only within the tested scope.

### Semantic subsidy

A representation appears self-sufficient because another context source,
artifact, convention, or service supplies meaning that the representation does
not itself preserve.

Withdrawal may expose that:

    meaning recoverable under shared context
    !=
    meaning owned by the representation

### Authority subsidy

An operation appears locally self-sufficient because another capability is
silently exercising permission on its behalf.

Withdrawal may expose that:

    operation can be computed
    !=
    operation can be durably admitted

or another equivalent tested authority separation.

These subsidy classes are diagnostic lenses, not exhaustive ontology.

---

## Preconditions

Before executing the pressure, declare:

1. **apparently atomic behavior** — the operation or coupling under test;
2. **withdrawn capability** — exactly one capability to remove or deny;
3. **held coordinates** — what must remain unchanged for the comparison to be
   interpretable;
4. **observation surface** — what survival, degradation, or failure can be
   observed;
5. **authority boundary** — what the test may and may not mutate;
6. **stop conditions** — when the withdrawal becomes unsafe, uninterpretable,
   or outside the authorized pressure.

If the withdrawal cannot be isolated from material collateral changes, the
result is UNRESOLVED rather than a forced decomposition.

---

## Procedure

### 1. Establish the coupled baseline

Record the smallest evidence needed to show the apparently atomic behavior
operating with the supporting capability present.

Do not infer atomicity merely because operation is smooth.

### 2. Withdraw exactly one supporting capability

Remove, deny, withhold, or disable only the declared capability.

Examples of capability classes include:

- write or mutation privilege;
- retrieval or context access;
- persistence or checkpoint access;
- tool availability;
- authority or admission rights;
- a shared source of semantic context;
- a convenience service that may be carrying hidden state.

Do not silently substitute an equivalent capability during the withdrawal.

### 3. Observe independent survival and failure

Record which sub-behaviors:

- continue unchanged;
- degrade;
- halt;
- become uncertain;
- become possible but inadmissible;
- remain semantically interpretable but no longer durably recordable.

Prefer raw or minimally transformed evidence when available.

### 4. Freeze the observed seam before repair

Before restoring the capability or introducing a compensating mechanism,
record:

    WHAT SURVIVED
    WHAT FRACTURED
    WHAT BECAME UNKNOWN
    WHAT AUTHORITY WAS ABSENT
    WHAT EVIDENCE SUPPORTS EACH CLAIM

Do not restore the capability merely to recover smoothness before the wound is
understood.

### 5. Preserve only earned non-equivalences

Promote only distinctions required by the observed fracture.

A valid result may be as small as:

    A != B

within the tested condition.

Do not infer that all remaining coupled terms are equivalent.

### 6. Separate diagnosis from repair

The method identifies hidden dependency structure.

It does not select the repair.

Branch/PR flow, sidecar persistence, admission services, replicated state,
different context carriers, or other mechanisms remain candidate repairs until
separate pressure selects among them.

---

## Result classes

A Capability Withdrawal Pressure should end in one of four bounded states.

### SEAM_EXPOSED

The withdrawn capability causes a reproducible separation between behaviors or
states that previously appeared atomic.

Allowed claim:

    the prior coupling was contingent on capability X

plus the exact observed non-equivalence.

### NO_OBSERVED_SEAM

The tested behavior survives the withdrawal on the declared observation
surface.

Allowed claim:

    no consequential dependence on capability X was observed
    within this tested scope

This does not prove global independence from X.

### CONFOUNDED

The withdrawal changes additional coordinates materially enough that the
observed fracture cannot be attributed to X alone.

No decomposition is earned.

### INADMISSIBLE

The required withdrawal would cross an authority, safety, privacy, or
irreversibility boundary not authorized by the pressure.

No experiment is run.

---

## Claim ceiling

The strongest generic inference available from a successful withdrawal is:

    withdraw X
    → seam appears

    therefore:
    the prior coupling was contingent on X

The following are not licensed without additional pressure:

    the decomposition is complete
    the exposed relation is universal
    X is the sole dependency
    the surviving components are independent
    functional dependence establishes shared meaning
    functional dependence grants authority
    absence of a fracture proves independence

A withdrawal can expose **a seam** without exposing **all seams**.

---

## Anti-patterns

### Restore-and-forget

    withdraw capability
    → system breaks
    → restore capability
    → declare problem solved

This erases the evidence that the capability was carrying hidden load.

### Compensation during withdrawal

Replacing the withdrawn capability with another hidden substitute destroys the
intended intervention.

### Authority rescue

    operation fails after authority withdrawal
    → grant broader authority so operation can continue

Continuity or availability pressure does not itself justify widening authority.

### Semantic promotion

A functional failure does not prove that two concepts mean the same thing.

### Final-ontology promotion

Repeated usefulness of this method does not make it a universal decomposition
theorem or foundational primitive.

---

## Minimal durable record

For each executed pressure, retain:

    PRESSURE ID:
    APPARENTLY ATOMIC BEHAVIOR:
    WITHDRAWN CAPABILITY:
    HELD COORDINATES:
    OBSERVATION SURFACE:
    BASELINE EVIDENCE:
    WITHDRAWAL EVIDENCE:
    WHAT SURVIVED:
    WHAT FRACTURED:
    WHAT REMAINS UNKNOWN:
    EARNED NON-EQUIVALENCE:
    CLAIM CEILING:
    REPAIR SELECTED: NONE | <separately authorized mechanism>

The record should distinguish direct observation from interpretation.

---

## Relationship to other DME_Lab methods

Capability Withdrawal Pressure is adjacent to, but not identical with,
distinction ablation.

Distinction ablation asks whether removing a represented distinction changes
behavior, trajectory, resource use, reconstruction, or reachability.

Capability withdrawal asks whether removing a supporting capability exposes
hidden dependency structure inside behavior that previously appeared smooth or
atomic.

Either method may motivate the other.

Neither method authorizes a stronger claim than its executed evidence supports.

---

## Method ceiling

This method should remain a small tool in the methods toolbox.

Its value is practical:

    coupling exposed
    → distinction recovered
    → evidence retained
    → repair delayed until pressure selects it

The durable reflex is:

> **When two things seem indistinguishable because they always co-move, perturb
> the condition that keeps them coupled. Then preserve only the
> non-equivalence actually earned.**

Smoothness is not evidence of correct factorization.
