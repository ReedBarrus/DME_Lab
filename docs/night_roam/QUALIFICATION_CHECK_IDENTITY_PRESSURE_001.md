# QUALIFICATION_CHECK_IDENTITY_PRESSURE_001

Status: PRESSURE DESIGN ONLY

Basis: `cockpit-perceptual-instrument-campaign-v0@a9b4ed3d1086f7a7042ecdb7d358109f53938722`

## Observed basis

The merged perceptual-instrument implementation declares a dedicated GitHub Actions workflow named `COCKPIT_PERCEPTUAL_INSTRUMENT_001`, whose sole job is named `pressure`. The implementation head `6dff701cd06ad19ce42c7e1fdd32917f61396af4` currently has five completed successful check runs, all surfaced with the same check-run name `pressure`.

The successful conclusions establish that five check runs completed successfully. Their shared display name does not, by itself, establish which qualification surface each check represents.

## Proposed distinction

```text
CHECK CONCLUSION = SUCCESS
!=
QUALIFICATION IDENTITY RECOVERABLE FROM CHECK SURFACE

MULTIPLE SUCCESSFUL CHECKS
!=
ONE QUALIFICATION

DISPLAY NAME EQUALITY
!=
SEMANTIC / WORKFLOW IDENTITY
```

## Why current evidence does not settle it

GitHub retains workflow/run/check metadata that may permit identity recovery by following each check's details URL, check suite, workflow run, or workflow file. Therefore duplicate check names are a legibility pressure, not evidence that qualification identity has actually been lost.

## Smallest discriminating pressure

Take the five successful `pressure` check runs attached to implementation head `6dff701c...` and attempt reconstruction under two conditions:

A. CHECK-SURFACE ONLY — use the check-run summary fields available to an operator deciding whether the implementation is qualified.

B. FULL METADATA — follow the mechanically linked run/suite/workflow identity for each check.

For each check, recover:

- workflow identity;
- exact tested commit;
- qualification/test family;
- conclusion;
- whether two same-named checks can be distinguished without narrative inference.

## Outcome cells

1. A and B both uniquely recover identity -> duplicate names are cosmetic only in tested scope.
2. A ambiguous, B unique -> qualification identity exists but operator-facing legibility is compressed.
3. A and B ambiguous -> mechanically relevant qualification provenance is under-specified.
4. Metadata resolves workflow but not tested basis/test family -> partial provenance only.

## Earned claim ceiling

Even a fully successful reconstruction earns only:

`QUALIFICATION CHECK IDENTITY IS MECHANICALLY RECOVERABLE IN THE TESTED GITHUB SURFACE.`

It does not earn semantic correctness, scientific standing, deployment readiness, merge authority, or equivalence among the successful checks.

## Dangerous neighboring inference

```text
GREEN CHECKS
=> IMPLEMENTATION QUALIFIED
=> SEMANTICS CORRECT
=> SAFE TO INTEGRATE
```

None of those arrows are established by this pressure.

## Mutation boundary

No workflow names, job names, tests, branch policy, or implementation are changed by this artifact. Do not rename checks until the pressure establishes whether identity is merely visually compressed or mechanically unrecoverable.
