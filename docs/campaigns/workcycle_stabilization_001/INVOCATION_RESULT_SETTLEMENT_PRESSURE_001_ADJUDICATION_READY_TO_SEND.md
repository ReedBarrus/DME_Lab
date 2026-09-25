# WORKCYCLE_STABILIZATION_001 — INVOCATION RESULT SETTLEMENT INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
INVOCATION_RESULT_SETTLEMENT_PRESSURE_001

ROLE:
INDEPENDENT_INVOCATION_RESULT_SETTLEMENT_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_SELF_REPAIR
+
NO_SELF_SETTLEMENT
+
NO_SEMANTIC_TRUTH_CLAIM
+
NO_QUALIFICATION
+
NO_AUTHORITY_GRANT
+
NO_EXECUTION
+
NO_ATLAS_MUTATION

IMPLEMENTATION_SOURCE_REF:
af385f8eead27460826bbdbc2160b8d21da5c5be

WITNESS_TRANSPORT_REF:
8bc95bf9cedb02a32da667beb07dde8565431875

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/INVOCATION_RESULT_WITNESS_PRESSURE_RESULT_001.md`

blob:

`287fe2b61121c622ab6f952deb55ae98edee87a5`

Required disposition:

`INVOCATION_RESULT_WITNESS_MATCHED`

If absent, mismatched, or unresolved, return
`INVOCATION_RESULT_SETTLEMENT_UNRESOLVED`.

# TARGET

Adjudicate only this relation:

```
ONE IMMUTABLE RESULT WITNESS
+
EXTERNALLY SUPPLIED FIELD DISPOSITIONS
+
EXPLICIT FIELD-LEVEL SETTLEMENT BASES
→
ONE DETERMINISTIC CANDIDATE SETTLEMENT RECORD
```

Allowed field dispositions:

```
CANDIDATE_ACCEPTED
CANDIDATE_HELD
CANDIDATE_REJECTED
UNRESOLVED
```

# IMPLEMENTATION EVIDENCE

At exact source ref
`af385f8eead27460826bbdbc2160b8d21da5c5be`:

1. `src/coordination/invocation_result_settlement_v0.py`
   blob:
   `57b36d8fe02e4a0d013f144617ff173d07ee9338`

2. `tests/coordination/test_invocation_result_settlement_v0.py`
   blob:
   `7f08ad5d6be1d591766fb1e705db60795a2ef57e`

3. `tools/observe_invocation_result_settlement_v0.py`
   blob:
   `aba4736949d7bf357afe04ae2485401ab3b70a30`

4. `docs/campaigns/workcycle_stabilization_001/INVOCATION_RESULT_SETTLEMENT_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `93d0e6fe444da505c61e07f3baed69e7ed783ff9`

5. `src/cockpit/workcycle_qualification.py`
   blob:
   `941c37467baddbfeaa799e4952b476da2e7c28b2`

6. `src/cockpit/pressure_justification.py`
   blob:
   `f02c586c2132c189bd2a4adab1020e4069bf5621`

# RUNTIME WITNESS

Use exactly:

`invocation_result_settlement_observation.json`

at witness transport ref:

`8bc95bf9cedb02a32da667beb07dde8565431875`

blob:

`5826a069d14ef8901953a488466f3ad0f57981f8`

The witness declares exercised repo head:

```
af385f8eead27460826bbdbc2160b8d21da5c5be
```

The only post-source branch delta through witness transport is:

```
invocation_result_settlement_observation.json
```

# REQUIRED SOURCE-WITNESS PRESERVATION

Adjudicate whether settlement binds:

```
source_witness_id
source_raw_output_sha256
source_work_attempt_id
```

and leaves the source witness unchanged.

The settlement gate must independently verify retained raw output against the
witness-declared raw-output digest.

# REQUIRED FIELD-LEVEL CASE

The fixture must preserve at least one field in each class:

```
accepted
held
rejected
unresolved
```

These classes must remain distinct.

# REQUIRED DETERMINISM CASE

Identical explicit:

```
witness
+
field dispositions
+
settlement bases
+
settlement actor identity
```

must yield the identical settlement record.

# REQUIRED DISPOSITION-MUTATION CASE

Change one field disposition while preserving the source witness.

Required:

```
settlement_id changes
source witness remains unchanged
```

# REQUIRED TAMPER CASE

