# Project State

Primary fast-entry working memory for DME_Lab.

## Status

Repository scaffold initialized.

Ledger pressure pass completed in `docs/decisions/ledger_pressure_pass_v0.md`.

Synthetic ledger append/replay/integrity harness implemented and tested.

Development distinction registry initialized as provisional, non-authoritative research memory.

v0 contract surface mapped in `docs/contracts/README.md`.

Ledger record schema hypothesis added as descriptive, shadow-only JSON Schema.

Bounded repository filesystem observer and separate Git observer implemented.

First live repository baseline captured in `traces/repo_snapshot_v0_baseline.json` and `traces/git_state_v0_baseline.json`.

Second live repository observations captured in `traces/repo_snapshot_v0_post_cleanup.json` and `traces/git_state_v0_post_cleanup.json`.

Repository transition pressure completed in `docs/decisions/repo_transition_pressure_v0.md`.

Bounded v0 ingest admission pressure completed in `docs/decisions/ingest_admission_pressure_v0.md`.

Bounded v0 reconstruction pressure completed in `docs/decisions/reconstruction_pressure_v0.md`.

First bounded live vertical-chain probe completed in `docs/decisions/live_vertical_probe_v0.md`.

Canonical bounded live ingest ledger extraction completed in `docs/decisions/live_ingest_ledger_extraction_v0.md`.

Canonical bounded live ingest ledger continuation completed in `docs/decisions/live_ingest_continuation_v0.md`.

Ledger continuity pressure completed in `docs/decisions/ledger_continuity_pressure_v0.md`.

History extent witness pressure completed in `docs/decisions/history_extent_witness_pressure_v0.md`.

Historical relation pressure completed in `docs/decisions/historical_relation_pressure_v0.md`.

Witness content ablation pressure completed in `docs/decisions/witness_content_ablation_pressure_v0.md`.

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

- no general OS raw observations captured
- no generalized live ingest admission rules
- no generalized live ingest envelope ledger
- JSONL append ledger pressure-tested mainly against synthetic envelopes, with bounded temporary live candidate-envelope handshakes
- raw replay validated only in canonical commit order
- no generalized projection exposed from evidence

## Next Smallest Question

What interpretation and provenance must accompany a minimal ordered-digest prefix witness before any persistence boundary is selected?

## Contract Surface Status

- projected: signal, provenance, general ingest envelope, generalized reconstruction, generalized exposed projection
- implemented within bounded v0 scope: ingest admission classification
- implemented within bounded v0 scope: admission relationship reconstruction
- implemented within bounded v0 scope: admitted projection
- pressure-tested within synthetic v0 scope, with canonical bounded live evidence: append ledger, raw replay
- implemented within bounded repository specimen: capture adapter
- deferred: general OS and Windows capture

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
- repository snapshot baseline produced a JSON-domain valid candidate envelope
- temporary ledger handshake for the live candidate passed schema shadow validation, replay, and integrity verification
- filesystem observation and Git observation are separate live evidence regimes
- snapshots expose endpoint structure, not complete transformation history
- second live transition produced 5 filesystem content changes, 0 filesystem adds, 0 filesystem removes, and 2 retrospective Git commits
- multi-source temporary ledger preserved filesystem and Git candidate envelopes without collapsing source-specific provenance
- repeated same-state observations currently reuse filesystem snapshot identity and candidate envelope identity
- metadata-only changes can alter snapshot identity without producing content-changed paths
- filesystem scope and Git scope are overlapping but non-coextensive
- root identity remains ambiguous when v0 observers are invoked with `.`
- bounded admission records now preserve `record_type`, `subject_record_id`, comparator identity/version, comparison result, decision, and decision basis
- rejected and unresolved observations remain replayable in the temporary admission pressure ledger
- admitted projection is derived from replayed observation and admission records, not duplicated into a second physical store
- one preserved observation can have multiple admission records under different comparator versions
- bounded reconstruction now recovers admission relationships from authoritative replayed ledger records
- reconstructed admission relationships preserve record-id paths back to observation provenance
- rebuilding reconstruction and admitted projection from the same replayed records is structurally stable in v0 pressure
- first live vertical probe preserved filesystem and Git observations through admission, replay, reconstruction, admitted projection, and provenance navigation
- capture sequence and ledger commit order are distinct; ledger commit_index records handling order, not source chronology
- canonical bounded live ingest history now lives in `traces/live_ingest_ledger_v0.jsonl`
- the live probe trace now summarizes and references authoritative history rather than owning complete records
- canonical bounded live ingest history continued from 12 to 14 records across reopen/process discontinuity
- the original 12-record prefix remained structurally unchanged after continuation
- per-record integrity verified before and after continuation, but ledger-wide history integrity remains unimplemented
- ledger-wide continuity verification now checks duplicate commit indices, missing internal commit indices, and duplicate record IDs separately from per-record integrity
- canonical live ingest continuity additionally requires start at commit index 1
- a derived experiment trace can witness prior H14 extent without becoming authoritative history
- temporary tail loss of `rec-000014` remains internally valid while failing witnessed extent correspondence
- witness disagreement is preserved as mismatch evidence, not corruption proof or repair authority
- exact extent equality collapses tail loss, extension, and replacement into generic mismatch
- lower-bound extent separates shrinkage from non-shrinkage but does not distinguish extension from replacement
- prefix preservation distinguishes loss, control, extension, and replacement within the bounded append-only pressure
- terminal record digest alone does not commit to interior prefix history in the current non-chained ledger
- ordered record IDs and commit indices do not establish historical content identity
- ordered record digests are the smallest sufficient tested prefix witness projection within the bounded pressure
- historical identity can change without changing current reconstruction/projection shape
- hash chains, manifests, partial-write recovery, and repair remain deferred
- no index exists or is yet justified by lookup pressure
