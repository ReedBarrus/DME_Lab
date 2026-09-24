# RUN A FINALIZATION RECEIPT V0

OBJECT_TYPE:
RUN_A_FINALIZATION_RECEIPT_V0

OBJECT_ID:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_001_RUN_A_FINALIZATION_RECEIPT_001

CAMPAIGN:
SEMANTIC_CONTINUITY_OPERATIVE_ATLAS_CAMPAIGN_001

run_id:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_001_REPAIRED_RUN_A_001

source_object_id:
PIMP_DADDY_D_CONVERSATION_SOURCE_001

source_packet_commit:
613c4ca6004d4709b7623509163f5f2ce65ae7e5

candidate_output_identity:
CONVERSATION_CANDIDATE_EXTRACTION_CELL_001_RUN_A_FROZEN_OUTPUT_001

candidate_output_blob:
99ec6e86c451fde01fcb0f82cee1aa6138f5b9fd

candidate_output_commit:
6f108b1c0019958cab4746317e6b590bb2ce857c

extractor_identity:
FRESH_EXTRACTOR_INSTANCE

finalized_at_or_sequence:
GIT_COMMIT_6f108b1c0019958cab4746317e6b590bb2ce857c

finalization_event_id:
RUN_A_FINALIZED_BY_GIT_COMMIT_6f108b1c0019958cab4746317e6b590bb2ce857c

variant_manifest_identity:
NOT_YET_MATERIALIZED

variant_materialization_state_at_finalization:
NOT_MATERIALIZED_OR_NOT_EXPOSED

ordering_witness:
The frozen Run A output exists at commit
6f108b1c0019958cab4746317e6b590bb2ce857c.
No repaired B1/B2/B3/B5 variant packet existed in the repository at that
commit. The variant packet, if created, must appear only in a descendant
commit. Git ancestry is the bounded ordering witness.

administration_status:
VALID_FOR_VARIANT_MATERIALIZATION

authority_effect:
NONE

execution_effect:
NONE

control_effect:
NONE

admission:
NONE

topology_mutation:
NONE

FREEZE:

RUN_A_FINALIZED
<
VARIANT_MATERIALIZATION

and:

FROZEN_OUTPUT_IDENTITY:
99ec6e86c451fde01fcb0f82cee1aa6138f5b9fd

This receipt establishes only the ordering and identity of the repaired
Run A artifact for this experiment. It does not validate the candidate's
scientific content.
