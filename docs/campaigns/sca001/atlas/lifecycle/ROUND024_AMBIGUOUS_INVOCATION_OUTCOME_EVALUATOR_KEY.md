# ROUND 024 — AMBIGUOUS INVOCATION OUTCOME EVALUATOR KEY

OBJECT_TYPE:
EVALUATOR_ONLY_KEY

DO_NOT_SEND_WITH_SOURCE_PACKET

# EXPECTED LOAD-BEARING INTERPRETATION

REQUEST_IDENTITY:
source value PRESERVED is compatible with the candidate law.

ATTEMPT_1_IDENTITY:
source value DEGRADED conflicts with SOURCE_ATTEMPT_IDENTITY:PRESERVED.
Outcome uncertainty does not erase or degrade the durable identity of the
attempt that crossed the boundary.

ATTEMPT_1_OUTCOME:
INVOCATION_OUTCOME_UNRESOLVED is the expected post-failure outcome.

AUTOMATIC_REPLAY:
DENIED is expected.

RETRY_ALLOWED_FROM_CURRENT_STATE:
YES conflicts with EXPLICIT_RETRY:BLOCKED_BY_DEFAULT because the specimen says
only that an operator proposes retry. It does not supply an explicit retry
warrant.

RETRY_REQUIREMENT:
The listed structural requirements are substantially correct for a later lawful
retry, but the timing/gate must remain explicit.

ATTEMPT_2_ID:
REQ-022::ATTEMPT-002 is a coherent candidate identity for a later retry, not
evidence that retry is already authorized.

PREDECESSOR_LINK:
the supplied link preserves lineage.

AUTHORIZATION_FOR_ATTEMPT_2:
FRESH_REQUIRED is expected.

CONSUMED_INVOCATIONS_AFTER_ATTEMPT_1:
1 is expected because the attempt crossed the invocation boundary.

CONSUMED_INVOCATIONS_IF_ATTEMPT_2_STARTS:
2 is expected conditionally if a later warranted ATTEMPT_2 actually starts.

SCIENTIFIC_STANDING_EFFECT:
NONE is expected.

AUTHORITY_EFFECT:
NONE is expected.

MAXIMUM_WARRANTED_CLAIM_FIELD:
likely reject or hold because "legally permissible" is temporally ambiguous and
can imply permission from the present unresolved state rather than permission
only after an explicit retry warrant and fresh authorization.

# EXPECTED CONSERVATION

ATTEMPT_IDENTITY_CONSERVATION:
VIOLATED by source field ATTEMPT_1_IDENTITY:DEGRADED

RETRY_WARRANT_GATE:
VIOLATED by source field RETRY_ALLOWED_FROM_CURRENT_STATE:YES

REQUEST_ATTEMPT_SEPARATION:
otherwise preserved

RETRY_REPLAY_SEPARATION:
partially preserved in structure, but current-state retry gating is defective

AUTHORIZATION_NONTRANSFER:
preserved

BUDGET_MONOTONICITY:
preserved

# EXPECTED ROUTING

REPAIR_REQUIRED_BEFORE_NEXT_LIFECYCLE_PRESSURE:
YES

SMALLEST_REPAIR:
pressure only the two failed distinctions:

1. ATTEMPT identity remains preserved while OUTCOME remains unresolved.
2. RETRY remains blocked after a proposal and becomes eligible only after an
   explicit retry warrant; later retry then requires new attempt identity, fresh
   authorization, predecessor linkage, and a new budget charge.

Do not broaden into authority consumption until this repaired seam survives.

# CLAIM CEILING

The expected result is a field-level candidate adjudication only.

No qualification is created by matching this key.
