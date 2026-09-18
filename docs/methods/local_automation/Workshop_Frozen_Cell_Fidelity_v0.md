# Workshop Pressure 001 — Frozen Cell Fidelity — Phase A Contract

**Status:** PROVISIONAL EXECUTABLE PRESSURE  
**Scope:** deterministic mock invocation only  
**Live provider:** NOT CONNECTED  
**LP-001 cell execution:** NOT AUTHORIZED

## Pressure

Can one frozen authorized cell either execute exactly once as declared or halt
legibly before crossing a violated boundary?

```text
one authorized cell
→ exact execution
OR
→ legible halt
```

Workshop Phase A is intentionally ignorant of lineage, scoring, experiment
meaning, and scientific standing.

## Properties under pressure

```text
P1 MANIFEST FIDELITY
P2 PAYLOAD FIDELITY
P3 INVOCATION FIDELITY
P4 OUTPUT FIDELITY
P5 FAULT ATOMICITY
```

The invocation surface preserves:

```text
DECLARED_ONLY
!=
VERIFIABLE_REQUIRED
!=
UNOBSERVABLE
```

A requested value is not promoted into observed evidence.

## State machine

```text
LOADED
→ MANIFEST_VERIFIED
→ INPUTS_VERIFIED
→ PAYLOAD_VERIFIED
→ INVOCATION_VERIFIED
→ INVOKED
→ OUTPUT_CAPTURED
→ OUTPUT_RETAINED
→ RECEIPT_COMMITTED

ANY FAULT
→ HALTED
```

There is no transition out of `HALTED` in v0.

## Artifact separation

```text
MANIFEST
= what may happen

RECEIPT
= what did happen

FAULT
= why execution stopped
```

Neither a receipt nor a fault changes authorization or standing.

## Phase A adapter

The only execution adapter in this pressure is
`MockInvocationAdapter`.

It maps an assembled payload SHA-256 to fixed output bytes. It does not call a
network, model provider, repository service, or experiment scorer.

## Adversarial matrix

```text
T00 clean control
→ exactly one invocation
→ RECEIPT_COMMITTED

T01 bad condition packet identity
→ E003
→ no invocation

T02 bad specimen identity
→ E004
→ no invocation

T03 assembled payload identity drift
→ E005
→ no invocation

T04 required observable invocation-surface drift
→ E006
→ no invocation

T05 post-invocation output capture failure
→ E011
→ execution fact retained
→ no success receipt

T06 unknown deviation during invocation-surface observation
→ E017
→ no invocation
→ no improvisation
```

## Claim ceiling

A passing Phase A matrix can establish only that this bounded mock runner
preserved the declared one-cell transition/fault behavior in the tested cases.

It does not establish:

- a qualified real-provider adapter;
- LP-001 execution readiness;
- correct scorer behavior;
- multi-cell sequencing;
- retry or recovery policy;
- autonomous experimentation;
- generalized Workshop architecture;
- scientific standing.

Phase B must separately pressure a real invocation boundary.
