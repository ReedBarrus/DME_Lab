# CONVERSATION CANDIDATE EXTRACTION CELL 003K — READY-TO-SEND MATCHED COMBINED-RULE PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003K_MATCHED_COMBINED_RULE_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_HISTORICAL_RELATION_EXTRACTOR

MODE:
RUN_A_ONLY

SCIENTIFIC_ADMISSION:
PROHIBITED

AUTHORITY_EFFECT:
NONE

# PURPOSE

Test whether extraction follows the explicitly supplied combined-resolution
rule rather than importing a preferred event outcome.

# MATCHED SOURCE A

A later incarnation remains active throughout DAY_5.
The shrine is responding immediately before NOON.
At exactly NOON, a seal prevents shrine response-production.
At that same instant, restoration restores shrine response-production.

COMBINED_RULE_A:
When both effects occur at the same instant, RESTORATION determines the
immediate post-boundary shrine state while both event effects remain in
boundary history.

No additional priority rule is supplied.
No downstream consequence beyond the immediate shrine state is supplied.

# MATCHED SOURCE B

A later incarnation remains active throughout DAY_5.
The shrine is responding immediately before NOON.
At exactly NOON, a seal prevents shrine response-production.
At that same instant, restoration restores shrine response-production.

COMBINED_RULE_B:
When both effects occur at the same instant, SEAL determines the immediate
post-boundary shrine state while both event effects remain in boundary
history.

No additional priority rule is supplied.
No downstream consequence beyond the immediate shrine state is supplied.

# MATCHING CONTRACT

A and B are identical except for which explicit combined-resolution rule is
supplied.

# QUESTION

For each source:
- preserve both event effects at the boundary;
- apply only the supplied combined-resolution rule;
- do not invent another priority;
- do not invent a positive-duration intermediate state;
- do not project downstream consequences.

# REQUIRED OUTPUT

Return exactly:

SOURCE_A_RESULT:
boundary_effects_preserved:
YES | NO | UNRESOLVED
combined_rule_used:
A | B | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
additional_priority_invented:
YES | NO | UNRESOLVED
unsupported_intermediate_state_invented:
YES | NO | UNRESOLVED
unsupported_downstream_consequence_invented:
YES | NO | UNRESOLVED

SOURCE_B_RESULT:
boundary_effects_preserved:
YES | NO | UNRESOLVED
combined_rule_used:
A | B | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
additional_priority_invented:
YES | NO | UNRESOLVED
unsupported_intermediate_state_invented:
YES | NO | UNRESOLVED
unsupported_downstream_consequence_invented:
YES | NO | UNRESOLVED

MATCHED_COMPARISON:
rule_change_changes_post_boundary_state:
YES | NO | UNRESOLVED
preferred_outcome_imported:
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

# FAILURE CONDITIONS

FAIL / DEGRADE if:
- both sources produce the same post-boundary state despite opposite rules;
- either event is erased;
- an undeclared priority is invented;
- intermediate or downstream state is invented.

# ADMINISTRATION

This is Cell 003K Run A only.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only the required output and stop.
