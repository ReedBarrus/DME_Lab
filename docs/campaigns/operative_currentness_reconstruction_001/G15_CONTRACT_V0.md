# G15 Operative Currentness Reconstruction Contract V0

STATUS:
CANDIDATE

TARGET_RELATION:
PLANNING_OR_TASK_ARTIFACT != CURRENT_OPERATIVE_STATE

CONTROL_CARRIER_BLOB:
00d6122d40ae3b4d9cf16b6ed2e3186c3cec7d47

ABLATION_CARRIER_BLOB:
c9a87dada6fb1e3e860756a4772decb3b61e0c04

CONTROL_REQUIRED_RETURN:

CAMPAIGN_POSTURE = CLOSED
CURRENT_HORIZON_POSTURE = CLOSED
NEXT_PRESSURE = null
SUCCESSOR_POSTURE = NO_SUCCESSOR
NEXT_PRESSURE_ALLOWED = false

ABLATION_REQUIRED_RETURN:

CAMPAIGN_POSTURE = UNRESOLVED_FROM_CARRIER
CURRENT_HORIZON_POSTURE = UNRESOLVED_FROM_CARRIER
NEXT_PRESSURE = UNRESOLVED_FROM_CARRIER
SUCCESSOR_POSTURE = UNRESOLVED_FROM_CARRIER
NEXT_PRESSURE_ALLOWED = UNRESOLVED_FROM_CARRIER

RECONSTRUCTION_RULE:

If a requested currentness coordinate is not explicitly supported by the carrier,
return UNRESOLVED_FROM_CARRIER.

Do not infer current operative state from:
- ACTIVE_CANDIDATE_SEQUENCE;
- READY_TO_SEND_WORK_PACKET;
- artifact existence;
- historical task readiness;
- source-handle availability.

CANDIDATE_MATCHED_RELATION:

CONTROL exact currentness reconstructs
+
ABLATION currentness does not reconstruct
+
the same non-authoritative planning/task surfaces remain visible
->
OPERATIVE_CURRENTNESS_RECONSTRUCTION_LOAD = YES

NONCLAIMS:

This does not establish:
- a generic currentness resolver;
- cross-campaign precedence;
- task ranking;
- planning activation;
- work selection;
- authority;
- execution;
- scientific standing.

CLAIM_CEILING:
One bounded WORKCYCLE_STABILIZATION_001 reconstruction test only.
