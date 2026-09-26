# WORKCYCLE_STABILIZATION_001 — MATERIALIZED INVOCATION RESULT SETTLEMENT INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_PRESSURE_001

ROLE:
INDEPENDENT_EXACT_MATERIALIZED_SETTLEMENT_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_REPAIR
+
NO_SEMANTIC_TRUTH_PROMOTION
+
NO_EXTERNAL_CONSEQUENCE_CLAIM
+
NO_BASIS_RECONCILIATION
+
NO_AUTHORITY_CHANGE
+
NO_EXECUTION
+
NO_ATLAS_MUTATION
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
8680b6a50f10acd43e34775cd272ddb5cfeeb4c3

WITNESS_TRANSPORT_REF:
3f363a06d865f75484838ea13e2a4dab8023c67a

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_INVOCATION_RESULT_WITNESS_PRESSURE_RESULT_001.md`

blob:

`3d16354dbb5c162d4a29f887d2fb0af497df5b4d`

Required disposition:

`MATERIALIZED_INVOCATION_RESULT_WITNESS_MATCHED`

If absent, mismatched, or unresolved, return:

`MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_UNRESOLVED`

# TARGET

Adjudicate only:

```
ONE IMMUTABLE EXACT MATERIALIZED-WORK RESULT WITNESS
+
EXTERNALLY SUPPLIED FIELD DISPOSITIONS
+
EXPLICIT SETTLEMENT BASES
→
ONE DETERMINISTIC CANDIDATE SETTLEMENT
```

while conserving exact:
- successor identity;
- work-spec identity;
- materialized-unit identity;
- atomic-admission identity;
- consumption identity;
- work-attempt identity;
- raw-output identity;
- source-witness identity.

# FROZEN IMPLEMENTATION EVIDENCE

At exact source ref
`8680b6a50f10acd43e34775cd272ddb5cfeeb4c3`:

1. `src/coordination/materialized_invocation_result_settlement_v0.py`
   blob:
   `43c011de42208879e356702c216bc9c5a72542e9`

2. `tests/coordination/test_materialized_invocation_result_settlement_v0.py`
   blob:
   `a5179fddb3added7f3e465dc9a24bebfae85bfa5`

3. `tools/observe_materialized_invocation_result_settlement_v0.py`
   blob:
   `b0e0abb310bd7c9c3704866d243006e5bf2677e6`

4. `docs/campaigns/workcycle_stabilization_001/MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `9abfa175ed5006122f92df79d441ba35ff7e5a1c`

5. `src/cockpit/workcycle_qualification.py`
   blob:
   `7e22ba77bafa909de1deab5180a0a74bae6f1d64`

6. `src/cockpit/pressure_justification.py`
   blob:
   `a6f5b64a837c56a18b5b38ed67ef5d1a33b60ada`

# RUNTIME WITNESS

Use exactly:

`materialized_invocation_result_settlement_observation.json`

at witness transport ref:

`3f363a06d865f75484838ea13e2a4dab8023c67a`

blob:

`2dc73570bab8fb35dec2ec0705c0cf82fd92e346`

The witness declares exercised repo head:

```
8680b6a50f10acd43e34775cd272ddb5cfeeb4c3
```

The only source→transport delta is:

```
materialized_invocation_result_settlement_observation.json
```

# REQUIRED SOURCE-WITNESS CASE

Adjudicate whether the source immutable result witness is preserved and bound by:

```
source_witness_id
source_raw_output_sha256
source_work_attempt_id
```

# REQUIRED EXACT-WORK LINEAGE CASE

The settlement must bind exact:

```
source_successor_id
source_successor_integrity_sha256

source_work_spec_id
source_work_spec_integrity_sha256

source_materialized_work_item_id
source_materialized_unit_integrity_sha256

source_consumption_id
source_atomic_admission_id
```

# REQUIRED FIELD-LEVEL SETTLEMENT CASE

The supplied runtime witness classifies fields with externally supplied dispositions.

Required disposition vocabulary:

```
CANDIDATE_ACCEPTED
CANDIDATE_HELD
CANDIDATE_REJECTED
UNRESOLVED
```

The runtime fixture directly demonstrates:
- `fixture_result` -> CANDIDATE_ACCEPTED
- `work_item_id` -> CANDIDATE_ACCEPTED
- `count` -> CANDIDATE_HELD

The test evidence separately exercises all four classes, including rejected and unresolved.

