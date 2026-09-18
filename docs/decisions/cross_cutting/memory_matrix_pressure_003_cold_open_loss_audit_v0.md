# Memory Matrix Pressure 003 — Cold Open Loss Audit

**Status:** ACTIVE PRESSURE  
**Pressure ID:** MM-003  
**Specimen:** the qualified MM-002 compositional hot-memory carrier  
**Purpose:** test whether an observer can expose a consequential loss that the
enumerated MM-002 round-trip questions never named.

## Question

Does the qualified MM-002 carrier still omit any consequential information that
matters for correct reconstruction, despite passing the targeted Round 3 test?

This pressure exists because:

```text
passing an enumerated reconstruction checklist
!=
demonstrating that the checklist named every consequential dimension
```

MM-003 therefore changes the test style rather than the carrier.

## Frozen carrier

The observer receives only:

1. `traces/multi_round_deliberation_001_checkpoint.json`
2. `docs/candidates/memory_matrix_v0/MM002_CHECKPOINT_BASIS_ENVELOPE_v0.md`
3. `docs/candidates/memory_matrix_v0/MM002_COUNCIL_CAUSAL_LINEAGE_ENVELOPE_v0.md`

No raw Council round artifacts, repository browsing, prior conversation, prior
MM-002 observer outputs, or enumerated MM-002 reconstruction questions are
provided.

## Test change

MM-002 used targeted prompts that explicitly named expected reconstruction
requirements.

MM-003 removes that scaffold.

The observer is asked to reconstruct freely and then identify anything
consequentially missing.

The prompt deliberately does not enumerate candidate loss classes.

## Pass criterion

PASS only if the observer:

- can reconstruct the carrier's meaning without inventing unsupported state;
- finds no consequential loss that requires information absent from the carrier
  and not safely recoverable through its exact retained source routes; and
- does not rely on the omitted MM-002 checklist to determine what matters.

A PASS is bounded evidence about this carrier and this open-ended audit.

It is not proof of semantic completeness.

## Fail criterion

FAIL if the observer identifies one smallest consequential loss that:

- matters to correct reconstruction or use of the retained deliberation; and
- cannot be recovered from the supplied carrier without reopening information
  the carrier was supposed to conserve hot.

The observer must distinguish:

```text
detail omitted but exactly recoverable from retained source
!=
consequential relation missing from the hot carrier
```

## Adjudication rule

If an observer exposes a real loss:

```text
do not widen the ontology
→ verify the loss against immutable raw basis
→ repair only the smallest missing relation
→ rerun targeted verification
→ rerun a fresh cold audit
```

If no observer exposes a loss, record only bounded additional confidence in the
qualified carrier and evaluate whether the cold-audit step belongs in the
memory method.

No method amendment is earned merely by staging MM-003.


## Cold audit 001 result

Two independent open-ended observers diverged:

- one returned `COLD OPEN LOSS AUDIT FAILS`;
- one returned `COLD OPEN LOSS AUDIT PASSES`.

The FAIL was verified against immutable repository history and is valid.

The exposed wound is:

```text
deliberation source closure
!=
operational dependency closure
```

The checkpoint's non-round evidence refs were not explicitly pinned by the
MM-002 envelopes. More importantly, the historical
`AGENT_CONTEXT.md` used by the continuity source lineage differs from the
same path at the later transplant commit.

Frozen source:

`f28187306d3282a66d95b9d85e764f75751e812d:AGENT_CONTEXT.md`
→ `416b2aaa6469d4e201860836399b8989c95dcaff`

Later transplant:

`cd4375dda09a2dfe5ba297de99bbef6bba38e9c9:AGENT_CONTEXT.md`
→ `5b1102a7b619985fbbcff7034acc92e2800bd71f`

The retained handoff rule already says inherited CE-000001 through CE-000010
relative refs must resolve through the frozen source lineage, not the
post-handoff branch.

### Minimal repair

Add only:

`docs/candidates/memory_matrix_v0/MM003_CONTINUITY_DEPENDENCY_BASIS_ENVELOPE_v0.md`

Then run:

`docs/candidates/memory_matrix_v0/MM003_TARGETED_REPAIR_PROMPT_001.md`

After targeted repair verification, rerun a fresh cold open-ended audit before
any new invariant or method rule is promoted.


## Targeted dependency repair verification 001

The minimal dependency-basis repair received two independent passes.

Both observers recovered the frozen pre-handoff continuity basis, exact
historical `AGENT_CONTEXT.md`, the detailed ritual owner and minimum ritual
relation, the frozen event/cursor artifacts, the transplant non-equivalence,
and the repair's nonclaims without guessing.

Result:

```text
MM003 DEPENDENCY REPAIR PASSES
MM003 DEPENDENCY REPAIR PASSES
```

The repair is therefore verified in its targeted scope.

### Cold audit 002

No invariant is promoted yet.

The repaired carrier now returns to an unscaffolded cold audit:

```text
checkpoint
+
MM-002 basis envelope
+
MM-002 causal-lineage envelope
+
MM-003 continuity-dependency basis envelope
```

Prompt:
`docs/candidates/memory_matrix_v0/COLD_OPEN_LOSS_AUDIT_PROMPT_003_ROUND_2.md`

Previous audit outputs and targeted verification questions must not be supplied.
