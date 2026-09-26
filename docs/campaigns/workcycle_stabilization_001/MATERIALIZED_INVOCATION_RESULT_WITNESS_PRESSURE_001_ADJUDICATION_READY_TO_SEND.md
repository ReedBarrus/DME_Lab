# WORKCYCLE_STABILIZATION_001 — MATERIALIZED INVOCATION RESULT WITNESS INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
MATERIALIZED_INVOCATION_RESULT_WITNESS_PRESSURE_001

ROLE:
INDEPENDENT_EXACT_MATERIALIZED_RESULT_WITNESS_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_REPAIR
+
NO_SEMANTIC_INTERPRETATION
+
NO_SETTLEMENT
+
NO_EXTERNAL_CONSEQUENCE_CLAIM
+
NO_AUTHORITY_CHANGE
+
NO_EXECUTION_CLAIM
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
5aafa4cb88cf4be6f1f430cfd10b31cbc135d3dd

WITNESS_TRANSPORT_REF:
f6cdb2bfef3ed77a3f3883d4ba50b9398a1a3c87

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE_RESULT_001.md`

blob:

`9bfa216b3177c1353c74bd17d015e37b4d5f0b4e`

Required disposition:

`MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_MATCHED`

# TARGET

Adjudicate only:

```
ONE ALREADY-CONSUMED EXACT MATERIALIZED-WORK ATTEMPT
+
ONE RAW CALLBACK RETURN
→
ONE DETERMINISTIC IMMUTABLE RESULT WITNESS
```

while conserving exact successor, work-spec, materialized-unit, admission,
consumption, attempt, and raw-output identities.

# FROZEN IMPLEMENTATION EVIDENCE

At exact source ref
`5aafa4cb88cf4be6f1f430cfd10b31cbc135d3dd`:

1. `src/observation/materialized_invocation_result_witness_v0.py`
   blob:
   `3bdb8478102a8699b2cfa9ed9cd6562a083a4d0b`

2. `tests/observation/test_materialized_invocation_result_witness_v0.py`
   blob:
   `9e5730dadc7ac765abce85950e260f7be8aee45c`

3. `tools/observe_materialized_invocation_result_witness_v0.py`
   blob:
   `c172e1a4a9cb10a69a1555fb23cd50d4e92b1ca7`

4. `docs/campaigns/workcycle_stabilization_001/MATERIALIZED_INVOCATION_RESULT_WITNESS_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `41a4e8240cd1aa2fee418788062e8499af98425a`

5. `src/cockpit/workcycle_qualification.py`
   blob:
   `f7ba351911eb5ee0f205ed79e900e1d7861a87f2`

6. `src/cockpit/pressure_justification.py`
   blob:
   `5dc4a475c819625771aecda71da183b609d303d5`

# RUNTIME WITNESS

Use exactly:

`materialized_invocation_result_witness_observation.json`

at witness transport ref:

`f6cdb2bfef3ed77a3f3883d4ba50b9398a1a3c87`

blob:

`668512437d97f307bef75712038c813366088960`

The witness declares exercised repo head:

```
5aafa4cb88cf4be6f1f430cfd10b31cbc135d3dd
```

The only source→transport delta is:

```
materialized_invocation_result_witness_observation.json
```

# REQUIRED LINEAGE BINDING

The immutable witness must bind exact:

```
consumption_id
composition_id
atomic_admission_id

successor_id
successor_integrity_sha256

work_spec_id
work_spec_integrity_sha256

materialized_work_item_id
materialized_unit_integrity_sha256

authority_binding_id
authority_consumption_receipt_id
authority_reservation_id
capability_id
work_attempt_id
```

# REQUIRED RAW OUTPUT BINDING

Required:

```
witness.raw_output == supplied raw output
witness.raw_output_sha256 == sha256(canonical JSON bytes)
```

# REQUIRED DETERMINISM

Identical exact inputs must produce the same witness.

# REQUIRED OUTPUT-MUTATION CASE

Holding all exact-work lineage fixed while changing raw output must change:
- raw_output_sha256;
- witness_id.

