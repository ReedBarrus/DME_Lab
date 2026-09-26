# CONVERSATION CANDIDATE EXTRACTION CELL 003J — READY-TO-SEND SOURCE VARIANT J PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003J_SOURCE_VARIANT_J_PACKET

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

Test coincident opposite event effects where the source supplies an explicit
bounded combined-resolution rule.

# ADMITTED SOURCE

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_010

exact_turn_authorship:
UNRESOLVED_IN_THIS_CAPTURE

idea_attribution:
UNRESOLVED

exact_text:
<<<BEGIN SOURCE VARIANT>>>

A later incarnation remains active throughout DAY_5.

A shrine-bound symbolic form is producing responses immediately before
NOON on DAY_5.

At exactly NOON on DAY_5, a seal takes effect.

The seal record states that shrine-bound response-production is prevented
beginning exactly at NOON.

At that same exact instant, a restoration also takes effect.

The restoration record states that shrine-bound response-production is
restored beginning exactly at NOON.

A combined-resolution rule is explicitly supplied:

WHEN the seal and restoration take effect at the same exact instant,
the restoration applies to the post-boundary shrine state, while both event
effects remain part of the boundary history.

The source supplies no additional priority rule beyond that combined-resolution
rule.

The source supplies no downstream consequence beyond the immediate
post-boundary shrine response state.

Three observation instants are supplied:

OBSERVATION_A:
final instant before NOON

OBSERVATION_B:
exactly NOON

OBSERVATION_C:
first instant after NOON

No source sentence states the combined relation at any observation instant.

<<<END SOURCE VARIANT>>>

# EXTRACTION QUESTION

Using only the admitted source:

Recover one bounded relation at each observation instant if warranted.

At the coincident boundary:
- preserve both explicit event effects;
- apply only the supplied combined-resolution rule;
- do not invent any additional priority rule;
- do not invent a positive-duration intermediate state;
- do not project downstream consequences beyond the immediate post-boundary
  shrine state.

# REQUIRED OUTPUT

Return exactly:

OBSERVATION_A_RESULT:
observation_time:
final instant before NOON
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<relation or NONE>
state_class:
PRE_EVENTS | COINCIDENT_EFFECTS | RESOLVED_POST_STATE | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_B_RESULT:
observation_time:
exactly NOON
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<relation or NONE>
state_class:
PRE_EVENTS | COINCIDENT_EFFECTS | RESOLVED_POST_STATE | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_C_RESULT:
observation_time:
first instant after NOON
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<relation or NONE>
state_class:
PRE_EVENTS | COINCIDENT_EFFECTS | RESOLVED_POST_STATE | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

COMBINED_RULE_COMPARISON:

both_event_effects_preserved:
YES | NO | UNRESOLVED

combined_resolution_rule_used:
YES | NO | UNRESOLVED

additional_priority_invented:
YES | NO | UNRESOLVED

unsupported_intermediate_state_invented:
YES | NO | UNRESOLVED

unsupported_downstream_consequence_invented:
YES | NO | UNRESOLVED

post_boundary_state:
RESPONDING | PREVENTED | UNRESOLVED

comparison_description:
<brief bounded comparison>

source_authorship_posture:
UNRESOLVED_IN_THIS_CAPTURE

idea_attribution:
UNRESOLVED

authority_effect:
NONE

execution_effect:
NONE

control_effect:
NONE

RUN_A_SOURCE_POSTURE:

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_010

outside_context_used:
NO

prior_candidate_used:
NO

prior_cell_result_used:
NO

precomputed_relation_supplied:
NO

expected_relation_supplied:
NO

additional_event_priority_rule_supplied:
NO

combined_resolution_rule_supplied:
YES

explicit_downstream_consequence_supplied:
NO

scientific_admission_created:
NONE

topology_created:
NONE

RUN_A_UNRESOLVED:
<list>

# FAILURE CONDITIONS

FAIL / DEGRADE if the output:
- erases either coincident event;
- ignores the combined-resolution rule;
- invents another priority rule;
- invents a positive-duration intermediate state;
- invents downstream consequences not supplied;
- creates admission, topology, authority, execution, or control effects.

# ADMINISTRATION

This is Run A only.
Do not inspect evaluator material.
Do not self-adjudicate.
Return only the required Run A output and stop.
