# Tie-Order Invariance Pressure v0

## Pressure

This pressure reused Chart 9 C2 unchanged. One pressure record and witnessed
`rec-000002` share commit index 2. Unequal indices remain ordered ascending, but
the tie has no canonical secondary order.

No runtime stable-sort order was treated as authoritative.

## Bounded Linearizations

Exactly two complete orderings satisfy the known constraints:

                                      prefix  ordered subsequence
    pressure record, then rec-000002    false          true
    rec-000002, then pressure record    false          true

All other record positions remain fixed by unequal commit indices.

## Result

Canonical replay ordering remains UNRESOLVED. Whole-state C2 admissibility also
remains UNRESOLVED.

Both relations are invariant across every bounded compatible linearization:

- prefix is RESOLVED_BY_ORDER_INVARIANCE as false
- ordered subsequence is RESOLVED_BY_ORDER_INVARIANCE as true

Existence of one favorable ordering was not sufficient. No tie-break or
secondary key was introduced.

## Back-Pressure

Chart 9 remains valid. C2 is refined by new evidence: unresolved exact order
does not force uncertainty in these two relation consequences when every
permitted ordering agrees.

This strengthens I_B(O) = (B, sigma_B(O)) without changing it. The bounded basis
can retain unresolved internal coordinates while its observed response remains
invariant over that uncertainty.

A future navigator may not require exact state resolution when every currently
admissible resolution produces the same decision-relevant consequence. No
navigator, scheduler, attention, or cost mechanism was added.

## Finding

ordering_resolution != relation_resolution

No production replay change, tie-break, secondary ordering key, partial-order
engine, permutation framework, basis object, tensor, atlas, schema, DSL,
persistence, or generalized interpreter was added.

Next pressure: one whole-stack adversarial composition pass across the currently
earned capture, ledger, reconstruction, and relation boundaries.
