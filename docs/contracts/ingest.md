# Ingest Contract

## Status

Projected.

## Role

Ingest admits captured observation structure into the ledger boundary as an ingest envelope.

## Input

Raw observation structure from a capture adapter or synthetic test fixture.

## Output

An admitted envelope suitable for ledger append.

## Must Preserve

- primitive signal content
- provenance fields that are present
- missingness as missingness
- distinction between source sequence, event time, arrival time, envelope identity, and ledger identity

## Must Not Claim

- event meaning
- intent
- causality
- consequence
- truth
- repaired or normalized source reality

## Known Pressure

- admission behavior is not yet implemented as its own boundary
- malformed and unavailable source structures need pressure
- synthetic envelopes exercise ledger shape
- bounded live candidate envelopes exercise shadow handshakes, not admission enforcement

## Evidence

No dedicated ingest implementation exists.

Evidence currently includes synthetic envelopes used by ledger tests and bounded live repository candidate-envelope handshakes.

A live repository snapshot candidate envelope has been constructed and compared in shadow mode:

- `src/runtime/repo_provenance_pressure.py`
- `traces/repo_provenance_pressure_v0.json`
- `docs/decisions/repo_provenance_pressure_v0.md`
- `src/runtime/repo_transition_pressure.py`
- `traces/repo_transition_pressure_v0.json`
- `docs/decisions/repo_transition_pressure_v0.md`

This does not implement or enforce ingest admission, and it does not define final ingest rules.
