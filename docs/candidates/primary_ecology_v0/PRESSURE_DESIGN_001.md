# PRIMARY_ECOLOGY_GRAMMAR_001 -- Pressure Design

## Subject

`PRIMARY_ECOLOGY_v0` candidate grammar.

## Non-effects

```text
LIVE ECOLOGY MUTATION: NONE
CONTINUITY REGISTRY MUTATION: NONE
LANE MUTATION: NONE
OCCUPANT BINDING: NONE
WORK CLAIM: NONE
AUTHORITY: NONE
EXECUTION: NONE
MERGE: NONE
```

## Required cross-object law

Individual schema validity is not sufficient for an ecology bundle.

```text
ROLE OBJECT
+
SEAT OBJECT
+
ENGAGEMENT BINDING
+
CURRENT OBSERVATION BASIS

MUST CORRESPOND ON:

role_id
seat_id
occupant_id
invocation_id
exact observation-basis identity
```

The binding's `observation_basis_ref` pins the canonical content identity of the
exact basis object. Reusing an older basis as current observation for a fresh
occupant or invocation is invalid.

```text
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

A fresh invocation basis must not inherit prior `observed_objects[]`,
`explicit_missing_objects[]`, or `source_refs[]` merely because a predecessor
basis exists. Current observation payload is empty unless explicitly supplied as
fresh input for the new invocation.

Explicit historical-basis reuse, if later needed, requires a separate typed
relation and is not modeled by this candidate.

Fresh observation payload is not established merely because a caller supplies
an `observed_objects[]` entry. For each current observed-object claim, the
claim's `source_ref` must also appear in the basis-level `source_refs[]`.

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

This v0 relation establishes only that an observation claim has an explicitly
represented source relation. It does not establish that the source proves the
claimed object identity.

## Cells

```text
A -- explicit empty seat
Expected: PASS
SEAT EXISTS != OCCUPANT EXISTS

B -- same role / two seats
Expected: PASS
ROLE IDENTITY != SEAT IDENTITY

C -- occupant rotation
Prior invocation carries synthetic claim/standing/authority refs.
Rotate occupant + invocation and establish a corresponding fresh observation basis.
Expected: same seat, fresh occupant/invocation, no inherited local refs.

D -- invocation rotation
Same occupant, fresh invocation and corresponding fresh observation basis.
Expected: no prior work claim / standing / authority refs inherited.

E -- invocation without work claim
Expected: valid synthetic engagement binding.
INVOCATION != WORK CLAIM

F -- work-claim reference without authority
Expected: authority standing remains ABSENT.
WORK CLAIM != AUTHORITY

G -- role authority leak
Mutate role authority_effect away from NONE.
Expected: reject.

H -- world object not in observation basis
Expected: UNKNOWN.
CURRENT WORLD != OBSERVATION BASIS

I -- explicitly missing object
Expected: MISSING, not ABSENT.

J -- later world changes
Later synthetic world contains an object omitted from the prior basis.
Expected: prior basis remains UNKNOWN for that object.

K -- placeholder occupant
Attempt occupied seat with occupant_id = TBD.
Expected: reject rather than manufacture identity.

L -- authority-looking role label + authority reference
Synthetic role label says AUTHORIZER and binding carries authority ref.
Expected: role authority effect remains NONE; authority ref remains UNADJUDICATED.

M1 -- invocation / basis mismatch
Seat + binding say INV_B while exact basis says INV_A.
Expected: reject BINDING_BASIS_INVOCATION_MISMATCH.

M2 -- occupant / basis mismatch
Seat + binding say occupant B while exact basis says occupant A.
Expected: reject BINDING_BASIS_OCCUPANT_MISMATCH.

M3 -- seat / basis mismatch
Seat + binding say SCIENCE_TEST_02 while exact basis says SCIENCE_TEST_01.
Expected: reject BINDING_BASIS_SEAT_MISMATCH.

M4 -- role / seat mismatch
Binding says PLANNER while role + seat say SCIENTIST.
Expected: reject ROLE_SEAT_BINDING_MISMATCH.

N0 -- coherent work-claim correspondence
Both seat + binding null, and separately both carry the exact same claim ref.
Expected: both valid.

N1 -- current work-claim identity mismatch
Seat says claim://A while binding says claim://B.
Expected: reject SEAT_BINDING_WORK_CLAIM_MISMATCH.

N2 -- seat claim / binding absent
Seat says claim://A while binding says null.
Expected: reject SEAT_BINDING_WORK_CLAIM_MISMATCH.

N3 -- seat absent / binding claim
Seat says null while binding says claim://A.
Expected: reject SEAT_BINDING_WORK_CLAIM_MISMATCH.

P1 -- old observed object must not auto-propagate
Old basis observes POISON_SENTINEL.
Rotate invocation with no fresh observation input.
Expected: new basis reports POISON_SENTINEL = UNKNOWN and observed_objects = [].

P2 -- old missingness must not auto-propagate
Old basis reports MISSING_POISON_SENTINEL = MISSING.
Rotate invocation with no fresh missingness input.
Expected: new basis reports it = UNKNOWN and explicit_missing_objects = [].

P3 -- fresh observation may reestablish same fact
Old basis observes POISON_SENTINEL.
Fresh invocation receives an explicitly supplied fresh observation of the same fact.
Expected: new basis may report POISON_SENTINEL = OBSERVED with fresh source refs.

P4 -- historical basis remains separate
Retain exact old basis reference while fresh current basis is empty.
Expected: old ref != current ref; binding points only to current ref; old payload
does not become current observation.

Q1 -- observed object with zero represented basis sources
observed_objects contains MAGIC_OBJECT with source://TOTALLY-REAL-BRO
while source_refs = [].
Expected: reject OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED.

Q2 -- observed object references an unsupplied source
observed object source_ref = source://A
while basis source_refs = [source://B].
Expected: reject OBSERVED_OBJECT_SOURCE_NOT_REPRESENTED.
```

Q3 -- source-to-object identity correspondence is deliberately not tested here.
A matching `source_ref` does not yet prove that the source establishes the
claimed `identity`. That remains a separate future pressure surface.

A separate focused regression mutates the contents of an otherwise matching
observation basis while retaining the old `observation_basis_ref`. Expected:
reject `BINDING_OBSERVATION_BASIS_REF_MISMATCH`.

## Terminal result

```text
QUALIFIED_SYNTHETIC_GRAMMAR
or
PRIMARY_ECOLOGY_GRAMMAR_FRACTURES
```

## Stop

Stop after bounded synthetic evaluation. Do not install seats or migrate any
legacy representation.
