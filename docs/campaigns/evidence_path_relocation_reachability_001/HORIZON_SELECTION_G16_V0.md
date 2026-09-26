# G16 Evidence Path Relocation / Reachability Horizon V0

STATUS:
JUSTIFIED_CANDIDATE

CURRENT_LEDGER_BLOB:
5f665ec27f07c46c83ca8427aa5a8697d2276253

PRE_MOVE_SOURCE:
cf2d62f175bfae784d3755dc83ab7ea1d4e33b2f

RELOCATION_COMMIT:
2ea35acb8d4fb61f55f4725a5af72510746460b5

RELOCATION_INVENTORY:
docs/evidence/for_planner/ROOT_EVIDENCE_INVENTORY.md

RELOCATION_INVENTORY_BLOB:
b5401152ef89b209e535c49ca4e989e32095ced3

TARGET_RELATION:
CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

QUESTION:
When an evidence artifact is moved with exact blob identity preserved, does a
previous repository-relative witness path remain a valid route to that evidence?

MECHANICALLY_OBSERVED_CURRENT_BREAK:
The current invariant ledger references six moved root-level witness paths whose
old paths no longer resolve, while each relocated path resolves to the same
recorded blob identity.

TEST_SET:
- declaration_work_eligibility_selection_load_v0_observation.json
- distinction_retention_currentness_v0_observation.json
- distinction_retention_mode_v0_observation.json
- partial_basis_residual_conservation_v0_observation.json
- partial_basis_retention_profile_v0_observation.json
- retention_scope_aggregation_v0_observation.json

REQUIRED_NONCOLLAPSES:
BLOB_IDENTITY_PRESERVED != PATH_HANDLE_PRESERVED
PATH_RELOCATION != EVIDENCE_LOSS
PATH_RELOCATION != SCIENTIFIC_STANDING_CHANGE
REFERENCE_BREAKAGE != CLAIM_FALSIFICATION
RECOVERABLE_BY_INVENTORY != ORIGINAL_PATH_STILL_VALID

DEFERRED:
automatic reference rewriting
archive-branch policy
cold-storage admission
source deletion
generic relocation resolver
global evidence lifecycle
planning
authority
execution

CLAIM_CEILING:
One bounded repository-path relocation pressure over the six listed invariant-ledger
witness references only.
