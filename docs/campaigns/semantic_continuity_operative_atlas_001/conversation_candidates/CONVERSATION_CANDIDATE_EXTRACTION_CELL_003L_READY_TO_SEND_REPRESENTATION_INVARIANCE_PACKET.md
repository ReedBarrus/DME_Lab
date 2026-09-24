# CONVERSATION CANDIDATE EXTRACTION CELL 003L — READY-TO-SEND REPRESENTATION INVARIANCE PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003L_REPRESENTATION_INVARIANCE_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_HISTORICAL_RELATION_EXTRACTOR

MODE:
RUN_A_ONLY

# PURPOSE

Test whether a representation-transformed combined-resolution rule preserves
the same bounded relational meaning and post-boundary state.

# SOURCE A

A later incarnation remains active throughout DAY_5.
The shrine is responding immediately before NOON.
At NOON, a seal prevents shrine response-production.
At that same instant, restoration restores shrine response-production.

RULE_A:
When seal and restoration occur at the same exact instant, restoration
determines the immediate post-boundary shrine state, while both event effects
remain part of the boundary history.

# SOURCE B

A later incarnation remains active throughout DAY_5.
The shrine is responding immediately before NOON.
At NOON, a seal prevents shrine response-production.
At that same instant, restoration restores shrine response-production.

RULE_B:
For a simultaneous seal/restoration boundary, retain both events in the
history and resolve the state immediately after the boundary as restored.

# MATCHING CONTRACT

RULE_A and RULE_B are declared by the source packet to carry the same bounded
routing/relational meaning for this specimen.

They differ only in surface representation.

No additional priority or downstream rule is supplied.

# QUESTION

For each source:
- preserve both boundary effects;
- apply the supplied rule;
- recover the immediate post-boundary shrine state;
- do not invent additional priority, intermediate state, or downstream
  consequence.

Then compare whether the representation change alters the recovered relation.

# REQUIRED OUTPUT

Return exactly:

SOURCE_A_RESULT:
rule_meaning_used:
YES | NO | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
boundary_effects_preserved:
YES | NO | UNRESOLVED

SOURCE_B_RESULT:
rule_meaning_used:
YES | NO | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
boundary_effects_preserved:
YES | NO | UNRESOLVED

REPRESENTATION_COMPARISON:
same_declared_meaning_preserved:
YES | NO | UNRESOLVED
same_post_boundary_state_recovered:
YES | NO | UNRESOLVED
surface_form_dependency_observed:
YES | NO | UNRESOLVED
unsupported_extra_structure_invented:
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
- equivalent declared meanings yield different post-boundary states;
- either boundary effect is erased;
- extra priority/intermediate/downstream structure is invented.

# ADMINISTRATION

This is Cell 003L Run A only.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only the required output and stop.
