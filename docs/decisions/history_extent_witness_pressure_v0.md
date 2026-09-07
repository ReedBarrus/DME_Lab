# History Extent Witness Pressure v0

## Pressure

A temporary ledger with final record `rec-000014` removed remains locally valid:
per-record integrity passes, continuity passes, replay succeeds, and
reconstruction/projection still run.

The question was whether existing non-authoritative evidence could expose that
the current extent no longer corresponds to a previously witnessed extent.

## Witness

Primary witness:

`traces/live_ingest_continuation_v0.json`

Classification:

derived experiment witness

It preserves `record_count`, terminal `record_id`, and terminal `commit_index`
for the 14-record continuation result.

## Result

Canonical H14 corresponds to the witness.

Temporary H13 does not:

- current `record_count`: `13`
- witnessed `record_count`: `14`
- current terminal record: `rec-000013`
- witnessed terminal record: `rec-000014`
- current terminal commit index: `13`
- witnessed terminal commit index: `14`

This is witness disagreement, not corruption proof.

## Downstream Difference

`rec-000013` survives as an observation.

`rec-000014`, its admission record, is absent from H13.

The admitted projection loses subject `rec-000013`.

## Deferred

No checkpoint, manifest, history digest, hash chain, Git-backed runtime storage,
repair policy, amendment record, witness registry, index, or database was added.
