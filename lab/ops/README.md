# Lab Ops Registry v0

This directory contains the first explicit operator-facing process registry for DME_Lab.

Its purpose is narrow:

```text
make current process reality reconstructible
without requiring Reed to remember it
```

## Non-collapse rules

```text
process complexity
!=
operator cognitive load

role-reported state
!=
canonical registry state

role affects registry
!=
role directly mutates registry

process registry
!=
scientific standing

process update
!=
execution authority

interesting candidate
!=
active process
```

## Active registry

`LAB_OPS_REGISTRY_v0.json` is a cockpit-consumable operational projection.

It answers only:

```text
WHAT EXISTS?
WHERE IS IT?
WHY IS IT STOPPED?
WHO OWNS THE NEXT MOVE?
DOES REED NEED TO DO ANYTHING?
```

It does not establish scientific validity, authorize execution, or replace process-specific evidence.

## Role turn-ending obligation

If a role turn materially changes its understanding of an active process's operational position, the role should emit exactly one `lab_process_update_v0` object before stopping.

If nothing operationally changed, emit:

```text
turn_effect = NO_CHANGE
```

A process update is a reported delta, not canonical state mutation.

The intended later path is:

```text
ROLE
  ↓ emits
PROCESS_UPDATE
  ↓ validated/admitted by future conductor logic
EVENT
  ↓ projected into
LAB_OPS_REGISTRY
  ↓ rendered by
COCKPIT
```

That admission/projector path is explicitly not implemented by this seed.

## Seeded active processes

Only three active processes are registered:

```text
LP-001
PULSE-CONTINUITY
CONDUCTOR-V0
```

The Epistemic Action Gate remains candidate-only and is intentionally absent.

## Operator success criterion

A returning operator should be able to inspect this one surface and answer:

```text
what is active?
what is blocked?
what moves next?
who owns it?
do I need to decide anything?
```

without reconstructing prior conversations.
