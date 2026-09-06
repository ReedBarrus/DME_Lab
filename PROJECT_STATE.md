# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

Ledger pressure pass completed in `docs/decisions/ledger_pressure_pass_v0.md`.

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
- no ingest envelopes written
- no append ledger format validated by runtime
- no replay output reconstructed
- no projection exposed from evidence

## Next Smallest Question

What is the smallest synthetic JSONL append/replay/integrity harness that can falsify the v0 ledger guarantees without introducing interpretation?

## Current Pressure

- keep `record_id`, envelope identity, source sequence, event time, arrival time, and `commit_index` distinct
- test raw replay in canonical commit order before resolved amendment views
- define the integrity hash boundary before implementation
- preserve missingness structurally without explaining it semantically
