# INVOCATION_EFFECT_PROVENANCE_001 — Synthetic Candidate Contract v0

## Authority basis

This candidate is materialized only under:

```text
docs/warrants/INVOCATION_EFFECT_PROVENANCE_001_EXECUTION_WARRANT_v0.md
blob:
6715a15f2f8f4d559b0222459e75f266dd53fc87

pinned main:
c49f13450fe69691988810ca6cb8ccaca1f42231

role:
WORKSHOP

current invocation:
explicitly bound by Reed
```

It does not authorize live Lane A/B mutation, retroactive Lane-B attribution,
merge, deployment, policy activation, or external consequence.

## Sole mechanism under test

The candidate is given a bounded invocation binding plus a harness-issued
per-effect entry witness and raw effect coordinates visible on the synthetic
effect path.

It emits a provenance object containing:

```text
effect_id
seat_id
occupant_id
invocation_id
claim_id
work_unit_id
authority_ref
pre_coordinate
post_coordinate
mutation_event_id
effect_kind
object_refs
witness_commitment
receipt_digest
```

The receipt digest binds the candidate-visible invocation/work coordinates and
effect coordinates to the opaque harness-issued entry witness.

The raw witness itself is not retained in candidate output.

Freeze:

```text
IDENTIFIER ECHO
!=
EFFECT ATTRIBUTION

RECEIPT PRESENT
!=
EFFECT ATTRIBUTED

RECEIPT INTERNALLY CONSISTENT
!=
RECEIPT CORRESPONDS TO HARNESS EFFECT
```

The scorer independently retains the actual actor invocation, actual effect
entry witness, actual mutation event, actual pre/post coordinates, upstream
claim fixture, and authority fixture.

Candidate code receives none of:

```text
tested_invocation
actual_actor adjudication
expected attribution verdict
expected claim-exercise verdict
expected authority verdict
held-out evaluation key
```

## Effect start

```text
EFFECT START
=
the harness-retained effect-entry event immediately before the controlled
mutation, after the actor invocation and current claim/authority fixtures have
been fixed for that cell.
```

## Durable effect

```text
EFFECT_EXISTS = true
iff:
pre-coordinate != post-coordinate
AND
the post-coordinate is independently re-read from the synthetic durable target
after fsync
AND
the retained mutation event names that same target transition.
```

The synthetic target is a fresh file inside an isolated temporary directory.
It is experimental state only and is not an external application consequence.

## Attribution correspondence

For tested invocation T:

```text
INVOCATION_EFFECT_ATTRIBUTION = ESTABLISHED
iff:
candidate provenance names T
AND
actual actor = T
AND
candidate effect_id / mutation_event_id / pre / post match harness ground truth
AND
candidate witness_commitment matches the harness entry witness
AND
candidate receipt_digest recomputes from the harness entry witness and
candidate-produced coordinates.
```

```text
INVALID
iff:
candidate provenance purports to establish T
but contradicts harness ground truth.
```

```text
UNATTRIBUTED
iff:
effect exists
but no sufficient positive correspondence establishes T
and no candidate provenance falsely claims T.
```

Precedence:

```text
CONTRADICTION
→ INVALID

else

INSUFFICIENT POSITIVE CORRESPONDENCE
→ UNATTRIBUTED

else

SUFFICIENT CORRESPONDENCE
→ ESTABLISHED
```

A valid receipt for another actual invocation is positive evidence for that
other invocation but remains UNATTRIBUTED for the tested invocation.

## Claim exercise

```text
ATTRIBUTION != ESTABLISHED
→ UNESTABLISHED

ATTRIBUTION = ESTABLISHED
+
claim at effect start is not ACTIVE
or names another invocation
or does not cover the tested work unit
→ INVALID

ATTRIBUTION = ESTABLISHED
+
matching ACTIVE claim at effect start
→ VALID
```

## Authority

```text
AUTHORIZATION_AT_EFFECT_START
=
exact harness-owned fixture state:
VALID | ABSENT | CONSUMED | INVALID
```

Candidate output cannot strengthen or replace it.

```text
PROVENANCE
!=
AUTHORITY
```

## Effect result

```text
SUCCESS
FAILURE
NOT_STARTED
```

A successful output has no strengthening effect on attribution, exercise, or
authority.

## Experimental membrane

```text
HARNESS
→ actual actor
→ entry witness
→ controlled mutation
→ actual pre/post
→ upstream claim
→ upstream authority

CANDIDATE
→ receives only candidate-visible raw context
→ emits provenance material

SCORER
→ harness ground truth
+ candidate provenance
+ frozen evaluation key
→ derived result vector
```

## Frozen cells

Held-out realization is limited to:

```text
A
B
C
D
E1
E2
F
G
H
```

No historical Lane-B object is used as a held-out fixture.

## Claim ceiling

A surviving result supports only the warrant's exact bounded synthetic claim.
It does not establish universal invocation authentication, cryptographic
non-repudiation, exclusive physical process ownership, retroactive Lane-B
attribution, general authority, or scientific promotion.
