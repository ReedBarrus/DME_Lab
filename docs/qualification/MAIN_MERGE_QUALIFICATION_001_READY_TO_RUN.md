# MAIN MERGE QUALIFICATION 001

OBJECT_TYPE:
READY_TO_RUN_BRANCH_WIDE_QUALIFICATION_PACKET

PRESSURE_ID:
MAIN_MERGE_QUALIFICATION_001

STATUS:
READY_AFTER_HORIZON_GAP_SELECTOR_V0_MATCHED

TARGET_BRANCH:
draci-v0-candidate-basis

TARGET_BASE:
origin/main

MODE:
BRANCH_WIDE_TEST_DISCOVERY
+
MAIN_ANCESTRY_CHECK
+
CLEAN_TREE_CHECK
+
FROZEN_STANDING_CHAIN_CHECK
+
NO_MERGE
+
NO_G4
+
NO_NEW_CAPABILITY

# REQUIRED PREDECESSOR STANDING

HORIZON_GAP_SELECTOR_V0_MATCHED

Required frozen chain:

MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_MATCHED
CONTROL_KERNEL_CELL_001_MATCHED
RELATIONAL_HORIZON_V0_MATCHED
HORIZON_GAP_SELECTOR_V0_MATCHED

# QUALIFICATION QUESTION

At one exact branch head, can the branch demonstrate all of:

1. origin/main is an ancestor of HEAD;
2. working tree is clean before the qualification run;
3. full unittest discovery under tests/ passes;
4. working tree remains clean after tests;
5. required frozen result artifacts contain their exact MATCHED dispositions;
6. WORKCYCLE_STABILIZATION_001 is CLOSED;
7. CONTROL_KERNEL_001 is checkpoint-closed with no current gap;
8. the control-kernel checkpoint does NOT already claim branch qualification.

# EXECUTION

```powershell
git pull
git fetch origin main

Remove-Item main_merge_qualification_observation.json -ErrorAction SilentlyContinue

python tools/observe_main_merge_qualification_v0.py
```

Expected shape:

```
[OK] wrote main_merge_qualification_observation.json
[OK] test_count <observed integer>
[OK] all_assertions_pass True
[OK] qualification_posture CANDIDATE_FOR_INDEPENDENT_MERGE_QUALIFICATION
```

# REQUIRED STOP LAW

A failed assertion means:

```
HOLD_NOT_QUALIFIED
→ DO NOT MERGE
→ REPAIR OR RECONCILE EXACT FAILURE
```

A passing witness means only:

```
CANDIDATE_FOR_INDEPENDENT_MERGE_QUALIFICATION
```

It still requires fresh independent adjudication before the branch may be called merge-qualified.

# CLAIM CEILING

Success establishes only that the exact observed branch head passed the discovered
test suite, remained clean, retained the required frozen standing chain, and was
not behind origin/main at observation time.

It does not merge the branch, authorize merge, create scientific standing,
qualify future commits, or establish the deferred G4+ capabilities.

STOPPED:
YES
