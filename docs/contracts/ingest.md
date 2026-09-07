# Ingest Contract

## Status

Projected for the general system.

A bounded v0 admission mechanism is implemented for temporary ledger pressure.

## Role

Ingest classifies preserved observation structure for downstream eligibility.

## Input

Raw observation structure from a capture adapter or synthetic test fixture.

## Output

Preserved observation records, admission records, and derived admitted projections.

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

- general admission behavior is not yet implemented
- malformed and unavailable source structures need pressure
- synthetic envelopes exercise ledger shape
- bounded live candidate envelopes exercise shadow handshakes, not admission enforcement
- bounded v0 admission records preserve classification without deleting observations

## Evidence

No generalized ingest implementation exists.

Evidence currently includes synthetic envelopes used by ledger tests and bounded live repository candidate-envelope handshakes.

A live repository snapshot candidate envelope has been constructed and compared in shadow mode:

- `src/runtime/repo_provenance_pressure.py`
- `traces/repo_provenance_pressure_v0.json`
- `docs/decisions/repo_provenance_pressure_v0.md`
- `src/runtime/repo_transition_pressure.py`
- `traces/repo_transition_pressure_v0.json`
- `docs/decisions/repo_transition_pressure_v0.md`
- `src/ingest/admission.py`
- `tests/ingest/test_admission.py`
- `src/runtime/ingest_admission_pressure.py`
- `traces/ingest_admission_pressure_v0.json`
- `docs/decisions/ingest_admission_pressure_v0.md`
- `traces/live_vertical_probe_v0.json`
- `docs/decisions/live_vertical_probe_v0.md`

The live vertical probe routes bounded live observations through the current admission mechanism. This does not define final ingest rules, a generalized policy engine, enforced admission, or a durable admitted store.
