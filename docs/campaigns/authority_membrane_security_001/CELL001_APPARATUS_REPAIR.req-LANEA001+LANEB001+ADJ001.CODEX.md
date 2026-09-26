# CODEX CELL 001 APPARATUS REPAIR — POST-APPROVAL SUBSTITUTION

OBJECT_TYPE:
AUTHORITY_MEMBRANE_SECURITY_CELL_001_CODEX_REPAIR_PACKET

OBJECT_ID:
CELL001_APPARATUS_REPAIR_001

REQUIRES:
LANE_A_CELL_001_REVIEW_RESULT
+
LANE_B_CELL_001_PRESSURE_RESULT
+
AUTHORITY_MEMBRANE_SECURITY_CELL_001_ADJUDICATION_001

ROLE:
IMPLEMENTATION / APPARATUS REPAIR

TARGET:
Instantiate the already-defined Cell-001 post-review A→B pressure exactly.

DO NOT:
- alter the Cell-001 claim
- add replay
- add denial retry
- add endpoint/model/policy/executor mutation
- add network/CLI/repo-write/persistent-seat capability
- modify installed trust root
- begin Cell 002

## Required sequence

CONTROL:

load/review P0
A = SHA256(P0)
approve P0/A
execution candidate remains P0
fresh pre-call identity check confirms A
invoke boundary called exactly once

PRESSURE:

load/review P0
A = SHA256(P0)
approve P0/A
AFTER APPROVAL ONLY:
execution candidate becomes P1
B = SHA256(P1)
A != B
fresh pre-call identity check detects mismatch
invoke boundary called zero times
emit apparatus rejection / revalidation witness

## Important apparatus constraint

Do not satisfy this by mutating the production executor between review and execution.

Prefer a deterministic injectable test seam / candidate-byte provider whose only role is to expose the execution-candidate bytes immediately before the final pre-call identity check.

The production default path must remain behaviorally identical when no test seam is supplied.

## Required assertions

PRESSURE:
approve calls = 1
invoke_lmstudio calls = 0
reviewed hash = A
execution candidate hash = B
A != B
decision = REJECT or REVALIDATE
lmstudio_invoked = false

CONTROL:
approve calls = 1
invoke_lmstudio calls = 1
reviewed hash = A
execution candidate hash = A

## Required witness

The pressure witness must distinguish:
- reviewed_input_sha256
- execution_candidate_sha256
- approval occurred
- rejection occurred after approval
- invocation did not occur

Executor and policy identity must remain recorded.

## Stop condition

Return:
A. exact diff
B. exact test commands
C. control result
D. pressure result
E. witness
F. regression result
G. explicit non-target match
H. anything preventing exact A→B post-approval materialization

STOP.
