# WORKCYCLE_STABILIZATION_001 — MATERIALIZED ADMITTED AUTHORITY CONSUMPTION INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE_001

ROLE:
INDEPENDENT_EXACT_MATERIALIZED_WORK_CONSUMPTION_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_REPAIR
+
NO_RESULT_INTERPRETATION
+
NO_RESULT_WITNESS_CREATION
+
NO_SETTLEMENT
+
NO_EXTERNAL_CONSEQUENCE_CLAIM
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
793672dbce01ecd0a5ecdb0cfe79f8487eed53f2

WITNESS_TRANSPORT_REF:
7967ef73e862fa0d5beea0c5941d46b385820aaa

AUTHORITY_EFFECT:
NONE

CONSUMPTION_EFFECT:
CONSUMED_ONE_USE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_RESULT_001.md`

blob:

`af2b2c813ae0d20c4d85434cca9a5a40fe5b72d5`

Required disposition:

`MATERIALIZED_UNIT_AUTHORITY_BINDING_REPAIR_MATCHED`

If absent, mismatched, or unresolved, return
`MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_UNRESOLVED`.

# TARGET

Adjudicate only:

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

while conserving exact:
- successor identity;
- work-spec identity;
- materialized workflow-unit identity;
- exact admission composition identity;
- work-attempt identity.

# FROZEN IMPLEMENTATION EVIDENCE

At exact source ref
`793672dbce01ecd0a5ecdb0cfe79f8487eed53f2`:

1. `src/coordination/materialized_admitted_authority_consumption_v0.py`
   blob:
   `4f959d5c4ef7d1703e7c710b79a751d1b3b09cdf`

2. `tests/coordination/test_materialized_admitted_authority_consumption_v0.py`
   blob:
   `237d69f9b692cf55f1cac8e11de4268eb5e11438`

3. `tools/observe_materialized_admitted_authority_consumption_v0.py`
   blob:
   `e635481b0381b354e64d2dae9a52ab7f9b908f2d`

4. `docs/campaigns/workcycle_stabilization_001/MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `899c61df13856de524ed626bc3bd51c9ed509bea`

5. `src/cockpit/workcycle_qualification.py`
   blob:
   `ccd3fa74550f98881b7556e73e365249d6485668`

6. `src/cockpit/pressure_justification.py`
   blob:
   `9709fa7d382fe7529cda4f4e30ff01d08dbe4b58`

# RUNTIME WITNESS

Use exactly:

`materialized_admitted_authority_consumption_observation.json`

at witness transport ref:

`7967ef73e862fa0d5beea0c5941d46b385820aaa`

blob:

`b71914071d166f7e729ac01f03d9ccca8a64afaa`

The witness declares exercised repo head:

```
793672dbce01ecd0a5ecdb0cfe79f8487eed53f2
```

The only source→transport delta is:

```
materialized_admitted_authority_consumption_observation.json
```

# REQUIRED EXACT CONSUMPTION CASE

Adjudicate whether one exact:
- successor;
- sealed externally supplied work spec;
- sealed materialized workflow unit;
- exact-work atomic admission receipt;
- current one-use authority envelope;

produces:

```
consumed = true
invocation_performed = true
invocation_count = 1
callback_calls = 1
authority_status_after = CONSUMED
authority_remaining_uses_after = 0
```

# REQUIRED LINEAGE CONSERVATION

The consumption receipt must bind exact:

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

Adjudicate whether:

```
invocation_result
==
exact caller-supplied callback return
```

and whether that return is preserved only as an uninterpreted value.

Do not treat it as:
- an immutable result witness;
- semantic truth;
- settlement;
- external consequence.

# REQUIRED REPLAY CASE

After successful consumption, adjudicate whether replay yields:

```
consumed = false
blocker = authority_verification_failed
callback_calls = 0
```

# REQUIRED WRONG-MATERIALIZATION CASE

Under a fresh authority/admission fixture for work A, supplying a different
same-successor work realization B must yield:

```
consumed = false
callback_calls = 0
authority_status_after = ACTIVE
authority_remaining_uses_after = 1
```

The supplied witness reports blocker:

```
admission_materialized_unit_integrity_sha256_mismatch
```

