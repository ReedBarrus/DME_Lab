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
BOUNDED_CROSS_SURFACE_REGRESSION_MATRIX
+
HISTORICAL_BRANCH_SCOPED_EXCLUSION_VERIFICATION
+
PER_CASE_TIMEOUTS
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
3. the bounded cross-surface regression matrix derived from applicable active repo CI plus the promoted consequence/control chain passes;
4. dedicated historical Lane-B qualification modules are excluded only if their branch scope is explicit and their required historical successor fixtures are absent at HEAD but present at their frozen basis;
5. every applicable regression case is bounded by an explicit timeout and the working tree remains clean after tests;
6. required frozen result artifacts contain their exact MATCHED dispositions;
7. WORKCYCLE_STABILIZATION_001 is CLOSED;
8. CONTROL_KERNEL_001 is checkpoint-closed with no current gap;
9. the control-kernel checkpoint does NOT already claim branch qualification.

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
[OK] regression_cases <observed integer>
[OK] regression_passed <same integer>
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

Success establishes only that the exact observed branch head passed the bounded
cross-surface regression matrix derived from applicable active repository CI plus
the promoted consequence/control chain; dedicated historical Lane-B qualification
modules were excluded only after mechanical verification of branch scope and the
absence-at-HEAD/presence-at-historical-basis fixture relation; the branch remained
clean, retained the required frozen standing chain, and was not behind origin/main
at observation time. It is not exhaustive proof over every historical test surface.

It does not merge the branch, authorize merge, create scientific standing,
qualify future commits, or establish the deferred G4+ capabilities.

STOPPED:
YES
