# ROUND 022 — AMBIGUOUS INVOCATION OUTCOME / RETRY PRESSURE

OBJECT_TYPE:
SINGLE_SEAT_LIFECYCLE_PRESSURE

ROLE:
BOUNDED_LIFECYCLE_EVALUATOR

MODE:
SELF_CONTAINED

AUTHORITY_EFFECT:
NONE

EXECUTION_EFFECT:
NONE

# CANDIDATE LAW

REQUEST_ID
!=
INVOCATION_ATTEMPT_ID

INVOCATION_RECEIPT
!=
PROOF_OF_MODEL_EXECUTION

TRANSPORT_FAILURE
!=
PROVEN_NONEXECUTION

RETRY
!=
REPLAY

One invocation-attempt identity may cross the consequence-producing boundary at
most once.

If execution cannot be proven and no trustworthy result witness exists, the
attempt remains:

INVOCATION_OUTCOME_UNRESOLVED

Automatic replay is denied.

A retry requires:
- a fresh attempt identity;
- predecessor linkage;
- fresh applicable authorization;
- a new budget charge.

# SPECIMEN

REQUEST_ID:
REQ-022

ATTEMPT_1_ID:
REQ-022::ATTEMPT-001

MODEL_PROFILE:
QWEN30_PROFILE_A

EVIDENCE_APERTURE:
APERTURE-022-A

AUTHORIZATION_ID:
AUTH-022-001

BUDGET:
MAX_INVOCATIONS = 2
CONSUMED_INVOCATIONS_BEFORE = 0

EVENTS:

1. REQ-022 is bound to ATTEMPT-001.
2. AUTH-022-001 authorizes exactly ATTEMPT-001 with the listed model profile and aperture.
3. A durable invocation-start receipt is written.
4. The local bridge sends the request.
5. The transport connection fails before the bridge receives a trustworthy result.
6. No result witness exists.
7. No evidence proves that the model did not execute the request.
8. An operator proposes retry.

# TASK

Evaluate the lawful post-failure state and the minimum legal retry transition.

Do not infer nonexecution from transport failure.

Do not reuse ATTEMPT-001.

Do not reuse AUTH-022-001.

Do not create scientific standing.

# REQUIRED OUTPUT

Return exactly:

REQUEST_IDENTITY:
PRESERVED | DEGRADED | UNRESOLVED

ATTEMPT_1_IDENTITY:
PRESERVED | DEGRADED | UNRESOLVED

ATTEMPT_1_OUTCOME:
INVOCATION_OUTCOME_UNRESOLVED | PROVEN_NONEXECUTION | RESULT_WITNESSED | UNRESOLVED

AUTOMATIC_REPLAY:
DENIED | ALLOWED | UNRESOLVED

RETRY_ALLOWED_FROM_CURRENT_STATE:
NO | YES | UNRESOLVED

RETRY_REQUIREMENT:
<one bounded statement>

ATTEMPT_2_ID:
REQ-022::ATTEMPT-002 | REUSE_ATTEMPT_001 | UNRESOLVED

PREDECESSOR_LINK:
REQ-022::ATTEMPT-002 -> REQ-022::ATTEMPT-001
|
NONE
|
UNRESOLVED

AUTHORIZATION_FOR_ATTEMPT_2:
FRESH_REQUIRED | AUTH_022_001_REUSABLE | UNRESOLVED

CONSUMED_INVOCATIONS_AFTER_ATTEMPT_1:
1 | 0 | UNRESOLVED

CONSUMED_INVOCATIONS_IF_ATTEMPT_2_STARTS:
2 | 1 | UNRESOLVED

SCIENTIFIC_STANDING_EFFECT:
NONE | CHANGED | UNRESOLVED

AUTHORITY_EFFECT:
NONE | EXPANDED | UNRESOLVED

MAXIMUM_WARRANTED_CLAIM:
<one bounded claim about the candidate retry semantics only>

UNRESOLVED:
<list>

Return only the required output and stop.
