# Constraint Registry

## Purpose

The Constraint Registry is non-authoritative development memory for reusable,
scoped limits on interpretation and equivalence. Its job is to reduce drift and
prevent already-disproven collapses, not to store every local distinction or
choose research direction.

Working interpretation:

```text
constraint
=
a reusable scoped limit on admissible equivalence / inference
supported by declared basis + provenance

distinction
=
a local discrimination produced when a constraint is applied
to concrete observations / subjects / claims under a declared basis
```

For example, D-0012 constrains a snapshot from being treated as complete
transformation history. Applied to the absent-interval evidence, it preserves
the local distinction between stasis and alpha -> beta -> alpha under an
endpoint-snapshot basis.

## Non-authority and scope

The registry is not evidence for its own entries, an ontology, a truth corpus,
a requirement set, a consequence field, a task list, a semantic graph, a
distinction-event store, or a runtime engine. Repository contracts, traces,
tests, implementation, and decision records remain the evidence surfaces.

`supported` always means supported under the entry's declared `scope`, `basis`,
and `provenance`. It does not promote a scoped relation into a general truth.
Design constraints are imposed rather than empirically discovered. Semantic
inferences are not deterministic proofs. Code-inspection and runtime-observation
entries remain vulnerable to implementation or specimen drift.

The registry constrains interpretation; pressure and consequence create the
research dynamics. Contradictory or stronger repository evidence wins.

## Historical identifiers

The `D-*` IDs are preserved historical identifiers. They are not renumbered
even though this artifact's current interpreted role is constraint memory.
Earlier decisions may correctly call them distinctions in their historical
context.

## Record shape

Each JSONL line is one provisional constraint-memory record:

```json
{
  "id": "D-0001",
  "left": "runtime_trace",
  "relation": "not_equivalent_to",
  "right": "test_verdict",
  "scope": "ledger_runtime_pressure_v0",
  "basis": "code_inspection",
  "provenance": ["src/runtime/ledger_pressure.py"],
  "standing": "supported",
  "note": "Short reason this distinction is currently conserved."
}
```

The reusable constraint is the scoped `left` / `relation` / `right` content.
The `basis` and `provenance` record why it is currently legitimate. Applying
that constraint to concrete evidence may produce a local distinction without
creating a new registry row.

## Basis Vocabulary

- `structural_observation`: Directly visible from persisted or machine-readable structure without requiring semantic interpretation.
- `deterministic_test`: Supported by a deterministic test with inspectable inputs, mechanism, and assertions.
- `runtime_observation`: Supported by observed runtime behavior but not necessarily encoded as a formal deterministic assertion.
- `code_inspection`: Derived from direct inspection of implementation structure.
- `semantic_inference`: Produced by human or probabilistic agent reasoning over available evidence.
- `design_constraint`: Intentionally imposed by an active project contract or development decision rather than discovered empirically.

These basis values preserve provenance. They are not confidence scores or an
epistemic ranking. A row may be reclassified when later evidence directly
strengthens or narrows its support, but that change must retain lineage.

## Standing Vocabulary

- `candidate`: Useful enough to preserve, but not yet strongly supported by
  current repository evidence.
- `supported`: Supported by the stated basis and provenance within the stated
  scope; not necessarily empirical or universal.

## Where concrete distinctions live

Concrete distinction events are currently represented mainly in pressure
traces, decision comparisons, and deterministic test assertions. Reconstruction
artifacts preserve source and admission relations used by some comparisons,
but do not persist a general distinction-event object. No explicit persistent
distinction-event store exists.

## Research use

This recurring descriptive pattern is not a formal engine order:

```text
pressure / consequence
-> observation
-> local comparison
-> constraint applied
-> distinction preserved
-> integration / projection
```

Constraints should prevent unsupported collapse while leaving selection of the
next pressure to the human research process.

## Amendability

Entries are provisional and may later be refined, narrowed, contradicted,
superseded, or represented differently.

Do not silently rewrite historical meaning when later evidence changes an
entry. No amendment mechanism, constraint operator, distinction detector, or
formal grammar is implemented or implied here.
