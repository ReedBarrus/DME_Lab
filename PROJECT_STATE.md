# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

Ledger pressure pass completed in `docs/decisions/ledger_pressure_pass_v0.md`.

Synthetic ledger append/replay/integrity harness implemented and tested.

Development distinction registry initialized as provisional, non-authoritative research memory.

## Objective

Build toward deterministic reconstruction of OS-derived event history while preserving provenance.

## Current Primitive Signal

- identity
- time
- type
- payload

## Current Provenance Boundary

Minimum surrounding metadata only:

- envelope identity
- source
- sequence
- integrity
- capture version

## Active Pipeline

```text
OS Source
-> Capture Adapter
-> Raw Observation
-> Ingest Envelope
-> Append Ledger
-> Replay
-> Reconstructed Topology
-> Exposed Projection
```

signal
-> provenance envelope
-> append-only ledger
-> deterministic replay
-> reconstructed topology

next:
navigation
-> comparison
-> projection
-> feedback

## Explicit Deferrals

- Windows capture adapter
- semantic interpretation
- intent inference
- consequence modeling
- feedback systems
- agents
- adaptive behavior
- large formal ontology

## Missing Evidence

- no raw observations captured
- no live ingest envelopes written
- JSONL append ledger validated only against synthetic envelopes
- raw replay validated only in canonical commit order
- no projection exposed from evidence

## Next Smallest Question

What is the smallest machine-readable ledger schema that can describe the tested record boundary without adding semantic fields?

## Current Pressure

- keep `record_id`, envelope identity, source sequence, event time, arrival time, and `commit_index` distinct
- test raw replay in canonical commit order before resolved amendment views
- keep the integrity hash boundary explicit: canonical JSON of record content without the `integrity` field
- preserve missingness structurally without explaining it semantically
- JSONL and complete-envelope storage remain provisional after small synthetic tests
- use `docs/distinctions/registry.jsonl` as appendable distinction memory, not as authority over runtime evidence
