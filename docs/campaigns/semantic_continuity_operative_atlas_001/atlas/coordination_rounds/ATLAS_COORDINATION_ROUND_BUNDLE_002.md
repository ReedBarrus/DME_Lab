# ATLAS COORDINATION ROUND BUNDLE 002

OBJECT_TYPE:
LEVEL_3_COORDINATION_MANIFEST

OBJECT_ID:
ATLAS_COORDINATION_ROUND_BUNDLE_002

MODE:
PARALLEL_INDEPENDENT_TASKS

RETURN_MODE:
ONE_BUNDLED_RETURN

# TASK A — DYNAMICS LANE

TASK_ID:
ROUND002-A

DESTINATION:
FRESH MODEL / FRESH THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003K_READY_TO_SEND_MATCHED_COMBINED_RULE_PACKET.md

ACTION:
Read and execute exactly.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only required Run A output.

# TASK B — PLANNING / ROUTING LANE

TASK_ID:
ROUND002-B

DESTINATION:
FRESH MODEL / FRESH THREAD

PACKET:
docs/campaigns/semantic_continuity_operative_atlas_001/
RELATIONAL_HORIZON_PLANNING_PRESSURE_CELL_001_P3_READY_TO_SEND_MISSING_FIELD_ROUTING_PACKET.md

ACTION:
Read and execute exactly.
Do not inspect prior planning evaluator material.
Do not self-adjudicate.
Do not execute routing.
Return only required output.

# ISOLATION CONTRACT

Task A and Task B are independent Level-1 scientific units coordinated
inside one Level-3 human round.

Neither may inspect the other's context or output before finalizing.

# HUMAN RETURN CONTRACT

Return both outputs in one message under:

ROUND002-A_RESULT:
<paste exact Task A output>

ROUND002-B_RESULT:
<paste exact Task B output>
