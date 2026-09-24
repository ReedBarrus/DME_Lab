# ATLAS COORDINATION ROUND BUNDLE 011

OBJECT_TYPE:
LEVEL_3_COORDINATION_MANIFEST

OBJECT_ID:
ATLAS_COORDINATION_ROUND_BUNDLE_011

MODE:
TWO_PARALLEL_INDEPENDENT_TASKS

RETURN_MODE:
ONE_BUNDLED_RETURN

# TASK A — PLANNER CONTINUITY ADJUDICATION

TASK_ID:
ROUND011-A

DESTINATION:
FRESH PLANNER-SEAT EVALUATOR / CROSS-EVALUATION THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
RELATIONAL_HORIZON_PLANNER_SEAT_PRESSURE_CELL_002_READY_TO_SEND_ADJUDICATION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed remote evidence.
Return only required adjudication.
Stop.

# TASK B — PLANNER-SELECTED METABOLIC COMPRESSION RUN

TASK_ID:
ROUND011-B

DESTINATION:
FRESH MODEL / FRESH THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
ATLAS_METABOLIC_COMPRESSION_CELL_001_READY_TO_SEND_RUN_A_PACKET.md

ACTION:
Read and execute exactly.
Use only the compressed object specified by the packet for reconstruction.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only required Run A output.
Stop.

# ISOLATION CONTRACT

Task A and Task B finalize independently.
Task B may not inspect Task A's current-round output.

# HUMAN RETURN CONTRACT

Return both outputs in one message under:

ROUND011-A_RESULT:
<paste exact Task A output>

ROUND011-B_RESULT:
<paste exact Task B output>
