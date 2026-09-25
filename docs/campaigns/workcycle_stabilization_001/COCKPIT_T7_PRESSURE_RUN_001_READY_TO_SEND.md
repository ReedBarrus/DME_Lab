# WORKCYCLE_STABILIZATION_001 — T7 OPERATOR VISIBILITY FRESH EVALUATION

OBJECT_TYPE:
READY_TO_SEND_PRESSURE_PACKET

ROLE:
INDEPENDENT_OPERATOR_VISIBILITY_EVALUATOR

MODE:
FRESH_SEAT
+
NO_LIVE_CHAT_CONTEXT
+
READ_ONLY
+
NO_SELF_REPAIR
+
NO_EXECUTION
+
NO_AUTHORITY_GRANT
+
NO_CAMPAIGN_REPLAN

EVIDENCE_SOURCE_REF:
f3453f16f7bbe40d4a3febba44ff4b9e33a21966

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SCIENTIFIC_STANDING_EFFECT:
NONE

# TARGET

Adjudicate whether the current WORKCYCLE_STABILIZATION_001 operator projection
truthfully exposes the bounded current operating world needed by an operator,
without projection itself creating authority, execution, campaign progress, or
scientific standing.

This is T7 only.

Do not redesign the Cockpit.
Do not repair code.
Do not infer missing runtime state.
Do not use predecessor reasoning or live-chat context.

# PRECONDITION

The local operator reported the required test suite as:

```
................
----------------------------------------------------------------------
Ran 16 tests in 0.063s

OK
```

The generated current projection snapshot is frozen as:
`t7_projection.json`

Treat the local-test result as reported evidence only; do not claim you reran it.

# USE ONLY

At exact source ref:
`f3453f16f7bbe40d4a3febba44ff4b9e33a21966`

1. `t7_projection.json`
   blob: `88a96691f726b1c880b63920a164b12a9e89091d`

2. `docs/campaigns/workcycle_stabilization_001/state/T7_LOCAL_PRECONDITION_RESULT_001.md`
   blob: `10afa7e66ddec54bd374b90eac2a7b1617725aab`

3. `src/cockpit/workcycle_projection.py`
   blob: `2df9c6a2146f5c68bf3508b86406125ac545b564`

4. `src/cockpit/live_runtime_projection.py`
   blob: `7e30dc5f91735f6e915e632873f10b26e7d35e3f`

5. `src/cockpit/workcycle_control.py`
   blob: `2b84cd65efc162dd6c58907f9b49b1c72cdcc631`

6. `src/coordination/workcycle_v0.py`
   blob: `b39338ac45ece77afe62ba64b525fe8def8ae75d`

7. `tests/cockpit/test_workcycle_projection.py`
   blob: `37ced8f7787b59f30cd7eb1641b4f2eba1c65b38`

8. `tests/coordination/test_workcycle_v0.py`
   blob: `7c9847850a66f8be5c025bb58a776fa42376e7a2`

9. `docs/campaigns/workcycle_stabilization_001/COCKPIT_T7_PRESSURE_READY_TO_SEND.md`
   blob: `7f7afb8aee5d2a93934fe351a98b9d752edfad4c`

Do not use any other repository files.

# CURRENT SNAPSHOT FACTS TO PRESSURE, NOT ASSUME

The frozen projection currently reports:

```
T0 = BOUNDED_PASS
T1 = BOUNDED_PASS
T2 = BOUNDED_PASS
T3 = BOUNDED_PASS
T4 = BOUNDED_PASS
T5 = BOUNDED_PASS
T6 = BOUNDED_PASS
T7 = IMPLEMENTED_UNPRESSURED

next_pressure = T7_PRESSURE

active_work_item = null
latest_completed_work_item = WORKCYCLE_STABILIZATION_001_COMPRESSION_W1
next_eligible_work_item = null

eligibility.posture = PARTIAL_COORDINATES_ONLY
eligibility.eligible = null

operative_control.status = LOCAL_OPERATOR_CONTROL_UNAVAILABLE
operator_summary.workflow = OFF
operator_summary.reed_action = REVIEW_NEXT_PRESSURE

projection_boundary.read_only = true
projection_boundary.creates_authority = false
projection_boundary.performs_execution = false
projection_boundary.advances_campaign_standing = false
projection_boundary.mutates_atlas = false

bounded qualification blockers:
- T7:IMPLEMENTED_UNPRESSURED
- TEMPORAL_HORIZON:UNFROZEN
```

