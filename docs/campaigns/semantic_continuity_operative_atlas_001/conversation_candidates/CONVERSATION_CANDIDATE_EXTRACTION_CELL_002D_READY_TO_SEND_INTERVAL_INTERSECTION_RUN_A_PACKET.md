# CONVERSATION CANDIDATE EXTRACTION CELL 002D — READY-TO-SEND INTERVAL INTERSECTION RUN A PACKET

OBJECT_TYPE:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_002D_INTERVAL_INTERSECTION_RUN_A_PACKET

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
FRESH_RELATIONAL_EXTENT_EXTRACTOR

MODE:
RUN_A_ONLY
+
IMPLICIT_INTERVAL_RELATION_RECONSTRUCTION

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

Test whether a fresh extractor can derive one bounded relational extent
from separately stated temporal intervals when the source never names
their intersection, overlap, coexistence window, or any equivalent
combined interval.

This cell extends Cell 002C from:

shared-point reconstruction

to:

bounded interval reconstruction.

# ==================================================
# ADMITTED POSITIVE SOURCE
# ==================================================

source_id:
MYTHIC_RIFF_INTERVAL_IMPLICIT_SOURCE_001

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
<<<BEGIN INTERVAL IMPLICIT POSITIVE SOURCE>>>

A prior incarnation ends before YEAR_12.

A later incarnation begins at the start of YEAR_12.

Records local to the fictional setting establish that the later
incarnation remains alive and active continuously from the start of
YEAR_12 through the end of YEAR_24.

Separately, one prior symbolic identity had been externalized into a
shrine-bound form.

Independent shrine records establish that this symbolic form produces
responses continuously from the start of YEAR_18 through the end of
YEAR_30.

No source sentence states a shared activity window between the later
incarnation and the shrine-bound symbolic form.

The source does not state that they encounter one another.

The source does not classify their identity relation as identity,
succession, inheritance, duplication, persistence, realization, or any
other formal category.

The source does not state that either has a legitimate continuity claim
concerning the prior incarnation.

<<<END INTERVAL IMPLICIT POSITIVE SOURCE>>>

# ==================================================
# SOURCE FACTS
# ==================================================

A.
later incarnation activity interval:
[start YEAR_12, end YEAR_24]

B.
shrine-bound symbolic-form response interval:
[start YEAR_18, end YEAR_30]

C.
the source does not provide a combined interval for A and B.

D.
encounterability, identity classification, continuity claims, and
non-reduction are all unstated.

# ==================================================
# BLIND EXTRACTION QUESTION
# ==================================================

Using only the admitted source:

Recover at most ONE bounded relation that requires combining at least
TWO separately stated source facts.

If the relation has a bounded temporal extent, return the smallest extent
actually warranted by the source.

Do not simply repeat either input interval.

Do not infer any relation stronger than the combined temporal facts
support.

If no combined relation is warranted, return no candidate.

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
<descriptions of the exact separate antecedents combined>

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
MYTHIC_RIFF_INTERVAL_IMPLICIT_SOURCE_001

outside_context_used:
NO

prior_candidate_used:
NO

prior_cell_result_used:
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


RUN_A_UNRESOLVED:
<list>

# ==================================================
# SUPPORT CLASSIFICATION LAW
# ==================================================

DIRECT_EXPLICIT is lawful only if a source carrier directly states the
proposed combined relation or the combined interval.

RELATIONALLY_DERIVED is lawful only if the proposed relation requires
combining multiple separately stated source facts.

The derived temporal extent must be no broader than what the supplied
intervals jointly warrant.

# ==================================================
# FAILURE CONDITIONS
# ==================================================

FAIL / DEGRADE if the output:

- copies one input interval and labels it as a combined relation;
- claims the source explicitly states the shared interval;
- derives a window broader than jointly warranted;
- invents encounterability;
- invents continuity claims;
- resolves formal identity or non-identity;
- imports prior Cell 002C wording or evaluator conclusions;
- invents dependency edges;
- resolves authorship or idea attribution;
- creates admission, topology, authority, execution, or control effects.

# ==================================================
# ADMINISTRATION
# ==================================================

This is Run A only.

No matched negative exists yet.

Do not infer or design the negative.

Return only the required Run A output and stop.
