# G18 Evidence Producer Route Alignment Horizon V0

STATUS:
JUSTIFIED_CANDIDATE

PREDECESSOR:
G17 / MECHANICAL_OCCURRENCE_INVENTORY_COMPLETE

G17_WITNESS:
docs/evidence/for_planner/evidence_relocation_reference_closure_v0_observation.json

G17_WITNESS_BLOB:
9cf234fffd1d5b63bfc0af2238e496a2402fe308

EARNED_INVARIANT:
EMI-015 / CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

TARGET_RELATION:
STORED_EVIDENCE_RELOCATION != PRODUCER_OUTPUT_ROUTE_MIGRATION

TEST_PRODUCER:
tools/observe_horizon_gap_selector_v0.py

TEST_PRODUCER_BLOB:
54891e276f28a3f4fe4d61775d14b706cf56bd1e

HISTORICAL_ARTIFACT:
horizon_gap_selector_v0_observation.json

RELOCATED_HISTORICAL_PATH:
docs/evidence/for_planner/horizon_gap_selector_v0_observation.json

RELOCATED_HISTORICAL_BLOB:
be23eba7c50f1b51a0e3b1412d9f5adc07dee1ff

STALE_PRODUCER_OUTPUT_BINDING:
ROOT / "horizon_gap_selector_v0_observation.json"

QUESTION:
After the historical evidence artifact has been relocated away from root, does the
unchanged producer follow that relocation, or does a fresh producer execution
reoccupy the old root output path?

PRESSURE_POSTURE:
Execute exactly one existing producer under a wrapper that:
- requires the old root output path to be absent before execution;
- verifies the relocated historical artifact at its expected blob;
- runs the exact producer once;
- observes whether the old root path is created;
- records the generated output identity;
- verifies the relocated historical blob remains unchanged;
- removes the temporary generated root output after observation.

REQUIRED_NONCOLLAPSES:
STORED_ARTIFACT_RELOCATION != PRODUCER_ROUTE_MIGRATION
OLD_PATH_REOCCUPATION != HISTORICAL_EVIDENCE_OVERWRITE
NEW_OUTPUT != HISTORICAL_ARTIFACT
PRODUCER_ROUTE_MISALIGNMENT != GENERIC_RELOCATION_POLICY
PRESSURE_CLEANUP != EVIDENCE_DELETION

DEFERRED:
repair of producer routes
repair of consumer routes
generic evidence intake routing
archive policy
cold-storage admission
deletion permission
automatic reference rewriting
global evidence lifecycle
planning
authority
execution

CLAIM_CEILING:
One bounded producer execution over observe_horizon_gap_selector_v0.py only.
