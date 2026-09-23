# CELL 002 — INSTALLED QUALIFICATION RESULT

OBJECT_TYPE:
AUTHORITY_MEMBRANE_SECURITY_CELL_002_INSTALLED_QUALIFICATION_RESULT

STATUS:
BOUNDEDLY_QUALIFIED

INSTALLED_COORDINATES:

bridge:
C:\Users\Admin\.dme_lab_bridge\bridge.py
sha256:
0f86b8499c269ee42ed50285e4429c504ff5e6f93a6e65836128e98ef9d2bb21

authority module:
C:\Users\Admin\.dme_lab_bridge\local_authority_consumption_v0.py
sha256:
bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303

policy:
C:\Users\Admin\.dme_lab_bridge\policy.json
sha256:
65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b

HARNESS:
tests/security/run_installed_authority_membrane_cell002.py

DURABLE_WITNESS:
traces/authority_membrane_security_cell_002_installed_qualification_result.json

WITNESS_SHA256:
bb6f042b854fa619f393c9d125e6bcd87a6693d74b79d7e08b212b6d35476dd1

# ==================================================
# PRESSURE RESULTS
# ==================================================

CONTROL:

reservation observed before invocation
invocation count = 1
status = CONSUMED
remaining_uses = 0
receipt persisted

EXACT REPLAY:

same exact capability object reused
new approval = 0
new capability = 0
new reservation = 0
invocation count = 0
decision = DENY
reason = AUTHORITY_EXHAUSTED

WRONG DECLARED PRINCIPAL:

issued principal = P
attempting principal = Q
reservation count = 0
invocation count = 0
status remains ACTIVE
remaining_uses remains 1
decision = DENY
reason = PRINCIPAL_MISMATCH

CELL 001 REGRESSION:

approved input = A
post-approval candidate = B
authority issuance = 0
authority consumption = 0
invocation count = 0
reason = POST_APPROVAL_INPUT_SHA256_MISMATCH

# ==================================================
# VERIFICATION
# ==================================================

Installed pressures:
4 / 4 PASS

Relevant regressions:
50 / 50 PASS

Python compilation:
PASS

Witness validation:
PASS

git diff --check:
PASS

Real LM Studio HTTP calls:
0

Installed trust-root mutation during qualification:
NONE

Installed approve path:
exercised with deterministic local YES fixture

IMPORTANT:
This does not attest human identity.

# ==================================================
# INSTALLED STANDING
# ==================================================

CELL_002_INSTALLED_EXECUTOR:
BOUNDEDLY_QUALIFIED

CLAIM:

At the tested installed bridge, policy, authority-module,
and temporary authority-state coordinates, the governed
single-process path enforced declared-principal-bound
one-shot invocation-boundary authority, rejected exact
sequential replay, rejected a mismatched declared principal
before reservation or invocation, and preserved Cell-001
revalidation before authority issuance.

# ==================================================
# CLAIM CEILING
# ==================================================

NOT ESTABLISHED:

principal authentication
principal forgery resistance
crash-safe exactly-once execution
concurrency safety
multi-process safety
distributed replay resistance
installed default authority-state qualification
local-state tamper resistance
broader bridge bypass resistance
process containment
network containment
filesystem containment
revocation correctness
freeze correctness

FREEZE:

DECLARED PRINCIPAL CORRESPONDENCE
!=
PRINCIPAL AUTHENTICATION

TEMPORARY AUTHORITY-STATE PRESSURE
!=
DEFAULT INSTALLED AUTHORITY-STATE QUALIFICATION

GOVERNED PATH QUALIFICATION
!=
BRIDGE-WIDE BYPASS RESISTANCE
