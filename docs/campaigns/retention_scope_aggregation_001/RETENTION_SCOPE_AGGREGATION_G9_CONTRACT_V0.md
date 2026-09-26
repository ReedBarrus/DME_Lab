# RETENTION_SCOPE_AGGREGATION_001 — G9 Contract V0

STATUS:
CANDIDATE

GAP:
G9_RETENTION_SCOPE_AGGREGATION

PREDECESSOR:
DISTINCTION_RETENTION_CURRENTNESS_V0_MATCHED

DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

PURPOSE:
Test whether multiple horizon-local hot-retention requirements for the same
distinction can be mechanically aggregated into one declared retention-scope
posture without claiming global ecology completeness.

This pressure asks:

```
GIVEN AN EXACT DECLARED SET OF HORIZONS,
DOES THIS DISTINCTION NEED TO STAY HOT
FOR THAT SET?
```

It does not ask whether the distinction is globally required by the entire
ecology, nor does it execute a retention transition.

## Horizon-local input law

Each declared horizon contributes exactly one externally supplied local posture:

```
REQUIRED
NOT_REQUIRED_FOR_DECLARED_HORIZON
UNRESOLVED
```

These local postures must already be earned or externally supplied according to
the G8 currentness membrane.

## Scope aggregation law

For one non-empty declared horizon set:

```
if ANY local posture == REQUIRED:
    DECLARED_SCOPE_HOT_REQUIREMENT = REQUIRED

else if ANY local posture == UNRESOLVED:
    DECLARED_SCOPE_HOT_REQUIREMENT = UNRESOLVED

else:
    DECLARED_SCOPE_HOT_REQUIREMENT = NOT_REQUIRED_FOR_DECLARED_SCOPE
```

Required calibration cases:

```
{REQUIRED, NOT_REQUIRED_FOR_DECLARED_HORIZON}
→ REQUIRED

{NOT_REQUIRED_FOR_DECLARED_HORIZON,
 NOT_REQUIRED_FOR_DECLARED_HORIZON}
→ NOT_REQUIRED_FOR_DECLARED_SCOPE

{NOT_REQUIRED_FOR_DECLARED_HORIZON, UNRESOLVED}
→ UNRESOLVED

{REQUIRED, UNRESOLVED}
→ REQUIRED
```

## Required scope split

For every case:

```
DECLARED_SCOPE_COMPLETE_FOR_SUPPLIED_HORIZONS = YES

GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED

EXACT_COLD_SOURCE_RETENTION_REQUIRED = YES
```

The declared scope is complete only for the exact supplied horizon set.
It is not asserted to enumerate all relevant horizons in the ecology.

## Required non-collapses

```
DECLARED HORIZON SET
!=
GLOBAL ECOLOGY

SCOPE HOT REQUIREMENT
!=
GLOBAL HOT REQUIREMENT

NO REQUIRED LOCAL HORIZON IN DECLARED SET
!=
SAFE GLOBAL COOLING

SCOPE AGGREGATION
!=
RETENTION TRANSITION

RETENTION TRANSITION
!=
AUTHORITY

UNRESOLVED LOCAL HORIZON
!=
NOT REQUIRED

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

G9 may establish only that an exact non-empty declared set of horizon-local
retention requirements for one distinction can be aggregated deterministically
into one declared-scope hot-requirement posture.

It does not establish that the declared set is globally complete, does not
resolve global ecology hot requirement, and does not establish cooling
authority, deletion permission, depreciation, retirement, quantitative cost
optimization, method capitalization, autonomous planning, authority, execution,
or scientific standing.
