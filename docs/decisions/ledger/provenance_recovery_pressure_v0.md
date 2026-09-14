# Provenance Recovery Pressure v0

## Pressure

The prior witness-content ablation found that ordered record digests were the
smallest tested carrier for bounded H14 prefix distinction.

This pressure kept the same H14 ordered digest carrier fixed and changed only
the available interpretation regime.

No witness persistence, checkpoint, manifest, verifier registry, atlas, or
general relation machinery was introduced.

## Carrier

Carrier:

`W14_ordered_record_digests`

Source:

`e399720:traces/live_ingest_ledger_v0.jsonl`

The carrier stores ordered digest bytes. It does not include its own
interpretation.

## Outcomes

Local outcomes:

- `RECOVERED`: the supplied regime can evaluate the H14 prefix and finds it conserved
- `MISMATCHED`: the supplied regime can execute comparison and finds incompatible commitments or extent
- `UNRESOLVED`: the supplied regime lacks information needed to justify recovered or mismatched

`UNRESOLVED` is not treated as false, corruption, or mismatch.

## Chart 3

```text
                         R0   R1   R2   R3   R4   R5   R6   R7   R8
H13 tail loss             M    U    U    U    U    U    M    M    M
H14 control               R    U    U    U    U    U    R    M    M
H16 extension             R    U    U    U    U    U    R    M    M
H16 ID replacement        M    U    U    U    U    U    M    M    M
H16 content replacement   M    U    U    U    U    U    M    M    M
```

Legend:

- `R` = `RECOVERED`
- `M` = `MISMATCHED`
- `U` = `UNRESOLVED`

Regimes:

- `R0`: full current ambient semantics
- `R1`: digest carrier only
- `R2`: algorithm only
- `R3`: algorithm plus boundary, no canonicalization
- `R4`: commitment semantics, no ordering or relation
- `R5`: commitment plus ordering, no prefix rule
- `R6`: sufficient bounded historical verifier semantics
- `R7`: wrong boundary, envelope only
- `R8`: wrong canonicalization, spaced JSON

## Result

The same digest carrier produced:

- `RECOVERED`: 4 cells
- `MISMATCHED`: 16 cells
- `UNRESOLVED`: 25 cells

Missing interpretation yielded `UNRESOLVED`.

Complete but wrong interpretation yielded `MISMATCHED`.

The nearest insufficient regime was commitment plus ordering without the prefix
comparison rule.

The smallest sufficient tested regime included:

- SHA-256 identity
- current commitment boundary
- exact canonicalization
- commit-index ordering
- prefix comparison
- candidate commitment recomputation semantics

## Metadata Drift

A temporary H14 specimen changed `integrity.algorithm` and
`integrity.boundary` while leaving digest bytes and committed content unchanged.

Current `JsonlLedger.verify()` still passed.

Stored integrity metadata does not currently govern verifier execution.

## Overlap

This creates stable overlap with:

- historical relation chart: historical transformation x observer relation
- witness-content chart: historical transformation x witness representation
- provenance-recovery chart: witness carrier x interpretation regime

Shared referents now include H14, H16 extension, H16 content replacement,
ordered digest witness, and prefix preservation.

No transition map was implemented.

## Finding

`witness_carrier_survival` is not equivalent to
`historical_relation_recovery`.

## Deferred

No witness file, checkpoint, manifest, hash chain, Merkle structure, verifier
registry, provenance registry, atlas, repair, recovery, or generalized relation
algebra was added.

Next pressure: test a minimal non-persistent declarative commitment-semantics
record against the same recovery chart.
