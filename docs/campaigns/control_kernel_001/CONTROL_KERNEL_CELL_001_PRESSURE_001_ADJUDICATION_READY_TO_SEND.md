# CONTROL_KERNEL_001 — CELL 001 INDEPENDENT ADJUDICATION

PRESSURE_ID:
CONTROL_KERNEL_CELL_001_PRESSURE_001

ROLE:
FRESH_INDEPENDENT_EXTERNAL_ONE_GAP_CALIBRATION_ADJUDICATOR

MODE:
READ_ONLY
+
NO_LIVE_CHAT_CONTEXT
+
NO_REPAIR
+
NO_MACHINE_GAP_SELECTION
+
NO_GENERALIZED_HORIZON_REPRESENTATION
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
4ade4448871e30b630f72ded79335eeebde4d396

WITNESS_TRANSPORT_REF:
272a3c1b445923e40e5f1676522881b30dfd30c1

PREDECESSOR_RESULT:
docs/campaigns/workcycle_stabilization_001/pressure_runs/MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_PRESSURE_RESULT_001.md

PREDECESSOR_BLOB:
3488108dcf974d03262406e6dc39cdb883189263

PREDECESSOR_REQUIRED:
MATERIALIZED_RECONCILIATION_SUCCESSOR_PROJECTION_MATCHED

FROZEN_EVIDENCE:
- docs/campaigns/control_kernel_001/state/CONTROL_KERNEL_CELL_001_SPECIMEN_V0.json
  blob 3875683a77294648cc84a522e40f467e5a8a2ddc
- src/control/control_kernel_cell_001_v0.py
  blob 37e997d2e33af48f1940457fa025dc5ebeccc06f
- tests/control/test_control_kernel_cell_001_v0.py
  blob ebcd23cbb767889221f3ed0bace2d0703b2bfeac
- tools/observe_control_kernel_cell_001_v0.py
  blob 559a65f9cb3fb15b42fbfcf443ab33fbd173029c
- docs/campaigns/control_kernel_001/CONTROL_KERNEL_CELL_001_PRESSURE_001_READY_TO_RUN.md
  blob 5038396104e8a641345d89f6c057a6bebdae3ba7
- control_kernel_cell_001_observation.json
  at witness transport ref 272a3c1b445923e40e5f1676522881b30dfd30c1
  blob 32faec55330cf1243c858377241edf77f4822ce8

WITNESS_SOURCE:
4ade4448871e30b630f72ded79335eeebde4d396

WITNESS_ONLY_TRANSPORT_REQUIRED:
YES

TARGET:
Adjudicate only whether one externally supplied operative horizon with exactly one externally supplied live gap and no competing gaps can be reconciled against one bounded observed repository repair such that the supplied gap is removed and the cell terminates with NO_JUSTIFIED_WORK and STOP.

REQUIRED_BOOTSTRAP_POSTURE:
selection_source = EXTERNALLY_SUPPLIED
machine_selection_claimed = false
exactly one supplied live gap
competing_gaps = []
selection_problem = NONE

REQUIRED_REPOSITORY_OBSERVATION:
precondition_present_before = true
postcondition_present_after = true
bounded_delta_observed = true
changed_paths = exactly:
docs/projections/POST_CONSEQUENCE_SPINE_CONTROL_ECONOMY_PROJECTIONS_V0.md

REQUIRED_TERMINAL_POSTURE:
horizon_posture = HORIZON_SATISFIED
remaining_gap_ids = []
terminal_posture = NO_JUSTIFIED_WORK
stop_required = true

REQUIRED_NON_COLLAPSES:
EXTERNALLY_SUPPLIED_GAP != MACHINE_SELECTED_GAP
ONE_GAP_CALIBRATION != GENERALIZED_HORIZON_REPRESENTATION
NO_JUSTIFIED_WORK != FAILURE
STOP != FIND_SOMETHING_ELSE
OBSERVED_REPOSITORY_CHANGE != CELL_EXECUTION_AUTHORITY

REQUIRED_EFFECTS:
gap_selection_effect = NONE
work_materialization_effect = NONE
work_admission_effect = NONE
authority_effect = NONE
execution_effect = NONE
scientific_standing_effect = NONE

CLAIM_CEILING:
At the exact supplied source, one externally supplied operative horizon with exactly one externally supplied live gap and no competing gaps can be reconciled against one bounded observed repository repair. Once that repair removes the supplied gap, the cell returns HORIZON_SATISFIED, an empty supplied gap set, NO_JUSTIFIED_WORK, and STOP. The cell does not establish generalized relational-horizon representation, machine gap selection, multi-gap ranking, planning automation, authority, execution, or scientific standing.

ALLOWED_DISPOSITIONS:
CONTROL_KERNEL_CELL_001_MATCHED
CONTROL_KERNEL_CELL_001_PARTIAL
CONTROL_KERNEL_CELL_001_FRACTURED
CONTROL_KERNEL_CELL_001_UNRESOLVED

RETURN_ONLY:
PRESSURE_ID
PREDECESSOR_SUCCESSOR_OR_NO_SUCCESSOR
FROZEN_IMPLEMENTATION_SOURCE
WITNESS_SOURCE_MATCHED
WITNESS_ONLY_TRANSPORT
EXTERNALLY_SUPPLIED_HORIZON
MACHINE_SELECTION_CLAIMED
EXACTLY_ONE_SUPPLIED_GAP
COMPETING_GAPS
PRECONDITION_OBSERVED
POSTCONDITION_OBSERVED
BOUNDED_REPOSITORY_DELTA
HORIZON_POSTURE
REMAINING_GAP_IDS
TERMINAL_POSTURE
STOP_REQUIRED
GAP_SELECTION_EFFECT
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
