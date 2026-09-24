# CONVERSATION CANDIDATE EXTRACTION CELL 003F — READY-TO-SEND SOURCE VARIANT F PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003F_SOURCE_VARIANT_F_PACKET

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
- one fixed event sequence;
- an explicitly defined event-effect boundary;
- observation times immediately before, at, and after that boundary.

No expected observation relation, precomputed transition state, or
event-priority rule is supplied.

# ==================================================
# ADMITTED SOURCE
# ==================================================

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_006

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
the end of DAY_4.

At the end of DAY_4, a seal is applied to the shrine.

The event record states that the seal begins preventing shrine-bound
response-production exactly at the start of DAY_5.

No later shrine event is recorded before the end of DAY_10.

No later event affecting the later incarnation is recorded before the
end of DAY_10.

Three bounded observation instants are supplied:

OBSERVATION_A:
the final instant of DAY_4

OBSERVATION_B:
the first instant of DAY_5

OBSERVATION_C:
the first instant after the start of DAY_5

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

Recover at most ONE bounded relation for each supplied observation
instant.

Each recovered relation must combine the later-incarnation activity fact
with the shrine state warranted at that observation instant.

Preserve the source-defined transition boundary exactly.

Do not smear the seal effect backward into DAY_4.

Do not delay the seal effect beyond the first instant of DAY_5.

Do not infer any relation stronger than the source supports.

If no relation is warranted at an observation instant, return no
candidate for that observation.

# ==================================================
# REQUIRED OUTPUT
# ==================================================

Return exactly:

OBSERVATION_A_RESULT:

observation_time:
final instant of DAY_4

candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED

candidate_relation:
<one bounded relation or NONE>

boundary_state:
PRE_EFFECT | EFFECTIVE | POST_EFFECT | UNRESOLVED

support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

claim_ceiling:
<bounded claim ceiling or NONE>


OBSERVATION_B_RESULT:

observation_time:
first instant of DAY_5

candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED

candidate_relation:
<one bounded relation or NONE>

boundary_state:
PRE_EFFECT | EFFECTIVE | POST_EFFECT | UNRESOLVED

support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

claim_ceiling:
<bounded claim ceiling or NONE>


OBSERVATION_C_RESULT:

observation_time:
first instant after the start of DAY_5

candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED

candidate_relation:
<one bounded relation or NONE>

boundary_state:
PRE_EFFECT | EFFECTIVE | POST_EFFECT | UNRESOLVED

support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

claim_ceiling:
<bounded claim ceiling or NONE>


BOUNDARY_COMPARISON:

transition_boundary_preserved:
YES | NO | UNRESOLVED

pre_boundary_relation_differs_from_at_boundary:
YES | NO | UNRESOLVED

at_boundary_matches_post_boundary_effect_state:
YES | NO | UNRESOLVED

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
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_006

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

- treats the final instant of DAY_4 as already sealed;
- treats the first instant of DAY_5 as still pre-seal;
- shifts the source-defined transition boundary;
- invents shrine response-production after the effect begins;
- invents encounterability;
- invents continuity claims;
- resolves formal identity or non-identity;
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
