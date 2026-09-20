# Four-Root Round-Trip Basis Failure v0

## Status

**TEST-HARNESS FAILURE / NO COMPRESSION VERDICT**

This record preserves the first attempted independent round-trip test of the
four-root authority-spine compression candidate.

The attempt does not count as evidence for or against semantic compression
quality because the candidate four-root basis was not independently recoverable
to the observer.

## Prior candidate

Compression candidate decision:

`docs/decisions/cross_cutting/four_root_authority_spine_compression_candidate_v0.md`

Candidate commit:

`135de31e3401dbd7ff6f84ec1fdc4229482425a3`

The candidate root contents existed only as embedded fenced sections inside that
decision record.

The live repository roots remained unchanged.

## Observed failure

The independent observer correctly refused to substitute:

- the old live root documents;
- prior conversational descriptions;
- or the containing decision record as though it were the four candidate roots.

It reported:

```text
COMPRESSION ROUND-TRIP FAILS
```

but the failure discriminator was the supplied basis, not recovered semantic
loss.

The observer could recover only the pre-compression live roots and therefore
could not determine whether the candidate roots preserved, relocated,
superseded, or omitted consequential information.

## Smallest consequential loss

```text
candidate authority surface
not independently recoverable
```

Therefore:

```text
missing candidate basis
→ round-trip test cannot begin
```

This is upstream of every semantic compression question.

## Classification

```text
semantic compression verdict:
UNTESTED

candidate authority loss:
UNESTABLISHED

test harness:
FAILED

failure cause:
candidate roots embedded but not independently addressable
```

The failure does not authorize changing the candidate semantics.

## Packaging repair

The exact four candidate roots were materialized as **non-authoritative
candidate files** under:

`docs/candidates/four_root_authority_spine_v0/`

Files:

- `README.md`
- `PROJECT_STATE.md`
- `WORKFLOW.md`
- `AGENT_CONTEXT.md`

Only repository-relative links were rebased where necessary so the candidate
files can route an observer to the same lower evidence from their candidate
directory.

No live root file was modified.

Candidate materialization commits:

- README: `add9ca1fedc5a1a4f49e97896025c3de5c6597b0`
- PROJECT_STATE: `a33fadbb91147442cfed348ec37d0ea8a5480ad5`
- WORKFLOW: `8a9fc92ec17aa64d1635147aed21fa0fc883dea8`
- AGENT_CONTEXT: `9da950bebb308bc01afe1f6e33bdeef3c9970bef`

## Forced testing distinction

This pressure supports:

```text
semantic recoverability
requires
basis recoverability
```

and:

```text
candidate described in another artifact
!=
candidate supplied as test basis
```

This is retained as pressure evidence, not promoted as a universal formal rule.

## Next pressure

Repeat the independent compression round-trip using the four explicit candidate
paths as the only root authority basis.

The observer may follow repository links exposed by those candidate roots, but
must not substitute the live root files or prior conversation.

The semantic round-trip passes only if current governing state and consequential
lineage remain recoverable without relying on the old live roots for authority.

Live root migration remains unauthorized.
