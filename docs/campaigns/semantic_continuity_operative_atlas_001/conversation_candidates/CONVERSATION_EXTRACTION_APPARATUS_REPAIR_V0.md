# CONVERSATION EXTRACTION APPARATUS REPAIR V0

OBJECT_TYPE:
EXPERIMENTAL_APPARATUS_REPAIR

OBJECT_ID:
CONVERSATION_EXTRACTION_APPARATUS_REPAIR_V0

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

SOURCE_HEAD:
889020860e05d51917fae097d674d2f7f36c8763

STATUS:
FROZEN_FOR_REPAIRED_REPEAT

IMPLEMENTATION:
APPARATUS_CONTRACT_ONLY

REPO_MUTATION:
THIS ARTIFACT ONLY

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

CONTROL_EFFECT:
NONE

# ==================================================
# PURPOSE
# ==================================================

Repair the five apparatus wounds exposed by the first live
conversation-candidate extraction specimen before any repaired repeat.

The repaired experiment must preserve:

SOURCE_CAPTURE
!=
CONVERSATION_SOURCE

EXACT_SPAN_AUTHORSHIP
!=
PACKET_PARTICIPATION

DECLARED_RUN_A_FREEZE
!=
WITNESSED_RUN_A_FINALIZATION

SOURCE_LAYER_PRESSURE
!=
CANDIDATE_LAYER_CORRUPTION

MECHANISM_COMPONENTS
!=
INDEPENDENT_DEPENDENCE_RELATIONS

# ==================================================
# REPAIR 1 — SOURCE_CAPTURE_V0 != CONVERSATION_SOURCE_V0
# ==================================================

SOURCE_CAPTURE_V0 represents the captured material before semantic
source-boundary selection.

Minimum fields:

capture_id
capture_origin
capture_payload
capture_digest
captured_at_or_unresolved
capture_format
boundary_status

boundary_status:
RAW_CAPTURE

The capture may include:

conversation content
UI chrome
export chrome
attachment labels
transport artifacts
other non-conversation material

Nothing is silently discarded.

CONVERSATION_SOURCE_V0 represents an admitted conversation span derived
from a SOURCE_CAPTURE_V0.

Minimum fields:

source_id
capture_id
span_id
span_start_coordinate
span_end_coordinate
exact_text
source_digest
speaker_posture
boundary_derivation
boundary_witness
bounded_context_handles

Freeze:

SOURCE_CAPTURE_BYTES
!=
ADMITTED_CONVERSATION_CONTENT_SPAN

UI_CHROME_EXCLUDED
does not mean
UI_CHROME_NEVER_EXISTED_IN_CAPTURE.

The source object must preserve a challenge path back to the raw capture.

# ==================================================
# REPAIR 2 — EXACT SPAN AUTHORSHIP
# ==================================================

Packet-level participation does not establish exact span authorship.

Minimum source posture for the repaired specimen:

source_participants:
PIMP_DADDY_D
REED

exact_span_authorship:
UNRESOLVED

unless an independently inspectable turn / speaker boundary witness is
supplied.

Allowed authorship posture:

RESOLVED(actor)
UNRESOLVED

Forbidden without witness:

packet participation
→
sole exact-span authorship

Freeze:

SOURCE PARTICIPATION
!=
EXACT SPAN AUTHORSHIP

and:

EXACT WORDING PRESENT
!=
IDEA ORIGINATION

Idea attribution remains candidate-side and may be:

SUPPORTED(actor)
UNRESOLVED

but may not be mechanically inherited from source participation.

# ==================================================
# REPAIR 3 — RUN_A FINALIZATION / ORDERING WITNESS
# ==================================================

Run A must be finalized before any pressure variant is materialized or
exposed to the extractor.

A declaration that Run A is frozen is insufficient.

Introduce:

RUN_A_FINALIZATION_RECEIPT_V0

Minimum fields:

run_id
source_object_id
source_object_digest
candidate_output_identity
candidate_output_digest
extractor_identity
finalized_at_or_sequence
finalization_event_id
variant_manifest_identity
variant_materialization_state_at_finalization
ordering_witness
receipt_digest

Required value:

variant_materialization_state_at_finalization:
NOT_MATERIALIZED_OR_NOT_EXPOSED

The apparatus must support the relation:

RUN_A_FINALIZED
<
VARIANT_MATERIALIZED_OR_EXPOSED

The ordering witness may be a mechanically inspectable event sequence,
Git commit lineage, append-only event identity, or equivalent bounded
evidence.

Freeze:

FREEZE_ASSERTED
!=
FREEZE_WITNESSED

OUTPUT_UNCHANGED
!=
OUTPUT_FINALIZED_BEFORE_PRESSURE_INFORMATION

