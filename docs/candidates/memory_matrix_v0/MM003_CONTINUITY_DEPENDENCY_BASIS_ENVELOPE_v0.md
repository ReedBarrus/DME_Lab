# MM-003 Continuity Dependency Basis Envelope v0

**Status:** CANDIDATE MINIMAL REPAIR  
**Pressure:** MM-003  
**Purpose:** close the operational-dependency basis wound exposed by the cold
open audit without rewriting the qualified MM-002 carrier.

This envelope composes with:

- `traces/multi_round_deliberation_001_checkpoint.json`
- `docs/candidates/memory_matrix_v0/MM002_CHECKPOINT_BASIS_ENVELOPE_v0.md`
- `docs/candidates/memory_matrix_v0/MM002_COUNCIL_CAUSAL_LINEAGE_ENVELOPE_v0.md`

## Governing source basis

The Council deliberation and inherited continuity events belong to the frozen
pre-handoff continuity lineage:

```text
branch: continuity-delta-v0
commit: f28187306d3282a66d95b9d85e764f75751e812d
tree:   da96f8a5b5cd208d69094f4a4bf7e8271e421102
```

The retained handoff rule states that repository-relative refs in inherited
CE-000001 through CE-000010 must not be assumed to resolve against the
post-handoff branch.

Handoff witness:

`continuity/HANDOFF_BASIS.json`
→ blob `6a58ff6de5202fb42a31af5f32d31d357e11db1f`

## Exact operational dependencies

Resolve the checkpoint's operational evidence refs against the frozen source
commit above:

| Artifact | Blob SHA | Role |
| --- | --- | --- |
| `AGENT_CONTEXT.md` | `416b2aaa6469d4e201860836399b8989c95dcaff` | continuity-aware startup entry |
| `continuity/events.jsonl` | `a9e325a554ee23942e68fc1e51f5e489c5a93cff` | retained event stream through CE-000010 |
| `continuity/cursors/chatgpt.json` | `c25101bf46f0c2937c657ef154696889cf8e1602` | ChatGPT consumer coordinate |
| `continuity/cursors/codex.json` | `798ca0445c4a8e0faf9f9d9fd139db73c54d22ad` | Codex consumer coordinate |

The startup entry routes to:

| Artifact | Blob SHA | Role |
| --- | --- | --- |
| `continuity/SYNC_RITUAL.md` | `03c4384ef8fcfb3d61f679b22ea94fbbc68a6afb` | detailed synchronization ritual |
| `continuity/README.md` | `7dda8ea336366cbc49d4e38157e9acbde30f3170` | continuity contract and cursor/delta semantics |

## Minimal ritual relation preserved hot

The historical `AGENT_CONTEXT.md` requires consequential work to begin by
performing the synchronization ritual and then orienting from the
consumer-relative continuity delta.

The ritual's start sequence is:

```text
IDENTIFY_SELF
→ READ_CURSOR
→ READ_DELTA
→ ORIENT
→ RESOLVE_REQUIRED_REFS
→ DECLARE_LOCAL_CONTINUITY
→ WORK
```

After consequential work:

```text
append consequential activity
→ verify event append
→ advance cursor only through events actually consumed
```

This summary preserves the operational relation needed to understand what the
Council's proposed startup-discoverability pressure was attempting to observe.
The exact ritual remains recoverable at the pinned blob above.

## Transplant non-equivalence

The later transplant coordinate:

`cd4375dda09a2dfe5ba297de99bbef6bba38e9c9`

contains:

`AGENT_CONTEXT.md`
→ blob `5b1102a7b619985fbbcff7034acc92e2800bd71f`

That version is **not** the Council's frozen dependency basis.

Therefore:

```text
same repository path after handoff
!=
historical dependency version used by deliberation
```

The MM-002 basis envelope's transplant commit remains a valid immutable route
for the checkpoint and four round artifacts explicitly pinned there because
their blobs survived unchanged. It must not be generalized to every referenced
path.

## Repair boundary

This envelope adds only dependency-basis closure and the minimal ritual relation.

It does not add:

- new authority;
- new scientific standing;
- a generalized transitive dependency graph;
- automatic dependency discovery;
- a claim that every repository reference requires inline content;
- permission to delete raw continuity artifacts.

Candidate relation under pressure:

```text
primary carrier source closure
!=
operational dependency closure
```

This relation is not promoted to the earned invariant ledger by this artifact
alone.
