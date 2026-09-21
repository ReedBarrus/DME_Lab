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
Rotate occupant + invocation.
Expected: same seat, fresh occupant/invocation, no inherited local refs.

D -- invocation rotation
Same occupant, fresh invocation.
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
```

## Terminal result

```text
QUALIFIED_SYNTHETIC_GRAMMAR
or
PRIMARY_ECOLOGY_GRAMMAR_FRACTURES
```

## Stop

Stop after bounded synthetic evaluation. Do not install seats or migrate any
legacy representation.
