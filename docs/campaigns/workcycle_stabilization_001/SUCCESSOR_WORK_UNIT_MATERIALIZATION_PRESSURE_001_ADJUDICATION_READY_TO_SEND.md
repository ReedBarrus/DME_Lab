# WORKCYCLE_STABILIZATION_001 — SUCCESSOR WORK-UNIT MATERIALIZATION INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE_001

ROLE:
INDEPENDENT_SUCCESSOR_WORK_UNIT_MATERIALIZATION_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_WORK_SPEC_INVENTION
+
NO_WORK_ADMISSION
+
NO_AUTHORITY_GRANT
+
NO_EXECUTION
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
0c6eec42366ab715029e5c645cf9d5baae22ff79

WITNESS_TRANSPORT_REF:
94ff342c43996fd7ed3dc061f28b8b07242f2eaa

WORK_ADMISSION_EFFECT:
NONE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_RESULT_001.md`

blob:

`740f9d4b1b65eedf803a28047bde2957f5cc4dc8`

Required disposition:

`SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_MATCHED`

If absent, mismatched, or unresolved, return
`SUCCESSOR_WORK_UNIT_MATERIALIZATION_UNRESOLVED`.

# TARGET

Adjudicate only:

```
ONE EXACT SUCCESSOR_CANDIDATE_V1
+
ONE EXPLICIT EXTERNALLY SUPPLIED BOUNDED WORK SPEC
→
ONE COMPLETE basis_workcycle_v1-COMPATIBLE NEXT WORKFLOW UNIT
```

while preserving:

```
NEXT_PRESSURE_BASIS
!=
EXECUTABLE WORK SPEC

SUCCESSOR IDENTITY
!=
WORK SPEC IDENTITY

MATERIALIZED WORK UNIT
!=
WORK ADMISSION

PRESSURE ADMISSIBLE
!=
WORK ADMITTED
```

# FROZEN IMPLEMENTATION EVIDENCE

At exact source ref
`0c6eec42366ab715029e5c645cf9d5baae22ff79`:

1. `src/coordination/successor_work_unit_materialization_v0.py`
   blob:
   `6792554122a38fd034f3c9b5cafb7ce6382d9221`

2. `tests/coordination/test_successor_work_unit_materialization_v0.py`
   blob:
   `5a5b9dcb3bb7568aad3e05ddf8565209b030c0e3`

3. `tools/observe_successor_work_unit_materialization_v0.py`
   blob:
   `6dd6131b376bca3b73aa4b7e8c66dae4af03ad82`

4. `docs/campaigns/workcycle_stabilization_001/SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `49ada15d5b665e3c110f9c2c7640a7bda8cc09ab`

5. `src/coordination/basis_workcycle_v1.py`
   blob:
   `f714e86fec8addd9d5eaaa93fc52108253ae6238`

6. `src/cockpit/workcycle_qualification.py`
   blob:
   `0cd98f0a542b727d9b664460d541c0a30ace8e56`

7. `src/cockpit/pressure_justification.py`
   blob:
   `48db4d5fac34f1525c2b7ba4c58dbde194df6b9e`

# RUNTIME WITNESS

Use exactly:

`successor_work_unit_materialization_observation.json`

at witness transport ref:

`94ff342c43996fd7ed3dc061f28b8b07242f2eaa`

blob:

`4cd6cc5232318e44324f113e2b9641f498453e79`

The witness declares exercised repo head:

```
0c6eec42366ab715029e5c645cf9d5baae22ff79
```

The only source→transport delta is:

```
successor_work_unit_materialization_observation.json
```

# REQUIRED SUCCESSOR BINDING

Adjudicate whether:

```
materialized_unit.identity.work_item_id
==
source_successor.successor_id
```

and whether exact successor integrity, reconciliation identity, and
next-pressure basis remain bound into the materialization coordinates.

# REQUIRED WORK-SPEC BINDING

Adjudicate whether the work spec is explicitly:

```
spec_source = EXTERNALLY_SUPPLIED
```

and binds the exact successor identity/integrity, reconciliation identity, and
next-pressure basis.

The materializer must not claim to generate or infer the work spec.

# REQUIRED UNIT VALIDITY

Adjudicate whether the materialized object is a complete
`basis_workcycle_v1`-compatible workflow unit and whether the supplied
validator accepts it.

# REQUIRED DETERMINISM

Identical:

