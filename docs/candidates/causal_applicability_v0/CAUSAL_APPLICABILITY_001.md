# CAUSAL_APPLICABILITY_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

DEPENDENCY BASIS:
LABBOIB_CONTROLLER_BINDING_001 lineage

RULE:
EXACT GIT HEAD EQUALITY ONLY

DEPENDENCY-SENSITIVE APPLICABILITY:
NOT IMPLEMENTED

AUTHORITY EFFECT:
NONE

ADMISSION EFFECT:
NONE
```

## Sole question

```text
CAN AN OPERATOR REALIZATION
REMAIN DURABLY IDENTICAL AND RECOVERABLE

WHILE ITS CURRENT APPLICABILITY
CHANGES AS THE EXTERNAL GIT ENVIRONMENT MOVES?
```

## Smallest specimen

One realization:

```text
D1

identity:
FIXED

realization_basis:
H1

mechanical_result:
PASS
```

Applicability is represented by separate judgment objects.

```text
REALIZATION IDENTITY
!=
APPLICABILITY JUDGMENT
```

The v0 rule is deliberately conservative:

```text
comparison_basis == realization_basis
→ APPLICABLE

comparison_basis != realization_basis
→ STALE
```

No dependency graph, tree equivalence, path-sensitive invalidation, or semantic
relevance inference participates in v0.

## Core scars

```text
WORLD MOVED
!=
REALIZATION CHANGED

SEAT UNAWARE
!=
WORLD UNCHANGED

EVENT CONSUMED
!=
REALIZATION REWRITTEN

STALE CONSEQUENCE
!=
EVIDENCE DESTROYED

CURRENTLY STALE
!=
IRREVOCABLY INAPPLICABLE

APPLICABLE
!=
ADMITTED

MECHANICAL RESULT
!=
CURRENT APPLICABILITY
```

## Durable object split

### Realization

```text
causal_applicability_realization_v0
```

retains only historical realization facts needed by this pressure:

```text
realization_id
realization_kind
realization_basis
mechanical_result
payload_ref
```

It contains no current applicability field.

### Applicability judgment

```text
causal_applicability_judgment_v0
```

binds:

```text
judgment_id
exact realization identity
exact realization SHA-256
realization_basis
comparison_basis
rule
result = APPLICABLE | STALE
```

and explicitly carries:

```text
authority_effect = NONE
admission_effect = NONE
```

## Pressure cells

```text
A1 — UNCHANGED BASIS

D1 realized at H1
compare D1 against H1

→ APPLICABLE
→ D1 unchanged


A2 — WORLD MOVES

D1 realized at H1
Git HEAD advances to H2

→ STALE
→ D1 unchanged
→ D1 mechanical_result remains PASS


A3 — SEAT UNAWARE

world = H2
seat-retained observed basis = H1

compare D1 against actual H2

→ STALE
→ seat ignorance does not make the world H1


A4 — EVENT CONSUMED

seat later records H2 as consumed/known

→ seat state may change
→ D1 does not change


A5 — REJUDGMENT

same exact D1 receives another comparison

→ new judgment object
→ no mutation of D1


A6 — SAME CONTENT, DIFFERENT COMMIT

H3 restores the same repository tree content as H1
but H3 != H1

under v0:

→ STALE
```

This is intentional conservative false staleness.

```text
SAME TREE CONTENT
!=
SAME EXACT BASIS
```

### A7 — exact coordinate returns

If the observed Git ref later points to exact H1 again:

```text
D1 × H1
→ APPLICABLE
```

without rewriting D1 or either earlier judgment.

This directly pressures:

```text
CURRENTLY STALE
!=
IRREVOCABLY INAPPLICABLE
```

## Actor knowledge / effect boundary

The applicability evaluator consumes the comparison basis supplied by the
effect boundary. It does not rewrite seat memory.

Therefore a seat may honestly retain H1 while the effect boundary observes H2:

```text
ACTOR KNOWLEDGE
!=
ENVIRONMENTAL TRUTH

EFFECT GATING
!=
MEMORY FORGERY
```

The candidate does not define event delivery or cursor advancement.

## Claim ceiling

A passing pressure may support only:

```text
UNDER EXACT-GIT-HEAD EQUALITY,
A FIXED REALIZATION CAN RECEIVE
SEPARATE CURRENT APPLICABILITY JUDGMENTS

AS THE COMPARISON HEAD CHANGES,

WITHOUT THE TESTED REALIZATION
BEING REWRITTEN OR DESTROYED.
```

It does not establish:

```text
dependency-sensitive applicability
semantic equivalence of repository states
general causal validity
scope validity
mechanical qualification
authorization
admission
scheduler correctness
Codex implementation safety
general world-state comparison
```

## Composition target

If qualified, this relation is intended to sit below future bounded
implementation realization:

```text
IMPLEMENTATION REALIZATION
→ CAUSAL APPLICABILITY
→ scope / qualification / authority gates
→ possible successor admission
```

No implementation operator is authorized or materialized by this candidate.
