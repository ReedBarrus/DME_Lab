# Bridge Result Settlement Rule V0 — Candidate

OBJECT_TYPE:
RESULT_SETTLEMENT_RULE_CANDIDATE

OBJECT_ID:
BRIDGE_RESULT_SETTLEMENT_RULE_V0

STANDING:
CANDIDATE_ONLY

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# PURPOSE

Separate model-output witnessing from candidate Atlas settlement.

# CORE NON-COLLAPSES

MODEL_RESPONSE
!=
RESULT_WITNESS

RESULT_WITNESS
!=
CANDIDATE_SETTLEMENT

CANDIDATE_SETTLEMENT
!=
QUALIFIED_STANDING

QUALIFIED_STANDING
!=
AUTHORITY

# V0 SETTLEMENT INPUT

A settlement decision must bind to one immutable result witness by:

- request_id
- result witness path
- result witness SHA-256 or immutable repository identity
- model identity
- source packet identity
- response body identity

The settlement process must not rewrite the witnessed model output.

# V0 SETTLEMENT UNIT

Settlement may operate on explicit result fields rather than forcing an
all-or-nothing disposition for the entire response.

Each field may receive one of:

CANDIDATE_ACCEPTED
CANDIDATE_HELD
CANDIDATE_REJECTED
UNRESOLVED

# REQUIRED SETTLEMENT RECORD

A bounded settlement record should contain:

SETTLEMENT_ID
SOURCE_WITNESS_IDENTITY
SOURCE_REQUEST_ID
SOURCE_MODEL
SETTLED_FIELDS
HELD_FIELDS
REJECTED_FIELDS
SETTLEMENT_BASIS
SCIENTIFIC_ADMISSION_CREATED
AUTHORITY_EFFECT
EXECUTION_EFFECT
UNRESOLVED

# V0 AUTHORITY

Settlement authority remains human-mediated.

A model may propose a settlement classification.

A model may not self-settle its own result.

No bridge result file is automatically promoted into Atlas state.

# FIELD-LEVEL CONSERVATION

A valid field-level settlement must preserve the exact distinction between:

- useful supported content;
- overclaim;
- contradiction;
- unresolved content.

Example:

SELECTED_PRESSURE:
CANDIDATE_ACCEPTED

CLAIM_CEILING:
CANDIDATE_HELD

does not mutate the original model response and does not imply the full response
is scientifically admissible.

# CURRENT PRESSURE TARGET

Use the frozen Round 019 planner-selection result.

Known structure:

SUPPORTED / USEFUL:
- target preservation
- selected pressure = INVOCATION_RECEIPT_REPLAY_PRESSURE
- qualified-vs-candidate separation
- authority boundary
- execution boundary

KNOWN WOUNDS:
- claim ceiling strengthened selection into validation
- one unresolved statement referred to absence of a durable marker even though
  the supplied candidate state said the durable receipt was implemented

# CLAIM CEILING

Success in the next pressure can establish only that this field-level candidate
settlement rule can distinguish useful result content from held or rejected
content in the tested specimen.

It does not establish automatic settlement, general semantic adjudication,
scientific admission, or model self-governance.
