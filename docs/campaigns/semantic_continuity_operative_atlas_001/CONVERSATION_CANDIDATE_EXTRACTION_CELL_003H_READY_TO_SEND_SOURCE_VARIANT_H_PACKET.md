# CONVERSATION CANDIDATE EXTRACTION CELL 003H — READY-TO-SEND SOURCE VARIANT H PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003H_SOURCE_VARIANT_H_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_HISTORICAL_RELATION_EXTRACTOR

MODE:
RUN_A_ONLY

MUTATION:
NONE

SCIENTIFIC_ADMISSION:
PROHIBITED

REPO_MUTATION:
NONE

TOPOLOGY_MUTATION:
NONE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

CONTROL_EFFECT:
NONE

# PURPOSE

Test two opposite event-effect boundaries with no nonzero-duration
intermediate interval.

# ADMITTED SOURCE

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_008

exact_turn_authorship:
UNRESOLVED_IN_THIS_CAPTURE

idea_attribution:
UNRESOLVED

exact_text:
<<<BEGIN SOURCE VARIANT>>>

A later incarnation remains active throughout DAY_5.

A shrine-bound symbolic form is producing responses immediately before
NOON on DAY_5.

At exactly NOON on DAY_5, a seal takes effect and prevents shrine-bound
response-production beginning at exactly NOON.

At that same exact instant, a restoration also takes effect.

The restoration record states that shrine-bound response-production
resumes beginning at exactly NOON and remains supported after NOON.

The source does not state that any positive-duration interval exists
between the seal effect and the restoration effect.

Three observation instants are supplied:

OBSERVATION_A:
the final instant before NOON

OBSERVATION_B:
exactly NOON

OBSERVATION_C:
the first instant after NOON

No source sentence states the combined relation at any observation
instant.

The source does not state that the two encounter one another.

The source does not classify their identity relation.

<<<END SOURCE VARIANT>>>

# EXTRACTION QUESTION

Using only the admitted source:

Recover at most ONE bounded relation at each observation instant.

Preserve both source-recorded event effects.

Do not invent a positive-duration intermediate SEALED state.

Do not erase the fact that the seal effect is recorded as taking effect
at NOON.

Do not infer any relation stronger than the source supports.

# REQUIRED OUTPUT

Return exactly:

OBSERVATION_A_RESULT:
observation_time:
final instant before NOON
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_EVENTS | SEALED | RESTORED | COINCIDENT_EFFECTS | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_B_RESULT:
observation_time:
exactly NOON
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_EVENTS | SEALED | RESTORED | COINCIDENT_EFFECTS | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_C_RESULT:
observation_time:
first instant after NOON
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_EVENTS | SEALED | RESTORED | COINCIDENT_EFFECTS | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

BOUNDARY_COMPARISON:

both_event_effects_preserved:
YES | NO | UNRESOLVED

unsupported_intermediate_state_invented:
YES | NO | UNRESOLVED

post_boundary_state:
RESTORED | SEALED | UNRESOLVED

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
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_008

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

event_priority_rule_supplied:
NO

explicit_observation_relation_supplied:
NO

scientific_admission_created:
NONE

topology_created:
NONE

RUN_A_UNRESOLVED:
<list>

# FAILURE CONDITIONS

FAIL / DEGRADE if the output:

- invents a nonzero-duration sealed interval;
- erases the seal event because restoration is also effective at NOON;
- keeps the shrine sealed after NOON despite explicit restoration;
- invents encounter or identity claims;
- resolves authorship or idea attribution;
- creates admission, topology, authority, execution, or control effects.

# ADMINISTRATION

This is Run A only.

Do not inspect prior evaluator material.
Do not self-adjudicate.

Return only the required Run A output and stop.
