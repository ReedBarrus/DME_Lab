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
represented source relation.

Q3 adds a separate typed source carrier. The basis still carries only exact
source references; source carrier bytes live outside the observation basis and
are independently content-addressed.

```text
SOURCE REPRESENTED
!=
SOURCE CORRESPONDS TO CLAIMED OBJECT

SOURCE CORRESPONDS TO OBJECT
!=
SOURCE ESTABLISHES CLAIMED IDENTITY

SOURCE / OBJECT / IDENTITY CORRESPONDENCE
!=
SOURCE TRUTH
```

The candidate compares the observation row against the exact represented source
carrier on `source_ref`, `object_id`, and opaque `identity`. It does not
interpret the identity scheme or adjudicate source truth/authenticity.

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

F -- work-claim reference without represented authority ref
Expected: authority-reference standing remains NO_AUTHORITY_REF_REPRESENTED.
WORK CLAIM REPRESENTED != AUTHORITY REF REPRESENTED

G -- role authority leak
Mutate role authority_effect away from NONE.
Expected: reject.

H -- world object not in observation basis
Expected: UNKNOWN.
CURRENT WORLD != OBSERVATION BASIS

I -- represented missingness claim
Expected: MISSINGNESS_CLAIM_REPRESENTED, not ABSENT.

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

P3 -- fresh source claim may reestablish same fact
Old basis carries a POISON_SENTINEL source claim.
Fresh invocation receives an explicitly supplied source claim for the same fact,
plus exact source correspondence and current source encounter.
Expected: the basis row is SOURCE_CLAIM_REPRESENTED and the fully validated
current standing is SOURCE_PRESENTED.

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

Q3A -- source/object mismatch
Exact represented source carrier says:
object_id = GARY_FROM_ACCOUNTING
Observation says:
object_id = BIGFOOT
while both use the same exact source carrier ref.
Expected: reject OBSERVED_OBJECT_SOURCE_OBJECT_MISMATCH.

Q3B -- source/identity mismatch
Exact represented source carrier says:
object_id = BIGFOOT
identity = opaque:IDENTITY-B
Observation says:
object_id = BIGFOOT
identity = opaque:IDENTITY-A
Expected: reject OBSERVED_OBJECT_SOURCE_IDENTITY_MISMATCH.

Q3C -- exact correspondence
Exact represented source carrier and observation agree on:
source ref
object_id
identity
Expected: admissible as source-corresponding.

Q4A -- missingness witness not supplied
Basis claims SECRET_DRAGON_LEDGER = MISSING and names a witness ref, but no exact
witness carrier is supplied.
Expected: reject MISSINGNESS_WITNESS_NOT_SUPPLIED.

Q4B -- witness for wrong object
Witness says OTHER_OBJECT unavailable while basis says SECRET_DRAGON_LEDGER
missing.
Expected: reject MISSINGNESS_WITNESS_OBJECT_MISMATCH.

Q4C -- exact missingness correspondence
Witness says SECRET_DRAGON_LEDGER / UNAVAILABLE_AT_BASIS /
SOURCE_NOT_AVAILABLE_AT_BASIS and basis carries the same object/reason.
Expected: admissible as grounded missingness.

Q4D -- missingness reason mismatch
Witness says NETWORK_TIMEOUT while basis says PERMISSION_DENIED.
Expected: reject MISSINGNESS_WITNESS_REASON_MISMATCH.

Identity syntax remains opaque. Q3 does not require SHA-256 and does not qualify
the meaning, trustworthiness, or authenticity of any identity scheme.

Q4 addresses the second epistemic channel, `explicit_missing_objects[]`. A
missingness row must reference an exact typed `missingness_witness_v0` carrier
whose bytes establish only:

```text
object_id
standing = UNAVAILABLE_AT_BASIS
reason
```

The basis row and exact represented witness must correspond on `object_id` and
`reason`.

```text
MISSINGNESS DECLARED
!=
MISSINGNESS ESTABLISHED

REASON STRING PRESENT
!=
UNAVAILABILITY BASIS REPRESENTED

MISSINGNESS WITNESS CORRESPONDS
!=
OBJECT ABSENT
```

This does not claim universal retrieval impossibility or witness truth.

Q5 adds a bounded current-invocation encounter membrane for the observed channel.
An exact `source_encounter_v0` carrier represents only that one source was
presented to one seat / occupant / invocation at one basis coordinate.

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

For every current observed-object row, a supplied encounter must correspond on:

```text
seat_id
occupant_id
invocation_id
source_ref
basis_ref
```

