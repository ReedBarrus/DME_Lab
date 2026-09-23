# CELL 002 — INSTALLED BRIDGE BINDING IMPLEMENTATION FRAME

OBJECT_TYPE:
TRANSFORMATION_FRAME

TARGET:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

PURPOSE:

Produce the exact artifact that will bind the already-promoted
principal-bound authority-consumption module into the installed
LM Studio bridge invocation chokepoint.

THIS FRAME DOES NOT ITSELF MUTATE THE INSTALLED TRUST ROOT.

# ==================================================
# FRAME A — CURRENT OPERATIVE STATE
# ==================================================

SOURCE_OBJECT_A:
INSTALLED_BRIDGE

SOURCE_LOCATION_A:
C:\Users\Admin\.dme_lab_bridge\bridge.py

EXPECTED_SOURCE_A_SHA256:
5a4c466595ec4820bd8430ee3ee91f5a38437e55bfb48a8a756dfa53c87d7fdb

SOURCE_OBJECT_B:
INSTALLED_AUTHORITY_CONSUMPTION_MODULE

SOURCE_LOCATION_B:
C:\Users\Admin\.dme_lab_bridge\local_authority_consumption_v0.py

EXPECTED_SOURCE_B_SHA256:
bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303

SOURCE_OBJECT_C:
INSTALLED_POLICY

SOURCE_LOCATION_C:
C:\Users\Admin\.dme_lab_bridge\policy.json

EXPECTED_SOURCE_C_SHA256:
65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b

CURRENT_RELATION:

bridge.py
→ human approval
→ Cell-001 post-approval identity revalidation
→ invoke_lmstudio

Authority-consumption module is installed but not yet on the
operative invocation path.

# ==================================================
# FRAME B — REQUIRED TRANSFORMATION
# ==================================================

TRANSFORMATION:

Bind each governed LM Studio invocation to one explicit
principal-bound authority envelope before invoke_lmstudio can
cross.

REQUIRED ORDER:

REQUEST / INPUT VALIDATION
→ HUMAN APPROVAL
→ CELL-001 FRESH INPUT REVALIDATION
→ AUTHORITY ENVELOPE ISSUANCE
→ PRINCIPAL CORRESPONDENCE CHECK
→ PRE-CALL ONE-USE RESERVATION
→ invoke_lmstudio
→ CONSUMPTION / INVOCATION RECEIPT

NO ORDINARY GOVERNED PATH MAY CALL invoke_lmstudio
WITHOUT PASSING THROUGH THE AUTHORITY-CONSUMPTION PRIMITIVE.

# ==================================================
# MINIMUM IDENTITY RELATION
# ==================================================

For V0, request manifests must declare:

principal_id

This is a DECLARED principal identity only.

DECLARED PRINCIPAL
!=
AUTHENTICATED PRINCIPAL

The installed bridge must also receive / observe the
attempting principal identity explicitly.

Preferred minimal V0 surface:

--principal-id <ID>

for --once / --watch execution.

The authority envelope is bound to the request-declared
principal_id.

Consumption receives:

attempting_principal_id = CLI principal identity

Required:

attempting_principal_id
==
request-declared principal_id

before reservation.

# ==================================================
# AUTHORITY ISSUANCE V0
# ==================================================

Human approval remains mandatory.

For every approved invocation candidate, mint a fresh one-shot
authority envelope locally with:

object_type
capability_id
approval_id
principal_id
request_sha256
input_sha256
model
endpoint_identity
executor_sha256
policy_sha256
use_limit = 1
remaining_uses = 1
status = ACTIVE
issued_at
expires_at = null

Capability / approval IDs must be unique enough to prevent
accidental state collision.

Current authority state must remain under:

C:\Users\Admin\.dme_lab_bridge\authority_state_v0\

The repository must not be the current-authority source.

# ==================================================
# DESTINATION STATE
# ==================================================

DESTINATION_OBJECT:
CELL002_BOUND_INSTALLED_BRIDGE_CANDIDATE

DESTINATION_ARTIFACT_REQUIRED:
A complete replacement bridge.py

