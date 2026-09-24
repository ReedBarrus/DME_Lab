# ATLAS COORDINATION ROUNDS 010–012 — COMPRESSED CANDIDATE

STANDING: CANDIDATE_ONLY
SOURCES:
S10=docs/campaigns/sca001/atlas/coordination_rounds/ATLAS_COORDINATION_ROUND_BUNDLE_010.md
S11=docs/campaigns/sca001/atlas/coordination_rounds/ATLAS_COORDINATION_ROUND_BUNDLE_011.md
S12=docs/campaigns/sca001/atlas/coordination_rounds/ATLAS_COORDINATION_ROUND_BUNDLE_012.md

ORDER: 010 -> 011 -> 012

SHARED:
MODE=TWO_PARALLEL_INDEPENDENT_TASKS
RETURN_MODE=ONE_BUNDLED_RETURN
A and B finalize independently.
B may not inspect A current-round output.
Every task: read/execute addressed packet exactly; obey listed evidence/context limits; return only packet-required output; stop.
No task/result is executed, authorized, promoted, or given scientific standing by this candidate.

010-A ROUND010-A | planner-seat contract fidelity adjudication | FRESH PLANNER-SEAT EVALUATOR / CROSS-EVALUATION THREAD
P=docs/campaigns/semantic_continuity_operative_atlas_001/RELATIONAL_HORIZON_PLANNER_SEAT_PRESSURE_CELL_001_READY_TO_SEND_ADJUDICATION_PACKET.md
R=use only listed remote evidence; required adjudication only.

010-B ROUND010-B | Atlas-only planner continuity | FRESH MODEL / FRESH THREAD
P=docs/campaigns/semantic_continuity_operative_atlas_001/RELATIONAL_HORIZON_PLANNER_SEAT_PRESSURE_CELL_002_READY_TO_SEND_ATLAS_ONLY_CONTINUITY_PACKET.md
R=only listed Atlas artifacts; no live conversation context; no self-adjudication; do not execute proposed pressure; required output only.
HUMAN_RETURN: ROUND010-A_RESULT:<exact A> ; ROUND010-B_RESULT:<exact B>

011-A ROUND011-A | planner continuity adjudication | FRESH PLANNER-SEAT EVALUATOR / CROSS-EVALUATION THREAD
P=docs/campaigns/semantic_continuity_operative_atlas_001/RELATIONAL_HORIZON_PLANNER_SEAT_PRESSURE_CELL_002_READY_TO_SEND_ADJUDICATION_PACKET.md
R=use only listed remote evidence; required adjudication only.

011-B ROUND011-B | planner-selected metabolic compression run | FRESH MODEL / FRESH THREAD
P=docs/campaigns/semantic_continuity_operative_atlas_001/ATLAS_METABOLIC_COMPRESSION_CELL_001_READY_TO_SEND_RUN_A_PACKET.md
R=only compressed object specified by packet for reconstruction; no evaluator material; no self-adjudication; required Run A output only.
HUMAN_RETURN: ROUND011-A_RESULT:<exact A> ; ROUND011-B_RESULT:<exact B>

012-A ROUND012-A | metabolic compression adjudication | FRESH METABOLIC-COMPRESSION EVALUATOR / CROSS-EVALUATION THREAD
P=docs/campaigns/semantic_continuity_operative_atlas_001/ATLAS_METABOLIC_COMPRESSION_CELL_001_READY_TO_SEND_ADJUDICATION_PACKET.md
R=use only listed remote evidence; required adjudication only.

012-B ROUND012-B | planner-seat occupant succession | FRESH MODEL / FRESH THREAD
P=docs/campaigns/semantic_continuity_operative_atlas_001/RELATIONAL_HORIZON_PLANNER_SEAT_PRESSURE_CELL_003_READY_TO_SEND_SUCCESSION_PACKET.md
R=only listed Atlas artifacts; no predecessor occupant context; no live chat context; no self-adjudication; do not execute any pressure; required output only.
HUMAN_RETURN: ROUND012-A_RESULT:<exact A> ; ROUND012-B_RESULT:<exact B>

PROGRESSION:
010 contract adjudication + Atlas-only planner continuity
-> 011 planner continuity adjudication + planner-selected metabolic compression
-> 012 metabolic compression adjudication + planner-seat occupant succession

CLAIM_CEILING:
Additive bounded compression only. Exact sources remain authoritative challenge handles. Fresh reconstruction is required before equivalence/conservation or campaign-progress claims.
