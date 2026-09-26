# DISTINCTION_RETENTION_MODE_001 — G7 PRESSURE 001

OBJECT_TYPE:
READY_TO_RUN_RETENTION_MODE_PACKET

PRESSURE_ID:
DISTINCTION_RETENTION_MODE_V0_PRESSURE_001

GAP_ID:
G7_DISTINCTION_RETENTION_MODE

STATUS:
READY

PREDECESSOR:
CURRENT_HORIZON_DISTINCTION_DEPENDENCE_V0_MATCHED

DISTINCTION:
WORLD_CHANGE != METHOD_CHANGE

HORIZON:
COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0

MODE:
EXACT_G4_G5_G6_SOURCE_HANDLES
+
MINIMAL_HOT_MEMORY_CARRIER
+
COLD_SOURCE_ROUTABILITY
+
NO_RAW_SOURCE_DELETION
+
NO_GLOBAL_RETENTION_CLAIM
+
NO_QUANTITATIVE_COST_OPTIMUM
+
NO_METHOD_IMPROVEMENT
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

# FROZEN SOURCE HANDLES

G4_RESULT:
7a876e3e23b5a7f7d73f8ec86b393137da8f5ede

G4_WITNESS:
a49d948432c9560310133557ce6c8102ce4931ac

G5_RESULT:
d738dd57ae7866bdf584509b553a6b061cd714d7

G5_WITNESS:
a334412ac95fd66a228dba49fb888ffc225a6e7f

G6_RESULT:
bacc6f48a2c7c9a4658758cf663822b3b934557c

G6_WITNESS:
3e9c7b24cacbf608d87d2f14175e265267cc0ef1

Required G6 standing:

CURRENT_HORIZON_DISTINCTION_DEPENDENCE_V0_MATCHED

# MEMORY BASIS

Method:

docs/methods/MEMORY_COMPILATION_METHOD_v0.md

Required standing:

OPERABLE_V0

Invariant ledger:

docs/methods/EARNED_MEMORY_INVARIANTS_v0.md

Relevant method law:

```
REDUCE CARRYING COST
WHILE PRESERVING
RELATIONS REQUIRED
FOR CORRECT RECONSTRUCTION
```

and:

```
HOT / REQUIRED
→
COLD-RETENTION CANDIDATE
```

while:

```
COLD RETENTION
!=
DELETION
```

# MINIMAL HOT CARRIER

The candidate carrier may inline only:

```
DISTINCTION_ID

HORIZON_ID

METHOD_AXIS_APPLICABILITY_LAW:
  CHANGED    → APPLICABLE
  UNCHANGED  → NOT_APPLICABLE
  UNRESOLVED → UNRESOLVED

UNRESOLVED BOUNDARIES

EXACT SOURCE HANDLES
```

It must not inline the richer:

```
G4 six-case table
G5 collision table
G6 pre/post ablation tables
```

unless the pressure demonstrates they are required.

# RECONSTRUCTION TARGET

Given only the minimal carrier plus the six method-axis postures:

```
WORLD_ONLY        = UNCHANGED
METHOD_ONLY       = CHANGED
BOTH              = CHANGED
NEITHER           = UNCHANGED
WORLD_UNRESOLVED  = UNCHANGED
METHOD_UNRESOLVED = UNRESOLVED
```

the carrier must reconstruct exactly:

```
WORLD_ONLY        → NOT_APPLICABLE
METHOD_ONLY       → APPLICABLE
BOTH              → APPLICABLE
NEITHER           → NOT_APPLICABLE
WORLD_UNRESOLVED  → NOT_APPLICABLE
METHOD_UNRESOLVED → UNRESOLVED
```

# REQUIRED RETENTION SPLIT

If exact reconstruction succeeds:

```
DISTINCTION_RETENTION_REQUIRED_FOR_DECLARED_HORIZON:
YES

FULL_G4_G5_G6_INLINE_HOT_REQUIRED:
NO

MINIMAL_HOT_CARRIER_CANDIDATE:
YES

EXACT_COLD_SOURCE_RETENTION_REQUIRED:
YES
```

# REQUIRED NON-COLLAPSES

```
HOT CARRIER
!=
RAW SOURCE

COLD RETENTION
!=
DELETION

MINIMAL HOT CARRIER
!=
LOSS OF PROVENANCE

RETENTION REQUIREMENT
!=
METHOD IMPROVEMENT

RETENTION REQUIREMENT
!=
METHOD CAPITALIZATION

HORIZON-SCOPED RETENTION
!=
GLOBAL ECOLOGY RETENTION

COMPRESSION SUCCESS
!=
AUTHORITY

OBSERVABLE INTELLIGENCE
!=
CONSEQUENTIAL BEHAVIOR
```

# REQUIRED EFFECT CEILING

```
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

Remove-Item distinction_retention_mode_v0_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.control.test_distinction_retention_mode_v0 `
  tests.control.test_current_horizon_distinction_dependence_v0 `
  tests.control.test_method_distinction_load_ablation_v0 `
  tests.control.test_world_method_reconciliation_v0 `
  tests.control.test_horizon_gap_selector_v0 `
  tests.control.test_relational_horizon_v0

python tools/observe_distinction_retention_mode_v0.py
```

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] exact_horizon_reconstruction True
[OK] full_inline_hot_required NO
[OK] minimal_hot_carrier_candidate YES
[OK] exact_cold_source_retention_required YES
```

# STOP LAW

A passing witness may establish only:

```
THE DECLARED HORIZON
REQUIRES THE DISTINCTION
TO REMAIN RECOVERABLY AVAILABLE

BUT

THE FULL G4/G5/G6 EVIDENCE
NEED NOT REMAIN INLINE
IF A MINIMAL HOT CARRIER
PRESERVES THE OPERATIVE RELATION
AND EXACT COLD SOURCE ROUTES
```

It must stop before:

```
GLOBAL RETENTION
QUANTITATIVE COST OPTIMIZATION
CAPITALIZATION
DELETION
DEPRECIATION
RETIREMENT
AUTONOMOUS PLANNING
```

# CLAIM CEILING

At the exact supplied source, the G6 horizon dependence may be shown to survive
through a smaller hot-memory carrier while the richer G4/G5/G6 evidence remains
cold-routable through exact immutable source handles.

A passing result does not establish a quantitative carrying-cost optimum,
global ecology retention, method improvement, capitalization, deletion
permission, autonomous planning, authority, execution, or scientific standing.

STOPPED:
YES
