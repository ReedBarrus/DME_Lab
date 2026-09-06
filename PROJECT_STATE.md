# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

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

What is the minimal append-only ledger contract that can preserve raw observation identity, ordering, integrity, and replayability without adding interpretation?

