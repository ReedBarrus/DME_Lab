# RETENTION_SCOPE_AGGREGATION_001 — G9 PRESSURE 001

OBJECT_TYPE:
READY_TO_RUN_RETENTION_SCOPE_AGGREGATION_PACKET

PRESSURE_ID:
RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_001

GAP_ID:
G9_RETENTION_SCOPE_AGGREGATION

STATUS:
READY

PREDECESSOR:
DISTINCTION_RETENTION_CURRENTNESS_V0_MATCHED

DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

MODE:
EXACT_G8_CURRENTNESS_BASIS
+
DECLARED_HORIZON_SET
+
SCOPE_AGGREGATION_ONLY
+
NO_GLOBAL_ECOLOGY_COMPLETENESS
+
NO_GLOBAL_COOLING
+
NO_RETENTION_TRANSITION
+
NO_RAW_SOURCE_DELETION
+
NO_DEPRECIATION
+
NO_RETIREMENT
+
NO_QUANTITATIVE_COST_OPTIMUM
+
NO_METHOD_CAPITALIZATION
+
NO_AUTOMATIC_PLANNING
+
NO_AUTHORITY
+
NO_EXECUTION
+
NO_SCIENTIFIC_PROMOTION

# FROZEN G8 BASIS

Required G8 result:

`docs/campaigns/distinction_retention_currentness_001/pressure_runs/DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_RESULT_001.md`

Required G8 result blob:

`e5f603fbea6ef05193f092245252cd26d6eae66a`

Required G8 witness:

`distinction_retention_currentness_v0_observation.json`

Required G8 witness blob:

`949ff2b9333146ca16e68981123f338f6e4dfd15`

Required standing:

`DISTINCTION_RETENTION_CURRENTNESS_V0_MATCHED`

Required local posture vocabulary:

```
REQUIRED
NOT_REQUIRED_FOR_DECLARED_HORIZON
UNRESOLVED
```

# DECLARED-SCOPE AGGREGATION LAW

For one exact non-empty declared set of horizons:

```
if ANY local posture == REQUIRED:
    DECLARED_SCOPE_HOT_REQUIREMENT = REQUIRED

else if ANY local posture == UNRESOLVED:
    DECLARED_SCOPE_HOT_REQUIREMENT = UNRESOLVED

else:
    DECLARED_SCOPE_HOT_REQUIREMENT = NOT_REQUIRED_FOR_DECLARED_SCOPE
```

# REQUIRED CALIBRATION CASES

```
CASE_A:
{REQUIRED, NOT_REQUIRED_FOR_DECLARED_HORIZON}
→ REQUIRED

CASE_B:
{NOT_REQUIRED_FOR_DECLARED_HORIZON,
 NOT_REQUIRED_FOR_DECLARED_HORIZON}
→ NOT_REQUIRED_FOR_DECLARED_SCOPE

CASE_C:
{NOT_REQUIRED_FOR_DECLARED_HORIZON, UNRESOLVED}
→ UNRESOLVED

CASE_D:
{REQUIRED, UNRESOLVED}
→ REQUIRED
```

# REQUIRED SCOPE POSTURE

For every case:

```
DECLARED_SCOPE_COMPLETE_FOR_SUPPLIED_HORIZONS = YES

GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED

EXACT_COLD_SOURCE_RETENTION_REQUIRED = YES
```

# REQUIRED NON-COLLAPSES

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

# REQUIRED EFFECT CEILING

Every case must preserve:

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

# EXECUTION

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item retention_scope_aggregation_v0_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.control.test_retention_scope_aggregation_v0 `
  tests.control.test_distinction_retention_currentness_v0 `
  tests.control.test_distinction_retention_mode_v0 `
  tests.control.test_current_horizon_distinction_dependence_v0 `
  tests.control.test_method_distinction_load_ablation_v0 `
  tests.control.test_world_method_reconciliation_v0 `
  tests.control.test_horizon_gap_selector_v0 `
  tests.control.test_relational_horizon_v0

python tools/observe_retention_scope_aggregation_v0.py
```

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] REQUIRED + NOT_REQUIRED -> REQUIRED
[OK] all NOT_REQUIRED -> NOT_REQUIRED_FOR_DECLARED_SCOPE
[OK] NOT_REQUIRED + UNRESOLVED -> UNRESOLVED
[OK] REQUIRED + UNRESOLVED -> REQUIRED
[OK] global_ecology_hot_requirement UNRESOLVED
```

# STOP LAW

A passing witness may establish only:

```
AN EXACT DECLARED SET
OF HORIZON-LOCAL HOT REQUIREMENTS

CAN BE AGGREGATED
INTO ONE DECLARED-SCOPE POSTURE
```

It must stop before:

```
GLOBAL ECOLOGY COMPLETENESS
GLOBAL HOT REQUIREMENT
GLOBAL COOLING
RETENTION TRANSITION EXECUTION
RAW SOURCE DELETION
DEPRECIATION
RETIREMENT
QUANTITATIVE COST OPTIMIZATION
AUTONOMOUS PLANNING
```

# CLAIM CEILING

At the exact supplied source, a non-empty declared set of horizon-local
retention requirements for WORLD_CHANGE != METHOD_CHANGE may be aggregated
deterministically into one declared-scope hot-requirement posture.

A passing result does not establish that the declared set is globally complete,
does not resolve the global ecology hot requirement, and does not establish
cooling authority, retention-transition authority, deletion permission,
depreciation, retirement, quantitative carrying-cost optimization, method
capitalization, autonomous planning, authority, execution, or scientific
standing.

STOPPED:
YES
