# PARTIAL_BASIS_RETENTION_PROFILE_001 — G10 PRESSURE 001

OBJECT_TYPE:
READY_TO_RUN_PARTIAL_BASIS_RETENTION_PROFILE_PACKET

PRESSURE_ID:
PARTIAL_BASIS_RETENTION_PROFILE_V0_PRESSURE_001

GAP_ID:
G10_PARTIAL_DECLARED_BASIS_RETENTION_PROFILE

STATUS:
READY

PREDECESSOR:
RETENTION_SCOPE_AGGREGATION_V0_MATCHED

DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

MODE:
EXACT_G9_SCOPE_AGGREGATION_BASIS
+
PARTIAL_DECLARED_BASIS
+
NONSCALAR_RETENTION_PROFILE
+
BASIS_EXTENSION
+
NO_GLOBAL_COVERAGE_CLAIM
+
NO_LOAD_WEIGHTING
+
NO_SCALAR_HOTNESS
+
NO_ECONOMIC_OPTIMUM
+
NO_GLOBAL_INVARIANCE
+
NO_COOLING_AUTHORITY
+
NO_RETENTION_TRANSITION
+
NO_RAW_SOURCE_DELETION
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

# FROZEN G9 BASIS

Required G9 result:

`docs/campaigns/retention_scope_aggregation_001/pressure_runs/RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_RESULT_001.md`

Required G9 result blob:

`94152a26078c527cabfef7cd2cf1e7e3b4990df1`

Required G9 witness:

`retention_scope_aggregation_v0_observation.json`

Required G9 witness blob:

`212d7a9d4fb7bc982cb83b418ee6d5982008c574`

Required standing:

`RETENTION_SCOPE_AGGREGATION_V0_MATCHED`

# LOCAL POSTURE VOCABULARY

```
REQUIRED
UNRESOLVED
NOT_REQUIRED_FOR_DECLARED_HORIZON
```

# BASIS B0

```
H_A = REQUIRED
H_B = NOT_REQUIRED_FOR_DECLARED_HORIZON
```

Required profile:

```
REQUIRED_MEMBERS = {H_A}
UNRESOLVED_MEMBERS = {}
NOT_REQUIRED_MEMBERS = {H_B}

N_REQUIRED = 1
N_UNRESOLVED = 0
N_NOT_REQUIRED = 1
BASIS_SIZE = 2

DECLARED_SCOPE_HOT_REQUIREMENT = REQUIRED

EXTERIOR_POSTURE = UNRESOLVED
GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED
```

# BASIS B1

Extend B0 by exactly:

```
H_C = UNRESOLVED
```

Required profile:

```
REQUIRED_MEMBERS = {H_A}
UNRESOLVED_MEMBERS = {H_C}
NOT_REQUIRED_MEMBERS = {H_B}

N_REQUIRED = 1
N_UNRESOLVED = 1
N_NOT_REQUIRED = 1
BASIS_SIZE = 3

DECLARED_SCOPE_HOT_REQUIREMENT = REQUIRED

EXTERIOR_POSTURE = UNRESOLVED
GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED
```

# REQUIRED EXTENSION RELATION

```
B0 subset B1

PRIOR_LOCAL_COORDINATES_PRESERVED = YES

NEW_HORIZONS = {H_C}
```

The following coordinates must remain unchanged across B0 → B1:

```
H_A = REQUIRED
H_B = NOT_REQUIRED_FOR_DECLARED_HORIZON
```

# REQUIRED NON-COLLAPSES

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

# REQUIRED EFFECT CEILING

Both B0 and B1 must preserve:

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

The extension relation must preserve:

```
global_invariance_effect = NONE
planning_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

# EXECUTION

```powershell
git switch world-method-reconciliation-v0
git pull

Remove-Item partial_basis_retention_profile_v0_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.control.test_partial_basis_retention_profile_v0 `
  tests.control.test_retention_scope_aggregation_v0 `
  tests.control.test_distinction_retention_currentness_v0 `
  tests.control.test_distinction_retention_mode_v0 `
  tests.control.test_current_horizon_distinction_dependence_v0 `
  tests.control.test_method_distinction_load_ablation_v0 `
  tests.control.test_world_method_reconciliation_v0 `
  tests.control.test_horizon_gap_selector_v0 `
  tests.control.test_relational_horizon_v0

python tools/observe_partial_basis_retention_profile_v0.py
```

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] B0 profile (1,0,1)
[OK] B1 profile (1,1,1)
[OK] prior_local_coordinates_preserved YES
[OK] exterior_posture UNRESOLVED
[OK] scalar_hotness NOT_ESTABLISHED
```

# STOP LAW

A passing witness may establish only:

```
ONE EXACT PARTIAL DECLARED BASIS
CAN CARRY A NONSCALAR RETENTION PROFILE

AND

AN EXTENSION THAT PRESERVES PRIOR LOCAL INPUTS
PRESERVES THOSE PRIOR LOCAL COORDINATES
```

It must stop before:

```
GLOBAL ECOLOGY COVERAGE
LOAD WEIGHTING
SCALAR HOTNESS
ECONOMIC OPTIMIZATION
GLOBAL INVARIANCE
COOLING AUTHORITY
RETENTION TRANSITION EXECUTION
RAW SOURCE DELETION
AUTONOMOUS PLANNING
```

# CLAIM CEILING

At the exact supplied source, one partial declared basis may be shown to carry
an explicit retention profile over REQUIRED / UNRESOLVED / NOT_REQUIRED member
sets, while the exterior remains explicitly unresolved. An exact basis extension
may be shown to preserve unchanged prior local coordinates.

A passing result does not establish global ecology coverage, load weights,
scalar hotness, economic optimality, global invariance, cooling authority,
retention-transition authority, deletion permission, method capitalization,
autonomous planning, authority, execution, or scientific standing.

STOPPED:
YES
