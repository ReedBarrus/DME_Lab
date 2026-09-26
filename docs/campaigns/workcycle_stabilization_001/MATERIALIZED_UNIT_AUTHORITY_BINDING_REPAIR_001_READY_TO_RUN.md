# WORKCYCLE_STABILIZATION_001 — MATERIALIZED UNIT AUTHORITY BINDING REPAIR 001

OBJECT_TYPE:
READY_TO_RUN_REPAIR_PRESSURE_PACKET

PRESSURE_ID:
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_001

PREDECESSOR_FRACTURE:
MATERIALIZED_UNIT_AUTHORITY_BINDING_FRACTURED

REPAIR_SCOPE:
EXACT MATERIALIZED-WORK AUTHORITY BINDING BEFORE ATOMIC ADMISSION

RUN_SOURCE_IDENTITY:
CAPTURE_EXACT_REPO_HEAD_IN_RUNTIME_WITNESS

# FROZEN FRACTURE

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_UNIT_AUTHORITY_BINDING_PRESSURE_RESULT_001.md`

Required disposition:

`MATERIALIZED_UNIT_AUTHORITY_BINDING_FRACTURED`

The frozen wound is:

```
same successor S
+
distinct work spec A / unit A
+
distinct work spec B / unit B

→ same successor-bound authority coordinates
→ both cross existing admission
→ receipts omit exact unit/work-spec identity
```

# REPAIR LAW

For exact materialized-work admission, authority coordinates must bind:

```
successor_id
successor_integrity_sha256

materialized_work_item_id
materialized_unit_integrity_sha256

work_spec_id
work_spec_integrity_sha256

campaign_id
parent_work_item_id
basis_id
operative_frame_ref
reconciliation_identity
successor_posture
```

and:

```
authority input_sha256
=
exact materialized_unit_integrity_sha256
```

# REQUIRED SAME-SUCCESSOR / DIFFERENT-WORK CASE

Derive one successor S and two valid materializations:

```
S + SPEC_A -> UNIT_A
S + SPEC_B -> UNIT_B
```

Required:

```
SPEC_A != SPEC_B
UNIT_A.integrity != UNIT_B.integrity
```

# REQUIRED AUTHORITY-COORDINATE CASE

Required:

```
authority_coordinates(S, SPEC_A, UNIT_A)
!=
authority_coordinates(S, SPEC_B, UNIT_B)

A.input_sha256 == UNIT_A.integrity
A.input_sha256 != UNIT_B.integrity
```

# REQUIRED EXACT-ADMISSION CASE

Issue one current one-use authority envelope for:

```
S + SPEC_A + UNIT_A
```

Required:

```
A-authority + S + SPEC_A + UNIT_A
→ admitted = true
```

The receipt must bind:

```
successor_id
successor_integrity_sha256
materialized_unit_integrity_sha256
work_spec_id
work_spec_integrity_sha256
authority_request_sha256
authority_input_sha256
```

# REQUIRED WRONG-MATERIALIZATION CASE

Using the same successor S, attempt:

```
A-authority + S + SPEC_B + UNIT_B
```

Required:

```
admitted = false
blocker includes authority_request_materialized_work_mismatch
```

The difference must arise from exact work semantics, not successor identity.

# REQUIRED INVALID-BINDING CASES

The implementation tests must fail closed for:
- same materialized unit paired with the wrong sealed work spec;
- tampered materialized workflow unit;
- previously consumed authority.

# REQUIRED SAME-PROCESS CONTENTION CASE

Two callers using the same exact:

```
S + SPEC_A + UNIT_A + authority
```

must preserve the already-qualified atomic-admission property:

```
exactly one admitted
exactly one blocked by active_admission
```

# REQUIRED NEUTRALITY

A successful exact-work admission must preserve:

```
authority_consumed = false
authority_effect = NONE
consumption_effect = NONE
execution_effect = NONE
model_invocation_effect = NONE
execution_performed = false
```

# REQUIRED NON-COLLAPSES

```
SUCCESSOR-BOUND AUTHORITY
!=
EXACT MATERIALIZED-WORK AUTHORITY

AUTHORITY BINDING
!=
AUTHORITY CONSUMPTION

ATOMIC ADMISSION
!=
WORK EXECUTION

MATERIALIZED UNIT
!=
QUALIFIED RESULT

EXACT WORK AUTHORITY
!=
REPEATED METABOLIC LOOP STANDING
```

# EXECUTION

```powershell
git pull

Remove-Item materialized_unit_authority_binding_repair_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.coordination.test_materialized_unit_authority_admission_v0 `
  tests.coordination.test_verified_authority_admission_v0 `
  tests.coordination.test_successor_work_unit_materialization_v0 `
  tests.cockpit.test_workcycle_qualification `
  tests.cockpit.test_pressure_justification

python tools/observe_materialized_unit_authority_binding_repair_v0.py
```

Expected witness:

`materialized_unit_authority_binding_repair_observation.json`

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] exact_unit_a_admitted True
[OK] same_successor_wrong_unit_b_blocked True
[OK] receipt_binds_exact_materialized_unit True
```

# CLAIM CEILING

Success may establish only:

```
At the exact supplied repaired source, one current verified one-use local
authority envelope can bind one exact sealed successor, one exact sealed
externally supplied work specification, and one exact sealed materialized
workflow unit before one same-process atomic admission. Authority for one
materialization rejects a different materialization under the same successor.
The admission receipt conserves exact successor/unit/work-spec identities.
Authority remains unconsumed and no model invocation or work execution occurs.
```

It does not establish:
- authority consumption;
- model invocation;
- work execution;
- cross-process authority/admission atomicity;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
