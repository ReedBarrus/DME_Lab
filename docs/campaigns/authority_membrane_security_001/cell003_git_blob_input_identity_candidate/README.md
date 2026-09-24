# Cell 003 — Git Blob Input Identity Candidate

STATUS: REPO CANDIDATE / NOT INSTALLED

This candidate is derived from the qualified Cell 002 installed-bridge candidate.

It changes one author-facing input identity coordinate:

```
V0:
input_sha256 = author-declared SHA256 of committed prompt bytes

V0.1:
input_blob_sha = author-declared Git blob OID
```

The trusted executor still derives SHA-256 from the immutable blob bytes and
binds that observed SHA-256 into human approval, post-approval revalidation,
the one-shot authority envelope, and the invocation witness.

## Preserved membrane

- trust root remains local and pinned;
- no auto-update;
- local human approval required;
- principal-bound authority required;
- one-shot authority consumption unchanged;
- consumed authority non-reusable;
- authority module unchanged;
- installed policy unchanged;
- no tools / previous response state / external retrieval / arbitrary network;
- localhost LM Studio only;
- no repo auto-commit, merge, or force push;
- post-approval byte and coordinate revalidation remain fail-closed.

## New V0.1 request identity

```
source_ref
+
input_path
+
input_blob_sha
```

The executor independently resolves the Git blob at `source_ref + input_path`
and requires the observed blob OID to equal `input_blob_sha` before approval.

Then:

```
observed_input_sha256 = SHA256(exact Git blob bytes)
```

is computed locally.

## Standing

```
REPO CANDIDATE IMPLEMENTED
!=
INSTALLED TRUST ROOT PROMOTED
!=
SECURITY PRESSURE QUALIFIED
```


## Result witness routing

Invocation result witnesses are experiment artifacts and are written to:

```
<repo_root>/bridge/results/
```

The local trust root retains installed executor, policy, and authority-bearing
state only.

Therefore:

```
RESULT WITNESS STORAGE
!=
AUTHORITY STATE STORAGE
```

Writing a witness into the repository working tree does not grant commit,
merge, push, or other Git mutation authority.
