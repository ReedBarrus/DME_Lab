# Reconstruction Contract

## Status

Projected for the general system.

A bounded v0 reconstruction mechanism is implemented for admission relationships.

## Role

Reconstruction derives a recoverable structure from replayed ledger entries.

## Input

Raw replay output from a valid ledger state.

## Output

A reconstructed representation derived from recorded observations.

## Initial Requirement

Reconstruction must be deterministic for the same ledger input.

## Must Preserve

- determinism for the same valid input
- authoritative record references
- provenance back to replayed ledger records
- missing observations as missing

## Boundary

Reconstruction is not authoritative history, proof of what happened outside recorded evidence, or an index. Missing observations remain missing.

## Must Not Claim

- truth outside recorded evidence
- inferred causality
- intent
- consequence
- completeness of OS history
- independent source-of-truth status

## Open Pressure

- no generalized topology exists
- no index exists
- admission conflict resolution remains deferred
- latest-decision semantics remain deferred

## Evidence

Bounded admission relationship reconstruction evidence:

- `src/reconstruction/admission.py`
- `tests/reconstruction/test_admission_reconstruction.py`
- `src/runtime/reconstruction_pressure.py`
- `traces/reconstruction_pressure_v0.json`
- `docs/decisions/reconstruction_pressure_v0.md`
- `traces/live_ingest_ledger_v0.jsonl`
- `traces/live_vertical_probe_v0.json`
- `docs/decisions/live_vertical_probe_v0.md`
- `docs/decisions/live_ingest_ledger_extraction_v0.md`

This evidence does not validate generalized topology, indexing, projection engines, or OS event reconstruction.
