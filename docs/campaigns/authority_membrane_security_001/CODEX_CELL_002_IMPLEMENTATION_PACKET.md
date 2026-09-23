# CODEX IMPLEMENTATION PACKET — AUTHORITY MEMBRANE CELL 002

ROLE:
IMPLEMENTATION / APPARATUS

TARGET:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

OBJECTIVE:

Implement the smallest explicit authority-consumption mechanism
needed to pressure use_limit=1 replay on the local model-invocation path.

DO NOT:
- add repo-write/network/CLI capability
- add persistent agents
- redesign policy system broadly
- add generalized token service
- add distributed consensus
- begin Cell 003
- modify installed trust root directly

MINIMUM CANDIDATE PRIMITIVE:

authority envelope with:
- capability_id
- approval_id
- request identity/hash
- input hash
- model
- endpoint identity
- executor hash
- policy hash
- use_limit
- remaining_uses
- status
- issued_at
- optional expires_at

For V0:
use_limit = 1

REQUIRED BEHAVIOR:

CONTROL:
fresh authority envelope
remaining_uses=1
→ approve exact consequence
→ consume authority
→ invoke once
→ remaining_uses=0
→ status=CONSUMED
→ emit consumption receipt

PRESSURE:
reuse exact same envelope
→ reject before invocation
→ invocation count=0
→ emit exhausted/replay denial witness
→ historical receipt remains readable
→ current authority remains NONE

IMPORTANT:

Consumption ordering must be explicit enough to avoid:
"invoke succeeded but consumption never recorded"
or
"two concurrent uses both saw remaining_uses=1"

Do not solve distributed/concurrent atomicity unless required for this single-process cell.
If atomicity is not established beyond single-process scope, state that explicitly.

STATE STORAGE:

Prefer a local trust-root-owned state surface,
not GitHub,
for current authority consumption state.

History may later be projected into Cockpit,
but current remaining authority must not be writable by the repo.

DELIVERABLES:

A. exact diff
B. authority-envelope schema / representation
C. local state path
D. control test
E. replay pressure test
F. durable consumption receipt
G. durable replay-denial witness
H. regression result
I. explicit claim ceiling
J. explicit untested race/crash boundaries

STOP after Cell 002 apparatus is executable.
