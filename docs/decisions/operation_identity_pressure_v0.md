# Operation Identity Pressure v0

## Pressure

Chart 6 held the H14 digest carrier, S9 declaration, V2a vocabulary, five
historical specimens, and outcome vocabulary fixed. It varied only the prefix
operation descriptor and evaluator realization.

No evaluator-version framework or operation registry was introduced.

## Evaluator Regimes

- E0: current Chart 5 prefix evaluator control
- E1: descriptor present, implementation absent
- E2: separately implemented iterative prefix
- E3: unchanged descriptor realized as sequence equality
- E4: renamed descriptor with iterative prefix
- E5: partial reflexive specification with extension behavior absent
- E6: one discriminating behavioral case selects a realization
- E7: one equal-history case matches both candidate realizations

E2 and E4 execute through operation_identity_pressure._prefix_alternate_iterative,
not the Chart 5 relation implementation.

## Chart 6

                                     H13  H14  H16+  H16-ID  H16-content
    E0 current prefix                  M    R    R      M         M
    E1 implementation absent           U    U    U      U         U
    E2 alternate iterative prefix      M    R    R      M         M
    E3 same descriptor, equality       M    R    M      M         M
    E4 renamed descriptor, prefix      M    R    R      M         M
    E5 partial specification           U    U    U      U         U
    E6 discriminating witness          M    R    R      M         M
    E7 equal-history witness           U    U    U      U         U

R is RECOVERED, M is MISMATCHED, and U is UNRESOLVED.

Counts: 9 recovered, 16 mismatched, and 15 unresolved.

## Behavioral Witness

Both prefix and equality accept H14 against H14. That case cannot identify the
operation.

Prefix accepts witnessed H14 against legitimate H16 extension; equality does
not. This one actual-domain case uniquely selected the alternate prefix among
the two tested realizations.

The one-case witness is the smallest sufficient tested operation-identity
representation. It is not evidence of universal operation equivalence and
depends on the tested candidate set.

## Result

The current and separately implemented iterative prefix paths produced the same
bounded historical outcomes. Implementation identity was not required.

The same descriptor paired with equality changed the H16 extension outcome.
Descriptor survival therefore did not establish operation recovery.

A renamed descriptor paired with equivalent iterative behavior preserved the
same historical consequences.

## Back-Pressure

Chart 6 refines Chart 5's semantic operation binding into operation descriptor,
implementation identity, and bounded behavioral identity. Chart 5 remains
valid under its tested evaluator.

This second axis split earns chart-fold pressure, but no folding machinery or
transition map was implemented.

Operation recognition now survives bounded lexical and implementation change.
This strengthens proto-scheduler grounding, but no schedulable primitive exists:
preconditions, effects, and admissibility remain absent.

## Finding

implementation_identity != operation_identity

No scheduler, queue, planner, agent runtime, operation registry, capability
registry, semantic registry, behavioral-contract framework, schema, DSL,
atlas, persistence, or generalized interpreter was added.

Next pressure: test the one-case behavioral witness against one additional
executable relation realization.
