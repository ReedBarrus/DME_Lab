# ATLAS LOCAL SEAT INVOCATION ROUND 013

OBJECT_TYPE:
LOCAL_SEAT_INVOCATION_ROUND

OBJECT_ID:
ATLAS_LOCAL_SEAT_INVOCATION_ROUND_013

TRANSPORT:
LOCAL_LMSTUDIO_BRIDGE_V0

HUMAN_ACTION:
ONE_LOCAL_COMMAND_PLUS_PER_INVOCATION_KEYSTROKE_APPROVAL

# TASK A

REQUEST:
bridge/requests/ROUND013_PLANNER_SUCCESSION_ADJUDICATION.json

MODEL:
qwen/qwen3-coder-30b

PURPOSE:
Fresh adjudication of planner-seat occupant succession continuity.

# TASK B

REQUEST:
bridge/requests/ROUND013_COMPRESSION_VARIANT_RUN_A.json

MODEL:
microsoft/phi-4

PURPOSE:
Fresh Run A reconstruction of the further-reduced metabolic compression specimen.

# AUTHORITY CONTRACT

REMOTE_REQUEST
!=
LOCAL_AUTHORIZATION

Each invocation requires the local bridge approval keystroke.

No model tools.
No repository access by the model.
No connectors.
No prior-response state.
No automatic result push.

# OPERATOR PROCEDURE

From the DME_Lab checkout:

python tools/local_lmstudio_bridge_v0.py --once

Review each invocation summary and approve only the intended request.

# EXPECTED RESULTS

bridge/results/ROUND013_PLANNER_SUCCESSION_ADJUDICATION.json

bridge/results/ROUND013_COMPRESSION_VARIANT_RUN_A.json

# RETURN CONTRACT

Return the assistant_text field from both result witnesses, preserving task identity.

ROUND013-A_RESULT:
<assistant_text from planner succession adjudication>

ROUND013-B_RESULT:
<assistant_text from compression variant Run A>
