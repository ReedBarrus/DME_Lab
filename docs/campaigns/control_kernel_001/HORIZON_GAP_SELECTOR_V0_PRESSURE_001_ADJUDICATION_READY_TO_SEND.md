# CONTROL_KERNEL_001 — HORIZON_GAP_SELECTOR_V0 INDEPENDENT ADJUDICATION

PRESSURE_ID:
HORIZON_GAP_SELECTOR_V0_PRESSURE_001

CELL_ID:
CONTROL_KERNEL_CELL_003

ROLE:
FRESH_INDEPENDENT_SINGLE_GAP_OR_STOP_SELECTOR_ADJUDICATOR

MODE:
READ_ONLY
+
NO_LIVE_CHAT_CONTEXT
+
NO_REPAIR
+
NO_MULTI_GAP_RANKING
+
NO_PLANNING
+
NO_WORK_MATERIALIZATION
+
NO_ADMISSION
+
NO_AUTHORITY
+
NO_EXECUTION
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
e8cd3acd34e84c15279c275590950a6d304d2885

WITNESS_TRANSPORT_REF:
484750cc84d6e14b7b76b7fa31b2566c5bc1bfa0

PREDECESSOR_RESULT:
docs/campaigns/control_kernel_001/pressure_runs/RELATIONAL_HORIZON_V0_PRESSURE_RESULT_001.md

PREDECESSOR_BLOB:
698f8e9a50ca5690c4a331c8b996aa9ca6198195

PREDECESSOR_REQUIRED:
RELATIONAL_HORIZON_V0_MATCHED

FROZEN_EVIDENCE:
- src/control/horizon_gap_selector_v0.py
  blob 069df1107266411a41bab8594952e46ed0045605
- tests/control/test_horizon_gap_selector_v0.py
  blob cc34dd0659d1617bcdb462ed04f635901f6942cd
- tools/observe_horizon_gap_selector_v0.py
  blob 54891e276f28a3f4fe4d61775d14b706cf56bd1e
- docs/campaigns/control_kernel_001/HORIZON_GAP_SELECTOR_V0_PRESSURE_001_READY_TO_RUN.md
  blob 90281cc65a1b220f3ca79b0bcd6a0a85a477f3a7
- horizon_gap_selector_v0_observation.json
  at witness transport ref 484750cc84d6e14b7b76b7fa31b2566c5bc1bfa0
  blob be23eba7c50f1b51a0e3b1412d9f5adc07dee1ff

WITNESS_SOURCE:
e8cd3acd34e84c15279c275590950a6d304d2885

WITNESS_ONLY_TRANSPORT_REQUIRED:
YES

TARGET:
Adjudicate only whether HORIZON_GAP_SELECTOR_V0 deterministically returns the exact sole already-declared work-eligible gap from one validated represented horizon, returns NO_JUSTIFIED_WORK when zero eligible gaps exist, and rejects rather than ranks a horizon with multiple eligible gaps.

REQUIRED_ONE_GAP_CASE:
selection_posture = EXACT_ELIGIBLE_GAP
eligible_gap_count = 1
selected_gap_id = G1_STALE_SUCCESSOR_3_HANDOFF
stop_required = false

REQUIRED_ZERO_GAP_CASE:
selection_posture = NO_JUSTIFIED_WORK
eligible_gap_count = 0
selected_gap_id = null
stop_required = true

REQUIRED_MULTI_GAP_CASE:
multiple eligible gaps
→ rejected
→ not ranked

REQUIRED_BINDING:
source_horizon_id preserved
source_horizon_state_id bound
source_horizon_integrity_sha256 bound
before/after selector results bind distinct state identities for the same logical horizon

REQUIRED_NON_COLLAPSES:
DECLARED_WORK_ELIGIBLE != PLANNED
SELECTED_GAP != WORK_SPEC
SELECTED_GAP != WORK_ADMISSION
NO_JUSTIFIED_WORK != FAILURE
MULTI_GAP_REJECTION != RANKING

REQUIRED_EFFECTS:
ranking_effect = NONE
planning_effect = NONE
work_materialization_effect = NONE
work_admission_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE

CLAIM_CEILING:
At the exact supplied source, HORIZON_GAP_SELECTOR_V0 deterministically returns the exact sole already-declared work-eligible gap from one validated represented horizon, and returns NO_JUSTIFIED_WORK when no eligible gap exists. Multiple eligible gaps are rejected rather than ranked. No semantic discovery of gaps, multi-gap optimization, planning, work materialization, admission, authority, execution, or scientific standing is established.

ALLOWED_DISPOSITIONS:
HORIZON_GAP_SELECTOR_V0_MATCHED
HORIZON_GAP_SELECTOR_V0_PARTIAL
HORIZON_GAP_SELECTOR_V0_FRACTURED
HORIZON_GAP_SELECTOR_V0_UNRESOLVED

RETURN_ONLY:
PRESSURE_ID
PREDECESSOR_RELATIONAL_HORIZON
FROZEN_IMPLEMENTATION_SOURCE
WITNESS_SOURCE_MATCHED
WITNESS_ONLY_TRANSPORT
ONE_GAP_SELECTION_POSTURE
ONE_GAP_SELECTED_ID
ONE_GAP_ELIGIBLE_COUNT
ZERO_GAP_SELECTION_POSTURE
ZERO_GAP_SELECTED_ID
ZERO_GAP_ELIGIBLE_COUNT
ZERO_GAP_STOP_REQUIRED
MULTI_GAP
SAME_LOGICAL_HORIZON
STATE_SPECIFIC_BINDING
FIXED_INPUTS_DETERMINISTIC
RANKING_EFFECT
PLANNING_EFFECT
WORK_MATERIALIZATION_EFFECT
WORK_ADMISSION_EFFECT
AUTHORITY_EFFECT
EXECUTION_EFFECT
SCIENTIFIC_STANDING_EFFECT
CLAIM_CEILING_PRESERVED
DISPOSITION
UNRESOLVED
CLAIM_CEILING
STOPPED
