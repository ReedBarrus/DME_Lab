# Ledger Runtime Pressure v0

## Status

Synthetic ledger harness executed.

Runtime scope remained:

```text
synthetic envelope generation
-> append
-> JSONL persistence
-> replay
-> integrity verification
-> test evidence
```

No reconstruction, live OS capture, semantic interpretation, causality, consequence, admissibility, feedback, agents, databases, services, content addressing, hash chains, or resolved amendment views were introduced.

## Integrity Boundary Tested

Per-record integrity hashes cover:

```text
canonical JSON of the ledger record without its integrity field,
using sort_keys=True and compact separators
```

The hashed boundary includes:

- `record_id`
- `commit_index`
- complete `envelope`

It excludes the `integrity` object itself.

This detects mutation of committed content. It does not establish truth, authenticity, causality, or semantic correctness.

## Guarantees Tested

- deterministic order
- stable identity
- envelope preservation
- integrity
- missingness preservation
- append-only amendment

## Test Results

- tests passed: 6
- tests failed: 0
- runtime evidence: `traces/ledger_runtime_pressure_v0.json`

## Observed Pressure

- Ordering conflict survived: replay stayed in `commit_index` order while source sequence and event time disagreed.
- Identity collision survived: duplicate envelope identity did not merge distinct ledger records.
- Envelope preservation survived: opaque payload, explicit null, missing field, and unusual valid values replayed without repair or default filling.
- Integrity mutation survived: post-commit persisted-content mutation was detected by per-record hash verification.
- Missingness survived: `absent`, `explicit_null`, `unavailable`, and `malformed` remained structurally distinct.
- Append-only amendment survived: original and amendment both replayed in commit order, with no resolved view produced.

## Hidden Assumptions Surfaced

- JSON serialization stability is now part of the v0 integrity hypothesis.
- Complete-envelope storage is adequate for tiny synthetic fixtures, but storage pressure has not been meaningfully tested.
- Single local writer is adequate for deterministic commit assignment in this harness only.
- Amendment lookup cost is untested because raw replay does not resolve amendments.
- Missingness is represented by a small structural convention, not by a semantic model.

## Choices Still Adequate

- local JSONL persistence
- one complete envelope per ledger record
- single local writer
- generated `record_id`
- monotonic `commit_index`
- raw replay in canonical commit order
- per-record hash over explicit canonical boundary
- synthetic envelopes before live OS capture

## Choices Under Pressure

- JSONL remains provisional because integrity depends on canonical JSON serialization.
- Complete-envelope storage remains provisional because repeated payload/provenance growth was not stressed.
- Amendment labels remain provisional because no resolved amendment view exists.
- Missingness representation remains provisional until more malformed or unavailable source shapes appear.

## Contract Amendment Recommendation

Do not amend `docs/contracts/ledger.md` from this run alone.

The current contract already names the distinctions this harness exercised. Runtime evidence supports the narrow v0 contract under synthetic pressure, but does not yet justify stronger claims.

## Storage Recommendation

Keep JSONL and complete-envelope storage as provisional v0 choices.

Reconsider them only after observed pressure from larger fixtures, unstable canonicalization, replay cost, verification cost, amendment lookup cost, or repeated content duplication.

## Recommended Next Smallest Question

What is the smallest machine-readable ledger schema that can describe the tested record boundary without adding semantic fields?

