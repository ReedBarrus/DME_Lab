# Single-Seat Atlas Lifecycle Operator Map V0 — Candidate

OBJECT_TYPE:
SINGLE_SEAT_LIFECYCLE_OPERATOR_MAP

OBJECT_ID:
SINGLE_SEAT_ATLAS_LIFECYCLE_OPERATOR_MAP_V0

STANDING:
CANDIDATE_ONLY

# PURPOSE

Make the basic single-seat lifecycle explicit as a relationally continuous set
of operators over Atlas-carried state, bridge invocation mechanics, cells,
metabolism, and authority boundaries.

# CORE ENTITIES

SEAT:
stable role-address and lifecycle contract

OCCUPANT:
replaceable model instance performing one bounded operation

ATLAS_STATE:
reconstructable target, trajectory, standing, provenance, unresolved load,
horizon, and operator-facing state

CELL:
bounded pressure object with explicit inputs, outputs, claim ceiling, and stop

RESULT_WITNESS:
immutable observation of one invocation consequence

SETTLEMENT_RECORD:
field-level candidate classification over a witnessed result

QUALIFICATION_RECORD:
separate adjudication that may change scientific standing

AUTHORITY_ENVELOPE:
current bounded permission surface

BUDGET_ENVELOPE:
candidate future bound over compute, calls, time, tokens, retries, or other
consequence capacity

# LIFECYCLE STATES

S0 DORMANT
seat exists; no occupant materialized

S1 RECOVERING
candidate occupant reconstructs current Atlas state

S2 READY
state recovered; current target/horizon/standing/unresolved load legible

S3 PRESSURE_SELECTED
exactly one bounded pressure selected

S4 INVOCATION_PROPOSED
request manifest binds pressure, model, evidence aperture, and generation bounds

S5 AUTHORIZED
local human approval granted for one invocation

S6 INVOCATION_STARTED
durable local receipt exists; automatic replay denied

S7 RESULT_WITNESSED
exact model output and invocation metadata durably witnessed

S8 SETTLEMENT_PENDING
witness exists but no field-level candidate settlement exists yet

S9 CANDIDATE_SETTLED
supported / held / rejected / unresolved fields explicitly classified

S10 ADJUDICATION_PENDING
candidate settlement may be sent to an independent evaluator

S11 QUALIFIED_UPDATE
a bounded qualification decision is recorded

S12 ATLAS_UPDATED
new state frame incorporates only warranted changes while preserving lineage

S13 PAUSED
seat lifecycle intentionally halted without state erasure

S14 STOPPED
no further invocation may occur absent a new explicit activation transition

# BASIC OPERATORS

O1 RECOVER_STATE
DORMANT → RECOVERING → READY

O2 SELECT_PRESSURE
READY → PRESSURE_SELECTED

O3 BIND_INVOCATION
PRESSURE_SELECTED → INVOCATION_PROPOSED

O4 AUTHORIZE_ONCE
INVOCATION_PROPOSED → AUTHORIZED

O5 BEGIN_INVOCATION
AUTHORIZED → INVOCATION_STARTED

O6 WITNESS_RESULT
INVOCATION_STARTED → RESULT_WITNESSED

O7 OPEN_SETTLEMENT
RESULT_WITNESSED → SETTLEMENT_PENDING

O8 SETTLE_FIELDS
SETTLEMENT_PENDING → CANDIDATE_SETTLED

O9 REQUEST_ADJUDICATION
CANDIDATE_SETTLED → ADJUDICATION_PENDING

O10 APPLY_QUALIFICATION
ADJUDICATION_PENDING → QUALIFIED_UPDATE

O11 UPDATE_ATLAS_STATE
QUALIFIED_UPDATE → ATLAS_UPDATED

O12 RETURN_READY
ATLAS_UPDATED → READY

O13 PAUSE
READY | PRESSURE_SELECTED | INVOCATION_PROPOSED | RESULT_WITNESSED |
SETTLEMENT_PENDING | CANDIDATE_SETTLED | ADJUDICATION_PENDING → PAUSED

O14 RESUME
PAUSED → RECOVERING

O15 STOP
any non-terminal state → STOPPED

