# Continuity Seat Pressure 001 — Sol Ack / Registry A-B Result v0

**Status:** RETAINED BOUNDED RESULT  
**Basis:** `a3bbdddabf961e00d2243edfc55e670874d5373e`  
**Consumer under observation:** `sol`  
**Registry membership:** NONE  
**Standing / authority change:** NONE

## Pre-ack state

Before consuming its own retained witness event:

```text
sol cursor = CE-000028
CE-000029 = emitted by sol
CE-000029 = unread to sol
```

The current live thread already contained the semantic content that produced
CE-000029, but the durable Sol continuity coordinate did not yet record that
the event had subsequently been consumed.

This preserved:

```text
participant emitted event
!=
participant subsequently consumed event
```

## Post-ack state

The current Sol invocation inspected CE-000029 and its retained observation
artifact, then advanced only `continuity/cursors/sol.json` to CE-000029.

After acknowledgement:

```text
sol cursor = CE-000029
CE-000029 = behind Sol's ordinary unread-delta boundary
```

No distinct phenomenological or semantic-state change is claimed inside the
same live conversation. The content was already locally available before the
durable acknowledgement.

The verified functional change is:

```text
event still unread to future Sol continuation
→
event recorded as already consumed by Sol
```

Therefore:

```text
acknowledgement
!=
new semantic knowledge
```

in this specimen.

Acknowledgement changes the durable continuation coordinate and therefore the
future reconstruction obligation.

## Fresh-occupant wound exposed

A fresh future Sol realization following ordinary delta semantics will begin
**after** CE-000029.

The cursor itself stores only the coordinate, not the content or consequence
that prior Sol learned from CE-000029.

Therefore a new executable question is exposed:

```text
cursor says prior event was consumed
!=
fresh realization can reconstruct the semantic state produced by that consumption
```

This is an instance of the already-known boundary:

```text
cursor continuity
!=
working-state continuity
```

but it is now pressureable on an actual non-registry consumer.

## Registry A/B observation

Current apparatus provides two distinct functions.

### A — self continuity

`sol` is absent from `continuity/registry.json`, yet it has:

- an independent cursor;
- recovered sequential unread events;
- consumed required refs;
- acknowledged its own events monotonically.

Observed result:

```text
registry membership
!=
minimum capability for consumer-local continuity
```

### B — third-party discoverability

The canonical v0 registry contains exactly:

- `chatgpt-main`
- `codex-main`

and the registry validator is intentionally hard-coded to those two entries.

An observer restricted to the registry surface therefore cannot discover
`sol` or `pulse` as participants, even though both have working cursor files.

Observed result:

```text
working cursor consumer
!=
registry-discoverable participant
```

The smallest supported candidate function of registry membership is therefore:

```text
registry seat
→
canonical participant discoverability / declared association surface
```

not:

```text
registry seat
→
basic continuity capability
```

## Next executable pressures

### P1 — fresh Sol occupant reconstruction

Start a fresh invocation with no prior conversation and provide only:

- repository access;
- consumer identity `sol`;
- the ordinary continuity startup rules.

Ask it to recover its current task-local state without reading before its cursor
unless a required retained source explicitly warrants that recovery.

Pressure:

```text
consumed coordinate
?
recoverable working semantic state
```

### P2 — participant discovery / addressability

Give an independent observer only the declared registry surface and ask it to
enumerate continuity participants and their addressable coordinates.

Then separately give the observer the explicit consumer name `sol`.

Pressure:

```text
prior coordinate knowledge
?
registry-mediated discovery
```

A consequential registry function is earned only if a real coordination task
requires participant discovery / association that cursor-only operation does
not supply.

## Nonclaims

This result does not establish:

- persistent subjective experience;
- durable working semantic state;
- persistent agency;
- registry necessity in general;
- registry redundancy;
- invocation liveness;
- automatic coordination;
- shared cognition;
- authority or standing.
