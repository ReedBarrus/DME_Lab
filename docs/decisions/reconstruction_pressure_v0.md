# Reconstruction Pressure v0

## Status

Bounded v0 reconstruction mechanism implemented for admission relationships.

This pass did not implement indexing, generalized topology, a graph database, a generalized reconstruction engine, a generalized projection engine, admission conflict resolution, latest-decision semantics, Windows capture, a filesystem watcher, distributed state, or agent runtime.

## Executable Relation

The implemented relation is:

```text
authoritative ledger replay
-> reconstructed observation/admission relationships
-> derived admitted projection
-> provenance path back to source records
```

The append-only ledger remains authoritative. Reconstruction is derived from replay and is not a second source of truth.

## Reconstructed Structure

The bounded reconstruction is `admission_relationships_v0`.

It preserves:

- `reconstruction_type`
- authoritative replayed `record_id`s
- observation record id and commit index
- observation source
- observation provenance
- preserved observation payload
- referring admission record ids and commit indices
- comparator identity and version
- comparison result
- admission decision
- decision basis
- admitted projection participation
- orphan admission records when a subject record is missing

It does not create graph nodes, generalized edge types, topology classes, or an index.

## Projection

The bounded admitted projection now consumes reconstructed relationships.

Current v0 semantics remain:

```text
subject participates if at least one referring admission decision is admitted
```

Conflicting admission records are preserved and not resolved.

## Runtime Evidence

Trace:

```text
traces/reconstruction_pressure_v0.json
```

The trace rebuilds reconstruction and projection twice from the same replayed authoritative records.

Results:

- authoritative records replayed: 8
- reconstructed observations: 3
- admitted projected subjects: 2
- reconstruction rebuild structural equality: yes
- projection rebuild structural equality: yes
- integrity verification: yes

## Earned Distinctions

- `authoritative_history != reconstructed_representation`
- `reconstruction != projection`

`replay != reconstruction` is preserved by the runtime shape, but not registered separately in this pass.

No index distinctions were added because no index exists.

## Contract Changes

General reconstruction remains projected.

A bounded v0 reconstruction mechanism is implemented for admission relationships only.

Projection remains projected for the general system, with one bounded admitted projection consumed by the reconstruction pressure trace.

## Unresolved Pressure

- no index or acceleration surface
- no generalized topology
- no admission conflict resolution
- no latest-decision semantics
- no reconstruction over repository transition paths
- no durable reconstruction store
- no generalized projection engine

## Next Frontier

Run the controlled repository probe through the current chain:

```text
capture observations
-> append observation/admission records
-> replay
-> reconstruct admission relationships
-> derive admitted projection
```

Do not introduce an index until replay scans fail under concrete lookup pressure.
