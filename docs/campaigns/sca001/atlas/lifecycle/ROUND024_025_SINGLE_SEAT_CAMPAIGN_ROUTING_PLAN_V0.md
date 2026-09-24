# ROUND 024–025 — SINGLE-SEAT CAMPAIGN ROUTING PLAN V0

OBJECT_TYPE:
CAMPAIGN_ROUTING_PLAN

STANDING:
OPERATIVE_WORKFLOW_PLAN

SOURCE_BRANCH:
draci-v0-candidate-basis

SOURCE_HEAD_AT_PLAN:
35bbb66c8e44bc3728358fb0825ab5d59348d342

# ACTIVE HORIZON

STABILIZE_SINGLE_SEAT_DYNAMICS_ON_ATLAS

# CURRENT LOAD-BEARING SEQUENCE

1. ROUND 024
   Independently adjudicate the Round 022 ambiguous-outcome / retry witness.

2. CONDITIONAL REPAIR
   If Round 024 rejects or holds attempt-identity conservation or retry gating,
   repair the smallest semantic seam and rerun only that seam.

3. ROUND 025
   Pressure authority consumption as an orthogonal coordinate to seat lifecycle
   state.

4. LATER, ONLY AFTER THE ABOVE SURVIVE
   - failure / hold orthogonality
   - settlement routing
   - pause / resume / stop
   - budget plane
   - whole single-seat loop

# ROUND 024 ROUTING

PACKET:
bridge/prompts/ROUND024_AMBIGUOUS_INVOCATION_OUTCOME_INDEPENDENT_ADJUDICATION_READY_TO_SEND.md

DESTINATION:
fresh independent lifecycle evaluator thread

DO NOT SEND:
docs/campaigns/sca001/atlas/lifecycle/ROUND024_AMBIGUOUS_INVOCATION_OUTCOME_EVALUATOR_KEY.md

RETURN:
only the required adjudication output

# ROUND 024 DECISION GATE

ADVANCE_DIRECTLY_TO_ROUND_025 only if the adjudication preserves all of:

- REQUEST_ID != INVOCATION_ATTEMPT_ID
- ATTEMPT_1 identity is conserved despite outcome ambiguity
- INVOCATION_OUTCOME_UNRESOLVED does not imply nonexecution
- automatic replay is denied
- an operator proposal to retry is not itself a retry warrant
- retry remains blocked until an explicit retry warrant exists
- any later retry uses a fresh attempt identity
- predecessor linkage is preserved
- predecessor authorization is not reused
- invocation consumption remains monotonic
- no scientific standing or authority expansion is created

If either ATTEMPT_1_IDENTITY or RETRY_ALLOWED_FROM_CURRENT_STATE fails this gate,
do not broaden the lifecycle. Create one minimal repaired pressure and rerun it.

# ROUND 025 ROUTING

PACKET:
bridge/prompts/ROUND025_AUTHORITY_CONSUMPTION_ORTHOGONALITY_READY_TO_SEND.md

PRIMARY SOURCE ACTOR:
LM Studio bounded source model after the Round 024 gate clears.

PREFERRED INITIAL MODEL:
qwen/qwen3-coder-30b

RATIONALE:
Keep the source consequence deterministic and tool-free; use a separate fresh
thread for independent adjudication afterward.

ROUND 025 is prepared but MUST NOT be treated as qualified or executed merely
because the packet exists.

# CAMPAIGN LAW

Do not expand the seat into a Cartesian-product state machine.

Track at least these as separable coordinates:

SEAT_LIFECYCLE
×
AUTHORITY_LIFECYCLE
×
BUDGET_LIFECYCLE
×
SCIENTIFIC_STANDING
×
FAILURE_OR_HOLD_POSTURE

A transition in one coordinate does not silently imply a transition in another.

# CLAIM CEILING

This routing plan controls campaign order only.

It creates no scientific admission, authority, execution permission, or
qualification.
