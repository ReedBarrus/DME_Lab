# G15 Pressure 001 Ready To Run

PRESSURE_ID:
OPERATIVE_CURRENTNESS_RECONSTRUCTION_V0_PRESSURE_001

HORIZON_SELECTION_BLOB:
ed738ef043653555df50cf5d0843f4d5d926dad3

CONTRACT_BLOB:
b2fa2484e64cd287099d1bda173d94c4dedfc5b0

CONTROL_CARRIER:
docs/campaigns/operative_currentness_reconstruction_001/specimens/
OPERATIVE_CURRENTNESS_CONTROL_CARRIER_V0.json

CONTROL_BLOB:
00d6122d40ae3b4d9cf16b6ed2e3186c3cec7d47

ABLATION_CARRIER:
docs/campaigns/operative_currentness_reconstruction_001/specimens/
OPERATIVE_CURRENTNESS_ABLATION_CARRIER_V0.json

ABLATION_BLOB:
c9a87dada6fb1e3e860756a4772decb3b61e0c04

RUN:
two fresh independent reconstruction threads

READ:
only the assigned carrier

DO NOT:
read the other carrier
open source handles
use live chat context
infer currentness from task or packet labels
infer unsupported coordinates

RETURN:
CAMPAIGN_POSTURE
CURRENT_HORIZON_POSTURE
NEXT_PRESSURE
SUCCESSOR_POSTURE
NEXT_PRESSURE_ALLOWED

MISSING_RULE:
UNRESOLVED_FROM_CARRIER

CONTROL_EXPECTATION:
CAMPAIGN_POSTURE = CLOSED
CURRENT_HORIZON_POSTURE = CLOSED
NEXT_PRESSURE = null
SUCCESSOR_POSTURE = NO_SUCCESSOR
NEXT_PRESSURE_ALLOWED = false

ABLATION_EXPECTATION:
all five requested currentness coordinates = UNRESOLVED_FROM_CARRIER

STOP:
after five returned fields
