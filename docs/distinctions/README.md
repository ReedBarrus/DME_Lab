# Distinction Registry

## Purpose

The distinction registry is development memory for distinctions that have become useful enough to conserve.

It helps future human and agent work reduce drift, avoid rediscovering the same non-equivalences, and preserve the basis by which a distinction is currently supported.

## Non-Authority

The registry is not the DME distinction field, an ontology, a truth corpus, a consequence field, a semantic knowledge graph, an embedding space, or a geometric atlas.

Repository contracts, runtime traces, tests, and implementation remain the primary evidence surfaces according to project authority order. A registry entry should guide attention; it does not override contradictory runtime evidence.

## Record Shape

Each JSONL line is one provisional distinction record:

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

The distinction is the `left` / `relation` / `right` content. The `basis` records why it is currently supported.

## Basis Vocabulary

- `structural_observation`: Directly visible from persisted or machine-readable structure without requiring semantic interpretation.
- `deterministic_test`: Supported by a deterministic test with inspectable inputs, mechanism, and assertions.
- `runtime_observation`: Supported by observed runtime behavior but not necessarily encoded as a formal deterministic assertion.
- `code_inspection`: Derived from direct inspection of implementation structure.
- `semantic_inference`: Produced by human or probabilistic agent reasoning over available evidence.
- `design_constraint`: Intentionally imposed by an active project contract or development decision rather than discovered empirically.

These basis values preserve provenance. They are not confidence scores or an epistemic ranking.

## Standing Vocabulary

- `candidate`: Useful enough to preserve, but not yet strongly supported by current repository evidence.
- `supported`: Supported by current repository evidence within its stated scope.

## Amendability

Entries are provisional and may later be refined, superseded, structurally reconstructed, or represented differently.

Do not silently rewrite the historical meaning of an entry when later evidence changes it. A future amendment mechanism may be introduced if runtime pressure demands it.

## Future Direction

The registry may later become one projection over a more structurally reconstructed distinction topology:

```text
runtime / ledger / traces
-> reconstructed topology
-> detected structural distinction
-> distinction registry projection
-> human / agent readable expression
```

Current development may also proceed in the opposite direction:

```text
human / LLM reasoning
-> semantic distinction candidate
-> testable formulation
-> runtime pressure
-> structural evidence
```

Neither path is fully implemented yet. The registry should preserve enough provenance that those paths can later be compared.

