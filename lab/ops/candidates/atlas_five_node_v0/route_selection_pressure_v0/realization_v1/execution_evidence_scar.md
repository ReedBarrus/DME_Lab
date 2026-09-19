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
