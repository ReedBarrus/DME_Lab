# Invocation Attempt Identity & Ambiguous Outcome V0 — Candidate

OBJECT_TYPE:
SINGLE_SEAT_BRIDGE_LIFECYCLE_CANDIDATE

OBJECT_ID:
INVOCATION_ATTEMPT_IDENTITY_AND_AMBIGUOUS_OUTCOME_V0

STANDING:
CANDIDATE_ONLY

# PURPOSE

Separate request identity from one consequence-producing invocation attempt and
preserve uncertainty when execution cannot be proven.

# CORE LAWS

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

HISTORICAL_AUTHORIZATION
!=
REUSABLE_AUTHORIZATION

# ATTEMPT IDENTITY

Each consequence-producing attempt receives a distinct identity.

One attempt identity may cross the invocation boundary at most once.

A retry must create a new attempt identity and bind:

RETRY_ATTEMPT_ID
→ PREDECESSOR_INVOCATION_ATTEMPT_ID

The predecessor attempt remains preserved.

# AMBIGUOUS OUTCOME HOLD

If an invocation request crosses the local invocation boundary but the system
cannot establish either:

A. a trustworthy result witness; or
B. proven nonexecution,

then the attempt enters:

INVOCATION_OUTCOME_UNRESOLVED

While unresolved:

AUTOMATIC_REPLAY:
DENIED

EXPLICIT_RETRY:
BLOCKED_BY_DEFAULT

SOURCE_ATTEMPT_IDENTITY:
PRESERVED

UNRESOLVED_CONSEQUENCE_LOAD:
PRESERVED

# RETRY REQUIREMENT

A later retry is lawful only after an explicit operator decision that creates a
new attempt identity.

The retry does not reuse predecessor authorization.

Candidate relation:

PREDECESSOR_ATTEMPT
→ unresolved or resolved disposition
→ EXPLICIT_RETRY_WARRANT
→ NEW_ATTEMPT_ID
→ FRESH_APPLICABLE_AUTHORIZATION
→ invocation

# AUTHORITY

Authorization binds to the exact attempt configuration:

- request identity
- invocation-attempt identity
- model profile
- evidence aperture
- authority envelope
- budget envelope

Changing a bound dimension invalidates the authorization for that attempt.

# BUDGET

Each started attempt consumes at least one invocation-attempt unit.

Retry consumes a new attempt unit.

Pause, resume, occupant swap, model swap, or retry may not restore already
consumed budget.

# CLAIM CEILING

This candidate specifies identity and hold semantics only.

It does not establish full replay resistance, transport truth, retry authority,
or whole-loop safety until executable pressures qualify them.
