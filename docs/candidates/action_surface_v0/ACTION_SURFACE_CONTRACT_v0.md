# ACTION_SURFACE_v0

## Status

```text
CANDIDATE COCKPIT SURFACE
READ-ONLY
NON-AUTHORIZING
NON-EXECUTING
```

## Question

Can the Cockpit expose the next declared routing operation for each committed
Lab process without inventing process liveness, choosing an action, widening
authority, or replaying consequence?

## Source basis

The bounded source surface is:

```text
lab/processes/*.json
lab/events/events.jsonl
```

The action projection is derived only from the exact committed source tree used
by the Cockpit projection.

```text
PROCESS SPEC EXISTS
!=
PROCESS REGISTERED

PROCESS REGISTERED
!=
PROCESS ACTIVE

ACTION VISIBLE
!=
ACTION SELECTED

ACTION SELECTED
!=
ACTION AUTHORIZED

ACTION AUTHORIZED
!=
ACTION EXECUTED
```

An absent `PROCESS_REGISTERED` event must remain explicit. The projector may
show the declared initial transition from a process specification for operator
orientation, but must label it:

```text
SPEC_ONLY_UNREGISTERED
```

It must not silently promote the process to live routing state.

## Projection semantics

Each `action_surface_v0` object reports:

```text
process identity
runtime registration presence / absence
reconstructed phase
reconstructed routing status
declared next transition
transition kind
capability requirement
role-judgment requirement
human-decision requirement
blocker / pending role / pending decision
event count consumed
projection boundary
source provenance
```

The surface may classify the next declared routing relation as:

```text
SPEC_ONLY_UNREGISTERED
MECHANICAL_ROUTING_AVAILABLE
MECHANICAL_CAPABILITY_REQUIRED
REQUIRES_ROLE_JUDGMENT
REQUIRES_EXPLICIT_HUMAN_DECISION
BLOCKED
FAILED
STOPPED_BY_HUMAN
TERMINAL
UNRESOLVED
```

These values describe routing posture. They are not action permissions.

## Authority boundary

Every surface must retain:

```text
authority_effect = NONE_BY_ACTION_SURFACE
execution_effect = NONE_BY_ACTION_SURFACE
```

and:

```text
read_only = true
creates_authority = false
performs_execution = false
selects_action = false
advances_cursor = false
```

The Cockpit v0 Action lens contains no execution button.

A future executable action surface requires separate pressure over exact
authority transport, stale-basis handling, action request identity, execution
receipt identity, and recovery behavior.

## Reconstruction boundary

The projector may replay the declared routing event vocabulary only to recover
process position. It must never replay an external consequence.

Unknown or malformed event/process material must fail legibly rather than be
normalized into an apparently available action.

```text
ROUTING RECONSTRUCTION
!=
CONSEQUENCE REPLAY
```

## Current initial specimen

On the source basis from which this candidate was cut,
`lab/events/events.jsonl` is empty while the committed conductor fixture
exists.

The expected action-surface posture is therefore:

```text
LP-001-CONDUCTOR-FIXTURE

runtime_registration:
ABSENT

phase:
SEEDED

routing_status:
UNREGISTERED

declared_next_action.transition_id:
LOAD_FROZEN_CONTRACT

declared_next_action.transition_kind:
MECHANICAL

declared_next_action.eligibility:
SPEC_ONLY_UNREGISTERED
```

This specimen intentionally pressures:

```text
DECLARED PROCESS GEOMETRY
!=
LIVE PROCESS EVENT
```

## Nonclaims

This candidate does not establish:

```text
scheduled invocation
shared-room transport
automatic continuity consumption
agent persistence
action execution
authority delegation
role invocation
capability availability
scientific standing
global Lab state
```

Those remain separate future pressures.
