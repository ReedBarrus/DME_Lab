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

and enforcing the current-bundle correspondence relation:

```text
ROLE
+
SEAT
+
ENGAGEMENT BINDING
+
CURRENT OBSERVATION BASIS

MUST REFER TO
THE SAME CURRENT
role / seat / occupant / invocation
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
and current observation basis for synthetic pressure.

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
work claim, standing, authority references, **or current observation content**.

Changing observer metadata, basis ID, or content hash is not evidence that the
new invocation observed the predecessor's payload.

## Cross-object correspondence

Schema-valid component objects do not make a valid ecology bundle by themselves.

The current engagement bundle is valid only when:

```text
binding.role_id
=
role.role_id
=
seat.role_id

binding.seat_id
=
seat.seat_id
=
basis.observer_seat_id

binding.occupant_id
=
seat.occupant_id
=
basis.observer_occupant_id

binding.invocation_id
=
seat.invocation_id
=
basis.observer_invocation_id
```

and:

```text
binding.observation_basis_ref
=
canonical identity of the exact basis object

binding.work_claim_ref
=
seat.work_claim_ref
```

Thus:

```text
INDIVIDUALLY VALID OBJECTS
!=
VALID COMPOSED ECOLOGY BUNDLE
```

The seat and engagement binding therefore cannot disagree about which current
work claim exists. Mutual null is a valid no-current-claim state; a non-null
current claim is valid only when both surfaces carry the exact same reference.

An older observation basis may later be carried as historical provenance only
through an explicitly typed historical-basis relation. That relation is not
materialized or qualified here.

Role-definition content identity/versioning remains unresolved in this candidate.
The current pressure correlates role objects by `role_id`; it does not yet
establish whether that identifier names a mutable current definition or an exact
versioned semantic object.

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

OLD OBSERVATION BASIS
!=
CURRENT INVOCATION OBSERVATION

FRESH BASIS IDENTITY
!=
FRESH OBSERVATION

REBASE OBSERVER METADATA
!=
REOBSERVE WORLD
```

Rotation constructs a fresh current basis carrier. By default its
`observed_objects[]`, `explicit_missing_objects[]`, and `source_refs[]` are
empty. Observation or missingness may be re-established only through explicitly
supplied fresh inputs for the new invocation.

A supplied observed-object claim is admitted only when its `source_ref` is also
present in the same basis object's `source_refs[]`.

```text
EXPLICITLY SUPPLIED
!=
ESTABLISHED

SOURCE REF NAMED
!=
SOURCE SUPPLIED

OBSERVATION CLAIM
!=
OBSERVATION GROUNDING
```

This first grounding membrane establishes an explicit
claim-to-represented-source relation.

A separate `observation_source_v0` carrier now represents the source-side
object coordinate:

```text
source_id
object_id
identity
```

The basis references the carrier by a content-addressed source ref derived from
the exact carrier bytes. A current observed-object claim is source-corresponding
only when the exact represented carrier agrees on:

```text
source_ref
object_id
identity
```

This earns only exact represented correspondence.

```text
SOURCE REPRESENTED
!=
SOURCE CORRESPONDS TO CLAIMED OBJECT

SOURCE CORRESPONDS TO OBJECT
!=
SOURCE ESTABLISHES CLAIMED IDENTITY

SOURCE / OBJECT / IDENTITY AGREEMENT
!=
SOURCE TRUTH
```

The `identity` value remains opaque and nonempty. This candidate does not
qualify an identity scheme, require SHA-256, authenticate the source, or establish
that the source's semantic claim is true.

The `explicit_missing_objects[]` channel is separately grounded by exact typed
`missingness_witness_v0` carriers. Each missingness row carries a
`witness_ref`, and the exact represented witness must agree on:

```text
object_id
reason
```

while the witness itself has:

```text
standing = UNAVAILABLE_AT_BASIS
```

This establishes only a represented current-basis unavailability relation.

```text
MISSINGNESS DECLARED
!=
MISSINGNESS ESTABLISHED

REASON STRING PRESENT
!=
UNAVAILABILITY BASIS REPRESENTED

MISSING
!=
ABSENT

MISSINGNESS WITNESS CORRESPONDS
!=
UNIVERSAL RETRIEVAL IMPOSSIBILITY
```

The witness is not treated as an authority grant or a proof that the object does
not exist, and witness truth/authenticity remains unqualified.

The observed-object channel also requires a typed `source_encounter_v0`
carrier. This carrier records a bounded current relation:

```text
seat_id
occupant_id
invocation_id
source_ref
encounter_kind = PRESENTED_TO_INVOCATION
basis_ref
```

A current observed-object claim is composition-valid only when the exact source
carrier corresponds and a source encounter is represented for the same current
seat, occupant, invocation, exact source ref, and basis coordinate.

```text
SOURCE CARRIER SUPPLIED
!=
SOURCE ENCOUNTERED

SOURCE ENCOUNTERED
!=
SOURCE UNDERSTOOD

SOURCE ENCOUNTERED
!=
SOURCE TRUE

SOURCE ENCOUNTERED
!=
OBJECT DIRECTLY PERCEIVED
```

The encounter relation does not make the chassis a full event/runtime system. It
does not establish encounter truth/authenticity, comprehension, direct
perception, or semantic truth.

The MISSING channel retains a separate specimen-specific encounter carrier:
`missingness_witness_encounter_v0`. A current missingness claim is
composition-valid only when its exact missingness witness corresponds and an
encounter with that exact witness is represented for the same current:

```text
seat_id
occupant_id
invocation_id
witness_ref
basis_ref
```

No generic epistemic-encounter abstraction is claimed from these two specimens.

```text
MISSINGNESS WITNESS SUPPLIED
!=
MISSINGNESS WITNESS ENCOUNTERED

WITNESS ENCOUNTERED
!=
WITNESS TRUE

WITNESS ENCOUNTERED
!=
OBJECT ABSENT

WITNESS ENCOUNTERED
!=
UNIVERSAL UNAVAILABILITY

WITNESS ENCOUNTERED
!=
MISSINGNESS-REASON UNDERSTANDING
```

The predecessor basis remains separately recoverable by exact identity, but its
payload is not current observation. A typed historical-consultation relation is
still future work and is not manufactured by this repair.

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
> references, and observation bases while enforcing the tested cross-object
> current-identity correspondence, work-claim correspondence, fresh-observation
> payload noninheritance, explicit represented source relations, exact
> represented source/object/identity correspondence for current observed-object
> claims, exact current-invocation source-encounter correspondence, exact
> represented missingness witness correspondence, and exact current-invocation
> missingness-witness encounter correspondence while avoiding the tested
> identity/authority/missingness collapses.

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
historical-basis reuse semantics
observation identity-scheme semantics
source truth / authenticity
semantic truth of source claims
source encounter truth / authenticity
source understanding or direct object perception
missingness witness truth / authenticity
missingness witness encounter truth / authenticity
missingness-reason understanding
generic epistemic-carrier encounter abstraction
universal retrieval impossibility
representation succession
legacy-seat migration
```
