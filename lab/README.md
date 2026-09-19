# Lab Conductor v0 surfaces

This directory contains a deliberately narrow process-routing prototype.

It preserves these boundaries:

```text
process state != scientific standing
mechanical routing != semantic judgment
packet validity != claim validity
replay != re-execution
logged intent != completed consequence
process projection != universal representation
human authority != human state transport
role != current occupant
advancing a frozen process != choosing the next scientific process
```

## Surfaces

- `events/events.jsonl` — append-only retained process events.
- `packets/` — conserved role-to-role packet objects. Roles are logical seats;
  executor/invocation identity is receipt metadata only.
- `state/LAB_STATE_v0.json` — rebuildable operational routing projection.
- `processes/` — explicitly declared process graphs. Conductor advancement is
  permitted only inside these graphs and only for `MECHANICAL` transitions.

`LAB_STATE_v0.json` is not evidence of scientific validity, authorization,
relevance, or project standing. It is one derived process projection.

Replay reconstructs state from retained events and never re-performs external
side effects.

A `ROLE_JUDGMENT` transition emits `ROLE_JUDGMENT_REQUIRED` and stops. A
`HUMAN_DECISION` transition emits a complete decision object and stops. A
mechanical transition requiring unavailable capability emits `BLOCKED` and
stops.

Conductor v0 does not invoke models, choose scientific pressures, merge pull
requests, mutate continuity cursors, adjudicate packet claims, or execute the
live LP-001 experiment.
