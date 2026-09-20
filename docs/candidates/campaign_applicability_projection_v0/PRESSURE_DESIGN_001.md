# CAMPAIGN_APPLICABILITY_PROJECTION_001 — PRESSURE DESIGN 001

## STATUS

```text
PRESSURE DESIGN FROZEN

IMPLEMENTATION:
NONE

EXECUTION:
NONE

CAMPAIGN_ADOPTION_001:
HELD

DOGFOOD_001 RETRY:
HELD

COS-R2:
UNCHANGED
```

## Primary specimen

```text
campaign:
COCKPIT_OPERATING_SPACE_001

historical campaign basis:
retained exactly

qualified warrant source:
CAMPAIGN_BASIS_REVALIDATION_001

operational consumer:
campaign / selection applicability projection
```

The realization must pin exact campaign, basis, and revalidation identities at
execution time.

## Required cells

### P1 — historical basis current, no revalidation needed

```text
CampaignStore.snapshot().basis_status = CURRENT

revalidation:
NONE

EXPECTED:
historical_basis_status = CURRENT
revalidation_status = NONE
effective_applicability = CURRENT_BY_HISTORICAL_BASIS
```

This is the historical control cell.

### P2 — historical basis stale + exact valid revalidation

```text
historical_basis_status = STALE

valid durable revalidation:
campaign identity exact
queried basis identity exact
disposition CURRENTLY_APPLICABLE

EXPECTED:
revalidation_status = CURRENTLY_APPLICABLE
effective_applicability = CURRENT_BY_REVALIDATION

CampaignStore.snapshot().basis_status:
STILL STALE
```

Proves:

```text
HISTORY DID NOT BECOME CURRENT
```

### P3 — valid revalidation exists for B2, query is B3

```text
R1:
CURRENTLY_APPLICABLE @ B2

query:
B3

EXPECTED:
R1 MUST NOT UNBLOCK

historical warrant:
retained

relative revalidation status:
STALE_REVALIDATION

effective_applicability:
NOT_CURRENT
```

This is the primary anti-magic-bypass cell.

### P4 — revalidation belongs to wrong campaign identity

```text
campaign_id label may match
campaign_sha256 differs

EXPECTED:
REJECT WARRANT FOR THIS PROJECTION
effective_applicability != CURRENT_BY_REVALIDATION
```

### P5 — revalidation disposition INSUFFICIENT_BASIS

```text
exact campaign
exact queried basis
disposition:
INSUFFICIENT_BASIS

EXPECTED:
revalidation_status = INSUFFICIENT_BASIS
effective_applicability = NOT_CURRENT
```

### P6 — revalidation disposition NOT_APPLICABLE

```text
exact campaign
exact queried basis
disposition:
NOT_APPLICABLE

EXPECTED:
revalidation_status = NOT_APPLICABLE
effective_applicability = NOT_CURRENT
```

### P7 — selection projection consumes valid warrant

Fixture only:

```text
existing selected request
relation standing OPEN

historical basis:
STALE

effective applicability:
CURRENT_BY_REVALIDATION
```

EXPECTED:

```text
request_applicability:
CURRENT_BY_REVALIDATION

preparation:
ELIGIBLE_FOR_PACKET_PREPARATION
```

No new selection event is created.

### P8 — selection projection does not consume stale warrant

Fixture only:

```text
existing selected request
historical basis:
STALE

only CURRENTLY_APPLICABLE warrant:
B2

query:
B3
```

EXPECTED:

```text
request remains blocked

preparation:
BLOCKED_PENDING_REVALIDATION
or equivalent explicit NOT_CURRENT state
```

No downstream object is created.

### P9 — historical snapshot is unchanged by projection

Before and after projection:

```text
campaign bytes:
IDENTICAL

CampaignStore.snapshot(...):
IDENTICAL for same query

relation standing:
UNCHANGED
```

Projection is read-only.

### P10 — valid warrant does not adopt campaign

```text
effective_applicability:
CURRENT_BY_REVALIDATION

EXPECTED EFFECTS:
adoption NONE
live contract NOT_ESTABLISHED
selection creation NONE
assignment NONE
priority NONE
standing NONE
authority NONE
scheduler NONE
wake NONE
execution NONE
```

### P11 — exact warrant identity is exposed