DESTINATION_INSTALL_LOCATION_LATER:
C:\Users\Admin\.dme_lab_bridge\bridge.py

DO NOT INSTALL IT IN THIS IMPLEMENTATION STEP.

Also produce:

1. exact candidate bridge SHA256;
2. exact authority-module SHA256 expected;
3. exact policy SHA256 expected;
4. deterministic promotion script that:
   - verifies all pre-state hashes;
   - backs up current bridge.py;
   - replaces bridge.py with the reviewed candidate;
   - verifies destination hash;
   - leaves policy.json unchanged;
   - leaves authority module unchanged.

# ==================================================
# MATCHED TESTS REQUIRED BEFORE PROMOTION
# ==================================================

CONTROL:

request principal = P
attempting principal = P
human approval = YES
fresh CAP use_limit=1

EXPECTED:
reservation before invocation
invoke count = 1
final current authority = NONE
status = CONSUMED
receipt persists

REPLAY:

same exact CAP / approval / principal P

EXPECTED:
invoke count delta = 0
decision = DENY
reason = AUTHORITY_EXHAUSTED

WRONG PRINCIPAL:

request principal = P
attempting principal = Q

EXPECTED:
human approval occurrence may remain visible
reservation count = 0
invoke count = 0
authority remains ACTIVE / remaining=1
reason = PRINCIPAL_MISMATCH

CELL-001 REGRESSION:

approve exact input A
post-approval candidate mutates to B

EXPECTED:
Cell-001 revalidation rejects
no authority envelope should be consumed for B
invoke count = 0

# ==================================================
# HUMAN AUTHORIZATION V0
# ==================================================

NO NON-HUMAN SELF-AUTHORIZATION.

Every new active envelope requires explicit local human approval.

Agents / seats may propose request manifests containing
principal_id and desired consequence.

They may not activate the envelope themselves.

# ==================================================
# DO NOT
# ==================================================

DO NOT:
- change installed policy semantics;
- add use_limit > 1;
- add self-authorization;
- add seat / cursor spawning authority;
- add repo-write / CLI / arbitrary network authority;
- add revocation / freeze semantics yet;
- add real principal authentication;
- claim bypass resistance outside the governed bridge path;
- mutate the installed trust root during implementation.

# ==================================================
# REQUIRED RETURN
# ==================================================

Return:

A. exact diff / replacement bridge artifact;
B. candidate bridge SHA256;
C. promotion script;
D. exact source → destination transform frame;
E. control result;
F. replay result;
G. wrong-principal result;
H. Cell-001 regression result;
I. full regression count;
J. explicit remaining bypass / crash / concurrency limits.

STOP BEFORE INSTALLATION.


# ==================================================
# REVIEW FEEDBACK INTEGRATION — REQUIRED
# ==================================================

The following constraints are now part of the implementation frame.

## 1. Declared principal correspondence only

principal_id remains a DECLARED principal identity.

The wrong-principal pressure may establish only:

DECLARED PRINCIPAL CORRESPONDENCE
IS ENFORCED

It may NOT establish:

PRINCIPAL IDENTITY
IS AUTHENTICATED

Do not introduce authentication claims.

## 2. Approval-to-envelope coordinate conservation

Human approval must bind the exact same authority-material coordinates
that are written into the minted envelope.

The implementation must preserve, without recomputation/substitution drift:

request identity
input identity
model
endpoint identity
executor identity
policy identity
principal_id
invocation parameters that are authority-material

Freeze:

APPROVED COORDINATES
=
MINTED ENVELOPE COORDINATES
=
EXECUTION-BOUND COORDINATES

Any material mismatch must revalidate or stop.

Do not mint from a later independently reconstructed view of the request
if that could differ from the approved object.

## 3. Pre-call consumption ordering

Required V0 logical order:

ACTIVE
→ durable CONSUMING / one-use reservation
→ current authority unavailable to second admission
→ invoke_lmstudio
→ CONSUMED receipt

Crash recovery remains UNQUALIFIED.

