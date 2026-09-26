# WORKCYCLE_STABILIZATION_001 — SUCCESSOR WORK-UNIT MATERIALIZATION PRESSURE 001

OBJECT_TYPE:
READY_TO_RUN_RUNTIME_OBSERVATION_PACKET

PRESSURE_ID:
SUCCESSOR_WORK_UNIT_MATERIALIZATION_PRESSURE_001

STATUS:
READY_AFTER_SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_MATCHED

ROLE:
LOCAL_SUCCESSOR_WORK_UNIT_MATERIALIZATION_WITNESS

MODE:
DISPOSABLE_SAME_PROCESS_FIXTURE
+
EXTERNALLY_SUPPLIED_WORK_SPEC
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

RUN_SOURCE_IDENTITY:
CAPTURE_EXACT_REPO_HEAD_IN_RUNTIME_WITNESS

# REQUIRED PREDECESSOR

```
SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_MATCHED
```

at:

`docs/campaigns/workcycle_stabilization_001/pressure_runs/SECOND_SUCCESSOR_FROM_RECONCILIATION_REPAIR_RESULT_001.md`

# TARGET

Pressure exactly:

```
ONE EXACT SUCCESSOR_CANDIDATE_V1
+
ONE EXPLICIT EXTERNALLY SUPPLIED BOUNDED WORK SPEC
→
ONE COMPLETE basis_workcycle_v1-COMPATIBLE NEXT WORKFLOW UNIT
```

The materializer must not infer or invent the work spec.

# CORE NON-COLLAPSES

```
NEXT_PRESSURE_BASIS
!=
EXECUTABLE WORK SPEC

SUCCESSOR IDENTITY
!=
WORK SPEC

WORK SPEC
!=
AUTHORITY

MATERIALIZED WORK UNIT
!=
WORK ADMISSION

PRESSURE ADMISSIBLE
!=
WORK ADMITTED

MATERIALIZED
!=
QUALIFIED

MATERIALIZED
!=
EXECUTED
```

# REQUIRED SUCCESSOR CASE

Derive one exact PARTIALLY_SATISFIED successor:

```
PARTIALLY_SATISFIED
→ RESOLVE_LOAD_BEARING_GAP
→ PROPOSED_NOT_ADMITTED
→ successor_id != null
→ next_pressure_basis != null
```

No human/manual successor ID may be supplied.

# REQUIRED WORK-SPEC CASE

The explicit work spec must bind exactly:

```
source_successor_id
source_successor_integrity_sha256
source_reconciliation_identity
source_next_pressure_basis
```

and must declare:

```
spec_source = EXTERNALLY_SUPPLIED
```

The spec must separately carry bounded transformation semantics including:
- desired consequence;
- relevance question;
- pressure ID;
- target distinction;
- selection basis;
- expected information gain;
- application dependency;
- load-bearing effects;
- allowed/prohibited operations;
- success/failure/unresolved conditions;
- pressure budget;
- application target/proposed change;
- expected effect;
- operating change.

# REQUIRED MATERIALIZATION CASE

The materialized unit must satisfy:

```
identity.work_item_id == successor.successor_id
identity.campaign_id == successor.campaign_id
identity.parent_work_item_id == successor.parent_work_item_id
identity.operative_frame_ref == successor.operative_frame_ref

basis.basis_id == successor.basis_id
basis.statement == successor.next_pressure_basis
basis.current_obstruction.statement == successor.next_pressure_basis

materialization.source_successor_id == successor.successor_id
materialization.source_reconciliation_identity == successor.reconciliation_identity
materialization.work_spec_id == explicit work_spec.work_spec_id
```

and must pass:

`basis_workcycle_v1.validate_workflow_unit()`

# REQUIRED DETERMINISM CASE

Identical:

```
successor
+
work spec
```

must yield an identical materialized unit and unit integrity identity.

# REQUIRED SPEC-VARIATION CASE

Hold the successor fixed and change the explicit bounded work spec.

Required:

```
successor_id unchanged
materialized unit integrity changes
```

This preserves:

```
SUCCESSOR IDENTITY
!=
WORK SPEC IDENTITY
```

# REQUIRED TAMPER CASE

Mutate the sealed work spec without resealing it.

Required:

```
materialization
→ REJECT
```

# REQUIRED NO-SUCCESSOR CASE

A:

```
SATISFIED
→ CLOSE_BASIS
→ NO_SUCCESSOR
```

projection must not be materializable as a new work unit.

# REQUIRED ADMISSIBILITY SEPARATION

The completed materialized unit may be structurally pressure-admissible.

Required:

```
pressure_admissible = true
work_admission_effect = NONE
```

This does not admit the unit.

# REQUIRED NEUTRAL EFFECTS

The materialized unit must begin with:

```
qualification.scientific_standing = NONE
application.application_status = NOT_YET_ELIGIBLE

materialization.work_admission_effect = NONE
materialization.authority_effect = NONE
materialization.execution_effect = NONE
materialization.scientific_standing_effect = NONE
```

# EXECUTION

```powershell
git pull

Remove-Item successor_work_unit_materialization_observation.json -ErrorAction SilentlyContinue

python -m unittest `
  tests.coordination.test_basis_workcycle_v1 `
  tests.coordination.test_successor_work_unit_materialization_v0 `
  tests.cockpit.test_workcycle_qualification `
  tests.cockpit.test_pressure_justification

python tools/observe_successor_work_unit_materialization_v0.py
```

Expected witness:

`successor_work_unit_materialization_observation.json`

Expected terminal shape:

```
[OK] all_assertions_pass True
[OK] successor_id successor:sha256:...
[OK] materialized_work_item_id successor:sha256:...
[OK] pressure_admissible True
```

# CLAIM CEILING

Success may establish only:

```
At the exact supplied source, one exact deterministic successor candidate plus
one externally supplied bounded work specification can materialize one complete
basis_workcycle_v1-compatible next workflow unit while conserving exact
successor, reconciliation, and next-pressure lineage. The same successor can
bind different explicit work specs into different materialized units, so
successor identity and executable work specification remain distinct.
Materialization creates no qualification, work admission, authority, execution,
or scientific standing.
```

It does not establish:
- automatic work-spec generation;
- planner standing;
- autonomous decomposition;
- successor admission;
- authority;
- execution;
- repeated metabolic loop standing;
- self-moving-workcycle standing.

WORK_ADMISSION_EFFECT:
NONE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

STOPPED:
YES
