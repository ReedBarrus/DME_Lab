# WORKCYCLE_STABILIZATION_001 — T7 COCKPIT PROJECTION PRESSURE

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

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

## PRECONDITION

Run only after local tests for:
- tests.coordination.test_workcycle_v0
- tests.cockpit.test_workcycle_projection
pass.

## USE ONLY

1. `src/cockpit/workcycle_projection.py`
2. `src/cockpit/live_runtime_projection.py`
3. `src/coordination/workcycle_v0.py`
4. `docs/campaigns/workcycle_stabilization_001/state/`
5. output of:
   `python tools/project_workcycle_v0.py`

## TARGET

Determine whether the operator can recover, from structured projection alone:

- campaign identity;
- active horizon;
- T0-T7 postures;
- next pressure;
- latest observed consequence;
- consequence evaluation;
- repair spec/result separation;
- budget state;
- workflow control state;
- whether automatic continuation is enabled;
- whether Reed action is currently required.

Check that the projection itself:
- creates no authority;
- performs no execution;
- advances no campaign/scientific standing;
- does not infer PASS from implementation existence alone.

## ADVERSARIAL CURRENTNESS QUESTIONS

The evaluator must explicitly test:

1. Does "active work item" mean actually active, rather than merely latest completed?
2. Is latest completed work separated from next eligible work?
3. Can result-file existence alone create BOUNDED_PASS?
4. Can malformed, stale, or identity-mismatched consequence/evaluation state create a positive projection?
5. Is real eligibility distinguished from budget-only/partial eligibility when seat, authority, frame, dependency, or hold coordinates are unresolved?
6. Can historical unresolved debt remain visible without being misrepresented as current unresolved load after a later evaluation?
7. Is the current budget honestly labeled as per-wake capacity rather than cumulative campaign budget?
8. Can repository-authored requested control state silently become operative execution control?
9. Are repair specification and repair result kept distinct?
10. Is the Workcycle witness/control surface visibly reachable without scrolling through unrelated inspector content?

Required non-collapses:

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

PARTIAL ELIGIBILITY COORDINATES
!=
REAL ELIGIBILITY

REPO CONTROL REQUEST
!=
LOCAL EXECUTION AUTHORITY

WAKE BUDGET
!=
CUMULATIVE CAMPAIGN BUDGET
```

## OPERATOR-LOCAL CONTROL QUESTIONS

Also pressure the connected left-rail control membrane:

1. Is operator-local control state stored outside the repository?
2. Does repository-requested ON remain non-operative?
3. Does local ENABLE change the operative workflow projection to ON?
4. Does WAKE fail while the workflow is disabled?
5. Does local WAKE create a new wake generation and visible wake request?
6. Do PAUSE and STOP visibly close further local motion?
7. Does ADMIT_ONE fail closed while real eligibility coordinates remain unresolved?
8. Is durable seat identity visible independently of live occupancy?
9. Does a seat's existence remain distinct from occupant binding and execution authority?
10. Does every local control mutation require preview identity + explicit REED confirmation?

Required non-collapses:

```
REPO REQUESTED CONTROL
!=
OPERATIVE LOCAL CONTROL

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
```

## DISPOSITION

Return exactly one:

```
COCKPIT_PROJECTION_MATCHED
COCKPIT_PROJECTION_PARTIAL
COCKPIT_PROJECTION_FRACTURED
COCKPIT_PROJECTION_UNRESOLVED
```

## REQUIRED RETURN

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
AUTHORITY_EFFECT:
EXECUTION_EFFECT:
DISPOSITION:
UNRESOLVED:
STOPPED:
```
