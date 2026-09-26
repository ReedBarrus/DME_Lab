# G16 Evidence Path Relocation / Reachability Contract V0

STATUS:
CANDIDATE

TARGET_RELATION:
CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

PRE_MOVE_SOURCE:
cf2d62f175bfae784d3755dc83ab7ea1d4e33b2f

RELOCATION_COMMIT:
2ea35acb8d4fb61f55f4725a5af72510746460b5

INVENTORY_BLOB:
b5401152ef89b209e535c49ca4e989e32095ced3

TEST_SET:
1. declaration_work_eligibility_selection_load_v0_observation.json
   expected_blob = 54ab5157ec936474c6189f2d956127fc5cb1e0c0
2. distinction_retention_currentness_v0_observation.json
   expected_blob = 949ff2b9333146ca16e68981123f338f6e4dfd15
3. distinction_retention_mode_v0_observation.json
   expected_blob = 1ff52354096371710ccdcdd77dfb9a6b2c1ada3b
4. partial_basis_residual_conservation_v0_observation.json
   expected_blob = 1736d63c13c27d37641f3a6f78825c9288428a50
5. partial_basis_retention_profile_v0_observation.json
   expected_blob = 4f4c7efef184c1f60ab362420d7ef09a1c43dab1
6. retention_scope_aggregation_v0_observation.json
   expected_blob = 212d7a9d4fb7bc982cb83b418ee6d5982008c574

REQUIRED_CONTROL:
At PRE_MOVE_SOURCE, each root path resolves to the expected blob.

REQUIRED_RELOCATION:
At RELOCATION_COMMIT:
- each original root path is absent;
- each relocated path under docs/evidence/for_planner/ resolves;
- each relocated path resolves to the same expected blob.

MATCH_CANDIDATE:
If all six satisfy the control and relocation conditions:

CONTENT_IDENTITY_PRESERVED = YES
ORIGINAL_WITNESS_PATH_REACHABILITY_PRESERVED = NO
RELOCATED_WITNESS_PATH_REACHABILITY = YES
REFERENCE_ROUTE_BREAK_PRESENT = YES

CANDIDATE_RELATION:
CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

NONCLAIMS:
No evidence loss.
No claim falsification.
No scientific-standing change.
No automatic reference-rewrite authority.
No generic relocation resolver.
No archive/cold-storage policy.
No deletion permission.
No planning, authority, or execution effect.

STOP:
After producing one mechanical observation.
