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
