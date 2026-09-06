# Ledger Contract

The ledger is append-only storage for ingest envelopes.

## Initial Requirement

Ledger entries must preserve enough information to replay raw observations in deterministic order while keeping signal content and provenance metadata distinguishable.

## Boundary

The ledger does not interpret events, infer causality, or compress missing information into assumed facts.

## Open Pressure

The minimal entry shape, integrity check, and ordering rule are not yet implemented.