# REQUIRED TAMPER CASE

Mutating consumed-work lineage without a matching consumption identity must be
rejected.

# REQUIRED MODEL-IDENTITY CASE

If model identity is not explicitly supplied:

```
model_identity = null
model_identity ∈ unresolved_fields
model_identity ∉ measured_fields
```

No model identity may be inferred from callback occurrence.

# REQUIRED NEUTRALITY

Required:

```
semantic_interpretation = NONE
settlement_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
external_effect_inferred = false
```

# REQUIRED NON-COLLAPSES

```
RAW CALLBACK RETURN
!=
IMMUTABLE RESULT WITNESS

RESULT WITNESS
!=
SEMANTIC TRUTH

RESULT WITNESS
!=
SETTLEMENT

RESULT WITNESS
!=
EXTERNAL CONSEQUENCE

MISSING MODEL IDENTITY
!=
INFERRED MODEL IDENTITY

WITNESS
!=
EXECUTION STANDING
```

# CLAIM CEILING

The strongest admissible MATCHED claim is:

```
At the exact supplied source, one already-consumed exact materialized-work
attempt can bind its exact raw callback return into one deterministic immutable
result witness while conserving exact successor, work-spec, materialized-unit,
admission, consumption, and attempt identities. Output mutation changes witness
identity and chain tampering is rejected. Missing model identity remains
explicitly unresolved. No semantic interpretation, settlement, external effect,
execution standing, authority, or scientific standing is created.
```

Do NOT infer:
- semantic correctness;
- model identity unless explicitly supplied;
- settlement;
- external consequence;
- work execution standing;
- production execution;
- scientific standing;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

# DISPOSITION LAW

Return exactly one:

```
MATERIALIZED_INVOCATION_RESULT_WITNESS_MATCHED
MATERIALIZED_INVOCATION_RESULT_WITNESS_PARTIAL
MATERIALIZED_INVOCATION_RESULT_WITNESS_FRACTURED
MATERIALIZED_INVOCATION_RESULT_WITNESS_UNRESOLVED
```

MATCHED requires:
- predecessor matched;
- witness source matches exact source;
- witness-only transport;
- exact successor lineage bound;
- exact work-spec lineage bound;
- exact materialized-unit lineage bound;
- exact consumption/admission/attempt lineage bound;
- raw output preserved and identity-bound;
- fixed inputs deterministic;
- output mutation changes witness identity;
- tampered chain rejected;
- missing model identity remains unresolved;
- no semantic/settlement/external-effect/authority/execution/standing effect;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_MATERIALIZED_AUTHORITY_CONSUMPTION:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

FROZEN_IMPLEMENTATION_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

WITNESS_ONLY_TRANSPORT:
YES | NO | UNRESOLVED

SUCCESSOR_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

WORK_SPEC_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

MATERIALIZED_UNIT_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

CONSUMPTION_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

RAW_OUTPUT_PRESERVED:
YES | NO | UNRESOLVED

RAW_OUTPUT_IDENTITY_BOUND:
YES | NO | UNRESOLVED

FIXED_INPUTS_DETERMINISTIC:
YES | NO | UNRESOLVED

OUTPUT_MUTATION_CHANGES_WITNESS:
YES | NO | UNRESOLVED

TAMPERED_CHAIN:
REJECTED | ACCEPTED | UNRESOLVED

MISSING_MODEL_IDENTITY:
UNRESOLVED_PRESERVED | INFERRED | UNRESOLVED

SEMANTIC_INTERPRETATION:
NONE | NON_NONE | UNRESOLVED

SETTLEMENT_EFFECT:
NONE | NON_NONE | UNRESOLVED

EXTERNAL_EFFECT_INFERRED:
true | false | UNRESOLVED

AUTHORITY_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
MATERIALIZED_INVOCATION_RESULT_WITNESS_MATCHED
| MATERIALIZED_INVOCATION_RESULT_WITNESS_PARTIAL
| MATERIALIZED_INVOCATION_RESULT_WITNESS_FRACTURED
| MATERIALIZED_INVOCATION_RESULT_WITNESS_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
