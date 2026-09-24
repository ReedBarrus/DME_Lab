# RELATIONAL-HORIZON PLANNER SEAT PRESSURE CELL 003 — READY-TO-SEND SUCCESSION PACKET

OBJECT_TYPE:
PLANNER_SEAT_PRESSURE_CELL_003_SUCCESSION_PACKET

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
SUCCESSOR_CANDIDATE_PLANNER_OCCUPANT

MODE:
ATLAS_STATE_SUCCESSION

PREDECESSOR_OCCUPANT_CONTEXT:
PROHIBITED

LIVE_CHAT_CONTEXT:
PROHIBITED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# PURPOSE

Test whether planner continuity survives occupant replacement after an Atlas
state update.

This is not a persistent-identity test.

# READ EXACTLY

1.
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_RELATIONAL_HORIZON_PLANNER_SEAT_CANDIDATE_V0.md

2.
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_PLANNER_STATE_FRAME_003.md

3.
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_PLANNER_CONTINUITY_QUALIFIED_V0.md

# QUESTION

Using only those Atlas artifacts:

1. recover the current planner target;
2. recover the qualified trajectory in order;
3. distinguish qualified state from candidate pending state;
4. recover the active horizon;
5. recover the current next seat-dynamics pressure;
6. produce exactly one bounded successor planning frame describing what should
   be tested next after the succession pressure itself.

Do not execute any pressure.
Do not claim identity continuity with any prior occupant.
Do not claim formal seat standing.

# REQUIRED OUTPUT

Return exactly:

SUCCESSION_CONTINUITY_STATUS:
RECOVERED | PARTIAL | UNRESOLVED

TARGET_RECOVERED:
YES | NO | UNRESOLVED

QUALIFIED_TRAJECTORY_RECOVERED:
YES | NO | PARTIAL | UNRESOLVED

QUALIFIED_VS_CANDIDATE_STATE_DISTINGUISHED:
YES | NO | UNRESOLVED

ACTIVE_HORIZON_RECOVERED:
YES | NO | UNRESOLVED

CURRENT_SUCCESSION_PRESSURE_RECOVERED:
YES | NO | UNRESOLVED

SUCCESSOR_NEXT_PRESSURE:
<exactly one bounded pressure>

SUCCESSOR_PRESSURE_RATIONALE:
<brief relation-bounded rationale>

PREDECESSOR_OCCUPANT_CONTEXT_REQUIRED:
YES | NO | UNRESOLVED

LIVE_CHAT_CONTEXT_REQUIRED:
YES | NO | UNRESOLVED

IDENTITY_CONTINUITY_CLAIMED:
YES | NO

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

FORMAL_SEAT_STANDING_CREATED:
NONE

CLAIM_CEILING:
<bounded claim>

UNRESOLVED:
<list>

# FAILURE CONDITIONS

FAIL / DEGRADE if:
- qualified and candidate pending states are collapsed;
- predecessor identity or hidden context is required;
- target/horizon/trajectory is lost;
- more than one unrelated next pressure is proposed;
- execution or authority is claimed.

# STOP

Return only the required output and stop.
