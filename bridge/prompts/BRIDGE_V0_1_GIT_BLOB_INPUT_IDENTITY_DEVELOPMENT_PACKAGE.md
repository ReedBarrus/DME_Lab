# BRIDGE V0.1 — GIT BLOB INPUT IDENTITY DEVELOPMENT PACKAGE

OBJECT_TYPE:
READY_TO_SEND_DEVELOPMENT_PACKAGE

ADDRESS:
FRESH CHATGPT DEVELOPMENT THREAD / BRIDGE SECURITY IMPLEMENTER

REPOSITORY:
ReedBarrus/DME_Lab

BRANCH:
draci-v0-candidate-basis

MODE:
IMPLEMENTATION + TESTS + PROMOTION_CANDIDATE
NO_LIVE_CHAT_CONTEXT_REQUIRED

# TARGET

Evolve the installed LM Studio trust-root bridge so remote request manifests no
longer require a manually precomputed prompt SHA-256.

The current installed bridge is principal-bound, human-approved, one-shot, and
fail-closed. Preserve those properties exactly.

The new request identity should use the immutable Git blob object id resolved
from:

SOURCE_REF + INPUT_PATH

instead of requiring the remote request author to manually supply the prompt's
SHA-256.

The bridge must still compute SHA-256 locally after resolving the immutable blob
and bind that observed SHA-256 into approval, authority, receipt, and witness
surfaces.

# MOTIVATING WOUND

Current request authoring requires:

input_sha256:
<manually precomputed sha256>

The installed bridge independently resolves:

source_ref + input_path
→ immutable prompt bytes
→ observed sha256

This has repeatedly caused fail-closed rejections due to author-side hash
mismatch, even though the immutable Git prompt object itself is correctly
addressed.

Desired distinction:

REMOTE AUTHOR DECLARED CONTENT HASH
!=
TRUSTED EXECUTOR OBSERVED CONTENT HASH

and:

IMMUTABLE GIT OBJECT ID
=
STABLE REMOTE HANDLE

# AUTHORITATIVE CURRENT INSTALLED-BRIDGE CANDIDATE

Read:

docs/campaigns/authority_membrane_security_001/
cell002_bound_installed_bridge_candidate/bridge.py

and:

docs/campaigns/authority_membrane_security_001/
cell002_bound_installed_bridge_candidate/promote.ps1

and:

tests/security/test_cell002_bound_installed_bridge_candidate.py

Also inspect:

src/runtime/local_authority_consumption_v0.py

bridge/CURRENT.md

# NON-NEGOTIABLE CONSERVATION

Preserve all existing security properties:

- local trust root remains outside repo
- trust_root_auto_update = false
- repo may not modify installed executor automatically
- repo may not modify installed policy automatically
- human approval remains required
- principal binding remains required
- authority use_limit remains exactly 1
- consumed authority cannot be reused
- no model tools
- no previous-response state
- no external retrieval
- no arbitrary network
- no CLI authority
- no repo auto-commit / merge / force push
- post-approval coordinate revalidation remains fail-closed
- model invocation remains inside authority consumer only

# NEW REQUEST SCHEMA

Add backward-compatible support for:

schema_version:
LOCAL_INVOCATION_REQUEST_V0_1

V0.1 replaces:

input_sha256

with:

input_blob_sha

where input_blob_sha is the exact 40-character Git blob OID for input_path at
source_ref.

Suggested V0.1 manifest fields:

schema_version
request_id
enabled
source_ref
input_path
input_blob_sha
principal_id
model
temperature
max_tokens
purpose

Keep V0 request parsing operational if possible.

# REQUIRED RESOLUTION LAW

The trusted executor must resolve:

source_ref
+
input_path
→ observed Git blob OID
→ blob bytes

Then require:

observed_blob_oid == declared input_blob_sha

before local approval.

If mismatch:

REJECT
lmstudio_invoked = false
authority_issued = false

# LOCAL DERIVED HASH LAW

After immutable blob resolution, the trusted executor computes:

observed_input_sha256 = SHA256(blob_bytes)

This SHA-256 must remain part of:

- approval candidate
- post-approval input revalidation
- authority envelope
- invocation witness
- any relevant durable receipt / audit surface

The remote request author no longer needs to compute it.

# APPROVAL DISPLAY

Human approval should show at least:

request_id
principal_id
source_ref
input_path
input_blob_sha
observed_input_sha256
request_manifest_sha256
model
temperature
max_tokens
endpoint identity
executor sha256
policy sha256

# TESTS REQUIRED

Create a new security cell / test family rather than silently editing prior
qualified evidence.

Required tests:

1. V0.1 control:
   matching source_ref + path + blob OID reaches approval and invocation.

2. Blob mismatch:
   declared blob OID differs from resolved blob OID
   → reject before approval / authority / invocation.

3. Content revalidation:
   execution candidate differs after approval
   → reject before authority issuance exactly as current Cell 001 law requires.

4. Principal mismatch:
   preserve existing denial behavior.

5. One-shot replay:
   preserve existing authority exhaustion behavior.

6. V0 compatibility:
   prior input_sha256 manifests remain accepted under the old schema if
   backward compatibility is retained.

7. Structural call-site check:
   only one invoke_lmstudio call remains and it stays inside the authority
   consumer.

8. Promotion script:
   fixed-hash, explicit, local-human-operated promotion only.
   No auto-update path.

# ARTIFACT TOPOLOGY

Prefer a new candidate family, e.g.:

docs/campaigns/authority_membrane_security_001/
cell003_git_blob_input_identity_candidate/

containing:

bridge.py
promote.ps1
README.md or candidate law

and corresponding tests under:

tests/security/

Do not overwrite Cell 002 evidence.

# OPERATIVE SURFACE UPDATE

After tests pass, update:

bridge/CURRENT.md
OPERATIVE_SURFACE_MAP.md
PROJECT_STATE.md

to distinguish:

REPO CANDIDATE IMPLEMENTED
!=
INSTALLED TRUST ROOT PROMOTED
!=
SECURITY PRESSURE QUALIFIED

# ROUND 032 COMPATIBILITY NOTE

The current Round 032 prompt Git blob OID on branch at package creation is:

967c3c2e33c71f0b717b9b7b0d30ba9eb0c1c7e2

Current prompt path:

bridge/prompts/ROUND032_POST_SETTLEMENT_NONLINEAR_ROUTING_READY_TO_SEND.md

Do not alter Round 032 scientific content as part of this bridge upgrade.

# REQUIRED RETURN

Return:

IMPLEMENTATION_STATUS:
COMPLETE | PARTIAL | BLOCKED

FILES_CREATED_OR_CHANGED:
<list>

TESTS_RUN:
<commands and results>

SECURITY_PROPERTIES_PRESERVED:
<list>

NEW_REQUEST_SCHEMA:
<exact schema>

PROMOTION_STATUS:
NOT_INSTALLED | INSTALLED_UNQUALIFIED | OTHER

UNRESOLVED:
<list>

MAXIMUM_WARRANTED_CLAIM:
<one bounded claim>

# STOP

Do not claim the installed trust root changed unless the explicit local promotion
step actually occurred and was verified.
