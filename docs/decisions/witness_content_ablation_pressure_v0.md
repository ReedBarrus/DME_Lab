# Witness Content Ablation Pressure v0

## Pressure

Prefix preservation distinguished tail loss, control, extension, and larger
replacement. This pressure removed witness information to find which projected
content actually carried that distinction.

No first-class witness storage was introduced.

## Specimens

The prior H14 comparison evidence came from Git commit `e399720`.

Temporary specimens:

- H13 tail loss
- H14 control
- H16 extension
- H16 ID replacement
- H16 content replacement

The content replacement changed only:

`envelope.provenance.observation_point`

on record `rec-000001`, then recomputed that record digest.

All specimens passed current per-record integrity and continuity.

## Projection Finding

Tested witness projections:

- extent only
- terminal digest only
- ordered record IDs
- ordered record IDs plus commit indices
- ordered record digests
- ordered commit index plus digest
- current five-field prefix identity
- full canonical prior records

Smallest sufficient tested projection:

`ordered_record_digests`

This is sufficient only in the bounded pressure, with current digest semantics
available.

Record IDs plus commit indices did not detect same-ID content replacement.

Terminal digest did not detect interior prefix replacement because records are
not hash-chained.

Commit indices did not add branch-discrimination power beyond ordered digests,
but they remain diagnostically useful.

## Digest Boundary

Current digest commits to:

- `record_id`
- `commit_index`
- `envelope`

`integrity.algorithm` and `integrity.boundary` are stored, but current
verification does not check them.

They are redundant for this bounded discrimination when runtime constants are
assumed, but remain necessary interpretation metadata for an independent digest
sequence.

## Result

`record_identity_sequence` is not equivalent to `record_content_identity`.

H16 content replacement broke historical identity while leaving current
reconstruction/projection shape unchanged.

## Deferred

No checkpoint, manifest, history digest, hash chain, Merkle structure, witness
registry, recovery, repair, amendment, database, or index was added.
