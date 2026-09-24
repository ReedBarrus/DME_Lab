# CONVERSATION CANDIDATE EXTRACTION CELL 003C — READY-TO-SEND SOURCE VARIANT C PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_003C_SOURCE_VARIANT_C_PACKET

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
- an earlier documented state;
- two later events with documented local effects;
- a later state fact.

No expected relation, precomputed transformed extent, event-priority
rule, or consequence classification is supplied.

# ==================================================
# ADMITTED SOURCE
# ==================================================

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_003

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

Before any later event is considered, shrine records support continuous
response-production through the end of YEAR_20.

At the end of YEAR_20, a reinforcement is applied to the shrine.

The event record states that, beginning at the start of YEAR_21, the
reinforced shrine-bound symbolic form continues producing responses
continuously through the end of YEAR_26.

At the end of YEAR_23, a seal is applied to the shrine.

The later event record states that the seal prevents the shrine-bound
symbolic form from producing responses beginning at the start of
YEAR_24.

No still-later shrine event is recorded before the end of YEAR_30.

No later event affecting the later incarnation is recorded before the
end of YEAR_30.

No source sentence states the final jointly supported activity interval
between the later incarnation and the shrine-bound symbolic form.

The source does not state that the two encounter one another.

The source does not classify their identity relation.

The source does not state that either has a legitimate continuity claim
concerning a prior incarnation.

<<<END SOURCE VARIANT>>>

# ==================================================
# EXTRACTION QUESTION
# ==================================================

Using only the admitted source:

Recover at most ONE bounded current relation that requires combining
multiple separately stated source facts, including both historical
events where relevant.

If the current relation has a bounded temporal extent, return the exact
extent warranted after accounting for the event sequence.

Do not merely repeat:
- the pre-event source interval;
- the state after only the first event;
- the effect of only the second event in isolation.

Do not invent an event-priority rule beyond what temporal order and the
event records support.

Do not infer any relation stronger than the source supports.

If no combined current relation is warranted, return no candidate.

# ==================================================
# REQUIRED OUTPUT
# ==================================================

Return exactly:

RUN_A_CANDIDATE_STATUS:
RECOVERED | NOT_RECOVERED | UNRESOLVED

RUN_A_CANDIDATE:

candidate_id:
<local id or NONE>

standing:
CANDIDATE_ONLY | NONE

subject_candidate:
<bounded subject or NONE>

relation_candidate:
<one current relation or NONE>

object_or_value_candidate:
<bounded object/value or NONE>

derived_extent:
<bounded extent if warranted, otherwise NONE>

historical_changes_used:
<brief ordered description of both event contributions or NONE>

event_order_effect:
<brief source-bounded description of how order affects the current relation, or NONE>

candidate_description:
<short explanation or NONE>

support_posture:
RELATIONALLY_DERIVED
|
DIRECT_EXPLICIT
|
UNRESOLVED
|
NONE

source_support_handles:
<descriptions of exact separate antecedents/event facts combined>

source_authorship_posture:
UNRESOLVED_IN_THIS_CAPTURE

idea_attribution:
UNRESOLVED

scope_candidate:
<bounded fictional/design scope>

claim_ceiling_candidate:
<what the candidate does and does not establish>

dependency_candidates:
NONE unless independently warranted

contradictions:
<source-local only>

unresolved:
<explicit unresolveds>

authority_effect:
NONE

execution_effect:
NONE

control_effect:
NONE


RUN_A_SOURCE_POSTURE:

source_id:
MYTHIC_RIFF_HISTORICAL_VARIANT_SOURCE_003

outside_context_used:
NO

prior_candidate_used:
NO

prior_cell_result_used:
NO

precomputed_relation_supplied:
NO

precomputed_transformed_extent_supplied:
NO

expected_relation_supplied:
NO

event_priority_rule_supplied:
NO

explicit_final_shared_window_supplied:
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

- uses only one of the two event records when both affect supported current state;
- stops at the first-event extension through YEAR_26;
- ignores the later seal beginning at YEAR_24;
- invents response-production after the seal takes effect;
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

No matched sequence variant has been materialized.

Do not infer why this event sequence was selected.
Do not inspect prior evaluator material.
Do not self-adjudicate.

Return only the required Run A output and stop.
