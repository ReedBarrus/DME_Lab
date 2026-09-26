# WORKCYCLE_STABILIZATION_001 — MATERIALIZED UNIT AUTHORITY BINDING INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

PRESSURE_ID:
MATERIALIZED_UNIT_AUTHORITY_BINDING_PRESSURE_001

ROLE:
INDEPENDENT_MATERIALIZED_UNIT_AUTHORITY_BINDING_ADJUDICATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_REPAIR
+
NO_AUTHORITY_GRANT
+
NO_AUTHORITY_CONSUMPTION
+
NO_EXECUTION
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
1984164bf4f6797d8249ceaf49fae712aa2445bf

WITNESS_TRANSPORT_REF:
c34b37b681c717dcc1b426385c942522dfc71a15

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# REQUIRED PREDECESSOR

Use exactly:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE_RESULT_001.md`

blob:

`b7d29f42141075e0c915e4a4744d0896ed101e3c`

Required disposition:

`SUCCESSOR_WORK_UNIT_MATERIALIZATION_MATCHED`

If absent, mismatched, or unresolved, return
`MATERIALIZED_UNIT_AUTHORITY_BINDING_UNRESOLVED`.

# TARGET

Adjudicate only whether the existing qualified successor-bound
authority/admission layer also binds the exact materialized workflow-unit and
work-spec identity now established beneath that successor.

Target distinction:

```
SUCCESSOR-BOUND AUTHORITY
!=
EXACT MATERIALIZED-WORK AUTHORITY
```

# FROZEN IMPLEMENTATION EVIDENCE

At exact source ref
`1984164bf4f6797d8249ceaf49fae712aa2445bf`:

1. `src/coordination/verified_authority_admission_v0.py`
   blob:
   `1dc9be5833f1af06af820ac454d368d696e11f61`

2. `src/coordination/successor_work_unit_materialization_v0.py`
   blob:
   `6792554122a38fd034f3c9b5cafb7ce6382d9221`

3. `tools/observe_materialized_unit_authority_binding_v0.py`
   blob:
   `4a9459c41ee8b3d5fc1db279a301cb2c8aa08cac`

4. `docs/campaigns/workcycle_stabilization_001/MATERIALIZED_UNIT_AUTHORITY_BINDING_PRESSURE_001_READY_TO_RUN.md`
   blob:
   `e6c7322740faf5df883aff3df8331e64317421ec`

5. `src/cockpit/workcycle_qualification.py`
   blob:
   `3824c6eed055c957518e6e32106dcf3995d5be88`

6. `src/cockpit/pressure_justification.py`
   blob:
   `e5bca8ece203955410c78fd8feb85cdbbeb168d7`

# RUNTIME WITNESS

Use exactly:

`materialized_unit_authority_binding_observation.json`

at witness transport ref:

`c34b37b681c717dcc1b426385c942522dfc71a15`

blob:

`09675a38c133e02f89b498ae364cc414da69a6f0`

The witness declares exercised repo head:

```
1984164bf4f6797d8249ceaf49fae712aa2445bf
```

The only source→transport delta is:

```
materialized_unit_authority_binding_observation.json
```

# REQUIRED SAME-SUCCESSOR / DIFFERENT-WORK CASE

The witness must establish:

```
same successor_id

WORK_SPEC_A != WORK_SPEC_B

UNIT_A.integrity != UNIT_B.integrity
```

while both materialized units retain:

```
work_item_id == successor_id
```

# REQUIRED AUTHORITY-COORDINATE CASE

Adjudicate whether current successor authority coordinates satisfy:

```
authority_input_sha256 == successor_integrity_sha256
authority_input_sha256 != UNIT_A.integrity_sha256
authority_input_sha256 != UNIT_B.integrity_sha256
```

and whether the same successor authority request/input coordinates are therefore
shared across both materializations.

# REQUIRED ADMISSION CASE

In separate disposable roots, adjudicate whether the existing
successor-bound atomic-admission path admits:

```
UNIT_A's successor
and
UNIT_B's successor
```

under the same successor-bound authority coordinates.

Do not infer that both units were executed. Only the admission decision is under
pressure.

# REQUIRED RECEIPT-IDENTITY CASE

Adjudicate whether the resulting admission receipts lack both:

```
materialized_unit_integrity_sha256
work_spec_id
```

and therefore do not bind the exact materialized work semantics.

# REQUIRED FRACTURE CHARACTERIZATION

Adjudicate whether the evidence supports:

```
SUCCESSOR-BOUND AUTHORITY:
still valid under its prior claim ceiling

