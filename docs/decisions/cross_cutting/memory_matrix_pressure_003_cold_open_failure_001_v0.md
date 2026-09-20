# Memory Matrix Pressure 003 — Cold Open Failure 001

**Status:** VALID COLD-AUDIT FAILURE / MINIMAL REPAIR ACTIVE  
**Pressure:** MM-003  
**Specimen:** qualified MM-002 compositional carrier  
**Observer outcome:** one independent FAIL, one independent PASS  
**Adjudication:** FAIL is valid after immutable-source verification

## Cold-audit finding

One observer identified a consequential dependency-closure gap that the
enumerated MM-002 prompts never named:

```text
deliberation source closure
!=
operational dependency closure
```

The MM-002 checkpoint names these non-round evidence refs:

- `AGENT_CONTEXT.md`
- `continuity/events.jsonl`
- `continuity/cursors/chatgpt.json`
- `continuity/cursors/codex.json`

and its surviving proposal depends on an existing continuity / synchronization
ritual.

The MM-002 basis envelope pinned the checkpoint and four Council rounds, but did
not explicitly pin the historical versions of those operational dependencies
or the ritual definition they reference.

## Verification against immutable history

The failure is stronger than a missing-SHA complaint.

The continuity handoff artifact states that repository-relative refs in
inherited CE-000001 through CE-000010 must **not** be assumed to resolve against
the post-handoff branch. It identifies the frozen source lineage as:

```text
source branch: continuity-delta-v0
source commit: f28187306d3282a66d95b9d85e764f75751e812d
source tree:   da96f8a5b5cd208d69094f4a4bf7e8271e421102
```

At that source commit:

`AGENT_CONTEXT.md`
→ blob `416b2aaa6469d4e201860836399b8989c95dcaff`

explicitly routes consequential startup through:

`continuity/SYNC_RITUAL.md`
→ blob `03c4384ef8fcfb3d61f679b22ea94fbbc68a6afb`

At the later transplant commit used by the MM-002 basis envelope:

`cd4375dda09a2dfe5ba297de99bbef6bba38e9c9:AGENT_CONTEXT.md`
→ blob `5b1102a7b619985fbbcff7034acc92e2800bd71f`

That is a different file version and does **not** carry the same durable
continuity-startup text.

Therefore:

```text
round/checkpoint blobs survived transplant unchanged
!=
all referenced dependency paths preserved the same historical content
```

The MM-002 basis envelope remains valid for the checkpoint and four round
artifacts it explicitly pins. It is insufficient as closure for every
repository-relative dependency named by the checkpoint.

## Additional exact dependency coordinates

At the frozen source commit
`f28187306d3282a66d95b9d85e764f75751e812d`:

| Dependency | Blob SHA |
| --- | --- |
| `AGENT_CONTEXT.md` | `416b2aaa6469d4e201860836399b8989c95dcaff` |
| `continuity/SYNC_RITUAL.md` | `03c4384ef8fcfb3d61f679b22ea94fbbc68a6afb` |
| `continuity/README.md` | `7dda8ea336366cbc49d4e38157e9acbde30f3170` |
| `continuity/events.jsonl` | `a9e325a554ee23942e68fc1e51f5e489c5a93cff` |
| `continuity/cursors/chatgpt.json` | `c25101bf46f0c2937c657ef154696889cf8e1602` |
| `continuity/cursors/codex.json` | `798ca0445c4a8e0faf9f9d9fd139db73c54d22ad` |

The retained handoff artifact is:

`continuity/HANDOFF_BASIS.json`
→ blob `6a58ff6de5202fb42a31af5f32d31d357e11db1f`

## Divergent observer result

A second independent cold observer returned PASS and did not identify this
dependency-basis wound.

That PASS remains evidence about what that observer successfully reconstructed.
It does not erase the verified failure.

```text
one cold-audit PASS
!=
absence of a consequential loss
```

No generalized claim about observer quality is earned.

## Smallest repair

Do not rewrite the checkpoint, MM-002 basis envelope, or causal envelope.

Add only:

`docs/candidates/memory_matrix_v0/MM003_CONTINUITY_DEPENDENCY_BASIS_ENVELOPE_v0.md`

to preserve:

1. the correct pre-handoff dependency basis;
2. exact identities for the checkpoint's operational evidence refs;
3. the exact ritual-definition route;
4. the fact that transplant-path resolution is not a valid substitute when
   content changed.

No new invariant is promoted until the repaired carrier survives targeted
verification and another fresh cold audit.
