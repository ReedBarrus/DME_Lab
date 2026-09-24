# CONVERSATION CANDIDATE EXTRACTION CELL 001 — REPAIRED PACKET TEMPLATE V0

OBJECT_TYPE:
REPAIRED_EXPERIMENT_PACKET_TEMPLATE

OBJECT_ID:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_001_REPAIRED_PACKET_TEMPLATE_V0

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

APPARATUS_BASIS:
docs/campaigns/semantic_continuity_operative_atlas_001/CONVERSATION_EXTRACTION_APPARATUS_REPAIR_V0.md

APPARATUS_HEAD:
2598600c014717e7c7905936a035348a44cc5ee3

# ==================================================
# PACKET A0 — SOURCE_CAPTURE_V0
# ==================================================

SOURCE_CAPTURE_V0

capture_id:
<stable capture id>

capture_origin:
<historical conversation/export origin>

capture_payload:
<exact captured material, including UI/export chrome if present>

capture_digest:
<mechanically calculated digest>

captured_at_or_unresolved:
<timestamp or UNRESOLVED>

capture_format:
<text/export/etc>

boundary_status:
RAW_CAPTURE


# ==================================================
# PACKET A1 — CONVERSATION_SOURCE_V0
# ==================================================

CONVERSATION_SOURCE_V0

source_id:
<stable source id>

capture_id:
<must equal A0 capture_id>

span_id:
<stable span id>

span_start_coordinate:
<mechanically inspectable coordinate>

span_end_coordinate:
<mechanically inspectable coordinate>

exact_text:
<exact admitted conversation content span>

source_digest:
<mechanically calculated digest>

source_participants:
- PIMP_DADDY_D
- REED

exact_span_authorship:
UNRESOLVED

speaker_posture:
PACKET_PARTICIPATION_KNOWN_EXACT_SPAN_AUTHORSHIP_UNRESOLVED

boundary_derivation:
<rule used to exclude UI/export chrome>

boundary_witness:
<mechanical or bounded witness back to A0>

bounded_context_handles:
<list or NONE>


# ==================================================
# RUN A OUTPUT
# ==================================================

The extractor receives A1 only as admitted conversation source.

It must emit exactly one:

CANDIDATE_DISTINCTION_V0

and stop.

No B variant may be materialized or exposed before the candidate is
finalized.


# ==================================================
# RUN_A_FINALIZATION_RECEIPT_V0
# ==================================================

RUN_A_FINALIZATION_RECEIPT_V0

run_id:
<stable run id>

source_object_id:
<A1 source_id>

source_object_digest:
<A1 source_digest>

candidate_output_identity:
<stable candidate identity>

candidate_output_digest:
<mechanically calculated candidate digest>

extractor_identity:
<fresh extractor instance identity>

finalized_at_or_sequence:
<mechanically inspectable time or sequence coordinate>

finalization_event_id:
<event/commit/receipt id>

variant_manifest_identity:
<manifest id>

variant_materialization_state_at_finalization:
NOT_MATERIALIZED_OR_NOT_EXPOSED

ordering_witness:
<evidence showing Run A finalized before B variant exposure>

receipt_digest:
<mechanically calculated digest>


# ==================================================
# VARIANT MANIFEST
# ==================================================

VARIANT_MANIFEST_V0

manifest_id:
<stable id>

source_object_id:
<A1 source_id>

run_a_finalization_receipt:
<receipt id>

B1:
SPEAKER_EVIDENCE_REMOVED

B2:
SUPPORT_SPAN_TRUNCATED

B3:
SUPPORT_BEARING_TEXT_REMOVED

B5:
BOUNDED_CONTEXT_REMOVED

B4:
ABSENT_FROM_THIS_CELL

Freeze:

B1/B2/B3/B5
must each mutate exactly one intended source relation.

The manifest and variants may be materialized only after the Run A
ordering witness exists.


# ==================================================
# DEPENDENCY / MECHANISM POSTURE
# ==================================================

For this specimen:

mechanism_components:
- RAW_EXECUTION_EVIDENCE
- PINNED_ISOLATION_VERIFIER

mechanism_posture:
CANDIDATE_MECHANISM

dependency_relations:
NONE_ADMITTED

Any dependency proposal emitted by an extractor remains:

CANDIDATE_ONLY


# ==================================================
# ADMINISTRATIVE STOP
# ==================================================

STOP if:

- exact span authorship is upgraded without witness;
- candidate is admitted;
- topology is mutated;
- B4 is reintroduced as source-layer extraction pressure;
- variants are materialized/exposed before Run A finalization witness;
- mechanism components are treated as admitted dependence edges.
