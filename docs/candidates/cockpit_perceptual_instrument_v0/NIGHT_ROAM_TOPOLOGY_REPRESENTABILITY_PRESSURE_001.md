# NIGHT_ROAM_TOPOLOGY_REPRESENTABILITY_PRESSURE_001

## Status

```text
PRESSURE DESIGN ONLY
IMPLEMENTATION REPAIR: NONE
PROMOTION: NONE
AUTHORITY EFFECT: NONE
EXECUTION EFFECT: NONE
```

## Exact observed basis

Basis coordinate:

```text
cockpit-perceptual-instrument-campaign-v0
a9b4ed3d1086f7a7042ecdb7d358109f53938722
```

The frozen perceptual contract requires representation switching to preserve an exact selected address whenever that address is representable in the destination projection, and requires explicit failure-legible loss when it is not.

The implementation currently contains two distinct topology-representability behaviors:

1. `projectionAddressStatus('TOPOLOGY', ...)` returns `REPRESENTABLE` for every non-empty address set without consulting the loaded semantic observer basis.
2. `renderTopology(...)` separately resolves each address against the operational graph and `observerAddressObject(...)`; when neither resolves it, the renderer says the coordinate is retained but absent from the currently loaded topology basis.

The existing perceptual-instrument test explicitly asserts `REPRESENTABLE` for a semantic-only pressure address using only the operational graph, without supplying or proving a matching observer coordinate.

## Proposed distinction

```text
ADDRESS RETAINED ACROSS PROJECTION SWITCH
!=
ADDRESS REPRESENTABLE IN DESTINATION BASIS

REPRESENTATION KIND IS TOPOLOGY
!=
SELECTED COORDINATE EXISTS IN LOADED TOPOLOGY BASIS

FAILURE-LEGIBLE RENDERING
!=
REPRESENTABILITY PREDICATE IS SOUND
```

## Why current evidence does not settle it

The renderer is failure-legible for an unresolved coordinate, but the exported representability predicate and its test encode a stronger claim. Current evidence does not establish that every semantic address is present in every loaded observer model, nor that address kind alone is sufficient evidence of presence.

This is therefore not yet an implementation-repair authorization. The smallest next step is to pressure the predicate against exact loaded bases before choosing whether the predicate, caller contract, or test is wrong.

## Smallest discriminating pressure

Hold selected address identity constant while varying only whether the destination basis contains that exact coordinate.

### T1 — exact semantic coordinate present

```text
address = pressure_occurrence:P1-exact
observer basis contains P1-exact
graph does not contain P1-exact
```

Expected observable if basis-relative representability is correct:

```text
TOPOLOGY status = REPRESENTABLE
missing = []
```

### T2 — same semantic kind, exact coordinate absent

```text
address = pressure_occurrence:P1-absent
observer basis does not contain P1-absent
graph does not contain P1-absent
```

Discriminator:

```text
REPRESENTABLE
vs
ADDRESS_NOT_REPRESENTABLE
```

If T2 remains `REPRESENTABLE`, the predicate is kind-relative rather than basis-relative.

### T3 — exact operational coordinate present

```text
address = request:R1
graph contains request:R1
observer basis need not contain request:R1
```

Expected:

```text
TOPOLOGY status = REPRESENTABLE
```

because the current topology renderer can explain the operational node and its exact operational relations.

### T4 — operational coordinate absent from both loaded bases

```text
address = request:R-missing
graph does not contain request:R-missing
observer basis does not contain request:R-missing
```

Expected if the predicate matches rendered basis reality:

```text
TOPOLOGY status = ADDRESS_NOT_REPRESENTABLE
missing = [request:R-missing]
```

## Outcome claim ceilings

If T1/T3 represent and T2/T4 reject:

```text
EARNED:
loaded-basis-relative topology representability can be mechanically discriminated

NOT EARNED:
semantic equivalence across projections
```

If all topology addresses report representable while T2/T4 render unresolved:

```text
EARNED:
current representability predicate is weaker / differently scoped than rendered topology presence

NOT EARNED:
that the renderer itself loses address continuity
```

If exact absent addresses are intentionally defined as representable because retention alone satisfies the predicate:

```text
EARNED:
predicate name / contract requires explicit clarification

NOT EARNED:
implementation bug
```

## Dangerous neighboring inference

Do not infer any of the following from this pressure:

```text
SAME ADDRESS
=> SAME SEMANTIC OBJECT ACROSS BASES

RAW OBJECT PRESENT
=> CLAIM STANDING

TOPOLOGY REPRESENTABLE
=> CONSEQUENCE REPRESENTABLE

ADDRESS RETAINED
=> RELATION RETAINED

UI WARNING
=> SEMANTIC FAILURE
```

## Future campaign merit

```text
YES — SMALL
```

This deserves a bounded executable pressure because it tests the primary perceptual law directly and can expose a false-positive address-continuity signal without touching authority, control, runtime execution, or external effects.
