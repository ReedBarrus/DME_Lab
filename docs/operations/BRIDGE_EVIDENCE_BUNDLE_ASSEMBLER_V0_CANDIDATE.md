# Bridge Evidence Bundle Assembler V0 — Candidate

## Standing

CANDIDATE_ONLY

This document specifies a narrow evidence-selection and assembly surface for the
Local LM Studio bridge. It does not grant repository access to the model and
does not create publication, write, tool, network, or execution authority.

## Problem

Current Local LM Studio bridge requests can point at one immutable prompt artifact.
That is sufficient for self-contained packets.

It is not sufficient for packets that reference several required evidence files because:

PACKET REFERENCES EVIDENCE != MODEL RECEIVES EVIDENCE

The Round 014 compression adjudication exposed this failure mode.

## Target

request manifest
→ exact evidence coordinates
→ immutable blob resolution
→ identity verification
→ deterministic extraction / assembly
→ bounded model-visible bundle
→ bundle identity witness
→ local human approval
→ one model invocation

while preserving:

MODEL HAS EVIDENCE != MODEL HAS REPOSITORY ACCESS
BUNDLE ASSEMBLY != SCIENTIFIC INTERPRETATION
EVIDENCE SELECTION != AUTHORITY TO PROMOTE

## Candidate evidence item

Each evidence item should minimally declare:

{
  "label": "CELL_002_RUN_A",
  "source_ref": "<40-char commit SHA>",
  "path": "<allowlisted repo-relative path>",
  "sha256": "<expected exact bytes SHA-256>",
  "mode": "full_text"
}

V0 should support only full_text.

No semantic extraction, summarization, search, regex slicing, or model-selected retrieval
in the first version. That keeps the first apparatus deterministic.

## Candidate bundle manifest

A request may declare LOCAL_INVOCATION_REQUEST_V1 with:
- one immutable instruction object (source_ref, path, sha256);
- an ordered evidence array of immutable evidence items;
- model, temperature, max_tokens, and purpose.

## Deterministic assembly

The bridge should construct exactly one UTF-8 bundle in manifest order:

=== INSTRUCTION ===
<exact instruction bytes>

=== EVIDENCE 001: <label> ===
SOURCE_REF: <sha>
PATH: <path>
SHA256: <sha256>

<exact evidence bytes>

Evidence order must equal manifest order. No hidden context may be added.
The assembled bundle receives its own SHA-256.

## Approval surface

Before invocation, show:
- request id and purpose;
- model;
- instruction identity;
- evidence count;
- each evidence label/path/source ref;
- total bundle bytes;
- final bundle SHA-256;
- temperature and token ceiling;
- tools: NONE;
- history: NONE;
- repository access by model: NONE.

The local y remains the V0 authorization membrane.

## Result witness extension

The witness should add:
- bundle_schema_version;
- bundle_sha256;
- bundle_bytes;
- evidence_count;
- evidence_items with label, source_ref, path, declared_sha256, observed_sha256.

## Failure behavior

Reject before approval and before LM Studio invocation if:
- an evidence path is outside allowlisted prefixes;
- a source ref is not an exact immutable commit;
- path resolution fails;
- exact bytes do not match declared SHA-256;
- item count exceeds a policy ceiling;
- assembled bundle exceeds a policy byte ceiling;
- any item is not UTF-8;
- a duplicate label exists;
- an unsupported extraction mode is requested.

Desired behavior:

MISSING / MUTATED / UNREADABLE EVIDENCE
→ EXPLICIT REJECTION
→ LM STUDIO NOT INVOKED

## Deliberately absent in V0

No model repository browsing, semantic file search, recursive directory ingestion,
model-directed retrieval, automatic source discovery, arbitrary local filesystem reads,
model tools, network tools, automatic result publication, or automatic Atlas settlement.

## Later extractor layer

Only after full-text bundle assembly is stable should a separate extractor surface be pressured.
Potential later mechanical modes:
- exact line range;
- exact heading range;
- deterministic JSON pointer;
- deterministic object-id extraction.

Semantic search / model-directed evidence selection should remain a later, separately
authorized surface because it changes the epistemic aperture rather than merely
transporting named evidence.

## Development consequence

EVIDENCE COORDINATES
→ BOUNDED APERTURE
→ MODEL COGNITION

without collapsing the aperture into repository access.

That is suitable for current single-seat testing and later comparison against Atlas-seated retrieval.
