# CAUSAL_APPLICABILITY_001 — Qualification 001

## Tested basis

```text
candidate branch:
causal-applicability-v0

tested head:
7e3c244613b10e70fc0514410dee17266402a5c3

stack base:
goblin-pool-v0
16f1994c8c7cc6f3b7ff54c709f419eb50689cc5

workflow:
CAUSAL_APPLICABILITY_001

run:
35502093296

job:
106055551156

conclusion:
SUCCESS
```

## Exact tested artifacts

```text
candidate design:
a974c45c982c16c2d11ca01f4039984266b5edc9

evaluator:
1af117138bb21161014abc270ebe7f28cbedbe33

pressure suite:
697ed987324bd33fd0b415729f935bd13eb0a3f0

realization schema:
c3819a0080fa7c9c4217311893bfedfa94944146

judgment schema:
3f157d734fadf447c8837d77dbddcf043cdffa05

Causal Distinction Method note:
967bc8c939ff59627e6368e5fcd655907c7c24ee
```

## Observed pressure

The exact candidate pressure suite executed seven cells.

```text
A1 unchanged exact basis:
PASS

A2 world H1 → H2:
PASS
D1 remained unchanged
judgment became STALE

A3 seat remained epistemically at H1 while world = H2:
PASS
effect-boundary judgment remained STALE
seat state was not rewritten by evaluator

A4 seat later consumed/recorded H2:
PASS
D1 remained unchanged

A5 repeated comparison:
PASS
new judgment identity
same exact D1 identity

A6 H3 restored H1 tree content but H3 != H1:
PASS
judgment remained STALE under exact-head v0

A7 repository ref returned to exact H1:
PASS
same D1 became APPLICABLE again
```

This mechanically distinguishes, in the tested fixture:

```text
REALIZATION IDENTITY
!=
APPLICABILITY JUDGMENT

CURRENTLY STALE
!=
IRREVOCABLY INAPPLICABLE

SAME TREE CONTENT
!=
SAME EXACT BASIS

EFFECT GATING
!=
MEMORY FORGERY

APPLICABLE
!=
ADMITTED
```

## Realization conservation

The pressure retained one realization object D1 with:

```text
realization_basis:
H1

mechanical_result:
PASS
```

Across APPLICABLE → STALE → APPLICABLE judgments:

```text
canonical realization bytes:
UNCHANGED

realization SHA-256:
UNCHANGED

mechanical_result:
PASS
```

The applicability evaluator emitted separate judgment objects and did not mutate
the realization, seat memory, authority, or successor state.

## Conservative v0 boundary

The exact rule tested was only:

```text
comparison_basis == realization_basis
→ APPLICABLE

otherwise
→ STALE
```

A new commit whose tree content equals H1 remains stale when its commit identity
differs from H1.

Therefore this qualification does not imply dependency-sensitive or
content-equivalent applicability.

## Composition regression

The same workflow also re-executed:

```text
LABBOIB_CONTROLLER_BINDING_001 regression:
PASS

GOBLIN_POOL_001 regression:
PASS

direct causal-applicability CLI:
PASS
```

So the new candidate did not merely assume its immediate controller substrate
remained intact on the tested descendant checkout.

## Bounded mechanical result

The executed fixture supports only:

```text
UNDER THE TESTED EXACT-GIT-HEAD RULE,
ONE FIXED REALIZATION CAN RECEIVE
SEPARATE APPLICABILITY JUDGMENTS

AS THE COMPARISON BASIS CHANGES,

WITHOUT OBSERVED MUTATION OR DESTRUCTION
OF THE REALIZATION.
```

## Nonclaims

This qualification does not establish:

```text
dependency-sensitive applicability
semantic equivalence of repository states
scope validity
mechanical qualification beyond the tested result
authorization
admission
Codex implementation safety
scheduler correctness
general world-state comparison
general causal semantics
```

The method note is preserved only as:

```text
METHOD DESCRIBED
!=
METHOD VALIDATED AS GENERAL
```

## Standing boundary

```text
MECHANICAL QUALIFICATION:
7 / 7 PASS

COMPOSITION REGRESSION:
PASS

SCIENTIFIC PROMOTION:
NONE BY THIS RECEIPT

MERGE AUTHORITY:
NONE

CODEX HAND:
NOT MATERIALIZED

SCHEDULER:
UNTOUCHED
```
