# METHOD_DISTINCTION_LOAD_001 — G5 Contract V0

STATUS:
CANDIDATE

GAP:
G5_METHOD_DISTINCTION_LOAD_ABLATION

PREDECESSOR:
WORLD_METHOD_RECONCILIATION_V0_MATCHED

SPECIMEN_DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

PURPOSE:
Test whether one exact admitted distinction carries any declared load by
mechanically ablating the distinction and observing what representational
discrimination is lost.

## Ablation

Pre-ablation representation:

```
WORLD_POSTURE_CHANGE
x
COGNITIVE_METHOD_CHANGE
```

Ablated representation:

```
GENERIC_CHANGE_POSTURE
```

with deterministic projection:

```
if either source axis is UNRESOLVED:
  GENERIC_CHANGE_POSTURE = UNRESOLVED

else if either source axis is CHANGED:
  GENERIC_CHANGE_POSTURE = CHANGED

else:
  GENERIC_CHANGE_POSTURE = UNCHANGED
```

Required collisions:

```
WORLD_ONLY
METHOD_ONLY
BOTH
→ CHANGED

NEITHER
→ UNCHANGED

WORLD_UNRESOLVED
METHOD_UNRESOLVED
→ UNRESOLVED
```

## Six-dimensional load profile

Use exactly the existing V0 load dimensions:

```
FUNCTIONAL
SEMANTIC
AUTHORITY
PROVENANCE
TEMPORAL
COORDINATION
```

For this calibration specimen the permitted result ceiling is:

```
SEMANTIC_LOAD_CHANGE = YES
```

only if ablation causes deterministic loss of previously preserved
world-vs-method discrimination.

All other load dimensions remain:

```
UNRESOLVED
```

unless this exact specimen mechanically exposes them.

## Required non-collapses

```
ABLATION EFFECT
!=
CURRENT LOAD-BEARING STATUS

SEMANTIC LOAD CHANGE
!=
METHOD IMPROVEMENT

SEMANTIC LOAD CHANGE
!=
RETENTION JUSTIFICATION

SEMANTIC LOAD CHANGE
!=
METHOD CAPITALIZATION

REPRESENTATIONAL COLLISION
!=
WORLD CONSEQUENCE

LOAD PROFILE
!=
SCALAR IMPORTANCE

DISTINCTION REPRESENTED
!=
DISTINCTION WORLD-SUPPORTED
```

## Effect ceiling

```
current_load_bearing_status = UNRESOLVED
retention_effect = NONE
method_capitalization_effect = NONE
policy_mutation_effect = NONE
gap_selection_effect = NONE
work_justification_effect = NONE
planning_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

## Claim ceiling

G5 may establish only that removing the exact distinction
WORLD_CHANGE != METHOD_CHANGE from the exact G4 case frame causes
deterministic representational collisions, and therefore that the distinction
carries semantic / representational load within that frame.

It does not establish current live-horizon dependence, functional load,
authority load, provenance load, temporal load, coordination load, causal
benefit, method improvement, retention value, capitalization, policy mutation,
work justification, authority, execution, or scientific standing.
