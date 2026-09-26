# WORKCYCLE_STABILIZATION_001 — ATOMIC ADMISSION WINDOWS LOCK REPAIR INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_001

ROLE:
INDEPENDENT_ATOMIC_ADMISSION_REPAIR_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_SELF_REPAIR
+
NO_MODEL_INVOCATION
+
NO_WORK_EXECUTION
+
NO_AUTHORITY_GRANT
+
NO_PRODUCTION_CONTROL_MUTATION

IMPLEMENTATION_SOURCE_REF:
11da60ee7b6de02dcea39537301c6c317cd44d9b

WITNESS_TRANSPORT_REF:
e63e467ea5d75f6c8f97c5cfd9966a2909720d62

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# HISTORICAL PREDECESSOR

The prior frozen source had already earned:

```
DISPOSITION:
ATOMIC_ADMISSION_MATCHED
```

at:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/ATOMIC_ADMISSION_PRESSURE_RESULT_001.md`

This adjudication does NOT transfer that standing automatically to the repaired
source. It evaluates only whether the repaired current source re-establishes the
same bounded same-process relation after the observed Windows lock-acquisition
apparatus defect.

# OBSERVED FRACTURE

A prerequisite race test on Windows produced:

```
PermissionError: [Errno 13] Permission denied
atomic_admission.lock
```

during `os.open(... O_CREAT | O_EXCL ...)`.

The repair treats both:

```
FileExistsError
PermissionError
```

as bounded sentinel-acquisition contention.

Persistent acquisition failure still ends fail-closed as:

```
AtomicAdmissionError("atomic admission lock timeout")
```

# TARGET

Adjudicate only whether the repaired source restores:

```
same process
+
same local admission store
+
same wake generation
+
two competing callers
→
exactly 1 admitted
+
exactly 1 blocked
```

while preserving:

- first serial attempt admitted;
- second same-wake serial attempt blocked;
- unsatisfied authority blocked;
- no model invocation;
- no work execution;
- no authority grant;
- persistent lock-acquisition failure remains fail-closed.

# IMPLEMENTATION EVIDENCE

At exact source ref
`11da60ee7b6de02dcea39537301c6c317cd44d9b`:

1. `src/coordination/atomic_admission_v0.py`
   blob:
   `28520f9d7fc85fa68f563890b13da25ba55a33c1`

2. `tests/coordination/test_atomic_admission_v0.py`
   blob:
   `2863a6f9b27383b02a6e737525ded07ee3581e29`

3. `tools/observe_atomic_admission_v0.py`
   blob:
   `81ba85ec39b167927b0c4ec39bd7ac30a045b9c6`

4. `docs/campaigns/workcycle_stabilization_001/ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_001_READY_TO_RUN.md`
   blob:
   `0811f558c042ed76512d469f928d76b843efcb04`

5. `docs/campaigns/workcycle_stabilization_001/state/MECHANIZED_DEPTH_PROFILE_V0.json`
   blob:
   `f51f9680331ae4e8ac49c5cc4545df2c95b3b07f`

# RUNTIME WITNESS

Use exactly:

`atomic_admission_observation.json`

at transport ref:

`e63e467ea5d75f6c8f97c5cfd9966a2909720d62`

blob:

`f5a2b06e489b2675889171c7a2d033835e314717`

The witness declares exercised repo head:

```
11da60ee7b6de02dcea39537301c6c317cd44d9b
```

The only post-source branch delta through witness transport is:

```
atomic_admission_observation.json
```

# REQUIRED OBSERVATIONS

Adjudicate whether the witness and repaired tests support all of:

```
SERIAL FIRST:
admitted = true

SERIAL SECOND SAME WAKE:
admitted = false
blockers include:
- active_admission
- budget_reservable
- seat_available

UNSATISFIED AUTHORITY:
admitted = false
blocker includes:
- authority_satisfied

TWO-CALLER RACE:
race_admitted_count = 1
race_blocked_count = 1
```

The repaired tests must also preserve:

```
transient PermissionError
→ retry boundedly

persistent PermissionError
→ AtomicAdmissionError
→ fail closed
```

Across the runtime witness:

```
model_invocation_effect = NONE
execution_performed = false
authority_effect = NONE
```

# REQUIRED NON-COLLAPSES

```
WINDOWS PermissionError
!=
ADMISSION FAILURE BY ITSELF

WINDOWS PermissionError
!=
LOCK OWNERSHIP PROOF

BOUNDED CONTENTION RETRY
!=
STALE-LOCK RECOVERY

SAME-PROCESS CONTENTION
!=
CROSS-PROCESS ATOMICITY

LOCK ACQUISITION
!=
POWER-LOSS DURABILITY

REPAIRED SOURCE
!=
AUTOMATICALLY QUALIFIED SOURCE

VALID DOWNSTREAM OBSERVER OUTPUT
!=
VALID COMPOSITION CLAIM
WHEN A REQUIRED PREDECESSOR IS UNQUALIFIED
```

# CLAIM CEILING

The strongest admissible claim is:

```
At the exact repaired source, same-process two-caller local-filesystem atomic
admission again yields exactly one admitted caller and one blocked caller under
the bounded fixture. Windows PermissionError during O_EXCL sentinel acquisition
is treated as bounded contention, while persistent inability to acquire remains
fail-closed. This does not establish cross-process contention safety,
stale-lock recovery, crash safety, power-loss durability, verified-authority
composition, model invocation, work execution, or self-moving-workcycle standing.
```

# DISPOSITION LAW

Return exactly one:

```
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_MATCHED
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_PARTIAL
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_FRACTURED
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_UNRESOLVED
```

MATCHED requires:
- witness source matches the exact repaired implementation source;
- witness transport contains no implementation drift;
- serial first remains admitted;
- serial second remains blocked;
- unsatisfied authority remains blocked;
- two-caller race yields exactly one admitted and one blocked;
- transient PermissionError is bounded-retry behavior;
- persistent PermissionError remains fail-closed;
- no authority grant;
- no model invocation;
- no work execution;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

FROZEN_IMPLEMENTATION_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

WITNESS_ONLY_TRANSPORT:
YES | NO | UNRESOLVED

SERIAL_FIRST:
SERIAL_SECOND:
UNSATISFIED_AUTHORITY_CASE:
RACE_ADMITTED_COUNT:
RACE_BLOCKED_COUNT:

TRANSIENT_PERMISSION_ERROR:
BOUNDED_CONTENTION | NOT_BOUNDED | UNRESOLVED

PERSISTENT_PERMISSION_ERROR:
FAILS_CLOSED | DOES_NOT_FAIL_CLOSED | UNRESOLVED

MODEL_INVOCATION_EFFECT:
EXECUTION_PERFORMED:
AUTHORITY_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_MATCHED
| ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_PARTIAL
| ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_FRACTURED
| ATOMIC_ADMISSION_WINDOWS_LOCK_REPAIR_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
```
