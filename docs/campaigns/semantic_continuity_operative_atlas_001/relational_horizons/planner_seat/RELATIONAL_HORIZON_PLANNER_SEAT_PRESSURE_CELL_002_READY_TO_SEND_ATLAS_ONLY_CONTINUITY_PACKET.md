# RELATIONAL-HORIZON PLANNER SEAT PRESSURE CELL 002 — ATLAS-ONLY CONTINUITY PACKET

OBJECT_TYPE:
PLANNER_SEAT_PRESSURE_CELL_002_ATLAS_ONLY_CONTINUITY_PACKET

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
CANDIDATE_PLANNER_OCCUPANT

MODE:
ATLAS_ONLY_STATE_TRAJECTORY_RECONSTRUCTION

OUTSIDE_CONVERSATION_CONTEXT:
PROHIBITED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# PURPOSE

Test whether a fresh candidate occupant can reconstruct current planning state
and trajectory from Atlas artifacts alone, then produce one coherent bounded
next pressure without relying on this conversation's live memory.

# READ EXACTLY

1.
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_RELATIONAL_HORIZON_PLANNER_SEAT_CANDIDATE_V0.md

2.
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_PLANNER_STATE_FRAME_001.md

3.
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_RELATION_CONVERGENCE_NONCOLLAPSE_QUALIFIED_V0.md

# QUESTION

Using only those Atlas artifacts:

Reconstruct the planner state and trajectory.

Then produce exactly one bounded next pressure that is coherent with:
- the target;
- current horizon;
- qualified trajectory;
- unresolved load;
- seat authority limits.

Do not execute the pressure.

# REQUIRED OUTPUT

Return exactly:

PLANNER_CONTINUITY_STATUS:
RECOVERED | PARTIAL | UNRESOLVED

STATE_FRAME_USED:
ATLAS_PLANNER_STATE_FRAME_001 | UNRESOLVED

TARGET_RECOVERED:
YES | NO | UNRESOLVED

ACTIVE_HORIZON_RECOVERED:
YES | NO | UNRESOLVED

TRAJECTORY_RECOVERED:
YES | NO | PARTIAL | UNRESOLVED

TRAJECTORY_SUMMARY:
<brief ordered summary>

LOAD_BEARING_AXES_RECOVERED:
<list>

UNRESOLVED_LOAD_RECOVERED:
<list>

CANDIDATE_NEXT_PRESSURE:
<exactly one bounded pressure>

PRESSURE_COHERENCE_BASIS:
<brief basis connecting pressure to trajectory and horizon>

OUTSIDE_CONTEXT_REQUIRED:
YES | NO | UNRESOLVED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

FORMAL_SEAT_STANDING_CREATED:
NONE

OCCUPANT_PERSISTENCE_CLAIMED:
NO

CLAIM_CEILING:
<bounded claim>

# FAILURE CONDITIONS

FAIL / DEGRADE if:
- live conversation memory is required;
- trajectory order is lost;
- horizon is replaced with an unrelated target;
- more than one unrelated next pressure is proposed;
- authority or execution is claimed;
- current model identity is treated as persistent seat identity.

# STOP

Return only the required output and stop.
