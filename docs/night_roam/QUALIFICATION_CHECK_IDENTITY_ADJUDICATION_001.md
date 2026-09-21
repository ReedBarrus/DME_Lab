# QUALIFICATION_CHECK_IDENTITY_ADJUDICATION_001

## Status

```text
PRESSURE:
EXECUTED AGAINST GITHUB CHECK / RUN METADATA

RESULT:
OPERATOR-FACING COMPRESSION

MECHANICAL QUALIFICATION IDENTITY:
RECOVERABLE IN TESTED SURFACE

WORKFLOW / JOB RENAME:
HELD

AUTHORITY EFFECT:
NONE
```

## Basis

Implementation head:

```text
6dff701cd06ad19ce42c7e1fdd32917f61396af4
```

The commit exposes five successful check runs whose displayed check-run name is:

```text
pressure
```

for all five rows.

## Check-surface observation

From the commit check-run surface alone, all five rows share:

```text
name = pressure
head_sha = 6dff701c...
conclusion = success
```

The rows remain distinguishable by check-run id, check-suite id, and details URL,
but the qualification family is not legible from the shared display name alone.

Therefore:

```text
CHECK-SURFACE DISPLAY NAME
IS AMBIGUOUS AS QUALIFICATION FAMILY
```

## Full linked metadata reconstruction

Following the mechanically linked workflow-run metadata uniquely recovers:

```text
run 35518361039
workflow = BOUNDED_REENTRY_001
path = .github/workflows/bounded-reentry-001.yml
head = 6dff701c...
conclusion = success

run 35518361014
workflow = COCKPIT_CONTROL_ADAPTER_001
path = .github/workflows/cockpit-control-adapter-001.yml
head = 6dff701c...
conclusion = success

run 35518361000
workflow = COCKPIT_PERCEPTUAL_INSTRUMENT_001
path = .github/workflows/cockpit-perceptual-instrument-001.yml
head = 6dff701c...
conclusion = success

run 35518361028
workflow = LIVE_RUNTIME_PROJECTION_001
path = .github/workflows/live-runtime-projection-001.yml
head = 6dff701c...
conclusion = success

run 35518361030
workflow = DEVELOPMENT_HORIZON_PROJECTION_001
path = .github/workflows/development-horizon-projection-001.yml
head = 6dff701c...
conclusion = success
```

Each run has a distinct workflow id and run id while conserving the same exact
tested commit coordinate.

## Mechanical result

The pressure resolves as:

```text
CHECK-SURFACE ONLY:
QUALIFICATION FAMILY AMBIGUOUS FROM DISPLAY NAME

FULL LINKED METADATA:
QUALIFICATION IDENTITY UNIQUELY RECOVERABLE
```

This is outcome 2 from the pressure design:

```text
A ambiguous
B unique
→ qualification identity exists
  but operator-facing legibility is compressed
```

## Earned claim

```text
FOR THE TESTED FIVE CHECKS,

QUALIFICATION / WORKFLOW IDENTITY
IS MECHANICALLY RECOVERABLE
THROUGH LINKED GITHUB RUN METADATA

DESPITE IDENTICAL JOB DISPLAY NAMES.
```

## Not earned

This does not establish:

```text
semantic correctness
scientific standing
deployment readiness
integration safety
equivalence among the five successful workflows
qualification solely from green status
```

## Disposition

No workflow rename is required to preserve mechanical provenance.

A future Cockpit / operator-facing qualification surface may choose to display
workflow identity directly so the operator does not need to follow the
details-link indirection.

That is a legibility improvement, not a provenance repair.

## Conserved scars

```text
CHECK SUCCESS
!=
QUALIFICATION IDENTITY

DISPLAY NAME EQUALITY
!=
WORKFLOW IDENTITY

OPERATOR LEGIBILITY
!=
MECHANICAL PROVENANCE
```
