# Signal Contract

## Status

Projected.

A signal is the primitive observed event content.

## Role

Carry the smallest observed event content across the initial pipeline.

## Input

Raw observation content admitted by ingest or generated synthetically for tests.

## Output

Primitive signal content inside an ingest envelope.

## Required Fields

- identity
- time
- type
- payload

## Must Preserve

- identity as observed or admitted
- time as observed or admitted
- type as observed or admitted
- payload as opaque content

## Boundary

The signal does not include interpretation, inferred intent, modeled consequence, or feedback state.

## Must Not Claim

- truth
- causality
- persistent identity continuity
- semantic meaning
- source authority

## Open Pressure

The exact field encodings remain provisional until tested against real captured observations.

## Evidence

No live signal capture evidence exists. Synthetic signal-shaped content is exercised only inside ledger tests.
