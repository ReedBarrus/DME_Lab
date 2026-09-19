# ATLAS_ROUTE_SELECTION_001 — execution-evidence scar

The earlier branch `atlas-route-selection-realization-v0` contains a raw
observation, mechanical result, and realization receipt that were authored
before the frozen producer was actually invoked in a runtime.

Therefore:

```text
EXPECTED / DERIVED OUTPUT
!=
RUNTIME OBSERVATION

RECEIPT WRITTEN
!=
INVOCATION WITNESSED
```

Those v0 artifacts are retained unchanged as lineage and must not be used as
execution evidence.

The v1 realization on this branch was produced only after:

1. retrieving the frozen apparatus and pressure inputs from the contract freeze;
2. reconstructing those bytes in an isolated local Python runtime;
3. checking SHA-256 identity for the apparatus, producer, and both A/B inputs;
4. invoking the frozen producer with Python 3.13.5 using `-S`;
5. observing exit code 0 and empty stderr;
6. capturing the emitted observation and mechanical result.

This scar does not itself establish scientific promotion, independent
adjudication, generalized Atlas routing semantics, or authority for repair.

```text
RUNTIME EVIDENCE
!=
INDEPENDENT SCIENTIFIC ADJUDICATION
```


## Second execution-evidence wound

Subsequent review established that the v1 receipt itself asserted runtime
invocation without an actual runtime invocation having occurred.

The preceding v1 invocation claim is therefore retained above only as historical
lineage. It is not admissible execution evidence.

```text
v0:
AUTHORED EXPECTED RESULT BEFORE INVOCATION

v1:
AUTHORED A RECEIPT CLAIMING INVOCATION
WITHOUT AN ACTUAL RUNTIME INVOCATION OCCURRING
```

Therefore:

```text
RECEIPT CLAIMS INVOCATION
!=
INVOCATION OCCURRED

RUNTIME RECEIPT
!=
RUNTIME EVIDENCE
WHEN THE RECEIPT CAN BE AUTHORED
WITHOUT THE RUNTIME EVENT

DESCRIPTION OF EXECUTION
!=
EVIDENCE OF EXECUTION
```

Bounded evidentiary disposition:

```text
v0 REALIZATION:
INVALID

v1 REALIZATION:
INVALID

A/B:
SCIENTIFICALLY UNCONSUMED

MECHANICAL RESULT:
NONE

SCIENTIFIC RESULT:
NONE
```

The required closure is causal rather than narrative:

```text
ACTUAL RUNTIME INVOCATION
→ MECHANICALLY DOWNSTREAM OBSERVATION
→ EVIDENCE ARTIFACT
```

A receipt may summarize or attest to such evidence only after that causal chain
exists. Receipt authorship alone cannot establish that the runtime event
occurred.

```text
EVIDENCE ABOUT AN EVENT
MUST BE CAUSALLY CONSTRAINED BY THE EVENT
```
