# CAMPAIGN_ADOPTION_001 — PRESSURE DESIGN 001

## STATUS

```text
PRESSURE DESIGN FROZEN

IMPLEMENTATION:
NONE

EXECUTION:
NONE

DOGFOOD_001 RETRY:
HELD

COS-R2:
UNCHANGED
```

## Primary specimen

```text
campaign:
COCKPIT_OPERATING_SPACE_001

prerequisite:
one exact CAMPAIGN_BASIS_REVALIDATION_v0 result
with disposition CURRENTLY_APPLICABLE
for one exact current basis
```

The realization must pin exact campaign and revalidation identities at execution time.

## Required cells

### A1 — valid applicable revalidation + explicit adoption

```text
exact campaign
+
exact CURRENTLY_APPLICABLE revalidation
+
exact current basis
+
explicit Reed adoption gesture

EXPECTED:
LIVE_DEVELOPMENTAL_CONTRACT
```

No downstream control effects.

### A2 — applicable but not adopted

```text
campaign:
CURRENTLY_APPLICABLE

adoption:
NONE

EXPECTED:
NOT_LIVE
```

Proves:

```text
APPLICABLE
!=
ADOPTED
```

### A3 — adoption against failed / insufficient applicability

```text
revalidation disposition:
INSUFFICIENT_BASIS
or
NOT_APPLICABLE

EXPECTED:
REJECT
```

### A4 — wrong campaign identity

```text
campaign_id may match label

campaign_sha256 does not match
revalidation.campaign_sha256

EXPECTED:
REJECT
```

### A5 — wrong revalidation identity

```text
revalidation_id label may match

revalidation_sha256 does not match
exact durable result bytes

EXPECTED:
REJECT
```

### A6 — idempotent adoption replay

```text
same adoption_id
+
same durable adoption bytes

EXPECTED:
IDEMPOTENT
```

### A7 — same adoption ID + changed bytes

```text
same adoption_id
+
different durable bytes

EXPECTED:
REJECT
```

### A8 — successful adoption has no neighboring effects

```text
ADOPTED

EXPECTED:
selection NONE
assignment NONE
priority NONE
standing NONE
authority NONE
scheduler NONE
wake NONE
execution NONE
```

Operational stores outside the adoption store should remain byte-for-byte unchanged where inspectable.

### A9 — explicit release ends exact adoption

```text
A1:
ADOPTED

A2:
ADOPTION_RELEASED
targeting exact A1 identity

EXPECTED:
A1 remains historical
current live contract from A1 ends
campaign identity unchanged
revalidation identity unchanged
standing unchanged
```

### A10 — world moves after adoption

```text
R1:
CURRENTLY_APPLICABLE @ B2

A1:
ADOPTED against R1 @ B2

world → B3

EXPECTED:
R1 remains historical
A1 remains historical
CURRENT LIVE STATE @ B3:
NOT_ESTABLISHED
```

### A11 — new revalidation does not inherit old adoption

```text
R2:
CURRENTLY_APPLICABLE @ B3

prior:
A1 ADOPTED against R1 @ B2

EXPECTED:
R2 does not become live from A1

new explicit adoption required
```

Proves:

```text
NEW REVALIDATION
!=
RENEWED HUMAN INTENT
```

### A12 — simultaneous live campaigns do not create priority

```text
C1:
valid applicable revalidation + valid adoption

C2:
valid applicable revalidation + valid adoption

EXPECTED:
both may be LIVE

priority:
NONE

ordering:
NON-SEMANTIC
```

## Additional adversarial cells

### X1 — release targets wrong adoption bytes

```text
release target_adoption_id matches
but target_adoption_sha256 differs

EXPECTED:
REJECT
```

### X2 — release without exact target

```text
ADOPTION_RELEASED
with only campaign_id / campaign_sha256

EXPECTED:
REJECT
```

Proves:

```text
RELEASE CAMPAIGN
!=
RELEASE EXACT ADOPTION RELATION
```

### X3 — second independent adoption does not imply priority

If the implementation permits a second adoption event for another campaign or another separately current relation:

```text
event insertion order
!=
priority
```

If v0 instead enforces one current adoption per exact campaign+revalidation relation, that constraint must be explicit and tested; it must not be inferred from row uniqueness accidentally.

### X4 — storage metadata excluded from durable adoption identity

```text
_seq
_rowid
_inserted_at
projection annotations

!=
durable adoption bytes
```

### X5 — caller cannot smuggle downstream state

Reject input fields such as:

```text
priority = 1
selected = true
authority_granted = true
standing = EARNED
wake_now = true
execute = true
```

### X6 — adoption cannot revalidate

Supply a stale / non-current revalidation relation plus otherwise valid adoption bytes.

```text
EXPECTED:
REJECT

ADOPTION
!=
REVALIDATION
```

### X7 — inferred intent is not explicit adoption

No explicit Reed adoption event exists.

The campaign is applicable, recently used, previously adopted, or appears at top of the UI.

```text
EXPECTED:
NOT_LIVE
```

### X8 — projection order is non-semantic

Reverse retrieval / row / UI ordering of multiple live campaigns.

```text
EXPECTED:
same live set
priority NONE
```

## Smallest apparatus boundary

The first executable apparatus should do no more than:

```text
1. load exact campaign identity

2. load exact durable revalidation identity

3. verify the revalidation is CURRENTLY_APPLICABLE
   for the exact adoption basis

4. accept one explicit Reed adoption or release gesture

5. retain one exact durable adoption event

6. derive current live developmental-contract state
   from adoption history + current applicability
```

It must not:

```text
rewrite campaign
rewrite revalidation
derive semantic equivalence
draft requests
select work
assign seats
create priority
change standing
grant authority
schedule
ring bells
wake seats
execute consequences
```

## Success boundary

A green pressure result would support only:

```text
EXPLICIT HUMAN DEVELOPMENTAL INTENT

CAN BE REPRESENTED AS A SEPARATE,
DURABLE,
BASIS-RELATIVE ADOPTION RELATION

BOUND TO AN EXACT CURRENTLY-APPLICABLE
CAMPAIGN JUDGMENT

WITHOUT BECOMING PRIORITY,
AUTHORITY,
SELECTION,
OR EXECUTION.
```

## Held next step

Only after mechanical qualification of this membrane may the exact same dogfood specimen be retried:

```text
COCKPIT_OPERATING_SPACE_001
COS-R2

FOCUS
→ ASSIGN
→ RING
→ MAYA
```

No change to the target is authorized here.
