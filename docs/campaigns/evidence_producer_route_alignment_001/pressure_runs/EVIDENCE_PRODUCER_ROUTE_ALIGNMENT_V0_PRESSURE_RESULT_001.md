# G18 Evidence Producer Route Alignment Pressure 001 Result

PRESSURE_ID:
EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_PRESSURE_001

FROZEN_SETUP_SOURCE:
ed1a91184e836bfeb8b73e3126aa1b7e235fe07b

WITNESS_TRANSPORT:
774782748eb2aaea25fda13d05e08d6ecc004197

WITNESS:
docs/evidence/for_planner/evidence_producer_route_alignment_v0_observation.json

WITNESS_BLOB:
9d6e627401c3c51b9cc30449d80f6c94a99711d7

WITNESS_ONLY_TRANSPORT:
YES

TEST_PRODUCER:
tools/observe_horizon_gap_selector_v0.py

TEST_PRODUCER_BLOB_MATCHED:
YES

PRODUCER_EXIT_CODE:
0

OLD_ROOT_OUTPUT_CREATED:
true

GENERATED_ROOT_GIT_BLOB:
4333eca449c24dfaa09a126afc7937be403e6af1

RELOCATED_HISTORICAL_BLOB:
be23eba7c50f1b51a0e3b1412d9f5adc07dee1ff

GENERATED_ROOT_BLOB_NE_HISTORICAL_BLOB:
true

RELOCATED_HISTORICAL_BLOB_PRESERVED:
true

PRESSURE_CLEANUP_COMPLETE:
true

PRODUCER_OUTPUT_ROUTE_MIGRATED:
false

STORED_EVIDENCE_RELOCATION_NE_PRODUCER_OUTPUT_ROUTE_MIGRATION:
YES

EFFECTS:

producer_repair_effect = NONE
consumer_repair_effect = NONE
generic_intake_router_effect = NONE
archive_policy_effect = NONE
cold_storage_admission_effect = NONE
deletion_permission_effect = NONE
automatic_reference_rewrite_effect = NONE
planning_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE

DISPOSITION:
CANDIDATE_RELATION_OBSERVED_AWAITING_INDEPENDENT_ADJUDICATION

CLAIM_CEILING:
One bounded execution of tools/observe_horizon_gap_selector_v0.py. The unchanged
producer recreated a fresh observation at the old root output path after the
historical observation had been relocated, while the relocated historical blob
remained unchanged and the temporary root output was removed after capture.
This does not establish producer repair authority, consumer repair authority,
a generic intake router, archive policy, cold-storage admission, deletion
permission, automatic reference rewriting, planning, authority, execution,
or scientific standing.

STOPPED:
YES
