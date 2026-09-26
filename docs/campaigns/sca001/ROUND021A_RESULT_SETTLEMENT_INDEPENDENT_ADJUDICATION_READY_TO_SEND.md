# ROUND 021A — RESULT SETTLEMENT INDEPENDENT ADJUDICATION

OBJECT_TYPE:
READY_TO_SEND_ADJUDICATION_PACKET

DESTINATION:
FRESH MODEL / FRESH THREAD

ROLE:
INDEPENDENT_SETTLEMENT_EVALUATOR

MODE:
SELF_CONTAINED

DO_NOT_USE:
prior conversation context
live chat context
source-model hidden reasoning

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# CANDIDATE SETTLEMENT LAW

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

A model may propose settlement classification.

The source-producing model must not settle its own result for this pressure.

Settlement does not rewrite source output.

# SOURCE MODEL RESULT

SOURCE_MODEL:
qwen/qwen3-coder-30b

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

UNRESOLVED_ITEM_1:
Formal replay-resistance qualification

UNRESOLVED_ITEM_2:
Whether automatic replay risk is fully mitigated when no durable
invocation-start marker exists

# SUPPLIED CANDIDATE CONTEXT

BRIDGE_INVOCATION_RECEIPT_V0 is implemented as a candidate repair:

LOCAL_APPROVAL
→ durable local invocation receipt
→ model invocation

Formal replay-resistance qualification:
NONE

Primitive stdlib tests established only:

- first receipt creation succeeds;
- duplicate receipt creation fails closed;
- explicit clear removes the receipt;
- clear does not itself invoke a model.

No full failed-invocation replay lifecycle qualification has yet been admitted.

# QUESTIONS

1. Which source fields may be retained as candidate content?
2. Which must be held or rejected because they overclaim, conflict with supplied
   candidate context, or exceed the tested standing?
3. Does the candidate field-level settlement law survive this specimen?
4. What is the maximum warranted settlement-mechanism claim?

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

NEXT_LAWFUL_PRESSURE:
<one bounded next pressure only>

UNRESOLVED:
<list>

Return only the required adjudication and stop.
