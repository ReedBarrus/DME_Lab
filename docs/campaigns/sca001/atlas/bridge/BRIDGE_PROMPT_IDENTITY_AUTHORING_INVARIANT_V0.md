# Bridge Prompt Identity Authoring Invariant V0

OBJECT_TYPE:
OPERATIVE_BRIDGE_AUTHORING_LAW

STATUS:
OPERATIVE_FOR_REQUEST_AUTHORING

# PURPOSE

Prevent request identity failures caused by conflating mutable repository state,
working-tree bytes, or author-side hash calculation with the immutable prompt
object actually executed by the local bridge.

# CORE NON-COLLAPSES

BRANCH_HEAD
!=
PROMPT_IDENTITY

WORKING_TREE
!=
PROMPT_IDENTITY

LOCAL_FILESYSTEM_BYTES
!=
AUTHORITATIVE_EXECUTION_INPUT

REQUEST_COMMIT
!=
PROMPT_CREATION_COMMIT

# AUTHORITATIVE EXECUTION INPUT

For one prompt artifact:

PROMPT_WRITE
→ PROMPT_CREATION_COMMIT P

Then:

PROMPT_IDENTITY
=
P
+
INPUT_PATH

The trusted executor resolves:

SOURCE_REF = P
+
INPUT_PATH
→ EXACT_GIT_BLOB
→ BLOB_BYTES

Those bytes are authoritative for invocation.

Later commits, later pulls, later request-manifest commits, and current checkout
state do not alter the bytes addressed by P + INPUT_PATH.

# V0 AUTHORING LAW

While LOCAL_INVOCATION_REQUEST_V0 remains installed:

1. Create prompt artifact.
2. Retain the exact commit created by that prompt write.
3. Set request.source_ref to that exact prompt-creation commit.
4. Set request.input_path to the path at that commit.
5. Resolve the Git blob from source_ref + input_path.
6. Hash the exact committed blob bytes.
7. Put that SHA-256 in request.input_sha256.
8. Create the request manifest only after those coordinates are fixed.

Do not hash the working-tree file as a substitute.

# WHY WORKING-TREE HASHING IS NOT AUTHORITATIVE

Potential differences include:

- newline normalization;
- local checkout transformations;
- author accidentally hashing a newer revision;
- prompt moved or edited after the retained source_ref;
- request creation occurring after HEAD advances.

Therefore:

SHA256(WORKING_TREE_FILE)
MAY_DIFFER_FROM
SHA256(GIT_BLOB_AT_SOURCE_REF)

# V0.1 TARGET LAW

For LOCAL_INVOCATION_REQUEST_V0_1:

REMOTE AUTHOR DECLARES:

source_ref
input_path
input_blob_sha

TRUSTED EXECUTOR RESOLVES:

source_ref + input_path
→ observed_blob_sha

and requires:

observed_blob_sha
==
declared input_blob_sha

Then the trusted executor derives:

observed_input_sha256
=
SHA256(blob_bytes)

locally.

# OBSERVATIONAL HASH ROLE

In V0.1, SHA-256 remains valuable but changes role.

It is no longer an author-computed identity coordinate.

It becomes a trusted local observation bound into:

- human approval;
- post-approval revalidation;
- authority envelope;
- durable receipt where applicable;
- invocation witness;
- audit surfaces.

Therefore:

REMOTE_IDENTITY_HANDLE:
GIT_BLOB_OID

LOCAL_OBSERVATION:
SHA256(BLOB_BYTES)

# TRUST-ROOT CONSERVATION

Changing the request identity handle must not weaken:

- local human approval;
- principal binding;
- one-shot authority consumption;
- authority nontransfer;
- post-approval input revalidation;
- post-approval coordinate revalidation;
- no tools;
- no previous-response state;
- no external retrieval;
- localhost-only model endpoint;
- no request-driven CLI;
- no repo auto-commit / merge / force push;
- trust-root auto-update prohibition.

# INSTALLED-STANDING DISTINCTION

REPO_SUPPORTS_V0_1
!=
INSTALLED_TRUST_ROOT_SUPPORTS_V0_1

INSTALLED_TRUST_ROOT_SUPPORTS_V0_1
!=
V0_1_SECURITY_PRESSURE_QUALIFIED

# CURRENT CAMPAIGN CONSEQUENCE

Round 032 successfully executed under V0 after its exact committed prompt bytes
were bound correctly.

Round 033 prompt may be prepared independently, but its invocation request
should not be armed with a guessed or placeholder V0 input_sha256.

# CLAIM CEILING

This artifact defines authoring and identity discipline only.
It does not modify the installed trust root, grant execution authority, or
qualify V0.1.