R1 -- source exists, no encounter
Exact source carrier and observed row correspond, but no encounter carrier is
supplied.
Expected: reject CURRENT_SOURCE_ENCOUNTER_NOT_SUPPLIED.

R2 -- encounter belongs to wrong invocation
Expected: reject SOURCE_ENCOUNTER_INVOCATION_MISMATCH.

R3 -- encounter points to wrong source
Expected: reject SOURCE_ENCOUNTER_SOURCE_MISMATCH.

R4 -- exact current encounter
Current seat / occupant / invocation / exact source / basis coordinate all agree.
Expected: admissible as currently encountered.

R5 -- encounter belongs to wrong seat
Expected: reject SOURCE_ENCOUNTER_SEAT_MISMATCH.

R6 -- encounter belongs to wrong occupant
Expected: reject SOURCE_ENCOUNTER_OCCUPANT_MISMATCH.

R7 -- encounter belongs to wrong basis coordinate
Expected: reject SOURCE_ENCOUNTER_BASIS_MISMATCH.

The encounter carrier is not an event-runtime claim and does not qualify whether
the represented encounter itself is truthful.

Q6 pressures the symmetric missingness-side encounter relation without
generalizing the two encounter carriers into one abstraction.

A typed `missingness_witness_encounter_v0` represents only that one exact
missingness witness was presented to one current seat / occupant / invocation at
one basis coordinate.

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
INVOCATION UNDERSTOOD WHY RETRIEVAL FAILED
```

For every current missingness row, the encounter must correspond on:

```text
seat_id
occupant_id
invocation_id
witness_ref
basis_ref
```

S1 -- exact witness, no encounter
Expected: reject CURRENT_MISSINGNESS_WITNESS_ENCOUNTER_NOT_SUPPLIED.

S2 -- encounter belongs to wrong invocation
Expected: reject MISSINGNESS_WITNESS_ENCOUNTER_INVOCATION_MISMATCH.

S3 -- encounter points to wrong witness
Expected: reject MISSINGNESS_WITNESS_ENCOUNTER_WITNESS_MISMATCH.

S4 -- exact current witness encounter
Expected: admissible as currently encountered missingness basis.

S5 -- encounter belongs to wrong seat
Expected: reject MISSINGNESS_WITNESS_ENCOUNTER_SEAT_MISMATCH.

S6 -- encounter belongs to wrong occupant
Expected: reject MISSINGNESS_WITNESS_ENCOUNTER_OCCUPANT_MISMATCH.

S7 -- encounter belongs to wrong basis coordinate
Expected: reject MISSINGNESS_WITNESS_ENCOUNTER_BASIS_MISMATCH.

This pressure does not establish witness truth, object absence, universal
unavailability, or comprehension of the failure reason.

Q7 pressures the standing label earned by the observed-side machinery. The
legacy structural field name `observed_objects[]` is not itself semantic
standing.

```text
FIELD NAME observed_objects
!=
OBSERVED STANDING

SOURCE PRESENTED TO INVOCATION
!=
SOURCE INSPECTED / CONSUMED

SOURCE PRESENTED
!=
OBJECT DIRECTLY OBSERVED
```

T1 -- basis row alone
A basis row with source/object/identity content, without consulting the wider
current bundle, earns only:
SOURCE_CLAIM_REPRESENTED.

T2 -- full current chain
Exact source carrier + exact source/object/identity correspondence + exact
current source encounter with encounter_kind = PRESENTED_TO_INVOCATION earns:
SOURCE_PRESENTED.

T3 -- semantic ceiling
Neither basis-only status nor the fully validated current status may emit
OBSERVED under the present machinery.

Stronger future standing such as OBSERVED requires additional machinery for
inspection, consumption, attention, parsing, or another explicitly qualified
relation. Q7 does not choose that future mechanism.

Q8 pressures the symmetric semantic ceiling on the missingness side.

```text
FIELD NAME explicit_missing_objects
!=
MISSING STANDING

MISSINGNESS WITNESS PRESENTED
!=
RETRIEVAL ATTEMPT PERFORMED

MISSINGNESS WITNESS PRESENTED
!=
RETRIEVAL FAILURE DIRECTLY EXPERIENCED

MISSINGNESS WITNESS PRESENTED
!=
OBJECT ABSENT

