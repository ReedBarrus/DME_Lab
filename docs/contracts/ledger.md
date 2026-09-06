# Ledger Contract

The ledger is append-only storage for ingest envelopes.

## Initial Requirement

Ledger entries must preserve enough information to replay raw observations in deterministic order while keeping signal content and provenance metadata distinguishable.

## Boundary

The ledger does not interpret events, infer causality, or compress missing information into assumed facts.

## Open Pressure

The minimal entry shape, integrity check, and ordering rule are not yet implemented.

# Core Question

What minimum guarantees must an append-only ledger provide so that admitted event envelopes can be replayed deterministically, verified for integrity, and traced back to their source observations without introducing semantic interpretation?

# 4 Functionality Basis Tests

1. ORDER
Given the same ledger, replay always receives records
in the same canonical sequence.

2. IDENTITY
Every replayed record can be traced to exactly one
committed ledger identity and admitted envelope.

3. INTEGRITY
The system can detect whether committed content has
changed or become unavailable.

4. PROVENANCE
Every reconstructed result can descend through ledger
records to the original captured observation or to an
explicit declaration that some source material is missing.