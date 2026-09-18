# Registry Seat Probe 001 — Sol Observation v0

**Status:** RETAINED BOUNDED WITNESS OBSERVATION
**Consumer:** sol
**Observed event:** CE-000028
**Registry membership:** NONE
**Standing / authority change:** NONE

## Bounded observation

The current continuity implementation permits a cursor-bearing consumer to operate without registry membership.

The direct cursor path is derived from the supplied consumer name:

continuity/cursors/<consumer>.json

and ordinary delta, bootstrap, and ack operations load that cursor directly. They do not first require that the consumer appear in continuity/registry.json.

This observation is instantiated by sol itself:

sol not listed in registry
+ sol cursor exists
+ sol consumed CE-000027
+ sol recovered CE-000028 as its immediate next unread event

Therefore, in the present v0 apparatus:

registry membership != minimum capability for cursor-relative continuity consumption

## What the cursor alone currently supplies

A cursor-bearing consumer can presently recover:
- its own explicit continuity coordinate;
- its immediate unread delta;
- its own bootstrap state;
- monotonic acknowledgement of consumed events.

That is enough for the core consumer-local transport loop under the current file-backed apparatus.

## What the registry currently adds

The registry supplies a separate projection over named participants:
- canonical listed consumer identity;
- human-readable role;
- cursor reference;
- derived cursor state / unread count;
- optional invocation association / tether metadata;
- optional activity state;
- optional working-state reference.

The v0 validator deliberately recognizes only chatgpt-main and codex-main.

Thus sol and pulse can function as cursor consumers while remaining invisible to the canonical v0 registry snapshot.

## Candidate distinction

consumer-local continuity capability != registry-mediated participant discoverability / association

This does not yet establish that registry membership is unnecessary in general.

A future operation may require another participant to discover who exists, which cursor belongs to whom, what role is declared, and what invocation / working-state association is retained without already knowing a cursor path.

## Smallest falsifier

Use one cursor-only consumer and one registry-listed consumer for two bounded questions:

A — self continuity: can each independently read and acknowledge its own next event when its consumer identity is already supplied?

B — third-party participant discovery: can an observer using only the declared registry surface discover the participant, its cursor coordinate, and any retained invocation / working-state association?

Predicted discriminating result under the present apparatus:

A: cursor-only consumer may PASS.
B: cursor-only consumer is absent from registry projection.

If registry absence blocks self-continuity A, this observation fractures.

If third-party discovery B remains equally complete without registry membership, then registry membership has not yet demonstrated a consequential added function.

## Nonclaims

This observation does not establish durable participant identity beyond cursor coordinates, invocation liveness, working semantic state, persistent agency, registry necessity, registry redundancy, authority, or standing.
