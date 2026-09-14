# Admissible History Discriminator Pressure v0

## Pressure

This pressure asked whether the abstract difference between prefix and ordered
subsequence is reachable by a candidate history admitted by the current bounded
ledger contract.

The H14 carrier, digest boundary, replay ordering, continuity validator, and
canonical history remained unchanged.

## Abstract Control

For W = [a, b, c] and C = [a, X, b, c], prefix is false and ordered subsequence
is true. This demonstrates different operation semantics but is not a valid
historical specimen.

## Chart 8

                         integrity continuity ordered subsequence prefix admissible discriminator
    duplicate index          T          F         T        T         F       F          F
    fractional index         T          F         T        T         F       F          F
    shift later indices      T          T         T        F         F       T          F
    normal append            T          T         T        T         T       T          F

The duplicate index failed continuity. The fractional index was non-integer.
Shifting indices 2..14 and rehashing preserved integrity and continuity but only
one of fourteen H14 digests. Normal append preserved H14 as both relations.

## Result

No tested admissible discriminator exists. Under the exact current commitment
construction, ascending commit-index order, complete-history continuity, exact
digest comparison, the bounded H14 source, and absent a constructed digest
collision, preserved H14 digests retain indices 1..14. Any additional admissible
record must therefore follow them.

Within those assumptions:

admissible candidate history + exact H14 digest subsequence preservation
implies H14 digest prefix preservation.

This is not a universal theorem about append-only history or SHA-256.

## Back-Pressure

Chart 7 remains valid. Its empirical local indistinguishability is strengthened:
the current admissible history constraints prevent the interior sequence shape
needed to distinguish prefix from ordered subsequence for H14.

The evidence supports the local interpretation I_B(O) = (B, sigma_B(O)), where
B includes the admissible specimen domain. No runtime basis abstraction was
introduced.

A future navigator must preserve ambiguity when a discriminating pressure lies
outside its admissible state domain. No scheduler or tie-breaker was added.

## Finding

operation_semantics_difference != distinguishability_on_admissible_history

No canonical history, validator, digest boundary, scheduler, admissibility
engine, registry architecture, tensor, atlas, schema, DSL, persistence, search
framework, or generalized interpreter was added.

Next pressure: identify which single current history constraint is necessary
for the observed admissibility collapse.