A repaired repeat is administratively invalid if the ordering witness is
missing or does not establish the required order.

# ==================================================
# REPAIR 4 — REMOVE B4 FROM EXTRACTION PRESSURE
# ==================================================

Original B4 attempted to corrupt idea_attribution.

idea_attribution belongs to CANDIDATE_DISTINCTION_V0, not
CONVERSATION_SOURCE_V0.

Therefore B4 is removed from the repaired extractor-pressure suite.

Repaired source-layer variants:

B1:
speaker evidence removed

B2:
designated support span truncated

B3:
support-bearing text removed

B5:
bounded context removed

No B4 placeholder is retained in the extractor cell.

A separate future object may test:

CANDIDATE_ATTRIBUTION_CORRUPTION_CELL_001

where:

SOURCE:
IDENTICAL

SEMANTIC CANDIDATE:
IDENTICAL

SUPPORT:
IDENTICAL

ONLY MUTATION:
idea_attribution

That future pressure asks an evaluator question, not an extractor
question.

Freeze:

SOURCE-SIDE ATTRIBUTION PRESSURE
!=
CANDIDATE-SIDE ATTRIBUTION CORRUPTION

# ==================================================
# REPAIR 5 — MECHANISM COMPONENTS != DEPENDENCE EDGES
# ==================================================

For the repaired specimen, the source-supported mechanism contains:

RAW_EXECUTION_EVIDENCE
→
PINNED_ISOLATION_VERIFIER
→
POLICY_VERIFICATION_RESULT
→
ISOLATION_RECEIPT

The source supports these as components of one proposed verification
mechanism.

It does not establish multiple independently earned dependence
relations.

Candidate extraction may represent:

mechanism_components:
- RAW_EXECUTION_EVIDENCE
- PINNED_ISOLATION_VERIFIER

mechanism_posture:
CANDIDATE_MECHANISM

dependency_relations:
NONE_ADMITTED

If the extractor proposes dependency hypotheses, they must remain:

CANDIDATE_ONLY

and must not be interpreted as orthogonal dependence standing.

Freeze:

TWO COMPONENTS
!=
TWO INDEPENDENT DEPENDENCIES

MECHANISM STRUCTURE
!=
ATLAS DEPENDENCE TOPOLOGY

# ==================================================
# REPAIRED PRESSURE GEOMETRY
# ==================================================

SOURCE_CAPTURE_V0
→
BOUNDARY DERIVATION
→
CONVERSATION_SOURCE_V0
→
RUN_A EXTRACTION
→
RUN_A_FINALIZATION_RECEIPT_V0
→
ONLY THEN B1 / B2 / B3 / B5
→
FIELD-WISE COMPARISON
→
CROSS-INSTANCE ADJUDICATION
→
STOP

# ==================================================
# FIELD-WISE COMPARISON SURFACE
# ==================================================

Compare only:

candidate semantic wording
subject / target
source binding
source authorship posture
idea attribution posture
support posture
scope
claim ceiling
mechanism components
dependency hypotheses
unresolveds
candidate-only standing
authority / execution / control effects

Do not compare wrapper byte identity as scientific equivalence.

# ==================================================
# ADMINISTRATION VALIDITY
# ==================================================

A repaired run is VALID only if:

1. raw capture identity is preserved;
2. admitted conversation source points back to that capture;
3. boundary derivation is explicit;
4. exact span authorship remains unresolved unless witnessed;
5. Run A finalization receipt exists;
6. ordering witness establishes Run A before variant exposure;
7. B1/B2/B3/B5 each mutate one intended source relation only;
8. no B4 candidate-side mutation is relabeled as extractor pressure;
9. mechanism components do not become admitted dependence edges;
10. no candidate is admitted, registered, or projected into Atlas topology.

# ==================================================
# CLAIM CEILING
# ==================================================

This apparatus repair establishes only the experimental contract for a
cleaner repeat of Conversation Candidate Extraction Cell 001.

It does NOT establish:

extractor correctness
conversation-memory correctness
generic source segmentation
generic attribution correctness
generic dependence inference
candidate admission
symbolic continuity completeness
autonomous extraction safety

# ==================================================
# READY STATE
# ==================================================

REPAIR_1_SOURCE_CAPTURE_SPLIT:
FROZEN

REPAIR_2_AUTHORSHIP_POSTURE:
FROZEN

REPAIR_3_FINALIZATION_WITNESS:
FROZEN

REPAIR_4_B4_REMOVAL:
FROZEN

REPAIR_5_MECHANISM_DEPENDENCE_SEPARATION:
FROZEN

APPARATUS_READY_FOR_REPAIRED_REPEAT:
YES
