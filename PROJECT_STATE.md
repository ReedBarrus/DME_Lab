# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

Ledger pressure pass completed in `docs/decisions/ledger_pressure_pass_v0.md`.

Synthetic ledger append/replay/integrity harness implemented and tested.

Development distinction registry initialized as provisional, non-authoritative research memory.

v0 contract surface mapped in `docs/contracts/README.md`.

Ledger record schema hypothesis added as descriptive, shadow-only JSON Schema.

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

What is the smallest ingest/provenance admission experiment that can decide which structures may enter the ledger as admitted envelopes?

## Contract Surface Status

- projected: signal, provenance, ingest envelope, reconstruction, exposed projection
- pressure-tested within synthetic v0 scope: append ledger, raw replay
- deferred: capture adapter

## Current Pressure

- keep `record_id`, envelope identity, source sequence, event time, arrival time, and `commit_index` distinct
- test raw replay in canonical commit order before resolved amendment views
- keep the integrity hash boundary explicit: canonical JSON of record content without the `integrity` field
- preserve missingness structurally without explaining it semantically
- JSONL and complete-envelope storage remain provisional after small synthetic tests
- use `docs/distinctions/registry.jsonl` as appendable distinction memory, not as authority over runtime evidence
- keep schema work local to boundaries with executable evidence; ledger record remains the current strongest candidate
- current synthetic runtime records conform to `schemas/ledger_record_v0.schema.json`
- schema validation remains shadow-only and does not regulate ledger append
- runtime can currently produce some records the schema rejects, including non-object envelopes and non-finite JSON values
- ingest/provenance admission is now the likely next pressure frontier
