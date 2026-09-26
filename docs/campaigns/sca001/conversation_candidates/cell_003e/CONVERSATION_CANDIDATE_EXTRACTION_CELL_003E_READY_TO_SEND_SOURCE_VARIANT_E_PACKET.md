# CONVERSATION CANDIDATE EXTRACTION CELL 003E — READY-TO-SEND SOURCE VARIANT E PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003E_SOURCE_VARIANT_E_PACKET

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
- one observation time before the second event takes effect;
- one observation time after the second event takes effect.

No expected relation at either observation time, precomputed state, or
event-priority rule is supplied.

# ==================================================
# ADMITTED SOURCE
# ==================================================

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_005

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

At the start of YEAR_10, a later incarnation becomes active.

Records establish that the later incarnation remains continuously active
through the end of YEAR_30.

Separately, a shrine-bound symbolic form begins producing responses at
the start of YEAR_16.

Before any later shrine event is considered, records support continuous
response-production through the end of YEAR_20.

At the end of YEAR_20, a seal is applied to the shrine.

The event record states that, beginning at the start of YEAR_21, the seal
prevents shrine-bound response-production unless a later shrine event
changes that condition.

At the end of YEAR_23, a reinforcement is applied to the shrine.

The later event record states that, beginning at the start of YEAR_24,
the reinforcement restores shrine-bound response-production and supports
continuous responses through the end of YEAR_26.

No still-later shrine event is recorded before the end of YEAR_30.

No later event affecting the later incarnation is recorded before the
end of YEAR_30.

Two bounded observation times are supplied:

OBSERVATION_A:
YEAR_22

OBSERVATION_B:
YEAR_25

No source sentence states the relation between the later incarnation and
the shrine-bound symbolic form at either observation time.

The source does not state that the two encounter one another.

The source does not classify their identity relation.

The source does not state that either has a legitimate continuity claim
concerning a prior incarnation.

<<<END SOURCE VARIANT>>>

# ==================================================
# EXTRACTION QUESTION
# ==================================================

Using only the admitted source:

Recover at most TWO bounded relations:
- one at OBSERVATION_A;
- one at OBSERVATION_B.

Each recovered relation must require combining multiple separately
stated source facts, including historical events where relevant.

Account for the same event sequence in source order.

Do not infer an event-priority rule beyond what the source records
support.

Do not infer any relation stronger than the source supports.

If no combined relation is warranted at one observation time, return no
candidate for that observation.

# ==================================================
# REQUIRED OUTPUT
# ==================================================

Return exactly:

OBSERVATION_A_RESULT:

observation_time:
YEAR_22

candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED

candidate_relation:
<one bounded relation at YEAR_22 or NONE>

historical_state_used:
<brief ordered source-bounded state reconstruction or NONE>

support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

claim_ceiling:
<bounded claim ceiling or NONE>


OBSERVATION_B_RESULT:

observation_time:
YEAR_25

candidate_status:
RECOVERED | NOT_RECOVERED | UNRESOLVED

candidate_relation:
<one bounded relation at YEAR_25 or NONE>

historical_state_used:
<brief ordered source-bounded state reconstruction or NONE>

support_posture:
RELATIONALLY_DERIVED | DIRECT_EXPLICIT | UNRESOLVED | NONE

claim_ceiling:
<bounded claim ceiling or NONE>


OBSERVATION_COMPARISON:

same_event_sequence:
YES | NO | UNRESOLVED

observation_time_changes_relation:
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
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_005

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

- changes the event sequence between observations;
- ignores that YEAR_22 occurs after the seal but before restoration;
- ignores that YEAR_25 occurs after restoration;
- invents shrine response-production at YEAR_22;
- denies shrine response-production at YEAR_25 despite the later restoration;
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
Do not infer why these observation times were selected.
Do not self-adjudicate.

Return only the required Run A output and stop.
