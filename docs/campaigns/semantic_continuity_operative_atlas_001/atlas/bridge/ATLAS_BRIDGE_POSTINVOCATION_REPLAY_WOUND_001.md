# ATLAS BRIDGE POST-INVOCATION REPLAY WOUND 001

OBJECT_TYPE:
APPARATUS_FAILURE_WITNESS

OBJECT_ID:
ATLAS_BRIDGE_POSTINVOCATION_REPLAY_WOUND_001

STATUS:
FROZEN

# OBSERVED FAILURE

During ROUND017 local model fitness benchmarking, LM Studio invocations returned,
but bridge witness construction failed afterward because performance telemetry
referenced undefined variables.

Observed error:

name 'elapsed_seconds' is not defined

Because no result witness file was written, the watch loop later presented the
same request again and the operator could authorize another invocation.

# NON-COLLAPSES

MODEL INVOCATION COMPLETED
!=
RESULT WITNESS COMMITTED

RESULT WITNESS ABSENT
!=
REQUEST NEVER CONSUMED

REQUEST STILL VISIBLE
!=
SAFE TO REPLAY

POST-INFERENCE APPARATUS FAILURE
!=
MODEL FAILURE

# RISK

The current V0 queue uses existence of the final result file as its practical
consumption marker.

Therefore a failure after model invocation but before witness persistence can
cause duplicate model invocations for the same request.

This is a direct single-seat lifecycle wound.

# IMMEDIATE REPAIR

Bridge telemetry variable initialization was repaired in commit:

232ec878a1fd8d1b63d3eeaf1c9d4465585ed227

This repairs the observed exception only.

# NEXT PRESSURE

Pressure request consumption / replay semantics so that:

authorization
→ invocation begins
→ invocation receipt exists durably

before any later witness formatting or settlement stage can fail.

Candidate future relation:

AUTHORIZED_INVOCATION_STARTED
→ REQUEST_NONREPLAYABLE_BY_DEFAULT

with explicit operator override required for retry.

# CLAIM CEILING

No replay-resistance qualification is established.

The observed duplicate-invocation opportunity is evidence that replay resistance
must become an explicit bridge lifecycle surface.
