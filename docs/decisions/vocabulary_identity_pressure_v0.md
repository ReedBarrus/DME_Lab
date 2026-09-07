# Vocabulary Identity Pressure v0

## Pressure

Chart 5 held the H14 ordered-digest carrier, S9 declaration structure, five
historical specimens, and recovery question fixed. It varied only declaration
token interpretation.

The vocabulary descriptions remained local experiment values. They are not a
schema, registry, DSL, persistent format, or interpretation-free semantics.

## Mapping Candidate

The correct local vocabulary supplied eight bindings:

- SHA-2/256 algorithm operation
- record_id, commit_index, and envelope source paths and boundary keys
- JSON text serialization
- UTF-8 encoding
- ascending ordering
- left-sequence-prefix comparison

Optional vocabulary name, version, and provenance metadata did not affect the
bounded evaluator.

## Chart 5

                                         H13  H14  H16+  H16-ID  H16-content
    V0  ambient control                    M    R    R      M         M
    V1  tokens only                        U    U    U      U         U
    V2  correct mapping with identity      M    R    R      M         M
    V2a mapping only                       M    R    R      M         M
    V3a no relation mapping                U    U    U      U         U
    V3b no record_id field mapping         U    U    U      U         U
    V3c no serialization mapping           U    U    U      U         U
    V3d no algorithm mapping               U    U    U      U         U
    V4  prefix mapped to equality          M    R    M      M         M
    V5  wrong record_id field binding      M    M    M      M         M
    V6  selected tokens renamed            M    R    R      M         M
    V7  all tokens and identity renamed     M    R    R      M         M

R is RECOVERED, M is MISMATCHED, and U is UNRESOLVED.

Counts: 11 recovered, 24 mismatched, and 25 unresolved.

## Result

V2a was the smallest sufficient tested vocabulary description: eight semantic
bindings without vocabulary identity metadata. V3a was the selected nearest
insufficient regime at seven bindings; the three other focused one-binding
omissions were tied.

Tokens without mappings and partial mappings did not inherit ambient meaning.
Wrong complete mappings remained executable: sequence equality rejected the
legitimate H16 extension, while the wrong field binding mismatched every
history.

These mismatches are interpretation results, not evidence that history is
corrupt.

V6 and V7 changed lexical coordinates while preserving descriptor mappings,
declaration shape, and the complete R6/S9 historical outcome pattern.

## Back-Pressure

Chart 4's ten components remain necessary under its fixed evaluator vocabulary.
Chart 5 refines that result by separating semantic role, token spelling, and
recoverable binding. Original lexical values are not phenomenon-level
necessities when equivalent mappings survive.

This axis split supports chart-fold pressure. It does not invalidate Chart 4,
and no folding or transition machinery was implemented.

## Residual Interpretation

The evaluator still supplies the vocabulary-description structure and executes
the hash, field, serialization, encoding, ordering, and relation descriptors.

vocabulary interpretation conserved != interpretation eliminated

## Finding

token_identity != semantic_operation_identity

No vocabulary registry, semantic registry, schema, DSL, parser framework,
ontology, chart registry, atlas, transition map, witness persistence, repair,
or generalized interpreter was added.

Next pressure: test one operation descriptor identity across evaluator-version
change without persistence.
