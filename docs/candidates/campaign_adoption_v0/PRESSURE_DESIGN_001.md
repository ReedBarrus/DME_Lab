# CAMPAIGN_ADOPTION_001 — PRESSURE DESIGN 002

## STATUS

```text
CORRECTED PRESSURE DESIGN FROZEN

IMPLEMENTATION:
AUTHORIZED AFTER THIS FREEZE

DOGFOOD_001 RETRY:
HELD UNTIL DURABLE ADOPTION EXISTS

COS-R2:
UNCHANGED
```

## Primary specimen

```text
campaign:
COCKPIT_OPERATING_SPACE_001

adopter:
REED

admission prerequisite:
effective_applicability is current
via CAMPAIGN_APPLICABILITY_PROJECTION_001
```

## Required cells

### A1 — applicable + explicit Reed adoption

```text
exact campaign
+
effective_applicability CURRENT
+
explicit Reed gesture

EXPECTED:
current_adoption_state = ADOPTED
live_developmental_contract = LIVE
```

### A2 — applicable but not adopted

```text
effective_applicability CURRENT
adoption history EMPTY

EXPECTED:
current_adoption_state = NOT_ADOPTED
live = NOT_LIVE
```

### A3 — adoption attempted while applicability not current

```text
effective_applicability NOT_CURRENT

EXPECTED:
REJECT NEW ADOPTION EVENT
```

Adoption cannot create its own applicability.

### A4 — wrong campaign identity

Same campaign label with different campaign bytes:

```text
EXPECTED:
REJECT
```

### A5 — explicit gesture provenance absent

```text
actor_id = REED
but no admissible explicit gesture reference

EXPECTED:
REJECT
```

### A6 — same adoption ID + same bytes

```text
EXPECTED:
IDEMPOTENT
```

### A7 — same adoption ID + changed bytes

```text
EXPECTED:
REJECT
```

### A8 — successful adoption has no neighboring effects

```text
selection NONE
assignment NONE
priority NONE
standing NONE
authority NONE
scheduler NONE
wake NONE
execution NONE
```

### A9 — explicit release targets exact adoption

```text
A1 ADOPTED

A2 ADOPTION_RELEASED
target_adoption_id = A1.id
target_adoption_sha256 = exact A1 durable identity

EXPECTED:
A1 remains historical
current_adoption_state = NOT_ADOPTED
live = NOT_LIVE
```

### A10 — world moves after adoption

```text
B2:
A1 unreleased
effective applicability CURRENT
→ LIVE

world → B3:
effective applicability NOT_CURRENT

EXPECTED:
A1 remains unreleased
current_adoption_state = ADOPTED
live = BLOCKED_NOT_CURRENT / NOT_LIVE
```

Proves:

```text
CURRENT APPLICABILITY LOST
!=
ADOPTION RELEASED
```

### A11 — applicability later restored without re-adoption

```text
same unreleased A1

B3 later receives valid current warrant

EXPECTED:
current_adoption_state = ADOPTED
live = LIVE

new adoption event:
NONE
```

Proves:

```text
CURRENT APPLICABILITY RESTORED
!=
NEW ADOPTION REQUIRED
```

### A12 — two campaigns adopted simultaneously

```text
C1 adopted
C2 adopted

EXPECTED:
both current adoption states = ADOPTED

priority:
NONE

event order:
NON-SEMANTIC
```

## Adversarial cells

### X1 — release wrong adoption SHA

Matching adoption ID, wrong durable SHA:

```text
EXPECTED:
REJECT
```

### X2 — release by campaign label only

```text
EXPECTED:
REJECT
```

### X3 — release already released adoption

```text
EXPECTED:
REJECT
or exact idempotent replay only if same release event ID + same bytes
```

### X4 — storage metadata excluded from adoption identity

```text
_seq
_rowid
_inserted_at
projection annotations
!=
durable adoption bytes
```

### X5 — downstream state smuggling rejected

Reject fields such as:

```text
priority
selected
assignment
authority_granted
standing
wake_now
execute
```

### X6 — adoption cannot provide or override applicability

Reject caller attempts to set:

```text
effective_applicability
historical_basis_status
revalidation_status
```

The apparatus consumes the read-only applicability projection.

### X7 — inferred intent is not adoption

Applicable campaign, recent activity, top UI position, or old chat context with
no durable adoption event:

```text
EXPECTED:
NOT_ADOPTED
```

### X8 — row / retrieval order does not create priority

Reverse history retrieval ordering for two campaigns:

```text
same adoption set
priority NONE
```

### X9 — applicability source unavailable

New adoption attempt when applicability projector/source is unavailable:

```text
EXPECTED:
FAIL CLOSED
NO ADOPTION WRITE
```

Existing historical adoption remains history; live state cannot become true
without current applicability.

### X10 — release does not alter applicability or standing

Before/after exact release:

```text
campaign applicability projection:
UNCHANGED

relation standing:
UNCHANGED
```

### X11 — operational stores unchanged

Around an adoption/release write, inspect:

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
```

### X12 — applicability restoration does not emit adoption

Transition:

```text
NOT_CURRENT → CURRENT_BY_REVALIDATION
```

with an existing unreleased adoption.

EXPECTED:
live projection changes
adoption history count unchanged
```

## Smallest apparatus boundary

The first executable apparatus should do no more than:

```text
1. load exact campaign identity

2. consume read-only effective applicability

3. validate explicit REED gesture for new ADOPTED event

4. retain exact append-only adoption/release event

5. derive current adoption state

6. derive current live state as:
   current adoption × current applicability
```

It must not:

```text
rewrite campaign
create or alter revalidation
override applicability
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

A green result supports only:

```text
EXPLICIT HUMAN DEVELOPMENTAL COMMITMENT
CAN BE DURABLY RETAINED AS ITS OWN RELATION

AND CURRENT LIVE STATUS CAN BE DERIVED FROM:

UNRELEASED ADOPTION
×
CURRENT EFFECTIVE APPLICABILITY

WITHOUT TURNING ADOPTION INTO
APPLICABILITY, PRIORITY, AUTHORITY,
SELECTION, OR EXECUTION.
```

## Held next step

After qualification and one durable adoption of:

```text
COCKPIT_OPERATING_SPACE_001
```

the exact same DOGFOOD_001 / COS-R2 specimen may proceed to its next transition.

No change to COS-R2 is authorized.