O16 EXPLICIT_RETRY
failed INVOCATION_STARTED with retained receipt
→ operator clears receipt under explicit retry warrant
→ INVOCATION_PROPOSED
A new local approval remains required.

O17 OCCUPANT_SWAP
DORMANT | READY | PAUSED
→ new occupant materialization
→ RECOVERING
Seat lineage must remain distinct from occupant identity.

O18 MODEL_PROFILE_SELECT
PRESSURE_SELECTED
→ choose one qualified or candidate model profile
→ INVOCATION_PROPOSED
Model selection does not modify seat authority.

# FAILURE / HOLD STATES

F1 STATE_RECOVERY_UNRESOLVED
missing load-bearing Atlas field
→ no pressure selection

F2 REQUEST_IDENTITY_REJECTED
manifest/input mismatch
→ no authorization

F3 MODEL_LOAD_FAILED_AFTER_RECEIPT
receipt retained
→ automatic replay denied

F4 RESPONSE_WITNESS_FAILED
receipt retained
→ automatic replay denied

F5 SETTLEMENT_UNRESOLVED
witness remains immutable
→ no automatic qualification

F6 ADJUDICATION_REJECTED
candidate standing does not advance

F7 ATLAS_UPDATE_CONFLICT
qualification exists but state update cannot be applied coherently
→ explicit unresolved / repair pressure

# RELATIONAL CONTINUITY

The intended loop is:

ATLAS STATE
→ CELL / PRESSURE
→ REQUEST
→ AUTHORIZATION
→ INVOCATION RECEIPT
→ MODEL CONSEQUENCE
→ RESULT WITNESS
→ FIELD SETTLEMENT
→ INDEPENDENT ADJUDICATION
→ QUALIFIED CHANGE
→ ATLAS STATE UPDATE
→ NEXT RECOVERY

# METABOLIC INTERFACE

The seat consumes bounded Atlas structure and produces witnessed candidate
structure.

Metabolism occurs only when useful consequence-bearing structure moves from a
fragile live process into reconstructable external structure while preserving:

- identity;
- provenance;
- claim ceiling;
- challenge path;
- authority boundary;
- unresolved load.

Therefore:

MODEL OUTPUT
!=
METABOLIZED STATE

and:

WITNESS + SETTLEMENT + QUALIFICATION + ATLAS UPDATE
=>
CANDIDATE METABOLIC PATH

No generic autonomous metabolism is claimed.

# CELL INTERFACE

Every pressure cell should bind:

CELL_ID
INPUT_STATE_IDENTITY
PRESSURE_TARGET
ALLOWED_OPERATOR
EVIDENCE_APERTURE
MODEL_PROFILE
AUTHORITY_ENVELOPE
BUDGET_ENVELOPE
REQUIRED_OUTPUT
FAILURE_POSTURE
CLAIM_CEILING
STOP_CONDITION

# BUDGET INTERFACE — NOT YET QUALIFIED

Candidate budget dimensions:

MAX_INVOCATIONS
MAX_RETRIES
MAX_PROMPT_TOKENS
MAX_COMPLETION_TOKENS
MAX_WALL_SECONDS
MAX_MODEL_LOADS
MAX_EVIDENCE_BYTES
MAX_SETTLEMENT_PASSES
MAX_ADJUDICATION_PASSES

Budget exhaustion should produce:

BUDGET_EXHAUSTED
→ PAUSE OR STOP
→ NO SILENT CONTINUATION

# CURRENT QUALIFIED / OPERABLE SURFACES

Boundedly evidenced:
- Atlas-only planner state recovery
- occupant succession continuity
- request identity binding
- local human one-shot approval
- model invocation without tools/repo/network
- result witnessing
- invocation receipt primitive fail-closed duplicate creation
- explicit receipt clearing primitive
- bounded model-profile observation

Candidate / unresolved:
- field-level settlement
- independent settlement evaluator rule
- replay resistance across actual failed invocation lifecycle
- pause/resume lifecycle
- stop semantics
- Atlas state update after qualification
- model swap under one seat contract
- budget envelope
- event-based firing
- autonomous routing
- automatic qualification
- automatic Atlas mutation

# CLAIM CEILING

This map is a candidate lifecycle topology, not a qualified runtime.

Its purpose is to expose missing operators and dependency order so each seam can
be independently pressured before the loop is run as a whole.
