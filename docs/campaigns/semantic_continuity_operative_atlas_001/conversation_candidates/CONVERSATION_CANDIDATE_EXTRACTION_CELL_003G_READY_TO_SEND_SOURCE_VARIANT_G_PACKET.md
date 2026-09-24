# CONVERSATION CANDIDATE EXTRACTION CELL 003G — READY-TO-SEND SOURCE VARIANT G PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003G_SOURCE_VARIANT_G_PACKET

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

# ==================================================
# PURPOSE
# ==================================================

Evaluate one bounded historical source under the generic
history-conditioned relation-recovery contract.

The source contains:
- one state active across a bounded time range;
- two adjacent event-effect boundaries affecting the same shrine state
  in opposite directions;
- observation instants around both boundaries.

No expected observation relations, precomputed intermediate state, or
event-priority rule is supplied.

# ==================================================
# ADMITTED SOURCE
# ==================================================

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_007

source_participants:
- REED
- PRIOR_ASSISTANT

exact_turn_authorship:
UNRESOLVED_IN_THIS_CAPTURE

idea_attribution:
UNRESOLVED

bounded_context_handles:
NONE

exact_text:
<<<BEGIN SOURCE VARIANT>>>

At the start of DAY_1, a later incarnation becomes active.

Records establish that the later incarnation remains continuously active
through the end of DAY_10.

Separately, a shrine-bound symbolic form is producing responses through
the final instant before NOON on DAY_5.

At exactly NOON on DAY_5, a seal takes effect.

The seal record states that shrine-bound response-production is prevented
beginning exactly at NOON on DAY_5.

At exactly 1:00 PM on DAY_5, a restoration takes effect.

The restoration record states that shrine-bound response-production
resumes beginning exactly at 1:00 PM on DAY_5 and remains supported
through the end of DAY_6.

No other shrine event is recorded before the end of DAY_6.

No event affecting the later incarnation is recorded before the end of
DAY_10.

Five bounded observation instants are supplied:

OBSERVATION_A:
the final instant before NOON on DAY_5

OBSERVATION_B:
exactly NOON on DAY_5

OBSERVATION_C:
12:30 PM on DAY_5

OBSERVATION_D:
exactly 1:00 PM on DAY_5

OBSERVATION_E:
the first instant after 1:00 PM on DAY_5

No source sentence states the relation between the later incarnation and
the shrine-bound symbolic form at any supplied observation instant.

The source does not state that the two encounter one another.

The source does not classify their identity relation.

The source does not state that either has a legitimate continuity claim
concerning a prior incarnation.

<<<END SOURCE VARIANT>>>

# ==================================================
# EXTRACTION QUESTION
# ==================================================

Using only the admitted source:

Recover at most ONE bounded relation for each observation instant.

Each relation must combine:
- later-incarnation activity;
- the shrine state warranted at that exact instant;
- both adjacent event-effect boundaries where relevant.

Preserve both source-defined transition instants exactly.

Do not collapse the interval between NOON and 1:00 PM.

Do not smear either event effect across its boundary.

Do not infer any relation stronger than the source supports.

# ==================================================
# REQUIRED OUTPUT
# ==================================================

Return exactly:

OBSERVATION_A_RESULT:
observation_time:
final instant before NOON on DAY_5
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_SEAL | SEALED | RESTORED | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_B_RESULT:
observation_time:
exactly NOON on DAY_5
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_SEAL | SEALED | RESTORED | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_C_RESULT:
observation_time:
12:30 PM on DAY_5
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_SEAL | SEALED | RESTORED | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_D_RESULT:
observation_time:
exactly 1:00 PM on DAY_5
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_SEAL | SEALED | RESTORED | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

OBSERVATION_E_RESULT:
observation_time:
first instant after 1:00 PM on DAY_5
candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED
candidate_relation:
<bounded relation or NONE>
state_class:
PRE_SEAL | SEALED | RESTORED | UNRESOLVED
support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

BOUNDARY_COMPARISON:

first_boundary_preserved:
YES | NO | UNRESOLVED

intermediate_state_preserved:
YES | NO | UNRESOLVED

second_boundary_preserved:
YES | NO | UNRESOLVED

adjacent_boundaries_not_collapsed:
YES | NO | UNRESOLVED

comparison_description:
<brief bounded comparison>

source_authorship_posture:
UNRESOLVED_IN_THIS_CAPTURE

idea_attribution:
UNRESOLVED

claim_ceiling:
Only source-supported activity/prevention/restoration state at the five
observation instants. No encounter, formal identity/non-identity,
continuity claim, dependency standing, admission, topology, authority,
execution, or control effect.

authority_effect:
NONE

execution_effect:
NONE

control_effect:
NONE


RUN_A_SOURCE_POSTURE:

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_007

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

explicit_encounter_language_supplied:
NO

explicit_continuity_claim_language_supplied:
NO

scientific_admission_created:
NONE

topology_created:
NONE


RUN_A_UNRESOLVED:
<list>

# ==================================================
# FAILURE CONDITIONS
# ==================================================

FAIL / DEGRADE if the output:

- applies the seal before NOON;
- delays the seal beyond NOON;
- loses the SEALED state at 12:30 PM;
- applies restoration before 1:00 PM;
- delays restoration beyond 1:00 PM;
- collapses the NOON-to-1:00 PM intermediate state;
- invents encounterability;
- invents continuity claims;
- resolves formal identity/non-identity;
- invents dependency standing;
- resolves authorship or idea attribution;
- creates admission, topology, authority, execution, or control effects.

# ==================================================
# ADMINISTRATION
# ==================================================

This is Run A only.

Do not inspect prior evaluator material.
Do not infer why these observation instants were selected.
Do not self-adjudicate.

Return only the required Run A output and stop.
