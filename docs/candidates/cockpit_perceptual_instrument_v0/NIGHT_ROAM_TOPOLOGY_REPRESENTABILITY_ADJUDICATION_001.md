# NIGHT_ROAM_TOPOLOGY_REPRESENTABILITY_ADJUDICATION_001

## Status

```text
PRESSURE:
EXECUTED

MECHANICAL RESULT:
FRACTURE CONFIRMED IN ORIGINAL PREDICATE

REPAIR:
BOUNDED

QUALIFICATION SCOPE:
TESTED LOADED-BASE REPRESENTABILITY ONLY

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE
```

## Basis

Original campaign basis:

```text
cockpit-perceptual-instrument-campaign-v0
a9b4ed3d1086f7a7042ecdb7d358109f53938722
```

Pressure/repair head:

```text
night-roam/topology-representability-001
e1bc1cae89bd5b184e1eaedbca2866e65b31f461
```

## Original fracture

The original exported predicate:

```text
projectionAddressStatus('TOPOLOGY', ...)
```

returned `REPRESENTABLE` for every non-empty address set without consulting
either the operational graph or the loaded semantic observer basis.

The topology renderer separately checked exact presence and could report:

```text
Coordinate retained but not present in the currently loaded topology basis.
```

Therefore the original implementation admitted:

```text
ADDRESS RETAINED
!=
ADDRESS REPRESENTABLE IN DESTINATION BASIS
```

while the predicate collapsed the two.

## Repair

Topology representability is now computed from exact loaded basis presence:

```text
operational graph contains exact address
OR
semantic observer basis contains exact address
```

Otherwise:

```text
ADDRESS_NOT_REPRESENTABLE
```

The address remains retained; no nearby substitution is performed.

## Executed pressure cells

The new deterministic test varies exact presence while holding address identity
and projection kind explicit:

```text
T1 semantic coordinate present:
REPRESENTABLE

T2 same semantic kind, exact coordinate absent:
ADDRESS_NOT_REPRESENTABLE

T3 operational coordinate present:
REPRESENTABLE

T4 operational coordinate absent from both loaded bases:
ADDRESS_NOT_REPRESENTABLE
```

The prior cross-projection test was also tightened so its semantic coordinate is
actually present in the supplied observer basis before expecting topology
representability.

## CI evidence

Exact head:

```text
e1bc1cae89bd5b184e1eaedbca2866e65b31f461
```

Workflow:

```text
COCKPIT_PERCEPTUAL_INSTRUMENT_001
run 35557359971
SUCCESS
job 106203483674
SUCCESS
```

Inherited Cockpit/control/runtime/horizon tests in that workflow also completed
successfully.

## Earned claim

```text
FOR THE TESTED ADDRESS KINDS AND LOADED BASES,

TOPOLOGY REPRESENTABILITY
IS SENSITIVE TO EXACT BASIS PRESENCE

AND DOES NOT REPORT AN ABSENT EXACT COORDINATE
AS REPRESENTABLE.
```

## Not earned

This does not establish:

```text
semantic equivalence across projections
identity continuity across transformed bases
relation preservation
standing
authority
consequence availability
universal representability for every future address kind
```

## Conserved scars

```text
ADDRESS RETAINED
!=
ADDRESS REPRESENTABLE

REPRESENTATION KIND
!=
OBJECT PRESENCE

FAILURE-LEGIBLE RENDERING
!=
SOUND REPRESENTABILITY PREDICATE
```
