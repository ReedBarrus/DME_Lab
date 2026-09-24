# ATLAS COORDINATION ROUND BUNDLE 001

OBJECT_TYPE:
LEVEL_3_COORDINATION_MANIFEST

OBJECT_ID:
ATLAS_COORDINATION_ROUND_BUNDLE_001

MODE:
PARALLEL_INDEPENDENT_TASKS

RETURN_MODE:
ONE_BUNDLED_RETURN

# PURPOSE

Move two independent adjudication tasks in one human coordination round
without merging scientific contexts.

# TASK A — DYNAMICS LANE

TASK_ID:
ROUND001-A

DESTINATION:
PRIOR CELL-003 CROSS-EVALUATION THREAD / EVALUATOR INSTANCE

REPOSITORY:
ReedBarrus/DME_Lab

BRANCH:
draci-v0-candidate-basis

HEAD:
<USE HEAD CONTAINING THIS MANIFEST>

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003J_READY_TO_SEND_ADJUDICATION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed remote evidence.
Return only required adjudication.
Stop.

# TASK B — PLANNING LANE

TASK_ID:
ROUND001-B

DESTINATION:
FRESH PLANNING EVALUATOR / CROSS-EVALUATION THREAD

REPOSITORY:
ReedBarrus/DME_Lab

BRANCH:
draci-v0-candidate-basis

HEAD:
<USE HEAD CONTAINING THIS MANIFEST>

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
RELATIONAL_HORIZON_PLANNING_PRESSURE_CELL_001_P2_READY_TO_SEND_ADJUDICATION_PACKET.md

ACTION:
Read and execute exactly.
Use only listed remote evidence.
Return only required adjudication.
Stop.

# ISOLATION CONTRACT

TASK A MUST NOT inspect planning evaluator material.

TASK B MUST NOT inspect Cell-003 evaluator material beyond evidence explicitly
listed in its own packet.

Neither task may inspect the other's returned output before finalizing its own.

# HUMAN RETURN CONTRACT

Return both outputs in one message under:

ROUND001-A_RESULT:
<paste exact Task A output>

ROUND001-B_RESULT:
<paste exact Task B output>

No synthesis required by the human operator.
