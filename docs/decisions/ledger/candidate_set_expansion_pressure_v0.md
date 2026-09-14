# Candidate Set Expansion Pressure v0

## Pressure

The H14 carrier, S9 declaration, V2a vocabulary, B0/B1 cases, five historical
specimens, and Chart 6 implementations remained fixed.

One independent realization was added: `ordered_subsequence_v1`. It accepts a
witness whose digests occur in candidate order without requiring a contiguous
left prefix.

## Chart 7

                                     B0   B1   H13  H14  H16+  H16-ID  H16-content
    alternate iterative prefix       T    T     M    R    R      M         M
    sequence equality                 T    F     M    R    M      M         M
    ordered subsequence               T    T     M    R    R      M         M

T and F are executed behavioral results. R is RECOVERED and M is MISMATCHED.

## Selection

B1 uniquely selected iterative prefix from the original two candidates. After
candidate expansion, B1 matched iterative prefix and ordered subsequence.
Selection therefore returned UNRESOLVED. Candidate order did not break the tie.

## Observational Limit

Prefix and ordered subsequence produced the same complete outcome pattern over
all five existing historical specimens. They are locally indistinguishable
under this observer basis; universal behavioral equivalence is not claimed.

## Back-Pressure

Chart 6 E6 was sufficient relative to its original two-realization candidate
set. Candidate expansion refines that interpretation without invalidating the
Chart 6 experiment or D-0037.

A future scheduler cannot treat behavioral recognition as established when
multiple executable realizations remain consistent with the available evidence.
No scheduler or tie-break mechanism was added.

## Finding

behavioral_witness_sufficiency != candidate_set_independent_identity

No new historical specimen, registry architecture, equivalence-class machinery,
schema, DSL, persistence, atlas, transition map, or generalized interpreter was
added.

Next pressure: identify the smallest additional historical specimen that
distinguishes prefix from ordered subsequence.
