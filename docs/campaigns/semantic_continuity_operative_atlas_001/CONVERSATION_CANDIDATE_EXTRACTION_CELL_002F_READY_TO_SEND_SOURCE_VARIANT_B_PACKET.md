# CONVERSATION CANDIDATE EXTRACTION CELL 002F — READY-TO-SEND SOURCE VARIANT B PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002F_SOURCE_VARIANT_B_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_RELATIONAL_EXTENT_EXTRACTOR

MODE:
SOURCE_VARIANT

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

Evaluate one bounded temporal source variant under the generic
relation-recovery contract.

No characterization of the relation between the supplied intervals is
provided.

# ==================================================
# ADMITTED SOURCE
# ==================================================

source_id:
MYTHIC_RIFF_INTERVAL_VARIANT_SOURCE_004_NEUTRAL_REPEAT

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

A later incarnation begins at the start of YEAR_16.

Records local to the fictional setting establish that the later
incarnation remains alive and active continuously from the start of
YEAR_16 through the end of YEAR_22.

Separately, one prior symbolic identity had been externalized into a
shrine-bound form.

Independent shrine records establish that this symbolic form produces
responses continuously from the start of YEAR_10 through the end of
YEAR_30.

No source sentence states a shared activity window between the later
incarnation and the shrine-bound symbolic form.

The source does not state that they encounter one another.

The source does not classify their identity relation as identity,
succession, inheritance, duplication, persistence, realization, or any
other formal category.

The source does not state that either has a legitimate continuity claim
concerning a prior incarnation.

<<<END SOURCE VARIANT>>>

# ==================================================
# EXTRACTION QUESTION
# ==================================================

Using only the admitted source:

Recover at most ONE bounded relation that requires combining at least
TWO separately stated source facts.

If the relation has a bounded temporal extent, return the smallest extent
actually warranted by the source.

Do not simply repeat either input interval as if it were already the
combined relation.

Do not infer any relation stronger than the combined temporal facts
support.

If no combined relation is warranted, return no candidate.

# ==================================================
# REQUIRED OUTPUT
# ==================================================

Return exactly:

VARIANT_CANDIDATE_STATUS:
RECOVERED | NOT_RECOVERED | UNRESOLVED

VARIANT_CANDIDATE:

candidate_id:
<local id or NONE>

standing:
CANDIDATE_ONLY | NONE

subject_candidate:
<bounded subject or NONE>

relation_candidate:
<one relation or NONE>

object_or_value_candidate:
<bounded object/value or NONE>

derived_extent:
<bounded interval if warranted, otherwise NONE>

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
<descriptions of exact separate antecedents combined>

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


VARIANT_SOURCE_POSTURE:

source_id:
MYTHIC_RIFF_INTERVAL_VARIANT_SOURCE_004_NEUTRAL_REPEAT

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

explicit_overlap_language_supplied:
NO

explicit_shared_window_supplied:
NO

explicit_encounter_language_supplied:
NO

explicit_continuity_claim_language_supplied:
NO

explicit_non_reduction_language_supplied:
NO

scientific_admission_created:
NONE

topology_created:
NONE


VARIANT_UNRESOLVED:
<list>

# ==================================================
# FAILURE CONDITIONS
# ==================================================

FAIL / DEGRADE if the output:

- imports a prior candidate as evidence;
- merely repeats one interval without establishing a combined relation;
- derives a shared extent broader than jointly warranted;
- invents encounterability;
- invents continuity claims;
- resolves formal identity or non-identity;
- invents dependency standing;
- resolves authorship or idea attribution;
- creates admission, topology, authority, execution, or control effects.

# ==================================================
# ADMINISTRATION
# ==================================================

Use only this source and contract.

Do not inspect evaluator material.
Do not infer why this variant was selected.
Do not self-adjudicate.

Return only the required output and stop.
