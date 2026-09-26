# WORKCYCLE_STABILIZATION_001 — MATERIALIZED ADMITTED AUTHORITY CONSUMPTION PRESSURE 001

OBJECT_TYPE:
READY_TO_RUN_RUNTIME_OBSERVATION_PACKET

PRESSURE_ID:
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE_001

STATUS:
READY_AFTER_MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_MATCHED

ROLE:
LOCAL_EXACT_MATERIALIZED_WORK_CONSUMPTION_WITNESS

MODE:
DISPOSABLE_SAME_PROCESS_FIXTURE
+
ONE_USE_AUTHORITY
+
CALLER_SUPPLIED_CALLBACK
+
NO_RESULT_INTERPRETATION
+
NO_SETTLEMENT
+
NO_EXTERNAL_CONSEQUENCE_CLAIM
+
NO_SCIENTIFIC_PROMOTION

RUN_SOURCE_IDENTITY:
CAPTURE_EXACT_REPO_HEAD_IN_RUNTIME_WITNESS

# REQUIRED PREDECESSOR

```
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_MATCHED
```

at:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_RESULT_001.md`

# TARGET

Pressure exactly:

```
EXACT ADMITTED MATERIALIZED WORK
+
SAME CURRENT ONE-USE AUTHORITY
→
ONE AUTHORITY RESERVATION
→
ONE CALLER-SUPPLIED CALLBACK
→
ONE RAW RETURN VALUE
→
AUTHORITY CONSUMED
```

while preserving exact:
- successor identity;
- work-spec identity;
- materialized workflow-unit identity;
- admission composition identity;
- work-attempt identity.

# REQUIRED NON-COLLAPSES

```
AUTHORITY BINDING
!=
AUTHORITY CONSUMPTION

AUTHORITY CONSUMPTION
!=
WORK EXECUTION

CALLBACK INVOCATION
!=
MODEL INVOCATION CLAIM

RAW CALLBACK RETURN
!=
RESULT WITNESS

RAW CALLBACK RETURN
!=
SETTLEMENT

RAW CALLBACK RETURN
!=
EXTERNAL CONSEQUENCE
```

# REQUIRED SUCCESS CASE

Given one exact:
- successor S;
- externally supplied sealed work spec A;
- sealed materialized unit A;
- exact-work admission receipt A;
- current one-use authority envelope A;

required:

```
consume once
→ consumed = true
→ invocation_performed = true
→ callback_calls = 1
→ invocation_count = 1
→ authority_status_after = CONSUMED
→ authority_remaining_uses_after = 0
```

The consumption receipt must bind:

```
successor_id
successor_integrity_sha256

work_spec_id
work_spec_integrity_sha256

materialized_work_item_id
materialized_unit_integrity_sha256

composition_id
atomic_admission_id
authority_binding_id
authority_consumption_receipt_id
authority_reservation_id
capability_id
work_attempt_id
```

# REQUIRED RAW-RETURN CASE

The callback returns one canonical JSON-compatible fixture value.

Required:

```
invocation_result == exact supplied callback return
```

No semantic interpretation is allowed in this cell.

# REQUIRED REPLAY CASE

Repeat the same consumption request after success.

Required:

```
consumed = false
callback_calls = 0
blocker = authority_verification_failed
```

# REQUIRED WRONG-MATERIALIZATION CASE

Using a fresh exact admission/authority fixture for work A, supply a different:

```
same successor S
+
SPEC_B
+
UNIT_B
```

Required:

```
consumed = false
callback_calls = 0
authority remains ACTIVE
remaining_uses remains 1
```

The mismatch must block before authority consumption.

# REQUIRED TAMPER CASE

A tampered exact admission receipt must block before consumption and callback.

# REQUIRED POST-RESERVATION FAILURE CASE

If the callback raises after authority reservation:

```
authority status
→ RECOVERY_REQUIRED

remaining_uses
→ 0

replay
→ denied
```

No automatic retry is admitted.

# REQUIRED NEUTRALITY

Successful consumption may establish:

```
authority_consumed = true
consumption_effect = CONSUMED_ONE_USE
invocation_performed = true
```

but must retain:

```
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

The callback crossing is not itself a work-execution standing claim.

# EXECUTION

```powershell
git pull

Remove-Item materialized_admitted_authority_consumption_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.coordination.test_materialized_admitted_authority_consumption_v0 `
  tests.coordination.test_materialized_unit_authority_admission_v0 `
  tests.coordination.test_admitted_authority_consumption_v0 `
  tests.cockpit.test_workcycle_qualification `
  tests.cockpit.test_pressure_justification

python tools/observe_materialized_admitted_authority_consumption_v0.py
```

Expected witness:

`materialized_admitted_authority_consumption_observation.json`

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] exact_consumed True
[OK] exact_callback_once True
[OK] wrong_materialization_blocked_before_consumption True
```

# CLAIM CEILING

Success may establish only:

```
At the exact supplied source, one exact admitted materialized-work object can be
rebound to the same current one-use local authority and cross one caller-supplied
callback exactly once under one-shot consumption while conserving exact
successor, work-spec, and materialized-unit identities. Replay is denied; a
different materialization is blocked before consumption; post-reservation
callback failure leaves RECOVERY_REQUIRED with zero remaining uses and replay
denied. The raw callback return is preserved only as an uninterpreted return
value. No result witness, settlement, external consequence, work-execution
standing, or scientific standing is established.
```

It does not establish:
- result witnessing;
- settlement;
- semantic correctness;
- external consequence;
- model identity;
- production execution;
- cross-process atomicity;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

AUTHORITY_EFFECT:
NONE

CONSUMPTION_EFFECT:
CONSUMED_ONE_USE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
