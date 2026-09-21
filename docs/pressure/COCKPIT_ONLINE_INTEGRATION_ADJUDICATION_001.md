# COCKPIT_ONLINE_INTEGRATION_ADJUDICATION_001

## Status

```text
PRESSURE:
EXECUTED

READ-ORIENTED COMPOSITION:
SURVIVES TESTED INTEGRATION PRESSURE

CONTROL BACKEND:
NOT INTEGRATED

DEPLOYMENT TO USER MACHINE:
NONE

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE
```

## Tested basis

```text
base main:
00b3783683ad9009d6152cc861b9383087aece7f

perceptual source lineage:
0fd6f3d81393eb81e4f8d3df86e6b6d411d2c0f9

integration pressure branch:
cockpit-online-integration-pressure-v0

green implementation head before this receipt:
44cf401c16452b445a8f2197269ba2c981e499dd
```

## Composition

The bounded integration preserved current-main Cockpit surfaces while importing
only the read-oriented perceptual/runtime bundle.

Preserved from current `main`:

```text
repository-derived observer
Action Surface
projection adapter
ACTIONS lens
existing science/navigation views
```

Composed from the perceptual lineage:

```text
perceptual_instrument.mjs
runtime_live.mjs
control_live.mjs
live_runtime_projection.py
development_horizon_projection.py
instrument / runtime / control DOM roots
perceptual/runtime/control CSS
```

Explicitly not imported:

```text
src/cockpit/control_adapter.py
write-capable campaign/selection/preparation/assignment/wake stack
```

Therefore:

```text
COCKPIT READ / PERCEPTION ONLINE
!=
CONTROL MEMBRANE ONLINE
```

## First composition rake

The first integration run failed:

```text
COCKPIT_ONLINE_INTEGRATION_001
run 35558841138
FAIL
```

The failure was not an app/runtime collision.

Current `main` already exposed the bounded `ACTIONS` lens through
`VIEW_NAMES`, but one observer test still asserted the older five-lens
vocabulary that omitted `ACTIONS`.

The smallest repair updated that stale test expectation only.

No observer implementation semantics changed.

This earned the local maintenance distinction:

```text
CURRENT IMPLEMENTATION
!=
CURRENT TEST EXPECTATION
```

and demonstrated that cross-lineage composition can expose pre-existing
single-lineage residue.

## Green composed run

After the stale expectation repair:

```text
COCKPIT_ONLINE_INTEGRATION_001
run 35558881193
job 106207776800
SUCCESS
```

Observed test groups:

```text
main Python Cockpit regressions:
15 / 15 PASS

main observer:
40 / 40 PASS

perceptual + browser-boundary group:
24 / 24 PASS

read-side runtime integration:
4 / 4 PASS
```

The integration-specific browser cells established:

```text
composed app retains:
MAIN ACTION SURFACE
+
PERCEPTUAL ADDRESSING
+
RUNTIME STARTUP
+
CONTROL STARTUP SHELL

unconfigured control:
EXPLICITLY UNAVAILABLE
NO CLIENT CREATED

unconfigured runtime:
EXPLICITLY UNAVAILABLE
NO EVENTSOURCE CREATED
```

The read-side runtime cells established:

```text
unconfigured sources remain explicit
configured missing source => PARTIAL
same durable state => same state_sha256
POST / PUT / PATCH / DELETE => 405
cross-store atomicity => NOT_ESTABLISHED
projection / authority / execution / standing effects => NONE
```

## Earned claim

```text
ON THE TESTED COMPOSED LINEAGE,

THE READ-ORIENTED PERCEPTUAL COCKPIT BUNDLE
COEXISTS WITH THE CURRENT-MAIN OBSERVER
AND ACTION SURFACE

WITHOUT THE TESTED REGRESSIONS,

WHILE RUNTIME AND CONTROL REMAIN
FAILURE-LEGIBLE WHEN UNCONFIGURED.
```

## Not earned

This does not establish:

```text
deployment to Reed's local Cockpit
write-capable control integration
authenticated human control
automatic scheduling
automatic wake
automatic work selection
seat continuity
parallel-seat coordination
scientific standing from UI state
general branch-composition safety
```

## Conserved scars

```text
GOOD BRANCH
+
GOOD BRANCH
!=
GOOD UNION

INTEGRATION
!=
BRANCH MERGE

PERCEPTUAL CONTROL AFFORDANCE
!=
CONTROL BACKEND

COCKPIT ONLINE IN REPOSITORY
!=
DEPLOYED ON USER MACHINE
```

## Next boundary

The next operating expansion should not widen this integration by importing the
entire control stack merely for completeness.

The next independent pressure is coordination:

```text
TWO_LANE_COORDINATION_001
```

with:

```text
two isolated seats / branches
+
shared append-only coordination evidence
+
per-seat coordination cursor
+
semantic work claims
+
pre-mutation revalidation
+
serialized authoritative integration
```

No scheduler, lease expiry, leader election, or automatic conflict resolution
is implied.
