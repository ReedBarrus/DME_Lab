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
```

Explicit historical-basis reuse, if later needed, requires a separate typed
relation and is not modeled by this candidate.

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
```

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