```
successor
+
work spec
```

must produce identical materialized unit identity.

# REQUIRED SPEC-VARIATION CASE

Holding successor identity fixed while changing the explicit work spec must:

```
preserve successor_id
change work_spec_id
change materialized unit identity
```

This establishes only that successor identity and work-spec identity are
distinct coordinates.

# REQUIRED TAMPER CASE

A mutated sealed work spec without a matching seal must be rejected.

# REQUIRED NO-SUCCESSOR CASE

A no-successor projection must not be materializable into a new workflow unit.

# REQUIRED ADMISSIBILITY SEPARATION

Adjudicate whether the completed materialized unit can be:

```
pressure_admissible = true
```

while still retaining:

```
work_admission_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE
```

# REQUIRED INITIAL POSTURE

The materialized unit must begin with no inherited standing:

```
qualification.scientific_standing = NONE
application.application_status = NOT_YET_ELIGIBLE
```

# CLAIM CEILING

The strongest admissible MATCHED claim is:

```
At the exact supplied source, one exact deterministic successor candidate plus
one externally supplied bounded work specification can materialize one complete
basis_workcycle_v1-compatible next workflow unit while conserving exact
successor, reconciliation, and next-pressure lineage. The same successor can
bind different explicit work specifications into different materialized units,
so successor identity and executable work specification remain distinct.
Materialization creates no qualification, work admission, authority, execution,
or scientific standing.
```

Do NOT infer:
- automatic work-spec generation;
- planner standing;
- autonomous decomposition;
- successor admission;
- authority;
- execution;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

# DISPOSITION LAW

Return exactly one:

```
SUCCESSOR_WORK_UNIT_MATERIALIZATION_MATCHED
SUCCESSOR_WORK_UNIT_MATERIALIZATION_PARTIAL
SUCCESSOR_WORK_UNIT_MATERIALIZATION_FRACTURED
SUCCESSOR_WORK_UNIT_MATERIALIZATION_UNRESOLVED
```

MATCHED requires:
- predecessor matched;
- witness source matches exact implementation source;
- witness-only transport;
- successor identity becomes exact work-item identity;
- successor integrity/reconciliation/next-pressure identity remains bound;
- work spec is externally supplied and exactly bound;
- materialized unit validates under the current workflow-unit law;
- fixed inputs are deterministic;
- changed work spec changes materialized unit without changing successor;
- tampered work spec is rejected;
- no-successor projection cannot be materialized;
- pressure admissibility remains distinct from work admission;
- no qualification, authority, execution, or scientific-standing effect;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_SECOND_SUCCESSOR_REPAIR:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

FROZEN_IMPLEMENTATION_SOURCE:
WITNESS_SOURCE_MATCHED:
YES | NO | UNRESOLVED

WITNESS_ONLY_TRANSPORT:
YES | NO | UNRESOLVED

SUCCESSOR_IDENTITY_BECOMES_WORK_ITEM_IDENTITY:
YES | NO | UNRESOLVED

SUCCESSOR_LINEAGE_BOUND:
MATCHED | FRACTURED | UNRESOLVED

WORK_SPEC_SOURCE:
EXTERNALLY_SUPPLIED | SELF_GENERATED | UNRESOLVED

WORK_SPEC_BINDING:
MATCHED | FRACTURED | UNRESOLVED

MATERIALIZED_UNIT_VALID:
YES | NO | UNRESOLVED

FIXED_INPUTS_DETERMINISTIC:
YES | NO | UNRESOLVED

SPEC_VARIATION_PRESERVES_SUCCESSOR:
YES | NO | UNRESOLVED

SPEC_VARIATION_CHANGES_UNIT:
YES | NO | UNRESOLVED

TAMPERED_WORK_SPEC:
REJECTED | ACCEPTED | UNRESOLVED

NO_SUCCESSOR_MATERIALIZATION:
REJECTED | ACCEPTED | UNRESOLVED

PRESSURE_ADMISSIBLE:
true | false | UNRESOLVED

WORK_ADMISSION_EFFECT:
AUTHORITY_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
SUCCESSOR_WORK_UNIT_MATERIALIZATION_MATCHED
| SUCCESSOR_WORK_UNIT_MATERIALIZATION_PARTIAL
| SUCCESSOR_WORK_UNIT_MATERIALIZATION_FRACTURED
| SUCCESSOR_WORK_UNIT_MATERIALIZATION_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
