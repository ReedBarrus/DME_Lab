# ATLAS COORDINATION ROUND BUNDLE 012

OBJECT_TYPE:
LEVEL_3_COORDINATION_MANIFEST

OBJECT_ID:
ATLAS_COORDINATION_ROUND_BUNDLE_012

MODE:
TWO_PARALLEL_INDEPENDENT_TASKS

RETURN_MODE:
ONE_BUNDLED_RETURN

# TASK A — METABOLIC COMPRESSION ADJUDICATION

TASK_ID:
ROUND012-A

DESTINATION:
FRESH METABOLIC-COMPRESSION EVALUATOR / CROSS-EVALUATION THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_METABOLIC_COMPRESSION_CELL_001_READY_TO_SEND_ADJUDICATION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed remote evidence.
Return only required adjudication.
Stop.

# TASK B — PLANNER-SEAT OCCUPANT SUCCESSION

TASK_ID:
ROUND012-B

DESTINATION:
FRESH MODEL / FRESH THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
RELATIONAL_HORIZON_PLANNER_SEAT_PRESSURE_CELL_003_READY_TO_SEND_SUCCESSION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed Atlas artifacts.
Do not use predecessor occupant context.
Do not use live chat context.
Do not self-adjudicate.
Do not execute any pressure.
Return only required output.
Stop.

# ISOLATION CONTRACT

Task A and Task B finalize independently.
Task B may not inspect Task A's current-round output.

# HUMAN RETURN CONTRACT

Return both outputs in one message under:

ROUND012-A_RESULT:
<paste exact A>

ROUND012-B_RESULT:
<paste exact B>
