# WORKCYCLE_STABILIZATION_001 — MATERIALIZED UNIT AUTHORITY BINDING REPAIR INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_001

ROLE:
INDEPENDENT_EXACT_MATERIALIZED_WORK_AUTHORITY_REPAIR_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_SELF_REPAIR
+
NO_AUTHORITY_CONSUMPTION
+
NO_MODEL_INVOCATION
+
NO_WORK_EXECUTION
+
NO_SCIENTIFIC_PROMOTION

REPAIRED_SOURCE_REF:
9ce423bfc53610e0b650927709baeedfce360030

WITNESS_TRANSPORT_REF:
2529aec9996d796636fb5f1806563561c7bd6843

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED FRACTURE PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_UNIT_AUTHORITY_BINDING_PRESSURE_RESULT_001.md`

blob:

`ff5f82ba4ffa718e58db1a28d6d5f4a157085ec8`

Required disposition:

`MATERIALIZED_UNIT_AUTHORITY_BINDING_FRACTURED`

The frozen fracture established that two distinct materialized work units under
the same successor shared successor-bound authority coordinates and could each
cross the old successor-bound admission decision without exact unit/work-spec
identity being bound in the receipt.

# TARGET

Adjudicate only whether the narrow repair restores exact materialized-work
authority binding before one same-process atomic admission:

```
exact successor
+
exact sealed work spec
+
exact sealed materialized workflow unit
+
current verified one-use authority
→
one atomic admission decision
```

while preserving:

```
AUTHORITY BINDING
!=
AUTHORITY CONSUMPTION

ATOMIC ADMISSION
!=
MODEL INVOCATION

ATOMIC ADMISSION
!=
WORK EXECUTION
```

# REPAIRED IMPLEMENTATION EVIDENCE

At exact source ref
`9ce423bfc53610e0b650927709baeedfce360030`:

1. `src/coordination/materialized_unit_authority_admission_v0.py`
   blob:
   `8ff018afb5eddbf04c204e8f61e48d05f8e1b237`

2. `tests/coordination/test_materialized_unit_authority_admission_v0.py`
   blob:
   `4b67f6d7f889a8413fe6056017e8aee6d9402077`

3. `tools/observe_materialized_unit_authority_binding_repair_v0.py`
   blob:
   `76aaae887e8ac433107aca0f9d312b85f40f2148`

4. `docs/campaigns/workcycle_stabilization_001/MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_001_READY_TO_RUN.md`
   blob:
   `72980c8bd53a795c74ad56af33084bdf9d3e3c40`

5. `src/cockpit/workcycle_qualification.py`
   blob:
   `94b54c12d851d4b907fcfb05c5182be1e36cf844`

6. `src/cockpit/pressure_justification.py`
   blob:
   `1f4fc1f06de1287a361b4f24339906670505a39e`

# RUNTIME WITNESS

Use exactly:

`materialized_unit_authority_binding_repair_observation.json`

at witness transport ref:

`2529aec9996d796636fb5f1806563561c7bd6843`

blob:

`9f1f23ad3988e0515c859eb643a61c3fac6e8ed0`

The witness declares exercised repo head:

```
9ce423bfc53610e0b650927709baeedfce360030
```

The only source→transport delta is:

```
materialized_unit_authority_binding_repair_observation.json
```

# REQUIRED EXACT-WORK COORDINATE CASE

The witness must show one successor S with two distinct work realizations:

```
S + SPEC_A -> UNIT_A
S + SPEC_B -> UNIT_B

SPEC_A != SPEC_B
UNIT_A.integrity != UNIT_B.integrity
```

The repaired authority coordinates must differ across the two realizations.

Required:

```
A.input_sha256 == UNIT_A.integrity
A.input_sha256 != UNIT_B.integrity
```

# REQUIRED EXACT-ADMISSION CASE

Under current authority issued for:

```
S + SPEC_A + UNIT_A
```

required:

```
A-authority + S + SPEC_A + UNIT_A
→ admitted = true
```

# REQUIRED WRONG-MATERIALIZATION CASE

Under the same successor S but different work realization:

```
A-authority + S + SPEC_B + UNIT_B
→ admitted = false
```

with blocker:

```
authority_request_materialized_work_mismatch
```

# REQUIRED RECEIPT BINDING

The admitted exact-work receipt must bind:

```
successor_id
successor_integrity_sha256

materialized_work_item_id
materialized_unit_integrity_sha256

work_spec_id
work_spec_integrity_sha256