These are claims under evaluation, not pre-adjudicated facts.

# REQUIRED NON-COLLAPSES

```
RESULT FILE EXISTS
!=
RESULT SUPPORTS PASS

HISTORICAL UNRESOLVED
!=
CURRENT UNRESOLVED

LATEST COMPLETED
!=
ACTIVE

PARTIAL ELIGIBILITY
!=
REAL ELIGIBILITY

REPO REQUESTED CONTROL
!=
OPERATIVE LOCAL CONTROL

WAKE BUDGET
!=
CUMULATIVE CAMPAIGN BUDGET

REGISTERED SEAT
!=
LIVE OCCUPANT
!=
EXECUTION AUTHORITY

WAKE REQUEST
!=
WORK ADMISSION
!=
MODEL INVOCATION

CURRENT WORLD
!=
REPLAY ENTIRE HISTORY

OPTIONAL OVERLAY FAILURE
!=
CURRENT WORLD FAILURE
```

# EVALUATION QUESTIONS

Adjudicate whether the supplied projection + implementation + tests support the
following operator-visible properties:

1. campaign identity is visible;
2. active horizon is visible;
3. currentness separates:
   - active work,
   - latest completed work,
   - next eligible work,
   - current unresolved,
   - historical unresolved;
4. latest consequence and its evaluation are visible;
5. repair specification and repair result remain distinct;
6. wake budget is visible and not mislabeled as cumulative campaign budget;
7. requested repository control is distinct from operator-local control;
8. partial eligibility remains explicitly non-admitted;
9. durable seat identity remains distinct from live occupancy and authority;
10. projection itself remains read-only and non-authorizing;
11. operator-facing next pressure is visible;
12. whether Reed action is required is visible;
13. malformed/stale optional evidence degrades legibly rather than manufacturing PASS;
14. the current-world projection does not require replaying all history;
15. local control semantics require preview identity + explicit REED confirmation.

For runtime behaviors not actually witnessed by the frozen current projection,
distinguish:
```
IMPLEMENTATION/TEST SUPPORT
!=
CURRENT LIVE RUNTIME OBSERVATION
```

Do not mark a runtime behavior as currently observed merely because a unit test
covers it.

# DISPOSITION LAW

Return exactly one:

```
COCKPIT_PROJECTION_MATCHED
COCKPIT_PROJECTION_PARTIAL
COCKPIT_PROJECTION_FRACTURED
COCKPIT_PROJECTION_UNRESOLVED
```

MATCHED requires no unresolved load-bearing wound in the T7 operator-visibility
claim within this evidence aperture.

PARTIAL is appropriate when the projection is substantively correct but one or
more requested T7 operator-visible properties are supported only by
implementation/tests rather than current-world evidence, or a non-load-bearing
visibility wound remains.

FRACTURED requires a material contradiction or collapse in the claimed T7
operator-visibility semantics.

UNRESOLVED applies when the supplied evidence aperture cannot support a bounded
determination.

# REQUIRED RETURN

Return only:

```
CAMPAIGN_VISIBLE:
HORIZON_VISIBLE:
CURRENTNESS_LEGIBLE:
CONSEQUENCE_VISIBLE:
REPAIR_SPEC_RESULT_SEPARATED:
BUDGET_VISIBLE:
CONTROL_VISIBLE:
NEXT_PRESSURE_VISIBLE:
REED_ACTION_VISIBLE:
PROJECTION_READ_ONLY:

IMPLEMENTATION_TEST_SUPPORT:
CURRENT_RUNTIME_OBSERVATION_LIMIT:

AUTHORITY_EFFECT:
EXECUTION_EFFECT:

DISPOSITION:
COCKPIT_PROJECTION_MATCHED
| COCKPIT_PROJECTION_PARTIAL
| COCKPIT_PROJECTION_FRACTURED
| COCKPIT_PROJECTION_UNRESOLVED

UNRESOLVED:
[...]

CLAIM_CEILING:

STOPPED:
YES
```
