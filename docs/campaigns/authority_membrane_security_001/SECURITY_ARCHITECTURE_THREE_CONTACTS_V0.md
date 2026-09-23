# SECURITY ARCHITECTURE — THREE CONTACTS V0

STATUS:
PROVISIONAL LARGE-SCALE SECURITY SHAPE

## Contact 1 — Authority bond / bridge

Question:

MAY THIS CONSEQUENCE BEGIN?

Responsibilities:

- exact request / principal / capability correspondence;
- human operator authorization V0;
- bounded authority envelopes;
- consumption accounting;
- denial;
- current authority state;
- receipts.

## Contact 2 — Consequence monitor

Question:

IS REALIZED ACTIVITY STILL WITHIN THE WARRANTED ENVELOPE?

Responsibilities:

- observe activity attributable to an admitted envelope;
- correlate activity with capability / principal / task;
- detect scope or budget departure;
- request freeze / revoke / quarantine / escalation;
- preserve evidence;
- feed Cockpit.

This layer does not silently expand authority.

## Contact 3 — Environmental membrane

Question:

CAN OUT-OF-ENVELOPE CONSEQUENCE PHYSICALLY / LOGICALLY PROPAGATE?

Responsibilities may include, when later implemented:

- process boundaries;
- filesystem boundaries;
- network boundaries;
- credential scoping;
- hardware access;
- CLI chokepoints;
- child-process / replication controls.

The environmental membrane provides the corrective teeth.

## Roles / ecology

Roles are a fourth, softer defense layer:

- peer challenge;
- refusal;
- domain tension;
- scientific review;
- anomaly surfacing;
- social / semantic coregulation.

ROLE COREGULATION
!=
PRIMARY CONTAINMENT

Security should survive role malfunction within the declared
technical control range.

## Membrane integrity target

A future installed membrane should detect unauthorized mutation
of its own trusted state / executable identity.

Candidate future response:

trusted-state identity mismatch
-> reject new requests
-> freeze active warrants where safely possible
-> isolate rupture
-> preserve evidence
-> enter RECOVERY_REQUIRED
-> request operator repair

Do not claim this behavior until explicitly implemented and pressured.

## Large-scale objective

PRE-CONSEQUENCE AUTHORITY CONTROL
+
IN-CONSEQUENCE OBSERVATION
+
ENVIRONMENTAL CONTAINMENT
+
ROLE COREGULATION

with Cockpit as the human legibility / request surface,
not the root of authority.