authority_request_sha256
authority_input_sha256
```

and:

```
authority_input_sha256 == exact materialized_unit_integrity_sha256
```

# REQUIRED AUTHORITY POSTURE

The witness must preserve:

```
authority_consumed = false
authority_effect = NONE
consumption_effect = NONE
execution_effect = NONE
execution_performed = false
model_invocation_effect = NONE
```

The authority store must remain unchanged by the admission composition.

# REQUIRED TESTED NEGATIVE CASES

The supplied test evidence must fail closed for:
- same materialized unit paired with the wrong sealed work spec;
- tampered materialized workflow unit;
- already-consumed exact authority.

# REQUIRED SAME-PROCESS CONTENTION CASE

Two same-process callers using the same exact:

```
successor
+
work spec
+
materialized unit
+
authority
```

must retain exactly:
- one admitted;
- one blocked by active_admission.

Do not infer cross-process standing.

# REQUIRED REPAIR CHARACTERIZATION

Adjudicate whether the supplied evidence supports:

```
FRACTURE:
authority resolution stopped at successor identity

REPAIR:
authority resolution now reaches exact consequence-bearing
materialized work identity and work-spec identity
```

while preserving the old successor-bound authority result under its prior claim
ceiling.

# REQUIRED NON-COLLAPSES

Preserve:

```
SUCCESSOR-BOUND AUTHORITY
!=
EXACT MATERIALIZED-WORK AUTHORITY

EXACT MATERIALIZED-WORK AUTHORITY
!=
AUTHORITY CONSUMPTION

AUTHORITY CONSUMPTION
!=
MODEL INVOCATION

ATOMIC ADMISSION
!=
WORK EXECUTION

MATCHED REPAIR
!=
REPEATED METABOLIC LOOP STANDING

MATCHED REPAIR
!=
PRODUCTION AUTONOMY
```

# CLAIM CEILING

The strongest admissible MATCHED claim is:

```
At the exact supplied repaired source, one current verified one-use local
authority envelope can bind one exact sealed successor, one exact sealed
externally supplied work specification, and one exact sealed materialized
workflow unit before one same-process atomic admission. Authority for one
materialization rejects a different materialization under the same successor.
The admission receipt conserves exact successor, work-spec, materialized-unit,
and authority coordinates. Authority remains unconsumed and no model invocation
or work execution occurs.
```

Do NOT infer:
- authority consumption;
- model invocation;
- work execution;
- cross-process authority/admission atomicity;
- production durability;
- repeated metabolic loop standing;
- self-moving-workcycle standing;
- production autonomy.

# DISPOSITION LAW

Return exactly one:

```
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_MATCHED
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_PARTIAL
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_FRACTURED
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_UNRESOLVED
```

MATCHED requires:
- frozen fracture predecessor present and exact;
- witness source equals repaired source;
- witness-only transport;
- same successor yields two distinct work realizations;
- repaired authority coordinates differ across exact materializations;
- A input binds exact UNIT_A integrity and not UNIT_B;
- A exact-work admission succeeds;
- same-successor B realization is blocked under A authority;
- receipt binds exact successor/work-spec/unit identities;
- authority remains unconsumed;
- no model invocation or work execution;
- tested negative cases fail closed;
- same-process atomic one-winner property remains;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_MATERIALIZED_UNIT_AUTHORITY_FRACTURE:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

REPAIRED_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

WITNESS_ONLY_TRANSPORT:
YES | NO | UNRESOLVED

SAME_SUCCESSOR_ID:
YES | NO | UNRESOLVED

WORK_SPECS_DIFFER:
YES | NO | UNRESOLVED

MATERIALIZED_UNITS_DIFFER:
YES | NO | UNRESOLVED

AUTHORITY_COORDINATES_DIFFER_BY_MATERIALIZED_WORK:
YES | NO | UNRESOLVED

AUTHORITY_INPUT_BINDS_EXACT_UNIT_A:
YES | NO | UNRESOLVED

AUTHORITY_INPUT_BINDS_UNIT_B:
YES | NO | UNRESOLVED

EXACT_UNIT_A_ADMITTED:
YES | NO | UNRESOLVED

SAME_SUCCESSOR_WRONG_UNIT_B:
BLOCKED | ADMITTED | UNRESOLVED

RECEIPT_BINDS_EXACT_SUCCESSOR:
YES | NO | UNRESOLVED

RECEIPT_BINDS_EXACT_WORK_SPEC:
YES | NO | UNRESOLVED

RECEIPT_BINDS_EXACT_MATERIALIZED_UNIT:
YES | NO | UNRESOLVED

AUTHORITY_CONSUMED:
true | false | UNRESOLVED

EXECUTION_PERFORMED:
true | false | UNRESOLVED

MODEL_INVOCATION_EFFECT:
NONE | NON_NONE | UNRESOLVED

SAME_PROCESS_ONE_WINNER_PROPERTY:
PRESERVED | FRACTURED | UNRESOLVED

AUTHORITY_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_MATCHED
| MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_PARTIAL
| MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_FRACTURED
| MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