# REQUIRED TESTED FAILURE CASES

The supplied tests must support:

1. tampered exact admission receipt blocks before consumption/callback;
2. callback failure after reservation leaves:
   ```
   RECOVERY_REQUIRED
   remaining_uses = 0
   replay denied
   ```
3. no automatic retry occurs.

# REQUIRED EFFECT SEPARATION

Preserve:

```
authority_consumed = true
consumption_effect = CONSUMED_ONE_USE
invocation_performed = true

BUT

authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

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
MODEL EXECUTION CLAIM

RAW CALLBACK RETURN
!=
RESULT WITNESS

RAW CALLBACK RETURN
!=
SETTLEMENT

RAW CALLBACK RETURN
!=
EXTERNAL CONSEQUENCE

MATCHED CONSUMPTION
!=
REPEATED METABOLIC LOOP STANDING
```

# CLAIM CEILING

The strongest admissible MATCHED claim is:

```
At the exact supplied source, one exact admitted materialized-work object can be
rebound to the same current one-use local authority and cross one caller-supplied
callback exactly once under one-shot consumption while conserving exact
successor, work-spec, and materialized-unit identities. Replay is denied and a
different materialization is blocked before consumption. Post-reservation
callback failure leaves RECOVERY_REQUIRED with zero remaining uses and replay
denied. The raw callback return is preserved only as an uninterpreted return
value; no result witness, settlement, external consequence, work-execution
standing, or scientific standing is established.
```

Do NOT infer:
- immutable result witnessing;
- semantic correctness;
- settlement;
- external consequence;
- model identity;
- work execution;
- production execution;
- cross-process atomicity;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

# DISPOSITION LAW

Return exactly one:

```
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_MATCHED
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_PARTIAL
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_FRACTURED
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_UNRESOLVED
```

MATCHED requires:
- predecessor exact-work authority repair matched;
- witness source matches exact source;
- witness-only transport;
- exact one-shot consumption succeeds;
- callback count is exactly one;
- receipt conserves exact successor/work-spec/materialized-unit lineage;
- raw return is preserved without interpretation;
- replay is blocked without callback;
- wrong materialization blocks before consumption and leaves authority active;
- tested post-reservation failure enters RECOVERY_REQUIRED with replay denied;
- execution/scientific-standing effects remain NONE;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_EXACT_MATERIALIZED_WORK_AUTHORITY:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

FROZEN_IMPLEMENTATION_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

WITNESS_ONLY_TRANSPORT:
YES | NO | UNRESOLVED

EXACT_CONSUMPTION_CASE:
MATCHED | FRACTURED | UNRESOLVED

AUTHORITY_CONSUMED:
true | false | UNRESOLVED

INVOCATION_PERFORMED:
true | false | UNRESOLVED

INVOCATION_COUNT:
1 | OTHER | UNRESOLVED

CALLBACK_CALLS:
1 | OTHER | UNRESOLVED

SUCCESSOR_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

WORK_SPEC_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

MATERIALIZED_UNIT_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

RAW_RETURN_PRESERVED:
YES | NO | UNRESOLVED

RAW_RETURN_INTERPRETED_AS_RESULT:
YES | NO | UNRESOLVED

REPLAY:
BLOCKED | ADMITTED | UNRESOLVED

REPLAY_CALLBACK_CALLS:
0 | OTHER | UNRESOLVED

WRONG_MATERIALIZATION:
BLOCKED_BEFORE_CONSUMPTION | CONSUMED | UNRESOLVED

WRONG_MATERIALIZATION_AUTHORITY_STATUS:
ACTIVE | OTHER | UNRESOLVED

WRONG_MATERIALIZATION_REMAINING_USES:
1 | OTHER | UNRESOLVED

POST_RESERVATION_FAILURE:
RECOVERY_REQUIRED | OTHER | UNRESOLVED

FAILURE_REPLAY:
BLOCKED | ADMITTED | UNRESOLVED

AUTHORITY_EFFECT:
CONSUMPTION_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_MATCHED
| MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_PARTIAL
| MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_FRACTURED
| MATERIALIZED_ADMITTED_AUTHORITY_CONSUMPTION_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
