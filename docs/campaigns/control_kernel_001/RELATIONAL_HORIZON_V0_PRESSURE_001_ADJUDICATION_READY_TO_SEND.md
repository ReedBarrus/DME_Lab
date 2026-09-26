# CONTROL_KERNEL_001 — RELATIONAL_HORIZON_V0 INDEPENDENT ADJUDICATION

PRESSURE_ID:
RELATIONAL_HORIZON_V0_PRESSURE_001

CELL_ID:
CONTROL_KERNEL_CELL_002

ROLE:
FRESH_INDEPENDENT_RELATIONAL_HORIZON_REPRESENTATION_ADJUDICATOR

MODE:
READ_ONLY
+
NO_LIVE_CHAT_CONTEXT
+
NO_REPAIR
+
NO_GAP_SELECTION
+
NO_RANKING
+
NO_WORK_JUSTIFICATION
+
NO_PLANNING
+
NO_AUTHORITY
+
NO_EXECUTION
+
NO_SCIENTIFIC_PROMOTION

IMPLEMENTATION_SOURCE_REF:
88dfac53e6e78f63a8833383e3415f210f05e57d

WITNESS_TRANSPORT_REF:
511d4ce3697c8a6d88d8230f98f2ed56f09fdacb

PREDECESSOR_RESULT:
docs/campaigns/control_kernel_001/pressure_runs/CONTROL_KERNEL_CELL_001_PRESSURE_RESULT_001.md

PREDECESSOR_BLOB:
932e14cc6e6a99a2f4aa06115fd86d6c30879737

PREDECESSOR_REQUIRED:
CONTROL_KERNEL_CELL_001_MATCHED

FROZEN_EVIDENCE:
- src/control/relational_horizon_v0.py
  blob 73ea154933c81bd9758f86aa4ab1a31cf6f7f037
- tests/control/test_relational_horizon_v0.py
  blob f631af1d4e9f85574044c60b3932939bdf390d91
- tools/observe_relational_horizon_v0.py
  blob aac7f6f204fc56fbd0b1e848bceec0122b8a3a70
- docs/campaigns/control_kernel_001/RELATIONAL_HORIZON_V0_PRESSURE_001_READY_TO_RUN.md
  blob b1a0389d39b44ee80c0e9f8ea005c2919b6098be
- relational_horizon_v0_observation.json
  at witness transport ref 511d4ce3697c8a6d88d8230f98f2ed56f09fdacb
  blob a7f4e14c932f361db9c21178ef70edd5bc404a1d

WITNESS_SOURCE:
88dfac53e6e78f63a8833383e3415f210f05e57d

WITNESS_ONLY_TRANSPORT_REQUIRED:
YES

TARGET:
Adjudicate only whether RELATIONAL_HORIZON_V0 can mechanically represent the same logical externally supplied horizon before and after one bounded repository consequence while state identity changes with posture/gap state.

REQUIRED_BEFORE:
horizon_id = H1_POST_CONSEQUENCE_PHASE_HANDOFF
posture = PARTIAL
exactly one declared gap = G1_STALE_SUCCESSOR_3_HANDOFF
representation_source = EXTERNALLY_SUPPLIED

REQUIRED_AFTER:
same horizon_id
posture = CLOSED
declared gap set = []
representation_source = EXTERNALLY_SUPPLIED

REQUIRED_IDENTITY:
horizon_id(before) = horizon_id(after)
horizon_state_id(before) != horizon_state_id(after)
integrity(before) != integrity(after)

REQUIRED_EVIDENCE:
before source contains stale SUCCESSOR_3 activation gate
after source contains successor-or-no-successor terminal gate
both source refs are exactly the supplied bounded repository evidence

REQUIRED_NON_COLLAPSES:
HORIZON_ID != HORIZON_STATE_ID
REPRESENTED_GAP != SELECTED_GAP
REPRESENTATION != WORK_JUSTIFICATION
CHALLENGE_POSTURE != AUTOMATIC_WORK
CLOSED_HORIZON != NEW_WORK_SEARCH

REQUIRED_EFFECTS:
gap_selection_effect = NONE
work_justification_effect = NONE
work_materialization_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE

CLAIM_CEILING:
At the exact supplied source, one externally supplied relational horizon can mechanically represent the same stable logical horizon before and after one bounded repository consequence while its state identity changes from PARTIAL with one declared live gap to CLOSED with an empty declared gap set. No gap selection, ranking, work justification, planning, authority, execution, or scientific standing is established.

ALLOWED_DISPOSITIONS:
RELATIONAL_HORIZON_V0_MATCHED
RELATIONAL_HORIZON_V0_PARTIAL
RELATIONAL_HORIZON_V0_FRACTURED
RELATIONAL_HORIZON_V0_UNRESOLVED

RETURN_ONLY:
PRESSURE_ID
PREDECESSOR_CONTROL_KERNEL_CELL_001
FROZEN_IMPLEMENTATION_SOURCE
WITNESS_SOURCE_MATCHED
WITNESS_ONLY_TRANSPORT
BEFORE_EVIDENCE_OBSERVED
AFTER_EVIDENCE_OBSERVED
LOGICAL_HORIZON_IDENTITY_PRESERVED
HORIZON_STATE_IDENTITY_CHANGED
INTEGRITY_CHANGED
BEFORE_POSTURE
BEFORE_DECLARED_GAP_COUNT
BEFORE_GAP_ID
AFTER_POSTURE
AFTER_DECLARED_GAP_COUNT
REPRESENTATION_SOURCE
GAP_SELECTION_EFFECT
WORK_JUSTIFICATION_EFFECT
WORK_MATERIALIZATION_EFFECT
AUTHORITY_EFFECT
EXECUTION_EFFECT
SCIENTIFIC_STANDING_EFFECT
CLAIM_CEILING_PRESERVED
DISPOSITION
UNRESOLVED
CLAIM_CEILING
STOPPED