MISSINGNESS WITNESS PRESENTED
!=
WITNESS TRUE
```

U1 -- basis row alone
A basis row in `explicit_missing_objects[]` earns only:
MISSINGNESS_CLAIM_REPRESENTED.

U2 -- full current chain
Exact witness + object/reason correspondence + exact current witness encounter
with encounter_kind = PRESENTED_TO_INVOCATION earns:
MISSINGNESS_WITNESS_PRESENTED.

U3 -- semantic ceiling
Neither basis-only status nor the fully validated current status may emit
MISSING under the present machinery.

Stronger future standing such as MISSING or RETRIEVAL_FAILED requires additional
machinery establishing the relevant retrieval or failure relation. Q8 does not
choose that future mechanism.

Q9 pressures the semantic ceiling on basis silence.

```text
CLAIM NOT REPRESENTED
!=
UNKNOWN

BASIS SILENT
!=
INVOCATION IGNORANT

NO CURRENT ROW
!=
NEGATIVE EPISTEMIC FACT
```

V1 -- basis silent
No source row and no missingness row exist for PROJECT_X.
Expected: UNREPRESENTED_AT_BASIS, not UNKNOWN.

V2 -- full current bundle silent
The entire current bundle validates but still contains no epistemic carrier for
PROJECT_X.
Expected: NO_CURRENT_REPRESENTED_CLAIM, not UNKNOWN.

V3 -- semantic ceiling
Silence must not manufacture UNKNOWN, ABSENT, MISSING, FALSE, or UNAVAILABLE.

Genuine UNKNOWN standing would require stronger future machinery such as a
declared exhaustive scope plus a qualified relation between the queried object
and that scope. Q9 does not invent such machinery.

Q10 pressures the cross-layer identity of both encounter types.

```text
SAME BASIS COORDINATE STRING
!=
SAME BASIS CONTENT IDENTITY

ENCOUNTER CORRESPONDS TO BASIS LABEL
!=
ENCOUNTER CORRESPONDS TO EXACT CURRENT BASIS
```

Both `source_encounter_v0` and
`missingness_witness_encounter_v0` retain the friendly `basis_ref` coordinate
but must additionally pin the exact current `observation_basis_ref` produced by
`observation_basis_ref(current_basis)`.

W1 -- source encounter / same friendly label / different basis bytes
Binding correctly pins the mutated current basis. Reusing the predecessor source
encounter must reject SOURCE_ENCOUNTER_EXACT_BASIS_MISMATCH.

W2 -- missingness encounter / same friendly label / different basis bytes
Binding correctly pins the mutated current basis. Reusing the predecessor
missingness encounter must reject
MISSINGNESS_WITNESS_ENCOUNTER_EXACT_BASIS_MISMATCH.

W3 -- exact current basis identity
Encounter and binding both pin the exact current basis identity.
Expected: admissible.

W4 -- mutate any basis byte after encounter
Keep seat / occupant / invocation / carrier / friendly basis coordinate stable,
repin the binding to the new exact basis, and reuse the old encounter.
Expected: old encounter no longer establishes current presentation.

A separate focused regression still verifies that mutating basis contents while
retaining an old binding `observation_basis_ref` rejects
`BINDING_OBSERVATION_BASIS_REF_MISMATCH`.

Q11 pressures the semantic ceiling on authority-reference silence.

```text
AUTHORITY REF SILENT
!=
AUTHORITY ABSENT

NO LOCAL AUTHORITY REF
!=
NO EXTERNAL AUTHORITY

NO REPRESENTED AUTHORITY
!=
AUTHORITY DENIED

NO REPRESENTED AUTHORITY
!=
AUTHORITY ESTABLISHED
```

X1 -- empty authority refs
`authority_refs = []`.
Expected: NO_AUTHORITY_REF_REPRESENTED, not ABSENT.

X2 -- unqualified authority ref present
`authority_refs = [authority://Q11-UNQUALIFIED]`.
Expected: UNADJUDICATED, not AUTHORIZED.

X3 -- negative semantic ceiling
Empty authority refs must not manufacture ABSENT, DENIED, UNAUTHORIZED, REVOKED,
or INVALID.

X4 -- work claim without authority ref
A work claim may be represented while the local authority-reference surface
remains empty.
Expected: work claim remains represented; authority-reference standing remains
NO_AUTHORITY_REF_REPRESENTED; authority effect remains NONE.

This pressure does not adjudicate authority validity, external authority,
execution permission, or denial. It establishes only what the binding itself
represents.

## Terminal result

```text
QUALIFIED_SYNTHETIC_GRAMMAR
or
PRIMARY_ECOLOGY_GRAMMAR_FRACTURES
```

## Stop

Stop after bounded synthetic evaluation. Do not install seats or migrate any
legacy representation.
