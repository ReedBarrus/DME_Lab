# HISTORICAL_P11_PRODUCER_QUALIFICATION_001

## Object

```text
OBJECT_TYPE:
UPSTREAM_STANDING_PRODUCER_QUALIFICATION

OBJECT_ID:
HISTORICAL_P11_PRODUCER_QUALIFICATION_001

RELATION_TYPE:
REFERENCE_RETENTION_STATUS

TARGET_CONSUMER:
LANE_LIFECYCLE_DISPOSITION_001 / P11

REPAIR:
P11_EXACT_P10_SET_BINDING_001
```

## Sole question

Given the exact P10 conserved-reference set identity and raw carrier/retrieval
topology for a proposed RELEASE, can a producer derive exactly one of:

```text
RETAINABLE
NOT_RETAINABLE
```

without treating a retainable supplied subset as proof that the exact P10 set
is retainable?

## Repaired raw membrane

Allowed candidate input:

```text
p10_set_identity

required_refs[]:
  ref_id
  carrier_id
  content_id

carriers[]:
  carrier_id
  content_id

retrieval_edges[]:
  ref_id
  carrier_id

release_delete_carrier_ids[]
```

The producer first derives the exact identity of the supplied required-ref set
from the unique `ref_id` members using canonical set ordering.

Administration is valid only when:

```text
derived required-ref set identity
=
p10_set_identity
```

Only then may retention be evaluated.

Freeze:

```text
ALL SUPPLIED REFERENCES RETAINABLE
!=
EXACT P10 REFERENCE SET RETAINABLE

SUPPLIED SUBSET
!=
P10 SUBJECT SET

P10 SET IDENTITY
!=
CALLER ASSERTION ABOUT SET COMPLETENESS
```

Duplicate required-reference identities invalidate administration rather than
allowing multiplicity to disguise subject-set mismatch.

Set identity is order-insensitive:

```text
{R1,R2}
=
{R2,R1}
```

but content-sensitive to membership:

```text
{R1,R2}
!=
{R1,R2,R3}
```

## Retention derivation

After exact P10 subject binding succeeds, every required reference must have:

```text
exact carrier present
+
exact content identity match
+
explicit retrieval edge
+
carrier not deleted by proposed RELEASE
```

No partial success.

```text
OBJECT EXISTS NOW
!=
REFERENCE SURVIVES RELEASE

CARRIER EXISTS
!=
CONTENT IDENTITY MATCHES

MOST REFERENCES RETAINABLE
!=
REFERENCE SET RETAINABLE
```

## Frozen cells

```text
A
exact P10 set {R1,R2}; all references retained
=> VALID / RETAINABLE

B
exact P10 set; required retrieval edge absent
=> VALID / NOT_RETAINABLE

C
exact P10 set; required carrier deleted by RELEASE
=> VALID / NOT_RETAINABLE

D
exact P10 set; carrier content identity mismatch
=> VALID / NOT_RETAINABLE

E
exact P10 set; required carrier absent
=> VALID / NOT_RETAINABLE

F
P10 identity = {R1,R2,R3}
supplied required_refs = {R1,R2}
=> ADMINISTRATION_INVALID

G
same supplied members as valid set but changed P10 set identity
=> ADMINISTRATION_INVALID

H
duplicate-ref trick against a two-member P10 identity
=> ADMINISTRATION_INVALID

I
same exact P10 members supplied in different list order
=> VALID / RETAINABLE
```

Cell F is the explicit omitted-reference attack.

Cells G/H prove:

```text
MEMBERS LOOK PLAUSIBLE
!=
SUBJECT SET BOUND

NO DUPLICATE TRICK
NO CHANGED-IDENTITY TRICK
```

## Claim ceiling

A positive qualification establishes only the derivation law for retention of
an exactly P10-bound conserved-reference set.

It does not establish:

```text
P10 for historical Lane B
P11 for historical Lane B
historical RELEASE admissibility
```

Historical application must first derive the exact historical P10 reference set
and preserve its exact set identity into P11 administration.

No live lane mutation. No RELEASE. No P09 standing. No P18 repair. No merge authorization.