Mutate retained raw output while leaving its declared digest unchanged.

Required:

```
settlement construction
→ REJECT
```

# REQUIRED CLASSIFICATION-SOURCE CASE

The settlement must record:

```
classification_source = EXTERNALLY_SUPPLIED
```

The settlement mechanism must not infer or invent its own classifications.

# REQUIRED NON-COLLAPSES

```
RESULT WITNESS
!=
CANDIDATE SETTLEMENT

FIELD CLASSIFICATION
!=
SEMANTIC TRUTH

CANDIDATE_ACCEPTED
!=
QUALIFIED

CANDIDATE_HELD
!=
CANDIDATE_REJECTED

CANDIDATE_REJECTED
!=
SEAT STOP

SETTLEMENT
!=
AUTHORITY CHANGE

SETTLEMENT
!=
EXECUTION

SETTLEMENT
!=
ATLAS MUTATION

SETTLEMENT
!=
EXTERNAL CONSEQUENCE

EXTERNALLY SUPPLIED CLASSIFICATION
!=
MODEL SELF-SETTLEMENT
```

# REQUIRED EFFECTS

```
scientific_admission_created = false
qualification_effect = NONE
authority_effect = NONE
execution_effect = NONE
atlas_mutation_effect = NONE
```

# CLAIM CEILING

The strongest admissible claim is:

```
At the exact supplied source, one immutable invocation result witness in a
disposable same-process fixture can receive externally supplied field-level
candidate dispositions and explicit bases in one deterministic settlement
record while preserving accepted, held, rejected, and unresolved as distinct
classes and preserving source-witness immutability. Raw-output tampering is
rejected and candidate acceptance creates no qualification, authority,
execution, external consequence, or Atlas mutation.
```

Do NOT infer:
- semantic truth;
- external consequence;
- automatic settlement;
- model self-settlement;
- scientific qualification;
- authority;
- execution;
- Atlas mutation;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

# DISPOSITION LAW

Return exactly one:

```
INVOCATION_RESULT_SETTLEMENT_MATCHED
INVOCATION_RESULT_SETTLEMENT_PARTIAL
INVOCATION_RESULT_SETTLEMENT_FRACTURED
INVOCATION_RESULT_SETTLEMENT_UNRESOLVED
```

MATCHED requires:
- predecessor matched;
- witness source equals exact implementation source;
- witness-only transport;
- source witness preserved;
- witness identity and output identity bound;
- all four field dispositions remain distinct;
- fixed inputs deterministic;
- changed disposition changes settlement identity;
- tampered raw output rejected;
- classification source externally supplied;
- accepted does not qualify;
- no authority effect;
- no execution effect;
- no Atlas mutation;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_INVOCATION_RESULT_WITNESS:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

FROZEN_IMPLEMENTATION_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

WITNESS_ONLY_TRANSPORT:
YES | NO | UNRESOLVED

SOURCE_WITNESS_PRESERVED:
YES | NO | UNRESOLVED

SOURCE_WITNESS_ID_BOUND:
YES | NO | UNRESOLVED

SOURCE_OUTPUT_IDENTITY_BOUND:
YES | NO | UNRESOLVED

FIELD_LEVEL_DISPOSITIONS:
MATCHED | PARTIAL | FRACTURED | UNRESOLVED

FIXED_INPUTS_DETERMINISTIC:
YES | NO | UNRESOLVED

DISPOSITION_CHANGE_CHANGES_SETTLEMENT:
YES | NO | UNRESOLVED

TAMPERED_RAW_OUTPUT:
REJECTED | ACCEPTED | UNRESOLVED

CLASSIFICATION_SOURCE:
EXTERNALLY_SUPPLIED | SELF_CLASSIFIED | UNRESOLVED

ACCEPTED_CREATES_QUALIFICATION:
true | false | UNRESOLVED

SCIENTIFIC_ADMISSION_CREATED:
true | false | UNRESOLVED

QUALIFICATION_EFFECT:
AUTHORITY_EFFECT:
EXECUTION_EFFECT:
ATLAS_MUTATION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
INVOCATION_RESULT_SETTLEMENT_MATCHED
| INVOCATION_RESULT_SETTLEMENT_PARTIAL
| INVOCATION_RESULT_SETTLEMENT_FRACTURED
| INVOCATION_RESULT_SETTLEMENT_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