# REQUIRED CLASSIFICATION-SOURCE CASE

Required:

```
classification_source = EXTERNALLY_SUPPLIED
```

The settlement layer must not invent its own field dispositions.

# REQUIRED DETERMINISM

Identical:
- source witness;
- field dispositions;
- settlement bases;
- settlement actor identity;

must produce identical settlement identity.

# REQUIRED DISPOSITION-MUTATION CASE

Holding source witness and bases fixed while changing one field disposition must change:

```
settlement_id
```

# REQUIRED TAMPER CASES

Adjudicate whether:
- exact-work lineage tampering is rejected;
- raw-output tampering without matching digest/witness identity is rejected by supplied tests.

# REQUIRED ACCEPTANCE NEUTRALITY

A field classified:

```
CANDIDATE_ACCEPTED
```

must NOT imply:

```
QUALIFIED
SEMANTIC_TRUTH
EXTERNAL_CONSEQUENCE
```

Required:

```
scientific_admission_created = false
qualification_effect = NONE
external_consequence_effect = NONE
```

# REQUIRED EFFECT NEUTRALITY

Required:

```
authority_effect = NONE
execution_effect = NONE
external_consequence_effect = NONE
atlas_mutation_effect = NONE
scientific_standing_effect = NONE
```

# REQUIRED NON-COLLAPSES

Preserve:

```
CANDIDATE_ACCEPTED
!=
QUALIFIED

SETTLEMENT
!=
SEMANTIC TRUTH

SETTLEMENT
!=
EXTERNAL CONSEQUENCE

SETTLEMENT
!=
BASIS RECONCILIATION

SETTLEMENT
!=
AUTHORITY

SETTLEMENT
!=
WORK EXECUTION

SETTLEMENT
!=
ATLAS MUTATION

MATCHED SETTLEMENT
!=
REPEATED METABOLIC LOOP STANDING
```

# CLAIM CEILING

The strongest admissible MATCHED claim is:

```
At the exact supplied source, one immutable exact materialized-work result
witness can receive externally supplied field-level candidate dispositions and
explicit bases in one deterministic settlement record while conserving exact
successor, work-spec, materialized-unit, admission, consumption, attempt, and
output lineage. Candidate acceptance creates no qualification and settlement
creates no external consequence, authority, execution, Atlas mutation, or
scientific standing.
```

Do NOT infer:
- semantic truth;
- scientific qualification;
- external consequence;
- basis reconciliation;
- work execution standing;
- production execution;
- authority;
- Atlas mutation;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

# DISPOSITION LAW

Return exactly one:

```
MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_MATCHED
MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_PARTIAL
MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_FRACTURED
MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_UNRESOLVED
```

MATCHED requires:
- predecessor exact result-witness standing MATCHED;
- witness source equals exact source;
- witness-only transport;
- source witness preserved;
- source witness/output identities bound;
- exact successor/work-spec/materialized-unit lineage bound;
- admission/consumption/attempt lineage bound;
- field-level dispositions recorded;
- classification source externally supplied;
- fixed inputs deterministic;
- disposition change changes settlement identity;
- tampered chain rejected;
- accepted fields create no qualification;
- no consequence/authority/execution/Atlas/standing effect;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_MATERIALIZED_RESULT_WITNESS:
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

SUCCESSOR_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

WORK_SPEC_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

MATERIALIZED_UNIT_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

ADMISSION_CONSUMPTION_ATTEMPT_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

FIELD_LEVEL_DISPOSITIONS:
MATCHED | FRACTURED | UNRESOLVED

CLASSIFICATION_SOURCE:
EXTERNALLY_SUPPLIED | OTHER | UNRESOLVED

FIXED_INPUTS_DETERMINISTIC:
YES | NO | UNRESOLVED

DISPOSITION_CHANGE_CHANGES_SETTLEMENT:
YES | NO | UNRESOLVED

TAMPERED_CHAIN:
REJECTED | ACCEPTED | UNRESOLVED

ACCEPTED_CREATES_QUALIFICATION:
true | false | UNRESOLVED

EXTERNAL_CONSEQUENCE_EFFECT:
NONE | NON_NONE | UNRESOLVED

AUTHORITY_EFFECT:
EXECUTION_EFFECT:
ATLAS_MUTATION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_MATCHED
| MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_PARTIAL
| MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_FRACTURED
| MATERIALIZED_INVOCATION_RESULT_SETTLEMENT_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
