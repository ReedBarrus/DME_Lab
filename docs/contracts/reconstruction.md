# Reconstruction Contract

## Status

Projected.

## Role

Reconstruction derives topology from replayed ledger entries.

## Input

Raw replay output from a valid ledger state.

## Output

A reconstructed topology derived from recorded observations.

## Initial Requirement

Reconstruction must be deterministic for the same ledger input.

## Must Preserve

- determinism for the same valid input
- provenance back to replayed ledger records
- missing observations as missing

## Boundary

Reconstruction is not proof of what happened outside the recorded evidence. Missing observations remain missing.

## Must Not Claim

- truth outside recorded evidence
- inferred causality
- intent
- consequence
- completeness of OS history

## Open Pressure

The first reconstruction target should be small enough to compare directly against the source ledger.

## Evidence

No reconstruction implementation or runtime evidence exists.
