# v0 Observability Projection

This projection describes the first visible shape of the system. It is not proof that the system works.

## Goal

Observe OS-derived events as primitive signals and preserve enough provenance to replay them deterministically later.

## Primitive Signal

- identity
- time
- type
- payload

## Provenance Shell

The signal is surrounded by minimal provenance metadata:

- envelope identity
- source
- sequence
- integrity
- capture version

## Falsification Pressure

This projection fails if replay cannot reconstruct event ordering, identity, or provenance boundaries from recorded ledger entries.