For CURRENT_BY_REVALIDATION:

```text
projection includes:
revalidation_id
revalidation_sha256
```

The SHA is computed from the durable revalidation object only.

Storage/history fields such as:

```text
_seq
_rowid
_inserted_at
```

must not alter the durable warrant identity.

### P12 — multiple matching warrants do not create priority

If two exact CURRENTLY_APPLICABLE warrants exist for the same campaign and basis:

```text
EXPECTED:
effective applicability remains current

priority:
NONE

retrieval order:
NON-SEMANTIC

insertion order:
NON-SEMANTIC
```

If one warrant is exposed as the representative warrant, the selection rule must
be deterministic and explicitly non-authoritative. Prefer exposing all exact
matching identities if that is the smaller truthful implementation.

## Additional adversarial cells

### X1 — caller supplies fake effective-applicability verdict

Reject or ignore caller-supplied fields such as:

```text
effective_applicability = CURRENT_BY_REVALIDATION
historical_basis_status = CURRENT
revalidation_status = CURRENTLY_APPLICABLE
```

The projection derives these values from stores and exact inputs.

### X2 — revalidation ID exists but durable bytes changed

```text
same revalidation_id
different durable result SHA

EXPECTED:
warrant does not validate
```

### X3 — wrong basis hash with visually similar refs

```text
queried refs differ
queried basis hash differs

EXPECTED:
no CURRENT_BY_REVALIDATION
```

Exact basis identity is required.

### X4 — historical basis is CURRENT and stale historical revalidations exist

```text
historical basis:
CURRENT

old revalidations:
other bases

EXPECTED:
CURRENT_BY_HISTORICAL_BASIS

old warrants do not override or degrade historical truth
```

### X5 — revalidation store unavailable

If the optional revalidation source cannot be read:

```text
EXPECTED:
failure-legible NOT_CURRENT / unavailable state

NOT:
optimistic CURRENT_BY_REVALIDATION
```

The implementation must not fabricate applicability from missing evidence.

### X6 — projection writes nothing

Hash or otherwise inspect relevant stores before and after:

```text
campaign
revalidation
selection
preparation
assignment
wake
reentry
controller
```

EXPECTED:
UNCHANGED

No projection-side write is admitted.

### X7 — standing still gates preparation independently

```text
effective applicability:
CURRENT_BY_REVALIDATION

standing:
FRACTURED
```

EXPECTED:
preparation remains BLOCKED_OBSOLETE
or equivalent existing standing-derived block.

Likewise:

```text
standing:
EARNED
```

must remain blocked as resolved.

Applicability must not impersonate developmental relevance.

### X8 — applicability projection does not create live intent

Even if:

```text
campaign historically adopted elsewhere
or
UI displays campaign prominently
or
revalidation was just created
```

without the separately admitted adoption relation:

```text
live developmental contract:
NOT_ESTABLISHED
```

## Smallest apparatus boundary

The first executable apparatus should do no more than:

```text
1. load exact historical campaign snapshot

2. compute exact queried basis identity

3. inspect the dedicated revalidation store

4. validate matching durable warrant identity

5. derive:
   historical_basis_status
   revalidation_status
   effective_applicability

6. expose exact warrant identity when used

7. let the existing selection projection consume
   effective_applicability for preparation gating
```

It must not:

```text
rewrite CampaignStore.snapshot()
rewrite campaign bytes
create or alter revalidation results
adopt campaign
create selection events
assign seats
create priority
change standing
schedule
ring bells
wake seats
execute consequences
```

## Success boundary

A green pressure result would support only:

```text
AN EXACT REVALIDATION WARRANT
CAN BE CONSUMED BY THE EXISTING
OPERATIONAL APPLICABILITY PATH

FOR THE SAME EXACT CAMPAIGN
AND SAME EXACT CURRENT BASIS

WITHOUT FALSIFYING HISTORICAL
BASIS STATUS OR CREATING
DOWNSTREAM CONTROL EFFECTS.
```

## Held next steps

After qualification:

```text
CAMPAIGN_ADOPTION_001
implementation may be reconsidered

THEN

DOGFOOD_001 may be retried
against the SAME COS-R2 target
only after explicit adoption exists.
```

No dogfood continuation is authorized by this pressure design.
