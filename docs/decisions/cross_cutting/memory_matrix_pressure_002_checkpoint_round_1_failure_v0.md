# Memory Matrix Pressure 002 — Checkpoint-Only Round 1 Failure

**Status:** TWO INDEPENDENT FAILURES / MINIMAL REPAIR ACTIVE  
**Pressure:** MM-002  
**Checkpoint blob:** `0cad066f48de2a42a45017487ec2bcde855fbaa6`  
**Observers:** Claude and Gemini, operator-supplied independent reconstructions

## Convergent result

Both observers successfully reconstructed from the checkpoint alone:

- frontier before and after;
- three considered proposal states;
- why the read-only inspect path fractured;
- why the startup-pointer pressure survived;
- three earned distinctions;
- unresolved residue;
- unchanged authority and standing;
- explicit non-implementation;
- recommended next pressure;
- materially relevant measurements.

Both independently returned:

`CHECKPOINT MEMORY ROUND-TRIP FAILS`

## Shared smallest consequential loss

The checkpoint's `EVIDENCE_REFS` contain repository-relative paths but no
immutable commit or blob coordinates for the four underlying Council rounds.

Therefore:

```text
checkpoint can name its sources
!=
checkpoint can re-resolve the exact historical source versions
```

This violates the historical source-closure rule earned by MM-001.

## Secondary candidate loss

Both observers also noted that the checkpoint pools deliberation outcomes and
does not fully reconstruct which actor/round introduced, attacked, displaced,
or accepted each consequential transition.

That issue is **not repaired yet**.

It remains intentionally exposed so Round 2 can determine whether actor/round
causal attribution is actually consequential after immutable basis closure is
restored.

## Minimal repair

Do not rewrite the checkpoint.

Add only:

`docs/candidates/memory_matrix_v0/MM002_CHECKPOINT_BASIS_ENVELOPE_v0.md`

containing the shared immutable historical commit and exact blob SHA for each
round artifact.

Round 2 tests:

```text
existing checkpoint
+
minimal basis envelope
```

No generalized memory schema or new deliberation packet is earned by this
repair.
