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
- synthetic envelopes exercise shape, not live capture

## Evidence

No dedicated ingest implementation exists.

Current evidence is limited to synthetic envelopes used by ledger tests.

