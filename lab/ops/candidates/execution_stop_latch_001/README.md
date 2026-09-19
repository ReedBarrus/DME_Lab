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

## Bounded surface

`stop_latch.py` retains state by exact `execution_envelope_id`.

`guarded_surface.py` exposes two specimen-local consequence paths:

```text
create_held_out_condition_root
emit_experimental_score
```

Both call the same identity-bound guard before producing filesystem consequences.

Reacquiring the same envelope identity against the same store recovers retained
state. Calling `materialize_active()` on an already retained STOPPED envelope
returns STOPPED and does not reactivate it.

## Allowed while STOPPED

```text
inspection
receipt emission
caller termination
```

## Not implemented

```text
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

The tests cover a clean path, rejection on two distinct consequence paths, retained
STOPPED state after reacquisition of the same envelope identity, and inspection
while stopped.

## Claim ceiling

If the pressure passes:

> Within the tested bounded execution surface, a terminal STOP bound to one
> execution-envelope identity remained terminal across later guarded operations
> and reacquisition of that identity.
