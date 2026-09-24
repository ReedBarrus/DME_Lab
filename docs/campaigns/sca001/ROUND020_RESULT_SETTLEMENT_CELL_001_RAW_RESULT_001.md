# ROUND 020 — RESULT SETTLEMENT CELL 001 — RAW RESULT 001

OBJECT_TYPE:
RAW_SETTLEMENT_RESULT

OBJECT_ID:
ROUND020_RESULT_SETTLEMENT_CELL_001_RAW_RESULT_001

STATUS:
FROZEN_NOT_ADMITTED

SOURCE_REQUEST:
ROUND020_RESULT_SETTLEMENT_CELL_001

SOURCE_MODEL:
qwen/qwen3-coder-30b

SETTLEMENT_RULE_RECOVERY:
RECOVERED

TARGET_PRESERVED:
CANDIDATE_ACCEPTED

SELECTED_PRESSURE:
CANDIDATE_ACCEPTED

SELECTION_BASIS:
CANDIDATE_ACCEPTED

QUALIFIED_VS_CANDIDATE_SEPARATION:
CANDIDATE_ACCEPTED

AUTHORITY_BOUNDARY:
CANDIDATE_ACCEPTED

EXECUTION_BOUNDARY:
CANDIDATE_ACCEPTED

CLAIM_CEILING:
CANDIDATE_ACCEPTED

UNRESOLVED_ITEM_1:
UNRESOLVED

UNRESOLVED_ITEM_2:
UNRESOLVED

SCIENTIFIC_ADMISSION_CREATED:
NONE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SETTLEMENT_DISPOSITION:
FIELD_LEVEL_CANDIDATE_SETTLEMENT_RECOVERED

MAXIMUM_WARRANTED_CLAIM:
The replay resistance mechanism of the bridge invocation receipt is tested and
validated, ensuring failed invocations cannot be automatically replayed without
explicit clearance.

# REVIEW WOUNDS

WOUND_1:
CLAIM_CEILING_ACCEPTED_DESPITE_OVERCLAIM

The source claim strengthened pressure selection into validation of replay
resistance. The candidate settlement rule explicitly exists to distinguish
useful content from overclaim. Accepting this field defeats the pressure.

WOUND_2:
SOURCE_MODEL_EQUALS_SETTLEMENT_MODEL

The source planner result and the settlement evaluator were both produced by
qwen/qwen3-coder-30b.

The candidate rule states:

A model may propose a settlement classification.
A model may not self-settle its own result.

At minimum, same-model settlement standing is unresolved and cannot be treated
as satisfying the intended independence boundary without a separate warrant.

WOUND_3:
STALE_UNRESOLVED_CONTENT_NOT_CLASSIFIED

The source unresolved item about "no durable invocation-start marker" conflicts
with the supplied candidate context stating that a durable receipt is now
implemented. The evaluator left it UNRESOLVED rather than classifying the
stale/inconsistent content.

# DISPOSITION

SETTLEMENT_MECHANISM_NOT_YET_QUALIFIED

The raw output is preserved as pressure evidence only.
