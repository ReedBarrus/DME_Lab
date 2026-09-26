# PARTIAL_BASIS_RETENTION_PROFILE_001 — G10 Contract V0

STATUS:
CANDIDATE

GAP:
G10_PARTIAL_DECLARED_BASIS_RETENTION_PROFILE

PREDECESSOR:
RETENTION_SCOPE_AGGREGATION_V0_MATCHED

DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

PURPOSE:
Test whether one exact partial declared basis can carry a non-scalar retention
profile over its supplied horizons while the exterior remains explicitly
unresolved, and whether extending that basis preserves unchanged local horizon
coordinates.

This pressure asks:

```
WHAT IS THE RETENTION PROFILE
ON THIS EXACT DECLARED BASIS?
```

not:

```
WHAT IS GLOBAL HOTNESS?
WHAT IS A UTILITY SCORE?
WHAT IS THE OPTIMAL RETENTION POLICY?
```

## Local posture vocabulary

Each horizon in the declared basis carries exactly one local posture:

```
REQUIRED
UNRESOLVED
NOT_REQUIRED_FOR_DECLARED_HORIZON
```

## Basis profile

For a non-empty declared basis B, preserve the profile as three explicit member
sets:

```
REQUIRED_MEMBERS
UNRESOLVED_MEMBERS
NOT_REQUIRED_MEMBERS
```

and exact counts:

```
N_REQUIRED
N_UNRESOLVED
N_NOT_REQUIRED
BASIS_SIZE
```

No scalar importance or load score is inferred from these counts.

The basis also carries:

```
EXTERIOR_POSTURE = UNRESOLVED
GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED
```

because the declared basis is not asserted to exhaust all relevant horizons.

## Extension law

For an exact basis extension:

```
B0 subset B1
```

where every horizon already present in B0 retains the same local posture in B1:

```
PRIOR_LOCAL_COORDINATES_PRESERVED = YES
```

New horizons may extend the profile without mutating unchanged prior local
coordinates.

Required calibration:

```
B0:
H_A = REQUIRED
H_B = NOT_REQUIRED_FOR_DECLARED_HORIZON

PROFILE(B0):
REQUIRED = {H_A}
UNRESOLVED = {}
NOT_REQUIRED = {H_B}
COUNTS = (1, 0, 1)

B1 = B0 + H_C
H_C = UNRESOLVED

PROFILE(B1):
REQUIRED = {H_A}
UNRESOLVED = {H_C}
NOT_REQUIRED = {H_B}
COUNTS = (1, 1, 1)

PRIOR_LOCAL_COORDINATES_PRESERVED = YES
```

## Relationship to G9

The existing G9 aggregation law may still derive:

```
DECLARED_SCOPE_HOT_REQUIREMENT
```

from the profile.

But:

```
RETENTION PROFILE VECTOR
!=
DECLARED-SCOPE AGGREGATE POSTURE

DECLARED-SCOPE AGGREGATE POSTURE
!=
GLOBAL ECOLOGY HOT REQUIREMENT
```

## Required non-collapses

```
PARTIAL DECLARED BASIS
!=
GLOBAL ECOLOGY

PROFILE COUNTS
!=
LOAD WEIGHTS

PROFILE VECTOR
!=
SCALAR HOTNESS

BASIS EXTENSION
!=
PRIOR LOCAL INVALIDATION

UNRESOLVED EXTERIOR
!=
EMPTY EXTERIOR

LOCAL COORDINATE PRESERVATION
!=
GLOBAL INVARIANCE

OBSERVABLE INTELLIGENCE
!=
CONSEQUENTIAL BEHAVIOR
```

## Effect ceiling

```
retention_transition_effect = NONE
raw_source_deletion_effect = NONE
method_capitalization_effect = NONE
policy_mutation_effect = NONE
planning_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

## Claim ceiling

G10 may establish only that one exact partial declared basis can be represented
as a non-scalar retention profile over REQUIRED / UNRESOLVED / NOT_REQUIRED
member sets, with the exterior remaining explicitly unresolved, and that an
extension preserving prior local inputs preserves those prior local
coordinates.

It does not establish global ecology coverage, load weighting, scalar hotness,
economic optimality, global invariance, cooling authority, retention transition,
deletion permission, capitalization, autonomous planning, authority, execution,
or scientific standing.
