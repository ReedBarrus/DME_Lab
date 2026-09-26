# WORKCYCLE_STABILIZATION_001 — ATOMIC ADMISSION INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
ATOMIC_ADMISSION_PRESSURE_001

ROLE:
INDEPENDENT_ATOMIC_ADMISSION_ADJUDICATOR

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
NO_PRODUCTION_CONTROL_MUTATION
+
NO_TRUST_ROOT_MUTATION
+
NO_AUTHORITY_GRANT

IMPLEMENTATION_SOURCE_REF:
3a96f87599b6e5da03565b3bf8fba3000704c528

WITNESS_TRANSPORT_REF:
53c698575efbec5560c065ee4779a9a837a14b4c

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# GATE

Do not return ATOMIC_ADMISSION_MATCHED unless the predecessor one-successor
result has been independently frozen as:

```
DISPOSITION:
ONE_SUCCESSOR_MATCHED
```

at:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/ONE_SUCCESSOR_CONTINUATION_PRESSURE_RESULT_001.md`

If that predecessor is absent or not matched, return:

```
DISPOSITION:
ATOMIC_ADMISSION_UNRESOLVED
```

with the predecessor gap named exactly.

# TARGET

Adjudicate the repo-local atomic relation:

```
ELIGIBILITY CHECK
+
SEAT / OCCUPANT LEASE
+
WORK ATTEMPT IDENTITY
+
WAKE-BUDGET RESERVATION
+
PRE-SATISFIED AUTHORITY COORDINATE
→
ONE FAIL-CLOSED ADMISSION RECEIPT
```

under competing local callers.

No model is invoked.
No admitted work is executed.

# IMPLEMENTATION EVIDENCE

At exact source ref
`3a96f87599b6e5da03565b3bf8fba3000704c528`:

1. `src/coordination/atomic_admission_v0.py`
   blob:
   `bbd64618187621c75b00812c649d4158636603f2`

2. `tests/coordination/test_atomic_admission_v0.py`
   blob:
   `8cebb1b8bf45425bfe5b9bd2a767a2ba94f193d6`

3. `src/coordination/workcycle_v0.py`
   blob:
   `b39338ac45ece77afe62ba64b525fe8def8ae75d`

4. `docs/campaigns/workcycle_stabilization_001/ATOMIC_ADMISSION_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `035d991f8d6e8498cbc63c5641af65ae880b80f7`

# RUNTIME WITNESS

Use exactly:

`atomic_admission_observation.json`

at witness transport ref
`53c698575efbec5560c065ee4779a9a837a14b4c`

blob:
`ca804d2d97023f54695fee15538076bfa5d81836`

The witness declares its exercised repo head as:

```
3a96f87599b6e5da03565b3bf8fba3000704c528
```

# REQUIRED OBSERVATIONS

Adjudicate whether the witness supports all of:

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
blocker includes authority_satisfied

TWO-CALLER RACE:
exactly 1 admitted
exactly 1 blocked
```

The admitted receipt must bind:

```
campaign_id
work_item_id
work_attempt_id
seat_id
occupant_id
wake_generation
authority_coordinate
pre_state_sha256
reserved_budget_sha256
```

Across all observed decisions:

```
model_invocation_effect = NONE
execution_performed = false
authority_effect = NONE
```

# REQUIRED NON-COLLAPSES

```
ATOMIC ADMISSION
!=
MODEL INVOCATION

PRE-SATISFIED AUTHORITY COORDINATE
!=
AUTHORITY GRANT

ADMISSION RECEIPT
!=
WORK EXECUTION

REPO-LOCAL FILE LOCK
!=
GENERIC DISTRIBUTED LOCK

ATOMIC_ADMISSION_MATCHED
!=
SELF_MOVING_WORKCYCLE_QUALIFIED
```

# CLAIM CEILING

Preserve:

```
Repo-local concurrency-safe admission candidate only.
The fixture does not establish distributed/process-independent locking
across arbitrary filesystems,
does not grant authority,
does not invoke a model,
and does not execute admitted work.
```

# DISPOSITION LAW

Return exactly one:

```
ATOMIC_ADMISSION_MATCHED
ATOMIC_ADMISSION_PARTIAL
ATOMIC_ADMISSION_FRACTURED
ATOMIC_ADMISSION_UNRESOLVED
```

MATCHED requires:
- predecessor ONE_SUCCESSOR_MATCHED;
- exactly one admission under the observed two-caller race;
- correct identity binding in the receipt;
- fail-closed authority behavior;
- no authority grant;
- no model invocation;
- no work execution;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_ONE_SUCCESSOR:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

FROZEN_IMPLEMENTATION_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

SERIAL_FIRST:
SERIAL_SECOND:
UNSATISFIED_AUTHORITY_CASE:
RACE_ADMITTED_COUNT:
RACE_BLOCKED_COUNT:

RECEIPT_IDENTITY_BINDING:
MATCHED | PARTIAL | FRACTURED | UNRESOLVED

MODEL_INVOCATION_EFFECT:
EXECUTION_PERFORMED:
AUTHORITY_EFFECT:

LOCAL_CONCURRENCY_CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
ATOMIC_ADMISSION_MATCHED
| ATOMIC_ADMISSION_PARTIAL
| ATOMIC_ADMISSION_FRACTURED
| ATOMIC_ADMISSION_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
```
