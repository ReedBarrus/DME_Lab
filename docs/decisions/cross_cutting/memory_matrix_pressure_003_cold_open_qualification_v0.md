# Memory Matrix Pressure 003 — Cold Open Qualification

**Status:** PASSED IN TESTED SCOPE  
**Pressure:** MM-003  
**Specimen:** repaired MM-002 compositional carrier plus continuity-dependency basis envelope

## Sequence

MM-003 tested the qualified MM-002 carrier without an enumerated reconstruction checklist.

```text
cold audit 001
→ one PASS
→ one FAIL

verified FAIL
→ operational dependency basis wound

minimal repair
→ continuity-dependency basis envelope

targeted verification
→ PASS
→ PASS

fresh cold audit 002
→ PASS
→ PASS
```

The first cold audit therefore exposed a consequential relation that the targeted
MM-002 checklist had not named.

The verified wound was:

```text
primary deliberation source closure
!=
operational dependency closure
```

Specifically, the MM-002 basis envelope correctly pinned the checkpoint and four
Council round artifacts, but that did not establish the historical identity of
other operational dependencies referenced by the checkpoint.

The failure became consequential because the same repository path,
`AGENT_CONTEXT.md`, referred to different content across the frozen
pre-handoff continuity basis and the later transplant basis.

## Repair

The minimal repair added:

`docs/candidates/memory_matrix_v0/MM003_CONTINUITY_DEPENDENCY_BASIS_ENVELOPE_v0.md`

It pins the pre-handoff continuity source basis and exact historical identities
for:

- `AGENT_CONTEXT.md`;
- `continuity/SYNC_RITUAL.md`;
- `continuity/README.md`;
- `continuity/events.jsonl`;
- both Council-relevant consumer cursors;
- the retained handoff-basis witness.

It also preserves only the minimum ritual relation required to understand the
Council's startup-discoverability proposal.

## Earned methodological result

MM-003 supports two bounded method refinements.

First:

```text
closing provenance for one referenced artifact set
!=
closing provenance for every consequential dependency of the carrier
```

Historical dependency identity must be checked at the basis actually governing
that dependency when correct reconstruction depends on it.

Second:

```text
targeted reconstruction success
!=
open-ended loss-audit success
```

A targeted checklist can verify known repairs while still failing to expose a
consequential dimension it never asks about.

Therefore a cold, unscaffolded loss audit is now part of the bounded memory
qualification method before a repaired carrier is treated as stable within its
declared scope.

## Bounded conclusion

The repaired carrier survived two independent targeted dependency-repair
verifications and two independent fresh cold-open audits.

No further consequential loss was identified in that final tested carrier.

This does not establish:

- universal semantic completeness;
- that one cold audit is sufficient for every specimen;
- automatic dependency discovery;
- a generalized transitive dependency graph;
- generalized semantic-continuity verification;
- source deletion authority.

Raw sources remain retained.
