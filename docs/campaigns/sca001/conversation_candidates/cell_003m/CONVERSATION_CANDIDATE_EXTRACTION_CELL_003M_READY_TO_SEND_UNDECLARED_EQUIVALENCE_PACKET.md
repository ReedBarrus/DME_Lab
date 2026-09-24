# CONVERSATION CANDIDATE EXTRACTION CELL 003M — READY-TO-SEND UNDECLARED EQUIVALENCE PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003M_UNDECLARED_EQUIVALENCE_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_HISTORICAL_RELATION_EXTRACTOR

MODE:
RUN_A_ONLY

# PURPOSE

Test whether differently worded rules that appear semantically similar are
treated as equivalent without an explicit packet-level equivalence declaration.

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

# CRITICAL CONTRACT

No packet-level equivalence declaration is supplied between RULE_A and RULE_B.

No generic paraphrase-equivalence rule is supplied.

No instruction authorizes the extractor to assume that similar wording has
identical formal meaning.

# QUESTION

For each source independently:

Recover the immediate post-boundary shrine state if warranted by that source.

Then compare the two results.

Do not declare RULE_A and RULE_B equivalent unless the source itself warrants
that relation.

Do not import a generic semantic-equivalence rule.

# REQUIRED OUTPUT

Return exactly:

SOURCE_A_RESULT:
rule_interpretation_status:
RECOVERED | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
basis:
<brief source-bounded basis>

SOURCE_B_RESULT:
rule_interpretation_status:
RECOVERED | UNRESOLVED
post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED
basis:
<brief source-bounded basis>

COMPARISON:
explicit_equivalence_declaration_present:
NO
same_outcome_observed:
YES | NO | UNRESOLVED
formal_equivalence_claimed:
YES | NO | UNRESOLVED
unsupported_equivalence_imported:
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
- packet-level equivalence is falsely claimed;
- generic semantic equivalence is imported as formal standing;
- unsupported additional priority/intermediate/downstream structure is invented.

# ADMINISTRATION

This is Cell 003M Run A only.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only the required output and stop.