BUT

EXACT MATERIALIZED-WORK AUTHORITY:
not established
```

and specifically:

```
AUTHORITY RESOLUTION
<
CURRENT CONSEQUENCE-BEARING WORK RESOLUTION
```

Do not repair the authority law.

# REQUIRED NON-COLLAPSES

Preserve:

```
SUCCESSOR IDENTITY
!=
MATERIALIZED WORK-UNIT IDENTITY

MATERIALIZED WORK-UNIT IDENTITY
!=
WORK-SPEC IDENTITY

SUCCESSOR-BOUND AUTHORITY
!=
EXACT WORK-UNIT AUTHORITY

COMPONENT STANDING
!=
COMPOSITION STANDING

ADMISSION
!=
EXECUTION

OBSERVED FRACTURE
!=
PRODUCTION EXPLOIT

FRACTURE
!=
REPAIR AUTHORIZED
```

# CLAIM CEILING

A FRACTURED result may establish only:

```
At the exact supplied source, the existing qualified successor-bound
authority/admission layer does not bind exact materialized workflow-unit
integrity or work-spec identity. Two distinct materialized units derived from
the same successor share the same successor authority coordinates and can each
cross the existing successor-bound admission decision in separate disposable
fixtures without presenting exact materialized-unit identity to that layer.
This does not invalidate successor-bound authority/admission standing in
isolation and does not establish a production exploit.
```

Do NOT infer:
- incorrect successor identity;
- incorrect materialization;
- invalid successor-authority standing in isolation;
- authority consumption;
- work execution;
- model invocation;
- production exploit;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

# DISPOSITION LAW

Return exactly one:

```
MATERIALIZED_UNIT_AUTHORITY_BINDING_MATCHED
MATERIALIZED_UNIT_AUTHORITY_BINDING_PARTIAL
MATERIALIZED_UNIT_AUTHORITY_BINDING_FRACTURED
MATERIALIZED_UNIT_AUTHORITY_BINDING_UNRESOLVED
```

MATCHED requires current authority/admission to distinguish exact materialized
unit/work-spec identity before admission.

FRACTURED is appropriate if:
- predecessor matched;
- witness source matches exact source;
- witness-only transport;
- same successor yields two distinct materialized units;
- authority binds successor integrity but neither unit integrity;
- same successor authority coordinates admit both cases;
- admission receipts do not bind unit integrity or work-spec identity;
- component standing remains intact;
- claim ceiling preserved.

# REQUIRED RETURN

Return only:

```
PRESSURE_ID:

PREDECESSOR_SUCCESSOR_WORK_UNIT_MATERIALIZATION:
MATCHED | NOT_MATCHED | ABSENT | UNRESOLVED

FROZEN_IMPLEMENTATION_SOURCE:
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

AUTHORITY_BINDS_SUCCESSOR_INTEGRITY:
YES | NO | UNRESOLVED

AUTHORITY_BINDS_UNIT_A_INTEGRITY:
YES | NO | UNRESOLVED

AUTHORITY_BINDS_UNIT_B_INTEGRITY:
YES | NO | UNRESOLVED

SAME_SUCCESSOR_AUTHORITY_ACCEPTS_UNIT_A:
YES | NO | UNRESOLVED

SAME_SUCCESSOR_AUTHORITY_ACCEPTS_UNIT_B:
YES | NO | UNRESOLVED

ADMISSION_RECEIPTS_BIND_MATERIALIZED_UNIT:
YES | NO | UNRESOLVED

ADMISSION_RECEIPTS_BIND_WORK_SPEC:
YES | NO | UNRESOLVED

COMPONENT_STANDING_COLLAPSED:
YES | NO | UNRESOLVED

AUTHORITY_EFFECT:
EXECUTION_EFFECT:
SCIENTIFIC_STANDING_EFFECT:

CLAIM_CEILING_PRESERVED:
YES | NO | UNRESOLVED

DISPOSITION:
MATERIALIZED_UNIT_AUTHORITY_BINDING_MATCHED
| MATERIALIZED_UNIT_AUTHORITY_BINDING_PARTIAL
| MATERIALIZED_UNIT_AUTHORITY_BINDING_FRACTURED
| MATERIALIZED_UNIT_AUTHORITY_BINDING_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
