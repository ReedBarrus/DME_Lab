# DISTINCTION_RETENTION_CURRENTNESS_001 — G8 PRESSURE 001

OBJECT_TYPE:
READY_TO_RUN_RETENTION_CURRENTNESS_PACKET

PRESSURE_ID:
DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_001

GAP_ID:
G8_RETENTION_CURRENTNESS_MEMBRANE

STATUS:
READY

PREDECESSOR:
DISTINCTION_RETENTION_MODE_V0_MATCHED

DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

HORIZON:
COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0

MODE:
EXACT_G7_RETENTION_BASIS
+
EXTERNALLY_SUPPLIED_CURRENTNESS
+
RETENTION_REQUIREMENT_ONLY
+
NO_RETENTION_TRANSITION
+
NO_GLOBAL_COOLING
+
NO_RAW_SOURCE_DELETION
+
NO_DEPRECIATION_SCHEDULE
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

# FROZEN G7 BASIS

Required G7 result:

`docs/campaigns/distinction_retention_mode_001/pressure_runs/DISTINCTION_RETENTION_MODE_V0_PRESSURE_RESULT_001.md`

Required G7 result blob:

`7d037362dd0e438ae7c1fb2553d452a9ae2fd233`

Required G7 witness:

`distinction_retention_mode_v0_observation.json`

Required G7 witness blob:

`1ff52354096371710ccdcdd77dfb9a6b2c1ada3b`

Required standing:

`DISTINCTION_RETENTION_MODE_V0_MATCHED`

Required predecessor relation:

```
DISTINCTION_RETENTION_REQUIRED_FOR_DECLARED_HORIZON = YES
EXACT_COLD_SOURCE_RETENTION_REQUIRED = YES
```

# CURRENTNESS INPUT

Currentness is externally supplied only.

Allowed exact values:

```
CURRENT
NONCURRENT
UNRESOLVED
```

This cell does not infer currentness.

# REQUIRED RETENTION-REQUIREMENT LAW

```
CURRENT
→ DECLARED_HORIZON_HOT_REQUIREMENT = REQUIRED

NONCURRENT
→ DECLARED_HORIZON_HOT_REQUIREMENT = NOT_REQUIRED_FOR_DECLARED_HORIZON

UNRESOLVED
→ DECLARED_HORIZON_HOT_REQUIREMENT = UNRESOLVED
```

For every case:

```
GLOBAL_HOT_REQUIREMENT = UNRESOLVED
EXACT_COLD_SOURCE_RETENTION_REQUIRED = YES
```

# REQUIRED NON-COLLAPSES

```
HORIZON NONCURRENT
!=
GLOBAL DISTINCTION IRRELEVANCE

HOT NOT REQUIRED FOR THIS HORIZON
!=
SAFE TO DELETE

HOT NOT REQUIRED FOR THIS HORIZON
!=
GLOBAL COOLING AUTHORITY

CURRENTNESS
!=
CLOCK RECENCY

RETENTION REQUIREMENT
!=
RETENTION ACTION

RETENTION ACTION
!=
AUTHORITY

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

Remove-Item distinction_retention_currentness_v0_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.control.test_distinction_retention_currentness_v0 `
  tests.control.test_distinction_retention_mode_v0 `
  tests.control.test_current_horizon_distinction_dependence_v0 `
  tests.control.test_method_distinction_load_ablation_v0 `
  tests.control.test_world_method_reconciliation_v0 `
  tests.control.test_horizon_gap_selector_v0 `
  tests.control.test_relational_horizon_v0

python tools/observe_distinction_retention_currentness_v0.py
```

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] CURRENT -> REQUIRED
[OK] NONCURRENT -> NOT_REQUIRED_FOR_DECLARED_HORIZON
[OK] UNRESOLVED -> UNRESOLVED
[OK] global_hot_requirement UNRESOLVED
```

# STOP LAW

A passing witness may establish only:

```
THE HOT-RETENTION REQUIREMENT
FOR THE EXACT DECLARED HORIZON
IS CONDITIONED BY
THAT HORIZON'S CURRENTNESS
```

It must stop before:

```
GLOBAL COOLING
RETENTION TRANSITION EXECUTION
RAW SOURCE DELETION
DEPRECIATION
RETIREMENT
QUANTITATIVE COST OPTIMIZATION
AUTONOMOUS PLANNING
```

# CLAIM CEILING

At the exact supplied source, the G7 horizon-scoped hot-retention requirement
may be shown to follow externally supplied currentness of the exact declared
horizon: CURRENT preserves REQUIRED, NONCURRENT yields
NOT_REQUIRED_FOR_DECLARED_HORIZON, and UNRESOLVED remains UNRESOLVED.

Global hot requirement remains UNRESOLVED and exact cold source retention remains
required in all cases. No retention transition, raw-source deletion, global
cooling, depreciation, retirement, quantitative carrying-cost optimum, method
improvement, capitalization, autonomous planning, authority, execution, or
scientific standing is established.

STOPPED:
YES
