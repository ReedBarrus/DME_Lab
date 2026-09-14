# Ingest Admission Pressure v0

## Status

Bounded v0 ingest admission mechanism implemented.

This pass did not implement a generalized admission framework, topology generation, policy engine, source registry, cost model, graph store, Windows capture, filesystem watcher, semantic truth classification, or reconstruction engine.

## Executable Primitive

The implemented primitive is:

```text
preserved observation
-> provenance-bearing comparison/admission record
-> replay
-> derived admitted projection
```

One physical append-only JSONL ledger is used. Layers are logical:

- L0: observation / provenance record
- L1: comparison / admission record referring to L0
- L2: admitted projection derived from replay

## Record Shapes

L0 observation envelopes preserve:

```text
record_type
source
observation
provenance
```

L1 admission envelopes preserve exactly:

```text
record_type
subject_record_id
comparator_identity
comparator_version
comparison_result
decision
decision_basis
```

Initial decisions:

- `admitted`
- `rejected`
- `unresolved`

## Admission Behavior

Admission does not determine whether the original observation is preserved.

The observation record is appended first. The admission record later refers to its `record_id`.

The admitted projection is derived from replayed records by finding observation records with at least one referring admission record whose decision is `admitted`.

Multiple admission records for the same subject are preserved. No latest-policy or conflict-resolution mechanism exists.

## Comparator

The bounded comparator reuses the existing schema validation machinery with a small local schema for candidate observation records.

The comparator records:

- comparator identity
- comparator version
- comparison status
- comparison validity
- comparison errors

The schema comparison is not itself the admission decision.

## Runtime Evidence

Trace:

```text
traces/ingest_admission_pressure_v0.json
```

Pressure cases:

- structurally valid filesystem candidate: admitted
- structurally valid Git candidate: admitted
- malformed required field: rejected
- non-JSON-admissible value: preserved in temporary ledger, rejected by comparison
- same observation under two comparator versions: both admission records preserved
- unknown comparator version: unresolved

The non-JSON value case uses `math.nan` to expose current runtime behavior. The JSON trace summarizes that value rather than serializing it into the trace.

## Reconstructability Target

After replay, the implementation reconstructs:

- what observation was preserved
- which comparator examined it
- which comparator version was used
- what comparison result was produced
- what admission decision followed
- what decision basis was recorded
- whether the subject participates in the admitted projection

This is the full reconstructability target for this pass.

## Earned Distinctions

- `persisted_observation != admission_classification`
- `rejected != deleted`
- `observation_identity != admission_classification`

`comparison_result != admission_decision` remains important pressure, but this pass preserves it structurally rather than registering it as a separate earned distinction.

## Contract Changes

Ingest remains projected for the general system.

The bounded v0 admission mechanism is implemented and tested in a temporary ledger scope.

Ledger, schema, reconstruction, projection, capture, and provenance maturity are not upgraded.

## Unresolved Pressure

- no generalized admission policy
- no latest-applicable-decision rule
- no admission conflict resolution
- no cost or resource policy
- no topology participation rule beyond the simple admitted projection
- no durable admitted ledger
- no reconstruction engine consuming admission records
- non-JSON persistence remains current-runtime pressure, not a stable format guarantee

## Next Frontier

The next pressure frontier is the controlled repository probe:

```text
deliberate filesystem content transition
-> observe before Git commit
-> observe Git dirty state
-> commit
-> observe after commit
```

Use the admission mechanism to classify each preserved observation without deleting rejected or unresolved evidence.
