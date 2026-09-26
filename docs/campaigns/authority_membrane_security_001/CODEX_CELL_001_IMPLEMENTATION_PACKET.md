# CODEX IMPLEMENTATION PACKET — AUTHORITY MEMBRANE CELL 001

ROLE:
IMPLEMENTATION / APPARATUS

TARGET:
AUTHORITY_MEMBRANE_SECURITY_CELL_001

OBJECTIVE:

Implement the smallest executable pressure needed to determine whether
a post-review input identity mutation can cross the current local invocation membrane.

DO NOT:
- add new capability classes
- add repo-write authority
- add network authority
- add CLI authority
- add persistent seat authority
- redesign the whole bridge
- generalize into a security framework
- weaken local approval
- move trust authority back into the repo

CURRENT TRUST BOUNDARY:

Authoritative installed executor and policy live outside the repo
under the operator's local trust root.

Repo-side bridge code is reference / candidate code only.

IMPLEMENTATION REQUIREMENTS:

1. Preserve the current happy path.

2. Add or expose a deterministic test path for:
   declared input_sha256 = A
   observed prompt bytes hash = B
   where A != B.

3. Demonstrate that the executor does NOT invoke LM Studio.

4. Emit an apparatus-authored rejection / witness record containing enough information to establish:
   - request id
   - declared input hash
   - observed input hash
   - executor hash
   - policy hash
   - decision
   - reason
   - lmstudio_invoked = false

5. Model output must not be used to prove rejection or administration state.

6. Do not rely on a human manually editing the trusted installed executor during the test.
   Prefer a bounded test fixture or harness around the reference implementation that can later be promoted after review.

7. Preserve fail-closed behavior.

TESTS REQUIRED:

CONTROL:
exact reviewed input executes through the existing one-shot path.

PRESSURE:
mutated input identity is rejected before LM Studio invocation.

NO SECONDARY PRESSURES:
do not combine replay, endpoint mutation, policy mutation, executor mutation, or denial retry into this cell.

DELIVERABLES:

A. implementation diff
B. exact test command(s)
C. control result
D. pressure result
E. witness artifacts
F. explicit statement of what was NOT tested
G. any discovered ambiguity in the current executor that prevents a clean cell

STOP CONDITION:

Stop after Cell 001 is executable and evidenced.
Do not proceed to Cell 002 without fresh authorization.
