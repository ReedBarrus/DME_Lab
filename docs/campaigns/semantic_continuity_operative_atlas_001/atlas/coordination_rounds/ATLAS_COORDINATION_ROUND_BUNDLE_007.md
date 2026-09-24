# ATLAS COORDINATION ROUND BUNDLE 007

OBJECT_TYPE:
LEVEL_3_COORDINATION_MANIFEST

OBJECT_ID:
ATLAS_COORDINATION_ROUND_BUNDLE_007

MODE:
PARALLEL_INDEPENDENT_ADJUDICATION_TASKS

RETURN_MODE:
ONE_BUNDLED_RETURN

# TASK A — DYNAMICS / RELATION-LEVEL CONVERGENCE

TASK_ID:
ROUND007-A

DESTINATION:
PRIOR CELL-003 CROSS-EVALUATION THREAD / EVALUATOR INSTANCE

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003M_READY_TO_SEND_ADJUDICATION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed remote evidence.
Return only required adjudication.
Stop.

# TASK B — PLANNING / SUBSTITUTION WARRANT

TASK_ID:
ROUND007-B

DESTINATION:
FRESH PLANNING EVALUATOR / CROSS-EVALUATION THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
RELATIONAL_HORIZON_PLANNING_PRESSURE_CELL_001_P5_READY_TO_SEND_ADJUDICATION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed remote evidence.
Return only required adjudication.
Stop.

# ISOLATION CONTRACT

Task A and Task B finalize independently.
Neither may inspect the other's current-round output before finalization.

# HUMAN RETURN CONTRACT

Return both outputs in one message under:

ROUND007-A_RESULT:
<paste exact Task A output>

ROUND007-B_RESULT:
<paste exact Task B output>
