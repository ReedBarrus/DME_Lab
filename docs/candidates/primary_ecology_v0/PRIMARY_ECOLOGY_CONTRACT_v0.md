# PRIMARY_ECOLOGY_v0 -- Candidate Grammar Contract

## Status

```text
CANDIDATE GRAMMAR ONLY
PROJECTED / EXTENSIBLE
NOT DURABLE ECOLOGY INSTALLATION
NO LIVE OCCUPANTS
NO LIVE INVOCATIONS
NO WORK CLAIMS
NO AUTHORITY
NO EXECUTION
```

## Sole bounded question

Can DME_Lab represent a minimal persistent ecology grammar without collapsing:

```text
ROLE
!=
SEAT
!=
OCCUPANT
!=
INVOCATION
!=
WORK CLAIM
!=
AUTHORITY
```

while also preserving:

```text
CURRENT WORLD
!=
OBSERVATION BASIS

MISSING
!=
ABSENT

FUNCTION EXISTS
!=
FUNCTION NEEDS A SEAT
```

The candidate does not qualify role intelligence, planning quality, scientific
quality, autonomy, scheduling, migration, or authority policy.

## Candidate role vocabulary

The retained fixture uses a bounded initial vocabulary:

```text
SCIENTIST
ADVERSARY
PLANNER
WORKSHOP
QC
RECONSTRUCTOR
COORDINATOR
```

The vocabulary is explicitly non-exhaustive.

```text
PROJECTED ROLE VOCABULARY
!=
FINAL ECOLOGY ONTOLOGY
```

`ARCHIVIST` remains deliberately unresolved between an interpretive role and a
deterministic support function.

## Role object

`ecology_role_v0` expresses only purpose and allowed/forbidden semantic output
classes. A role has no authority or execution effect.

```text
ROLE LABEL
!=
AUTHORITY PRINCIPAL

ROLE OUTPUT
!=
OUTPUT ADOPTION
```

## Seat object

`ecology_seat_v0` represents a durable place independently of occupancy.

```text
SEAT EXISTS
!=
OCCUPANT EXISTS
```

An empty seat is explicit:

```text
seat_state = AVAILABLE_UNOCCUPIED
occupant_id = null
invocation_id = null
work_claim_ref = null
```

A test occupant may be represented only as `OCCUPIED_CANDIDATE` with explicit
occupant and invocation identities. The candidate seat itself has no authority
or execution effect.

The fixture contains two Scientist seats to pressure:

```text
SAME ROLE
!=
SAME SEAT
```

## Engagement binding

`ecology_engagement_binding_v0` couples one role, seat, occupant, invocation,
and observation basis for synthetic pressure.

It may carry references to claims, standing, or authority, but references are
not adjudications.

```text
REFERENCE PRESENT
!=
REFERENCE VALID

AUTHORITY REF PRESENT
!=
AUTHORITY ESTABLISHED
```

A fresh occupant or invocation must not silently inherit prior invocation-local
work claim, standing, or authority references.

## Observation basis

`observation_basis_v0` records what one invocation actually observed at one
basis and what was explicitly unavailable.

```text
OBJECT EXISTS IN LATER WORLD
!=
OBJECT OBSERVED AT DECISION BASIS

OBJECT NOT OBSERVED
!=
OBJECT ABSENT

EXPLICITLY MISSING
!=
ABSENT
```

The basis is immutable input to the bounded evaluator; later world changes do
not rewrite it.

## Existing lineage

This candidate does not replace or mutate existing specialized continuity or
seat objects such as LABBOIB temporal-seat artifacts, `lab_packet_v0`, or the
continuity registry.

```text
GENERIC GRAMMAR CANDIDATE
!=
LEGACY SEAT MIGRATION
```

Representation succession and legacy-seat migration remain separate future
pressure surfaces.

## Claim ceiling

A green pressure may establish only:

> Under the frozen synthetic pressure, the candidate grammar can represent
> roles, seats, occupants, invocations, work-claim references, authority
> references, and observation bases without the tested identity/authority/
> missingness collapses.

It does not establish:

```text
durable ecology installation
role quality
seat autonomy
scheduler behavior
persistent occupant identity
standing inheritance
claim validity
authority validity
execution permission
representation succession
legacy-seat migration
```
