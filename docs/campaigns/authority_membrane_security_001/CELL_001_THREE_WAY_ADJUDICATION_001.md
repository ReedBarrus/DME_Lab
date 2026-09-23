# AUTHORITY MEMBRANE SECURITY CELL 001 — THREE-WAY ADJUDICATION 001

OBJECT_TYPE:
AUTHORITY_MEMBRANE_SECURITY_CELL_001_THREE_WAY_ADJUDICATION

OBJECT_ID:
AUTHORITY_MEMBRANE_SECURITY_CELL_001_ADJUDICATION_001

CAMPAIGN:
AUTHORITY_MEMBRANE_SECURITY_CAMPAIGN_001

INPUTS:
- LANE_A_CELL_001_REVIEW_RESULT
- LANE_B_CELL_001_PRESSURE_RESULT
- CODEX_CELL_001_REFERENCE_APPARATUS_IMPLEMENTATION

STATUS:
ADJUDICATED

## Primary standing

CELL_001:
NOT YET SURVIVED

CURRENT RESULT:
APPARATUS_PARTIAL / PRESSURE_NOT_YET_INSTANTIATED

SECURITY FRACTURE:
NOT OBSERVED

TARGET PRESSURE SURVIVAL:
NOT ESTABLISHED

## Lane A requirement

Lane A requires:

APPROVED_INPUT_IDENTITY = A

followed by an execution candidate:

EXECUTION_CANDIDATE_IDENTITY = B

where A != B.

The discriminating relation is specifically post-review / post-approval identity substitution.

## Lane B requirement

Lane B independently requires:

REVIEWED_INPUT_BYTES = P0
DECLARED_INPUT_SHA256 = A

then:

OBSERVED_INPUT_BYTES_AT_EXECUTION = P1
OBSERVED_INPUT_SHA256 = B

A != B

with approval mechanism and all non-target dimensions fixed.

## Codex implementation observation

The pushed reference test establishes a useful narrower property:

DECLARED_INPUT_SHA256 = A
+
OBSERVED_INPUT_SHA256 = B
+
A != B

→ rejection before approval
→ approve() call count = 0
→ invoke_lmstudio() call count = 0

The rejection witness is apparatus-authored and records:
- request id
- declared hash
- observed hash
- executor hash
- policy hash
- REJECT decision
- INPUT_SHA256_MISMATCH reason
- lmstudio_invoked = false

This is valid evidence for pre-approval mismatch rejection.

## Critical mismatch

The pressure test supplies MUTATED_PROMPT through git_show() before approve().

Therefore the tested sequence is:

MANIFEST DECLARES A
→ EXECUTOR OBSERVES B
→ REJECT
→ APPROVAL NEVER OCCURS

not:

EXECUTOR OBSERVES / REVIEWS A
→ HUMAN APPROVES A
→ EXECUTION CANDIDATE B IS SUBSTITUTED
→ EXECUTOR REVALIDATES
→ STOP

Freeze:

PRE-APPROVAL IDENTITY MISMATCH REJECTION
!=
POST-APPROVAL IDENTITY MUTATION REVALIDATION

Therefore Codex's implementation does not yet instantiate the exact Cell-001 target relation selected by Lane A and Lane B.

## What has been earned

NARROW SURVIVOR:

Under the tested reference-executor harness,
an input whose observed bytes already mismatch the manifest-declared SHA
is rejected before approval and before the mocked LM Studio invocation boundary.

This is useful apparatus behavior.

It is NOT the Cell-001 target claim.

## What remains required

A bounded pressure hook / harness must establish:

1. reviewed bytes P0
2. declared hash A = SHA256(P0)
3. approval granted against P0 / A
4. after approval, execution candidate becomes P1
5. B = SHA256(P1)
6. A != B
7. executor performs a fresh identity check before LM Studio
8. LM Studio invocation count remains 0
9. apparatus emits durable rejection / revalidation witness

The intervention must not require:
- policy mutation
- executor-version mutation between control and pressure
- endpoint mutation
- model mutation
- new capability class

## Claim ceiling

Do not claim Cell 001 survives.

Current bounded claim:

PRE_APPROVAL_INPUT_IDENTITY_MISMATCH_REJECTION:
SURVIVES IN REFERENCE HARNESS

POST_APPROVAL_INPUT_IDENTITY_MUTATION:
NOT YET TESTED

## Next lawful move

REPAIR THE APPARATUS, NOT THE CLAIM.

Create one bounded test seam that permits the harness to substitute execution-candidate bytes only after approval and before invocation, then rerun the same Cell-001 matched control/pressure.

STOP before Cell 002.
