# WORKCYCLE_STABILIZATION_001 — ATOMIC ADMISSION WINDOWS LOCK REPAIR REOBSERVATION

OBJECT_TYPE:
READY_TO_RUN_RUNTIME_OBSERVATION_PACKET

PRESSURE_ID:
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_001

STATUS:
BLOCKING_REOBSERVATION_AFTER_APPARATUS_REPAIR

ROLE:
LOCAL_ATOMIC_ADMISSION_REPAIR_WITNESS

MODE:
DISPOSABLE_LOCAL_CONCURRENCY_FIXTURE
+
NO_MODEL_INVOCATION
+
NO_WORK_EXECUTION
+
NO_AUTHORITY_GRANT

# OBSERVED APPARATUS WOUND

During the prerequisite suite for
`VERIFIED_AUTHORITY_ATOMIC_ADMISSION_PRESSURE_001`, the existing two-caller
atomic-admission test reached:

```
PermissionError: [Errno 13] Permission denied
atomic_admission.lock
```

on Windows during `os.open(... O_CREAT | O_EXCL ...)`.

The composition observer generated later in that same run is NOT eligible for
standing because the prerequisite suite failed.

# NARROW REPAIR

Current candidate repair treats:

```
FileExistsError
OR
PermissionError
```

during sentinel acquisition as bounded contention only.

Persistent failure still ends fail-closed as:

```
AtomicAdmissionError("atomic admission lock timeout")
```

No admission occurs merely because PermissionError was observed.

# TARGET

Re-witness the existing same-process two-caller relation at the repaired source:

```
two callers
+
same local admission store
+
same wake generation
→
exactly 1 admitted
+
exactly 1 blocked
```

Also preserve:
- serial first admitted / second blocked;
- unsatisfied authority blocked;
- no model invocation;
- no execution;
- no authority grant.

# EXECUTION

The previous atomic and composition witnesses must not be reused across this
source change.

```powershell
git pull

Remove-Item atomic_admission_observation.json -ErrorAction SilentlyContinue
Remove-Item verified_authority_atomic_admission_observation.json -ErrorAction SilentlyContinue

python -m unittest tests.coordination.test_atomic_admission_v0

python tools/observe_atomic_admission_v0.py
```

Expected:

```
all tests pass

[OK] all_assertions_pass True
[OK] race_admitted_count 1
[OK] race_blocked_count 1
```

# CLAIM CEILING

This reobservation may restore only the repaired current-source same-process
two-caller local-filesystem atomic-admission relation.

It does not establish cross-process locking, stale-lock recovery, crash safety,
power-loss durability, verified-authority composition, model invocation, work
execution, or self-moving-workcycle standing.

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
