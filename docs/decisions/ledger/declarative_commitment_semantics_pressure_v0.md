# Declarative Commitment Semantics Pressure v0

## Pressure

Chart 4 kept the H14 ordered-digest carrier and five historical specimens fixed.
It changed only how commitment interpretation was represented.

The declaration remained a local in-memory experiment value. It is not a
schema, persistent format, or interpretation-free specification.

## Full Candidate

```json
{
  "algorithm": {"name": "sha256"},
  "boundary": {"fields": ["record_id", "commit_index", "envelope"]},
  "canonicalization": {
    "format": "json",
    "sort_keys": true,
    "separators": [",", ":"],
    "ensure_ascii": false,
    "encoding": "utf-8"
  },
  "ordering": {"field": "commit_index", "direction": "ascending"},
  "relation": {"type": "prefix"},
  "candidate_commitment": {"mode": "recompute_from_record"}
}
```

## Chart 4

```text
                                         H13  H14  H16+ H16-ID H16-content
S0  full explicit semantics               M    R    R     M       M
S1  no algorithm                          U    U    U     U       U
S2  no boundary                           U    U    U     U       U
S3  no canonicalization                   U    U    U     U       U
S3a no canonicalization format            U    U    U     U       U
S3b no canonicalization sort_keys         U    U    U     U       U
S3c no canonicalization separators        U    U    U     U       U
S3d no canonicalization ensure_ascii      U    U    U     U       U
S3e no canonicalization encoding          U    U    U     U       U
S4  no ordering                           U    U    U     U       U
S4a no ordering field                     U    U    U     U       U
S5  no relation                           U    U    U     U       U
S6  opaque aliases only                   U    U    U     U       U
S7  wrong complete boundary               M    M    M     M       M
S8  wrong complete canonicalization       M    M    M     M       M
S9  no candidate commitment mode          M    R    R     M       M
S10 no ordering direction                 U    U    U     U       U
```

`R` is `RECOVERED`, `M` is `MISMATCHED`, and `U` is `UNRESOLVED`.

Counts: 4 recovered, 16 mismatched, and 65 unresolved.

## Result

S0 reproduced the Chart 3 R6 outcomes. S9 preserved the same outcomes after
removing `candidate_commitment.mode`; recomputation is already implied by the
bounded evaluator operation.

The smallest sufficient tested declaration therefore contains:

- `algorithm.name`
- `boundary.fields`
- all five tested canonicalization parameters
- `ordering.field` and `ordering.direction`
- `relation.type`

Removing any one of those components made all five histories unresolved. S5 is
the selected nearest smaller insufficient representation because it directly
corresponds to Chart 3 R5. Other one-component ablations have the same measured
size and are retained in the trace.

S6 showed that `current_record` and `current` are ambient implementation handles,
not independently recoverable semantic descriptions. S7 and S8 remained
executable but made every history mismatched.

## Residual Interpretation

The evaluator still supplies the declaration vocabulary, token mappings,
field lookup, boundary construction, sorting, prefix comparison, outcome rules,
and recomputation operation.

`declarative semantics survived != semantics are interpretation-free`

## Overlap

R6 and S0/S9 produced equal outcomes over shared H13, H14, and H16 specimens.
This is an executable bounded correspondence across Charts 1-4. It strengthens
proto-transition pressure but does not establish or implement a transition map.

## Finding

`semantic_label != recoverable_semantic_description`

No persistence, schema, manifest, checkpoint, registry architecture, atlas,
transition map, hash chain, repair, or generalized interpreter was added.

Next pressure: identify the minimum identity and provenance needed to recover
the local evaluator vocabulary without creating persistence architecture.
