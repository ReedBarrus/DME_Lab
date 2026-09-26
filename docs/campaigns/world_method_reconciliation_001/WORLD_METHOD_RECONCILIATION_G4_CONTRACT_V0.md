# WORLD_METHOD_RECONCILIATION_001 — G4 Contract V0

STATUS:
CANDIDATE

GAP:
G4_WORLD_METHOD_RECONCILIATION_FORK

PREDECESSOR FLOOR:
main @ fcaf3fe49e1f76781a1f568caa87540d00da4937

PURPOSE:
Represent two distinct post-consequence questions without collapsing them:

```
DID THE WORLD / TARGET POSTURE CHANGE?
!=
DID THE COGNITIVE METHOD CHANGE?
```

## Axes

WORLD_POSTURE_CHANGE:

```
CHANGED
UNCHANGED
UNRESOLVED
```

COGNITIVE_METHOD_CHANGE:

```
CHANGED
UNCHANGED
UNRESOLVED
```

The axes are independent.

Required representable examples:

```
WORLD_ONLY
  world  = CHANGED
  method = UNCHANGED

METHOD_ONLY
  world  = UNCHANGED
  method = CHANGED

BOTH
  world  = CHANGED
  method = CHANGED

NEITHER
  world  = UNCHANGED
  method = UNCHANGED

UNRESOLVED on either axis
  remains explicitly unresolved
```

## Required bindings

Every reconciliation must bind:

- one exact source reconciliation identity;
- exact source reconciliation state identity hash;
- externally supplied world-change disposition;
- externally supplied world evidence refs;
- externally supplied method-change disposition;
- externally supplied method evidence refs.

## Required non-collapses

```
WORLD CHANGE
!=
METHOD CHANGE

OBSERVED CHANGE
!=
CAUSAL ATTRIBUTION

METHOD CHANGE
!=
METHOD IMPROVEMENT

METHOD IMPROVEMENT
!=
METHOD CAPITALIZATION

RECONCILIATION
!=
POLICY MUTATION

RECONCILIATION
!=
NEW WORK JUSTIFICATION
```

## Effect ceiling

This cell must create:

```
gap_selection_effect = NONE
work_justification_effect = NONE
planning_effect = NONE
method_capitalization_effect = NONE
policy_mutation_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

## Claim ceiling

G4 may establish only that one exact source reconciliation can be extended with
two separately evidenced, deterministic, non-causal post-consequence axes for
world posture change and cognitive method change.

It does not establish automatic learning, causal inference, policy update,
method promotion, gap discovery, work selection, authority, execution, or
scientific standing.
