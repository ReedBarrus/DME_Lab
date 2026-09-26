# G18 Evidence Producer Route Alignment Contract V0

STATUS:
CANDIDATE

TARGET_RELATION:
STORED_EVIDENCE_RELOCATION != PRODUCER_OUTPUT_ROUTE_MIGRATION

TEST_PRODUCER:
tools/observe_horizon_gap_selector_v0.py

TEST_PRODUCER_BLOB:
54891e276f28a3f4fe4d61775d14b706cf56bd1e

OLD_ROOT_OUTPUT_PATH:
horizon_gap_selector_v0_observation.json

RELOCATED_HISTORICAL_PATH:
docs/evidence/for_planner/horizon_gap_selector_v0_observation.json

RELOCATED_HISTORICAL_BLOB:
be23eba7c50f1b51a0e3b1412d9f5adc07dee1ff

PRECONDITIONS:
- old root output path absent
- relocated historical path present
- relocated historical blob matches expected
- test producer blob matches expected

PRESSURE:
Run the exact existing producer once without modifying it.

REQUIRED_OBSERVATION:
- producer exit code = 0
- old root output path created = true
- generated root output is readable
- relocated historical path remains present
- relocated historical blob remains exact expected blob
- old root output removed by wrapper after capture
- relocated historical file is not deleted or rewritten

CANDIDATE_MATCH:
If the producer successfully creates a new observation at the old root path while
the relocated historical artifact remains unchanged:

STORED_EVIDENCE_RELOCATION = YES
PRODUCER_OUTPUT_ROUTE_MIGRATED = NO
OLD_ROOT_PATH_REOCCUPIED_BY_FRESH_OUTPUT = YES
RELOCATED_HISTORICAL_BLOB_PRESERVED = YES
STORED_EVIDENCE_RELOCATION_NE_PRODUCER_OUTPUT_ROUTE_MIGRATION = YES

OPTIONAL_OBSERVATION:
GENERATED_ROOT_GIT_BLOB_NE_HISTORICAL_RELOCATED_GIT_BLOB

This optional difference is informative but is not required for the target relation.

NONCLAIMS:
No producer repair authority.
No consumer repair authority.
No generic intake router.
No archive policy.
No cold-storage admission.
No deletion permission.
No automatic reference rewriting.
No planning, authority, execution, or scientific standing.

STOP:
after one producer execution, capture, and cleanup.