The implementation must keep visible that:

CONSUMING
does not prove consequence completed

and:

MODEL INVOCATION OCCURRED
does not prove final consumption receipt persisted

Do not infer exactly-once crash-safe semantics.

## 4. Replay pressure must reuse the exact same capability object

The replay test must retain and deliberately resubmit the first issued
capability object.

It must NOT:
- request a new approval;
- mint a fresh capability;
- clone equivalent fields into a new authority instance;
- reset local state.

Freeze:

SAME FIELD VALUES
!=
SAME CAPABILITY INSTANCE

The pressure target is reuse of the exact consumed capability instance.

## 5. Promotion tooling is consequential

The promotion script must be intentionally dumb.

It may ONLY:

- verify exact current installed bridge SHA256;
- verify exact installed authority-module SHA256;
- verify exact installed policy SHA256;
- verify exact candidate bridge SHA256;
- create a backup of the installed bridge;
- replace the installed bridge from the already-reviewed candidate artifact;
- verify destination SHA256;
- stop.

It MUST NOT:

- fetch latest;
- rebuild the candidate;
- regenerate source;
- edit policy;
- install dependencies;
- mutate authority state;
- invoke the model;
- choose branches / commits dynamically.

Promotion tooling itself must return a clear transformation witness:

SOURCE OBJECT / HASH
→ COPY / REPLACE
→ DESTINATION OBJECT / HASH

## 6. Single governed invocation chokepoint

All ordinary governed LM Studio calls in the candidate bridge must cross
the same authority-consumption chokepoint.

If any ordinary path can call invoke_lmstudio without:

approval
→ Cell-001 revalidation
→ authority issue
→ principal correspondence
→ pre-call reservation

then the implementation must explicitly report that bypass and the claim
must remain scoped only to the wrapped path.

Required audit:

enumerate every call site / reachable ordinary path to invoke_lmstudio
and show whether it is governed.

Do not claim bridge-wide bypass resistance unless every ordinary path
is demonstrated governed and separately pressured as necessary.

## 7. Capability / approval identity construction

"Unique enough" is not acceptable for authority-instance identity.

Use an explicit collision-resistant construction.

Preferred acceptable V0 choices:

- cryptographically random UUID / nonce;
or
- deterministic content-addressed identity including a unique issuance nonce.

The implementation must state the exact construction.

A freshly minted authority instance with equivalent fields is not the
same capability for replay purposes.

## 8. Required risk posture in return

Return an explicit posture:

DESIGN BOUNDARY:
GOOD | FRACTURED | PARTIAL

CAPABILITY EXPANSION:
NONE | DESCRIBE

HUMAN AUTHORITY:
PRESERVED | FRACTURED

REPLAY TARGET:
CLEAN | CONFOUNDED

DECLARED PRINCIPAL CORRESPONDENCE:
QUALIFIED_CANDIDATE | FRACTURED

PRINCIPAL AUTHENTICATION:
NOT ESTABLISHED

CRASH ATOMICITY:
NOT ESTABLISHED

CONCURRENCY:
NOT ESTABLISHED

BYPASS RESISTANCE:
GOVERNED PATH ONLY | BROADER BASIS EXPLICITLY SHOWN

INSTALLATION:
NOT AUTHORIZED IN THIS STEP

## 9. Claim tattoo

The result must preserve this exact claim ceiling in substance:

CELL 002 MAY QUALIFY
ONE-SHOT CONSUMPTION
ON THE GOVERNED BRIDGE PATH.

IT DOES NOT QUALIFY
PRINCIPAL AUTHENTICATION,
CRASH RECOVERY,
CONCURRENCY,
OR BRIDGE-WIDE BYPASS RESISTANCE.

# ==================================================
# ADDITIONAL REQUIRED RETURN
# ==================================================

K. exact approval → envelope coordinate mapping;
L. exact capability_id / approval_id construction;
M. invoke_lmstudio call-site / bypass audit;
N. replay proof that the same capability instance was reused;
O. promotion-script behavior audit;
P. explicit risk posture above.
