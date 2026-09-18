# MM-002 Council Checkpoint Basis Envelope v0

**Status:** CANDIDATE MINIMAL REPAIR  
**Purpose:** add immutable historical source closure to the existing Council
checkpoint without duplicating its deliberation summary.

## Carrier

Primary hot-memory carrier:

`traces/multi_round_deliberation_001_checkpoint.json`

Checkpoint blob:

`0cad066f48de2a42a45017487ec2bcde855fbaa6`

## Immutable historical basis

The checkpoint and all four underlying Council round artifacts are jointly
retained at:

`cd4375dda09a2dfe5ba297de99bbef6bba38e9c9`

That commit is the current-main transplant coordinate for the frozen continuity
v0 source material.

Exact round artifacts:

| Actor / round label | Path | Blob SHA |
| --- | --- | --- |
| ChatGPT round 1 | `continuity/council/multi_round_001_chatgpt_round_1.json` | `55dc0e28cb3e78681a7c43254d8d5ba829e9dae6` |
| Codex round 1 | `continuity/council/multi_round_001_codex_round_1.json` | `eb326bcf32a727c474cbe53a2eb0c916e210afd5` |
| ChatGPT round 2 | `continuity/council/multi_round_001_chatgpt_round_2.json` | `f5afc17abbfd72992fa8b9a69a124be3b51361fd` |
| Codex round 2 | `continuity/council/multi_round_001_codex_round_2.json` | `37445955d56bba9893b533a70af60d6483409911` |

Checkpoint:

`traces/multi_round_deliberation_001_checkpoint.json`
→ `0cad066f48de2a42a45017487ec2bcde855fbaa6`

## Repair boundary

This envelope repairs only:

```text
repository-relative source path
!=
immutable historical source identity
```

It does **not** add:

- per-round causal argument summaries;
- actor-specific attack/acceptance attribution beyond filenames/labels;
- omitted round prose;
- new standing;
- new authority;
- a second deliberation summary.

If correct reconstruction still requires one of those, MM-002 must expose that
as a separate subsequent loss.

## Nonclaim

```text
checkpoint + exact basis closure
!=
proof checkpoint preserves every consequential deliberation relation
```

Round 2 exists to test that question.
