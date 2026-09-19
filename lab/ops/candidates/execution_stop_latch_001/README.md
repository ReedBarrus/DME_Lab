# EXECUTION_STOP_LATCH_001

Specimen-local repair candidate for Workshop execution administration.

## Target

```text
TERMINAL_STOP(E)
→ STOPPED(E)

STOPPED(E)
↛ ACTIVE(E)
```

for one execution-envelope identity `E` inside the bounded state store.

The latch consumes a terminal-stop signal. It does not decide which condition should
produce that signal.

## Initial authority boundary

```text
FIXTURE MATERIALIZATION
!=
AUTHORITY GRANT
```

The bounded specimen assumes an upstream authority object has already declared the
execution envelope initially ACTIVE. `fixture_setup.py` may materialize those
declared bytes exactly once; it does not decide whether that declaration is
warranted or authorized.

```text
upstream authority object
→ declares ACTIVE(E)

specimen setup
→ materializes exact ACTIVE(E) bytes

ExecutionStopLatch
→ reads / consumes / terminates retained authority
```

If no authority state has been materialized, the latch cannot inspect ACTIVE, cannot
consume a terminal STOP for an unknown envelope, and cannot successfully guard a
consequence. Absence does not create authority.

## Bounded surface

`stop_latch.py` retains state by exact `execution_envelope_id` and exposes no API
that materializes ACTIVE authority.

`guarded_surface.py` exposes two specimen-local consequence paths:

```text
create_held_out_condition_root
emit_experimental_score
```

Both call the same identity-bound guard before producing filesystem consequences.

Reacquiring the same envelope identity against the same store recovers retained
state. Once STOPPED, the same authority locus remains STOPPED and both guarded
paths reject.

## Allowed while STOPPED

```text
inspection
receipt emission
caller termination
```

## Not implemented

```text
initial authority adjudication
STOP policy
repair
retry
reauthorization
new-envelope policy
general workflow machinery
scientific-standing mutation
campaign progression
```

## Pressure

```bash
python -m unittest tests.lab.test_execution_stop_latch_001 -v
```

The tests cover absence without authority creation, declared initial authority,
rejection on two distinct consequence paths, retained STOPPED state after
reacquisition of the same authority locus, rejection of repeat materialization,
and inspection while stopped.

## Claim ceiling

If the pressure passes:

> Within the tested single-actor bounded surface, the latch consumed pre-existing
> authority without originating authority from absence, and a terminal STOP remained
> terminal for the same bounded authority locus across reacquisition and later
> guarded operations.

No concurrency claim, generalized admission claim, or claim that fixture
materialization itself grants authority follows.
