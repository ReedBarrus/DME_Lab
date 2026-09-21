# TWO_LANE_COORDINATION_001 — Qualification 001

## Status

```text
CONTRACT:
MATERIALIZED

GUARD:
MATERIALIZED

PRESSURE:
EXECUTED

QUALIFICATION:
SUPPORTED IN BOUNDED TESTED SCOPE

ACTIVE OPERATING LANES:
NOT YET INSTANTIATED AT THIS RECEIPT

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE

INTEGRATION AUTHORITY:
NONE
```

## Basis

```text
base main:
8a5321c098b7f3a944e180612cd2e670b20f282e

qualification branch:
two-lane-coordination-pressure-v0

green pre-receipt head:
3670943f56386633561719ca08ffb7d18c734f3a
```

## Natural failure specimen

The governing real specimen was the concurrent INVOCATION_RECOVERY_001
apparatus materialization:

```text
two invocations
same apparatus trajectory
same branch
same semantic purpose
no shared work claim
no pre-mutation coordination

Git serialization:
successful

byte divergence:
none in duplicated common components

coordination:
absent

collision detection:
late, before held-out realization
```

This supports:

```text
GIT SERIALIZATION != WORK COORDINATION
BYTE EQUIVALENCE != PROVENANCE COORDINATION
```

## Executed pressure

Workflow:

```text
TWO_LANE_COORDINATION_001
run 35563697384
job 106221251820
SUCCESS
```

Focused pressure:

```text
8 / 8 PASS
```

Cells establish, in bounded scope:

```text
A
non-overlapping work
→ NO_COORDINATION_BLOCK

B
same path / different declared semantics
→ REPRESENTATION_OVERLAP_ONLY
→ no automatic semantic block

C
different files / same exact semantic surface
→ SEMANTIC_COLLISION
→ COORDINATION_HOLD

D
same target lineage
+ same consequence envelope
+ overlapping artifact scope
→ PROVENANCE_COLLISION
→ COORDINATION_HOLD

E
peer branch advances
+ exact peer claim unchanged
→ activity visible
→ no mandatory stale ping-pong

E2
current acknowledged overlap
→ COORDINATION_HOLD

F
peer claim digest changes without acknowledgement
→ REVALIDATION_REQUIRED

malformed/effect-bearing claim
→ rejected
```

## Pressure-discovered repair

The first apparatus form treated any peer branch-head movement as semantic
staleness.

That would make:

```text
peer performs unrelated commit
→ local lane stale
→ local acknowledgement commit
→ peer lane stale
→ acknowledgement ping-pong
```

The repaired relation is:

```text
PEER BRANCH ACTIVITY
!=
PEER WORK-CLAIM CHANGE
```

Branch head remains observable provenance/activity telemetry.

The exact peer work-claim digest is the v0 semantic coordination freshness key.

## Earned claim

```text
TWO BOUNDED LANES
CAN PUBLISH EXACT WORK CLAIMS,
DISTINGUISH TESTED REPRESENTATION OVERLAP
FROM TESTED SEMANTIC / PROVENANCE COLLISION,
AND REQUIRE REVALIDATION WHEN
THE PEER CLAIM ITSELF CHANGES.
```

## Not earned

```text
SYSTEM_WRITE AUTHORITY
ROLE AUTHENTICATION
OCCUPANT AUTHENTICATION
GENERAL SEMANTIC CONFLICT DETECTION
SCHEDULER SAFETY
LEASE / HEARTBEAT SAFETY
AUTOMATIC WORK ALLOCATION
PARALLEL AUTHORITATIVE INTEGRATION
DISTRIBUTED CONSENSUS
```

```text
NO_COORDINATION_BLOCK
!=
AUTHORIZED_TO_MUTATE
```

## Operating boundary

A real lane may become ACTIVE only after a future invocation has:

1. been explicitly assigned that lane;
2. published its exact current work claim;
3. observed current relevant peer claims;
4. retained a peer coordination cursor;
5. passed the pre-mutation coordination guard;
6. separately possesses valid mutation authority.

Authoritative integration remains serialized.
