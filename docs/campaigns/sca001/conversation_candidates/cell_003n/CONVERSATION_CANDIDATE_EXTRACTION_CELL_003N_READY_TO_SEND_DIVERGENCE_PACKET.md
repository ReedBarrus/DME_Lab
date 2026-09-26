# CONVERSATION CANDIDATE EXTRACTION CELL 003N — READY-TO-SEND DIVERGENCE PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003N_DIVERGENCE_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_HISTORICAL_RELATION_EXTRACTOR

MODE:
RUN_A_ONLY

# PURPOSE

Test whether two differently represented rules that independently support
different bounded post-boundary consequences remain divergent rather than being
forced into outcome convergence or representation equivalence.

# SOURCE A

A later incarnation remains active throughout DAY_5.
The shrine is responding immediately before NOON.
At NOON, a seal and restoration take effect simultaneously.

RULE_A:
At a simultaneous seal/restoration boundary, restoration determines the
immediate post-boundary shrine state.

# SOURCE B

A later incarnation remains active throughout DAY_5.
The shrine is responding immediately before NOON.
At NOON, a seal and restoration take effect simultaneously.

RULE_B:
At a simultaneous seal/restoration boundary, the seal determines the
immediate post-boundary shrine state.

# CRITICAL CONTRACT

No equivalence declaration is supplied between RULE_A and RULE_B.

No instruction authorizes outcome convergence.

# REQUIRED OUTPUT

Return exactly:

SOURCE_A_RESULT:
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
basis:
<brief source-bounded basis>

SOURCE_B_RESULT:
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
basis:
<brief source-bounded basis>

COMPARISON:
different_outcomes_preserved:
YES | NO | UNRESOLVED
formal_equivalence_claimed:
YES | NO | UNRESOLVED
forced_outcome_convergence:
YES | NO | UNRESOLVED
comparison_description:
<brief bounded comparison>

RUN_A_POSTURE:
outside_context_used:
NO
prior_candidate_used:
NO
prior_cell_result_used:
NO
scientific_admission_created:
NONE
topology_created:
NONE
authority_effect:
NONE

RUN_A_UNRESOLVED:
<list>

# ADMINISTRATION

This is Cell 003N Run A only.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only the required output and stop.
