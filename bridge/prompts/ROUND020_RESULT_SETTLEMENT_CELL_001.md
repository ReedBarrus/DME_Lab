# ROUND 020 — RESULT SETTLEMENT CELL 001

OBJECT_TYPE:
RESULT_SETTLEMENT_PRESSURE

ROLE:
INDEPENDENT_SETTLEMENT_EVALUATOR

MODE:
SELF_CONTAINED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# CANDIDATE RULE

MODEL_RESPONSE
!=
RESULT_WITNESS
!=
CANDIDATE_SETTLEMENT
!=
QUALIFIED_STANDING
!=
AUTHORITY

Settlement is field-level.

Allowed field dispositions:

CANDIDATE_ACCEPTED
CANDIDATE_HELD
CANDIDATE_REJECTED
UNRESOLVED

A model may propose settlement classification but may not self-settle its own
result.

Settlement does not rewrite source output.

# SOURCE RESULT

SOURCE_REQUEST_ID:
ROUND019_SINGLE_SEAT_PLANNER_FINITE_SELECTION

SOURCE_MODEL:
qwen/qwen3-coder-30b

SOURCE_FIELDS:

TARGET_PRESERVED:
YES

SELECTED_PRESSURE:
INVOCATION_RECEIPT_REPLAY_PRESSURE

SELECTION_BASIS:
The newest unqualified load-bearing repair is the formal replay-resistance
qualification for BRIDGE_INVOCATION_RECEIPT_V0, currently NONE. The pressure
directly tests whether a failed invocation after receipt creation can replay
without explicit clearing.

QUALIFIED_VS_CANDIDATE_SEPARATION:
PRESERVED

AUTHORITY_BOUNDARY:
CONSERVED

EXECUTION_BOUNDARY:
CONSERVED

CLAIM_CEILING:
This selection tests and validates the replay resistance mechanism of the
bridge invocation receipt, ensuring failed invocations cannot be automatically
replayed without explicit clearance.

UNRESOLVED:
- Formal replay-resistance qualification
- Whether automatic replay risk is fully mitigated when no durable
  invocation-start marker exists

# KNOWN SOURCE CONTEXT

The supplied candidate state explicitly stated:

BRIDGE_INVOCATION_RECEIPT_V0 is implemented as a candidate repair:

LOCAL_APPROVAL
→ durable local invocation receipt
→ model invocation

Formal replay-resistance qualification:
NONE

# TASK

Apply the candidate settlement rule to the source fields.

Do not adjudicate whether replay resistance itself is established.

Do not improve or rewrite the source result.

Distinguish supported candidate content from overclaim and stale/inconsistent
content.

# REQUIRED OUTPUT

Return exactly:

SETTLEMENT_RULE_RECOVERY:
RECOVERED | PARTIAL | UNRESOLVED

TARGET_PRESERVED:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

SELECTED_PRESSURE:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

SELECTION_BASIS:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

QUALIFIED_VS_CANDIDATE_SEPARATION:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

AUTHORITY_BOUNDARY:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

EXECUTION_BOUNDARY:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

CLAIM_CEILING:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

UNRESOLVED_ITEM_1:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

UNRESOLVED_ITEM_2:
CANDIDATE_ACCEPTED | CANDIDATE_HELD | CANDIDATE_REJECTED | UNRESOLVED

SCIENTIFIC_ADMISSION_CREATED:
NONE

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

SETTLEMENT_DISPOSITION:
FIELD_LEVEL_CANDIDATE_SETTLEMENT_RECOVERED
|
FIELD_LEVEL_CANDIDATE_SETTLEMENT_PARTIAL
|
FIELD_LEVEL_CANDIDATE_SETTLEMENT_FAILED
|
UNRESOLVED

MAXIMUM_WARRANTED_CLAIM:
<one bounded claim about the settlement mechanism only>

UNRESOLVED:
<list>

Return only the required output and stop.
