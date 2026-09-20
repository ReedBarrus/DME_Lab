# Memory Matrix Pressure 002 — Round 2 Failure Checkpoint

**Status:** TWO INDEPENDENT FAILURES / ROUND 3 REPAIR ACTIVE  
**Pressure:** MM-002  
**Round 2 carrier:** checkpoint + immutable basis envelope  
**Observers:** Claude and Gemini, operator-supplied independent reconstructions

## Result

Both observers confirmed that the Round 1 loss was repaired:

```text
repository-relative path
!=
immutable historical source identity
```

They could recover the exact four Council round blobs and shared historical
commit without guessing.

Both observers nevertheless returned:

`CHECKPOINT MEMORY ROUND-TRIP FAILS`

## Shared smallest consequential loss

The repaired carrier still pools deliberation outcomes and does not preserve
which actor/round introduced, attacked, displaced, accepted, or narrowed each
consequential proposal transition.

Therefore:

```text
decision-level outcome topology
!=
actor/round causal topology
```

The exact source blobs make the raw history reachable, but the hot-memory
carrier itself cannot reconstruct that causal provenance without reopening the
raw rounds.

## Why this counts as consequential

The missing attribution distinguishes:

- proposal introduction from criticism;
- preservation-as-candidate from displacement;
- replacement from acceptance;
- scope narrowing from validation;
- supersession from falsification.

Without those relations, an observer can recover *what survived* but not the
causal deliberation path that made the surviving proposal warranted.

## Minimal repair

Do not rewrite the checkpoint or basis envelope.

Add only:

`docs/candidates/memory_matrix_v0/MM002_COUNCIL_CAUSAL_LINEAGE_ENVELOPE_v0.md`

which maps the four immutable round artifacts to the consequential
proposal-transition relations they establish.

Round 3 tests:

```text
checkpoint
+
immutable basis envelope
+
causal lineage envelope
```

No generalized deliberation schema, graph ontology, or raw-round duplication is
earned by this repair.
