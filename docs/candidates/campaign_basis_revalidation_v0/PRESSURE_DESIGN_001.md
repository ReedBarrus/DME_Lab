# CAMPAIGN_BASIS_REVALIDATION_001 — PRESSURE DESIGN 001

## STATUS

```text
PRESSURE DESIGN FROZEN

IMPLEMENTATION:
NONE

EXECUTION:
NONE

CAMPAIGN_ADOPTION_001:
UNTOUCHED

DOGFOOD_001 RETRY:
NOT EXECUTED
```

## Test specimen

Primary historical campaign:

```text
COCKPIT_OPERATING_SPACE_001
```

Observed dogfood stop:

```text
DOGFOOD_BLOCKED_BASIS
```

Primary historical campaign basis includes:

```text
git:2ee939453651da741769ea07210fcdeaec9da971
```

First observed dogfood current head:

```text
621f840709fc64c3b3947dcda945be9f5f14f399
```

Blocked receipt branch later retained:

```text
a4aaeab1783ed2e7689d0d5b53071a51a0e23137
```

The pressure implementation must pin exact identities at realization time. These
historical values do not authorize assuming later branch heads are equivalent.

## Ten required cells

### R1 — exact same basis

```text
historical campaign exact identity
candidate current basis == original campaign basis
raw evidence valid

EXPECTED:
CURRENTLY_APPLICABLE

replay:
idempotent exact relation

campaign bytes:
unchanged
```

This is the control cell.

### R2 — basis moved, required surfaces conserved

```text
current Git basis differs
BUT
all mechanically derived campaign-relevant
qualified surfaces / relations remain conserved
under inspectable current evidence

EXPECTED:
revalidation MAY return CURRENTLY_APPLICABLE
only if the apparatus establishes every grounded requirement

NOT ALLOWED:
"HEAD is descendant" as sufficient proof
```

This is the central positive continuity cell.

### R3 — required surface changed without current qualification

```text
one grounded required surface changes identity
and no admissible current evidence qualifies the replacement

EXPECTED:
INSUFFICIENT_BASIS
```

Historical campaign remains intact.

### R4 — required semantic relation fractured

```text
raw evidence establishes that one grounded
campaign-relevant relation no longer holds

EXPECTED:
NOT_APPLICABLE
```

No standing change is implied by this disposition.

### R5 — unrelated world change

```text
repository basis changes

change is outside the mechanically grounded
campaign-relevant requirement set

all grounded requirements remain established

EXPECTED:
campaign may remain CURRENTLY_APPLICABLE

ONLY IF:
irrelevance is mechanically established
rather than asserted by operator judgment
```

This cell pressures:

```text
WHOLE WORLD CHANGED
!=
CAMPAIGN-RELEVANT WORLD CHANGED
```

If the apparatus cannot mechanically prove irrelevance, the expected safe result
is `INSUFFICIENT_BASIS`, not optimistic applicability.

### R6 — historical campaign bytes changed

```text
campaign_id label reused
but historical campaign bytes / campaign_sha256 differ

EXPECTED:
prior revalidation DOES NOT TRANSFER

new exact campaign identity requires independent treatment
```

### R7 — revalidation succeeds without adoption

```text
revalidation disposition:
CURRENTLY_APPLICABLE

EXPECTED EFFECTS:
adoption NONE
selection NONE
assignment NONE
priority NONE
standing NONE
authority NONE
execution NONE
scheduler NONE
```

This cell must prove:

```text
REVALIDATED
!=
ADOPTED
```

### R8 — failure preserves history

```text
revalidation:
NOT_APPLICABLE
or
INSUFFICIENT_BASIS

EXPECTED:
historical campaign bytes unchanged
historical prior evidence retained
no destructive rewrite
no synthetic standing change
```

### R9 — world moves after successful revalidation

```text
R validates campaign against B2

current world later becomes B3

EXPECTED:
R remains valid historical evidence about B2
R does NOT make campaign applicable at B3

current applicability:
must be rederived
```

This cell proves:

```text
REVALIDATED AT B2
!=
APPLICABLE AT B3
```

### R10 — answer-key input rejected

```text
caller attempts to supply pre-adjudicated fields such as:

campaign_currently_applicable = true
surface_compatible = true
requirement_passed = true

EXPECTED:
REJECT

the apparatus may receive raw inspectable evidence,
not semantic verdicts disguised as inputs
```

## Additional adversarial checks

The realization should also verify that:

```text
- requirement derivation is deterministic for exact same inputs
- requirement omission is failure-legible
- requirement order does not silently change identity unless order is semantic
- storage/history metadata does not leak into campaign or evidence identity
- revalidation identifier replay with changed bytes is rejected
- current-basis identity is explicit and content-addressed
- no revalidation result mutates relation_standing
- no revalidation result enters selection history
- no revalidation result creates assignment, bell, wake, or controller rows
```

## Smallest apparatus boundary

The first executable apparatus should do no more than:

```text
1. load exact historical campaign bytes

2. derive the campaign-relevant continuity requirements
   from frozen historical material / pinned qualified surfaces

3. load raw current evidence for those requirements

4. evaluate each requirement

5. retain one basis-relative revalidation result

6. derive current applicability only when
   current basis identity exactly matches
   the successful revalidation basis
```

It must not:

```text
adopt campaign
draft requests
select work
assign seats
emit bells
wake seats
change standing
grant authority
schedule work
execute consequences
```

## Success boundary

A green pressure result would support only:

```text
CURRENT APPLICABILITY CAN BE
RE-ESTABLISHED AS A SEPARATE
BASIS-RELATIVE RELATION

WITHOUT REWRITING THE HISTORICAL CAMPAIGN.
```

It would not authorize adoption or DOGFOOD_001 continuation.

## Next authorized question after qualification

Only after this membrane is mechanically qualified should the separate question
be posed:

```text
CAMPAIGN_ADOPTION_001

Does Reed explicitly adopt
this exact currently-applicable campaign
as a live developmental contract?
```

That membrane is intentionally absent here.
