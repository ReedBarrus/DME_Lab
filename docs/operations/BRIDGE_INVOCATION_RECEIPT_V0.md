# Bridge Invocation Receipt V0

OBJECT_TYPE:
BRIDGE_LIFECYCLE_CONTROL

OBJECT_ID:
BRIDGE_INVOCATION_RECEIPT_V0

STANDING:
IMPLEMENTED_CANDIDATE

IMPLEMENTATION:
tools/local_lmstudio_bridge_v0.py

LOCAL_STATE:
bridge/local/invocation_receipts/

# PURPOSE

Close the post-authorization replay wound exposed when a model invocation
completed but witness construction failed.

# CURRENT RELATION

LOCAL_APPROVAL
→ write durable invocation receipt
→ invoke LM Studio

If invocation or later witness construction fails:

receipt remains

and:

AUTOMATIC_REPLAY:
DENIED

A later watch cycle must not prompt for the same request again.

# MANUAL RETRY

Retry requires explicit local operator action:

python tools/local_lmstudio_bridge_v0.py --clear-receipt REQUEST_ID

Clearing the receipt does not itself invoke the model.

Any later invocation still requires the normal local y approval.

# NON-COLLAPSES

REQUEST_VISIBLE
!=
REQUEST_REPLAYABLE

RESULT_WITNESS_ABSENT
!=
INVOCATION_NEVER_STARTED

RETRY
!=
AUTOMATIC_REPLAY

RECEIPT
!=
SCIENTIFIC_SETTLEMENT

# CURRENT LIMIT

The receipt is local runtime state, not yet an Atlas lifecycle object.

No crash-consistency claim beyond local file persistence is qualified yet.
No cross-machine replay fencing is established.
