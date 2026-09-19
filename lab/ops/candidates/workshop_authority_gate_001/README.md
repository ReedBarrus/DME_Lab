# WORKSHOP_AUTHORITY_GATE_001 — bounded integration apparatus

**Basis:** `d83429f8cc25cfb2a6105af7ae9d41bcb1b023a2`  
**Status:** APPARATUS ONLY — held-out A/B0 not executed  
**STOPPED pressure:** not exercised  
**Scientific standing:** unchanged

## Target apparatus

This candidate adds one bounded path:

```text
run_frozen_cell(...)
→ ExecutionStopLatch.require_active(E)
→ adapter surface observation
→ adapter invocation
→ exclusive creation of one fresh external filesystem target
```

The gate executes before the first adapter interaction when an
`execution_stop_latch` is supplied to the Workshop runner.

Legacy ungated calls remain outside this apparatus and are not claimed guarded.

## Consequence

The specimen-local adapter creates one file with `O_EXCL`; overwrite is not
permitted. Its target is outside the execution-authority state store.

```text
instrumentation
!=
external consequence
```

The runner report and `observe_target()` are separate witnesses.

## Qualification

Only dummy authority state is used:

```text
python -m unittest tests.runtime.test_workshop_authority_gate_001 -v
```

Qualification checks:

- dummy ACTIVE reaches the existing Workshop adapter dispatch path exactly once;
- dummy ABSENT blocks before any adapter surface observation or invocation;
- ACTIVE authority setup does not create the external consequence target;
- ACTIVE and ABSENT use the same manifest and execution-envelope identity in
  separate fresh state stores;
- external target observation agrees with the filesystem;
- target creation is exclusive and does not overwrite a pre-existing target;
- ABSENT performs no retry, recovery, or authority materialization;
- no held-out A/B0 cell is executed;
- STOPPED is not exercised.

## Claim ceiling

Successful qualification establishes only that a bounded apparatus exists that
can later pressure whether retained ACTIVE(E) controls one selected Workshop
consequence path. It does not establish that ACTIVE is behaviorally material in
the held-out pressure, that all Workshop paths are guarded, that STOPPED is
terminal for this path, or that authority is atomic across execution.
